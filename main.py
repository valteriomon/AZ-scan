import argparse
import os
from core.constants import APP_TITLE
from core.styles import *
from core.postcard_view import PostcardView
from core.map_view import MapView
import tkinter as tk
from tkinter import ttk
from tkinter import font
from dotenv import load_dotenv

style = None       # Global style object

def startup_window(root):
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
    root.resizable(True, True)

    if AppClass == PostcardView:
        pass
    elif AppClass == MapView:
        pass

    root.geometry("")
    AppClass(root, go_back_callback=lambda: startup_window(root))

    if os.getenv('ENVIRONMENT') == 'dev':
        geom = os.getenv('TKINTER_GEOMETRY', '')
        root.geometry(geom)

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
    env_file = f".env.{env}"
    load_dotenv(dotenv_path=env_file, override=True)

    root = tk.Tk()
    root.geometry("400x300")
    root.resizable(False, False)
    root.title(APP_TITLE)
    root.iconbitmap("assets/images/logo32.ico")

    root.bind("<Escape>", lambda event: root.quit())

    # # Set a global default font
    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(family="Segoe UI", size=11)
    default_font = font.nametofont("TkTextFont")
    default_font.configure(family="Segoe UI", size=11)


    # Set global default font for all ttk widgets
    style = ttk.Style()
    style.configure('.', font=("Segoe UI", 11))
    style.configure("Big.TRadiobutton", font=("Segoe UI", 11))
    style.configure("Zigzag.TButton", font=("Segoe UI", 18), padding=5)
    # style.configure('my.TMenubutton', font=('Segoe UI', 16))

    # # Optional: Configure other default fonts too
    # font.nametofont("TkTextFont").configure(family="Segoe UI", size=11)
    # font.nametofont("TkFixedFont").configure(family="Segoe UI", size=11)
    # font.nametofont("TkMenuFont").configure(family="Segoe UI", size=11)


    # style = ttk.Style()
    style.configure("Big.TButton", font=BIG_FONT, padding=10)
    style.configure("TEntry", font=("Segoe UI", 11))

    # style.configure("TFrame", background="#000000")
    if args.view == "map":
        launch_app(root, MapView)
    elif args.view == "postcard":
        launch_app(root, PostcardView)
    else:
        startup_window(root)

    root.mainloop()

if __name__ == "__main__":
    main()
