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

    def run(self, command, use_wsl=False, **kwargs):
        """
        Run a command, automatically prepending 'wsl' on Windows and
        converting paths if requested.

        Args:
            command (list or str): The command to run.
            wsl_paths (bool): Convert file paths to WSL format (only on Windows).
            kwargs: Passed to subprocess.run.
        """
        kwargs.setdefault("capture_output", False)
        kwargs.setdefault("check", True)
        kwargs.setdefault("text", True)

        is_windows = platform.system().lower() == "windows"

        if isinstance(command, list):
            command = [str(arg) for arg in command]  # Ensure all elements are strings

            if is_windows and use_wsl:
                if shutil.which("wsl") is None:
                    raise EnvironmentError("WSL is not installed or not found in PATH")

                command = [
                    self.to_wsl_path(arg) if os.path.exists(arg) else arg
                    for arg in command
                ]
                command = ['wsl'] + command

            command_str = " ".join(command)
        else:
            command_str = str(command)

            if is_windows and use_wsl:
                command = f"wsl {command_str}"

        print(f"Running command: {command_str}")

        try:
            result = subprocess.run(command, **kwargs)
            print("Command completed successfully.")
            return result
        except subprocess.CalledProcessError as e:
            print(f"Command failed with return code {e.returncode}")
            print(f"Output: {e.output}")
            raise

    def to_wsl_path(self, path):
        # Converts "C:\Users\Me\file.txt" to "/mnt/c/Users/Me/file.txt"
        drive, rest = os.path.splitdrive(path)
        return f"/mnt/{drive[0].lower()}{rest.replace(os.sep, '/')}"

    def wsl(self, command, **kwargs):
        return self.run(command, use_wsl=True, **kwargs)

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