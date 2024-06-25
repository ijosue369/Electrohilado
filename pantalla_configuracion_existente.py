import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from estilos import *
from PIL import Image, ImageTk
import json

class App(ctk.CTk):
    def __init__(self, config_name=None):
        # Configuración de la ventana
        super().__init__(fg_color=AZUL)
        self.title('Electrohilado')
        self.geometry('1024x600')
        self.resizable(False, False)

        # Layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=2)
        self.rowconfigure(2, weight=1)

        # Widgets
        Fondo(self)
        Titulo(self)
        self.parametros_frame = Parametros(self, config_name)
        Botones(self, config_name)
        
        self.mainloop()

class Fondo(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent, fg_color='transparent', border_width=18, border_color=BLANCO, width=1024, height=600)
        self.place(x=0, y=0, relwidth=1, relheight=1)

class Titulo(ctk.CTkLabel):
    def __init__(self, parent):
        fuente = ctk.CTkFont(family='Arial Rounded MT Bold', size=54)
        super().__init__(master=parent, text='Parámetros de operación', font=fuente, justify='center', text_color='#FFFFFF')
        self.grid(column=0, row=0)

def entrada(parent, texto_etiqueta, unidades, variable):
    fuente = ctk.CTkFont(family='Arial Rounded MT Bold', size=30)
    frame = ctk.CTkFrame(master=parent, fg_color='transparent')

    frame.rowconfigure(0, weight=1)
    frame.columnconfigure((0, 1), weight=1, uniform='y')

    ctk.CTkLabel(frame, text=f'{texto_etiqueta}:', font=fuente, text_color='#ffffff').grid(row=0, column=0, padx=15, sticky='e')
    datos = ctk.CTkFrame(frame, fg_color='#D9D9D9', width=343, height=51)
       
    datos.columnconfigure(0, weight=5, uniform='e')
    datos.columnconfigure(1, weight=1, uniform='e')
    
    ctk.CTkEntry(datos, font=fuente, width=343, text_color='#3E5164', fg_color='transparent', border_width=0, textvariable=variable, justify='right', state='disabled').grid(row=0, column=0, sticky='nwes')
    ctk.CTkLabel(datos, text=f'{unidades}', font=fuente, text_color=AZUL).grid(row=0, column=1, ipadx=3, sticky='nwes')

    datos.grid(row=0, column=1, ipadx=15, sticky='nwes')
    
    return frame

class Parametros(ctk.CTkFrame):
    def __init__(self, parent, config_name):
        super().__init__(master=parent, fg_color='transparent')
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure((0, 1, 2, 3), weight=1, uniform='z')

        # Cargar configuraciones JSON
        try:
            with open('configuraciones.json', 'r') as file:
                data = json.load(file)
            
            config = data.get(config_name, {})
            
            self.velocidad_inyeccion = tk.DoubleVar(value=config.get("velocidad_inyeccion", 0.1))
            self.velocidad_colector = tk.DoubleVar(value=config.get("velocidad_colector", 100.0))
            self.voltaje_operacion = tk.DoubleVar(value=config.get("voltaje_operacion", 3.0))
            self.temperatura_solucion = tk.DoubleVar(value=config.get("temperatura_solucion", 20.0))

        except FileNotFoundError:
            print("Error: El archivo JSON no se encontró.")
            self.velocidad_inyeccion = tk.DoubleVar(value=0.1)
            self.velocidad_colector = tk.DoubleVar(value=100.0)
            self.voltaje_operacion = tk.DoubleVar(value=3.0)
            self.temperatura_solucion = tk.DoubleVar(value=20.0)
        except json.JSONDecodeError:
            print("Error: El archivo JSON está mal formado.")
            self.velocidad_inyeccion = tk.DoubleVar(value=0.1)
            self.velocidad_colector = tk.DoubleVar(value=100.0)
            self.voltaje_operacion = tk.DoubleVar(value=3.0)
            self.temperatura_solucion = tk.DoubleVar(value=20.0)

        entrada(self, 'Velocidad de inyección', 'ml/h', self.velocidad_inyeccion).grid(row=0, column=0, sticky='n')
        entrada(self, 'Velocidad de colector', 'rpm', self.velocidad_colector).grid(row=1, column=0, sticky='n')
        entrada(self, 'Voltaje de operación', 'kV', self.voltaje_operacion).grid(row=2, column=0, sticky='n')
        entrada(self, 'Temperatura de solución', '°C', self.temperatura_solucion).grid(row=3, column=0, sticky='n')

        self.grid(column=0, row=1, sticky='ns')

class Botones(ctk.CTkFrame):
    def __init__(self, parent, config_name):
        super().__init__(master=parent, fg_color='transparent')
        
        fuente = ctk.CTkFont(family='Arial Rounded MT Bold', size=36)
        
        self.columnconfigure((0, 1), weight=1, uniform='c')
        self.rowconfigure(0, weight=1, uniform='d')

        ctk.CTkButton(self, width=390, height=120, text='Borrar\nconfiguración', font=fuente, corner_radius=60, fg_color='#B25A68', border_color='#903846', border_width=6, text_color='#FFFFFF', command=lambda: self.confirmar_borrado(config_name)).grid(row=0, column=0, padx = 12)
        ctk.CTkButton(self, width=390, height=120, text='Iniciar', font=fuente, corner_radius=60, fg_color='#798796', border_color='#172B40', border_width=6, text_color='#FFFFFF', command=lambda: self.iniciar(config_name)).grid(row=0, column=1, padx = 12)
        
        self.grid(row=2, column=0, sticky='n')

    def confirmar_borrado(self, config_name):
        respuesta = messagebox.askyesno("Confirmar", f"¿Deseas borrar la configuración '{config_name}'?")
        if respuesta:
            self.borrar_configuracion(config_name)

    def borrar_configuracion(self, config_name):
        try:
            with open('configuraciones.json', 'r') as file:
                data = json.load(file)
            
            if config_name in data:
                del data[config_name]
                with open('configuraciones.json', 'w') as file:
                    json.dump(data, file, indent=4)
                print(f"Configuración '{config_name}' borrada exitosamente.")
            else:
                print(f"Configuración '{config_name}' no encontrada.")
        except FileNotFoundError:
            print("Error: El archivo JSON no se encontró.")
        except json.JSONDecodeError:
            print("Error: El archivo JSON está mal formado.")
        except Exception as e:
            print(f"Error al borrar configuración: {e}")

        self.master.destroy()
        import pantalla_parametros
        pantalla_parametros.App()

    def iniciar(self, config_name):
        self.master.destroy()
        import pantalla_operacion
        pantalla_operacion.App(config_name)
            
if __name__ == "__main__":
    # Asumir que el nombre de configuración se pasa desde Opciones
    config_name = "Cuatro"  # Puedes cambiar esto por la configuración deseada
    App(config_name=config_name)
