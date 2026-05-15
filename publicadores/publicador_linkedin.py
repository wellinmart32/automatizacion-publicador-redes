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


class PublicadorLinkedIn:
    """Publicador automático para LinkedIn — solo versión FULL"""

    LIMITE_CONEXIONES_PAGADO = 10

    def __init__(self, config, es_full=False):
        self.config  = config
        self.es_full = es_full
        self.driver  = None

    # ==================== NAVEGADOR ====================

    def _iniciar_navegador(self):
        """Inicia Firefox con el perfil dedicado de LinkedIn"""
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        options = FirefoxOptions()

        if self.config.get('usar_perfil_existente') == 'si':
            perfil_path = os.path.join(base_dir, 'perfiles', 'linkedin_publicador')
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

    def verificar_sesion_linkedin(self):
        """Verifica sesión en LinkedIn — espera login si es necesario"""
        print(f"{N}🔐 Verificando sesión de LinkedIn...{X}")
        try:
            self.driver.get("https://www.linkedin.com")
            time.sleep(4)

            # Detectar formulario de login
            login_elements = self.driver.find_elements(
                By.XPATH,
                "//input[@id='username' or @autocomplete='username']"
            )

            if login_elements:
                self._notificar_login(
                    "Iniciar sesión en LinkedIn",
                    "Ingresa tus credenciales en el navegador.\nTienes 2 minutos."
                )
                print(f"\n{A}{N}⚠️  NO HAS INICIADO SESIÓN EN LINKEDIN{X}")
                print(f"{A}" + "=" * 60 + X)
                print(f"{A}Por favor INICIA SESIÓN en LinkedIn ahora.{X}")
                print(f"{A}Tienes 2 MINUTOS para iniciar sesión.{X}")
                print(f"{A}" + "=" * 60 + X + "\n")

                timeout = 120
                transcurrido = 0
                while transcurrido < timeout:
                    time.sleep(5)
                    transcurrido += 5
                    try:
                        login_check = self.driver.find_elements(
                            By.XPATH, "//input[@id='username']"
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
                print(f"   {V}✅ Ya tienes sesión activa en LinkedIn{X}")
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
        """Abre el compositor de nueva publicación en LinkedIn"""
        print(f"📝 Abriendo compositor de publicación...")

        selectores_nuevo = [
            "//button[contains(@class, 'share-box-feed-entry__trigger')]",
            "//*[@aria-label='Iniciar una publicación']",
            "//*[@aria-label='Start a post']",
            "//span[text()='Iniciar una publicación']/..",
            "//span[text()='Start a post']/..",
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

        # Estrategia 2: buscar área de texto directamente
        try:
            area = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@role='textbox'][@contenteditable='true']")
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
        """Ingresa el texto del post"""
        print(f"✍️  Ingresando texto...")
        try:
            campo = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@contenteditable='true'][@role='textbox']")
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
        """Sube imágenes al post de LinkedIn"""
        print(f"   🖼️  Subiendo {len(imagenes)} imagen(es)...")
        try:
            # Buscar botón de adjuntar foto
            selectores_foto = [
                "//button[@aria-label='Añadir una foto']",
                "//button[@aria-label='Add a photo']",
                "//button[contains(@aria-label, 'foto') or contains(@aria-label, 'photo')]",
            ]
            btn_foto = None
            for selector in selectores_foto:
                try:
                    btn_foto = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except Exception:
                    continue

            if btn_foto:
                btn_foto.click()
                time.sleep(1)

            inputs = self.driver.find_elements(By.XPATH, "//input[@type='file']")
            if inputs:
                inputs[0].send_keys(imagenes[0])
                time.sleep(3)
                print(f"   {V}✅ Imagen cargada{X}")
                return True

            print(f"   {A}⚠️  No se encontró input de archivo{X}")
            return False

        except Exception as e:
            print(f"   {A}⚠️  Error subiendo imagen: {e}{X}")
            return False

    def _hacer_clic_publicar(self):
        """Hace clic en el botón Publicar"""
        print(f"   🚀 Buscando botón publicar...")

        selectores_publicar = [
            "//button[@class='share-actions__primary-action']",
            "//button[contains(@class,'share-actions__primary')]",
            "//span[text()='Publicar']/..",
            "//span[text()='Post']/..",
        ]

        for selector in selectores_publicar:
            try:
                btn = WebDriverWait(self.driver, 8).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                self.driver.execute_script("arguments[0].click();", btn)
                print(f"   {V}✅ Post publicado{X}")
                return True
            except Exception:
                continue

        print(f"   {R}❌ No se encontró botón Publicar{X}")
        return False

    # ==================== PUBLICAR ====================

    def publicar(self, texto, imagenes=None, videos=None):
        """
        Publica en LinkedIn

        Args:
            texto: Texto del post
            imagenes: Lista de rutas de imágenes (solo FULL)
            videos: Lista de rutas de videos (solo FULL)

        Returns:
            bool: True si se publicó correctamente
        """
        if not self.es_full:
            print(f"   {A}ℹ️  LinkedIn requiere versión FULL{X}")
            return False

        intentos_max = self.config.get('max_intentos_por_publicacion', 3)

        for intento in range(1, intentos_max + 1):
            print(f"\n{N}" + "="*70 + X)
            print(f"{N}🔄 INTENTO {intento} DE {intentos_max} — LinkedIn{X}")
            print(f"{N}" + "="*70 + X)

            try:
                if not self.driver:
                    self._iniciar_navegador()

                if not self.verificar_sesion_linkedin():
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
                print(f"{V}{N}✅ PUBLICACIÓN EXITOSA EN LINKEDIN{X}")
                print(f"{V}{N}" + "="*70 + X)
                return True

            except Exception as e:
                print(f"   {R}❌ Error en intento {intento}: {e}{X}")
                if intento < intentos_max:
                    time.sleep(self.config.get('tiempo_entre_intentos', 3))

        print(f"\n{R}{N}" + "="*70 + X)
        print(f"{R}{N}❌ NO SE PUDO PUBLICAR EN LINKEDIN{X}")
        print(f"{R}{N}" + "="*70 + X)
        return False

    # ==================== SOLICITUDES DE CONEXIÓN ====================

    def enviar_solicitudes_conexion(self, cantidad=None):
        """
        Envía solicitudes de conexión en LinkedIn

        Args:
            cantidad: Número de solicitudes (máx 10 en FULL)

        Returns:
            int: Número de solicitudes enviadas
        """
        if not self.es_full:
            print(f"   {A}ℹ️  Enviar conexiones requiere versión FULL{X}")
            return 0

        limite = self.LIMITE_CONEXIONES_PAGADO
        if cantidad:
            limite = min(cantidad, limite)

        enviadas = 0

        try:
            if not self.driver:
                self._iniciar_navegador()

            if not self.verificar_sesion_linkedin():
                print(f"   {R}❌ No se pudo verificar la sesión{X}")
                return 0

            print(f"\n👥 Enviando hasta {limite} solicitudes de conexión en LinkedIn...")
            self.driver.get("https://www.linkedin.com/mynetwork/")
            time.sleep(4)

            while enviadas < limite:
                try:
                    botones = self.driver.find_elements(
                        By.XPATH,
                        "//button[contains(@aria-label, 'Conectar') or contains(@aria-label, 'Connect')]"
                    )

                    if not botones:
                        print(f"   ℹ️  No se encontraron más sugerencias")
                        break

                    for btn in botones:
                        if enviadas >= limite:
                            break
                        try:
                            if btn.is_displayed() and btn.is_enabled():
                                self.driver.execute_script(
                                    "arguments[0].scrollIntoView({block: 'center'});", btn
                                )
                                time.sleep(0.5)
                                btn.click()
                                time.sleep(1)

                                # Confirmar si aparece diálogo
                                try:
                                    confirmar = WebDriverWait(self.driver, 3).until(
                                        EC.element_to_be_clickable(
                                            (By.XPATH, "//button[@aria-label='Enviar sin nota' or @aria-label='Send without a note']")
                                        )
                                    )
                                    confirmar.click()
                                except Exception:
                                    pass

                                enviadas += 1
                                print(f"   {V}✅ Solicitud enviada ({enviadas}/{limite}){X}")
                                time.sleep(random.uniform(2, 5))
                        except Exception:
                            continue

                    self.driver.execute_script("window.scrollBy(0, 600);")
                    time.sleep(2)

                except Exception as e:
                    print(f"   {A}⚠️  Error enviando solicitudes: {e}{X}")
                    break

        except Exception as e:
            print(f"   {R}❌ Error en envío de solicitudes: {e}{X}")

        print(f"\n   📊 Solicitudes enviadas: {enviadas}/{limite}")
        return enviadas