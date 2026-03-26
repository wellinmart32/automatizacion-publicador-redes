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
from selenium.webdriver.firefox.service import Service


class PublicadorFacebook:
    """Publicador automático para Facebook"""

    # Límites por tipo de licencia
    LIMITE_PUBLICACIONES_GRATIS = 1
    LIMITE_SOLICITUDES_GRATIS = 5
    LIMITE_SOLICITUDES_PAGADO = 10

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

            perfil_path = os.path.join(base_dir, self.config.get('carpeta_perfil_custom', 'perfiles/publicador_redes'))
            os.makedirs(perfil_path, exist_ok=True)
            options.add_argument(f"-profile")
            options.add_argument(perfil_path)

        if self.config.get('desactivar_notificaciones'):
            options.set_preference("dom.webnotifications.enabled", False)
            options.set_preference("dom.push.enabled", False)

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
                "//*[contains(text(), 'puzzle')]",
                "//*[contains(@class, 'puzzle')]"
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
        Publica en Facebook

        Args:
            texto: Texto del anuncio
            imagenes: Lista de rutas de imágenes (solo versión FULL)
            videos: Lista de rutas de videos (solo versión FULL)

        Returns:
            bool: True si se publicó correctamente
        """
        # Versión gratis solo permite texto
        if not self.es_full:
            imagenes = None
            videos = None

        try:
            if not self.driver:
                self._iniciar_navegador()

            print("📘 Abriendo Facebook...")
            self.driver.get("https://www.facebook.com")
            time.sleep(3)

            self._manejar_puzzle()

            # Buscar área de publicación
            print("   Buscando área de publicación...")
            selectores_area = [
                "//div[@role='button'][contains(@aria-label, '¿Qué')]",
                "//div[@role='button'][contains(@aria-label, 'What')]",
                "//div[contains(@class, 'x1i10hfl')][contains(@role, 'button')]"
            ]

            area = None
            for selector in selectores_area:
                try:
                    area = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except Exception:
                    continue

            if not area:
                print("   ❌ No se encontró el área de publicación")
                return False

            area.click()
            time.sleep(2)

            self._manejar_puzzle()

            # Ingresar texto
            print("   Ingresando texto...")
            try:
                campo_texto = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@role='textbox']"))
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

            # Agregar videos si es FULL
            if self.es_full and videos:
                print(f"   Agregando {len(videos)} video(s)...")
                # TODO: implementar subida de videos
                pass

            # Buscar botón publicar
            print("   Buscando botón publicar...")
            selectores_publicar = [
                "//div[@aria-label='Publicar'][@role='button']",
                "//div[@aria-label='Post'][@role='button']",
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
            print("   ✅ Publicación enviada")
            time.sleep(self.config.get('espera_despues_publicar', 5))

            return True

        except Exception as e:
            print(f"❌ Error publicando en Facebook: {e}")
            return False

    def enviar_solicitudes_amistad(self, cantidad=None):
        """
        Envía solicitudes de amistad

        Args:
            cantidad: Número de solicitudes (5 gratis, 10 pagado)

        Returns:
            int: Número de solicitudes enviadas
        """
        limite = self.LIMITE_SOLICITUDES_PAGADO if self.es_full else self.LIMITE_SOLICITUDES_GRATIS
        if cantidad:
            limite = min(cantidad, limite)

        enviadas = 0

        try:
            if not self.driver:
                self._iniciar_navegador()

            print(f"👥 Enviando hasta {limite} solicitudes de amistad...")
            self.driver.get("https://www.facebook.com/friends/suggestions")
            time.sleep(3)

            self._manejar_puzzle()

            selectores_agregar = [
                "//div[@aria-label='Agregar amigo'][@role='button']",
                "//div[@aria-label='Add friend'][@role='button']",
                "//span[text()='Agregar amigo']/..",
                "//span[text()='Add friend']/.."
            ]

            for i in range(limite):
                btn_agregar = None
                for selector in selectores_agregar:
                    try:
                        botones = self.driver.find_elements(By.XPATH, selector)
                        if botones:
                            btn_agregar = botones[0]
                            break
                    except Exception:
                        continue

                if not btn_agregar:
                    print(f"   No hay más sugerencias disponibles ({enviadas} enviadas)")
                    break

                try:
                    btn_agregar.click()
                    enviadas += 1
                    print(f"   ✅ Solicitud {enviadas}/{limite} enviada")
                    # Delay aleatorio entre solicitudes para evitar detección
                    delay = random.uniform(3, 8)
                    time.sleep(delay)
                    self._manejar_puzzle()
                except Exception as e:
                    print(f"   ⚠️ Error enviando solicitud: {e}")
                    break

        except Exception as e:
            print(f"❌ Error enviando solicitudes: {e}")

        return enviadas