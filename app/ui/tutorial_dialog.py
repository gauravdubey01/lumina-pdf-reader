"""
Interactive Tutorial & User Guide Dialog for OmniPDF.
Provides a comprehensive, beginner-friendly walkthrough of all core capabilities:
Reading modes, themes, annotations, PDF tools, web-to-pdf, and shortcuts.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QWidget, QScrollArea,
    QFrame, QTextBrowser
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from app import __version__

class TutorialDialog(QDialog):
    KO_FI_URL = "https://ko-fi.com/gauravdubeypro"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("How to Use OmniPDF — User Guide & Tutorial")
        self.resize(780, 620)
        self.setMinimumSize(700, 540)

        self.setStyleSheet("""
            QDialog {
                background-color: #0b1120;
                color: #f8fafc;
            }
            QLabel {
                color: #f8fafc;
            }
            QPushButton#closeBtn {
                background-color: #1e293b;
                color: #f8fafc;
                border: 1px solid #334155;
                padding: 6px 14px;
                border-radius: 6px;
            }
            QPushButton#closeBtn:hover {
                background-color: #334155;
            }
        """)

        self._init_ui()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setSpacing(12)
        root_layout.setContentsMargins(16, 16, 16, 14)

        # Header Title
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("🎓 Welcome to OmniPDF User Guide")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #38bdf8;")
        subtitle = QLabel("Master all the powerful features of your modern PDF reader & productivity suite.")
        subtitle.setStyleSheet("font-size: 12px; color: #94a3b8;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        version_badge = QLabel(f"Version {__version__}")
        version_badge.setStyleSheet("""
            background-color: #1e293b;
            color: #38bdf8;
            font-size: 11px;
            font-weight: bold;
            padding: 4px 10px;
            border-radius: 12px;
            border: 1px solid #334155;
        """)
        header_layout.addWidget(version_badge)
        root_layout.addLayout(header_layout)

        # Tab Widget for Sections
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #334155;
                border-radius: 6px;
                background-color: #0f172a;
                padding: 10px;
            }
            QTabBar::tab {
                background: #1e293b;
                color: #94a3b8;
                padding: 8px 16px;
                margin-right: 4px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background: #0284c7;
                color: #ffffff;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected {
                background: #334155;
                color: #f8fafc;
            }
        """)

        self.tabs.addTab(self._create_getting_started_tab(), "🚀 Quick Start")
        self.tabs.addTab(self._create_reading_tab(), "📖 Book & Modes")
        self.tabs.addTab(self._create_themes_tab(), "🌙 Themes")
        self.tabs.addTab(self._create_tools_tab(), "🛠 PDF Tools")
        self.tabs.addTab(self._create_markup_tab(), "✏️ Markup & Draw")
        self.tabs.addTab(self._create_web_tab(), "🌐 Web to PDF")
        self.tabs.addTab(self._create_shortcuts_tab(), "⌨ Shortcuts")

        root_layout.addWidget(self.tabs, 1)

        # Bottom Creator Banner & Actions
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(4, 4, 4, 0)

        creator_label = QLabel("Crafted with ❤️ by <b>Gaurav Dubey</b>")
        creator_label.setStyleSheet("font-size: 12px; color: #cbd5e1;")
        footer_layout.addWidget(creator_label)

        btn_kofi = QPushButton("☕ Support on Ko-fi")
        btn_kofi.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_kofi.setStyleSheet("""
            QPushButton {
                background-color: #ff5e5b;
                color: #ffffff;
                font-weight: bold;
                font-size: 12px;
                padding: 6px 14px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #e04b48;
            }
        """)
        btn_kofi.clicked.connect(self._open_kofi)
        footer_layout.addWidget(btn_kofi)

        footer_layout.addStretch()

        btn_close = QPushButton("Close Guide")
        btn_close.setObjectName("closeBtn")
        btn_close.setFixedWidth(100)
        btn_close.clicked.connect(self.accept)
        footer_layout.addWidget(btn_close)

        root_layout.addLayout(footer_layout)

    def _create_scrollable_text(self, html_content: str) -> QWidget:
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setStyleSheet("""
            QTextBrowser {
                background-color: #0f172a;
                color: #e2e8f0;
                border: none;
                font-size: 13px;
                line-height: 1.6;
            }
        """)
        browser.setHtml(html_content)
        return browser

    def _create_getting_started_tab(self) -> QWidget:
        html = """
        <div style="padding: 10px; font-family: 'Segoe UI', sans-serif;">
            <h2 style="color: #38bdf8; margin-top: 0;">Getting Started with OmniPDF</h2>
            <p>Welcome! OmniPDF is engineered to provide a lightning-fast, distraction-free PDF reading and editing experience.</p>
            
            <h3 style="color: #60a5fa;">1. Opening Documents</h3>
            <ul>
                <li><b>Open Button / Ctrl+O:</b> Click the <b>📂 Open</b> button on the top toolbar or press <b>Ctrl+O</b> to browse for any PDF.</li>
                <li><b>Drag and Drop:</b> Drag any PDF directly from File Explorer into OmniPDF to open it instantly.</li>
                <li><b>Recent Files:</b> Re-open your favorite documents quickly from <b>File &rarr; Recent Files</b>.</li>
                <li><b>Password-Protected PDFs:</b> OmniPDF automatically prompts for password decryption whenever an encrypted document is detected.</li>
            </ul>

            <h3 style="color: #60a5fa;">2. Multi-Tab Workspaces</h3>
            <ul>
                <li>Open multiple documents simultaneously using tabs at the top (<b>Ctrl+T</b>).</li>
                <li>Switch tabs anytime or close them individually with <b>Ctrl+W</b>.</li>
            </ul>

            <h3 style="color: #60a5fa;">3. Thumbnails & Outline Sidebar</h3>
            <ul>
                <li>Press <b>Ctrl+B</b> or click <b>📑 Sidebar</b> to reveal document thumbnails, table of contents (bookmarks), and text search.</li>
                <li>Click on any thumbnail or bookmark node to jump immediately to that page.</li>
            </ul>
        </div>
        """
        return self._create_scrollable_text(html)

    def _create_reading_tab(self) -> QWidget:
        html = """
        <div style="padding: 10px; font-family: 'Segoe UI', sans-serif;">
            <h2 style="color: #38bdf8; margin-top: 0;">Reading Modes Designed for Flow</h2>
            
            <h3 style="color: #60a5fa;">📖 Book Reading Mode (Two-Page Spread)</h3>
            <p>Read PDFs like a real hardcover or paperback book! Two pages are displayed side-by-side with realistic book shadows and page turning.</p>
            <ul>
                <li><b>Activate:</b> Click <b>📖 Book</b> on the toolbar or press <b>Ctrl+2</b>.</li>
                <li><b>Book Cover Offset:</b> Enable <b>View &rarr; Book Mode: Cover Offset</b> to display Page 1 solo as a realistic front cover, with subsequent pages paired together as spreads.</li>
                <li><b>Turn Spreads:</b> Press <b>Right Arrow</b>, <b>Page Down</b>, or <b>Spacebar</b> to flip to the next spread.</li>
            </ul>

            <h3 style="color: #60a5fa;">📄 Single Page View</h3>
            <p>Ideal for slides, certificates, and single-column viewing. Press <b>Ctrl+1</b> or click <b>📄 Single</b>.</p>

            <h3 style="color: #60a5fa;">📜 Continuous Scroll Mode</h3>
            <p>Scroll seamlessly through the entire document from start to end without page breaks. Press <b>Ctrl+3</b> or click <b>📜 Continuous</b>.</p>

            <h3 style="color: #60a5fa;">⏩ Auto-Scroll Reading</h3>
            <p>Relax your hands! Toggle automatic hands-free scrolling by pressing <b>Spacebar</b> or choosing <b>View &rarr; Auto-Scroll</b>.</p>
        </div>
        """
        return self._create_scrollable_text(html)

    def _create_themes_tab(self) -> QWidget:
        html = """
        <div style="padding: 10px; font-family: 'Segoe UI', sans-serif;">
            <h2 style="color: #38bdf8; margin-top: 0;">Themes & Eye-Care Modes</h2>
            <p>OmniPDF lets you read in any lighting condition without eye strain:</p>

            <h3 style="color: #60a5fa;">🌙 Dark Mode</h3>
            <ul>
                <li>Converts bright white document backgrounds into comfortable dark surfaces with crisp light text.</li>
                <li>Protects your vision during night reading and long study sessions.</li>
                <li>Shortcut: <b>Theme &rarr; Dark Mode</b> or select from the toolbar dropdown.</li>
            </ul>

            <h3 style="color: #60a5fa;">☀️ Light Mode</h3>
            <ul>
                <li>Pristine, clean standard document rendering with high-contrast text and bright white pages.</li>
                <li>Ideal for well-lit office environments and printing verification.</li>
            </ul>

            <h3 style="color: #60a5fa;">📜 Sepia Warm Paper</h3>
            <ul>
                <li>Soft amber / cream tinted pages reminiscent of vintage books and e-ink displays.</li>
                <li>Reduces blue light emissions for maximum reading comfort.</li>
            </ul>
        </div>
        """
        return self._create_scrollable_text(html)

    def _create_tools_tab(self) -> QWidget:
        html = """
        <div style="padding: 10px; font-family: 'Segoe UI', sans-serif;">
            <h2 style="color: #38bdf8; margin-top: 0;">Built-in PDF Productivity Suite</h2>
            
            <h3 style="color: #60a5fa;">🔀 Merge Multiple PDFs</h3>
            <p>Combine several PDF files into one clean document. Open <b>Tools &rarr; Merge Multiple PDFs</b>, add your files, arrange their order, and click Merge.</p>

            <h3 style="color: #60a5fa;">✂️ Split & Extract Pages</h3>
            <p>Extract exact page ranges into a new PDF (e.g. <code>1-5, 8, 12-20</code>) or split a document into single-page files via <b>Tools &rarr; Split / Extract PDF</b>.</p>

            <h3 style="color: #60a5fa;">🔄 Rotate Pages</h3>
            <p>Fix sideways scans instantly! Press <b>Ctrl+R</b> to rotate clockwise 90°, or <b>Ctrl+Shift+R</b> to rotate counter-clockwise.</p>

            <h3 style="color: #60a5fa;">🔒 Protect & Encrypt PDF</h3>
            <p>Protect sensitive information with high-grade 256-bit AES encryption. Set a custom user password via <b>Tools &rarr; Protect & Encrypt PDF</b>.</p>

            <h3 style="color: #60a5fa;">🖼 Export to Images / Text</h3>
            <p>Export pages as PNG or JPEG image files, or extract all readable text to a <code>.txt</code> file via <b>File &rarr; Export Pages / Text</b>.</p>
        </div>
        """
        return self._create_scrollable_text(html)

    def _create_markup_tab(self) -> QWidget:
        html = """
        <div style="padding: 10px; font-family: 'Segoe UI', sans-serif;">
            <h2 style="color: #38bdf8; margin-top: 0;">Text Selection, Highlighting & Drawing</h2>

            <h3 style="color: #60a5fa;">🔤 Select & Copy Text</h3>
            <p>Select the <b>🔤 Select</b> tool on the toolbar. Click and drag across any text to highlight it, then press <b>Ctrl+C</b> or right-click to copy to clipboard.</p>

            <h3 style="color: #60a5fa;">🖍 Highlight Tool</h3>
            <p>Click <b>🖍 Highlight</b> on the toolbar. Drag over words or passages to add permanent, glowing text highlights.</p>

            <h3 style="color: #60a5fa;">✏️ Freehand Pen Tool</h3>
            <p>Select <b>✏️ Pen</b> to sketch, write handwritten notes, underline sentences, or draw diagrams anywhere on the page.</p>

            <h3 style="color: #60a5fa;">💬 Sticky Notes</h3>
            <p>Select <b>💬 Note</b> and click anywhere on the page to insert an expandable sticky note comment.</p>

            <h3 style="color: #60a5fa;">💾 Saving Your Changes</h3>
            <p>Once you make annotations, press <b>Ctrl+S</b> or <b>File &rarr; Save Annotations</b> to save your markup directly into the PDF file!</p>
        </div>
        """
        return self._create_scrollable_text(html)

    def _create_web_tab(self) -> QWidget:
        html = """
        <div style="padding: 10px; font-family: 'Segoe UI', sans-serif;">
            <h2 style="color: #38bdf8; margin-top: 0;">Webpages & Chrome Print to PDF</h2>

            <h3 style="color: #60a5fa;">🌐 Convert Webpage to PDF</h3>
            <p>Convert any web article, documentation page, or blog into an offline PDF in seconds:</p>
            <ul>
                <li>Press <b>Ctrl+Shift+W</b> or click <b>🌐 Web PDF</b> on the toolbar.</li>
                <li>Enter any URL (e.g. <code>https://en.wikipedia.org/wiki/Book</code>).</li>
                <li>OmniPDF fetches the webpage, renders clean formatting, and saves it as a PDF ready to read.</li>
            </ul>

            <h3 style="color: #60a5fa;">🖨 Saving Chrome / Browser Printouts to OmniPDF</h3>
            <p>You can effortlessly bring any website or web report into OmniPDF using Chrome or Edge:</p>
            <ol>
                <li>In Google Chrome or Microsoft Edge, press <b>Ctrl + P</b> to open the Print dialog.</li>
                <li>In the <b>Destination</b> dropdown, select <b>Save as PDF</b>.</li>
                <li>Save the file to your computer.</li>
                <li>Drag and drop the file into OmniPDF or open it via <b>Ctrl + O</b> to read, annotate, or merge!</li>
            </ol>
        </div>
        """
        return self._create_scrollable_text(html)

    def _create_shortcuts_tab(self) -> QWidget:
        html = """
        <div style="padding: 10px; font-family: 'Segoe UI', sans-serif;">
            <h2 style="color: #38bdf8; margin-top: 0;">Key Shortcuts Cheat Sheet</h2>
            <table width="100%" cellpadding="6" cellspacing="0" style="border-collapse: collapse; font-size: 13px;">
                <tr style="background: #1e293b; color: #38bdf8;">
                    <th align="left" style="padding: 8px; border-bottom: 2px solid #334155;">Action</th>
                    <th align="left" style="padding: 8px; border-bottom: 2px solid #334155;">Shortcut</th>
                </tr>
                <tr style="border-bottom: 1px solid #1e293b;"><td>Open PDF File</td><td><b>Ctrl + O</b></td></tr>
                <tr style="border-bottom: 1px solid #1e293b;"><td>Open New Tab</td><td><b>Ctrl + T</b></td></tr>
                <tr style="border-bottom: 1px solid #1e293b;"><td>Close Current Tab</td><td><b>Ctrl + W</b></td></tr>
                <tr style="border-bottom: 1px solid #1e293b;"><td>Save Document Annotations</td><td><b>Ctrl + S</b></td></tr>
                <tr style="border-bottom: 1px solid #1e293b;"><td>Print Document</td><td><b>Ctrl + P</b></td></tr>
                <tr style="border-bottom: 1px solid #1e293b;"><td>Convert Webpage to PDF</td><td><b>Ctrl + Shift + W</b></td></tr>
                <tr style="border-bottom: 1px solid #1e293b;"><td>Toggle Thumbnails / Sidebar</td><td><b>Ctrl + B</b></td></tr>
                <tr style="border-bottom: 1px solid #1e293b;"><td>Find / Search Text</td><td><b>Ctrl + F</b></td></tr>
                <tr style="border-bottom: 1px solid #1e293b;"><td>Next Page / Spread</td><td><b>Right Arrow / PageDown</b></td></tr>
                <tr style="border-bottom: 1px solid #1e293b;"><td>Previous Page / Spread</td><td><b>Left Arrow / PageUp</b></td></tr>
                <tr style="border-bottom: 1px solid #1e293b;"><td>Toggle Auto-Scroll</td><td><b>Spacebar</b></td></tr>
                <tr style="border-bottom: 1px solid #1e293b;"><td>Interactive Zoom</td><td><b>Ctrl + Mouse Wheel</b></td></tr>
                <tr style="border-bottom: 1px solid #1e293b;"><td>Zoom In / Out</td><td><b>Ctrl + Plus / Ctrl + Minus</b></td></tr>
                <tr style="border-bottom: 1px solid #1e293b;"><td>Rotate Clockwise</td><td><b>Ctrl + R</b></td></tr>
                <tr style="border-bottom: 1px solid #1e293b;"><td>Toggle Fullscreen</td><td><b>F11</b></td></tr>
            </table>
        </div>
        """
        return self._create_scrollable_text(html)

    def _open_kofi(self):
        QDesktopServices.openUrl(QUrl(self.KO_FI_URL))
