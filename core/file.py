from pathlib import Path

class File:

    def save():
        pass

    def load():
        pass

    @classmethod
    def exists(self, full_path) -> bool:
        return Path(full_path).exists()