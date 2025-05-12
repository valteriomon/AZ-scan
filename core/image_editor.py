"""
TODO
    - Set in all editors same config.
    - Crosshair mode.
"""
import os, shutil, threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from core.image_viewer import ImageViewer
import math
import numpy as np
from PIL import Image
from core.auto_crop import AutoCrop
from core.constants import APP_TITLE, EDITOR_VIEW_TITLE

class ImageEditor(ImageViewer):
    def __init__(self, master, filepath, status_bar_enabled=False):
        super().__init__(master, filepath, status_bar_enabled)
        self.master = master
        self.title = f"{APP_TITLE} - {EDITOR_VIEW_TITLE}"
        self.original_image = None
        # Rotations are applied on cropped image
        self.cropped_image = None

    def set_image(self, filepath=None):
        super().set_image(filepath)
        self.original_image = self.pil_image.copy()
        self.cropped_image = self.pil_image.copy()
        self._set_initial_state()

    def _create_canvas(self):
        super()._create_canvas()
        self._add_bindings()

    def _setup_widgets(self):
        def _create_editor_top_toolbar():
            """Creates and enables the editor mode, including a top bar."""
            self.editor_top_tool_frame = tk.Frame(self.layout_frame, padx=5, pady=5)
            self.editor_top_tool_frame.pack(side=tk.TOP, fill=tk.X)

            self.rotation_angle_var = tk.DoubleVar(value=0.0)
            self.rotation_angle_var.trace_add("write", self._update_rotation_label)

            self.editor_top_basic_tools = tk.Frame(self.editor_top_tool_frame, padx=5, pady=5)
            self.editor_top_basic_tools.pack(side=tk.TOP, fill=tk.X)

            ttk.Button(self.editor_top_basic_tools, text="⟲ Rotar en sentido antihorario", command=self._rotate_left, width=30).pack(side="left")
            ttk.Button(self.editor_top_basic_tools, text="⟳ Rotar en sentido horario", command=self._rotate_right, width=30).pack(side="left")

            # ttk.Label(self.editor_top_basic_tools, text=f"Rotación fina:").pack(side="left", padx=10)
            self.fine_rotation_var = tk.StringVar(value="0.5")

            # ttk.Radiobutton(self.editor_top_basic_tools, text="0.1°", variable=self.fine_rotation_var, value="0.1").pack(side='left', padx=5)
            # ttk.Radiobutton(self.editor_top_basic_tools, text="0.5°", variable=self.fine_rotation_var, value="0.5").pack(side='left', padx=5)
            # ttk.Radiobutton(self.editor_top_basic_tools, text="1°", variable=self.fine_rotation_var, value="1").pack(side='left', padx=5)
            # ttk.Radiobutton(self.editor_top_basic_tools, text="5°", variable=self.fine_rotation_var, value="5").pack(side='left', padx=5)

            self.rotation_label = ttk.Label(self.editor_top_basic_tools, text=f"Rotación actual: 0°")
            self.rotation_label.pack(side="right")

        def _create_editor_bottom_toolbar():
            self.editor_bottom_tool_frame = tk.Frame(self.layout_frame, padx=0, pady=5)
            self.editor_bottom_tool_frame.pack(side=tk.BOTTOM, fill=tk.X)

            # ttk.Button(self.editor_bottom_tool_frame, text="Deshacer (ctrl + z)", command=self._undo, width=18).pack(side="left", padx=(0,8))
            # ttk.Button(self.editor_bottom_tool_frame, text="Resetear", command=self._reset_original, width=18).pack(side="left")
            self.save_button = ttk.Button(self.editor_bottom_tool_frame, text="Guardar", command=self._save, width=18)
            self.save_button.pack(side="right", padx=(8,0))
            ttk.Button(self.editor_bottom_tool_frame, text="Abrir carpeta", command=self._open_folder, width=18).pack(side="right")

        _create_editor_top_toolbar()
        super()._setup_widgets()
        # _create_editor_bottom_toolbar()

    def _set_initial_state(self, event=None):
        self.rotation_angle = 0
        self.rotation_angle_var.set(self.rotation_angle)
        if not hasattr(self, "image_stack"):
            self.image_stack = []
        else:
            self.image_stack.clear()

        self.level_line = None
        self.ctrl_held = False
        self.rect = None
        # Crop tool variables
        self.crop_start = None
        self.crop_rect = None
        # self.start_x = self.start_y = None
        # self.temp_guides = []  # Two guide line IDs during Alt-drag
        # self.guide_stack = []  # Stores both lines per guide crosshair

    def _update_rotation_label(self, *args):
        display_angle = round(self.rotation_angle_var.get(), 1)
        if isinstance(display_angle, float) and display_angle.is_integer():
            display_angle = int(display_angle)
        self.rotation_label.config(text=f"Rotación: {display_angle}°")

    def _save(self, event=None):
        image_path = self.filepath.get()
        if self.pil_image and image_path:
            # self.save_button.config(state="disabled")

            # Save (overwrite)
            self.pil_image.save(image_path)
            # self.save_button.config(state="normal")
        else:
            print("No image loaded or original path unknown.")

    def _backup(image_path):

        # Prepare backup folder
        base_dir = os.path.dirname(image_path)
        backup_dir = os.path.join(base_dir, "Escaneos originales")
        os.makedirs(backup_dir, exist_ok=True)  # Create if it doesn't exist

        # Create timestamped backup filename
        base_name, ext = os.path.splitext(os.path.basename(image_path))
        human_timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        backup_filename = f"{base_name}.{human_timestamp}.bak{ext}"
        backup_path = os.path.join(backup_dir, backup_filename)

        # Backup original file
        if not os.path.exists(backup_path):
            shutil.copy2(image_path, backup_path)
        else:
            print(f"Backup already exists at: {backup_path}")


    def _undo(self, event=None):
        if self.image_stack:
            self.previous_image = self.image_stack.pop()
            self.pil_image = self.previous_image.get("image", self.original_image)
            self.cropped_image = self.pil_image.copy()
            self.rotation_angle = self.previous_image.get("rotation_angle", 0)
            self.rotation_angle_var.set(self.rotation_angle)
            if not self.image_stack:
                self._set_initial_state()
        self._zoom_fit()

    def _reset_original(self, event=None):
        self.pil_image = self.original_image.copy()
        self.cropped_image = self.original_image.copy()
        self._set_initial_state()
        self._zoom_fit()

    def _cycle_fine_rotation(self, event=None):
        options = ["0.1", "0.5", "1", "5"]
        current = self.fine_rotation_var.get()
        try:
            index = options.index(current)
        except ValueError:
            index = 0
        next_index = (index + 1) % len(options)
        self.fine_rotation_var.set(options[next_index])

    """
    Events
    """
    def _mouse_wheel(self, event):
        if event.state & 0x0004:  # Control key
            if (event.delta < 0):
                self._rotate_right()
            else:
                self._rotate_left()
        elif event.state & 0x0001:  # Shift key
            step = float(self.fine_rotation_var.get())
            if event.delta < 0:
                self._fine_rotate(-step)
            else:
                self._fine_rotate(step)
        else:
            return super()._mouse_wheel(event)

    def _mouse_press_left(self, event):
        if event.state & 0x0001:  # Shift key
            self._level_line_press(event)
    #         self._ImageViewer__old_event = event
        elif event.state & 0x0004:  # Control key
            self._crop_press(event)
        else:
            super()._mouse_press_left(event)

    def _mouse_release_left(self, event):
        if event.state & 0x0001:  # Shift key
            self._level_line_release(event)
        elif event.state & 0x0004:  # Control key
            self._crop_release(event)

    def _mouse_move_left(self, event):

        if event.state & 0x0001:  # Shift key
            self._level_line_drag(event)
            print("_mouse_move_left")
        elif event.state & 0x0004:  # Control key
            self._crop_drag(event)
        else:
            super()._mouse_move_left(event)

    #         self.editing = False

    def _on_ctrl_press(self, event):
        if not self.ctrl_held:
            self.ctrl_held = True
            self._zoom_fit()


    def _on_ctrl_release(self, event):
        self.ctrl_held = False

    """
    Rotating using line as reference.
    """
    def _level_line_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        self.level_line = self.canvas.create_line(event.x, event.y, event.x, event.y, fill="red", width=2)

    def _level_line_drag(self, event):
        if self.level_line:
            self.canvas.coords(self.level_line, self.start_x, self.start_y, event.x, event.y)

    def _level_line_release(self, event):
        if self.level_line:
            coords = self.canvas.coords(self.level_line)
            if len(coords) == 4:
                x0, y0, x1, y1 = coords
                self.canvas.delete(self.level_line)
                self.level_line = None
                self.canvas.delete(self.level_line)
                self._level_image_from_line(x0, y0, x1, y1)
            else:
                print("Warning: level_line has invalid coordinates:", coords)
                self.canvas.delete(self.level_line)
                self.level_line = None

    def _level_image_from_line(self, x0, y0, x1, y1):
        # Convert canvas coords to image coords
        (scale, offsetx, offsety) = self._compute_scale_and_offset()
        img_x0 = (x0 - offsetx) * scale
        img_y0 = (y0 - offsety) * scale
        img_x1 = (x1 - offsetx) * scale
        img_y1 = (y1 - offsety) * scale

        # Calculate angle in degrees
        dx = img_x1 - img_x0
        dy = img_y1 - img_y0
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)

        # Rotate image so that the line becomes horizontal
        self._rotate_image(angle_deg)

    """
    Rotation
    """
    def _rotate_left(self, event=None):
        self._rotate_image(90, self._save)

    def _rotate_right(self, event=None):
        self._rotate_image(-90, self._save)

    def _fine_rotate(self, angle):
        self._rotate_image(angle)

    def _rotate_image(self, angle, callback=None):
        def worker():
            if self.pil_image:
                self.total_rotation = (self.rotation_angle - angle) % 360
                self.rotation_angle = self.total_rotation
                # rotated = self.original_image.rotate(-self.total_rotation, expand=True, resample=Image.BICUBIC)
                rotated = self.cropped_image.rotate(-self.total_rotation, expand=True, resample=Image.BICUBIC)
                self.image_stack.append({
                    "image": self.pil_image.copy(),
                    "rotation_angle": self.total_rotation
                })
                # self.rotation_angle_var.set(self.total_rotation)
                self.after(0, lambda: self._apply_rotation_result(rotated, callback=callback))

        threading.Thread(target=worker, daemon=True).start()

    def _apply_rotation_result(self, rotated_image, callback=None):
        self.pil_image = rotated_image
        self.rotation_angle_var.set(self.total_rotation)
        if callback:
            callback()
        self._zoom_fit()

    """
    Cropping
    """
    def _crop_press(self, event):
    #     if self.pil_image:
    #         self.start_x = event.x
    #         self.start_y = event.y
    #         self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red", width=2)
    #     else:
    #         self.rect = None

    # def start_crop(self, event):
        if self.pil_image:
            self.crop_start = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
            if self.crop_rect:
                self.canvas.delete(self.crop_rect)

    def _crop_drag(self, event):
    #     if self.rect:
    #         self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    # def draw_crop(self, event):
        img = self.pil_image
        if img and self.crop_start:
            x0, y0 = self.crop_start
            x1, y1 = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
            if self.crop_rect:
                self.canvas.delete(self.crop_rect)
            self.crop_rect = self.canvas.create_rectangle(x0, y0, x1, y1, outline="red", width=2)

    def _crop_release(self, event):
        if self.pil_image and self.crop_rect:
            coords = self.canvas.coords(self.crop_rect)
            if len(coords) != 4:
                # Invalid or zero-size rectangle, clean up and abort
                self.canvas.delete(self.crop_rect)
                self.crop_rect = None
                return

            x0, y0, x1, y1 = map(int, coords)
            x0, x1 = sorted((x0, x1))
            y0, y1 = sorted((y0, y1))

            (scale, offsetx, offsety) = self._compute_scale_and_offset()

            x0_adj = int((x0 - offsetx) / scale)
            y0_adj = int((y0 - offsety) / scale)
            x1_adj = int((x1 - offsetx) / scale)
            y1_adj = int((y1 - offsety) / scale)

            if (x1_adj > x0_adj and y1_adj > y0_adj and
                0 <= x0_adj < self.pil_image.width and
                0 <= y0_adj < self.pil_image.height and
                x1_adj <= self.pil_image.width and
                y1_adj <= self.pil_image.height):

                self.image_stack.append({"image": self.pil_image.copy(), "rotation_angle": self.rotation_angle})  # Save for undo
                self.cropped_image = self.pil_image.crop((x0_adj, y0_adj, x1_adj, y1_adj))
                self.pil_image = self.cropped_image.copy()
                self._zoom_fit()

        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
            self.crop_rect = None

    # def end_crop(self, event):
        # img = self.pil_image
        # if img and self.crop_start and self.crop_rect:
        #     x0, y0 = map(int, self.crop_start)
        #     x1, y1 = map(int, (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)))
        #     x0, x1 = sorted([x0, x1])
        #     y0, y1 = sorted([y0, y1])

        #     canvas_bbox = self.canvas.bbox(self.image_container)
        #     if not canvas_bbox:  # Ensure the image container exists
        #         return

        #     disp_w = canvas_bbox[2] - canvas_bbox[0]
        #     disp_h = canvas_bbox[3] - canvas_bbox[1]

        #     ratio_x = img.width / disp_w
        #     ratio_y = img.height / disp_h

        #     img_x0, img_y0 = self.canvas.coords(self.image_container)

        #     crop_x0 = int((x0 - img_x0) * ratio_x)
        #     crop_y0 = int((y0 - img_y0) * ratio_y)
        #     crop_x1 = int((x1 - img_x0) * ratio_x)
        #     crop_y1 = int((y1 - img_y0) * ratio_y)

        #     if crop_x1 - crop_x0 > 0 and crop_y1 - crop_y0 > 0:
        #         # save_history()
        #         img = img.crop((crop_x0, crop_y0, crop_x1, crop_y1))
        #         self.pil_image = img
        #         self._zoom_fit()
        #         # update_display(img)

        #     self.canvas.delete(self.crop_rect)
        #     self.crop_rect = None
        #     self.crop_start = None







    # def _crosshair_remove(self, event):
    #     if self.guide_stack:
    #         last = self.guide_stack.pop()
    #         if "ids" in last:
    #             for gid in last["ids"]:
    #                 self.canvas.delete(gid)

    # def _redraw_crosshairs(self):
    #     # First, delete any existing crosshair lines
    #     for guide in self.guide_stack:
    #         if "ids" in guide:
    #             for gid in guide["ids"]:
    #                 self.canvas.delete(gid)
    #         guide["ids"] = []  # Clear old ids

    #     # Then, re-create them and store new ids
    #     for guide in self.guide_stack:
    #         scale, offsetx, offsety = self._compute_scale_and_offset(
    #             self.canvas.winfo_width(), self.canvas.winfo_height(),
    #             self.pil_image.width, self.pil_image.height
    #         )

    #         rel_x, rel_y = guide["rel_coords"]
    #         canvas_x = rel_x * scale + offsetx
    #         canvas_y = rel_y * scale + offsety

    #         vline = self.canvas.create_line(canvas_x, 0, canvas_x, self.canvas.winfo_height(), fill="red")
    #         hline = self.canvas.create_line(0, canvas_y, self.canvas.winfo_width(), canvas_y, fill="red")
    #         guide["ids"] = [vline, hline]

    # def _crop_using_crosshairs(self, event):
    #     if len(self.guide_stack) != 2:
    #         print("Need exactly 2 crosshairs to crop.")
    #         return

    #     # Get relative coordinates from guide stack
    #     rel_coords_1 = self.guide_stack[0]["rel_coords"]
    #     rel_coords_2 = self.guide_stack[1]["rel_coords"]

    #     # Convert to image coordinates
    #     x0 = int(min(rel_coords_1[0], rel_coords_2[0]))
    #     y0 = int(min(rel_coords_1[1], rel_coords_2[1]))
    #     x1 = int(max(rel_coords_1[0], rel_coords_2[0]))
    #     y1 = int(max(rel_coords_1[1], rel_coords_2[1]))

    #     # Ensure bounds are valid
    #     if (x1 > x0 and y1 > y0 and
    #         0 <= x0 < self.pil_image.width and
    #         0 <= y0 < self.pil_image.height and
    #         x1 <= self.pil_image.width and
    #         y1 <= self.pil_image.height):

    #         self.image_stack.append(self.pil_image.copy())  # Save for undo

    #         self.pil_image = self.pil_image.crop((x0, y0, x1, y1))
    #         self.guide_stack = []  # Clear guides
    #         self._zoom_fit()
    #         # self._redraw_image()
    #         # self._redraw_crosshairs()
    #     else:
    #         print("Invalid crop bounds.")

    """
    Bindings
    """
    def _add_bindings(self):
        pass
        # self.master.bind_all("<Control-z>", self._undo)
        # self.master.bind_all("<Control-s>", self._save)
        # self.master.bind_all("<f>", self._rotate_right)
        # self.master.bind_all("<F>", self._rotate_right)
        # self.master.bind_all("<d>", self._rotate_left)
        # self.master.bind_all("<D>", self._rotate_left)
        # self.master.bind_all("<r>", self._cycle_fine_rotation)
        # self.master.bind_all("<R>", self._cycle_fine_rotation)
        # self.canvas.bind("<ButtonRelease-1>", self._mouse_release_left)
        # self.canvas.bind("<Control_L>", self._on_ctrl_press)
        # self.canvas.bind("<KeyRelease-Control_L>", self._on_ctrl_release)
        # self.canvas.focus_set()

        # self.master.bind_all("<Control-Button-1>", self._crop_press)
        # Bind crop tool events to the canvas
        # self.master.bind_all("<Control-Button-1>", self.start_crop)
        # self.master.bind_all("<Control-B1-Motion>", self.draw_crop)
        # self.master.bind_all("<Control-ButtonRelease-1>", self.end_crop)

    def _autocrop(self, event):
        np_array = AutoCrop(self.pil_image).method()
        self.pil_image = Image.fromarray(np_array)
        self._zoom_fit()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Image editor.")
    parser.add_argument("image", help="Path to the image file.")
    args = parser.parse_args()

    root = tk.Tk()
    app = ImageEditor(master=root, filepath=args.image)

    app.mainloop()