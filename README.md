# Avro Tray Indicator (`avro-tray`)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: Linux](https://img.shields.io/badge/Platform-Linux%20(Ubuntu%20%2F%20GNOME)-orange.svg)]()
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)]()

> A lightweight, responsive system tray indicator and fast language switcher for **Avro Keyboard** on modern Linux desktop environments (GNOME, Wayland, X11).

---

## 🌟 Overview

On modern Linux distributions like Ubuntu with GNOME on Wayland, using Avro Keyboard (via `ibus-avro` or `openbangla-keyboard`) often presents two frustrating challenges:
1. **No Visual State Indicator**: Users cannot easily see in the top panel whether they are currently typing in English or Bangla without typing a test character.
2. **Broken or Laggy Shortcut Switching**: The standard Windows Avro hotkey (`F12`) often conflicts with GNOME's built-in window manager switcher overlay, swallowing keypresses or cycling sluggishly.

**`avro-tray`** solves both problems cleanly:
* Displays a **live badge indicator** in the top-right system tray (`[ EN ]` or `[ বাং ]`).
* Enables **instant one-click toggling** via mouse.
* Restores the classic **`F12`** (and **`Ctrl + Space`**) instant toggle hotkey using a sub-millisecond local Unix socket IPC.
* Integrates smoothly with **`systemd --user`** and Ubuntu's AppIndicator system.

---

## 📸 Tray Badges

| Mode | Top-Right Panel Badge | Description |
| :---: | :---: | :--- |
| **English** | `[ EN ]` (Royal Blue) | Standard US English input active. |
| **Bangla** | `[ বাং ]` (Emerald Green + Red Dot) | Avro Phonetic active! Keystrokes produce Bangla characters. |

---

## ✨ Features

* **Real-time Status Sync**: Detects language changes triggered by hotkeys, mouse clicks, or GNOME's native switcher (`Super + Space`) within milliseconds.
* **Instant Mouse Toggle**: Left-click on the tray icon to flip between English and Bangla immediately.
* **Right-Click Menu**:
  * Select languages directly.
  * Switch between typing engines (`ibus-avro` or `OpenBangla Keyboard`).
  * Toggle on-screen notifications ON/OFF.
* **Sub-Millisecond Hotkey Response**: Hotkey commands (`toggle-avro.sh`) communicate with the tray daemon over a Unix domain socket, avoiding process restarts or polling delay.
* **Desktop Notifications**: Optional sleek toast notifications on switch (`🇧🇩 বাংলা (Avro Phonetic)` / `🇺🇸 English (US)`).
* **Zero Sudo Required**: Installs entirely in user space (`~/.local/bin`, `~/.config/systemd/user`).

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have an Avro engine and PyQt5 installed:
```bash
# Install Avro (choose either or both)
sudo apt install ibus-avro

# Install PyQt5 (system or conda/mamba)
sudo apt install python3-pyqt5
# or if using conda / miniforge:
# conda install pyqt
```

### 2. Installation
Clone the repository and run the installer:
```bash
git clone https://github.com/paulshamrat/avro-tray.git
cd avro-tray
./install.sh
```

That's it! The tray icon will appear immediately in your top-right panel.

---

## ⌨️ Shortcuts

The installer automatically configures GNOME media-keys to trigger the fast switcher:
* **`F12`**: Instant English ⇄ Bangla toggle (classic Avro behavior).
* **`Ctrl + Space`**: Alternative fast toggle.
* **`Super + Space`**: Preserved for GNOME's native switcher if needed.

---

## 🛠️ Architecture

```
[ F12 / Ctrl+Space ] ──────> [ toggle-avro.sh ]
                                    │
                         (Unix Domain Socket)
                                    ▼
                          [ avro-tray Daemon ]
                           ├── QSystemTrayIcon (Top-Right Panel)
                           ├── IBus Controller (sets ibus-avro / English)
                           └── notify-send (On-screen toast)
```

---

## 📁 Repository Structure

```
avro-tray/
├── bin/
│   ├── avro-tray             # CLI launcher script
│   └── toggle-avro.sh        # Fast hotkey switcher
├── src/
│   └── avro_tray/
│       ├── __init__.py       # Package metadata
│       ├── icons.py          # Procedural high-DPI badge generator
│       └── main.py           # Application runtime & socket server
├── assets/
│   ├── avro-tray.desktop     # Desktop autostart entry
│   └── avro-tray.service     # Systemd user unit
├── install.sh                # Automated installer
├── uninstall.sh              # Clean uninstaller
├── requirements.txt          # Python dependencies
├── pyproject.toml            # Build metadata
├── LICENSE                   # MIT License
└── README.md                 # Project documentation
```

---

## ⚙️ Management

Check daemon status:
```bash
systemctl --user status avro-tray
```

Restart daemon:
```bash
systemctl --user restart avro-tray
```

View logs:
```bash
journalctl --user -u avro-tray -f
```

---

## 🗑️ Uninstallation

To remove `avro-tray`:
```bash
cd avro-tray
./uninstall.sh
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
