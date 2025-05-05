import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np

class ImageCropperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Cropper and Guide Drawer")

        self.canvas = tk.Canvas(root, cursor="cross", bg="black")
        self.canvas.pack(fill="both", expand=True)

        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack(fill="x")
        tk.Button(self.btn_frame, text="Open", command=self.open_image).pack(side="left")
        tk.Button(self.btn_frame, text="Undo", command=self.undo_crop).pack(side="left")
        tk.Button(self.btn_frame, text="Save", command=self.save_image).pack(side="left")

        self.image = None
        self.display_image = None
        self.tk_image = None
        self.original_image = None
        self.image_stack = []

        self.rect = None
        self.start_x = self.start_y = None

        self.temp_guides = []  # Two guide line IDs during Alt-drag
        self.guide_stack = []  # Stores both lines per guide crosshair

        # Events
        self.canvas.bind("<ButtonPress-1>", self.on_left_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_release)
        self.canvas.bind("<ButtonPress-3>", self.on_right_press)

        self.root.bind("<Configure>", lambda e: self.update_display_image())

    def open_image(self):
        path = filedialog.askopenfilename()
        if path:
            self.image = Image.open(path).convert("RGB")
            self.original_image = self.image.copy()
            self.update_display_image()

    def update_display_image(self):
        if not self.image:
            return

        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        img_w, img_h = self.image.size
        ratio = min(w / img_w, h / img_h)
        new_w, new_h = int(img_w * ratio), int(img_h * ratio)

        img_cv = cv2.resize(np.array(self.image), (new_w, new_h))
        self.display_image = Image.fromarray(img_cv)
        self.tk_image = ImageTk.PhotoImage(self.display_image)

        self.canvas.delete("all")
        self.canvas.create_image(w // 2, h // 2, image=self.tk_image, anchor="center")

        for guide in self.guide_stack:
            for gid in guide["ids"]:
                self.canvas.create_line(*guide["coords"][gid], fill="green", width=1)

    def undo_crop(self):
        if self.image_stack:
            self.image = self.image_stack.pop()
            self.update_display_image()

    def save_image(self):
        if self.image:
            path = filedialog.asksaveasfilename(defaultextension=".png")
            if path:
                self.image.save(path)

    def crop_image(self, x0, y0, x1, y1):
        if self.image and x0 != x1 and y0 != y1:
            img_x0 = int((x0 - self.img_offset_x) * self.img_scale_x)
            img_y0 = int((y0 - self.img_offset_y) * self.img_scale_y)
            img_x1 = int((x1 - self.img_offset_x) * self.img_scale_x)
            img_y1 = int((y1 - self.img_offset_y) * self.img_scale_y)

            img_x0, img_x1 = sorted((img_x0, img_x1))
            img_y0, img_y1 = sorted((img_y0, img_y1))

            self.image_stack.append(self.image.copy())
            self.image = self.image.crop((img_x0, img_y0, img_x1, img_y1))

            # Remove all guides
            for guide in self.guide_stack:
                for gid in guide["ids"]:
                    self.canvas.delete(gid)
            self.guide_stack.clear()

            self.update_display_image()


    def on_left_press(self, event):
        modifiers = event.state
        self.start_x, self.start_y = event.x, event.y

        if modifiers & 0x0004:  # Control key → Crop
            self.rect = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="red")

        elif modifiers & 0x0008:  # Alt key → Guide crosshair
            self.temp_guides = [None, None]  # [vertical_id, horizontal_id]

    def on_mouse_drag(self, event):
        if self.rect:
            self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

        elif self.temp_guides:
            if self.temp_guides[0]:
                self.canvas.delete(self.temp_guides[0])
            if self.temp_guides[1]:
                self.canvas.delete(self.temp_guides[1])

            self.temp_guides[0] = self.canvas.create_line(event.x, 0, event.x, self.canvas.winfo_height(), fill="green")
            self.temp_guides[1] = self.canvas.create_line(0, event.y, self.canvas.winfo_width(), event.y, fill="green")

    def on_left_release(self, event):
        if self.rect:
            x0, y0, x1, y1 = self.canvas.coords(self.rect)
            self.canvas.delete(self.rect)
            self.rect = None
            self.crop_image(x0, y0, x1, y1)

        elif self.temp_guides and all(self.temp_guides):
            x, y = event.x, event.y
            ids = self.temp_guides
            coords = {
                ids[0]: (x, 0, x, self.canvas.winfo_height()),
                ids[1]: (0, y, self.canvas.winfo_width(), y)
            }
            self.guide_stack.append({"ids": ids, "coords": coords})
            self.temp_guides = []

    def on_right_press(self, event):
        if event.state & 0x0008:  # Alt+Right Click
            if self.guide_stack:
                last = self.guide_stack.pop()
                for gid in last["ids"]:
                    self.canvas.delete(gid)

    @property
    def img_offset_x(self):
        return (self.canvas.winfo_width() - self.display_image.width) // 2

    @property
    def img_offset_y(self):
        return (self.canvas.winfo_height() - self.display_image.height) // 2

    @property
    def img_scale_x(self):
        return self.image.width / self.display_image.width

    @property
    def img_scale_y(self):
        return self.image.height / self.display_image.height


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCropperApp(root)
    root.mainloop()
