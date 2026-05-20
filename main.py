import json
import os
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex
from kivy.core.window import Window

RUTINA = {
    "Día 1: Pecho, Hombro y Tríceps": [
        "Press Plano con mancuernas", "Cruces de aperturas en polea alta", 
        "Pecho declinado máquina agarre neutro", "Press militar con mancuernas", 
        "Extensión de hombro en polea baja", "Tríceps empuje con barra corta en polea", 
        "Tríceps trasnuca polea baja"
    ],
    "Día 2: Espalda, Deltoides y Bíceps": [
        "Jalones al pecho en polea agarre prono", "Remo con polea agarre neutro", 
        "Jalones en polea agarre neutro cerrado", "Jalones a la cadera con polea alta", 
        "Extensiones para deltoides posterior polea", "Curl de bíceps con mancuerna"
    ],
    "Día 3: Pierna Completa": [
        "Prensa para cuadriceps", "Femoral en máquina", "Cuadriceps en máquina", 
        "Extensión de pierna", "Contracción de pierna", "Gemelos"
    ],
    "Día 4: Hombro, Bíceps y Tríceps": [
        "Press militar en máquina", "Extensiones frontales con polea baja", 
        "Curl de bíceps predicador con barra Z", "Curl de bíceps extendido con polea baja", 
        "Press francés", "Press cerrado para tríceps con barra Z"
    ]
}

DATA_FILE = "progreso_gym.json"

def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_datos(datos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Layout principal que se encarga de CENTRAR todo el bloque en la pantalla vertical
        layout_centrado = BoxLayout(orientation='vertical', padding=dp(20))
        
        # Contenedor interno con tamaño FIJO y EXACTO para tu celular (Ancho 320dp, Alto 520dp aprox)
        # Esto evita que Kivy estire las cosas al fondo de la pantalla.
        box_bloque = BoxLayout(
            orientation='vertical', 
            spacing=dp(16), 
            size_hint=(None, None), 
            width=dp(320), 
            height=dp(520)
        )
        # Código mágico para que quede en el centro exacto de la pantalla vertical
        box_bloque.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        
        # Título del menú centrado dentro del bloque
        box_bloque.add_widget(Label(
            text="REGISTRO GYM", 
            font_size=sp(32), 
            bold=True, 
            color=get_color_from_hex("#FFFFFF"),
            size_hint_y=None, 
            height=dp(70)
        ))
        
        # Crear los botones grandes tipo tarjeta para los días
        for dia in RUTINA.keys():
            btn = Button(
                text=dia, 
                size_hint=(1, None), 
                height=dp(68), # Altura cómoda para el dedo
                font_size=sp(16),
                bold=True,
                background_normal='',
                background_color=get_color_from_hex("#1E88E5") # Azul
            )
            btn.bind(on_press=self.ir_a_dia)
            box_bloque.add_widget(btn)
            
        # Botón del historial grande
        btn_historial = Button(
            text="Ver Historial / Avances", 
            size_hint=(1, None), 
            height=dp(72), 
            font_size=sp(18),
            bold=True,
            background_normal='',
            background_color=get_color_from_hex("#43A047") # Verde
        )
        btn_historial.bind(on_press=self.ir_a_historial)
        box_bloque.add_widget(btn_historial)
        
        # Añadimos el bloque centrado a la pantalla
        layout_centrado.add_widget(box_bloque)
        self.add_widget(layout_centrado)

    def ir_a_dia(self, instance):
        self.manager.get_screen('entrenamiento').preparar_dia(instance.text)
        self.manager.current = 'entrenamiento'
        
    def ir_a_historial(self, instance):
        self.manager.get_screen('historial').actualizar_historial()
        self.manager.current = 'historial'


class EntrenamientoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inputs = {}
        self.dia_actual = ""
        
        self.layout_principal = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))
        
        # Cabecera fija superior
        box_cabecera = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(55), spacing=dp(10))
        btn_volver = Button(text="< Volver", size_hint_x=0.3, font_size=sp(15), bold=True, background_color=get_color_from_hex("#E53935"))
        btn_volver.bind(on_press=self.volver_menu)
        
        self.lbl_titulo = Label(text="", font_size=sp(16), size_hint_x=0.4, bold=True, halign='center')
        
        btn_guardar = Button(text="Guardar", size_hint_x=0.3, font_size=sp(15), bold=True, background_color=get_color_from_hex("#43A047"))
        btn_guardar.bind(on_press=self.guardar_entrenamiento)
        
        box_cabecera.add_widget(btn_volver)
        box_cabecera.add_widget(self.lbl_titulo)
        box_cabecera.add_widget(btn_guardar)
        self.layout_principal.add_widget(box_cabecera)
        
        # Zona deslizable para los ejercicios en vertical
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(25))
        self.container.bind(minimum_height=self.container.setter('height'))
        
        self.scroll.add_widget(self.container)
        self.layout_principal.add_widget(self.scroll)
        
        self.add_widget(self.layout_principal)

    def preparar_dia(self, nombre_dia):
        self.container.clear_widgets()
        self.inputs = {}
        self.dia_actual = nombre_dia
        self.lbl_titulo.text = nombre_dia.split(":")[0]
        
        for ej in RUTINA[nombre_dia]:
            box_ej = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(130), spacing=dp(5))
            
            lbl_ej = Label(text=ej, font_size=sp(16), bold=True, color=get_color_from_hex("#FFB300"), size_hint_y=None, height=dp(30), halign='left', valign='middle')
            lbl_ej.bind(size=lbl_ej.setter('text_size'))
            box_ej.add_widget(lbl_ej)
            
            box_series = BoxLayout(orientation='horizontal', spacing=dp(8), size_hint_y=None, height=dp(90))
            self.inputs[ej] = []
            
            for i in range(4):
                box_serie = BoxLayout(orientation='vertical', spacing=dp(2))
                box_serie.add_widget(Label(text=f"S{i+1}", font_size=sp(12), bold=True, size_hint_y=None, height=dp(15)))
                
                in_peso = TextInput(hint_text="Kg", input_filter='float', multiline=False, font_size=sp(15), padding=[dp(4), dp(8), dp(4), dp(8)])
                in_reps = TextInput(hint_text="Reps", input_filter='int', multiline=False, font_size=sp(15), padding=[dp(4), dp(8), dp(4), dp(8)])
                
                box_serie.add_widget(in_peso)
                box_serie.add_widget(in_reps)
                box_series.add_widget(box_serie)
                
                self.inputs[ej].append((in_peso, in_reps))
                
            box_ej.add_widget(box_series)
            self.container.add_widget(box_ej)

    def guardar_entrenamiento(self, instance):
        datos = cargar_datos()
        fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        if fecha_hoy not in datos:
            datos[fecha_hoy] = {}
            
        for ej, series in self.inputs.items():
            datos[fecha_hoy][ej] = []
            for in_peso, in_reps in series:
                peso = in_peso.text.strip()
                reps = in_reps.text.strip()
                if peso or reps:
                    datos[fecha_hoy][ej].append({"peso": peso or "0", "reps": reps or "0"})
                    
        guardar_datos(datos)
        self.manager.current = 'menu'

    def volver_menu(self, instance):
        self.manager.current = 'menu'


class HistorialScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout_principal = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))
        
        self.scroll = ScrollView(size_hint=(1, 1))
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(15))
        self.container.bind(minimum_height=self.container.setter('height'))
        self.scroll.add_widget(self.container)
        
        self.layout_principal.add_widget(Label(text="Historial de Avances", font_size=sp(24), bold=True, size_hint_y=None, height=dp(50)))
        self.layout_principal.add_widget(self.scroll)
        
        btn_volver = Button(text="Volver al Menú", size_hint_y=None, height=dp(60), font_size=sp(16), bold=True, background_color=get_color_from_hex("#E53935"))
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        self.layout_principal.add_widget(btn_volver)
        
        self.add_widget(self.layout_principal)

    def actualizar_historial(self):
        self.container.clear_widgets()
        datos = cargar_datos()
        
        if not datos:
            self.container.add_widget(Label(text="No hay entrenamientos aún.", font_size=sp(16), size_hint_y=None, height=dp(40)))
        else:
            for fecha in sorted(datos.keys(), reverse=True):
                box_fecha = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
                lbl_fecha = Label(text=f"Fecha: {fecha}", font_size=sp(16), bold=True, color=get_color_from_hex("#FFB300"), size_hint_y=None, height=dp(30))
                box_fecha.add_widget(lbl_fecha)
                
                altura_bloque = dp(30)
                for ej, series in datos[fecha].items():
                    if series:
                        texto_series = ", ".join([f"S{i+1}: {s['peso']}kg x {s['reps']}" for i, s in enumerate(series)])
                        lbl_ej = Label(text=f"• {ej}\n  {texto_series}", font_size=sp(14), halign='left', size_hint_y=None, height=dp(45))
                        lbl_ej.bind(size=lbl_ej.setter('text_size'))
                        box_fecha.add_widget(lbl_ej)
                        altura_bloque += dp(45)
                
                box_fecha.height = altura_bloque
                self.container.add_widget(box_fecha)


class RutinaGymApp(App): # <-- Cambiado nombre interno para reiniciar la app
    def build(self):
        sm = ScreenManager()
        Window.clearcolor = get_color_from_hex("#121212")
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(EntrenamientoScreen(name='entrenamiento'))
        sm.add_widget(HistorialScreen(name='historial'))
        return sm

if __name__ == '__main__':
    RutinaGymApp().run()
