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
from kivy.uix.spinner import Spinner
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.graphics import Color, Line, Ellipse, Rectangle

# Configuración de ventana para Android
Window.softinput_mode = 'resize'

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
            try: return json.load(f)
            except: return {}
    return {}

def guardar_datos(datos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

# --- WIDGET DE GRÁFICA PERSONALIZADA ---
class GraficaWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.puntos = []
        self.labels_x = []
        
    def dibujar(self, datos_puntos):
        self.canvas.after.clear()
        if not datos_puntos or len(datos_puntos) < 1:
            return

        with self.canvas.after:
            # Margen y dimensiones
            m = dp(40)
            ancho = self.width - (m * 2)
            alto = self.height - (m * 2)
            
            # Obtener escalas
            val_y = [p[1] for p in datos_puntos]
            min_y, max_y = min(val_y), max(val_y)
            rango_y = (max_y - min_y) if max_y != min_y else 10
            
            # Dibujar Cuadrícula de fondo
            Color(0.2, 0.2, 0.2, 1)
            for i in range(5):
                y_line = m + (alto / 4 * i)
                Line(points=[m, y_line, self.width - m, y_line], width=1)

            # Dibujar Línea de Progreso
            Color(0.12, 0.53, 0.9, 1) # Azul brillante
            puntos_canvas = []
            
            paso_x = ancho / (len(datos_puntos) - 1) if len(datos_puntos) > 1 else ancho
            
            for i, p in enumerate(datos_puntos):
                x = m + (i * paso_x)
                y = m + ((p[1] - min_y) / rango_y * alto)
                puntos_canvas.extend([x, y])
                
                # Dibujar punto (Ellipse)
                Color(1, 0.7, 0, 1) # Naranja/Oro
                Ellipse(pos=(x - dp(5), y - dp(5)), size=(dp(10), dp(10)))
                Color(0.12, 0.53, 0.9, 1)

            if len(puntos_canvas) > 2:
                Line(points=puntos_canvas, width=dp(2), joint='round')

# --- PANTALLAS ---

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20))
        box = BoxLayout(orientation='vertical', spacing=dp(12), size_hint=(None, None), width=dp(300), height=dp(580))
        box.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        
        box.add_widget(Label(text="MI PROGRESO", font_size=sp(28), bold=True, height=dp(60), size_hint_y=None))
        
        for dia in RUTINA.keys():
            btn = Button(text=dia, height=dp(60), size_hint_y=None, background_color=get_color_from_hex("#1E88E5"), bold=True)
            btn.bind(on_press=lambda x, d=dia: self.ir_a_entreno(d))
            box.add_widget(btn)
        
        box.add_widget(Label(size_hint_y=None, height=dp(10))) # Espacio
        
        btn_hist = Button(text="Ver Historial (Tablas)", height=dp(65), size_hint_y=None, background_color=get_color_from_hex("#43A047"), bold=True)
        btn_hist.bind(on_press=lambda x: setattr(self.manager, 'current', 'historial'))
        box.add_widget(btn_hist)
        
        btn_graph = Button(text="Gráficas de Avance 📈", height=dp(65), size_hint_y=None, background_color=get_color_from_hex("#FB8C00"), bold=True)
        btn_graph.bind(on_press=lambda x: setattr(self.manager, 'current', 'graficas'))
        box.add_widget(btn_graph)
        
        layout.add_widget(box)
        self.add_widget(layout)

    def ir_a_entreno(self, dia):
        self.manager.get_screen('entrenamiento').preparar_dia(dia)
        self.manager.current = 'entrenamiento'

class EntrenamientoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dia_actual = ""
        self.inputs = {}
        
        layout = BoxLayout(orientation='vertical', padding=dp(10))
        
        # Barra superior
        nav = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
        btn_atras = Button(text="<", size_hint_x=None, width=dp(50), background_color=get_color_from_hex("#E53935"))
        btn_atras.bind(on_press=self.volver)
        self.lbl_title = Label(text="Día", bold=True)
        btn_save = Button(text="Guardar", size_hint_x=None, width=dp(100), background_color=get_color_from_hex("#43A047"))
        btn_save.bind(on_press=self.guardar)
        nav.add_widget(btn_atras); nav.add_widget(self.lbl_title); nav.add_widget(btn_save)
        layout.add_widget(nav)

        self.scroll = ScrollView()
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(20), padding=[0,0,0,dp(400)])
        self.container.bind(minimum_height=self.container.setter('height'))
        self.scroll.add_widget(self.container)
        layout.add_widget(self.scroll)
        self.add_widget(layout)

    def preparar_dia(self, dia):
        self.dia_actual = dia
        self.lbl_title.text = dia.split(":")[0]
        self.container.clear_widgets()
        self.inputs = {}
        
        for ej in RUTINA[dia]:
            box_ej = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(110))
            box_ej.add_widget(Label(text=ej, bold=True, color=get_color_from_hex("#FFB300"), halign='left', text_size=(dp(280), None)))
            
            grid = BoxLayout(orientation='horizontal', spacing=dp(5))
            self.inputs[ej] = []
            for i in range(4):
                col = BoxLayout(orientation='vertical')
                in_p = TextInput(hint_text="Kg", multiline=False, input_filter='float', halign='center')
                in_r = TextInput(hint_text="R", multiline=False, input_filter='int', halign='center')
                col.add_widget(in_p); col.add_widget(in_r)
                grid.add_widget(col)
                self.inputs[ej].append((in_p, in_r))
            box_ej.add_widget(grid)
            self.container.add_widget(box_ej)

    def guardar(self, instance):
        datos = cargar_datos()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        datos[fecha] = {}
        for ej, series in self.inputs.items():
            datos[fecha][ej] = []
            for p, r in series:
                if p.text and r.text:
                    datos[fecha][ej].append({"peso": p.text, "reps": r.text})
        guardar_datos(datos)
        self.manager.current = 'menu'

    def volver(self, *args): self.manager.current = 'menu'

class GraficasScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # Selector de ejercicio
        self.todos_ejercicios = []
        for lista in RUTINA.values(): self.todos_ejercicios.extend(lista)
        
        self.spinner = Spinner(text="Selecciona Ejercicio", values=self.todos_ejercicios, size_hint_y=None, height=dp(50), background_color=get_color_from_hex("#1E88E5"))
        self.spinner.bind(text=self.actualizar_grafica)
        
        self.lbl_info = Label(text="Tendencia de Fuerza Estimada (1RM)", size_hint_y=None, height=dp(30), color=get_color_from_hex("#B0BEC5"))
        
        # El widget donde se dibuja
        self.canvas_grafica = GraficaWidget(size_hint_y=1)
        
        btn_back = Button(text="Volver", size_hint_y=None, height=dp(50), background_color=get_color_from_hex("#E53935"))
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        
        self.layout.add_widget(Label(text="EVOLUCIÓN", font_size=sp(22), bold=True, size_hint_y=None, height=dp(40)))
        self.layout.add_widget(self.spinner)
        self.layout.add_widget(self.lbl_info)
        self.layout.add_widget(self.canvas_grafica)
        self.layout.add_widget(btn_back)
        self.add_widget(self.layout)

    def actualizar_grafica(self, spinner, text):
        datos = cargar_datos()
        puntos_ejercicio = []
        
        # Extraer puntos (Fecha, 1RM Estimado)
        for fecha in sorted(datos.keys()):
            if text in datos[fecha]:
                max_1rm = 0
                for s in datos[fecha][text]:
                    p = float(s['peso'])
                    r = int(s['reps'])
                    if p > 0:
                        # Fórmula de Epley: 1RM = Peso * (1 + Reps/30)
                        uno_rm = p * (1 + r/30.0)
                        if uno_rm > max_1rm: max_1rm = uno_rm
                if max_1rm > 0:
                    puntos_ejercicio.append((fecha, max_1rm))
        
        if len(puntos_ejercicio) > 0:
            self.lbl_info.text = f"Progreso en {text}: {round(puntos_ejercicio[-1][1],1)} kg (1RM)"
            # Forzar el dibujo en el canvas
            self.canvas_grafica.dibujar(puntos_ejercicio)
        else:
            self.lbl_info.text = "Sin datos registrados para este ejercicio."

class HistorialScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(10))
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(15))
        self.container.bind(minimum_height=self.container.setter('height'))
        scroll = ScrollView(); scroll.add_widget(self.container)
        
        btn_v = Button(text="Volver", size_hint_y=None, height=dp(50), background_color=get_color_from_hex("#E53935"))
        btn_v.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        
        layout.add_widget(Label(text="HISTORIAL", font_size=sp(22), bold=True, size_hint_y=None, height=dp(40)))
        layout.add_widget(scroll); layout.add_widget(btn_v)
        self.add_widget(layout)

    def actualizar_historial(self):
        self.container.clear_widgets()
        datos = cargar_datos()
        for fecha in sorted(datos.keys(), reverse=True):
            box = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(10))
            box.add_widget(Label(text=f"FECHA: {fecha}", bold=True, color=get_color_from_hex("#4CAF50"), size_hint_y=None, height=dp(25), halign='left', text_size=(dp(300), None)))
            h = dp(30)
            for ej, series in datos[fecha].items():
                if series:
                    txt = " | ".join([f"{s['peso']}x{s['reps']}" for s in series])
                    l = Label(text=f"[b]{ej}[/b]: {txt}", markup=True, size_hint_y=None, height=dp(40), halign='left', text_size=(dp(300), None))
                    box.add_widget(l); h += dp(40)
            box.height = h
            self.container.add_widget(box)

class MainApp(App):
    def build(self):
        sm = ScreenManager()
        Window.clearcolor = get_color_from_hex("#121212")
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(EntrenamientoScreen(name='entrenamiento'))
        sm.add_widget(HistorialScreen(name='historial'))
        sm.add_widget(GraficasScreen(name='graficas'))
        return sm

if __name__ == '__main__':
    MainApp().run()
