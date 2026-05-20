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

# Forzar redimensionamiento nativo en Android
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
            return json.load(f)
    return {}

def guardar_datos(datos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout_centrado = BoxLayout(orientation='vertical', padding=dp(20))
        
        box_bloque = BoxLayout(
            orientation='vertical', 
            spacing=dp(16), 
            size_hint=(None, None), 
            width=dp(320), 
            height=dp(540)
        )
        box_bloque.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        
        box_bloque.add_widget(Label(
            text="REGISTRO GYM", 
            font_size=sp(32), 
            bold=True, 
            color=get_color_from_hex("#FFFFFF"),
            size_hint_y=None, 
            height=dp(70)
        ))
        
        for dia in RUTINA.keys():
            btn = Button(
                text=dia, 
                size_hint=(1, None), 
                height=dp(68), 
                font_size=sp(16),
                bold=True,
                background_normal='',
                background_color=get_color_from_hex("#1E88E5")
            )
            btn.bind(on_press=self.ir_a_dia)
            box_bloque.add_widget(btn)
            
        btn_historial = Button(
            text="Ver Historial / Avances", 
            size_hint=(1, None), 
            height=dp(72), 
            font_size=sp(18),
            bold=True,
            background_normal='',
            background_color=get_color_from_hex("#43A047")
        )
        btn_historial.bind(on_press=self.ir_a_historial)
        box_bloque.add_widget(btn_historial)
        
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
        
        # CABECERA FIJA
        box_cabecera = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(55), spacing=dp(10))
        btn_volver = Button(text="< Volver", size_hint_x=0.3, font_size=sp(15), bold=True, background_color=get_color_from_hex("#E53935"))
        btn_volver.bind(on_press=self.volver_menu)
        
        self.lbl_titulo = Label(text="", font_size=sp(18), size_hint_x=0.4, bold=True, halign='center')
        
        btn_guardar = Button(text="Guardar", size_hint_x=0.3, font_size=sp(15), bold=True, background_color=get_color_from_hex("#43A047"))
        btn_guardar.bind(on_press=self.guardar_entrenamiento)
        
        box_cabecera.add_widget(btn_volver)
        box_cabecera.add_widget(self.lbl_titulo)
        box_cabecera.add_widget(btn_guardar)
        self.layout_principal.add_widget(box_cabecera)
        
        # PANEL DE MÉTRICAS (Estadísticas de fuerza superiores en tiempo real)
        self.panel_metricas = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10), padding=[0, dp(5), 0, dp(5)])
        self.lbl_volumen_total = Label(text="Volumen Total\n0 kg", font_size=sp(13), halign='center', color=get_color_from_hex("#B0BEC5"))
        self.lbl_record_fuerza = Label(text="Mejor Marca Histórica\nCargando...", font_size=sp(13), halign='center', color=get_color_from_hex("#FFB300"))
        self.panel_metricas.add_widget(self.lbl_volumen_total)
        self.panel_metricas.add_widget(self.lbl_record_fuerza)
        self.layout_principal.add_widget(self.panel_metricas)
        
        # ZONA DESLIZANTE CON CONTENEDOR FLEXIBLE
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(30))
        self.container.bind(minimum_height=self.container.setter('height'))
        
        self.scroll.add_widget(self.container)
        self.layout_principal.add_widget(self.scroll)
        
        self.add_widget(self.layout_principal)

    def calcular_estadisticas_dia(self, nombre_dia):
        datos = cargar_datos()
        max_peso = 0
        estimado_1rm = 0
        
        # Buscar en el historial el peso más alto levantado en los ejercicios de este día
        ejercicios_del_dia = RUTINA[nombre_dia]
        for fecha, entrenamientos in datos.items():
            for ej, series in entrenamientos.items():
                if ej in ejercicios_del_dia:
                    for s in series:
                        p = float(s.get("peso", 0))
                        r = int(s.get("reps", 0))
                        if p > max_peso:
                            max_peso = p
                        # Fórmula de Epley para calcular el 1RM Máximo Estimado
                        if r > 1:
                            uno_rm = p * (1 + r / 30.0)
                            if uno_rm > estimado_1rm:
                                estimado_1rm = uno_rm
                                
        if max_peso > 0:
            self.lbl_record_fuerza.text = f"Mejor Marca: {max_peso} kg\nEst. 1RM: {round(estimado_1rm, 1)} kg"
        else:
            self.lbl_record_fuerza.text = "Mejor Marca\n-- Sin historial --"

    def actualizar_volumen_tiempo_real(self, *args):
        volumen_total = 0
        for ej, series in self.inputs.items():
            for in_peso, in_reps in series:
                try:
                    p = float(in_peso.text) if in_peso.text else 0.0
                    r = int(in_reps.text) if in_reps.text else 0
                    volumen_total += (p * r)
                except ValueError:
                    continue
        self.lbl_volumen_total.text = f"Volumen Total\n{round(volumen_total, 1)} kg"

    def preparar_dia(self, nombre_dia):
        self.container.clear_widgets()
        self.inputs = {}
        self.dia_actual = nombre_dia
        self.lbl_titulo.text = nombre_dia.split(":")[0]
        
        self.calcular_estadisticas_dia(nombre_dia)
        
        # Generar las tarjetas de entrada
        for ej in RUTINA[nombre_dia]:
            box_ej = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(135), spacing=dp(6))
            
            lbl_ej = Label(text=ej, font_size=sp(16), bold=True, color=get_color_from_hex("#FFB300"), size_hint_y=None, height=dp(30), halign='left', valign='middle')
            lbl_ej.bind(size=lbl_ej.setter('text_size'))
            box_ej.add_widget(lbl_ej)
            
            box_series = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(95))
            self.inputs[ej] = []
            
            for i in range(4):
                box_serie = BoxLayout(orientation='vertical', spacing=dp(3))
                box_serie.add_widget(Label(text=f"S{i+1}", font_size=sp(12), bold=True, size_hint_y=None, height=dp(15), color=get_color_from_hex("#90A4AE")))
                
                in_peso = TextInput(hint_text="Kg", input_filter='float', multiline=False, font_size=sp(16), padding=[dp(4), dp(8), dp(4), dp(8)], halign='center')
                in_reps = TextInput(hint_text="Reps", input_filter='int', multiline=False, font_size=sp(16), padding=[dp(4), dp(8), dp(4), dp(8)], halign='center')
                
                # Escuchar cambios para actualizar estadísticas de volumen arriba
                in_peso.bind(text=self.actualizar_volumen_tiempo_real)
                in_reps.bind(text=self.actualizar_volumen_tiempo_real)
                
                box_serie.add_widget(in_peso)
                box_serie.add_widget(in_reps)
                box_series.add_widget(box_serie)
                
                self.inputs[ej].append((in_peso, in_reps))
                
            box_ej.add_widget(box_series)
            self.container.add_widget(box_ej)
            
        # 🚀 EL TRUCO MAESTRO: Bloque invisible gigante al final del scroll para ganarle espacio al teclado
        espaciador_teclado = BoxLayout(size_hint_y=None, height=dp(420))
        self.container.add_widget(espaciador_teclado)

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
        self.layout_principal = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(12))
        
        self.scroll = ScrollView(size_hint=(1, 1))
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(18))
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
            self.container.add_widget(Label(text="No hay entrenamientos guardados aún.", font_size=sp(16), size_hint_y=None, height=dp(40)))
        else:
            for fecha in sorted(datos.keys(), reverse=True):
                # Contenedor tipo Tarjeta para la sesión
                box_fecha = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(6), padding=dp(10))
                
                # Encabezado estilo tabla con color de éxito
                lbl_fecha = Label(
                    text=f"📅 Sesión: {fecha}", 
                    font_size=sp(16), 
                    bold=True, 
                    color=get_color_from_hex("#4CAF50"), 
                    size_hint_y=None, 
                    height=dp(30),
                    halign='left'
                )
                lbl_fecha.bind(size=lbl_fecha.setter('text_size'))
                box_fecha.add_widget(lbl_fecha)
                
                altura_bloque = dp(35)
                for ej, series in datos[fecha].items():
                    if series:
                        # Crear el formato de tabla limpia para cada ejercicio
                        texto_series = " | ".join([f"S{i+1}: {s['peso']}kg x {s['reps']}" for i, s in enumerate(series)])
                        
                        lbl_ej = Label(
                            text=f"[b]• {ej}[/b]\n[color=B0BEC5]  {texto_series}[/color]", 
                            font_size=sp(14), 
                            halign='left', 
                            size_hint_y=None, 
                            height=dp(50),
                            markup=True # Permite usar negritas y colores personalizados en el texto
                        )
                        lbl_ej.bind(size=lbl_ej.setter('text_size'))
                        box_fecha.add_widget(lbl_ej)
                        altura_bloque += dp(52)
                
                box_fecha.height = altura_bloque
                self.container.add_widget(box_fecha)


class RutinaGymApp(App):
    def build(self):
        sm = ScreenManager()
        Window.clearcolor = get_color_from_hex("#121212")
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(EntrenamientoScreen(name='entrenamiento'))
        sm.add_widget(HistorialScreen(name='historial'))
        return sm

if __name__ == '__main__':
    RutinaGymApp().run()
