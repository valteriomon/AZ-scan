- Maps scanning



Postales
- Escanear
- Nombrar
- Dar opciones: Ingresar código (elegir de lista o ingresar nuevo), ingresar número (libre) o elegir siguiente, o pasar B, elegir lado.

P1: Si hubo escaneo anterior
Scan anterior?
Si es A, B?
Else Numero que sigue
Else otro, usar mismo código
Else otro código, existe o nuevo?
Skip B side

rotate option

Add a "crop" option

refresh dropdown with saved prefix

make font bigger

naps2 scan
preview scan

save scan
    # def save_config():
    #     pass

    # def get_last_scan():
    #     pass
    def save_last_state(self):
        pass


    # def save_prefix(self, new_prefix, index):
    #     pass
    # #     if new_prefix not in self.prefixes:
    # #         self.prefixes.append(new_prefix)
    # #         with open(App.CONFIG_FILE, "w") as f:
    # #             yaml.dump({"prefixes": prefixes}, f)
    # def sync_prefix(self, value):

    #     self.save_last_state()
        # self.text_input_var.set(value)

    def scan_action(self):
        # prefix =
        # if self.postcard_prefix.get() not in self.prefixes:
        #     self.save_prefix(self.postcard_prefix.get())
        pass
    #     value = self.text_input_var.get().strip()
    #     if value and value not in self.prefixes:
    #         prefixes.append(value)
    #         save_dropdown_option(value)

    #         # Update dropdown menu with new value
    #         menu = self.dropdown["menu"]
    #         menu.add_command(label=value, command=lambda v=value: self.dropdown_var.set(v))
    #     print(f"Scan triggered with value: {value}")
    #     self.scan_button.config(text="Scanning...")

def save_dropdown_option(new_option):
    options = load_dropdown_options()
    if new_option not in options:
        options.append(new_option)
        with open(YAML_FILE, "w") as f:
            yaml.dump({"dropdown_options": options}, f)

    def scan_action(self):
        value = self.text_input_var.get().strip()
        if value and value not in dropdown_values:
            dropdown_values.append(value)
            save_dropdown_option(value)

            # Update dropdown menu with new value
            menu = self.dropdown["menu"]
            menu.add_command(label=value, command=lambda v=value: self.dropdown_var.set(v))
        print(f"Scan triggered with value: {value}")
        self.scan_button.config(text="Scanning...")

