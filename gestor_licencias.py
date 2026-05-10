import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path


class GestorLicencias:
    """Gestor de licencias con sistema de cache local"""

    def __init__(self, nombre_app="PublicadorRedes"):
        self.nombre_app = nombre_app
        self.url_backend = "https://automapro-backend.onrender.com/api/public/verificar-licencia"

        self.codigo_developer_master = "LIC-MASTER-WELLI"

        if os.name == 'nt':
            base_path = Path(os.environ.get('USERPROFILE', '~'))
        else:
            base_path = Path.home()

        self.carpeta_config = base_path / '.config' / 'AutomaPro' / nombre_app
        self.archivo_config = self.carpeta_config / 'config.json'
        self.dias_revalidacion = 7

        if os.name == 'nt':
            appdata = Path(os.environ.get('LOCALAPPDATA', base_path / 'AppData' / 'Local'))
        else:
            appdata = Path.home() / '.local' / 'share'
        self.carpeta_respaldo = appdata / 'AutomaPro' / nombre_app
        self.archivo_respaldo = self.carpeta_respaldo / 'lic.json'

    def _es_codigo_developer_permanente(self, codigo):
        return codigo == self.codigo_developer_master

    def obtener_codigo_guardado(self):
        try:
            if self.archivo_config.exists():
                contenido = self.archivo_config.read_text(encoding='utf-8').strip()
                if not contenido:
                    return ''
                datos = json.loads(contenido)
                return datos.get('codigo_licencia', '')
        except Exception as e:
            print(f"Error leyendo configuración local: {e}")
        return ''

    def guardar_codigo_licencia(self, codigo):
        try:
            self.carpeta_config.mkdir(parents=True, exist_ok=True)
            datos = {}
            if self.archivo_config.exists():
                with open(self.archivo_config, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
            datos['codigo_licencia'] = codigo
            with open(self.archivo_config, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error guardando código de licencia: {e}")
            return False

    def _obtener_cache_local(self):
        cache = self._leer_cache(self.archivo_config)
        if cache:
            return cache
        cache_respaldo = self._leer_cache(self.archivo_respaldo, es_respaldo=True)
        if cache_respaldo:
            try:
                self.carpeta_config.mkdir(parents=True, exist_ok=True)
                config = {'datos_licencia': cache_respaldo}
                with open(self.archivo_respaldo, 'r', encoding='utf-8') as f:
                    respaldo = json.load(f)
                if respaldo.get('codigo_licencia'):
                    config['codigo_licencia'] = respaldo['codigo_licencia']
                with open(self.archivo_config, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
            except Exception:
                pass
            return cache_respaldo
        return None

    def _leer_cache(self, archivo, es_respaldo=False):
        try:
            archivo = Path(archivo)
            if not archivo.exists():
                return None
            contenido = archivo.read_text(encoding='utf-8').strip()
            if not contenido:
                return None
            datos = json.loads(contenido)
            cache = datos.get('datos_licencia')
            if not cache:
                return None
            if cache.get('es_developer_permanente'):
                return cache
            if cache.get('tipo') in ['FULL', 'MASTER'] and cache.get('valida'):
                return cache
            fecha_verificacion = cache.get('fecha_verificacion')
            if fecha_verificacion:
                fecha_cache = datetime.fromisoformat(fecha_verificacion)
                dias_desde_verificacion = (datetime.now() - fecha_cache).days
                if dias_desde_verificacion <= self.dias_revalidacion:
                    return cache
        except Exception as e:
            print(f"Error leyendo cache: {e}")
        return None

    def _guardar_cache_local(self, datos_licencia):
        try:
            self.carpeta_config.mkdir(parents=True, exist_ok=True)
            config = {}
            if self.archivo_config.exists():
                with open(self.archivo_config, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            datos_cache = {
                'tipo': datos_licencia.get('tipo'),
                'valida': datos_licencia.get('valida'),
                'expirada': datos_licencia.get('expirada'),
                'dias_restantes': datos_licencia.get('diasRestantes'),
                'fecha_verificacion': datetime.now().isoformat(),
                'es_developer_permanente': datos_licencia.get('developer_permanente', False)
            }
            config['datos_licencia'] = datos_cache
            with open(self.archivo_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            try:
                self.carpeta_respaldo.mkdir(parents=True, exist_ok=True)
                respaldo = {
                    'codigo_licencia': self.obtener_codigo_guardado(),
                    'datos_licencia': datos_cache
                }
                with open(self.archivo_respaldo, 'w', encoding='utf-8') as f:
                    json.dump(respaldo, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"Error guardando respaldo: {e}")
            return True
        except Exception as e:
            print(f"Error guardando cache: {e}")
            return False

    def verificar_licencia(self, codigo_licencia, mostrar_mensajes=True, forzar_backend=False):
        if self._es_codigo_developer_permanente(codigo_licencia):
            datos_permanente = {
                'tipo': 'FULL',
                'valida': True,
                'expirada': False,
                'diasRestantes': 999,
                'developer_permanente': True
            }
            self._guardar_cache_local(datos_permanente)
            if mostrar_mensajes:
                print("👑 Licencia MASTER permanente activada")
            return {
                'tipo': 'FULL',
                'valida': True,
                'expirada': False,
                'diasRestantes': 999,
                'mensaje': 'Licencia MASTER permanente',
                'desde_cache': False,
                'developer_permanente': True
            }

        cache = self._obtener_cache_local()

        try:
            if mostrar_mensajes:
                print(f"🔍 Verificando licencia: {codigo_licencia}")

            payload = {
                'codigo': codigo_licencia,
                'nombreApp': self.nombre_app
            }

            respuesta = requests.post(
                self.url_backend,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=15,
                verify=False
            )

            if respuesta.status_code == 200:
                datos = respuesta.json()
                valida = datos.get('valida', False)
                if valida:
                    self._guardar_cache_local(datos)
                    if mostrar_mensajes:
                        tipo = datos.get('tipo', 'TRIAL')
                        dias = datos.get('diasRestantes')
                        if tipo in ['FULL', 'MASTER']:
                            print("✅ Licencia FULL verificada correctamente")
                        else:
                            print(f"⚠️  Licencia TRIAL — {dias} días restantes")
                return {
                    'tipo': datos.get('tipo', 'TRIAL'),
                    'valida': valida,
                    'expirada': datos.get('expirada', False),
                    'diasRestantes': datos.get('diasRestantes'),
                    'mensaje': datos.get('mensaje', ''),
                    'desde_cache': False,
                    'developer_permanente': datos.get('developer_permanente', False)
                }
            else:
                raise Exception(f"Backend retornó {respuesta.status_code}")

        except Exception as e:
            if cache and cache.get('valida'):
                if mostrar_mensajes:
                    print(f"⚠️  Backend no disponible. Usando cache local.")
                return {
                    'tipo': cache.get('tipo', 'TRIAL'),
                    'valida': True,
                    'expirada': False,
                    'diasRestantes': cache.get('dias_restantes'),
                    'mensaje': 'Licencia válida (cache)',
                    'desde_cache': True,
                    'developer_permanente': cache.get('es_developer_permanente', False)
                }
            else:
                if mostrar_mensajes:
                    print(f"❌ Error: {e}")
                return {
                    'tipo': 'TRIAL',
                    'valida': False,
                    'expirada': False,
                    'diasRestantes': None,
                    'mensaje': f'Error al verificar: {e}',
                    'desde_cache': False,
                    'developer_permanente': False
                }

    def verificar_e_iniciar(self, mostrar_mensajes=True):
        codigo = self.obtener_codigo_guardado()
        if not codigo:
            if mostrar_mensajes:
                print("❌ No hay código de licencia guardado")
            return {
                'tipo': 'TRIAL',
                'valida': False,
                'expirada': False,
                'diasRestantes': None,
                'mensaje': 'No hay código de licencia',
                'desde_cache': False,
                'developer_permanente': False
            }
        return self.verificar_licencia(codigo, mostrar_mensajes)

    def registrar_instalacion(self, email=None):
        try:
            import uuid
            import hashlib
            import socket
            hostname = socket.gethostname()
            username = os.environ.get('USERNAME', os.environ.get('USER', 'unknown'))
            try:
                mac = hex(uuid.getnode())[2:]
            except Exception:
                mac = '000000000000'
            device_string = f"{hostname}_{username}_{mac}_{self.nombre_app}"
            device_uuid = hashlib.sha256(device_string.encode()).hexdigest()[:32]
            payload = {
                'deviceUuid': device_uuid,
                'nombreApp': self.nombre_app,
                'hostname': hostname
            }
            if email:
                payload['email'] = email
            response = requests.post(
                self.url_backend.replace('/verificar-licencia', '/registrar-instalacion'),
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10,
                verify=False
            )
            if response.status_code == 200:
                datos = response.json()
                codigo = datos.get('codigo')
                if codigo:
                    self.guardar_codigo_licencia(codigo)
                    return codigo
        except Exception as e:
            print(f"⚠️  Error registrando instalación: {e}")
        return None

    def verificar_email(self, email):
        try:
            url = self.url_backend.replace('/verificar-licencia', '/verificar-email')
            respuesta = requests.get(
                url,
                params={'email': email, 'app': self.nombre_app},
                timeout=10,
                verify=False
            )
            if respuesta.status_code == 200:
                return respuesta.json()
        except Exception as e:
            print(f"⚠️  Error verificando email: {e}")
        return None

    def verificar_actualizacion(self, version_actual):
        try:
            url = f"https://automapro-backend.onrender.com/api/public/version?nombre=PublicadorRedes"
            respuesta = requests.get(url, timeout=10, verify=False)
            if respuesta.status_code == 200:
                datos = respuesta.json()
                version_nueva = datos.get('version', version_actual)
                url_descarga = datos.get('rutaArchivo', '')
                hay_actualizacion = version_nueva != version_actual and version_nueva != ''
                return {
                    'hay_actualizacion': hay_actualizacion,
                    'version_actual': version_actual,
                    'version_nueva': version_nueva,
                    'url_descarga': url_descarga,
                    'ruta_archivo': url_descarga
                }
        except Exception as e:
            print(f"⚠️  Error en verificar_actualizacion: {e}")
        return {'hay_actualizacion': False}

    def limpiar_cache(self):
        try:
            if self.archivo_config.exists():
                self.archivo_config.unlink()
                print("✅ Cache eliminado correctamente")
                return True
        except Exception as e:
            print(f"❌ Error al eliminar cache: {e}")
            return False


if __name__ == "__main__":
    print("=== Prueba del Gestor de Licencias ===\n")
    gestor = GestorLicencias()
    print("Verificando con código guardado...")
    resultado = gestor.verificar_e_iniciar()
    print(f"Resultado: {resultado}\n")