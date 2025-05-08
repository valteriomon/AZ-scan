from .constants import APP_TITLE, POSTCARD_VIEW_TITLE
from .app_state import AppState
from .image_viewer  import ImageViewer, EditorImageViewer
from .console import Console
from .custom_error import FileAlreadyExistsError
from pathlib import Path
import os
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import font

class PostcardView:
    def __init__(self, root, go_back_callback=None):
        self.root = root
        self.go_back_callback = go_back_callback
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
        self.root.bind("<Control-s>", lambda event: self.scan())

        self.update_next_file()
        # # Lock window size to content
        self.root.update_idletasks()  # Let Tkinter layout all widgets
        w, h = self.root.winfo_width(), self.root.winfo_height()
        self.root.minsize(w, h)       # Prevent shrinking smaller than content
        self.root.resizable(True, True)  # Allow user to resize larger
        self.root.geometry("")  # Let the geometry be determined by the content
        self.resize_after_id = None
        self.viewers = []        # List of ImageViewer instances
        self.current_index = -1  # Index of currently visible viewer



    def build_ui(self, root):
        self.get_state()

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = ttk.Frame(root)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)  # row_5 will go here

        # Row 1
        row_1 = ttk.Frame(main_frame)
        row_1.grid(row=0, column=0, sticky="ew")
        ttk.Button(row_1, text="Elegir carpeta para los escaneos", width=30, command=self.choose_folder).grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(row_1, textvariable=self.folder, anchor="w").grid(row=0, column=1, columnspan=4, padx=5, pady=5, sticky="ew")
        row_1.columnconfigure(1, weight=1)

        # Row 2
        row_2 = ttk.Frame(main_frame)
        row_2.grid(row=1, column=0, sticky="ew")

        # Prefix dropdown + entry
        ttk.Label(row_2, text="Código:", anchor="w").grid(row=0, column=0, padx=5, pady=0)
        self.prefix_dropdown = ttk.OptionMenu(row_2, self.prefix, self.prefix.get(), *self.prefix_list)
        self.prefix_dropdown["menu"].configure(font=("Arial",16))
        self.prefix_dropdown.grid(row=0, column=1, padx=5, pady=5)
        self.prefix_dropdown.config(width=14)
        self.prefix_entry = ttk.Entry(row_2, textvariable=self.prefix, width=25)
        self.prefix_entry.grid(row=0, column=2, columnspan=2, padx=5, pady=5)

        #  Index entry with +/- buttons
        ttk.Label(row_2, text="Número:").grid(row=0, column=4, padx=5, pady=5)
        ttk.Entry(row_2, textvariable=self.index, width=5).grid(row=0, column=6, padx=5, pady=5)
        ttk.Button(row_2, text="-", width=3, command=self.decrease_index).grid(row=0, column=5, padx=0, pady=5)
        ttk.Button(row_2, text="+", width=3, command=self.increase_index).grid(row=0, column=7, padx=0, pady=5)

        # Radio Buttons
        ttk.Label(row_2, text="Lado:").grid(row=0, column=8, padx=5, pady=5)
        ttk.Radiobutton(row_2, text="A", variable=self.side, value="A").grid(row=0, column=9, padx=5, pady=5)
        ttk.Radiobutton(row_2, text="B", variable=self.side, value="B").grid(row=0, column=10, padx=5, pady=5)

        # Save state
        # self.save_state = tk.IntVar(value=True)
        # ttk.Checkbutton(row_2, text="Recordar estado", variable=self.save_state, onvalue=True, offvalue=False).grid(row=0, column=11, padx=5, pady=5)

        # Scan Button
        self.scan_button = ttk.Button(row_2, text="Escanear", command=self.scan)
        self.scan_button.grid(row=0, column=11, columnspan=2, pady=5)

        # Row 3 to 4
        row_3_to_4 = ttk.Frame(main_frame)
        row_3_to_4.grid(row=2, column=0, sticky="ew")
        row_3_to_4.columnconfigure(1, weight=1)

        # Previous filename
        ttk.Label(row_3_to_4, text="Anterior:", anchor="w").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Entry(row_3_to_4, textvariable=self.prev_file, state="readonly", relief="flat", borderwidth=0, highlightthickness=0).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Next filename
        ttk.Label(row_3_to_4, text="Próximo:", anchor="w").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(row_3_to_4, textvariable=self.next_file, anchor="w").grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Row 5 (should expand)
        self.row_5 = ttk.Frame(main_frame)
        self.row_5.grid(row=4, column=0, sticky="nsew", padx=5, pady=5)

        # Row 6: Navigation buttons and filename label
        self.row_6 = ttk.Frame(main_frame)
        self.row_6.grid(row=5, column=0, sticky="ew", padx=5, pady=(0, 5))

        # Centering container
        center_frame = ttk.Frame(self.row_6)
        center_frame.pack(expand=True)

        # Navigation buttons frame
        nav_frame = ttk.Frame(center_frame)
        nav_frame.pack(side=tk.LEFT)

        self.prev_btn = ttk.Button(nav_frame, text="← Anterior", command=self.show_previous, state=tk.DISABLED)
        self.prev_btn.pack(side=tk.LEFT, padx=5)

        self.next_btn = ttk.Button(nav_frame, text="Siguiente →", command=self.show_next, state=tk.DISABLED)
        self.next_btn.pack(side=tk.LEFT, padx=5)

        # Filename label
        self.viewer_label = ttk.Label(center_frame, textvariable=self.viewer_label_var)
        self.viewer_label.pack(side=tk.LEFT, padx=20)


        # Row 99: Status bar pinned to bottom
        row_99 = tk.Frame(root, bg="#dfe6e9")
        row_99.grid(row=1, column=0, sticky="ew")

        row_99.columnconfigure(0, weight=1)
        self.status_label = tk.Label(row_99, text="", anchor="w", bg="#dfe6e9", fg="#2d3436")
        self.status_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)

        menu_link = tk.Label(row_99, text="Menú", fg="blue", bg="#dfe6e9", cursor="hand2")
        menu_link.grid(row=0, column=1, sticky="e", padx=5, pady=2)
        menu_link.bind("<Button-1>", lambda e: self.on_back())

        self.status_label.config(text="Listo para escanear.")

    def get_state(self):
        self.viewer_label_var = tk.StringVar(value="Sin escaneos")

        self.prefix = tk.StringVar(value=self.state.prefix)
        self.index = tk.StringVar(value=self.state.index)
        self.side = tk.StringVar(value=self.state.side)

        self.prev_file = tk.StringVar(value=self.state.last_filepath)
        self.folder = tk.StringVar(value=self.state.folder)
        self.next_file = tk.StringVar()

        self.prefix_list = self.state.get_prefix_list()
        self.prefix_dict = self.state.get_prefix_dict()
        self.filetype = self.state.filetype


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
            # self.show_image(next_file)
            # viewer = tk.Toplevel(self.root)
            # viewer.focus_force()


            image_filename = os.path.abspath(next_file)
            viewer = EditorImageViewer(self.row_5, image_filename)
            # viewer.pack(fill=tk.BOTH, expand=True)
            self.viewers.append(viewer)
            self.show_viewer(len(self.viewers) - 1)
            # ImageViewer(self.row_5, image_filename)

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

    def on_back(self):
        if self.go_back_callback:
            self.go_back_callback()

    def show_image(self, filepath):
        pass

    def show_viewer(self, index):
        for viewer in self.viewers:
            viewer.pack_forget()

        if 0 <= index < len(self.viewers):
            self.viewers[index].pack(fill=tk.BOTH, expand=True)
            self.current_index = index

            filename = Path(self.viewers[index].filename).name
            self.viewer_label_var.set(f"Escaneo {index + 1} de {len(self.viewers)} - {filename}")

        self.update_nav_buttons()

    def show_previous(self):
        if self.current_index > 0:
            self.show_viewer(self.current_index - 1)

    def show_next(self):
        if self.current_index < len(self.viewers) - 1:
            self.show_viewer(self.current_index + 1)

    def update_nav_buttons(self):
        self.prev_btn.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.current_index < len(self.viewers) - 1 else tk.DISABLED)
