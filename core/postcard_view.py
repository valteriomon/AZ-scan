from .app_state import AppState
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import font

class PostcardView:
    def __init__(self, root):
        state = AppState()

        self.root = root
        root.title("AZ-scan - Escáner de Archivos - Postales")
        root.configure(padx=15, pady=15)

        self.prefix_list = state.get_prefix_list()
        self.prefix = tk.StringVar(value=state.get_last_prefix())
        self.index = tk.StringVar(value=state.get_last_index())
        self.side = tk.StringVar(value="A")
        self.prev_file = tk.StringVar(value=state.get_last_scan())
        self.next_file = tk.StringVar()
        self.scan_folder = tk.StringVar(value=state.get_last_folder())

        # #################
        # UI
        # #################

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
        ttk.Radiobutton(row_2, text="A", variable=self.side, value="A", command=self.update_state).grid(row=0, column=9, padx=5, pady=5)
        ttk.Radiobutton(row_2, text="B", variable=self.side, value="B", command=self.update_state).grid(row=0, column=10, padx=5, pady=5)

        # Scan Button
        self.scan_button = ttk.Button(row_2, text="Escanear", command=self.scan_action)
        self.scan_button.grid(row=0, column=11, columnspan=2, pady=5)

        # Row 3 to 4
        row_3_to_4 = ttk.Frame(root)
        row_3_to_4.pack(fill="x")

        # Previous filename
        ttk.Label(row_3_to_4, text="Último escaneo:", anchor="w").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(row_3_to_4, textvariable=self.prev_file, anchor="w").grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Next filename
        ttk.Label(row_3_to_4, text="Próximo escaneo:", anchor="w").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(row_3_to_4, textvariable=self.next_file, anchor="w").grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Triggers updates
        self.prefix.trace_add("write", lambda *_: self.update_state())
        self.index.trace_add("write", lambda *_: self.update_state())
        self.side.trace_add("write", lambda *_: self.update_state())

        # #################

        # Shortcuts
        root.bind("<Control-s>", lambda event: self.scan())

        self.update_state()

        # Lock window size to content
        root.update_idletasks()
        w, h = root.winfo_width(), root.winfo_height()
        root.minsize(w, h)

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

    def update_state(self):
        text = rf"{self.scan_folder.get()}\{self.prefix.get()}_{self.index.get()}_{self.side.get()}.png"
        self.next_file.set(text)

    def scan_action(self):
        pass

    def scan(self):
        pass