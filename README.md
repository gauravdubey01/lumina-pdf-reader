# Lumina PDF Reader & Tools 📖

A modern, fast, and feature-rich Windows PDF Reader desktop application built with Python, PyQt6, and PyMuPDF.

![Lumina PDF Icon](assets/icon.png)

## ✨ Features

- **🎨 Modern Windows 11 Fluent UI & Themes**:
  - 🌙 **Dark Mode**: OLED/Dark UI with smart inverted PDF page rendering for comfortable night reading.
  - ☀️ **Light Mode**: Clean, crisp daytime reading theme.
  - 📜 **Sepia Warm Paper Mode**: Eye-comfort warm tone filtering blue light.
- **📖 Book Reading Mode (Two-Page Spread)**:
  - Side-by-side two-page reading layout with realistic book crease shadow and cover page offset simulation.
  - Single Page mode and Continuous Vertical Scroll mode.
  - Interactive smooth zoom (`Ctrl + Mouse Wheel`, Fit-to-Page, Fit-to-Width) and mouse panning.
- **📑 Interactive Sidebar (`Ctrl + B`)**:
  - **Page Thumbnails Tab**: Live grid of page previews with active page tracking.
  - **Bookmarks / Table of Contents Tab**: Hierarchical document outline navigation.
  - **Full-Text Search Tab**: Instant search with snippet previews and yellow highlight overlays on the PDF canvas.
- **🛠️ Built-in PDF Power Tools**:
  - 🔀 **Merge PDFs**: Combine multiple PDF documents with drag/reorder support.
  - ✂️ **Split PDF**: Extract custom page ranges, burst all pages into single files, or split into equal $N$-page chunks.
  - 🔄 **Rotate Pages**: 90° clockwise/counter-clockwise.
- **🚀 Standalone Executable**:
  - Single `.exe` build ready to run without installing Python or dependencies.

---

## 🚀 Quick Start

### Running from Source
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python main.py
   # or double-click run.bat
   ```

### Building Standalone EXE
```bash
python build_exe.py
# or double-click build_exe.bat
```
The resulting executable will be in `dist/LuminaPDF.exe`.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Ctrl + O` | Open PDF File |
| `Ctrl + B` | Toggle Sidebar (Thumbnails / TOC / Search) |
| `Right Arrow` / `Space` / `PageDown` | Next Page (or Next 2 Pages in Book Mode) |
| `Left Arrow` / `PageUp` | Previous Page |
| `Home` / `End` | First Page / Last Page |
| `Ctrl + Wheel` | Smooth Zoom In / Zoom Out |
| `Ctrl + +` / `Ctrl + -` | Zoom In / Zoom Out |
| `Ctrl + 0` | Reset Zoom (100%) |
| `Ctrl + R` | Rotate Clockwise (90°) |
| `F11` | Toggle Fullscreen Mode |
| `Ctrl + Q` | Exit Application |

---

## 📄 License
MIT License
