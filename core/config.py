import os
import yaml

class Config:
    FILE = "config.yml"
    data = {}  # This is the shared config dictionary

    @classmethod
    def load(cls):
        if os.path.exists(cls.FILE):
            with open(cls.FILE, "r") as f:
                cls.data = yaml.safe_load(f) or {}
        else:
            cls.data = {}
        return cls

    @classmethod
    def get(cls, key, default=None):
        return cls.data.get(key, default)

    @classmethod
    def __getitem__(cls, key):
        return cls.data[key]

    @classmethod
    def __setitem__(cls, key, value):
        cls.data[key] = value

    @classmethod
    def save(cls):
        with open(cls.FILE, "w") as f:
            yaml.dump(cls.data, f)
