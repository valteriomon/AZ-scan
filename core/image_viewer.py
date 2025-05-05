import tkinter as tk
from PIL import Image, ImageTk
import math
import numpy as np
import os

class ImageViewer(tk.Frame):
    EDITOR_ENABLED = True

    def __init__(self, master, filename):
        super().__init__(master)
        self.filename = filename
        self.is_main_window = isinstance(master, (tk.Tk, tk.Toplevel))

        if self.is_main_window:
            master.geometry("800x600")
            master.title("Python Image Viewer")
            try:
                master.iconbitmap("assets/images/logo32.ico")
            except Exception:
                pass

        self.pil_image = None
        self.my_title = "Python Image Viewer"
        self.resize_after_id = None

        self.create_widget()
        self.reset_transform()
        self.after(100, self.set_image)

        if self.is_main_window:
            self.pack(expand=True, fill=tk.BOTH)
            master.bind("<Configure>", self.on_resize)  # Bind to top-level winImageViewer.zoom_fitdow
        else:
            self.bind("<Configure>", self.on_resize)    # Bind to self when embedded

    def on_resize(self, event):
        if self.resize_after_id:
            self.after_cancel(self.resize_after_id)
        self.resize_after_id = self.after(200, lambda: (self.zoom_fit(self.pil_image.width, self.pil_image.height), self.redraw_image()))

    def create_widget(self):
        frame_statusbar = tk.Frame(self, bd=1, relief=tk.SUNKEN)
        self.label_filepath = tk.Label(frame_statusbar, text=os.path.basename(self.filename), anchor=tk.W, padx=5)
        self.label_filepath.pack(side=tk.LEFT)

        self.label_image_info = tk.Label(frame_statusbar, text="image info", anchor=tk.E, padx=5)
        self.label_image_info.pack(side=tk.RIGHT)

        frame_statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas = tk.Canvas(self, background="black")
        self.canvas.pack(expand=True, fill=tk.BOTH)

        # Bind to self.canvas for more consistent behavior across modes
        bind_target = self.canvas

        bind_target.bind("<Button-1>", self.mouse_down_left)
        bind_target.bind("<B1-Motion>", self.mouse_move_left)
        bind_target.bind("<Double-Button-1>", self.mouse_double_click_left)
        bind_target.bind("<MouseWheel>", self.mouse_wheel)

        if ImageViewer.EDITOR_ENABLED:
            # Context menu
            self.context_menu = tk.Menu(self.canvas, tearoff=0)
            self.context_menu.add_command(label="Print file path", command=self.print_filepath)
            bind_target.bind("<Button-3>", self.show_context_menu)

        # Escape key should still go to top-level window
        if self.is_main_window:
            self.master.bind("<Escape>", self.menu_quit_clicked)


    def set_image(self):
        if not self.filename:
            return
        self.pil_image = Image.open(self.filename)
        self.zoom_fit(self.pil_image.width, self.pil_image.height)
        self.zoom_level = 0
        self.draw_image(self.pil_image)
        if self.is_main_window:
            self.master.title(self.my_title + " - " + os.path.basename(self.filename))
        self.label_image_info["text"] = f"{self.pil_image.format} : {self.pil_image.width} x {self.pil_image.height} {self.pil_image.mode}"


    def menu_quit_clicked(self, event):
        self.master.destroy()
        return "break"

    def mouse_down_left(self, event):
        self.__old_event = event

    def mouse_move_left(self, event):
        if (self.pil_image == None):
            return
        self.translate(event.x - self.__old_event.x, event.y - self.__old_event.y)
        self.redraw_image()
        self.__old_event = event


    def mouse_double_click_left(self, event):
        if self.pil_image == None:
            return
        self.zoom_fit(self.pil_image.width, self.pil_image.height)
        self.redraw_image()

    def mouse_wheel(self, event):
        if self.pil_image is None:
            return

        if event.state != 9:
            if event.delta > 0:
                self.zoom_level += 1
                self.scale_at(1.25, event.x, event.y)  # Zoom in
            else:
                if self.zoom_level > 0:
                    self.scale_at(0.8, event.x, event.y)  # Zoom out
                    self.zoom_level -= 1
                else:
                    self.zoom_fit(self.pil_image.width, self.pil_image.height)
        # else:
        #     if event.delta > 0:
        #         self.rotate_at(90, event.x, event.y)  # Rotate clockwise
        #     else:
        #         self.rotate_at(-90, event.x, event.y)  # Rotate counter-clockwise

        self.redraw_image()

    def reset_transform(self):
        self.mat_affine = np.eye(3)

    def translate(self, offset_x, offset_y):
        mat = np.eye(3)
        mat[0, 2] = float(offset_x)
        mat[1, 2] = float(offset_y)
        self.mat_affine = np.dot(mat, self.mat_affine)

    def scale(self, scale:float):
        mat = np.eye(3)
        mat[0, 0] = scale
        mat[1, 1] = scale
        self.mat_affine = np.dot(mat, self.mat_affine)

    def scale_at(self, scale:float, cx:float, cy:float):
        self.translate(-cx, -cy)
        self.scale(scale)
        self.translate(cx, cy)

    def rotate(self, deg:float):
        mat = np.eye(3)
        mat[0, 0] = math.cos(math.pi * deg / 180)
        mat[1, 0] = math.sin(math.pi * deg / 180)
        mat[0, 1] = -mat[1, 0]
        mat[1, 1] = mat[0, 0]

        self.mat_affine = np.dot(mat, self.mat_affine)

    def rotate_at(self, deg:float, cx:float, cy:float):
        self.translate(-cx, -cy)
        self.rotate(deg)
        self.translate(cx, cy)

    def zoom_fit(self, image_width, image_height):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if (image_width * image_height <= 0) or (canvas_width * canvas_height <= 0):
            return
        self.reset_transform()

        scale, offsetx, offsety = self.compute_scale_and_offset(canvas_width, canvas_height, image_width, image_height)

        self.scale(scale)
        self.translate(offsetx, offsety)

    def compute_scale_and_offset(self, canvas_width, canvas_height, image_width, image_height):
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

    def to_image_point(self, x, y):
        if self.pil_image == None:
            return []

        mat_inv = np.linalg.inv(self.mat_affine)
        image_point = np.dot(mat_inv, (x, y, 1.))
        if  image_point[0] < 0 or image_point[1] < 0 or image_point[0] > self.pil_image.width or image_point[1] > self.pil_image.height:
            return []
        return image_point

    def draw_image(self, pil_image):
        if pil_image == None:
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
                    Image.NEAREST
                    )
        im = ImageTk.PhotoImage(image=dst)
        item = self.canvas.create_image(
                0, 0,
                anchor='nw',
                image=im
                )
        self.image = im

    def redraw_image(self):
        if self.pil_image == None:
            return
        self.draw_image(self.pil_image)

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def print_filepath(self):
        print(self.filename)
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = ImageViewer(master=root)
#     app.mainloop()