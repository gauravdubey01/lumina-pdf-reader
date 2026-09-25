"""
Security & Password Protection Dialog.
Allows users to encrypt/password-protect a PDF document.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt
import os
import pymupdf as fitz

class SecurityDialog(QDialog):
    def __init__(self, current_file: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Protect & Encrypt PDF")
        self.resize(460, 280)
        self.current_file = current_file

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Set Document Password & Encryption")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title)

        box = QGroupBox("Password Settings")
        box_layout = QVBoxLayout(box)
        box_layout.setSpacing(8)

        pass_lbl = QLabel("User Password (Required to open the PDF):")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setPlaceholderText("Enter password")
        box_layout.addWidget(pass_lbl)
        box_layout.addWidget(self.pass_input)

        confirm_lbl = QLabel("Confirm Password:")
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setPlaceholderText("Confirm password")
        box_layout.addWidget(confirm_lbl)
        box_layout.addWidget(self.confirm_input)

        layout.addWidget(box)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("secondaryBtn")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.protect_btn = QPushButton("Protect & Save As...")
        self.protect_btn.clicked.connect(self._on_protect)
        btn_layout.addWidget(self.protect_btn)

        layout.addLayout(btn_layout)

    def _on_protect(self):
        pwd = self.pass_input.text()
        confirm = self.confirm_input.text()

        if not pwd:
            QMessageBox.warning(self, "Security", "Please enter a password.")
            return

        if pwd != confirm:
            QMessageBox.warning(self, "Security", "Passwords do not match. Please re-enter.")
            return

        if not self.current_file or not os.path.exists(self.current_file):
            src_file, _ = QFileDialog.getOpenFileName(self, "Select PDF to Protect", "", "PDF Files (*.pdf)")
            if not src_file:
                return
            self.current_file = src_file

        out_file, _ = QFileDialog.getSaveFileName(
            self, "Save Protected PDF As", "Protected_" + os.path.basename(self.current_file), "PDF Files (*.pdf)"
        )
        if not out_file:
            return

        try:
            doc = fitz.open(self.current_file)
            # AES 256-bit encryption
            perm = fitz.PDF_PERM_ACCESSIBILITY | fitz.PDF_PERM_PRINT | fitz.PDF_PERM_COPY
            doc.save(
                out_file,
                encryption=fitz.PDF_ENCRYPT_AES_256,
                user_pw=pwd,
                owner_pw=pwd,
                permissions=perm
            )
            doc.close()
            QMessageBox.information(self, "Success", f"Password-protected PDF saved successfully to:\n{out_file}")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not protect PDF: {e}")
