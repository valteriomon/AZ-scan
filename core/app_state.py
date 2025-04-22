from pathlib import Path
from .config import Config

class AppState:
    def __init__(self):
        self.config = Config.load()

        self.scan_folder = Path(self.config.get("last_folder", Path.home()))
        self.next_filename = 1
        self.prev_filename = 1

        self.prefix_dict = {
            prefix["code"]: prefix.get("last_index", 1)
            for prefix in self.config.get("prefixes", [])
        }
        self.prefix_list = list(self.prefix_dict.keys())

    def get_last_prefix(self) -> str:
        # Fallback to first prefix if not set
        return self.config.get("last_prefix") or (self.prefix_list[0] if self.prefix_list else "")

    def set_last_prefix(self, prefix: str):
        self.config["last_prefix"] = prefix
        self.config.save()

    def get_last_index(self, prefix: str = None) -> int:
        prefix = prefix or self.get_last_prefix()
        return self.prefix_dict.get(prefix, 1)

    def set_last_index(self, prefix: str, index: int):
        self.prefix_dict[prefix] = index
        for item in self.config.get("prefixes", []):
            if item["code"] == prefix:
                item["last_index"] = index
                break
        self.config["last_index"] = index
        self.config.save()

    def get_last_folder(self) -> Path:
        return Path(self.config.get("last_folder", str(self.scan_folder)))

    def set_last_folder(self, folder: Path):
        self.scan_folder = folder
        self.config["last_folder"] = str(folder)
        self.config.save()

    def get_last_scan(self) -> str:
        value = self.config.get("last_scan") or "No encontrado."
        return str(Path(value))

    def set_last_scan(self, scan: Path):
        self.config["last_scan"] = str(scan)
        self.config.save()

    def get_prefix_list(self) -> list:
        return self.prefix_list