---
title: "Ghostty + tmux + Neovim: полная настройка окружения (Gruvbox)"
date: 2025-02-14T12:00:00+03:00
draft: false
summary: "Как собрать удобное DevOps-окружение на базе Ghostty, tmux, zsh и Neovim с темой Gruvbox — от выбора инструментов до готового workflow."
categories: ["Технологии"]
tags: ["ghostty", "tmux", "neovim", "gruvbox", "терминал", "разработка", "настройка", "cli", "zsh", "powerlevel10k"]
cover:
  image: "/images/ghostty-tmux-nvim-cover.png"
  alt: "Окружение Ghostty + tmux + Neovim с темой Gruvbox"
  caption: "Терминал Ghostty, мультиплексор tmux и редактор Neovim — единая связка для разработки"
---

В очередной раз, сбрасывая свой ноутбук, я решил настроить всё по-человечески и сохранить все нужные конфигурации в одном месте. Мне нравится тема **Gruvbox** — тёплые, приятные глазу цвета и хорошая читаемость в любое время суток. С неё и начал. Дальше пошёл искать более лёгкий терминал: раньше пользовался iTerm2, но он стал слишком тяжёлым и долго запускается — выбор пал на **Ghostty**.

В этой статье — зачем такая связка, как её собрать и какие настройки использовать, чтобы получить готовое окружение для разработки и DevOps.

![Окружение Ghostty с tmux и Neovim в тёмной теме](/images/ghostty-tmux-nvim-cover.png "Окружение Ghostty с tmux и Neovim")

## Зачем эта связка

**Ghostty** — быстрый кроссплатформенный терминал с нативной UI и GPU-ускорением. Запускается мгновенно, не тянет лишнюю память, поддерживает лигатуры, темы и низкую задержку ввода. После iTerm2 разница в отзывчивости очень заметна.

**tmux** — мультиплексор терминала: сессии, окна и панели в одном месте. Можно отключиться от сессии и подключиться снова с другого устройства — всё остаётся на месте. Удобно для долгих задач, логов, нескольких проектов одновременно.

**Neovim** — редактор с LSP, автодополнением и привычным для vim-пользователей управлением. Работает одинаково локально и по SSH, что важно для единого workflow.

**zsh + Oh My Zsh + Powerlevel10k** — удобная оболочка и информативный prompt без лишней возни с настройкой.

Вместе это даёт единое окружение: один терминал, одна тема (Gruvbox), одни сочетания клавиш. Идеально подходит для ежедневной разработки и DevOps: код в Neovim, логи в соседней панели tmux, команды в третьей панели.

![Код в тёмной теме — типичный вид при работе в Neovim](https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800 "Код в тёмной теме")

## Содержание

- Установка зависимостей
- Настройка Ghostty (Gruvbox)
- Настройка tmux
- zsh + Oh My Zsh + Powerlevel10k
- Настройка Neovim (vim-plug, Gruvbox, LSP)
- LSP-серверы
- Плагины и расширения: где и зачем
- Шпаргалка по горячим клавишам
- Типичный DevOps workflow

---

## Установка зависимостей

Установите Homebrew, если ещё не установлен:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Установите нужные инструменты:

```bash
brew install tmux neovim git fzf bat eza node
brew install --cask ghostty font-jetbrains-mono-nerd-font
```

Шрифт **JetBrains Mono Nerd Font** нужен для иконок в prompt и лигатур в коде.

---

## Настройка Ghostty (Gruvbox)

Файл конфигурации:

```
~/.config/ghostty/config
```

Создайте директорию и файл:

```bash
mkdir -p ~/.config/ghostty
nano ~/.config/ghostty/config
```

Пример конфига с темой Gruvbox:

```ini
font-family = JetBrainsMono Nerd Font
font-size = 14

window-padding-x = 6
window-padding-y = 6

background-opacity = 1.0

copy-on-select = false

scrollback-limit = 10000000

cursor-style = block

term = xterm-256color

macos-option-as-alt = true

background = #282828
foreground = #ebdbb2

cursor-color = #ebdbb2

selection-background = #3c3836
selection-foreground = #ebdbb2

palette = 0=#282828
palette = 1=#cc241d
palette = 2=#98971a
palette = 3=#d79921
palette = 4=#458588
palette = 5=#b16286
palette = 6=#689d6a
palette = 7=#a89984
palette = 8=#928374
palette = 9=#fb4934
palette = 10=#b8bb26
palette = 11=#fabd2f
palette = 12=#83a598
palette = 13=#d3869b
palette = 14=#8ec07c
palette = 15=#ebdbb2
```

После сохранения перезапустите Ghostty — тема применится.

---

## Настройка tmux

Файл конфигурации: `~/.tmux.conf`

Пример настроек под Ghostty и 256 цветов:

