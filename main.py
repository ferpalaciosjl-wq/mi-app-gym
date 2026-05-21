import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock

# Enlace directo verificado a tu código real
URL_CODIGO_REAL = "https://raw.githubusercontent.com/ferpalaciosjl-wq/mi-app-gym/main/app_real.py"

class CascaronApp(App):
    def build(self):
        # Creamos el ScreenManager base que exige tu app_real para poder montarse
        self.root = ScreenManager()
        
        # Pantalla de carga temporal
        self.layout_carga = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.lbl_estado = Label(text="🔍 Buscando actualizaciones...", font_size='18sp', halign='center')
        self.layout_carga.add_widget(self.lbl_estado)
        
        # Forzar el inicio de la descarga un instante después de abrir
        Clock.schedule_once(self.verificar_actualizacion, 0.5)
        return self.layout_carga

    def verificar_actualizacion(self, dt):
        UrlRequest(
            URL_CODIGO_REAL, 
            on_success=self.descarga_exitosa, 
            on_failure=self.usar_copia_local, 
            on_error=self.usar_copia_local,
            timeout=7
        )

    def descarga_exitosa(self, req, resultado):
        self.lbl_estado.text = "⚡ ¡App actualizada! Iniciando..."
        
        # Guardamos el código fresco en la memoria del celular
        with open("app_real.py", "w", encoding="utf-8") as f:
            f.write(resultado)
            
        Clock.schedule_once(self.lanzar_app_real, 0.5)

    def usar_copia_local(self, req, *args):
        if os.path.exists("app_real.py"):
            self.lbl_estado.text = "📴 Sin internet. Iniciando copia local..."
            Clock.schedule_once(self.lanzar_app_real, 0.5)
        else:
            self.lbl_estado.text = "❌ Error de conexión.\nSe necesita internet para el primer inicio."
            btn_reintentar = Button(text="Reintentar Conexión 🔄", size_hint_y=None, height=50)
            btn_reintentar.bind(on_press=lambda x: self.verificar_actualizacion(0))
            self.layout_carga.add_widget(btn_reintentar)

    def lanzar_app_real(self, dt):
        try:
            import importlib
            import app_real
            importlib.reload(app_real)
            
            # Removemos el aviso de carga e inyectamos las pantallas reales
            self.root_window.remove_widget(self.layout_carga)
            app_real.iniciar_desde_cascaron(self)
        except Exception as e:
            self.lbl_estado.text = f"💥 Error al ejecutar app_real:\n{str(e)}"
