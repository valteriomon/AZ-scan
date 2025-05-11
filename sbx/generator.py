import tkinter as tk
from tkinter import ttk

class UnionTool(ttk.Frame):
    def __init__(self, root, go_back_callback=None):
        super().__init__(root, padding=20)
        self.go_back_callback = go_back_callback
        self.pack(expand=True, fill='both')

        root.title("Herramientas de Unión")

        self.columnconfigure(0, weight=1)

        # Row 1: FOV selector
        row1 = ttk.Frame(self)
        row1.grid(row=0, column=0, sticky="ew", pady=5)
        row1.columnconfigure(1, weight=1)
        ttk.Label(row1, text="FOV").grid(row=0, column=0, sticky="w")
        self.fov_var = tk.IntVar(value="AUTO")
        fov_select = ttk.Combobox(row1, textvariable=self.fov_var, values=["AUTO"] + list(range(1, 11)), state="readonly")
        fov_select.grid(row=0, column=1, sticky="ew")

        # Row 2: Crear puntos de unión + estrategia dropdown
        row2 = ttk.Frame(self)
        row2.grid(row=1, column=0, sticky="ew", pady=5)
        row2.columnconfigure((0, 1, 2), weight=1)

        btn_union = ttk.Button(row2, text="Crear puntos de unión")
        btn_union.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        ttk.Label(row2, text="Estrategia:").grid(row=0, column=1, sticky="e", padx=(5, 5))
        self.strategy_var = tk.StringVar()
        strategy_select = ttk.Combobox(row2, textvariable=self.strategy_var,
                                       values=["Prealineada", "Cuadruples", "Petroff", "Hugin"],
                                       state="readonly")
        strategy_select.grid(row=0, column=2, sticky="ew")

        # Row 3: Crear archivo de proyecto vacío
        btn_empty = ttk.Button(self, text="Crear archivo de proyecto vacío")
        btn_empty.grid(row=2, column=0, sticky="ew", pady=5)

        # Row 4: Unir imágenes con Hugin
        btn_stitch = ttk.Button(self, text="Unir imágenes con Hugin")
        btn_stitch.grid(row=3, column=0, sticky="ew", pady=5)

        # Row 5: Abrir proyecto en Hugin
        btn_open = ttk.Button(self, text="Abrir proyecto en Hugin")
        btn_open.grid(row=4, column=0, sticky="ew", pady=5)

        # Optional: go back
        if self.go_back_callback:
            btn_back = ttk.Button(self, text="← Volver", command=self.go_back_callback)
            btn_back.grid(row=5, column=0, sticky="w", pady=(10, 0))
