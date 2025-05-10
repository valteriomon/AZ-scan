# TODO:

import os, threading
from pathlib import Path
from core.constants import APP_TITLE, MAPS_VIEW_TITLE
from core.config import Config
from core.image_viewer  import ImageViewer
from core.console import Console
from core.ui_modules import Ui
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

        self.button_pixel_size = (200, 200)
        self.grid = []
        self.rows = 0
        self.cols = 0
        self.buttons = {}
        self.image_cache = {}

        self._config = Config().load()
        self._build_ui(root)

    def _build_ui(self, root):
        def top_frame(frame):
            frame.pack(fill="both", expand=False)

            frame.columnconfigure(0, weight=1)
            frame.columnconfigure(1, weight=0)
            frame.columnconfigure(2, weight=1)

            center_frame = ttk.Frame(frame)
            center_frame.grid(row=0, column=1)

            label_project_code = ttk.Label(center_frame, text="Código de proyecto:")
            label_project_code.grid(row=0, column=0, padx=10, pady=5)

            self.project_code = tk.StringVar()
            self.project_code.trace_add("write", self._update_start_button_state)

            self.entry_project_code = ttk.Entry(center_frame, textvariable=self.project_code)
            self.entry_project_code.grid(row=0, column=1, padx=10, pady=5)

            self.project_folder = tk.StringVar(value=self._get_project_folder())
            self.label_project_folder = ttk.Label(center_frame, textvariable=self.project_folder)
            self.label_project_folder.grid(row=0, column=2, padx=10, pady=5, sticky="ew")

            self.button_project_folder = ttk.Button(center_frame, text="Elegir carpeta", command=lambda: (self._select_project_folder(), self._reset_min_size()))
            self.button_project_folder.grid(row=0, column=3, padx=10, pady=5)

            self.label_warning = ttk.Label(center_frame, text="Los campos no podrán modificarse una vez empezado el proyecto.", font=styles.FONT_DEFAULT_ITALIC)
            self.label_warning.grid(row=1, columnspan=4, padx=10, pady=5)

        for widget in root.winfo_children():
            widget.destroy()

        Ui.menu(self.root, [
            {
                "label": "Nuevo",
                "command": self._reset
            },
            {
                "label": "Cargar proyecto",
                "command": lambda: print("Cargar proyecto")
            },
            {
                "label": "Menú principal",
                "command": self.go_back_callback
            }
        ])

        self.wrapper = ttk.Frame(root)
        self.wrapper.pack(fill="both", expand=True)
        top_frame(ttk.Frame(self.wrapper))

        self.container_frame = ttk.Frame(self.wrapper, padding=20)
        self.container_frame.pack(fill="x", expand=True)
        self.container_frame.grid_rowconfigure(0, weight=1)
        self.container_frame.grid_rowconfigure(2, weight=1)
        self.container_frame.grid_columnconfigure(0, weight=1)
        self.container_frame.grid_columnconfigure(2, weight=1)

        self._init_buttons()
        self._render_buttons()
        self._reset_min_size()

    def _reset(self):
        self._build_ui(self.root)

    def _get_project_folder(self):
        return self._config.get("multi_scan", {}).get("folder", None)

    def _select_project_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.project_folder.set(Path(folder))

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
        button.grid(row=1, column=1, pady=80, sticky="nsew")
        self.buttons[ButtonType.START]["button"] = button

    def _on_start_clicked(self):
        self.entry_project_code.config(state="disabled")
        self._scan(0, 0)

    def _update_start_button_state(self, *args):
        if self.project_code.get().strip():
            self.buttons[ButtonType.START]["button"].config(state="normal")
        else:
            self.buttons[ButtonType.START]["button"].config(state="disabled")

    def _render_next_col_button(self):
        button = self._make_plus_button("+\n(c)ol.", self.add_cell)
        self.buttons[ButtonType.COL]["button"] = button

    def _render_next_row_button(self):
        button = self._make_plus_button("+\n(f)ila", lambda: self.add_cell(row=True))
        self.buttons[ButtonType.ROW]["button"] = button

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
        )
        plus_button.pack(fill="both", expand=True)
        return plus_button_frame

    def _make_grid_button(self, text, command):
        return tk.Button(
            self.content_frame,
            image=self.image_cache.get("test"),
            command=command,
            width=self.button_pixel_size[0],
            height=self.button_pixel_size[1],
            font=("Helvetica", 18),
            bg="#000000",
            borderwidth=0,
            highlightthickness=0
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
        height = self.root.winfo_reqheight()
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
        x = max((canvas_width - content_width) // 2, 0)
        y = max((canvas_height - content_height) // 2, 0)
        self.canvas.coords(self.content_window, x, y)

    def _bind_mouse_scroll_events(self):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)  # Windows/macOS
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)    # Linux scroll up
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)    # Linux scroll down
        # self.canvas.bind("<Configure>", self._center_content)

    def _bind_resize_events(self):
        self.root.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        if self.main_frame:
            required_height = self.main_frame.winfo_reqheight()
            required_width = self.main_frame.winfo_reqwidth()
            self.canvas.config(height=required_height, width=required_width)
        self._update_scroll_region(event)
            # self._reset_min_size()
        self._center_content()

    def _update_scroll_region(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        content_height = self.canvas.bbox("all")[3]
        canvas_height = self.canvas.winfo_height()

        if content_height > canvas_height:
            if not self.scrollbar_visible:
                self.scrollbar.pack(side="right", fill="y")
                self.scrollbar_visible = True
        else:
            if self.scrollbar_visible:
                self.scrollbar.pack_forget()
                self.scrollbar_visible = False

        # self._center_content()









    def _create_grid(self):
        for widget in self.container_frame.winfo_children():
            widget.destroy()

        self.canvas = tk.Canvas(self.container_frame, bd=0, highlightthickness=2, highlightbackground="black")
        self.canvas.pack(in_=self.container_frame, fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.container_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self._bind_mouse_scroll_events()
        self._bind_resize_events()

        self.scrollbar_visible = False

        self.main_frame = ttk.Frame(self.canvas, padding=0)
        self.content_window = self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")

        self.header_frame = ttk.Frame(self.main_frame, padding=0)
        self.header_frame.grid(row=0, column=1, sticky="nw")
        self.side_frame = ttk.Frame(self.main_frame, padding=0)
        self.side_frame.grid(row=1, column=0, sticky="ew")
        self.content_frame = ttk.Frame(self.main_frame, padding=0)
        self.content_frame.grid(row=1, column=1, sticky="nsew")

        # self._center_content()
        # self.canvas.update_idletasks()

        # self.main_frame.bind("<Configure>", self._update_scroll_region)
        # self._last_geometry = ""
        # self._poll_for_resize()

    def _scan(self, row, col):
        filename = f"./{row}-{col}.png"
        # self.scan_button.config(state="disabled")
        # self.status_label.config(text="Escaneando...")

        def do_scan():

            try:
                # Console().scan(filename)
                pass
            except FileAlreadyExistsError as e:
                # self.root.after(0, lambda: self.scan_button.config(state="normal"))
                # self.root.after(0, lambda: self.status_label.config(text=""))
                self.root.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"El siguiente archivo que se intenta crear ya existe:\n\n{filename}\n\n"
                    "Eliminar el archivo o actualizar el nombre del próximo escaneo."
                ))
                print("Error:", e)
                return

            # self.state.prefix = self.prefix.get()
            # self.state.folder = self.folder.get()
            # self.state.save_config()
            self._create_grid()
            return

            self.root.after(0, lambda: (
                self._load_images(filename),
                self.add_cell()
            ))

            # self.root.after(0, lambda: self.scan_button.config(state="normal"))
            # self.root.after(0, lambda: self.status_label.config(text="Escaneo finalizado. Listo para escanear."))

        threading.Thread(target=do_scan, daemon=True).start()

    def add_cell(self, row=False):
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

        for r, row_items in enumerate(self.grid):
            for c, btn in enumerate(row_items):
                if isinstance(btn, tk.Button):
                    btn.configure(text=f"{utils.alpha_converter(r)}, {c}")
                    btn.configure(command=self._make_callback(r, c))

                    # double-click
                                        # Right-click menu
                    menu = self._make_right_click_menu(r, c)
                    btn.bind("<Button-3>", lambda e: menu.tk_popup(e.x_root, e.y_root))
                    btn.grid(row=r, column=c, padx=2, pady=2)

        self.rows = len(self.grid)
        self.cols = max(len(row) for row in self.grid)
        self._render_buttons()
        self._update_column_headers()
        self._update_row_headers()
        # self._update_window_size()





    def _make_callback(self, r, c):
        return self._show_full_image
        # return lambda: self.scan(r, c)

    def _make_double_click_callback(self, r, c):
        def callback(event):
            print(f"Double-clicked on button at {r}, {c}")
            # your logic here
        return callback

    def _make_right_click_menu(self, r, c):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Option A", command=lambda: print(f"Option A at {r}, {c}"))
        menu.add_command(label="Option B", command=lambda: print(f"Option B at {r}, {c}"))
        return menu

    def _show_full_image(self):
        viewer = tk.Toplevel(self.root)
        viewer.focus_force()
        image_filename = os.path.abspath("test/test.png")

        viewer = ImageViewer(viewer, image_filename)

        # viewer_window = tk.Toplevel(self.root)  # Use Toplevel instead of creating a new root
        # viewer = ImageViewer(master=viewer_window)

        # top.geometry("600x400")
        # viewer = ImageViewer(master=top)
        # viewer.pack(fill=tk.BOTH, expand=True)

    def _load_images(self, filename):
        image_path = os.path.join(filename)
        original = Image.open(image_path)

        # Cache the full-size original image for popup
        self.image_cache["test_original"] = original.copy()

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
        self.image_cache["test"] = ImageTk.PhotoImage(resized)

    # # def set_scan_folder(self, folder):
    # #     Config().set_scan_folder(folder)
    #     # self._load_images()




















    # def _poll_for_resize(self):
    #     current_geometry = self.root.geometry()
    #     if current_geometry != self._last_geometry:
    #         self._last_geometry = current_geometry
    #         self._center_content()
    #         self._update_scroll_region(None)
    #     self.root.after(200, self._poll_for_resize)

    # def _update_window_size(self):
        # self.root.update_idletasks()
        # width = self.main_frame.winfo_reqwidth()
        # height = self.main_frame.winfo_reqheight()
        # current_width = self.root.winfo_width()
        # current_height = self.root.winfo_height()

        # if width > current_width:
        #     self.root.geometry(f"{width}x{current_height}")
        # if height > current_height:
        #     self.root.geometry(f"{current_width}x{height}")
        # self.root.minsize(width, self.min_height)


