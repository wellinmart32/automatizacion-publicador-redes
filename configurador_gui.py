import os
import sys
import configparser
import tkinter as tk
from tkinter import ttk, messagebox
from compartido.toast import Toast


class ConfiguradorGUI:
    """Interfaz gráfica para configurar el sistema de Publicador Redes"""

    def __init__(self):
        self.config = configparser.RawConfigParser(delimiters=('=',))

        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.archivo_config = os.path.join(self.base_dir, "config_global.txt")

        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('AutomaPro.ConfiguradorRedes')
        except Exception:
            pass

        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("⚙️ Configurador - Publicador Redes")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        try:
            base_ico = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
            self.root.iconbitmap(os.path.join(base_ico, 'iconos', 'settings.ico'))
        except Exception:
            pass

        # Reaplicar icono múltiples veces para garantizar que Windows lo aplique
        try:
            ico = os.path.join(self.base_dir, 'iconos', 'settings.ico')
            self.root.after(100, lambda: self.root.iconbitmap(ico))
            self.root.after(300, lambda: self.root.iconbitmap(ico))
        except Exception:
            pass

        width = 640
        height = 640
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        self._cargar_config()
        self.es_full = self._verificar_licencia_full()
        self._construir_ui()

        self.root.deiconify()

    def _verificar_licencia_full(self):
        """Verifica si la licencia es FULL/MASTER — solo cache, sin llamada de red"""
        try:
            from gestor_licencias import GestorLicencias
            gl = GestorLicencias("PublicadorRedes")
            cache = gl._obtener_cache_local()
            if cache and cache.get('valida'):
                tipo = cache.get('tipo', 'TRIAL')
                return tipo in ['FULL', 'MASTER'] or cache.get('es_developer_permanente', False)
            return False
        except Exception:
            return False

    def _cargar_config(self):
        """Carga la configuración desde config_global.txt"""
        if os.path.exists(self.archivo_config):
            self.config.read(self.archivo_config, encoding='utf-8')

    def _get(self, seccion, clave, defecto=''):
        """Obtiene un valor de la config ignorando comentarios inline"""
        try:
            valor = self.config[seccion][clave].split('#')[0].strip()
            return valor if valor else defecto
        except Exception:
            return defecto

    def _guardar_config(self):
        """Guarda todos los cambios en config_global.txt"""
        try:
            # [GENERAL]
            self.config['GENERAL']['navegador'] = self.var_navegador.get()

            # [ANUNCIOS]
            self.config['ANUNCIOS']['seleccion'] = self.var_seleccion.get()
            self.config['ANUNCIOS']['historial_evitar_repetir'] = self.var_historial.get()
            self.config['ANUNCIOS']['agregar_hashtags'] = self.var_hashtags.get()
            self.config['ANUNCIOS']['hashtags'] = self.var_hashtags_texto.get()
            self.config['ANUNCIOS']['agregar_firma'] = self.var_firma.get()
            self.config['ANUNCIOS']['texto_firma'] = self.var_firma_texto.get()

            # [PUBLICACION]
            self.config['PUBLICACION']['tiempo_entre_intentos'] = self.var_tiempo_intentos.get()
            self.config['PUBLICACION']['max_intentos_por_publicacion'] = self.var_max_intentos.get()
            self.config['PUBLICACION']['espera_despues_publicar'] = self.var_espera.get()

            # [NAVEGADOR]
            self.config['NAVEGADOR']['usar_perfil_existente'] = self.var_usar_perfil.get()
            self.config['NAVEGADOR']['maximizar_ventana'] = self.var_maximizar.get()

            # [LIMITES]
            self.config['LIMITES']['tiempo_minimo_entre_publicaciones_segundos'] = self.var_tiempo_minimo.get()
            self.config['LIMITES']['permitir_forzar_publicacion_manual'] = self.var_forzar_manual.get()

            # [MODULOS]
            self.config['MODULOS']['publicar_facebook'] = self.var_mod_facebook.get()
            if self.es_full:
                self.config['MODULOS']['publicar_instagram'] = self.var_mod_instagram.get()
                self.config['MODULOS']['publicar_twitter'] = self.var_mod_twitter.get()
                self.config['MODULOS']['publicar_linkedin'] = self.var_mod_linkedin.get()
            else:
                self.config['MODULOS']['publicar_instagram'] = 'no'
                self.config['MODULOS']['publicar_twitter'] = 'no'
                self.config['MODULOS']['publicar_linkedin'] = 'no'

            with open(self.archivo_config, 'w', encoding='utf-8') as f:
                f.write("# ============================================================\n")
                f.write("# CONFIGURACIÓN GLOBAL - PUBLICADOR REDES\n")
                f.write("# ============================================================\n\n")
                self.config.write(f)

            Toast.exito(self.root, "Configuración guardada correctamente")
            self.root.after(3500, self.root.destroy)

        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al guardar: {e}")

    def _seccion(self, parent, texto):
        """Crea un label de sección"""
        tk.Label(
            parent,
            text=texto,
            font=("Segoe UI", 10, "bold"),
            bg="#f0f0f0",
            fg="#333"
        ).pack(anchor='w', padx=20, pady=(12, 2))

    def _radio_si_no(self, parent, variable):
        """Crea radio buttons Sí/No"""
        frame = tk.Frame(parent, bg="#f0f0f0")
        frame.pack(anchor='w', padx=20, pady=(0, 12))
        for opcion, label in [('si', 'Sí'), ('no', 'No')]:
            tk.Radiobutton(
                frame, text=label,
                variable=variable, value=opcion,
                bg="#f0f0f0", font=("Segoe UI", 10)
            ).pack(side='left', padx=8)

    def _radio_navegador(self, parent, variable):
        """Crea radio buttons de navegador"""
        frame = tk.Frame(parent, bg="#f0f0f0")
        frame.pack(anchor='w', padx=20, pady=(0, 12))
        for opcion in ['firefox', 'chrome']:
            tk.Radiobutton(
                frame, text=opcion.capitalize(),
                variable=variable, value=opcion,
                bg="#f0f0f0", font=("Segoe UI", 10)
            ).pack(side='left', padx=8)

    def _construir_ui(self):
        """Construye la interfaz del configurador"""

        # Header
        header = tk.Frame(self.root, bg="#7c3aed", pady=12)
        header.pack(fill='x')
        tk.Label(
            header,
            text="⚙️  Configurador - Publicador Redes",
            font=("Segoe UI", 14, "bold"),
            bg="#7c3aed",
            fg="white"
        ).pack()

        # Notebook de pestañas
        style = ttk.Style()
        style.configure('TNotebook.Tab', font=('Segoe UI', 9))

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # ==================== PESTAÑA GENERAL ====================
        tab_general = ttk.Frame(notebook)
        notebook.add(tab_general, text="⚙️ General")

        tk.Label(
            tab_general,
            text="Configuración general del sistema de publicación",
            font=("Segoe UI", 9), fg="#555", bg="#f0f0f0"
        ).pack(anchor='w', padx=20, pady=(10, 0))

        self._seccion(tab_general, "🌐 Navegador")
        self.var_navegador = tk.StringVar(value=self._get('GENERAL', 'navegador', 'firefox'))
        self._radio_navegador(tab_general, self.var_navegador)

        self._seccion(tab_general, "👤 Usar perfil existente del navegador")
        self.var_usar_perfil = tk.StringVar(value=self._get('NAVEGADOR', 'usar_perfil_existente', 'si'))
        self._radio_si_no(tab_general, self.var_usar_perfil)

        self._seccion(tab_general, "🖥️ Maximizar ventana del navegador")
        self.var_maximizar = tk.StringVar(value=self._get('NAVEGADOR', 'maximizar_ventana', 'si'))
        self._radio_si_no(tab_general, self.var_maximizar)

        # ==================== PESTAÑA ANUNCIOS ====================
        tab_anuncios = ttk.Frame(notebook)
        notebook.add(tab_anuncios, text="📢 Anuncios")

        tk.Label(
            tab_anuncios,
            text="Configura cómo se eligen y formatean los anuncios al publicar",
            font=("Segoe UI", 9), fg="#555", bg="#f0f0f0"
        ).pack(anchor='w', padx=20, pady=(10, 0))

        self._seccion(tab_anuncios, "🎯 Selección de anuncio")
        self.var_seleccion = tk.StringVar(value=self._get('ANUNCIOS', 'seleccion', 'secuencial'))
        frame_sel = tk.Frame(tab_anuncios, bg="#f0f0f0")
        frame_sel.pack(anchor='w', padx=20, pady=(0, 12))
        for opcion in ['secuencial', 'aleatorio']:
            tk.Radiobutton(
                frame_sel, text=opcion.capitalize(),
                variable=self.var_seleccion, value=opcion,
                bg="#f0f0f0", font=("Segoe UI", 10)
            ).pack(side='left', padx=8)

        self._seccion(tab_anuncios, "🧠 Memoria: últimos N anuncios a evitar repetir")
        self.var_historial = tk.StringVar(value=self._get('ANUNCIOS', 'historial_evitar_repetir', '5'))
        tk.Spinbox(
            tab_anuncios, from_=0, to=20,
            textvariable=self.var_historial,
            width=8, font=("Segoe UI", 10)
        ).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_anuncios, "# Agregar hashtags automáticamente")
        self.var_hashtags = tk.StringVar(value=self._get('ANUNCIOS', 'agregar_hashtags', 'no'))
        self._radio_si_no(tab_anuncios, self.var_hashtags)

        self._seccion(tab_anuncios, "📎 Hashtags (separados por comas)")
        self.var_hashtags_texto = tk.StringVar(
            value=self._get('ANUNCIOS', 'hashtags', '#Marketing,#Publicidad,#Negocios'))
        tk.Entry(
            tab_anuncios, textvariable=self.var_hashtags_texto,
            width=40, font=("Segoe UI", 10)
        ).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_anuncios, "✍️ Agregar firma al final del anuncio")
        self.var_firma = tk.StringVar(value=self._get('ANUNCIOS', 'agregar_firma', 'no'))
        self._radio_si_no(tab_anuncios, self.var_firma)

        self._seccion(tab_anuncios, "📝 Texto de la firma")
        self.var_firma_texto = tk.StringVar(
            value=self._get('ANUNCIOS', 'texto_firma', 'Publicado automáticamente'))
        tk.Entry(
            tab_anuncios, textvariable=self.var_firma_texto,
            width=40, font=("Segoe UI", 10)
        ).pack(anchor='w', padx=20, pady=(0, 12))

        # ==================== PESTAÑA PUBLICACIÓN ====================
        tab_pub = ttk.Frame(notebook)
        notebook.add(tab_pub, text="🚀 Publicación")

        tk.Label(
            tab_pub,
            text="Configura los tiempos y comportamiento de la publicación automática",
            font=("Segoe UI", 9), fg="#555", bg="#f0f0f0"
        ).pack(anchor='w', padx=20, pady=(10, 0))

        self._seccion(tab_pub, "⏱️ Tiempo entre intentos (segundos)")
        tk.Label(
            tab_pub,
            text="Segundos a esperar entre cada reintento fallido",
            font=("Segoe UI", 8), fg="gray", bg="#f0f0f0"
        ).pack(anchor='w', padx=20)
        self.var_tiempo_intentos = tk.StringVar(
            value=self._get('PUBLICACION', 'tiempo_entre_intentos', '3'))
        tk.Spinbox(
            tab_pub, from_=1, to=30,
            textvariable=self.var_tiempo_intentos,
            width=8, font=("Segoe UI", 10)
        ).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_pub, "🔄 Máximo de intentos por publicación")
        self.var_max_intentos = tk.StringVar(
            value=self._get('PUBLICACION', 'max_intentos_por_publicacion', '3'))
        tk.Spinbox(
            tab_pub, from_=1, to=10,
            textvariable=self.var_max_intentos,
            width=8, font=("Segoe UI", 10)
        ).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_pub, "⏳ Espera después de publicar (segundos)")
        self.var_espera = tk.StringVar(
            value=self._get('PUBLICACION', 'espera_despues_publicar', '5'))
        tk.Spinbox(
            tab_pub, from_=1, to=60,
            textvariable=self.var_espera,
            width=8, font=("Segoe UI", 10)
        ).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_pub, "⏱️ Tiempo mínimo entre publicaciones (segundos)")
        tk.Label(
            tab_pub,
            text="Recomendado: 120 segundos (2 minutos) para evitar spam",
            font=("Segoe UI", 8), fg="gray", bg="#f0f0f0"
        ).pack(anchor='w', padx=20)
        self.var_tiempo_minimo = tk.StringVar(
            value=self._get('LIMITES', 'tiempo_minimo_entre_publicaciones_segundos', '120'))
        tk.Spinbox(
            tab_pub, from_=30, to=3600,
            textvariable=self.var_tiempo_minimo,
            width=8, font=("Segoe UI", 10)
        ).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_pub, "💪 Permitir forzar publicación manual")
        self.var_forzar_manual = tk.StringVar(
            value=self._get('LIMITES', 'permitir_forzar_publicacion_manual', 'si'))
        self._radio_si_no(tab_pub, self.var_forzar_manual)

        # ==================== PESTAÑA MÓDULOS ====================
        tab_modulos = ttk.Frame(notebook)
        notebook.add(tab_modulos, text="📱 Módulos")

        tk.Label(
            tab_modulos,
            text="Activa o desactiva las redes sociales donde se publicará",
            font=("Segoe UI", 9), fg="#555", bg="#f0f0f0"
        ).pack(anchor='w', padx=20, pady=(10, 0))

        # Facebook — siempre disponible
        self._seccion(tab_modulos, "📘 Facebook")
        self.var_mod_facebook = tk.StringVar(
            value=self._get('MODULOS', 'publicar_facebook', 'si'))
        self._radio_si_no(tab_modulos, self.var_mod_facebook)

        # Instagram — solo FULL
        self._seccion(tab_modulos, "📸 Instagram" + ("" if self.es_full else "  🔒 versión Completa"))
        self.var_mod_instagram = tk.StringVar(
            value=self._get('MODULOS', 'publicar_instagram', 'no'))
        frame_ig = tk.Frame(tab_modulos, bg="#f0f0f0")
        frame_ig.pack(anchor='w', padx=20, pady=(0, 12))
        for opcion, label in [('si', 'Sí'), ('no', 'No')]:
            tk.Radiobutton(
                frame_ig, text=label,
                variable=self.var_mod_instagram, value=opcion,
                bg="#f0f0f0", font=("Segoe UI", 10),
                state='normal' if self.es_full else 'disabled'
            ).pack(side='left', padx=8)

        # Twitter/X — solo FULL
        self._seccion(tab_modulos, "🐦 Twitter / X" + ("" if self.es_full else "  🔒 versión Completa"))
        self.var_mod_twitter = tk.StringVar(
            value=self._get('MODULOS', 'publicar_twitter', 'no'))
        frame_tw = tk.Frame(tab_modulos, bg="#f0f0f0")
        frame_tw.pack(anchor='w', padx=20, pady=(0, 12))
        for opcion, label in [('si', 'Sí'), ('no', 'No')]:
            tk.Radiobutton(
                frame_tw, text=label,
                variable=self.var_mod_twitter, value=opcion,
                bg="#f0f0f0", font=("Segoe UI", 10),
                state='normal' if self.es_full else 'disabled'
            ).pack(side='left', padx=8)

        # LinkedIn — solo FULL
        self._seccion(tab_modulos, "💼 LinkedIn" + ("" if self.es_full else "  🔒 versión Completa"))
        self.var_mod_linkedin = tk.StringVar(
            value=self._get('MODULOS', 'publicar_linkedin', 'no'))
        frame_li = tk.Frame(tab_modulos, bg="#f0f0f0")
        frame_li.pack(anchor='w', padx=20, pady=(0, 12))
        for opcion, label in [('si', 'Sí'), ('no', 'No')]:
            tk.Radiobutton(
                frame_li, text=label,
                variable=self.var_mod_linkedin, value=opcion,
                bg="#f0f0f0", font=("Segoe UI", 10),
                state='normal' if self.es_full else 'disabled'
            ).pack(side='left', padx=8)

        if not self.es_full:
            banner = tk.Frame(tab_modulos, bg="#fff3cd", pady=8)
            banner.pack(fill='x', padx=20, pady=(15, 0))
            tk.Label(
                banner,
                text="🔒 Instagram, Twitter y LinkedIn requieren la versión Completa\n"
                     "Visita: automapro-frontend.vercel.app",
                font=("Segoe UI", 9),
                bg="#fff3cd",
                fg="#856404",
                justify='center'
            ).pack(padx=10)

        # ==================== BOTÓN GUARDAR ====================
        frame_guardar = tk.Frame(self.root, bg="#f0f0f0", pady=10)
        frame_guardar.pack(fill='x', padx=20)

        tk.Button(
            frame_guardar,
            text="💾  Guardar configuración",
            font=("Segoe UI", 11, "bold"),
            bg="#7c3aed",
            fg="white",
            activebackground="#6d28d9",
            activeforeground="white",
            cursor="hand2",
            pady=8,
            command=self._guardar_config
        ).pack(fill='x')

    def ejecutar(self):
        self.root.mainloop()


def main():
    app = ConfiguradorGUI()
    app.ejecutar()


if __name__ == "__main__":
    main()