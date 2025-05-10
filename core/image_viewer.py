import os
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
from core.constants import APP_TITLE, VIEWER_VIEW_TITLE

class ImageViewer(tk.Frame):
    def __init__(self, master, filepath, status_bar_enabled=True):
        super().__init__(master)
        self.filepath = tk.StringVar(value=filepath)
        # self.editor_enabled = editor_enabled
        self.status_bar_enabled = status_bar_enabled

        self.is_main_window = isinstance(master, (tk.Tk, tk.Toplevel))
        self.title = f"{APP_TITLE} - {VIEWER_VIEW_TITLE}"

        if self.is_main_window:
            master.geometry("900x600")
            master.geometry("-1200+200")
            master.title(self.title)
            try:
                master.iconbitmap("assets/images/logo32.ico")
            except Exception:
                pass

        self.pil_image = None
        self.hq_render_after_id = None

        self.layout_frame = tk.Frame(self)
        self.layout_frame.pack(expand=True, fill=tk.BOTH)

        self._setup_widgets()

        self._reset_transform()

        if self.status_bar_enabled:
            self._create_status_bar()

        self.after(100, self.set_image)

        if self.is_main_window:
            self.pack(expand=True, fill=tk.BOTH)
            # Bind to top-level ImageViewer.
            master.bind("<Configure>", self._on_resize)
        else:
            # Bind to self when embedded.
            self.bind("<Configure>", self._on_resize)

    def set_image(self, filepath=None):
        if not filepath:
            filepath = self.filepath.get()

        self.pil_image = Image.open(filepath)
        self.filepath.set(filepath)
        self._zoom_fit()

        if self.is_main_window:
            filename = os.path.basename(filepath)
            self.master.title(f"{self.title} - {filename}")

    def _setup_widgets(self):
        self._create_canvas()

    def _on_resize(self, event):
        if self.pil_image:
            self._zoom_fit()

    def _create_canvas(self):
        self.canvas = tk.Canvas(self.layout_frame, background="black", bd=0, highlightthickness=0)
        self.canvas.pack(expand=True, fill=tk.BOTH)

        self._visor_mode_bindings()

        # Escape key should still go to top-level window
        if self.is_main_window:
            self.master.bind("<Escape>", self._menu_quit_clicked)

    def _create_status_bar(self):
        self.frame_status_bar = tk.Frame(self.layout_frame)

        self.label_filepath = tk.Label(self.frame_status_bar, anchor=tk.W, padx=5)
        self.label_filepath.pack(side=tk.LEFT)

        self.label_image_info = tk.Label(self.frame_status_bar, anchor=tk.E, padx=5)
        self.label_image_info.pack(side=tk.RIGHT)

        self.frame_status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        def update_status_bar(name=None, index=None, mode=None):
            self.label_filepath["text"]     = os.path.abspath(self.filepath.get())
            self.label_image_info["text"]   = f"{self.pil_image.format} : {self.pil_image.width} x {self.pil_image.height} {self.pil_image.mode}"

        self.filepath.trace_add("write", update_status_bar)

    def _visor_mode_bindings(self):
        self.canvas.bind("<Button-1>", self._mouse_press_left)
        self.canvas.bind("<B1-Motion>", self._mouse_move_left)
        self.canvas.bind("<Double-Button-1>", self._mouse_double_click_left)
        self.canvas.bind("<MouseWheel>", self._mouse_wheel)

    def _menu_quit_clicked(self, event):
        self.master.destroy()
        return "break"

    def _mouse_press_left(self, event):
        self.__old_event = event

    def _mouse_move_left(self, event):
        if (self.pil_image == None):
            return
        self._translate(event.x - self.__old_event.x, event.y - self.__old_event.y)
        self._redraw_image()
        self.__old_event = event

    def _mouse_double_click_left(self, event):
        if self.pil_image == None:
            return
        if self.zoom_level or not self.centered:
            self._zoom_fit()
            # self._redraw_image()

    def _mouse_wheel(self, event):
        if self.pil_image is None:
            return

        if event.state != 9:
            if event.delta > 0:
                self.zoom_level += 1
                self._scale_at(1.25, event.x, event.y)  # Zoom in
            elif self.zoom_level > 0:
                self._scale_at(0.8, event.x, event.y)  # Zoom out
                self.zoom_level -= 1
            elif self.zoom_level == 0 and not self.centered:
                self._zoom_fit()
            else:
                return
            self._redraw_image()

    def _reset_transform(self):
        self.mat_affine = np.eye(3)

    def _translate(self, offset_x, offset_y):
        self.centered = False
        mat = np.eye(3)
        mat[0, 2] = float(offset_x)
        mat[1, 2] = float(offset_y)
        self.mat_affine = np.dot(mat, self.mat_affine)

    def _scale(self, scale:float):
        mat = np.eye(3)
        mat[0, 0] = scale
        mat[1, 1] = scale
        self.mat_affine = np.dot(mat, self.mat_affine)

    def _scale_at(self, scale:float, cx:float, cy:float):
        self._translate(-cx, -cy)
        self._scale(scale)
        self._translate(cx, cy)

    def _on_canvas_ready(self):
        if self.canvas.winfo_width() > 1 and self.canvas.winfo_height() > 1:
            self._zoom_fit()
        else:
            self.after(50, self._on_canvas_ready)

    def _zoom_fit(self):
        image_width, image_height = self.pil_image.width, self.pil_image.height
        canvas_width, canvas_height = self.canvas.winfo_width(), self.canvas.winfo_height()

        # if canvas_width <= 1 or canvas_height <= 1:
        #     self.root.after(100, self._zoom_fit)
        #     return

        if (image_width * image_height <= 0) or (canvas_width * canvas_height <= 0):
            return

        self._reset_transform()

        scale, offsetx, offsety = self._compute_scale_and_offset()

        self._scale(scale)
        self._translate(offsetx, offsety)

        self.zoom_level = 0
        self.centered = True

        self._redraw_image()

    def _compute_scale_and_offset(self):
        canvas_width, canvas_height = self.canvas.winfo_width(), self.canvas.winfo_height()
        image_width, image_height = self.pil_image.width, self.pil_image.height

        scale = 1.0
        offsetx = 0.0
        offsety = 0.0

        if (canvas_width * image_height) > (image_width * canvas_height):
            scale = canvas_height / image_height
            offsetx = (canvas_width - image_width * scale) / 2
        else:
            scale = canvas_width / image_width
            offsety = (canvas_height - image_height * scale) / 2

        return scale, offsetx, offsety

    def _draw_image(self, pil_image, resample=Image.NEAREST):
        if pil_image is None:
            return

        self.pil_image = pil_image
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        mat_inv = np.linalg.inv(self.mat_affine)
        affine_inv = (
            mat_inv[0, 0], mat_inv[0, 1], mat_inv[0, 2],
            mat_inv[1, 0], mat_inv[1, 1], mat_inv[1, 2]
        )
        dst = self.pil_image.transform(
            (canvas_width, canvas_height),
            Image.AFFINE,
            affine_inv,
            resample
        )

        im = ImageTk.PhotoImage(image=dst)
        self.canvas.delete("all")  # Clear previous image
        self.canvas.create_image(0, 0, anchor='nw', image=im)
        self.image = im

    def _redraw_image(self):
        if self.pil_image is None:
            return
        # Fast redraw with NEAREST
        self._draw_image(self.pil_image, resample=Image.NEAREST)
        # Cancel any previously scheduled high-quality redraw
        if self.hq_render_after_id:
            self.after_cancel(self.hq_render_after_id)
        # Schedule a high-quality redraw after 300 ms
        self.hq_render_after_id = self.after(300, lambda: self._draw_image(self.pil_image, resample=Image.BICUBIC))

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Simple responsive image viewer.")
    parser.add_argument("image", help="Path to the image file.")
    args = parser.parse_args()

    root = tk.Tk()
    app = ImageViewer(master=root, filepath=args.image)

    app.mainloop()