```conf
set -g mouse on
set -g history-limit 200000

set -g default-terminal "screen-256color"

set -ga terminal-overrides ",xterm-256color:Tc"
set -ga terminal-overrides ",xterm-ghostty:Tc"

set -sg escape-time 0

set -g focus-events on

bind r source-file ~/.tmux.conf \; display "reloaded"
```

Перезагрузить конфиг без выхода из tmux: `Ctrl+b`, затем `r`.

---

## zsh + Oh My Zsh + Powerlevel10k

Установка Oh My Zsh:

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

Установка темы Powerlevel10k:

```bash
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git \
  ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k
```

В `~/.zshrc` укажите тему:

```bash
ZSH_THEME="powerlevel10k/powerlevel10k"
```

После перезапуска терминала запустите настройку внешнего вида:

```bash
p10k configure
```

---

## Настройка Neovim (vim-plug, Gruvbox, LSP)

Создайте конфиг:

```bash
mkdir -p ~/.config/nvim
nano ~/.config/nvim/init.vim
```

Минимальный пример с Gruvbox, LSP и Telescope:

```vim
set number
set relativenumber
set mouse=a
set expandtab
set tabstop=2
set shiftwidth=2
set termguicolors

let mapleader=" "

call plug#begin(stdpath('data') . '/plugged')

Plug 'morhetz/gruvbox'
Plug 'neovim/nvim-lspconfig'
Plug 'hrsh7th/nvim-cmp'
Plug 'hrsh7th/cmp-nvim-lsp'
Plug 'nvim-lua/plenary.nvim'
Plug 'nvim-telescope/telescope.nvim'

call plug#end()

colorscheme gruvbox
```

Установите vim-plug:

```bash
curl -fLo ~/.local/share/nvim/site/autoload/plug.vim --create-dirs \
  https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
```

Установите плагины: откройте Neovim и выполните `:PlugInstall`, или из терминала:

```bash
nvim +PlugInstall +qall
```

---

## LSP-конфигурация (Neovim 0.11+)

В тот же `init.vim` можно добавить блок для LSP (TypeScript и Python):

```vim
lua << EOF
local capabilities = require("cmp_nvim_lsp").default_capabilities()

vim.lsp.config("ts_ls", {
  capabilities = capabilities,
})

vim.lsp.config("pyright", {
  capabilities = capabilities,
})

vim.lsp.enable({
  "ts_ls",
  "pyright",
})
EOF
```

Установите LSP-серверы глобально (или через Mason и т.п.):

```bash
npm install -g typescript typescript-language-server
npm install -g pyright
```

---

## Плагины и расширения: где и зачем

В этой связке плагины есть у **zsh** (Oh My Zsh + темы) и у **Neovim**. Ghostty и tmux работают по конфигу без отдельно подключаемых модулей.

### zsh: Oh My Zsh и Powerlevel10k

| Что | Где используется | Зачем |
|-----|-------------------|--------|
| **Oh My Zsh** | Оболочка zsh | Фреймворк: упрощённая настройка, каталог плагинов и тем, автообновление. |
| **Powerlevel10k** | Тема для Oh My Zsh (`ZSH_THEME`) | Красивый и быстрый prompt: git-статус, время, путь, виртуальные окружения — всё в одной строке без тормозов. |

Остальные утилиты из `brew install` (fzf, bat, eza) — отдельные программы в PATH, не плагины: **fzf** для нечёткого поиска по файлам и истории, **bat** для подсветки вывода в терминале, **eza** как замена `ls`.

### Neovim: плагины (vim-plug)

| Плагин | Назначение |
|--------|------------|
| **vim-plug** | Менеджер плагинов: установка, обновление, загрузка по требованию. Вызывается через `call plug#begin()` / `Plug 'repo/name'` / `call plug#end()`. |
| **morhetz/gruvbox** | Цветовая схема. Тёплые цвета, хорошая читаемость, единый вид с терминалом Ghostty. Включается через `colorscheme gruvbox`. |
| **neovim/nvim-lspconfig** | Конфигурация встроенного LSP-клиента Neovim. Подключает языковые серверы (ts_ls, pyright и др.) без лишнего кода. |
| **hrsh7th/nvim-cmp** | Движок автодополнения: показывает меню с вариантами (из LSP, буфера, путей). Работает вместе с источниками вроде cmp-nvim-lsp. |
| **hrsh7th/cmp-nvim-lsp** | Источник дополнений из LSP. Даёт nvim-cmp подсказки от языкового сервера (методы, переменные, аргументы). |
| **nvim-lua/plenary.nvim** | Библиотека Lua для плагинов: асинхронные функции, утилиты. Нужна Telescope и многим другим плагинам как зависимость. |
| **nvim-telescope/telescope.nvim** | Нечёткий поиск: по файлам, по тексту в проекте, по буферам. В статье привязан к `Space+f` (файлы) и `Space+g` (поиск по тексту). |

