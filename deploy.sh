#!/bin/bash
# Деплой starodubov.pro в Yandex Object Storage через yc storage s3 cp.
# Каждый тип файлов грузится своим проходом с явными Content-Type и Cache-Control:
#  - immutable assets (css/js/изображения/шрифты) — год + immutable
#  - HTML / XML / JSON / robots.txt — 5 минут с must-revalidate

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BUCKET="starodubov.pro"
S3_URI="s3://${BUCKET}/"
CACHE_LONG="public, max-age=31536000, immutable"
CACHE_SHORT="public, max-age=300, must-revalidate"

echo -e "${BLUE}🚀 Деплой ${BUCKET}${NC}"
echo "=================================="

if ! command -v hugo &> /dev/null; then
    echo -e "${RED}❌ Hugo не установлен (https://gohugo.io/installation/)${NC}" >&2
    exit 1
fi

if ! command -v yc &> /dev/null; then
    echo -e "${RED}❌ Yandex CLI (yc) не найден${NC}" >&2
    exit 1
fi

if ! yc config list &> /dev/null; then
    echo -e "${RED}❌ Yandex CLI не настроен (yc init)${NC}" >&2
    exit 1
fi

echo -e "\n${YELLOW}🔨 Сборка...${NC}"
hugo --minify --gc --cleanDestinationDir
[ -d public ] || { echo -e "${RED}❌ public/ не создан${NC}" >&2; exit 1; }
echo -e "${GREEN}✅ Сайт собран ($(du -sh public | cut -f1))${NC}"

# Аплоад одного типа файлов: pattern, content-type, cache-control, описание
upload_type() {
    local pattern=$1 ct=$2 cache=$3 label=$4
    local count
    count=$(find public -name "$pattern" -type f 2>/dev/null | wc -l | tr -d ' ')
    [ "$count" -eq 0 ] && return 0
    echo -e "${BLUE}  → ${label} (${count} файлов)${NC}"
    yc storage s3 cp public/ "$S3_URI" \
        --recursive \
        --content-type "$ct" \
        --cache-control "$cache" \
        --no-guess-mime-type \
        --exclude "*" \
        --include "$pattern" \
        --only-show-errors 2>&1 | grep -v "YC_CLI_INITIALIZATION_SILENCE" || true
}

echo -e "\n${YELLOW}📤 Immutable-ассеты (1 год кэша)${NC}"
upload_type "*.css"      "text/css; charset=utf-8"          "$CACHE_LONG" "CSS"
upload_type "*.js"       "application/javascript; charset=utf-8" "$CACHE_LONG" "JavaScript"
upload_type "*.svg"      "image/svg+xml"                    "$CACHE_LONG" "SVG"
upload_type "*.jpg"      "image/jpeg"                       "$CACHE_LONG" "JPEG"
upload_type "*.jpeg"     "image/jpeg"                       "$CACHE_LONG" "JPEG"
upload_type "*.png"      "image/png"                        "$CACHE_LONG" "PNG"
upload_type "*.gif"      "image/gif"                        "$CACHE_LONG" "GIF"
upload_type "*.webp"     "image/webp"                       "$CACHE_LONG" "WebP"
upload_type "*.avif"     "image/avif"                       "$CACHE_LONG" "AVIF"
upload_type "*.ico"      "image/x-icon"                     "$CACHE_LONG" "ICO"
upload_type "*.woff"     "font/woff"                        "$CACHE_LONG" "WOFF"
upload_type "*.woff2"    "font/woff2"                       "$CACHE_LONG" "WOFF2"
upload_type "*.ttf"      "font/ttf"                         "$CACHE_LONG" "TTF"

echo -e "\n${YELLOW}📤 Динамика (5 мин кэш с must-revalidate)${NC}"
upload_type "*.html"        "text/html; charset=utf-8"           "$CACHE_SHORT" "HTML"
upload_type "*.xml"         "application/xml; charset=utf-8"     "$CACHE_SHORT" "XML"
upload_type "*.json"        "application/json; charset=utf-8"    "$CACHE_SHORT" "JSON"
upload_type "*.webmanifest" "application/manifest+json"          "$CACHE_SHORT" "WebManifest"
upload_type "*.txt"         "text/plain; charset=utf-8"          "$CACHE_SHORT" "TXT"

echo -e "\n${YELLOW}🔍 Проверка MIME и Cache-Control...${NC}"
check_url() {
    local key=$1 expect_ct=$2 expect_cache=$3
    local headers ct cache
    headers=$(curl -sI "https://${BUCKET}/${key}" 2>/dev/null)
    ct=$(echo "$headers" | grep -i "^content-type:" | tr -d '\r' | sed 's/^[Cc]ontent-[Tt]ype: *//')
    cache=$(echo "$headers" | grep -i "^cache-control:" | tr -d '\r' | sed 's/^[Cc]ache-[Cc]ontrol: *//')
    if [[ "$ct" == "$expect_ct"* ]]; then
        echo -e "${GREEN}  ✅ ${key}${NC}"
        echo -e "${GREEN}     Content-Type: ${ct}${NC}"
        echo -e "${GREEN}     Cache-Control: ${cache}${NC}"
    else
        echo -e "${RED}  ❌ ${key}${NC}"
        echo -e "${RED}     Content-Type: ${ct} (ожидался ${expect_ct})${NC}"
        echo -e "${RED}     Cache-Control: ${cache}${NC}"
    fi
}

CSS_KEY=$(find public -name "*.css" -type f | head -1 | sed 's|^public/||')
JS_KEY=$(find public -name "*.js" -type f | head -1 | sed 's|^public/||')
[ -n "$CSS_KEY" ] && check_url "$CSS_KEY" "text/css" "$CACHE_LONG"
[ -n "$JS_KEY" ] && check_url "$JS_KEY" "application/javascript" "$CACHE_LONG"
check_url "index.html" "text/html" "$CACHE_SHORT"

echo -e "\n${GREEN}=================================="
echo -e "✅ Деплой завершён"
echo -e "==================================${NC}"
echo -e "${BLUE}🌐 https://${BUCKET}${NC}"
