"""
Main Window for Lumina PDF Reader.
Coordinates the UI, Viewer, Sidebar, Dialogs, Themes, and Shortcuts.
"""
import os
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QToolBar,
    QFileDialog, QMessageBox, QLabel, QLineEdit, QSpinBox,
    QComboBox, QSplitter, QStatusBar, QMenuBar, QMenu,
    QApplication, QToolButton, QButtonGroup, QDialog
)
from PyQt6.QtCore import Qt, QSize, QUrl
from PyQt6.QtGui import QAction, QActionGroup, QIcon, QKeySequence, QDragEnterEvent, QDropEvent

from app.core.pdf_document import PDFDocument
from app.core.settings import AppSettings
from app.ui.viewer_widget import PDFViewerWidget
from app.ui.sidebar_widget import SidebarWidget
from app.ui.merge_dialog import MergePDFDialog
from app.ui.split_dialog import SplitPDFDialog
from app.ui.styles import get_theme_stylesheet

class MainWindow(QMainWindow):
    def __init__(self, initial_file: str = None):
        super().__init__()
        self.setWindowTitle("Lumina PDF Reader")
        self.resize(1200, 850)
        self.setMinimumSize(800, 600)
        self.setAcceptDrops(True)

        self.settings = AppSettings()
        self.current_doc: PDFDocument = PDFDocument()

        self._init_ui()
        self._load_saved_settings()

        if initial_file and os.path.exists(initial_file):
            self.open_pdf(initial_file)

    def _init_ui(self):
        # Central Widget & Splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Sidebar
        self.sidebar = SidebarWidget(self)
        self.sidebar.page_selected.connect(self._on_sidebar_page_selected)
        self.sidebar.search_result_selected.connect(self._on_search_result_selected)
        self.splitter.addWidget(self.sidebar)

        # Viewer
        self.viewer = PDFViewerWidget(self)
        self.viewer.page_changed.connect(self._on_page_changed)
        self.viewer.zoom_changed.connect(self._on_zoom_changed)
        self.splitter.addWidget(self.viewer)

        # Set splitter sizes (280px sidebar, remainder viewer)
        self.splitter.setSizes([280, 920])
        self.setCentralWidget(self.splitter)

        # Build MenuBar, ToolBar, StatusBar
        self._create_menu_bar()
        self._create_toolbar()
        self._create_status_bar()

    def _create_menu_bar(self):
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open PDF...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._on_open_file_dialog)
        file_menu.addAction(open_action)

        self.recent_menu = file_menu.addMenu("Recent &Files")
        self._update_recent_files_menu()

        file_menu.addSeparator()

        save_as_action = QAction("Save &Copy As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self._on_save_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View Menu
        view_menu = menubar.addMenu("&View")

        self.toggle_sidebar_action = QAction("Toggle &Sidebar", self)
        self.toggle_sidebar_action.setShortcut(QKeySequence("Ctrl+B"))
        self.toggle_sidebar_action.setCheckable(True)
        self.toggle_sidebar_action.setChecked(True)
        self.toggle_sidebar_action.triggered.connect(self._toggle_sidebar)
        view_menu.addAction(self.toggle_sidebar_action)

        view_menu.addSeparator()

        # View modes
        self.act_book_mode = QAction("📖 &Book Mode (Two Pages)", self)
        self.act_book_mode.setCheckable(True)
        self.act_book_mode.triggered.connect(lambda: self.set_view_mode("book"))
        view_menu.addAction(self.act_book_mode)

        self.act_single_mode = QAction("📄 &Single Page Mode", self)
        self.act_single_mode.setCheckable(True)
        self.act_single_mode.triggered.connect(lambda: self.set_view_mode("single"))
        view_menu.addAction(self.act_single_mode)

        self.act_cont_mode = QAction("📜 &Continuous Scroll Mode", self)
        self.act_cont_mode.setCheckable(True)
        self.act_cont_mode.triggered.connect(lambda: self.set_view_mode("continuous"))
        view_menu.addAction(self.act_cont_mode)

        view_mode_group = QActionGroup(self)
        view_mode_group.addAction(self.act_book_mode)
        view_mode_group.addAction(self.act_single_mode)
        view_mode_group.addAction(self.act_cont_mode)

        view_menu.addSeparator()

        self.act_cover_offset = QAction("First Page as Book &Cover Alone", self)
        self.act_cover_offset.setCheckable(True)
        self.act_cover_offset.setChecked(True)
        self.act_cover_offset.triggered.connect(self._toggle_cover_offset)
        view_menu.addAction(self.act_cover_offset)

        view_menu.addSeparator()

        fullscreen_action = QAction("&Full Screen", self)
        fullscreen_action.setShortcut(QKeySequence("F11"))
        fullscreen_action.triggered.connect(self._toggle_fullscreen)
        view_menu.addAction(fullscreen_action)

        # Tools Menu
        tools_menu = menubar.addMenu("&Tools")

        merge_action = QAction("🔀 &Merge Multiple PDFs...", self)
        merge_action.triggered.connect(self._open_merge_dialog)
        tools_menu.addAction(merge_action)

        split_action = QAction("✂️ &Split / Extract PDF...", self)
        split_action.triggered.connect(self._open_split_dialog)
        tools_menu.addAction(split_action)

        tools_menu.addSeparator()

        rot_cw = QAction("Rotate Clockwise (90°)", self)
        rot_cw.setShortcut(QKeySequence("Ctrl+R"))
        rot_cw.triggered.connect(self.viewer.rotate_clockwise)
        tools_menu.addAction(rot_cw)

        rot_ccw = QAction("Rotate Counter-Clockwise (90°)", self)
        rot_ccw.setShortcut(QKeySequence("Ctrl+Shift+R"))
        rot_ccw.triggered.connect(self.viewer.rotate_counter_clockwise)
        tools_menu.addAction(rot_ccw)

        # Theme Menu
        theme_menu = menubar.addMenu("&Theme")

        self.act_theme_dark = QAction("🌙 Dark Mode", self)
        self.act_theme_dark.setCheckable(True)
        self.act_theme_dark.triggered.connect(lambda: self.set_theme("dark"))
        theme_menu.addAction(self.act_theme_dark)

        self.act_theme_light = QAction("☀️ Light Mode", self)
        self.act_theme_light.setCheckable(True)
        self.act_theme_light.triggered.connect(lambda: self.set_theme("light"))
        theme_menu.addAction(self.act_theme_light)

        self.act_theme_sepia = QAction("📜 Sepia Warm Paper", self)
        self.act_theme_sepia.setCheckable(True)
        self.act_theme_sepia.triggered.connect(lambda: self.set_theme("sepia"))
        theme_menu.addAction(self.act_theme_sepia)

        theme_group = QActionGroup(self)
        theme_group.addAction(self.act_theme_dark)
        theme_group.addAction(self.act_theme_light)
        theme_group.addAction(self.act_theme_sepia)

        # Help Menu
        help_menu = menubar.addMenu("&Help")
        about_action = QAction("&About Lumina PDF", self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)

    def _create_toolbar(self):
        self.toolbar = QToolBar("Main Navigation")
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(self.toolbar)

        # Open File Button
        self.btn_open = QToolButton()
        self.btn_open.setText("📂 Open")
        self.btn_open.setToolTip("Open PDF Document (Ctrl+O)")
        self.btn_open.clicked.connect(self._on_open_file_dialog)
        self.toolbar.addWidget(self.btn_open)

        # Toggle Sidebar
        self.btn_sidebar = QToolButton()
        self.btn_sidebar.setText("📑 Sidebar")
        self.btn_sidebar.setCheckable(True)
        self.btn_sidebar.setChecked(True)
        self.btn_sidebar.setToolTip("Toggle Thumbnails & Outline Sidebar (Ctrl+B)")
        self.btn_sidebar.clicked.connect(self._toggle_sidebar)
        self.toolbar.addWidget(self.btn_sidebar)

        self.toolbar.addSeparator()

        # Page Navigation
        self.btn_first = QToolButton()
        self.btn_first.setText("⏮")
        self.btn_first.setToolTip("First Page (Home)")
        self.btn_first.clicked.connect(self.viewer.first_page)
        self.toolbar.addWidget(self.btn_first)

        self.btn_prev = QToolButton()
        self.btn_prev.setText("◀ Prev")
        self.btn_prev.setToolTip("Previous Page (Left Arrow / PageUp)")
        self.btn_prev.clicked.connect(self.viewer.prev_page)
        self.toolbar.addWidget(self.btn_prev)

        # Page Number input
        self.page_spin = QSpinBox()
        self.page_spin.setRange(1, 1)
        self.page_spin.setFixedWidth(65)
        self.page_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_spin.valueChanged.connect(self._on_spin_page_changed)
        self.toolbar.addWidget(self.page_spin)

        self.lbl_total_pages = QLabel(" / 0 ")
        self.lbl_total_pages.setStyleSheet("color: #94a3b8; font-weight: bold; margin-right: 4px;")
        self.toolbar.addWidget(self.lbl_total_pages)

        self.btn_next = QToolButton()
        self.btn_next.setText("Next ▶")
        self.btn_next.setToolTip("Next Page (Right Arrow / Space / PageDown)")
        self.btn_next.clicked.connect(self.viewer.next_page)
        self.toolbar.addWidget(self.btn_next)

        self.btn_last = QToolButton()
        self.btn_last.setText("⏭")
        self.btn_last.setToolTip("Last Page (End)")
        self.btn_last.clicked.connect(self.viewer.last_page)
        self.toolbar.addWidget(self.btn_last)

        self.toolbar.addSeparator()

        # View Mode Selector Buttons
        self.tb_book_mode = QToolButton()
        self.tb_book_mode.setText("📖 Book View")
        self.tb_book_mode.setCheckable(True)
        self.tb_book_mode.setToolTip("Two-Page Spread Book Reading Mode")
        self.tb_book_mode.clicked.connect(lambda: self.set_view_mode("book"))
        self.toolbar.addWidget(self.tb_book_mode)

        self.tb_single_mode = QToolButton()
        self.tb_single_mode.setText("📄 Single Page")
        self.tb_single_mode.setCheckable(True)
        self.tb_single_mode.setToolTip("Single Page View")
        self.tb_single_mode.clicked.connect(lambda: self.set_view_mode("single"))
        self.toolbar.addWidget(self.tb_single_mode)

        self.tb_cont_mode = QToolButton()
        self.tb_cont_mode.setText("📜 Continuous")
        self.tb_cont_mode.setCheckable(True)
        self.tb_cont_mode.setToolTip("Continuous Scroll View")
        self.tb_cont_mode.clicked.connect(lambda: self.set_view_mode("continuous"))
        self.toolbar.addWidget(self.tb_cont_mode)

        self.toolbar.addSeparator()

        # Zoom Controls
        self.btn_zoom_out = QToolButton()
        self.btn_zoom_out.setText("🔍-")
        self.btn_zoom_out.setToolTip("Zoom Out (Ctrl -)")
        self.btn_zoom_out.clicked.connect(self.viewer.zoom_out)
        self.toolbar.addWidget(self.btn_zoom_out)

        self.zoom_combo = QComboBox()
        self.zoom_combo.setFixedWidth(105)
        self.zoom_combo.addItems(["Fit Page", "Fit Width", "50%", "75%", "100%", "125%", "150%", "200%"])
        self.zoom_combo.currentTextChanged.connect(self._on_zoom_combo_changed)
        self.toolbar.addWidget(self.zoom_combo)

        self.btn_zoom_in = QToolButton()
        self.btn_zoom_in.setText("🔍+")
        self.btn_zoom_in.setToolTip("Zoom In (Ctrl +)")
        self.btn_zoom_in.clicked.connect(self.viewer.zoom_in)
        self.toolbar.addWidget(self.btn_zoom_in)

        self.toolbar.addSeparator()

        # PDF Tools Buttons
        self.btn_merge = QToolButton()
        self.btn_merge.setText("🔀 Merge")
        self.btn_merge.setToolTip("Merge Multiple PDFs into One")
        self.btn_merge.clicked.connect(self._open_merge_dialog)
        self.toolbar.addWidget(self.btn_merge)

        self.btn_split = QToolButton()
        self.btn_split.setText("✂️ Split")
        self.btn_split.setToolTip("Split or Extract PDF Pages")
        self.btn_split.clicked.connect(self._open_split_dialog)
        self.toolbar.addWidget(self.btn_split)

        self.toolbar.addSeparator()

        # Theme Switcher Selector
        self.theme_combo = QComboBox()
        self.theme_combo.setFixedWidth(110)
        self.theme_combo.addItems(["🌙 Dark", "☀️ Light", "📜 Sepia"])
        self.theme_combo.currentIndexChanged.connect(self._on_theme_combo_changed)
        self.toolbar.addWidget(self.theme_combo)

    def _create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.lbl_status_msg = QLabel("Ready")
        self.lbl_status_zoom = QLabel("Zoom: 100%")
        self.lbl_status_file = QLabel("")

        self.status_bar.addWidget(self.lbl_status_msg, 1)
        self.status_bar.addPermanentWidget(self.lbl_status_zoom)
        self.status_bar.addPermanentWidget(self.lbl_status_file)

    def _load_saved_settings(self):
        # Apply theme
        theme = self.settings.theme
        self.set_theme(theme)

        # Apply view mode
        mode = self.settings.view_mode
        self.set_view_mode(mode)

        # Apply book cover offset
        offset = self.settings.book_cover_offset
        self.act_cover_offset.setChecked(offset)
        self.viewer.set_book_cover_offset(offset)

        # Apply sidebar visibility
        side_vis = self.settings.sidebar_visible
        self.sidebar.setVisible(side_vis)
        self.btn_sidebar.setChecked(side_vis)
        self.toggle_sidebar_action.setChecked(side_vis)

    def open_pdf(self, file_path: str):
        if not file_path or not os.path.exists(file_path):
            return

        success = self.current_doc.load(file_path)
        if not success:
            QMessageBox.critical(self, "Error Opening PDF", f"Failed to open PDF document:\n{file_path}")
            return

        self.viewer.set_document(self.current_doc)
        self.sidebar.set_document(self.current_doc)

        total_pages = self.current_doc.page_count
        self.page_spin.blockSignals(True)
        self.page_spin.setRange(1, max(1, total_pages))
        self.page_spin.setValue(1)
        self.page_spin.blockSignals(False)

        self.lbl_total_pages.setText(f" / {total_pages} ")
        self.lbl_status_file.setText(f"📄 {os.path.basename(file_path)} ({total_pages} pages)")
        self.lbl_status_msg.setText(f"Opened: {os.path.basename(file_path)}")
        self.setWindowTitle(f"{os.path.basename(file_path)} - Lumina PDF Reader")

        self.settings.add_recent_file(file_path)
        self._update_recent_files_menu()

    def _on_open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open PDF Document", "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.open_pdf(file_path)

    def _on_save_as(self):
        if not self.current_doc or not self.current_doc.is_valid():
            return
        out_path, _ = QFileDialog.getSaveFileName(
            self, "Save Copy As", "Copy_" + os.path.basename(self.current_doc.file_path or "Document.pdf"), "PDF Files (*.pdf)"
        )
        if out_path:
            try:
                self.current_doc.doc.save(out_path, deflate=True)
                QMessageBox.information(self, "Saved", f"Document saved successfully to:\n{out_path}")
            except Exception as e:
                QMessageBox.critical(self, "Save Failed", f"Could not save document: {e}")

    def _update_recent_files_menu(self):
        self.recent_menu.clear()
        recent = self.settings.recent_files
        if not recent:
            no_rec = QAction("No Recent Files", self)
            no_rec.setEnabled(False)
            self.recent_menu.addAction(no_rec)
            return

        for fpath in recent:
            act = QAction(os.path.basename(fpath), self)
            act.setToolTip(fpath)
            act.setData(fpath)
            act.triggered.connect(lambda checked, p=fpath: self.open_pdf(p))
            self.recent_menu.addAction(act)

        self.recent_menu.addSeparator()
        clear_act = QAction("Clear Recent Files", self)
        clear_act.triggered.connect(self._clear_recent_files)
        self.recent_menu.addAction(clear_act)

    def _clear_recent_files(self):
        self.settings.clear_recent_files()
        self._update_recent_files_menu()

    def set_theme(self, theme_name: str):
        if theme_name not in ["dark", "light", "sepia"]:
            theme_name = "dark"

        self.settings.theme = theme_name
        self.setStyleSheet(get_theme_stylesheet(theme_name))
        self.viewer.set_theme(theme_name)

        # Update Theme Combo
        idx_map = {"dark": 0, "light": 1, "sepia": 2}
        self.theme_combo.blockSignals(True)
        self.theme_combo.setCurrentIndex(idx_map.get(theme_name, 0))
        self.theme_combo.blockSignals(False)

        # Update Menu actions
        self.act_theme_dark.setChecked(theme_name == "dark")
        self.act_theme_light.setChecked(theme_name == "light")
        self.act_theme_sepia.setChecked(theme_name == "sepia")

    def _on_theme_combo_changed(self, index: int):
        themes = ["dark", "light", "sepia"]
        if 0 <= index < len(themes):
            self.set_theme(themes[index])

    def set_view_mode(self, mode: str):
        self.settings.view_mode = mode
        self.viewer.set_view_mode(mode)

        # Update Toolbar Buttons
        self.tb_book_mode.setChecked(mode == "book")
        self.tb_single_mode.setChecked(mode == "single")
        self.tb_cont_mode.setChecked(mode == "continuous")

        # Update Menu actions
        self.act_book_mode.setChecked(mode == "book")
        self.act_single_mode.setChecked(mode == "single")
        self.act_cont_mode.setChecked(mode == "continuous")

    def _toggle_cover_offset(self, checked: bool):
        self.settings.book_cover_offset = checked
        self.viewer.set_book_cover_offset(checked)

    def _toggle_sidebar(self):
        is_visible = not self.sidebar.isVisible()
        self.sidebar.setVisible(is_visible)
        self.btn_sidebar.setChecked(is_visible)
        self.toggle_sidebar_action.setChecked(is_visible)
        self.settings.sidebar_visible = is_visible

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _on_page_changed(self, current_page: int, total_pages: int):
        self.page_spin.blockSignals(True)
        self.page_spin.setValue(current_page + 1)
        self.page_spin.blockSignals(False)
        self.lbl_total_pages.setText(f" / {total_pages} ")
        self.sidebar.set_current_page(current_page)

    def _on_spin_page_changed(self, value: int):
        self.viewer.go_to_page(value - 1)

    def _on_zoom_changed(self, zoom: float):
        pct = int(zoom * 100)
        self.lbl_status_zoom.setText(f"Zoom: {pct}%")
        self.zoom_combo.blockSignals(True)
        self.zoom_combo.setEditText(f"{pct}%")
        self.zoom_combo.blockSignals(False)

    def _on_zoom_combo_changed(self, text: str):
        if text == "Fit Page":
            self.viewer.set_zoom_mode("fit_page")
        elif text == "Fit Width":
            self.viewer.set_zoom_mode("fit_width")
        else:
            try:
                val = float(text.replace("%", "").strip()) / 100.0
                self.viewer.set_zoom(val, custom=True)
            except ValueError:
                pass

    def _on_sidebar_page_selected(self, page_num: int):
        self.viewer.go_to_page(page_num)

    def _on_search_result_selected(self, page_num: int, rects: list):
        self.viewer.highlight_search_results(page_num, rects)

    def _open_merge_dialog(self):
        initial = [self.current_doc.file_path] if self.current_doc and self.current_doc.file_path else []
        dlg = MergePDFDialog(self, initial_files=initial)
        dlg.exec()

    def _open_split_dialog(self):
        curr_path = self.current_doc.file_path if self.current_doc and self.current_doc.file_path else ""
        dlg = SplitPDFDialog(self, pdf_path=curr_path)
        dlg.exec()

    def _show_about_dialog(self):
        QMessageBox.about(
            self,
            "About Lumina PDF Reader",
            "<h2>Lumina PDF Reader & Tools</h2>"
            "<p><b>Version 1.0.0</b></p>"
            "<p>A modern, lightweight Windows PDF reader with book reading mode, "
            "dark & light themes, and built-in PDF merge & split tools.</p>"
            "<p>Powered by PyQt6 and PyMuPDF.</p>"
        )

    # Drag & Drop Support
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(".pdf"):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            fpath = url.toLocalFile()
            if fpath.lower().endswith(".pdf") and os.path.exists(fpath):
                self.open_pdf(fpath)
                event.acceptProposedAction()
                break
