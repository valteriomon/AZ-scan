from .custom_error import FileAlreadyExistsError
from .config import Config
import os
import platform, shutil
import subprocess
from pathlib import Path

class Console:

    def __init__(self):
        self._config = Config()
        self._state = self._config.load()
        self._options = self._state["options"]

    @classmethod
    def run(cls, command, use_wsl=False, popen=False, **kwargs):
        """
        Run a command, with optional WSL support and popen execution.

        Args:
            command (list or str): The command to run.
            use_wsl (bool): Whether to run under WSL on Windows.
            popen (bool): Use subprocess.Popen instead of subprocess.run.
            kwargs: Additional keyword arguments passed to subprocess.
        """

        is_windows = platform.system().lower() == "windows"

        if isinstance(command, list):
            command = [str(arg) for arg in command]
            if is_windows and use_wsl:
                if shutil.which("wsl") is None:
                    raise EnvironmentError("WSL is not installed or not found in PATH")

                command_with_linux_paths = []
                for arg in command:
                    if os.path.exists(arg):
                        abs_path = os.path.abspath(arg)
                        command_with_linux_paths.append(PathConverter.to_wsl_path(abs_path))
                    else:
                        command_with_linux_paths.append(arg)
                command = command_with_linux_paths

                command = ['wsl'] + command
            command_str = " ".join(command)
        else:
            command_str = str(command)
            if is_windows and use_wsl:
                command = f"wsl {command_str}"

        print(f"Running command: {command_str}")

        try:
            kwargs.setdefault("text", True)
            if popen:
                process = subprocess.Popen(command, **kwargs)
                return process
            else:
                kwargs.setdefault("capture_output", False)
                kwargs.setdefault("check", True)
                result = subprocess.run(command, **kwargs)
                print("Command completed successfully.")
                return result
        except subprocess.CalledProcessError as e:
            print(f"Command failed with return code {e.returncode}")
            print(f"Output: {e.output}")
            raise

    @classmethod
    def to_wsl_path(cls, path):
        # Converts "C:\Users\Me\file.txt" to "/mnt/c/Users/Me/file.txt"
        drive, rest = os.path.splitdrive(path)
        return f"/mnt/{drive[0].lower()}{rest.replace(os.sep, '/')}"

    @classmethod
    def to_windows_path(cls, wsl_path):
        # Converts "/mnt/c/Users/Me/file.txt" to "C:\Users\Me\file.txt"
        if wsl_path.startswith("/mnt/") and len(wsl_path) > 6:
            drive_letter = wsl_path[5].upper()
            rest = wsl_path[6:]  # everything after /mnt/c
            windows_path = f"{drive_letter}:{rest}".replace("/", os.sep)
            return windows_path
        return wsl_path  # return unchanged if not a WSL path

    @classmethod
    def wsl(cls, command, popen=False, **kwargs):
        return cls.run(command, use_wsl=True, popen=popen, **kwargs)

    # Naps2 CLI
    # https://www.naps2.com/doc/command-line
    def scan(self, output_filepath) -> bool:
        if Path(output_filepath).is_file():
            raise FileAlreadyExistsError(f"File already exists: {output_filepath}")

        command_values = {
            "naps2_path": self._options["scanner"]["naps2_path"],
            "driver": self._options["scanner"]["driver"],
            "device": self._options["scanner"]["device"],
            "dpi": self._options["scanner"]["dpi"],
        }

        # Convert all values in command_values to strings
        command_values = {key: str(value) for key, value in command_values.items()}

        command = [
            command_values["naps2_path"],
            '--output', output_filepath,
            '--noprofile',
            '--driver', command_values["driver"],
            '--device', command_values["device"],
            '--dpi', command_values["dpi"],
            '--force'
        ]
        self.run(command)
        return True

    # Fred's ImageMagick multicrop through WSL
    # http://www.fmwconcepts.com/imagemagick/multicrop/index.php
    # def autocrop(self, path, full_filename):
    #     input_file = f"{path}/{full_filename}"
    #     output_file = f"tmp/{full_filename}"
    #     command_values = {
    #         "discard": '200',
    #         "crop_factor": '10',
    #         "coordinates": "0,0"
    #     }
    #     command = [
    #         'wsl',
    #         './scripts/multicrop',
    #         '-d', command_values["discard"],
    #         '-f', command_values["crop_factor"],
    #         '-c', command_values["coordinates"],
    #         input_file,
    #         output_file
    #     ]
    #     self.run(command)

class PathConverter:

    @classmethod
    def to_wsl_path(cls, path):
        # Converts "C:\Users\Me\file.txt" to "/mnt/c/Users/Me/file.txt"
        drive, rest = os.path.splitdrive(path)
        if drive:
            return f"/mnt/{drive[0].lower()}{rest.replace(os.sep, '/')}"
        return path

    @classmethod
    def to_windows_path(cls, wsl_path):
        # Converts "/mnt/c/Users/Me/file.txt" to "C:\Users\Me\file.txt"
        if wsl_path.startswith("/mnt/") and len(wsl_path) > 6:
            drive_letter = wsl_path[5].upper()
            rest = wsl_path[6:]
            return f"{drive_letter}:{rest}".replace("/", os.sep)
        return wsl_path

    @classmethod
    def to_native_path(cls, path):
        if platform.system() == "Windows":
            return cls.to_windows_path(path)
        else:
            return cls.to_wsl_path(path)