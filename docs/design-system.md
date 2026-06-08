# Design System — starodubov.pro

Документ для передачи дизайн-системы (будущему себе, разработчику, LLM-агенту). Описывает токены, компоненты, паттерны и решения, принятые при vcard-редизайне.

**Стек:** Hugo + theme `hugo-narrow` (Tailwind CSS) + кастомные partials и CSS-оверрайды.

**Текущая палитра:** `claude` (warm caramel, переопределена для WCAG AA).

---

## 1. Принципы

1. **Consistency over creativity.** Один helper для секций, один класс для карточек. Если нужен новый стиль — сначала проверь, нет ли существующего токена.
2. **Tokens по умолчанию.** Никаких hex-цветов и арбитрарных пикселей в partials. Только CSS-переменные и Tailwind-scale.
3. **Accessibility-first.** WCAG 2.1 AA не сдвигается ради эстетики. Контраст ≥4.5:1 для текста, ≥3:1 для UI, фокус всегда видим.
4. **Minimal JS.** Все интерактивы либо CSS, либо native HTML. Animation через `transition`, уважение `prefers-reduced-motion`.

---

## 2. Design Tokens

Все токены — CSS custom properties, определённые в `[data-theme="claude"]` (light) и `[data-theme="claude"].dark` (dark). Light-токены переопределены в `assets/css/custom/a11y.css` для соответствия WCAG.

### 2.1 Colors

| Token | Light (OKLCH) | Dark (OKLCH) | Контраст с background | Использование |
|-------|---------------|--------------|----------------------|---------------|
| `--color-background` | `0.98 0.01 95` | `0.27 0 107` | — | Фон страницы |
| `--color-foreground` | `0.34 0.03 96` | `0.81 0.01 93` | 11.1 / 8.4 | Body text, H1-H3 |
| `--color-muted` | `0.93 0.02 90` | `0.22 0 107` | — | Фон badge/пилюль |
| `--color-muted-foreground` | **`0.45 0.02 95`** ⬅ | `0.77 0.02 99` | 7.0 / 7.3 | Даты, мета, secondary text |
| `--color-primary` | **`0.52 0.16 38`** ⬅ | `0.67 0.13 39` | 5.6 / 4.8 | Ссылки, CTA, акценты |
| `--color-primary-foreground` | **`1 0 0`** ⬅ | `1 0 0` | 5.9 / на primary | Текст внутри primary CTA |
| `--color-border` | **`0.65 0.02 95`** ⬅ | **`0.54 0.02 100`** ⬅ | 3.05 / 3.0 | Бордеры карточек, инпутов |
| `--color-card` | `0.98 0.01 95` | `0.27 0 107` | — | Фон карточек (= background) |

⬅ = переопределено в `a11y.css`. Без переопределения тема выдавала 3.58:1 для muted и 1.35:1 для border (не AA).

**Использование в Tailwind**: `text-foreground`, `bg-muted`, `border-border`, `text-primary` и т.д. Также opacity-варианты: `border-foreground/20`, `bg-primary/10`.

### 2.2 Typography

Используется Tailwind-scale без кастома.

| Role | Tailwind | Computed |
|------|----------|----------|
| H1 (hero) | `text-4xl md:text-5xl font-bold tracking-tight leading-[1.1]` | 36→48px |
| H2 (секция) | `text-2xl md:text-3xl font-bold tracking-tight` | 24→30px |
| H3 (карточка) | `text-lg font-semibold leading-snug` | 18px |
| Body | `text-base md:text-lg` | 16→18px |
| Body small | `text-sm` | 14px |
| Caption / meta | `text-xs` | 12px |
| Eyebrow | `text-xs font-medium uppercase tracking-wider text-primary` | 12px |

**Шрифты**: системный sans-serif стек темы. Без кастом-веб-шрифтов (для перфоманса).

### 2.3 Spacing

Tailwind-scale (rem-based). Правила использования:

| Контекст | Класс | rem |
|----------|-------|-----|
| **Section bottom margin** | `mb-16` | 4 |
| Section content gap внутри | `mb-6` / `mb-8` | 1.5 / 2 |
| Внутри карточки между элементами | `mb-2` / `mb-4` | 0.5 / 1 |
| Grid gap (карточки) | `gap-3` / `gap-4` | 0.75 / 1 |
| Card padding (large) | `p-6` | 1.5 |
| Card padding (medium) | `p-5` | 1.25 |
| Card padding (small) | `p-4` | 1 |

