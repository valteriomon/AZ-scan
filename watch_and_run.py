import subprocess
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os

SCRIPT_TO_RUN = "main.py"

class ReloadHandler(FileSystemEventHandler):
    def __init__(self, args):
        self.args = args
        self.process = None
        self.start_process()

    def start_process(self):
        if self.process:
            self.process.kill()
        command = [sys.executable, SCRIPT_TO_RUN] + self.args
        print(f"▶️  Running: {' '.join(command)}")
        self.process = subprocess.Popen(command)

    def on_any_event(self, event):
        if event.src_path.endswith(".py"):
            print(f"🔁 Detected change in {event.src_path}, restarting...")
            self.start_process()

if __name__ == "__main__":
    script_args = sys.argv[1:]  # Get args passed to this wrapper script

    path = os.path.dirname(os.path.abspath(SCRIPT_TO_RUN))
    event_handler = ReloadHandler(script_args)
    observer = Observer()
    observer.schedule(event_handler, path=path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.kill()
    observer.join()
