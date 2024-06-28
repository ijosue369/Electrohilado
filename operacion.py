import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from estilos import *
from PIL import Image, ImageTk
import json
import RPi.GPIO as GPIO
import time
import threading
import board
import digitalio
import adafruit_max31865


#================================= Declaracion de pines =================================

#------------------------------ Sistema de inyeccion (SI) -------------------------------
SI_PIN_PASO = 20                
SI_PIN_DIRECCION = 21           
SI_PIN_SENSOR_LIMITE = 26       

#------------------------------ Sistema de coleccion (SC) -------------------------------
SC_PIN_ENTRADA_1 = 27
SC_PIN_ENTRADA_2 = 17
SC_PIN_HABILITACION = 22

#----------------------------- Sistema de temperatura (ST) ------------------------------
ST_TEMPERATURA_PIN = 4

#-------------------------------- Panel de control (PC) ---------------------------------
PC_PIN_ROJO = 11
PC_PIN_VERDE = 9
PC_PUERTA = 12

#================================ Configuracion de pines ================================
GPIO.setmode(GPIO.BCM)

#------------------------------ Sistema de inyeccion (SI) -------------------------------
GPIO.setup(SI_PIN_PASO, GPIO.OUT)
GPIO.setup(SI_PIN_DIRECCION, GPIO.OUT)
GPIO.setup(SI_PIN_SENSOR_LIMITE, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#------------------------------ Sistema de coleccion (SC) -------------------------------
GPIO.setup(SC_PIN_ENTRADA_1, GPIO.OUT)
GPIO.setup(SC_PIN_ENTRADA_2, GPIO.OUT)
GPIO.setup(SC_PIN_HABILITACION, GPIO.OUT)
GPIO.output(SC_PIN_ENTRADA_1, GPIO.HIGH)
GPIO.output(SC_PIN_ENTRADA_2, GPIO.LOW)

#----------------------------- Sistema de temperatura (ST) ------------------------------
GPIO.setup(ST_TEMPERATURA_PIN, GPIO.OUT)

#-------------------------------- Panel de control (PC) ---------------------------------
GPIO.setup(PC_PIN_ROJO, GPIO.OUT)
GPIO.setup(PC_PIN_VERDE, GPIO.OUT)
GPIO.output(PC_PIN_ROJO, GPIO.LOW)
GPIO.output(PC_PIN_VERDE, GPIO.LOW)

#=============================== Declaracion de variables ===============================

#------------------------------ Sistema de inyeccion (SI) -------------------------------
si_detener_motor_pasos = False
si_pasos_totales = 0
si_tiempo_micropaso = 0
si_aviso = True

#------------------------------ Sistema de coleccion (SC) -------------------------------
sc_pwm = GPIO.PWM(SC_PIN_HABILITACION, 100)
sc_pwm.start(0)
sc_aviso = True

#----------------------------- Sistema de temperatura (ST) ------------------------------
st_temperatura_histeresis = 0.12
st_temperatura_tiempo_inicio = time.time()
st_temperatura_medida = 0
st_spi = board.SPI() 
st_cs = digitalio.DigitalInOut(board.D5)
sensor = adafruit_max31865.MAX31865(st_spi, st_cs, wires=3)
st_aviso = True

#-------------------------------- Panel de control (PC) ---------------------------------
iu_pausado = False
iu_detener = False
estado = "OPERANDO"
pausa_event = threading.Event()


#=============================== Declaracion de funciones ===============================

#------------------------------ Sistema de inyeccion (SI) -------------------------------

def si_detener_motor_callback(channel):
    global si_detener_motor_pasos, si_pasos_totales, si_tiempo_micropaso
    
    print("(Sistema de inyeccion) La jeringa se ha vaciado")
    
    si_detener_motor_pasos = True

    GPIO.output(SI_PIN_DIRECCION, GPIO.LOW)
    for _ in range(si_pasos_totales):
        GPIO.output(SI_PIN_PASO, GPIO.HIGH)
        time.sleep(si_tiempo_micropaso)
        GPIO.output(SI_PIN_PASO, GPIO.LOW)
        time.sleep(si_tiempo_micropaso)
    
    si_pasos_totales = 0

def si_flujo_a_tiempo_micropaso(flujo_ml_h):
    flujo_ml_s = (flujo_ml_h * 1000) / 3600
    tiempo_micropaso = 4 / (2 * 13.248 * flujo_ml_s)
    return tiempo_micropaso

def si_controlar_motor_pasos(flujo_ml_h):
    global si_detener_motor_pasos, si_pasos_totales, si_tiempo_micropaso, si_aviso

    
    time.sleep(6)
    
    GPIO.output(SI_PIN_DIRECCION, GPIO.HIGH)
    
    si_tiempo_micropaso = si_flujo_a_tiempo_micropaso(flujo_ml_h)
    si_detener_motor_pasos = False

    try:
        while not si_detener_motor_pasos:
            
            if iu_detener:
                print("(Sistema de inyeccion) Apagando")
                GPIO.output(SI_PIN_PASO, GPIO.LOW)
                si_detener_motor_pasos = True
                break

            while iu_pausado:
                if si_aviso:
                    print("(Sistema de inyección) Pausado")
                    si_aviso = False
                pausa_event.wait()  # Espera hasta que se desactive la pausa
            si_aviso = True
            
            GPIO.output(SI_PIN_PASO, GPIO.HIGH)
            time.sleep(si_tiempo_micropaso)
            GPIO.output(SI_PIN_PASO, GPIO.LOW)
            time.sleep(si_tiempo_micropaso)
            si_pasos_totales += 1
            
            
    except KeyboardInterrupt:
        print("(Sistema de inyeccion) Apagando")
        GPIO.output(SI_PIN_PASO, GPIO.LOW)
        si_detener_motor_pasos = True

def si_iniciar_motor(flujo_ml_h, pausa_event):
    si_controlar_motor_pasos(flujo_ml_h)
    
GPIO.add_event_detect(SI_PIN_SENSOR_LIMITE, GPIO.FALLING, callback=si_detener_motor_callback, bouncetime=200)

#------------------------------ Sistema de coleccion (SC) -------------------------------

def sc_detener_motor():
    sc_pwm.ChangeDutyCycle(0)
    print("(Sistema de coleccion) Motor detenido")

def sc_controlar_motor(rpm, pausa_event):
    global sc_aviso
    velocidad = (rpm*25) / 500
    print(velocidad)
    try:
        while True:
            if iu_detener:
                print("(Sistema de coleccion) Apagando")
                sc_pwm.ChangeDutyCycle(0)
                break
            while iu_pausado:
                if sc_aviso:
                    print("(Sistema de coleccion) Pausado")
                    sc_aviso = False
                pausa_event.wait()  # Espera hasta que se desactive la pausa
            sc_aviso = True
            time.sleep(3)
            if rpm <= 500:
                sc_pwm.ChangeDutyCycle(velocidad)
                print(f"(Sistema de coleccion) Velocidad: {rpm:.2f}%")
            else:
                sc_detener_motor()
    except KeyboardInterrupt:
        print("(Sistema de coleccion) Apagando")
        sc_pwm.ChangeDutyCycle(0)

#----------------------------- Sistema de temperatura (ST) ------------------------------

def st_medir_temperatura():
    temperatura = sensor.temperature
    return temperatura

def st_controlar_temperatura(temperatura_solucion):
    global st_temperatura_medida, st_aviso

    try: 
        while True:
            if iu_detener:
                GPIO.output(ST_TEMPERATURA_PIN, GPIO.LOW)
                print("(Sistema de temperatura) Apagando")
                break

            st_temperatura_medida = st_medir_temperatura()
            tiempo_actual = time.time()
            tiempo_transcurrido = tiempo_actual - st_temperatura_tiempo_inicio
            print("(Sistema de temperatura) Temperatura: {0:0.2f}C".format(st_temperatura_medida),
                  f"Tiempo: {tiempo_transcurrido:.1f} segundos")

            if st_temperatura_medida < temperatura_solucion - st_temperatura_histeresis:
                GPIO.output(ST_TEMPERATURA_PIN, GPIO.HIGH)
            
            elif st_temperatura_medida > temperatura_solucion + st_temperatura_histeresis:
                GPIO.output(ST_TEMPERATURA_PIN, GPIO.LOW)
            
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("(Sistema de temperatura) Apagando")
        GPIO.output(ST_TEMPERATURA_PIN, GPIO.LOW)

#-------------------------------- Panel de control (PC) ---------------------------------
def pc_puerta_abierta(channel):
    if GPIO.input(PC_PUERTA) == GPIO.LOW:
        GPIO.output(PC_PIN_ROJO, GPIO.LOW)
        GPIO.output(PC_PIN_VERDE, GPIO.LOW)
        
    else:
        GPIO.output(PC_PIN_ESTROBOSCOPICA, GPIO.LOW)

GPIO.setup(PC_PUERTA, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(PC_PUERTA, GPIO.FALLING, callback=pc_puerta_abierta, bouncetime=200)

def pc_parpadeo(encendido, apagado):
    GPIO.output(apagado, GPIO.LOW)
    GPIO.output(encendido, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(encendido, GPIO.LOW)
    time.sleep(1)

def pc_encender_una_luz(encendido, apagado):
    GPIO.output(apagado, GPIO.LOW)
    GPIO.output(encendido, GPIO.HIGH)

def pc_encender_ambas_luces():
    GPIO.output(PC_PIN_VERDE, GPIO.HIGH)
    GPIO.output(PC_PIN_ROJO, GPIO.HIGH)


#------------------------------ Interfaz de usuario (IU) --------------------------------
def on_closing():
    GPIO.cleanup()

def iu_cargar_configuracion(nombre_configuracion):
    if nombre_configuracion == "Temporal":
        try:
            with open('configuracion_temp.json', 'r') as file:
                configuracion = json.load(file)
        except FileNotFoundError:
            configuracion = {
                "velocidad_inyeccion": 0.1,
                "velocidad_colector": 100.0,
                "voltaje_operacion": 3.0,
                "temperatura_solucion": 27.0
            }
        except json.JSONDecodeError:
            configuracion = {
                "velocidad_inyeccion": 0.1,
                "velocidad_colector": 100.0,
                "voltaje_operacion": 3.0,
                "temperatura_solucion": 27.0
            }
    else:
        try:
            with open('configuraciones.json', 'r') as file:
                data = json.load(file)
            configuracion = data.get(nombre_configuracion, {})
        except FileNotFoundError:
            configuracion = {
                "velocidad_inyeccion": 0.1,
                "velocidad_colector": 100.0,
                "voltaje_operacion": 3.0,
                "temperatura_solucion": 27.0
            }
        except json.JSONDecodeError:
            configuracion = {
                "velocidad_inyeccion": 0.1,
                "velocidad_colector": 100.0,
                "voltaje_operacion": 3.0,
                "temperatura_solucion": 27.0
            }
    return configuracion
#========================= Creacion de Interfaz de Usuario (IU) =========================

class App(ctk.CTk):
    def __init__(self, nombre_configuracion):
        global iu_pausado
        super().__init__(fg_color="#3E5164")
        self.title('Electrohilado')
        self.geometry('1024x600')
        self.resizable(False, False)

        nombre_configuracion
        configuracion = iu_cargar_configuracion(nombre_configuracion)
        
        print(configuracion)
        temperatura_solucion = configuracion.get('temperatura_solucion', 0)
        velocidad_colector = configuracion.get('velocidad_colector', 0)
        velocidad_inyeccion = configuracion.get('velocidad_inyeccion', 0)

        iu_pausado = False

        if temperatura_solucion > 0:
            sistema_temperatura = threading.Thread(target=st_controlar_temperatura, args=(configuracion['temperatura_solucion'],))
            sistema_temperatura.start()
            
        if velocidad_colector > 0:
            sistema_coleccion = threading.Thread(target=sc_controlar_motor, args=(configuracion['velocidad_colector'], pausa_event))

        if velocidad_inyeccion > 0:
            sistema_inyeccion = threading.Thread(target=si_iniciar_motor, args=(configuracion['velocidad_inyeccion'], pausa_event))

        if st_temperatura_medida <= temperatura_solucion:
            sistema_coleccion.start()
            sistema_inyeccion.start()

        # Layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure((0, 1), weight=1, uniform='a')

        # Widgets
        Fondo(self)
        Configuracion(self, configuracion)
        Estado(self, temperatura_solucion, velocidad_colector, velocidad_inyeccion, sistema_coleccion, sistema_inyeccion)
        
        self.mainloop()
        GPIO.cleanup()

def iu_mostrar_parametro(parent, texto_etiqueta, unidades, valor_inicial):
    fuente = ctk.CTkFont(family='Arial Rounded MT Bold', size=30)
    frame = ctk.CTkFrame(master=parent, fg_color='transparent')

    frame.rowconfigure((0, 1), weight=1, uniform='f')
    frame.columnconfigure(0, weight=1)

    ctk.CTkLabel(frame, text=f'{texto_etiqueta}:', font=fuente, text_color='#ffffff', width=390).grid(row=0, column=0, pady=15, sticky='s')
    
    datos = ctk.CTkFrame(frame, fg_color='#D9D9D9', width=390, height=100)
    datos.columnconfigure(0, weight=4, uniform='i')
    datos.columnconfigure(1, weight=1, uniform='i')
    
    entry = ctk.CTkEntry(datos, font=fuente, text_color='#3E5164', fg_color='transparent', border_width=0, justify='right', width=300, height=30, textvariable=tk.DoubleVar(value=valor_inicial), state='disabled')
    entry.grid(row=0, column=0, sticky='ns')
    ctk.CTkLabel(datos, text=f'{unidades}', font=fuente, text_color="#3E5164", width=60).grid(row=0, column=1, sticky='n')
    
    datos.grid(row=1, column=0, pady=15, sticky='nwes')
        
    return frame

class Fondo(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent, fg_color='transparent', border_width=18, border_color="#FFFFFF", width=1024, height=600)
        self.place(x=0, y=0, relwidth=1, relheight=1)

class Configuracion(ctk.CTkFrame):
    def __init__(self, parent, configuracion):
        super().__init__(master=parent, fg_color='transparent')
        self.columnconfigure((0, 1), weight=1, uniform='g')
        self.rowconfigure((0, 1), weight=1, uniform='h')
        
        iu_mostrar_parametro(self, 'Velocidad de inyeccion', 'ml/h', configuracion.get('velocidad_inyeccion', 0.1)).grid(row=0, column=0, padx=15)
        iu_mostrar_parametro(self, 'Voltaje de operacion', 'kV', configuracion.get('voltaje_operacion', 3.0)).grid(row=0, column=1, padx=15)
        iu_mostrar_parametro(self, 'Velocidad de colector', 'rpm', configuracion.get('velocidad_colector', 100.0)).grid(row=1, column=0, padx=15)
        iu_mostrar_parametro(self, 'Temperatura de solucion', 'C', configuracion.get('temperatura_solucion', 27.0)).grid(row=1, column=1, padx=15)
        self.grid(column=0, row=0, sticky='s', pady=18)

class Estado(ctk.CTkFrame):
    def __init__(self, parent, temperatura_solucion, velocidad_colector, velocidad_inyeccion, sistema_coleccion, sistema_inyeccion):
        fuente = ctk.CTkFont(family='Arial Rounded MT Bold', size=27)
        super().__init__(master=parent, fg_color='transparent')
        self.columnconfigure((0, 1), weight=1, uniform='c')
        self.rowconfigure((0, 1), weight=1, uniform='d')

        fuente = ctk.CTkFont(family='Arial Rounded MT Bold', size=45)
        label_estado = ctk.CTkLabel(self, width=490, height=90, text=estado, font=fuente, justify='center', text_color='#FFFFFF', fg_color='#769E6C', corner_radius=15)
        label_estado.grid(row=0, column=0, columnspan=2, pady=10)

        fuente = ctk.CTkFont(family='Arial Rounded MT Bold', size=27)
        
        boton_pausar = ctk.CTkButton(self, width=360, height=90, text='Pausar', font=fuente, corner_radius=60, fg_color='#C2BE71', border_color='#A19C4A', border_width=3, text_color='#FFFFFF', 
                                     command=lambda: self.pausar(boton_pausar, label_estado))
        boton_pausar.grid(row=1, column=0, padx=24)
        
        boton_detener = ctk.CTkButton(self, width=360, height=90, text='Terminar', font=fuente, corner_radius=60, fg_color='#B25A68', border_color='#903846', border_width=3, text_color='#FFFFFF',
                                     command=lambda: self.detener(boton_pausar, boton_detener, label_estado))
        boton_detener.grid(row=1, column=1, padx=24)
        
        self.grid(row=1, column=0, sticky='n', pady=30)

    def pausar(self, boton, estado):
        global iu_pausado

        if boton.cget("text") == "Pausar":
            iu_pausado = True
            boton.configure(text="Reanudar")
        else:
            iu_pausado = False
            pausa_event.set()
            boton.configure(text="Pausar")

    def detener(self, boton_p, boton_d, estado):
        global iu_detener

        iu_detener = True

        print(threading.active_count())

        estado.configure(text="Electrohilado terminado")   

        messagebox.showinfo("Electrohilado terminado")
        self.master.destroy()
        GPIO.cleanup()
        import pantalla_inicio
        pantalla_inicio.App()     

if __name__ == "__main__":
    app = App("Temporal")