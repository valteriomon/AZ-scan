from .constants import APP_TITLE, MAPS_VIEW_TITLE

class MapView:
    def __init__(self, root):
        self.root = root
        root.title(f"{APP_TITLE} - {MAPS_VIEW_TITLE}")