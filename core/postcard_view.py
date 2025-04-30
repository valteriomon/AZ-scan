from .constants import APP_TITLE, POSTCARD_VIEW_TITLE
from .app_state import AppState
from core.console import Console
from core.custom_error import FileAlreadyExistsError
from pathlib import Path
import os
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
        self.bind_var(self.prefix, lambda v: self.state.set_last_prefix(v, int(self.index.get())), self.update_next_file)
        self.bind_var(self.index, lambda v: self.state.set_last_index(self.prefix.get(), int(v)), self.update_next_file)
        self.bind_var(self.side, None, self.update_next_file)
        self.bind_var(self.scan_folder, lambda v: self.state.set_last_folder(Path(v)), self.update_next_file)

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
        self.prefix = tk.StringVar(value=self.state.get_last_prefix())
        self.index = tk.StringVar(value=self.state.get_last_index())
        self.side = tk.StringVar(value="A")

        self.prev_file = tk.StringVar(value=self.state.get_last_filepath())
        self.scan_folder = tk.StringVar(value=self.state.get_last_folder())
        self.next_file = tk.StringVar()

        self.prefix_list = self.state.get_prefix_list()
        self.prefix_dict = self.state.get_prefix_dict()
        self.filetype = self.state.get_scanner().get('filetype')

    def build_ui(self, root):
        self.get_state()

        # Row 1
        row_1 = ttk.Frame(root)
        row_1.pack(fill="x")
        # Choose folder
        ttk.Button(row_1, text="Elegir carpeta para los escaneos", width=30, command=self.choose_folder).grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(row_1, textvariable=self.scan_folder, anchor="w").grid(row=0, column=1, columnspan=5, padx=5, pady=5, sticky="ew")

        # Row 2
        row_2 = ttk.Frame(root)
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
        row_3_to_4 = ttk.Frame(root)
        row_3_to_4.pack(fill="x")

        # Previous filename
        ttk.Label(row_3_to_4, text="Último escaneo:", anchor="w").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Entry(row_3_to_4, textvariable=self.prev_file, state="readonly", relief="flat", borderwidth=0, highlightthickness=0).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Next filename
        ttk.Label(row_3_to_4, text="Próximo escaneo:", anchor="w").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(row_3_to_4, textvariable=self.next_file, anchor="w").grid(row=1, column=1, padx=5, pady=5, sticky="w")

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.scan_folder.set(folder)

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
        self.next_filename = f"{self.prefix.get()}_{self.index.get()}_{self.side.get()}"
        self.next_file.set(os.path.join(rf"{self.scan_folder.get()}", f"{self.next_filename}.{self.filetype}"))

    def scan(self):
        next_file = self.next_file.get()
        # try:
        #     Console().scan(next_file)
        # except FileAlreadyExistsError as e:
        #     messagebox.showerror(
        #         "Error",
        #         f"El siguiente archivo que se intenta crear ya existe:\n\n{next_file}\n\n"
        #         "Eliminar el archivo o actualizar el nombre del próximo escaneo."
        #     )
        #     print("Error:", e)
        #     return False
        self.state.set_last_prefix(self.prefix.get(), int(self.index.get()))
        self.state.save_config()
        self.update_ui()

        return True

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
