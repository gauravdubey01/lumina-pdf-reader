"""
Automated unit and integration test suite for Lumina PDF Reader.
"""
import os
import sys
from PyQt6.QtWidgets import QApplication

# Ensure QApplication exists for Qt types
app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

from app.core.pdf_document import PDFDocument
from app.core.pdf_tools import PDFTools
from app.core.settings import AppSettings
from app.ui.main_window import MainWindow

def test_pdf_document():
    print("Testing PDFDocument...")
    doc = PDFDocument("Sample_Book.pdf")
    assert doc.is_valid(), "Document should be valid"
    assert doc.page_count == 6, f"Expected 6 pages, got {doc.page_count}"
    
    # Test Outline
    outline = doc.get_outline()
    print(f"  Extracted {len(outline)} TOC items")
    assert len(outline) >= 5, "Outline should have at least 5 items"

    # Test Search
    results = doc.search_text("Dark Mode")
    print(f"  Search for 'Dark Mode': found {len(results)} pages with matches")
    assert len(results) > 0, "Search for 'Dark Mode' should return matches"

    # Test Rendering in all modes
    pix_light = doc.render_page(0, zoom=1.0, theme="light")
    assert not pix_light.isNull(), "Light render should succeed"

    pix_dark = doc.render_page(1, zoom=1.0, theme="dark")
    assert not pix_dark.isNull(), "Dark render should succeed"

    pix_sepia = doc.render_page(2, zoom=1.0, theme="sepia")
    assert not pix_sepia.isNull(), "Sepia render should succeed"

    # Test Thumbnail
    thumb = doc.render_thumbnail(0, width=120)
    assert not thumb.isNull(), "Thumbnail render should succeed"

    doc.close()
    print("  [PASS] PDFDocument tests passed successfully.")

def test_pdf_tools():
    print("\nTesting PDFTools...")
    
    # 1. Merge Test
    success, msg = PDFTools.merge_pdfs(
        ["Document_A.pdf", "Document_B.pdf"],
        "Test_Merged.pdf"
    )
    assert success, f"Merge failed: {msg}"
    doc_m = PDFDocument("Test_Merged.pdf")
    assert doc_m.page_count == 5, f"Merged doc should have 3+2=5 pages, got {doc_m.page_count}"
    doc_m.close()
    print("  [PASS] PDFTools.merge_pdfs passed (3 + 2 -> 5 pages).")

    # 2. Split by Range Test
    success, msg = PDFTools.split_pdf_by_range("Sample_Book.pdf", "1, 3-4, 6", "Test_Split_Range.pdf")
    assert success, f"Split range failed: {msg}"
    doc_s = PDFDocument("Test_Split_Range.pdf")
    assert doc_s.page_count == 4, f"Extracted doc should have 4 pages, got {doc_s.page_count}"
    doc_s.close()
    print("  [PASS] PDFTools.split_pdf_by_range passed.")

    # 3. Split into Single Pages
    out_dir_single = "test_single_pages"
    success, msg = PDFTools.split_into_single_pages("Document_A.pdf", out_dir_single)
    assert success, f"Split single failed: {msg}"
    files = [f for f in os.listdir(out_dir_single) if f.endswith(".pdf")]
    assert len(files) == 3, f"Expected 3 single page files, found {len(files)}"
    print("  [PASS] PDFTools.split_into_single_pages passed.")

    # 4. Split every N pages
    out_dir_chunks = "test_chunks"
    success, msg = PDFTools.split_every_n_pages("Sample_Book.pdf", 2, out_dir_chunks)
    assert success, f"Split chunks failed: {msg}"
    files_c = [f for f in os.listdir(out_dir_chunks) if f.endswith(".pdf")]
    assert len(files_c) == 3, f"Expected 3 chunk files (6 pages / 2), found {len(files_c)}"
    print("  [PASS] PDFTools.split_every_n_pages passed.")

    # 5. Rotate Pages
    success, msg = PDFTools.rotate_pdf_pages("Document_B.pdf", 90, "Test_Rotated.pdf")
    assert success, f"Rotate failed: {msg}"
    print("  [PASS] PDFTools.rotate_pdf_pages passed.")

def test_main_window_ui():
    print("\nTesting MainWindow UI & Themes...")
    win = MainWindow(initial_file="Sample_Book.pdf")
    assert win.current_doc.is_valid(), "MainWindow should load initial file"
    assert win.viewer.current_page == 0, "Initial page should be 0"

    # Test View Modes
    win.set_view_mode("book")
    assert win.viewer.view_mode == "book"
    win.viewer.next_page()
    assert win.viewer.current_page == 1, "Next page in book mode with cover offset should go to page 1"
    win.viewer.next_page()
    assert win.viewer.current_page == 3, "Next page from spread (1,2) should go to page 3"

    win.set_view_mode("single")
    assert win.viewer.view_mode == "single"

    win.set_view_mode("continuous")
    assert win.viewer.view_mode == "continuous"

    # Test Themes
    win.set_theme("dark")
    assert win.settings.theme == "dark"
    win.set_theme("light")
    assert win.settings.theme == "light"
    win.set_theme("sepia")
    assert win.settings.theme == "sepia"

    # Test Zoom
    win.viewer.zoom_in()
    win.viewer.zoom_out()
    win.viewer.zoom_original()

    win.close()
    print("  [PASS] MainWindow UI & Themes tests passed.")

if __name__ == "__main__":
    test_pdf_document()
    test_pdf_tools()
    test_main_window_ui()
    print("\n==========================================")
    print("ALL TESTS PASSED SUCCESSFULLY! (100% OK)")
    print("==========================================")
