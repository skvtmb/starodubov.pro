---
title: "Ghostty + tmux + Neovim: full environment setup (Gruvbox)"
slug: "ghostty-tmux-nvim-setup"
date: 2025-02-14T12:00:00+03:00
draft: false
summary: "Building a DevOps setup on Ghostty, tmux, zsh, and Neovim with the Gruvbox theme: configs, plugins, hotkeys."
categories: ["Technology"]
tags: ["ghostty", "tmux", "neovim", "gruvbox", "terminal", "development", "setup", "cli", "zsh", "powerlevel10k"]
cover:
  image: "/images/ghostty-tmux-nvim-cover.png"
  alt: "Ghostty + tmux + Neovim environment with Gruvbox theme"
  caption: "Ghostty terminal, tmux multiplexer, and Neovim — one stack for development"
---

I was wiping my laptop again and decided to set everything up properly this time, with all configs in one place. The theme is **Gruvbox**: warm colors, easy on the eyes in the evening. Then I needed a lighter terminal. I'd been on iTerm2 for years, but it got noticeably slow to launch. Switched to **Ghostty** and never looked back.

Here's what I put together.

![Ghostty with tmux and Neovim in dark theme](/images/ghostty-tmux-nvim-cover.png "Ghostty with tmux and Neovim")

## Why this stack

**Ghostty** — cross-platform terminal with GPU acceleration. Starts instantly, ligatures, themes, low input latency. After iTerm2 the difference is obvious.

**tmux** — sessions, windows, panes in one place. Detach, come back later from another machine, everything's still there. Handy for long tasks and several projects at once.

**Neovim** — editor with LSP and completion. Works the same locally and over SSH, which is the deciding factor for me.

**zsh + Oh My Zsh + Powerlevel10k** — shell and an informative prompt without much fuss.

Together: one terminal, one theme, one set of shortcuts. Code in Neovim, logs and commands in adjacent tmux panes.

