import os
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock

# 🔍 CONFIGURA TUS DATOS AQUÍ:
USUARIO = "ferpalaciosjl-wq"      # Pon tu nombre de usuario de GitHub aquí
REPOSITORIO = "mi-app-gym"             # Pon el nombre de tu repositorio aquí
RAMA = "main"

URL_CODIGO_REAL = f"https://raw.githubusercontent.com/{USUARIO}/{REPOSITORIO}/{RAMA}/app_real.py"

class CascaronApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.lbl_estado = Label(text="🔍 Buscando actualizaciones...", font_size='18sp', halign='center')
        self.layout.add_widget(self.lbl_estado)
        
        # Arrancar la verificación un instante después de abrir la app
        Clock.schedule_once(self.verificar_actualizacion, 0.5)
        return self.layout

    def verificar_actualizacion(self, dt):
        # Intentar descargar el código real desde tu GitHub
        UrlRequest(
            URL_CODIGO_REAL, 
            on_success=self.descarga_exitosa, 
            on_failure=self.usar_copia_local, 
            on_error=self.usar_copia_local,
            timeout=5
        )

    def descarga_exitosa(self, req, resultado):
        self.lbl_estado.text = "⚡ ¡App actualizada! Iniciando..."
        
        # Guardar el código nuevo en la memoria del celular
        with open("app_real.py", "w", encoding="utf-8") as f:
            f.write(resultado)
            
        Clock.schedule_once(self.lanzar_app_real, 0.5)

    def usar_copia_local(self, req, *args):
        # Si no hay internet, revisa si ya teníamos una copia guardada antes
        if os.path.exists("app_real.py"):
            self.lbl_estado.text = "📴 Sin internet. Iniciando copia local..."
            Clock.schedule_once(self.lanzar_app_real, 0.5)
        else:
            self.lbl_estado.text = "❌ Error: Se necesita internet\npara la primera configuración."
            btn_reintentar = Button(text="Reintentar 🔄", size_hint_y=None, height=50)
            btn_reintentar.bind(on_press=self.verificar_actualizacion)
            self.layout.add_widget(btn_reintentar)

    def lanzar_app_real(self, dt):
        try:
            # Este comando mágico de Python carga el archivo descargado y lo ejecuta en vivo
            import importlib
            import app_real
            importlib.reload(app_real)
            
            # Detener la pantalla del cascarón y arrancar la app real con tus iconos y gráficos
            self.root_window.remove_widget(self.layout)
            app_real.iniciar_desde_cascaron(self)
        except Exception as e:
            self.lbl_estado.text = f"💥 Error al ejecutar la app:\n{str(e)}"
