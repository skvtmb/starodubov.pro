#!/bin/bash
# Скрипт деплоя сайта starodubov.pro в Yandex Object Storage
# с правильными MIME-типами
# Использует Yandex CLI (yc)

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Конфигурация
BUCKET="starodubov.pro"

# macOS хранит имена файлов в NFD (й = и + ◌̆), а Hugo генерирует ссылки в NFC —
# без нормализации ключей кириллические URL с «й»/«ё» отдают 404
nfc_key() {
    printf '%s' "$1" | /usr/bin/python3 -c 'import sys,unicodedata;sys.stdout.write(unicodedata.normalize("NFC",sys.stdin.read()))'
}

echo -e "${BLUE}🚀 Деплой сайта starodubov.pro${NC}"
echo "=================================="

# Проверка наличия Hugo
if ! command -v hugo &> /dev/null; then
    echo -e "${RED}❌ Hugo не установлен!${NC}"
    echo "Установите Hugo: https://gohugo.io/installation/"
    exit 1
fi

# Проверка наличия yc
if ! command -v yc &> /dev/null; then
    echo -e "${RED}❌ Yandex CLI (yc) не найден!${NC}"
    echo "Установите Yandex CLI:"
    echo "  curl https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash"
    echo "Или добавьте в PATH, если уже установлен"
    exit 1
fi

# Проверка конфигурации yc
if ! yc config list &> /dev/null; then
    echo -e "${RED}❌ Yandex CLI не настроен!${NC}"
    echo "Настройте CLI:"
    echo "  yc init"
    exit 1
fi

# Сборка сайта
echo -e "\n${YELLOW}🔨 Сборка сайта...${NC}"
hugo --minify

if [ ! -d "public" ]; then
    echo -e "${RED}❌ Папка public/ не создана!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Сайт собран${NC}"

# Загрузка в Object Storage
echo -e "\n${YELLOW}📤 Загрузка файлов в Yandex Object Storage...${NC}"

# Функция для загрузки файлов с правильным MIME-типом
upload_files() {
    local pattern=$1
    local content_type=$2
    local description=$3
    
    echo -e "\n${BLUE}${description}${NC}"
    local count=$(find public -name "$pattern" -type f 2>/dev/null | wc -l | tr -d ' ')
    
    if [ "$count" -gt 0 ]; then
        echo "   Найдено файлов: $count"
        find public -name "$pattern" -type f | while read file; do
            key=$(nfc_key "${file#public/}")
            if yc storage s3api put-object \
                --bucket "$BUCKET" \
                --key "$key" \
                --body "$file" \
                --content-type "$content_type" &> /dev/null; then
                echo -n "."
            else
                echo -n "!"
            fi
        done
        echo ""
        echo -e "${GREEN}   ✅ Загружено${NC}"
    fi
}

# Загрузка файлов по типам с правильными MIME-типами
upload_files "*.css" "text/css" "Загрузка CSS файлов"
upload_files "*.js" "application/javascript" "Загрузка JS файлов"
upload_files "*.json" "application/json" "Загрузка JSON файлов"
upload_files "*.svg" "image/svg+xml" "Загрузка SVG файлов"
upload_files "*.xml" "application/xml" "Загрузка XML файлов"
upload_files "*.webmanifest" "application/manifest+json" "Загрузка WebManifest файлов"

# Загрузка HTML файлов
echo -e "\n${BLUE}Загрузка HTML файлов${NC}"
find public -name "*.html" -type f | while read file; do
    key=$(nfc_key "${file#public/}")
    yc storage s3api put-object \
        --bucket "$BUCKET" \
        --key "$key" \
        --body "$file" \
        --content-type "text/html; charset=utf-8" &> /dev/null && echo -n "." || echo -n "!"
done
echo ""
echo -e "${GREEN}   ✅ HTML файлы загружены${NC}"

# Загрузка изображений и других файлов
echo -e "\n${BLUE}Загрузка остальных файлов${NC}"
find public -type f ! -name "*.css" ! -name "*.js" ! -name "*.json" ! -name "*.svg" ! -name "*.xml" ! -name "*.webmanifest" ! -name "*.html" | while read file; do
    key=$(nfc_key "${file#public/}")
    # Определяем MIME-тип по расширению
    case "$file" in
        *.png) content_type="image/png" ;;
        *.jpg|*.jpeg) content_type="image/jpeg" ;;
        *.gif) content_type="image/gif" ;;
        *.webp) content_type="image/webp" ;;
        *.avif) content_type="image/avif" ;;
        *.ico) content_type="image/x-icon" ;;
        *.woff) content_type="font/woff" ;;
        *.woff2) content_type="font/woff2" ;;
        *.ttf) content_type="font/ttf" ;;
        *.eot) content_type="application/vnd.ms-fontobject" ;;
        *) content_type="application/octet-stream" ;;
    esac
    yc storage s3api put-object \
        --bucket "$BUCKET" \
        --key "$key" \
        --body "$file" \
        --content-type "$content_type" &> /dev/null && echo -n "." || echo -n "!"
