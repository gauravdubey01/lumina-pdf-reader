"""
Lumina PDF Reader - Main Entry Point.
"""
import sys
import os
import ctypes

def setup_windows_app_id():
    """Ensure proper taskbar icon behavior on Windows."""
    if sys.platform == "win32":
        try:
            myappid = "lumina.pdfreader.desktop.v1"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

def get_resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

def main():
    setup_windows_app_id()

    # Enable High DPI scaling
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt

    app = QApplication(sys.argv)
    app.setApplicationName("Lumina PDF Reader")
    app.setOrganizationName("LuminaApps")
    app.setApplicationVersion("1.0.0")

    from PyQt6.QtGui import QIcon
    icon_path = get_resource_path(os.path.join("assets", "icon.png"))
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    from app.ui.main_window import MainWindow

    initial_file = None
    if len(sys.argv) > 1:
        arg_file = sys.argv[1]
        if os.path.exists(arg_file) and arg_file.lower().endswith(".pdf"):
            initial_file = arg_file

    window = MainWindow(initial_file=initial_file)
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
