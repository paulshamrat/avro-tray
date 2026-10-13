#!/usr/bin/env bash
# ==============================================================================
# Avro Tray Indicator & Fast Switcher - Uninstaller
# ==============================================================================

echo "==> Uninstalling Avro Tray Indicator..."

# 1. Stop and disable systemd service
systemctl --user stop avro-tray.service 2>/dev/null || true
systemctl --user disable avro-tray.service 2>/dev/null || true
rm -f "${HOME}/.config/systemd/user/avro-tray.service"
systemctl --user daemon-reload 2>/dev/null || true

# 2. Remove desktop files
rm -f "${HOME}/.config/autostart/avro-tray.desktop"
rm -f "${HOME}/.local/share/applications/avro-tray.desktop"

# 3. Remove binary symlinks
rm -f "${HOME}/.local/bin/avro-tray"
rm -f "${HOME}/.local/bin/toggle-avro.sh"

# 4. Remove socket and lock if present
rm -f "/tmp/avro-tray-${EUID}.sock"
rm -f "/tmp/avro-tray-${EUID}.lock"

echo "==> Avro Tray Indicator removed successfully."
