import time
import random
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options


class PublicadorTwitter:
    """Publicador automático para Twitter/X — solo versión FULL"""

    LIMITE_SEGUIR_PAGADO = 10

    def __init__(self, config, es_full=False):
        self.config = config
        self.es_full = es_full
        self.driver = None

    def _iniciar_navegador(self):
        """Inicia Firefox con el perfil configurado"""
        import os
        import sys

        options = Options()

        if self.config.get('usar_perfil_existente') == 'si':
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            perfil_path = os.path.join(base_dir, 'perfiles', 'twitter_publicador')
            os.makedirs(perfil_path, exist_ok=True)
            options.add_argument("-profile")
            options.add_argument(perfil_path)

        if self.config.get('desactivar_notificaciones'):
            options.set_preference("dom.webnotifications.enabled", False)

        self.driver = webdriver.Firefox(options=options)

        if self.config.get('maximizar_ventana'):
            self.driver.maximize_window()

        return self.driver

    def _cerrar_navegador(self):
        """Cierra el navegador"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

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
                    print("⚠️  Puzzle/captcha detectado. Por favor resuélvelo manualmente.")
                    input("   Presiona Enter cuando hayas resuelto el puzzle...")
                    return True
        except Exception:
            pass
        return False

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
            print("ℹ️  Twitter requiere versión FULL para publicar")
            return False

        # Limitar texto a 280 caracteres
        if len(texto) > 280:
            texto = texto[:277] + "..."

        try:
            if not self.driver:
                self._iniciar_navegador()

            print("🐦 Abriendo Twitter/X...")
            self.driver.get("https://www.x.com")
            time.sleep(3)

            self._manejar_puzzle()

            # Buscar botón de nuevo tweet
            print("   Buscando área de publicación...")
            selectores_nuevo = [
                "//a[@data-testid='SideNav_NewTweet_Button']",
                "//a[@aria-label='Publicar']",
                "//a[@aria-label='Post']",
                "//span[text()='Publicar']/..",
                "//span[text()='Post']/.."
            ]

            btn_nuevo = None
            for selector in selectores_nuevo:
                try:
                    btn_nuevo = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except Exception:
                    continue

            if not btn_nuevo:
                print("   ❌ No se encontró el botón de nueva publicación")
                return False

            btn_nuevo.click()
            time.sleep(2)

            self._manejar_puzzle()

            # Ingresar texto
            print("   Ingresando texto...")
            try:
                campo_texto = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@data-testid='tweetTextarea_0']"))
                )
                campo_texto.click()
                time.sleep(1)
                pyperclip.copy(texto)
                ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                time.sleep(2)
            except Exception as e:
                print(f"   ❌ Error ingresando texto: {e}")
                return False

            # Agregar imágenes si es FULL
            if self.es_full and imagenes:
                print(f"   Agregando {len(imagenes)} imagen(es)...")
                # TODO: implementar subida de imágenes
                pass

            # Buscar botón publicar
            print("   Buscando botón publicar...")
            selectores_publicar = [
                "//button[@data-testid='tweetButtonInline']",
                "//button[@data-testid='tweetButton']",
                "//span[text()='Publicar']/..",
                "//span[text()='Post']/.."
            ]

            btn_publicar = None
            for selector in selectores_publicar:
                try:
                    btn_publicar = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except Exception:
                    continue

            if not btn_publicar:
                print("   ❌ No se encontró el botón publicar")
                return False

            btn_publicar.click()
            print("   ✅ Tweet publicado")
            time.sleep(self.config.get('espera_despues_publicar', 5))

            return True

        except Exception as e:
            print(f"❌ Error publicando en Twitter: {e}")
            return False

    def seguir_usuarios(self, cantidad=None):
        """
        Sigue usuarios automáticamente

        Args:
            cantidad: Número de usuarios a seguir (máx 10 en FULL)

        Returns:
            int: Número de usuarios seguidos
        """
        if not self.es_full:
            print("ℹ️  Seguir usuarios requiere versión FULL")
            return 0

        limite = self.LIMITE_SEGUIR_PAGADO
        if cantidad:
            limite = min(cantidad, limite)

        seguidos = 0

        try:
            if not self.driver:
                self._iniciar_navegador()

            print(f"👥 Siguiendo hasta {limite} usuarios en Twitter...")
            self.driver.get("https://www.x.com/who_to_follow")
            time.sleep(3)

            self._manejar_puzzle()

            selectores_seguir = [
                "//button[@data-testid='1481562-follow']",
                "//span[text()='Seguir']/..",
                "//span[text()='Follow']/.."
            ]

            for i in range(limite):
                btn_seguir = None
                for selector in selectores_seguir:
                    try:
                        botones = self.driver.find_elements(By.XPATH, selector)
                        if botones:
                            btn_seguir = botones[0]
                            break
                    except Exception:
                        continue

                if not btn_seguir:
                    print(f"   No hay más sugerencias ({seguidos} seguidos)")
                    break

                try:
                    btn_seguir.click()
                    seguidos += 1
                    print(f"   ✅ Usuario {seguidos}/{limite} seguido")
                    delay = random.uniform(3, 8)
                    time.sleep(delay)
                    self._manejar_puzzle()
                except Exception as e:
                    print(f"   ⚠️ Error siguiendo usuario: {e}")
                    break

        except Exception as e:
            print(f"❌ Error siguiendo usuarios en Twitter: {e}")

        return seguidos