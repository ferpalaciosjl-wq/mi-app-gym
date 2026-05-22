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
from kivy.clock import Clock
from kivy.graphics import Color, Line, Ellipse

# Forzar a Android a redimensionar la app cuando el teclado suba
Window.softinput_mode = 'resize'

DATA_FILE = "progreso_gym.json"
CONFIG_FILE = "config_rutina.json"

RUTINA_PREDETERMINADA = {
    "Dia 1: Pecho, Hombro y Triceps": [
        "Press Plano con mancuernas", "Cruces de aperturas en polea alta", 
        "Pecho declinado maquina agarre neutro", "Press militar con mancuernas", 
        "Extension de hombro en polea baja", "Triceps empuje con barra corta", 
        "Triceps trasnuca polea baja"
    ],
    "Dia 2: Espalda, Deltoides y Biceps": [
        "Jalones al pecho agarre prono", "Remo con polea agarre neutro", 
        "Jalones en polea agarre cerrado", "Jalones a la cadera polea alta", 
        "Extensiones deltoides posterior", "Curl de biceps con mancuerna"
    ],
    "Dia 3: Pierna Completa": [
        "Prensa para cuadriceps", "Femoral en maquina", "Cuadriceps en maquina", 
        "Extension de pierna", "Contraccion de pierna", "Gemelos"
    ],
    "Dia 4: Hombro, Biceps y Triceps": [
        "Press militar en maquina", "Extensiones frontales polea baja", 
        "Curl de biceps barra Z", "Curl de biceps polea baja", 
        "Press frances", "Press cerrado con barra Z"
    ]
}

def get_base_path():
    try:
        from android.storage import app_storage_path
        return app_storage_path()
    except:
        return "."

def get_file_path(filename):
    return os.path.join(get_base_path(), filename)

def cargar_rutinas():
    path = get_file_path(CONFIG_FILE)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return RUTINA_PREDETERMINADA
    return RUTINA_PREDETERMINADA

def guardar_rutinas(rutinas):
    with open(get_file_path(CONFIG_FILE), "w", encoding="utf-8") as f:
        json.dump(rutinas, f, indent=4, ensure_ascii=False)

def cargar_datos():
    path = get_file_path(DATA_FILE)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return {}
    return {}

