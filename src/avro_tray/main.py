"""
Avro Tray Indicator & Fast Switcher
Main application runtime.
"""

import sys
import os
import signal
import subprocess
import fcntl
from PyQt5 import QtWidgets, QtCore, QtNetwork

from avro_tray.icons import get_english_icon, get_bangla_icon

LOCK_PATH = f"/tmp/avro-tray-{os.getuid()}.lock"
SOCKET_PATH = f"/tmp/avro-tray-{os.getuid()}.sock"
DEFAULT_BN_ENGINE = "ibus-avro"
ENGLISH_ENGINE = "xkb:us::eng"

_lock_file = None


def acquire_single_instance_lock() -> bool:
    """Ensure only one instance runs per user session using an exclusive file lock."""
    global _lock_file
    try:
        _lock_file = open(LOCK_PATH, "a+")
        fcntl.flock(_lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except (IOError, OSError):
        return False



class SocketServer(QtCore.QObject):
    """Local Unix domain socket server to receive fast toggle commands from hotkeys."""
    toggle_requested = QtCore.pyqtSignal()
    set_bn_requested = QtCore.pyqtSignal()
    set_en_requested = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.server = QtNetwork.QLocalServer(self)
        if os.path.exists(SOCKET_PATH):
            try:
                os.remove(SOCKET_PATH)
            except OSError:
                pass
        self.server.listen(SOCKET_PATH)
        self.server.newConnection.connect(self._on_new_connection)

    def _on_new_connection(self):
        client = self.server.nextPendingConnection()
        if not client:
            return
        client.readyRead.connect(lambda: self._handle_client(client))

    def _handle_client(self, client):
        data = bytes(client.readAll()).decode("utf-8", errors="ignore").strip()
        if data == "TOGGLE":
            self.toggle_requested.emit()
            client.write(b"OK\n")
        elif data == "SET_BN":
            self.set_bn_requested.emit()
            client.write(b"OK\n")
        elif data == "SET_EN":
            self.set_en_requested.emit()
            client.write(b"OK\n")
        elif data == "PING":
            client.write(b"PONG\n")
        else:
            client.write(b"UNKNOWN\n")
        client.flush()
        client.disconnectFromServer()


class AvroTrayApp(QtWidgets.QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False)

        # State configuration
        self.current_bn_engine = DEFAULT_BN_ENGINE
        self.show_notifications = True
        self.last_detected_engine = ""

        # Pre-render icons
        self.icon_en = get_english_icon()
        self.icon_bn = get_bangla_icon()

        # Create System Tray Icon
        self.tray = QtWidgets.QSystemTrayIcon(self)
        self.tray.setIcon(self.icon_en)
        self.tray.setToolTip("Avro Keyboard: English [F12 to switch]")
        self.tray.activated.connect(self._on_tray_activated)

        # Context menu
        self._build_menu()
        self.tray.setContextMenu(self.menu)
        self.tray.show()

        # Socket listener for instant hotkey triggers
        self.socket_server = SocketServer(self)
        self.socket_server.toggle_requested.connect(self.toggle_language)
        self.socket_server.set_bn_requested.connect(lambda: self.switch_to_engine(self.current_bn_engine))
        self.socket_server.set_en_requested.connect(lambda: self.switch_to_engine(ENGLISH_ENGINE))

        # Periodic sync timer to watch IBus changes
        self.sync_timer = QtCore.QTimer(self)
        self.sync_timer.timeout.connect(self.sync_engine_state)
        self.sync_timer.start(350)

        # Initial synchronization
        self.sync_engine_state()

    def _build_menu(self):
        self.menu = QtWidgets.QMenu()

        self.action_bn = self.menu.addAction("🇧🇩 বাংলা (Avro Phonetic)")
        self.action_bn.setCheckable(True)
        self.action_bn.triggered.connect(lambda: self.switch_to_engine(self.current_bn_engine))

        self.action_en = self.menu.addAction("🇺🇸 English (US)")
        self.action_en.setCheckable(True)
        self.action_en.triggered.connect(lambda: self.switch_to_engine(ENGLISH_ENGINE))

        self.menu.addSeparator()

        self.action_toggle = self.menu.addAction("🔄 Toggle Language (F12)")
        self.action_toggle.triggered.connect(self.toggle_language)

        # Engine selection submenu
        engine_menu = self.menu.addMenu("⚙️ Avro Engine Preference")
        self.group_engine = QtWidgets.QActionGroup(self)

        self.action_engine_avro = engine_menu.addAction("ibus-avro (Classic Avro Phonetic)")
        self.action_engine_avro.setCheckable(True)
        self.action_engine_avro.setChecked(self.current_bn_engine == "ibus-avro")
        self.action_engine_avro.setActionGroup(self.group_engine)
        self.action_engine_avro.triggered.connect(lambda: self._set_preferred_bn_engine("ibus-avro"))

        self.action_engine_ob = engine_menu.addAction("OpenBangla Keyboard (v2.0)")
        self.action_engine_ob.setCheckable(True)
        self.action_engine_ob.setChecked(self.current_bn_engine == "OpenBangla")
        self.action_engine_ob.setActionGroup(self.group_engine)
        self.action_engine_ob.triggered.connect(lambda: self._set_preferred_bn_engine("OpenBangla"))

        # Notification toggle
        self.action_notify = self.menu.addAction("🔔 Show Switch Notifications")
        self.action_notify.setCheckable(True)
        self.action_notify.setChecked(self.show_notifications)
        self.action_notify.triggered.connect(self._toggle_notifications)

        self.menu.addSeparator()

        self.action_quit = self.menu.addAction("🚪 Quit Avro Tray")
        self.action_quit.triggered.connect(self.quit_app)

    def _set_preferred_bn_engine(self, engine_name: str):
        self.current_bn_engine = engine_name
        if self.is_bangla_active():
            self.switch_to_engine(engine_name)

    def _toggle_notifications(self, checked: bool):
        self.show_notifications = checked

    def _on_tray_activated(self, reason):
        if reason in (QtWidgets.QSystemTrayIcon.Trigger, QtWidgets.QSystemTrayIcon.DoubleClick):
            self.toggle_language()

    def get_current_engine(self) -> str:
        try:
            res = subprocess.run(["ibus", "engine"], capture_output=True, text=True, timeout=1)
            if res.returncode == 0:
                return res.stdout.strip()
        except Exception:
            pass
        return ""

    def is_bangla_active(self, engine: str = None) -> bool:
        if engine is None:
            engine = self.get_current_engine()
        eng_lower = engine.lower()
        return ("avro" in eng_lower) or ("bangla" in eng_lower) or ("bn" in eng_lower)

    def sync_engine_state(self):
        engine = self.get_current_engine()
        if engine == self.last_detected_engine:
            return
        self.last_detected_engine = engine

        is_bn = self.is_bangla_active(engine)
        if is_bn:
            self.tray.setIcon(self.icon_bn)
            self.tray.setToolTip(f"Avro Keyboard: বাংলা Active [{engine}] (Press F12 to switch)")
            self.action_bn.setChecked(True)
            self.action_en.setChecked(False)
        else:
            self.tray.setIcon(self.icon_en)
            self.tray.setToolTip("Avro Keyboard: English (Press F12 to switch)")
            self.action_bn.setChecked(False)
            self.action_en.setChecked(True)

    def switch_to_engine(self, target_engine: str, notify: bool = True):
        try:
            subprocess.run(["ibus", "engine", target_engine], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

        self.sync_engine_state()

        if notify and self.show_notifications:
            is_bn = (target_engine != ENGLISH_ENGINE)
            title = "🇧🇩 বাংলা (Avro Phonetic)" if is_bn else "🇺🇸 English (US)"
            msg = "Keyboard set to বাংলা" if is_bn else "Keyboard set to English"
            try:
                subprocess.Popen(
                    ["notify-send", "-t", "1000", "-a", "Avro Keyboard",
                     "-i", "/usr/share/pixmaps/openbangla-keyboard.png", title, msg],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            except Exception:
                pass

    def toggle_language(self):
        current = self.get_current_engine()
        if self.is_bangla_active(current):
            self.switch_to_engine(ENGLISH_ENGINE)
        else:
            self.switch_to_engine(self.current_bn_engine)

    def quit_app(self):
        global _lock_file
        if os.path.exists(SOCKET_PATH):
            try:
                os.remove(SOCKET_PATH)
            except OSError:
                pass
        if _lock_file:
            try:
                fcntl.flock(_lock_file.fileno(), fcntl.LOCK_UN)
                _lock_file.close()
            except OSError:
                pass
        self.quit()


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)

    if not acquire_single_instance_lock():
        print("Avro Tray Indicator is already running. Exiting.", file=sys.stderr)
        sys.exit(0)

    app = AvroTrayApp(sys.argv)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

