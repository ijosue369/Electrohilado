import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from estilos import *
import json
from PIL import Image, ImageTk

class App(ctk.CTk):
    def __init__(self):
        # Configuración de la ventana
        super().__init__(fg_color=AZUL)
        self.title('Electrohilado')
        self.geometry('1024x600')
        self.resizable(False, False)

        # Configuración del layout
        self.setup_layout()

        # Crear widgets
        self.create_widgets()

        self.mainloop()

    def setup_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure((0, 1, 2), weight=1, uniform='a')

    def create_widgets(self):
        Fondo(self)
        Titulo(self)
        self.entrada = Entrada(self)
        self.boton = Boton(self)

class Fondo(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent, fg_color='transparent', border_width=18, border_color=BLANCO, width=1024, height=600)
        self.place(x=0, y=0, relwidth=1, relheight=1)

class Titulo(ctk.CTkLabel):
    def __init__(self, parent):
        fuente = ctk.CTkFont(family='Arial Rounded MT Bold', size=48)
        super().__init__(master=parent, text='Guardar configuración de\nparámetros', font=fuente, justify='center', text_color='#FFFFFF')
        self.grid(column=0, row=0, padx=20, pady=20)

class Entrada(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent, fg_color='transparent')
        self.columnconfigure(0, weight=1)
        self.rowconfigure((0, 1), weight=1, uniform='b')

        self.nombre_configuracion = tk.StringVar()
        fuente = ctk.CTkFont(family='Arial Rounded MT Bold', size=30)

        ctk.CTkLabel(self, text='Nombre de configuración:', font=fuente, text_color='#ffffff').grid(row=0, column=0, padx=20, pady=10, sticky='ns')
        self.entry_nombre = ctk.CTkEntry(self, font=fuente, width=470, height=50, text_color='#3E5164', fg_color='#ffffff', border_width=0, textvariable=self.nombre_configuracion, justify='center')
        self.entry_nombre.grid(row=1, column=0, padx=20, pady=10, sticky='n')

        self.grid(row=1, column=0, sticky='nwes', padx=20, pady=20)

class Boton(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent, fg_color='transparent')
        fuente = ctk.CTkFont(family='Arial Rounded MT Bold', size=27)

        self.guardar_btn = ctk.CTkButton(self, width=390, height=90, text='Guardar', font=fuente, corner_radius=60, fg_color=GRIS, border_width=0, border_color='#153250', text_color='#FFFFFF', command=self.guardar_configuracion)
        self.guardar_btn.grid(column=0, row=0, pady=20)

        self.grid(column=0, row=2, pady=(0, 40), sticky='n')

    def guardar_configuracion(self):
        nombre_configuracion = self.master.entrada.nombre_configuracion.get()
        if nombre_configuracion:
            try:
                with open('configuracion_temp.json', 'r') as temp_file:
                    parametros = json.load(temp_file)

                configuraciones = {}
                try:
                    with open('configuraciones.json', 'r') as file:
                        configuraciones = json.load(file)
                except FileNotFoundError:
                    pass

                configuraciones[nombre_configuracion] = parametros

                with open('configuraciones.json', 'w') as file:
                    json.dump(configuraciones, file, indent=4)

                # Mostrar mensaje de éxito
                messagebox.showinfo("Éxito", f"Configuración '{nombre_configuracion}' guardada exitosamente.")
                self.master.destroy()
                import pantalla_parametros
                pantalla_parametros.App()

            except Exception as e:
                print(f"Error al guardar la configuración: {e}")
        else:
            messagebox.showwarning("Advertencia", "Por favor, ingresa un nombre para la configuración.")

if __name__ == "__main__":
    App()