# starodubov.pro

Персональный блог Константина Стародубова о технологиях, информационной безопасности и жизни. Сайт собран на [Hugo](https://gohugo.io/) с темой [Narrow](https://github.com/tom2almighty/hugo-narrow) и доступен по адресу [starodubov.pro](https://starodubov.pro/).

## Запуск локально

Требуется установленный Hugo (extended).

```bash
# Инициализировать тему (подмодуль) после клонирования
git submodule update --init --recursive

# Запустить локальный сервер
hugo server -D
```

Сайт будет доступен на `http://localhost:1313/`.

## Структура

- `content/posts/` — статьи блога (русский язык)
- `content/_index.md`, `content/_index.en.md` — главная страница (RU/EN)
- `config/_default/` — конфигурация Hugo (основные настройки, языки, меню, параметры)
- `themes/` — тема оформления (git-подмодуль)
- `static/` — статические файлы (изображения, favicon)

## Деплой

Инструкция по публикации репозитория и деплою на GitHub Pages — в [git.md](git.md).
