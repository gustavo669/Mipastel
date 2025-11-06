"""
Lanzador del sistema Mi Pastel v2.0
CORREGIDO - Versión funcional
"""
import sys
import os
import subprocess
import time
import threading
from pathlib import Path

# Configurar paths ABSOLUTOS
BASE_DIR = Path(__file__).parent.absolute()
print(f"📁 Directorio base: {BASE_DIR}")

# Rutas principales
BACKEND_APP = BASE_DIR / "app.py"
ADMIN_APP = BASE_DIR / "admin" / "admin_app.py"

print(f"🔍 Backend: {BACKEND_APP}")
print(f"🔍 Admin: {ADMIN_APP}")

class MiPastelLauncher:
    def __init__(self):
        self.servidor_proceso = None
        self.servidor_activo = False

    def verificar_estructura(self):
        """Verifica que todos los archivos necesarios existan"""
        print("\n🔍 Verificando estructura...")

        archivos_necesarios = {
            "Backend (app.py)": BACKEND_APP,
            "Admin App": ADMIN_APP,
            "Database": BASE_DIR / "database.py",
            "Templates": BASE_DIR / "templates",
        }

        todos_ok = True
        for nombre, archivo in archivos_necesarios.items():
            if archivo.exists():
                print(f"   ✅ {nombre}")
            else:
                print(f"   ❌ {nombre} - NO ENCONTRADO")
                todos_ok = False

        return todos_ok

    def start_fastapi(self):
        """Inicia el servidor FastAPI"""
        try:
            print(f"\n🚀 Iniciando servidor web...")

            # Cambiar al directorio base
            os.chdir(BASE_DIR)
            print(f"📂 Directorio de trabajo: {os.getcwd()}")

            # Ejecutar el servidor
            proceso = subprocess.Popen(
                [sys.executable, "app.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                encoding="utf-8",      # <--- AGREGA ESTA LÍNEA
                bufsize=1
            )

            self.servidor_proceso = proceso
            self.servidor_activo = True

            # Hilo para leer la salida
            def leer_salida():
                while True:
                    output = proceso.stdout.readline()
                    if output == '' and proceso.poll() is not None:
                        break
                    if output:
                        print(f"[Servidor] {output.strip()}")

            thread = threading.Thread(target=leer_salida, daemon=True)
            thread.start()

            # Esperar a que el servidor esté listo
            print("⏳ Esperando que el servidor inicie...")
            for i in range(25):
                try:
                    import requests
                    response = requests.get("http://127.0.0.1:5000/health", timeout=2)
                    if response.status_code == 200:
                        print("✅ Servidor web listo y respondiendo")
                        return True
                except:
                    pass

                # Verificar si el proceso sigue vivo
                if proceso.poll() is not None:
                    error_output = proceso.stderr.read()
                    print(f"❌ El servidor falló: {error_output}")
                    return False

                time.sleep(1)
                if i % 5 == 0:
                    print(f"   ⏳ Esperando... ({i+1}/25s)")

            print("❌ Timeout: El servidor no respondió en 25 segundos")
            return False

        except Exception as e:
            print(f"❌ Error al iniciar servidor: {e}")
            import traceback
            traceback.print_exc()
            return False

    def start_admin_app(self):
        """Inicia la aplicación de administración"""
        try:
            print("\n🖥️  Iniciando aplicación de administración...")

            # Agregar paths al sistema
            sys.path.insert(0, str(BASE_DIR))

            from PySide6.QtWidgets import QApplication
            from admin.admin_app import AdminApp

            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)

            # Configurar estilo básico
            app.setStyleSheet("""
                QMainWindow { background-color: #fffaf6; font-family: Arial; }
                QPushButton { 
                    background-color: #ff99cc; 
                    padding: 8px 15px; 
                    border-radius: 4px; 
                    border: none; 
                    font-weight: bold; 
                    color: white;
                }
                QPushButton:hover { background-color: #ff66b2; }
            """)

            ventana = AdminApp()
            ventana.show()

            print("✅ Aplicación de administración lista")
            return app, ventana

        except Exception as e:
            print(f"❌ Error al iniciar aplicación admin: {e}")
            import traceback
            traceback.print_exc()
            return None, None

    def run(self):
        """Ejecuta el lanzador principal"""
        print("=" * 60)
        print("🧁 Mi Pastel - Sistema de Gestión v2.0")
        print("=" * 60)

        # Verificar estructura
        if not self.verificar_estructura():
            print("\n❌ Faltan archivos esenciales. No se puede iniciar.")
            input("Presiona Enter para salir...")
            return

        # Iniciar servidor web
        if not self.start_fastapi():
            print("\n❌ No se pudo iniciar el servidor web")
            input("Presiona Enter para salir...")
            return

        # Iniciar aplicación de administración
        app, ventana = self.start_admin_app()
        if app is None or ventana is None:
            print("❌ No se pudo iniciar la aplicación de administración")
            self.stop_fastapi()
            input("Presiona Enter para salir...")
            return

        # Mostrar información
        print("\n" + "=" * 60)
        print("✅ SISTEMA INICIADO CORRECTAMENTE")
        print("   🌐 Servidor web: http://127.0.0.1:5000")
        print("   🖥️  App admin: Abierta")
        print("   📊 Health check: http://127.0.0.1:5000/health")
        print("   💡 Para cerrar: Cierra la ventana de administración")
        print("=" * 60)

        # Ejecutar loop
        try:
            exit_code = app.exec()
        except KeyboardInterrupt:
            print("\n⚠️  Interrupción por usuario")
            exit_code = 0
        except Exception as e:
            print(f"❌ Error en la aplicación: {e}")
            exit_code = 1
        finally:
            self.cleanup()

        print("\n👋 ¡Hasta pronto! - Mi Pastel v2.0")
        sys.exit(exit_code)

    def stop_fastapi(self):
        """Detiene el servidor FastAPI"""
        if self.servidor_proceso and self.servidor_activo:
            print("\n🛑 Deteniendo servidor web...")
            self.servidor_proceso.terminate()
            try:
                self.servidor_proceso.wait(timeout=5)
                print("✅ Servidor web detenido")
            except subprocess.TimeoutExpired:
                self.servidor_proceso.kill()
                print("⚠️  Servidor forzado a cerrar")
            self.servidor_activo = False

    def cleanup(self):
        """Limpia recursos"""
        print("\n🧹 Limpiando recursos...")
        self.stop_fastapi()

def main():
    launcher = MiPastelLauncher()
    launcher.run()

if __name__ == "__main__":
    main()