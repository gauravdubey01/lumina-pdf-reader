"""
Modern Windows 11 Fluent QSS Stylesheets for Lumina PDF Reader.
Includes Dark, Light, and Sepia themes.
"""

DARK_THEME = """
QWidget {
    background-color: #1a1b1e;
    color: #e2e8f0;
    font-family: 'Segoe UI', 'SF Pro Display', -apple-system, sans-serif;
    font-size: 13px;
}

/* Main Window */
QMainWindow {
    background-color: #141517;
}

/* ToolBar */
QToolBar {
    background-color: #202227;
    border-bottom: 1px solid #2d3139;
    spacing: 6px;
    padding: 6px 10px;
}

QToolButton {
    background-color: transparent;
    color: #cbd5e1;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 6px 10px;
    font-weight: 500;
}

QToolButton:hover {
    background-color: #2e323b;
    color: #ffffff;
    border: 1px solid #3d424e;
}

QToolButton:pressed {
    background-color: #3b82f6;
    color: #ffffff;
}

QToolButton:checked {
    background-color: #2563eb;
    color: #ffffff;
    border: 1px solid #3b82f6;
}

/* Menu Bar & Menus */
QMenuBar {
    background-color: #1a1b1e;
    color: #e2e8f0;
    border-bottom: 1px solid #2d3139;
    padding: 2px;
}

QMenuBar::item {
    background: transparent;
    padding: 6px 10px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #2e323b;
}

QMenu {
    background-color: #202227;
    color: #e2e8f0;
    border: 1px solid #2d3139;
    border-radius: 8px;
    padding: 6px;
}

QMenu::item {
    padding: 6px 24px 6px 12px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #2563eb;
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background: #2d3139;
    margin: 4px 8px;
}

/* Status Bar */
QStatusBar {
    background-color: #141517;
    color: #94a3b8;
    border-top: 1px solid #2d3139;
    font-size: 12px;
    padding: 3px 8px;
}

/* ScrollArea / Viewer */
QScrollArea {
    background-color: #121316;
    border: none;
}

/* Sidebar / DockWidget / TabWidget */
QTabWidget::pane {
    border: 1px solid #2d3139;
    background-color: #1a1b1e;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #141517;
    color: #94a3b8;
    border: 1px solid transparent;
    padding: 8px 14px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #1a1b1e;
    color: #38bdf8;
    border: 1px solid #2d3139;
    border-bottom: 1px solid #1a1b1e;
}

QTabBar::tab:hover:!selected {
    background-color: #202227;
    color: #e2e8f0;
}

/* TreeView & ListView */
QTreeView, QListView {
    background-color: #1a1b1e;
    color: #e2e8f0;
    border: 1px solid #2d3139;
    border-radius: 6px;
    padding: 4px;
    outline: 0;
}

QTreeView::item, QListView::item {
    padding: 6px 8px;
    border-radius: 4px;
}

QTreeView::item:hover, QListView::item:hover {
    background-color: #262930;
}

QTreeView::item:selected, QListView::item:selected {
    background-color: #2563eb;
    color: #ffffff;
}

/* Buttons */
QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    border: 1px solid #3b82f6;
    border-radius: 6px;
    padding: 7px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #1d4ed8;
}

QPushButton:pressed {
    background-color: #1e40af;
}

QPushButton:disabled {
    background-color: #2a2d35;
    color: #64748b;
    border: 1px solid #333842;
}

QPushButton#secondaryBtn {
    background-color: #262930;
    color: #e2e8f0;
    border: 1px solid #3d424e;
}

QPushButton#secondaryBtn:hover {
    background-color: #323640;
}

/* LineEdit / Inputs */
QLineEdit, QSpinBox, QComboBox {
    background-color: #202227;
    color: #f1f5f9;
    border: 1px solid #333842;
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: #2563eb;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #3b82f6;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #141517;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #333842;
    min-height: 25px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: #141517;
    height: 10px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background: #333842;
    min-width: 25px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background: #475569;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Progress Bar */
QProgressBar {
    background-color: #202227;
    border: 1px solid #2d3139;
    border-radius: 6px;
    text-align: center;
    color: #ffffff;
    font-weight: bold;
}

QProgressBar::chunk {
    background-color: #3b82f6;
    border-radius: 5px;
}

/* Slider */
QSlider::groove:horizontal {
    border: none;
    height: 4px;
    background: #333842;
    border-radius: 2px;
}

QSlider::sub-page:horizontal {
    background: #3b82f6;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #60a5fa;
    border: none;
    width: 12px;
    height: 12px;
    margin: -4px 0;
    border-radius: 6px;
}

QSlider::handle:horizontal:hover {
    background: #93c5fd;
}

QTabBar::close-button {
    image: none;
    padding: 2px;
    border-radius: 3px;
}

QTabBar::close-button:hover {
    background-color: #ef4444;
    color: white;
}
"""

