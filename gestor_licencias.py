import tkinter as tk
from tkinter import messagebox, simpledialog
import webbrowser


class DialogosLicencia:
    """Diálogos de interfaz para gestión de licencias"""

    @staticmethod
    def _root_topmost():
        """Crea una ventana Tk oculta siempre al frente para diálogos en segundo plano"""
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        return root

    @staticmethod
    def solicitar_codigo_licencia():
        """Mostrar diálogo para ingresar código de licencia"""
        root = DialogosLicencia._root_topmost()
        codigo = simpledialog.askstring(
            "Código de Licencia",
            "Ingresa tu código de licencia:\n\n(Ejemplo: LIC-TRIAL001)",
            parent=root
        )
        root.destroy()
        return codigo

    @staticmethod
    def mostrar_trial_expirado(codigo_licencia):
        """Mostrar diálogo cuando expira el trial"""
        root = DialogosLicencia._root_topmost()
        mensaje = (
            "Tu período de prueba ha terminado\n\n"
            "Desbloquea todas las funciones premium ahora\n\n"
            "Precio: $19.99 USD (pago único)\n"
            "✅ Sin suscripciones\n"
            "✅ Actualizaciones gratis\n"
            "✅ Soporte prioritario"
        )
        respuesta = messagebox.askquestion(
            "Trial Expirado",
            mensaje,
            icon='warning',
            type='yesno',
            default='yes',
            parent=root
        )
        root.destroy()
        if respuesta == 'yes':
            url = f"https://automapro-frontend.vercel.app/cliente/comprar?codigo={codigo_licencia}&app=2"
            webbrowser.open(url)
        return False

    @staticmethod
    def mostrar_banner_trial(dias_restantes):
        """Mostrar mensaje de trial activo"""
        print(f"\n{'='*70}")
        print(f"⚠️  MODO TRIAL - Quedan {dias_restantes} días")
        print(f"{'='*70}\n")

    @staticmethod
    def mostrar_error(mensaje):
        """Mostrar diálogo de error"""
        root = DialogosLicencia._root_topmost()
        messagebox.showerror("Error de Licencia", mensaje, parent=root)
        root.destroy()

    @staticmethod
    def mostrar_exito(mensaje):
        """Mostrar diálogo de éxito"""
        root = DialogosLicencia._root_topmost()
        messagebox.showinfo("Licencia Activada", mensaje, parent=root)
        root.destroy()

    @staticmethod
    def confirmar_salida():
        """Confirmar si el usuario quiere salir"""
        root = DialogosLicencia._root_topmost()
        respuesta = messagebox.askyesno(
            "Salir",
            "¿Deseas salir de la aplicación?",
            icon='question',
            parent=root
        )
        root.destroy()
        return respuesta

    @staticmethod
    def mostrar_funcion_premium():
        """Mostrar mensaje cuando se intenta usar función premium en TRIAL"""
        root = DialogosLicencia._root_topmost()
        mensaje = (
            "Esta función requiere licencia completa\n\n"
            "Desbloquea esta y todas las funciones premium\n"
            "Precio: $19.99 USD (pago único)"
        )
        respuesta = messagebox.askquestion(
            "Función Premium",
            mensaje,
            icon='info',
            type='yesno',
            default='no',
            parent=root
        )
        root.destroy()
        if respuesta == 'yes':
            webbrowser.open("https://automapro-frontend.vercel.app/cliente/comprar?app=2")