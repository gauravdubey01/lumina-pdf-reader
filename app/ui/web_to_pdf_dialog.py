"""
Web to PDF Dialog for Lumina PDF Reader.
Allows converting Web URLs and online articles into PDF documents.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QProgressBar, QMessageBox,
    QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import os
import tempfile
from app.core.web_converter import WebConverter

class WebConvertWorker(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str, str) # success, message, file_path

    def __init__(self, url: str, output_path: str):
        super().__init__()
        self.url = url
        self.output_path = output_path

    def run(self):
        success, msg = WebConverter.convert_url_to_pdf(
            self.url,
            self.output_path,
            progress_callback=self.progress_signal.emit
        )
        self.finished_signal.emit(success, msg, self.output_path)

class WebToPDFDialog(QDialog):
    converted_pdf_ready = pyqtSignal(str) # output_path

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Convert Webpage / Article to PDF")
        self.resize(520, 260)
        self.worker = None

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Convert Webpage or Online Article to PDF")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title)

        desc = QLabel("Enter any website URL to generate a formatted PDF with bookmarks and chapters:")
        desc.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(desc)

        # URL Input Row
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://en.wikipedia.org/wiki/Python_(programming_language)")
        self.url_input.returnPressed.connect(self._on_convert)
        layout.addWidget(self.url_input)

        # Open in Lumina Checkbox
        self.chk_auto_open = QCheckBox("Open automatically in Lumina PDF after conversion")
        self.chk_auto_open.setChecked(True)
        layout.addWidget(self.chk_auto_open)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(14)
        self.progress_bar.setRange(0, 0) # Indeterminate spinner
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet("color: #38bdf8; font-size: 11px;")
        layout.addWidget(self.status_lbl)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("secondaryBtn")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.convert_btn = QPushButton("Convert to PDF")
        self.convert_btn.clicked.connect(self._on_convert)
        btn_layout.addWidget(self.convert_btn)

        layout.addLayout(btn_layout)
        self.url_input.setFocus()

    def _on_convert(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Invalid URL", "Please enter a valid website URL.")
            return

        if self.chk_auto_open.isChecked():
            # Save to temporary or downloads folder
            tmp_dir = os.path.join(tempfile.gettempdir(), "LuminaWebPDFs")
            os.makedirs(tmp_dir, exist_ok=True)
            domain = url.replace("https://", "").replace("http://", "").split("/")[0].replace(".", "_")
            out_file = os.path.join(tmp_dir, f"Webpage_{domain}.pdf")
        else:
            out_file, _ = QFileDialog.getSaveFileName(
                self, "Save Webpage PDF As", "Webpage_Article.pdf", "PDF Files (*.pdf)"
            )
            if not out_file:
                return

        self.progress_bar.show()
        self.convert_btn.setEnabled(False)
        self.status_lbl.setText("Connecting...")

        self.worker = WebConvertWorker(url, out_file)
        self.worker.progress_signal.connect(self.status_lbl.setText)
        self.worker.finished_signal.connect(self._on_conversion_finished)
        self.worker.start()

    def _on_conversion_finished(self, success: bool, msg: str, out_path: str):
        self.progress_bar.hide()
        self.convert_btn.setEnabled(True)

        if success:
            self.converted_pdf_ready.emit(out_path)
            self.accept()
        else:
            self.status_lbl.setText("")
            QMessageBox.critical(self, "Conversion Failed", msg)
