import os
import sys
import tkinter as tk
from tkinter import messagebox
from compartido.toast import Toast
import configparser
import re
import subprocess
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from gestor_licencias import GestorLicencias

COLOR_PRINCIPAL = "#7c3aed"
COLOR_HOVER     = "#6d28d9"


class WizardPrimeraVez:
    """Wizard de configuración inicial para PublicadorRedes"""

    def __init__(self):
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('AutomaPro.WizardPublicador')
        except Exception:
            pass

        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("🎉 Bienvenido - Publicador Redes")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        try:
            base_ico = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
            self.root.iconbitmap(os.path.join(base_ico, 'iconos', 'wizard.ico'))
        except Exception:
            pass

        width = 600
        height = 500
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        try:
            base_ico = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
            ico = os.path.join(base_ico, 'iconos', 'wizard.ico')
            self.root.after(100, lambda: self.root.iconbitmap(ico))
            self.root.after(300, lambda: self.root.iconbitmap(ico))
            self.root.after(500, lambda: self.root.iconbitmap(ico))
        except Exception:
            pass

        self.paso_actual = 0
        self.datos_config = {
            'codigo_licencia': '',
            'navegador': 'firefox',
            'usar_perfil': 'si',
            'usar_ejemplos': False
        }
        self.gestor_licencias = GestorLicencias("PublicadorRedes")
        self.licencia_validada = False
        self.tipo_licencia = None

        # Si ya existe configuración, lanzar Panel de Control directamente
        if self.gestor_licencias.obtener_codigo_guardado():
            try:
                if getattr(sys, 'frozen', False):
                    base_dir = os.path.dirname(sys.executable)
                    panel = os.path.join(base_dir, "PanelControlRedes.exe")
                else:
                    panel = os.path.join(os.path.dirname(os.path.abspath(__file__)), "panel_control.py")
                if os.path.exists(panel):
                    if panel.endswith('.exe'):
                        subprocess.Popen([panel])
                    else:
                        subprocess.Popen([sys.executable, panel])
            except Exception:
                pass
            self.root.after(100, self.root.destroy)
            return

        self.root.deiconify()
        self._mostrar_paso()

    def _limpiar_ventana(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def _mostrar_paso(self):
        self._limpiar_ventana()
        if self.paso_actual == 0:
            self._paso_bienvenida()
        elif self.paso_actual == 1:
            self._paso_licencia()
        elif self.paso_actual == 2:
            self._paso_configuracion()
        elif self.paso_actual == 3:
            self._paso_anuncios()
        elif self.paso_actual == 4:
            self._paso_finalizar()

    # ==================== PASO 0: BIENVENIDA ====================

    def _paso_bienvenida(self):
        header = tk.Frame(self.root, bg=COLOR_PRINCIPAL, pady=20)
        header.pack(fill='x')
        tk.Label(header, text="🎉 Bienvenido a Publicador Redes",
                 font=("Segoe UI", 16, "bold"), bg=COLOR_PRINCIPAL, fg="white").pack()

        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill='both', expand=True, padx=40, pady=30)

        tk.Label(frame, text="Esta aplicación publica anuncios automáticamente\nen tus redes sociales.",
                 font=("Segoe UI", 12), bg="#f0f0f0", justify='center').pack(pady=(0, 20))

        tk.Label(frame, text="Vamos a configurarla juntos paso a paso\n(solo esta vez).",
                 font=("Segoe UI", 11), bg="#f0f0f0", fg="gray", justify='center').pack(pady=(0, 30))

        tk.Label(frame,
                 text="✨ Características:\n\n"
                      "• Publicación automática en Facebook\n"
                      "• Instagram, Twitter y LinkedIn (Versión Completa)\n"
                      "• Soporte para texto, imágenes y videos\n"
                      "• Delays aleatorios para evitar detección",
                 font=("Segoe UI", 10), bg="#f0f0f0", justify='left').pack(pady=(0, 20))

        frame_btn = tk.Frame(self.root, bg="#f0f0f0", pady=20)
        frame_btn.pack(fill='x', side='bottom')
        tk.Button(frame_btn, text="▶️  Comenzar", font=("Segoe UI", 11, "bold"),
                  bg=COLOR_PRINCIPAL, fg="white", width=20, command=self._siguiente).pack()

    # ==================== PASO 1: LICENCIA ====================

    def _paso_licencia(self):
        header = tk.Frame(self.root, bg=COLOR_PRINCIPAL, pady=15)
        header.pack(fill='x')
        tk.Label(header, text="Paso 1 de 4: Activar Licencia",
                 font=("Segoe UI", 14, "bold"), bg=COLOR_PRINCIPAL, fg="white").pack()

        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill='both', expand=True, padx=40, pady=20)

        tk.Label(frame, text="Paso 1 — Ingresa tu email de AutomaPro:",
                 font=("Segoe UI", 11, "bold"), bg="#f0f0f0").pack(anchor='w', pady=(0, 5))

        frame_email = tk.Frame(frame, bg="#f0f0f0")
        frame_email.pack(fill='x', pady=(0, 5))

        self.entry_email = tk.Entry(frame_email, font=("Segoe UI", 11), width=28, justify='center')
        self.entry_email.pack(side='left', padx=(0, 5))
        self.entry_email.focus()

        self.btn_verificar_email = tk.Button(frame_email, text="Verificar",
                                             font=("Segoe UI", 9, "bold"),
                                             bg=COLOR_PRINCIPAL, fg="white",
                                             command=self._verificar_email_wizard)
        self.btn_verificar_email.pack(side='left')

        self.label_estado_email = tk.Label(frame, text="", font=("Segoe UI", 9), bg="#f0f0f0")
        self.label_estado_email.pack(anchor='w', pady=(0, 15))

        tk.Frame(frame, bg="#e0e0e0", height=1).pack(fill='x', pady=(0, 15))

        tk.Label(frame, text="Paso 2 — ¿Tienes licencia completa? (opcional):",
                 font=("Segoe UI", 11, "bold"), bg="#f0f0f0").pack(anchor='w', pady=(0, 5))

        self.entry_licencia = tk.Entry(frame, font=("Segoe UI", 12), width=22,
                                       justify='center', state='disabled')
        self.entry_licencia.pack(anchor='w', pady=(0, 5))
        self.entry_licencia.bind('<KeyRelease>', self._on_codigo_cambio)

        self.label_formato = tk.Label(frame, text="", font=("Segoe UI", 9),
                                      bg="#f0f0f0", fg="gray")
        self.label_formato.pack(anchor='w', pady=(0, 15))

        frame_btn = tk.Frame(self.root, bg="#f0f0f0", pady=20)
        frame_btn.pack(fill='x', side='bottom')

        tk.Button(frame_btn, text="◀️ Atrás", font=("Segoe UI", 10),
                  bg="#e0e0e0", width=12, command=self._anterior).pack(side='left', padx=(40, 10))
        tk.Button(frame_btn, text="🆓 Usar Prueba", font=("Segoe UI", 10),
                  bg="#e65100", fg="white", width=12, command=self._usar_trial).pack(side='left', padx=(0, 10))
        tk.Button(frame_btn, text="Siguiente ▶️", font=("Segoe UI", 10, "bold"),
                  bg="#28a745", fg="white", width=12, command=self._validar_licencia).pack(side='right', padx=(10, 40))

    def _verificar_email_wizard(self):
        email = self.entry_email.get().strip()
        if not email:
            messagebox.showwarning("Email requerido", "Ingresa tu email.")
            return

        self.label_estado_email.config(fg="gray", text="⏳ Verificando...")
        self.btn_verificar_email.config(state='disabled')
        self.root.update()

        try:
            url = self.gestor_licencias.url_backend.replace('/verificar-licencia', '/verificar-email')
            resp = requests.get(url, params={'email': email, 'nombreApp': 'PublicadorRedes'},
                                timeout=30, verify=False)

            if resp.status_code != 200:
                self.label_estado_email.config(fg="#dc3545", text="❌ Error al verificar. Intenta nuevamente.")
                self.btn_verificar_email.config(state='normal')
                return

            datos = resp.json()

            if not datos.get('existe'):
                self.label_estado_email.config(fg="#dc3545", text="❌ Email no encontrado en AutomaPro.")
                self.btn_verificar_email.config(state='normal')
                return

            tipo = datos.get('tipo', 'NINGUNA')
            dias = datos.get('diasRestantes', 0)

            if tipo == 'FULL':
                codigo = datos.get('codigo', '')
                if codigo:
                    self.entry_licencia.config(state='normal')
                    self.entry_licencia.delete(0, tk.END)
                    self.entry_licencia.insert(0, codigo)
                    self.entry_licencia.config(state='disabled')
                    self.label_formato.config(fg="#28a745", text="✅ LICENCIA COMPLETA")
                    self.licencia_validada = True
                    self.tipo_licencia = 'FULL'
                self.label_estado_email.config(fg="#28a745", text="✅ Email verificado — Licencia Completa activa")
                self.btn_verificar_email.config(state='disabled')

            elif tipo == 'TRIAL':
                if dias is not None and dias <= 0:
                    self.label_estado_email.config(fg="#dc3545", text="❌ Tu período de prueba ha expirado.")
                    self.entry_licencia.config(state='normal')
                    self.label_formato.config(fg="gray", text="Ingresa un código de licencia completa")
                    self.btn_verificar_email.config(state='disabled')
                else:
                    self.label_estado_email.config(fg="#28a745",
                                                   text=f"✅ Email verificado — Prueba activa ({dias} días restantes)")
                    self.entry_licencia.config(state='normal')
                    self.label_formato.config(fg="gray", text="Opcional: ingresa código de licencia completa")
                    self.licencia_validada = True
                    self.tipo_licencia = 'TRIAL'
                    self.btn_verificar_email.config(state='disabled')

            elif tipo == 'NINGUNA':
                self.label_estado_email.config(fg="#28a745", text="✅ Email verificado")
                self.entry_licencia.config(state='normal')
                self.label_formato.config(fg="gray", text="Opcional: ingresa código de licencia completa")
                self.btn_verificar_email.config(state='disabled')

        except Exception:
            self.label_estado_email.config(fg="#e65100", text="⏳ Servidor iniciando...")
            messagebox.showwarning("Servidor iniciando",
                                   "El servidor está iniciando. Esto puede tomar hasta 2 minutos.\n\n"
                                   "Por favor espera un momento e intenta nuevamente.")
            self.btn_verificar_email.config(state='normal')

    def _on_codigo_cambio(self, event):
        codigo = self.entry_licencia.get().strip().upper()
        codigo_limpio = re.sub(r'[^A-Z0-9]', '', codigo)
        if len(codigo_limpio) == 14:
            self._verificar_licencia_tiempo_real(
                f"{codigo_limpio[:3]}-{codigo_limpio[3:9]}-{codigo_limpio[9:]}")
        elif len(codigo_limpio) > 0:
            self.label_formato.config(fg="gray", text=f"{len(codigo_limpio)}/14 caracteres")
            self.licencia_validada = False

    def _verificar_licencia_tiempo_real(self, codigo):
        self.label_formato.config(fg="gray", text="⏳ Verificando...")
        self.root.update()
        try:
            codigo_limpio = re.sub(r'[^A-Z0-9]', '', codigo)
            if len(codigo_limpio) != 14:
                self.label_formato.config(fg="#dc3545", text="❌ FORMATO INCORRECTO")
                self.licencia_validada = False
                return
            codigo_formateado = f"{codigo_limpio[:3]}-{codigo_limpio[3:9]}-{codigo_limpio[9:]}"
            resultado = self.gestor_licencias.verificar_licencia(codigo_formateado, mostrar_mensajes=False)
            if resultado.get('valida'):
                self.label_formato.config(fg="#28a745", text=f"✅ LICENCIA {resultado.get('tipo')} VÁLIDA")
                self.licencia_validada = True
                self.tipo_licencia = resultado.get('tipo')
            else:
                self.label_formato.config(fg="#dc3545", text="❌ LICENCIA INVÁLIDA")
                self.licencia_validada = False
                self.tipo_licencia = None
        except Exception:
            self.label_formato.config(fg="#dc3545", text="❌ Error de conexión")
            self.licencia_validada = False

    def _usar_trial(self):
        email = self.entry_email.get().strip() if hasattr(self, 'entry_email') else None
        if not email:
            messagebox.showwarning("Email requerido", "Primero verifica tu email con el botón Verificar.")
            return
        estado_email = self.label_estado_email.cget("text") if hasattr(self, 'label_estado_email') else ""
        if not estado_email or "❌" in estado_email:
            messagebox.showwarning("Email no verificado", "Primero verifica tu email con el botón Verificar.")
            return
        if self.tipo_licencia == 'FULL':
            messagebox.showinfo("Licencia Completa", "Ya tienes licencia completa activada. Da clic en Siguiente.")
            return

        self.label_formato.config(fg="gray", text="⏳ Activando período de prueba...")
        self.root.update()
        try:
            codigo = self.gestor_licencias.registrar_instalacion(email=email)
            if codigo:
                self.datos_config['codigo_licencia'] = codigo
                self.licencia_validada = True
                self.tipo_licencia = 'TRIAL'
                self.label_formato.config(fg="#28a745", text="✅ Período de prueba activado")
                self.root.after(1000, self._siguiente)
            else:
                self.label_formato.config(fg="#dc3545", text="❌ Error al activar. Verifica tu conexión.")
        except Exception as e:
            self.label_formato.config(fg="#dc3545", text=f"❌ Error: {e}")

    def _validar_licencia(self):
        codigo = self.entry_licencia.get().strip().upper()
        estado_email = self.label_estado_email.cget("text") if hasattr(self, 'label_estado_email') else ""
        if not estado_email or "❌" in estado_email:
            messagebox.showwarning("Email no verificado", "Primero verifica tu email con el botón Verificar.")
            return
        if self.tipo_licencia == 'FULL' and self.licencia_validada:
            self.datos_config['codigo_licencia'] = self.entry_licencia.get().strip().upper()
            self.gestor_licencias.guardar_codigo_licencia(self.datos_config['codigo_licencia'])
            self._siguiente()
            return
        if self.tipo_licencia == 'TRIAL' and self.licencia_validada and not codigo:
            self._siguiente()
            return
        if not codigo:
            messagebox.showwarning("Campo Vacío", "Debes ingresar un código de licencia o presionar 'Usar Prueba'.")
            return
        codigo_limpio = re.sub(r'[^A-Z0-9]', '', codigo)
        if len(codigo_limpio) != 14:
            messagebox.showerror("Formato Incorrecto",
                                 f"El código debe tener exactamente 14 caracteres.\n\n"
                                 f"Formato: XXX-XXXXXX-XXXXX\n"
                                 f"Tienes: {len(codigo_limpio)} caracteres")
            return
        if not self.licencia_validada:
            messagebox.showerror("Licencia Inválida",
                                 "El código ingresado no es válido.\n\nPor favor verifica el código o usa Prueba.")
            return
        codigo_formateado = f"{codigo_limpio[:3]}-{codigo_limpio[3:9]}-{codigo_limpio[9:]}"
        self.datos_config['codigo_licencia'] = codigo_formateado
        self.gestor_licencias.guardar_codigo_licencia(codigo_formateado)
        self._siguiente()

    # ==================== PASO 2: CONFIGURACIÓN ====================

    def _paso_configuracion(self):
        header = tk.Frame(self.root, bg=COLOR_PRINCIPAL, pady=15)
        header.pack(fill='x')
        tk.Label(header, text="Paso 2 de 4: Configuración",
                 font=("Segoe UI", 14, "bold"), bg=COLOR_PRINCIPAL, fg="white").pack()

        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill='both', expand=True, padx=40, pady=25)

        tk.Label(frame, text="🌐 Navegador a usar:",
                 font=("Segoe UI", 11, "bold"), bg="#f0f0f0").pack(anchor='w', pady=(0, 8))

        self.var_navegador = tk.StringVar(value='firefox')
        frame_nav = tk.Frame(frame, bg="#f0f0f0")
        frame_nav.pack(anchor='w', pady=(0, 20))
        for valor, label in [('firefox', '🦊 Firefox (recomendado)'), ('chrome', '🌐 Chrome')]:
            tk.Radiobutton(frame_nav, text=label, variable=self.var_navegador, value=valor,
                           bg="#f0f0f0", font=("Segoe UI", 10)).pack(side='left', padx=(0, 20))

        tk.Label(frame, text="👤 Usar perfil guardado del navegador:",
                 font=("Segoe UI", 11, "bold"), bg="#f0f0f0").pack(anchor='w', pady=(0, 5))
        tk.Label(frame, text="Recomendado: Sí — mantiene tu sesión de Facebook iniciada",
                 font=("Segoe UI", 9), bg="#f0f0f0", fg="gray").pack(anchor='w', pady=(0, 8))

        self.var_perfil = tk.StringVar(value='si')
        frame_perf = tk.Frame(frame, bg="#f0f0f0")
        frame_perf.pack(anchor='w', pady=(0, 20))
        for valor, label in [('si', 'Sí'), ('no', 'No')]:
            tk.Radiobutton(frame_perf, text=label, variable=self.var_perfil, value=valor,
                           bg="#f0f0f0", font=("Segoe UI", 10)).pack(side='left', padx=(0, 20))

        tk.Label(frame, text="💡 Después podrás cambiar estas opciones\nen el Configurador.",
                 font=("Segoe UI", 9), bg="#f0f0f0", fg="gray", justify='left').pack(anchor='w')

        frame_btn = tk.Frame(self.root, bg="#f0f0f0", pady=20)
        frame_btn.pack(fill='x', side='bottom')
        tk.Button(frame_btn, text="◀️ Atrás", font=("Segoe UI", 10),
                  bg="#e0e0e0", width=12, command=self._anterior).pack(side='left', padx=(40, 10))
        tk.Button(frame_btn, text="Siguiente ▶️", font=("Segoe UI", 10, "bold"),
                  bg="#28a745", fg="white", width=12, command=self._guardar_config_basica).pack(side='right', padx=(10, 40))

    def _guardar_config_basica(self):
        self.datos_config['navegador'] = self.var_navegador.get()
        self.datos_config['usar_perfil'] = self.var_perfil.get()
        self._crear_config_completa()
        self._siguiente()

    def _crear_config_completa(self):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        config = configparser.ConfigParser()
        config['GENERAL'] = {'nombre_proyecto': 'Publicador Redes', 'carpeta_anuncios': 'anuncios',
                              'navegador': self.datos_config['navegador'], 'modo_debug': 'si'}
        config['ANUNCIOS'] = {'seleccion': 'secuencial', 'historial_evitar_repetir': '5',
                              'agregar_hashtags': 'no', 'hashtags': '#Marketing,#Publicidad,#Negocios',
                              'agregar_firma': 'no', 'texto_firma': 'Publicado automáticamente'}
        config['PUBLICACION'] = {'tiempo_entre_intentos': '3', 'max_intentos_por_publicacion': '3',
                                 'espera_despues_publicar': '5', 'verificar_publicacion_exitosa': 'si',
                                 'espera_estabilizacion_modal': '3'}
        config['NAVEGADOR'] = {'usar_perfil_existente': self.datos_config['usar_perfil'],
                               'carpeta_perfil_custom': 'perfiles/publicador_redes',
                               'desactivar_notificaciones': 'si', 'maximizar_ventana': 'si'}
        config['LIMITES'] = {'tiempo_minimo_entre_publicaciones_segundos': '120',
                             'permitir_duplicados': 'no', 'permitir_forzar_publicacion_manual': 'si'}
        config['MODULOS'] = {'publicar_facebook': 'si', 'publicar_instagram': 'no',
                             'publicar_twitter': 'no', 'publicar_linkedin': 'no'}
        config['DEBUG'] = {'modo_debug': 'detallado'}

        archivo = os.path.join(base_dir, 'config_global.txt')
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write("# ============================================================\n")
            f.write("# CONFIGURACIÓN GLOBAL - PUBLICADOR REDES\n")
            f.write("# ============================================================\n\n")
            config.write(f)

    # ==================== PASO 3: ANUNCIOS ====================

    def _paso_anuncios(self):
        header = tk.Frame(self.root, bg=COLOR_PRINCIPAL, pady=15)
        header.pack(fill='x')
        tk.Label(header, text="Paso 3 de 4: Tus Anuncios",
                 font=("Segoe UI", 14, "bold"), bg=COLOR_PRINCIPAL, fg="white").pack()

        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill='both', expand=True, padx=40, pady=25)

        tk.Label(frame, text="📢 ¿Cómo quieres preparar tus anuncios?",
                 font=("Segoe UI", 11, "bold"), bg="#f0f0f0").pack(anchor='w', pady=(0, 15))

        tk.Button(frame, text="📂  Abrir Gestor de Anuncios",
                  font=("Segoe UI", 10, "bold"), bg=COLOR_PRINCIPAL, fg="white",
                  anchor='w', padx=15, pady=8, cursor="hand2",
                  command=self._abrir_gestor_anuncios).pack(fill='x', pady=(0, 8))

        tk.Label(frame, text="Abre el editor visual para crear tus anuncios con\ntexto, imágenes y videos.",
                 font=("Segoe UI", 9), bg="#f0f0f0", fg="gray", justify='left').pack(anchor='w', pady=(0, 15))

        tk.Button(frame, text="✨  Crear anuncio de ejemplo",
                  font=("Segoe UI", 10), bg="#17a2b8", fg="white",
                  anchor='w', padx=15, pady=8, cursor="hand2",
                  command=self._crear_anuncio_ejemplo).pack(fill='x', pady=(0, 8))

        tk.Label(frame, text="Crea un anuncio de ejemplo para empezar rápido.\nPuedes editarlo después.",
                 font=("Segoe UI", 9), bg="#f0f0f0", fg="gray", justify='left').pack(anchor='w', pady=(0, 15))

        self.lbl_anuncios = tk.Label(frame, text=self._contar_anuncios_texto(),
                                     font=("Segoe UI", 10), bg="#f0f0f0", fg="#28a745")
        self.lbl_anuncios.pack(anchor='w')

        frame_btn = tk.Frame(self.root, bg="#f0f0f0", pady=20)
        frame_btn.pack(fill='x', side='bottom')
        tk.Button(frame_btn, text="◀️ Atrás", font=("Segoe UI", 10),
                  bg="#e0e0e0", width=12, command=self._anterior).pack(side='left', padx=(40, 10))
        tk.Button(frame_btn, text="Siguiente ▶️", font=("Segoe UI", 10, "bold"),
                  bg="#28a745", fg="white", width=12, command=self._verificar_anuncios).pack(side='right', padx=(10, 40))

    def _contar_anuncios_texto(self):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        carpeta = os.path.join(base_dir, 'anuncios')
        if not os.path.exists(carpeta):
            return "📦 0 anuncios creados"
        anuncios = [d for d in os.listdir(carpeta)
                    if os.path.isdir(os.path.join(carpeta, d)) and d.startswith('anuncio_')]
        n = len(anuncios)
        if n == 0:
            return "📦 0 anuncios creados — crea al menos uno para continuar"
        return f"📦 {n} anuncio(s) listo(s) ✅"

    def _abrir_gestor_anuncios(self):
        try:
            if getattr(sys, 'frozen', False):
                exe = os.path.join(os.path.dirname(sys.executable), 'GestorAnuncios.exe')
                if os.path.exists(exe):
                    subprocess.Popen([exe])
                else:
                    messagebox.showwarning("Aviso", "El gestor de anuncios no se encontró.")
            else:
                subprocess.Popen([sys.executable, os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), 'gestor_anuncios.py')])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el gestor: {e}")
        self.root.after(2000, self._actualizar_contador_anuncios)

    def _actualizar_contador_anuncios(self):
        if hasattr(self, 'lbl_anuncios'):
            self.lbl_anuncios.config(text=self._contar_anuncios_texto())

    def _crear_anuncio_ejemplo(self):
        try:
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
            carpeta = os.path.join(base_dir, 'anuncios', 'anuncio_001')
            os.makedirs(os.path.join(carpeta, 'imagenes'), exist_ok=True)
            os.makedirs(os.path.join(carpeta, 'videos'), exist_ok=True)
            with open(os.path.join(carpeta, 'datos.txt'), 'w', encoding='utf-8') as f:
                f.write("[ANUNCIO]\n")
                f.write("texto = 🎉 ¡Oferta especial! Visita nuestro negocio y descubre increíbles productos al mejor precio. ¡No te lo pierdas!\n")
                f.write("plataformas = facebook\n")
                f.write("estado = pendiente\n")
            self.datos_config['usar_ejemplos'] = True
            messagebox.showinfo("✅ Éxito", "Se creó el anuncio de ejemplo.\nPuedes editarlo desde el Gestor de Anuncios.")
            if hasattr(self, 'lbl_anuncios'):
                self.lbl_anuncios.config(text=self._contar_anuncios_texto())
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el ejemplo: {e}")

    def _verificar_anuncios(self):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        carpeta = os.path.join(base_dir, 'anuncios')
        anuncios = []
        if os.path.exists(carpeta):
            anuncios = [d for d in os.listdir(carpeta)
                        if os.path.isdir(os.path.join(carpeta, d)) and d.startswith('anuncio_')]
        if not anuncios:
            messagebox.showwarning("Aviso",
                                   "Necesitas al menos un anuncio para continuar.\n\n"
                                   "Crea uno con el Gestor de Anuncios o usa el ejemplo.")
            return
        self._siguiente()

    # ==================== PASO 4: FINALIZAR ====================

    def _paso_finalizar(self):
        tipo = self.tipo_licencia or 'TRIAL'
        nueva_altura = 560 if tipo in ['FULL', 'MASTER'] else 440
        self.root.geometry(f"600x{nueva_altura}")
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 600) // 2
        y = (self.root.winfo_screenheight() - nueva_altura) // 2
        self.root.geometry(f'600x{nueva_altura}+{x}+{y}')

        header = tk.Frame(self.root, bg="#28a745", pady=15)
        header.pack(fill='x')
        tk.Label(header, text="Paso 4 de 4: ¡Listo!",
                 font=("Segoe UI", 14, "bold"), bg="#28a745", fg="white").pack()

        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill='both', expand=True, padx=40, pady=20)

        tk.Label(frame, text="✅ ¡Configuración completada!",
                 font=("Segoe UI", 14, "bold"), bg="#f0f0f0", fg="#28a745").pack(pady=(0, 15))

        if tipo in ['FULL', 'MASTER']:
            msg = "🎉 Licencia Completa activada\nTodas las funciones desbloqueadas"
            color = "#28a745"
        else:
            msg = "⚠️ Versión de Prueba activada (30 días)\nSolo Facebook, solo texto"
            color = "#e65100"

        tk.Label(frame, text=msg, font=("Segoe UI", 11), bg="#f0f0f0",
                 fg=color, justify='center').pack(pady=(0, 20))

        if tipo in ['FULL', 'MASTER']:
            tk.Frame(frame, bg="#e0e0e0", height=1).pack(fill='x', pady=(0, 15))
            tk.Label(frame, text="🗓️ ¿Crear tareas automáticas predeterminadas?",
                     font=("Segoe UI", 11, "bold"), bg="#f0f0f0").pack(anchor='w', pady=(0, 5))
            tk.Label(frame, text="Programa publicaciones automáticas\nLunes a Viernes a las 9:00 AM",
                     font=("Segoe UI", 9), bg="#f0f0f0", fg="gray").pack(anchor='w', pady=(0, 10))
            self.var_crear_tareas = tk.BooleanVar(value=False)
            tk.Checkbutton(frame, text="Sí, crear tareas automáticas",
                           variable=self.var_crear_tareas, bg="#f0f0f0",
                           font=("Segoe UI", 10)).pack(anchor='w', pady=(0, 15))

        frame_btn = tk.Frame(self.root, bg="#f0f0f0", pady=20)
        frame_btn.pack(fill='x', side='bottom')
        tk.Button(frame_btn, text="❌ Ahora no", font=("Segoe UI", 10),
                  bg="#e0e0e0", width=15, command=self._finalizar_sin_publicar).pack(side='left', padx=(40, 10))
        tk.Button(frame_btn, text="▶️ Abrir Panel de Control",
                  font=("Segoe UI", 10, "bold"), bg="#28a745", fg="white", width=20,
                  command=self._publicar_ahora).pack(side='right', padx=(10, 40))

    def _finalizar_sin_publicar(self):
        if hasattr(self, 'var_crear_tareas') and self.var_crear_tareas.get():
            self._crear_tareas_predeterminadas()
            self.root.after(4500, self._mostrar_mensaje_final_y_cerrar)
        else:
            self._mostrar_mensaje_final_y_cerrar()

    def _mostrar_mensaje_final_y_cerrar(self):
        self._mostrar_toast("¡Todo listo!\n\nPuedes ejecutar 'Publicador Redes' cuando quieras publicar.",
                            duracion=3000, color="#28a745")
        self.root.after(3000, self.root.destroy)

    def _publicar_ahora(self):
        try:
            if hasattr(self, 'var_crear_tareas') and self.var_crear_tareas.get():
                self._crear_tareas_predeterminadas()
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
                panel = os.path.join(base_dir, 'PanelControlRedes.exe')
            else:
                panel = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'panel_control.py')
            if os.path.exists(panel):
                if panel.endswith('.exe'):
                    subprocess.Popen([panel])
                else:
                    subprocess.Popen([sys.executable, panel])
            self._mostrar_toast("🚀 Abriendo Panel de Control\n\nYa puedes comenzar a publicar.",
                                duracion=3000, color="#28a745")
            self.root.after(3000, self.root.destroy)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el Panel de Control: {e}")

    def _crear_tareas_predeterminadas(self):
        try:
            prefijo = "AutomaPro_PublicadorRedes"
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
                exe = os.path.join(base_dir, "PublicadorRedes.exe")
                comando_tarea = f'"{exe}"'
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                script = os.path.join(base_dir, "publicar_redes.py")
                comando_tarea = f'cmd /c "cd /d "{base_dir}" && py "{script}""'

            comando = ['schtasks', '/Create', '/TN', f'{prefijo}_LunesViernes_9AM',
                       '/TR', comando_tarea, '/SC', 'WEEKLY', '/D', 'MON,TUE,WED,THU,FRI',
                       '/ST', '09:00', '/F']
            subprocess.run(comando, capture_output=True, text=True,
                           creationflags=subprocess.CREATE_NO_WINDOW)
            self._mostrar_toast("✅ Tareas automáticas creadas\n\nLunes a Viernes a las 9:00 AM",
                                duracion=4000, color="#28a745")
        except Exception as e:
            messagebox.showerror("Error", f"Error creando tareas automáticas:\n{e}")

    def _mostrar_toast(self, mensaje, duracion=3000, color="#28a745"):
        if color == Toast.COLOR_ERROR or color == "#dc3545":
            Toast.error(self.root, mensaje, duracion)
        elif color == Toast.COLOR_ADVERTENCIA or color == "#e65100":
            Toast.advertencia(self.root, mensaje, duracion)
        elif color == Toast.COLOR_INFO:
            Toast.info(self.root, mensaje, duracion)
        else:
            Toast.exito(self.root, mensaje, duracion)

    def _siguiente(self):
        self.paso_actual += 1
        self._mostrar_paso()

    def _anterior(self):
        self.paso_actual -= 1
        self._mostrar_paso()

    def ejecutar(self):
        self.root.mainloop()


def main():
    wizard = WizardPrimeraVez()
    wizard.ejecutar()


if __name__ == "__main__":
    main()