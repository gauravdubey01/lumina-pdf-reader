"""
Main Window for Lumina PDF Reader.
Professional Desktop Application with Multi-Tab Management, Tool Ribbons,
Annotations, Printing, Password Security, Export, Shortcuts, and Status Stats.
"""
import os
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QToolBar,
    QFileDialog, QMessageBox, QLabel, QLineEdit, QSpinBox,
    QComboBox, QSplitter, QStatusBar, QMenuBar, QMenu,
    QApplication, QToolButton, QSlider, QDialog
)
from PyQt6.QtCore import Qt, QSize, QUrl
from typing import Optional, List, Dict, Any
from PyQt6.QtGui import QAction, QActionGroup, QIcon, QKeySequence, QDragEnterEvent, QDropEvent

from app.core.pdf_document import PDFDocument
from app.core.settings import AppSettings
from app.core.print_manager import PrintManager
from app.ui.viewer_widget import PDFViewerWidget, ToolMode
from app.ui.sidebar_widget import SidebarWidget
from app.ui.tab_manager import TabManager, DocumentTab
from app.ui.merge_dialog import MergePDFDialog
from app.ui.split_dialog import SplitPDFDialog
from app.ui.password_dialog import PasswordDialog
from app.ui.security_dialog import SecurityDialog
from app.ui.export_dialog import ExportDialog
from app.ui.web_to_pdf_dialog import WebToPDFDialog
from app.ui.image_to_pdf_dialog import ImageToPDFDialog
from app.ui.shortcuts_dialog import ShortcutsDialog
from app.ui.styles import get_theme_stylesheet

