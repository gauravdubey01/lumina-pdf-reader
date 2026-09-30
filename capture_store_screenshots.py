"""
Captures 4 pristine 1920x1080 Microsoft Store screenshots of OmniPDF.
Showcases:
1. Two-Page Book Reading Mode (Dark Mode)
2. Interactive Markup, Highlighter & Annotations (Light Mode)
3. Eye-Care Sepia Warm Paper with Table of Contents Outline
4. Built-in PDF Productivity Suite (Merge & Reorganize Dialog)
"""
import os
import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer, QRect
from PyQt6.QtGui import QPixmap, QPainter, QImage

from app.ui.main_window import MainWindow
from app.ui.viewer_widget import ToolMode
from app.ui.merge_dialog import MergePDFDialog

def capture():
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    project_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(project_dir, "assets", "StoreScreenshots")
    os.makedirs(output_dir, exist_ok=True)

    def save_1080p(pixmap: QPixmap, filename: str):
        target = pixmap.scaled(
            1920, 1080,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        path = os.path.join(output_dir, filename)
        target.save(path, "PNG")
        print(f"Saved: {path} ({target.width()}x{target.height()})")

    # ----------------------------------------------------
    # Screenshot 1: Book Reading Mode (Dark Mode)
    # ----------------------------------------------------
    print("Capturing Screenshot 1: Book Mode (Dark)...")
    win = MainWindow(initial_file=os.path.join(project_dir, "Sample_Book.pdf"))
    win.resize(1920, 1080)
    win.set_theme("dark")
    win.set_view_mode("book")
    win.show()
    app.processEvents()

    if win.current_viewer:
        win.current_viewer.go_to_page(1) # Show spread Pages 2 & 3
        win.current_viewer.set_zoom_mode("fit_page")
    if hasattr(win.sidebar, "tab_widget"):
        win.sidebar.tab_widget.setCurrentIndex(0) # Thumbnails tab

    for _ in range(15):
        app.processEvents()
        time.sleep(0.05)

    pix1 = win.grab()
    save_1080p(pix1, "screenshot_1_book_mode_dark.png")

    # ----------------------------------------------------
    # Screenshot 2: Annotations & Highlighting (Light Mode)
    # ----------------------------------------------------
    print("Capturing Screenshot 2: Annotations & Highlighting (Light)...")
    win.open_pdf(os.path.join(project_dir, "Sample_Annotated.pdf"))
    win.set_theme("light")
    win.set_view_mode("book")
    win._set_tool_mode(ToolMode.HIGHLIGHT)
    app.processEvents()

    if win.current_viewer:
        win.current_viewer.go_to_page(1) # Show annotated pages
        win.current_viewer.set_zoom_mode("fit_page")

    for _ in range(15):
        app.processEvents()
        time.sleep(0.05)

    pix2 = win.grab()
    save_1080p(pix2, "screenshot_2_annotations_light.png")

    # ----------------------------------------------------
    # Screenshot 3: Sepia Warm Paper & Table of Contents Outline
    # ----------------------------------------------------
    print("Capturing Screenshot 3: Sepia Mode & Outline...")
    win.open_pdf(os.path.join(project_dir, "Sample_Book.pdf"))
    win.set_theme("sepia")
    win.set_view_mode("book")
    win._set_tool_mode(ToolMode.SELECT)
    if hasattr(win.sidebar, "tabs"):
        win.sidebar.tabs.setCurrentIndex(1) # Outline/TOC tab
        if hasattr(win.sidebar, "outline_tree"):
            win.sidebar.outline_tree.expandAll()

    if win.current_viewer:
        win.current_viewer.go_to_page(1)
        win.current_viewer.set_zoom_mode("fit_page")

    for _ in range(15):
        app.processEvents()
        time.sleep(0.05)

    pix3 = win.grab()
    save_1080p(pix3, "screenshot_3_sepia_reading.png")

    # ----------------------------------------------------
    # Screenshot 4: PDF Productivity Suite (Merge Dialog overlay)
    # ----------------------------------------------------
    print("Capturing Screenshot 4: PDF Productivity Tools...")
    win.set_theme("dark")
    if hasattr(win.sidebar, "tab_widget"):
        win.sidebar.tab_widget.setCurrentIndex(0)

    # Create Merge Dialog overlay
    sample_a = os.path.join(project_dir, "Document_A.pdf")
    sample_b = os.path.join(project_dir, "Document_B.pdf")
    sample_book = os.path.join(project_dir, "Sample_Book.pdf")
    merge_dlg = MergePDFDialog(win, initial_files=[sample_book, sample_a, sample_b])
    merge_dlg.setWindowModality(Qt.WindowModality.NonModal)
    merge_dlg.setFixedSize(620, 480)
    
    # Center merge dialog over main window
    dlg_x = (win.width() - merge_dlg.width()) // 2
    dlg_y = (win.height() - merge_dlg.height()) // 2
    merge_dlg.move(win.x() + dlg_x, win.y() + dlg_y)
    merge_dlg.show()

    for _ in range(15):
        app.processEvents()
        time.sleep(0.05)

    # Composite merge dialog onto main window grab
    base_pix = win.grab()
    dlg_pix = merge_dlg.grab()

    painter = QPainter(base_pix)
    # Draw soft semi-transparent dimming background
    painter.fillRect(0, 0, base_pix.width(), base_pix.height(), Qt.GlobalColor.transparent)
    painter.drawPixmap(dlg_x, dlg_y, dlg_pix)
    painter.end()

    merge_dlg.close()
    save_1080p(base_pix, "screenshot_4_productivity_tools.png")

    print("\nAll 4 screenshots generated successfully!")
    app.quit()

if __name__ == "__main__":
    capture()
