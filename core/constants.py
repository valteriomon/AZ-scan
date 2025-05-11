import os

APP_TITLE = "AZ-scan - Escáner de Archivos - Fundación Azara"
POSTCARD_VIEW_TITLE = "Postales"
MAPS_VIEW_TITLE = "Mapas"
VIEWER_VIEW_TITLE = "Visor"
EDITOR_VIEW_TITLE = "Editor"

SCANNER_DRIVER = "wia" if os.getenv('ENVIRONMENT', 'prod') == 'dev' else "twain"
SCANNER_DEVICE = "lide" if os.getenv('ENVIRONMENT', 'prod') == 'dev' else "twain"

DEFAULT_STATE = {
    "prefixes": [
        {"code": "00_TBD", "last_index": None}
    ],
    "last_scan": {
        "prefix": None,
        "folder": None,
        "filename": None,
    },
    "options": {
        "scanner": {
            "naps2_path": "C:\\Program Files\\NAPS2\\NAPS2.Console.exe",
            "driver": SCANNER_DRIVER,
            "device": SCANNER_DEVICE,
            "dpi": 600,
            "filetype": "png"
        }
    },
    "multi_scan": {
        "folder": None
    }
}


TKINTER_STYLES = {
    "BIG_FONT": {
        "font": ("Segoe UI", 12, "bold")
    }
}