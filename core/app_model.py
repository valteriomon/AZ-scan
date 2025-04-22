from .config import Config

class AppModel:
    def __init__(self):
        self.config = Config.load()

        # Get prefixes dict from config
        prefixes = self.config.get('prefixes', [])

        # Build a dict from code -> last_index
        prefix_dict = {prefix["code"]: prefix.get("last_index") for prefix in prefixes}
        prefix_codes = list(prefix_dict.keys())

        # Determine last_prefix
        last_prefix = self.config.get("last_prefix", "")
        if not last_prefix and len(prefixes) > 0:
            last_prefix = prefixes[0].get('code')

        # Determine last_index
        last_index = 1
        if last_prefix and last_prefix in prefix_dict:
            last_index = prefix_dict.get(last_prefix) or 1
