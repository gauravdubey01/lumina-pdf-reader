"""
PDF Viewer Widget.
Supports Single Page, Book Reading Mode (Two-Page Spread), Continuous Scroll,
Zooming, Theme Inversion, Search Highlight, Text Selection & Copy, Markup Annotations
(Highlight, Underline, Strikethrough, Pen Ink, Sticky Notes), Interactive Hyperlinks,
Navigation History, and Hands-Free Auto-Scroll.
"""
from PyQt6.QtWidgets import (
    QWidget, QScrollArea, QVBoxLayout, QHBoxLayout, QLabel,
    QMenu, QInputDialog, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal, QSize, QTimer, QUrl
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QPixmap, QWheelEvent,
    QKeyEvent, QMouseEvent, QCursor, QAction, QDesktopServices,
    QClipboard
)
from app.core.pdf_document import PDFDocument
from typing import Optional, List, Dict, Any, Tuple
import os

class ToolMode:
    HAND = "hand"
    SELECT = "select"
    HIGHLIGHT = "highlight"
    UNDERLINE = "underline"
    STRIKEOUT = "strikeout"
    PEN = "pen"
    NOTE = "note"

class PDFViewerWidget(QScrollArea):
    page_changed = pyqtSignal(int, int)  # current_page (0-indexed), total_pages
    zoom_changed = pyqtSignal(float)      # zoom_factor
    view_mode_changed = pyqtSignal(str)   # view_mode
    status_message = pyqtSignal(str)      # message

    def __init__(self, parent=None):
        super().__init__(parent)
        self.doc: Optional[PDFDocument] = None
        self.current_page = 0
        self.zoom_factor = 1.0
        self.zoom_mode = "fit_page"  # "fit_page", "fit_width", "custom"
        self.view_mode = "book"      # "single", "book", "continuous"
        self.book_cover_offset = True # First page is cover (alone)
        self.theme = "dark"          # "dark", "light", "sepia"
        self.rotation = 0            # 0, 90, 180, 270

        self.tool_mode = ToolMode.SELECT
        self.pen_color = (0.9, 0.2, 0.2)
        self.pen_width = 2.5
        self.highlight_color = (1.0, 0.9, 0.0)

        self.highlight_rects: List[Tuple[int, float, float, float, float]] = []

        # Navigation History
        self.history: List[int] = []
        self.history_index: int = -1
        self._suppress_history = False

        # Auto-Scroll Engine
        self.auto_scroll_timer = QTimer(self)
        self.auto_scroll_timer.timeout.connect(self._auto_scroll_tick)
        self.auto_scroll_speed = 2  # pixels per tick
        self.is_auto_scrolling = False

        # Canvas Widget
        self.canvas = ViewerCanvas(self)
        self.setWidget(self.canvas)
        self.setWidgetResizable(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._update_background_color()

    def set_document(self, doc: Optional[PDFDocument]):
        self.doc = doc
        self.current_page = 0
        self.highlight_rects.clear()
        self.history = [0]
        self.history_index = 0
        if self.doc and self.doc.is_valid():
            self.update_zoom_for_mode()
            self.page_changed.emit(self.current_page, self.doc.page_count)
        self.canvas.update_layout()
        self.canvas.update()

    def set_tool_mode(self, mode: str):
        self.tool_mode = mode
        self.canvas.clear_selection()
        self.canvas.update_cursor()

    def set_theme(self, theme: str):
        self.theme = theme
        self._update_background_color()
        self.canvas.update()

    def _update_background_color(self):
        if self.theme == "dark":
            bg_color = "#121316"
        elif self.theme == "sepia":
            bg_color = "#dfd2bc"
        else:
            bg_color = "#e2e8f0"
        self.setStyleSheet(f"QScrollArea {{ background-color: {bg_color}; border: none; }}")
        self.canvas.setStyleSheet(f"background-color: {bg_color};")

    def set_view_mode(self, mode: str):
        if mode in ["single", "book", "continuous"]:
            self.view_mode = mode
            self.update_zoom_for_mode()
            self.view_mode_changed.emit(mode)
            self.canvas.update_layout()
            self.canvas.update()

    def set_book_cover_offset(self, offset: bool):
        self.book_cover_offset = offset
        self.canvas.update_layout()
        self.canvas.update()

    def set_zoom(self, zoom: float, custom: bool = True):
        self.zoom_factor = max(0.2, min(5.0, zoom))
        if custom:
            self.zoom_mode = "custom"
        self.zoom_changed.emit(self.zoom_factor)
        self.canvas.update_layout()
        self.canvas.update()

    def zoom_in(self):
        self.set_zoom(self.zoom_factor * 1.2, custom=True)

    def zoom_out(self):
        self.set_zoom(self.zoom_factor / 1.2, custom=True)

    def zoom_original(self):
        self.set_zoom(1.0, custom=True)

    def set_zoom_mode(self, mode: str):
        self.zoom_mode = mode
        self.update_zoom_for_mode()

    def rotate_clockwise(self):
        self.rotation = (self.rotation + 90) % 360
        self.canvas.update_layout()
        self.canvas.update()

    def rotate_counter_clockwise(self):
        self.rotation = (self.rotation - 90) % 360
        self.canvas.update_layout()
        self.canvas.update()

    def update_zoom_for_mode(self):
        if not self.doc or not self.doc.is_valid():
            return

        viewport_size = self.viewport().size()
        avail_w = max(viewport_size.width() - 40, 100)
        avail_h = max(viewport_size.height() - 40, 100)

        pw, ph = self.doc.get_page_size(self.current_page)
        if self.rotation in (90, 270):
            pw, ph = ph, pw

        if self.view_mode == "book":
            total_w = pw * 2 + 20
            total_h = ph
        else:
            total_w = pw
            total_h = ph

        if self.zoom_mode == "fit_width":
            new_zoom = avail_w / max(total_w, 1)
            self.set_zoom(new_zoom, custom=False)
        elif self.zoom_mode == "fit_page":
            new_zoom = min(avail_w / max(total_w, 1), avail_h / max(total_h, 1))
            self.set_zoom(new_zoom, custom=False)

    def go_to_page(self, page_num: int, add_history: bool = True):
        if not self.doc or not self.doc.is_valid():
            return
        total = self.doc.page_count
        new_page = max(0, min(page_num, total - 1))
        if new_page != self.current_page:
            if add_history and not self._suppress_history:
                if self.history_index < len(self.history) - 1:
                    self.history = self.history[:self.history_index + 1]
                self.history.append(new_page)
                self.history_index = len(self.history) - 1

            self.current_page = new_page
            self.page_changed.emit(self.current_page, total)
            self.canvas.update_layout()
            self.canvas.update()

    def history_back(self):
        if self.history_index > 0:
            self._suppress_history = True
            self.history_index -= 1
            self.go_to_page(self.history[self.history_index], add_history=False)
            self._suppress_history = False

    def history_forward(self):
        if self.history_index < len(self.history) - 1:
            self._suppress_history = True
            self.history_index += 1
            self.go_to_page(self.history[self.history_index], add_history=False)
            self._suppress_history = False

    def next_page(self):
        if not self.doc or not self.doc.is_valid():
            return
        step = 2 if self.view_mode == "book" else 1
        if self.view_mode == "book" and self.book_cover_offset and self.current_page == 0:
            step = 1
        self.go_to_page(self.current_page + step)

    def prev_page(self):
        if not self.doc or not self.doc.is_valid():
            return
        step = 2 if self.view_mode == "book" else 1
        if self.view_mode == "book" and self.book_cover_offset and self.current_page <= 2:
            step = 1 if self.current_page == 1 else 2
        self.go_to_page(self.current_page - step)

    def first_page(self):
        self.go_to_page(0)

    def last_page(self):
        if self.doc and self.doc.is_valid():
            self.go_to_page(self.doc.page_count - 1)

    def highlight_search_results(self, page_num: int, rects: list):
        self.highlight_rects = [(page_num, r[0], r[1], r[2], r[3]) for r in rects]
        self.go_to_page(page_num)

    def clear_highlights(self):
        self.highlight_rects.clear()
        self.canvas.update()

    # Auto-Scroll
    def toggle_auto_scroll(self):
        if self.is_auto_scrolling:
            self.stop_auto_scroll()
        else:
            self.start_auto_scroll()

    def start_auto_scroll(self):
        self.is_auto_scrolling = True
        self.auto_scroll_timer.start(30)
        self.status_message.emit(f"Auto-scroll started (Speed: {self.auto_scroll_speed})")

    def stop_auto_scroll(self):
        self.is_auto_scrolling = False
        self.auto_scroll_timer.stop()
        self.status_message.emit("Auto-scroll paused")

    def change_auto_scroll_speed(self, delta: int):
        self.auto_scroll_speed = max(1, min(20, self.auto_scroll_speed + delta))
        self.status_message.emit(f"Auto-scroll speed: {self.auto_scroll_speed}")

    def _auto_scroll_tick(self):
        vbar = self.verticalScrollBar()
        if vbar.value() >= vbar.maximum():
            if self.current_page < (self.doc.page_count - 1 if self.doc else 0):
                self.next_page()
                vbar.setValue(vbar.minimum())
            else:
                self.stop_auto_scroll()
        else:
            vbar.setValue(vbar.value() + self.auto_scroll_speed)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.zoom_mode in ["fit_page", "fit_width"]:
            self.update_zoom_for_mode()

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()

        if modifiers & Qt.KeyboardModifier.AltModifier:
            if key == Qt.Key.Key_Left:
                self.history_back()
                event.accept()
                return
            elif key == Qt.Key.Key_Right:
                self.history_forward()
                event.accept()
                return

        if modifiers & Qt.KeyboardModifier.ControlModifier:
            if key in (Qt.Key.Key_Plus, Qt.Key.Key_Equal):
                self.zoom_in()
                event.accept()
            elif key == Qt.Key.Key_Minus:
                self.zoom_out()
                event.accept()
            elif key == Qt.Key.Key_0:
                self.zoom_original()
                event.accept()
            elif key == Qt.Key.Key_C:
                self.canvas.copy_selected_text()
                event.accept()
            else:
                super().keyPressEvent(event)
            return

        if key == Qt.Key.Key_Space:
            if modifiers & Qt.KeyboardModifier.ShiftModifier:
                self.toggle_auto_scroll()
            else:
                self.next_page()
            event.accept()
        elif key in (Qt.Key.Key_Right, Qt.Key.Key_Down, Qt.Key.Key_PageDown):
            self.next_page()
            event.accept()
        elif key in (Qt.Key.Key_Left, Qt.Key.Key_Up, Qt.Key.Key_PageUp):
            self.prev_page()
            event.accept()
        elif key == Qt.Key.Key_Home:
            self.first_page()
            event.accept()
        elif key == Qt.Key.Key_End:
            self.last_page()
            event.accept()
        else:
            super().keyPressEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            angle = event.angleDelta().y()
            if angle > 0:
                self.zoom_in()
            elif angle < 0:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)


