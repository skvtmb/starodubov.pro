---
title: "macOS defaults: настройка системы через defaults write"
date: 2025-02-15T12:00:00+03:00
draft: false
summary: "Примеры настроек macOS через команды defaults write: Finder, Dock, скриншоты, клавиатура, трекпад и Mission Control. Готовый скрипт для применения."
categories: ["Технологии"]
tags: ["macos", "defaults", "finder", "dock", "настройка", "скрипт", "терминал", "трекпад", "клавиатура"]
---

Многие настройки macOS недоступны через стандартный интерфейс «Системные настройки», но их можно изменить через команду **`defaults write`** в терминале. Это удобно при переносе окружения на новый Mac или при автоматизации настройки: один скрипт — и Finder, Dock, скриншоты и клавиатура ведут себя так, как нужно.

В этой статье — готовый скрипт с примерами и кратким пояснением, что за что отвечает. Справка по ключам: [macos-defaults.com](https://macos-defaults.com/).

## Содержание

- Finder
- Dock
- Скриншоты
- Клавиатура и глобальные настройки
- Трекпад
- Mission Control
- Разное
- Как применить

---

## Finder

- **Скрытые файлы** — показывать точки и служебные файлы.
- **Расширения файлов** — видеть суффикс (например, `.md`, `.png`).
- **Путь внизу окна** — строка пути внизу окна Finder.
- **Статус-бар** — количество элементов и свободное место.
- **Папки сверху** — при сортировке папки выше файлов.
- **Вид по умолчанию** — `Nlsv` (список), `icnv` (иконки), `clmv` (колонки).
- **Предупреждение при смене расширения** — защита от случайного переименования.

```bash
# Показывать скрытые файлы
defaults write com.apple.finder AppleShowAllFiles -bool true

# Показывать расширения файлов
defaults write com.apple.finder AppleShowAllExtensions -bool true

# Показывать путь внизу окна Finder
defaults write com.apple.finder ShowPathbar -bool true

# Показывать статус-бар
defaults write com.apple.finder ShowStatusBar -bool true

# Папки сверху при сортировке
defaults write com.apple.finder _FXSortFoldersFirst -bool true

# Стиль вида по умолчанию: Nlsv=List, icnv=Icon, clmv=Column
defaults write com.apple.finder FXPreferredViewStyle -string "Nlsv"

# Предупреждение при смене расширения
defaults write com.apple.finder FXEnableExtensionChangeWarning -bool true
```

---

## Dock

- **Автоскрытие** — Dock уезжает за край экрана и появляется при наведении.
- **Задержка** — `0` значит без задержки при появлении/скрытии.
- **Размер иконок** — в пикселях (например, 36).
- **Позиция** — `left`, `bottom` или `right`.
- **Эффект сворачивания** — `genie` или `scale`.
- **Индикатор открытых приложений** — точка под иконкой.
- **Недавние приложения** — отключение вкладки «Недавние» в Dock.

```bash
# Автоскрытие Dock
defaults write com.apple.dock autohide -bool true

# Убрать задержку при автоскрытии (0 = мгновенно)
defaults write com.apple.dock autohide-delay -float 0

# Размер иконок Dock
defaults write com.apple.dock tilesize -int 36

# Позиция: left | bottom | right
defaults write com.apple.dock orientation -string "bottom"

# Эффект сворачивания: genie | scale
defaults write com.apple.dock mineffect -string "genie"

# Показывать индикатор открытых приложений
defaults write com.apple.dock show-process-indicators -bool true

# Не показывать недавние приложения
defaults write com.apple.dock show-recents -bool false
```

---

## Скриншоты

- **Формат** — `png`, `jpg` или `pdf`.
- **Папка** — куда сохранять снимки экрана (например, отдельная папка на рабочем столе).
- **Тень у окон** — отключение тени вокруг окна на скриншоте.
- **Миниатюра** — показывать превью в углу перед сохранением (можно отключить).

```bash
# Формат: png | jpg | pdf
defaults write com.apple.screencapture type -string "png"

# Папка для скриншотов
defaults write com.apple.screencapture location -string "${HOME}/Desktop/screenshots"

# Без тени у окон
defaults write com.apple.screencapture disable-shadow -bool true

# Показывать миниатюру
defaults write com.apple.screencapture show-thumbnail -bool false
```

Не забудьте создать папку, если её нет: `mkdir -p ~/Desktop/screenshots`.

---

## Клавиатура и глобальные настройки (NSGlobalDomain)

- **KeyRepeat** — скорость повтора при удержании клавиши (меньше значение — быстрее повтор). Типичные значения 1–2 для быстрого повтора.
- **InitialKeyRepeat** — задержка до начала повтора в миллисекундах (15 — короткая задержка).
- **Умные кавычки и тире** — отключение автозамены «кавычек» и — тире.
- **Точка по двойному пробелу** — отключение автоматической точки после двойного пробела.

```bash
# Скорость повтора клавиш (в миллисекундах, 2 = очень быстро)
defaults write -g KeyRepeat -int 2

# Задержка до повтора (в миллисекундах)
defaults write -g InitialKeyRepeat -int 15

# Отключить «умные» кавычки и тире
defaults write -g NSAutomaticQuoteSubstitutionEnabled -bool false
defaults write -g NSAutomaticDashSubstitutionEnabled -bool false

# Точка по двойному пробелу
defaults write -g NSAutomaticPeriodSubstitutionEnabled -bool false
```

---

## Трекпад

**Трёхпальцевое перетаскивание** — перетаскивание окна или выделенного текста тремя пальцами без включения «Блокировка перетаскивания». Удобно для тех, кто не любит «нажимать и тянуть».

```bash
# Трёхпальцевое перетаскивание (без drag lock)
defaults write com.apple.driver.AppleBluetoothMultitouch.trackpad TrackpadThreeFingerDrag -bool true
defaults write com.apple.AppleMultitouchTrackpad TrackpadThreeFingerDrag -bool true
```

---

## Mission Control

- **Группировать по приложению** — в Mission Control окна сгруппированы по приложениям.
- **Не переключаться на Space** — при активации приложения не переключать рабочий стол на тот, где открыто его окно.

```bash
# Группировать окна по приложению
defaults write com.apple.dock expose-group-by-app -bool true

# Не переключаться на Space с открытым окном
defaults write com.apple.dock AppleSpacesSwitchOnActivate -bool false
```

---

## Разное

- **Сохранять окна при выходе** — `false` означает не восстанавливать окна при следующем запуске приложения (классическое поведение).
- **Карантин скачанных приложений** — отключение закомментировано: без карантина macOS не будет предупреждать о непроверенных приложениях (использовать осторожно).
- **Анимации** — закомментированы примеры отключения анимаций для ускорения интерфейса.

```bash
# Сохранять окна при выходе из приложения
defaults write -g NSQuitAlwaysKeepsWindows -bool false

# Отключить карантин для скачанных приложений (осторожно!)
# defaults write com.apple.LaunchServices LSQuarantine -bool false

# Отключить анимации (для ускорения)
# defaults write -g NSAutomaticWindowAnimationsEnabled -bool false
# defaults write -g NSWindowResizeTime -float 0.001
```

---

## Полный скрипт и применение

Скрипт ниже объединяет все приведённые настройки. Запуск: `./macos-defaults-examples.sh` (файл должен быть исполняемым: `chmod +x macos-defaults-examples.sh`). Или копируйте нужные блоки в свой скрипт.

```bash
#!/usr/bin/env bash
# macOS defaults — примеры настроек
# Запуск: ./macos-defaults-examples.sh
# Или копируйте нужные команды в свой скрипт.
# Справка: https://macos-defaults.com/

set -e

echo "Applying macOS defaults (examples)..."

# === Finder ===
defaults write com.apple.finder AppleShowAllFiles -bool true
defaults write com.apple.finder AppleShowAllExtensions -bool true
defaults write com.apple.finder ShowPathbar -bool true
defaults write com.apple.finder ShowStatusBar -bool true
defaults write com.apple.finder _FXSortFoldersFirst -bool true
defaults write com.apple.finder FXPreferredViewStyle -string "Nlsv"
defaults write com.apple.finder FXEnableExtensionChangeWarning -bool true

# === Dock ===
defaults write com.apple.dock autohide -bool true
defaults write com.apple.dock autohide-delay -float 0
defaults write com.apple.dock tilesize -int 36
defaults write com.apple.dock orientation -string "bottom"
defaults write com.apple.dock mineffect -string "genie"
defaults write com.apple.dock show-process-indicators -bool true
defaults write com.apple.dock show-recents -bool false

# === Скриншоты ===
defaults write com.apple.screencapture type -string "png"
defaults write com.apple.screencapture location -string "${HOME}/Desktop/screenshots"
defaults write com.apple.screencapture disable-shadow -bool true
defaults write com.apple.screencapture show-thumbnail -bool false

# === Глобальные настройки (NSGlobalDomain) ===
defaults write -g KeyRepeat -int 2
defaults write -g InitialKeyRepeat -int 15
defaults write -g NSAutomaticQuoteSubstitutionEnabled -bool false
defaults write -g NSAutomaticDashSubstitutionEnabled -bool false
defaults write -g NSAutomaticPeriodSubstitutionEnabled -bool false

# === Трекпад ===
defaults write com.apple.driver.AppleBluetoothMultitouch.trackpad TrackpadThreeFingerDrag -bool true
defaults write com.apple.AppleMultitouchTrackpad TrackpadThreeFingerDrag -bool true

# === Mission Control ===
defaults write com.apple.dock expose-group-by-app -bool true
defaults write com.apple.dock AppleSpacesSwitchOnActivate -bool false

# === Разное ===
defaults write -g NSQuitAlwaysKeepsWindows -bool false

echo "Done. Restart Finder and Dock: killall Finder Dock"
```

После применения перезапустите Finder и Dock, чтобы изменения вступили в силу:

```bash
killall Finder Dock
```

Часть настроек (например, трекпад) может потребовать выхода из учётной записи или перезагрузки. Полный справочник по ключам и возможным значениям — на [macos-defaults.com](https://macos-defaults.com/).
