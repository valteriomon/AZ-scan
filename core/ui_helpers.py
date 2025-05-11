import tkinter as tk
from tkinter import ttk

class Ui:
    class Tooltip:
        def __init__(self, widget, text):
            self.widget = widget
            self.text = text
            self.tip = None
            widget.bind("<Enter>", self.show_tip)
            widget.bind("<Leave>", self.hide_tip)

        def show_tip(self, event):
            if self.tip or not self.text:
                return
            x, y, _, _ = self.widget.bbox("insert") or (0, 0, 0, 0)
            x += self.widget.winfo_rootx()
            y += self.widget.winfo_rooty()
            self.tip = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.geometry(f"+{x}+{y}")
            label = tk.Label(tw, text=self.text, background="lightyellow", relief=tk.SOLID, borderwidth=1)
            label.pack()

        def hide_tip(self, event):
            if self.tip:
                self.tip.destroy()
                self.tip = None

    @staticmethod
    def prompt(parent, title=None, message="Are you sure?"):
        result = {"answer": None}

        def on_yes(event=None):
            result["answer"] = True
            dialog.destroy()

        def on_no(event=None):
            result["answer"] = False
            dialog.destroy()

        dialog = tk.Toplevel(parent)
        dialog.transient(parent)        # Keep on top of parent
        dialog.grab_set()               # Make modal
        dialog.resizable(False, False)

        # Inherit title and icon if not set
        if title is None:
            title = parent.title()
        dialog.title(title)

        # Padding frame for consistent layout
        content = tk.Frame(dialog, padx=20, pady=15)
        content.pack()

        # Message label
        tk.Label(content, text=message, wraplength=300, justify="center").pack(pady=(0, 10))

        # Button row
        btn_frame = tk.Frame(content)
        btn_frame.pack()

        yes_btn = ttk.Button(btn_frame, text="Sí", width=10, command=on_yes)
        yes_btn.pack(side="left", padx=10)
        no_btn = ttk.Button(btn_frame, text="No", width=10, command=on_no)
        no_btn.pack(side="right", padx=10)

        # Keyboard bindings
        dialog.bind("<Return>", on_yes)
        dialog.bind("<Escape>", on_no)

        # Focus and layout
        dialog.update_idletasks()
        dialog.minsize(dialog.winfo_reqwidth(), dialog.winfo_reqheight())
        dialog.geometry(f"+{parent.winfo_rootx() + 100}+{parent.winfo_rooty() + 100}")
        yes_btn.focus_set()

        dialog.wait_window()
        return result["answer"]

    def menu(root, menu_options=[]):
        menu_bar = tk.Menu(root)
        options_menu = tk.Menu(menu_bar, tearoff=tk.OFF)

        for option in menu_options:
            options_menu.add_command(label=option["label"], command=option["command"])

        if menu_options:
            options_menu.add_separator()
        options_menu.add_command(label="Salir", command=root.quit)

        menu_bar.add_cascade(label="Opciones", menu=options_menu)
        root.config(menu=menu_bar)