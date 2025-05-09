from core.constants import APP_TITLE, POSTCARD_VIEW_TITLE
from core.app_state import AppState
from core.image_viewer  import ImageViewer
from core.console import Console
from core.custom_error import FileAlreadyExistsError
from core.ui_modules import Ui
from pathlib import Path
import os
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import font
import core.ui_styles as styles

class PostcardView:
    def __init__(self, root, go_back_callback=None):
        self.root = root
        self.go_back_callback = go_back_callback

        self.root.title(f"{APP_TITLE} - {POSTCARD_VIEW_TITLE}")
        self.root.geometry("")
        self.root.resizable(True, True)

        self.state = AppState()

        self._set_vars()
        self._build_ui(root)
        self._key_bindings()

        # Lock window size to content
        self.root.update_idletasks()
        width, height = self.root.winfo_width(), self.root.winfo_height()
        self.root.minsize(width, height)

        # Let the geometry be determined by the content
        self.resize_after_id = None

        # self.viewers = []        # List of ImageViewer instances
        # self.current_index = -1  # Index of currently visible viewer

    def _key_bindings(self):
        self.root.bind("<Return>", lambda event: self.scan())
        self.root.bind("<KP_Enter>", lambda event: self.scan())

    def _set_vars(self):
        self.folder = tk.StringVar(value=self.state.folder)
        self.save_state = tk.IntVar(value=True)

        self.prefix = tk.StringVar(value=self.state.prefix)
        self.index = tk.StringVar(value=self.state.index)
        self.side = tk.StringVar(value=self.state.side)

        self.next_scan = tk.StringVar(value=self.state.next_scan)
        self.last_scan = tk.StringVar(value=self.state.last_scan)

        # self.viewer_label_var = tk.StringVar(value="Sin escaneos")

        # Triggers updates
        self._bind_var(self.folder, lambda v: setattr(self.state, "folder", v), self._update_next_scan)
        self._bind_var(self.prefix, lambda v: setattr(self.state, "prefix", v), self._update_next_scan)
        self._bind_var(self.prefix, lambda v: setattr(self.state, "prefix", v), self._update_index)
        self._bind_var(self.index, lambda v: setattr(self.state, "index", int(v)) if v.isdigit() else None, self._update_next_scan)
        self._bind_var(self.side, lambda v: setattr(self.state, "side", v), self._update_next_scan)

    def _bind_var(self, var, state_callback=None, ui_callback=None):
        def wrapped_callback(*_):
            if state_callback:
                state_callback(var.get())
            if ui_callback:
                ui_callback()
        var.trace_add("write", wrapped_callback)

    def _build_ui(self, root):
        def _ui_first_row(row):
            row.pack(fill="x", expand=True)
            row.grid(row=0, column=0, sticky="ew")

            button_change_project_folder = ttk.Button(row, text="Elegir", width=10, command=self._change_project_folder)
            button_change_project_folder.grid(row=0, column=0, padx=4, pady=4)

            button_open_project_folder = ttk.Button(row, text="Abrir", width=10, command=self._open_project_folder)
            button_open_project_folder.grid(row=0, column=1, padx=4, pady=4)

            label_project_description = ttk.Label(row, text="Carpeta de proyectos:")
            label_project_description.grid(row=0, column=2, padx=4, pady=4)

            label_project_folder = ttk.Label(row, textvariable=self.folder, font=styles.FONT_DEFAULT_BOLD)
            label_project_folder.grid(row=0, column=3, padx=4, pady=4, sticky="ew")

            # Save state
            checkbox_save_state = ttk.Checkbutton(row, text="Recordar estado", variable=self.save_state, onvalue=True, offvalue=False)
            checkbox_save_state.grid(row=0, column=4, padx=4, pady=4, sticky="e")

            row.columnconfigure(4, weight=1)

        def _ui_second_row(row):
            row.grid(row=1, column=0, sticky="ew")

            # Prefix
            label_prefix =ttk.Label(row, text="Código:")
            label_prefix.grid(row=0, column=0, padx=4, pady=4)

            self.dropdown_prefix = ttk.OptionMenu(row, self.prefix, self.prefix.get(), *self.state.prefix_list)
            self.dropdown_prefix["menu"].configure(font=styles.FONT_DEFAULT)
            self.dropdown_prefix.grid(row=0, column=1, padx=4, pady=4)
            self.dropdown_prefix.config(width=10)

            entry_prefix = ttk.Entry(row, textvariable=self.prefix, width=10)
            entry_prefix.grid(row=0, column=2, padx=4, pady=4)

            #  Index
            label_index = ttk.Label(row, text="Número:")
            label_index.grid(row=0, column=3, padx=(30,4), pady=4)

            entry_index = ttk.Entry(row, textvariable=self.index, width=5, justify="center")
            entry_index.grid(row=0, column=5, padx=4, pady=4)
            button_index_decrease = ttk.Button(row, text="-", width=3, command=self._decrease_index)
            button_index_decrease.grid(row=0, column=4, padx=0, pady=4)
            button_index_increase = ttk.Button(row, text="+", width=3, command=self._increase_index)
            button_index_increase.grid(row=0, column=6, padx=0, pady=4)

            # Side
            label_side = ttk.Label(row, text="Lado:")
            label_side.grid(row=0, column=8, padx=(30,4), pady=4)

            radio_side_a = ttk.Radiobutton(row, text="A", variable=self.side, value="A")
            radio_side_a.grid(row=0, column=9, padx=4, pady=4)
            radio_side_b = ttk.Radiobutton(row, text="B", variable=self.side, value="B")
            radio_side_b.grid(row=0, column=10, padx=4, pady=4)

            # Next scan
            label_next_scan = ttk.Label(row, textvariable=self.next_scan, font=styles.FONT_DEFAULT_BOLD)
            label_next_scan.grid(row=0, column=11, padx=(30,4), pady=4, sticky="w")

            # Actions
            button_skip = ttk.Button(row, text="Siguiente", width=10, command=self._increase_index)
            button_skip.grid(row=0, column=12, padx=(30,4), pady=4, sticky="e")

            self.scan_button = ttk.Button(row, text="ESCANEAR (↩)", width=24, command=self._scan)
            self.scan_button.grid(row=0, column=13, padx=4,  pady=4, sticky="e")

            row.columnconfigure(11, weight=1)

        def _ui_separator(row):
            row.grid(row=2, column=0, sticky="ew")
            ttk.Separator(row, orient='horizontal').pack(fill='x', padx=4, pady=(10))

        def _ui_third_row(row):
            row.grid(row=3, column=0, sticky="ew")

            # Previous filename
            label_last_scan =ttk.Label(row, text="Último escaneo:")
            label_last_scan.grid(row=0, column=0, padx=4, pady=4, sticky="w")

            entry_last_scan = tk.Entry(row, textvariable=self.last_scan, state="readonly", relief="flat", borderwidth=0, highlightthickness=0, font=styles.FONT_DEFAULT_BOLD)
            entry_last_scan.grid(row=0, column=1, padx=4, pady=4, sticky="ew")

            button_open_file_folder = ttk.Button(row, text="Abrir ubicación de archivo", width=24, command=self._open_file_folder)
            button_open_file_folder.grid(row=0, column=2, padx=4, pady=4, sticky="e")

            row.columnconfigure(1, weight=1)

        def _ui_preview(row):
            row.grid(row=4, column=0, sticky="nsew", padx=4, pady=(14,5))

        def _ui_navigation_row(row):
            row.grid(row=5, column=0, sticky="ew")

            button_redo_scan = ttk.Button(row, text="Rehacer escaneo", width=24, command=self._redo_scan, state=tk.DISABLED)
            button_redo_scan.grid(row=0, column=0, padx=4, pady=4, sticky="w")

            button_delete_scan = ttk.Button(row, text="Eliminar", width=24, command=self._delete_scan, state=tk.DISABLED)
            button_delete_scan.grid(row=0, column=1, padx=4, pady=4, sticky="w")

            # Navigation buttons frame
            self.prev_btn = ttk.Button(row, text="← Anterior", command=self._previous_viewer, state=tk.DISABLED)
            self.prev_btn.grid(row=0, column=2, padx=4, pady=4, sticky="e")
            self.next_btn = ttk.Button(row, text="Siguiente →", command=self._next_viewer, state=tk.DISABLED)
            self.next_btn.grid(row=0, column=3, padx=4, pady=4, sticky="e")

            row.columnconfigure(2, weight=1)

        def _ui_status_row(row):
            row.grid(row=1, column=0, sticky="ew")

            row.columnconfigure(0, weight=1)
            self.status_label = tk.Label(row, text="", anchor="w", bg="#cccccc", fg="#171717", padx=5, pady=2)
            self.status_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

            self.status_label.config(text="Listo para escanear.")

        # #################################################

        Ui.menu(self.root, [
            {
                "label": "Menú principal",
                "command": self.go_back_callback
            }
        ])

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = ttk.Frame(root)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 14), pady=10)
        main_frame.rowconfigure(4, weight=1)
        main_frame.columnconfigure(0, weight=1)

        _ui_first_row(ttk.Frame(main_frame))
        _ui_second_row(ttk.Frame(main_frame))
        _ui_separator(ttk.Frame(main_frame))
        _ui_third_row(ttk.Frame(main_frame))

        self.preview_frame = ttk.Frame(main_frame)
        _ui_preview(self.preview_frame)

        _ui_navigation_row(ttk.Frame(main_frame))
        _ui_status_row(tk.Frame(root, bg="#cccccc"))

    # #################################################
    # UI updates  #####################################
    # #################################################

    def _update_next_scan(self):
        self.next_scan.set(self.state.next_scan)

    def _update_index(self):
    #     self.index.set(self.prefix_dict.get(self.prefix.get(), 1))
        self.index.set(self.state.index)
        self.side.set("A")

    def update_ui(self):
        if self.side.get() == "A":
            self.side.set("B")
        else:
            self._increase_index()
            self.side.set("A")
        # self.last_scan.set(self.state.last_scan)

        # self.update_filenames()

        menu = self.dropdown_prefix["menu"]
        menu.delete(0, "end")
        for value in self.state.prefix_list:
            menu.add_command(
                label=value,
                command=tk._setit(self.prefix, value)
        )

    # #################################################
    # Button actions ##################################
    # #################################################

    def _change_project_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder.set(Path(folder))

    def _open_project_folder(self):
        Console.open_folder(self.folder.get())

    def _open_file_folder(self):
        pass

    def _decrease_index(self):
        index = self.index.get()
        if index.isdigit() and int(index) > 0:
            self.index.set(int(index) - 1)
            self.side.set("A")

    def _increase_index(self):
        index = self.index.get()
        if index.isdigit():
            self.index.set(int(index) + 1)
            self.side.set("A")

    def _redo_scan(self):
        pass

    def _delete_scan(self, file_path):
        pass
    #     if os.path.exists(file_path):
    #         os.remove(file_path)
    #         print("File removed.")
    #     else:
    #         print("File does not exist.")

    def _scan(self):

    # #     self.scan_button.config(state="disabled")
    # #     self.status_label.config(text="Escaneando...")

        def do_scan():
            index = self.index.get()
            if not index.isdigit():
                return
            else:
                self.state.index = int(index)

            try:
                Console().scan(self.state.next_scan)
            except FileAlreadyExistsError as e:
    # #             self.root.after(0, lambda: self.scan_button.config(state="normal"))
    # #             self.root.after(0, lambda: self.status_label.config(text=""))
                self.root.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"El siguiente archivo que se intenta crear ya existe:\n\n{next_file}\n\n"
                    "Eliminar el archivo o actualizar el nombre del próximo escaneo."
                ))
                print("Error:", e)
                return

            if self.save_state.get():
                self.last_scan.set(self.state.next_scan)
                self.state.save_config()
                self.update_ui()
                # self.last_scan.set(self.state.last_scan)

    #     #         # self.show_image(next_file)
    #     #         # viewer = tk.Toplevel(self.root)
    #     #         # viewer.focus_force()


                image_filename = os.path.abspath(next_file)
    #     #         viewer = ImageViewer(self.preview_frame, image_filename, status_bar_enabled=False)

    #     #         # viewer.pack(fill=tk.BOTH, expand=True)
    #     #         self.viewers.append(viewer)
    #     #         self.show_viewer(len(self.viewers) - 1)

    #     #         # ImageViewer(self.row_5, image_filename)

                # self.root.after(0, self.update_ui)
    #     #         self.root.after(0, lambda: self.scan_button.config(state="normal"))
    #     #         self.root.after(0, lambda: self.status_label.config(text="Escaneo finalizado. Listo para escanear."))

        threading.Thread(target=do_scan, daemon=True).start()



    # # def show_image(self, filepath):
    # #     pass

    # # def show_viewer(self, index):
    # #     for viewer in self.viewers:
    # #         viewer.pack_forget()

    # #     if 0 <= index < len(self.viewers):
    # #         self.viewers[index].pack(fill=tk.BOTH, expand=True)
    # #         self.current_index = index

    # #         filename = Path(self.viewers[index].filepath.get()).name
    # #         self.viewer_label_var.set(f"Escaneo {index + 1} de {len(self.viewers)} - {filename}")

    # #     self.update_nav_buttons()

    def _previous_viewer(self):
        pass
    # #     if self.current_index > 0:
    # #         self.show_viewer(self.current_index - 1)

    def _next_viewer(self):
        pass
    # #     if self.current_index < len(self.viewers) - 1:
    # #         self.show_viewer(self.current_index + 1)

    # # def update_nav_buttons(self):
    # #     self.prev_btn.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
    # #     self.next_btn.config(state=tk.NORMAL if self.current_index < len(self.viewers) - 1 else tk.DISABLED)
