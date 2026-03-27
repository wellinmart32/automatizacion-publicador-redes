import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
from datetime import datetime
from gestor_licencias import GestorLicencias


class GestorTareasGUI:
    """Gestor de tareas automáticas - Windows Task Scheduler"""

    def __init__(self):
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('AutomaPro.GestorTareasRedes')
        except Exception:
            pass

        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("🗓️ Gestor de Tareas Automáticas - Publicador Redes")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        try:
            base_ico = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
            self.root.iconbitmap(os.path.join(base_ico, 'iconos', 'calendar.ico'))
        except Exception:
            pass

        x = (self.root.winfo_screenwidth() // 2) - 450
        y = (self.root.winfo_screenheight() // 2) - 300

        try:
            base_ico = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
            ico = os.path.join(base_ico, 'iconos', 'calendar.ico')
            self.root.iconbitmap(ico)
        except Exception:
            pass

        self.root.geometry(f'900x600+{x}+{y}')
        self.root.deiconify()

        try:
            self.root.after(50,  lambda: self.root.iconbitmap(ico))
            self.root.after(200, lambda: self.root.iconbitmap(ico))
            self.root.after(500, lambda: self.root.iconbitmap(ico))
        except Exception:
            pass

        self.gestor_licencias = GestorLicencias("PublicadorRedes")
        if not self._verificar_licencia_full():
            messagebox.showerror(
                "Licencia Requerida",
                "Esta función requiere licencia FULL.\n\nActualiza tu licencia para acceder."
            )
            self.root.destroy()
            return

        self.prefijo_tarea = "AutomaPro_PublicadorRedes"

        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
            self.ruta_exe = os.path.join(self.base_dir, "PublicadorRedes.exe")
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
            self.ruta_exe = None

        self.ruta_script = os.path.join(self.base_dir, "publicar_redes.py")

        self.dias_map = {
            'L': 'MON', 'M': 'TUE', 'X': 'WED',
            'J': 'THU', 'V': 'FRI', 'S': 'SAT', 'D': 'SUN'
        }

        self.dias_map_inverso = {
            'MON': 'L', 'TUE': 'M', 'WED': 'X',
            'THU': 'J', 'FRI': 'V', 'SAT': 'S', 'SUN': 'D'
        }

        self._construir_ui()
        self._cargar_tareas()

    def _verificar_licencia_full(self):
        """Verifica si la licencia es FULL — usa cache primero"""
        try:
            cache = self.gestor_licencias._obtener_cache_local()
            if cache and cache.get('valida'):
                tipo = cache.get('tipo', 'TRIAL')
                return tipo in ['FULL', 'MASTER'] or cache.get('es_developer_permanente', False)

            codigo = self.gestor_licencias.obtener_codigo_guardado()
            if not codigo:
                return False
            resultado = self.gestor_licencias.verificar_licencia(codigo, mostrar_mensajes=False)
            return resultado.get('valida') and (
                resultado.get('tipo') in ['FULL', 'MASTER'] or resultado.get('developer_permanente')
            )
        except Exception:
            return False

    def _mostrar_toast(self, mensaje, duracion=3000, color="#28a745"):
        """Muestra notificación toast que desaparece automáticamente"""
        toast = tk.Toplevel(self.root)
        toast.withdraw()
        toast.overrideredirect(True)

        frame = tk.Frame(toast, bg=color, padx=20, pady=15)
        frame.pack()

        tk.Label(
            frame,
            text=mensaje,
            font=("Segoe UI", 11),
            bg=color,
            fg="white",
            justify='center'
        ).pack()

        toast.update_idletasks()
        w = toast.winfo_width()
        h = toast.winfo_height()
        x = (toast.winfo_screenwidth() // 2) - (w // 2)
        y = toast.winfo_screenheight() - h - 50
        toast.geometry(f'+{x}+{y}')
        toast.deiconify()
        toast.after(duracion, toast.destroy)

    def _construir_ui(self):
        """Construye la interfaz gráfica"""

        # Header
        header = tk.Frame(self.root, bg="#7c3aed", pady=20)
        header.pack(fill='x')

        tk.Label(
            header,
            text="🗓️ Gestor de Tareas Automáticas",
            font=("Segoe UI", 16, "bold"),
            bg="#7c3aed",
            fg="white"
        ).pack()

        tk.Label(
            header,
            text="Programa publicaciones automáticas en días y horarios específicos",
            font=("Segoe UI", 10),
            bg="#7c3aed",
            fg="white"
        ).pack()

        # Toolbar
        toolbar = tk.Frame(self.root, bg="#f0f0f0", pady=15)
        toolbar.pack(fill='x', padx=20)

        tk.Button(
            toolbar,
            text="➕ Nueva Tarea",
            font=("Segoe UI", 11, "bold"),
            bg="#7c3aed",
            fg="white",
            width=20,
            command=self._nueva_tarea
        ).pack(side='left', padx=(0, 10))

        tk.Button(
            toolbar,
            text="🔄 Actualizar",
            font=("Segoe UI", 11),
            bg="#e0e0e0",
            width=15,
            command=self._cargar_tareas
        ).pack(side='left')

        # Tabla de tareas
        frame_lista = tk.Frame(self.root, bg="#f0f0f0")
        frame_lista.pack(fill='both', expand=True, padx=20, pady=(0, 15))

        scrollbar = ttk.Scrollbar(frame_lista)
        scrollbar.pack(side='right', fill='y')

        columnas = ('nombre', 'dias', 'proxima', 'estado')
        self.tree = ttk.Treeview(
            frame_lista,
            columns=columnas,
            show='headings',
            yscrollcommand=scrollbar.set,
            selectmode='browse'
        )

        self.tree.heading('nombre', text='Nombre de Tarea')
        self.tree.heading('dias', text='Días')
        self.tree.heading('proxima', text='Próxima Ejecución')
        self.tree.heading('estado', text='Estado')

        self.tree.column('nombre', width=300)
        self.tree.column('dias', width=100)
        self.tree.column('proxima', width=250)
        self.tree.column('estado', width=150)

        self.tree.pack(fill='both', expand=True)
        scrollbar.config(command=self.tree.yview)
        self.tree.bind('<Double-1>', lambda e: self._editar_tarea())

        # Botones de acción
        acciones_frame = tk.Frame(self.root, bg="#f0f0f0")
        acciones_frame.pack(fill='x', padx=20, pady=(0, 15))

        tk.Button(
            acciones_frame,
            text="📋 Ver Detalles",
            font=("Segoe UI", 10),
            bg="#17a2b8",
            fg="white",
            width=15,
            command=self._ver_detalles
        ).pack(side='left', padx=(0, 10))

        tk.Button(
            acciones_frame,
            text="✏️ Editar",
            font=("Segoe UI", 10),
            bg="#ffc107",
            width=12,
            command=self._editar_tarea
        ).pack(side='left', padx=(0, 10))

        tk.Button(
            acciones_frame,
            text="🗑️ Eliminar",
            font=("Segoe UI", 10),
            bg="#dc3545",
            fg="white",
            width=12,
            command=self._eliminar_tarea
        ).pack(side='left')

    def _cargar_tareas(self):
        """Carga las tareas programadas del sistema"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            resultado = subprocess.run(
                ['schtasks', '/Query', '/FO', 'CSV'],
                capture_output=True,
                text=True,
                encoding='cp850',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if resultado.returncode != 0:
                self.tree.insert('', 'end', values=('Error cargando tareas', '', '', ''))
                return

            lineas = resultado.stdout.strip().split('\n')
            tareas_encontradas = False

            for linea in lineas[1:]:
                partes = linea.split('","')
                if len(partes) >= 3:
                    nombre = partes[0].replace('"', '').strip()
                    proxima = partes[1].replace('"', '').strip() if len(partes) > 1 else 'N/A'
                    estado_raw = partes[2].replace('"', '').strip() if len(partes) > 2 else 'N/A'

                    if self.prefijo_tarea in nombre:
                        nombre_corto = nombre.split('\\')[-1]
                        detalles = self._obtener_detalles_tarea(nombre_corto)
                        dias_texto = self._extraer_dias_cortos(detalles) if detalles else 'N/A'

                        estado_lower = estado_raw.lower()
                        if any(x in estado_lower for x in ['ready', 'listo', 'en espera', 'queued']):
                            estado = '✅ Activa'
                        elif any(x in estado_lower for x in ['disabled', 'deshabilitado', 'desactivado']):
                            estado = '⏸️ Pausada'
                        elif any(x in estado_lower for x in ['running', 'en ejecución', 'ejecutando']):
                            estado = '▶️ En ejecución'
                        else:
                            estado = estado_raw

                        self.tree.insert('', 'end', values=(nombre_corto, dias_texto, proxima, estado))
                        tareas_encontradas = True

            if not tareas_encontradas:
                self.tree.insert('', 'end', values=('No hay tareas programadas', '', '', ''))

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar tareas:\n{e}")

    def _obtener_detalles_tarea(self, nombre_tarea):
        """Obtiene detalles de una tarea específica"""
        try:
            nombre_completo = (
                nombre_tarea if nombre_tarea.startswith(self.prefijo_tarea)
                else f"{self.prefijo_tarea}_{nombre_tarea}"
            )

            resultado = subprocess.run(
                ['schtasks', '/Query', '/TN', nombre_completo, '/FO', 'LIST', '/V'],
                capture_output=True,
                text=True,
                encoding='cp850',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if resultado.returncode != 0:
                return None

            detalles = {}
            for linea in resultado.stdout.split('\n'):
                linea = linea.strip()
                if ':' in linea:
                    partes = linea.split(':', 1)
                    if len(partes) == 2:
                        clave = partes[0].strip()
                        valor = partes[1].strip()
                        detalles[clave] = valor

            return detalles

        except Exception:
            return None

    def _extraer_dias_cortos(self, detalles):
        """Extrae los días de la tarea en formato corto (L,M,X...)"""
        try:
            for clave in detalles:
                if 'día' in clave.lower() or 'day' in clave.lower():
                    valor = detalles[clave]
                    dias_en = [d.strip() for d in valor.split(',')]
                    dias_cortos = [self.dias_map_inverso.get(d, d) for d in dias_en]
                    return ','.join(dias_cortos)
            return 'Diario'
        except Exception:
            return 'N/A'

    def _nueva_tarea(self):
        """Abre el formulario para crear una nueva tarea"""
        self._abrir_formulario_tarea()

    def _editar_tarea(self):
        """Edita la tarea seleccionada"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Selecciona una tarea para editar")
            return

        item = self.tree.item(seleccion[0])
        nombre_tarea = item['values'][0]

        if nombre_tarea == 'No hay tareas programadas':
            return

        detalles = self._obtener_detalles_tarea(nombre_tarea)
        self._abrir_formulario_tarea(nombre_tarea, detalles, es_edicion=True)

    def _abrir_formulario_tarea(self, nombre_actual=None, detalles=None, es_edicion=False):
        """Formulario para crear o editar una tarea"""
        ventana = tk.Toplevel(self.root)
        ventana.withdraw()
        ventana.title("✏️ Editar Tarea" if es_edicion else "➕ Nueva Tarea")
        ventana.resizable(False, False)
        ventana.configure(bg="#f0f0f0")
        ventana.transient(self.root)
        ventana.grab_set()

        # Header
        header = tk.Frame(ventana, bg="#7c3aed", pady=12)
        header.pack(fill='x')
        tk.Label(
            header,
            text="✏️ Editar Tarea" if es_edicion else "➕ Nueva Tarea",
            font=("Segoe UI", 13, "bold"),
            bg="#7c3aed",
            fg="white"
        ).pack()

        frame = tk.Frame(ventana, bg="#f0f0f0", padx=30, pady=15)
        frame.pack(fill='both', expand=True)

        # Nombre
        tk.Label(frame, text="Nombre de la tarea:", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w')
        var_nombre = tk.StringVar(value=nombre_actual or f"Publicacion_{datetime.now().strftime('%H%M')}")
        tk.Entry(frame, textvariable=var_nombre, width=35, font=("Segoe UI", 10),
                 state='disabled' if es_edicion else 'normal').pack(anchor='w', pady=(0, 12))

        # Hora
        tk.Label(frame, text="Hora de ejecución (HH:MM):", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w')
        hora_actual = '08:00'
        if detalles:
            for clave in detalles:
                if 'hora' in clave.lower() or 'start time' in clave.lower():
                    hora_actual = detalles[clave][:5]
                    break
        var_hora = tk.StringVar(value=hora_actual)
        tk.Entry(frame, textvariable=var_hora, width=10, font=("Segoe UI", 10)).pack(anchor='w', pady=(0, 12))

        # Frecuencia
        tk.Label(frame, text="Frecuencia:", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w')
        var_freq = tk.StringVar(value='WEEKLY')
        frame_freq = tk.Frame(frame, bg="#f0f0f0")
        frame_freq.pack(anchor='w', pady=(0, 12))
        for opcion, label in [('DAILY', 'Diaria'), ('WEEKLY', 'Semanal')]:
            tk.Radiobutton(
                frame_freq, text=label,
                variable=var_freq, value=opcion,
                bg="#f0f0f0", font=("Segoe UI", 10)
            ).pack(side='left', padx=8)

        # Días de la semana
        tk.Label(frame, text="Días (solo para semanal):", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w')
        frame_dias = tk.Frame(frame, bg="#f0f0f0")
        frame_dias.pack(anchor='w', pady=(0, 12))

        dias_vars = {}
        dias_labels = [('L', 'Lun'), ('M', 'Mar'), ('X', 'Mié'), ('J', 'Jue'),
                       ('V', 'Vie'), ('S', 'Sáb'), ('D', 'Dom')]

        for clave, label in dias_labels:
            var = tk.BooleanVar(value=True if clave in ['L', 'M', 'X', 'J', 'V'] else False)
            dias_vars[clave] = var
            tk.Checkbutton(
                frame_dias, text=label, variable=var,
                bg="#f0f0f0", font=("Segoe UI", 9)
            ).pack(side='left', padx=3)

        # Botones
        frame_btns = tk.Frame(ventana, bg="#f0f0f0", pady=10)
        frame_btns.pack(fill='x')

        tk.Button(
            frame_btns,
            text="Cancelar",
            font=("Segoe UI", 10),
            bg="#6c757d",
            fg="white",
            width=12,
            command=lambda: [ventana.grab_release(), ventana.destroy()]
        ).pack(side='left', padx=(30, 10))

        def guardar():
            nombre = var_nombre.get().strip()
            hora = var_hora.get().strip()
            frecuencia = var_freq.get()

            if not nombre:
                messagebox.showwarning("Aviso", "Ingresa un nombre para la tarea", parent=ventana)
                return

            if not hora or len(hora) != 5 or hora[2] != ':':
                messagebox.showwarning("Aviso", "Formato de hora inválido. Usa HH:MM", parent=ventana)
                return

            dias_seleccionados = [
                self.dias_map[k] for k, v in dias_vars.items() if v.get()
            ]

            if frecuencia == 'WEEKLY' and not dias_seleccionados:
                messagebox.showwarning("Aviso", "Selecciona al menos un día", parent=ventana)
                return

            ventana.grab_release()
            ventana.destroy()
            self._crear_tarea_windows(nombre, frecuencia, hora, dias_seleccionados)

        tk.Button(
            frame_btns,
            text="💾 Guardar Cambios" if es_edicion else "✅ Crear Tarea",
            font=("Segoe UI", 10, "bold"),
            bg="#28a745",
            fg="white",
            width=18,
            command=guardar
        ).pack(side='right', padx=(10, 30))

        x = (ventana.winfo_screenwidth() // 2) - 300
        y = (ventana.winfo_screenheight() // 2) - 300
        ventana.geometry(f'600x500+{x}+{y}')
        ventana.deiconify()

    def _crear_tarea_windows(self, nombre, frecuencia, horario, dias=None, ya_mostro_aviso=False):
        """Crea una tarea en el Programador de Tareas de Windows"""
        try:
            nombre_completo = (
                nombre if nombre.startswith(self.prefijo_tarea)
                else f"{self.prefijo_tarea}_{nombre}"
            )

            if self.ruta_exe and os.path.exists(self.ruta_exe):
                comando_tarea = f'"{self.ruta_exe}"'
            else:
                directorio_trabajo = os.path.dirname(self.ruta_script)
                comando_tarea = f'cmd /c "cd /d "{directorio_trabajo}" && py "{self.ruta_script}""'

            comando = [
                'schtasks', '/Create',
                '/TN', nombre_completo,
                '/TR', comando_tarea,
                '/SC', frecuencia,
                '/ST', horario
            ]

            if frecuencia == 'WEEKLY' and dias:
                comando.extend(['/D', ','.join(dias)])

            comando.append('/F')

            resultado = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if resultado.returncode == 0:
                self._cargar_tareas()
                if not ya_mostro_aviso:
                    detalles = self._obtener_detalles_tarea(nombre_completo)
                    proxima = detalles.get('Hora próxima ejecución', 'próximamente') if detalles else 'próximamente'
                    self._mostrar_toast(f"✅ Tarea programada para {proxima}")
            else:
                messagebox.showerror("❌ Error", f"No se pudo crear la tarea:\n{resultado.stderr}")

        except Exception as e:
            messagebox.showerror("❌ Error", f"Error creando tarea:\n{e}")

    def _ver_detalles(self):
        """Muestra los detalles de la tarea seleccionada"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Selecciona una tarea para ver sus detalles")
            return

        item = self.tree.item(seleccion[0])
        nombre_tarea = item['values'][0]

        if nombre_tarea == 'No hay tareas programadas':
            return

        detalles = self._obtener_detalles_tarea(nombre_tarea)

        if not detalles:
            messagebox.showinfo("Detalles", "No se pudieron obtener los detalles de la tarea")
            return

        ventana = tk.Toplevel(self.root)
        ventana.withdraw()
        ventana.title(f"📋 Detalles — {nombre_tarea}")
        ventana.resizable(False, False)
        ventana.configure(bg="#f0f0f0")
        ventana.transient(self.root)
        ventana.grab_set()

        header = tk.Frame(ventana, bg="#7c3aed", pady=10)
        header.pack(fill='x')
        tk.Label(
            header, text=f"📋 {nombre_tarea}",
            font=("Segoe UI", 12, "bold"),
            bg="#7c3aed", fg="white"
        ).pack()

        frame = tk.Frame(ventana, bg="white", padx=20, pady=15)
        frame.pack(fill='both', expand=True, padx=15, pady=10)

        campos_relevantes = [
            'Nombre de la tarea', 'Estado', 'Hora de inicio',
            'Hora próxima ejecución', 'Última hora de ejecución',
            'Última vez que se ejecutó', 'Programar tipo'
        ]

        for clave, valor in detalles.items():
            if any(c.lower() in clave.lower() for c in campos_relevantes):
                row = tk.Frame(frame, bg="white")
                row.pack(fill='x', pady=3)
                tk.Label(
                    row, text=f"{clave}:",
                    font=("Segoe UI", 9, "bold"),
                    bg="white", anchor='w', width=30
                ).pack(side='left')
                tk.Label(
                    row, text=valor,
                    font=("Segoe UI", 9),
                    bg="white", anchor='w'
                ).pack(side='left')

        tk.Button(
            ventana, text="Cerrar",
            font=("Segoe UI", 10),
            bg="#6c757d", fg="white", width=12,
            command=lambda: [ventana.grab_release(), ventana.destroy()]
        ).pack(pady=10)

        ventana.protocol("WM_DELETE_WINDOW",
                         lambda: [ventana.grab_release(), ventana.destroy()])

        x = (ventana.winfo_screenwidth() // 2) - 300
        y = (ventana.winfo_screenheight() // 2) - 200
        ventana.geometry(f'600x420+{x}+{y}')
        ventana.deiconify()

    def _eliminar_tarea(self):
        """Elimina la tarea seleccionada"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Selecciona una tarea para eliminar")
            return

        item = self.tree.item(seleccion[0])
        nombre_tarea = item['values'][0]

        if nombre_tarea == 'No hay tareas programadas':
            return

        if nombre_tarea.startswith('\\'):
            nombre_tarea = nombre_tarea[1:]

        if not messagebox.askyesno("Confirmar", f"¿Eliminar la tarea '{nombre_tarea}'?"):
            return

        try:
            nombre_completo = (
                nombre_tarea if nombre_tarea.startswith(self.prefijo_tarea)
                else f"{self.prefijo_tarea}_{nombre_tarea}"
            )

            resultado = subprocess.run(
                ['schtasks', '/Delete', '/TN', nombre_completo, '/F'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if resultado.returncode == 0:
                self._cargar_tareas()
                self._mostrar_toast("✅ Tarea eliminada correctamente")
            else:
                messagebox.showerror("❌ Error", "No se pudo eliminar la tarea")

        except Exception as e:
            messagebox.showerror("❌ Error", f"Error eliminando tarea:\n{e}")

    def ejecutar(self):
        """Inicia la interfaz"""
        self.root.mainloop()


def main():
    gestor = GestorTareasGUI()
    gestor.ejecutar()


if __name__ == "__main__":
    main()