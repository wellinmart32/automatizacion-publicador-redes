import os
import sys
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ── Colores ANSI ──────────────────────────────────────────────
V  = '\033[92m'   # verde
R  = '\033[91m'   # rojo
A  = '\033[93m'   # amarillo
C  = '\033[96m'   # cian
N  = '\033[1m'    # negrita
X  = '\033[0m'    # reset
# ─────────────────────────────────────────────────────────────

from compartido.gestor_archivos import leer_config_global, verificar_y_crear_estructura, obtener_anuncio
from gestor_licencias import GestorLicencias
from gestor_registro import GestorRegistro


def mostrar_banner():
    """Muestra el banner de inicio"""
    print(f"\n{N}{C}" + "="*70 + X)
    print(f"{N}{C}" + " " * 18 + "🟣 PUBLICADOR REDES — AutomaPro" + X)
    print(f"{N}{C}" + "="*70 + X + "\n")


def mostrar_configuracion(config):
    """Muestra la configuración activa del sistema"""
    print("📁 Verificando estructura...")
    verificar_y_crear_estructura()
    print()
    print("⚙️  CONFIGURACIÓN DEL SISTEMA:")
    print(f"   📁 Carpeta anuncios: {config['carpeta_anuncios']}")
    print(f"   🌐 Navegador: {config['navegador'].upper()}")
    print(f"   🎲 Selección: {config['seleccion'].capitalize()}")
    print(f"   💾 Memoria: Últimos {config['historial_evitar_repetir']} anuncios")
    print(f"   🔄 Máx. intentos: {config['max_intentos_por_publicacion']}")
    print()
    print("📱 MÓDULOS ACTIVOS:")
    print(f"   📘 Facebook:   {'✅ Sí' if config.get('modulo_facebook') else '⛔ No'}")
    print(f"   📸 Instagram:  {'✅ Sí' if config.get('modulo_instagram') else '⛔ No'}")
    print(f"   🐦 Twitter/X:  {'✅ Sí' if config.get('modulo_twitter') else '⛔ No'}")
    print(f"   💼 LinkedIn:   {'✅ Sí' if config.get('modulo_linkedin') else '⛔ No'}")
    print()


def _verificar_wizard_completado():
    """Si no hay licencia configurada, lanza el wizard y termina"""
    import subprocess
    gestor = GestorLicencias("PublicadorRedes")
    try:
        config_path = gestor.archivo_config
        tiene_configuracion = False
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                if datos.get('codigo_licencia'):
                    tiene_configuracion = True

        if not tiene_configuracion:
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
                wizard = os.path.join(base_dir, "WizardPublicador.exe")
            else:
                wizard = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wizard_primera_vez.py")
            if os.path.exists(wizard):
                subprocess.Popen([wizard] if wizard.endswith('.exe') else [sys.executable, wizard])
            return False
        return True
    except Exception:
        return True


