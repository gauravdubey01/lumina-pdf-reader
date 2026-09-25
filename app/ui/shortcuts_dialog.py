"""
Keyboard Shortcuts Dialog for Lumina PDF Reader.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton
)
from PyQt6.QtCore import Qt

class ShortcutsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Keyboard Shortcuts")
        self.resize(540, 520)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Lumina PDF Reader - Keyboard Shortcuts")
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title)

        shortcuts = [
            ("File Operations", ""),
            ("Ctrl + O", "Open PDF Document"),
            ("Ctrl + T", "Open New Document Tab"),
            ("Ctrl + W", "Close Current Tab"),
            ("Ctrl + S", "Save Annotations / Document"),
            ("Ctrl + P", "Print Document"),
            ("Ctrl + Q", "Exit Application"),
            ("Navigation", ""),
            ("Right Arrow / Space / PageDown", "Next Page (or Spread in Book mode)"),
            ("Left Arrow / PageUp", "Previous Page"),
            ("Home / End", "First Page / Last Page"),
            ("Alt + Left", "Navigate Back"),
            ("Alt + Right", "Navigate Forward"),
            ("View & Zoom", ""),
            ("Ctrl + Wheel", "Interactive Smooth Zoom"),
            ("Ctrl + + / Ctrl + -", "Zoom In / Zoom Out"),
            ("Ctrl + 0", "Reset Zoom to 100%"),
            ("Ctrl + B", "Toggle Sidebar (Thumbnails, Outline, Search)"),
            ("F11", "Toggle Fullscreen"),
            ("Tools & Annotations", ""),
            ("Ctrl + C", "Copy Selected Text"),
            ("Ctrl + R", "Rotate Clockwise 90°"),
            ("Shift + Space", "Toggle Auto-Scroll Play/Pause"),
            ("F1", "Open this Keyboard Shortcuts Guide")
        ]

        table = QTableWidget(len(shortcuts), 2)
        table.setHorizontalHeaderLabels(["Shortcut", "Action"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        for row, (key, desc) in enumerate(shortcuts):
            if not desc:
                # Category Header
                item_key = QTableWidgetItem(key)
                item_key.setFlags(Qt.ItemFlag.NoItemFlags)
                item_key.setStyleSheet("font-weight: bold; color: #38bdf8;")
                table.setItem(row, 0, item_key)
                table.setSpan(row, 0, 1, 2)
            else:
                item_key = QTableWidgetItem(key)
                item_desc = QTableWidgetItem(desc)
                table.setItem(row, 0, item_key)
                table.setItem(row, 1, item_desc)

        layout.addWidget(table)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
