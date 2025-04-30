import os
import yaml
import copy
from pathlib import Path
from .constants import FILE_PATH, DEFAULT_STATE

class AppState:
    def __init__(self):
        self.load_config()

    def load_config(self):
        """Load state from a YAML file and override defaults."""
        if os.path.exists(FILE_PATH):
            with open(FILE_PATH, "r", encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f) or {}
                self._state = self._merge_with_defaults(copy.deepcopy(DEFAULT_STATE), yaml_data)
        else:
            self._state = copy.deepcopy(DEFAULT_STATE)
            self.save()
        self._original_state = copy.deepcopy(self._state)

    def save_config(self):
        """Save current state to the YAML file."""
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            yaml.safe_dump(self._state, f, sort_keys=False)
            self._original_state = copy.deepcopy(self._state)

    def _merge_with_defaults(self, default, override):
        if isinstance(default, dict):
            merged = default.copy()
            for k, v in override.items():
                if k in merged:
                    merged[k] = self._merge_with_defaults(merged[k], v)
                else:
                    merged[k] = v
            return merged
        elif isinstance(default, list) and all(isinstance(i, dict) for i in default):
            # Override based on matching 'code' key if present
            if all("code" in item for item in default):
                merged = {item["code"]: item.copy() for item in default}
                for item in override:
                    code = item.get("code")
                    if code in merged:
                        merged[code].update(item)
                    else:
                        merged[code] = item
                return list(merged.values())
            else:
                return override
        else:
            return override

    def get_prefix_list(self) -> list:
        return list(self.get_prefix_dict().keys())

    def get_prefix_dict(self):
        return {
            prefix["code"]: prefix.get("last_index") or 1
            for prefix in self._state.get("prefixes", [])
        }

    def get_last_prefix(self) -> str:
        prefix = self._state.get("last_scan", {}).get("prefix")
        if prefix:
            return prefix
        prefix_list = self.get_prefix_list()
        return prefix_list[0] if prefix_list else ""

    def get_last_index(self, prefix: str = None) -> int:
        prefix = prefix or self.get_last_prefix()
        return self.get_prefix_dict().get(prefix) or 1

    def get_last_filepath(self) -> str:
        directory = self._state.get("last_scan", {}).get("directory")
        filename = self._state.get("last_scan", {}).get("filename")
        if directory and filename:
            return os.path.join(directory, filename)
        return "No encontrado."

    def get_last_folder(self) -> Path:
        return Path(self._state.get("last_scan", {}).get("directory") or Path.home())

    def get_scanner(self) -> dict:
        return self._state.get("scanner", {})

    # Setters
    def set_last_prefix(self, prefix: str, index: int = 1):
        self._state["last_scan"]["prefix"] = prefix
        # Work with a copy of the original prefixes
        updated_prefixes = list(self._original_state.get("prefixes", []))
        if not self.code_exists(updated_prefixes, prefix):
            updated_prefixes.append({"code": prefix, "last_index": index})
        else:
            for entry in updated_prefixes:
                if entry["code"] == prefix:
                    entry["last_index"] = index
        self._state["prefixes"] = self.sort_prefixes(updated_prefixes)

    def code_exists(self, prefixes, code):
        return any(entry.get("code") == code for entry in prefixes)

    def sort_prefixes(self, data):
        first = data[0:1]
        rest = sorted(data[1:], key=lambda x: x["code"])
        return first + rest

    def set_last_index(self, code, index):
        for prefix in self._state["prefixes"]:
            if prefix["code"] == code:
                prefix["last_index"] = index
                break

    def set_last_folder(self, folder: Path):
        self._state["last_scan"]["directory"] = str(folder)

    # Last filename