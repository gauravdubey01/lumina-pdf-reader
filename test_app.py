"""
Automated unit and integration test suite for Lumina PDF Reader Professional Suite.
"""
import os
import sys
from PyQt6.QtWidgets import QApplication

# Ensure QApplication exists
app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

from app.core.pdf_document import PDFDocument
from app.core.pdf_tools import PDFTools
from app.core.settings import AppSettings
from app.ui.main_window import MainWindow
from app.ui.viewer_widget import ToolMode
from app.ui.tab_manager import TabManager, DocumentTab
import pymupdf as fitz

def test_pdf_document_core():
    print("1. Testing PDFDocument Core & Rendering...")
    doc = PDFDocument("Sample_Book.pdf")
    assert doc.is_valid(), "Document should be valid"
    assert doc.page_count == 6, f"Expected 6 pages, got {doc.page_count}"
    
    # Test Outline
    outline = doc.get_outline()
    print(f"   Extracted {len(outline)} TOC items")
    assert len(outline) >= 5, "Outline should have at least 5 items"

    # Test Search
    results = doc.search_text("Dark Mode")
    assert len(results) > 0, "Search for 'Dark Mode' should return matches"

    # Test Rendering in all modes
    pix_light = doc.render_page(0, zoom=1.0, theme="light")
    assert not pix_light.isNull(), "Light render should succeed"

    pix_dark = doc.render_page(1, zoom=1.0, theme="dark")
    assert not pix_dark.isNull(), "Dark render should succeed"

    pix_sepia = doc.render_page(2, zoom=1.0, theme="sepia")
    assert not pix_sepia.isNull(), "Sepia render should succeed"

    # Test Text Words Extraction & Rect text
    words = doc.get_text_words(1)
    assert len(words) > 0, "Page 1 should have extracted words"
    text_sample = doc.get_text_in_rect(1, (50, 50, 500, 300))
    assert len(text_sample) > 0, "Text within rect should not be empty"

    # Test Links extraction
    links = doc.get_page_links(0)
    print(f"   Extracted {len(links)} links on page 0")

    doc.close()
    print("   [PASS] PDFDocument core tests passed.")

def test_pdf_annotations_and_save():
    print("\n2. Testing Annotations & Document Modification...")
    # Make a copy of Sample_Book for testing annotations
    test_pdf = "Test_Annot_Sample.pdf"
    with fitz.open("Sample_Book.pdf") as src:
        src.save(test_pdf)

    doc = PDFDocument(test_pdf)
    assert doc.is_valid()

    # Add Highlights
    doc.add_highlight(1, [(60, 140, 300, 180)], color=(1.0, 1.0, 0.0))
    assert doc.is_modified, "Document should be marked as modified"

    # Add Underline
    doc.add_underline(1, [(60, 200, 300, 220)], color=(0.1, 0.5, 0.9))

    # Add Strikeout
    doc.add_strikeout(1, [(60, 240, 300, 260)], color=(0.9, 0.2, 0.2))

    # Add Ink drawing
    doc.add_ink_drawing(1, [(100, 100), (120, 130), (150, 120), (180, 160)])

    # Add Sticky Note
    doc.add_sticky_note(1, (200, 300), "This is a test note!")

    # Save to disk
    assert doc.save_document(), "Save document should succeed"
    doc.close()

    # Reload and verify annotations persisted
    reload_doc = fitz.open(test_pdf)
    page1 = reload_doc[1]
    annots = list(page1.annots())
    print(f"   Reloaded document: found {len(annots)} persistent annotations on Page 1")
    assert len(annots) >= 4, "Page 1 should have persistent annotations"
    reload_doc.close()

    if os.path.exists(test_pdf):
        os.remove(test_pdf)
    print("   [PASS] Annotations and persistent save tests passed.")

def test_page_organizer():
    print("\n3. Testing Page Organizer (Delete, Rotate, Duplicate, Insert)...")
    test_pdf = "Test_Org_Sample.pdf"
    with fitz.open("Sample_Book.pdf") as src:
        src.save(test_pdf)

    doc = PDFDocument(test_pdf)
    initial_pages = doc.page_count # 6

    # Rotate page
    assert doc.rotate_page(0, 90), "Rotate page should succeed"

    # Duplicate page
    assert doc.duplicate_page(0), "Duplicate page should succeed"
    assert doc.page_count == initial_pages + 1, "Page count should increase by 1"

    # Insert blank page
    assert doc.insert_blank_page(1), "Insert blank page should succeed"
    assert doc.page_count == initial_pages + 2, "Page count should increase by 2"

    # Delete page
    assert doc.delete_page(0), "Delete page should succeed"
    assert doc.page_count == initial_pages + 1, "Page count should decrease by 1"

    doc.close()
    if os.path.exists(test_pdf):
        os.remove(test_pdf)
    print("   [PASS] Page organizer tests passed.")

