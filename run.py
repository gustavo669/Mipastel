import sys
import os
import subprocess
import time
import threading
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()
print(f"Directorio base: {BASE_DIR}")


BACKEND_APP = BASE_DIR / "app.py"
ADMIN_APP = BASE_DIR / "admin" / "admin_app.py"

print(f"Backend: {BACKEND_APP}")
print(f"Admin: {ADMIN_APP}")

class MiPastelLauncher:
    def __init__(self):
        self.servidor_proceso = None
        self.servidor_activo = False

    def verificar_estructura(self):
        """Verifica que todos los archivos necesarios existan"""
        print("\nVerificando estructura...")

        archivos_necesarios = {
            "Backend (app.py)": BACKEND_APP,
            "Admin App": ADMIN_APP,
            "Database": BASE_DIR / "database.py",
            "Templates": BASE_DIR / "templates",
        }

        todos_ok = True
        for nombre, archivo in archivos_necesarios.items():
            if archivo.exists():
                print(f"✓ {nombre}")
            else:
                print(f"✗ {nombre} - NO ENCONTRADO")
                todos_ok = False
        return todos_ok

    def start_fastapi(self):
        """Inicia el servidor FastAPI"""
        try:
            print(f"\nIniciando servidor web...")

            os.chdir(BASE_DIR)
            print(f"Directorio de trabajo: {os.getcwd()}")

            proceso = subprocess.Popen(
                [sys.executable, "app.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                encoding="utf-8",
                bufsize=1
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

            for i in range(25):
                try:
                    import requests
                    response = requests.get("http://127.0.0.1:5000/health", timeout=2)
                    if response.status_code == 200:
                        return True
                except:
                    pass

                if proceso.poll() is not None:
                    error_output = proceso.stderr.read()
                    return False

                time.sleep(1)
                if i % 5 == 0:
                    print(f"  Esperando... ({i+1}/25s)")

            return False

        except Exception as e:
            import traceback
            traceback.print_exc()
            return False

    def start_admin_app(self):
        """Inicia la aplicación de administración"""
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
        """Ejecuta el lanzador principal"""
        print("=" * 60)
        print("Mi Pastel - Sistema de Gestión")
        print("=" * 60)

        if not self.verificar_estructura():
            return

        if not self.start_fastapi():
            return

        app, ventana = self.start_admin_app()
        if app is None or ventana is None:
            self.stop_fastapi()
            return

        print("\n" + "=" * 60)
        print("SISTEMA INICIADO CORRECTAMENTE")
        print("Servidor web: http://127.0.0.1:5000")
        print("App admin: Abierta")
        print("Health check: http://127.0.0.1:5000/health")
        print("Para cerrar: Cierra la ventana de administración")
        print("=" * 60)

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
        """Detiene el servidor FastAPI"""
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

    def cleanup(self):
        """Limpia recursos"""
        print("\nLimpiando recursos...")
        self.stop_fastapi()


def main():
    launcher = MiPastelLauncher()
    launcher.run()

if __name__ == "__main__":
    main()