import os
import tkinter as tk
from core.image_viewer import ImageViewer
import numpy as np

class ImageEditor(ImageViewer):
    def __init__(self, master, filepath, status_bar_enabled=True):
        super().__init__(master, filepath, status_bar_enabled)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Image editor.")
    parser.add_argument("image", help="Path to the image file.")
    args = parser.parse_args()

    root = tk.Tk()
    app = ImageEditor(master=root, filepath=args.image)

    app.mainloop()