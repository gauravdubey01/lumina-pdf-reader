"""
Merge PDFs Dialog.
Allows users to add, reorder, and merge multiple PDF documents into one.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QFileDialog, QLabel, QProgressBar, QMessageBox,
    QFrame
)
from PyQt6.QtCore import Qt, QSize
import os
import pymupdf as fitz
from app.core.pdf_tools import PDFTools

class MergePDFDialog(QDialog):
    def __init__(self, parent=None, initial_files=None):
        super().__init__(parent)
        self.setWindowTitle("Merge PDF Files")
        self.resize(600, 480)
        self.setMinimumSize(500, 400)

        self._init_ui()
        if initial_files:
            self.add_files(initial_files)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Header description
        title_label = QLabel("Combine Multiple PDFs into One Document")
        title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title_label)

        desc_label = QLabel("Add PDF files and arrange them in the order you want them merged.")
        desc_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(desc_label)

        # File List and Control buttons
        main_content = QHBoxLayout()

        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        main_content.addWidget(self.file_list, 1)

        # Side action buttons
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(8)

        self.add_btn = QPushButton("Add Files...")
        self.add_btn.clicked.connect(self._on_add_files)
        btn_layout.addWidget(self.add_btn)

        self.up_btn = QPushButton("Move Up")
        self.up_btn.setObjectName("secondaryBtn")
        self.up_btn.clicked.connect(self._move_up)
        btn_layout.addWidget(self.up_btn)

        self.down_btn = QPushButton("Move Down")
        self.down_btn.setObjectName("secondaryBtn")
        self.down_btn.clicked.connect(self._move_down)
        btn_layout.addWidget(self.down_btn)

        self.remove_btn = QPushButton("Remove")
        self.remove_btn.setObjectName("secondaryBtn")
        self.remove_btn.clicked.connect(self._remove_selected)
        btn_layout.addWidget(self.remove_btn)

        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.setObjectName("secondaryBtn")
        self.clear_btn.clicked.connect(self.file_list.clear)
        btn_layout.addWidget(self.clear_btn)

        btn_layout.addStretch()
        main_content.addLayout(btn_layout)
        layout.addLayout(main_content)

        # Summary Info
        self.info_label = QLabel("0 files selected (0 total pages)")
        self.info_label.setStyleSheet("font-weight: 500; color: #94a3b8;")
        layout.addWidget(self.info_label)

        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(16)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # Bottom buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("secondaryBtn")
        self.cancel_btn.clicked.connect(self.reject)
        bottom_layout.addWidget(self.cancel_btn)

        self.merge_btn = QPushButton("Merge & Save PDF")
        self.merge_btn.clicked.connect(self._on_merge)
        bottom_layout.addWidget(self.merge_btn)

        layout.addLayout(bottom_layout)

    def add_files(self, paths: list):
        for p in paths:
            if not p or not os.path.exists(p) or not p.lower().endswith(".pdf"):
                continue
            # Get page count
            try:
                with fitz.open(p) as doc:
                    pages = len(doc)
                size_mb = os.path.getsize(p) / (1024 * 1024)
                item = QListWidgetItem(f"{os.path.basename(p)}  ({pages} pages, {size_mb:.1f} MB)\n{p}")
                item.setData(Qt.ItemDataRole.UserRole, p)
                self.file_list.addItem(item)
            except Exception as e:
                print(f"Error opening {p}: {e}")
        self._update_summary()

    def _on_add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select PDF files to merge", "", "PDF Files (*.pdf)"
        )
        if files:
            self.add_files(files)

    def _move_up(self):
        row = self.file_list.currentRow()
        if row > 0:
            item = self.file_list.takeItem(row)
            self.file_list.insertItem(row - 1, item)
            self.file_list.setCurrentRow(row - 1)

    def _move_down(self):
        row = self.file_list.currentRow()
        if row >= 0 and row < self.file_list.count() - 1:
            item = self.file_list.takeItem(row)
            self.file_list.insertItem(row + 1, item)
            self.file_list.setCurrentRow(row + 1)

    def _remove_selected(self):
        row = self.file_list.currentRow()
        if row >= 0:
            self.file_list.takeItem(row)
            self._update_summary()

    def _update_summary(self):
        total_files = self.file_list.count()
        total_pages = 0
        for i in range(total_files):
            fpath = self.file_list.item(i).data(Qt.ItemDataRole.UserRole)
            try:
                with fitz.open(fpath) as doc:
                    total_pages += len(doc)
            except Exception:
                pass
        self.info_label.setText(f"{total_files} file(s) selected ({total_pages} total pages)")

    def _on_merge(self):
        total_files = self.file_list.count()
        if total_files < 2:
            QMessageBox.warning(self, "Merge PDFs", "Please add at least 2 PDF files to merge.")
            return

        file_paths = []
        for i in range(total_files):
            file_paths.append(self.file_list.item(i).data(Qt.ItemDataRole.UserRole))

        out_path, _ = QFileDialog.getSaveFileName(
            self, "Save Merged PDF As", "Merged_Document.pdf", "PDF Files (*.pdf)"
        )
        if not out_path:
            return

        self.progress_bar.show()
        self.progress_bar.setRange(0, total_files)
        self.merge_btn.setEnabled(False)

        def progress(curr, total, name):
            self.progress_bar.setValue(curr)

        success, msg = PDFTools.merge_pdfs(file_paths, out_path, progress_callback=progress)

        self.progress_bar.hide()
        self.merge_btn.setEnabled(True)

        if success:
            QMessageBox.information(self, "Merge Successful", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Merge Failed", msg)
