import subprocess
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os
import argparse

class ReloadHandler(FileSystemEventHandler):
    def __init__(self, script, args):
        self.script = script
        self.args = args
        self.process = None
        self.start_process()

    def start_process(self):
        if self.process:
            self.process.kill()
        if self.script.endswith(".py"):
            module = []
        else:
            module = ["-m"]

        command = [sys.executable] +  module + [self.script] + self.args
        print(f"▶️  Running: {' '.join(command)}")
        self.process = subprocess.Popen(command)

    def on_any_event(self, event):
        if event.src_path.endswith(".py"):
            print(f"🔁 Detected change in {event.src_path}, restarting...")
            self.start_process()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple responsive image viewer.")
    parser.add_argument("script", help="Path to the script file.")
    parser.add_argument("additional_args", nargs=argparse.REMAINDER, help="Additional arguments for the script.")
    args = parser.parse_args()

    path = os.path.dirname(os.path.abspath(args.script))

    event_handler = ReloadHandler(args.script, args.additional_args)
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
