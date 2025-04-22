import os
import yaml

class Config:
    FILE = "config.yml"

    @classmethod
    def load(cls):
        if os.path.exists(cls.FILE):
            with open(cls.FILE, "r") as f:
                return yaml.safe_load(f) or {}
        return {}

    @classmethod
    def get(cls, key, default=None):
        return cls.data.get(key, default)

    @classmethod
    def set(cls, key, value):
        cls.data[key] = value

    @classmethod
    def save(cls):
        with open(cls.FILE, "w") as f:
            yaml.dump(cls.data, f)

# import os
# import yaml

# class Config:
#     def __init__(self, path="config.yaml"):
#         self.path = path
#         self.data = self.load()

#     def load(self):
#         if os.path.exists(self.path):
#             with open(self.path, "r") as f:
#                 return yaml.safe_load(f) or {}
#         return {}

#     def save(self):
#         with open(self.path, "w") as f:
#             yaml.dump(self.data, f)

#     def get(self, key, default=None):
#         return self.data.get(key, default)

#     def set(self, key, value):
#         self.data[key] = value