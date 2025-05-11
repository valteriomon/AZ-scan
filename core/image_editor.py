"""
TODO
    - Set in all editors same config.
"""
import os
import tkinter as tk
from tkinter import ttk
from core.image_viewer import ImageViewer
import math
import numpy as np
from PIL import Image
from core.constants import APP_TITLE, EDITOR_VIEW_TITLE

class ImageEditor(ImageViewer):
    def __init__(self, master, filepath, status_bar_enabled=False):
        super().__init__(master, filepath, status_bar_enabled)
        self.title = f"{APP_TITLE} - {EDITOR_VIEW_TITLE}"
        self.original_image = None

    def set_image(self, filepath=None):
        super().set_image(filepath)
        self.original_image = self.pil_image.copy()
        self._set_initial_state()

    def _create_canvas(self):
        super()._create_canvas()
        self._add_bindings()

    def _setup_widgets(self):
        def _create_editor_top_toolbar():
            """Creates and enables the editor mode, including a top bar."""
            self.editor_top_tool_frame = tk.Frame(self.layout_frame, padx=5, pady=5)
            self.editor_top_tool_frame.pack(side=tk.TOP, fill=tk.X)

            self.advanced_mode_var = tk.BooleanVar(value=False)
            self.advanced_mode_var.trace_add("write", self._toggle_advanced_mode)
            self.rotation_angle_var = tk.DoubleVar(value=0.0)
            self.rotation_angle_var.trace_add("write", self._update_rotation_label)

            self.editor_top_basic_tools = tk.Frame(self.editor_top_tool_frame, padx=5, pady=5)
            self.editor_top_basic_tools.pack(side=tk.TOP, fill=tk.X)

            ttk.Button(self.editor_top_basic_tools, text="⟲ Rotar en sentido antihorario (d)", command=self._rotate_left, width=30).pack(side="left")
            ttk.Button(self.editor_top_basic_tools, text="⟳ Rotar en sentido horario (f)", command=self._rotate_right, width=30).pack(side="left")

            ttk.Checkbutton(self.editor_top_basic_tools, text="Modo editor (e)", variable=self.advanced_mode_var).pack(side="right", padx=(20, 0))
            self.rotation_label = ttk.Label(self.editor_top_basic_tools, text=f"Rotación actual: 0°")
            self.rotation_label.pack(side="right")

        def _create_editor_bottom_toolbar():
            self.editor_bottom_tool_frame = tk.Frame(self.layout_frame, padx=5, pady=5)
            self.editor_bottom_tool_frame.pack(side=tk.BOTTOM, fill=tk.X)

            ttk.Button(self.editor_bottom_tool_frame, text="Deshacer (ctrl + z)", command=self._undo).pack(side="left")
            ttk.Button(self.editor_bottom_tool_frame, text="Resetear (q)", command=self._reset_original).pack(side="left")
            ttk.Button(self.editor_bottom_tool_frame, text="Guardar (ctrl + s)", command=self._save).pack(side="right")

        def _create_editor_advanced_toolbar():
            self.editor_advanced_tool_frame = tk.Frame(self.editor_top_tool_frame, padx=5, pady=5)

            self.rotation_horizon_var = tk.BooleanVar(value=False)
            # self.rotation_horizon_var.trace_add("write", self._toggle_advanced_mode)

            ttk.Checkbutton(self.editor_advanced_tool_frame, text="Horizonte de rotación (r)", variable=self.rotation_horizon_var).pack(side="left", padx=(0,10))

            ttk.Label(self.editor_advanced_tool_frame, text=f"Rotación fina (t):").pack(side="left")
            self.fine_rotation_var = tk.StringVar(value="0.5")

            ttk.Radiobutton(self.editor_advanced_tool_frame, text="0.1", variable=self.fine_rotation_var, value="0.1").pack(side='left', padx=5)
            ttk.Radiobutton(self.editor_advanced_tool_frame, text="0.5", variable=self.fine_rotation_var, value="0.5").pack(side='left', padx=5)
            ttk.Radiobutton(self.editor_advanced_tool_frame, text="1", variable=self.fine_rotation_var, value="1").pack(side='left', padx=5)
            ttk.Radiobutton(self.editor_advanced_tool_frame, text="5", variable=self.fine_rotation_var, value="5").pack(side='left', padx=5)

        _create_editor_top_toolbar()
        _create_editor_advanced_toolbar()
        super()._setup_widgets()
        _create_editor_bottom_toolbar()

    def _set_initial_state(self, event=None):
        self.rotation_angle = 0
        self.rotation_angle_var.set(self.rotation_angle)
        if not hasattr(self, "image_stack"):
            self.image_stack = []
        else:
            self.image_stack.clear()

        # self.editing = False
        # self.level_line = None
        # self.advanced_editor = False
        # self.rect = None
        # self.start_x = self.start_y = None

    def _update_rotation_label(self, *args):
        display_angle = round(self.rotation_angle_var.get(), 1)

        if isinstance(display_angle, float) and display_angle.is_integer():
            display_angle = int(display_angle)

        self.rotation_label.config(text=f"Rotation: {display_angle}°")

    def _toggle_advanced_mode(self, *args):
        advanced_mode = self.advanced_mode_var.get()
        if advanced_mode:
            self.editor_advanced_tool_frame.pack(side=tk.TOP, fill=tk.X)
        else:
            self.editor_advanced_tool_frame.pack_forget()

    # def _toggle_rotation_horizon(self, *args):
    #     self.rotation_horizon = self.advanced_mode_var.get()

    def _save(self, event=None):
        pass

    def _undo(self, event=None):
        if self.image_stack:
            self.previous_image = self.image_stack.pop()
            self.pil_image = self.previous_image.get("image", self.original_image)
            self.rotation_angle = self.previous_image.get("rotation_angle", 0)
            self.rotation_angle_var.set(self.rotation_angle)
            # self.rotation_angle_var.set(360 - int(self.rotation_angle))
            if not self.image_stack:
                self._set_initial_state()
        self._zoom_fit()

    def _reset_original(self, event=None):
        self.pil_image = self.original_image.copy()
        self._set_initial_state()
        self._zoom_fit()

    def _rotate_left(self, event=None):
        self._rotate_image(90)
        self._zoom_fit()

    def _rotate_right(self, event=None):
        self._rotate_image(-90)
        self._zoom_fit()

    def _fine_rotate(self, angle):
        self._rotate_image(angle)
        self._zoom_fit()

    def _rotate_image(self, angle):
        if self.pil_image:
            self.total_rotation = (self.rotation_angle - angle) % 360
            self.rotation_angle = self.total_rotation

            # if angle == 90 or angle == -90:
            #     self.rotation_angle = (self.rotation_angle + angle) % 360  # Reset to 90-degree increments
            # else:
            #     self.rotation_angle += angle
            # self.rotation_angle %= 360  # Ensure rotation stays within 0-360 degrees
            # current_rotation_angle = self.rotation_angle_var.get()

            self.image_stack.append({
                "image": self.pil_image.copy(),
                "rotation_angle": self.total_rotation
            })
            print(angle, self.total_rotation)
            # self.pil_image = self.pil_image.rotate(angle, expand=True)
            self.pil_image = self.original_image.rotate(-self.total_rotation, expand=True, resample=Image.BICUBIC)
            self.rotation_angle_var.set(self.total_rotation)
            # self.rotation_angle_var.set(new_rotation_angle)

    def _mouse_wheel(self, event):
        if event.state & 0x0004:  # Control key
            if (event.delta < 0):
                self._rotate_right()
            else:
                self._rotate_left()
        elif event.state & 0x0001:  # Shift key
            step = float(self.fine_rotation_var.get())
            print(step)
            if event.delta < 0:
                self._fine_rotate(-step)
            else:
                self._fine_rotate(step)
        else:
            return super()._mouse_wheel(event)

    def _cycle_fine_rotation(self, event=None):
        options = ["0.1", "0.5", "1", "5"]
        current = self.fine_rotation_var.get()
        try:
            index = options.index(current)
        except ValueError:
            index = 0
        next_index = (index + 1) % len(options)
        self.fine_rotation_var.set(options[next_index])

    def _add_bindings(self):
        self.master.bind_all("<Control-z>", self._undo)
        self.master.bind_all("<q>", self._reset_original)
        self.master.bind_all("<Q>", self._reset_original)
        self.master.bind_all("<e>", lambda e: self.advanced_mode_var.set(not self.advanced_mode_var.get()))
        self.master.bind_all("<E>", lambda e: self.advanced_mode_var.set(not self.advanced_mode_var.get()))
        self.master.bind_all("<f>", self._rotate_right)
        self.master.bind_all("<F>", self._rotate_right)
        self.master.bind_all("<d>", self._rotate_left)
        self.master.bind_all("<D>", self._rotate_left)
        self.master.bind_all("<r>", self._cycle_fine_rotation)
        self.master.bind_all("<R>", self._cycle_fine_rotation)
        self.master.bind_all("<t>", lambda e: self.rotation_horizon_var.set(not self.rotation_horizon_var.get()))
        self.master.bind_all("<T>", lambda e: self.rotation_horizon_var.set(not self.rotation_horizon_var.get()))

        self.master.bind_all("<ButtonRelease-1>", self._mouse_release_left)




    def _mouse_press_left(self, event):
        if event.state & 0x0001:  # Shift key
            self._level_line_press(event)
            print("_mouse_press_left")
            pass
        elif event.state & 0x0004:  # Control key
            pass
        else:
            super()._mouse_press_left(event)


    def _mouse_release_left(self, event):
        if event.state & 0x0001:  # Shift key
            self._level_line_release(event)
            print("_mouse_release_left")
            self._zoom_fit()
            pass
        elif event.state & 0x0004:  # Control key
            pass


    def _mouse_move_left(self, event):
        # self.__old_event = event
        if event.state & 0x0001:  # Shift key
            self._level_line_drag(event)
            print("_mouse_move_left")
            pass
        elif event.state & 0x0004:  # Control key
            pass
        else:
            super()._mouse_move_left(event)





    def _level_line_press(self, event):
        print("level_line_press", event.x, event.y)
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
        # self.pil_image = self.pil_image.rotate(angle_deg, expand=True, resample=Image.BICUBIC)
        self._rotate_image(angle_deg)



























        # bind_target.bind("<ButtonPress-3>", self._level_line_press)
        # bind_target.bind("<B3-Motion>", self._level_line_drag)


        # bind_target.bind("<x>", self._crop_using_crosshairs)
        # bind_target.bind_all("<KeyPress-Control_L>", self._on_key_press)
        # bind_target.bind_all("<KeyRelease-Control_L>", self._on_key_release)
        # bind_target.bind_all("<KeyPress-Control_R>", self._on_key_press)
        # bind_target.bind_all("<KeyRelease-Control_R>", self._on_key_release)
        # bind_target.bind_all("<KeyPress-Shift_L>", self._on_key_press)
        # bind_target.bind_all("<KeyRelease-Shift_L>", self._on_key_release)
        # bind_target.bind_all("<KeyPress-Shift_R>", self._on_key_press)
        # bind_target.bind_all("<KeyRelease-Shift_R>", self._on_key_release)

        # bind_target.focus_set()  # Make surfe the canvas has keyboard focus

        # Advanced editor
        # Right click
        # Left click
        # Middle click
        # Double click
        # Scroll wheel
        # Modifiers ctrl, alt, shift













        # if self.original_image:
        #     self.image = self.original_image.copy()  # Restore the original image
        #     self.rotation_angle = 0  # Reset the rotation angle
        #     self.scale.set(1) # Reset the scale
        #     self.image_stack.clear()
        #     self.update_display_image()
        #     self.update_rotation_label()
    # def _clear_editing_state(self):
    #     self.editing = False
    #     self._ImageViewer__old_event = None
    #     self.start_x = None
    #     self.start_y = None
    #     if hasattr(self, "level_line") and self.level_line:
    #         self.canvas.delete(self.level_line)
    #         self.level_line = None
    #     if hasattr(self, "rect") and self.rect:
    #         self.canvas.delete(self.rect)
    #         self.rect = None



    # def _save(self, event=None):
    #     return
    #     self.pil_image.save(self.filepath.get())

    #     print("image_path")
    #     image_path = self.filepath.get()

    #     if self.pil_image and image_path:
    #         # Backup first
    #         base, ext = os.path.splitext(image_path)
    #         timestamp = int(time.time())
    #         backup_path = f"{base}.{timestamp}.bak{ext}"
    #         if not os.path.exists(backup_path):
    #             shutil.copy2(image_path, backup_path)
    #         else:
    #             print(f"Backup already exists at: {backup_path}")

    #         # Save (overwrite)
    #         self.pil_image.save(image_path)
    #         print(f"Image saved and original backed up at: {backup_path}")

    #     else:
    #         print("No image loaded or original path unknown.")






    # def _mouse_press_left(self, event):
    #     if event.state & 0x0001:  # Shift key
    #         self._ImageViewer__old_event = event
    #         self.editing = True
    #         self._level_line_press(event)
    #     elif event.state & 0x0004:  # Control key
    #         self._ImageViewer__old_event = event
    #         self.editing = True
    #         self._crop_press(event)
    #     else:
    #         super()._mouse_press_left(event)


    # def _mouse_release_left(self, event):

    #     if event.state & 0x0001:  # Shift key
    #         self._level_line_release(event)
    #     elif event.state & 0x0004:  # Control key
    #         self._crop_release(event)
    #     elif self.editing:
    #         self.editing = False
    #         # self._zoom_fit()

    # def _mouse_move_left(self, event):
    #     # self.__old_event = event
    #     if event.state & 0x0001:  # Shift key
    #         self._level_line_drag(event)
    #     elif event.state & 0x0004:  # Control key
    #         self._crop_drag(event)

    #     else:
    #         super()._mouse_move_left(event)













    # def _crop_press(self, event):
    #     # if self.display_image:
    #         self.start_x = event.x
    #         self.start_y = event.y
    #         self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    # def _crop_drag(self, event):
    #     if self.rect:
    #         self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    # def _crop_release(self, event):
    #     if self.pil_image and self.rect:
    #         x0, y0, x1, y1 = map(int, self.canvas.coords(self.rect))
    #         x0, x1 = sorted((x0, x1))
    #         y0, y1 = sorted((y0, y1))

    #         (scale, offsetx, offsety) = self._compute_scale_and_offset()

    #         # Adjust for image position and scale
    #         # x0_adj = int((x0 - self.img_offset_x) * self.img_scale_x)
    #         # y0_adj = int((y0 - self.img_offset_y) * self.img_scale_y)
    #         # x1_adj = int((x1 - self.img_offset_x) * self.img_scale_x)
    #         # y1_adj = int((y1 - self.img_offset_y) * self.img_scale_y)

    #         x0_adj = int((x0 - offsetx) / scale)
    #         y0_adj = int((y0 - offsety) / scale)
    #         x1_adj = int((x1 - offsetx) / scale)
    #         y1_adj = int((y1 - offsety) / scale)


    #         print(x0_adj, y0_adj, x1_adj, y1_adj)

    #         if (x1_adj > x0_adj and y1_adj > y0_adj and
    #             0 <= x0_adj < self.pil_image.width and
    #             0 <= y0_adj < self.pil_image.height and
    #             x1_adj <= self.pil_image.width and
    #             y1_adj <= self.pil_image.height):

    #             self.image_stack.append({"img": self.pil_image.copy()})  # Save for undo

    #             self.pil_image = self.pil_image.crop((x0_adj, y0_adj, x1_adj, y1_adj))
    #             self._zoom_fit()

    #         self.canvas.delete(self.rect)
    #         self.rect = None













if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Image editor.")
    parser.add_argument("image", help="Path to the image file.")
    args = parser.parse_args()

    root = tk.Tk()
    app = ImageEditor(master=root, filepath=args.image)

    app.mainloop()