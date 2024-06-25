import tkinter as tk
import customtkinter as ctk
from estilos import *
from PIL import Image, ImageTk

class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=AZUL)
        self.title('Electrohilado')
        self.geometry('1024x600')
        self.resizable(False, False)

        self.setup_layout()
        self.create_widgets()

        self.mainloop()

    def setup_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure((0, 1, 2), weight=1, uniform='a')

    def create_widgets(self):
        Fondo(self)
        Titulo(self)
        Logo(self)
        Boton(self)

class Fondo(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent, fg_color='transparent', border_width=17, border_color=BLANCO, width=1024, height=600)
        self.place(x=0, y=0)

class Logo(ctk.CTkLabel):
    def __init__(self, parent):
        logotipo = ctk.CTkImage(
            light_image=Image.open('C:/Users/Josue/Desktop/kinter-complete/Electrohilado/logo_upiita.png'),
            dark_image=Image.open('C:/Users/Josue/Desktop/kinter-complete/Electrohilado/logo_upiita.png'),
            size=(135, 135))

        super().__init__(master=parent, text=' ', image=logotipo, justify='center', text_color='#FFFFFF')
        self.grid(column=0, row=0, sticky='s')

class Titulo(ctk.CTkLabel):
    def __init__(self, parent):
        fuente = ctk.CTkFont(family='Arial Rounded MT Bold', size=72)
        super().__init__(master=parent, text='MÁQUINA DE\nELECTROHILADO', font=fuente, justify='center',
                         text_color='#FFFFFF', bg_color='transparent')
        self.grid(column=0, row=1)

class Boton(ctk.CTkButton):
    def __init__(self, parent):
        fuente = ctk.CTkFont(family='Arial Rounded MT Bold', size=45)
        super().__init__(master=parent, width=394, height=119, text='INICIAR', font=fuente, corner_radius=60,
                         fg_color=GRIS, border_width=6, border_color='#153250', text_color='#FFFFFF', command=self.iniciar)
        self.grid(column=0, row=2)

    def iniciar(self):
        self.master.destroy()
        import pantalla_parametros
        pantalla_parametros.App()

if __name__ == "__main__":
    App()
