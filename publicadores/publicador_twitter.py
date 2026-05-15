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

LIMITE_CARACTERES_TWEET = 280


class PublicadorTwitter:
    """Publicador automático para Twitter/X — solo versión FULL"""

    LIMITE_SEGUIR_PAGADO = 10

    def __init__(self, config, es_full=False):
        self.config  = config
        self.es_full = es_full
        self.driver  = None

    # ==================== NAVEGADOR ====================

    def _iniciar_navegador(self):
        """Inicia Firefox con el perfil dedicado de Twitter"""
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        options = FirefoxOptions()

        if self.config.get('usar_perfil_existente') == 'si':
            perfil_path = os.path.join(base_dir, 'perfiles', 'twitter_publicador')
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

    def verificar_sesion_twitter(self):
        """Verifica sesión en Twitter/X — espera login si es necesario"""
        print(f"{N}🔐 Verificando sesión de Twitter/X...{X}")
        try:
            self.driver.get("https://www.x.com")
            time.sleep(4)

            # Detectar formulario de login
            login_elements = self.driver.find_elements(
                By.XPATH,
                "//input[@name='text' or @autocomplete='username']"
            )

            if login_elements:
                self._notificar_login(
                    "Iniciar sesión en Twitter/X",
                    "Ingresa tus credenciales en el navegador.\nTienes 2 minutos."
                )
                print(f"\n{A}{N}⚠️  NO HAS INICIADO SESIÓN EN TWITTER/X{X}")
                print(f"{A}" + "=" * 60 + X)
                print(f"{A}Por favor INICIA SESIÓN en Twitter/X ahora.{X}")
                print(f"{A}Tienes 2 MINUTOS para iniciar sesión.{X}")
                print(f"{A}" + "=" * 60 + X + "\n")

                timeout = 120
                transcurrido = 0
                while transcurrido < timeout:
                    time.sleep(5)
                    transcurrido += 5
                    try:
                        login_check = self.driver.find_elements(
                            By.XPATH, "//input[@autocomplete='username']"
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
                print(f"   {V}✅ Ya tienes sesión activa en Twitter/X{X}")
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

    # ==================== COMPOSITOR ====================

    def _abrir_compositor(self):
        """Abre el compositor de nuevo tweet"""
        print(f"📝 Abriendo compositor de tweet...")

        selectores_nuevo = [
            "//a[@data-testid='SideNav_NewTweet_Button']",
            "//a[@aria-label='Publicar']",
            "//a[@aria-label='Post']",
            "//span[text()='Publicar']/..",
            "//span[text()='Post']/..",
        ]

        for selector in selectores_nuevo:
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

        # Estrategia 2: clic en área de texto principal
        try:
            area = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@data-testid='tweetTextarea_0']")
                )
            )
            area.click()
            time.sleep(1)
            print(f"   {V}✅ Compositor abierto (estrategia 2){X}")
            return True
        except Exception:
            pass

        print(f"   {R}❌ No se pudo abrir el compositor{X}")
        return False

    def _ingresar_texto(self, texto):
        """Ingresa el texto del tweet"""
        print(f"✍️  Ingresando texto...")

        # Limitar a 280 caracteres
        if len(texto) > LIMITE_CARACTERES_TWEET:
            texto = texto[:LIMITE_CARACTERES_TWEET - 3] + "..."
            print(f"   {A}⚠️  Texto recortado a {LIMITE_CARACTERES_TWEET} caracteres{X}")

        try:
            campo = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@data-testid='tweetTextarea_0']")
                )
            )
            campo.click()
            time.sleep(1)

            pyperclip.copy(texto)
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            time.sleep(2)

            print(f"   {V}✅ Texto ingresado ({len(texto)} caracteres){X}")
            return True

        except Exception as e:
            print(f"   {R}❌ Error ingresando texto: {e}{X}")
            return False

    def _subir_imagenes(self, imagenes):
        """Sube imágenes al tweet (máx 4)"""
        imagenes = imagenes[:4]
        print(f"   🖼️  Subiendo {len(imagenes)} imagen(es)...")
        try:
            btn_media = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//input[@data-testid='fileInput' or @type='file']")
                )
            )
            for img in imagenes:
                btn_media.send_keys(img)
                time.sleep(2)
            print(f"   {V}✅ Imagen(es) cargada(s){X}")
            return True
        except Exception as e:
            print(f"   {A}⚠️  Error subiendo imágenes: {e}{X}")
            return False

    def _hacer_clic_publicar(self):
        """Hace clic en el botón Publicar/Post"""
        print(f"   🚀 Buscando botón publicar...")

        selectores_publicar = [
            "//button[@data-testid='tweetButtonInline']",
            "//button[@data-testid='tweetButton']",
            "//span[text()='Publicar']/..",
            "//span[text()='Post']/..",
        ]

        for selector in selectores_publicar:
            try:
                btn = WebDriverWait(self.driver, 8).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                self.driver.execute_script("arguments[0].click();", btn)
                print(f"   {V}✅ Tweet publicado{X}")
                return True
            except Exception:
                continue

        print(f"   {R}❌ No se encontró botón Publicar{X}")
        return False

    # ==================== PUBLICAR ====================

    def publicar(self, texto, imagenes=None, videos=None):
        """
        Publica un tweet en Twitter/X

        Args:
            texto: Texto del tweet (máx 280 caracteres)
            imagenes: Lista de rutas de imágenes (solo FULL)
            videos: Lista de rutas de videos (solo FULL)

        Returns:
            bool: True si se publicó correctamente
        """
        if not self.es_full:
            print(f"   {A}ℹ️  Twitter/X requiere versión FULL{X}")
            return False

        intentos_max = self.config.get('max_intentos_por_publicacion', 3)

        for intento in range(1, intentos_max + 1):
            print(f"\n{N}" + "="*70 + X)
            print(f"{N}🔄 INTENTO {intento} DE {intentos_max} — Twitter/X{X}")
            print(f"{N}" + "="*70 + X)

            try:
                if not self.driver:
                    self._iniciar_navegador()

                if not self.verificar_sesion_twitter():
                    print(f"   {R}❌ No se pudo verificar la sesión{X}")
                    if intento < intentos_max:
                        time.sleep(self.config.get('tiempo_entre_intentos', 3))
                    continue

                self._manejar_puzzle()

                if not self._abrir_compositor():
                    if intento < intentos_max:
                        time.sleep(self.config.get('tiempo_entre_intentos', 3))
                    continue

                if not self._ingresar_texto(texto):
                    continue

                if self.es_full and imagenes:
                    self._subir_imagenes(imagenes)
                    time.sleep(2)

                time.sleep(random.uniform(1.5, 3.0))

                if not self._hacer_clic_publicar():
                    continue

                time.sleep(self.config.get('espera_despues_publicar', 5))

                print(f"\n{V}{N}" + "="*70 + X)
                print(f"{V}{N}✅ PUBLICACIÓN EXITOSA EN TWITTER/X{X}")
                print(f"{V}{N}" + "="*70 + X)
                return True

            except Exception as e:
                print(f"   {R}❌ Error en intento {intento}: {e}{X}")
                if intento < intentos_max:
                    time.sleep(self.config.get('tiempo_entre_intentos', 3))

        print(f"\n{R}{N}" + "="*70 + X)
        print(f"{R}{N}❌ NO SE PUDO PUBLICAR EN TWITTER/X{X}")
        print(f"{R}{N}" + "="*70 + X)
        return False

    # ==================== SEGUIR USUARIOS ====================

    def seguir_usuarios(self, cantidad=None):
        """
        Sigue usuarios automáticamente en Twitter/X

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

            if not self.verificar_sesion_twitter():
                print(f"   {R}❌ No se pudo verificar la sesión{X}")
                return 0

            print(f"\n👥 Siguiendo hasta {limite} usuarios en Twitter/X...")
            self.driver.get("https://www.x.com/who_to_follow")
            time.sleep(4)

            while seguidos < limite:
                try:
                    botones = self.driver.find_elements(
                        By.XPATH,
                        "//button[@data-testid='1198986181-follow']"
                    )

                    if not botones:
                        print(f"   ℹ️  No se encontraron más sugerencias")
                        break

                    for btn in botones:
                        if seguidos >= limite:
                            break
                        try:
                            if btn.is_displayed() and btn.is_enabled():
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