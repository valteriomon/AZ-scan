import argparse
import os
from core.constants import APP_TITLE
import core.ui_styles  as styles
from core.postcard_view import PostcardView
from core.map_view import MapView
from core.stitcher_view import StitcherView
import tkinter as tk
from tkinter import PhotoImage, ttk
from tkinter import font
from dotenv import load_dotenv

def startup_window(root):
    # Clear the root window
    for widget in root.winfo_children():
        widget.destroy()

    # Set window options
    width, height = 600, 450
    root.title(APP_TITLE)
    root.state("normal")
    root.geometry(f"{width}x{height}")
    root.minsize(width, height)
    root.resizable(False, False)

    # Unbind any previous M/P bindings
    root.unbind("<m>")
    root.unbind("<M>")
    root.unbind("<p>")
    root.unbind("<P>")

    frame = ttk.Frame(root, padding=20)
    frame.pack(expand=True, fill='both')

    frame.columnconfigure(0, weight=1)

    # Postcard button
    postcard_button = ttk.Button(frame, text="Escaneo simple", command=lambda: launch_app(root, PostcardView))
    postcard_button.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 5), ipadx=10, ipady=10)
    postcard_button.configure(style="Big.TButton")
    postcard_button['underline'] = 0

    # Label for postcard
    ttk.Label(
        frame,
        text="Documentos tamaño carta o menor como postales y fotografías.",
        font=styles.FONT_MEDIUM
    ).grid(row=1, column=0, padx=10, pady=(0, 30))

    # Map button
    map_button = ttk.Button(frame, text="Cuadrícula", command=lambda: launch_app(root, MapView))
    map_button.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 5), ipadx=10, ipady=10)
    map_button.configure(style="Big.TButton")
    map_button['underline'] = 0

    # Label for map
    ttk.Label(
        frame,
        text="Documentos de gran formato como mapas o láminas.",
        font=styles.FONT_MEDIUM
    ).grid(row=3, column=0, padx=10, pady=(0, 0))

    separator = ttk.Separator(frame, orient='horizontal')
    separator.grid(row=4, column=0, sticky="ew", padx=10, pady=30)

    # Stitch button
    stitch_button = ttk.Button(frame, text="Unir cuadrícula", command=lambda: launch_app(root, StitcherView))
    stitch_button.grid(row=5, column=0, sticky="ew", padx=10, pady=(0, 5), ipadx=10, ipady=10)
    stitch_button.configure(style="Big.TButton")

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

def main():
    # Load the main .env file
    load_dotenv()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Launch application with specified environment.")
    parser.add_argument('--env', choices=['dev', 'prod'], default='dev', help='Set the environment (dev or prod).')
    parser.add_argument('--view', choices=['map', 'postcard', 'stitch'], help='Directly launch a specific view.')
    args = parser.parse_args()

    # Determine which environment to use
    env = args.env if args.env else os.getenv('ENVIRONMENT', 'prod')
    load_dotenv(dotenv_path=f".env.{env}", override=True)

    root = tk.Tk()
    icon = PhotoImage(file="assets/images/logo32.gif")
    root.iconphoto(True, icon)

    if env == 'dev':
        dev_geometry = os.getenv('TKINTER_GEOMETRY', '')
        root.geometry(dev_geometry)

    root.bind("<Escape>", lambda event: root.quit())

    # Set global default font for all ttk widgets
    style = ttk.Style()

    style.configure('.', font=styles.FONT_DEFAULT)
    style.configure("Big.TButton", font=styles.FONT_BIG, padding=10)
    style.configure("Zigzag.TButton", font=styles.MAP_PLUS_BUTTON, padding=5)
    style.configure("Big.TRadiobutton", font=styles.FONT_DEFAULT)
    style.configure("TEntry", font=styles.FONT_DEFAULT)

    # Set a global default font
    font.nametofont("TkDefaultFont").configure(family=styles.FONT_DEFAULT_FAMILY, size=styles.FONT_DEFAULT_SIZE)
    font.nametofont("TkTextFont").configure(family=styles.FONT_DEFAULT_FAMILY, size=styles.FONT_DEFAULT_SIZE)
    font.nametofont("TkMenuFont").configure(family=styles.FONT_DEFAULT_FAMILY, size=styles.FONT_DEFAULT_SIZE)
    font.nametofont("TkFixedFont").configure(family=styles.FONT_DEFAULT_FAMILY, size=styles.FONT_DEFAULT_SIZE)

    # Determine which window to launch
    if args.view == "map":
        launch_app(root, MapView)
    elif args.view == "postcard":
        launch_app(root, PostcardView)
    elif args.view == "stitch":
        launch_app(root, StitcherView)
    else:
        startup_window(root)

    root.mainloop()

if __name__ == "__main__":
    main()
