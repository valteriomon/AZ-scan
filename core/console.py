from .custom_error import FileAlreadyExistsError
from .config import Config
import subprocess

from pathlib import Path

class Console:

    def __init__(self):
        self._config = Config()
        self._state = self._config.load()
        self._options = self._state["options"]

    def run(self, command, **kwargs):
        """
        Run a command using subprocess.run.

        Args:
            command (list or str): The command to run.
            kwargs: Additional keyword arguments for subprocess.run.

        Returns:
            CompletedProcess: The result of subprocess.run.
        """
        command_str = " ".join(str(arg) for arg in command) if isinstance(command, list) else command
        print(f"Running command: {command_str}")

        try:
            result = subprocess.run(command, capture_output=False, check=True, text=True, **kwargs)
            print("Command completed successfully.")
            return result
        except subprocess.CalledProcessError as e:
            print(f"Command failed with return code {e.returncode}")
            print(f"Output: {e.output}")
            return e

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
    def crop(self, path, full_filename):
        input_file = f"{path}/{full_filename}"
        output_file = f"tmp/{full_filename}"
        command_values = {
            "discard": '200',
            "crop_factor": '10',
            "coordinates": "0,0"
        }
        command = [
            'wsl',
            './scripts/multicrop',
            '-d', command_values["discard"],
            '-f', command_values["crop_factor"],
            '-c', command_values["coordinates"],
            input_file,
            output_file
        ]
        self.run(command)