import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from estilos import *
import json
from PIL import Image, ImageTk

class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=AZUL)
        self.title('Electrohilado')
        self.geometry('1024x600')
        self.resizable(False, False)

        # Configuración del layout
        self.setup_layout()
        
        # Creación de widgets
        self.create_widgets()
        self.cargar_configuraciones()
        
        self.mainloop()

    def setup_layout(self):
        self.columnconfigure((0, 1), weight=1, uniform='a')
        self.rowconfigure((0, 1, 2, 3), weight=1, uniform='b')

    def create_widgets(self):
        Fondo(self)
        Titulo(self)
        self.boton = Boton(self)
        self.opciones = Opciones(self)

    def cargar_configuraciones(self):
        try:
            with open('configuraciones.json', 'r') as file:
                self.configuraciones = json.load(file)
                self.opciones.actualizar_botones(self.configuraciones)
        except FileNotFoundError:
            self.configuraciones = {}

class Fondo(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent, fg_color='transparent', border_width=18, border_color=BLANCO,
                         width=1024, height=600)
        self.place(x=0, y=0)

class Titulo(ctk.CTkLabel):
    def __init__(self, parent):
        fuente = ctk.CTkFont(family='Arial Rounded MT Bold', size=54)
        super().__init__(master=parent, text='Elegir parámetros', font=fuente, justify='center', text_color='#FFFFFF')
        self.grid(column=0, row=0, columnspan=2)

class Boton(ctk.CTkButton):
    def __init__(self, parent):
        fuente = ctk.CTkFont(family='Arial Rounded MT Bold', size=27)
        super().__init__(master=parent, width=460, height=90, text='Nueva configuración',
                         font=fuente, corner_radius=60, fg_color=GRIS, border_width=6,
                         border_color='#153250', text_color='#FFFFFF', command=self.nueva_configuracion)
        self.grid(column=1, row=2, sticky='nw')

    def nueva_configuracion(self):
        self.master.destroy()
        import pantalla_nueva_configuracion
        pantalla_nueva_configuracion.App()

class Opciones(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        fuente = ctk.CTkFont(family='Arial Rounded MT Bold', size=27)
        super().__init__(master=parent, width=338, height=371, fg_color='transparent',
                         scrollbar_button_color=GRIS, scrollbar_fg_color='#153250')

        self.botones_configuraciones = []
        self.grid(column=0, row=1, rowspan=3)

    def actualizar_botones(self, configuraciones):
        for boton in self.botones_configuraciones:
            boton.destroy()
        
        self.botones_configuraciones = []
        fuente = ctk.CTkFont(family='Arial Rounded MT Bold', size=27)
        for nombre, _ in configuraciones.items():
            boton_config = ctk.CTkButton(self, width=263, height=79, corner_radius=60, font=fuente,
                                        fg_color=GRIS, text_color='#FFFFFF', text=nombre,
                                        command=lambda nombre=nombre: self.cargar_configuracion(self._parent_frame, nombre))
            boton_config.pack(pady=10)
            self.botones_configuraciones.append(boton_config)

    def cargar_configuracion(self, padre, nombre):
        padre.master.destroy()
        import pantalla_configuracion_existente
        pantalla_configuracion_existente.App(nombre)
    
if __name__ == "__main__":
    App()