def guardar_datos(datos):
    with open(get_file_path(DATA_FILE), "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)


# --- CANVAS NATIVO PARA TABLAS Y GRÁFICOS DE AVANCE ---
class GraficaWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.datos_pendientes = []

    def dibujar(self, datos_puntos):
        self.datos_pendientes = datos_puntos
        Clock.schedule_once(self._ejecutar_dibujo, 0.1)
        
    def _ejecutar_dibujo(self, dt):
        self.canvas.after.clear()
        if not self.datos_pendientes or len(self.datos_pendientes) < 1:
            return
        with self.canvas.after:
            m = dp(40)
            ancho = self.width - (m * 2)
            alto = self.height - (m * 2)
            val_y = [p[1] for p in self.datos_pendientes]
            min_y, max_y = min(val_y), max(val_y)
            rango_y = (max_y - min_y) if max_y != min_y else 10
            
            # Líneas guía horizontales (Escala de la tabla)
            Color(0.2, 0.2, 0.2, 1)
            for i in range(5):
                y_line = m + (alto / 4 * i)
                Line(points=[m, y_line, self.width - m, y_line], width=1)
                
            # Trazado de la línea de progreso (Azul Premium)
            Color(0.12, 0.53, 0.9, 1)
            puntos_canvas = []
            paso_x = ancho / (len(self.datos_pendientes) - 1) if len(self.datos_pendientes) > 1 else ancho
            
            for i, p in enumerate(self.datos_pendientes):
                x = m + (i * paso_x)
                y = m + ((p[1] - min_y) / rango_y * alto)
                puntos_canvas.extend([x, y])
                
                # Nodos/Puntos de fuerza (Naranja brillante)
                Color(1, 0.55, 0, 1)
                Ellipse(pos=(x - dp(5), y - dp(5)), size=(dp(10), dp(10)))
                Color(0.12, 0.53, 0.9, 1)
                
            if len(puntos_canvas) > 2:
                Line(points=puntos_canvas, width=dp(3), joint='round')


# --- PANTALLAS DE LA INTERFAZ ---

class MenuScreen(Screen):
    def on_enter(self, *args):
        self.layout_principal.clear_widgets()
        self.inicializar_menu()
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout_principal = BoxLayout(orientation='vertical', padding=dp(20))
        self.add_widget(self.layout_principal)
        
    def inicializar_menu(self):
        rutinas = cargar_rutinas()
        box = BoxLayout(orientation='vertical', spacing=dp(12), size_hint=(None, None), width=dp(310), height=dp(600))
        box.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        
        box.add_widget(Label(text="TRAINING TRACKER", font_size=sp(24), bold=True, height=dp(50), size_hint_y=None, color=get_color_from_hex("#FFB300")))
        
        # Botones dinámicos de las Rutinas
        for dia in rutinas.keys():
            btn = Button(text=dia, height=dp(55), size_hint_y=None, background_color=get_color_from_hex("#1E88E5"), bold=True, font_size=sp(15))
            btn.bind(on_press=lambda x, d=dia: self.ir_a_entreno(d))
            box.add_widget(btn)
            
        box.add_widget(Label(size_hint_y=None, height=dp(10)))
        
        # Botón Historial
        btn_hist = Button(text="[ Ver Historial / Tablas ]", height=dp(58), size_hint_y=None, background_color=get_color_from_hex("#43A047"), bold=True, font_size=sp(16))
        btn_hist.bind(on_press=lambda x: setattr(self.manager, 'current', 'historial'))
        box.add_widget(btn_hist)
        
        # Botón Gráficas
        btn_graph = Button(text="[ Ver Graficas de Avance ]", height=dp(58), size_hint_y=None, background_color=get_color_from_hex("#FB8C00"), bold=True, font_size=sp(16))
        btn_graph.bind(on_press=lambda x: setattr(self.manager, 'current', 'graficas'))
        box.add_widget(btn_graph)
        
        # Botón Configurar/Editar
        btn_edit_rutina = Button(text="[ Configurar / Editar Rutinas ]", height=dp(58), size_hint_y=None, background_color=get_color_from_hex("#7E57C2"), bold=True, font_size=sp(16))
        btn_edit_rutina.bind(on_press=lambda x: setattr(self.manager, 'current', 'editar_rutina'))
        box.add_widget(btn_edit_rutina)
        
        self.layout_principal.add_widget(box)

    def ir_a_entreno(self, dia):
        self.manager.get_screen('entrenamiento').preparar_dia(dia)
        self.manager.current = 'entrenamiento'


class EntrenamientoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dia_actual = ""
        self.inputs = {}
        layout = BoxLayout(orientation='vertical', padding=dp(10))
        
        nav = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
        btn_atras = Button(text="< Volver", size_hint_x=None, width=dp(95), background_color=get_color_from_hex("#E53935"), bold=True)
        btn_atras.bind(on_press=self.volver)
        self.lbl_title = Label(text="Entrenamiento", bold=True, font_size=sp(16))
        btn_save = Button(text="GUARDAR", size_hint_x=None, width=dp(100), background_color=get_color_from_hex("#43A047"), bold=True)
        btn_save.bind(on_press=self.guardar)
        nav.add_widget(btn_atras); nav.add_widget(self.lbl_title); nav.add_widget(btn_save)
        layout.add_widget(nav)
        
        self.scroll = ScrollView()
        # Colchón inferior masivo de dp(450) para que los renglones suban por completo y el teclado no tape nada
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(22), padding=[0, 0, 0, dp(450)])
        self.container.bind(minimum_height=self.container.setter('height'))
        self.scroll.add_widget(self.container); layout.add_widget(self.scroll)
        self.add_widget(layout)

    def preparar_dia(self, dia):
        rutinas = cargar_rutinas(); self.dia_actual = dia; self.lbl_title.text = dia
        self.container.clear_widgets(); self.inputs = {}
        ejercicios = rutinas.get(dia, [])
        
        if not ejercicios:
            self.container.add_widget(Label(text="-- No hay ejercicios guardados --", halign='center', size_hint_y=None, height=dp(100)))
            return
            
        for ej in ejercicios:
            box_ej = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(115))
            box_ej.add_widget(Label(text=f"> {ej}", bold=True, color=get_color_from_hex("#FFB300"), halign='left', text_size=(dp(290), None), font_size=sp(15)))
            
            grid = BoxLayout(orientation='horizontal', spacing=dp(6))
            self.inputs[ej] = []
            for i in range(4):
                col = BoxLayout(orientation='vertical', spacing=dp(2))
                in_p = TextInput(hint_text="Kg", multiline=False, input_filter='float', halign='center', font_size=sp(14))
                in_r = TextInput(hint_text="Reps", multiline=False, input_filter='int', halign='center', font_size=sp(14))
                col.add_widget(in_p); col.add_widget(in_r); grid.add_widget(col)
                self.inputs[ej].append((in_p, in_r))
                
            box_ej.add_widget(grid); self.container.add_widget(box_ej)

    def guardar(self, instance):
        datos = cargar_datos(); fecha = datetime.now().strftime("%Y-%m-%d %H:%M"); datos[fecha] = {}
        hay_datos = False
        for ej, series in self.inputs.items():
            datos[fecha][ej] = []
            for p, r in series:
                if p.text.strip() and r.text.strip():
                    datos[fecha][ej].append({"peso": p.text.strip(), "reps": r.text.strip()})
                    hay_datos = True
        if hay_datos:
            guardar_datos(datos)
        self.manager.current = 'menu'

    def volver(self, *args): 
        self.manager.current = 'menu'