class MainWindow(QMainWindow):
    def __init__(self, initial_file: str = None):
        super().__init__()
        self.setWindowTitle("Lumina PDF Reader")
        self.resize(1260, 880)
        self.setMinimumSize(850, 600)
        self.setAcceptDrops(True)

        self.settings = AppSettings()

        self._init_ui()
        self._load_saved_settings()

        if initial_file and os.path.exists(initial_file):
            self.open_pdf(initial_file)

    def _init_ui(self):
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Sidebar (Thumbnails, Outline, Search)
        self.sidebar = SidebarWidget(self)
        self.sidebar.page_selected.connect(self._on_sidebar_page_selected)
        self.sidebar.search_result_selected.connect(self._on_search_result_selected)
        self.sidebar.document_structure_changed.connect(self._on_doc_structure_changed)
        self.splitter.addWidget(self.sidebar)

        # Central Tab Manager
        self.tab_manager = TabManager(self)
        self.tab_manager.active_document_changed.connect(self._on_active_doc_changed)
        self.tab_manager.tab_count_changed.connect(self._on_tab_count_changed)
        self.splitter.addWidget(self.tab_manager)

        self.splitter.setSizes([280, 980])
        self.setCentralWidget(self.splitter)

        self._create_menu_bar()
        self._create_toolbar()
        self._create_status_bar()

    @property
    def current_doc(self) -> Optional[PDFDocument]:
        return self.tab_manager.get_current_document()

    @property
    def current_viewer(self) -> Optional[PDFViewerWidget]:
        return self.tab_manager.get_current_viewer()

    def _create_menu_bar(self):
        menubar = self.menuBar()

        # ----------------- File Menu -----------------
        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open PDF...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._on_open_file_dialog)
        file_menu.addAction(open_action)

        new_tab_action = QAction("Open in &New Tab", self)
        new_tab_action.setShortcut(QKeySequence("Ctrl+T"))
        new_tab_action.triggered.connect(self._on_open_file_dialog)
        file_menu.addAction(new_tab_action)

        self.recent_menu = file_menu.addMenu("Recent &Files")
        self._update_recent_files_menu()

        file_menu.addSeparator()

        save_action = QAction("&Save Annotations", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._on_save_document)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &Copy As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self._on_save_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        export_action = QAction("&Export Pages / Text...", self)
        export_action.triggered.connect(self._open_export_dialog)
        file_menu.addAction(export_action)

        web_to_pdf_act = QAction("🌐 &Convert Webpage to PDF...", self)
        web_to_pdf_act.setShortcut(QKeySequence("Ctrl+Shift+W"))
        web_to_pdf_act.triggered.connect(self._open_web_to_pdf_dialog)
        file_menu.addAction(web_to_pdf_act)

        print_action = QAction("&Print...", self)
        print_action.setShortcut(QKeySequence.StandardKey.Print)
        print_action.triggered.connect(self._on_print)
        file_menu.addAction(print_action)

        file_menu.addSeparator()

        close_tab_action = QAction("&Close Tab", self)
        close_tab_action.setShortcut(QKeySequence("Ctrl+W"))
        close_tab_action.triggered.connect(self.tab_manager.close_current_tab)
        file_menu.addAction(close_tab_action)

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # ----------------- View Menu -----------------
        view_menu = menubar.addMenu("&View")

        self.toggle_sidebar_action = QAction("Toggle &Sidebar", self)
        self.toggle_sidebar_action.setShortcut(QKeySequence("Ctrl+B"))
        self.toggle_sidebar_action.setCheckable(True)
        self.toggle_sidebar_action.setChecked(True)
        self.toggle_sidebar_action.triggered.connect(self._toggle_sidebar)
        view_menu.addAction(self.toggle_sidebar_action)

        view_menu.addSeparator()

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

        auto_scroll_act = QAction("Toggle &Auto-Scroll", self)
        auto_scroll_act.setShortcut(QKeySequence("Shift+Space"))
        auto_scroll_act.triggered.connect(self._toggle_auto_scroll)
        view_menu.addAction(auto_scroll_act)

        fullscreen_action = QAction("&Full Screen", self)
        fullscreen_action.setShortcut(QKeySequence("F11"))
        fullscreen_action.triggered.connect(self._toggle_fullscreen)
        view_menu.addAction(fullscreen_action)

        # ----------------- Tools Menu -----------------
        tools_menu = menubar.addMenu("&Tools")

        web_tool_act = QAction("🌐 &Convert Webpage to PDF...", self)
        web_tool_act.triggered.connect(self._open_web_to_pdf_dialog)
        tools_menu.addAction(web_tool_act)

        img_tool_act = QAction("🖼 &Convert Images to PDF...", self)
        img_tool_act.triggered.connect(self._open_image_to_pdf_dialog)
        tools_menu.addAction(img_tool_act)

        tools_menu.addSeparator()

        merge_action = QAction("🔀 &Merge Multiple PDFs...", self)
        merge_action.triggered.connect(self._open_merge_dialog)
        tools_menu.addAction(merge_action)

        split_action = QAction("✂️ &Split / Extract PDF...", self)
        split_action.triggered.connect(self._open_split_dialog)
        tools_menu.addAction(split_action)

        protect_action = QAction("🔒 &Protect & Encrypt PDF...", self)
        protect_action.triggered.connect(self._open_security_dialog)
        tools_menu.addAction(protect_action)

        tools_menu.addSeparator()

        rot_cw = QAction("Rotate Clockwise (90°)", self)
        rot_cw.setShortcut(QKeySequence("Ctrl+R"))
        rot_cw.triggered.connect(self._rotate_clockwise)
        tools_menu.addAction(rot_cw)

        rot_ccw = QAction("Rotate Counter-Clockwise (90°)", self)
        rot_ccw.setShortcut(QKeySequence("Ctrl+Shift+R"))
        rot_ccw.triggered.connect(self._rotate_counter_clockwise)
        tools_menu.addAction(rot_ccw)

        # ----------------- Theme Menu -----------------
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

        # ----------------- Help Menu -----------------
        help_menu = menubar.addMenu("&Help")

        shortcuts_act = QAction("⌨ &Keyboard Shortcuts", self)
        shortcuts_act.setShortcut(QKeySequence("F1"))
        shortcuts_act.triggered.connect(self._show_shortcuts_dialog)
        help_menu.addAction(shortcuts_act)

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

        # Web to PDF Button
        self.btn_web = QToolButton()
        self.btn_web.setText("🌐 Web PDF")
        self.btn_web.setToolTip("Convert Webpage or Article to PDF (Ctrl+Shift+W)")
        self.btn_web.clicked.connect(self._open_web_to_pdf_dialog)
        self.toolbar.addWidget(self.btn_web)

        # Toggle Sidebar
        self.btn_sidebar = QToolButton()
        self.btn_sidebar.setText("📑 Sidebar")
        self.btn_sidebar.setCheckable(True)
        self.btn_sidebar.setChecked(True)
        self.btn_sidebar.setToolTip("Toggle Thumbnails & Outline Sidebar (Ctrl+B)")
        self.btn_sidebar.clicked.connect(self._toggle_sidebar)
        self.toolbar.addWidget(self.btn_sidebar)

        self.toolbar.addSeparator()

        # Navigation History (Back / Forward)
        self.btn_nav_back = QToolButton()
        self.btn_nav_back.setText("⮜")
        self.btn_nav_back.setToolTip("Back (Alt+Left)")
        self.btn_nav_back.clicked.connect(self._history_back)
        self.toolbar.addWidget(self.btn_nav_back)

        self.btn_nav_fwd = QToolButton()
        self.btn_nav_fwd.setText("⮞")
        self.btn_nav_fwd.setToolTip("Forward (Alt+Right)")
        self.btn_nav_fwd.clicked.connect(self._history_forward)
        self.toolbar.addWidget(self.btn_nav_fwd)

        self.toolbar.addSeparator()

        # Page Navigation
        self.btn_first = QToolButton()
        self.btn_first.setText("⏮")
        self.btn_first.setToolTip("First Page (Home)")
        self.btn_first.clicked.connect(self._first_page)
        self.toolbar.addWidget(self.btn_first)

        self.btn_prev = QToolButton()
        self.btn_prev.setText("◀ Prev")
        self.btn_prev.setToolTip("Previous Page (Left Arrow / PageUp)")
        self.btn_prev.clicked.connect(self._prev_page)
        self.toolbar.addWidget(self.btn_prev)

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
        self.btn_next.clicked.connect(self._next_page)
        self.toolbar.addWidget(self.btn_next)

        self.btn_last = QToolButton()
        self.btn_last.setText("⏭")
        self.btn_last.setToolTip("Last Page (End)")
        self.btn_last.clicked.connect(self._last_page)
        self.toolbar.addWidget(self.btn_last)

        self.toolbar.addSeparator()

        # Cursor & Annotation Tools
        self.btn_tool_select = QToolButton()
        self.btn_tool_select.setText("✋ Hand")
        self.btn_tool_select.setCheckable(True)
        self.btn_tool_select.clicked.connect(lambda: self._set_tool_mode(ToolMode.HAND))
        self.toolbar.addWidget(self.btn_tool_select)

        self.btn_tool_text = QToolButton()
        self.btn_tool_text.setText("🔤 Select")
        self.btn_tool_text.setCheckable(True)
        self.btn_tool_text.setChecked(True)
        self.btn_tool_text.clicked.connect(lambda: self._set_tool_mode(ToolMode.SELECT))
        self.toolbar.addWidget(self.btn_tool_text)

        self.btn_tool_highlight = QToolButton()
        self.btn_tool_highlight.setText("🖍 Highlight")
        self.btn_tool_highlight.setCheckable(True)
        self.btn_tool_highlight.clicked.connect(lambda: self._set_tool_mode(ToolMode.HIGHLIGHT))
        self.toolbar.addWidget(self.btn_tool_highlight)

        self.btn_tool_pen = QToolButton()
        self.btn_tool_pen.setText("✏️ Pen")
        self.btn_tool_pen.setCheckable(True)
        self.btn_tool_pen.clicked.connect(lambda: self._set_tool_mode(ToolMode.PEN))
        self.toolbar.addWidget(self.btn_tool_pen)

        self.btn_tool_note = QToolButton()
        self.btn_tool_note.setText("💬 Note")
        self.btn_tool_note.setCheckable(True)
        self.btn_tool_note.clicked.connect(lambda: self._set_tool_mode(ToolMode.NOTE))
        self.toolbar.addWidget(self.btn_tool_note)

        self.toolbar.addSeparator()

        # View Mode Selector Buttons
        self.tb_book_mode = QToolButton()
        self.tb_book_mode.setText("📖 Book")
        self.tb_book_mode.setCheckable(True)
        self.tb_book_mode.setToolTip("Two-Page Spread Book Reading Mode")
        self.tb_book_mode.clicked.connect(lambda: self.set_view_mode("book"))
        self.toolbar.addWidget(self.tb_book_mode)

        self.tb_single_mode = QToolButton()
        self.tb_single_mode.setText("📄 Single")
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
        self.btn_zoom_out.clicked.connect(self._zoom_out)
        self.toolbar.addWidget(self.btn_zoom_out)

        self.zoom_combo = QComboBox()
        self.zoom_combo.setFixedWidth(105)
        self.zoom_combo.addItems(["Fit Page", "Fit Width", "50%", "75%", "100%", "125%", "150%", "200%"])
        self.zoom_combo.currentTextChanged.connect(self._on_zoom_combo_changed)
        self.toolbar.addWidget(self.zoom_combo)

        self.btn_zoom_in = QToolButton()
        self.btn_zoom_in.setText("🔍+")
        self.btn_zoom_in.setToolTip("Zoom In (Ctrl +)")
        self.btn_zoom_in.clicked.connect(self._zoom_in)
        self.toolbar.addWidget(self.btn_zoom_in)

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

        # Zoom Slider
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(20, 300)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setFixedWidth(110)
        self.zoom_slider.setToolTip("Adjust Zoom Level")
        self.zoom_slider.valueChanged.connect(self._on_zoom_slider_changed)

        self.status_bar.addWidget(self.lbl_status_msg, 1)
        self.status_bar.addPermanentWidget(self.zoom_slider)
        self.status_bar.addPermanentWidget(self.lbl_status_zoom)
        self.status_bar.addPermanentWidget(self.lbl_status_file)

    def _load_saved_settings(self):
        theme = self.settings.theme
        self.set_theme(theme)

        mode = self.settings.view_mode
        self.set_view_mode(mode)

        offset = self.settings.book_cover_offset
        self.act_cover_offset.setChecked(offset)
        if self.current_viewer:
            self.current_viewer.set_book_cover_offset(offset)

        side_vis = self.settings.sidebar_visible
        self.sidebar.setVisible(side_vis)
        self.btn_sidebar.setChecked(side_vis)
        self.toggle_sidebar_action.setChecked(side_vis)

    def open_pdf(self, file_path: str, password: str = None):
        if not file_path or not os.path.exists(file_path):
            return

        # Check if password protected
        test_doc = PDFDocument()
        if not test_doc.load(file_path, password):
            if test_doc.is_encrypted():
                pwd_dlg = PasswordDialog(os.path.basename(file_path), self)
                if pwd_dlg.exec() == QDialog.DialogCode.Accepted:
                    password = pwd_dlg.get_password()
                else:
                    return

        tab = self.tab_manager.open_document(file_path, password)
        if not tab:
            QMessageBox.critical(self, "Error Opening PDF", f"Failed to open PDF document:\n{file_path}")
            return

        viewer = tab.viewer
        viewer.set_theme(self.settings.theme)
        viewer.set_view_mode(self.settings.view_mode)
        viewer.set_book_cover_offset(self.settings.book_cover_offset)
        viewer.page_changed.connect(self._on_page_changed)
        viewer.zoom_changed.connect(self._on_zoom_changed)
        viewer.status_message.connect(self.lbl_status_msg.setText)

        self.sidebar.set_document(tab.doc)
        self._update_ui_for_doc(tab.doc, viewer)
        self.settings.add_recent_file(file_path)
        self._update_recent_files_menu()

    def _update_ui_for_doc(self, doc: Optional[PDFDocument], viewer: Optional[PDFViewerWidget]):
        if not doc or not doc.is_valid() or not viewer:
            self.page_spin.setValue(1)
            self.page_spin.setRange(1, 1)
            self.lbl_total_pages.setText(" / 0 ")
            self.lbl_status_file.setText("")
            self.setWindowTitle("Lumina PDF Reader")
            return

        total_pages = doc.page_count
        self.page_spin.blockSignals(True)
        self.page_spin.setRange(1, max(1, total_pages))
        self.page_spin.setValue(viewer.current_page + 1)
        self.page_spin.blockSignals(False)

        self.lbl_total_pages.setText(f" / {total_pages} ")
        self.lbl_status_file.setText(f"📄 {os.path.basename(doc.file_path or 'Untitled')} ({total_pages} pages)")
        self.lbl_status_msg.setText(f"Opened: {os.path.basename(doc.file_path or 'Document')}")
        self.setWindowTitle(f"{os.path.basename(doc.file_path or 'Document')} - Lumina PDF Reader")

    def _on_active_doc_changed(self, doc: Optional[PDFDocument], viewer: Optional[PDFViewerWidget]):
        self.sidebar.set_document(doc)
        self._update_ui_for_doc(doc, viewer)

    def _on_tab_count_changed(self, count: int):
        if count == 0:
            self.sidebar.set_document(None)
            self._update_ui_for_doc(None, None)

    def _on_open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open PDF Document", "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.open_pdf(file_path)

    def _on_save_document(self):
        if not self.current_doc:
            return
        if self.current_doc.save_document():
            self.lbl_status_msg.setText("Saved changes successfully.")
            QMessageBox.information(self, "Saved", "Annotations and modifications saved successfully.")
        else:
            QMessageBox.critical(self, "Save Error", "Could not save document changes.")

    def _on_save_as(self):
        if not self.current_doc or not self.current_doc.is_valid():
            return
        out_path, _ = QFileDialog.getSaveFileName(
            self, "Save Copy As", "Copy_" + os.path.basename(self.current_doc.file_path or "Document.pdf"), "PDF Files (*.pdf)"
        )
        if out_path:
            if self.current_doc.save_document(out_path):
                QMessageBox.information(self, "Saved", f"Document saved successfully to:\n{out_path}")

    def _on_print(self):
        if self.current_doc:
            PrintManager.print_document(self.current_doc, self)

    def _open_export_dialog(self):
        if self.current_doc:
            dlg = ExportDialog(self.current_doc, self)
            dlg.exec()

    def _open_web_to_pdf_dialog(self):
        dlg = WebToPDFDialog(self)
        dlg.converted_pdf_ready.connect(self.open_pdf)
        dlg.exec()

    def _open_image_to_pdf_dialog(self):
        dlg = ImageToPDFDialog(self)
        dlg.converted_pdf_ready.connect(self.open_pdf)
        dlg.exec()

    def _open_security_dialog(self):
        curr_file = self.current_doc.file_path if self.current_doc else ""
        dlg = SecurityDialog(current_file=curr_file, parent=self)
        dlg.exec()

    def _open_merge_dialog(self):
        initial = [self.current_doc.file_path] if self.current_doc and self.current_doc.file_path else []
        dlg = MergePDFDialog(self, initial_files=initial)
        dlg.exec()

    def _open_split_dialog(self):
        curr_path = self.current_doc.file_path if self.current_doc and self.current_doc.file_path else ""
        dlg = SplitPDFDialog(self, pdf_path=curr_path)
        dlg.exec()

    def _show_shortcuts_dialog(self):
        dlg = ShortcutsDialog(self)
        dlg.exec()

    def _show_about_dialog(self):
        QMessageBox.about(
            self,
            "About Lumina PDF Reader",
            "<h2>Lumina PDF Reader & Tools</h2>"
            "<p><b>Version 1.1.0 (Professional Edition)</b></p>"
            "<p>A modern, high-performance Windows PDF suite featuring Book Reading Mode, "
            "Dark & Light Themes, Multi-Document Tabs, Text Selection, Markup & Annotations, "
            "Native Printing, Password Encryption, and Page Organization.</p>"
            "<p>Powered by PyQt6 and PyMuPDF.</p>"
        )

    def _set_tool_mode(self, mode: str):
        self.btn_tool_select.setChecked(mode == ToolMode.HAND)
        self.btn_tool_text.setChecked(mode == ToolMode.SELECT)
        self.btn_tool_highlight.setChecked(mode == ToolMode.HIGHLIGHT)
        self.btn_tool_pen.setChecked(mode == ToolMode.PEN)
        self.btn_tool_note.setChecked(mode == ToolMode.NOTE)

        if self.current_viewer:
            self.current_viewer.set_tool_mode(mode)

    def _history_back(self):
        if self.current_viewer:
            self.current_viewer.history_back()

    def _history_forward(self):
        if self.current_viewer:
            self.current_viewer.history_forward()

    def _first_page(self):
        if self.current_viewer:
            self.current_viewer.first_page()

    def _prev_page(self):
        if self.current_viewer:
            self.current_viewer.prev_page()

    def _next_page(self):
        if self.current_viewer:
            self.current_viewer.next_page()

    def _last_page(self):
        if self.current_viewer:
            self.current_viewer.last_page()

    def _zoom_in(self):
        if self.current_viewer:
            self.current_viewer.zoom_in()

    def _zoom_out(self):
        if self.current_viewer:
            self.current_viewer.zoom_out()

    def _rotate_clockwise(self):
        if self.current_viewer:
            self.current_viewer.rotate_clockwise()

    def _rotate_counter_clockwise(self):
        if self.current_viewer:
            self.current_viewer.rotate_counter_clockwise()

    def _toggle_auto_scroll(self):
        if self.current_viewer:
            self.current_viewer.toggle_auto_scroll()

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

    def _toggle_cover_offset(self, checked: bool):
        self.settings.book_cover_offset = checked
        if self.current_viewer:
            self.current_viewer.set_book_cover_offset(checked)

    def set_theme(self, theme_name: str):
        if theme_name not in ["dark", "light", "sepia"]:
            theme_name = "dark"
        self.settings.theme = theme_name
        self.setStyleSheet(get_theme_stylesheet(theme_name))
        for idx in range(self.tab_manager.count()):
            tab = self.tab_manager.widget(idx)
            if isinstance(tab, DocumentTab):
                tab.viewer.set_theme(theme_name)

        idx_map = {"dark": 0, "light": 1, "sepia": 2}
        self.theme_combo.blockSignals(True)
        self.theme_combo.setCurrentIndex(idx_map.get(theme_name, 0))
        self.theme_combo.blockSignals(False)

        self.act_theme_dark.setChecked(theme_name == "dark")
        self.act_theme_light.setChecked(theme_name == "light")
        self.act_theme_sepia.setChecked(theme_name == "sepia")

    def _on_theme_combo_changed(self, index: int):
        themes = ["dark", "light", "sepia"]
        if 0 <= index < len(themes):
            self.set_theme(themes[index])

    def set_view_mode(self, mode: str):
        self.settings.view_mode = mode
        for idx in range(self.tab_manager.count()):
            tab = self.tab_manager.widget(idx)
            if isinstance(tab, DocumentTab):
                tab.viewer.set_view_mode(mode)

        self.tb_book_mode.setChecked(mode == "book")
        self.tb_single_mode.setChecked(mode == "single")
        self.tb_cont_mode.setChecked(mode == "continuous")

        self.act_book_mode.setChecked(mode == "book")
        self.act_single_mode.setChecked(mode == "single")
        self.act_cont_mode.setChecked(mode == "continuous")

    def _on_page_changed(self, current_page: int, total_pages: int):
        self.page_spin.blockSignals(True)
        self.page_spin.setValue(current_page + 1)
        self.page_spin.blockSignals(False)
        self.lbl_total_pages.setText(f" / {total_pages} ")
        self.sidebar.set_current_page(current_page)

    def _on_spin_page_changed(self, value: int):
        if self.current_viewer:
            self.current_viewer.go_to_page(value - 1)

    def _on_zoom_changed(self, zoom: float):
        pct = int(zoom * 100)
        self.lbl_status_zoom.setText(f"Zoom: {pct}%")
        self.zoom_slider.blockSignals(True)
        self.zoom_slider.setValue(max(20, min(300, pct)))
        self.zoom_slider.blockSignals(False)

        self.zoom_combo.blockSignals(True)
        self.zoom_combo.setEditText(f"{pct}%")
        self.zoom_combo.blockSignals(False)

    def _on_zoom_slider_changed(self, value: int):
        if self.current_viewer:
            self.current_viewer.set_zoom(value / 100.0, custom=True)

    def _on_zoom_combo_changed(self, text: str):
        if not self.current_viewer:
            return
        if text == "Fit Page":
            self.current_viewer.set_zoom_mode("fit_page")
        elif text == "Fit Width":
            self.current_viewer.set_zoom_mode("fit_width")
        else:
            try:
                val = float(text.replace("%", "").strip()) / 100.0
                self.current_viewer.set_zoom(val, custom=True)
            except ValueError:
                pass

    def _on_sidebar_page_selected(self, page_num: int):
        if self.current_viewer:
            self.current_viewer.go_to_page(page_num)

    def _on_search_result_selected(self, page_num: int, rects: list):
        if self.current_viewer:
            self.current_viewer.highlight_search_results(page_num, rects)

    def _on_doc_structure_changed(self):
        if self.current_viewer and self.current_doc:
            self.current_viewer.canvas.update_layout()
            self.current_viewer.canvas.update()
            self._update_ui_for_doc(self.current_doc, self.current_viewer)

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
