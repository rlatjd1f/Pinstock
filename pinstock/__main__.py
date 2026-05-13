"""python -m pinstock 진입점."""

import sys

from PyQt6.QtWidgets import QApplication

from .core.storage import migrate_legacy_config


def main():
    migrate_legacy_config()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 트레이만 있어도 계속 실행

    from .ui_windows.manager import WidgetManager
    manager = WidgetManager(app)
    app.aboutToQuit.connect(manager.save_positions)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
