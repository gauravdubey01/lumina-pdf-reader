"""
Sidebar Widget containing Page Thumbnails, Bookmarks (TOC), and Full-Text Search.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem,
    QLineEdit, QPushButton, QLabel, QProgressBar, QAbstractItemView,
    QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QIcon
from app.core.pdf_document import PDFDocument
from typing import Optional, List, Dict, Any

class SidebarWidget(QWidget):
    page_selected = pyqtSignal(int)  # 0-indexed page
    search_result_selected = pyqtSignal(int, list)  # page_num, rects

    def __init__(self, parent=None):
        super().__init__(parent)
        self.doc: Optional[PDFDocument] = None

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)

        # Tab 1: Thumbnails
        self.thumb_tab = QWidget()
        thumb_layout = QVBoxLayout(self.thumb_tab)
        thumb_layout.setContentsMargins(2, 4, 2, 4)
        self.thumb_list = QListWidget()
        self.thumb_list.setIconSize(QSize(130, 170))
        self.thumb_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.thumb_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.thumb_list.setMovement(QListWidget.Movement.Static)
        self.thumb_list.setSpacing(10)
        self.thumb_list.itemClicked.connect(self._on_thumbnail_clicked)
        thumb_layout.addWidget(self.thumb_list)

        # Tab 2: Bookmarks / Outline
        self.outline_tab = QWidget()
        outline_layout = QVBoxLayout(self.outline_tab)
        outline_layout.setContentsMargins(2, 4, 2, 4)
        self.outline_tree = QTreeWidget()
        self.outline_tree.setHeaderHidden(True)
        self.outline_tree.itemClicked.connect(self._on_outline_clicked)
        self.no_outline_label = QLabel("No Table of Contents in document")
        self.no_outline_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_outline_label.setStyleSheet("color: #94a3b8; font-style: italic; padding: 20px;")
        self.no_outline_label.hide()
        outline_layout.addWidget(self.outline_tree)
        outline_layout.addWidget(self.no_outline_label)

        # Tab 3: Search
        self.search_tab = QWidget()
        search_layout = QVBoxLayout(self.search_tab)
        search_layout.setContentsMargins(4, 4, 4, 4)
        search_layout.setSpacing(6)

        search_input_layout = QHBoxLayout()
        search_input_layout.setSpacing(4)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search document text...")
        self.search_input.returnPressed.connect(self.perform_search)
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.perform_search)
        search_input_layout.addWidget(self.search_input)
        search_input_layout.addWidget(self.search_btn)
        search_layout.addLayout(search_input_layout)

        self.search_status_label = QLabel("")
        self.search_status_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
        search_layout.addWidget(self.search_status_label)

        self.search_results_list = QListWidget()
        self.search_results_list.itemClicked.connect(self._on_search_item_clicked)
        search_layout.addWidget(self.search_results_list)

        # Add tabs
        self.tabs.addTab(self.thumb_tab, "Pages")
        self.tabs.addTab(self.outline_tab, "Outline")
        self.tabs.addTab(self.search_tab, "Search")

        layout.addWidget(self.tabs)
        self.setMinimumWidth(230)
        self.setMaximumWidth(360)

    def set_document(self, doc: Optional[PDFDocument]):
        self.doc = doc
        self.thumb_list.clear()
        self.outline_tree.clear()
        self.search_results_list.clear()
        self.search_status_label.setText("")

        if not self.doc or not self.doc.is_valid():
            self.no_outline_label.hide()
            return

        self._populate_thumbnails()
        self._populate_outline()

    def _populate_thumbnails(self):
        if not self.doc:
            return
        total = self.doc.page_count
        for i in range(total):
            item = QListWidgetItem(f"Page {i + 1}")
            item.setData(Qt.ItemDataRole.UserRole, i)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # Render low-res thumbnail
            pix = self.doc.render_thumbnail(i, width=120)
            if not pix.isNull():
                item.setIcon(QIcon(pix))
            self.thumb_list.addItem(item)

    def _populate_outline(self):
        if not self.doc:
            return
        outline = self.doc.get_outline()
        if not outline:
            self.outline_tree.hide()
            self.no_outline_label.show()
            return

        self.no_outline_label.hide()
        self.outline_tree.show()

        level_stack = [self.outline_tree]

        for item in outline:
            level = item["level"]
            title = item["title"]
            page = item["page"]

            tree_item = QTreeWidgetItem([title])
            tree_item.setData(0, Qt.ItemDataRole.UserRole, page)

            # Adjust stack for nesting
            while len(level_stack) > level:
                level_stack.pop()

            parent = level_stack[-1]
            if isinstance(parent, QTreeWidget):
                parent.addTopLevelItem(tree_item)
            else:
                parent.addChild(tree_item)

            level_stack.append(tree_item)

        self.outline_tree.expandToDepth(1)

    def perform_search(self):
        query = self.search_input.text().strip()
        if not self.doc or not self.doc.is_valid() or not query:
            return

        self.search_results_list.clear()
        self.search_status_label.setText("Searching...")

        results = self.doc.search_text(query)
        total_occurrences = sum(r["count"] for r in results)

        if not results:
            self.search_status_label.setText("No matches found.")
            return

        self.search_status_label.setText(f"Found {total_occurrences} matches on {len(results)} pages.")

        for r in results:
            p_no = r["page"]
            snippet = r["snippet"]
            item = QListWidgetItem(f"Page {p_no + 1} ({r['count']} match)\n{snippet}")
            item.setData(Qt.ItemDataRole.UserRole, (p_no, r["rects"]))
            self.search_results_list.addItem(item)

    def set_current_page(self, page_num: int):
        # Highlight corresponding thumbnail
        if page_num < self.thumb_list.count():
            self.thumb_list.blockSignals(True)
            self.thumb_list.setCurrentRow(page_num)
            item = self.thumb_list.item(page_num)
            if item:
                self.thumb_list.scrollToItem(item, QAbstractItemView.ScrollHint.EnsureVisible)
            self.thumb_list.blockSignals(False)

    def _on_thumbnail_clicked(self, item: QListWidgetItem):
        page = item.data(Qt.ItemDataRole.UserRole)
        if page is not None:
            self.page_selected.emit(page)

    def _on_outline_clicked(self, item: QTreeWidgetItem, column: int):
        page = item.data(0, Qt.ItemDataRole.UserRole)
        if page is not None:
            self.page_selected.emit(page)

    def _on_search_item_clicked(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            page, rects = data
            self.search_result_selected.emit(page, rects)
