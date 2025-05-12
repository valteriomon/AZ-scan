"""
TODO:
    - Missing images in grid on project load.
    - Pre-set map grid.
    - Join with drag and drop (web app).
    - Log errors.
"""

import os, threading, re, time
from pathlib import Path
from core.constants import APP_TITLE, MAPS_VIEW_TITLE
from core.config import Config
from core.image_viewer  import ImageViewer
from core.console import Console
from core.ui_helpers import Ui
import core.ui_styles as styles
import core.utils as utils
from core.custom_error import FileAlreadyExistsError
from enum import Enum
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

class ButtonType(Enum):
    START = "start"
    COL = "col"
    ROW = "row"

class MapView:
    def __init__(self, root, go_back_callback=None):
        self.root = root
        self.go_back_callback = go_back_callback
        self.root.title(f"{APP_TITLE} - {MAPS_VIEW_TITLE}")

        self.min_width = 600
        self.min_height = 400
        self.root.minsize(self.min_width, self.min_height)
        self.scanning = False
        self.rotation_angle = 0

        self.button_pixel_size = (120, 120)

        self._config = Config().load()
        self._filetype = self._config.get("options", {}).get("scanner", {}).get("filetype", "png") or "png"

        self._reset()

    def _bind_keys(self):
        self.root.bind("<Key-c>", self._on_key_c)
        self.root.bind("<Key-C>", self._on_key_c)
        self.root.bind("<Key-f>", self._on_key_f)
        self.root.bind("<Key-F>", self._on_key_f)

    def _on_key_c(self, event):
        if getattr(self, "col_scan_enabled", False):
            self._scan_next()

    def _on_key_f(self, event):
        if getattr(self, "row_scan_enabled", False):
            self._scan_next(new_row=True)

    def _build_ui(self, root):
        def top_frame(frame):
            frame.pack(fill="both", expand=False, padx=40, pady=(10, 0))

            frame.columnconfigure(0, weight=1)
            frame.columnconfigure(1, weight=0)
            frame.columnconfigure(2, weight=1)

            center_frame = ttk.Frame(frame)
            center_frame.grid(row=0, column=1)

            label_project_code = ttk.Label(center_frame, text="Código de proyecto:")
            label_project_code.grid(row=0, column=0, padx=5, pady=5)

            self.project_code = tk.StringVar()
            self.project_code.trace_add("write", self._update_start_button_state)
            self.project_code.trace_add("write", self._on_project_code_change)

            self.entry_project_code = ttk.Entry(center_frame, textvariable=self.project_code, width=10)
            self.entry_project_code.grid(row=0, column=1, padx=(5, 60), pady=5)

            self.base_project_folder = self._get_project_folder()
            self.project_folder = tk.StringVar(value=self.base_project_folder)
            self.label_project_folder = ttk.Label(center_frame, textvariable=self.project_folder)
            self.label_project_folder.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

            self.button_project_folder = ttk.Button(center_frame, text="Elegir carpeta", command=lambda: (self._select_project_folder(), self._reset_min_size()), width=16, padding=1)
            self.button_project_folder.grid(row=0, column=3, padx=5, pady=5)

            self.label_warning = ttk.Label(center_frame, text="Los campos no podrán modificarse una vez empezado el proyecto.\nSe creará una carpeta con el código ingresado.", font=styles.FONT_DEFAULT_ITALIC, justify="center")
            self.label_warning.grid(row=1, columnspan=4, padx=10, pady=5)

        for widget in root.winfo_children():
            widget.destroy()

        menu_options = [{
            "label": "Nuevo",
            "command": self._reset
        },
        {
            "label": "Cargar proyecto",
            "command": self._load_project
        }]
        if self.go_back_callback:
            menu_options.append({
                "label": "Menú principal",
                "command": self.go_back_callback
            })
        Ui.menu(self.root, menu_options)

        self.wrapper = ttk.Frame(root)
        self.wrapper.pack(fill="both", expand=True)
        top_frame(ttk.Frame(self.wrapper))

        self.container_frame = ttk.Frame(self.wrapper)
        self.container_frame.pack(fill="x", expand=True)
        self.container_frame.grid_rowconfigure(0, weight=1)
        self.container_frame.grid_rowconfigure(2, weight=1)
        self.container_frame.grid_columnconfigure(0, weight=1)
        self.container_frame.grid_columnconfigure(2, weight=1)

        self.bottom_frame = tk.Frame(self.wrapper, bg="#cccccc")
        self.bottom_frame.pack(side="bottom", fill="x")

        self.status_bar = tk.Label(self.bottom_frame, text="Listo para escanear.", anchor="w", bg="#cccccc", fg="#171717", padx=5, pady=4)
        self.status_bar.pack(side="left", fill="x", expand=True)

        self._init_buttons()
        self._render_buttons()

    def _reset(self):
        self.root.unbind("<Configure>")
        self.root.unbind("<Key-c>")
        self.root.unbind("<Key-C>")
        self.root.unbind("<Key-f>")
        self.root.unbind("<Key-F>")

        self.grid = []
        self.rows = 0
        self.cols = 0
        self.buttons = {}
        self.image_cache = {}
        self.image_paths = {}
        self._build_ui(self.root)
        self._reset_min_size()

    def _get_project_folder(self):
        project_folder = self._config.get("multi_scan", {}).get("folder", None)
        if project_folder and os.path.isdir(project_folder) and os.listdir(project_folder):
            return project_folder
        else:
            return os.path.expanduser("~")

    def _set_project_folder(self):
        if "multi_scan" not in self._config:
            self._config["multi_scan"] = {}
        self._config["multi_scan"]["folder"] = str(self.base_project_folder)
        Config().save(self._config)

    def _on_project_code_change(self, *args):
        self._update_start_button_state()
        self.project_folder.set(f"{self.base_project_folder}{os.path.sep}{self.project_code.get()}")

    def _select_project_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.base_project_folder = Path(folder)
            self.project_folder.set(f"{self.base_project_folder}{os.path.sep}{self.project_code.get()}")

    def _open_project_folder(self):
        Console.open_folder(self.project_folder.get())

    def _init_buttons(self):
        self.buttons = {
            ButtonType.START: {"display": True, "fn": self._render_start_button, "button": None},
            ButtonType.COL: {"display": False, "fn": self._render_next_col_button, "button": None},
            ButtonType.ROW: {"display": False, "fn": self._render_next_row_button, "button": None},
        }

    def _render_buttons(self):
        for key, value in self.buttons.items():
            display = value.get("display", False)
            if display:
                if value["button"] is None:
                    value["fn"]()
                if key is not ButtonType.START:
                    if display == "right":
                        self.buttons[key]["button"].grid(row=self.rows - 1, column=len(self.grid[-1]), padx=2, pady=2)
                    elif display == "left":
                        col = next((i for i, x in enumerate(self.grid[-1]) if x is not None), 0) - 1
                        self.buttons[key]["button"].grid(row=self.rows - 1, column=col, padx=2, pady=2)
                    else:
                        if self.rows % 2:
                            self.buttons[key]["button"].grid(row=self.rows, column=self.cols - 1, padx=2, pady=2)
                        else:
                            self.buttons[key]["button"].grid(row=self.rows, column=0, padx=2, pady=2)
            else:
                self._destroy_button(key)

    def _destroy_button(self, key):
        button = self.buttons[key].get("button")
        if button:
            button.destroy()
            self.buttons[key]["button"] = None

    def _render_start_button(self):
        button = ttk.Button(
            self.container_frame,
            text="Comenzar",
            command=self._on_start_clicked,
            style="Big.TButton",
            state="disabled"
        )
        button.grid(row=1, column=1, pady=(60,80), sticky="nsew")
        self.buttons[ButtonType.START]["button"] = button

    def _on_start_clicked(self):
        self.entry_project_code.config(state="disabled")
        self.buttons[ButtonType.START]["button"].config(state="disabled")
        project_folder = self.project_folder.get()
        os.makedirs(project_folder, exist_ok=True)
        if os.path.isdir(project_folder):
            self.button_project_folder.config(text="Abrir carpeta", command=self._open_project_folder)
            self._scan(1, 1)
        else:
            raise RuntimeError(f"No se pudo crear la carpeta del proyecto: {project_folder}")

    def _update_start_button_state(self, *args):
        if self.project_code.get().strip():
            self.buttons[ButtonType.START]["button"].config(state="normal")
        else:
            self.buttons[ButtonType.START]["button"].config(state="disabled")

    def _render_next_col_button(self):
        button = self._make_plus_button("+\ncol.", self._scan_next)
        self.buttons[ButtonType.COL]["button"] = button
        self.col_scan_enabled = True

    def _render_next_row_button(self):
        button = self._make_plus_button("+\nfila", lambda: self._scan_next(new_row=True))
        self.buttons[ButtonType.ROW]["button"] = button
        self.row_scan_enabled = True

    def _make_plus_button(self, text, command):
        plus_button_frame = tk.Frame(self.content_frame, width=self.button_pixel_size[0], height=self.button_pixel_size[1])
        plus_button_frame.pack_propagate(False)
        plus_button = tk.Button(
            plus_button_frame,
            text=text,
            command=command,
            width=self.button_pixel_size[0] // 7,
            height=self.button_pixel_size[1] // 15,
            font=styles.MAP_PLUS_BUTTON,
            borderwidth=0,
            highlightthickness=0,
            pady=0,
            padx=0,
            underline=2
        )
        plus_button.pack(fill="both", expand=True)
        return plus_button_frame

    def _make_grid_button(self, text, command):
        return tk.Button(
            self.content_frame,
            command=command,
            width=self.button_pixel_size[0],
            height=self.button_pixel_size[1],
            font=("Helvetica", 18),
            bg="#000000",
            borderwidth=0,
            highlightthickness=0,
            pady=0,
            padx=0
        )

    def _update_column_headers(self):
        # Clear old headers
        for widget in self.header_frame.winfo_children():
            widget.destroy()
        # Reset column weights to ensure proper spacing
        for col in range(self.cols):
            self.header_frame.grid_columnconfigure(col, weight=0, minsize=self.button_pixel_size[0])
        # Define bold, larger font
        header_font = tkfont.Font(weight="bold", size=12)  # Increase size as needed
        for col in range(self.cols):
            label = ttk.Label(
                self.header_frame,
                text=col + 1,
                anchor="center",
                font=header_font
            )
            label.grid(row=0, column=col, sticky="nsew", padx=2, pady=2)

    def _update_row_headers(self):
        # Clear old headers
        for widget in self.side_frame.winfo_children():
            widget.destroy()
        # Reset row weights and sizes
        for row in range(self.rows):
            self.side_frame.grid_rowconfigure(row, weight=0, minsize=self.button_pixel_size[1])
        # Define bold, larger font
        header_font = tkfont.Font(weight="bold", size=12)
        extra_row = self.buttons[ButtonType.ROW]["display"]
        for row in range(self.rows):
            label = ttk.Label(
                self.side_frame,
                text=utils.alpha_converter(row),
                anchor="center",
                font=header_font
            )
            if extra_row:
                label.grid(row=row, column=0, sticky="n", padx=6, pady=2)
            else:
                label.grid(row=row, column=0, sticky="nsew", padx=6, pady=2)
        if extra_row:
            ttk.Label(
                self.side_frame,
                anchor="center",
                font=header_font
            ).grid(row=self.rows, column=0, sticky="n", padx=6, pady=2)

    # Resize and scroll related events
    def _reset_min_size(self):
        self.root.update_idletasks()
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight() + 260
        self.root.minsize(width, height)

    def _on_mousewheel(self, event):
        if not self.scrollbar_visible:
            return
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            direction = -1 if event.delta > 0 else 1
            self.canvas.yview_scroll(direction, "units")

    def _center_content(self, event=None):
        self.canvas.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        content_width = self.main_frame.winfo_reqwidth()
        content_height = self.main_frame.winfo_reqheight()

        # Only center if content is smaller than canvas
        x = max((canvas_width - content_width) // 2, 0)
        y = max((canvas_height - content_height) // 2, 0)

        self.canvas.coords(self.content_window, x, y)

    def _bind_mouse_scroll_events(self):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)  # Windows/macOS
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)    # Linux scroll up
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)    # Linux scroll down

    def _bind_resize_events(self):
        self.root.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Configure>", self._update_scroll_region)
        self.main_frame.bind("<Configure>", self._update_scroll_region)

    def _on_resize(self, event):
        required_height = self.main_frame.winfo_reqheight()
        required_width = self.main_frame.winfo_reqwidth()
        self.canvas.config(height=required_height, width=required_width)

    def _update_scroll_region(self, event=None):
        self.canvas.update_idletasks()
        bbox = self.canvas.bbox("all")
        if bbox:
            self.canvas.config(scrollregion=bbox)

        content_height = self.main_frame.winfo_height()
        canvas_height = self.canvas.winfo_height()

        if content_height > canvas_height:
            if not self.scrollbar_visible:
                self.scrollbar.grid(row=0, column=2, sticky="nsw")
                self.scrollbar_visible = True
        else:
            if self.scrollbar_visible:
                self.scrollbar.grid_forget()
                self.scrollbar_visible = False

    def _create_grid(self):
        self.container_frame.destroy()
        if not self.grid:
            self._reset_min_size()

        self.col_scan_enabled = False
        self.row_scan_enabled = False

        self.container_frame = ttk.Frame(self.wrapper, padding=20)
        self.container_frame.pack(fill="x", expand=True)
        self.container_frame.grid_rowconfigure(0, weight=1)

        self.container_frame.grid_columnconfigure(0, weight=1)
        self.container_frame.grid_columnconfigure(1, weight=0)
        self.container_frame.grid_columnconfigure(2, weight=1)

        self.canvas = tk.Canvas(self.container_frame, bd=0, highlightthickness=0)
        self.canvas.grid(row=0, column=1, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self.container_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar_visible = False

        self.main_frame = ttk.Frame(self.canvas, padding=0)
        self.content_window = self.canvas.create_window(0, 0, window=self.main_frame, anchor="nw")

        self.header_frame = ttk.Frame(self.main_frame, padding=0)
        self.header_frame.grid(row=0, column=1, sticky="nw")
        self.side_frame = ttk.Frame(self.main_frame, padding=0)
        self.side_frame.grid(row=1, column=0, sticky="ew")
        self.content_frame = ttk.Frame(self.main_frame, padding=0)
        self.content_frame.grid(row=1, column=1, sticky="nsew")

        self._bind_resize_events()
        self._bind_mouse_scroll_events()

    def _compute_grid_buttons(self, row=False):
        button = self._make_grid_button("", None)
        if not self.grid:  # Empty grid. Create first cell: Create first row and add first col -> Next only "Add col" available
            self.buttons[ButtonType.START]["display"] = False
            self.buttons[ButtonType.COL]["display"] = "right"
            self.grid.append([button])
        elif len(self.grid) == 1: # Only one row with at least one cell -> Both "Add col" and "Add row" available
            if len(self.grid[0]) > 1 and row: # More than one cell on first row, requested new row
                self.buttons[ButtonType.ROW]["display"] = False
                self.buttons[ButtonType.COL]["display"] = "left"
                self.grid.append([None] * len(self.grid[0]))
                self.grid[-1][-1] = button
            else: # Either adding second cell (always new col) or requested new col on first row
                self.buttons[ButtonType.ROW]["display"] = True
                self.grid[0].append(button)
        elif not len(self.grid) % 2: # Starting from second row, all even rows (2, 4, 6, etc)
            for index in reversed(range(len(self.grid[-1]))): # "Add col" available on all but last col, "Add row" available on last col
                if self.grid[-1][index] is None: # Go left
                    if index == 0: # Go down
                        self.buttons[ButtonType.ROW]["display"] = True
                        self.buttons[ButtonType.COL]["display"] = False
                    self.grid[-1][index] = button
                    break
                elif index == 0: # Go right on next row
                    self.buttons[ButtonType.ROW]["display"] = False
                    self.buttons[ButtonType.COL]["display"] = "right"
                    self.grid.append([button])
        else: # All odd rows after the second one (3, 5, 7, etc)
            if len(self.grid[-1]) == len(self.grid[0]):
                self.buttons[ButtonType.ROW]["display"] = False
                self.buttons[ButtonType.COL]["display"] = "left"
                self.grid.append([None] * len(self.grid[0]))
                self.grid[-1][-1] = button
            else:
                if len(self.grid[-1]) == len(self.grid[0]) - 1:
                    self.buttons[ButtonType.ROW]["display"] = True
                    self.buttons[ButtonType.COL]["display"] = False
                self.grid[-1].append(button)

    def _add_cell(self, row=False):
        self._compute_grid_buttons(row)
        for r, row_items in enumerate(self.grid):
            for c, btn in enumerate(row_items):
                if isinstance(btn, tk.Button):
                    btn.configure(image=self.image_cache.get(f"{r+1}-{c+1}"))
                    btn.configure(text=f"{utils.alpha_converter(r)}, {c}")
                    # btn.configure(command=self._make_callback(r, c))
                    btn.bind("<Double-Button-1>", self._make_double_click_callback(r, c))
                    right_click_menu = self._make_right_click_menu(r, c)
                    btn.bind("<Button-3>", lambda e, menu=right_click_menu: menu.tk_popup(e.x_root, e.y_root))
                    btn.grid(row=r, column=c, padx=2, pady=2)

        self.rows = len(self.grid)
        self.cols = max(len(row) for row in self.grid)
        self._render_buttons()
        self._update_column_headers()
        self._update_row_headers()

    # def _make_callback(self, r, c):
    #     return lambda: print(f"Callback for {r}, {c}")

    def _make_double_click_callback(self, r, c):
        def callback(event):
            self._view_scan(self._get_file_path(r, c))
        return callback

    def _make_right_click_menu(self, r, c):
        filepath = self._get_file_path(r, c)
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Ver", command=lambda: self._view_scan(filepath))
        menu.add_command(label="Re-escanear", command=lambda: self._rescan(r+1, c+1,filepath))
        menu.add_command(label="⟳ Rotar 90°", command=lambda: self._rotate_image_clockwise(r+1, c+1))
        menu.add_command(label="⟲ Rotar -90°", command=lambda: self._rotate_image_counterclockwise(r+1, c+1))
        return menu

    def _get_file_path(self, row, col):
        alpha_row = utils.alpha_converter(row)
        return f"{self.project_folder.get()}/{self.project_code.get()}_{alpha_row}{col+1}.{self._filetype}"

    def _scan_next(self, new_row=False):
        if new_row:
            next_row = self.rows + 1
            if self.rows % 2: # Odd rows (1, 3, 5, 7...)
                next_col = self.cols
            else: # Even rows (2, 4, 6, 8...)
                next_col = 1
        else:
            next_row = self.rows
            if self.rows % 2: # Odd rows (1, 3, 5, 7...)
                next_col = len(self.grid[-1]) + 1
            else: # Even rows (2, 4, 6, 8...)
                (_, next_col) = utils.get_first_valid_element(self.grid[-1])
        self._scan(next_row, next_col, new_row=new_row)

    def _scan(self, row, col, new_row=False):
        if self.scanning:
            print("Already scanning")
            return
        project_folder = self.project_folder.get()
        project_code = self.project_code.get()
        alpha_row = utils.alpha_converter(row, zero_based=False)
        filename = f"{project_code}_{alpha_row}{col}.{self._filetype}"
        filepath = f"{project_folder}/{filename}"
        self.status_bar.config(text="Escaneando...")
        def do_scan():
            try:
                self.scanning = True
                Console().scan(filepath)
                if self.rotation_angle != 0:
                    img = Image.open(filepath)
                    rotated = img.rotate(-self.rotation_angle, expand=True)
                    rotated.save(filepath)
                self.status_bar.config(text="Escaneo finalizado. Listo para escanear.")
                if not self.grid:
                    self._create_grid()
                    self._new_grid_ui()

                self.root.after(0, lambda: (
                    self._cache_thumbnails(filepath, filename, row, col),
                    self._add_cell(new_row)
                ))
            except FileAlreadyExistsError as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"El siguiente archivo que se intenta crear ya existe:\n\n{filepath}\n\n"
                    "Eliminar el archivo o actualizar el nombre del próximo escaneo."
                ))
                self.status_bar.config(text=f"Error: {e}")
            finally:
                self.scanning = False
        threading.Thread(target=do_scan, daemon=True).start()

    def _rescan(self, row, col, filepath):
        if self.scanning:
            print("Already scanning")
            return
        self.status_bar.config(text="Escaneando...")
        def do_scan():
            try:
                self.scanning = True
                Console().scan(filepath)
                if self.rotation_angle != 0:
                    img = Image.open(filepath)
                    rotated = img.rotate(-self.rotation_angle, expand=True)
                    rotated.save(filepath)
                self._cache_thumbnails(filepath, None, row, col)
                btn = self.grid[row-1][col-1]
                if btn:
                    btn.configure(image=self.image_cache.get(f"{row}-{col}"))
                self.status_bar.config(text="Escaneo finalizado. Listo para escanear.")
            except FileAlreadyExistsError as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"El siguiente archivo que se intenta crear ya existe:\n\n{filepath}\n\n"
                    "Eliminar el archivo o actualizar el nombre del próximo escaneo."
                ))
                self.status_bar.config(text=f"Error: {e}")
            finally:
                self.scanning = False
        threading.Thread(target=do_scan, daemon=True).start()

    def _view_scan(self, filepath):
        viewer = tk.Toplevel(self.root)
        viewer.focus_force()
        image_filename = os.path.abspath(filepath)
        viewer = ImageViewer(viewer, image_filename)

    def _cache_thumbnails(self, filepath, filename, row, col):
        image_path = os.path.join(filepath)
        original = Image.open(image_path)
        # Crop to square (centered)
        width, height = original.size
        min_side = min(width, height)
        left = (width - min_side) // 2
        top = (height - min_side) // 2
        right = left + min_side
        bottom = top + min_side
        cropped = original.crop((left, top, right, bottom))
        # Resize to button pixel size with high-quality resampling
        resized = cropped.resize(self.button_pixel_size, Image.Resampling.LANCZOS)
        self.image_cache[f"{row}-{col}"] = ImageTk.PhotoImage(resized)
        self.image_paths[f"{row}-{col}"] = image_path

    def _rotate_image_clockwise(self, row, col):
        self._rotate_image(row, col, angle=-90)

    def _rotate_image_counterclockwise(self, row, col):
        self._rotate_image(row, col, angle=90)

    def _rotate_image(self, row, col, angle):
        key = f"{row}-{col}"
        filepath = self.image_paths.get(key)
        if not filepath or not os.path.exists(filepath):
            print(f"No image found at {key}")
            return
        img = Image.open(filepath)
        rotated = img.rotate(angle, expand=True)
        rotated.save(filepath)
        self._cache_thumbnails(filepath, None, row, col)
        btn = self.grid[row-1][col-1]
        if btn:
            btn.configure(image=self.image_cache.get(f"{row}-{col}"))

    def _rotate_all_images_clockwise(self):
        self.rotation_angle = (self.rotation_angle + 90) % 360
        self.rotation_label_var.set(value=f"Rotación actual: {self.rotation_angle}°")
        self._rotate_all_images(angle=-90)

    def _rotate_all_images_counterclockwise(self):
        self.rotation_angle = (self.rotation_angle - 90) % 360
        self.rotation_label_var.set(value=f"Rotación actual: {self.rotation_angle}°")
        self._rotate_all_images(angle=90)

    def _rotate_all_images(self, angle):
        self.status_bar.config(text="Rotando imágenes...")
        thread = threading.Thread(target=self._rotate_all_images_threaded, args=(angle,))
        thread.start()

    def _rotate_all_images_threaded(self, angle):
        for row in range(1, self.rows + 1):
            for col in range(1, self.cols + 1):
                key = f"{row}-{col}"
                filepath = self.image_paths.get(key)
                if not filepath or not os.path.exists(filepath):
                    continue

                try:
                    img = Image.open(filepath)
                    rotated = img.rotate(angle, expand=True)
                    rotated.save(filepath)
                    self._cache_thumbnails(filepath, None, row, col)

                    def update_ui(r=row, c=col):
                        btn = self.grid[r-1][c-1]
                        if btn:
                            btn.configure(image=self.image_cache.get(f"{r}-{c}"))

                    self.root.after(0, update_ui)

                except Exception as e:
                    print(f"Error rotating {filepath}: {e}")

        self.root.after(0, lambda: self.status_bar.config(text="Todas las imágenes han sido rotadas. Listo para escanear."))

    def _load_project(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        self._reset()
        code = os.path.basename(folder)
        self.project_code.set(code)
        self.project_folder.set(folder)
        self.buttons[ButtonType.START]["button"].config(state="disabled")
        self.entry_project_code.config(state="disabled")
        self.button_project_folder.config(text="Abrir carpeta", command=self._open_project_folder)
        self.status_bar.config(text="Cargando proyecto...")
        threading.Thread(target=self._load_project_threaded, args=(folder,), daemon=True).start()

    def _load_project_threaded(self, folder):
        all_files = os.listdir(folder)
        filetype = self._filetype
        file_pattern = re.compile(rf"^(.+)_([A-Z]+)(\d+)\.{filetype}$")
        matched_files = [f for f in all_files if file_pattern.match(f)]
        if not matched_files:
            self.after(0, lambda: messagebox.showwarning("Advertencia", "No se encontraron archivos válidos en la carpeta."))
            return

        grid_data = {}
        row_max_col = {}
        max_row = 0
        max_col = 0
        for filename in matched_files:
            match = file_pattern.match(filename)
            if not match:
                continue
            alpha_row, col = match.group(2), int(match.group(3))
            row = utils.alpha_converter(alpha_row, zero_based=False)
            grid_data[(row, col)] = filename
            max_row = max(max_row, row)
            max_col = max(max_col, col)
            row_max_col[row] = max(row_max_col.get(row, 0), col)

        grid = []
        for row in range(1, max_row + 1):
            max_col = row_max_col.get(row, 0)
            row_buttons = [None for _ in range(max_col)]
            grid.append(row_buttons)

        image_cache = {}
        image_paths = {}
        button_info = []

        for (row, col), filename in grid_data.items():
            filepath = os.path.join(folder, filename)
            self._cache_thumbnails(filepath, filename, row, col)
            image_cache[f"{row}-{col}"] = self.image_cache[f"{row}-{col}"]
            image_paths[f"{row}-{col}"] = filepath
            button_info.append((row, col))

        # Now apply UI changes in the main thread
        def update_ui():

            self._create_grid()
            self._new_grid_ui()
            self.grid = grid
            self.image_paths.update(image_paths)

            for (row, col) in button_info:
                button = self._make_grid_button("", None)
                button.configure(image=image_cache[f"{row}-{col}"])
                button.configure(text=f"{utils.alpha_converter(row-1)}, {col-1}")
                button.bind("<Double-Button-1>", self._make_double_click_callback(row-1, col-1))
                right_click_menu = self._make_right_click_menu(row-1, col-1)
                button.bind("<Button-3>", lambda e, menu=right_click_menu: menu.tk_popup(e.x_root, e.y_root))
                button.grid(row=row-1, column=col-1, padx=2, pady=2)
                self.grid[row-1][col-1] = button

            self.rows = len(self.grid)
            self.cols = max((len(r) for r in self.grid if r), default=0)

            if self.rows == 1:
                self.buttons[ButtonType.COL]["display"] = "right"
                if len(self.grid[0]) > 1:
                    self.buttons[ButtonType.ROW]["display"] = True
            elif self.rows % 2:
                if len(self.grid[-1]) == self.cols:
                    self.buttons[ButtonType.ROW]["display"] = True
                else:
                    self.buttons[ButtonType.COL]["display"] = "right"
            else:
                if self.grid[-1][0] is None:
                    self.buttons[ButtonType.COL]["display"] = "left"
                else:
                    self.buttons[ButtonType.ROW]["display"] = True

            self._render_buttons()
            self._update_column_headers()
            self._update_row_headers()
            self.status_bar.config(text="Proyecto cargado. Listo para escanear.")

        self.root.after(0, update_ui)



    def _new_grid_ui(self):
        self.label_warning.config(text="Atajos de teclado: (c) para escanear columnas, (f) para escanear filas.")
        self._bind_keys()
        self._set_project_folder()
        rotate_right_btn = tk.Button(self.bottom_frame, text="⟳ Rotar todo", command=self._rotate_all_images_clockwise, bg="#cccccc", activebackground="#bbbbbb", relief="flat")
        rotate_right_btn.pack(side="right", padx=(5, 0))
        rotate_left_btn = tk.Button(self.bottom_frame, text="⟲ Rotar todo", command=self._rotate_all_images_counterclockwise, bg="#cccccc", activebackground="#bbbbbb", relief="flat")
        rotate_left_btn.pack(side="right", padx=(5, 0))
        self.rotation_label_var = tk.StringVar(value=f"Rotación actual: {self.rotation_angle}°")
        self.rotation_label = tk.Label(
            self.bottom_frame,
            textvariable=self.rotation_label_var,
            bg="#cccccc",
            fg="#171717",
            padx=5,
            pady=4
        )
        self.rotation_label.pack(side="right")