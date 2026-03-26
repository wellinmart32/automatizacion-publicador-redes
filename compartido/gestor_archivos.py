import os
import sys
import json
import configparser
import random
from datetime import datetime


def _base_dir():
    """Retorna el directorio base del proyecto"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def leer_config_global():
    """Lee config_global.txt y retorna un diccionario con la configuración"""
    base = _base_dir()
    archivo_config = os.path.join(base, "config_global.txt")

    if not os.path.exists(archivo_config):
        print("⚠️  No existe config_global.txt. Creando configuración por defecto...")
        crear_config_defecto()

    config = configparser.RawConfigParser(delimiters=('=',))
    config.read(archivo_config, encoding='utf-8')

    config_dict = {
        # [GENERAL]
        'nombre_proyecto': config['GENERAL']['nombre_proyecto'],
        'carpeta_anuncios': config['GENERAL']['carpeta_anuncios'],
        'navegador': config['GENERAL']['navegador'].lower(),
        'modo_debug': config['GENERAL']['modo_debug'].lower() == 'si',

        # [ANUNCIOS]
        'seleccion': config['ANUNCIOS']['seleccion'].lower(),
        'historial_evitar_repetir': int(config['ANUNCIOS']['historial_evitar_repetir']),
        'agregar_hashtags': config['ANUNCIOS']['agregar_hashtags'].lower() == 'si',
        'hashtags': config['ANUNCIOS']['hashtags'],
        'agregar_firma': config['ANUNCIOS']['agregar_firma'].lower() == 'si',
        'texto_firma': config['ANUNCIOS']['texto_firma'],

        # [PUBLICACION]
        'tiempo_entre_intentos': int(config['PUBLICACION']['tiempo_entre_intentos']),
        'max_intentos_por_publicacion': int(config['PUBLICACION']['max_intentos_por_publicacion']),
        'espera_despues_publicar': int(config['PUBLICACION']['espera_despues_publicar']),
        'verificar_publicacion_exitosa': config['PUBLICACION']['verificar_publicacion_exitosa'].lower() == 'si',
        'espera_estabilizacion_modal': int(config['PUBLICACION']['espera_estabilizacion_modal']),

        # [NAVEGADOR]
        'usar_perfil_existente': config['NAVEGADOR']['usar_perfil_existente'].lower(),
        'carpeta_perfil_custom': config['NAVEGADOR']['carpeta_perfil_custom'],
        'desactivar_notificaciones': config['NAVEGADOR']['desactivar_notificaciones'].lower() == 'si',
        'maximizar_ventana': config['NAVEGADOR']['maximizar_ventana'].lower() == 'si',

        # [LIMITES]
        'tiempo_minimo_entre_publicaciones_segundos': int(config['LIMITES']['tiempo_minimo_entre_publicaciones_segundos']),
        'permitir_duplicados': config['LIMITES']['permitir_duplicados'].lower() == 'si',
        'permitir_forzar_publicacion_manual': config['LIMITES']['permitir_forzar_publicacion_manual'].lower() == 'si',

        # [MODULOS]
        'modulo_facebook': config['MODULOS']['publicar_facebook'].lower() == 'si' if config.has_option('MODULOS', 'publicar_facebook') else True,
        'modulo_instagram': config['MODULOS']['publicar_instagram'].lower() == 'si' if config.has_option('MODULOS', 'publicar_instagram') else False,
        'modulo_twitter': config['MODULOS']['publicar_twitter'].lower() == 'si' if config.has_option('MODULOS', 'publicar_twitter') else False,
        'modulo_linkedin': config['MODULOS']['publicar_linkedin'].lower() == 'si' if config.has_option('MODULOS', 'publicar_linkedin') else False,
    }

    return config_dict


def crear_config_defecto():
    """Crea config_global.txt con valores por defecto"""
    base = _base_dir()
    archivo_config = os.path.join(base, "config_global.txt")

    config = configparser.ConfigParser()

    config['GENERAL'] = {
        'nombre_proyecto': 'Publicador Redes',
        'carpeta_anuncios': 'anuncios',
        'navegador': 'firefox',
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
        'usar_perfil_existente': 'si',
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

    config['DEBUG'] = {
        'modo_debug': 'detallado'
    }

    with open(archivo_config, 'w', encoding='utf-8') as f:
        f.write("# ============================================================\n")
        f.write("# CONFIGURACIÓN GLOBAL - PUBLICADOR REDES\n")
        f.write("# ============================================================\n\n")
        config.write(f)

    print("✅ config_global.txt creado con valores por defecto")


def verificar_y_crear_estructura():
    """Verifica y crea la estructura de carpetas necesaria"""
    config = leer_config_global()
    base = _base_dir()

    carpetas_necesarias = [
        os.path.join(base, config['carpeta_anuncios']),
        os.path.join(base, 'perfiles'),
    ]

    for carpeta in carpetas_necesarias:
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
            print(f"✅ Carpeta creada: {carpeta}")

    return True


def obtener_anuncio(registro_publicaciones):
    """
    Obtiene el siguiente anuncio según la configuración de selección

    Returns:
        tuple: (texto_anuncio, nombre_archivo, imagenes, videos) o (None, None, [], [])
    """
    config = leer_config_global()
    base = _base_dir()
    carpeta = os.path.join(base, config['carpeta_anuncios'])

    if not os.path.exists(carpeta):
        print(f"❌ No existe la carpeta de anuncios: {carpeta}")
        return None, None, [], []

    # Obtener todos los anuncios (carpetas)
    anuncios = [d for d in os.listdir(carpeta)
                if os.path.isdir(os.path.join(carpeta, d))]

    if not anuncios:
        print("❌ No hay anuncios en la carpeta")
        return None, None, [], []

    # Seleccionar anuncio según configuración
    if config['seleccion'] == 'aleatorio':
        anuncio_dir = random.choice(anuncios)
    else:
        # Secuencial — basado en historial
        historial = registro_publicaciones.get('historial', [])
        ultimos = [h.get('anuncio') for h in historial[-config['historial_evitar_repetir']:]]
        disponibles = [a for a in anuncios if a not in ultimos]
        if not disponibles:
            disponibles = anuncios
        anuncio_dir = disponibles[0]

    ruta_anuncio = os.path.join(carpeta, anuncio_dir)

    # Leer texto del anuncio
    texto = None
    archivo_texto = os.path.join(ruta_anuncio, 'texto.txt')
    if os.path.exists(archivo_texto):
        with open(archivo_texto, 'r', encoding='utf-8') as f:
            texto = f.read().strip()

    # Aplicar hashtags y firma
    if texto:
        if config['agregar_hashtags'] and config['hashtags']:
            texto += f"\n\n{config['hashtags']}"
        if config['agregar_firma'] and config['texto_firma']:
            texto += f"\n\n{config['texto_firma']}"

    # Obtener imágenes
    imagenes = []
    for ext in ['.jpg', '.jpeg', '.png', '.webp']:
        imagenes += [os.path.join(ruta_anuncio, f)
                     for f in os.listdir(ruta_anuncio)
                     if f.lower().endswith(ext)]

    # Obtener videos
    videos = []
    for ext in ['.mp4', '.avi', '.mov']:
        videos += [os.path.join(ruta_anuncio, f)
                   for f in os.listdir(ruta_anuncio)
                   if f.lower().endswith(ext)]

    return texto, anuncio_dir, imagenes, videos