**Правило**: между секциями всегда `mb-16`. Если хочется «больше воздуха» — поменяй на уровне `<main>` (`py-6`), не точечно в секциях.

### 2.4 Border radius

| Token | Класс | Использование |
|-------|-------|---------------|
| Full circle | `rounded-full` | Аватары, пилюли badges |
| 2xl (16px) | `rounded-2xl` | Крупные карточки (services), портрет |
| xl (12px) | `rounded-xl` | Средние карточки (tiles, clusters), badge-иконки |
| lg (8px) | `rounded-lg` | Кнопки, инпуты |

### 2.5 Shadows

| Класс | Использование |
|-------|---------------|
| `shadow-xl` | Hero portrait |
| `shadow-sm` (custom через `.card-interactive:hover`) | Карточки при hover |
| Без shadow по умолчанию | Карточки в покое (border достаточно) |

`shadow-sm` — кастомный `box-shadow: 0 1px 2px 0 color-mix(in oklab, var(--color-foreground) 8%, transparent)`.

### 2.6 Motion

| Свойство | Значение |
|----------|----------|
| Default transition | `transition-all duration-200` |
| Easing | Tailwind default `cubic-bezier(0.4, 0, 0.2, 1)` |
| Hover lift | `translateY(-2px)` |
| Focus | Без motion (только outline) |

**`prefers-reduced-motion: reduce`** уважается — все transitions и animations отключаются глобально в `a11y.css`.

---

## 3. Components

### 3.1 Vcard hero

**Файл:** `layouts/_partials/home/vcard-hero.html`
**Использование:** только на главной (`home.contentOrder` → `vcard-hero`).

#### Что показывает
Портрет (1120×1400, AVIF + JPG через `<picture>`), имя (H1), должность, 3 пилюли метаданных, CTA-кнопки соцсетей.

#### Особенности
- Портрет: `loading="eager"`, `decoding="async"`, `fetchpriority="high"`, preloaded в `<head>` для LCP.
- Если файл `static/images/portrait.jpg` отсутствует — fallback на initials с gradient-фоном (`from-primary/30 via-primary/10 to-muted`).
- На мобильных: stack вертикально, портрет центрирован.
- На md+ : grid `[auto_1fr]` — портрет слева, identity справа.

#### A11y
- `<h1>` уникальный на странице.
- `alt` на `<img>` = имя автора.
- Социальные ссылки: `rel="noopener noreferrer"` для внешних.

#### Не делать
- Не добавлять в hero описание/bio — оно в about-section (`page-content`).
- Не дублировать H1.

---

### 3.2 Section heading

**Файл:** `layouts/_partials/home/_section-heading.html`
**Use whenever** есть заголовок секции на главной. **Обязательно** используется во всех `_partials/home/*.html`.

#### Параметры

| Param | Type | Required | Описание |
|-------|------|----------|----------|
| `title` | string | yes | Текст H2 |
| `eyebrow` | string | no | Маленькая надпись над заголовком (UPPERCASE tracking-wider primary) |
| `cta` | dict `{text, url}` | no | Ссылка справа (скрывается на mobile) |

#### Пример

```go-html-template
{{ partial "home/_section-heading.html" (dict
  "title" "Свежие статьи"
  "cta" (dict "text" "Все статьи →" "url" "/posts/"))
}}

{{ partial "home/_section-heading.html" (dict
  "eyebrow" "/now"
  "title" "Сейчас"
  "cta" (dict "text" "подробнее →" "url" "/now/"))
}}
```

#### Не делать
- Не писать собственный H2 в новом partial — всегда через helper. Если нужны другие стили — обнови helper.

---

### 3.3 Card (interactive)

**CSS-класс:** `.card-interactive` (в `assets/css/custom/a11y.css`)
**Используется в:** `services.html`, `section-tiles.html`, `topic-clusters.html`.

#### Что делает
Стандартизирует фон, border, transition, hover-lift, shadow, focus-within для любой clickable/highlightable карточки.

#### Поведение
| State | Visual |
|-------|--------|
| Default | `bg-card`, `border 1px var(--color-border)` |
| Hover | Border → `foreground/20`, `transform: translateY(-2px)`, `shadow-sm` |
| Focus-within | Border → `foreground/30` (для клавиатуры) |

