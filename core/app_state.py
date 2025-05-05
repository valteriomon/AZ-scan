import os
import copy
from pathlib import Path
from config import Config
import utils as utils

class AppState:
    def __init__(self):
        self._config = Config()
        self._state = self._config.load()  # Load the current state from some config source
        self._original_state = copy.deepcopy(self._state)  # Preserve an untouched copy
        self._side = "A" # Side not saved into config, assumed A

    def save_config(self):
        self._original_state = self._config.save(self._state)

    @property
    def prefix(self):
        prefix = self._state.get("last_scan", {}).get("prefix")
        if prefix:
            return prefix
        prefix_list = self.get_prefix_list()
        return prefix_list[0] if prefix_list else ""

    @prefix.setter
    def prefix(self, value: str):
        self._state["last_scan"]["prefix"] = value
        updated_prefixes = list(self._original_state.get("prefixes", []))
        if not utils.dict_key_has_value(updated_prefixes, "code", value):
            updated_prefixes.append({"code": value, "last_index": self.index})
        else:
            for entry in updated_prefixes:
                if entry["code"] == value:
                    entry["last_index"] = self.index
        self._state["prefixes"] = self.sort_prefixes(updated_prefixes)
        self._state["last_scan"]["filename"] = self.filename

    @property
    def index(self):
        return self.get_prefix_dict().get(self.prefix) or 1

    @index.setter
    def index(self, value):
        for prefix in self._state["prefixes"]:
            if prefix["code"] == self.prefix:
                prefix["last_index"] = value
                break
        self._state["last_scan"]["filename"] = self.filename

    @property
    def side(self):
        return self._side

    @side.setter
    def side(self, value):
        self._side = value
        self._state["last_scan"]["filename"] = self.filename

    @property
    def last_filepath(self) -> str:
        last_folder = self._original_state.get("last_scan", {}).get("folder")
        last_filename = self._original_state.get("last_scan", {}).get("filename")
        if last_folder and last_filename:
            return f"{os.path.join(last_folder, last_filename)}.{self.filetype}"
        return "No encontrado."

    @property
    def next_filepath(self) -> str:
        if self.folder and self.filename:
            return f"{os.path.join(self.folder, self.filename)}.{self.filetype}"
        return "No encontrado."

    @property
    def filename(self) -> str:
        return f"{self.prefix}_{self.index}_{self.side}"

    @property
    def folder(self) -> Path:
        folder = self._state.get("last_scan", {}).get("folder")
        return Path(folder) if folder else Path.home()

    @folder.setter
    def folder(self, folder: Path):
        self._state["last_scan"]["folder"] = str(folder)

    @property
    def filetype(self) -> str:
        return self._state.get("options", {}).get("scanner", {}).get("filetype", "jpg")

    @property
    def next_index(self) -> int:
        return int(self.index) + 1

    # Alt methods
    def get_prefix_list(self) -> list:
        return list(self.get_prefix_dict().keys())

    def get_prefix_dict(self):
        return {
            prefix["code"]: prefix.get("last_index") or 1
            for prefix in self._state.get("prefixes", [])
        }

    # Class utility methods
    @staticmethod
    def sort_prefixes(data):
        first = data[0:1]
        rest = sorted(data[1:], key=lambda x: x["code"])
        return first + rest