"""
Settings management for Lumina PDF Reader.
Persists user preferences like theme, view mode, recent files, and window geometry.
"""
from PyQt6.QtCore import QSettings
import os
import json

class AppSettings:
    ORGANIZATION = "LuminaApps"
    APPLICATION = "LuminaPDF"

    def __init__(self):
        self.settings = QSettings(self.ORGANIZATION, self.APPLICATION)

    # Theme: 'dark', 'light', 'sepia'
    @property
    def theme(self) -> str:
        return self.settings.value("theme", "dark", type=str)

    @theme.setter
    def theme(self, value: str):
        self.settings.setValue("theme", value)

    # View mode: 'single', 'book', 'continuous'
    @property
    def view_mode(self) -> str:
        return self.settings.value("view_mode", "book", type=str)

    @view_mode.setter
    def view_mode(self, value: str):
        self.settings.setValue("view_mode", value)

    # Book mode cover offset: bool
    @property
    def book_cover_offset(self) -> bool:
        return self.settings.value("book_cover_offset", True, type=bool)

    @book_cover_offset.setter
    def book_cover_offset(self, value: bool):
        self.settings.setValue("book_cover_offset", value)

    # Recent files: list of file paths
    @property
    def recent_files(self) -> list:
        val = self.settings.value("recent_files", "[]", type=str)
        try:
            files = json.loads(val)
            # Filter out non-existent files
            return [f for f in files if os.path.exists(f)]
        except Exception:
            return []

    def add_recent_file(self, file_path: str):
        if not file_path or not os.path.exists(file_path):
            return
        files = self.recent_files
        norm_path = os.path.abspath(file_path)
        if norm_path in files:
            files.remove(norm_path)
        files.insert(0, norm_path)
        # Keep top 15
        files = files[:15]
        self.settings.setValue("recent_files", json.dumps(files))

    def clear_recent_files(self):
        self.settings.setValue("recent_files", "[]")

    # Zoom mode: 'fit_width', 'fit_page', 'custom'
    @property
    def zoom_mode(self) -> str:
        return self.settings.value("zoom_mode", "fit_page", type=str)

    @zoom_mode.setter
    def zoom_mode(self, value: str):
        self.settings.setValue("zoom_mode", value)

    # Last zoom factor: float (e.g. 1.0, 1.25)
    @property
    def zoom_factor(self) -> float:
        return float(self.settings.value("zoom_factor", 1.0))

    @zoom_factor.setter
    def zoom_factor(self, value: float):
        self.settings.setValue("zoom_factor", value)

    # Sidebar visible: bool
    @property
    def sidebar_visible(self) -> bool:
        return self.settings.value("sidebar_visible", True, type=bool)

    @sidebar_visible.setter
    def sidebar_visible(self, value: bool):
        self.settings.setValue("sidebar_visible", value)

    # Window geometry & state
    def save_window_state(self, geometry, window_state):
        self.settings.setValue("geometry", geometry)
        self.settings.setValue("windowState", window_state)

    def load_window_geometry(self):
        return self.settings.value("geometry")

    def load_window_state(self):
        return self.settings.value("windowState")
