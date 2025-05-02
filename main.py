import argparse
import os
from core.constants import APP_TITLE
from core.postcard_view import PostcardView
from core.map_view import MapView
import tkinter as tk
from tkinter import ttk
from tkinter import font
from dotenv import load_dotenv

BIG_FONT = ("Arial", 16)
# dark_mode = True  # Global flag
# style = None       # Global style object

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

    # apply_theme()

# def apply_theme():
#     global style, dark_mode
#     if not style:
#         style = ttk.Style()

#     if dark_mode:
#         root_bg = "#2e2e2e"
#         fg = "#ffffff"
#         button_bg = "#444444"
#     else:
#         root_bg = "#f0f0f0"
#         fg = "#000000"
#         button_bg = "#e0e0e0"

#     style.configure("TFrame", background=root_bg)
#     style.configure("TLabel", background=root_bg, foreground=fg)
    # style.configure("TButton", background=button_bg, foreground=fg)
    # style.configure("Big.TButton", font=BIG_FONT, padding=10, background=button_bg, foreground=fg)

# def toggle_dark_mode():
#     global dark_mode
#     dark_mode = not dark_mode
#     apply_theme()

# def setup_menu(root):
#     menubar = tk.Menu(root)
#     view_menu = tk.Menu(menubar, tearoff=0)
#     view_menu.add_command(label="Cambiar tema", command=toggle_dark_mode)
#     menubar.add_cascade(label="Opciones", menu=view_menu)
#     root.config(menu=menubar)

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
    root.geometry(os.getenv('TKINTER_GEOMETRY', ''))
    AppClass(root, go_back_callback=lambda: main_menu(root))
    # apply_theme()

def main():
    # Load the main .env file
    load_dotenv()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Launch application with specified environment.")
    parser.add_argument('--env', choices=['dev', 'prod'], default='dev', help='Set the environment (dev or prod).')
    parser.add_argument('--view', choices=['map', 'postcard'], help='Directly launch a specific view.')
    args = parser.parse_args()

    # Determine which environment to use
    # If an argument is passed, use it. Otherwise, use the ENVIRONMENT variable from .env
    env = args.env if args.env else os.getenv('ENVIRONMENT', 'dev')

    # Load the appropriate .env file based on the environment argument
    env_file = f".env.{env}"
    load_dotenv(dotenv_path=env_file, override=True)

    root = tk.Tk()
    root.geometry("400x300")
    root.minsize(400, 300)
    root.title(APP_TITLE)
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
    # style.configure("TFrame", background="#000000")
    if args.view == "map":
        launch_app(root, MapView)
    elif args.view == "postcard":
        launch_app(root, PostcardView)
    else:
        main_menu(root)
    # setup_menu(root)
    root.mainloop()

if __name__ == "__main__":
    main()
