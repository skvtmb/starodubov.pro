# Signal — тёмная тема для Hugo

Смелая тёмная тема для личного сайта эксперта: герой с портретом, блок «обо мне», услуги, разделы, блог с категориями/тегами и аккуратные страницы статей с оглавлением и прогресс-баром чтения.

Моноширинные акценты, неоновый зелёный, типографика Space Grotesk / Manrope / JetBrains Mono.

---

## Что внутри

```
hugo-theme-signal/
├── theme.toml                 — метаданные темы
├── archetypes/default.md      — шаблон новой статьи
├── assets/
│   ├── css/signal.css         — все стили (проходят minify + fingerprint)
│   └── js/signal.js           — reveal, прогресс чтения, активный пункт оглавления
├── layouts/
│   ├── _default/baseof.html   — каркас страницы
│   ├── _default/single.html   — статья (оглавление, автор, «читать дальше»)
│   ├── _default/list.html     — лента раздела (с пагинацией)
│   ├── _default/taxonomy.html — список категорий / тегов
│   ├── _default/term.html     — материалы одной категории / тега
│   ├── index.html             — главная (собирается из front matter _index.md)
│   ├── page/single.html       — простые страницы (например «Сейчас»)
│   ├── partials/              — head, header, footer, карточка поста
│   └── shortcodes/callout.html— блок-врезка {{</* callout "TL;DR" */>}}…{{</* /callout */>}}
└── exampleSite/               — готовый рабочий пример (контент Стародубова)
```

---

## Быстрый старт

### Вариант 1. Посмотреть пример

```bash
cd hugo-theme-signal/exampleSite
hugo server --themesDir ../..
```

Откройте http://localhost:1313 — это полностью собранный сайт со всеми страницами.

### Вариант 2. Поставить на свой сайт

1. Скопируйте папку темы в свой проект:
   ```bash
   cp -r hugo-theme-signal <ваш-сайт>/themes/signal
   ```
2. В `hugo.toml` укажите тему и перенесите блок `[params]`, `[menu]`,
   `[taxonomies]` и `[markup]` из `exampleSite/hugo.toml`:
   ```toml
   theme = "signal"
   ```
3. Скопируйте `exampleSite/content/_index.md` в свой `content/` и отредактируйте
   текст героя, блок «обо мне» и услуги прямо во front matter.
4. Положите своё фото в `static/images/portrait.png`.

> Требуется Hugo **extended** 0.128+ (для `minify`/`fingerprint` и нового блока `[pagination]`).

---

## Как редактировать контент

| Что | Где |
|---|---|
| Имя, логотип-знак, контакты, подвал, соцсети | `hugo.toml` → `[params]` |
| Пункты меню | `hugo.toml` → `[menu]` |
| Герой, «обо мне», услуги, плитки разделов | `content/_index.md` (front matter) |
| Статьи | `content/posts/*.md` |
| Страница «Сейчас» | `content/now.md` |

### Новая статья

```bash
hugo new posts/moya-statya.md
```

Front matter статьи:

```yaml
---
title: "Заголовок"
date: 2026-02-01
description: "Короткое описание — станет лид-абзацем и текстом карточки."
categories: ["Информационная безопасность"]
tags: ["ФСТЭК", "комплаенс"]
cover: "/images/posts/cover.jpg"   # необязательно — обложка карточки и OG
---
```

Заголовки `##` автоматически попадают в оглавление и нумеруются (01, 02, …).

---

## Кастомизация цвета

Акцент и фон — CSS-переменные в начале `assets/css/signal.css`:

```css
:root{
  --bg:#0a0a0b;
  --acc:oklch(0.86 0.19 145);   /* неоновый зелёный — поменяйте оттенок здесь */
}
```

---

## Лицензия

MIT. Шрифты self-hosted (woff2 в static/fonts/, @font-face в signal.css).