#### Variants (через дополнительные классы)
| Variant | Padding | Radius | Когда |
|---------|---------|--------|-------|
| **Large** | `p-6` | `rounded-2xl` | Services / featured cards |
| **Medium** | `p-5` | `rounded-xl` | Topic clusters |
| **Small** | `p-4` | `rounded-xl` | Section tiles / quick links |

#### Пример

```html
<a href="/posts/" class="card-interactive group rounded-xl p-4 flex flex-col items-start">
  <div class="text-2xl mb-2" aria-hidden="true">📝</div>
  <h3 class="text-foreground group-hover:text-primary font-semibold text-sm transition-colors">Блог</h3>
  <p class="text-muted-foreground text-xs mt-1 leading-snug">Заметки про ИБ, финтех</p>
</a>
```

#### Не делать
- Не писать `bg-card border border-border hover:border-... hover:-translate-y-...` в новых местах — используй класс.
- Не накладывать `shadow-md` или другие тяжёлые shadows — система использует `shadow-sm`.

---

### 3.4 Icon badge

**CSS-класс:** `.icon-badge` (в `assets/css/custom/a11y.css`)
**Используется в:** `services.html` (5 карточек).

#### Что делает
Круглый-квадратный 48×48 контейнер для emoji-иконки на карточках services. На `group:hover` фон чуть ярче.

#### Размеры / визуал
- `3rem × 3rem`, `rounded-xl` (12px)
- `bg-primary/10` → `bg-primary/15` on hover
- Эмодзи: `text-2xl` (24px), центрирован

#### Пример

```html
<div class="icon-badge mb-4" aria-hidden="true">
  🛡
</div>
```

#### Не делать
- Не использовать в section-tiles / topic-clusters — там иконки plain (без badge), иначе перегрузка.

---

### 3.5 Section partials (home)

Полный inventory компонентов главной страницы:

| Partial | Назначение | В contentOrder |
|---------|-----------|----------------|
| `home/vcard-hero.html` | Hero с портретом и identity | ✅ |
| `home/page-content.html` | Bio (рендерит `content/_index.md` как prose) | ✅ |
| `home/services.html` | 5 карточек «сильные стороны» | ✅ |
| `home/section-tiles.html` | 4 плитки доступа к разделам | ✅ |
| `home/recent-posts.html` | Последние 3 поста через theme post-list | ✅ |
| `home/now-block.html` | Тизер /now/ (готов, но не активен) | ❌ |
| `home/topic-clusters.html` | 4 карточки категорий блога (готов, не активен) | ❌ |
| `home/_section-heading.html` | Helper для H2 (см. 3.2) | — |

**Конфиг порядка:** `config/_default/params.yaml` → `home.contentOrder`.

---

### 3.6 Search modal

**Файл:** `layouts/_partials/ui/search-modal.html` (override темы).

Тема предоставляет модалку поиска с `<input id="search-input">`. Я добавил `<label class="sr-only">` + `aria-label` для WCAG 3.3.2.

#### A11y
- `type="search"` (было `text`)
- `aria-label` дублирует label для надёжности
- Лейбл скрыт визуально через `sr-only`, но доступен screen reader'у

---

### 3.7 Yandex Metrica + informer

**Файлы:**
- `layouts/_partials/features/analytics.html` (dispatcher override темы — добавлен yandex)
- `layouts/_partials/features/analytics/yandex.html` (snippet счётчика)
- `layouts/_partials/layout/footer.html` (включает видимый informer 88×31)

**Конфиг:** `params.yaml` → `analytics.yandex.*`

| Param | Default | Описание |
|-------|---------|----------|
| `enabled` | `true` | Глобальный switch |
| `id` | `109105668` | Counter ID (number, не string) |
| `ssr` | `true` | |
| `webvisor` | `true` | Запись сессий (PII!) |
| `clickmap` | `true` | |
| `ecommerce` | `true` | |
| `accurateTrackBounce` | `true` | |
| `trackLinks` | `true` | |
| `informer.enabled` | `true` | Видимый бейдж в футере |
| `informer.type` | `pageviews` | `pageviews` / `visits` / `visitors` |
| `informer.lang` | `ru` | `ru` / `com` |

