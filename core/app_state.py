import os
import copy
from pathlib import Path
from core.config import Config
import core.utils as utils

class AppState:
    def __init__(self):
        self._config = Config()
        self._state = self._config.load()
        self._original_state = copy.deepcopy(self._state)
        self._side = "A"

    # Properties
    @property
    def folder(self):
        folder = self._state.get("last_scan", {}).get("folder", None)
        return Path(folder) if folder else Path.home()

    @folder.setter
    def folder(self, value):
        self._state["last_scan"]["folder"] = str(value)

    @property
    def prefix(self):
        prefix = self._state.get("last_scan", {}).get("prefix", None)
        if prefix:
            return prefix
        return self.prefix_list[0] if self.prefix_list else ""

    @prefix.setter
    def prefix(self, value: str):
        self._state["last_scan"]["prefix"] = value
        updated_prefixes = list(self._original_state.get("prefixes", []))
        if not utils.dict_key_has_value(updated_prefixes, "code", value):
            self.index = 1
            updated_prefixes.append({"code": value, "last_index": self.index})
        else:
            for entry in updated_prefixes:
                if entry["code"] == value:
                    entry["last_index"] = self.index
        self._state["prefixes"] = self.sort_prefixes(updated_prefixes)

    @property
    def index(self):
        return self.get_prefix_dict().get(self.prefix) or 0

    @index.setter
    def index(self, value):
        for prefix in self._state["prefixes"]:
            if prefix["code"] == self.prefix:
                prefix["last_index"] = value
                break

    @property
    def side(self):
        return self._side

    @side.setter
    def side(self, value):
        self._side = value

    @property
    def last_scan(self):
        last_folder = self._original_state.get("last_scan", {}).get("folder", None)
        last_prefix = self._original_state.get("last_scan", {}).get("prefix", None)
        last_filename = self._original_state.get("last_scan", {}).get("filename", None)
        if last_folder and last_prefix and last_filename:
            return f"{os.path.join(last_folder, last_prefix, last_filename)}.{self.filetype}"
        return "No encontrado."

    @property
    def prefix_list(self) -> list:
        return list(self.get_prefix_dict().keys())

    @property
    def next_scan(self) -> str:
        if self.folder and self.filename:
            return f"{os.path.join(self.folder, self.prefix, self.filename)}.{self.filetype}"

    @property
    def filename(self) -> str:
        self._state["last_scan"]["filename"] = f"{self.prefix}_{self.index}_{self.side}"
        return self._state["last_scan"]["filename"]

    @property
    def filetype(self) -> str:
        return self._state.get("options", {}).get("scanner", {}).get("filetype", "jpg")

    # Methods
    def get_prefix_dict(self):
        return {
            prefix["code"]: prefix.get("last_index") or 1
            for prefix in self._state.get("prefixes", [])
        }

    def save_config(self):
        temp_state = copy.deepcopy(self._state)
        for prefix in temp_state["prefixes"]:
            if prefix["code"] == self.prefix:
                prefix["last_index"] += 1
                break

        self._original_state = self._config.save(temp_state)

    @staticmethod
    def sort_prefixes(data):
        first = data[0:1]
        rest = sorted(data[1:], key=lambda x: x["code"])
        return first + rest