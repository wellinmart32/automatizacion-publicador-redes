import os
import sys
import tkinter as tk
from tkinter import messagebox
import subprocess
from gestor_licencias import GestorLicencias
from gestor_registro import GestorRegistro

# Color principal de PublicadorRedes
COLOR_PRINCIPAL = "#7c3aed"
COLOR_HOVER = "#6d28d9"


class PanelControl:
    """Panel de control principal - Publicador Redes"""

    def __init__(self):
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('AutomaPro.PanelControlRedes')
        except Exception:
            pass

        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("🟣 Publicador Redes - Panel de Control")
        self.root.geometry("700x680")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        self.gestor_licencias = GestorLicencias("PublicadorRedes")
        self.licencia = self._verificar_licencia()

        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        if not self.licencia:
            self.root.destroy()
            return

        self._construir_ui()

        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        self.root.deiconify()

    def _exe(self, nombre):
        """Retorna ruta al .exe en la misma carpeta del ejecutable"""
        if getattr(sys, 'frozen', False):
            base = os.path.dirname(sys.executable)
        else:
            base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, nombre)

    def _verificar_licencia(self):
        """Verifica licencia al inicio"""
        codigo = self.gestor_licencias.obtener_codigo_guardado()

        if not codigo:
            if getattr(sys, 'frozen', False):
                wizard = os.path.join(os.path.dirname(sys.executable), "WizardPublicador.exe")
            else:
                wizard = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wizard_primera_vez.py")
            if os.path.exists(wizard):
                subprocess.Popen([wizard] if wizard.endswith('.exe') else [sys.executable, wizard])
            else:
                messagebox.showwarning("Sin Licencia", "No hay licencia configurada.\n\nEjecuta el Wizard de primera vez.")
            return None

        resultado = self.gestor_licencias.verificar_licencia(codigo, mostrar_mensajes=False)

        if not resultado['valida']:
            tipo_error = resultado.get('mensaje', '')
            if 'Servidor no disponible' in tipo_error or 'cache' in tipo_error.lower():
                messagebox.showwarning(
                    "⏳ Servidor iniciando",
                    "El servidor está iniciando. Esto puede tomar hasta 2 minutos.\n\n"
                    "Por favor cierra y vuelve a abrir la aplicación en unos momentos."
                )
            else:
                messagebox.showerror(
                    "Licencia Inválida",
                    "Tu licencia no es válida o ha expirado.\n\n"
                    "Visita: automapro-frontend.vercel.app"
                )
            return None

        if resultado.get('tipo') == 'TRIAL':
            dias = resultado.get('diasRestantes', 0)
            if dias <= 0:
                messagebox.showwarning(
                    "Período de Prueba Expirado",
                    "Tu período de prueba ha terminado.\n\n"
                    "Adquiere la versión Completa para seguir publicando.\n\n"
                    "Visita: automapro-frontend.vercel.app"
                )
                return None

        return resultado

    def _construir_ui(self):
        """Construye la interfaz del panel"""

        # Header
        header = tk.Frame(self.root, bg=COLOR_PRINCIPAL, pady=20)
        header.pack(fill='x')

        tk.Label(
            header,
            text="🟣 Publicador Redes",
            font=("Segoe UI", 20, "bold"),
            bg=COLOR_PRINCIPAL,
            fg="white"
        ).pack()

        # Badge de licencia
        tipo_licencia = self.licencia.get('tipo', 'TRIAL')
        if self.licencia.get('developer_permanente'):
            texto_licencia = "👑 LICENCIA DEVELOPER"
            color_badge = "#1a73e8"
        elif tipo_licencia == "FULL":
            texto_licencia = "✅ LICENCIA COMPLETA"
            color_badge = "#28a745"
        else:
            dias = self.licencia.get('diasRestantes', 0)
            texto_licencia = f"⚠️ PRUEBA — {dias} días restantes"
            color_badge = "#ffc107"

        tk.Label(
            header,
            text=texto_licencia,
            font=("Segoe UI", 10, "bold"),
            bg=color_badge,
            fg="white",
            padx=15,
            pady=5
        ).pack(pady=(10, 0))

        # Contenedor principal
        container = tk.Frame(self.root, bg="#f0f0f0")
        container.pack(fill='both', expand=True, padx=30, pady=20)

        # Botón principal: PUBLICAR AHORA
        btn_publicar = tk.Button(
            container,
            text="▶️  PUBLICAR AHORA",
            font=("Segoe UI", 16, "bold"),
            bg=COLOR_PRINCIPAL,
            fg="white",
            activebackground=COLOR_HOVER,
            activeforeground="white",
            cursor="hand2",
            height=2,
            command=self._publicar_ahora
        )
        btn_publicar.pack(fill='x', pady=(0, 20))

        # Grid de opciones
        grid_frame = tk.Frame(container, bg="#f0f0f0")
        grid_frame.pack(fill='both', expand=True)

        # Fila 1
        self._crear_boton_opcion(
            grid_frame,
            "⚙️\nConfigurador",
            "Ajusta la configuración\nde publicación",
            self._abrir_configurador,
            0, 0
        )
        self._crear_boton_opcion(
            grid_frame,
            "📢\nGestor Anuncios",
            "Crea y edita tus\nanuncios",
            self._abrir_gestor_anuncios,
            0, 1
        )
        self._crear_boton_opcion(
            grid_frame,
            "📊\nEstadísticas",
            "Ver historial de\npublicaciones",
            self._abrir_estadisticas,
            0, 2
        )

        # Fila 2
        self._crear_boton_opcion(
            grid_frame,
            "🗓️\nTareas Automáticas",
            "Programa publicaciones\nautomáticas",
            self._abrir_tareas,
            1, 0
        )
        self._crear_boton_opcion(
            grid_frame,
            "👥\nSolicitudes",
            "Enviar solicitudes\nde amistad/conexión",
            self._abrir_solicitudes,
            1, 1
        )
        self._crear_boton_opcion(
            grid_frame,
            "🔄\nActualizar",
            "Verificar actualizaciones\ndisponibles",
            self._verificar_actualizacion,
            1, 2
        )

        # Footer
        footer = tk.Frame(self.root, bg="#e0e0e0", pady=8)
        footer.pack(fill='x', side='bottom')
        tk.Label(
            footer,
            text="AutomaPro — PublicadorRedes v1.0.0",
            font=("Segoe UI", 9),
            bg="#e0e0e0",
            fg="#666"
        ).pack()

    def _crear_boton_opcion(self, parent, titulo, descripcion, comando, fila, columna):
        """Crea un botón de opción en el grid"""
        frame = tk.Frame(parent, bg="white", relief='solid', bd=1, cursor="hand2")
        frame.grid(row=fila, column=columna, padx=5, pady=5, sticky='nsew')
        parent.grid_columnconfigure(columna, weight=1)
        parent.grid_rowconfigure(fila, weight=1)

        tk.Label(
            frame,
            text=titulo,
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg=COLOR_PRINCIPAL,
            justify='center'
        ).pack(pady=(15, 5))

        tk.Label(
            frame,
            text=descripcion,
            font=("Segoe UI", 8),
            bg="white",
            fg="gray",
            justify='center'
        ).pack(pady=(0, 15))

        frame.bind("<Button-1>", lambda e: comando())
        for widget in frame.winfo_children():
            widget.bind("<Button-1>", lambda e: comando())

    def _publicar_ahora(self):
        """Ejecuta el publicador principal"""
        try:
            exe = self._exe("PublicadorRedes.exe")
            if os.path.exists(exe):
                subprocess.Popen([exe])
            else:
                subprocess.Popen([sys.executable, self._exe("publicar_redes.py")])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar el publicador: {e}")

    def _abrir_configurador(self):
        """Abre el configurador"""
        messagebox.showinfo("Próximamente", "El configurador estará disponible en la próxima versión.")

    def _abrir_gestor_anuncios(self):
        """Abre el gestor de anuncios"""
        messagebox.showinfo("Próximamente", "El gestor de anuncios estará disponible en la próxima versión.")

    def _abrir_estadisticas(self):
        """Muestra estadísticas"""
        gestor = GestorRegistro()
        stats = gestor.obtener_estadisticas()
        msg = (
            f"📊 ESTADÍSTICAS\n\n"
            f"Total publicaciones: {stats['total']}\n"
            f"Exitosas: {stats['exitosas']}\n"
            f"Fallidas: {stats['fallidas']}\n"
            f"Tasa de éxito: {stats['tasa_exito']}%\n"
        )
        if stats['ultima_publicacion']:
            msg += f"Última publicación: {stats['ultima_publicacion'][:19]}"
        messagebox.showinfo("Estadísticas", msg)

    def _abrir_tareas(self):
        """Abre el gestor de tareas automáticas"""
        messagebox.showinfo("Próximamente", "Las tareas automáticas estarán disponibles en la próxima versión.")

    def _abrir_solicitudes(self):
        """Abre el módulo de solicitudes de amistad/conexión"""
        es_full = self.licencia.get('tipo') in ['FULL', 'MASTER'] or self.licencia.get('developer_permanente')
        if not es_full:
            messagebox.showwarning(
                "Versión Completa requerida",
                "El módulo de solicitudes requiere la versión Completa.\n\n"
                "Visita: automapro-frontend.vercel.app"
            )
            return
        messagebox.showinfo("Próximamente", "El módulo de solicitudes estará disponible en la próxima versión.")

    def _verificar_actualizacion(self):
        """Verifica actualizaciones disponibles"""
        messagebox.showinfo("Actualizaciones", "Tu aplicación está actualizada a la versión más reciente.")

    def ejecutar(self):
        self.root.mainloop()


def _verificar_wizard_completado():
    """Si no hay licencia configurada, lanza el wizard y termina"""
    gestor = GestorLicencias("PublicadorRedes")
    try:
        config_path = gestor.archivo_config
        tiene_configuracion = False
        if config_path.exists():
            import json
            with open(config_path, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                if datos.get('codigo_licencia'):
                    tiene_configuracion = True

        if not tiene_configuracion:
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
                wizard = os.path.join(base_dir, "WizardPublicador.exe")
            else:
                wizard = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wizard_primera_vez.py")
            if os.path.exists(wizard):
                subprocess.Popen([wizard] if wizard.endswith('.exe') else [sys.executable, wizard])
            return False
        return True
    except Exception:
        return True


def main():
    if not _verificar_wizard_completado():
        return
    panel = PanelControl()
    panel.ejecutar()


if __name__ == "__main__":
    main()