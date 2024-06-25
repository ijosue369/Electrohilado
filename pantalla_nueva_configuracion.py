import tkinter as tk
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

        # Creación de widgets
        self.create_widgets()

        self.mainloop()

    def setup_layout(self):
        self.columnconfigure((0, 1), weight=1, uniform='a')
        self.rowconfigure((0, 1, 2, 3), weight=1, uniform='b')

    def create_widgets(self):
        Fondo(self)
        Titulo(self)
        self.parametros = Parametros(self)
        self.botones = Botones(self)

class Fondo(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent, fg_color='transparent', border_width=18, border_color=BLANCO,
                         width=1024, height=600)
        self.place(x=0, y=0)

class Titulo(ctk.CTkLabel):
    def __init__(self, parent):
        fuente = ctk.CTkFont(family='Arial Rounded MT Bold', size=54)
        super().__init__(master=parent, text='Párametros de operación', font=fuente, justify='center', text_color='#FFFFFF')
        self.grid(column=0, row=0, columnspan=2)

def entrada(parent, texto_etiqueta, unidades, variable, incremento, min_value, max_value):
    fuente = ctk.CTkFont(family='Arial Rounded MT Bold', size=30)
    frame = ctk.CTkFrame(master=parent, fg_color='transparent')

    frame.rowconfigure(0, weight=1)
    frame.columnconfigure((0, 1), weight=1, uniform='d')

    ctk.CTkLabel(frame, text=f'{texto_etiqueta}:', font=fuente, text_color='#ffffff').grid(row=0, column=0, padx=15, sticky='e')
    datos = ctk.CTkFrame(frame, fg_color='#ffffff', width=343, height=51)

    datos.columnconfigure(0, weight=1, uniform='e')
    datos.columnconfigure(1, weight=3, uniform='e')
    datos.columnconfigure((2, 3), weight=1, uniform='e')

    def incrementar():
        if texto_etiqueta == "Velocidad de inyección" and variable.get() == 0.1:
            variable.set(0.0)
        if variable.get() + incremento <= max_value:
            variable.set(round(variable.get() + incremento, 1))

    def decrementar():
        if texto_etiqueta == "Velocidad de inyección" and variable.get() == 0.2:
            variable.set(0.1)
        if variable.get() - incremento >= min_value:
            variable.set(round(variable.get() - incremento, 1))

    ctk.CTkButton(datos, text='-', font=fuente, fg_color=GRIS, text_color='#ffffff', command=decrementar).grid(row=0, column=0, padx=6, pady=6)
    ctk.CTkEntry(datos, font=fuente, text_color='#3E5164', fg_color='#ffffff', border_width=0, textvariable=variable, justify='right', state='disabled', width=100).grid(row=0, column=1, sticky='nwes')
    ctk.CTkButton(datos, text='+', font=fuente, fg_color=GRIS, text_color='#ffffff', command=incrementar).grid(row=0, column=2, padx=6, pady=6)
    fuente = ctk.CTkFont(family='Arial Rounded MT Bold', size=24)
    ctk.CTkLabel(datos, text=f'{unidades}', font=fuente, text_color=AZUL).grid(row=0, column=3, padx=3)

    datos.grid(row=0, column=1, padx=15, sticky='e')

    return frame

class Parametros(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent, fg_color='transparent')

        self.columnconfigure(0, weight=1)
        self.rowconfigure((0, 1, 2, 3), weight=1, uniform='c')

        # Inicialización de variables con sus valores mínimos
        self.velocidad_inyeccion = tk.DoubleVar(value=0.1)
        self.velocidad_colector = tk.DoubleVar(value=0.0)
        self.voltaje_operacion = tk.DoubleVar(value=3.0)
        self.temperatura_solucion = tk.DoubleVar(value=27.0)

        # Llamadas a la función entrada() con los parámetros específicos
        entrada(self, 'Velocidad de inyección', 'ml/h', self.velocidad_inyeccion, 100, 100, 1200).grid(row=0, column=0, sticky='n')
        entrada(self, 'Velocidad de colector', 'V', self.velocidad_colector, 250, 0, 1200).grid(row=1, column=0, sticky='n')
        entrada(self, 'Voltaje de operación', 'kV', self.voltaje_operacion, 1, 15, 18).grid(row=2, column=0, sticky='n')
        entrada(self, 'Temperatura de solución', '°C', self.temperatura_solucion, 3, 33, 66).grid(row=3, column=0, sticky='n')

        self.grid(column=0, row=1, columnspan=2, rowspan=2, sticky='nwes', padx=60)

class Botones(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent, fg_color='transparent')
        fuente = ctk.CTkFont(family='Arial Rounded MT Bold', size=27)
        
        self.iniciar_btn = ctk.CTkButton(self, width=390, height=90, text='Iniciar', font=fuente, corner_radius=60, fg_color=GRIS, border_width=6, border_color='#153250', text_color='#FFFFFF', command=self.iniciar)
        self.iniciar_btn.grid(column=1, row=3, sticky='n', padx = 30)
        
        self.guardar_btn = ctk.CTkButton(self, width=390, height=90, text='Guardar', font=fuente, corner_radius=60, fg_color=GRIS, border_width=0, border_color='#153250', text_color='#FFFFFF', command=self.guardar_parametros)
        self.guardar_btn.grid(column=0, row=3, sticky='n', padx = 30)

        self.grid(row=3, columnspan=2, padx=20, pady=20)

    def guardar_parametros(self):
        parametros = {
            "velocidad_inyeccion": self.master.parametros.velocidad_inyeccion.get(),
            "velocidad_colector": self.master.parametros.velocidad_colector.get(),
            "voltaje_operacion": self.master.parametros.voltaje_operacion.get(),
            "temperatura_solucion": self.master.parametros.temperatura_solucion.get()
        }
        with open('configuracion_temp.json', 'w') as file:
            json.dump(parametros, file, indent=4)

        self.master.destroy()
        import prueba_guardar
        prueba_guardar.App()

    def iniciar(self):
        parametros = {
            "velocidad_inyeccion": self.master.parametros.velocidad_inyeccion.get(),
            "velocidad_colector": self.master.parametros.velocidad_colector.get(),
            "voltaje_operacion": self.master.parametros.voltaje_operacion.get(),
            "temperatura_solucion": self.master.parametros.temperatura_solucion.get()
        }
        with open('configuracion_temp.json', 'w') as file:
            json.dump(parametros, file, indent=4)

        self.master.destroy()
        import pantalla_operacion
        pantalla_operacion.App("Temporal")

if __name__ == "__main__":
    App()
