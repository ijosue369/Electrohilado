import tkinter as tk
import customtkinter as ctk
from estilos import *
from PIL import Image, ImageTk
import json
import RPi.GPIO as GPIO
import time

# Definir los pines GPIO para STEP, DIR y SENSOR_LIMITE
STEP = 20  # pin STEP del controlador A4988 conectado al GPIO 20
DIR = 21   # pin DIR del controlador A4988 conectado al GPIO 21
SENSOR_LIMITE = 26 # pin del sensor de limite conectado al GPIO 26

# Configurar GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)  # Desactivar advertencias de GPIO
try:
    GPIO.setup(STEP, GPIO.OUT)
    GPIO.setup(DIR, GPIO.OUT)
    GPIO.setup(SENSOR_LIMITE, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # configurar como entrada con pull-up
except RuntimeError as e:
    print(f"Error al configurar GPIO: {e}")
    exit(1)  # Salir del programa si hay un error en la configuracion

# Variables globales
detener_motor = False
pasos_totales = 0
tiempo_micropaso = 0  # Inicializar tiempo_micropaso

# Funcion para controlar el motor de manera continua
def controlar_motor_pasos(flujo_ml_h):
    global detener_motor, pasos_totales, tiempo_micropaso
    
    # Calcular el tiempo de micropaso basado en el flujo actual
    tiempo_micropaso = flujo_a_tiempo_micropaso(flujo_ml_h)
    
    # Configurar la direccion del motor (ejemplo: girar en un sentido)
    GPIO.output(DIR, GPIO.HIGH)
    
    detener_motor = False
    
    try:
        while not detener_motor:
            GPIO.output(STEP, GPIO.HIGH)
            time.sleep(tiempo_micropaso)
            GPIO.output(STEP, GPIO.LOW)
            time.sleep(tiempo_micropaso)
            pasos_totales += 1
            
    except KeyboardInterrupt:
        GPIO.output(STEP, GPIO.LOW)
        detener_motor = True

# Funcion de devolucion de llamada para detener el motor
def detener_motor_callback(channel):
    global detener_motor, pasos_totales, tiempo_micropaso
    print("Se detecto una interrupcion en el sensor de limite!")
    detener_motor = True  # Detener el motor

    # Giro en sentido contrario
    GPIO.output(DIR, GPIO.LOW)
    for _ in range(pasos_totales):
        GPIO.output(STEP, GPIO.HIGH)
        time.sleep(tiempo_micropaso)
        GPIO.output(STEP, GPIO.LOW)
        time.sleep(tiempo_micropaso)
    
    pasos_totales = 0  # Reiniciar contador de pasos

# Funcion para convertir ml/h a mm3/s y calcular el tiempo de micropaso
def flujo_a_tiempo_micropaso(flujo_ml_h):
    flujo_ml_s = (flujo_ml_h * 1000) / 3600
    tiempo_micropaso = 4 / (2 * 13.248 * flujo_ml_s)
    return tiempo_micropaso

# Configurar la interrupcion para el sensor de limite
GPIO.add_event_detect(SENSOR_LIMITE, GPIO.FALLING, callback=detener_motor_callback, bouncetime=200)

# Funcion para iniciar el motor
def iniciar_motor(flujo_ml_h):
    controlar_motor_pasos(flujo_ml_h)

class App(ctk.CTk):
    def __init__(self, config_name):
        # Configuración de la ventana
        super().__init__(fg_color=AZUL)
        self.title('Electrohilado')
        self.geometry('1024x600')
        self.resizable(False, False)

        self.config_name = config_name
        self.cargar_configuracion()

        # Layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure((0, 1), weight=1, uniform='a')

        # Widgets
        self.fondo = Fondo(self)
        self.configuracion = Configuracion(self)
        self.estado = Estado(self)
        
        # Iniciar motor automaticamente con la velocidad de inyeccion configurada
        self.after(1000, self.iniciar_motor_automaticamente)  # Iniciar motor despues de 1 segundo

        self.mainloop()

    def cargar_configuracion(self):
        if self.config_name == "Temporal":
            try:
                with open('configuracion_temp.json', 'r') as file:
                    data = json.load(file)
                self.config = data.get(self.config_name, {})
            except FileNotFoundError:
                self.config = {
                    "velocidad_inyeccion": 0.1,
                    "velocidad_colector": 100.0,
                    "voltaje_operacion": 3.0,
                    "temperatura_solucion": 20.0
                }
            except json.JSONDecodeError:
                self.config = {
                    "velocidad_inyeccion": 0.1,
                    "velocidad_colector": 100.0,
                    "voltaje_operacion": 3.0,
                    "temperatura_solucion": 20.0
                }
        else:
            try:
                with open('configuraciones.json', 'r') as file:
                    data = json.load(file)
                self.config = data.get(self.config_name, {})
            except FileNotFoundError:
                self.config = {
                    "velocidad_inyeccion": 0.1,
                    "velocidad_colector": 100.0,
                    "voltaje_operacion": 3.0,
                    "temperatura_solucion": 20.0
                }
            except json.JSONDecodeError:
                self.config = {
                    "velocidad_inyeccion": 0.1,
                    "velocidad_colector": 100.0,
                    "voltaje_operacion": 3.0,
                    "temperatura_solucion": 20.0
                }
        print(data)
        
    def iniciar_motor_automaticamente(self):
        flujo_ml_h = self.configuracion.velocidad_inyeccion_var.get()
        iniciar_motor(flujo_ml_h)

class Fondo(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent, fg_color='transparent', border_width=18, border_color=BLANCO, width=1024, height=600)
        self.place(x=0, y=0, relwidth=1, relheight=1)

def entrada(parent, texto_etiqueta, unidades, textvariable):
    fuente = ctk.CTkFont(family='Arial Rounded MT Bold', size=30)
    frame = ctk.CTkFrame(master=parent, fg_color='transparent')

    frame.rowconfigure((0, 1), weight=1, uniform='f')
    frame.columnconfigure(0, weight=1)

    ctk.CTkLabel(frame, text=f'{texto_etiqueta}:', font=fuente, text_color='#ffffff', width=390).grid(row=0, column=0, pady=15, sticky='s')
    
    datos = ctk.CTkFrame(frame, fg_color='#D9D9D9', width=390, height=100)
    datos.columnconfigure(0, weight=4, uniform='i')
    datos.columnconfigure(1, weight=1, uniform='i')
    
    fuente = ctk.CTkFont(family='Arial Rounded MT Bold', size=30)
    ctk.CTkEntry(datos, font=fuente, text_color='#3E5164', fg_color='transparent', border_width=0, justify='right', width=300, height=30, textvariable=textvariable, state='disabled').grid(row=0, column=0, sticky = 'ns')
    ctk.CTkLabel(datos, text=f'{unidades}', font=fuente, text_color=AZUL, width=60).grid(row=0, column=1, sticky='n')
    datos.grid(row=1, column=0, pady=15, sticky='nwes')
        
    return frame

class Configuracion(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent, fg_color='transparent')
        self.columnconfigure((0, 1), weight=1, uniform='g')
        self.rowconfigure((0, 1), weight=1, uniform='h')
        
        entrada(self, 'Velocidad de inyección', 'ml/h', self.configuracion.velocidad_inyeccion_var.get()).grid(row=0, column=0, padx=15)
        entrada(self, 'Voltaje de operación', 'kV', tk.DoubleVar(value=3.0)).grid(row=0, column=1, padx=15)
        entrada(self, 'Velocidad de colector', 'rpm', tk.DoubleVar(value=3.0)).grid(row=1, column=0, padx=15)
        entrada(self, 'Temperatura de solución', '°C', tk.DoubleVar(value=3.0)).grid(row=1, column=1, padx=15)
        self.grid(column=0, row=0, sticky='s', pady= 18)

class Estado(ctk.CTkFrame):
    def __init__(self, parent):
        fuente = ctk.CTkFont(family='Arial Rounded MT Bold', size=27)
        super().__init__(master=parent, fg_color='transparent')
        self.columnconfigure((0, 1), weight=1, uniform='c')
        self.rowconfigure((0, 1), weight=1, uniform='d')

        fuente = ctk.CTkFont(family='Arial Rounded MT Bold', size=45)
        ctk.CTkLabel(self, width=490, height=90, text='OPERANDO', font=fuente, justify='center', text_color='#FFFFFF', fg_color='#769E6C', corner_radius=15).grid(row=0, column=0, columnspan=2, pady=10)

        fuente = ctk.CTkFont(family='Arial Rounded MT Bold', size=27)
        ctk.CTkButton(self, width=360, height=90, text='Pausar', font=fuente, corner_radius=60, fg_color='#C2BE71', border_color='#A19C4A', border_width=3, text_color='#FFFFFF').grid(row=1, column=0, padx=24)
        ctk.CTkButton(self, width=360, height=90, text='Detener', font=fuente, corner_radius=60, fg_color='#B25A68', border_color='#903846', border_width=3, text_color='#FFFFFF').grid(row=1, column=1, padx=24)
        self.grid(row=1, column=0, sticky='n', pady=30)

if __name__ == "__main__":
    config_name = "Cuatro"
    App(config_name=config_name)