Итого: **vim-plug** ставит и грузит плагины, **gruvbox** даёт тему, **nvim-lspconfig** подключает LSP, **nvim-cmp** и **cmp-nvim-lsp** — автодополнение из LSP, **plenary.nvim** — зависимость, **telescope.nvim** — быстрая навигация по файлам и тексту.

---

## Шпаргалка по горячим клавишам

Полная шпаргалка для ежедневной работы в Ghostty + tmux + Neovim.

### Ghostty

**Окна и вкладки**

| Действие | Клавиши |
|----------|---------|
| Новое окно | `Cmd+N` |
| Новая вкладка | `Cmd+T` |
| Закрыть вкладку | `Cmd+W` |
| Следующая вкладка | `Cmd+Shift+]` |
| Предыдущая вкладка | `Cmd+Shift+[` |
| Fullscreen | `Cmd+Ctrl+F` |

**Перемещение окна** (если titlebar скрыт): `Cmd` + перетаскивание мышью.

**Копировать / вставить:** `Cmd+C` / `Cmd+V`.

### tmux

Префикс: **`Ctrl+b`**

**Сессии**

| Действие | Команда / сочетание |
|----------|----------------------|
| Создать сессию | `tmux new -s dev` |
| Список сессий | `tmux ls` |
| Подключиться | `tmux attach -t dev` |
| Отключиться (detach) | `Ctrl+b d` |
| Удалить сессию | `tmux kill-session -t dev` |

**Окна**

| Действие | Клавиши |
|----------|---------|
| Новое окно | `Ctrl+b c` |
| Следующее окно | `Ctrl+b n` |
| Предыдущее окно | `Ctrl+b p` |
| Список окон | `Ctrl+b w` |
| Закрыть окно | `Ctrl+b &` |

**Разбиение панелей (split)**

| Действие | Клавиши |
|----------|---------|
| Вертикальный split | `Ctrl+b %` |
| Горизонтальный split | `Ctrl+b "` |
| Переключение между панелями | `Ctrl+b` + стрелки |

**Изменение размера панелей:** `Ctrl+b Ctrl+←/→/↑/↓`

**Copy mode:** войти — `Ctrl+b [`, выделить — `Space`, скопировать — `Enter`, вставить — `Ctrl+b ]`.

### Neovim

**Режимы:** Normal — `Esc`, Insert — `i`, Visual — `v`, Command — `:`

**Сохранение и выход**

| Действие | Команда |
|----------|---------|
| Сохранить | `:w` |
| Выйти | `:q` |
| Сохранить и выйти | `:wq` |
| Выйти без сохранения | `:q!` |

**Навигация:** вверх `k`, вниз `j`, влево `h`, вправо `l`, начало строки `0`, конец строки `$`, начало файла `gg`, конец файла `G`.

**Редактирование:** удалить строку `dd`, удалить слово `dw`, отмена `u`, повтор `Ctrl+r`, копировать строку `yy`, вставить `p`. Удалить всё: `ggdG`.

**Поиск:** искать `/текст`, следующий результат `n`, предыдущий `N`.

**LSP:** определение `gd`, подсказка (hover) `K`, ссылки `gr`, переименование `Space+rn`, code action `Space+ca`.

**Telescope:** найти файл `Space+f`, поиск текста `Space+g`.

### Пример DevOps workflow

Создать сессию: `tmux new -s dev`. Разбить панель: `Ctrl+b %`. В левой — `nvim .`, в правой — `kubectl logs -f pod/...`. Отключиться: `Ctrl+b d`. Вернуться: `tmux attach -t dev`.

### Самые важные комбинации

**Ghostty:** `Cmd+T`, `Cmd+W`, `Cmd`+перетаскивание.

**tmux:** `Ctrl+b c`, `Ctrl+b %`, `Ctrl+b d`.

**Neovim:** `i`, `Esc`, `:w`, `:q`, `dd`, `gg`, `G`, `gd`, `K`.

---

## Типичный DevOps workflow

Один терминал Ghostty, внутри — одна tmux-сессия, в ней несколько панелей:

```
Ghostty
 └── tmux (сессия dev)
      ├── Neovim — код
      ├── kubectl logs / tail
      ├── terraform / ansible
      └── обычный shell
```

Так можно держать редактор, логи и команды в одном месте и при необходимости отключиться и подключиться снова.

---

## Итог

Стек полностью готов к работе:

- **Ghostty** — быстрый терминал с темой Gruvbox  
- **tmux** — сессии и панели без потери контекста  
- **Neovim** — редактор с LSP и автодополнением  
- **Powerlevel10k** — удобный prompt  
- **Gruvbox** — единая тема во всём окружении  

Если что-то из конфигов захотите разобрать подробнее или адаптировать под себя — напишите в комментариях, можно вынести в отдельные посты.
