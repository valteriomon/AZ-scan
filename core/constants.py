APP_TITLE = "AZ-scan - Escáner de Archivos - Fundación Azara"
POSTCARD_VIEW_TITLE = "Postales"
MAPS_VIEW_TITLE = "Mapas"
VIEWER_VIEW_TITLE = "Visor"

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
            "driver": "wia",
            "device": "lide",
            "dpi": 600,
            "filetype": "png"
        }
    }
}

TKINTER_STYLES = {
    "BIG_FONT": {
        "font": ("Segoe UI", 12, "bold")
    }
}