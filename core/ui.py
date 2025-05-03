import tkinter as tk

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
    def prompt(title="Confirm", message="Are you sure?"):
        result = {"answer": None}

        def on_yes():
            result["answer"] = True
            dialog.destroy()

        def on_no():
            result["answer"] = False
            dialog.destroy()

        dialog = tk.Toplevel()
        dialog.title(title)
        dialog.geometry("300x100")
        dialog.grab_set()  # Make modal

        tk.Label(dialog, text=message, pady=10).pack()

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Yes", width=10, command=on_yes).pack(side="left", padx=10)
        tk.Button(btn_frame, text="No", width=10, command=on_no).pack(side="right", padx=10)

        dialog.wait_window()
        return result["answer"]