class HistorialScreen(Screen):
    def on_enter(self, *args): self.actualizar_historial()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(15), padding=[0,0,0,dp(150)])
        self.container.bind(minimum_height=self.container.setter('height'))
        scroll = ScrollView(); scroll.add_widget(self.container)
        
        btn_v = Button(text="< Volver al Menu", size_hint_y=None, height=dp(50), background_color=get_color_from_hex("#E53935"), bold=True)
        btn_v.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        
        layout.add_widget(Label(text="TABLA DE HISTORIAL", font_size=sp(18), bold=True, size_hint_y=None, height=dp(40), color=get_color_from_hex("#4CAF50")))
        layout.add_widget(scroll); layout.add_widget(btn_v); self.add_widget(layout)

    def actualizar_historial(self):
        self.container.clear_widgets(); datos = cargar_datos()
        if not datos:
            self.container.add_widget(Label(text="-- Historial vacio. Agrega entrenamientos --", halign='center', size_hint_y=None, height=dp(60)))
            return
            
        for fecha in sorted(datos.keys(), reverse=True):
            box_sesion = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(8))
            fila_top = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(38))
            fila_top.add_widget(Label(text=f"Fecha: {fecha}", bold=True, color=get_color_from_hex("#4CAF50"), halign='left', text_size=(dp(200), None), font_size=sp(15)))
            
            btn_borrar = Button(text="BORRAR", size_hint_x=None, width=dp(90), background_color=get_color_from_hex("#D32F2F"), font_size=sp(12), bold=True)
            btn_borrar.bind(on_press=lambda x, f=fecha: self.eliminar_sesion(f))
            fila_top.add_widget(btn_borrar); box_sesion.add_widget(fila_top)
            
            h = dp(45)
            for ej, series in datos[fecha].items():
                if series:
                    txt = " | ".join([f"{s['peso']}kg x {s['reps']}" for s in series])
                    l = Label(text=f"[b]* {ej}[/b]:\n      [color=B0BEC5]{txt}[/color]", markup=True, size_hint_y=None, height=dp(45), halign='left', text_size=(dp(300), None), font_size=sp(14))
                    box_sesion.add_widget(l); h += dp(48)
            box_sesion.height = h; self.container.add_widget(box_sesion)

    def eliminar_sesion(self, fecha):
        datos = cargar_datos()
        if fecha in datos:
            del datos[fecha]
            guardar_datos(datos)
        self.actualizar_historial()


class EditarRutinaScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        self.layout.add_widget(Label(text="EDITOR DE RUTINAS", font_size=sp(20), bold=True, size_hint_y=None, height=dp(40), color=get_color_from_hex("#7E57C2")))
        
        rutinas = cargar_rutinas()
        self.spinner_dias = Spinner(text="-- Selecciona el Dia a Editar --", values=list(rutinas.keys()), size_hint_y=None, height=dp(50), background_color=get_color_from_hex("#7E57C2"), bold=True, font_size=sp(14))
        self.spinner_dias.bind(text=self.cargar_ejercicios_dia); self.layout.add_widget(self.spinner_dias)
        
        self.scroll = ScrollView()
        self.container_ejercicios = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8), padding=[0,0,0,dp(420)])
        self.container_ejercicios.bind(minimum_height=self.container_ejercicios.setter('height'))
        self.scroll.add_widget(self.container_ejercicios); self.layout.add_widget(self.scroll)
        
        box_nuevo = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(5))
        self.input_nuevo_ej = TextInput(hint_text="Escribe nuevo ejercicio aqui...", multiline=False, font_size=sp(15))
        btn_add = Button(text="+ Add", size_hint_x=None, width=dp(70), background_color=get_color_from_hex("#43A047"), bold=True)
        btn_add.bind(on_press=self.anadir_ejercicio)
        box_nuevo.add_widget(self.input_nuevo_ej); box_nuevo.add_widget(btn_add); self.layout.add_widget(box_nuevo)
        
        btn_back = Button(text="GUARDAR CAMBIOS", size_hint_y=None, height=dp(55), background_color=get_color_from_hex("#1E88E5"), bold=True, font_size=sp(15))
        btn_back.bind(on_press=self.finalizar_edicion); self.layout.add_widget(btn_back)
        self.add_widget(self.layout); self.inputs_ejercicios = []

    def cargar_ejercicios_dia(self, spinner, text_dia):
        self.container_ejercicios.clear_widgets(); self.inputs_ejercicios = []
        if text_dia.startswith("--"): return
        rutinas = cargar_rutinas()
        for ej in rutinas.get(text_dia, []):
            fila = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45), spacing=dp(5))
            txt_in = TextInput(text=ej, multiline=False, font_size=sp(15))
            btn_del = Button(text="Eliminar", size_hint_x=None, width=dp(85), background_color=get_color_from_hex("#E53935"), bold=True, font_size=sp(12))
            btn_del.bind(on_press=lambda x, f=fila: self.remover_fila(f))
            fila.add_widget(txt_in); fila.add_widget(btn_del); self.container_ejercicios.add_widget(fila); self.inputs_ejercicios.append(txt_in)

    def remover_fila(self, fila):
        for child in fila.children:
            if isinstance(child, TextInput) and child in self.inputs_ejercicios: 
                self.inputs_ejercicios.remove(child)
        self.container_ejercicios.remove_widget(fila)

    def anadir_ejercicio(self, instance):
        nombre = self.input_nuevo_ej.text.strip()
        if not nombre or self.spinner_dias.text.startswith("--"): return
        fila = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45), spacing=dp(5))
        txt_in = TextInput(text=nombre, multiline=False, font_size=sp(15))
        btn_del = Button(text="Eliminar", size_hint_x=None, width=dp(85), background_color=get_color_from_hex("#E53935"), bold=True, font_size=sp(12))
        btn_del.bind(on_press=lambda x, f=fila: self.remover_fila(f))
        fila.add_widget(txt_in); fila.add_widget(btn_del); self.container_ejercicios.add_widget(fila); self.inputs_ejercicios.append(txt_in)
        self.input_nuevo_ej.text = ""

    def finalizar_edicion(self, instance):
        dia = self.spinner_dias.text
        if not dia.startswith("--"):
            rutinas = cargar_rutinas()
            rutinas[dia] = [inp.text.strip() for inp in self.inputs_ejercicios if inp.text.strip()]
            guardar_rutinas(rutinas)
        self.manager.current = 'menu'


