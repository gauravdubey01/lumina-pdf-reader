"""
Export Dialog for Lumina PDF Reader.
Supports exporting PDF pages as Images (PNG, JPEG) or Plain Text (.txt).
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QRadioButton, QButtonGroup, QComboBox, QSpinBox,
    QPushButton, QFileDialog, QProgressBar, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt
import os
import pymupdf as fitz
from app.core.pdf_document import PDFDocument

class ExportDialog(QDialog):
    def __init__(self, doc: PDFDocument, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Document")
        self.resize(480, 360)
        self.doc = doc

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Export PDF Pages or Content")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title)

        # Export Format Options
        format_box = QGroupBox("Export Format")
        format_layout = QVBoxLayout(format_box)
        format_layout.setSpacing(8)

        self.btn_group = QButtonGroup(self)

        self.radio_images = QRadioButton("Export Pages as Images (PNG / JPEG)")
        self.radio_images.setChecked(True)
        self.btn_group.addButton(self.radio_images)
        format_layout.addWidget(self.radio_images)

        # Image settings row
        img_opts_layout = QHBoxLayout()
        img_opts_layout.setContentsMargins(20, 0, 0, 0)
        img_opts_layout.addWidget(QLabel("Format:"))
        self.img_format_combo = QComboBox()
        self.img_format_combo.addItems(["PNG", "JPEG", "WEBP"])
        img_opts_layout.addWidget(self.img_format_combo)

        img_opts_layout.addWidget(QLabel("DPI / Quality:"))
        self.dpi_combo = QComboBox()
        self.dpi_combo.addItems(["150 DPI (Standard)", "300 DPI (High Quality)", "600 DPI (Print Resolution)"])
        self.dpi_combo.setCurrentIndex(1)
        img_opts_layout.addWidget(self.dpi_combo)
        format_layout.addLayout(img_opts_layout)

        self.radio_text = QRadioButton("Export Extracted Plain Text (.txt)")
        self.btn_group.addButton(self.radio_text)
        format_layout.addWidget(self.radio_text)

        layout.addWidget(format_box)

        # Page Range
        range_box = QGroupBox("Pages to Export")
        range_layout = QHBoxLayout(range_box)
        self.radio_all_pages = QRadioButton("All Pages")
        self.radio_all_pages.setChecked(True)
        self.radio_curr_page = QRadioButton("Current Page Only")
        range_layout.addWidget(self.radio_all_pages)
        range_layout.addWidget(self.radio_curr_page)
        range_layout.addStretch()
        layout.addWidget(range_box)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(14)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("secondaryBtn")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.export_btn = QPushButton("Export...")
        self.export_btn.clicked.connect(self._on_export)
        btn_layout.addWidget(self.export_btn)

        layout.addLayout(btn_layout)

    def _on_export(self):
        if not self.doc or not self.doc.is_valid():
            QMessageBox.warning(self, "Export", "No document open to export.")
            return

        if self.radio_images.isChecked():
            out_dir = QFileDialog.getExistingDirectory(self, "Select Folder to Save Images")
            if not out_dir:
                return

            ext = self.img_format_combo.currentText().lower()
            dpi_map = {0: 150, 1: 300, 2: 600}
            dpi = dpi_map.get(self.dpi_combo.currentIndex(), 300)
            zoom = dpi / 72.0

            total = self.doc.page_count
            start_p = 0
            end_p = total - 1
            if self.radio_curr_page.isChecked():
                start_p = 0 # or current page
                end_p = 0

            self.progress_bar.show()
            self.progress_bar.setRange(0, total)
            self.export_btn.setEnabled(False)

            base_name = os.path.splitext(os.path.basename(self.doc.file_path or "Page"))[0]
            count = 0
            for p in range(start_p, end_p + 1):
                self.progress_bar.setValue(p + 1)
                page = self.doc.doc[p]
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                out_file = os.path.join(out_dir, f"{base_name}_page_{p + 1:04d}.{ext}")
                pix.save(out_file)
                count += 1

            self.progress_bar.hide()
            self.export_btn.setEnabled(True)
            QMessageBox.information(self, "Export Complete", f"Exported {count} image(s) to:\n{out_dir}")
            self.accept()

        elif self.radio_text.isChecked():
            out_file, _ = QFileDialog.getSaveFileName(self, "Save Extracted Text", "Extracted_Text.txt", "Text Files (*.txt)")
            if not out_file:
                return

            text_content = []
            for p in range(self.doc.page_count):
                page_text = self.doc.doc[p].get_text("text")
                text_content.append(f"--- Page {p + 1} ---\n" + page_text)

            with open(out_file, "w", encoding="utf-8") as f:
                f.write("\n\n".join(text_content))

            QMessageBox.information(self, "Export Complete", f"Text successfully extracted to:\n{out_file}")
            self.accept()
