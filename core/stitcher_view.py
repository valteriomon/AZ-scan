from core.constants import APP_TITLE, STITCHER_VIEW_TITLE
from core.ui_helpers import Ui
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import threading
import subprocess

class StitcherView:
    def __init__(self, root, go_back_callback=None):
        self.root = root
        self.go_back_callback = go_back_callback
        self.root.title(f"{APP_TITLE} - {STITCHER_VIEW_TITLE}")
        self._build_ui()
        # Force geometry update so we can set minsize
        self.root.update_idletasks()

        # Get current requested size and make that the minimum
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()
        self.root.minsize(width, height)

    def _build_ui(self):
        # frame = ttk.Frame(self.root, padding=20)
        # frame.pack(expand=True, fill='both')
        # frame.grid(row=0, column=1, sticky="nsew")
        # frame.columnconfigure(0, weight=0)
        # frame.columnconfigure(1, weight=1)
        # frame.columnconfigure(0, weight=0)
        menu_options = []
        if self.go_back_callback:
            menu_options.append({
                "label": "Menú principal",
                "command": self.go_back_callback
            })
        Ui.menu(self.root, menu_options)

        # Configure root window with 3 columns (left, center, right)
        self.root.grid_columnconfigure(0, weight=1)  # left filler
        self.root.grid_columnconfigure(1, weight=0)  # center
        self.root.grid_columnconfigure(2, weight=1)  # right filler
        self.root.grid_rowconfigure(0, weight=1)

        # Center frame with padding and min width
        center_frame = ttk.Frame(self.root, padding=20)
        center_frame.grid(row=0, column=1, sticky="nsew")

        # Force contents to expand to fill width of center_frame
        center_frame.columnconfigure(0, weight=1)

        # Row 0
        row0 = ttk.Frame(center_frame)
        row0.grid(row=0, column=0, sticky="ew", pady=5)

        # row0.columnconfigure(0, weight=1)
        # row0.columnconfigure(1, weight=0)
        # row0.columnconfigure(2, weight=1)

        # project_load_btn = ttk.Button(row0, text="Cargar proyecto")
        # project_load_btn.grid(row=0, column=1, sticky="ew", padx=(0, 5))


        # Row 1: FOV selector
        row1 = ttk.Frame(center_frame)
        row1.grid(row=1, column=0, sticky="ew", pady=5)

        row1.columnconfigure(0, weight=1)
        row1.columnconfigure(1, weight=0)
        row1.columnconfigure(2, weight=0)
        row1.columnconfigure(3, weight=1)

        ttk.Label(row1, text="FOV", width=5).grid(row=0, column=1, sticky="w")
        self.fov_var = tk.IntVar(value="AUTO")
        fov_select = ttk.Combobox(row1, textvariable=self.fov_var, values=["AUTO"] + list(range(1, 11)), state="readonly", width=6)
        fov_select.grid(row=0, column=2, sticky="ew")

        # Row 2: Crear puntos de unión + estrategia dropdown
        row2 = ttk.Frame(center_frame)
        row2.grid(row=2, column=0, sticky="ew", pady=5)
        row2.columnconfigure((0, 1, 2), weight=1)

        btn_union = ttk.Button(row2, text="Crear puntos de unión", width=24)
        btn_union.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        ttk.Label(row2, text="Estrategia:").grid(row=0, column=1, sticky="e", padx=(5, 5))
        self.strategy_var = tk.StringVar()
        strategy_select = ttk.Combobox(row2, textvariable=self.strategy_var,
                                       values=["Prealineada", "Cuadruples", "Petroff", "Hugin"],
                                       state="readonly")
        strategy_select.grid(row=0, column=2, sticky="ew")

        # Row 3: Crear archivo de proyecto vacío
        btn_empty = ttk.Button(center_frame, text="Crear archivo de proyecto vacío",  command=self._create_empty_project)
        btn_empty.grid(row=3, column=0, sticky="ew", pady=5)
        # btn_empty.configure(style="Big.TButton")

        # Row 4: Unir imágenes con Hugin
        btn_stitch = ttk.Button(center_frame, text="Unir imágenes con Hugin", command=self._stitch_using_hugin)
        btn_stitch.grid(row=4, column=0, sticky="ew", pady=5)
        # btn_stitch.configure(style="Big.TButton")

        # Row 5: Abrir proyecto en Hugin
        btn_open = ttk.Button(center_frame, text="Abrir proyecto en Hugin", command=self._open_hugin)
        btn_open.grid(row=5, column=0, sticky="ew", pady=5)
        # btn_open.configure(style="Big.TButton")

        self.text = ScrolledText(center_frame, height=20, width=80)
        self.text.grid(row=6, column=0, sticky="nsew", pady=10)

        self.run_button = ttk.Button(center_frame, text="Run Command", command=self._run_command)
        self.run_button.grid(row=7, column=0, sticky="ew", pady=5)


    def _open_hugin(self):
        pass

    def _stitch_using_hugin(self):
        pass

    def _create_empty_project(self):
        pass

    def _run_command(self):
        # Disable the button to prevent multiple runs
        self.run_button.config(state=tk.DISABLED)
        threading.Thread(target=self._execute_subprocess, daemon=True).start()

    def _execute_subprocess(self):
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
    app = StitcherView(root)
    root.mainloop()