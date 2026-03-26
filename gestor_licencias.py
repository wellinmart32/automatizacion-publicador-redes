import os
import json
import requests
from datetime import datetime
from pathlib import Path


class GestorLicencias:
    """Gestor de licencias con sistema de cache local"""

    def __init__(self, nombre_app="PublicadorRedes"):
        self.nombre_app = nombre_app
        self.url_backend = "https://automapro-backend.onrender.com/api/public/verificar-licencia"

        # Código developer maestro (funciona para todas las apps)
        self.codigo_developer_master = "LIC-MASTER-WELLI"

        # Ruta del archivo de configuración local
        if os.name == 'nt':
            base_path = Path(os.environ.get('USERPROFILE', '~'))
        else:
            base_path = Path.home()

        self.carpeta_config = base_path / '.config' / 'AutomaPro' / nombre_app
        self.archivo_config = self.carpeta_config / 'config.json'
        self.dias_revalidacion = 7

        # Respaldo permanente en AppData
        if os.name == 'nt':
            appdata = Path(os.environ.get('LOCALAPPDATA', base_path / 'AppData' / 'Local'))
        else:
            appdata = Path.home() / '.local' / 'share'
        self.carpeta_respaldo = appdata / 'AutomaPro' / nombre_app
        self.archivo_respaldo = self.carpeta_respaldo / 'lic.json'

    def _es_codigo_developer_permanente(self, codigo):
        """Verifica si es un código developer master"""
        return codigo == self.codigo_developer_master

    def obtener_codigo_guardado(self):
        """Obtiene el código de licencia guardado localmente"""
        try:
            if self.archivo_config.exists():
                with open(self.archivo_config, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    return datos.get('codigo_licencia', '')
        except Exception as e:
            print(f"Error leyendo configuración local: {e}")
        return ''

    def guardar_codigo_licencia(self, codigo):
        """Guarda el código de licencia localmente"""
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
        """Obtiene la información de cache local, con fallback a respaldo AppData"""
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
        """Lee y valida cache desde un archivo"""
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
                dias = (datetime.now() - fecha_cache).days
                if dias <= self.dias_revalidacion:
                    return cache
        except Exception as e:
            print(f"Error leyendo cache: {e}")
        return None

    def _guardar_cache_local(self, datos_licencia):
        """Guarda los datos de la licencia en cache local y respaldo"""
        datos_cache = {
            'tipo': datos_licencia.get('tipo'),
            'valida': datos_licencia.get('valida'),
            'expirada': datos_licencia.get('expirada'),
            'dias_restantes': datos_licencia.get('diasRestantes'),
            'fecha_verificacion': datetime.now().isoformat(),
            'es_developer_permanente': datos_licencia.get('developer_permanente', False)
        }

        try:
            self.carpeta_config.mkdir(parents=True, exist_ok=True)
            config = {}
            if self.archivo_config.exists():
                contenido = self.archivo_config.read_text(encoding='utf-8').strip()
                if contenido:
                    config = json.loads(contenido)
            config['datos_licencia'] = datos_cache
            with open(self.archivo_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando cache principal: {e}")

        # Respaldo en AppData solo para FULL/MASTER
        tipo = datos_licencia.get('tipo', 'TRIAL')
        es_full = tipo in ['FULL', 'MASTER'] or datos_licencia.get('developer_permanente', False)
        if es_full:
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

    def verificar_licencia(self, codigo_licencia, mostrar_mensajes=True, forzar_backend=False):
        """Verifica la licencia contra el backend"""
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
            url = f"{self.url_backend}/{codigo_licencia}"
            response = requests.get(url, timeout=30, verify=False)

            if response.status_code == 200:
                datos = response.json()
                self._guardar_cache_local(datos)
                if mostrar_mensajes:
                    print(f"✅ Licencia verificada: {datos.get('tipo')} - Válida: {datos.get('valida')}")
                return {
                    'tipo': datos.get('tipo', 'TRIAL'),
                    'valida': datos.get('valida', False),
                    'expirada': datos.get('expirado', False),
                    'diasRestantes': datos.get('diasRestantes', 0),
                    'mensaje': 'Verificado contra backend',
                    'desde_cache': False,
                    'developer_permanente': False
                }
            else:
                raise Exception(f"Backend respondió {response.status_code}")

        except Exception as e:
            if mostrar_mensajes:
                print(f"⚠️ Backend no disponible: {e}")
            if cache:
                if mostrar_mensajes:
                    print("📦 Usando cache local como fallback")
                return {
                    'tipo': cache.get('tipo', 'TRIAL'),
                    'valida': cache.get('valida', False),
                    'expirada': cache.get('expirada', False),
                    'diasRestantes': cache.get('dias_restantes', 0),
                    'mensaje': 'Servidor no disponible - usando cache',
                    'desde_cache': True,
                    'developer_permanente': cache.get('es_developer_permanente', False)
                }
            return {
                'tipo': 'TRIAL',
                'valida': False,
                'expirada': True,
                'diasRestantes': 0,
                'mensaje': 'Sin conexión y sin cache local',
                'desde_cache': False,
                'developer_permanente': False
            }

    def registrar_instalacion(self, email):
        """Registra la instalación y obtiene código TRIAL"""
        try:
            url = self.url_backend.replace('/verificar-licencia', '/registrar-instalacion')
            payload = {
                'email': email,
                'nombreApp': self.nombre_app
            }
            response = requests.post(url, json=payload, timeout=30, verify=False)
            if response.status_code == 200:
                datos = response.json()
                codigo = datos.get('codigo')
                if codigo:
                    self.guardar_codigo_licencia(codigo)
                    return codigo
        except Exception as e:
            print(f"Error registrando instalación: {e}")
        return None