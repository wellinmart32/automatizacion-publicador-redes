import os
import sys
import tkinter as tk
from tkinter import messagebox
import subprocess
from gestor_licencias import GestorLicencias
from gestor_registro import GestorRegistro
from compartido.toast import Toast

COLOR_PRINCIPAL = "#7c3aed"
COLOR_HOVER     = "#6d28d9"


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

        try:
            base_ico = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
            self.root.iconbitmap(os.path.join(base_ico, 'iconos', 'dashboard.ico'))
        except Exception:
            pass

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

        try:
            ico = os.path.join(self.base_dir, 'iconos', 'dashboard.ico')
            self.root.after(100, lambda: self.root.iconbitmap(ico))
            self.root.after(300, lambda: self.root.iconbitmap(ico))
        except Exception:
            pass

        self._verificar_actualizacion()

    def _exe(self, nombre):
        if getattr(sys, 'frozen', False):
            base = os.path.dirname(sys.executable)
        else:
            base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, nombre)

    def _verificar_licencia(self):
        codigo = self.gestor_licencias.obtener_codigo_guardado()

        if not codigo:
            if getattr(sys, 'frozen', False):
                wizard = os.path.join(os.path.dirname(sys.executable), "WizardPublicador.exe")
            else:
                wizard = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wizard_primera_vez.py")
            if os.path.exists(wizard):
                subprocess.Popen([wizard] if wizard.endswith('.exe') else [sys.executable, wizard])
            else:
                messagebox.showwarning("Sin Licencia", "No hay licencia configurada.")
            return None

        resultado = self.gestor_licencias.verificar_licencia(codigo, mostrar_mensajes=False)

        if not resultado['valida']:
            messagebox.showerror("Licencia Inválida", "Tu licencia no es válida o ha expirado.")
            return None

        tipo = resultado.get('tipo', 'TRIAL')
        if tipo == 'TRIAL':
            dias = resultado.get('diasRestantes', 0)
            if dias is not None and dias <= 0:
                messagebox.showwarning("⏰ Período de Prueba Expirado",
                    "Tu período de prueba ha terminado.\n\nVisita: automapro-frontend.vercel.app")
                self._abrir_upgrade()
                return None

        return resultado

    def _construir_ui(self):
        tipo_licencia = self.licencia.get('tipo', 'TRIAL')
        es_full = tipo_licencia in ['FULL', 'MASTER'] or self.licencia.get('developer_permanente')

        header = tk.Frame(self.root, bg=COLOR_PRINCIPAL, pady=15)
        header.pack(fill='x')

        try:
            with open(os.path.join(self.base_dir, 'version.txt'), 'r', encoding='utf-8') as f:
                version = f.read().strip()
        except Exception:
            version = '1.0.0'

        tk.Label(header, text="🟣 Publicador Redes",
                 font=("Segoe UI", 20, "bold"), bg=COLOR_PRINCIPAL, fg="white").pack()
        tk.Label(header, text=f"v{version}",
                 font=("Segoe UI", 9), bg=COLOR_PRINCIPAL, fg="#d8c8f8").pack()

        if self.licencia.get('developer_permanente'):
            texto_lic, color_lic = "👑 LICENCIA MAESTRA", "#6f42c1"
        elif tipo_licencia == "FULL":
            texto_lic, color_lic = "✅ LICENCIA COMPLETA", "#28a745"
        else:
            dias = self.licencia.get('diasRestantes', 0)
            texto_lic, color_lic = f"⚠️  PRUEBA — {dias} días restantes", "#e65100"

        tk.Label(header, text=texto_lic, font=("Segoe UI", 10, "bold"),
                 bg=color_lic, fg="white", padx=15, pady=4).pack(pady=(8, 0))

        if not es_full:
            banner = tk.Frame(self.root, bg="#fff3cd", pady=8)
            banner.pack(fill='x')
            tk.Label(banner,
                     text="🔓 Desbloquea Instagram, Twitter, LinkedIn y más con la versión Completa",
                     font=("Segoe UI", 9), bg="#fff3cd", fg="#856404").pack(side='left', padx=(15, 10))
            tk.Button(banner, text="⬆️ Comprar versión Completa",
                      font=("Segoe UI", 9, "bold"), bg="#ffc107", fg="#212529",
                      cursor="hand2", relief='flat', padx=10,
                      command=self._abrir_upgrade).pack(side='right', padx=(0, 15))

        container = tk.Frame(self.root, bg="#f0f0f0")
        container.pack(fill='both', expand=True, padx=25, pady=15)
        grid = tk.Frame(container, bg="#f0f0f0")
        grid.pack(fill='both', expand=True)
        self._botones_grid = []

        self._boton(grid, "⚡\nAcciones", "Publicar y automatizar",
                    self._abrir_acciones, row=0, col=0, color="#e65100")
        self._boton(grid, "⚙️\nConfigurador", "Ajustar configuración",
                    self._abrir_configurador, row=0, col=1, en_hilo=True)

        if es_full:
            self._boton(grid, "📢\nAnuncios", "Gestionar anuncios",
                        self._abrir_gestor_anuncios, row=1, col=0, en_hilo=True)
        else:
            self._boton(grid, "📢\nAnuncios", "Ver carpeta de anuncios",
                        self._abrir_carpeta_anuncios, row=1, col=0)
        self._boton(grid, "📊\nEstadísticas", "Ver historial",
                    self._ver_estadisticas, row=1, col=1)

        if es_full:
            self._boton(grid, "🗓️\nTareas Automáticas", "Programar publicaciones",
                        self._gestionar_tareas, row=2, col=0, color="#28a745", en_hilo=True)
        else:
            self._boton(grid, "🔒\nTareas Automáticas", "Solo versión Completa",
                        self._mostrar_mensaje_upgrade, row=2, col=0, color="#9e9e9e")
        self._boton(grid, "❓\nAyuda", "Cómo usar el sistema",
                    self._mostrar_ayuda, row=2, col=1)
        self._boton(grid, "❌\nSalir", "Cerrar panel",
                    self.root.destroy, row=3, col=0, color="#dc3545")

        footer = tk.Frame(self.root, bg="#e0e0e0", pady=8)
        footer.pack(fill='x', side='bottom')
        tk.Label(footer, text="AutomaPro — PublicadorRedes v1.0.0",
                 font=("Segoe UI", 9), bg="#e0e0e0", fg="#666").pack()

    def _boton(self, parent, texto, subtexto, comando, row, col, color="white", en_hilo=False):
        frame = tk.Frame(parent, bg="white", relief='solid', bd=1, cursor="hand2")
        frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        parent.grid_columnconfigure(col, weight=1)
        parent.grid_rowconfigure(row, weight=1)

        es_coloreado = color != "white"
        bg_texto = color if es_coloreado else "white"
        fg_texto = "white" if es_coloreado else COLOR_PRINCIPAL

        lbl_titulo = tk.Label(frame, text=texto, font=("Segoe UI", 11, "bold"),
                              bg=bg_texto, fg=fg_texto, justify='center')
        lbl_titulo.pack(pady=(15, 5), fill='both', expand=True)

        lbl_sub = tk.Label(frame, text=subtexto, font=("Segoe UI", 8),
                           bg=bg_texto, fg="white" if es_coloreado else "gray", justify='center')
        lbl_sub.pack(pady=(0, 15))

        if es_coloreado:
            frame.config(bg=color)

        frame._cmd = comando
        frame._en_hilo = en_hilo
        frame._color = color
        widgets = [lbl_titulo, lbl_sub]
        self._botones_grid.append((frame, widgets))

        accion = (lambda c=comando: self._lanzar_en_hilo(c)) if en_hilo else comando

        def _on_enter(e, f=frame, ws=widgets, c=color):
            bg_h = "#f3e8ff" if c == "white" else c
            f.config(bg=bg_h)
            for w in ws:
                w.config(bg=bg_h)

        def _on_leave(e, f=frame, ws=widgets, c=color):
            f.config(bg=c)
            for w in ws:
                w.config(bg=c)

        frame.bind('<Button-1>', lambda e, a=accion: a())
        frame.bind('<Enter>', _on_enter)
        frame.bind('<Leave>', _on_leave)
        for w in widgets:
            w.bind('<Button-1>', lambda e, a=accion: a())
            w.bind('<Enter>', _on_enter)
            w.bind('<Leave>', _on_leave)

    def _bloquear_grid(self):
        self.root.config(cursor="wait")
        for frame, widgets in self._botones_grid:
            frame.config(cursor="", bg="#e0e0e0")
            for w in widgets:
                w.config(bg="#e0e0e0")
                w.unbind('<Button-1>')
                w.unbind('<Enter>')
                w.unbind('<Leave>')
            frame.unbind('<Button-1>')
            frame.unbind('<Enter>')
            frame.unbind('<Leave>')

    def _desbloquear_grid(self):
        self.root.config(cursor="")
        for frame, widgets in self._botones_grid:
            color_orig = getattr(frame, '_color', 'white')
            bg_orig = color_orig if color_orig != "white" else "white"
            frame.config(cursor="hand2", bg=bg_orig)
            cmd = frame._cmd
            en_hilo = frame._en_hilo
            accion = (lambda c=cmd: self._lanzar_en_hilo(c)) if en_hilo else cmd

            def _on_enter(e, f=frame, ws=widgets, c=color_orig):
                bg_h = "#f3e8ff" if c == "white" else c
                f.config(bg=bg_h)
                for w in ws:
                    w.config(bg=bg_h)

            def _on_leave(e, f=frame, ws=widgets, c=color_orig):
                f.config(bg=c)
                for w in ws:
                    w.config(bg=c)

            for w in widgets:
                w.config(bg=bg_orig)
                w.bind('<Button-1>', lambda e, a=accion: a())
                w.bind('<Enter>', _on_enter)
                w.bind('<Leave>', _on_leave)
            frame.bind('<Button-1>', lambda e, a=accion: a())
            frame.bind('<Enter>', _on_enter)
            frame.bind('<Leave>', _on_leave)
        self.root.update_idletasks()
        self.root.update()
        self.root.after(100, self._refrescar_ventana)

    def _refrescar_ventana(self):
        try:
            self.root.withdraw()
            self.root.after(50, self.root.deiconify)
        except Exception:
            pass

    def _lanzar_en_hilo(self, cmd):
        self._bloquear_grid()
        import threading
        def _hilo():
            try:
                cmd()
            finally:
                self.root.after(0, self._desbloquear_grid)
        threading.Thread(target=_hilo, daemon=True).start()

    def _centrar_ventana(self, ventana, ancho, alto):
        x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
        y = (ventana.winfo_screenheight() // 2) - (alto // 2)
        ventana.geometry(f'{ancho}x{alto}+{x}+{y}')

    # ==================== VENTANA ACCIONES ====================

    def _abrir_acciones(self):
        tipo_licencia = self.licencia.get('tipo', 'TRIAL')
        es_full = tipo_licencia in ['FULL', 'MASTER'] or self.licencia.get('developer_permanente')

        ventana = tk.Toplevel(self.root)
        ventana.withdraw()
        ventana.title("⚡ Acciones")
        ventana.resizable(False, False)
        ventana.configure(bg="#f0f0f0")
        ventana.transient(self.root)
        ventana.grab_set()

        header = tk.Frame(ventana, bg="#e65100", pady=12)
        header.pack(fill='x')
        tk.Label(header, text="⚡ Acciones",
                 font=("Segoe UI", 14, "bold"), bg="#e65100", fg="white").pack()
        tk.Label(header, text="Selecciona qué deseas ejecutar",
                 font=("Segoe UI", 9), bg="#e65100", fg="white").pack()

        frame = tk.Frame(ventana, bg="#f0f0f0")
        frame.pack(fill='both', expand=True, padx=20, pady=20)

        def _cerrar_y(comando):
            ventana.grab_release()
            ventana.destroy()
            comando()

        # Botón 1 — Ejecutar Secuencia
        tk.Button(frame,
            text="⚡  Ejecutar Secuencia Configurada",
            font=("Segoe UI", 12, "bold"),
            bg="#e65100", fg="white",
            cursor="hand2", anchor='w', padx=20, pady=12,
            command=lambda: _cerrar_y(self._ejecutar_secuencia)
        ).pack(fill='x', pady=(0, 8))
        tk.Label(frame, text="Corre todos los módulos activados en el Configurador → Secuencia",
                 font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(anchor='w', pady=(0, 15))

        tk.Frame(frame, bg="#e0e0e0", height=1).pack(fill='x', pady=(0, 15))

        # Botón 2 — Publicar
        tk.Button(frame,
            text="📢  Publicar",
            font=("Segoe UI", 12, "bold"),
            bg="#1877f2", fg="white",
            cursor="hand2", anchor='w', padx=20, pady=12,
            command=lambda: _cerrar_y(lambda: self._abrir_submenu_publicar(es_full))
        ).pack(fill='x', pady=(0, 8))
        tk.Label(frame, text="Publica un anuncio en Facebook, Instagram, Twitter/X o LinkedIn",
                 font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(anchor='w', pady=(0, 15))

        tk.Frame(frame, bg="#e0e0e0", height=1).pack(fill='x', pady=(0, 15))

        # Botón 3 — Contactos
        btn_contactos_color = "#7c3aed" if es_full else "#e0e0e0"
        btn_contactos_fg = "white" if es_full else "#9e9e9e"
        tk.Button(frame,
            text="👥  Contactos" if es_full else "🔒  Contactos  —  versión Completa",
            font=("Segoe UI", 12, "bold") if es_full else ("Segoe UI", 12),
            bg=btn_contactos_color, fg=btn_contactos_fg,
            cursor="hand2", anchor='w', padx=20, pady=12,
            command=lambda: _cerrar_y(lambda: self._abrir_submenu_contactos(es_full)) if es_full else self._mostrar_mensaje_upgrade
        ).pack(fill='x', pady=(0, 8))
        tk.Label(frame, text="Envía solicitudes de amistad o sigue usuarios en redes sociales",
                 font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(anchor='w', pady=(0, 15))

        tk.Button(frame, text="Cancelar", font=("Segoe UI", 10),
                  bg="#6c757d", fg="white", width=12,
                  command=lambda: [ventana.grab_release(), ventana.destroy()]
                  ).pack(pady=(5, 0))

        ventana.protocol("WM_DELETE_WINDOW",
                         lambda: [ventana.grab_release(), ventana.destroy()])
        self._centrar_ventana(ventana, 460, 480)
        ventana.deiconify()

    def _abrir_submenu_publicar(self, es_full):
        """Submenú de publicación por red social"""
        ventana = tk.Toplevel(self.root)
        ventana.withdraw()
        ventana.title("📢 Publicar")
        ventana.resizable(False, False)
        ventana.configure(bg="#f0f0f0")
        ventana.transient(self.root)
        ventana.grab_set()

        header = tk.Frame(ventana, bg="#1877f2", pady=12)
        header.pack(fill='x')
        tk.Label(header, text="📢 Publicar",
                 font=("Segoe UI", 13, "bold"), bg="#1877f2", fg="white").pack()

        frame = tk.Frame(ventana, bg="#f0f0f0")
        frame.pack(fill='both', expand=True, padx=20, pady=15)

        def _cerrar_y(cmd):
            ventana.grab_release()
            ventana.destroy()
            cmd()

        def _boton(texto, color, cmd, activo=True):
            tk.Button(frame,
                text=texto if activo else f"🔒  {texto[2:].strip()}  —  versión Completa",
                font=("Segoe UI", 11, "bold") if activo else ("Segoe UI", 10),
                bg=color if activo else "#e0e0e0",
                fg="white" if activo else "#9e9e9e",
                cursor="hand2", anchor='w', padx=15, pady=8,
                command=lambda: _cerrar_y(cmd) if activo else self._mostrar_mensaje_upgrade
            ).pack(fill='x', pady=(0, 6))

        _boton("📘  Facebook", "#1877f2", self._publicar_facebook)
        _boton("📸  Instagram", "#e1306c", self._publicar_instagram, activo=es_full)
        _boton("🐦  Twitter/X", "#1da1f2", self._publicar_twitter, activo=es_full)
        _boton("💼  LinkedIn", "#0077b5", self._publicar_linkedin, activo=es_full)

        tk.Button(frame, text="← Volver", font=("Segoe UI", 10),
                  bg="#6c757d", fg="white", width=12,
                  command=lambda: [ventana.grab_release(), ventana.destroy(),
                                   self._abrir_acciones()]
                  ).pack(pady=(10, 0))

        ventana.protocol("WM_DELETE_WINDOW",
                         lambda: [ventana.grab_release(), ventana.destroy()])
        self._centrar_ventana(ventana, 400, 340)
        ventana.deiconify()

    def _abrir_submenu_contactos(self, es_full):
        """Submenú de contactos por red social"""
        ventana = tk.Toplevel(self.root)
        ventana.withdraw()
        ventana.title("👥 Contactos")
        ventana.resizable(False, False)
        ventana.configure(bg="#f0f0f0")
        ventana.transient(self.root)
        ventana.grab_set()

        header = tk.Frame(ventana, bg="#7c3aed", pady=12)
        header.pack(fill='x')
        tk.Label(header, text="👥 Contactos",
                 font=("Segoe UI", 13, "bold"), bg="#7c3aed", fg="white").pack()

        frame = tk.Frame(ventana, bg="#f0f0f0")
        frame.pack(fill='both', expand=True, padx=20, pady=15)

        def _cerrar_y(cmd):
            ventana.grab_release()
            ventana.destroy()
            cmd()

        def _boton(texto, color, cmd):
            tk.Button(frame,
                text=texto,
                font=("Segoe UI", 11, "bold"),
                bg=color, fg="white",
                cursor="hand2", anchor='w', padx=15, pady=8,
                command=lambda: _cerrar_y(cmd)
            ).pack(fill='x', pady=(0, 6))

        _boton("📘  Solicitudes de Amistad — Facebook", "#1877f2", self._solicitudes_facebook)
        _boton("📸  Seguir Usuarios — Instagram", "#e1306c", self._seguir_instagram)
        _boton("🐦  Seguir Usuarios — Twitter/X", "#1da1f2", self._seguir_twitter)
        _boton("💼  Solicitudes de Conexión — LinkedIn", "#0077b5", self._conexiones_linkedin)

        tk.Button(frame, text="← Volver", font=("Segoe UI", 10),
                  bg="#6c757d", fg="white", width=12,
                  command=lambda: [ventana.grab_release(), ventana.destroy(),
                                   self._abrir_acciones()]
                  ).pack(pady=(10, 0))

        ventana.protocol("WM_DELETE_WINDOW",
                         lambda: [ventana.grab_release(), ventana.destroy()])
        self._centrar_ventana(ventana, 400, 340)
        ventana.deiconify()

    def _ejecutar_secuencia(self):
        """Ejecuta la secuencia completa configurada"""
        self._lanzar_exe()
        self._toast("⚡ Secuencia iniciada", "Ejecutando módulos configurados...")

    # ==================== MÉTODOS DE ACCIÓN ====================

    def _lanzar_exe(self, argumento=None):
        """Lanza PublicadorRedes.exe con argumento opcional — muestra consola"""
        exe = self._exe("PublicadorRedes.exe")
        if os.path.exists(exe):
            cmd = [exe] + ([argumento] if argumento else [])
        else:
            cmd = [sys.executable, os.path.join(self.base_dir, "publicar_redes.py")]
            if argumento:
                cmd.append(argumento)
        subprocess.Popen(cmd)

    def _publicar_facebook(self):
        self._lanzar_exe()
        self._toast("🚀 Publicación iniciada", "El navegador se abrirá en unos segundos...")

    def _solicitudes_facebook(self):
        self._lanzar_exe("--solicitudes-facebook")
        self._toast("👥 Enviando solicitudes", "Facebook — consola abierta...")

    def _publicar_instagram(self):
        self._lanzar_exe("--publicar-instagram")
        self._toast("📸 Publicando en Instagram", "El navegador se abrirá en unos segundos...")

    def _seguir_instagram(self):
        self._lanzar_exe("--seguir-instagram")
        self._toast("👥 Siguiendo usuarios", "Instagram — consola abierta...")

    def _publicar_twitter(self):
        self._lanzar_exe("--publicar-twitter")
        self._toast("🐦 Publicando en Twitter/X", "El navegador se abrirá en unos segundos...")

    def _seguir_twitter(self):
        self._lanzar_exe("--seguir-twitter")
        self._toast("👥 Siguiendo usuarios", "Twitter/X — consola abierta...")

    def _publicar_linkedin(self):
        self._lanzar_exe("--publicar-linkedin")
        self._toast("💼 Publicando en LinkedIn", "El navegador se abrirá en unos segundos...")

    def _conexiones_linkedin(self):
        self._lanzar_exe("--conexiones-linkedin")
        self._toast("👥 Enviando conexiones", "LinkedIn — consola abierta...")

    # ==================== OTROS MÉTODOS ====================

    def _abrir_configurador(self):
        try:
            exe = self._exe("ConfiguradorRedes.exe")
            if os.path.exists(exe):
                subprocess.run([exe])
            else:
                subprocess.run([sys.executable,
                                os.path.join(self.base_dir, "configurador_gui.py")])
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo abrir el configurador:\n{e}")

    def _abrir_gestor_anuncios(self):
        try:
            exe = self._exe("GestorAnuncios.exe")
            if os.path.exists(exe):
                subprocess.run([exe])
            else:
                subprocess.run([sys.executable,
                                os.path.join(self.base_dir, "gestor_anuncios.py")])
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo abrir el gestor de anuncios:\n{e}")

    def _abrir_carpeta_anuncios(self):
        import subprocess as sp
        carpeta = os.path.join(self.base_dir, "anuncios")
        os.makedirs(carpeta, exist_ok=True)
        sp.Popen(f'explorer "{carpeta}"')
        self._toast("📢 Tus Anuncios",
                    "Carpeta abierta — versión Completa incluye editor visual", duracion=5000)

    def _gestionar_tareas(self):
        try:
            exe = self._exe("GestorTareasRedes.exe")
            if os.path.exists(exe):
                subprocess.run([exe])
            else:
                messagebox.showerror("❌ Error", "No se encontró GestorTareasRedes.exe")
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo abrir el gestor de tareas:\n{e}")

    def _ver_estadisticas(self):
        try:
            gestor = GestorRegistro()
            stats = gestor.obtener_estadisticas()

            ventana = tk.Toplevel(self.root)
            ventana.withdraw()
            ventana.title("📊 Estadísticas")
            ventana.resizable(False, False)
            ventana.configure(bg="#f0f0f0")
            ventana.transient(self.root)
            ventana.grab_set()

            header = tk.Frame(ventana, bg=COLOR_PRINCIPAL, pady=12)
            header.pack(fill='x')
            tk.Label(header, text="📊 Estadísticas de Publicación",
                     font=("Segoe UI", 13, "bold"), bg=COLOR_PRINCIPAL, fg="white").pack()

            frame = tk.Frame(ventana, bg="white", padx=30, pady=20)
            frame.pack(fill='both', expand=True, padx=20, pady=15)

            fecha_ultima = stats.get('ultima_publicacion', 'Nunca')
            if fecha_ultima and fecha_ultima != 'Nunca':
                fecha_ultima = fecha_ultima[:19]

            items = [
                ("📦 Total publicaciones:", str(stats.get('total', 0))),
                ("✅ Exitosas:", str(stats.get('exitosas', 0))),
                ("❌ Fallidas:", str(stats.get('fallidas', 0))),
                ("🎯 Tasa de éxito:", f"{stats.get('tasa_exito', 0)}%"),
                ("📅 Última publicación:", fecha_ultima),
            ]

            for label, valor in items:
                row = tk.Frame(frame, bg="white")
                row.pack(fill='x', pady=5)
                tk.Label(row, text=label, font=("Segoe UI", 10, "bold"),
                         bg="white", anchor='w', width=25).pack(side='left')
                tk.Label(row, text=valor, font=("Segoe UI", 10),
                         bg="white", anchor='w').pack(side='left')

            tk.Button(ventana, text="Cerrar", font=("Segoe UI", 10),
                      bg="#6c757d", fg="white", width=12,
                      command=lambda: [ventana.grab_release(), ventana.destroy()]
                      ).pack(pady=15)

            ventana.protocol("WM_DELETE_WINDOW",
                             lambda: [ventana.grab_release(), ventana.destroy()])
            self._centrar_ventana(ventana, 400, 370)
            ventana.deiconify()

        except Exception as e:
            messagebox.showerror("❌ Error", f"Error mostrando estadísticas:\n{e}")

    def _mostrar_ayuda(self):
        ventana = tk.Toplevel(self.root)
        ventana.withdraw()
        ventana.title("❓ Centro de Ayuda")
        ventana.resizable(False, False)
        ventana.configure(bg="#f0f0f0")
        ventana.transient(self.root)
        ventana.grab_set()

        TEMAS = [
            ("⚡  Acciones",
             "⚡ ACCIONES\n\n"
             "Abre el menú de acciones disponibles según tu licencia.\n\n"
             "Acciones disponibles:\n"
             "• Publicar en Facebook (siempre disponible)\n"
             "• Enviar Solicitudes de Amistad en Facebook (versión Completa)\n"
             "• Publicar en Instagram, Twitter/X, LinkedIn (versión Completa)\n"
             "• Seguir usuarios / Enviar solicitudes de conexión (versión Completa)"),
            ("📢  Gestionar Anuncios",
             "📢 GESTIONAR ANUNCIOS\n\n"
             "Editor visual para crear, editar y organizar los anuncios.\n\n"
             "Estructura:\n"
             "• anuncios/anuncio_001/datos.txt\n"
             "• anuncios/anuncio_001/imagenes/\n"
             "• anuncios/anuncio_001/videos/\n\n"
             "⚠️ Requiere versión Completa"),
            ("⚙️  Configurador",
             "⚙️ CONFIGURADOR\n\n"
             "Panel de configuración del sistema.\n\n"
             "• General → navegador, perfil\n"
             "• Anuncios → selección, hashtags\n"
             "• Publicación → tiempos, reintentos\n"
             "• Módulos → activar/desactivar redes\n\n"
             "Recuerda presionar 💾 Guardar."),
            ("📊  Estadísticas",
             "📊 ESTADÍSTICAS\n\n"
             "Resumen del historial de publicaciones:\n"
             "• Total, exitosas y fallidas\n"
             "• Tasa de éxito\n"
             "• Última publicación"),
            ("🗓️  Tareas Automáticas",
             "🗓️ TAREAS AUTOMÁTICAS\n\n"
             "Programa publicaciones automáticas.\n\n"
             "• Días y hora de ejecución\n"
             "• Usa el Programador de Tareas de Windows\n\n"
             "⚠️ Requiere versión Completa"),
        ]

        header = tk.Frame(ventana, bg=COLOR_PRINCIPAL, pady=12)
        header.pack(fill='x')
        tk.Label(header, text="❓ Centro de Ayuda",
                 font=("Segoe UI", 13, "bold"), bg=COLOR_PRINCIPAL, fg="white").pack()

        cuerpo = tk.Frame(ventana, bg="#f0f0f0")
        cuerpo.pack(fill='both', expand=True, padx=10, pady=10)

        panel_izq = tk.Frame(cuerpo, bg="#f0f0f0", width=200)
        panel_izq.pack(side='left', fill='y', padx=(0, 5))
        panel_izq.pack_propagate(False)

        panel_der = tk.Frame(cuerpo, bg="white", relief='solid', bd=1)
        panel_der.pack(side='left', fill='both', expand=True)

        scroll = tk.Scrollbar(panel_der)
        texto_detalle = tk.Text(panel_der, wrap='word', font=("Segoe UI", 10),
                                bg="white", relief='flat', padx=15, pady=15,
                                state='disabled', yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        texto_detalle.pack(fill='both', expand=True)

        botones = []

        def seleccionar(idx):
            for i, btn in enumerate(botones):
                btn.config(bg=COLOR_PRINCIPAL if i == idx else "white",
                           fg="white" if i == idx else "#333")
            texto_detalle.config(state='normal')
            texto_detalle.delete('1.0', tk.END)
            texto_detalle.insert(tk.END, TEMAS[idx][1])
            texto_detalle.config(state='disabled')

        for i, (nombre, _) in enumerate(TEMAS):
            btn = tk.Button(panel_izq, text=nombre, font=("Segoe UI", 9),
                            bg="white", fg="#333", anchor='w', padx=8, pady=5,
                            relief='solid', borderwidth=1, cursor="hand2",
                            command=lambda idx=i: seleccionar(idx))
            btn.pack(fill='x', pady=2)
            botones.append(btn)

        seleccionar(0)

        tk.Button(ventana, text="Cerrar", font=("Segoe UI", 10),
                  bg="#6c757d", fg="white", width=12,
                  command=lambda: [ventana.grab_release(), ventana.destroy()]
                  ).pack(pady=10)

        ventana.protocol("WM_DELETE_WINDOW",
                         lambda: [ventana.grab_release(), ventana.destroy()])
        self._centrar_ventana(ventana, 780, 520)
        ventana.deiconify()

    def _abrir_upgrade(self):
        import webbrowser
        try:
            codigo = self.gestor_licencias.obtener_codigo_guardado()
            url = f"https://automapro-frontend.vercel.app/cliente/comprar?codigo={codigo}&app=2"
            webbrowser.open(url)
        except Exception:
            webbrowser.open("https://automapro-frontend.vercel.app/catalogo")

    def _mostrar_mensaje_upgrade(self):
        messagebox.showinfo("🔒 Versión Completa requerida",
                            "Esta función requiere la versión Completa.\n\n"
                            "Visita: automapro-frontend.vercel.app\n"
                            "Precio: $19.99 USD (pago único)")

    def _verificar_actualizacion(self):
        import threading
        def consultar():
            try:
                with open(os.path.join(self.base_dir, 'version.txt'), 'r') as f:
                    version_local = f.read().strip()
            except Exception:
                version_local = "1.0.0"
            resultado = self.gestor_licencias.verificar_actualizacion(version_local)
            if resultado.get('hay_actualizacion'):
                version_nueva = resultado.get('version_nueva')
                ruta_archivo = resultado.get('ruta_archivo', '')
                self.root.after(0, lambda: self._mostrar_ventana_actualizacion(version_nueva, ruta_archivo))
        threading.Thread(target=consultar, daemon=True).start()

    def _mostrar_ventana_actualizacion(self, version_nueva, ruta_archivo):
        import urllib.request, tempfile, threading
        from tkinter import ttk

        ventana = tk.Toplevel(self.root)
        ventana.title("Actualización Disponible")
        ventana.resizable(False, False)
        ventana.configure(bg="#f0f0f0")
        ventana.grab_set()
        ventana.withdraw()

        w, h = 420, 280
        x = (ventana.winfo_screenwidth() // 2) - (w // 2)
        y = (ventana.winfo_screenheight() // 2) - (h // 2)
        ventana.geometry(f"{w}x{h}+{x}+{y}")
        ventana.deiconify()

        header = tk.Frame(ventana, bg=COLOR_PRINCIPAL, pady=15)
        header.pack(fill='x')
        tk.Label(header, text="🔄  Actualización Disponible",
                 font=("Segoe UI", 13, "bold"), bg=COLOR_PRINCIPAL, fg="white").pack()

        cuerpo = tk.Frame(ventana, bg="#f0f0f0", padx=30, pady=15)
        cuerpo.pack(fill='both', expand=True)

        try:
            with open(os.path.join(self.base_dir, 'version.txt'), 'r') as f:
                version_local = f.read().strip()
        except Exception:
            version_local = "1.0.0"

        tk.Label(cuerpo, text=f"Versión actual:      {version_local}",
                 font=("Segoe UI", 10), bg="#f0f0f0", anchor='w').pack(fill='x')
        tk.Label(cuerpo, text=f"Nueva versión:       {version_nueva}",
                 font=("Segoe UI", 10, "bold"), bg="#f0f0f0",
                 fg=COLOR_PRINCIPAL, anchor='w').pack(fill='x', pady=(0, 10))
        tk.Label(cuerpo, text="Hay una nueva versión disponible.\nHaz clic en Actualizar para instalarla.",
                 font=("Segoe UI", 10), bg="#f0f0f0", justify='left').pack(fill='x')

        barra = ttk.Progressbar(ventana, mode='indeterminate')

        def actualizar_ahora():
            if not ruta_archivo:
                messagebox.showwarning("Sin enlace", "No hay enlace de descarga disponible.")
                return
            barra.pack(fill='x', padx=30, pady=(0, 10))
            barra.start()
            btn_actualizar.config(state='disabled')

            def _descargar():
                try:
                    tmp = tempfile.mktemp(suffix='.exe')
                    urllib.request.urlretrieve(ruta_archivo, tmp)
                    ventana.after(0, lambda: [barra.stop(), subprocess.Popen([tmp]), ventana.destroy()])
                except Exception as ex:
                    ventana.after(0, lambda: [barra.stop(),
                                              messagebox.showerror("Error", f"No se pudo descargar:\n{ex}")])
            threading.Thread(target=_descargar, daemon=True).start()

        btn_actualizar = tk.Button(ventana, text="⬆️ Actualizar ahora",
                                   font=("Segoe UI", 10, "bold"),
                                   bg=COLOR_PRINCIPAL, fg="white", width=18,
                                   command=actualizar_ahora)
        btn_actualizar.pack(side='left', padx=(30, 10), pady=10)
        tk.Button(ventana, text="Ahora no", font=("Segoe UI", 10),
                  bg="#6c757d", fg="white", width=12,
                  command=ventana.destroy).pack(side='right', padx=(0, 30), pady=10)

    def _toast(self, titulo, mensaje="", duracion=3000, color="#28a745"):
        if color == Toast.COLOR_ERROR or color == "#dc3545":
            Toast.error(self.root, f"{titulo}\n{mensaje}", duracion)
        elif color == Toast.COLOR_ADVERTENCIA or color == "#e65100":
            Toast.advertencia(self.root, f"{titulo}\n{mensaje}", duracion)
        elif color == Toast.COLOR_INFO or color == COLOR_PRINCIPAL:
            Toast.info(self.root, f"{titulo}\n{mensaje}", duracion)
        else:
            Toast.exito(self.root, f"{titulo}\n{mensaje}", duracion)

    def ejecutar(self):
        self.root.mainloop()


def _verificar_wizard_completado():
    gestor = GestorLicencias("PublicadorRedes")
    if not gestor.archivo_config.exists():
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
            wizard = os.path.join(base_dir, "WizardPublicador.exe")
        else:
            wizard = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wizard_primera_vez.py")
        if os.path.exists(wizard):
            subprocess.Popen([wizard] if wizard.endswith('.exe') else [sys.executable, wizard])
        else:
            root = tk.Tk()
            root.withdraw()
            messagebox.showwarning("Configuración requerida",
                                   "Por favor ejecuta WizardPublicador.exe para configurar el sistema.")
            root.destroy()
        return False
    return True


def main():
    if not _verificar_wizard_completado():
        return
    panel = PanelControl()
    panel.ejecutar()


if __name__ == "__main__":
    main()