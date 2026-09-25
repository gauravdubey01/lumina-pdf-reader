"""
Web and Content Converter for Lumina PDF Reader.
Converts Web URLs, HTML documents, and image collections into formatted PDF files.
"""
import os
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import pymupdf as fitz
from typing import List, Tuple, Optional, Callable

class WebConverter:
    @staticmethod
    def convert_url_to_pdf(
        url: str,
        output_path: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Tuple[bool, str]:
        """
        Fetches web page from URL, extracts readable article structure,
        and generates a clean, paginated PDF document with TOC bookmarks.
        """
        try:
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "https://" + url

            if progress_callback:
                progress_callback("Connecting to webpage...")

            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                html_bytes = response.read()

            if progress_callback:
                progress_callback("Parsing content and styling...")

            soup = BeautifulSoup(html_bytes, "html.parser")

            # Remove scripts, styles, iframes, navbars, ads
            for tag in soup(["script", "style", "nav", "footer", "aside", "header", "noscript", "svg", "form"]):
                tag.decompose()

            # Extract title
            title = soup.title.string.strip() if soup.title and soup.title.string else urllib.parse.urlparse(url).netloc

            # Extract main article or body
            main_content = soup.find("article") or soup.find("main") or soup.find("div", {"id": "content"}) or soup.body

            if not main_content:
                return False, "Could not extract readable article content from webpage."

            if progress_callback:
                progress_callback("Generating PDF document...")

            doc = fitz.open()

            # Colors
            primary_color = (0.15, 0.35, 0.65)
            heading_color = (0.1, 0.2, 0.4)
            text_color = (0.15, 0.15, 0.15)
            meta_color = (0.45, 0.45, 0.45)

            # Page settings (A4: 595 x 842 pt)
            page_w, page_h = 595.0, 842.0
            margin_x, margin_y = 50.0, 50.0
            content_w = page_w - 2 * margin_x

            # Page 1 - Title Header
            page = doc.new_page(width=page_w, height=page_h)
            curr_y = margin_y + 20

            # Title Header Box
            page.draw_rect(fitz.Rect(margin_x, curr_y - 10, page_w - margin_x, curr_y + 60),
                           color=primary_color, width=1.5, fill=(0.95, 0.97, 1.0))
            page.insert_text(fitz.Point(margin_x + 15, curr_y + 22), title[:65], fontsize=18, color=primary_color)
            page.insert_text(fitz.Point(margin_x + 15, curr_y + 44), f"Source: {url[:75]}", fontsize=9, color=meta_color)

            curr_y += 85

            toc = [[1, title[:40], 1]]

            # Extract headings and paragraphs
            elements = main_content.find_all(["h1", "h2", "h3", "p", "li", "blockquote"])

            for elem in elements:
                tag_name = elem.name
                text = elem.get_text().strip()
                if not text:
                    continue

                if tag_name in ("h1", "h2"):
                    fontsize = 15
                    color = heading_color
                    line_height = 20
                    space_before = 18
                    # Add to TOC
                    if len(text) < 60:
                        toc.append([2, text, len(doc)])
                elif tag_name == "h3":
                    fontsize = 13
                    color = heading_color
                    line_height = 16
                    space_before = 14
                else: # p, li, blockquote
                    fontsize = 10.5
                    color = text_color
                    line_height = 14
                    space_before = 8

                # Check page overflow
                if curr_y + space_before + line_height * 2 > page_h - margin_y:
                    page = doc.new_page(width=page_w, height=page_h)
                    curr_y = margin_y + 20

                curr_y += space_before

                # Word wrap into lines
                words = text.split()
                line = ""
                for w in words:
                    test_line = (line + " " + w).strip()
                    # Approximate width in points: char_count * fontsize * 0.55
                    if len(test_line) * fontsize * 0.55 > content_w and line:
                        if curr_y + line_height > page_h - margin_y:
                            page = doc.new_page(width=page_w, height=page_h)
                            curr_y = margin_y + 20
                        page.insert_text(fitz.Point(margin_x, curr_y), line, fontsize=fontsize, color=color)
                        curr_y += line_height
                        line = w
                    else:
                        line = test_line

                if line:
                    if curr_y + line_height > page_h - margin_y:
                        page = doc.new_page(width=page_w, height=page_h)
                        curr_y = margin_y + 20
                    page.insert_text(fitz.Point(margin_x, curr_y), line, fontsize=fontsize, color=color)
                    curr_y += line_height

            # Add page numbers and footer
            total_pages = len(doc)
            for i, p in enumerate(doc):
                p.draw_line(fitz.Point(margin_x, page_h - 35), fitz.Point(page_w - margin_x, page_h - 35),
                            color=(0.8, 0.8, 0.8), width=0.8)
                p.insert_text(fitz.Point(page_w / 2 - 20, page_h - 20), f"Page {i + 1} of {total_pages}",
                              fontsize=9, color=meta_color)

            doc.set_toc(toc)
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            doc.save(output_path, deflate=True)
            doc.close()

            return True, f"Successfully created {total_pages}-page PDF from webpage:\n{output_path}"
        except Exception as e:
            return False, f"Failed to convert webpage: {str(e)}"

    @staticmethod
    def convert_images_to_pdf(
        image_paths: List[str],
        output_path: str,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Tuple[bool, str]:
        """
        Converts a list of images (PNG, JPEG, WEBP, BMP) into a multi-page PDF document.
        """
        if not image_paths:
            return False, "No images selected for conversion."

        try:
            doc = fitz.open()
            total = len(image_paths)

            for i, img_path in enumerate(image_paths):
                if not os.path.exists(img_path):
                    continue
                if progress_callback:
                    progress_callback(i + 1, total)

                # Open image with fitz
                img = fitz.open(img_path)
                rect = img[0].rect
                pdfbytes = img.convert_to_pdf()
                img.close()

                img_pdf = fitz.open("pdf", pdfbytes)
                page = doc.new_page(width=rect.width, height=rect.height)
                page.show_pdf_page(rect, img_pdf, 0)
                img_pdf.close()

            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            doc.save(output_path, deflate=True)
            doc.close()
            return True, f"Successfully converted {total} image(s) to:\n{output_path}"
        except Exception as e:
            return False, f"Failed to convert images to PDF: {str(e)}"
