# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Личный сайт Константина Стародубова на Hugo (extended). Только русский язык. Цель сайта, аудитории и ограничения — в [PRODUCT.md](PRODUCT.md); подробности структуры и деплоя — в [README.md](README.md).

## Команды

```bash
hugo server --buildFuture        # локально, http://localhost:1313 (конфигурация «hugo» в .claude/launch.json)
hugo --minify --cleanDestinationDir   # прод-сборка в public/
./deploy.sh                      # сборка + выгрузка в Yandex Object Storage (нужен настроенный yc)
./deploy.sh --no-delete          # то же, но без удаления устаревших объектов бакета
```

Тестов нет. Проверка — сборка без ошибок и просмотр страниц в браузере на 375 и 1280 px.

## Как устроено

- Тема — собственная `themes/signal/` (в репозитории, не сабмодуль). Стили одним файлом `assets/css/signal.css`: цвета и размеры текста — только через токены в `:root`; скрипты — `assets/js/signal.js`.
- Шрифты self-hosted в `static/fonts/`: Geologica (заголовки), Manrope (текст), JetBrains Mono (код). Новый шрифт должен иметь кириллицу.
- Картинки: JPEG/PNG, которые нужно обработать (WebP, `srcset`, `width/height`), кладутся в `assets/images/…`; в Markdown ссылка остаётся `/images/…`, файл находят `_markup/render-image.html` и `partials/cover-url.html`. В `static/images/` — только SVG и файлы, которые должны отдаваться как есть.
- Таблицы из Markdown оборачивает `_markup/render-table.html` (прокрутка по горизонтали).
- Разделы: `content/posts/` (адрес `/:slug/`), `content/fotografiya/` (`/фото/:slug/`), страницы `about`, `now`, «Материалы», «Рекомендации». Кириллические адреса и редиректы со старых `/ru/…`, `/en/` сохранять.
- Посты датированы будущим — поэтому `buildFuture: true`.

## Правила

- Сайт выкладывается из рабочей копии: всё, что лежит в `content/`, после `./deploy.sh` становится публичным.
- `deploy.sh` пропускает копии iCloud вида `index 2.html` и по умолчанию удаляет из бакета объекты, которых нет в сборке.
- Платных услуг сайт не предлагает: не добавлять тексты про консультации и «обсудить задачу».
- Никаких английских версий (`*.en.md` — архив, язык `en` отключён).
- Утверждения о себе и фактах в статьях — только проверяемые; не выдумывать отзывы, клиентов, цифры.
- Правки дизайна согласовывать с PRODUCT.md и отчётами в `.impeccable/`.