LIGHT_THEME = """
QWidget {
    background-color: #f8fafc;
    color: #1e293b;
    font-family: 'Segoe UI', 'SF Pro Display', -apple-system, sans-serif;
    font-size: 13px;
}

/* Main Window */
QMainWindow {
    background-color: #f1f5f9;
}

/* ToolBar */
QToolBar {
    background-color: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    spacing: 6px;
    padding: 6px 10px;
}

QToolButton {
    background-color: transparent;
    color: #334155;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 6px 10px;
    font-weight: 500;
}

QToolButton:hover {
    background-color: #f1f5f9;
    color: #0f172a;
    border: 1px solid #cbd5e1;
}

QToolButton:pressed {
    background-color: #2563eb;
    color: #ffffff;
}

QToolButton:checked {
    background-color: #eff6ff;
    color: #2563eb;
    border: 1px solid #93c5fd;
}

/* Menu Bar & Menus */
QMenuBar {
    background-color: #ffffff;
    color: #1e293b;
    border-bottom: 1px solid #e2e8f0;
    padding: 2px;
}

QMenuBar::item {
    background: transparent;
    padding: 6px 10px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #f1f5f9;
}

QMenu {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 6px;
}

QMenu::item {
    padding: 6px 24px 6px 12px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #2563eb;
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background: #e2e8f0;
    margin: 4px 8px;
}

/* Status Bar */
QStatusBar {
    background-color: #ffffff;
    color: #64748b;
    border-top: 1px solid #e2e8f0;
    font-size: 12px;
    padding: 3px 8px;
}

/* ScrollArea / Viewer */
QScrollArea {
    background-color: #e2e8f0;
    border: none;
}

/* Sidebar / DockWidget / TabWidget */
QTabWidget::pane {
    border: 1px solid #e2e8f0;
    background-color: #ffffff;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #f1f5f9;
    color: #64748b;
    border: 1px solid transparent;
    padding: 8px 14px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #2563eb;
    border: 1px solid #e2e8f0;
    border-bottom: 1px solid #ffffff;
}

QTabBar::tab:hover:!selected {
    background-color: #e2e8f0;
    color: #1e293b;
}

/* TreeView & ListView */
QTreeView, QListView {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 4px;
    outline: 0;
}

QTreeView::item, QListView::item {
    padding: 6px 8px;
    border-radius: 4px;
}

QTreeView::item:hover, QListView::item:hover {
    background-color: #f1f5f9;
}

QTreeView::item:selected, QListView::item:selected {
    background-color: #2563eb;
    color: #ffffff;
}

/* Buttons */
QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    border: 1px solid #2563eb;
    border-radius: 6px;
    padding: 7px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #1d4ed8;
}

QPushButton:pressed {
    background-color: #1e40af;
}

QPushButton:disabled {
    background-color: #e2e8f0;
    color: #94a3b8;
    border: 1px solid #cbd5e1;
}

QPushButton#secondaryBtn {
    background-color: #ffffff;
    color: #334155;
    border: 1px solid #cbd5e1;
}

QPushButton#secondaryBtn:hover {
    background-color: #f8fafc;
}

/* LineEdit / Inputs */
QLineEdit, QSpinBox, QComboBox {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: #2563eb;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #2563eb;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #f1f5f9;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #cbd5e1;
    min-height: 25px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #94a3b8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: #f1f5f9;
    height: 10px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background: #cbd5e1;
    min-width: 25px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background: #94a3b8;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Progress Bar */
QProgressBar {
    background-color: #e2e8f0;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    text-align: center;
    color: #0f172a;
    font-weight: bold;
}

QProgressBar::chunk {
    background-color: #2563eb;
    border-radius: 5px;
}
"""

