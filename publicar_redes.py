import os
import sys
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from compartido.gestor_archivos import leer_config_global, verificar_y_crear_estructura, obtener_anuncio
from gestor_licencias import GestorLicencias
from gestor_registro import GestorRegistro


def _ocultar_consola():
    """Oculta la consola en Windows si se ejecuta con doble clic"""
    pass


def _abrir_consola():
    """Muestra la consola para ver el progreso"""
    pass


def mostrar_banner():
    """Muestra el banner de inicio"""
    print("\n" + "="*60)
    print("  🟣 PUBLICADOR REDES — AutomaPro")
    print("="*60 + "\n")


def _verificar_wizard_completado():
    """Si no hay licencia configurada, lanza el wizard y termina"""
    import subprocess
    gestor = GestorLicencias("PublicadorRedes")
    try:
        config_path = gestor.archivo_config
        tiene_configuracion = False
        if config_path.exists():
            import json
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

    # Verificar estructura de carpetas
    verificar_y_crear_estructura()

    # Leer configuración
    try:
        config = leer_config_global()
    except Exception as e:
        print(f"❌ Error leyendo configuración: {e}")
        return

    # Verificar licencia
    gestor_lic = GestorLicencias("PublicadorRedes")
    codigo = gestor_lic.obtener_codigo_guardado()
    if not codigo:
        print("❌ No hay código de licencia configurado")
        return

    estado_licencia = gestor_lic.verificar_licencia(codigo, mostrar_mensajes=True)
    if not estado_licencia['valida']:
        print("❌ Licencia inválida o expirada")
        print("   Visita: automapro-frontend.vercel.app")
        return

    es_full = estado_licencia.get('tipo') in ['FULL', 'MASTER'] or estado_licencia.get('developer_permanente')

    if es_full:
        print("✅ Licencia Completa activada — todas las funciones desbloqueadas")
    else:
        dias = estado_licencia.get('diasRestantes', 0)
        print(f"⚠️  Versión de Prueba — {dias} días restantes")
        print("   Funciones limitadas: solo texto, solo Facebook, 1 publicación/día, 5 solicitudes/día")

    # Gestor de registro
    gestor_reg = GestorRegistro()

    # Obtener anuncio
    registro = {'historial': []}
    texto, anuncio_dir, imagenes, videos = obtener_anuncio(registro)

    if not texto and not imagenes and not videos:
        print("❌ No hay anuncios disponibles")
        print("   Agrega anuncios en la carpeta 'anuncios/'")
        return

    print(f"\n📢 Anuncio seleccionado: {anuncio_dir}")
    if texto:
        print(f"   Texto: {texto[:50]}..." if len(texto) > 50 else f"   Texto: {texto}")
    print(f"   Imágenes: {len(imagenes)}")
    print(f"   Videos: {len(videos)}")

    # Publicar en plataformas activas
    resultados = {}

    if config.get('modulo_facebook'):
        print("\n📘 Publicando en Facebook...")
        from publicadores.publicador_facebook import PublicadorFacebook
        pub = PublicadorFacebook(config, es_full=es_full)
        exito = pub.publicar(texto, imagenes if es_full else None, videos if es_full else None)
        resultados['facebook'] = exito
        if exito:
            gestor_reg.registrar_publicacion_exitosa('facebook', 'anuncio', anuncio_dir)
        else:
            gestor_reg.registrar_error('facebook', 'publicacion', 'Falló la publicación')
        pub._cerrar_navegador()

    if config.get('modulo_instagram') and es_full:
        print("\n📷 Publicando en Instagram...")
        from publicadores.publicador_instagram import PublicadorInstagram
        pub = PublicadorInstagram(config, es_full=es_full)
        exito = pub.publicar(texto, imagenes, videos)
        resultados['instagram'] = exito
        if exito:
            gestor_reg.registrar_publicacion_exitosa('instagram', 'anuncio', anuncio_dir)
        else:
            gestor_reg.registrar_error('instagram', 'publicacion', 'Falló la publicación')
        pub._cerrar_navegador()

    if config.get('modulo_twitter') and es_full:
        print("\n🐦 Publicando en Twitter/X...")
        from publicadores.publicador_twitter import PublicadorTwitter
        pub = PublicadorTwitter(config, es_full=es_full)
        exito = pub.publicar(texto, imagenes, videos)
        resultados['twitter'] = exito
        if exito:
            gestor_reg.registrar_publicacion_exitosa('twitter', 'anuncio', anuncio_dir)
        else:
            gestor_reg.registrar_error('twitter', 'publicacion', 'Falló la publicación')
        pub._cerrar_navegador()

    if config.get('modulo_linkedin') and es_full:
        print("\n💼 Publicando en LinkedIn...")
        from publicadores.publicador_linkedin import PublicadorLinkedIn
        pub = PublicadorLinkedIn(config, es_full=es_full)
        exito = pub.publicar(texto, imagenes, videos)
        resultados['linkedin'] = exito
        if exito:
            gestor_reg.registrar_publicacion_exitosa('linkedin', 'anuncio', anuncio_dir)
        else:
            gestor_reg.registrar_error('linkedin', 'publicacion', 'Falló la publicación')
        pub._cerrar_navegador()

    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN:")
    for plataforma, exito in resultados.items():
        estado = "✅ Exitoso" if exito else "❌ Fallido"
        print(f"   {plataforma.capitalize()}: {estado}")
    print("="*60 + "\n")


if __name__ == "__main__":
    if not _verificar_wizard_completado():
        sys.exit(0)
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Proceso cancelado por el usuario\n")
        sys.exit(0)
    except Exception as e:
        import traceback
        print(f"\n❌ Error inesperado: {e}")
        traceback.print_exc()