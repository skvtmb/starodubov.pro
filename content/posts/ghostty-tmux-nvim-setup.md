---
title: "Ghostty + tmux + Neovim: полная настройка окружения (Gruvbox)"
date: 2025-02-14T12:00:00+03:00
draft: false
summary: "Как я собрал DevOps-окружение на Ghostty, tmux, zsh и Neovim с темой Gruvbox: конфиги, плагины, шорткаты."
categories: ["Технологии"]
tags: ["ghostty", "tmux", "neovim", "gruvbox", "терминал", "разработка", "настройка", "cli", "zsh", "powerlevel10k"]
cover:
  image: "/images/ghostty-tmux-nvim-cover.png"
  alt: "Окружение Ghostty + tmux + Neovim с темой Gruvbox"
  caption: "Терминал Ghostty, мультиплексор tmux и редактор Neovim — единая связка для разработки"
---

Сбрасывал в очередной раз ноутбук и решил наконец-то собрать рабочее окружение по-человечески, чтобы конфиги лежали в одном месте и я больше не вспоминал, что куда. Тема — **Gruvbox**, мне нравятся её тёплые цвета, глаза не устают вечером. Дальше понадобился терминал полегче: на iTerm2 я сидел давно, но он стал заметно тормозить при запуске. Поставил **Ghostty** — и больше не возвращался.

Ниже — что собрал и как настроил.

![Окружение Ghostty с tmux и Neovim в тёмной теме](/images/ghostty-tmux-nvim-cover.png "Окружение Ghostty с tmux и Neovim")

## Зачем эта связка

**Ghostty** — кроссплатформенный терминал с GPU-ускорением. Запускается мгновенно, лигатуры, темы, минимальная задержка ввода. После iTerm2 разница в отзывчивости заметна сразу.

**tmux** — сессии, окна и панели в одном месте. Отключился, подключился потом с другой машины — всё на месте. Для долгих задач и нескольких проектов одновременно.

**Neovim** — редактор с LSP и автодополнением. Локально и по SSH работает одинаково, для меня это решающее.

**zsh + Oh My Zsh + Powerlevel10k** — оболочка и информативный prompt без долгой возни.

Вместе это одно окружение: один терминал, одна тема, одни шорткаты. Код в Neovim, логи и команды в соседних панелях tmux.

![Код в тёмной теме — типичный вид при работе в Neovim](/images/ghostty-tmux-nvim/code-dark.jpg "Код в тёмной теме")
*Фото: [Luca Bravo](https://unsplash.com/photos/text-DnkogahEs1k) / Unsplash*

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

Если Homebrew ещё нет — ставим:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Дальше — нужный софт:

```bash
brew install tmux neovim git fzf bat eza node
brew install --cask ghostty font-jetbrains-mono-nerd-font
```

**JetBrains Mono Nerd Font** — для иконок в prompt и лигатур в коде.

---

## Настройка Ghostty (Gruvbox)

Файл конфигурации лежит здесь:

```
~/.config/ghostty/config
```

Создаём директорию и файл:

```bash
mkdir -p ~/.config/ghostty
nano ~/.config/ghostty/config
```

Мой конфиг с темой Gruvbox:

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

Сохранили, перезапустили Ghostty — тема на месте.

---

## Настройка tmux

Файл `~/.tmux.conf`. Минимум, который мне нужен под Ghostty и 256 цветов:

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

Перезагрузить конфиг, не выходя из tmux: `Ctrl+b`, затем `r`.

---

## zsh + Oh My Zsh + Powerlevel10k

Ставим Oh My Zsh:

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

Тема Powerlevel10k:

```bash
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git \
  ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k
```

В `~/.zshrc`:

```bash
ZSH_THEME="powerlevel10k/powerlevel10k"
```

После перезапуска терминала — настройка внешнего вида:

```bash
p10k configure
```

---

## Настройка Neovim (vim-plug, Gruvbox, LSP)

Конфиг:

```bash
mkdir -p ~/.config/nvim
nano ~/.config/nvim/init.vim
```

Минимум с Gruvbox, LSP и Telescope:

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

Ставим vim-plug:

```bash
curl -fLo ~/.local/share/nvim/site/autoload/plug.vim --create-dirs \
  https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
```

Плагины ставятся через `:PlugInstall` в Neovim или одной командой:

```bash
nvim +PlugInstall +qall
```

---

## LSP-конфигурация (Neovim 0.11+)

В тот же `init.vim` добавляем блок для LSP (у меня TypeScript и Python):

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

LSP-серверы я ставлю глобально, без Mason:

```bash
npm install -g typescript typescript-language-server
npm install -g pyright
```

---

## Плагины и расширения: где и зачем

Плагины тут только у **zsh** (Oh My Zsh + темы) и **Neovim**. Ghostty и tmux обходятся конфигом.

### zsh: Oh My Zsh и Powerlevel10k

| Что | Где используется | Зачем |
|-----|-------------------|--------|
| **Oh My Zsh** | Оболочка zsh | Фреймворк: упрощённая настройка, каталог плагинов и тем, автообновление. |
| **Powerlevel10k** | Тема для Oh My Zsh (`ZSH_THEME`) | Красивый и быстрый prompt: git-статус, время, путь, виртуальные окружения — всё в одной строке без тормозов. |

Остальные утилиты из `brew install` (fzf, bat, eza) — это просто программы в PATH, не плагины. fzf — нечёткий поиск по файлам и истории, bat — подсветка вывода, eza — замена `ls`.

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

Если коротко: vim-plug ставит, gruvbox раскрашивает, nvim-lspconfig + nvim-cmp + cmp-nvim-lsp дают автодополнение из LSP, telescope.nvim (через plenary) — поиск по файлам и тексту.

---

## Шпаргалка по горячим клавишам

То, чем я реально пользуюсь каждый день.

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

Один Ghostty, внутри одна tmux-сессия с панелями:

```
Ghostty
 └── tmux (сессия dev)
      ├── Neovim — код
      ├── kubectl logs / tail
      ├── terraform / ansible
      └── обычный shell
```

Редактор, логи и команды в одном окне, можно отключиться и вернуться позже без потерь.

---

## Итог

Что получилось:

- Ghostty — быстрый терминал, Gruvbox
- tmux — сессии и панели без потери контекста
- Neovim — редактор с LSP и автодополнением
- Powerlevel10k — prompt без долгой настройки

Если по конфигам есть вопросы или хочется разобрать что-то отдельно — пишите в комментариях.