SEPIA_THEME = """
QWidget {
    background-color: #f4ecd8;
    color: #433422;
    font-family: 'Segoe UI', 'SF Pro Display', -apple-system, sans-serif;
    font-size: 13px;
}

/* Main Window */
QMainWindow {
    background-color: #eadeca;
}

/* ToolBar */
QToolBar {
    background-color: #efe5cf;
    border-bottom: 1px solid #dacdb3;
    spacing: 6px;
    padding: 6px 10px;
}

QToolButton {
    background-color: transparent;
    color: #5c4832;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 6px 10px;
    font-weight: 500;
}

QToolButton:hover {
    background-color: #e4d8bf;
    color: #2d2216;
    border: 1px solid #cbbda3;
}

QToolButton:pressed {
    background-color: #b45309;
    color: #ffffff;
}

QToolButton:checked {
    background-color: #fdf8eb;
    color: #b45309;
    border: 1px solid #d97706;
}

/* Menu Bar & Menus */
QMenuBar {
    background-color: #efe5cf;
    color: #433422;
    border-bottom: 1px solid #dacdb3;
    padding: 2px;
}

QMenuBar::item:selected {
    background-color: #e4d8bf;
}

QMenu {
    background-color: #faf4e6;
    color: #433422;
    border: 1px solid #dacdb3;
    border-radius: 8px;
    padding: 6px;
}

QMenu::item:selected {
    background-color: #b45309;
    color: #ffffff;
}

QStatusBar {
    background-color: #efe5cf;
    color: #78644e;
    border-top: 1px solid #dacdb3;
    font-size: 12px;
    padding: 3px 8px;
}

QScrollArea {
    background-color: #dfd2bc;
    border: none;
}

QTabWidget::pane {
    border: 1px solid #dacdb3;
    background-color: #faf4e6;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #eadeca;
    color: #78644e;
    border: 1px solid transparent;
    padding: 8px 14px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #faf4e6;
    color: #b45309;
    border: 1px solid #dacdb3;
    border-bottom: 1px solid #faf4e6;
}

QTreeView, QListView {
    background-color: #faf4e6;
    color: #433422;
    border: 1px solid #dacdb3;
    border-radius: 6px;
    padding: 4px;
}

QTreeView::item:hover, QListView::item:hover {
    background-color: #efe5cf;
}

QTreeView::item:selected, QListView::item:selected {
    background-color: #b45309;
    color: #ffffff;
}

QPushButton {
    background-color: #b45309;
    color: #ffffff;
    border: 1px solid #b45309;
    border-radius: 6px;
    padding: 7px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #92400e;
}

QPushButton#secondaryBtn {
    background-color: #faf4e6;
    color: #433422;
    border: 1px solid #dacdb3;
}

QPushButton#secondaryBtn:hover {
    background-color: #efe5cf;
}

QLineEdit, QSpinBox, QComboBox {
    background-color: #faf4e6;
    color: #433422;
    border: 1px solid #dacdb3;
    border-radius: 6px;
    padding: 6px 10px;
}

QScrollBar:vertical, QScrollBar:horizontal {
    background: #eadeca;
}

QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #cbbda3;
    border-radius: 5px;
}
"""

def get_theme_stylesheet(theme_name: str) -> str:
    if theme_name == "light":
        return LIGHT_THEME
    elif theme_name == "sepia":
        return SEPIA_THEME
    return DARK_THEME