---

### 3.8 Icon partial

**Файл:** `layouts/_partials/features/icon.html` (override темы).

#### A11y default
- Если передан `ariaLabel` → `aria-label="..."` + `role="img"` (значащая иконка)
- Иначе → `aria-hidden="true"` + `focusable="false"` (декоративная)

#### Использование

```go-html-template
{{ partial "features/icon.html" (dict "name" "telegram" "size" "sm") }}
{{/* decorative — aria-hidden */}}

{{ partial "features/icon.html" (dict "name" "telegram" "size" "sm" "ariaLabel" "Telegram") }}
{{/* значащая — role=img + aria-label */}}
```

---

## 4. Patterns

### 4.1 Vcard landing (главная)

Порядок секций (`home.contentOrder`):
```yaml
- vcard-hero        # identity
- page-content      # bio
- services          # что предлагаю
- section-tiles     # навигация
- recent-posts      # последние статьи
```

Каждая секция:
- `mb-16` снизу
- H2 через `_section-heading.html` (кроме hero где H1)
- Контент в Container `max-w-4xl mx-auto` (из baseof)

### 4.2 Article page (post)

Тема рендерит:
- Cover (через `image-processor.html` — обрабатывает map/string `cover:` frontmatter)
- H1 (один, из frontmatter `title:`) — markdown body **должен** начинаться с `##`, не `#`
- TOC sidebar (если включён `params.toc.enabled`)
- Контент (prose-стилизация темы)

### 4.3 Skip-to-content

В `layouts/baseof.html` первым элементом `<body>`:

```html
<a href="#main" class="sr-only focus:not-sr-only focus:fixed focus:top-2 ...">
  {{ i18n "a11y.skip_to_content" }}
</a>
```

`<main id="main">` — целевой landmark.

---

## 5. Accessibility baseline (WCAG 2.1 AA)

| Критерий | Реализация |
|----------|-----------|
| 1.1.1 Non-text content | Все meaningful `<img>` имеют `alt`. Декоративные SVG — `aria-hidden`. |
| 1.3.1 Semantic structure | `<main>`, `<header>`, `<nav>`, `<footer>`, `<article>`. Heading hierarchy: 1×H1 на страницу, без skip-уровней. |
| 1.4.3 Contrast (text) | ≥4.5:1 для normal, ≥3:1 для large. Палитра переопределена в `a11y.css`. |
| 1.4.11 Non-text contrast | Бордеры карточек/инпутов ≥3:1. |
| 2.1.1 Keyboard | Skip-link, никакого `tabindex` ≥1, native интерактивы. |
| 2.4.3 Focus order | DOM order, нет manual tabindex. |
| 2.4.7 Focus visible | `*:focus-visible { outline: 2px solid var(--color-primary); outline-offset: 2px; }` — глобально. |
| 2.5.5 Touch target | `min-height: 44px` для nav, dock, search-modal через `a11y.css`. |
| 3.1.1 Language | `<html lang="ru-RU">` / `<html lang="en-US">`. |
| 3.3.2 Form labels | Search input: `<label class="sr-only">` + `aria-label`. |
| 4.1.2 Name/role/value | Icon partial выставляет `aria-hidden` или `role="img"+aria-label` по умолчанию. |

**Bonus:** `prefers-reduced-motion: reduce` уважается — все transitions ≤0.01ms.

---

## 6. File map