def main():
    """Función principal del publicador"""
    mostrar_banner()

    # Verificar estructura de carpetas y mostrar configuración
    try:
        config = leer_config_global()
    except Exception as e:
        print(f"{R}❌ Error leyendo configuración: {e}{X}")
        return

    mostrar_configuracion(config)

    # Verificar licencia
    gestor_lic = GestorLicencias("PublicadorRedes")
    codigo = gestor_lic.obtener_codigo_guardado()
    if not codigo:
        print(f"{R}❌ No hay código de licencia configurado{X}")
        return

    estado_licencia = gestor_lic.verificar_licencia(codigo, mostrar_mensajes=True)
    if not estado_licencia['valida']:
        print(f"{R}❌ Licencia inválida o expirada{X}")
        print("   Visita: automapro-frontend.vercel.app")
        return

    es_full = estado_licencia.get('tipo') in ['FULL', 'MASTER'] or estado_licencia.get('developer_permanente')

    if es_full:
        print(f"{V}✅ Licencia Completa activada — todas las funciones desbloqueadas{X}\n")
    else:
        dias = estado_licencia.get('diasRestantes', 0)
        print(f"{A}⚠️  Versión de Prueba — {dias} días restantes{X}")
        print("   Funciones limitadas: solo texto, solo Facebook\n")

    # Gestor de registro
    gestor_reg = GestorRegistro()
    gestor_reg.mostrar_estadisticas()

    # Obtener anuncio
    registro = gestor_reg._leer_registro()
    texto, anuncio_dir, imagenes, videos = obtener_anuncio(registro)

    if not texto and not imagenes and not videos:
        print(f"{R}❌ No hay anuncios disponibles{X}")
        print("   Agrega anuncios en la carpeta 'anuncios/'")
        return

    print(f"\n{N}📢 Anuncio seleccionado: {anuncio_dir}{X}")
    if texto:
        print(f"   Texto: {texto[:50]}..." if len(texto) > 50 else f"   Texto: {texto}")
    print(f"   Imágenes: {len(imagenes)}")
    print(f"   Videos: {len(videos)}")

    # Countdown automático
    print(f"\n⏳ Iniciando en 3 segundos... (Ctrl+C para cancelar)\n")
    try:
        for i in range(3, 0, -1):
            print(f"   {i}...", end='\r', flush=True)
            import time
            time.sleep(1)
        print("   ✅ ¡Iniciando!\n")
    except KeyboardInterrupt:
        print(f"\n\n{R}❌ Proceso cancelado por el usuario{X}\n")
        return

    # Publicar en plataformas activas
    resultados = {}

    if config.get('modulo_facebook'):
        print(f"\n{N}{C}📘 Publicando en Facebook...{X}")
        from publicadores.publicador_facebook import PublicadorFacebook
        pub = PublicadorFacebook(config, es_full=es_full)
        exito = pub.publicar(texto, imagenes if es_full else None, videos if es_full else None)
        resultados['facebook'] = exito
        if exito:
            gestor_reg.registrar_publicacion_exitosa('facebook', 'anuncio', anuncio_dir)
        else:
            gestor_reg.registrar_error('facebook', 'publicacion', 'Falló la publicación')
        pub.cerrar_navegador()

    if config.get('modulo_instagram') and es_full:
        print(f"\n{N}{C}📸 Publicando en Instagram...{X}")
        from publicadores.publicador_instagram import PublicadorInstagram
        pub = PublicadorInstagram(config, es_full=es_full)
        exito = pub.publicar(texto, imagenes, videos)
        resultados['instagram'] = exito
        if exito:
            gestor_reg.registrar_publicacion_exitosa('instagram', 'anuncio', anuncio_dir)
        else:
            gestor_reg.registrar_error('instagram', 'publicacion', 'Falló la publicación')
        pub.cerrar_navegador()

    if config.get('modulo_twitter') and es_full:
        print(f"\n{N}{C}🐦 Publicando en Twitter/X...{X}")
        from publicadores.publicador_twitter import PublicadorTwitter
        pub = PublicadorTwitter(config, es_full=es_full)
        exito = pub.publicar(texto, imagenes, videos)
        resultados['twitter'] = exito
        if exito:
            gestor_reg.registrar_publicacion_exitosa('twitter', 'anuncio', anuncio_dir)
        else:
            gestor_reg.registrar_error('twitter', 'publicacion', 'Falló la publicación')
        pub.cerrar_navegador()

    if config.get('modulo_linkedin') and es_full:
        print(f"\n{N}{C}💼 Publicando en LinkedIn...{X}")
        from publicadores.publicador_linkedin import PublicadorLinkedIn
        pub = PublicadorLinkedIn(config, es_full=es_full)
        exito = pub.publicar(texto, imagenes, videos)
        resultados['linkedin'] = exito
        if exito:
            gestor_reg.registrar_publicacion_exitosa('linkedin', 'anuncio', anuncio_dir)
        else:
            gestor_reg.registrar_error('linkedin', 'publicacion', 'Falló la publicación')
        pub.cerrar_navegador()

    # Resumen final
    print(f"\n{N}" + "="*70 + X)
    print(f"{N}📊 RESUMEN DE PUBLICACIONES{X}")
    print(f"{N}" + "="*70 + X)
    for plataforma, exito in resultados.items():
        estado = f"{V}✅ Exitoso{X}" if exito else f"{R}❌ Fallido{X}"
        print(f"   {plataforma.capitalize()}: {estado}")
    print(f"{N}" + "="*70 + X + "\n")


if __name__ == "__main__":
    if not _verificar_wizard_completado():
        sys.exit(0)
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{R}❌ Proceso cancelado por el usuario{X}\n")
        sys.exit(0)
    except Exception as e:
        import traceback
        print(f"\n{R}❌ Error inesperado: {e}{X}")
        traceback.print_exc()