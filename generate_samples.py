"""
Generates sample PDF files for testing Lumina PDF Reader.
Creates:
1. 'Sample_Book.pdf': A 6-page book with chapters, TOC outline, and rich text.
2. 'Document_A.pdf': 3-page document for merge testing.
3. 'Document_B.pdf': 2-page document for merge testing.
"""
import os
import pymupdf as fitz

def create_sample_book(output_path="Sample_Book.pdf"):
    doc = fitz.open()

    # Colors
    primary_color = (0.15, 0.35, 0.65) # Navy blue
    dark_text = (0.1, 0.1, 0.1)

    # Page 1: Cover Page
    page1 = doc.new_page(width=595, height=842) # A4
    # Draw Cover Art
    page1.draw_rect(fitz.Rect(40, 40, 555, 802), color=primary_color, width=3)
    page1.draw_rect(fitz.Rect(50, 50, 545, 250), color=None, fill=(0.95, 0.96, 0.98))
    page1.insert_text(fitz.Point(80, 130), "THE ART OF READING", fontsize=28, color=primary_color)
    page1.insert_text(fitz.Point(80, 170), "A Journey Through Books & Digital Pages", fontsize=16, color=(0.3, 0.3, 0.3))
    page1.insert_text(fitz.Point(80, 210), "By Lumina Publishing", fontsize=12, color=(0.4, 0.4, 0.4))
    
    page1.insert_text(fitz.Point(80, 400), "Welcome to Lumina PDF Reader!", fontsize=18, color=primary_color)
    page1.insert_text(
        fitz.Point(80, 440),
        "This sample book demonstrates the two-page Book Reading Mode,\n"
        "smart Dark & Light themes, full-text search, and sidebar navigation.\n"
        "Notice how the cover page is displayed gracefully, followed by\n"
        "two-page spreads in book mode!",
        fontsize=13,
        color=dark_text
    )
    page1.insert_text(fitz.Point(260, 780), "Page 1 (Cover)", fontsize=10, color=(0.6, 0.6, 0.6))

    # Page 2: Chapter 1 - The Digital Canvas
    page2 = doc.new_page(width=595, height=842)
    page2.insert_text(fitz.Point(60, 80), "Chapter 1: The Digital Canvas", fontsize=20, color=primary_color)
    page2.draw_line(fitz.Point(60, 95), fitz.Point(535, 95), color=primary_color, width=1.5)
    page2.insert_text(
        fitz.Point(60, 140),
        "Reading on a digital screen should feel as natural, comfortable, and\n"
        "immersive as holding a printed volume in your hands.\n\n"
        "With Book Mode enabled, your screen presents two pages side-by-side,\n"
        "complete with a subtle center spine crease shadow that mimics physical binding.\n\n"
        "Key Advantages of Modern Reading:\n"
        "  * Instant high-resolution rendering at any zoom level.\n"
        "  * Instant full-text search across thousands of pages.\n"
        "  * Seamless switching between Day, Night, and Sepia paper tones.\n"
        "  * Rapid merging and splitting of documents without external web tools.",
        fontsize=13,
        color=dark_text
    )
    page2.insert_text(fitz.Point(280, 800), "2", fontsize=11, color=(0.5, 0.5, 0.5))

    # Page 3: Chapter 1 Continued
    page3 = doc.new_page(width=595, height=842)
    page3.insert_text(fitz.Point(60, 80), "Typography & Visual Ergonomics", fontsize=18, color=primary_color)
    page3.draw_line(fitz.Point(60, 95), fitz.Point(535, 95), color=(0.7, 0.7, 0.7), width=1)
    page3.insert_text(
        fitz.Point(60, 140),
        "Dark Mode in Lumina PDF is engineered specifically for eye comfort.\n"
        "Rather than harsh pure black and piercing white, our dark filter softens\n"
        "backgrounds into deep slate while keeping text legible and diagrams clear.\n\n"
        "Sepia Mode applies an organic warm filter inspired by aged parchment,\n"
        "filtering out blue light and providing relaxing long-session reading.\n\n"
        "Try switching themes from the top toolbar or the Theme menu!",
        fontsize=13,
        color=dark_text
    )
    page3.insert_text(fitz.Point(280, 800), "3", fontsize=11, color=(0.5, 0.5, 0.5))

    # Page 4: Chapter 2 - Document Tools
    page4 = doc.new_page(width=595, height=842)
    page4.insert_text(fitz.Point(60, 80), "Chapter 2: PDF Manipulation Tools", fontsize=20, color=primary_color)
    page4.draw_line(fitz.Point(60, 95), fitz.Point(535, 95), color=primary_color, width=1.5)
    page4.insert_text(
        fitz.Point(60, 140),
        "Document workflows often require combining multiple files or extracting\n"
        "specific sections for review.\n\n"
        "1. Merge Tool:\n"
        "   Allows selecting multiple PDF files, rearranging their sequence with\n"
        "   Move Up / Move Down buttons, and combining them into a clean single PDF.\n\n"
        "2. Split Tool:\n"
        "   Provides flexible extraction modes:\n"
        "   - Custom page ranges (e.g., pages 1-3, 5)\n"
        "   - Bursting all pages into individual single-page documents\n"
        "   - Dividing large manuals every N pages into equal parts.",
        fontsize=13,
        color=dark_text
    )
    page4.insert_text(fitz.Point(280, 800), "4", fontsize=11, color=(0.5, 0.5, 0.5))

    # Page 5: Chapter 2 Continued - Keyboard Shortcuts
    page5 = doc.new_page(width=595, height=842)
    page5.insert_text(fitz.Point(60, 80), "Productivity & Keyboard Shortcuts", fontsize=18, color=primary_color)
    page5.draw_line(fitz.Point(60, 95), fitz.Point(535, 95), color=(0.7, 0.7, 0.7), width=1)
    page5.insert_text(
        fitz.Point(60, 140),
        "Mastering keyboard navigation makes reading effortless:\n\n"
        "  Navigation:\n"
        "    * Space / Right Arrow / Page Down : Next Page\n"
        "    * Left Arrow / Page Up           : Previous Page\n"
        "    * Home / End                     : First / Last Page\n\n"
        "  Zoom & View:\n"
        "    * Ctrl + Mouse Wheel             : Smooth Zoom\n"
        "    * Ctrl + / Ctrl -                : Zoom In / Zoom Out\n"
        "    * Ctrl + 0                       : Reset Zoom to 100%\n"
        "    * F11                            : Toggle Fullscreen\n"
        "    * Ctrl + B                       : Toggle Sidebar",
        fontsize=13,
        color=dark_text
    )
    page5.insert_text(fitz.Point(280, 800), "5", fontsize=11, color=(0.5, 0.5, 0.5))

    # Page 6: Conclusion / Appendix
    page6 = doc.new_page(width=595, height=842)
    page6.insert_text(fitz.Point(60, 80), "Conclusion & Epilogue", fontsize=20, color=primary_color)
    page6.draw_line(fitz.Point(60, 95), fitz.Point(535, 95), color=primary_color, width=1.5)
    page6.insert_text(
        fitz.Point(60, 140),
        "Thank you for exploring Lumina PDF Reader.\n\n"
        "Everything in this application has been crafted to deliver speed,\n"
        "clarity, and ease of use on Windows.\n\n"
        "Enjoy your reading journey!",
        fontsize=13,
        color=dark_text
    )
    page6.insert_text(fitz.Point(280, 800), "6", fontsize=11, color=(0.5, 0.5, 0.5))

    # Table of Contents / Outline (TOC)
    toc = [
        [1, "Cover Page", 1],
        [1, "Chapter 1: The Digital Canvas", 2],
        [2, "Typography & Visual Ergonomics", 3],
        [1, "Chapter 2: Document Tools", 4],
        [2, "Productivity & Shortcuts", 5],
        [1, "Conclusion & Epilogue", 6]
    ]
    doc.set_toc(toc)

    doc.save(output_path)
    doc.close()
    print(f"Created {output_path}")

def create_sample_parts():
    # Document A
    doc_a = fitz.open()
    for i in range(3):
        p = doc_a.new_page(width=595, height=842)
        p.insert_text(fitz.Point(80, 100), f"Document Part A - Page {i + 1}", fontsize=22, color=(0.1, 0.4, 0.2))
        p.insert_text(fitz.Point(80, 160), f"This is page {i + 1} of Part A.", fontsize=14)
    doc_a.save("Document_A.pdf")
    doc_a.close()

    # Document B
    doc_b = fitz.open()
    for i in range(2):
        p = doc_b.new_page(width=595, height=842)
        p.insert_text(fitz.Point(80, 100), f"Document Part B - Page {i + 1}", fontsize=22, color=(0.6, 0.2, 0.1))
        p.insert_text(fitz.Point(80, 160), f"This is page {i + 1} of Part B.", fontsize=14)
    doc_b.save("Document_B.pdf")
    doc_b.close()

if __name__ == "__main__":
    create_sample_book("Sample_Book.pdf")
    create_sample_parts()
    print("All sample PDF files generated successfully!")
