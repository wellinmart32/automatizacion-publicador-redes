#!/usr/bin/env python3
"""
Script de Reinicio del Sistema - Publicador Redes
Permite reiniciar diferentes partes del sistema con un menú interactivo
Simétrico a reiniciar_sistema.py de MensajesBiblicos
"""

import json
import os
import shutil
from datetime import datetime


class ReiniciadorSistema:
    """Gestiona el reinicio de diferentes componentes del sistema"""

    def __init__(self):
        self.archivo_registro = "registro_publicaciones.json"
        self.carpeta_anuncios = "anuncios"
        self.carpeta_mensajes = "mensajes"
        self.carpeta_perfiles = "perfiles"

    def limpiar_pantalla(self):
        """Limpia la consola"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def mostrar_header(self):
        """Muestra el encabezado"""
        print("=" * 70)
        print(" " * 15 + "🔄 REINICIAR SISTEMA")
        print(" " * 12 + "Publicador Redes — AutomaPro")
        print("=" * 70)
        print()

    def cargar_registro(self):
        """Carga el registro actual"""
        if not os.path.exists(self.archivo_registro):
            return None
        try:
            with open(self.archivo_registro, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def mostrar_estado_actual(self):
        """Muestra el estado actual del sistema"""
        self.limpiar_pantalla()
        self.mostrar_header()

        print("📊 ESTADO ACTUAL DEL SISTEMA:\n")

        registro = self.cargar_registro()

        if not registro:
            print("⚠️  No se encontró registro_publicaciones.json")
            print("   El sistema parece estar sin inicializar.\n")
        else:
            print(f"📈 PUBLICACIONES:")
            print(f"   Total: {registro.get('total_publicaciones', 0)}")
            print(f"   Exitosas: {registro.get('publicaciones_exitosas', 0)}")
            print(f"   Fallidas: {registro.get('publicaciones_fallidas', 0)}")
            ultima = registro.get('ultima_publicacion', 'Nunca')
            print(f"   Última publicación: {ultima}")

        # Contar anuncios
        print(f"\n📂 ARCHIVOS:")
        if os.path.exists(self.carpeta_anuncios):
            anuncios = [
                d for d in os.listdir(self.carpeta_anuncios)
                if os.path.isdir(os.path.join(self.carpeta_anuncios, d))
                and d.startswith('anuncio_')
            ]
            print(f"   Anuncios: {len(anuncios)} carpetas")

        if os.path.exists(self.carpeta_perfiles):
            perfiles = os.listdir(self.carpeta_perfiles)
            print(f"   Perfiles de navegador: {len(perfiles)} carpetas")

        print()
        input("Presiona Enter para continuar...")

    def reiniciar_historial_publicaciones(self):
        """Opción 1: Reinicia solo el historial de publicaciones"""
        self.limpiar_pantalla()
        self.mostrar_header()

        print("📊 OPCIÓN 1: REINICIAR HISTORIAL DE PUBLICACIONES\n")

        registro = self.cargar_registro()

        if not registro:
            print("⚠️  No hay registro que reiniciar")
            input("\nPresiona Enter para continuar...")
            return

        total = registro.get('total_publicaciones', 0)

        print("📋 ACCIÓN A REALIZAR:")
        print(f"   Se borrarán {total} publicaciones del historial")
        print(f"   Las estadísticas se resetearán a 0\n")

        print("=" * 70)
        print("\n⚠️  ADVERTENCIA CRÍTICA: Esta acción es PERMANENTE\n")
        confirmacion = input("Escribe 'SI' en MAYÚSCULAS para confirmar: ")

        if confirmacion != 'SI':
            print("\n❌ Operación cancelada")
            input("\nPresiona Enter para continuar...")
            return

        # Resetear registro
        registro['total_publicaciones'] = 0
        registro['publicaciones_exitosas'] = 0
        registro['publicaciones_fallidas'] = 0
        registro['ultima_publicacion'] = None
        registro['historial'] = []

        with open(self.archivo_registro, 'w', encoding='utf-8') as f:
            json.dump(registro, f, indent=2, ensure_ascii=False)

        print("\n✅ Historial reiniciado exitosamente")
        print("   Total publicaciones: 0")
        input("\nPresiona Enter para continuar...")

    def reiniciar_todo_sistema(self):
        """Opción 2: Reinicia TODO el sistema"""
        self.limpiar_pantalla()
        self.mostrar_header()

        print("🔄 OPCIÓN 2: REINICIAR TODO EL SISTEMA\n")

        print("⚠️  ADVERTENCIA: Esta acción eliminará:\n")
        print("   ❌ registro_publicaciones.json → se reseteará completamente")
        print("   ❌ perfiles/ → sesiones de navegador")
        print("\n   ✅ SE CONSERVARÁ:")
        print("   ✓ anuncios/ → tus anuncios creados")
        print("   ✓ config_global.txt → tu configuración")
        print("   ✓ Código del sistema\n")
        print("\n💡 Es como ejecutar el sistema por primera vez.")

        print("\n" + "=" * 70)
        print("\n⚠️  ADVERTENCIA CRÍTICA: Esta acción es PERMANENTE\n")
        confirmacion = input("Escribe 'SI' en MAYÚSCULAS para confirmar: ")

        if confirmacion != 'SI':
            print("\n❌ Operación cancelada")
            input("\nPresiona Enter para continuar...")
            return

        print("\n🔄 Reiniciando sistema...\n")

        # 1. Resetear registro
        registro_nuevo = {
            'total_publicaciones': 0,
            'publicaciones_exitosas': 0,
            'publicaciones_fallidas': 0,
            'ultima_publicacion': None,
            'historial': []
        }

        with open(self.archivo_registro, 'w', encoding='utf-8') as f:
            json.dump(registro_nuevo, f, indent=2, ensure_ascii=False)
        print("   ✅ registro_publicaciones.json reseteado")

        # 2. Borrar perfiles de navegador
        if os.path.exists(self.carpeta_perfiles):
            try:
                shutil.rmtree(self.carpeta_perfiles)
                os.makedirs(self.carpeta_perfiles)
                print("   ✅ Carpeta 'perfiles/' eliminada")
            except Exception as e:
                print(f"   ⚠️  Error eliminando perfiles/: {e}")
        else:
            print("   ℹ️  Carpeta 'perfiles/' no existe")

        print("\n" + "=" * 70)
        print("✅ SISTEMA REINICIADO COMPLETAMENTE")
        print("=" * 70)
        print("\n💡 PRÓXIMOS PASOS:")
        print("   1. Abre el Panel de Control")
        print("   2. Configura tus redes sociales")
        print("   3. Agrega tus anuncios")
        print("   4. ¡Empieza a publicar!")
        print("=" * 70)

        input("\nPresiona Enter para continuar...")

    def mostrar_menu(self):
        """Muestra el menú principal"""
        while True:
            self.limpiar_pantalla()
            self.mostrar_header()

            print("¿Qué deseas hacer?\n")
            print("1. 📊 Reiniciar SOLO historial de publicaciones")
            print("   └─ Limpia historial y estadísticas\n")

            print("2. 💥 Reiniciar TODO el sistema")
            print("   └─ Resetea historial + elimina perfiles")
            print("   └─ Conserva anuncios y configuración\n")

            print("3. 📋 Ver estado actual del sistema\n")

            print("4. ❌ Salir\n")

            print("=" * 70)
            opcion = input("Selecciona una opción (1-4): ")

            if opcion == '1':
                self.reiniciar_historial_publicaciones()
            elif opcion == '2':
                self.reiniciar_todo_sistema()
            elif opcion == '3':
                self.mostrar_estado_actual()
            elif opcion == '4':
                print("\n👋 ¡Hasta luego!\n")
                break
            else:
                print("\n❌ Opción inválida. Intenta de nuevo.")
                input("\nPresiona Enter para continuar...")


def main():
    """Función principal"""
    try:
        reiniciador = ReiniciadorSistema()
        reiniciador.mostrar_menu()
    except KeyboardInterrupt:
        print("\n\n❌ Proceso cancelado por el usuario\n")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresiona Enter para salir...")


if __name__ == "__main__":
    main()