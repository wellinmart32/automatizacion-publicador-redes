import os
import sys
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog


class GestorAnuncios:
    """Interfaz gráfica para gestionar anuncios de PublicadorRedes"""

    def __init__(self):
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('AutomaPro.GestorAnuncios')
        except Exception:
            pass

        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.carpeta_anuncios = os.path.join(self.base_dir, "anuncios")

        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("📢 Gestor de Anuncios - Publicador Redes")
        self.root.minsize(800, 560)
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f0f0")

        try:
            base_ico = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
            self.root.iconbitmap(os.path.join(base_ico, 'iconos', 'anuncios.ico'))
        except Exception:
            pass

        width = 900
        height = 660
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        self.root.deiconify()

        try:
            ico = os.path.join(self.base_dir, 'iconos', 'anuncios.ico')
            self.root.after(100, lambda: self.root.iconbitmap(ico))
            self.root.after(300, lambda: self.root.iconbitmap(ico))
            self.root.after(500, lambda: self.root.iconbitmap(ico))
        except Exception:
            pass

        self.anuncio_actual = None

        self._construir_ui()
        self._cargar_anuncios()

    def _construir_ui(self):
        """Construye la interfaz principal"""

        # Header
        header = tk.Frame(self.root, bg="#7c3aed", pady=12)
        header.pack(fill='x')
        tk.Label(
            header,
            text="📢 Gestor de Anuncios",
            font=("Segoe UI", 14, "bold"),
            bg="#7c3aed",
            fg="white"
        ).pack()

        # Panel principal dividido en 2
        panel = tk.Frame(self.root, bg="#f0f0f0")
        panel.pack(fill='both', expand=True, padx=10, pady=10)

        # ==================== PANEL IZQUIERDO (lista) ====================
        panel_izq = tk.Frame(panel, bg="#f0f0f0", width=230)
        panel_izq.pack(side='left', fill='y', padx=(0, 5))
        panel_izq.pack_propagate(False)

        tk.Label(
            panel_izq,
            text="📂 Anuncios disponibles",
            font=("Segoe UI", 10, "bold"),
            bg="#f0f0f0"
        ).pack(anchor='w', pady=(0, 5))

        self.lbl_contador = tk.Label(
            panel_izq,
            text="0 anuncios",
            font=("Segoe UI", 8),
            fg="gray",
            bg="#f0f0f0"
        )
        self.lbl_contador.pack(anchor='w', pady=(0, 5))

        frame_lista = tk.Frame(panel_izq, bg="#f0f0f0")
        frame_lista.pack(fill='both', expand=True)

        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side='right', fill='y')

        self.lista = tk.Listbox(
            frame_lista,
            yscrollcommand=scrollbar.set,
            font=("Segoe UI", 9),
            selectmode='single',
            bg="white",
            relief='solid',
            borderwidth=1
        )
        self.lista.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.lista.yview)
        self.lista.bind('<<ListboxSelect>>', self._on_seleccionar)

        # Botones lista
        frame_btn_lista = tk.Frame(panel_izq, bg="#f0f0f0")
        frame_btn_lista.pack(fill='x', pady=(8, 0))

        tk.Button(
            frame_btn_lista,
            text="✚ Nuevo",
            font=("Segoe UI", 10, "bold"),
            bg="#7c3aed",
            fg="white",
            command=self._nuevo_anuncio
        ).pack(side='left', expand=True, fill='x', padx=(0, 2), ipady=6)

        tk.Button(
            frame_btn_lista,
            text="🗑️ Eliminar",
            font=("Segoe UI", 10),
            bg="#dc3545",
            fg="white",
            command=self._eliminar_anuncio
        ).pack(side='right', expand=True, fill='x', padx=(2, 0), ipady=6)

        # ==================== PANEL DERECHO (editor) ====================
        panel_der = tk.Frame(panel, bg="#f0f0f0")
        panel_der.pack(side='left', fill='both', expand=True)

        # Nombre del anuncio seleccionado
        frame_nombre = tk.Frame(panel_der, bg="#f0f0f0")
        frame_nombre.pack(fill='x', pady=(0, 8))

        tk.Label(
            frame_nombre,
            text="Anuncio:",
            font=("Segoe UI", 9, "bold"),
            bg="#f0f0f0"
        ).pack(side='left')

        self.lbl_anuncio = tk.Label(
            frame_nombre,
            text="(ninguno seleccionado)",
            font=("Segoe UI", 9),
            fg="gray",
            bg="#f0f0f0"
        )
        self.lbl_anuncio.pack(side='left', padx=(5, 0))

        # Notebook del editor
        self.notebook_editor = ttk.Notebook(panel_der)
        self.notebook_editor.pack(fill='both', expand=True)

        # ---- Pestaña Texto ----
        tab_texto = ttk.Frame(self.notebook_editor)
        self.notebook_editor.add(tab_texto, text="📝 Texto")

        tk.Label(
            tab_texto,
            text="Texto del anuncio:",
            font=("Segoe UI", 9, "bold"),
            bg="#f0f0f0"
        ).pack(anchor='w', padx=5, pady=(8, 2))

        frame_texto = tk.Frame(tab_texto, bg="#f0f0f0")
        frame_texto.pack(fill='both', expand=True, padx=5, pady=(0, 5))

        scrollbar_texto = tk.Scrollbar(frame_texto)
        scrollbar_texto.pack(side='right', fill='y')

        self.texto = tk.Text(
            frame_texto,
            yscrollcommand=scrollbar_texto.set,
            font=("Segoe UI", 10),
            wrap='word',
            relief='solid',
            borderwidth=1,
            bg="white",
            padx=8,
            pady=8
        )
        self.texto.pack(fill='both', expand=True)
        scrollbar_texto.config(command=self.texto.yview)
        self.texto.bind('<KeyRelease>', self._actualizar_contador_chars)

        # Contador de chars y plataformas
        frame_info = tk.Frame(tab_texto, bg="#f0f0f0")
        frame_info.pack(fill='x', padx=5, pady=(0, 5))

        self.lbl_chars = tk.Label(
            frame_info,
            text="0 caracteres",
            font=("Segoe UI", 8),
            fg="gray",
            bg="#f0f0f0"
        )
        self.lbl_chars.pack(side='left')

        # ---- Pestaña Imágenes ----
        tab_imagenes = ttk.Frame(self.notebook_editor)
        self.notebook_editor.add(tab_imagenes, text="🖼️ Imágenes")

        frame_btn_img = tk.Frame(tab_imagenes, bg="#f0f0f0")
        frame_btn_img.pack(fill='x', padx=5, pady=8)

        tk.Button(
            frame_btn_img,
            text="➕ Agregar imágenes",
            font=("Segoe UI", 10, "bold"),
            bg="#7c3aed",
            fg="white",
            command=self._agregar_imagenes
        ).pack(side='left', padx=(0, 5))

        tk.Button(
            frame_btn_img,
            text="🗑️ Quitar seleccionada",
            font=("Segoe UI", 10),
            bg="#dc3545",
            fg="white",
            command=self._quitar_imagen
        ).pack(side='left')

        tk.Label(
            frame_btn_img,
            text="Máx. 10 imágenes",
            font=("Segoe UI", 8),
            fg="gray",
            bg="#f0f0f0"
        ).pack(side='right')

        frame_lista_img = tk.Frame(tab_imagenes, bg="#f0f0f0")
        frame_lista_img.pack(fill='both', expand=True, padx=5, pady=(0, 5))

        scrollbar_img = tk.Scrollbar(frame_lista_img)
        scrollbar_img.pack(side='right', fill='y')

        self.lista_imagenes = tk.Listbox(
            frame_lista_img,
            yscrollcommand=scrollbar_img.set,
            font=("Segoe UI", 9),
            selectmode='single',
            bg="white",
            relief='solid',
            borderwidth=1
        )
        self.lista_imagenes.pack(side='left', fill='both', expand=True)
        scrollbar_img.config(command=self.lista_imagenes.yview)

        # ---- Pestaña Videos ----
        tab_videos = ttk.Frame(self.notebook_editor)
        self.notebook_editor.add(tab_videos, text="🎬 Videos")

        frame_btn_vid = tk.Frame(tab_videos, bg="#f0f0f0")
        frame_btn_vid.pack(fill='x', padx=5, pady=8)

        tk.Button(
            frame_btn_vid,
            text="➕ Agregar video",
            font=("Segoe UI", 10, "bold"),
            bg="#7c3aed",
            fg="white",
            command=self._agregar_video
        ).pack(side='left', padx=(0, 5))

        tk.Button(
            frame_btn_vid,
            text="🗑️ Quitar seleccionado",
            font=("Segoe UI", 10),
            bg="#dc3545",
            fg="white",
            command=self._quitar_video
        ).pack(side='left')

        tk.Label(
            frame_btn_vid,
            text="Máx. 1 video por anuncio",
            font=("Segoe UI", 8),
            fg="gray",
            bg="#f0f0f0"
        ).pack(side='right')

        frame_lista_vid = tk.Frame(tab_videos, bg="#f0f0f0")
        frame_lista_vid.pack(fill='both', expand=True, padx=5, pady=(0, 5))

        scrollbar_vid = tk.Scrollbar(frame_lista_vid)
        scrollbar_vid.pack(side='right', fill='y')

        self.lista_videos = tk.Listbox(
            frame_lista_vid,
            yscrollcommand=scrollbar_vid.set,
            font=("Segoe UI", 9),
            selectmode='single',
            bg="white",
            relief='solid',
            borderwidth=1
        )
        self.lista_videos.pack(side='left', fill='both', expand=True)
        scrollbar_vid.config(command=self.lista_videos.yview)

        # ---- Pestaña Plataformas ----
        tab_plataformas = ttk.Frame(self.notebook_editor)
        self.notebook_editor.add(tab_plataformas, text="📱 Plataformas")

        tk.Label(
            tab_plataformas,
            text="¿En qué redes sociales publicar este anuncio?",
            font=("Segoe UI", 9),
            fg="#555",
            bg="#f0f0f0"
        ).pack(anchor='w', padx=10, pady=(10, 5))

        self.var_plat_facebook = tk.BooleanVar(value=True)
        self.var_plat_instagram = tk.BooleanVar(value=False)
        self.var_plat_twitter = tk.BooleanVar(value=False)
        self.var_plat_linkedin = tk.BooleanVar(value=False)

        plataformas = [
            ("📘 Facebook", self.var_plat_facebook),
            ("📸 Instagram", self.var_plat_instagram),
            ("🐦 Twitter / X", self.var_plat_twitter),
            ("💼 LinkedIn", self.var_plat_linkedin),
        ]

        for texto_plat, var in plataformas:
            tk.Checkbutton(
                tab_plataformas,
                text=texto_plat,
                variable=var,
                font=("Segoe UI", 11),
                bg="#f0f0f0",
                activebackground="#f0f0f0"
            ).pack(anchor='w', padx=20, pady=5)

        # Botones guardar
        frame_guardar = tk.Frame(panel_der, bg="#f0f0f0")
        frame_guardar.pack(fill='x', pady=(8, 0))

        tk.Button(
            frame_guardar,
            text="💾  Guardar anuncio",
            font=("Segoe UI", 10, "bold"),
            bg="#7c3aed",
            fg="white",
            activebackground="#6d28d9",
            cursor="hand2",
            pady=6,
            command=self._guardar_anuncio
        ).pack(side='left', fill='x', expand=True, padx=(0, 5))

        tk.Button(
            frame_guardar,
            text="📁 Abrir carpeta",
            font=("Segoe UI", 10),
            bg="#6c757d",
            fg="white",
            cursor="hand2",
            pady=6,
            command=self._abrir_carpeta_anuncio
        ).pack(side='left')

    def _cargar_anuncios(self):
        """Carga la lista de carpetas de anuncios"""
        self.lista.delete(0, tk.END)

        if not os.path.exists(self.carpeta_anuncios):
            os.makedirs(self.carpeta_anuncios)

        anuncios = sorted([
            d for d in os.listdir(self.carpeta_anuncios)
            if os.path.isdir(os.path.join(self.carpeta_anuncios, d))
            and d.startswith('anuncio_')
        ])

        for anuncio in anuncios:
            self.lista.insert(tk.END, anuncio)

        self.lbl_contador.config(text=f"{len(anuncios)} anuncios")

    def _on_seleccionar(self, event):
        """Al seleccionar un anuncio carga su contenido en el editor"""
        seleccion = self.lista.curselection()
        if not seleccion:
            return

        nombre = self.lista.get(seleccion[0])
        self.anuncio_actual = nombre
        ruta_anuncio = os.path.join(self.carpeta_anuncios, nombre)

        self.lbl_anuncio.config(text=nombre, fg="#7c3aed")

        # Cargar texto
        self.texto.delete('1.0', tk.END)
        archivo_texto = os.path.join(ruta_anuncio, 'datos.txt')
        if os.path.exists(archivo_texto):
            try:
                import configparser
                config = configparser.ConfigParser()
                config.read(archivo_texto, encoding='utf-8')
                texto = config.get('ANUNCIO', 'texto', fallback='') if config.has_section('ANUNCIO') else ''
                self.texto.insert('1.0', texto)

                # Cargar plataformas
                plataformas = config.get('ANUNCIO', 'plataformas', fallback='facebook').split(',')
                self.var_plat_facebook.set('facebook' in plataformas)
                self.var_plat_instagram.set('instagram' in plataformas)
                self.var_plat_twitter.set('twitter' in plataformas)
                self.var_plat_linkedin.set('linkedin' in plataformas)
            except Exception:
                pass

        self._actualizar_contador_chars()

        # Cargar imágenes
        self.lista_imagenes.delete(0, tk.END)
        carpeta_img = os.path.join(ruta_anuncio, 'imagenes')
        if os.path.exists(carpeta_img):
            for archivo in sorted(os.listdir(carpeta_img)):
                if archivo.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    self.lista_imagenes.insert(tk.END, archivo)

        # Cargar videos
        self.lista_videos.delete(0, tk.END)
        carpeta_vid = os.path.join(ruta_anuncio, 'videos')
        if os.path.exists(carpeta_vid):
            for archivo in sorted(os.listdir(carpeta_vid)):
                if archivo.lower().endswith(('.mp4', '.avi', '.mov')):
                    self.lista_videos.insert(tk.END, archivo)

    def _nuevo_anuncio(self):
        """Crea una nueva carpeta de anuncio"""
        anuncios_existentes = [
            d for d in os.listdir(self.carpeta_anuncios)
            if os.path.isdir(os.path.join(self.carpeta_anuncios, d))
            and d.startswith('anuncio_')
        ] if os.path.exists(self.carpeta_anuncios) else []

        siguiente_num = len(anuncios_existentes) + 1
        nombre_sugerido = f"anuncio_{siguiente_num:03d}"

        nombre = simpledialog.askstring(
            "Nuevo anuncio",
            "Nombre de la carpeta del anuncio:",
            initialvalue=nombre_sugerido,
            parent=self.root
        )

        if not nombre:
            return

        ruta = os.path.join(self.carpeta_anuncios, nombre)

        if os.path.exists(ruta):
            messagebox.showwarning("⚠️ Aviso", f"Ya existe un anuncio llamado '{nombre}'")
            return

        try:
            os.makedirs(os.path.join(ruta, 'imagenes'))
            os.makedirs(os.path.join(ruta, 'videos'))

            # Crear datos.txt inicial
            with open(os.path.join(ruta, 'datos.txt'), 'w', encoding='utf-8') as f:
                f.write("[ANUNCIO]\n")
                f.write("texto = \n")
                f.write("plataformas = facebook\n")
                f.write("estado = pendiente\n")

            self._cargar_anuncios()

            # Seleccionar el nuevo anuncio
            for i in range(self.lista.size()):
                if self.lista.get(i) == nombre:
                    self.lista.selection_clear(0, tk.END)
                    self.lista.selection_set(i)
                    self.lista.see(i)
                    self._on_seleccionar(None)
                    break

        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al crear el anuncio: {e}")

    def _eliminar_anuncio(self):
        """Elimina la carpeta del anuncio seleccionado"""
        seleccion = self.lista.curselection()
        if not seleccion:
            messagebox.showwarning("⚠️ Aviso", "Selecciona un anuncio para eliminar")
            return

        nombre = self.lista.get(seleccion[0])

        confirmar = messagebox.askyesno(
            "🗑️ Confirmar eliminación",
            f"¿Estás seguro de eliminar '{nombre}'?\n\n"
            "Se eliminarán el texto, imágenes y videos.\n"
            "Esta acción no se puede deshacer."
        )

        if not confirmar:
            return

        ruta = os.path.join(self.carpeta_anuncios, nombre)

        try:
            shutil.rmtree(ruta)
            self._cargar_anuncios()
            self._limpiar_editor()
            messagebox.showinfo("✅ Éxito", f"Anuncio eliminado: {nombre}")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al eliminar: {e}")

    def _guardar_anuncio(self):
        """Guarda el texto y configuración del anuncio actual"""
        if not self.anuncio_actual:
            messagebox.showwarning("⚠️ Aviso", "Selecciona un anuncio o crea uno nuevo")
            return

        texto = self.texto.get('1.0', tk.END).strip()
        ruta_anuncio = os.path.join(self.carpeta_anuncios, self.anuncio_actual)
        archivo_datos = os.path.join(ruta_anuncio, 'datos.txt')

        # Construir lista de plataformas
        plataformas = []
        if self.var_plat_facebook.get():
            plataformas.append('facebook')
        if self.var_plat_instagram.get():
            plataformas.append('instagram')
        if self.var_plat_twitter.get():
            plataformas.append('twitter')
        if self.var_plat_linkedin.get():
            plataformas.append('linkedin')

        if not plataformas:
            messagebox.showwarning("⚠️ Aviso", "Selecciona al menos una plataforma")
            return

        try:
            with open(archivo_datos, 'w', encoding='utf-8') as f:
                f.write("[ANUNCIO]\n")
                f.write(f"texto = {texto}\n")
                f.write(f"plataformas = {','.join(plataformas)}\n")
                f.write("estado = pendiente\n")

            messagebox.showinfo("✅ Éxito", f"Anuncio guardado: {self.anuncio_actual}")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al guardar: {e}")

    def _agregar_imagenes(self):
        """Agrega imágenes a la carpeta del anuncio actual"""
        if not self.anuncio_actual:
            messagebox.showwarning("⚠️ Aviso", "Selecciona un anuncio primero")
            return

        archivos = filedialog.askopenfilenames(
            title="Seleccionar imágenes",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.webp"), ("Todos", "*.*")],
            parent=self.root
        )

        if not archivos:
            return

        carpeta_img = os.path.join(self.carpeta_anuncios, self.anuncio_actual, 'imagenes')
        os.makedirs(carpeta_img, exist_ok=True)

        actuales = self.lista_imagenes.size()
        if actuales + len(archivos) > 10:
            messagebox.showwarning("⚠️ Aviso", f"Máximo 10 imágenes. Ya tienes {actuales}.")
            return

        copiadas = 0
        for archivo in archivos:
            nombre = os.path.basename(archivo)
            destino = os.path.join(carpeta_img, nombre)
            try:
                shutil.copy2(archivo, destino)
                self.lista_imagenes.insert(tk.END, nombre)
                copiadas += 1
            except Exception as e:
                messagebox.showerror("❌ Error", f"Error copiando {nombre}: {e}")

        if copiadas > 0:
            messagebox.showinfo("✅ Éxito", f"{copiadas} imagen(es) agregada(s)")

    def _quitar_imagen(self):
        """Elimina la imagen seleccionada de la carpeta del anuncio"""
        seleccion = self.lista_imagenes.curselection()
        if not seleccion:
            messagebox.showwarning("⚠️ Aviso", "Selecciona una imagen para quitar")
            return

        nombre = self.lista_imagenes.get(seleccion[0])
        ruta = os.path.join(self.carpeta_anuncios, self.anuncio_actual, 'imagenes', nombre)

        confirmar = messagebox.askyesno(
            "🗑️ Confirmar",
            f"¿Quitar '{nombre}' del anuncio?"
        )

        if not confirmar:
            return

        try:
            os.remove(ruta)
            self.lista_imagenes.delete(seleccion[0])
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al quitar imagen: {e}")

    def _agregar_video(self):
        """Agrega un video a la carpeta del anuncio actual"""
        if not self.anuncio_actual:
            messagebox.showwarning("⚠️ Aviso", "Selecciona un anuncio primero")
            return

        if self.lista_videos.size() >= 1:
            messagebox.showwarning("⚠️ Aviso", "Solo se permite 1 video por anuncio.\nQuita el actual primero.")
            return

        archivo = filedialog.askopenfilename(
            title="Seleccionar video",
            filetypes=[("Videos", "*.mp4 *.avi *.mov"), ("Todos", "*.*")],
            parent=self.root
        )

        if not archivo:
            return

        carpeta_vid = os.path.join(self.carpeta_anuncios, self.anuncio_actual, 'videos')
        os.makedirs(carpeta_vid, exist_ok=True)

        nombre = os.path.basename(archivo)
        destino = os.path.join(carpeta_vid, nombre)

        try:
            shutil.copy2(archivo, destino)
            self.lista_videos.insert(tk.END, nombre)
            messagebox.showinfo("✅ Éxito", f"Video agregado: {nombre}")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error copiando video: {e}")

    def _quitar_video(self):
        """Elimina el video seleccionado de la carpeta del anuncio"""
        seleccion = self.lista_videos.curselection()
        if not seleccion:
            messagebox.showwarning("⚠️ Aviso", "Selecciona un video para quitar")
            return

        nombre = self.lista_videos.get(seleccion[0])
        ruta = os.path.join(self.carpeta_anuncios, self.anuncio_actual, 'videos', nombre)

        confirmar = messagebox.askyesno(
            "🗑️ Confirmar",
            f"¿Quitar '{nombre}' del anuncio?"
        )

        if not confirmar:
            return

        try:
            os.remove(ruta)
            self.lista_videos.delete(seleccion[0])
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al quitar video: {e}")

    def _abrir_carpeta_anuncio(self):
        """Abre la carpeta del anuncio actual en el explorador"""
        if not self.anuncio_actual:
            messagebox.showwarning("⚠️ Aviso", "Selecciona un anuncio primero")
            return

        ruta = os.path.join(self.carpeta_anuncios, self.anuncio_actual)
        import subprocess
        subprocess.Popen(f'explorer "{ruta}"')

    def _limpiar_editor(self):
        """Limpia el editor al eliminar un anuncio"""
        self.anuncio_actual = None
        self.texto.delete('1.0', tk.END)
        self.lista_imagenes.delete(0, tk.END)
        self.lista_videos.delete(0, tk.END)
        self.lbl_anuncio.config(text="(ninguno seleccionado)", fg="gray")
        self.var_plat_facebook.set(True)
        self.var_plat_instagram.set(False)
        self.var_plat_twitter.set(False)
        self.var_plat_linkedin.set(False)
        self._actualizar_contador_chars()

    def _actualizar_contador_chars(self, event=None):
        """Actualiza el contador de caracteres"""
        contenido = self.texto.get('1.0', tk.END).strip()
        self.lbl_chars.config(text=f"{len(contenido)} caracteres")

    def ejecutar(self):
        self.root.mainloop()


def main():
    app = GestorAnuncios()
    app.ejecutar()


if __name__ == "__main__":
    main()