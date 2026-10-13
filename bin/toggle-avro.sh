#!/usr/bin/env bash
# Fast Avro Bangla / English Toggle Script
# Bound to F12 and Ctrl+Space

SOCKET="/tmp/avro-tray-${EUID}.sock"

# 1. If avro-tray is running, tell it to toggle instantly via Unix socket
if [ -S "$SOCKET" ]; then
    /usr/bin/python3 -c "
import socket, sys
try:
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(0.3)
    s.connect('$SOCKET')
    s.sendall(b'TOGGLE\n')
    s.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null && exit 0
fi

# 2. Fallback if avro-tray socket is not responding:
current=$(ibus engine 2>/dev/null || echo "")

case "$current" in
    *avro*|*Avro*|*OpenBangla*|*bangla*|*Bangla*|*bn*)
        ibus engine xkb:us::eng
        notify-send -t 1000 -a "Avro Switcher" "🇺🇸 English (US)" "Keyboard set to English"
        ;;
    *)
        if ibus list-engine 2>/dev/null | grep -q "ibus-avro"; then
            ibus engine ibus-avro
        else
            ibus engine OpenBangla
        fi
        notify-send -t 1000 -a "Avro Switcher" "🇧🇩 বাংলা (Avro Phonetic)" "Keyboard set to বাংলা"
        ;;
esac

# Auto-start avro-tray if not already running
if ! pgrep -f "avro_tray" >/dev/null; then
    SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
    SCRIPT_DIR="$(cd "$(dirname "${SCRIPT_PATH}")" && pwd)"
    if [ -x "${SCRIPT_DIR}/avro-tray" ]; then
        nohup "${SCRIPT_DIR}/avro-tray" >/dev/null 2>&1 &
    elif [ -x "${HOME}/.local/bin/avro-tray" ]; then
        nohup "${HOME}/.local/bin/avro-tray" >/dev/null 2>&1 &
    fi
fi
