import os
import json
from datetime import datetime
from pathlib import Path


class GestorRegistro:
    """Gestor de registro de publicaciones para PublicadorRedes"""

    def __init__(self):
        if os.name == 'nt':
            base_path = Path(os.environ.get('USERPROFILE', '~'))
        else:
            base_path = Path.home()

        self.carpeta_registro = base_path / '.config' / 'AutomaPro' / 'PublicadorRedes'
        self.archivo_registro = self.carpeta_registro / 'registro_publicaciones.json'
        self._inicializar_registro()

    def _inicializar_registro(self):
        """Inicializa el archivo de registro si no existe"""
        try:
            self.carpeta_registro.mkdir(parents=True, exist_ok=True)
            if not self.archivo_registro.exists():
                registro_inicial = {
                    'total_publicaciones': 0,
                    'publicaciones_exitosas': 0,
                    'publicaciones_fallidas': 0,
                    'ultima_publicacion': None,
                    'historial': []
                }
                with open(self.archivo_registro, 'w', encoding='utf-8') as f:
                    json.dump(registro_inicial, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error inicializando registro: {e}")

    def _leer_registro(self):
        """Lee el registro actual"""
        try:
            if self.archivo_registro.exists():
                with open(self.archivo_registro, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error leyendo registro: {e}")
        return {
            'total_publicaciones': 0,
            'publicaciones_exitosas': 0,
            'publicaciones_fallidas': 0,
            'ultima_publicacion': None,
            'historial': []
        }

    def _guardar_registro(self, registro):
        """Guarda el registro actualizado"""
        try:
            with open(self.archivo_registro, 'w', encoding='utf-8') as f:
                json.dump(registro, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando registro: {e}")

    def registrar_publicacion_exitosa(self, plataforma, tipo_contenido, anuncio_archivo):
        """Registra una publicación exitosa"""
        registro = self._leer_registro()
        registro['total_publicaciones'] += 1
        registro['publicaciones_exitosas'] += 1
        registro['ultima_publicacion'] = datetime.now().isoformat()
        registro['historial'].append({
            'fecha': datetime.now().isoformat(),
            'plataforma': plataforma,
            'tipo_contenido': tipo_contenido,
            'anuncio': anuncio_archivo,
            'resultado': 'exitoso'
        })
        # Mantener solo los últimos 100 registros
        if len(registro['historial']) > 100:
            registro['historial'] = registro['historial'][-100:]
        self._guardar_registro(registro)

    def registrar_error(self, plataforma, tipo_error, detalle):
        """Registra un error de publicación"""
        registro = self._leer_registro()
        registro['total_publicaciones'] += 1
        registro['publicaciones_fallidas'] += 1
        registro['historial'].append({
            'fecha': datetime.now().isoformat(),
            'plataforma': plataforma,
            'tipo_error': tipo_error,
            'detalle': detalle,
            'resultado': 'fallido'
        })
        if len(registro['historial']) > 100:
            registro['historial'] = registro['historial'][-100:]
        self._guardar_registro(registro)

    def puede_publicar_ahora(self, tiempo_minimo_segundos, plataforma=None):
        """Verifica si puede publicar según el tiempo mínimo entre publicaciones"""
        registro = self._leer_registro()
        ultima = registro.get('ultima_publicacion')
        if not ultima:
            return True, "Primera publicación"
        try:
            ultima_dt = datetime.fromisoformat(ultima)
            segundos_desde_ultima = (datetime.now() - ultima_dt).total_seconds()
            if segundos_desde_ultima >= tiempo_minimo_segundos:
                return True, "Tiempo suficiente transcurrido"
            restantes = int(tiempo_minimo_segundos - segundos_desde_ultima)
            return False, f"Esperar {restantes} segundos más"
        except Exception:
            return True, "Error leyendo tiempo"

    def obtener_estadisticas(self):
        """Retorna estadísticas del registro"""
        registro = self._leer_registro()
        total = registro.get('total_publicaciones', 0)
        exitosas = registro.get('publicaciones_exitosas', 0)
        tasa = (exitosas / total * 100) if total > 0 else 0
        return {
            'total': total,
            'exitosas': exitosas,
            'fallidas': registro.get('publicaciones_fallidas', 0),
            'tasa_exito': round(tasa, 1),
            'ultima_publicacion': registro.get('ultima_publicacion')
        }

    def mostrar_estadisticas(self):
        """Muestra estadísticas en consola"""
        stats = self.obtener_estadisticas()
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"   Total publicaciones: {stats['total']}")
        print(f"   Exitosas: {stats['exitosas']}")
        print(f"   Fallidas: {stats['fallidas']}")
        print(f"   Tasa de éxito: {stats['tasa_exito']}%")
        if stats['ultima_publicacion']:
            print(f"   Última publicación: {stats['ultima_publicacion'][:19]}")