import os
import sys
import tkinter as tk
from tkinter import messagebox
import configparser
import re
import subprocess
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from gestor_licencias import GestorLicencias

# Color principal de PublicadorRedes
COLOR_PRINCIPAL = "#7c3aed"
COLOR_HOVER = "#6d28d9"


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

        width = 600
        height = 520
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        self.root.deiconify()

        self.paso_actual = 0
        self.datos_config = {
            'codigo_licencia': '',
            'navegador': 'firefox',
            'usar_perfil': 'si',
        }
        self.gestor_licencias = GestorLicencias("PublicadorRedes")
        self.licencia_validada = False
        self.tipo_licencia = None

        self._mostrar_paso()

    def _limpiar_ventana(self):
        """Limpia todos los widgets de la ventana"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def _mostrar_paso(self):
        """Muestra el paso actual del wizard"""
        self._limpiar_ventana()
        if self.paso_actual == 0:
            self._paso_bienvenida()
        elif self.paso_actual == 1:
            self._paso_licencia()
        elif self.paso_actual == 2:
            self._paso_configuracion()
        elif self.paso_actual == 3:
            self._paso_finalizar()

    def _paso_bienvenida(self):
        """Paso 0: Pantalla de bienvenida"""
        header = tk.Frame(self.root, bg=COLOR_PRINCIPAL, pady=20)
        header.pack(fill='x')
        tk.Label(
            header,
            text="🟣 Bienvenido a Publicador Redes",
            font=("Segoe UI", 16, "bold"),
            bg=COLOR_PRINCIPAL,
            fg="white"
        ).pack()

        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill='both', expand=True, padx=40, pady=30)

        tk.Label(
            frame,
            text="Esta aplicación publica anuncios automáticamente\nen tus redes sociales.",
            font=("Segoe UI", 12),
            bg="#f0f0f0",
            justify='center'
        ).pack(pady=(0, 20))

        tk.Label(
            frame,
            text="Vamos a configurarla juntos paso a paso\n(solo esta vez).",
            font=("Segoe UI", 11),
            bg="#f0f0f0",
            fg="gray",
            justify='center'
        ).pack(pady=(0, 30))

        tk.Label(
            frame,
            text="✨ Características:\n\n"
                 "• Publicación automática en Facebook\n"
                 "• Instagram, Twitter y LinkedIn (Versión Completa)\n"
                 "• Envío de solicitudes de amistad\n"
                 "• Soporte para texto, imágenes y videos (Versión Completa)",
            font=("Segoe UI", 10),
            bg="#f0f0f0",
            justify='left'
        ).pack(pady=(0, 30))

        frame_btn = tk.Frame(self.root, bg="#f0f0f0", pady=20)
        frame_btn.pack(fill='x', side='bottom')

        tk.Button(
            frame_btn,
            text="▶️  Comenzar",
            font=("Segoe UI", 11, "bold"),
            bg=COLOR_PRINCIPAL,
            fg="white",
            width=20,
            command=self._siguiente
        ).pack()

    def _paso_licencia(self):
        """Paso 1: Activar licencia"""
        header = tk.Frame(self.root, bg=COLOR_PRINCIPAL, pady=15)
        header.pack(fill='x')
        tk.Label(
            header,
            text="Paso 1 de 3: Activar Licencia",
            font=("Segoe UI", 14, "bold"),
            bg=COLOR_PRINCIPAL,
            fg="white"
        ).pack()

        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill='both', expand=True, padx=40, pady=20)

        # Campo email
        tk.Label(
            frame,
            text="Paso 1 — Ingresa tu email de AutomaPro:",
            font=("Segoe UI", 11, "bold"),
            bg="#f0f0f0"
        ).pack(anchor='w', pady=(0, 5))

        frame_email = tk.Frame(frame, bg="#f0f0f0")
        frame_email.pack(fill='x', pady=(0, 5))

        self.entry_email = tk.Entry(
            frame_email,
            font=("Segoe UI", 11),
            width=28,
            justify='center'
        )
        self.entry_email.pack(side='left', padx=(0, 5))
        self.entry_email.focus()

        self.btn_verificar_email = tk.Button(
            frame_email,
            text="Verificar",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_PRINCIPAL,
            fg="white",
            command=self._verificar_email_wizard
        )
        self.btn_verificar_email.pack(side='left')

        self.label_estado_email = tk.Label(
            frame,
            text="",
            font=("Segoe UI", 9),
            bg="#f0f0f0"
        )
        self.label_estado_email.pack(anchor='w', pady=(0, 15))

        tk.Frame(frame, bg="#e0e0e0", height=1).pack(fill='x', pady=(0, 15))

        # Campo código
        tk.Label(
            frame,
            text="Paso 2 — ¿Tienes licencia completa? Ingresa tu código:",
            font=("Segoe UI", 11, "bold"),
            bg="#f0f0f0"
        ).pack(anchor='w', pady=(0, 5))

        tk.Label(
            frame,
            text="Si no tienes código, usa el botón 'Usar Prueba' abajo.",
            font=("Segoe UI", 9),
            bg="#f0f0f0",
            fg="gray"
        ).pack(anchor='w', pady=(0, 10))

        entry_frame = tk.Frame(frame, bg="#f0f0f0")
        entry_frame.pack(pady=(0, 5))

        self.entry_licencia = tk.Entry(
            entry_frame,
            font=("Segoe UI", 12, "bold"),
            width=20,
            justify='center',
            state='disabled'
        )
        self.entry_licencia.pack()

        self.label_formato = tk.Label(
            frame,
            text="Formato: XXX-XXXXXX-XXXXX",
            font=("Segoe UI", 9),
            fg="gray",
            bg="#f0f0f0"
        )
        self.label_formato.pack(pady=(5, 0))

        def insertar_mayuscula(event):
            if event.char and event.char.isalpha():
                self.entry_licencia.insert(tk.INSERT, event.char.upper())
                return "break"

        def auto_formateo(event):
            texto = self.entry_licencia.get().upper()
            solo_alfanum = re.sub(r'[^A-Z0-9]', '', texto)
            if len(solo_alfanum) > 14:
                solo_alfanum = solo_alfanum[:14]
            formateado = solo_alfanum
            if len(solo_alfanum) > 3:
                formateado = solo_alfanum[:3] + '-' + solo_alfanum[3:]
            if len(solo_alfanum) > 9:
                formateado = solo_alfanum[:3] + '-' + solo_alfanum[3:9] + '-' + solo_alfanum[9:]
            pos = self.entry_licencia.index(tk.INSERT)
            self.entry_licencia.delete(0, tk.END)
            self.entry_licencia.insert(0, formateado)
            self.entry_licencia.icursor(tk.END)
            if len(solo_alfanum) == 14:
                self._verificar_licencia_tiempo_real(formateado)
            elif len(solo_alfanum) > 0:
                self.label_formato.config(fg="#ffc107", text=f"⚠ Faltan {14 - len(solo_alfanum)} caracteres")
                self.licencia_validada = False
                self.tipo_licencia = None
            else:
                self.label_formato.config(fg="gray", text="Formato: XXX-XXXXXX-XXXXX")
                self.licencia_validada = False
                self.tipo_licencia = None

        self.entry_licencia.bind('<Key>', insertar_mayuscula)
        self.entry_licencia.bind('<KeyRelease>', auto_formateo)

        tk.Label(
            frame,
            text="Si no tienes código, puedes usar la versión Prueba\n"
                 "(limitada a 1 publicación/día, solo Facebook)",
            font=("Segoe UI", 9),
            bg="#f0f0f0",
            fg="gray",
            justify='center'
        ).pack(pady=(0, 20))

        frame_btn = tk.Frame(self.root, bg="#f0f0f0", pady=20)
        frame_btn.pack(fill='x', side='bottom')

        tk.Button(
            frame_btn,
            text="◀️ Atrás",
            font=("Segoe UI", 10),
            bg="#e0e0e0",
            width=12,
            command=self._anterior
        ).pack(side='left', padx=(40, 10))

        self.btn_usar_prueba = tk.Button(
            frame_btn,
            text="Usar Prueba",
            font=("Segoe UI", 10),
            bg="#ffc107",
            width=12,
            command=self._usar_trial
        )
        self.btn_usar_prueba.pack(side='left', padx=10)

        tk.Button(
            frame_btn,
            text="Siguiente ▶️",
            font=("Segoe UI", 10, "bold"),
            bg="#28a745",
            fg="white",
            width=12,
            command=self._validar_licencia
        ).pack(side='right', padx=(10, 40))

    def _verificar_email_wizard(self):
        """Verifica el email y determina el estado de la licencia"""
        email = self.entry_email.get().strip()
        if not email:
            messagebox.showwarning("Email requerido", "Ingresa tu email.")
            return

        self.label_estado_email.config(fg="gray", text="⏳ Verificando...")
        self.btn_verificar_email.config(state='disabled')
        self.root.update()

        try:
            url = self.gestor_licencias.url_backend.replace('/verificar-licencia', '/verificar-email')
            resp = requests.get(url, params={'email': email, 'nombreApp': 'PublicadorRedes'}, timeout=30, verify=False)

            if resp.status_code != 200:
                self.label_estado_email.config(fg="#dc3545", text="❌ Error al verificar. Intenta nuevamente.")
                self.btn_verificar_email.config(state='normal')
                return

            datos = resp.json()

            if not datos.get('existe'):
                self.label_estado_email.config(fg="#dc3545", text="❌ Email no encontrado en AutomaPro.")
                messagebox.showerror("Email no registrado",
                    f"El email '{email}' no está registrado.\n\nRegístrate en:\nautomapro-frontend.vercel.app")
                self.btn_verificar_email.config(state='normal')
                return

            tipo = datos.get('tipoLicencia', 'NINGUNA')

            if tipo == 'FULL':
                self.label_estado_email.config(fg="#28a745", text="✅ Email verificado — Licencia Completa encontrada")
                codigo = datos.get('codigo', '')
                self.entry_licencia.config(state='normal')
                self.entry_licencia.delete(0, tk.END)
                self.entry_licencia.insert(0, codigo)
                self.entry_licencia.config(state='disabled')
                self.label_formato.config(fg="#28a745", text="✅ LICENCIA COMPLETA VÁLIDA")
                self.licencia_validada = True
                self.tipo_licencia = 'FULL'
                self.btn_verificar_email.config(state='disabled')
                if hasattr(self, 'btn_usar_prueba'):
                    self.btn_usar_prueba.config(state='disabled')
                self.gestor_licencias.guardar_codigo_licencia(codigo)
                self.gestor_licencias._guardar_cache_local({
                    'tipo': 'FULL',
                    'valida': True,
                    'expirado': False,
                    'diasRestantes': None,
                    'developer_permanente': False
                })

            elif tipo == 'TRIAL':
                dias = datos.get('diasRestantes', 0)
                expirado = datos.get('expirado', False)
                if expirado:
                    self.label_estado_email.config(fg="#dc3545", text="⚠️ Email verificado — Período de prueba expirado")
                    self.entry_licencia.config(state='normal')
                    self.label_formato.config(fg="#ffc107", text="Ingresa tu código de licencia completa")
                    self.btn_verificar_email.config(state='disabled')
                    if hasattr(self, 'btn_usar_prueba'):
                        self.btn_usar_prueba.config(state='disabled')
                else:
                    self.label_estado_email.config(fg="#28a745", text=f"✅ Email verificado — Prueba activa ({dias} días restantes)")
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

        except Exception as e:
            self.label_estado_email.config(fg="#e65100", text="⏳ Servidor iniciando...")
            messagebox.showwarning(
                "Servidor iniciando",
                "El servidor está iniciando. Esto puede tomar hasta 2 minutos.\n\n"
                "Por favor espera un momento e intenta nuevamente."
            )
            self.btn_verificar_email.config(state='normal')

    def _verificar_licencia_tiempo_real(self, codigo):
        """Verifica la licencia en tiempo real mientras el usuario escribe"""
        email = self.entry_email.get().strip()
        self.label_formato.config(fg="gray", text="⏳ Verificando...")
        self.root.update()
        try:
            url = self.gestor_licencias.url_backend.replace('/verificar-licencia', '/verificar-licencia-email')
            resp = requests.get(url, params={'email': email, 'codigo': codigo}, timeout=30, verify=False)
            if resp.status_code == 200:
                datos = resp.json()
                if datos.get('valida'):
                    tipo = datos.get('tipo', 'FULL')
                    self.label_formato.config(fg="#28a745", text=f"✅ LICENCIA {tipo} VÁLIDA")
                    self.licencia_validada = True
                    self.tipo_licencia = tipo
                else:
                    mensaje = datos.get('mensaje', 'Código inválido')
                    self.label_formato.config(fg="#dc3545", text=f"❌ {mensaje}")
                    self.licencia_validada = False
                    self.tipo_licencia = None
            else:
                self.label_formato.config(fg="#dc3545", text="❌ LICENCIA INVÁLIDA")
                self.licencia_validada = False
        except Exception:
            self.label_formato.config(fg="#dc3545", text="❌ Error de conexión")
            self.licencia_validada = False

    def _usar_trial(self):
        """Registra la instalación y activa período de prueba"""
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
        """Valida la licencia antes de continuar"""
        codigo = self.entry_licencia.get().strip().upper()
        email = self.entry_email.get().strip() if hasattr(self, 'entry_email') else ""

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
                f"El código debe tener exactamente 14 caracteres.\n\nFormato: XXX-XXXXXX-XXXXX\nTienes: {len(codigo_limpio)} caracteres")
            return

        if not self.licencia_validada:
            messagebox.showerror("Licencia Inválida", "El código ingresado no es válido.\n\nPor favor verifica el código o usa Prueba.")
            return

        codigo_formateado = f"{codigo_limpio[:3]}-{codigo_limpio[3:9]}-{codigo_limpio[9:]}"
        self.datos_config['codigo_licencia'] = codigo_formateado
        self.gestor_licencias.guardar_codigo_licencia(codigo_formateado)
        self._siguiente()

    def _paso_configuracion(self):
        """Paso 2: Configuración del navegador y módulos"""
        header = tk.Frame(self.root, bg=COLOR_PRINCIPAL, pady=15)
        header.pack(fill='x')
        tk.Label(
            header,
            text="Paso 2 de 3: Configuración",
            font=("Segoe UI", 14, "bold"),
            bg=COLOR_PRINCIPAL,
            fg="white"
        ).pack()

        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill='both', expand=True, padx=40, pady=20)

        tk.Label(frame, text="Navegador:", font=("Segoe UI", 11, "bold"), bg="#f0f0f0").pack(anchor='w', pady=(0, 5))
        self.var_navegador = tk.StringVar(value="firefox")
        tk.Radiobutton(frame, text="Firefox (recomendado)", variable=self.var_navegador,
                       value="firefox", bg="#f0f0f0", font=("Segoe UI", 10)).pack(anchor='w')
        tk.Radiobutton(frame, text="Chrome", variable=self.var_navegador,
                       value="chrome", bg="#f0f0f0", font=("Segoe UI", 10)).pack(anchor='w', pady=(0, 15))

        tk.Label(frame, text="Perfil del navegador:", font=("Segoe UI", 11, "bold"), bg="#f0f0f0").pack(anchor='w', pady=(0, 5))
        self.var_perfil = tk.StringVar(value="si")
        tk.Radiobutton(frame, text="Usar perfil dedicado (recomendado)",
                       variable=self.var_perfil, value="si", bg="#f0f0f0", font=("Segoe UI", 10)).pack(anchor='w')
        tk.Radiobutton(frame, text="Usar perfil existente",
                       variable=self.var_perfil, value="no", bg="#f0f0f0", font=("Segoe UI", 10)).pack(anchor='w', pady=(0, 15))

        tk.Label(frame, text="Nota: Instagram, Twitter y LinkedIn\nrequieren versión Completa.",
                 font=("Segoe UI", 9), bg="#f0f0f0", fg="gray", justify='left').pack(anchor='w')

        frame_btn = tk.Frame(self.root, bg="#f0f0f0", pady=20)
        frame_btn.pack(fill='x', side='bottom')

        tk.Button(frame_btn, text="◀️ Atrás", font=("Segoe UI", 10),
                  bg="#e0e0e0", width=12, command=self._anterior).pack(side='left', padx=(40, 10))

        tk.Button(frame_btn, text="Siguiente ▶️", font=("Segoe UI", 10, "bold"),
                  bg="#28a745", fg="white", width=12, command=self._guardar_config_basica).pack(side='right', padx=(10, 40))

    def _guardar_config_basica(self):
        """Guarda la configuración básica y avanza"""
        self.datos_config['navegador'] = self.var_navegador.get()
        self.datos_config['usar_perfil'] = self.var_perfil.get()
        self._crear_config_completa()
        self._siguiente()

    def _crear_config_completa(self):
        """Crea el archivo config_global.txt"""
        import os
        import sys
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        config = configparser.ConfigParser()
        config['GENERAL'] = {
            'nombre_proyecto': 'Publicador Redes',
            'carpeta_anuncios': 'anuncios',
            'navegador': self.datos_config['navegador'],
            'modo_debug': 'si'
        }
        config['ANUNCIOS'] = {
            'seleccion': 'secuencial',
            'historial_evitar_repetir': '5',
            'agregar_hashtags': 'no',
            'hashtags': '#Marketing,#Publicidad,#Negocios',
            'agregar_firma': 'no',
            'texto_firma': 'Publicado automáticamente'
        }
        config['PUBLICACION'] = {
            'tiempo_entre_intentos': '3',
            'max_intentos_por_publicacion': '3',
            'espera_despues_publicar': '5',
            'verificar_publicacion_exitosa': 'si',
            'espera_estabilizacion_modal': '3'
        }
        config['NAVEGADOR'] = {
            'usar_perfil_existente': self.datos_config['usar_perfil'],
            'carpeta_perfil_custom': 'perfiles/publicador_redes',
            'desactivar_notificaciones': 'si',
            'maximizar_ventana': 'si'
        }
        config['LIMITES'] = {
            'tiempo_minimo_entre_publicaciones_segundos': '120',
            'permitir_duplicados': 'no',
            'permitir_forzar_publicacion_manual': 'si'
        }
        config['MODULOS'] = {
            'publicar_facebook': 'si',
            'publicar_instagram': 'no',
            'publicar_twitter': 'no',
            'publicar_linkedin': 'no'
        }
        config['DEBUG'] = {'modo_debug': 'detallado'}

        archivo = os.path.join(base_dir, 'config_global.txt')
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write("# ============================================================\n")
            f.write("# CONFIGURACIÓN GLOBAL - PUBLICADOR REDES\n")
            f.write("# ============================================================\n\n")
            config.write(f)

    def _paso_finalizar(self):
        """Paso 3: Finalizar configuración"""
        header = tk.Frame(self.root, bg=COLOR_PRINCIPAL, pady=15)
        header.pack(fill='x')
        tk.Label(
            header,
            text="Paso 3 de 3: ¡Todo listo!",
            font=("Segoe UI", 14, "bold"),
            bg=COLOR_PRINCIPAL,
            fg="white"
        ).pack()

        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill='both', expand=True, padx=40, pady=30)

        tk.Label(
            frame,
            text="✅ Configuración completada",
            font=("Segoe UI", 14, "bold"),
            bg="#f0f0f0",
            fg="#28a745"
        ).pack(pady=(0, 20))

        tipo = self.tipo_licencia or 'TRIAL'
        if tipo == 'FULL':
            msg = "🎉 Licencia Completa activada\nTodas las funciones desbloqueadas"
            color = "#28a745"
        else:
            msg = "⚠️ Versión de Prueba activada\n1 publicación/día, solo Facebook"
            color = "#ffc107"

        tk.Label(frame, text=msg, font=("Segoe UI", 11), bg="#f0f0f0", fg=color, justify='center').pack(pady=(0, 20))

        tk.Label(
            frame,
            text="Próximos pasos:\n\n"
                 "1. Agrega tus anuncios en la carpeta 'anuncios/'\n"
                 "2. Abre el Panel de Control\n"
                 "3. Configura las redes sociales\n"
                 "4. ¡Empieza a publicar!",
            font=("Segoe UI", 10),
            bg="#f0f0f0",
            justify='left'
        ).pack(pady=(0, 20))

        frame_btn = tk.Frame(self.root, bg="#f0f0f0", pady=20)
        frame_btn.pack(fill='x', side='bottom')

        tk.Button(
            frame_btn,
            text="🚀 Abrir Panel de Control",
            font=("Segoe UI", 11, "bold"),
            bg=COLOR_PRINCIPAL,
            fg="white",
            width=25,
            command=self._finalizar
        ).pack()

    def _finalizar(self):
        """Finaliza el wizard y abre el Panel de Control"""
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
        except Exception as e:
            print(f"Error abriendo Panel de Control: {e}")
        finally:
            self.root.destroy()

    def _siguiente(self):
        self.paso_actual += 1
        self._mostrar_paso()

    def _anterior(self):
        self.paso_actual -= 1
        self._mostrar_paso()

    def ejecutar(self):
        self.root.mainloop()


if __name__ == "__main__":
    wizard = WizardPrimeraVez()
    wizard.ejecutar()