![Code in dark theme — typical Neovim view](/images/ghostty-tmux-nvim/code-dark.jpg "Code in dark theme")
*Photo: [Luca Bravo](https://unsplash.com/photos/text-DnkogahEs1k) / Unsplash*

## Contents

- Installing dependencies
- Ghostty configuration (Gruvbox)
- tmux configuration
- zsh + Oh My Zsh + Powerlevel10k
- Neovim setup (vim-plug, Gruvbox, LSP)
- LSP servers
- Plugins and extensions: where and why
- Hotkey cheatsheet
- Typical DevOps workflow

---

## Installing dependencies

Install Homebrew if you don't have it:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Install the tools:

```bash
brew install tmux neovim git fzf bat eza node
brew install --cask ghostty font-jetbrains-mono-nerd-font
```

**JetBrains Mono Nerd Font** — for prompt icons and code ligatures.

---

## Ghostty configuration (Gruvbox)

Config file lives here:

```
~/.config/ghostty/config
```

Create the directory and file:

```bash
mkdir -p ~/.config/ghostty
nano ~/.config/ghostty/config
```

My Gruvbox config:

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

Save, restart Ghostty, theme applies.

---

## tmux configuration

The file is `~/.tmux.conf`. Minimum I want for Ghostty and 256 colors:

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

Reload config without leaving tmux: `Ctrl+b`, then `r`.

---

## zsh + Oh My Zsh + Powerlevel10k

Oh My Zsh:

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

Powerlevel10k theme:

```bash
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git \
  ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k
```

In `~/.zshrc`:

```bash
ZSH_THEME="powerlevel10k/powerlevel10k"
```

After restarting the terminal — run the prompt configurator:

```bash
p10k configure
```

---

## Neovim setup (vim-plug, Gruvbox, LSP)

Config:

```bash
mkdir -p ~/.config/nvim
nano ~/.config/nvim/init.vim
```

Minimum with Gruvbox, LSP, and Telescope:

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

Install vim-plug itself:

```bash
curl -fLo ~/.local/share/nvim/site/autoload/plug.vim --create-dirs \
  https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
```

Plugins go in via `:PlugInstall` inside Neovim, or one-shot from the terminal:

```bash
nvim +PlugInstall +qall
```

---

## LSP configuration (Neovim 0.11+)

Add this to the same `init.vim` (I run TypeScript and Python):

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

I install LSP servers globally, no Mason:

```bash
npm install -g typescript typescript-language-server
npm install -g pyright
```

---

## Plugins and extensions: where and why

Plugins live only in **zsh** (Oh My Zsh + themes) and **Neovim**. Ghostty and tmux get by on config alone.

### zsh: Oh My Zsh and Powerlevel10k

| What | Where used | Why |
|------|-------------|-----|
| **Oh My Zsh** | zsh shell | Framework: easy config, plugin/theme catalog, auto-updates. |
| **Powerlevel10k** | Oh My Zsh theme (`ZSH_THEME`) | Fast, informative prompt: git status, time, path, venvs — all in one line. |

The other tools from `brew install` (fzf, bat, eza) are just binaries in PATH, not plugins. fzf — fuzzy search over files and history, bat — syntax-highlighted output, eza — `ls` replacement.

### Neovim: plugins (vim-plug)

| Plugin | Purpose |
|--------|---------|
| **vim-plug** | Plugin manager: install, update, lazy-load. Used via `call plug#begin()` / `Plug 'repo/name'` / `call plug#end()`. |
| **morhetz/gruvbox** | Color scheme. Warm colors, good readability, matches Ghostty terminal. Enable with `colorscheme gruvbox`. |
| **neovim/nvim-lspconfig** | Config for Neovim’s built-in LSP client. Connects language servers (ts_ls, pyright, etc.) with minimal code. |
| **hrsh7th/nvim-cmp** | Completion engine: shows a menu of suggestions (from LSP, buffer, file paths). Works with sources like cmp-nvim-lsp. |
| **hrsh7th/cmp-nvim-lsp** | LSP completion source for nvim-cmp. Feeds methods, variables, arguments from the language server. |
| **nvim-lua/plenary.nvim** | Lua library for plugins: async helpers, utilities. Required by Telescope and many other plugins. |
| **nvim-telescope/telescope.nvim** | Fuzzy finder: files, text in project, buffers. In this article bound to `Space+f` (files) and `Space+g` (text search). |

Short version: vim-plug installs, gruvbox colors, nvim-lspconfig + nvim-cmp + cmp-nvim-lsp give LSP completion, telescope.nvim (via plenary) handles file and text search.

---

## Hotkey cheatsheet

What I actually use day-to-day.

### Ghostty

**Windows and tabs**

| Action | Keys |
|--------|------|
| New window | `Cmd+N` |
| New tab | `Cmd+T` |
| Close tab | `Cmd+W` |
| Next tab | `Cmd+Shift+]` |
| Previous tab | `Cmd+Shift+[` |
| Fullscreen | `Cmd+Ctrl+F` |

**Move window** (when titlebar is hidden): `Cmd` + drag with mouse.

**Copy / paste:** `Cmd+C` / `Cmd+V`.

### tmux

Prefix: **`Ctrl+b`**

**Sessions**

| Action | Command / shortcut |
|--------|---------------------|
| Create session | `tmux new -s dev` |
| List sessions | `tmux ls` |
| Attach | `tmux attach -t dev` |
| Detach | `Ctrl+b d` |
| Kill session | `tmux kill-session -t dev` |

**Windows**

| Action | Keys |
|--------|------|
| New window | `Ctrl+b c` |
| Next window | `Ctrl+b n` |
| Previous window | `Ctrl+b p` |
| List windows | `Ctrl+b w` |
| Close window | `Ctrl+b &` |

**Split panes**

| Action | Keys |
|--------|------|
| Vertical split | `Ctrl+b %` |
| Horizontal split | `Ctrl+b "` |
| Switch panes | `Ctrl+b` + arrow keys |

**Resize panes:** `Ctrl+b Ctrl+←/→/↑/↓`

**Copy mode:** enter — `Ctrl+b [`, select — `Space`, copy — `Enter`, paste — `Ctrl+b ]`.

### Neovim

**Modes:** Normal — `Esc`, Insert — `i`, Visual — `v`, Command — `:`

**Save and quit**

| Action | Command |
|--------|---------|
| Save | `:w` |
| Quit | `:q` |
| Save and quit | `:wq` |
| Quit without saving | `:q!` |

**Navigation:** up `k`, down `j`, left `h`, right `l`, line start `0`, line end `$`, file start `gg`, file end `G`.

**Editing:** delete line `dd`, delete word `dw`, undo `u`, redo `Ctrl+r`, yank line `yy`, paste `p`. Delete all: `ggdG`.

**Search:** search `/text`, next `n`, previous `N`.

**LSP:** go to definition `gd`, hover `K`, references `gr`, rename `Space+rn`, code action `Space+ca`.

**Telescope:** find file `Space+f`, search text `Space+g`.

### Example DevOps workflow

Create session: `tmux new -s dev`. Split: `Ctrl+b %`. Left pane: `nvim .`, right pane: `kubectl logs -f pod/...`. Detach: `Ctrl+b d`. Reattach: `tmux attach -t dev`.

### Most important shortcuts

**Ghostty:** `Cmd+T`, `Cmd+W`, `Cmd`+drag.

**tmux:** `Ctrl+b c`, `Ctrl+b %`, `Ctrl+b d`.

**Neovim:** `i`, `Esc`, `:w`, `:q`, `dd`, `gg`, `G`, `gd`, `K`.

---

## Typical DevOps workflow

One Ghostty, one tmux session, several panes inside:

```
Ghostty
 └── tmux (session dev)
      ├── Neovim — code
      ├── kubectl logs / tail
      ├── terraform / ansible
      └── shell
```

Editor, logs, commands in one window. Detach and reattach when you need to.

---

## Summary

What I ended up with:

- Ghostty — fast terminal, Gruvbox
- tmux — sessions and panes without losing context
- Neovim — editor with LSP and completion
- Powerlevel10k — prompt without much fuss

If you want me to dig deeper into any of these configs, leave a comment.
