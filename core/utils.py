class Utils:

    @classmethod
    def dict_key_has_value(cls, dict, key, value):
        return any(entry.get(key) == value for entry in dict)