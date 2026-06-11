# starodubov.pro

Личный сайт Константина Стародубова: информационная безопасность, комплаенс,
технологии идентификации. Генератор — [Hugo](https://gohugo.io/) (extended),
тема — собственная `themes/signal` (тёмная, неоновый акцент).

## Структура

- `content/` — контент: `_index.md` (главная, всё в front matter), `posts/`,
  `now.md`, `about.md`. Файлы `*.en.md` — архив английской версии, язык `en`
  отключён в `config/_default/languages.yaml`.
- `themes/signal/` — тема (включена в репозиторий, не сабмодуль).
- `config/_default/` — конфигурация (hugo, languages, menus, params).
- `static/` — favicon, robots.txt, изображения (`images/portrait.jpg` — фото
  для главной).
- `maintenance/index.html` — заглушка «сайт в разработке».
- `deploy.sh` — деплой в Yandex Object Storage.

## Локальная сборка

```bash
hugo server          # http://localhost:1313
hugo --minify        # прод-сборка в public/
```

Посты датированы будущим относительно создания сайта — в конфиге включён
`buildFuture: true`.

## Деплой

Хостинг — бакет Yandex Object Storage `starodubov.pro` (website hosting:
index `index.html`, ошибки `404.html`). Нужны Hugo и настроенный `yc`.

```bash
./deploy.sh
```

Скрипт собирает сайт, загружает файлы с корректными MIME-типами,
**нормализует ключи в NFC** (macOS хранит имена файлов в NFD — без этого
кириллические URL с «й»/«ё» отдают 404) и заливает редиректы со старых
адресов `/ru/...` и `/en/` на новые пути.

### Режим «сайт в разработке»

```bash
yc storage s3 rm s3://starodubov.pro --recursive
yc storage s3api put-object --bucket starodubov.pro --key index.html \
  --body maintenance/index.html --content-type "text/html; charset=utf-8"
yc storage s3api put-object --bucket starodubov.pro --key 404.html \
  --body maintenance/index.html --content-type "text/html; charset=utf-8"
```

Вернуть сайт: `./deploy.sh` (перезапишет и `index.html`, и `404.html`).
