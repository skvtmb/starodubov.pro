#!/bin/bash
# Деплой сайта starodubov.pro в Yandex Object Storage.
# - корректные MIME-типы и Cache-Control по типам файлов
# - NFC-нормализация ключей (macOS хранит имена в NFD — иначе кириллические
#   URL с «й»/«ё» отдают 404)
# - инкрементальность: неизменённые объекты (md5 == ETag) не перезаливаются
# - редиректы со старых адресов /ru/<путь>/ и /en/
# Использует Yandex CLI (yc).

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BUCKET="starodubov.pro"

echo -e "${BLUE}🚀 Деплой сайта starodubov.pro${NC}"
echo "=================================="

if ! command -v hugo &> /dev/null; then
    echo -e "${RED}❌ Hugo не установлен!${NC}"
    exit 1
fi

if ! command -v yc &> /dev/null; then
    echo -e "${RED}❌ Yandex CLI (yc) не найден!${NC}"
    echo "  curl https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash"
    exit 1
fi

if ! yc config list &> /dev/null; then
    echo -e "${RED}❌ Yandex CLI не настроен! Выполните: yc init${NC}"
    exit 1
fi

echo -e "\n${YELLOW}🔨 Сборка сайта...${NC}"
hugo --minify

if [ ! -d "public" ]; then
    echo -e "${RED}❌ Папка public/ не создана!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Сайт собран${NC}"

echo -e "\n${YELLOW}📤 Загрузка в Object Storage (инкрементально)...${NC}"

BUCKET="$BUCKET" python3 - <<'PYEOF'
import hashlib, html, json, os, subprocess, sys, tempfile, unicodedata
from concurrent.futures import ThreadPoolExecutor

BUCKET = os.environ['BUCKET']
SITE = 'https://starodubov.pro'

CONTENT_TYPES = {
    '.html': 'text/html; charset=utf-8', '.css': 'text/css',
    '.js': 'application/javascript', '.json': 'application/json',
    '.svg': 'image/svg+xml', '.xml': 'application/xml',
    '.webmanifest': 'application/manifest+json', '.txt': 'text/plain; charset=utf-8',
    '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
    '.gif': 'image/gif', '.webp': 'image/webp', '.avif': 'image/avif',
    '.ico': 'image/x-icon', '.woff': 'font/woff', '.woff2': 'font/woff2',
    '.ttf': 'font/ttf', '.eot': 'application/vnd.ms-fontobject',
}

def content_type(path):
    return CONTENT_TYPES.get(os.path.splitext(path)[1].lower(), 'application/octet-stream')

def cache_control(path):
    ext = os.path.splitext(path)[1].lower()
    # CSS/JS фингерпринтятся Hugo — можно кэшировать навсегда
    if ext in ('.css', '.js'):
        return 'public, max-age=31536000, immutable'
    if ext in ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.avif', '.ico',
               '.svg', '.woff', '.woff2', '.ttf', '.eot'):
        return 'public, max-age=2592000'
    if ext == '.html':
        return 'no-cache'
    return 'public, max-age=3600'

def nfc(s):
    return unicodedata.normalize('NFC', s)

def md5_file(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def list_remote():
    """key -> etag (md5 для немногочастных загрузок)"""
    remote, marker = {}, None
    while True:
        cmd = ['yc', 'storage', 's3api', 'list-objects', '--bucket', BUCKET,
               '--max-keys', '1000', '--format', 'json']
        if marker:
            cmd += ['--marker', marker]
        out = json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout or '{}')
        contents = out.get('contents') or []
        for obj in contents:
            remote[obj['key']] = (obj.get('etag') or '').strip('"')
        if out.get('is_truncated') and contents:
            marker = contents[-1]['key']
        else:
            return remote

def put(args):
    key, body = args
    cmd = ['yc', 'storage', 's3api', 'put-object', '--bucket', BUCKET,
           '--key', key, '--body', body,
           '--content-type', content_type(key),
           '--cache-control', cache_control(key)]
    r = subprocess.run(cmd, capture_output=True)
    return key, r.returncode == 0

print('Получаю список объектов бакета...')
remote = list_remote()
print(f'В бакете объектов: {len(remote)}')

# 1) файлы сайта из public/
jobs, skipped = [], 0
for root, _, files in os.walk('public'):
    for name in files:
        path = os.path.join(root, name)
        key = nfc(os.path.relpath(path, 'public'))
        if remote.get(key) == md5_file(path):
            skipped += 1
        else:
            jobs.append((key, path))

# 2) редиректы /ru/<путь>/ и /en/ со старой структуры
stub_dir = tempfile.mkdtemp()
stub_tpl = ('<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8">'
            '<meta http-equiv="refresh" content="0; url={u}">'
            '<link rel="canonical" href="{u}"><title>Перенаправление</title></head>'
            '<body><a href="{u}">Страница переехала</a></body></html>')
stub_keys = ['en/index.html']
for root, _, files in os.walk('public'):
    if 'index.html' in files:
        rel = nfc(os.path.relpath(root, 'public'))
        stub_keys.append('ru/index.html' if rel == '.' else f'ru/{rel}/index.html')
for i, key in enumerate(stub_keys):
    target = key[3:-len('index.html')].lstrip('/')
    body = stub_tpl.format(u=html.escape(f'{SITE}/{target}', quote=True))
    if remote.get(key) == hashlib.md5(body.encode()).hexdigest():
        skipped += 1
        continue
    path = os.path.join(stub_dir, f'stub{i}.html')
    open(path, 'w', encoding='utf-8').write(body)
    jobs.append((key, path))

print(f'К загрузке: {len(jobs)}, без изменений (пропущено): {skipped}')
failed = []
with ThreadPoolExecutor(max_workers=8) as ex:
    for key, ok in ex.map(put, jobs):
        sys.stdout.write('.' if ok else '!')
        sys.stdout.flush()
        if not ok:
            failed.append(key)
print()
if failed:
    print('ОШИБКИ загрузки:')
    for k in failed:
        print(' -', k)
    sys.exit(1)
print(f'Загружено: {len(jobs) - len(failed)}')
PYEOF

echo -e "\n${YELLOW}🔍 Проверка MIME-типов...${NC}"
CSS_FILE=$(find public -name "*.css" -type f | head -1)
if [ -n "$CSS_FILE" ]; then
    CSS_KEY="${CSS_FILE#public/}"
    CONTENT_TYPE=$(curl -sI "https://$BUCKET/$CSS_KEY" 2>/dev/null | grep -i "content-type:" | cut -d' ' -f2 | tr -d '\r')
    if [[ "$CONTENT_TYPE" == "text/css"* ]]; then
        echo -e "${GREEN}  ✅ CSS: $CONTENT_TYPE${NC}"
    else
        echo -e "${RED}  ❌ CSS: $CONTENT_TYPE (ожидается text/css)${NC}"
    fi
fi

echo -e "\n${GREEN}=================================="
echo -e "✅ Деплой завершен!"
echo -e "==================================${NC}"
echo -e "${BLUE}🌐 https://$BUCKET${NC}"
