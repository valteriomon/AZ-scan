import tkinter as tk

class Ui:
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