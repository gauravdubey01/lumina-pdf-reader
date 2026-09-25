"""
Tab Manager for multi-document PDF viewing in Lumina PDF Reader.
"""
from PyQt6.QtWidgets import (
    QWidget, QTabWidget, QVBoxLayout, QTabBar,
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import pyqtSignal, Qt
from app.core.pdf_document import PDFDocument
from app.ui.viewer_widget import PDFViewerWidget
from typing import Optional, List
import os

class DocumentTab(QWidget):
    def __init__(self, file_path: str = None, password: str = None, parent=None):
        super().__init__(parent)
        self.doc = PDFDocument(file_path, password)
        self.viewer = PDFViewerWidget(self)
        if file_path:
            self.viewer.set_document(self.doc)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.viewer)

class TabManager(QTabWidget):
    active_document_changed = pyqtSignal(object, object) # (doc, viewer)
    tab_count_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.currentChanged.connect(self._on_tab_changed)

    def open_document(self, file_path: str, password: str = None) -> Optional[DocumentTab]:
        # Check if file is already open
        norm_path = os.path.abspath(file_path)
        for idx in range(self.count()):
            tab = self.widget(idx)
            if isinstance(tab, DocumentTab) and tab.doc.file_path:
                if os.path.abspath(tab.doc.file_path) == norm_path:
                    self.setCurrentIndex(idx)
                    return tab

        tab = DocumentTab(file_path, password, self)
        if not tab.doc.is_valid():
            return None

        tab_title = os.path.basename(file_path)
        idx = self.addTab(tab, tab_title)
        self.setTabToolTip(idx, file_path)
        self.setCurrentIndex(idx)
        self.tab_count_changed.emit(self.count())

        # Listen for document modification to show dirty indicator *
        tab.doc.document_modified.connect(lambda: self._on_doc_modified(tab))
        return tab

    def get_current_tab(self) -> Optional[DocumentTab]:
        w = self.currentWidget()
        if isinstance(w, DocumentTab):
            return w
        return None

    def get_current_document(self) -> Optional[PDFDocument]:
        tab = self.get_current_tab()
        return tab.doc if tab else None

    def get_current_viewer(self) -> Optional[PDFViewerWidget]:
        tab = self.get_current_tab()
        return tab.viewer if tab else None

    def _on_doc_modified(self, tab: DocumentTab):
        idx = self.indexOf(tab)
        if idx >= 0 and tab.doc.file_path:
            title = os.path.basename(tab.doc.file_path)
            if tab.doc.is_modified:
                self.setTabText(idx, f"● {title}")
            else:
                self.setTabText(idx, title)

    def _on_tab_changed(self, index: int):
        tab = self.get_current_tab()
        if tab:
            self.active_document_changed.emit(tab.doc, tab.viewer)
        else:
            self.active_document_changed.emit(None, None)

    def close_tab(self, index: int) -> bool:
        tab = self.widget(index)
        if isinstance(tab, DocumentTab):
            if tab.doc.is_modified:
                ret = QMessageBox.question(
                    self, "Unsaved Changes",
                    f"The document '{tab.doc.title}' has unsaved annotations.\nSave changes before closing?",
                    QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
                )
                if ret == QMessageBox.StandardButton.Save:
                    tab.doc.save_document()
                elif ret == QMessageBox.StandardButton.Cancel:
                    return False

            tab.doc.close()
            self.removeTab(index)
            tab.deleteLater()
            self.tab_count_changed.emit(self.count())
            return True
        return False

    def close_current_tab(self) -> bool:
        curr = self.currentIndex()
        if curr >= 0:
            return self.close_tab(curr)
        return False
