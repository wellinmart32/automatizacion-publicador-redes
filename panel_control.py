import os
import sys
import tkinter as tk
from tkinter import messagebox
import subprocess
from gestor_licencias import GestorLicencias
from gestor_registro import GestorRegistro
from compartido.toast import Toast

# Color principal de PublicadorRedes
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

        # Reaplicar icono múltiples veces para garantizar que Windows lo aplique
        try:
            ico = os.path.join(self.base_dir, 'iconos', 'dashboard.ico')
            self.root.after(100, lambda: self.root.iconbitmap(ico))
            self.root.after(300, lambda: self.root.iconbitmap(ico))
        except Exception:
            pass

        self._verificar_actualizacion()

    def _exe(self, nombre):
        """Retorna ruta al .exe en la misma carpeta del ejecutable"""
        if getattr(sys, 'frozen', False):
            base = os.path.dirname(sys.executable)
        else:
            base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, nombre)

    def _verificar_licencia(self):
        """Verifica licencia — usa caché si no hay código guardado (caso TRIAL)"""
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
            messagebox.showerror("Licencia Inválida", "Tu licencia no es válida o ha expirado.")
            return None

        # Verificar expiración para licencias TRIAL
        tipo = resultado.get('tipo', 'TRIAL')
        if tipo == 'TRIAL':
            dias = resultado.get('diasRestantes', 0)
            if dias is not None and dias <= 0:
                messagebox.showwarning(
                    "⏰ Período de Prueba Expirado",
                    "Tu período de prueba ha terminado.\n\n"
                    "Adquiere la versión Completa para seguir usando todas las funciones.\n\n"
                    "Visita: automapro-frontend.vercel.app"
                )
                self._abrir_upgrade()
                return None

        return resultado

    def _construir_ui(self):
        """Construye la interfaz del panel"""
        tipo_licencia = self.licencia.get('tipo', 'TRIAL')
        es_full = tipo_licencia in ['FULL', 'MASTER'] or self.licencia.get('developer_permanente')

        # ==================== HEADER ====================
        header = tk.Frame(self.root, bg=COLOR_PRINCIPAL, pady=15)
        header.pack(fill='x')

        try:
            ruta_version = os.path.join(self.base_dir, 'version.txt')
            with open(ruta_version, 'r', encoding='utf-8') as f:
                version = f.read().strip()
        except Exception:
            version = '1.0.0'

        tk.Label(
            header,
            text="🟣 Publicador Redes",
            font=("Segoe UI", 20, "bold"),
            bg=COLOR_PRINCIPAL,
            fg="white"
        ).pack()

        tk.Label(
            header,
            text=f"v{version}",
            font=("Segoe UI", 9),
            bg=COLOR_PRINCIPAL,
            fg="#d8c8f8"
        ).pack()

        # Badge de licencia
        if self.licencia.get('developer_permanente'):
            texto_lic = "👑 LICENCIA MAESTRA"
            color_lic = "#6f42c1"
        elif tipo_licencia == "FULL":
            texto_lic = "✅ LICENCIA COMPLETA"
            color_lic = "#28a745"
        else:
            dias = self.licencia.get('diasRestantes', 0)
            texto_lic = f"⚠️  PRUEBA — {dias} días restantes"
            color_lic = "#e65100"

        tk.Label(
            header,
            text=texto_lic,
            font=("Segoe UI", 10, "bold"),
            bg=color_lic,
            fg="white",
            padx=15,
            pady=4
        ).pack(pady=(8, 0))

        # Banner upgrade (solo TRIAL)
        if not es_full:
            banner = tk.Frame(self.root, bg="#fff3cd", pady=8)
            banner.pack(fill='x')
            tk.Label(
                banner,
                text="🔓 Desbloquea Instagram, Twitter, LinkedIn y más con la versión Completa",
                font=("Segoe UI", 9),
                bg="#fff3cd",
                fg="#856404"
            ).pack(side='left', padx=(15, 10))
            tk.Button(
                banner,
                text="⬆️ Comprar versión Completa",
                font=("Segoe UI", 9, "bold"),
                bg="#ffc107",
                fg="#212529",
                cursor="hand2",
                relief='flat',
                padx=10,
                command=self._abrir_upgrade
            ).pack(side='right', padx=(0, 15))

        # ==================== GRID PRINCIPAL ====================
        container = tk.Frame(self.root, bg="#f0f0f0")
        container.pack(fill='both', expand=True, padx=25, pady=15)

        grid = tk.Frame(container, bg="#f0f0f0")
        grid.pack(fill='both', expand=True)

        self._botones_grid = []

        # Fila 0
        self._boton(grid, "⚡\nPublicar Ahora", "Publicar anuncio en redes",
                    self._publicar_ahora, row=0, col=0, color="#e65100")
        self._boton(grid, "⚙️\nConfigurador", "Ajustar configuración",
                    self._abrir_configurador, row=0, col=1, en_hilo=True)

        # Fila 1
        if es_full:
            self._boton(grid, "📢\nAnuncios", "Gestionar anuncios",
                        self._abrir_gestor_anuncios, row=1, col=0, en_hilo=True)
        else:
            self._boton(grid, "📢\nAnuncios", "Ver carpeta de anuncios",
                        self._abrir_carpeta_anuncios, row=1, col=0)
        self._boton(grid, "📊\nEstadísticas", "Ver historial",
                    self._ver_estadisticas, row=1, col=1)

        # Fila 2
        if es_full:
            self._boton(grid, "🗓️\nTareas Automáticas", "Programar publicaciones",
                        self._gestionar_tareas, row=2, col=0, color="#28a745", en_hilo=True)
        else:
            self._boton(grid, "🔒\nTareas Automáticas", "Solo versión Completa",
                        self._mostrar_mensaje_upgrade, row=2, col=0, color="#9e9e9e")

        self._boton(grid, "❓\nAyuda", "Cómo usar el sistema",
                    self._mostrar_ayuda, row=2, col=1)

        # Fila 3
        self._boton(grid, "❌\nSalir", "Cerrar panel",
                    self.root.destroy, row=3, col=0, color="#dc3545")

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

    def _boton(self, parent, texto, subtexto, comando, row, col,
               color="white", en_hilo=False):
        """Crea un botón de opción en el grid — simétrico a MensajesBiblicos"""
        frame = tk.Frame(parent, bg="white", relief='solid', bd=1, cursor="hand2")
        frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        parent.grid_columnconfigure(col, weight=1)
        parent.grid_rowconfigure(row, weight=1)

        es_coloreado = color != "white"
        bg_texto = color if es_coloreado else "white"
        fg_texto = "white" if es_coloreado else COLOR_PRINCIPAL

        lbl_titulo = tk.Label(
            frame,
            text=texto,
            font=("Segoe UI", 11, "bold"),
            bg=bg_texto,
            fg=fg_texto,
            justify='center'
        )
        lbl_titulo.pack(pady=(15, 5), fill='both', expand=True)

        lbl_sub = tk.Label(
            frame,
            text=subtexto,
            font=("Segoe UI", 8),
            bg=bg_texto,
            fg="white" if es_coloreado else "gray",
            justify='center'
        )
        lbl_sub.pack(pady=(0, 15))

        if es_coloreado:
            frame.config(bg=color)

        # Guardar referencias para bloquear/desbloquear
        frame._cmd = comando
        frame._en_hilo = en_hilo
        widgets = [lbl_titulo, lbl_sub]
        self._botones_grid.append((frame, widgets))

        accion = (lambda c=comando: self._lanzar_en_hilo(c)) if en_hilo else comando

        frame.bind('<Button-1>', lambda e, a=accion: a())
        frame.bind('<Enter>', lambda e, f=frame, c=color: f.config(bg="#f3e8ff" if c == "white" else c))
        frame.bind('<Leave>', lambda e, f=frame, c=color: f.config(bg=c))
        for w in widgets:
            w.bind('<Button-1>', lambda e, a=accion: a())
            w.bind('<Enter>', lambda e, f=frame, c=color: f.config(bg="#f3e8ff" if c == "white" else c))
            w.bind('<Leave>', lambda e, f=frame, c=color: f.config(bg=c))

    def _bloquear_grid(self):
        """Bloquea todos los botones del grid"""
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
        """Restaura todos los botones del grid"""
        self.root.config(cursor="")
        for frame, widgets in self._botones_grid:
            frame.config(cursor="hand2", bg="white")
            cmd = frame._cmd
            en_hilo = frame._en_hilo
            for w in widgets:
                w.config(bg="white")
                accion = (lambda c=cmd: self._lanzar_en_hilo(c)) if en_hilo else cmd
                w.bind('<Button-1>', lambda e, a=accion: a())
                w.bind('<Enter>', lambda e, f=frame: f.config(bg="#f3e8ff"))
                w.bind('<Leave>', lambda e, f=frame: f.config(bg="white"))
            accion = (lambda c=cmd: self._lanzar_en_hilo(c)) if en_hilo else cmd
            frame.bind('<Button-1>', lambda e, a=accion: a())
            frame.bind('<Enter>', lambda e, f=frame: f.config(bg="#f3e8ff"))
            frame.bind('<Leave>', lambda e, f=frame: f.config(bg="white"))

    def _lanzar_en_hilo(self, cmd):
        """Para subprocesos: bloquea grid, corre en hilo, desbloquea al terminar"""
        self._bloquear_grid()
        import threading
        def _hilo():
            try:
                cmd()
            finally:
                self.root.after(0, self._desbloquear_grid)
        threading.Thread(target=_hilo, daemon=True).start()

    def _centrar_ventana(self, ventana, ancho, alto):
        """Centra una ventana en pantalla antes de mostrarla"""
        x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
        y = (ventana.winfo_screenheight() // 2) - (alto // 2)
        ventana.geometry(f'{ancho}x{alto}+{x}+{y}')

    # ==================== ACCIONES ====================

    def _publicar_ahora(self):
        """Ejecuta el publicador principal"""
        try:
            exe = self._exe("PublicadorRedes.exe")
            if os.path.exists(exe):
                subprocess.Popen([exe])
            else:
                subprocess.Popen([sys.executable,
                                  os.path.join(self.base_dir, "publicar_redes.py")])
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo iniciar el publicador:\n{e}")

    def _abrir_configurador(self):
        """Abre el configurador GUI"""
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
        """Abre el gestor de anuncios (solo FULL)"""
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
        """TRIAL: abre la carpeta anuncios en el explorador"""
        import subprocess as sp
        carpeta = os.path.join(self.base_dir, "anuncios")
        os.makedirs(carpeta, exist_ok=True)
        sp.Popen(f'explorer "{carpeta}"')
        self._toast(
            "📢 Tus Anuncios",
            "Carpeta abierta — versión Completa incluye editor visual",
            duracion=5000
        )

    def _gestionar_tareas(self):
        """Abre el gestor de tareas automáticas"""
        try:
            exe = self._exe("GestorTareasRedes.exe")
            if os.path.exists(exe):
                subprocess.run([exe])
            else:
                messagebox.showerror("❌ Error", "No se encontró GestorTareasRedes.exe")
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo abrir el gestor de tareas:\n{e}")

    def _ver_estadisticas(self):
        """Muestra ventana de estadísticas"""
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
                     font=("Segoe UI", 13, "bold"),
                     bg=COLOR_PRINCIPAL, fg="white").pack()

            frame = tk.Frame(ventana, bg="white", padx=30, pady=20)
            frame.pack(fill='both', expand=True, padx=20, pady=15)

            fecha_ultima = stats.get('ultima_publicacion', 'Nunca')
            if fecha_ultima and fecha_ultima != 'Nunca':
                fecha_ultima = fecha_ultima[:19]

            total = stats.get('total', 0)
            exitosas = stats.get('exitosas', 0)
            fallidas = stats.get('fallidas', 0)
            tasa = stats.get('tasa_exito', 0)

            items = [
                ("📦 Total publicaciones:", str(total)),
                ("✅ Exitosas:", str(exitosas)),
                ("❌ Fallidas:", str(fallidas)),
                ("🎯 Tasa de éxito:", f"{tasa}%"),
                ("📅 Última publicación:", fecha_ultima),
            ]

            for label, valor in items:
                row = tk.Frame(frame, bg="white")
                row.pack(fill='x', pady=5)
                tk.Label(row, text=label, font=("Segoe UI", 10, "bold"),
                         bg="white", anchor='w', width=25).pack(side='left')
                tk.Label(row, text=valor, font=("Segoe UI", 10),
                         bg="white", anchor='w').pack(side='left')

            tk.Button(
                ventana, text="Cerrar",
                font=("Segoe UI", 10),
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
        """Muestra el centro de ayuda con panel de temas"""
        ventana = tk.Toplevel(self.root)
        ventana.withdraw()
        ventana.title("❓ Centro de Ayuda")
        ventana.resizable(False, False)
        ventana.configure(bg="#f0f0f0")
        ventana.transient(self.root)
        ventana.grab_set()

        TEMAS = [
            ("⚡  Publicar Ahora",
             "⚡ PUBLICAR AHORA\n\n"
             "Publica automáticamente tu anuncio en las redes sociales configuradas.\n\n"
             "¿Qué hace?\n"
             "• Abre el navegador Firefox con tu perfil guardado\n"
             "• Lee el siguiente anuncio de la carpeta 'anuncios/'\n"
             "• Publica el texto, imágenes y/o video según la plataforma\n"
             "• Registra la publicación en el historial\n\n"
             "¿Cuándo usarlo?\n"
             "• Cuando quieras publicar manualmente un anuncio\n"
             "• Si no tienes tareas automáticas programadas\n\n"
             "Configuración relacionada:\n"
             "• Configurador → General (navegador, selección de anuncio)\n"
             "• Configurador → Módulos (activar/desactivar redes sociales)"),

            ("📢  Gestionar Anuncios",
             "📢 GESTIONAR ANUNCIOS\n\n"
             "Editor visual para crear, editar y organizar los anuncios\n"
             "que se publicarán en tus redes sociales.\n\n"
             "¿Qué puedes hacer?\n"
             "• Crear anuncios nuevos con texto, imágenes y video\n"
             "• Editar o eliminar anuncios existentes\n"
             "• Reordenar el orden de publicación\n"
             "• Elegir en qué plataformas publicar cada anuncio\n\n"
             "Estructura de cada anuncio:\n"
             "• anuncios/anuncio_001/datos.txt  ← texto y configuración\n"
             "• anuncios/anuncio_001/imagenes/  ← imágenes del anuncio\n"
             "• anuncios/anuncio_001/videos/    ← videos del anuncio\n\n"
             "⚠️ Requiere versión Completa"),

            ("⚙️  Configurador",
             "⚙️ CONFIGURADOR\n\n"
             "Panel principal de configuración del sistema.\n\n"
             "Opciones disponibles:\n"
             "• General → navegador, perfil, modo debug\n"
             "• Anuncios → selección, hashtags, firma\n"
             "• Publicación → tiempos de espera, reintentos\n"
             "• Módulos → activar/desactivar redes sociales\n"
             "• Límites → tiempo mínimo entre publicaciones\n\n"
             "Recuerda presionar 💾 Guardar antes de cerrar."),

            ("📊  Estadísticas",
             "📊 ESTADÍSTICAS\n\n"
             "Muestra un resumen del historial de publicaciones.\n\n"
             "¿Qué información muestra?\n"
             "• Total de publicaciones realizadas\n"
             "• Publicaciones exitosas y fallidas\n"
             "• Tasa de éxito en porcentaje\n"
             "• Fecha de la última publicación\n\n"
             "Los datos se acumulan con el tiempo."),

            ("🗓️  Tareas Automáticas",
             "🗓️ TAREAS AUTOMÁTICAS\n\n"
             "Programa el sistema para que publique automáticamente\n"
             "en los días y horas que elijas.\n\n"
             "¿Qué puedes programar?\n"
             "• Días de la semana y hora de ejecución\n"
             "• Frecuencia de publicación\n\n"
             "Usa el Programador de Tareas de Windows internamente.\n\n"
             "⚠️ Requiere versión Completa"),
        ]

        # Layout del centro de ayuda
        header = tk.Frame(ventana, bg=COLOR_PRINCIPAL, pady=12)
        header.pack(fill='x')
        tk.Label(header, text="❓ Centro de Ayuda",
                 font=("Segoe UI", 13, "bold"),
                 bg=COLOR_PRINCIPAL, fg="white").pack()

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
        texto_detalle.configure(yscrollcommand=scroll.set)
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
        """Abre la página de compra con el código de licencia del usuario"""
        import webbrowser
        try:
            codigo = self.gestor_licencias.obtener_codigo_guardado()
            url = f"https://automapro-frontend.vercel.app/cliente/comprar?codigo={codigo}&app=2"
            webbrowser.open(url)
        except Exception:
            webbrowser.open("https://automapro-frontend.vercel.app/catalogo")

    def _mostrar_mensaje_upgrade(self):
        """Muestra mensaje de función bloqueada para TRIAL"""
        messagebox.showinfo(
            "🔒 Versión Completa requerida",
            "Esta función requiere la versión Completa.\n\n"
            "Visita: automapro-frontend.vercel.app\n"
            "Precio: $19.99 USD (pago único)"
        )

    def _verificar_actualizacion(self):
        """Verifica si hay una versión nueva disponible en segundo plano"""
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
        """Muestra ventana modal de actualización disponible"""
        import urllib.request, tempfile, threading

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
                 font=("Segoe UI", 13, "bold"),
                 bg=COLOR_PRINCIPAL, fg="white").pack()

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
        tk.Label(cuerpo,
                 text="Hay una nueva versión disponible.\nHaz clic en Actualizar para instalarla automáticamente.",
                 font=("Segoe UI", 10), bg="#f0f0f0", justify='left').pack(fill='x')

        barra = tk.ttk.Progressbar(ventana, mode='indeterminate')

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

        from tkinter import ttk
        btn_actualizar = tk.Button(ventana, text="⬆️ Actualizar ahora",
                                   font=("Segoe UI", 10, "bold"),
                                   bg=COLOR_PRINCIPAL, fg="white", width=18,
                                   command=actualizar_ahora)
        btn_actualizar.pack(side='left', padx=(30, 10), pady=10)

        tk.Button(ventana, text="Ahora no",
                  font=("Segoe UI", 10),
                  bg="#6c757d", fg="white", width=12,
                  command=ventana.destroy).pack(side='right', padx=(0, 30), pady=10)

    def _toast(self, titulo, mensaje="", duracion=3000, color="#28a745"):
        """Delega al sistema centralizado de toasts"""
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
    """Si no hay licencia configurada, lanza el wizard y termina"""
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
            messagebox.showwarning(
                "Configuración requerida",
                "Por favor ejecuta WizardPublicador.exe para configurar el sistema."
            )
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