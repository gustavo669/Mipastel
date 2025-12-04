import sys
import os
import subprocess
import time
import threading
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()

try:
    from pyngrok import ngrok
    NGROK_AVAILABLE = True
except ImportError:
    NGROK_AVAILABLE = False
    print("pyngrok no está instalado. Instala con: pip install pyngrok")


class MiPastelLauncherNgrok:
    def __init__(self, usar_ngrok=True):
        self.servidor_proceso = None
        self.servidor_activo = False
        self.ngrok_tunnel = None
        self.usar_ngrok = usar_ngrok and NGROK_AVAILABLE

    def start_fastapi(self):
        try:
            print(f"\nIniciando servidor web...")
            os.chdir(BASE_DIR)

            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            env["PYTHONUTF8"] = "1"
            
            proceso = subprocess.Popen(
                [sys.executable, "app.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=env,
                errors='replace'
            )

            self.servidor_proceso = proceso
            self.servidor_activo = True

            def leer_salida():
                while True:
                    output = proceso.stdout.readline()
                    if output == '' and proceso.poll() is not None:
                        break
                    if output:
                        print(f"[Servidor] {output.strip()}")

            thread = threading.Thread(target=leer_salida, daemon=True)
            thread.start()

            for _ in range(25):
                try:
                    import requests
                    response = requests.get("http://127.0.0.1:5000/health", timeout=2)
                    if response.status_code == 200:
                        return True
                except:
                    pass

                if proceso.poll() is not None:
                    return False

                time.sleep(1)

            return False

        except Exception as e:
            print(f"Error al iniciar servidor: {e}")
            import traceback
            traceback.print_exc()
            return False

    def start_ngrok(self):
        try:
            try:
                activos = ngrok.get_tunnels()
                for t in activos:
                    ngrok.disconnect(t.public_url)
            except:
                pass

            self.ngrok_tunnel = ngrok.connect(5000, bind_tls=True)
            url_publica = self.ngrok_tunnel.public_url

            print(f"URL Pública: {url_publica}")
            print(f"URL Local:   http://127.0.0.1:5000")

            return url_publica

        except Exception as e:
            print(f"Error al iniciar ngrok: {e}")
            return None

    def start_admin_app(self):
        try:
            print("\nIniciando aplicación de administración...")

            sys.path.insert(0, str(BASE_DIR))

            from PySide6.QtWidgets import QApplication
            from PySide6.QtGui import QFont
            from admin.admin_app import AdminApp, DARK_STYLE

            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)

            font = QFont("Segoe UI Variable", 10)
            if not font.exactMatch():
                font = QFont("Lato", 10)
            app.setFont(font)

            app.setStyleSheet(DARK_STYLE)

            ventana = AdminApp()
            ventana.show()

            return app, ventana

        except Exception as e:
            print(f"Error al iniciar aplicación admin: {e}")
            import traceback
            traceback.print_exc()
            return None, None

    def run(self):
        print("=" * 60)
        print("Mi Pastel - Sistema de Gestión")
        print("=" * 60)

        if not self.start_fastapi():
            print("No se pudo iniciar el servidor web")
            return

        url_publica = None
        if self.usar_ngrok:
            url_publica = self.start_ngrok()

        app, ventana = self.start_admin_app()
        if app is None or ventana is None:
            self.cleanup()
            return

        try:
            exit_code = app.exec()
        except KeyboardInterrupt:
            print("\nInterrupción por usuario")
            exit_code = 0
        except Exception as e:
            print(f"Error en la aplicación: {e}")
            exit_code = 1
        finally:
            self.cleanup()

        print("\n¡Hasta pronto! - Mi Pastel Administración")
        sys.exit(exit_code)

    def stop_fastapi(self):
        if self.servidor_proceso and self.servidor_activo:
            print("\nDeteniendo servidor web...")
            self.servidor_proceso.terminate()
            try:
                self.servidor_proceso.wait(timeout=5)
                print("Servidor web detenido")
            except subprocess.TimeoutExpired:
                self.servidor_proceso.kill()
                print("Servidor forzado a cerrar")
            self.servidor_activo = False

    def stop_ngrok(self):
        try:
            activos = ngrok.get_tunnels()
            for t in activos:
                ngrok.disconnect(t.public_url)
        except:
            pass

        self.ngrok_tunnel = None

    def cleanup(self):
        print("\nLimpiando recursos...")
        self.stop_ngrok()
        self.stop_fastapi()


def main():

    if not NGROK_AVAILABLE:
        print("\nngrok no está disponible")
        print("Para instalar: pip install pyngrok")
        print("\n¿Deseas continuar sin ngrok? (solo acceso local)")
        respuesta = input("Continuar [s/N]: ").strip().lower()

        if respuesta not in ['s', 'si', 'y', 'yes']:
            print("\nInstalación cancelada")
            print("Ejecuta: pip install pyngrok")
            return

        usar_ngrok = False
    else:
        usar_ngrok = True

    launcher = MiPastelLauncherNgrok(usar_ngrok=usar_ngrok)
    launcher.run()


if __name__ == "__main__":
    main()