def test_password_encryption():
    print("\n4. Testing Password Encryption & Unlocking...")
    test_pdf = "Test_Encrypted.pdf"
    pwd = "secretpassword123"

    with fitz.open("Document_A.pdf") as src:
        src.save(test_pdf, encryption=fitz.PDF_ENCRYPT_AES_256, user_pw=pwd, owner_pw=pwd)

    # Try loading without password
    doc = PDFDocument()
    loaded_no_pw = doc.load(test_pdf)
    assert not loaded_no_pw, "Loading encrypted doc without password should fail"
    assert doc.is_encrypted(), "Doc should report is_encrypted=True"

    # Authenticate with correct password
    assert doc.authenticate(pwd), "Authentication with correct password should succeed"
    assert doc.page_count == 3, f"Expected 3 pages, got {doc.page_count}"
    doc.close()

    if os.path.exists(test_pdf):
        os.remove(test_pdf)
    print("   [PASS] Password protection & decryption tests passed.")

def test_multi_tab_manager():
    print("\n5. Testing Multi-Tab Document Manager...")
    tm = TabManager()
    
    tab1 = tm.open_document("Document_A.pdf")
    assert tab1 is not None, "Tab 1 should open"
    assert tm.count() == 1, "Tab count should be 1"

    tab2 = tm.open_document("Document_B.pdf")
    assert tab2 is not None, "Tab 2 should open"
    assert tm.count() == 2, "Tab count should be 2"

    # Switch tab
    tm.setCurrentIndex(0)
    assert tm.get_current_document().file_path == tab1.doc.file_path

    # Close tab
    assert tm.close_tab(1), "Close tab should succeed"
    assert tm.count() == 1, "Tab count should be 1 after close"

    tm.close_tab(0)
    assert tm.count() == 0, "All tabs closed"
    print("   [PASS] Multi-tab manager tests passed.")

def test_main_window_full_ui():
    print("\n6. Testing MainWindow Full Professional UI...")
    win = MainWindow(initial_file="Sample_Book.pdf")
    assert win.current_doc is not None and win.current_doc.is_valid()
    viewer = win.current_viewer
    assert viewer is not None

    # Test Tool Modes
    win._set_tool_mode(ToolMode.SELECT)
    assert viewer.tool_mode == ToolMode.SELECT
    win._set_tool_mode(ToolMode.HIGHLIGHT)
    assert viewer.tool_mode == ToolMode.HIGHLIGHT
    win._set_tool_mode(ToolMode.PEN)
    assert viewer.tool_mode == ToolMode.PEN
    win._set_tool_mode(ToolMode.HAND)
    assert viewer.tool_mode == ToolMode.HAND

    # Test View Modes
    win.set_view_mode("book")
    assert viewer.view_mode == "book"
    viewer.next_page()
    assert viewer.current_page == 1
    viewer.next_page()
    assert viewer.current_page == 3

    # Test Navigation History
    viewer.history_back()
    assert viewer.current_page == 1
    viewer.history_forward()
    assert viewer.current_page == 3

    # Test Zoom Slider
    win._on_zoom_slider_changed(150)
    assert round(viewer.zoom_factor, 2) == 1.50

    # Test Themes
    win.set_theme("dark")
    assert win.settings.theme == "dark"
    win.set_theme("sepia")
    assert win.settings.theme == "sepia"
    win.set_theme("light")
    assert win.settings.theme == "light"

    win.close()
    print("   [PASS] MainWindow full UI integration tests passed.")

if __name__ == "__main__":
    test_pdf_document_core()
    test_pdf_annotations_and_save()
    test_page_organizer()
    test_password_encryption()
    test_multi_tab_manager()
    test_main_window_full_ui()
    print("\n========================================================")
    print("ALL 6 PROFESSIONAL TEST SUITES PASSED! (100% OK)")
    print("========================================================")