done
echo ""
echo -e "${GREEN}   ✅ Остальные файлы загружены${NC}"

# Редиректы со старых адресов /ru/<путь>/ и /en/ (до смены темы сайт жил в подкаталогах языков)
echo -e "\n${BLUE}Загрузка редиректов /ru/ и /en/${NC}"
STUBS_DIR=$(mktemp -d)
find public -name index.html | sed 's|^public/||; s|index.html$||' | while read p; do
    p_nfc=$(nfc_key "$p")
    mkdir -p "$STUBS_DIR/ru/$p"
    printf '<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=https://starodubov.pro/%s"><link rel="canonical" href="https://starodubov.pro/%s"><title>Перенаправление</title></head><body><a href="https://starodubov.pro/%s">Страница переехала</a></body></html>' "$p_nfc" "$p_nfc" "$p_nfc" > "$STUBS_DIR/ru/${p}index.html"
done
mkdir -p "$STUBS_DIR/en" && cp "$STUBS_DIR/ru/index.html" "$STUBS_DIR/en/index.html"
find "$STUBS_DIR" -name index.html | while read f; do
    key=$(nfc_key "${f#$STUBS_DIR/}")
    yc storage s3api put-object \
        --bucket "$BUCKET" \
        --key "$key" \
        --body "$f" \
        --content-type "text/html; charset=utf-8" &> /dev/null && echo -n "." || echo -n "!"
done
echo ""
echo -e "${GREEN}   ✅ Редиректы загружены${NC}"
rm -rf "$STUBS_DIR"

# Проверка MIME-типов критичных файлов
echo -e "\n${YELLOW}🔍 Проверка MIME-типов...${NC}"

# Находим первый CSS файл
CSS_FILE=$(find public -name "*.css" -type f | head -1)
if [ -n "$CSS_FILE" ]; then
    CSS_KEY="${CSS_FILE#public/}"
    echo -e "Проверка CSS: $CSS_KEY"
    CONTENT_TYPE=$(curl -sI "https://$BUCKET/$CSS_KEY" 2>/dev/null | grep -i "content-type:" | cut -d' ' -f2 | tr -d '\r')
    if [[ "$CONTENT_TYPE" == "text/css"* ]]; then
        echo -e "${GREEN}  ✅ CSS: $CONTENT_TYPE${NC}"
    else
        echo -e "${RED}  ❌ CSS: $CONTENT_TYPE (ожидается text/css)${NC}"
    fi
fi

# Находим первый JS файл
JS_FILE=$(find public -name "*.js" -type f | head -1)
if [ -n "$JS_FILE" ]; then
    JS_KEY="${JS_FILE#public/}"
    echo -e "Проверка JS: $JS_KEY"
    CONTENT_TYPE=$(curl -sI "https://$BUCKET/$JS_KEY" 2>/dev/null | grep -i "content-type:" | cut -d' ' -f2 | tr -d '\r')
    if [[ "$CONTENT_TYPE" == "application/javascript"* ]] || [[ "$CONTENT_TYPE" == "text/javascript"* ]]; then
        echo -e "${GREEN}  ✅ JS: $CONTENT_TYPE${NC}"
    else
        echo -e "${RED}  ❌ JS: $CONTENT_TYPE (ожидается application/javascript)${NC}"
    fi
fi

# Итоговое сообщение
echo -e "\n${GREEN}=================================="
echo -e "✅ Деплой завершен успешно!"
echo -e "==================================${NC}"
echo -e "\n${BLUE}🌐 Сайт доступен по адресу:${NC}"
echo -e "   https://$BUCKET"
echo -e "\n${YELLOW}💡 Рекомендации:${NC}"
echo -e "   1. Откройте сайт в браузере с Disable Cache (Cmd+Shift+R / Ctrl+Shift+R)"
echo -e "   2. Проверьте DevTools → Network → Content-Type для CSS/JS"
echo -e "   3. Убедитесь, что стили применяются корректно"
echo ""