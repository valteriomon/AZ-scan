from .constants import APP_TITLE, POSTCARD_VIEW_TITLE
from .app_state import AppState
from core.console import Console
from core.custom_error import FileAlreadyExistsError
from pathlib import Path
import os
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import font

class PostcardView:
    def __init__(self, root):
        self.root = root
        root.title(f"{APP_TITLE} - {POSTCARD_VIEW_TITLE}")
        root.configure(padx=15, pady=15)
        self.state = AppState()

        # Setup initial UI components
        self.build_ui(root)

        # Triggers updates
        self.bind_var(self.prefix, lambda v: setattr(self.state, "prefix", v), self.update_next_file)
        self.bind_var(self.index, lambda v: setattr(self.state, "index", v), self.update_next_file)
        self.bind_var(self.side, lambda v: setattr(self.state, "side", v), self.update_next_file)
        self.bind_var(self.folder, lambda v: setattr(self.state, "folder", v), self.update_next_file)

        # Get last index if prefix changes
        self.prefix.trace_add("write", lambda *_: self.index.set(self.prefix_dict.get(self.prefix.get(), 1)))

        # Shortcuts
        root.bind("<Control-s>", lambda event: self.scan())

        self.update_next_file()

        # Lock window size to content
        root.update_idletasks()
        w, h = root.winfo_width(), root.winfo_height()
        root.minsize(w, h)

    def get_state(self):
        self.prefix = tk.StringVar(value=self.state.prefix)
        self.index = tk.StringVar(value=self.state.index)
        self.side = tk.StringVar(value=self.state.side)

        self.prev_file = tk.StringVar(value=self.state.last_filepath)
        self.folder = tk.StringVar(value=self.state.folder)
        self.next_file = tk.StringVar()

        self.prefix_list = self.state.get_prefix_list()
        self.prefix_dict = self.state.get_prefix_dict()
        self.filetype = self.state.filetype

    def build_ui(self, root):
        self.get_state()

        main_frame = ttk.Frame(root)
        main_frame.pack(fill="both", expand=True)

        # Row 1
        row_1 = ttk.Frame(main_frame)
        row_1.pack(fill="x")
        # Choose folder
        ttk.Button(row_1, text="Elegir carpeta para los escaneos", width=30, command=self.choose_folder).grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(row_1, textvariable=self.folder, anchor="w").grid(row=0, column=1, columnspan=5, padx=5, pady=5, sticky="ew")

        # Row 2
        row_2 = ttk.Frame(main_frame)
        row_2.pack(fill="x")

        # Prefix dropdown + entry
        ttk.Label(row_2, text="Código:", anchor="w").grid(row=0, column=0, padx=5, pady=0)
        self.prefix_dropdown = ttk.OptionMenu(row_2, self.prefix, self.prefix.get(), *self.prefix_list)
        self.prefix_dropdown.grid(row=0, column=1, padx=5, pady=5)
        self.prefix_dropdown.config(width=14)
        self.prefix_entry = ttk.Entry(row_2, textvariable=self.prefix, width=25)
        self.prefix_entry.grid(row=0, column=2, columnspan=2, padx=5, pady=5)

        #  Index entry with +/- buttons
        ttk.Label(row_2, text="Número:").grid(row=0, column=4, padx=5, pady=5)
        ttk.Entry(row_2, textvariable=self.index, width=10).grid(row=0, column=6, padx=5, pady=5)
        ttk.Button(row_2, text="-", width=3, command=self.decrease_index).grid(row=0, column=5, padx=0, pady=5)
        ttk.Button(row_2, text="+", width=3, command=self.increase_index).grid(row=0, column=7, padx=0, pady=5)

        # Radio Buttons
        ttk.Label(row_2, text="Lado:").grid(row=0, column=8, padx=5, pady=5)
        ttk.Radiobutton(row_2, text="A", variable=self.side, value="A").grid(row=0, column=9, padx=5, pady=5)
        ttk.Radiobutton(row_2, text="B", variable=self.side, value="B").grid(row=0, column=10, padx=5, pady=5)

        # Scan Button
        self.scan_button = ttk.Button(row_2, text="Escanear", command=self.scan)
        self.scan_button.grid(row=0, column=11, columnspan=2, pady=5)

        # Row 3 to 4
        row_3_to_4 = ttk.Frame(main_frame)
        row_3_to_4.pack(fill="x")
        row_3_to_4.columnconfigure(1, weight=1)

        # Previous filename
        ttk.Label(row_3_to_4, text="Último escaneo:", anchor="w").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Entry(row_3_to_4, textvariable=self.prev_file, state="readonly", relief="flat", borderwidth=0, highlightthickness=0).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Next filename
        ttk.Label(row_3_to_4, text="Próximo escaneo:", anchor="w").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(row_3_to_4, textvariable=self.next_file, anchor="w").grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Row 99: Status bar pinned to bottom
        row_99 = tk.Frame(root, bg="#dfe6e9")  # regular tk.Frame with background
        row_99.pack(side="bottom", fill="x")

        self.status_label = tk.Label(row_99, text="", anchor="w", bg="#dfe6e9", fg="#2d3436")
        self.status_label.pack(fill="x", padx=5, pady=2)
        self.status_label.config(text="Listo para escanear.")

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder.set(Path(folder))

    def decrease_index(self):
        index = self.index.get()
        if index.isdigit() and int(index) > 0:
            self.index.set(int(index) - 1)

    def increase_index(self):
        index = self.index.get()
        if index.isdigit():
            self.index.set(int(index) + 1)
            self.side.set("A")

    def update_state(self):
        pass

    def update_next_file(self):
        self.next_file.set(self.state.next_filepath)

    def scan(self):
        self.scan_button.config(state="disabled")
        self.status_label.config(text="Escaneando...")

        def do_scan():
            next_file = self.next_file.get()
            try:
                Console().scan(next_file)
            except FileAlreadyExistsError as e:
                self.root.after(0, lambda: self.scan_button.config(state="normal"))
                self.root.after(0, lambda: self.status_label.config(text=""))
                self.root.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"El siguiente archivo que se intenta crear ya existe:\n\n{next_file}\n\n"
                    "Eliminar el archivo o actualizar el nombre del próximo escaneo."
                ))
                print("Error:", e)
                return

            self.state.prefix = self.prefix.get()
            self.state.folder = self.folder.get()
            self.state.save_config()

            self.root.after(0, self.update_ui)
            self.root.after(0, lambda: self.scan_button.config(state="normal"))
            self.root.after(0, lambda: self.status_label.config(text="Escaneo finalizado. Listo para escanear."))

        threading.Thread(target=do_scan, daemon=True).start()

    def update_ui(self):
        self.update_prefix_dropdown()
        self.update_filenames()

    def update_prefix_dropdown(self):
        menu = self.prefix_dropdown["menu"]
        menu.delete(0, "end")  # Clear all existing entries

        for value in self.state.get_prefix_list():
            menu.add_command(
                label=value,
                command=tk._setit(self.prefix, value)
        )

    def update_filenames(self):
        self.prev_file.set(self.next_file.get())
        if self.side.get() == "A":
            self.side.set("B")
        else:
            self.increase_index()
            self.side.set("A")

    def bind_var(self, var, state_callback=None, ui_callback=None):
        def wrapped_callback(*_):
            if state_callback:
                state_callback(var.get())
            if ui_callback:
                ui_callback()
        var.trace_add("write", wrapped_callback)
