"""
PDF Document Engine using PyMuPDF (fitz).
Provides high-performance page rendering, caching, outline extraction, and search.
"""
import pymupdf as fitz  # PyMuPDF
from PyQt6.QtGui import QImage, QPixmap, QColor
from PyQt6.QtCore import QObject, pyqtSignal, QSize
import numpy as np
from typing import List, Dict, Any, Optional, Tuple

class PDFDocument(QObject):
    page_rendered = pyqtSignal(int)  # page_num

    def __init__(self, file_path: str = None):
        super().__init__()
        self.file_path = file_path
        self.doc: Optional[fitz.Document] = None
        self._pixmap_cache: Dict[Tuple[int, float, str, int], QPixmap] = {}
        self._thumbnail_cache: Dict[int, QPixmap] = {}
        self._cache_order: List[Tuple[int, float, str, int]] = []
        self._max_cache_size = 60

        if file_path:
            self.load(file_path)

    def load(self, file_path: str) -> bool:
        try:
            self.close()
            self.file_path = file_path
            self.doc = fitz.open(file_path)
            self._pixmap_cache.clear()
            self._thumbnail_cache.clear()
            self._cache_order.clear()
            return True
        except Exception as e:
            print(f"Error loading PDF {file_path}: {e}")
            self.doc = None
            return False

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
        return meta.get("title") or (self.file_path.split("/")[-1].split("\\")[-1] if self.file_path else "Untitled")

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
        toc = self.doc.get_toc(simple=False)
        outline = []
        for item in toc:
            # item is [level, title, page_num, dest]
            level = item[0]
            title = item[1]
            page = item[2] - 1  # 0-indexed
            outline.append({
                "level": level,
                "title": title,
                "page": max(0, page)
            })
        return outline

    def search_text(self, query: str) -> List[Dict[str, Any]]:
        """
        Searches all pages for query.
        Returns list of {page: int, text: str, rects: list}
        """
        results = []
        if not self.is_valid() or not query.strip():
            return results

        query_clean = query.strip()
        for p_no in range(self.page_count):
            page = self.doc[p_no]
            rects = page.search_for(query_clean)
            if rects:
                # Extract surrounding text snippet
                text = page.get_text("text")
                # find query in text for snippet preview
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
        return results

    def render_page(self, page_num: int, zoom: float = 1.0, theme: str = "light", rotation: int = 0) -> QPixmap:
        """
        Renders a page to QPixmap with zoom, theme filter, and rotation.
        Theme options: 'light', 'dark', 'sepia'.
        """
        if not self.is_valid() or page_num < 0 or page_num >= self.page_count:
            return QPixmap()

        # Cache key: (page_num, rounded zoom, theme, rotation)
        key = (page_num, round(zoom, 2), theme, rotation % 360)
        if key in self._pixmap_cache:
            return self._pixmap_cache[key]

        try:
            page = self.doc[page_num]
            # Standard PDF resolution is 72 DPI. zoom 1.0 = standard matrix
            mat = fitz.Matrix(zoom, zoom).prerotate(rotation)
            pix = page.get_pixmap(matrix=mat, alpha=False)

            # Convert pixmap to QImage
            # pix.samples has raw RGB bytes
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)

            # Apply Theme Filters
            if theme == "dark":
                # Smart inversion: invert colors for dark mode reading
                img = self._apply_dark_filter(img)
            elif theme == "sepia":
                # Warm paper tone for reading comfort
                img = self._apply_sepia_filter(img)

            pixmap = QPixmap.fromImage(img)

            # Manage Cache
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
        """Renders a fast low-res thumbnail for sidebar."""
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
        """Applies a smooth high-contrast dark mode filter."""
        # Convert QImage to numpy or invert bits
        converted = img.convertToFormat(QImage.Format.Format_RGB32)
        ptr = converted.bits()
        ptr.setsize(converted.sizeInBytes())
        arr = np.frombuffer(ptr, np.uint8).reshape((converted.height(), converted.width(), 4))
        
        # arr[:, :, :3] are B, G, R channels
        # Calculate luminance
        b = arr[:, :, 0].astype(np.float32)
        g = arr[:, :, 1].astype(np.float32)
        r = arr[:, :, 2].astype(np.float32)
        
        # Invert with dark gray background (#1c1d21) instead of harsh pure black
        # and soft off-white text (#e2e8f0)
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        inv_factor = 255.0 - lum
        
        # Remap: 0 (black background in pdf) -> 240, 255 (white bg in pdf) -> 30
        target_lum = 30.0 + (inv_factor / 255.0) * (225.0 - 30.0)
        
        # Tone down saturated colors
        scale = np.clip(target_lum / np.maximum(lum, 1.0), 0.1, 3.0)
        
        arr[:, :, 0] = np.clip(255 - b * 0.85, 25, 230).astype(np.uint8)
        arr[:, :, 1] = np.clip(255 - g * 0.85, 25, 230).astype(np.uint8)
        arr[:, :, 2] = np.clip(255 - r * 0.85, 25, 230).astype(np.uint8)
        
        return converted

    def _apply_sepia_filter(self, img: QImage) -> QImage:
        """Applies a soft warm sepia tone."""
        converted = img.convertToFormat(QImage.Format.Format_RGB32)
        ptr = converted.bits()
        ptr.setsize(converted.sizeInBytes())
        arr = np.frombuffer(ptr, np.uint8).reshape((converted.height(), converted.width(), 4))
        
        b = arr[:, :, 0].astype(np.float32)
        g = arr[:, :, 1].astype(np.float32)
        r = arr[:, :, 2].astype(np.float32)

        # Sepia transformation matrix
        tr = np.clip(0.393 * r + 0.769 * g + 0.189 * b, 0, 255)
        tg = np.clip(0.349 * r + 0.686 * g + 0.168 * b, 0, 255)
        tb = np.clip(0.272 * r + 0.534 * g + 0.131 * b, 0, 255)

        # Blend with cozy warm background (#faf4e8)
        arr[:, :, 0] = (tb * 0.85 + 30).astype(np.uint8)
        arr[:, :, 1] = (tg * 0.95 + 10).astype(np.uint8)
        arr[:, :, 2] = (tr * 1.0).astype(np.uint8)

        return converted

    def close(self):
        if self.doc:
            try:
                self.doc.close()
            except Exception:
                pass
            self.doc = None
            self._pixmap_cache.clear()
            self._thumbnail_cache.clear()
            self._cache_order.clear()
