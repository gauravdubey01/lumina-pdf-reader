"""
PDF Tools: Merge, Split, Extract, Rotate, Delete pages.
Powered by PyMuPDF (fitz) for speed and fidelity.
"""
import pymupdf as fitz
import os
from typing import List, Callable, Optional, Tuple

class PDFTools:
    @staticmethod
    def merge_pdfs(
        file_paths: List[str],
        output_path: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Tuple[bool, str]:
        """
        Merges multiple PDF files into one output PDF.
        progress_callback: fn(current_index, total_files, current_filename)
        """
        if not file_paths:
            return False, "No PDF files selected to merge."

        try:
            merged_doc = fitz.open()
            total = len(file_paths)

            for i, fpath in enumerate(file_paths):
                if not os.path.exists(fpath):
                    continue
                if progress_callback:
                    progress_callback(i + 1, total, os.path.basename(fpath))

                with fitz.open(fpath) as src_doc:
                    merged_doc.insert_pdf(src_doc)

            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            merged_doc.save(output_path, deflate=True)
            merged_doc.close()
            return True, f"Successfully merged {total} files into:\n{output_path}"
        except Exception as e:
            return False, f"Failed to merge PDFs: {str(e)}"

    @staticmethod
    def parse_page_range(range_str: str, total_pages: int) -> List[int]:
        """
        Parses page range strings like '1-3, 5, 7-10' into 0-indexed page numbers.
        """
        pages = set()
        parts = [p.strip() for p in range_str.split(",") if p.strip()]
        for part in parts:
            if "-" in part:
                tokens = part.split("-")
                if len(tokens) == 2:
                    try:
                        start = int(tokens[0].strip())
                        end = int(tokens[1].strip())
                        start = max(1, min(start, total_pages))
                        end = max(1, min(end, total_pages))
                        for p in range(min(start, end), max(start, end) + 1):
                            pages.add(p - 1)
                    except ValueError:
                        pass
            else:
                try:
                    p = int(part)
                    if 1 <= p <= total_pages:
                        pages.add(p - 1)
                except ValueError:
                    pass
        return sorted(list(pages))

    @staticmethod
    def split_pdf_by_range(
        input_path: str,
        page_range_str: str,
        output_path: str
    ) -> Tuple[bool, str]:
        """
        Extracts selected pages from input PDF to output PDF.
        """
        try:
            with fitz.open(input_path) as src_doc:
                total_pages = len(src_doc)
                pages_to_keep = PDFTools.parse_page_range(page_range_str, total_pages)
                if not pages_to_keep:
                    return False, "No valid pages found in the specified range."

                out_doc = fitz.open()
                out_doc.insert_pdf(src_doc, from_page=0, to_page=0) # dummy init or select
                out_doc.close()
                out_doc = fitz.open()
                for p in pages_to_keep:
                    out_doc.insert_pdf(src_doc, from_page=p, to_page=p)

                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                out_doc.save(output_path, deflate=True)
                out_doc.close()
                return True, f"Saved {len(pages_to_keep)} pages to:\n{output_path}"
        except Exception as e:
            return False, f"Failed to extract pages: {str(e)}"

    @staticmethod
    def split_into_single_pages(
        input_path: str,
        output_dir: str,
        prefix: str = "page_",
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Tuple[bool, str]:
        """
        Splits PDF into individual single-page PDF files.
        """
        try:
            with fitz.open(input_path) as src_doc:
                total_pages = len(src_doc)
                os.makedirs(output_dir, exist_ok=True)

                base_name = os.path.splitext(os.path.basename(input_path))[0]
                for i in range(total_pages):
                    if progress_callback:
                        progress_callback(i + 1, total_pages)
                    out_doc = fitz.open()
                    out_doc.insert_pdf(src_doc, from_page=i, to_page=i)
                    out_file = os.path.join(output_dir, f"{base_name}_{prefix}{i + 1:04d}.pdf")
                    out_doc.save(out_file, deflate=True)
                    out_doc.close()

                return True, f"Successfully split {total_pages} pages into folder:\n{output_dir}"
        except Exception as e:
            return False, f"Failed to split PDF: {str(e)}"

    @staticmethod
    def split_every_n_pages(
        input_path: str,
        n_pages: int,
        output_dir: str,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Tuple[bool, str]:
        """
        Splits PDF into chunks of N pages each.
        """
        if n_pages <= 0:
            return False, "Number of pages must be greater than 0."

        try:
            with fitz.open(input_path) as src_doc:
                total_pages = len(src_doc)
                os.makedirs(output_dir, exist_ok=True)
                base_name = os.path.splitext(os.path.basename(input_path))[0]

                chunk_idx = 1
                for start_page in range(0, total_pages, n_pages):
                    end_page = min(start_page + n_pages - 1, total_pages - 1)
                    if progress_callback:
                        progress_callback(start_page + 1, total_pages)

                    out_doc = fitz.open()
                    out_doc.insert_pdf(src_doc, from_page=start_page, to_page=end_page)
                    out_file = os.path.join(
                        output_dir,
                        f"{base_name}_part{chunk_idx:02d}_p{start_page + 1}-{end_page + 1}.pdf"
                    )
                    out_doc.save(out_file, deflate=True)
                    out_doc.close()
                    chunk_idx += 1

                return True, f"Successfully created {chunk_idx - 1} parts in folder:\n{output_dir}"
        except Exception as e:
            return False, f"Failed to split PDF: {str(e)}"

    @staticmethod
    def rotate_pdf_pages(
        input_path: str,
        rotation_angle: int,
        output_path: str
    ) -> Tuple[bool, str]:
        """
        Rotates all pages of PDF by rotation_angle (90, 180, 270) and saves.
        """
        try:
            with fitz.open(input_path) as src_doc:
                for page in src_doc:
                    page.set_rotation((page.rotation + rotation_angle) % 360)
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                src_doc.save(output_path, deflate=True)
                return True, f"Saved rotated PDF to:\n{output_path}"
        except Exception as e:
            return False, f"Failed to rotate PDF: {str(e)}"
