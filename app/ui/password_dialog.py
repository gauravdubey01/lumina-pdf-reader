"""
Password Dialog for opening encrypted PDFs.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt

class PasswordDialog(QDialog):
    def __init__(self, file_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Password Protected Document")
        self.resize(380, 160)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        desc = QLabel(f"<b>{file_name}</b> is protected with a password.\nPlease enter the password to open it:")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setPlaceholderText("Enter document password")
        self.pass_input.returnPressed.connect(self.accept)
        layout.addWidget(self.pass_input)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("secondaryBtn")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.ok_btn = QPushButton("Unlock")
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)

        layout.addLayout(btn_layout)
        self.pass_input.setFocus()

    def get_password(self) -> str:
        return self.pass_input.text()
