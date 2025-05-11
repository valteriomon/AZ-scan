import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import subprocess

class SubprocessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Subprocess Output Viewer")

        self.text = ScrolledText(root, height=20, width=80)
        self.text.pack(padx=10, pady=10)

        self.run_button = tk.Button(root, text="Run Command", command=self.run_command)
        self.run_button.pack(pady=5)

    def run_command(self):
        # Disable the button to prevent multiple runs
        self.run_button.config(state=tk.DISABLED)
        threading.Thread(target=self.execute_subprocess, daemon=True).start()

    def execute_subprocess(self):
        # Replace with your desired command
        process = subprocess.Popen(
            ["ping", "localhost"],  # Change to ["ping", "localhost"] on Windows
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        for line in process.stdout:
            self.text.insert(tk.END, line)
            self.text.see(tk.END)

        process.stdout.close()
        process.wait()

        self.text.insert(tk.END, "\n[Finished]\n")
        self.text.see(tk.END)

        self.run_button.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    app = SubprocessApp(root)
    root.mainloop()