class GraficasScreen(Screen):
    def on_enter(self, *args):
        rutinas = cargar_rutinas(); todos = []
        for lista in rutinas.values(): todos.extend(lista)
        self.spinner.values = sorted(list(set(todos)))
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        self.spinner = Spinner(text="-- Selecciona Ejercicio --", values=[], size_hint_y=None, height=dp(50), background_color=get_color_from_hex("#FB8C00"), bold=True, font_size=sp(15))
        self.spinner.bind(text=self.actualizar_grafica)
        
        self.lbl_info = Label(text="Evolucion de Fuerza Estimada (1RM)", size_hint_y=None, height=dp(30), color=get_color_from_hex("#B0BEC5"), font_size=sp(14))
        self.canvas_grafica = GraficaWidget(size_hint_y=1)
        
        btn_back = Button(text="< Volver al Menu", size_hint_y=None, height=dp(50), background_color=get_color_from_hex("#E53935"), bold=True)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        
        self.layout.add_widget(Label(text="GRAFICAS DE AVANCE", font_size=sp(20), bold=True, size_hint_y=None, height=dp(40), color=get_color_from_hex("#FB8C00")))
        self.layout.add_widget(self.spinner); self.layout.add_widget(self.lbl_info); self.layout.add_widget(self.canvas_grafica); self.layout.add_widget(btn_back)
        self.add_widget(self.layout)

    def actualizar_grafica(self, spinner, text):
        if text.startswith("--"): return
        datos = cargar_datos(); puntos_ejercicio = []
        
        for fecha in sorted(datos.keys()):
            if text in datos[fecha]:
                max_1rm = 0
                for s in datos[fecha][text]:
                    try:
                        p = float(s['peso']); r = int(s['reps'])
                        if p > 0:
                            u_rm = p * (1 + r/30.0) # Formula de Epley para 1RM estimada
                            if u_rm > max_1rm: max_1rm = u_rm
                    except: continue
                if max_1rm > 0: 
                    puntos_ejercicio.append((fecha, max_1rm))
                    
        if puntos_ejercicio:
            self.lbl_info.text = f"Fuerza Max: {round(puntos_ejercicio[-1][1], 1)} kg (1RM)"
            self.canvas_grafica.dibujar(puntos_ejercicio)
        else: 
            self.lbl_info.text = "-- No hay registros de peso para este ejercicio --"
            self.canvas_grafica.canvas.after.clear()


class MainApp(App):
    def build(self):
        sm = ScreenManager()
        Window.clearcolor = get_color_from_hex("#121212") # Fondo oscuro profesional
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(EntrenamientoScreen(name='entrenamiento'))
        sm.add_widget(HistorialScreen(name='historial'))
        sm.add_widget(GraficasScreen(name='graficas'))
        sm.add_widget(EditarRutinaScreen(name='editar_rutina'))
        return sm

if __name__ == '__main__':
    MainApp().run()
