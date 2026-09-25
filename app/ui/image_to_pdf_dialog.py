"""
Images to PDF Dialog for Lumina PDF Reader.
Allows converting image files into a single unified PDF.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QFileDialog,
    QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
import os
from app.core.web_converter import WebConverter

class ImageToPDFDialog(QDialog):
    converted_pdf_ready = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Convert Images to PDF")
        self.resize(560, 420)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Convert Images to PDF Document")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title)

        desc = QLabel("Add images (PNG, JPG, WEBP) and arrange page order:")
        desc.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(desc)

        main_content = QHBoxLayout()
        self.img_list = QListWidget()
        main_content.addWidget(self.img_list, 1)

        btn_box = QVBoxLayout()
        btn_box.setSpacing(8)

        add_btn = QPushButton("Add Images...")
        add_btn.clicked.connect(self._on_add_images)
        btn_box.addWidget(add_btn)

        up_btn = QPushButton("Move Up")
        up_btn.setObjectName("secondaryBtn")
        up_btn.clicked.connect(self._move_up)
        btn_box.addWidget(up_btn)

        down_btn = QPushButton("Move Down")
        down_btn.setObjectName("secondaryBtn")
        down_btn.clicked.connect(self._move_down)
        btn_box.addWidget(down_btn)

        remove_btn = QPushButton("Remove")
        remove_btn.setObjectName("secondaryBtn")
        remove_btn.clicked.connect(self._remove_selected)
        btn_box.addWidget(remove_btn)

        btn_box.addStretch()
        main_content.addLayout(btn_box)
        layout.addLayout(main_content)

        self.summary_lbl = QLabel("0 images selected")
        self.summary_lbl.setStyleSheet("color: #94a3b8;")
        layout.addWidget(self.summary_lbl)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(14)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # Bottom Buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.clicked.connect(self.reject)
        bottom_layout.addWidget(cancel_btn)

        self.convert_btn = QPushButton("Convert & Save PDF")
        self.convert_btn.clicked.connect(self._on_convert)
        bottom_layout.addWidget(self.convert_btn)

        layout.addLayout(bottom_layout)

    def _on_add_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "", "Image Files (*.png *.jpg *.jpeg *.webp *.bmp)"
        )
        if files:
            for f in files:
                item = QListWidgetItem(f"{os.path.basename(f)}\n{f}")
                item.setData(Qt.ItemDataRole.UserRole, f)
                self.img_list.addItem(item)
            self.summary_lbl.setText(f"{self.img_list.count()} image(s) selected")

    def _move_up(self):
        row = self.img_list.currentRow()
        if row > 0:
            item = self.img_list.takeItem(row)
            self.img_list.insertItem(row - 1, item)
            self.img_list.setCurrentRow(row - 1)

    def _move_down(self):
        row = self.img_list.currentRow()
        if row >= 0 and row < self.img_list.count() - 1:
            item = self.img_list.takeItem(row)
            self.img_list.insertItem(row + 1, item)
            self.img_list.setCurrentRow(row + 1)

    def _remove_selected(self):
        row = self.img_list.currentRow()
        if row >= 0:
            self.img_list.takeItem(row)
            self.summary_lbl.setText(f"{self.img_list.count()} image(s) selected")

    def _on_convert(self):
        count = self.img_list.count()
        if count == 0:
            QMessageBox.warning(self, "No Images", "Please add at least one image to convert.")
            return

        out_file, _ = QFileDialog.getSaveFileName(
            self, "Save Converted PDF As", "Images_Document.pdf", "PDF Files (*.pdf)"
        )
        if not out_file:
            return

        paths = [self.img_list.item(i).data(Qt.ItemDataRole.UserRole) for i in range(count)]

        self.progress_bar.show()
        self.progress_bar.setRange(0, count)
        self.convert_btn.setEnabled(False)

        def progress(curr, total):
            self.progress_bar.setValue(curr)

        success, msg = WebConverter.convert_images_to_pdf(paths, out_file, progress_callback=progress)

        self.progress_bar.hide()
        self.convert_btn.setEnabled(True)

        if success:
            QMessageBox.information(self, "Success", msg)
            self.converted_pdf_ready.emit(out_file)
            self.accept()
        else:
            QMessageBox.critical(self, "Error", msg)
