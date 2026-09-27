"""
Exit Confirmation Dialog for OmniPDF.
Prompts the user before closing and provides a friendly note to support the creator on Ko-fi.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QCheckBox, QFrame
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QIcon
import os

class ExitConfirmDialog(QDialog):
    KO_FI_URL = "https://ko-fi.com/gauravdubeypro"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Exit OmniPDF")
        self.setFixedWidth(480)
        self.setModal(True)
        self.dont_ask_again = False

        self.setStyleSheet("""
            QDialog {
                background-color: #0b1120;
                color: #f8fafc;
            }
            QLabel {
                color: #f8fafc;
            }
            QCheckBox {
                color: #94a3b8;
            }
            QPushButton#secondaryBtn {
                background-color: #1e293b;
                color: #cbd5e1;
                border: 1px solid #334155;
                padding: 6px 14px;
                border-radius: 5px;
            }
            QPushButton#secondaryBtn:hover {
                background-color: #334155;
                color: #ffffff;
            }
        """)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 20, 24, 20)

        # Header Title
        lbl_title = QLabel("Exit OmniPDF")
        lbl_title.setStyleSheet("font-size: 17px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(lbl_title)

        # Primary question
        lbl_msg = QLabel("Are you sure you want to exit the application?")
        lbl_msg.setStyleSheet("font-size: 13px; margin-bottom: 2px;")
        layout.addWidget(lbl_msg)

        # Creator Support Card
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1e293b, stop:1 #0f172a);
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(8)

        lbl_support_title = QLabel("❤️ Don't forget to support the creator!")
        lbl_support_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #f43f5e; background: transparent;")
        card_layout.addWidget(lbl_support_title)

        lbl_support_text = QLabel(
            "OmniPDF is crafted with passion by <b>Gaurav Dubey</b>.<br>"
            "If OmniPDF makes reading and managing PDFs easier for you, "
            "a small tip on Ko-fi helps keep new updates, features, and fixes coming!"
        )
        lbl_support_text.setWordWrap(True)
        lbl_support_text.setStyleSheet("font-size: 11px; color: #cbd5e1; line-height: 1.4; background: transparent;")
        card_layout.addWidget(lbl_support_text)

        # Ko-fi button inside card
        btn_kofi = QPushButton("☕ Support on Ko-fi")
        btn_kofi.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_kofi.setStyleSheet("""
            QPushButton {
                background-color: #ff5e5b;
                color: #ffffff;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 16px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #e04b48;
            }
            QPushButton:pressed {
                background-color: #c93b38;
            }
        """)
        btn_kofi.clicked.connect(self._open_kofi)
        card_layout.addWidget(btn_kofi, alignment=Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(card)

        # Don't ask again checkbox
        self.chk_dont_ask = QCheckBox("Don't ask again when exiting")
        self.chk_dont_ask.setStyleSheet("font-size: 12px; color: #94a3b8;")
        layout.addWidget(self.chk_dont_ask)

        # Dialog buttons (Cancel, Exit)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setObjectName("secondaryBtn")
        self.btn_cancel.setFixedWidth(90)
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_exit = QPushButton("Exit OmniPDF")
        self.btn_exit.setFixedWidth(115)
        self.btn_exit.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                font-weight: 600;
                padding: 6px 14px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
            QPushButton:pressed {
                background-color: #b91c1c;
            }
        """)
        self.btn_exit.clicked.connect(self._on_confirm_exit)
        btn_layout.addWidget(self.btn_exit)

        layout.addLayout(btn_layout)

    def _open_kofi(self):
        QDesktopServices.openUrl(QUrl(self.KO_FI_URL))

    def _on_confirm_exit(self):
        self.dont_ask_again = self.chk_dont_ask.isChecked()
        self.accept()