class ViewerCanvas(QWidget):
    def __init__(self, viewer: PDFViewerWidget):
        super().__init__(viewer)
        self.viewer = viewer
        self.setMouseTracking(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        # Dragging / Selection state
        self._is_mouse_down = False
        self._drag_start_pos: Optional[QPointF] = None
        self._drag_current_pos: Optional[QPointF] = None
        self._last_mouse_pos = None

        # Text Selection
        self.selection_page: int = -1
        self.selection_rect: Optional[QRectF] = None
        self.selected_text: str = ""

        # Freehand Drawing Points (in page coordinates)
        self.current_stroke: List[Tuple[float, float]] = []
        self.drawing_page: int = -1

        # Page layout mapping cache: dict of page_num -> (page_x, page_y, page_w, page_h)
        self.page_rects: Dict[int, Tuple[int, int, int, int]] = {}

        self.update_cursor()

    def update_cursor(self):
        mode = self.viewer.tool_mode
        if mode == ToolMode.HAND:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        elif mode == ToolMode.SELECT:
            self.setCursor(Qt.CursorShape.IBeamCursor)
        elif mode in (ToolMode.HIGHLIGHT, ToolMode.UNDERLINE, ToolMode.STRIKEOUT):
            self.setCursor(Qt.CursorShape.CrossCursor)
        elif mode == ToolMode.PEN:
            self.setCursor(Qt.CursorShape.CrossCursor)
        elif mode == ToolMode.NOTE:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

    def clear_selection(self):
        self.selection_page = -1
        self.selection_rect = None
        self.selected_text = ""
        self.current_stroke.clear()
        self.update()

    def update_layout(self):
        doc = self.viewer.doc
        if not doc or not doc.is_valid():
            self.setMinimumSize(QSize(400, 400))
            self.page_rects.clear()
            self.update()
            return

        zoom = self.viewer.zoom_factor
        rot = self.viewer.rotation
        mode = self.viewer.view_mode
        self.page_rects.clear()

        if mode == "continuous":
            total_h = 20
            max_w = 0
            for p in range(doc.page_count):
                pw, ph = doc.get_page_size(p)
                if rot in (90, 270):
                    pw, ph = ph, pw
                pw = pw * zoom
                ph = ph * zoom
                total_h += int(ph + 15)
                max_w = max(max_w, int(pw))
            self.setMinimumSize(QSize(max_w + 40, total_h + 40))
        elif mode == "book":
            p1 = self.viewer.current_page
            if self.viewer.book_cover_offset and p1 == 0:
                pw, ph = doc.get_page_size(0)
                if rot in (90, 270):
                    pw, ph = ph, pw
                w = int(pw * zoom)
                h = int(ph * zoom)
                self.setMinimumSize(QSize(w + 40, h + 40))
            else:
                p_left = p1 if p1 % 2 != 0 else p1 - 1
                p_right = p_left + 1
                pw1, ph1 = doc.get_page_size(max(0, p_left))
                pw2, ph2 = doc.get_page_size(min(doc.page_count - 1, p_right))
                if rot in (90, 270):
                    pw1, ph1 = ph1, pw1
                    pw2, ph2 = ph2, pw2
                w = int((pw1 + pw2) * zoom + 30)
                h = int(max(ph1, ph2) * zoom)
                self.setMinimumSize(QSize(w + 40, h + 40))
        else: # Single page
            pw, ph = doc.get_page_size(self.viewer.current_page)
            if rot in (90, 270):
                pw, ph = ph, pw
            w = int(pw * zoom)
            h = int(ph * zoom)
            self.setMinimumSize(QSize(w + 40, h + 40))

        self.updateGeometry()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        doc = self.viewer.doc
        if not doc or not doc.is_valid():
            self._draw_welcome_placeholder(painter)
            return

        zoom = self.viewer.zoom_factor
        rot = self.viewer.rotation
        theme = self.viewer.theme
        mode = self.viewer.view_mode

        cx = self.width() // 2
        cy = self.height() // 2

        self.page_rects.clear()

        if mode == "book":
            self._paint_book_spread(painter, doc, zoom, rot, theme, cx, cy)
        elif mode == "continuous":
            self._paint_continuous(painter, doc, zoom, rot, theme, cx)
        else:
            self._paint_single_page(painter, doc, zoom, rot, theme, cx, cy)

        # Draw Live Drag Selection
        if self.selection_rect and self.selection_page >= 0 and self.selection_page in self.page_rects:
            px, py, pw, ph = self.page_rects[self.selection_page]
            painter.setPen(QPen(QColor(59, 130, 246, 200), 1.5))
            painter.setBrush(QBrush(QColor(59, 130, 246, 70)))
            painter.drawRect(self.selection_rect)

        # Draw Live Freehand Pen Stroke
        if self.current_stroke and len(self.current_stroke) >= 2 and self.drawing_page in self.page_rects:
            px, py, _, _ = self.page_rects[self.drawing_page]
            painter.setPen(QPen(QColor(int(self.viewer.pen_color[0] * 255),
                                      int(self.viewer.pen_color[1] * 255),
                                      int(self.viewer.pen_color[2] * 255)),
                                self.viewer.pen_width,
                                Qt.PenStyle.SolidLine,
                                Qt.PenCapStyle.RoundCap,
                                Qt.PenJoinStyle.RoundJoin))
            for i in range(len(self.current_stroke) - 1):
                p1 = self.current_stroke[i]
                p2 = self.current_stroke[i + 1]
                painter.drawLine(int(px + p1[0] * zoom), int(py + p1[1] * zoom),
                                 int(px + p2[0] * zoom), int(py + p2[1] * zoom))

    def _paint_single_page(self, painter: QPainter, doc: PDFDocument, zoom: float, rot: int, theme: str, cx: int, cy: int):
        p_no = self.viewer.current_page
        pixmap = doc.render_page(p_no, zoom, theme, rot)
        if pixmap.isNull():
            return

        pw = pixmap.width()
        ph = pixmap.height()
        x = max(20, cx - pw // 2)
        y = max(20, cy - ph // 2)

        self.page_rects[p_no] = (x, y, pw, ph)
        self._draw_page_shadow(painter, x, y, pw, ph)
        painter.drawPixmap(x, y, pixmap)
        self._draw_highlights_for_page(painter, p_no, x, y, zoom)

    def _paint_book_spread(self, painter: QPainter, doc: PDFDocument, zoom: float, rot: int, theme: str, cx: int, cy: int):
        p1 = self.viewer.current_page

        if self.viewer.book_cover_offset and p1 == 0:
            self._paint_single_page(painter, doc, zoom, rot, theme, cx, cy)
            return

        p_left = p1 if p1 % 2 != 0 else p1 - 1
        p_right = p_left + 1

        pix_left = doc.render_page(p_left, zoom, theme, rot) if 0 <= p_left < doc.page_count else None
        pix_right = doc.render_page(p_right, zoom, theme, rot) if 0 <= p_right < doc.page_count else None

        w_left = pix_left.width() if pix_left else 0
        w_right = pix_right.width() if pix_right else 0
        h = max(pix_left.height() if pix_left else 0, pix_right.height() if pix_right else 0)

        total_w = w_left + w_right
        start_x = max(20, cx - total_w // 2)
        y = max(20, cy - h // 2)

        if pix_left and not pix_left.isNull():
            lx = start_x
            self.page_rects[p_left] = (lx, y, w_left, h)
            self._draw_page_shadow(painter, lx, y, w_left, h)
            painter.drawPixmap(lx, y, pix_left)
            self._draw_highlights_for_page(painter, p_left, lx, y, zoom)

        if pix_right and not pix_right.isNull():
            rx = start_x + w_left
            self.page_rects[p_right] = (rx, y, w_right, h)
            self._draw_page_shadow(painter, rx, y, w_right, h)
            painter.drawPixmap(rx, y, pix_right)
            self._draw_highlights_for_page(painter, p_right, rx, y, zoom)

        if pix_left and pix_right:
            spine_x = start_x + w_left
            self._draw_book_spine_shadow(painter, spine_x, y, h)

    def _paint_continuous(self, painter: QPainter, doc: PDFDocument, zoom: float, rot: int, theme: str, cx: int):
        y_offset = 20
        viewport_top = self.viewer.verticalScrollBar().value() - 300
        viewport_bottom = viewport_top + self.viewer.viewport().height() + 600

        for p_no in range(doc.page_count):
            pw_pt, ph_pt = doc.get_page_size(p_no)
            if rot in (90, 270):
                pw_pt, ph_pt = ph_pt, pw_pt
            page_h = int(ph_pt * zoom)
            page_w = int(pw_pt * zoom)
            x = max(20, cx - page_w // 2)
            self.page_rects[p_no] = (x, y_offset, page_w, page_h)

            if y_offset + page_h >= viewport_top and y_offset <= viewport_bottom:
                pixmap = doc.render_page(p_no, zoom, theme, rot)
                if not pixmap.isNull():
                    self._draw_page_shadow(painter, x, y_offset, page_w, page_h)
                    painter.drawPixmap(x, y_offset, pixmap)
                    self._draw_highlights_for_page(painter, p_no, x, y_offset, zoom)

            y_offset += page_h + 15

    def _draw_page_shadow(self, painter: QPainter, x: int, y: int, w: int, h: int):
        shadow_color = QColor(0, 0, 0, 45 if self.viewer.theme != "dark" else 80)
        painter.fillRect(x + 4, y + 4, w, h, shadow_color)
        painter.fillRect(x + 2, y + 2, w, h, shadow_color)
        border_color = QColor(100, 100, 100, 60)
        painter.setPen(QPen(border_color, 1))
        painter.drawRect(x, y, w, h)

    def _draw_book_spine_shadow(self, painter: QPainter, spine_x: int, y: int, h: int):
        crease_w = 16
        for i in range(crease_w):
            alpha = int(40 * (1.0 - (i / crease_w)))
            painter.fillRect(spine_x - i - 1, y, 1, h, QColor(0, 0, 0, alpha))
            painter.fillRect(spine_x + i, y, 1, h, QColor(0, 0, 0, alpha))

    def _draw_highlights_for_page(self, painter: QPainter, p_no: int, x: int, y: int, zoom: float):
        if not self.viewer.highlight_rects:
            return
        highlight_brush = QBrush(QColor(255, 220, 0, 130))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(highlight_brush)

        for item in self.viewer.highlight_rects:
            rect_page, rx0, ry0, rx1, ry1 = item
            if rect_page == p_no:
                rx = x + rx0 * zoom
                ry = y + ry0 * zoom
                rw = (rx1 - rx0) * zoom
                rh = (ry1 - ry0) * zoom
                painter.drawRoundedRect(QRectF(rx, ry, rw, rh), 3, 3)

    def _draw_welcome_placeholder(self, painter: QPainter):
        cx = self.width() // 2
        cy = self.height() // 2
        is_dark = self.viewer.theme == "dark"
        text_color = QColor("#94a3b8") if is_dark else QColor("#64748b")
        title_color = QColor("#f1f5f9") if is_dark else QColor("#1e293b")
        accent_color = QColor("#3b82f6")

        painter.setPen(accent_color)
        font = painter.font()
        font.setPointSize(24)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRectF(cx - 250, cy - 80, 500, 40), Qt.AlignmentFlag.AlignCenter, "Lumina PDF Reader")

        font.setPointSize(13)
        font.setBold(False)
        painter.setFont(font)
        painter.setPen(title_color)
        painter.drawText(QRectF(cx - 250, cy - 30, 500, 30), Qt.AlignmentFlag.AlignCenter, "Fast, Modern & Distraction-Free Reading")

        font.setPointSize(11)
        painter.setFont(font)
        painter.setPen(text_color)
        painter.drawText(QRectF(cx - 250, cy + 10, 500, 50), Qt.AlignmentFlag.AlignCenter, "Drag & Drop a PDF here or click 'Open File' (Ctrl+O)\nto begin reading.")

    # ==========================================
    # Mouse Events (Selection, Links, Pan, Pen)
    # ==========================================

    def _get_page_at_pos(self, pos: QPointF) -> Tuple[int, Optional[Tuple[int, int, int, int]]]:
        for p_no, rect in self.page_rects.items():
            x, y, w, h = rect
            if x <= pos.x() <= x + w and y <= pos.y() <= y + h:
                return p_no, rect
        return -1, None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_mouse_down = True
            pos = event.position()
            p_no, rect = self._get_page_at_pos(pos)

            if self.viewer.tool_mode == ToolMode.HAND:
                self._last_mouse_pos = event.pos()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)

            elif self.viewer.tool_mode == ToolMode.PEN:
                if p_no >= 0 and rect:
                    self.drawing_page = p_no
                    zoom = self.viewer.zoom_factor
                    pt_x = (pos.x() - rect[0]) / zoom
                    pt_y = (pos.y() - rect[1]) / zoom
                    self.current_stroke = [(pt_x, pt_y)]

            elif self.viewer.tool_mode == ToolMode.NOTE:
                if p_no >= 0 and rect and self.viewer.doc:
                    zoom = self.viewer.zoom_factor
                    pt_x = (pos.x() - rect[0]) / zoom
                    pt_y = (pos.y() - rect[1]) / zoom
                    note_text, ok = QInputDialog.getMultiLineText(self, "Add Sticky Note", "Enter comment / note:")
                    if ok and note_text.strip():
                        self.viewer.doc.add_sticky_note(p_no, (pt_x, pt_y), note_text.strip())
                        self.update()

            else: # SELECT, HIGHLIGHT, UNDERLINE, STRIKEOUT
                # First check if clicking on a link
                if p_no >= 0 and rect and self.viewer.doc:
                    zoom = self.viewer.zoom_factor
                    pt_x = (pos.x() - rect[0]) / zoom
                    pt_y = (pos.y() - rect[1]) / zoom
                    links = self.viewer.doc.get_page_links(p_no)
                    for lnk in links:
                        rx0, ry0, rx1, ry1 = lnk["rect"]
                        if rx0 <= pt_x <= rx1 and ry0 <= pt_y <= ry1:
                            # Trigger link click
                            if lnk.get("uri"):
                                QDesktopServices.openUrl(QUrl(lnk["uri"]))
                                self._is_mouse_down = False
                                return
                            elif lnk.get("page", -1) >= 0:
                                self.viewer.go_to_page(lnk["page"])
                                self._is_mouse_down = False
                                return

                # Start selection drag
                if p_no >= 0:
                    self.selection_page = p_no
                    self._drag_start_pos = pos
                    self._drag_current_pos = pos
                    self.selection_rect = QRectF(pos, pos)
                    self.selected_text = ""
                    self.update()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.position()

        # Tooltip / Link Hover
        if not self._is_mouse_down and self.viewer.doc and self.viewer.doc.is_valid():
            p_no, rect = self._get_page_at_pos(pos)
            if p_no >= 0 and rect:
                zoom = self.viewer.zoom_factor
                pt_x = (pos.x() - rect[0]) / zoom
                pt_y = (pos.y() - rect[1]) / zoom
                links = self.viewer.doc.get_page_links(p_no)
                hovered_link = None
                for lnk in links:
                    rx0, ry0, rx1, ry1 = lnk["rect"]
                    if rx0 <= pt_x <= rx1 and ry0 <= pt_y <= ry1:
                        hovered_link = lnk
                        break

                if hovered_link:
                    self.setCursor(Qt.CursorShape.PointingHandCursor)
                    if hovered_link.get("uri"):
                        self.viewer.status_message.emit(f"🔗 {hovered_link['uri']}")
                    elif hovered_link.get("page", -1) >= 0:
                        self.viewer.status_message.emit(f"📄 Jump to Page {hovered_link['page'] + 1}")
                else:
                    self.update_cursor()

        if self._is_mouse_down:
            if self.viewer.tool_mode == ToolMode.HAND and self._last_mouse_pos:
                delta = event.pos() - self._last_mouse_pos
                self._last_mouse_pos = event.pos()
                hbar = self.viewer.horizontalScrollBar()
                vbar = self.viewer.verticalScrollBar()
                hbar.setValue(hbar.value() - delta.x())
                vbar.setValue(vbar.value() - delta.y())

            elif self.viewer.tool_mode == ToolMode.PEN and self.drawing_page in self.page_rects:
                px, py, _, _ = self.page_rects[self.drawing_page]
                zoom = self.viewer.zoom_factor
                pt_x = (pos.x() - px) / zoom
                pt_y = (pos.y() - py) / zoom
                self.current_stroke.append((pt_x, pt_y))
                self.update()

            elif self.selection_page >= 0 and self._drag_start_pos:
                self._drag_current_pos = pos
                top_left = QPointF(min(self._drag_start_pos.x(), pos.x()), min(self._drag_start_pos.y(), pos.y()))
                bot_right = QPointF(max(self._drag_start_pos.x(), pos.x()), max(self._drag_start_pos.y(), pos.y()))
                self.selection_rect = QRectF(top_left, bot_right)
                self.update()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_mouse_down = False

            if self.viewer.tool_mode == ToolMode.HAND:
                self.setCursor(Qt.CursorShape.OpenHandCursor)

            elif self.viewer.tool_mode == ToolMode.PEN and self.drawing_page in self.page_rects and self.viewer.doc:
                if len(self.current_stroke) >= 2:
                    self.viewer.doc.add_ink_drawing(
                        self.drawing_page,
                        self.current_stroke,
                        color=self.viewer.pen_color,
                        width=self.viewer.pen_width
                    )
                self.current_stroke = []
                self.drawing_page = -1
                self.update()

            elif self.selection_page >= 0 and self.selection_rect and self.viewer.doc:
                px, py, pw, ph = self.page_rects.get(self.selection_page, (0, 0, 0, 0))
                zoom = self.viewer.zoom_factor
                rx0 = (self.selection_rect.left() - px) / zoom
                ry0 = (self.selection_rect.top() - py) / zoom
                rx1 = (self.selection_rect.right() - px) / zoom
                ry1 = (self.selection_rect.bottom() - py) / zoom

                # Extract selected text
                self.selected_text = self.viewer.doc.get_text_in_rect(self.selection_page, (rx0, ry0, rx1, ry1)).strip()

                # Handle instant markup tools
                if self.viewer.tool_mode == ToolMode.HIGHLIGHT and self.selected_text:
                    self.viewer.doc.add_highlight(self.selection_page, [(rx0, ry0, rx1, ry1)], color=self.viewer.highlight_color)
                    self.clear_selection()
                elif self.viewer.tool_mode == ToolMode.UNDERLINE and self.selected_text:
                    self.viewer.doc.add_underline(self.selection_page, [(rx0, ry0, rx1, ry1)])
                    self.clear_selection()
                elif self.viewer.tool_mode == ToolMode.STRIKEOUT and self.selected_text:
                    self.viewer.doc.add_strikeout(self.selection_page, [(rx0, ry0, rx1, ry1)])
                    self.clear_selection()
                elif self.selected_text:
                    self.viewer.status_message.emit(f"Selected: {len(self.selected_text)} characters ('{self.selected_text[:30]}...')")

        super().mouseReleaseEvent(event)

    def copy_selected_text(self):
        if self.selected_text:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.selected_text)
            self.viewer.status_message.emit(f"Copied {len(self.selected_text)} characters to clipboard.")
            return True
        return False

    def _show_context_menu(self, pos):
        menu = QMenu(self)

        if self.selected_text and self.selection_page >= 0:
            copy_act = menu.addAction("📋 Copy Text (Ctrl+C)")
            copy_act.triggered.connect(self.copy_selected_text)

            menu.addSeparator()
            hl_menu = menu.addMenu("🖍 Highlight Selection")
            hl_yellow = hl_menu.addAction("🟡 Yellow")
            hl_yellow.triggered.connect(lambda: self._apply_markup("highlight", (1.0, 1.0, 0.0)))
            hl_green = hl_menu.addAction("🟢 Green")
            hl_green.triggered.connect(lambda: self._apply_markup("highlight", (0.2, 0.9, 0.3)))
            hl_pink = hl_menu.addAction("🌸 Pink")
            hl_pink.triggered.connect(lambda: self._apply_markup("highlight", (1.0, 0.4, 0.7)))
            hl_blue = hl_menu.addAction("🔵 Cyan")
            hl_blue.triggered.connect(lambda: self._apply_markup("highlight", (0.3, 0.8, 1.0)))

            und_act = menu.addAction("Underline")
            und_act.triggered.connect(lambda: self._apply_markup("underline", (0.1, 0.5, 0.9)))

            str_act = menu.addAction("Strikethrough")
            str_act.triggered.connect(lambda: self._apply_markup("strikeout", (0.9, 0.2, 0.2)))

            menu.addSeparator()
            search_web_act = menu.addAction("🌐 Search on Google")
            search_web_act.triggered.connect(self._search_selected_on_web)
            menu.addSeparator()

        # General Navigation Actions
        next_act = menu.addAction("Next Page ▶")
        next_act.triggered.connect(self.viewer.next_page)
        prev_act = menu.addAction("◀ Previous Page")
        prev_act.triggered.connect(self.viewer.prev_page)

        menu.addSeparator()
        zoom_in_act = menu.addAction("Zoom In (+)")
        zoom_in_act.triggered.connect(self.viewer.zoom_in)
        zoom_out_act = menu.addAction("Zoom Out (-)")
        zoom_out_act.triggered.connect(self.viewer.zoom_out)

        menu.exec(self.mapToGlobal(pos))

    def _apply_markup(self, markup_type: str, color: tuple):
        if not self.viewer.doc or self.selection_page < 0 or not self.selection_rect:
            return
        px, py, _, _ = self.page_rects.get(self.selection_page, (0, 0, 0, 0))
        zoom = self.viewer.zoom_factor
        rx0 = (self.selection_rect.left() - px) / zoom
        ry0 = (self.selection_rect.top() - py) / zoom
        rx1 = (self.selection_rect.right() - px) / zoom
        ry1 = (self.selection_rect.bottom() - py) / zoom

        if markup_type == "highlight":
            self.viewer.doc.add_highlight(self.selection_page, [(rx0, ry0, rx1, ry1)], color=color)
        elif markup_type == "underline":
            self.viewer.doc.add_underline(self.selection_page, [(rx0, ry0, rx1, ry1)], color=color)
        elif markup_type == "strikeout":
            self.viewer.doc.add_strikeout(self.selection_page, [(rx0, ry0, rx1, ry1)], color=color)

        self.clear_selection()

    def _search_selected_on_web(self):
        if self.selected_text:
            query = QUrl.toPercentEncoding(self.selected_text[:100])
            url = f"https://www.google.com/search?q={bytes(query).decode()}"
            QDesktopServices.openUrl(QUrl(url))
