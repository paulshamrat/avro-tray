#!/usr/bin/env bash
set -e

# ==============================================================================
# Avro Tray Indicator & Fast Switcher - Installer
# ==============================================================================

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${HOME}/.local/bin"
AUTOSTART_DIR="${HOME}/.config/autostart"
APPS_DIR="${HOME}/.local/share/applications"
SYSTEMD_USER_DIR="${HOME}/.config/systemd/user"

echo "==> Installing Avro Tray Indicator..."

# 1. Create target directories
mkdir -p "${BIN_DIR}" "${AUTOSTART_DIR}" "${APPS_DIR}" "${SYSTEMD_USER_DIR}"

# 2. Make scripts executable
chmod +x "${REPO_DIR}/bin/avro-tray"
chmod +x "${REPO_DIR}/bin/toggle-avro.sh"

# 3. Symlink binaries to ~/.local/bin
echo "==> Linking binaries into ${BIN_DIR}..."
ln -sf "${REPO_DIR}/bin/avro-tray" "${BIN_DIR}/avro-tray"
ln -sf "${REPO_DIR}/bin/toggle-avro.sh" "${BIN_DIR}/toggle-avro.sh"

# 4. Install Desktop Entries
echo "==> Installing desktop shortcuts..."
cp "${REPO_DIR}/assets/avro-tray.desktop" "${AUTOSTART_DIR}/avro-tray.desktop"
cp "${REPO_DIR}/assets/avro-tray.desktop" "${APPS_DIR}/avro-tray.desktop"

# 5. Install Systemd Service
echo "==> Setting up systemd user service..."
cp "${REPO_DIR}/assets/avro-tray.service" "${SYSTEMD_USER_DIR}/avro-tray.service"

# 6. Configure GNOME Shortcuts
echo "==> Configuring GNOME Shortcuts (F12 and Ctrl+Space)..."
# Clean up switch-input-source so it doesn't swallow F12
gsettings set org.gnome.desktop.wm.keybindings switch-input-source "['<Super>space']" 2>/dev/null || true

# Add custom keybindings for F12 and Ctrl+Space
CUSTOM_BASE="/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings"
CUSTOM0="${CUSTOM_BASE}/custom0/"
CUSTOM1="${CUSTOM_BASE}/custom1/"

gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "['${CUSTOM0}', '${CUSTOM1}']" 2>/dev/null || true

gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:${CUSTOM0} name "Toggle Avro (F12)" 2>/dev/null || true
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:${CUSTOM0} command "${BIN_DIR}/toggle-avro.sh" 2>/dev/null || true
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:${CUSTOM0} binding "F12" 2>/dev/null || true

gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:${CUSTOM1} name "Toggle Avro (Ctrl+Space)" 2>/dev/null || true
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:${CUSTOM1} command "${BIN_DIR}/toggle-avro.sh" 2>/dev/null || true
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:${CUSTOM1} binding "<Control>space" 2>/dev/null || true

# 7. Enable and Start Background Service
echo "==> Starting Avro Tray background service..."
systemctl --user daemon-reload 2>/dev/null || true
systemctl --user enable avro-tray.service 2>/dev/null || true
systemctl --user restart avro-tray.service 2>/dev/null || true

echo ""
echo "======================================================================"
echo " ✅ Avro Tray Indicator installed and activated successfully!"
echo "    - Look at the top-right corner of your top bar for the tray icon."
echo "    - Press F12 or Ctrl+Space anytime to toggle."
echo "======================================================================"
