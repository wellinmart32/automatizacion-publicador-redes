import os
import sys
import time
import random
import pyperclip

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import TimeoutException

# ── Colores ANSI ──────────────────────────────────────────────
V  = '\033[92m'   # verde
R  = '\033[91m'   # rojo
A  = '\033[93m'   # amarillo
C  = '\033[96m'   # cian
N  = '\033[1m'    # negrita
X  = '\033[0m'    # reset
# ─────────────────────────────────────────────────────────────


class PublicadorInstagram:
    """Publicador automático para Instagram — solo versión FULL"""

    LIMITE_SEGUIR_PAGADO = 10

    def __init__(self, config, es_full=False):
        self.config  = config
        self.es_full = es_full
        self.driver  = None

    # ==================== NAVEGADOR ====================

    def _iniciar_navegador(self):
        """Inicia Firefox con el perfil dedicado de Instagram"""
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        options = FirefoxOptions()

        if self.config.get('usar_perfil_existente') == 'si':
            perfil_path = os.path.join(base_dir, 'perfiles', 'instagram_publicador')
            os.makedirs(perfil_path, exist_ok=True)
            options.add_argument('-profile')
            options.add_argument(perfil_path)
            print(f"   ✓ Perfil Firefox: {os.path.basename(perfil_path)}")

        if self.config.get('desactivar_notificaciones'):
            options.set_preference("dom.webnotifications.enabled", False)
            options.set_preference("dom.push.enabled", False)

        self.driver = webdriver.Firefox(options=options)

        if self.config.get('maximizar_ventana'):
            self.driver.maximize_window()

        print(f"   {V}✅ Navegador iniciado{X}")
        return self.driver

    def cerrar_navegador(self):
        """Cierra el navegador"""
        if self.driver:
            print(f"\n{N}🔒 Cerrando navegador...{X}")
            try:
                self.driver.quit()
                print(f"   {V}✅ Navegador cerrado{X}")
            except Exception:
                pass
            self.driver = None

    # ==================== SEGURIDAD / SESIÓN ====================

    def _notificar_login(self, titulo, mensaje):
        """Muestra toast avisando que se necesita login"""
        import threading
        def _mostrar():
            try:
                import tkinter as tk
                from compartido.toast import Toast
                root = tk.Tk()
                root.withdraw()
                Toast.advertencia(root, f"{titulo}\n{mensaje}", duracion=8000)
                root.after(8500, root.destroy)
                root.mainloop()
            except Exception:
                pass
        threading.Thread(target=_mostrar, daemon=True).start()

    def verificar_sesion_instagram(self):
        """Verifica sesión en Instagram — espera login si es necesario"""
        print(f"{N}🔐 Verificando sesión de Instagram...{X}")
        try:
            self.driver.get("https://www.instagram.com")
            time.sleep(4)

            # Detectar formulario de login
            login_elements = self.driver.find_elements(
                By.XPATH, "//input[@name='username' or @name='password']"
            )

            if login_elements:
                self._notificar_login(
                    "Iniciar sesión en Instagram",
                    "Ingresa tus credenciales en el navegador.\nTienes 2 minutos."
                )
                print(f"\n{A}{N}⚠️  NO HAS INICIADO SESIÓN EN INSTAGRAM{X}")
                print(f"{A}" + "=" * 60 + X)
                print(f"{A}Por favor INICIA SESIÓN en Instagram ahora.{X}")
                print(f"{A}Tienes 2 MINUTOS para iniciar sesión.{X}")
                print(f"{A}" + "=" * 60 + X + "\n")

                timeout = 120
                transcurrido = 0
                while transcurrido < timeout:
                    time.sleep(5)
                    transcurrido += 5
                    try:
                        login_check = self.driver.find_elements(
                            By.XPATH, "//input[@name='username']"
                        )
                        if not login_check:
                            print(f"   {V}✅ Sesión iniciada correctamente{X}")
                            time.sleep(3)
                            return True
                        print(f"   ⏳ Esperando login... ({timeout - transcurrido}s restantes)")
                    except Exception:
                        print(f"   {V}✅ Sesión iniciada correctamente{X}")
                        time.sleep(3)
                        return True

                print(f"\n{R}❌ Tiempo de espera agotado.{X}")
                return False
            else:
                print(f"   {V}✅ Ya tienes sesión activa en Instagram{X}")
                return True

        except Exception as e:
            print(f"   {A}⚠️  Error verificando sesión: {e}{X}")
            return True

    def _manejar_puzzle(self):
        """Detecta y pausa para resolución manual de puzzle/captcha"""
        try:
            puzzles = [
                "//iframe[contains(@src, 'captcha')]",
                "//*[contains(@class, 'captcha')]",
            ]
            for selector in puzzles:
                elementos = self.driver.find_elements(By.XPATH, selector)
                if elementos:
                    print(f"\n{A}⚠️  Puzzle/captcha detectado. Por favor resuélvelo manualmente.{X}")
                    input("   Presiona Enter cuando hayas resuelto el puzzle...")
                    return True
        except Exception:
            pass
        return False

    def _cerrar_dialogo_notificaciones(self):
        """Cierra el diálogo de notificaciones si aparece"""
        try:
            botones = [
                "//button[contains(text(), 'Ahora no')]",
                "//button[contains(text(), 'Not Now')]",
                "//button[contains(text(), 'No, gracias')]",
            ]
            for selector in botones:
                try:
                    btn = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    btn.click()
                    time.sleep(1)
                    return True
                except Exception:
                    continue
        except Exception:
            pass
        return False

    # ==================== PUBLICAR ====================

    def _abrir_nuevo_post(self):
        """Abre el compositor de nueva publicación"""
        print(f"📝 Abriendo compositor de publicación...")

        # Cerrar diálogos de notificaciones
        self._cerrar_dialogo_notificaciones()
        time.sleep(1)

        # Estrategia 1: Botón crear (+)
        selectores_crear = [
            "//a[@href='/create/select/']",
            "//*[@aria-label='Nueva publicación']",
            "//*[@aria-label='New post']",
            "//*[@aria-label='Crear']",
            "//*[@aria-label='Create']",
            "//span[text()='Crear']/..",
            "//span[text()='Create']/..",
        ]

        for selector in selectores_crear:
            try:
                btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                btn.click()
                time.sleep(2)
                print(f"   {V}✅ Compositor abierto{X}")
                return True
            except Exception:
                continue

        # Estrategia 2: Buscar icono + en la barra de navegación
        try:
            iconos = self.driver.find_elements(By.XPATH, "//svg[@aria-label='Nueva publicación' or @aria-label='New post']")
            if iconos:
                iconos[0].click()
                time.sleep(2)
                print(f"   {V}✅ Compositor abierto (estrategia 2){X}")
                return True
        except Exception:
            pass

        print(f"   {R}❌ No se pudo abrir el compositor{X}")
        return False

    def _subir_archivo(self, ruta_archivo):
        """Sube un archivo (imagen o video) al compositor"""
        print(f"   📁 Subiendo archivo: {os.path.basename(ruta_archivo)}...")
        try:
            # Buscar input de archivo
            inputs = self.driver.find_elements(By.XPATH, "//input[@type='file']")

            if not inputs:
                # Hacer visible el input oculto
                self.driver.execute_script("""
                    var inputs = document.querySelectorAll('input[type="file"]');
                    inputs.forEach(function(input) {
                        input.style.display = 'block';
                        input.style.opacity = '1';
                    });
                """)
                time.sleep(1)
                inputs = self.driver.find_elements(By.XPATH, "//input[@type='file']")

            if inputs:
                inputs[0].send_keys(ruta_archivo)
                time.sleep(3)
                print(f"   {V}✅ Archivo cargado{X}")
                return True
            else:
                print(f"   {R}❌ No se encontró input de archivo{X}")
                return False

        except Exception as e:
            print(f"   {R}❌ Error subiendo archivo: {e}{X}")
            return False

    def _avanzar_pasos(self):
        """Hace clic en Siguiente para avanzar en los pasos del compositor"""
        selectores_siguiente = [
            "//button[contains(text(), 'Siguiente')]",
            "//button[contains(text(), 'Next')]",
            "//div[contains(text(), 'Siguiente')]",
            "//div[contains(text(), 'Next')]",
        ]

        for selector in selectores_siguiente:
            try:
                btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                btn.click()
                time.sleep(2)
                return True
            except Exception:
                continue
        return False

    def _ingresar_caption(self, texto):
        """Ingresa el caption/descripción del post"""
        print(f"✍️  Ingresando caption...")
        try:
            campo = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@aria-label='Escribe un pie de foto...' or @aria-label='Write a caption...' or @role='textbox']")
                )
            )
            campo.click()
            time.sleep(1)

            pyperclip.copy(texto)
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            time.sleep(2)

            print(f"   {V}✅ Caption ingresado{X}")
            return True

        except Exception as e:
            print(f"   {A}⚠️  Error ingresando caption: {e}{X}")
            return False

    def _compartir_post(self):
        """Hace clic en Compartir para publicar"""
        print(f"   🚀 Publicando...")
        selectores_compartir = [
            "//button[contains(text(), 'Compartir')]",
            "//button[contains(text(), 'Share')]",
            "//div[contains(text(), 'Compartir')]",
            "//div[contains(text(), 'Share')]",
        ]

        for selector in selectores_compartir:
            try:
                btn = WebDriverWait(self.driver, 8).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                btn.click()
                time.sleep(5)
                print(f"   {V}✅ Post compartido{X}")
                return True
            except Exception:
                continue

        print(f"   {R}❌ No se encontró botón Compartir{X}")
        return False

    def publicar(self, texto, imagenes=None, videos=None):
        """
        Publica en Instagram — requiere versión FULL e imágenes o videos

        Args:
            texto: Caption del post
            imagenes: Lista de rutas de imágenes (solo FULL)
            videos: Lista de rutas de videos (solo FULL)

        Returns:
            bool: True si se publicó correctamente
        """
        if not self.es_full:
            print(f"   {A}ℹ️  Instagram requiere versión FULL{X}")
            return False

        # Instagram requiere al menos una imagen o video
        if not imagenes and not videos:
            print(f"   {A}ℹ️  Instagram requiere al menos una imagen o video{X}")
            return False

        archivo = (imagenes[0] if imagenes else videos[0])
        intentos_max = self.config.get('max_intentos_por_publicacion', 3)

        for intento in range(1, intentos_max + 1):
            print(f"\n{N}" + "="*70 + X)
            print(f"{N}🔄 INTENTO {intento} DE {intentos_max} — Instagram{X}")
            print(f"{N}" + "="*70 + X)

            try:
                if not self.driver:
                    self._iniciar_navegador()

                if not self.verificar_sesion_instagram():
                    print(f"   {R}❌ No se pudo verificar la sesión{X}")
                    if intento < intentos_max:
                        time.sleep(self.config.get('tiempo_entre_intentos', 3))
                    continue

                self._cerrar_dialogo_notificaciones()

                if not self._abrir_nuevo_post():
                    print(f"   {R}❌ No se pudo abrir el compositor{X}")
                    if intento < intentos_max:
                        time.sleep(self.config.get('tiempo_entre_intentos', 3))
                    continue

                if not self._subir_archivo(archivo):
                    continue

                # Avanzar paso de recorte
                self._avanzar_pasos()
                time.sleep(1)

                # Avanzar paso de filtros
                self._avanzar_pasos()
                time.sleep(1)

                # Ingresar caption
                if texto:
                    self._ingresar_caption(texto)

                # Delay aleatorio antes de compartir
                time.sleep(random.uniform(1.5, 3.0))

                if not self._compartir_post():
                    continue

                time.sleep(self.config.get('espera_despues_publicar', 5))

                print(f"\n{V}{N}" + "="*70 + X)
                print(f"{V}{N}✅ PUBLICACIÓN EXITOSA EN INSTAGRAM{X}")
                print(f"{V}{N}" + "="*70 + X)
                return True

            except Exception as e:
                print(f"   {R}❌ Error en intento {intento}: {e}{X}")
                if intento < intentos_max:
                    time.sleep(self.config.get('tiempo_entre_intentos', 3))

        print(f"\n{R}{N}" + "="*70 + X)
        print(f"{R}{N}❌ NO SE PUDO PUBLICAR EN INSTAGRAM{X}")
        print(f"{R}{N}" + "="*70 + X)
        return False

    # ==================== SEGUIR USUARIOS ====================

    def seguir_usuarios(self, cantidad=None):
        """
        Sigue usuarios automáticamente en Instagram

        Args:
            cantidad: Número de usuarios a seguir (máx 10 en FULL)

        Returns:
            int: Número de usuarios seguidos
        """
        if not self.es_full:
            print(f"   {A}ℹ️  Seguir usuarios requiere versión FULL{X}")
            return 0

        limite = self.LIMITE_SEGUIR_PAGADO
        if cantidad:
            limite = min(cantidad, limite)

        seguidos = 0

        try:
            if not self.driver:
                self._iniciar_navegador()

            if not self.verificar_sesion_instagram():
                print(f"   {R}❌ No se pudo verificar la sesión{X}")
                return 0

            print(f"\n👥 Siguiendo hasta {limite} usuarios en Instagram...")
            self.driver.get("https://www.instagram.com/explore/people/")
            time.sleep(4)

            self._cerrar_dialogo_notificaciones()

            while seguidos < limite:
                try:
                    botones = self.driver.find_elements(
                        By.XPATH,
                        "//button[contains(text(), 'Seguir') or contains(text(), 'Follow')]"
                    )

                    if not botones:
                        print(f"   ℹ️  No se encontraron más sugerencias")
                        break

                    for btn in botones:
                        if seguidos >= limite:
                            break
                        try:
                            if btn.is_displayed() and btn.is_enabled():
                                texto_btn = btn.text.strip().lower()
                                if texto_btn in ['seguir', 'follow']:
                                    self.driver.execute_script(
                                        "arguments[0].scrollIntoView({block: 'center'});", btn
                                    )
                                    time.sleep(0.5)
                                    btn.click()
                                    seguidos += 1
                                    print(f"   {V}✅ Usuario seguido ({seguidos}/{limite}){X}")
                                    time.sleep(random.uniform(2, 5))
                        except Exception:
                            continue

                    self.driver.execute_script("window.scrollBy(0, 600);")
                    time.sleep(2)

                except Exception as e:
                    print(f"   {A}⚠️  Error siguiendo usuarios: {e}{X}")
                    break

        except Exception as e:
            print(f"   {R}❌ Error en seguir usuarios: {e}{X}")

        print(f"\n   📊 Usuarios seguidos: {seguidos}/{limite}")
        return seguidos