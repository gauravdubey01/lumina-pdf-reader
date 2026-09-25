"""
PDF Document Engine using PyMuPDF (fitz).
Provides high-performance page rendering, caching, outline extraction, search,
password unlocking, text selection, clickable links, annotations, and page modifications.
"""
import pymupdf as fitz  # PyMuPDF
from PyQt6.QtGui import QImage, QPixmap, QColor
from PyQt6.QtCore import QObject, pyqtSignal, QSize
import numpy as np
import os
from typing import List, Dict, Any, Optional, Tuple

class PDFDocument(QObject):
    page_rendered = pyqtSignal(int)  # page_num
    document_modified = pyqtSignal()  # emitted when annotations/pages change

    def __init__(self, file_path: str = None, password: str = None):
        super().__init__()
        self.file_path = file_path
        self.doc: Optional[fitz.Document] = None
        self._pixmap_cache: Dict[Tuple[int, float, str, int], QPixmap] = {}
        self._thumbnail_cache: Dict[int, QPixmap] = {}
        self._cache_order: List[Tuple[int, float, str, int]] = []
        self._max_cache_size = 60
        self.is_modified = False

        if file_path:
            self.load(file_path, password)

    def load(self, file_path: str, password: str = None) -> bool:
        try:
            self.close()
            self.file_path = file_path
            self.doc = fitz.open(file_path)
            if self.doc.is_encrypted:
                if password:
                    if not self.doc.authenticate(password):
                        return False
                else:
                    return False  # Caller should prompt for password

            self._clear_caches()
            self.is_modified = False
            return True
        except Exception as e:
            print(f"Error loading PDF {file_path}: {e}")
            self.doc = None
            return False

    def is_encrypted(self) -> bool:
        return self.doc is not None and self.doc.is_encrypted

    def authenticate(self, password: str) -> bool:
        if not self.doc:
            return False
        res = self.doc.authenticate(password)
        if res:
            self._clear_caches()
        return bool(res)

    def is_valid(self) -> bool:
        return self.doc is not None and not self.doc.is_closed

    @property
    def page_count(self) -> int:
        if not self.is_valid():
            return 0
        return len(self.doc)

    @property
    def title(self) -> str:
        if not self.is_valid():
            return ""
        meta = self.doc.metadata or {}
        return meta.get("title") or (os.path.basename(self.file_path) if self.file_path else "Untitled")

    @property
    def metadata(self) -> dict:
        if not self.is_valid():
            return {}
        return self.doc.metadata or {}

    def get_page_size(self, page_num: int) -> Tuple[float, float]:
        """Returns width, height in points for page (0-indexed)."""
        if not self.is_valid() or page_num < 0 or page_num >= self.page_count:
            return 612.0, 792.0
        page = self.doc[page_num]
        rect = page.rect
        return rect.width, rect.height

    def get_outline(self) -> List[Dict[str, Any]]:
        """Extracts table of contents as a list of dicts: {title, page, level}."""
        if not self.is_valid():
            return []
        try:
            toc = self.doc.get_toc(simple=False)
            outline = []
            for item in toc:
                level = item[0]
                title = item[1]
                page = item[2] - 1  # 0-indexed
                outline.append({
                    "level": level,
                    "title": title,
                    "page": max(0, page)
                })
            return outline
        except Exception:
            return []

    def get_page_links(self, page_num: int) -> List[Dict[str, Any]]:
        """Extracts interactive hyperlinks on the page (web URLs and internal page jumps)."""
        if not self.is_valid() or page_num < 0 or page_num >= self.page_count:
            return []
        try:
            page = self.doc[page_num]
            links = page.get_links()
            result = []
            for lnk in links:
                rect = lnk.get("from")  # fitz.Rect
                if not rect:
                    continue
                link_type = lnk.get("kind", 0)
                uri = lnk.get("uri", "")
                target_page = lnk.get("page", -1)
                result.append({
                    "rect": (rect.x0, rect.y0, rect.x1, rect.y1),
                    "kind": link_type,
                    "uri": uri,
                    "page": target_page
                })
            return result
        except Exception:
            return []

    def get_text_words(self, page_num: int) -> List[Tuple[float, float, float, float, str, int, int, int]]:
        """
        Returns list of (x0, y0, x1, y1, word_text, block_no, line_no, word_no)
        for precise hit testing during drag selection.
        """
        if not self.is_valid() or page_num < 0 or page_num >= self.page_count:
            return []
        try:
            page = self.doc[page_num]
            return page.get_text("words")
        except Exception:
            return []

    def get_text_in_rect(self, page_num: int, rect: Tuple[float, float, float, float]) -> str:
        """Extracts text within a given bounding box (x0, y0, x1, y1)."""
        if not self.is_valid() or page_num < 0 or page_num >= self.page_count:
            return ""
        try:
            page = self.doc[page_num]
            clip_rect = fitz.Rect(min(rect[0], rect[2]), min(rect[1], rect[3]),
                                  max(rect[0], rect[2]), max(rect[1], rect[3]))
            return page.get_text("text", clip=clip_rect)
        except Exception:
            return ""

    def search_text(self, query: str) -> List[Dict[str, Any]]:
        """Searches all pages for query. Returns list of {page, count, snippet, rects}."""
        results = []
        if not self.is_valid() or not query.strip():
            return results

        query_clean = query.strip()
        for p_no in range(self.page_count):
            try:
                page = self.doc[p_no]
                rects = page.search_for(query_clean)
                if rects:
                    text = page.get_text("text")
                    idx = text.lower().find(query_clean.lower())
                    snippet = ""
                    if idx != -1:
                        start = max(0, idx - 40)
                        end = min(len(text), idx + len(query_clean) + 40)
                        snippet = "..." + text[start:end].replace("\n", " ") + "..."
                    else:
                        snippet = f"Found {len(rects)} match(es)"

                    results.append({
                        "page": p_no,
                        "count": len(rects),
                        "snippet": snippet,
                        "rects": [(r.x0, r.y0, r.x1, r.y1) for r in rects]
                    })
            except Exception:
                continue
        return results

    # ==========================================
    # Annotation Methods (Highlight, Pen, Notes)
    # ==========================================

    def add_highlight(self, page_num: int, rects: List[Tuple[float, float, float, float]], color=(1.0, 1.0, 0.0)):
        """Adds text highlight annotation for selected rectangles."""
        if not self.is_valid() or page_num < 0 or page_num >= self.page_count:
            return
        try:
            page = self.doc[page_num]
            for r in rects:
                annot = page.add_highlight_annot(fitz.Rect(r[0], r[1], r[2], r[3]))
                annot.set_colors(stroke=color)
                annot.update()
            self._invalidate_page_cache(page_num)
            self.is_modified = True
            self.document_modified.emit()
        except Exception as e:
            print(f"Error adding highlight: {e}")

    def add_underline(self, page_num: int, rects: List[Tuple[float, float, float, float]], color=(0.1, 0.5, 0.9)):
        """Adds underline annotation."""
        if not self.is_valid() or page_num < 0 or page_num >= self.page_count:
            return
        try:
            page = self.doc[page_num]
            for r in rects:
                annot = page.add_underline_annot(fitz.Rect(r[0], r[1], r[2], r[3]))
                annot.set_colors(stroke=color)
                annot.update()
            self._invalidate_page_cache(page_num)
            self.is_modified = True
            self.document_modified.emit()
        except Exception as e:
            print(f"Error adding underline: {e}")

    def add_strikeout(self, page_num: int, rects: List[Tuple[float, float, float, float]], color=(0.9, 0.2, 0.2)):
        """Adds strikeout annotation."""
        if not self.is_valid() or page_num < 0 or page_num >= self.page_count:
            return
        try:
            page = self.doc[page_num]
            for r in rects:
                annot = page.add_strikeout_annot(fitz.Rect(r[0], r[1], r[2], r[3]))
                annot.set_colors(stroke=color)
                annot.update()
            self._invalidate_page_cache(page_num)
            self.is_modified = True
            self.document_modified.emit()
        except Exception as e:
            print(f"Error adding strikeout: {e}")

    def add_ink_drawing(self, page_num: int, point_list: List[Tuple[float, float]], color=(0.9, 0.2, 0.2), width=2.0):
        """Adds freehand ink drawing stroke to page."""
        if not self.is_valid() or page_num < 0 or page_num >= self.page_count or len(point_list) < 2:
            return
        try:
            page = self.doc[page_num]
            stroke = [(float(p[0]), float(p[1])) for p in point_list]
            annot = page.add_ink_annot([stroke])
            annot.set_colors(stroke=color)
            annot.set_border(width=width)
            annot.update()
            self._invalidate_page_cache(page_num)
            self.is_modified = True
            self.document_modified.emit()
        except Exception as e:
            print(f"Error adding ink drawing: {e}")

    def add_sticky_note(self, page_num: int, point: Tuple[float, float], text: str, color=(1.0, 0.8, 0.2)):
        """Adds text sticky note annotation."""
        if not self.is_valid() or page_num < 0 or page_num >= self.page_count or not text.strip():
            return
        try:
            page = self.doc[page_num]
            rect = fitz.Rect(point[0], point[1], point[0] + 24, point[1] + 24)
            annot = page.add_text_annot(rect.tl, text)
            annot.set_colors(stroke=color)
            annot.update()
            self._invalidate_page_cache(page_num)
            self.is_modified = True
            self.document_modified.emit()
        except Exception as e:
            print(f"Error adding sticky note: {e}")

    # ==========================================
    # Page Organizer Methods (Delete, Rotate, Duplicate)
    # ==========================================

    def delete_page(self, page_num: int) -> bool:
        if not self.is_valid() or self.page_count <= 1 or page_num < 0 or page_num >= self.page_count:
            return False
        try:
            self.doc.delete_page(page_num)
            self._clear_caches()
            self.is_modified = True
            self.document_modified.emit()
            return True
        except Exception as e:
            print(f"Error deleting page {page_num}: {e}")
            return False

    def rotate_page(self, page_num: int, angle: int) -> bool:
        if not self.is_valid() or page_num < 0 or page_num >= self.page_count:
            return False
        try:
            page = self.doc[page_num]
            page.set_rotation((page.rotation + angle) % 360)
            self._clear_caches()
            self.is_modified = True
            self.document_modified.emit()
            return True
        except Exception as e:
            print(f"Error rotating page {page_num}: {e}")
            return False

    def insert_blank_page(self, page_num: int, width: float = 595.0, height: float = 842.0) -> bool:
        if not self.is_valid():
            return False
        try:
            self.doc.new_page(pno=page_num + 1, width=width, height=height)
            self._clear_caches()
            self.is_modified = True
            self.document_modified.emit()
            return True
        except Exception as e:
            print(f"Error inserting blank page: {e}")
            return False

    def duplicate_page(self, page_num: int) -> bool:
        if not self.is_valid() or page_num < 0 or page_num >= self.page_count:
            return False
        try:
            # Duplicate by creating a single-page memory doc and inserting
            temp_doc = fitz.open()
            temp_doc.insert_pdf(self.doc, from_page=page_num, to_page=page_num)
            self.doc.insert_pdf(temp_doc, start_at=page_num + 1)
            temp_doc.close()
            self._clear_caches()
            self.is_modified = True
            self.document_modified.emit()
            return True
        except Exception as e:
            print(f"Error duplicating page: {e}")
            return False

    def save_document(self, output_path: str = None) -> bool:
        """Saves annotations and modifications back to disk."""
        if not self.is_valid():
            return False
        target_path = output_path or self.file_path
        if not target_path:
            return False
        try:
            if target_path == self.file_path:
                # Incremental save or save to temp and replace
                temp_path = target_path + ".tmp"
                self.doc.save(temp_path, deflate=True)
                self.close()
                if os.path.exists(target_path):
                    os.remove(target_path)
                os.rename(temp_path, target_path)
                self.load(target_path)
            else:
                self.doc.save(target_path, deflate=True)
            self.is_modified = False
            return True
        except Exception as e:
            print(f"Error saving document: {e}")
            return False

    # ==========================================
    # Page Rendering & Caching
    # ==========================================

    def render_page(self, page_num: int, zoom: float = 1.0, theme: str = "light", rotation: int = 0) -> QPixmap:
        """Renders page with zoom, theme filter, and rotation."""
        if not self.is_valid() or page_num < 0 or page_num >= self.page_count:
            return QPixmap()

        key = (page_num, round(zoom, 2), theme, rotation % 360)
        if key in self._pixmap_cache:
            return self._pixmap_cache[key]

        try:
            page = self.doc[page_num]
            mat = fitz.Matrix(zoom, zoom).prerotate(rotation)
            pix = page.get_pixmap(matrix=mat, alpha=False)

            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)

            if theme == "dark":
                img = self._apply_dark_filter(img)
            elif theme == "sepia":
                img = self._apply_sepia_filter(img)

            pixmap = QPixmap.fromImage(img)

            self._pixmap_cache[key] = pixmap
            self._cache_order.append(key)
            if len(self._cache_order) > self._max_cache_size:
                old_key = self._cache_order.pop(0)
                self._pixmap_cache.pop(old_key, None)

            return pixmap
        except Exception as e:
            print(f"Error rendering page {page_num}: {e}")
            return QPixmap()

    def render_thumbnail(self, page_num: int, width: int = 150) -> QPixmap:
        """Renders thumbnail for sidebar."""
        if not self.is_valid() or page_num < 0 or page_num >= self.page_count:
            return QPixmap()

        if page_num in self._thumbnail_cache:
            return self._thumbnail_cache[page_num]

        try:
            page = self.doc[page_num]
            rect = page.rect
            zoom = width / max(rect.width, 1)
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(img)
            self._thumbnail_cache[page_num] = pixmap
            return pixmap
        except Exception as e:
            print(f"Error rendering thumbnail for page {page_num}: {e}")
            return QPixmap()

    def _apply_dark_filter(self, img: QImage) -> QImage:
        converted = img.convertToFormat(QImage.Format.Format_RGB32)
        ptr = converted.bits()
        ptr.setsize(converted.sizeInBytes())
        arr = np.frombuffer(ptr, np.uint8).reshape((converted.height(), converted.width(), 4))
        
        b = arr[:, :, 0].astype(np.float32)
        g = arr[:, :, 1].astype(np.float32)
        r = arr[:, :, 2].astype(np.float32)
        
        arr[:, :, 0] = np.clip(255 - b * 0.85, 25, 230).astype(np.uint8)
        arr[:, :, 1] = np.clip(255 - g * 0.85, 25, 230).astype(np.uint8)
        arr[:, :, 2] = np.clip(255 - r * 0.85, 25, 230).astype(np.uint8)
        return converted

    def _apply_sepia_filter(self, img: QImage) -> QImage:
        converted = img.convertToFormat(QImage.Format.Format_RGB32)
        ptr = converted.bits()
        ptr.setsize(converted.sizeInBytes())
        arr = np.frombuffer(ptr, np.uint8).reshape((converted.height(), converted.width(), 4))
        
        b = arr[:, :, 0].astype(np.float32)
        g = arr[:, :, 1].astype(np.float32)
        r = arr[:, :, 2].astype(np.float32)

        tr = np.clip(0.393 * r + 0.769 * g + 0.189 * b, 0, 255)
        tg = np.clip(0.349 * r + 0.686 * g + 0.168 * b, 0, 255)
        tb = np.clip(0.272 * r + 0.534 * g + 0.131 * b, 0, 255)

        arr[:, :, 0] = (tb * 0.85 + 30).astype(np.uint8)
        arr[:, :, 1] = (tg * 0.95 + 10).astype(np.uint8)
        arr[:, :, 2] = (tr * 1.0).astype(np.uint8)
        return converted

    def _invalidate_page_cache(self, page_num: int):
        keys_to_remove = [k for k in self._pixmap_cache.keys() if k[0] == page_num]
        for k in keys_to_remove:
            self._pixmap_cache.pop(k, None)
        self._thumbnail_cache.pop(page_num, None)

    def _clear_caches(self):
        self._pixmap_cache.clear()
        self._thumbnail_cache.clear()
        self._cache_order.clear()

    def close(self):
        if self.doc:
            try:
                self.doc.close()
            except Exception:
                pass
            self.doc = None
            self._clear_caches()
