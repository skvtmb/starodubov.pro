---
title: "macOS defaults: System Tuning with defaults write"
date: 2025-02-15T12:00:00+03:00
draft: false
summary: "Examples of macOS settings via defaults write: Finder, Dock, screenshots, keyboard, trackpad, and Mission Control. Ready-to-run script included."
categories: ["Technology"]
tags: ["macos", "defaults", "finder", "dock", "setup", "script", "terminal", "trackpad", "keyboard"]
---

Many macOS settings are not exposed in System Settings but can be changed with the **`defaults write`** command in the terminal. That’s handy when moving to a new Mac or automating setup: one script and Finder, Dock, screenshots, and keyboard behave the way you want.

This post is a ready-made script with short explanations of what each option does. Full reference: [macos-defaults.com](https://macos-defaults.com/).

## Contents

- Finder
- Dock
- Screenshots
- Keyboard and global settings
- Trackpad
- Mission Control
- Miscellaneous
- How to apply

---

## Finder

- **Hidden files** — show dotfiles and system files.
- **File extensions** — show suffix (e.g. `.md`, `.png`).
- **Path bar** — show path at the bottom of the Finder window.
- **Status bar** — show item count and free space.
- **Folders on top** — when sorting, folders appear above files.
- **Default view** — `Nlsv` (list), `icnv` (icons), `clmv` (columns).
- **Extension change warning** — warn when renaming and changing extension.

```bash
# Show hidden files
defaults write com.apple.finder AppleShowAllFiles -bool true

# Show file extensions
defaults write com.apple.finder AppleShowAllExtensions -bool true

# Show path bar at bottom of Finder window
defaults write com.apple.finder ShowPathbar -bool true

# Show status bar
defaults write com.apple.finder ShowStatusBar -bool true

# Folders first when sorting
defaults write com.apple.finder _FXSortFoldersFirst -bool true

# Default view style: Nlsv=List, icnv=Icon, clmv=Column
defaults write com.apple.finder FXPreferredViewStyle -string "Nlsv"

# Warn when changing file extension
defaults write com.apple.finder FXEnableExtensionChangeWarning -bool true
```

---

## Dock

- **Auto-hide** — Dock hides off-screen and shows on hover.
- **Delay** — `0` means no delay when showing/hiding.
- **Icon size** — in pixels (e.g. 36).
- **Position** — `left`, `bottom`, or `right`.
- **Minimize effect** — `genie` or `scale`.
- **Process indicators** — dot under open apps.
- **Recents** — turn off the “Recent” section in the Dock.

```bash
# Auto-hide Dock
defaults write com.apple.dock autohide -bool true

# No delay when auto-hiding (0 = instant)
defaults write com.apple.dock autohide-delay -float 0

# Dock icon size
defaults write com.apple.dock tilesize -int 36

# Position: left | bottom | right
defaults write com.apple.dock orientation -string "bottom"

# Minimize effect: genie | scale
defaults write com.apple.dock mineffect -string "genie"

# Show open application indicators
defaults write com.apple.dock show-process-indicators -bool true

# Don’t show recent applications
defaults write com.apple.dock show-recents -bool false
```

---

## Screenshots

- **Format** — `png`, `jpg`, or `pdf`.
- **Location** — where to save screenshots (e.g. a folder on the Desktop).
- **Window shadow** — disable shadow around the window in screenshots.
- **Thumbnail** — show preview in corner before saving (can be disabled).

```bash
# Format: png | jpg | pdf
defaults write com.apple.screencapture type -string "png"

# Screenshot folder
defaults write com.apple.screencapture location -string "${HOME}/Desktop/screenshots"

# No window shadow
defaults write com.apple.screencapture disable-shadow -bool true

# Show thumbnail
defaults write com.apple.screencapture show-thumbnail -bool false
```

Create the folder if it doesn’t exist: `mkdir -p ~/Desktop/screenshots`.

---

## Keyboard and global settings (NSGlobalDomain)

- **KeyRepeat** — repeat rate when holding a key (lower = faster). Typical values 1–2 for fast repeat.
- **InitialKeyRepeat** — delay before repeat starts, in milliseconds (15 = short delay).
- **Smart quotes and dashes** — turn off auto-replacement of “quotes” and — dashes.
- **Period on double space** — turn off automatic period after double space.

```bash
# Key repeat speed (2 = very fast)
defaults write -g KeyRepeat -int 2

# Delay until repeat (milliseconds)
defaults write -g InitialKeyRepeat -int 15

# Disable “smart” quotes and dashes
defaults write -g NSAutomaticQuoteSubstitutionEnabled -bool false
defaults write -g NSAutomaticDashSubstitutionEnabled -bool false

# Period on double space
defaults write -g NSAutomaticPeriodSubstitutionEnabled -bool false
```

---

## Trackpad

**Three-finger drag** — drag windows or selected text with three fingers without enabling “Drag Lock”. Handy if you prefer not to “click and drag”.

```bash
# Three-finger drag (no drag lock)
defaults write com.apple.driver.AppleBluetoothMultitouch.trackpad TrackpadThreeFingerDrag -bool true
defaults write com.apple.AppleMultitouchTrackpad TrackpadThreeFingerDrag -bool true
```

---

## Mission Control

- **Group by application** — in Mission Control, windows are grouped by app.
- **Don’t switch Space** — when activating an app, don’t switch to the Space where its window is open.

```bash
# Group windows by application
defaults write com.apple.dock expose-group-by-app -bool true

# Don’t switch to Space with open window
defaults write com.apple.dock AppleSpacesSwitchOnActivate -bool false
```

---

## Miscellaneous

- **Restore windows on quit** — `false` means don’t restore windows on next launch (classic behavior).
- **Quarantine downloaded apps** — disabled in the script (commented out): without quarantine macOS won’t warn about unverified apps (use with care).
- **Animations** — commented examples for turning off animations to speed up the UI.

```bash
# Restore windows when quitting application
defaults write -g NSQuitAlwaysKeepsWindows -bool false

# Disable quarantine for downloaded apps (use with care!)
# defaults write com.apple.LaunchServices LSQuarantine -bool false

# Disable animations (for faster UI)
# defaults write -g NSAutomaticWindowAnimationsEnabled -bool false
# defaults write -g NSWindowResizeTime -float 0.001
```

---

## Full script and how to apply

The script below combines all the settings above. Run: `./macos-defaults-examples.sh` (make it executable first: `chmod +x macos-defaults-examples.sh`). Or copy the blocks you need into your own script.

```bash
#!/usr/bin/env bash
# macOS defaults — example settings
# Run: ./macos-defaults-examples.sh
# Or copy the commands you need into your script.
# Reference: https://macos-defaults.com/

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

# === Screenshots ===
defaults write com.apple.screencapture type -string "png"
defaults write com.apple.screencapture location -string "${HOME}/Desktop/screenshots"
defaults write com.apple.screencapture disable-shadow -bool true
defaults write com.apple.screencapture show-thumbnail -bool false

# === Global (NSGlobalDomain) ===
defaults write -g KeyRepeat -int 2
defaults write -g InitialKeyRepeat -int 15
defaults write -g NSAutomaticQuoteSubstitutionEnabled -bool false
defaults write -g NSAutomaticDashSubstitutionEnabled -bool false
defaults write -g NSAutomaticPeriodSubstitutionEnabled -bool false

# === Trackpad ===
defaults write com.apple.driver.AppleBluetoothMultitouch.trackpad TrackpadThreeFingerDrag -bool true
defaults write com.apple.AppleMultitouchTrackpad TrackpadThreeFingerDrag -bool true

# === Mission Control ===
defaults write com.apple.dock expose-group-by-app -bool true
defaults write com.apple.dock AppleSpacesSwitchOnActivate -bool false

# === Miscellaneous ===
defaults write -g NSQuitAlwaysKeepsWindows -bool false

echo "Done. Restart Finder and Dock: killall Finder Dock"
```

After running the script, restart Finder and Dock so changes take effect:

```bash
killall Finder Dock
```

Some options (e.g. trackpad) may require logging out or rebooting. Full reference for keys and values: [macos-defaults.com](https://macos-defaults.com/).
