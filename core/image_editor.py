











class EditorImageViewer(ImageViewer):
    def __init__(self, master, filepath, status_bar_enabled=True):
        super().__init__(master, filepath, status_bar_enabled)

        self.edit_mode = False
        self.image_stack = []
        self.original_image = None

        self.rotation_angle = 0
        self.level_line = None

        self.rect = None
        self.start_x = self.start_y = None

        self.temp_guides = []  # Two guide line IDs during Alt-drag
        self.guide_stack = []  # Stores both lines per guide crosshair

        self.rotation_label = tk.Label(self.frame_status_bar, text="Rotation: 0°")
        self.rotation_label.pack(side="right", padx=(10, 0))

    def set_image(self, filepath=None):
        if not filepath:
            filepath = self.filepath.get()

        self.pil_image = Image.open(filepath)
        self.original_image = self.pil_image.copy()
        self.filepath.set(filepath)
        self._zoom_fit()
        # self._draw_image(self.pil_image)

        if self.is_main_window:
            filename = os.path.basename(filepath)
            self.master.title(f"{self.title} - {filename}")
        # super().set_image(filepath)
        # self.image_stack.clear()
        # self.original_image = self.image_pil.copy()  # Store the original image
        # self.rotation_angle = 0  # Reset rotation

    def _setup_widgets(self):
        self._create_editor_mode()       # Insert toolbar FIRST
        super()._setup_widgets()         # Then canvas + status bar

    def _create_editor_mode(self):
        """Creates and enables the editor mode, including a top bar."""
        self.editor_mode_frame = tk.Frame(self.layout_frame)
        self.editor_mode_frame.pack(side=tk.TOP, fill=tk.X)

        self.editor_mode_var = tk.BooleanVar(value=False)

        tk.Button(self.editor_mode_frame, text="Deshacer", command=self.undo).pack(side="left")

        tk.Button(self.editor_mode_frame, text="⟲ Rotar en sentido antihorario").pack(side="left")   # Counterclockwise
        tk.Button(self.editor_mode_frame, text="⟳ Rotar en sentido horario", ).pack(side="left")  # Clockwise

        tk.Checkbutton(self.editor_mode_frame, text="Modo editor", variable=self.editor_mode_var).pack(side="right")


    def _create_canvas(self):
        super()._create_canvas()

        bind_target = self.canvas

        # bind_target.bind("<f>", lambda event: (self._rotate_at(90, event.x, event.y), self._redraw_image()))
        # bind_target.bind("<F>", lambda event: (self._rotate_at(90, event.x, event.y), self._redraw_image()))
        # bind_target.bind("<d>", lambda event: (self._rotate_at(-90, event.x, event.y), self._redraw_image()))
        # bind_target.bind("<D>", lambda event: (self._rotate_at(-90, event.x, event.y), self._redraw_image()))

        bind_target.bind("<f>", lambda event: self.rotate_image(-90))
        bind_target.bind("<F>", lambda event: self.rotate_image(-90))
        bind_target.bind("<d>", lambda event: self.rotate_image(90))
        bind_target.bind("<D>", lambda event: self.rotate_image(90))
        bind_target.bind("<Control-z>", self.undo)

        bind_target.bind("<ButtonPress-3>", self._level_line_press)
        bind_target.bind("<B3-Motion>", self._level_line_drag)
        bind_target.bind("<ButtonRelease-3>", self._level_line_release)

        bind_target.bind("<e>", self._toggle_edit_mode)
        bind_target.bind("<E>", self._toggle_edit_mode)

        bind_target.bind("<x>", self._crop_using_crosshairs)

        bind_target.bind_all("<KeyPress-Control_L>", self._on_key_press)
        bind_target.bind_all("<KeyRelease-Control_L>", self._on_key_release)
        bind_target.bind_all("<KeyPress-Control_R>", self._on_key_press)
        bind_target.bind_all("<KeyRelease-Control_R>", self._on_key_release)
        bind_target.bind_all("<KeyPress-Shift_L>", self._on_key_press)
        bind_target.bind_all("<KeyRelease-Shift_L>", self._on_key_release)
        bind_target.bind_all("<KeyPress-Shift_R>", self._on_key_press)
        bind_target.bind_all("<KeyRelease-Shift_R>", self._on_key_release)



        bind_target.focus_set()  # Make surfe the canvas has keyboard focus

    def _mouse_wheel(self, event):
        # Call the parent class's method
        super()._mouse_wheel(event)

        # Add custom behavior for the child class
        if self.pil_image is None:
            return

        if event.state == 9:
            if (event.delta < 0):
                self._rotate_at(90, event.x, event.y)
            else:
                self._rotate_at(-90, event.x, event.y)
            self._redraw_image()


    def _on_key_press(self, event):
        if event.keysym in ("Control_L", "Control_R"):
            print("ctrl_held = True")
        elif event.keysym in ("Shift_L", "Shift_R"):
            print("shift_held = True")

    def _on_key_release(self, event):
        if event.keysym in ("Control_L", "Control_R"):
            print("ctrl_held = False")
        elif event.keysym in ("Shift_L", "Shift_R"):
            print("shift_held = False")



    def _mouse_wheel_editor(self, event):
        # Call the parent class's method
        # super()._mouse_wheel(event)

        # # Add custom behavior for the child class
        # if self.pil_image is None:
        #     return

        # if event.state == 9:
        #     if (event.delta < 0):
        #         self._rotate_at(0.5, event.x, event.y)
        #     else:
        #         self._rotate_at(-0.5, event.x, event.y)
        #     self._redraw_image()

        is_ctrl = event.state & 0x0004
        is_shift = event.state & 0x0001

        if is_ctrl:
            step = 0.1
        elif is_shift:
            step = 5
        else:
            step = 0.5

        if event.delta < 0:
            self._rotate_at(step, event.x, event.y)
        else:
            self._rotate_at(-step, event.x, event.y)

        self._redraw_image()

    def _rotate(self, deg:float):
        mat = np.eye(3)
        mat[0, 0] = math.cos(math.pi * deg / 180)
        mat[1, 0] = math.sin(math.pi * deg / 180)
        mat[0, 1] = -mat[1, 0]
        mat[1, 1] = mat[0, 0]

        self.mat_affine = np.dot(mat, self.mat_affine)

    def _rotate_at(self, deg:float, cx:float, cy:float):
        self._translate(-cx, -cy)
        self._rotate(deg)
        self._translate(cx, cy)

    def rotate_image(self, angle):
        if self.pil_image:
            if angle == 90 or angle == -90:
                self.rotation_angle = (self.rotation_angle + angle) % 360  # Reset to 90-degree increments
            else:
                self.rotation_angle += angle

            self.rotation_angle %= 360  # Ensure rotation stays within 0-360 degrees
            self.image_stack.append(self.pil_image.copy())  # Save the previous state
            self.pil_image = self.original_image.rotate(self.rotation_angle, expand=True)  # Rotate the original image
            self._zoom_fit()
            # self.update_display_image()
            # self.update_rotation_label()

    def undo(self, event=None):
        if self.image_stack:
            self.pil_image = self.image_stack.pop()
            self._zoom_fit()



    def activate_editor_mode(self):
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<Double-Button-1>")
        self.canvas.unbind("<MouseWheel>")
        # bind editor-specific handlers here if needed
        self.canvas.bind("<ButtonPress-1>", self._crosshair_press)
        self.canvas.bind("<B1-Motion>", self._crosshair_drag)
        self.canvas.bind("<ButtonRelease-1>", self._crosshair_release)
        self.canvas.bind("<Control-s>", self._save)
        # self.canvas.bind("<Double-Button-1>", self._crop_release)
        self.canvas.bind("<MouseWheel>", self._mouse_wheel_editor)

        self.canvas.config(cursor="cross")

    def deactivate_editor_mode(self):
        self.canvas.bind("<Button-1>", self._mouse_press_left)
        self.canvas.bind("<B1-Motion>", self._mouse_move_left)
        self.canvas.bind("<Double-Button-1>", self._mouse_double_click_left)
        self.canvas.bind("<MouseWheel>", self._mouse_wheel)
        self.canvas.config(cursor="arrow")







    def _level_line_press(self, event):
        modifiers = event.state
        self.start_x, self.start_y = event.x, event.y

        if modifiers & 0x0004:  # Ctrl key
            self.level_line = self.canvas.create_line(event.x, event.y, event.x, event.y, fill="blue", width=2)

    def _level_line_drag(self, event):
        if self.level_line:
            self.canvas.coords(self.level_line, self.start_x, self.start_y, event.x, event.y)

    def _level_line_release(self, event):
        if self.level_line:
            x0, y0, x1, y1 = self.canvas.coords(self.level_line)
            self.canvas.delete(self.level_line)
            self.level_line = None
            self.level_image_from_line(x0, y0, x1, y1)









    def _crop_press(self, event):
        # if self.display_image:
            self.start_x = event.x
            self.start_y = event.y
            self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    def _crop_drag(self, event):
        if self.rect:
            self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def _crop_release(self, event):
        if self.pil_image and self.rect:
            x0, y0, x1, y1 = map(int, self.canvas.coords(self.rect))
            x0, x1 = sorted((x0, x1))
            y0, y1 = sorted((y0, y1))

            (scale, offsetx, offsety) = self._compute_scale_and_offset()

            # Adjust for image position and scale
            # x0_adj = int((x0 - self.img_offset_x) * self.img_scale_x)
            # y0_adj = int((y0 - self.img_offset_y) * self.img_scale_y)
            # x1_adj = int((x1 - self.img_offset_x) * self.img_scale_x)
            # y1_adj = int((y1 - self.img_offset_y) * self.img_scale_y)

            x0_adj = int((x0 - offsetx) / scale)
            y0_adj = int((y0 - offsety) / scale)
            x1_adj = int((x1 - offsetx) / scale)
            y1_adj = int((y1 - offsety) / scale)


            print(x0_adj, y0_adj, x1_adj, y1_adj)

            if (x1_adj > x0_adj and y1_adj > y0_adj and
                0 <= x0_adj < self.pil_image.width and
                0 <= y0_adj < self.pil_image.height and
                x1_adj <= self.pil_image.width and
                y1_adj <= self.pil_image.height):

                self.image_stack.append(self.pil_image.copy())  # Save for undo

                self.pil_image = self.pil_image.crop((x0_adj, y0_adj, x1_adj, y1_adj))
                self._zoom_fit()

            self.canvas.delete(self.rect)
            self.rect = None


    # def crop_image(self, x0, y0, x1, y1):
    #     if self.pil_image and x0 != x1 and y0 != y1:
    #         img_x0 = int((x0 - self.img_offset_x) * self.img_scale_x)
    #         img_y0 = int((y0 - self.img_offset_y) * self.img_scale_y)
    #         img_x1 = int((x1 - self.img_offset_x) * self.img_scale_x)
    #         img_y1 = int((y1 - self.img_offset_y) * self.img_scale_y)

    #         img_x0, img_x1 = sorted((img_x0, img_x1))
    #         img_y0, img_y1 = sorted((img_y0, img_y1))

    #         self.image_stack.append(self.pil_image.copy())
    #         self.pil_image = self.pil_image.crop((img_x0, img_y0, img_x1, img_y1))

            # # Remove all guides
            # for guide in self.guide_stack:
            #     for gid in guide["ids"]:
            #         self.canvas.delete(gid)
            # self.guide_stack.clear()

            # self.update_display_image()


    def _crosshair_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        self.temp_guides = [None, None]  # [vertical_id, horizontal_id]
        # Remove oldest if more than 1 pair already
        if len(self.guide_stack) >= 2:
            old = self.guide_stack.pop(0)
            if "ids" in old:
                for gid in old["ids"]:
                    self.canvas.delete(gid)



    def _crosshair_drag(self, event):
        if self.rect:
            self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

        elif self.temp_guides:
            if self.temp_guides[0]:
                self.canvas.delete(self.temp_guides[0])
            if self.temp_guides[1]:
                self.canvas.delete(self.temp_guides[1])

            self.temp_guides[0] = self.canvas.create_line(event.x, 0, event.x, self.canvas.winfo_height(), fill="red")
            self.temp_guides[1] = self.canvas.create_line(0, event.y, self.canvas.winfo_width(), event.y, fill="red")

    def _crosshair_release(self, event):
        if self.rect:
            return

        elif self.temp_guides and all(self.temp_guides):
            x, y = event.x, event.y

            (scale, offsetx, offsety) = self._compute_scale_and_offset(
                self.canvas.winfo_width(), self.canvas.winfo_height(),
                self.pil_image.width, self.pil_image.height
            )

            rel_x = int((x - offsetx) / scale)
            rel_y = int((y - offsety) / scale)

            self.guide_stack.append({
                "rel_coords": (rel_x, rel_y),
                "ids": self.temp_guides.copy()
            })

            self.temp_guides = []

            # If too many, remove oldest
            if len(self.guide_stack) > 2:
                old = self.guide_stack.pop(0)
                if "ids" in old:
                    for gid in old["ids"]:
                        self.canvas.delete(gid)

            # self._redraw_image()
            self._redraw_crosshairs()


    def _crosshair_remove(self, event):
        if self.guide_stack:
            last = self.guide_stack.pop()
            if "ids" in last:
                for gid in last["ids"]:
                    self.canvas.delete(gid)


    def _redraw_crosshairs(self):
        # First, delete any existing crosshair lines
        for guide in self.guide_stack:
            if "ids" in guide:
                for gid in guide["ids"]:
                    self.canvas.delete(gid)
            guide["ids"] = []  # Clear old ids

        # Then, re-create them and store new ids
        for guide in self.guide_stack:
            scale, offsetx, offsety = self._compute_scale_and_offset(
                self.canvas.winfo_width(), self.canvas.winfo_height(),
                self.pil_image.width, self.pil_image.height
            )

            rel_x, rel_y = guide["rel_coords"]
            canvas_x = rel_x * scale + offsetx
            canvas_y = rel_y * scale + offsety

            vline = self.canvas.create_line(canvas_x, 0, canvas_x, self.canvas.winfo_height(), fill="red")
            hline = self.canvas.create_line(0, canvas_y, self.canvas.winfo_width(), canvas_y, fill="red")
            guide["ids"] = [vline, hline]



    def _crop_using_crosshairs(self, event):
        if len(self.guide_stack) != 2:
            print("Need exactly 2 crosshairs to crop.")
            return

        # Get relative coordinates from guide stack
        rel_coords_1 = self.guide_stack[0]["rel_coords"]
        rel_coords_2 = self.guide_stack[1]["rel_coords"]

        # Convert to image coordinates
        x0 = int(min(rel_coords_1[0], rel_coords_2[0]))
        y0 = int(min(rel_coords_1[1], rel_coords_2[1]))
        x1 = int(max(rel_coords_1[0], rel_coords_2[0]))
        y1 = int(max(rel_coords_1[1], rel_coords_2[1]))

        # Ensure bounds are valid
        if (x1 > x0 and y1 > y0 and
            0 <= x0 < self.pil_image.width and
            0 <= y0 < self.pil_image.height and
            x1 <= self.pil_image.width and
            y1 <= self.pil_image.height):

            self.image_stack.append(self.pil_image.copy())  # Save for undo

            self.pil_image = self.pil_image.crop((x0, y0, x1, y1))
            self.guide_stack = []  # Clear guides
            self._zoom_fit()
            # self._redraw_image()
            # self._redraw_crosshairs()
        else:
            print("Invalid crop bounds.")









    def _toggle_edit_mode(self, event):
        editor_mode = self.editor_mode_var.get()
        self.editor_mode_var.set(not editor_mode)
        if editor_mode:
            self.deactivate_editor_mode()
        else:
            self.activate_editor_mode()

        print(self.editor_mode_var.get())
        # self.edit_mode = not self.edit_mode


    def level_image_from_line(self, x0, y0, x1, y1):
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
        self.rotate_image(angle_deg)

        self._zoom_fit()


    def reset_image(self):
        if self.original_image:
            self.image = self.original_image.copy()  # Restore the original image
            self.rotation_angle = 0  # Reset the rotation angle
            self.scale.set(1) # Reset the scale
            self.image_stack.clear()
            self.update_display_image()
            self.update_rotation_label()



    def _save(self, event):
        print("image_path")
        image_path = self.filepath.get()

        if self.pil_image and image_path:
            # Backup first
            base, ext = os.path.splitext(image_path)
            timestamp = int(time.time())
            backup_path = f"{base}.{timestamp}.bak{ext}"
            if not os.path.exists(backup_path):
                shutil.copy2(image_path, backup_path)
            else:
                print(f"Backup already exists at: {backup_path}")

            # Save (overwrite)
            self.pil_image.save(image_path)
            print(f"Image saved and original backed up at: {backup_path}")

        else:
            print("No image loaded or original path unknown.")


    # def open_image(self):
    #     filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])

    #     if filepath:
    #         self.set_image(filepath)

    # def update_rotation_label(self):
        # Normalize so 0° is upright, positive degrees are clockwise
        # angle = (-self.rotation_angle) % 360
        # self.rotation_label.config(text=f"Rotation: {angle:.1f}°")
    # def update_rotation_label(self):
    #     angle = (-self.rotation_angle) % 360
    #     step = self.rotation_steps[self.scale_index.get()]
    #     self.rotation_label.config(text=f"Rotation: {angle:.1f}°")
    #     self.scale_value_label.config(text=f"Step: {step}")


    # UI interations



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Simple responsive image viewer.")
    parser.add_argument("image", help="Path to the image file.")
    args = parser.parse_args()

    root = tk.Tk()
    app = EditorImageViewer(master=root, filepath=args.image)

    app.mainloop()

























    #     tk.Button(self.btn_frame, text="Save", command=self.save_image).pack(side="left")

    #     tk.Button(self.btn_frame, text="Reset", command=self.reset_image).pack(side="left")  # Reset to original

    #     self.rotation_label = tk.Label(self.btn_frame, text="Rotation: 0°")
    #     self.rotation_label.pack(side="left", padx=(10, 0))

    #     # Add scale control for finer adjustments
    #     self.scale_label = tk.Label(self.btn_frame, text="Scale:")
    #     self.scale_label.pack(side="left")
    #     # self.scale = tk.Scale(self.btn_frame, from_=0.1, to=2.5, resolution=0.5, orient="horizontal", showvalue=True)
    #     # self.scale.set(1)  # Default value set to 1
    #     # Custom rotation steps
    #     self.rotation_steps = [0.1, 0.2, 0.5, 1, 1.5, 2, 2.5]
    #     self.scale_index = tk.IntVar(value=self.rotation_steps.index(1))  # Start at 1

    #     self.scale_label = tk.Label(self.btn_frame, text="Scale:")
    #     self.scale_label.pack(side="left")

    #     self.scale = tk.Scale(
    #         self.btn_frame,
    #         from_=0,
    #         to=len(self.rotation_steps) - 1,
    #         variable=self.scale_index,
    #         orient="horizontal",
    #         showvalue=0,
    #         command=lambda val: self.update_rotation_label()
    #     )
    #     self.scale.pack(side="left")
    #     self.scale_value_label = tk.Label(self.btn_frame, text=f"Step: {self.rotation_steps[self.scale_index.get()]}")
    #     self.scale_value_label.pack(side="left", padx=(5, 0))

    #     self.image_stack = []  # Stack for undo
    #     self.image = None
    #     self.display_image = None
    #     self.tk_image = None
    #     self.start_x = self.start_y = self.rect = None
    #     self.rotation_angle = 0  # Cumulative rotation angle
    #     self.original_image = None  # Store the original image for reference







    #     # self.canvas.bind("<ButtonPress-1>", self.on_button_press)
    #     # self.canvas.bind("<B1-Motion>", self.on_move_press)
    #     # self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
    #     # self.root.bind("<Configure>", self.on_resize)
    #     # self.root.bind("<Control-z>", lambda e: self.undo_crop())
    #     # self.root.bind("<Control-MouseWheel>", self.on_ctrl_mousewheel)
    #     # self.root.bind("<Alt-MouseWheel>", self.on_alt_mousewheel)

    #     # # Bind Control and Alt click events
    #     # self.root.bind("<Control-Button-1>", self.on_ctrl_click)
    #     # self.root.bind("<Alt-Button-1>", self.on_alt_click)

    #     self.resize_after_id = None

    #     self.set_image()
    #     # self.after(100, self.set_image)



    # def update_display_image(self):
    #     if not self.image:
    #         return

    #     # Remove all previously drawn guides
    #     for guide in self.guide_stack:
    #         if "ids" in guide:
    #             for gid in guide["ids"]:
    #                 self.canvas.delete(gid)
    #             guide["ids"] = []



    #     # for guide in self.guide_stack:
    #     #     for gid in guide["ids"]:
    #     #         self.canvas.create_line(*guide["coords"][gid], fill="green", width=1)

    #     for guide in self.guide_stack:
    #         rel_x, rel_y = guide["rel_coords"]
    #         canvas_x = self.img_offset_x + rel_x / self.img_scale_x
    #         canvas_y = self.img_offset_y + rel_y / self.img_scale_y

    #         vline = self.canvas.create_line(canvas_x, 0, canvas_x, self.canvas.winfo_height(), fill="green")
    #         hline = self.canvas.create_line(0, canvas_y, self.canvas.winfo_width(), canvas_y, fill="green")
    #         guide["ids"] = [vline, hline]


    # # @property
    # # def img_offset_x(self):
    # #     return (self.canvas.winfo_width() - self.display_image.width) // 2

    # # @property
    # # def img_offset_y(self):
    # #     return (self.canvas.winfo_height() - self.display_image.height) // 2

    # # @property
    # # def img_scale_x(self):
    # #     return self.image.width / self.display_image.width

    # # @property
    # # def img_scale_y(self):
    #     # return self.image.height / self.display_image.height





    # def on_ctrl_mousewheel(self, event):
    #     if self.image:
    #         direction = 1 if event.delta > 0 else -1  # Scroll up → +, Scroll down → -
    #         # scale_factor = self.scale.get()  # Use the current scale value for finer rotation control
    #         scale_factor = self.rotation_steps[self.scale_index.get()]

    #         rotation_delta = direction * scale_factor  # Apply finer rotation
    #         self.rotate_image(rotation_delta)
    #     return "break"

    # def on_alt_mousewheel(self, event):
    #     if self.image:
    #         # scale_delta = 0.5 if event.delta > 0 else -0.5
    #         # new_scale = self.scale.get() + scale_delta
    #         # new_scale = max(0.1, min(new_scale, 2.5))  # Clamp the value between 0.1 and 2.5
    #         # self.scale.set(new_scale)
    #         direction = 1 if event.delta > 0 else -1
    #         new_index = self.scale_index.get() + direction
    #         new_index = max(0, min(new_index, len(self.rotation_steps) - 1))
    #         self.scale_index.set(new_index)
    #         self.update_rotation_label()
    #     return "break"


    # def on_alt_click(self, event):
    #     # Add a vertical and horizontal green line as guides
    #     if self.display_image:
    #         canvas_width = self.canvas.winfo_width()
    #         canvas_height = self.canvas.winfo_height()

    #         # Get the corresponding image position for the clicked location
    #         img_x = int((event.x - self.img_offset_x) * self.img_scale_x)
    #         img_y = int((event.y - self.img_offset_y) * self.img_scale_y)

    #         # Draw a green vertical line (x = img_x)
    #         self.canvas.create_line(event.x, 0, event.x, canvas_height, fill="green", dash=(4, 4))

    #         # Draw a green horizontal line (y = img_y)
    #         self.canvas.create_line(0, event.y, canvas_width, event.y, fill="green", dash=(4, 4))

    # def crop_image(self, x0, y0, x1, y1):
    #     if self.image and x0 != x1 and y0 != y1:
    #         img_x0 = int((x0 - self.img_offset_x) * self.img_scale_x)
    #         img_y0 = int((y0 - self.img_offset_y) * self.img_scale_y)
    #         img_x1 = int((x1 - self.img_offset_x) * self.img_scale_x)
    #         img_y1 = int((y1 - self.img_offset_y) * self.img_scale_y)

    #         img_x0, img_x1 = sorted((img_x0, img_x1))
    #         img_y0, img_y1 = sorted((img_y0, img_y1))

    #         self.image_stack.append(self.image.copy())
    #         self.image = self.image.crop((img_x0, img_y0, img_x1, img_y1))

    #         # Remove all guides
    #         for guide in self.guide_stack:
    #             for gid in guide["ids"]:
    #                 self.canvas.delete(gid)
    #         self.guide_stack.clear()

    #         self.update_display_image()


