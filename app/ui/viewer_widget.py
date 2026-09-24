"""
PDF Viewer Widget.
Supports Single Page, Book Reading Mode (Two-Page Spread), Continuous Scroll,
Zooming, Theme Inversion, and Search Highlight.
"""
from PyQt6.QtWidgets import (
    QWidget, QScrollArea, QVBoxLayout, QHBoxLayout, QLabel,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QGraphicsRectItem, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal, QSize
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QPixmap, QWheelEvent,
    QKeyEvent, QMouseEvent, QCursor
)
from app.core.pdf_document import PDFDocument
from typing import Optional, List, Dict, Any, Tuple

class PDFViewerWidget(QScrollArea):
    page_changed = pyqtSignal(int, int)  # current_page (0-indexed), total_pages
    zoom_changed = pyqtSignal(float)      # zoom_factor
    view_mode_changed = pyqtSignal(str)   # view_mode

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

        self.highlight_rects: List[Tuple[int, float, float, float, float]] = [] # (page, x0, y0, x1, y1)

        # Mouse Drag / Pan
        self._is_panning = False
        self._pan_start_pos = None

        # Container Widget
        self.canvas = ViewerCanvas(self)
        self.setWidget(self.canvas)
        self.setWidgetResizable(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Style background
        self._update_background_color()

    def set_document(self, doc: Optional[PDFDocument]):
        self.doc = doc
        self.current_page = 0
        self.highlight_rects.clear()
        if self.doc and self.doc.is_valid():
            self.update_zoom_for_mode()
            self.page_changed.emit(self.current_page, self.doc.page_count)
        self.canvas.update()

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

        # Get representative page size
        pw, ph = self.doc.get_page_size(self.current_page)
        if self.rotation in (90, 270):
            pw, ph = ph, pw

        if self.view_mode == "book":
            # Two pages side by side
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

    def go_to_page(self, page_num: int):
        if not self.doc or not self.doc.is_valid():
            return
        total = self.doc.page_count
        new_page = max(0, min(page_num, total - 1))
        if new_page != self.current_page:
            self.current_page = new_page
            self.page_changed.emit(self.current_page, total)
            self.canvas.update_layout()
            self.canvas.update()

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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.zoom_mode in ["fit_page", "fit_width"]:
            self.update_zoom_for_mode()

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key in (Qt.Key.Key_Right, Qt.Key.Key_Down, Qt.Key.Key_PageDown, Qt.Key.Key_Space):
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
        elif event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if key in (Qt.Key.Key_Plus, Qt.Key.Key_Equal):
                self.zoom_in()
                event.accept()
            elif key == Qt.Key.Key_Minus:
                self.zoom_out()
                event.accept()
            elif key == Qt.Key.Key_0:
                self.zoom_original()
                event.accept()
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Zoom with Ctrl + Wheel
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
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self._dragging = False
        self._last_mouse_pos = None

    def update_layout(self):
        doc = self.viewer.doc
        if not doc or not doc.is_valid():
            self.setMinimumSize(QSize(400, 400))
            self.update()
            return

        zoom = self.viewer.zoom_factor
        rot = self.viewer.rotation
        mode = self.viewer.view_mode

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
            # Spread logic
            if self.viewer.book_cover_offset and p1 == 0:
                pw, ph = doc.get_page_size(0)
                if rot in (90, 270):
                    pw, ph = ph, pw
                w = int(pw * zoom)
                h = int(ph * zoom)
                self.setMinimumSize(QSize(w + 40, h + 40))
            else:
                # Two pages
                p_left = p1 if p1 % 2 == 1 else p1 - 1
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
            # Draw Welcome Screen
            self._draw_welcome_placeholder(painter)
            return

        zoom = self.viewer.zoom_factor
        rot = self.viewer.rotation
        theme = self.viewer.theme
        mode = self.viewer.view_mode

        cx = self.width() // 2
        cy = self.height() // 2

        if mode == "book":
            self._paint_book_spread(painter, doc, zoom, rot, theme, cx, cy)
        elif mode == "continuous":
            self._paint_continuous(painter, doc, zoom, rot, theme, cx)
        else:
            self._paint_single_page(painter, doc, zoom, rot, theme, cx, cy)

    def _paint_single_page(self, painter: QPainter, doc: PDFDocument, zoom: float, rot: int, theme: str, cx: int, cy: int):
        p_no = self.viewer.current_page
        pixmap = doc.render_page(p_no, zoom, theme, rot)
        if pixmap.isNull():
            return

        pw = pixmap.width()
        ph = pixmap.height()
        x = max(20, cx - pw // 2)
        y = max(20, cy - ph // 2)

        # Draw Page Shadow & Border
        self._draw_page_shadow(painter, x, y, pw, ph)
        painter.drawPixmap(x, y, pixmap)

        # Draw Highlights if any
        self._draw_highlights_for_page(painter, p_no, x, y, zoom, rot, doc)

    def _paint_book_spread(self, painter: QPainter, doc: PDFDocument, zoom: float, rot: int, theme: str, cx: int, cy: int):
        p1 = self.viewer.current_page

        # If cover page offset and page 0 -> render single centered cover
        if self.viewer.book_cover_offset and p1 == 0:
            self._paint_single_page(painter, doc, zoom, rot, theme, cx, cy)
            return

        # Determine left and right page indices
        if self.viewer.book_cover_offset:
            # When cover offset is on: Page 0 is cover. Page 1 is Left, Page 2 is Right.
            p_left = p1 if p1 % 2 != 0 else p1 - 1
            p_right = p_left + 1
        else:
            # Standard even-odd
            p_left = p1 if p1 % 2 == 0 else p1 - 1
            p_right = p_left + 1

        pix_left = doc.render_page(p_left, zoom, theme, rot) if 0 <= p_left < doc.page_count else None
        pix_right = doc.render_page(p_right, zoom, theme, rot) if 0 <= p_right < doc.page_count else None

        w_left = pix_left.width() if pix_left else 0
        w_right = pix_right.width() if pix_right else 0
        h = max(pix_left.height() if pix_left else 0, pix_right.height() if pix_right else 0)

        total_w = w_left + w_right
        start_x = max(20, cx - total_w // 2)
        y = max(20, cy - h // 2)

        # Draw Left Page
        if pix_left and not pix_left.isNull():
            lx = start_x
            self._draw_page_shadow(painter, lx, y, w_left, h)
            painter.drawPixmap(lx, y, pix_left)
            self._draw_highlights_for_page(painter, p_left, lx, y, zoom, rot, doc)

        # Draw Right Page
        if pix_right and not pix_right.isNull():
            rx = start_x + w_left
            self._draw_page_shadow(painter, rx, y, w_right, h)
            painter.drawPixmap(rx, y, pix_right)
            self._draw_highlights_for_page(painter, p_right, rx, y, zoom, rot, doc)

        # Draw Book Spine / Crease Shadow
        if pix_left and pix_right:
            spine_x = start_x + w_left
            self._draw_book_spine_shadow(painter, spine_x, y, h)

    def _paint_continuous(self, painter: QPainter, doc: PDFDocument, zoom: float, rot: int, theme: str, cx: int):
        y_offset = 20
        viewport_top = self.viewer.verticalScrollBar().value() - 200
        viewport_bottom = viewport_top + self.viewer.viewport().height() + 400

        for p_no in range(doc.page_count):
            pw_pt, ph_pt = doc.get_page_size(p_no)
            if rot in (90, 270):
                pw_pt, ph_pt = ph_pt, pw_pt
            page_h = int(ph_pt * zoom)
            page_w = int(pw_pt * zoom)

            # Viewport culling for performance
            if y_offset + page_h >= viewport_top and y_offset <= viewport_bottom:
                pixmap = doc.render_page(p_no, zoom, theme, rot)
                if not pixmap.isNull():
                    x = max(20, cx - page_w // 2)
                    self._draw_page_shadow(painter, x, y_offset, page_w, page_h)
                    painter.drawPixmap(x, y_offset, pixmap)
                    self._draw_highlights_for_page(painter, p_no, x, y_offset, zoom, rot, doc)

            y_offset += page_h + 15

    def _draw_page_shadow(self, painter: QPainter, x: int, y: int, w: int, h: int):
        # Elegant drop shadow
        shadow_color = QColor(0, 0, 0, 45 if self.viewer.theme != "dark" else 80)
        painter.fillRect(x + 4, y + 4, w, h, shadow_color)
        painter.fillRect(x + 2, y + 2, w, h, shadow_color)
        # Subtle page border
        border_color = QColor(100, 100, 100, 60)
        painter.setPen(QPen(border_color, 1))
        painter.drawRect(x, y, w, h)

    def _draw_book_spine_shadow(self, painter: QPainter, spine_x: int, y: int, h: int):
        # Realistic book crease gradient / shadow down the middle
        crease_w = 16
        for i in range(crease_w):
            alpha = int(40 * (1.0 - (i / crease_w)))
            painter.fillRect(spine_x - i - 1, y, 1, h, QColor(0, 0, 0, alpha))
            painter.fillRect(spine_x + i, y, 1, h, QColor(0, 0, 0, alpha))

    def _draw_highlights_for_page(self, painter: QPainter, p_no: int, x: int, y: int, zoom: float, rot: int, doc: PDFDocument):
        if not self.viewer.highlight_rects:
            return

        highlight_brush = QBrush(QColor(255, 220, 0, 120))  # Semi-transparent yellow
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(highlight_brush)

        for item in self.viewer.highlight_rects:
            rect_page, rx0, ry0, rx1, ry1 = item
            if rect_page == p_no:
                # Convert points to zoomed canvas pixels
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

        font.setPointSize(14)
        font.setBold(False)
        painter.setFont(font)
        painter.setPen(title_color)
        painter.drawText(QRectF(cx - 250, cy - 30, 500, 30), Qt.AlignmentFlag.AlignCenter, "Fast, Beautiful & Distraction-Free")

        font.setPointSize(12)
        painter.setFont(font)
        painter.setPen(text_color)
        painter.drawText(QRectF(cx - 250, cy + 10, 500, 50), Qt.AlignmentFlag.AlignCenter, "Drag & Drop a PDF here or click 'Open File' (Ctrl+O)\nto begin reading.")

    # Pan / Dragging
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._last_mouse_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._dragging and self._last_mouse_pos:
            delta = event.pos() - self._last_mouse_pos
            self._last_mouse_pos = event.pos()
            hbar = self.viewer.horizontalScrollBar()
            vbar = self.viewer.verticalScrollBar()
            hbar.setValue(hbar.value() - delta.x())
            vbar.setValue(vbar.value() - delta.y())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)
