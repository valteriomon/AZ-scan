FILE_PATH = "config.yml"
APP_TITLE = "AZ-scan - Escáner de Archivos"
POSTCARD_VIEW_TITLE = "Postales"
MAPS_VIEW_TITLE = "Postales"

DEFAULT_STATE = {
    "prefixes": [
        {"code": "TBD", "last_index": None}
    ],
    "last_scan": {
        "prefix": None,
        "directory": None,
        "filename": None,
    },
    "scanner": {
        "driver": "wia",
        "device": "lide",
        "dpi": 600,
        "filetype": "png"
    }
}