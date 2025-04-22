from core.postcard_view import PostcardView
from core.map_view import MapView
import tkinter as tk
from tkinter import ttk
from tkinter import font

BIG_FONT = ("Arial", 16)

def main_menu(root):
    # Clear the root window
    for widget in root.winfo_children():
        widget.destroy()

    # Unbind any previous M/P bindings
    root.unbind("<m>")
    root.unbind("<M>")
    root.unbind("<p>")
    root.unbind("<P>")

    frame = ttk.Frame(root, padding=20)
    frame.pack(expand=True, fill='both')

    ttk.Label(frame, text="Escanear...", font=BIG_FONT).pack(pady=20)

    # Map button
    map_button = ttk.Button(frame, text="Mapa", width=30, command=lambda: launch_app(root, MapView))
    map_button.pack(pady=10, ipadx=10, ipady=10)
    map_button.configure(style="Big.TButton")
    map_button['underline'] = 0  # Underline 'M'

    # Postcard button
    postcard_button = ttk.Button(frame, text="Postales u otros", width=30, command=lambda: launch_app(root, PostcardView))
    postcard_button.pack(pady=10, ipadx=10, ipady=10)
    postcard_button.configure(style="Big.TButton")
    postcard_button['underline'] = 0  # Underline 'P'

    # Key bindings
    root.bind("<m>", lambda event: launch_app(root, MapView))
    root.bind("<M>", lambda event: launch_app(root, MapView))
    root.bind("<p>", lambda event: launch_app(root, PostcardView))
    root.bind("<P>", lambda event: launch_app(root, PostcardView))

def launch_app(root, AppClass):
    # Clear the window
    for widget in root.winfo_children():
        widget.destroy()

    # Unbind shortcuts once we move to the new view
    root.unbind("<m>")
    root.unbind("<M>")
    root.unbind("<p>")
    root.unbind("<P>")

    # if AppClass == PostcardView:
    #     root.geometry("800x600")
    # elif AppClass == MapView:
    #     root.geometry("1000x700")
    root.geometry("")
    AppClass(root)

def main():
    root = tk.Tk()
    root.geometry("400x300")
    root.minsize(400, 300)
    root.title("AZ-scan - Escáner de Archivos")
    root.iconbitmap("assets/images/logo32.ico")
    root.bind("<Escape>", lambda event: root.quit())

    # # Set a global default font
    # default_font = font.nametofont("TkDefaultFont")
    # default_font.configure(family="Segoe UI", size=12)

    # # Optional: Configure other default fonts too
    # font.nametofont("TkTextFont").configure(family="Segoe UI", size=12)
    # font.nametofont("TkFixedFont").configure(family="Segoe UI", size=12)
    # font.nametofont("TkMenuFont").configure(family="Segoe UI", size=12)

    style = ttk.Style()
    style.configure("Big.TButton", font=BIG_FONT, padding=10)

    main_menu(root)
    root.mainloop()

if __name__ == "__main__":
    main()
