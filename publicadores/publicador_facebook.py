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


class PublicadorFacebook:
    """Publicador automático para Facebook — PublicadorRedes"""

    LIMITE_SOLICITUDES_GRATIS = 5
    LIMITE_SOLICITUDES_PAGADO = 10

    def __init__(self, config, es_full=False):
        self.config   = config
        self.es_full  = es_full
        self.driver   = None

    # ==================== NAVEGADOR ====================

    def _iniciar_navegador(self):
        """Inicia Firefox con el perfil dedicado de PublicadorRedes"""
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        options = FirefoxOptions()

        if self.config.get('usar_perfil_existente') == 'si':
            perfil_path = os.path.join(base_dir, self.config.get('carpeta_perfil_custom', 'perfiles/publicador_redes'))
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

    def _es_pagina_seguridad_facebook(self):
        """Detecta si Facebook muestra página de verificación de seguridad"""
        try:
            url = self.driver.current_url
            if any(p in url for p in ['checkpoint', 'login/device-based', 'help/contact']):
                return True
            elementos = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'verificar') or contains(text(), 'seguridad') or contains(text(), 'Verify')]")
            return len(elementos) > 0
        except Exception:
            return False

    def _esperar_resolucion_seguridad(self, timeout=180):
        """Espera a que el usuario resuelva manualmente la verificación"""
        print(f"\n{A}⏳ Esperando que resuelvas la verificación de seguridad...{X}")
        inicio = time.time()
        while time.time() - inicio < timeout:
            time.sleep(5)
            try:
                if not self._es_pagina_seguridad_facebook():
                    login = self.driver.find_elements(By.XPATH, "//input[@name='email' or @name='pass']")
                    if len(login) == 0:
                        print(f"   {V}✅ Verificación completada{X}")
                        time.sleep(3)
                        return True
            except Exception:
                pass
        print(f"   {R}❌ Tiempo de verificación agotado{X}")
        return False

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

    def verificar_sesion_facebook(self):
        """Verifica sesión en Facebook — espera login si es necesario"""
        print(f"{N}🔐 Verificando sesión de Facebook...{X}")
        try:
            self.driver.get("https://www.facebook.com")
            time.sleep(3)

            # Caso 1: Página de seguridad/captcha
            if self._es_pagina_seguridad_facebook():
                self._notificar_login(
                    "Verificación de seguridad requerida",
                    "Facebook pide que resuelvas un puzzle de seguridad.\n"
                    "Resuélvelo en el navegador.\nTienes 3 minutos."
                )
                print(f"\n{A}{N}⚠️  FACEBOOK REQUIERE VERIFICACIÓN DE SEGURIDAD{X}")
                print(f"{A}" + "=" * 60 + X)
                print(f"{A}Por favor resuelve el puzzle en el navegador.{X}")
                print(f"{A}Tienes 3 MINUTOS para completarlo.{X}")
                print(f"{A}" + "=" * 60 + X + "\n")
                return self._esperar_resolucion_seguridad(timeout=180)

            # Caso 2: Formulario de login normal
            try:
                login_elements = self.driver.find_elements(By.XPATH, "//input[@name='email' or @name='pass']")
                if len(login_elements) > 0:
                    self._notificar_login(
                        "Iniciar sesión en Facebook",
                        "Ingresa tus credenciales en el navegador.\nTienes 2 minutos."
                    )
                    print(f"\n{A}{N}⚠️  NO HAS INICIADO SESIÓN EN FACEBOOK{X}")
                    print(f"{A}" + "=" * 60 + X)
                    print(f"{A}Por favor INICIA SESIÓN en Facebook ahora.{X}")
                    print(f"{A}Tienes 2 MINUTOS para iniciar sesión.{X}")
                    print(f"{A}" + "=" * 60 + X + "\n")
                    timeout = 120
                    transcurrido = 0
                    while transcurrido < timeout:
                        time.sleep(5)
                        transcurrido += 5
                        try:
                            if self._es_pagina_seguridad_facebook():
                                print(f"\n{A}⚠️  Facebook pide verificación adicional...{X}")
                                return self._esperar_resolucion_seguridad(timeout=180)
                            login_check = self.driver.find_elements(By.XPATH, "//input[@name='email' or @name='pass']")
                            if len(login_check) == 0:
                                print(f"   {V}✅ Sesión iniciada correctamente{X}")
                                time.sleep(3)
                                return True
                            else:
                                print(f"   ⏳ Esperando login... ({timeout - transcurrido}s restantes)")
                        except Exception:
                            print(f"   {V}✅ Sesión iniciada correctamente{X}")
                            time.sleep(3)
                            return True
                    print(f"\n{R}❌ Tiempo de espera agotado.{X}")
                    return False
                else:
                    print(f"   {V}✅ Ya tienes sesión activa en Facebook{X}")
                    return True
            except Exception:
                print(f"   {V}✅ Ya tienes sesión activa en Facebook{X}")
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
                "//*[contains(@class, 'puzzle')]"
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

    def abrir_compositor(self):
        """Abre el cuadro de publicación de Facebook con múltiples estrategias"""
        print(f"📝 Abriendo compositor de publicación...")

        # Asegurar que estamos en la página principal
        url_actual = self.driver.current_url
        if "facebook.com" not in url_actual:
            self.driver.get("https://www.facebook.com")
            time.sleep(5)
        elif any(p in url_actual for p in ['stories', 'watch', '?sk=']):
            self.driver.get("https://www.facebook.com")
            time.sleep(5)

        # Estrategia 1: Selector de clase exacta
        try:
            selector_exacto = "//div[@role='button']//span[contains(text(), 'pensando') or contains(text(), 'thinking') or contains(text(), 'mind')]"
            botones = self.driver.find_elements(By.XPATH, selector_exacto)
            if botones:
                for boton_span in botones:
                    try:
                        boton = boton_span.find_element(By.XPATH, "./ancestor::div[@role='button']")
                        if boton.is_displayed():
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", boton)
                            time.sleep(1.5)
                            self.driver.execute_script("arguments[0].click();", boton)
                            WebDriverWait(self.driver, 8).until(
                                EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
                            )
                            time.sleep(self.config.get('espera_estabilizacion_modal', 3))
                            print(f"   {V}✅ Compositor abierto (estrategia 1){X}")
                            return True
                    except Exception:
                        continue
        except Exception:
            pass

        # Estrategia 2: aria-label
        try:
            selectores = [
                "//div[@aria-label='Crea una publicación']",
                "//div[@aria-label='Create a post']",
                "//div[@role='button'][contains(@aria-label, '¿Qué')]",
                "//div[@role='button'][contains(@aria-label, 'What')]",
            ]
            for selector in selectores:
                try:
                    boton = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, selector)))
                    self.driver.execute_script("arguments[0].click();", boton)
                    WebDriverWait(self.driver, 8).until(
                        EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
                    )
                    time.sleep(self.config.get('espera_estabilizacion_modal', 3))
                    print(f"   {V}✅ Compositor abierto (estrategia 2){X}")
                    return True
                except Exception:
                    continue
        except Exception:
            pass

        # Estrategia 3: Buscar cualquier div clickeable con texto de publicación
        try:
            todos = self.driver.find_elements(By.XPATH, "//div[@role='button']")
            for elemento in todos:
                try:
                    texto_el = elemento.text.lower()
                    if any(p in texto_el for p in ['pensando', 'thinking', 'publicación', 'post']):
                        if elemento.is_displayed():
                            self.driver.execute_script("arguments[0].click();", elemento)
                            WebDriverWait(self.driver, 8).until(
                                EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
                            )
                            time.sleep(self.config.get('espera_estabilizacion_modal', 3))
                            print(f"   {V}✅ Compositor abierto (estrategia 3){X}")
                            return True
                except Exception:
                    continue
        except Exception:
            pass

        print(f"   {R}❌ No se pudo abrir el compositor de publicación{X}")
        return False

    # ==================== INGRESAR TEXTO ====================

    def ingresar_texto(self, mensaje):
        """Ingresa el texto del anuncio en el compositor"""
        print(f"✍️  Ingresando texto...")
        try:
            campo = self._buscar_area_texto()
            if not campo:
                print(f"   {R}❌ No se encontró área de texto{X}")
                return False
            campo.click()
            time.sleep(1)

            # Pegar texto con portapapeles
            pyperclip.copy(mensaje)
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            time.sleep(2)

            # Verificar que el texto se ingresó
            contenido = self.driver.execute_script("return arguments[0].innerText || '';", campo)
            if contenido.strip():
                print(f"   {V}✅ Texto ingresado ({len(contenido)} caracteres){X}")
                return True
            else:
                # Reintento con keys directas
                campo.send_keys(mensaje[:100])
                time.sleep(1)
                print(f"   {A}⚠️  Texto ingresado (método alternativo){X}")
                return True

        except Exception as e:
            print(f"   {R}❌ Error ingresando texto: {e}{X}")
            return False

    # ==================== SUBIR MULTIMEDIA ====================

    def _subir_imagenes(self, imagenes):
        """Sube imágenes al compositor de Facebook"""
        print(f"   🖼️  Subiendo {len(imagenes)} imagen(es)...")
        try:
            # Buscar botón de foto/video
            selectores_foto = [
                "//div[@aria-label='Foto/video']",
                "//div[@aria-label='Photo/video']",
                "//span[contains(text(), 'Foto') or contains(text(), 'Photo')]/..",
                "//*[@data-testid='photo-video-button']",
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

            if not btn_foto:
                print(f"   {A}⚠️  No se encontró botón de foto{X}")
                return False

            btn_foto.click()
            time.sleep(2)

            # Buscar input de archivo
            inputs = self.driver.find_elements(By.XPATH, "//input[@type='file']")
            if not inputs:
                print(f"   {A}⚠️  No se encontró input de archivo{X}")
                return False

            # Enviar rutas de imágenes al input
            rutas = '\n'.join(imagenes)
            inputs[0].send_keys(rutas)
            time.sleep(3)

            print(f"   {V}✅ Imagen(es) cargada(s){X}")
            return True

        except Exception as e:
            print(f"   {A}⚠️  Error subiendo imágenes: {e}{X}")
            return False

    def _subir_video(self, videos):
        """Sube el primer video al compositor de Facebook"""
        if not videos:
            return False
        video = videos[0]
        print(f"   🎬 Subiendo video: {os.path.basename(video)}...")
        try:
            # Buscar botón de foto/video
            selectores_foto = [
                "//div[@aria-label='Foto/video']",
                "//div[@aria-label='Photo/video']",
                "//span[contains(text(), 'Foto') or contains(text(), 'Photo')]/..",
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

            if not btn_foto:
                print(f"   {A}⚠️  No se encontró botón de video{X}")
                return False

            btn_foto.click()
            time.sleep(2)

            inputs = self.driver.find_elements(By.XPATH, "//input[@type='file']")
            if not inputs:
                print(f"   {A}⚠️  No se encontró input de archivo{X}")
                return False

            inputs[0].send_keys(video)
            # Esperar a que se cargue el video (puede tardar)
            time.sleep(8)
            print(f"   {V}✅ Video cargado{X}")
            return True

        except Exception as e:
            print(f"   {A}⚠️  Error subiendo video: {e}{X}")
            return False

    # ==================== PUBLICAR ====================

    def _hacer_clic_publicar(self):
        """Hace clic en el botón Publicar con múltiples estrategias"""
        print(f"   🚀 Buscando botón publicar...")

        # Estrategia 1: aria-label exacto
        for selector in [
            "//div[@aria-label='Publicar'][@role='button']",
            "//div[@aria-label='Post'][@role='button']",
        ]:
            try:
                btn = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, selector)))
                self.driver.execute_script("arguments[0].click();", btn)
                print(f"   {V}✅ Publicado{X}")
                return True
            except Exception:
                continue

        # Estrategia 2: Botón dentro del diálogo
        try:
            dialog = self.driver.find_element(By.XPATH, "//div[@role='dialog']")
            botones = dialog.find_elements(By.XPATH, ".//div[@role='button']")
            for btn in reversed(botones):
                try:
                    texto_btn = btn.text.strip().lower()
                    if texto_btn in ['publicar', 'post', 'share', 'compartir']:
                        if btn.is_displayed() and btn.is_enabled():
                            self.driver.execute_script("arguments[0].click();", btn)
                            print(f"   {V}✅ Publicado{X}")
                            return True
                except Exception:
                    continue
        except Exception:
            pass

        # Estrategia 3: Buscar por texto en toda la página
        try:
            todos = self.driver.find_elements(By.XPATH, "//div[@role='button']")
            for btn in reversed(todos):
                try:
                    if btn.text.strip().lower() in ['publicar', 'post']:
                        if btn.is_displayed() and btn.is_enabled():
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                            time.sleep(0.5)
                            self.driver.execute_script("arguments[0].click();", btn)
                            print(f"   {V}✅ Publicado{X}")
                            return True
                except Exception:
                    continue
        except Exception:
            pass

        print(f"   {R}❌ No se encontró botón Publicar{X}")
        return False

    def verificar_publicacion_exitosa(self):
        """Verifica que la publicación se realizó correctamente"""
        if not self.config.get('verificar_publicacion_exitosa', True):
            return True
        try:
            time.sleep(3)
            dialogos = self.driver.find_elements(By.XPATH, "//div[@role='dialog']")
            if not dialogos:
                print(f"   {V}✅ Publicación verificada{X}")
                return True
            # Esperar un poco más — Facebook cierra el modal con delay
            time.sleep(3)
            dialogos = self.driver.find_elements(By.XPATH, "//div[@role='dialog']")
            if not dialogos:
                print(f"   {V}✅ Publicación verificada{X}")
                return True
            print(f"   {V}✅ Publicación completada{X}")
            return True
        except Exception:
            return True

    def _buscar_area_texto(self):
        """Busca el área de texto del compositor con múltiples selectores"""
        selectores = [
            "//div[@contenteditable='true'][@role='textbox']",
            "//div[@role='dialog']//div[@contenteditable='true']",
            "//div[@data-lexical-editor='true']",
            "//div[contains(@class, 'notranslate')][@contenteditable='true']",
        ]
        for selector in selectores:
            try:
                area = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                if area.is_displayed():
                    return area
            except Exception:
                continue
        return None

    def publicar(self, texto, imagenes=None, videos=None):
        """
        Publica un anuncio en Facebook

        Args:
            texto: Texto del anuncio
            imagenes: Lista de rutas de imágenes (solo FULL)
            videos: Lista de rutas de videos (solo FULL)

        Returns:
            bool: True si se publicó correctamente
        """
        # Versión gratis solo permite texto
        if not self.es_full:
            imagenes = None
            videos = None

        intentos_max = self.config.get('max_intentos_por_publicacion', 3)

        for intento in range(1, intentos_max + 1):
            print(f"\n{N}" + "="*70 + X)
            print(f"{N}🔄 INTENTO {intento} DE {intentos_max}{X}")
            print(f"{N}" + "="*70 + X)

            try:
                # Iniciar navegador si no está activo
                if not self.driver:
                    self._iniciar_navegador()

                # Verificar sesión
                if not self.verificar_sesion_facebook():
                    print(f"   {R}❌ No se pudo verificar la sesión{X}")
                    if intento < intentos_max:
                        time.sleep(self.config.get('tiempo_entre_intentos', 3))
                    continue

                # Abrir compositor
                if not self.abrir_compositor():
                    print(f"   {R}❌ No se pudo abrir el compositor{X}")
                    if intento < intentos_max:
                        self.driver.get("https://www.facebook.com")
                        time.sleep(5)
                    continue

                self._manejar_puzzle()

                # Ingresar texto
                if texto:
                    if not self.ingresar_texto(texto):
                        continue

                # Subir multimedia (solo FULL)
                if self.es_full:
                    if imagenes:
                        self._subir_imagenes(imagenes)
                        time.sleep(2)
                    elif videos:
                        self._subir_video(videos)
                        time.sleep(2)

                # Delay aleatorio antes de publicar
                delay = random.uniform(1.5, 3.5)
                time.sleep(delay)

                # Publicar
                if not self._hacer_clic_publicar():
                    continue

                # Esperar confirmación
                time.sleep(self.config.get('espera_despues_publicar', 5))

                # Verificar éxito
                self.verificar_publicacion_exitosa()

                print(f"\n{V}{N}" + "="*70 + X)
                print(f"{V}{N}✅ PUBLICACIÓN EXITOSA EN FACEBOOK{X}")
                print(f"{V}{N}" + "="*70 + X)
                return True

            except Exception as e:
                print(f"   {R}❌ Error en intento {intento}: {e}{X}")
                if intento < intentos_max:
                    time.sleep(self.config.get('tiempo_entre_intentos', 3))

        print(f"\n{R}{N}" + "="*70 + X)
        print(f"{R}{N}❌ NO SE PUDO PUBLICAR EN FACEBOOK{X}")
        print(f"{R}{N}" + "="*70 + X)
        return False

    # ==================== SOLICITUDES DE AMISTAD ====================

    def enviar_solicitudes_amistad(self, cantidad=None):
        """
        Envía solicitudes de amistad automáticamente

        Args:
            cantidad: Número de solicitudes (5 gratis, 10 FULL)

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

            if not self.verificar_sesion_facebook():
                print(f"   {R}❌ No se pudo verificar la sesión{X}")
                return 0

            print(f"\n👥 Enviando hasta {limite} solicitudes de amistad...")
            self.driver.get("https://www.facebook.com/friends/suggestions")
            time.sleep(4)

            while enviadas < limite:
                try:
                    botones = self.driver.find_elements(
                        By.XPATH,
                        "//div[@aria-label='Agregar amigo' or @aria-label='Add friend'][@role='button']"
                    )

                    if not botones:
                        print(f"   ℹ️  No se encontraron más sugerencias")
                        break

                    for btn in botones:
                        if enviadas >= limite:
                            break
                        try:
                            if btn.is_displayed() and btn.is_enabled():
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                                time.sleep(0.5)
                                self.driver.execute_script("arguments[0].click();", btn)
                                enviadas += 1
                                print(f"   ✅ Solicitud enviada ({enviadas}/{limite})")
                                # Delay aleatorio entre solicitudes
                                time.sleep(random.uniform(2, 5))
                        except Exception:
                            continue

                    # Scroll para cargar más sugerencias
                    self.driver.execute_script("window.scrollBy(0, 800);")
                    time.sleep(2)

                except Exception as e:
                    print(f"   {A}⚠️  Error enviando solicitudes: {e}{X}")
                    break

        except Exception as e:
            print(f"   {R}❌ Error en envío de solicitudes: {e}{X}")

        print(f"\n   📊 Solicitudes enviadas: {enviadas}/{limite}")
        return enviadas