import os
import glob
import time
import uuid
import core.constants
from PIL import Image
from PIL.ExifTags import TAGS

def dict_key_has_value(dict, key, value):
    """
    Checks if a dictionary contains a specific key with a specific value
    """
    return any(entry.get(key) == value for entry in dict)

def alpha_converter(value, zero_based=False):
    """
    Converts an integer to an alphabetical string, and vice versa, starting at 1 (A = 1).
    """
    # Try to treat numeric strings like numbers
    if isinstance(value, str):
        value = value.strip()
        if value.isdigit():
            value = int(value)
        elif value.isalpha():
            value = value.upper()
            result = 0
            for char in value:
                result = result * 26 + (ord(char) - ord('A') + 1)
            return result - (1 if zero_based else 0)
        else:
            raise ValueError("String input must be either a number or letters only")
    # Now handle numeric input (int or digit string converted to int)
    if isinstance(value, int):
        if zero_based:
            if value < 0:
                raise ValueError("Number must be >= 0 for zero-based")
            value += 1  # Internally adjust for letter calculation
        else:
            if value < 1:
                raise ValueError("Number must be >= 1")

        result = ''
        while value > 0:
            value -= 1  # Adjust value to make A=1
            result = chr(value % 26 + ord('A')) + result
            value = value // 26
        return result
    raise TypeError("Input must be an int or a string containing either digits or letters only")

def get_last_valid_element(arr):
    for i in reversed(range(len(arr))):
        item = arr[i]
        if item not in (None, [], '', {}):
            return item, i
    raise ValueError("No valid (non-empty, non-None) element found.")

def get_first_valid_element(arr):
    for i in range(len(arr)):
        item = arr[i]
        if item not in (None, [], '', {}):
            return item, i
    raise ValueError("No valid (non-empty, non-None) element found.")

def count_valid_elements(arr):
    return sum(1 for item in arr if item not in (None, '', [], {}))

def rotate_matrix_180(matrix):
    return [row[::-1] for row in matrix[::-1]]

def uuid():
    return str(uuid.uuid4())

def current_unix_timestamp():
    return int(time.time())

#################################
#### File and directory helpers
#################################

class FileSystemUtils():
    def __init__(self, directory):
        self.directory = directory

    @staticmethod
    def get_filename_without_extension_or_final_folder(fullpath_or_full_filename):
        return os.path.splitext(os.path.basename(fullpath_or_full_filename))[0]

    @staticmethod
    def get_images_from_dir(self, path):
        extensions = ('*.jpg', '*.jpeg', '*.png', '*.tif', '*.tiff')
        images = []
        for ext in extensions:
            images.extend(glob.glob(os.path.join(path, ext)))
        return sorted(images)

    @staticmethod
    def create_folder(folder_name, path=None, exist_ok=True):
        target_path = os.path.join(path or os.getcwd(), folder_name)
        os.makedirs(target_path, exist_ok)
        return target_path
    # def list_filenames(directory, pattern="*"):
    #     """
    #     Returns a list of filenames (not full paths) in the given directory matching the pattern.

    #     Parameters:
    #         directory (str): The path to the directory.
    #         pattern (str): The file pattern to match (default is "*.png").

    #     Returns:
    #         list[str]: List of matching filenames.
    #     """
    #     search_path = os.path.join(directory, pattern)
    #     return [os.path.basename(f) for f in glob.glob(search_path)]

    # def list_folders(directory):
    #     """
    #     Returns a list of folder names in the given directory.

    #     Parameters:
    #         directory (str): The path to the directory.

    #     Returns:
    #         list[str]: List of folder names (not full paths).
    #     """
    #     return [name for name in os.listdir(directory)
    #             if os.path.isdir(os.path.join(directory, name))]


class ImageUtils:
    def __init__(self, filename, image):
        self.filename = filename
        self.image = image

    @staticmethod
    def get_rotation_degrees(path):
        orientation = ImageUtils._get_exif_orientation(path)
        return ImageUtils._get_rotation_degrees(orientation)

    @staticmethod
    def _get_exif_orientation(path):
        with Image.open(path) as img:
            exif = img._getexif()
            if not exif:
                return None

            for tag, value in exif.items():
                tag_name = TAGS.get(tag, tag)
                if tag_name == 'Orientation':
                    return value
            return None

    @staticmethod
    def _get_rotation_degrees(orientation):
        if orientation == 1:
            return 0
        elif orientation == 3:
            return 180
        elif orientation == 6:
            return 90
        elif orientation == 8:
            return 270
        elif orientation == 2:
            return "Mirrored horizontally"
        elif orientation == 4:
            return "Mirrored vertically"
        elif orientation == 5:
            return "Mirrored horizontally, then rotated 270°"
        elif orientation == 7:
            return "Mirrored horizontally, then rotated 90°"
        return None