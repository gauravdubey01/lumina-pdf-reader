"""
Split PDF Dialog.
Supports splitting by custom page ranges, into single pages, or every N pages.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QRadioButton,
    QButtonGroup, QLineEdit, QSpinBox, QLabel, QFileDialog,
    QProgressBar, QMessageBox, QGroupBox, QFrame
)
from PyQt6.QtCore import Qt
import os
import pymupdf as fitz
from app.core.pdf_tools import PDFTools

class SplitPDFDialog(QDialog):
    def __init__(self, parent=None, pdf_path: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Split PDF Document")
        self.resize(520, 420)
        self.pdf_path = pdf_path
        self.total_pages = 0

        if self.pdf_path and os.path.exists(self.pdf_path):
            try:
                with fitz.open(self.pdf_path) as doc:
                    self.total_pages = len(doc)
            except Exception:
                pass

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        # Header
        title_label = QLabel("Split PDF Pages & Sections")
        title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title_label)

        # Selected document info
        doc_box = QGroupBox("Target Document")
        doc_layout = QHBoxLayout(doc_box)
        self.file_label = QLabel(
            f"<b>{os.path.basename(self.pdf_path)}</b> ({self.total_pages} total pages)"
            if self.pdf_path else "No document selected"
        )
        self.file_label.setStyleSheet("color: #e2e8f0;")
        doc_layout.addWidget(self.file_label, 1)

        self.browse_doc_btn = QPushButton("Change File...")
        self.browse_doc_btn.setObjectName("secondaryBtn")
        self.browse_doc_btn.clicked.connect(self._on_browse_file)
        doc_layout.addWidget(self.browse_doc_btn)
        layout.addWidget(doc_box)

        # Split Options Group
        options_box = QGroupBox("Split Mode")
        options_layout = QVBoxLayout(options_box)
        options_layout.setSpacing(10)

        self.btn_group = QButtonGroup(self)

        # Option 1: Custom page range
        self.radio_range = QRadioButton("Extract Specific Page Range (e.g. 1-3, 5, 8-10)")
        self.radio_range.setChecked(True)
        self.btn_group.addButton(self.radio_range)
        options_layout.addWidget(self.radio_range)

        range_input_layout = QHBoxLayout()
        range_input_layout.setContentsMargins(20, 0, 0, 0)
        range_label = QLabel("Page Ranges:")
        self.range_input = QLineEdit()
        self.range_input.setPlaceholderText(f"1-{min(self.total_pages, 5)}")
        if self.total_pages > 0:
            self.range_input.setText(f"1-{min(self.total_pages, 3)}")
        range_input_layout.addWidget(range_label)
        range_input_layout.addWidget(self.range_input)
        options_layout.addLayout(range_input_layout)

        # Option 2: Split into single pages
        self.radio_single = QRadioButton(f"Extract every page into individual single-page PDFs")
        self.btn_group.addButton(self.radio_single)
        options_layout.addWidget(self.radio_single)

        # Option 3: Split every N pages
        self.radio_every_n = QRadioButton("Split document every N pages")
        self.btn_group.addButton(self.radio_every_n)
        options_layout.addWidget(self.radio_every_n)

        every_n_layout = QHBoxLayout()
        every_n_layout.setContentsMargins(20, 0, 0, 0)
        every_n_label = QLabel("Pages per split file:")
        self.spin_n = QSpinBox()
        self.spin_n.setRange(1, max(self.total_pages, 100))
        self.spin_n.setValue(min(5, max(1, self.total_pages // 2)))
        every_n_layout.addWidget(every_n_label)
        every_n_layout.addWidget(self.spin_n)
        every_n_layout.addStretch()
        options_layout.addLayout(every_n_layout)

        layout.addWidget(options_box)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(16)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # Bottom Buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("secondaryBtn")
        self.cancel_btn.clicked.connect(self.reject)
        bottom_layout.addWidget(self.cancel_btn)

        self.split_btn = QPushButton("Split PDF")
        self.split_btn.clicked.connect(self._on_split)
        bottom_layout.addWidget(self.split_btn)

        layout.addLayout(bottom_layout)

    def _on_browse_file(self):
        fpath, _ = QFileDialog.getOpenFileName(self, "Select PDF to Split", "", "PDF Files (*.pdf)")
        if fpath:
            self.pdf_path = fpath
            try:
                with fitz.open(self.pdf_path) as doc:
                    self.total_pages = len(doc)
                self.file_label.setText(
                    f"<b>{os.path.basename(self.pdf_path)}</b> ({self.total_pages} total pages)"
                )
                self.spin_n.setMaximum(max(self.total_pages, 100))
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not read PDF: {e}")

    def _on_split(self):
        if not self.pdf_path or not os.path.exists(self.pdf_path):
            QMessageBox.warning(self, "Split PDF", "Please select a valid PDF file first.")
            return

        if self.radio_range.isChecked():
            range_str = self.range_input.text().strip()
            if not range_str:
                QMessageBox.warning(self, "Split PDF", "Please enter a valid page range (e.g. 1-3, 5).")
                return

            out_file, _ = QFileDialog.getSaveFileName(
                self, "Save Extracted Pages As", "Extracted_Pages.pdf", "PDF Files (*.pdf)"
            )
            if not out_file:
                return

            success, msg = PDFTools.split_pdf_by_range(self.pdf_path, range_str, out_file)
            if success:
                QMessageBox.information(self, "Split Complete", msg)
                self.accept()
            else:
                QMessageBox.critical(self, "Split Failed", msg)

        elif self.radio_single.isChecked():
            out_dir = QFileDialog.getExistingDirectory(self, "Select Destination Folder for Single Pages")
            if not out_dir:
                return

            self.progress_bar.show()
            self.progress_bar.setRange(0, self.total_pages)
            self.split_btn.setEnabled(False)

            def progress(curr, total):
                self.progress_bar.setValue(curr)

            success, msg = PDFTools.split_into_single_pages(self.pdf_path, out_dir, progress_callback=progress)
            self.progress_bar.hide()
            self.split_btn.setEnabled(True)

            if success:
                QMessageBox.information(self, "Split Complete", msg)
                self.accept()
            else:
                QMessageBox.critical(self, "Split Failed", msg)

        elif self.radio_every_n.isChecked():
            n = self.spin_n.value()
            out_dir = QFileDialog.getExistingDirectory(self, f"Select Destination Folder for {n}-Page Chunks")
            if not out_dir:
                return

            self.progress_bar.show()
            self.progress_bar.setRange(0, self.total_pages)
            self.split_btn.setEnabled(False)

            def progress(curr, total):
                self.progress_bar.setValue(curr)

            success, msg = PDFTools.split_every_n_pages(self.pdf_path, n, out_dir, progress_callback=progress)
            self.progress_bar.hide()
            self.split_btn.setEnabled(True)

            if success:
                QMessageBox.information(self, "Split Complete", msg)
                self.accept()
            else:
                QMessageBox.critical(self, "Split Failed", msg)
