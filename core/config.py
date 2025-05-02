import os
import copy
import yaml
from .constants import DEFAULT_STATE

class Config:
    def __init__(self):
        self.config_file = os.getenv("CONFIG_FILE")
        if not self.config_file:
            raise ValueError("CONFIG_FILE environment variable not set.")

    def load(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f) or {}
                return self._merge_with_defaults(copy.deepcopy(DEFAULT_STATE), yaml_data)
        else:
            return copy.deepcopy(DEFAULT_STATE)

    def save(self, state):
        with open(self.config_file, "w", encoding="utf-8") as f:
            yaml.safe_dump(state, f, sort_keys=False)
        return state

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