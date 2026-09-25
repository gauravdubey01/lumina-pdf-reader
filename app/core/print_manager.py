"""
Print Manager for Lumina PDF Reader.
Provides native Windows print dialog and high-DPI document printing.
"""
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtGui import QPainter, QImage
from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtCore import QRectF
import pymupdf as fitz
from app.core.pdf_document import PDFDocument

class PrintManager:
    @staticmethod
    def print_document(doc: PDFDocument, parent: QWidget = None) -> bool:
        if not doc or not doc.is_valid():
            QMessageBox.warning(parent, "Print", "No document open to print.")
            return False

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setDocName(doc.title)

        dialog = QPrintDialog(printer, parent)
        dialog.setWindowTitle("Print Document")

        # Set page range options
        dialog.setMinMax(1, doc.page_count)
        printer.setFromTo(1, doc.page_count)

        if dialog.exec() != QPrintDialog.DialogCode.Accepted:
            return False

        # Determine pages to print
        from_page = printer.fromPage() - 1 if printer.fromPage() > 0 else 0
        to_page = printer.toPage() - 1 if printer.toPage() > 0 else doc.page_count - 1
        from_page = max(0, min(from_page, doc.page_count - 1))
        to_page = max(from_page, min(to_page, doc.page_count - 1))

        painter = QPainter()
        if not painter.begin(printer):
            QMessageBox.critical(parent, "Print Error", "Could not start printing.")
            return False

        try:
            for page_idx in range(from_page, to_page + 1):
                if page_idx > from_page:
                    printer.newPage()

                page = doc.doc[page_idx]
                # Render at 300 DPI for sharp physical printing
                dpi = 300
                mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)

                # Scale to printer printable page rect
                page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
                scaled_img = img.scaled(
                    int(page_rect.width()),
                    int(page_rect.height()),
                    aspectRatioMode=True  # Qt.AspectRatioMode.KeepAspectRatio
                )

                # Center image on page
                x = page_rect.x() + (page_rect.width() - scaled_img.width()) / 2
                y = page_rect.y() + (page_rect.height() - scaled_img.height()) / 2
                painter.drawImage(QRectF(x, y, scaled_img.width(), scaled_img.height()), scaled_img)

            painter.end()
            return True
        except Exception as e:
            painter.end()
            QMessageBox.critical(parent, "Print Error", f"Failed to print document: {e}")
            return False