```
.
├── assets/
│   ├── css/
│   │   └── custom/
│   │       └── a11y.css                        # все кастом-стили + token overrides
│   └── icons/
│       └── vk.svg                              # добавлен (в теме нет)
├── config/_default/
│   ├── hugo.yaml                               # baseURL, languages, permalinks
│   ├── languages.yaml                          # description/keywords per locale
│   ├── menus.yaml                              # nav + footer + social
│   └── params.yaml                             # author, verification, analytics, contentOrder
├── content/
│   ├── _index.md / .en.md                      # bio (рендерит page-content)
│   ├── now/_index.md / .en.md                  # страница /now/
│   └── posts/*.md                              # 11 RU постов + 11 EN
├── i18n/
│   ├── ru.yaml                                 # все строки UI (включая a11y, search)
│   └── en.yaml
├── layouts/
│   ├── baseof.html                             # skip-link, <main id=main>
│   ├── now/list.html                           # лейаут страницы /now/
│   └── _partials/
│       ├── content/image-processor.html        # обрабатывает cover как map ИЛИ string
│       ├── features/
│       │   ├── analytics.html                  # dispatcher + yandex
│       │   ├── analytics/yandex.html           # snippet Метрики
│       │   └── icon.html                       # a11y-default aria-hidden
│       ├── home/
│       │   ├── _section-heading.html           # helper
│       │   ├── vcard-hero.html                 # active
│       │   ├── page-content.html               # active (bio)
│       │   ├── services.html                   # active
│       │   ├── section-tiles.html              # active
│       │   ├── recent-posts.html               # active
│       │   ├── now-block.html                  # ready, not in contentOrder
│       │   └── topic-clusters.html             # ready, not in contentOrder
│       ├── layout/
│       │   ├── head.html                       # preload, theme-color, verification
│       │   ├── head/js.html                    # main.js defer
│       │   ├── head/seo.html                   # Person/BlogPosting/WebSite schema
│       │   └── footer.html                     # + Metrica informer
│       ├── ui/search-modal.html                # label + aria-label
│       └── hreflang.html
├── scripts/
│   └── sync_to_obsidian.py                     # синк в knowledge base
├── static/
│   ├── images/
│   │   ├── portrait.{jpg,avif}                 # LCP-asset
│   │   ├── og-banner.{jpg,avif}
│   │   └── tree-logo.png
│   └── robots.txt                              # Clean-param, AI-bots block
└── docs/
    └── design-system.md                        # ← этот файл
```

---

## 7. Расширение / правила maintenance

### Когда добавляешь новый компонент

1. **Проверь, нет ли существующего.** В разделе 3 этого документа.
2. **Используй существующие токены.** Никаких hex, никаких rem-magic numbers.
3. **Helper для H2.** Все заголовки секций через `_section-heading.html`.
4. **Карточки — через `.card-interactive`.** Не пиши свой `border + hover + transition`.
5. **A11y чек:** контраст, focus-visible, touch ≥44px, aria-label/role на иконках.
6. **Добавь раздел в этот доку** (section 3) с описанием, параметрами, не-делать.

### Когда меняешь токен

1. **Пересчитай контраст** для всего, что зависит от токена. Скрипт: см. ниже.
2. **Light + Dark** — не забудь оба режима.
3. **Обнови таблицу токенов** в section 2.

### Скрипт пересчёта WCAG-контраста

`scripts/check_contrast.py` (можно сгенерить аналогично — см. inline-питон в чате при последнем аудите). Принимает OKLCH-пары → выдаёт ratio и pass/fail для AA.

### Добавление нового языка

1. `config/_default/languages.yaml` — описание языка
2. `i18n/<lang>.yaml` — все ключи (см. ru.yaml как шаблон)
3. Контент: `content/posts/<slug>.<lang>.md`
4. Hreflang настроится автоматически (см. `layouts/_partials/hreflang.html`)

### Дизайн-decisions, которые **не** меняются без переаудита

| Решение | Почему |
|---------|--------|
| Container `max-w-4xl` (896px) | Read comfort + visual balance с портретом |
| H2 `text-2xl md:text-3xl` | Иерархия с H1 (text-4xl md:text-5xl) |
| Section `mb-16` | Visual rhythm, проверено глазами |
| `.card-interactive` hover `-translate-y-2px` | Subtle feedback, не отвлекает |
| AVIF + JPG fallback | Покрытие 95%+ браузеров |
| Цветовая палитра Claude | Бренд (warm caramel матчит «дуб познания» logo) |

---

## 8. Дальше (известные пункты в backlog)

| Приоритет | Что | Усилие |
|-----------|-----|--------|
| P1 | `.btn-primary` / `.btn-secondary` / `.btn-ghost` классы (сейчас inline) | 1ч |
| P1 | `now-block` / `topic-clusters` восстановить в contentOrder | 30мин |
| P2 | Per-page OG image с заголовком поста | 2ч |
| P2 | Tailwind purge оптимизация (CSS 109 KB → ~40 KB) | 2ч |
| P3 | Self-host KaTeX для постов где он нужен | 30мин |
| P3 | Scripts/check_contrast.py как формальный тул | 30мин |

---

*Последнее обновление: после design-system unification commit.*
