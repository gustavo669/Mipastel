#!/usr/bin/env python3
"""
Script de Configuración Inicial - Sistema Mi Pastel
=====================================================

Este script configura automáticamente:
1. Genera un SECRET_KEY seguro
2. Genera hashes de contraseñas para todos los usuarios
3. Crea el archivo .env con todas las configuraciones
4. Valida la configuración

Uso:
    python setup_env.py
"""

import secrets
import sys
from datetime import datetime
from pathlib import Path

import bcrypt


def generar_secret_key():
    """Genera una SECRET_KEY segura."""
    return secrets.token_hex(32)


def generar_hash_contraseña(contraseña):
    """Genera hash bcrypt para una contraseña."""
    salt = bcrypt.gensalt(rounds=12)
    hash_obj = bcrypt.hashpw(contraseña.encode('utf-8'), salt)
    return hash_obj.decode('utf-8')


def obtener_entrada_usuario(prompt, default=None):
    """Obtiene entrada del usuario con valor por defecto."""
    if default:
        entrada = input(f"{prompt} [{default}]: ").strip()
        return entrada if entrada else default
    else:
        while True:
            entrada = input(f"{prompt}: ").strip()
            if entrada:
                return entrada
            print("   Por favor ingresa un valor")


def obtener_contraseña_usuario(prompt):
    """Obtiene contraseña de forma segura sin mostrar caracteres."""
    import getpass
    while True:
        contraseña = getpass.getpass(f"{prompt}: ")
        if len(contraseña) < 6:
            print("  La contraseña debe tener al menos 6 caracteres")
            continue

        confirmación = getpass.getpass("Confirmar contraseña: ")
        if contraseña != confirmación:
            print("  Las contraseñas no coinciden")
            continue

        return contraseña


def crear_archivo_env():
    """Crea el archivo .env con todas las configuraciones."""
    print("\n" + "="*70)
    print("CONFIGURACIÓN INICIAL - SISTEMA MI PASTEL")
    print("="*70)

    # Generar SECRET_KEY
    print("\nGenerando SECRET_KEY segura...")
    secret_key = generar_secret_key()
    print(f"  SECRET_KEY generada: {secret_key[:16]}...")

    # Base de datos
    print("\n🗄️  CONFIGURACIÓN DE BASE DE DATOS")
    db_server = obtener_entrada_usuario(
        "  SQL Server (ej: (localdb)\\MSSQLLocalDB)",
        "(localdb)\\MSSQLLocalDB"
    )
    db_user = obtener_entrada_usuario("  Usuario BD", "")
    db_password = obtener_entrada_usuario("  Contraseña BD (dejar vacío si no aplica)", "")

    # Contraseñas de usuarios
    print("\n👥 CONFIGURACIÓN DE CONTRASEÑAS DE USUARIOS")
    print("   Déjalo en blanco para usar contraseñas por defecto")

    usuarios_sucursales = [
        ("jutiapa1", "Jutiapa 1"),
        ("jutiapa2", "Jutiapa 2"),
        ("jutiapa3", "Jutiapa 3"),
        ("progreso", "Progreso"),
        ("quesada", "Quesada"),
        ("acatempa", "Acatempa"),
        ("yupiltepeque", "Yupiltepeque"),
        ("atescatempa", "Atescatempa"),
        ("adelanto", "Adelanto"),
        ("jerez", "Jeréz"),
        ("comapa", "Comapa"),
        ("carina", "Carina"),
    ]

    hashes_usuarios = {}
    contraseñas_por_defecto = {
        "jutiapa1": "jut1pass",
        "jutiapa2": "jut2pass",
        "jutiapa3": "jut3pass",
        "progreso": "progpass",
        "quesada": "quespass",
        "acatempa": "acatpass",
        "yupiltepeque": "yupepass",
        "atescatempa": "atespass",
        "adelanto": "adelpass",
        "jerez": "jerpass",
        "comapa": "comapass",
        "carina": "caripass",
    }

    for usuario, sucursal in usuarios_sucursales:
        default = contraseñas_por_defecto[usuario]
        print(f"\n   {usuario} ({sucursal})")
        print(f"     Contraseña por defecto: {default}")
        usar_default = input("     ¿Usar por defecto? (s/n) [s]: ").strip().lower()

        if usar_default in ('', 's', 'si', 'yes'):
            contraseña = default
            print(f"   Usando contraseña por defecto")
        else:
            contraseña = obtener_contraseña_usuario(f"     Nueva contraseña para {usuario}")

        hashes_usuarios[usuario.upper() + "_PASSWORD_HASH"] = generar_hash_contraseña(contraseña)

    # Contraseña de admin
    print(f"\n   admin (Administrador)")
    print(f"     Contraseña por defecto: admin123")
    usar_default = input("     ¿Usar por defecto? (s/n) [n]: ").strip().lower()

    if usar_default in ('s', 'si', 'yes'):
        admin_contraseña = "admin123"
        print(f"   CAMBIAR esta contraseña en producción")
    else:
        admin_contraseña = obtener_contraseña_usuario("     Nueva contraseña para admin")

    admin_hash = generar_hash_contraseña(admin_contraseña)

    # Email (opcional)
    print("\nCONFIGURACIÓN DE EMAIL (Opcional)")
    usar_email = input("   ¿Configurar envío de reportes por email? (s/n) [n]: ").strip().lower()

    email_config = {}
    if usar_email in ('s', 'si', 'yes'):
        email_config['SMTP_SERVER'] = obtener_entrada_usuario("     Servidor SMTP", "smtp.gmail.com")
        email_config['SMTP_PORT'] = obtener_entrada_usuario("     Puerto SMTP", "587")
        email_config['SMTP_USER'] = obtener_entrada_usuario("     Email")
        email_config['SMTP_PASSWORD'] = obtener_entrada_usuario("     Contraseña email/app")
        email_config['SMTP_FROM_EMAIL'] = obtener_entrada_usuario("     Email remitente", "noreply@mipastel.com")

    # Otros parámetros
    print("\nOTROS PARÁMETROS")
    host = obtener_entrada_usuario("   HOST", "0.0.0.0")
    port = obtener_entrada_usuario("   PORT", "5000")
    session_hours = obtener_entrada_usuario("   Duración de sesión (horas)", "8")

    # Generar contenido del .env
    contenido_env = f"""# ============================================================================
# CONFIGURACIÓN DE BASE DE DATOS - SQL SERVER
# ============================================================================
DB_SERVER={db_server}
DB_USER={db_user}
DB_PASSWORD={db_password}
DB_NAME_NORMALES=MiPastel
DB_NAME_CLIENTES=MiPastel_Clientes
DB_DRIVER=ODBC Driver 17 for SQL Server

# ============================================================================
# CONFIGURACIÓN DE SEGURIDAD
# ============================================================================
SECRET_KEY={secret_key}
ADMIN_PASSWORD_HASH={admin_hash}

# ============================================================================
# CONFIGURACIÓN DEL SERVIDOR
# ============================================================================
HOST={host}
PORT={port}
DEBUG=False
LOG_LEVEL=INFO

# ============================================================================
# CONFIGURACIÓN DE SESIÓN
# ============================================================================
SESSION_DURATION_HOURS={session_hours}
MAX_LOGIN_ATTEMPTS=5
LOGIN_TIMEOUT_SECONDS=300

# ============================================================================
# CONFIGURACIÓN DE REDIS
# ============================================================================
REDIS_URL=redis://localhost:6379

# ============================================================================
# CONFIGURACIÓN DE CORS
# ============================================================================
ALLOWED_ORIGINS=http://localhost:5000,http://127.0.0.1:5000,http://192.168.1.100:5000

# ============================================================================
# CONTRASEÑAS DE USUARIOS - HASHES BCRYPT
# ============================================================================
"""

    for var_name, hash_value in sorted(hashes_usuarios.items()):
        contenido_env += f"{var_name}={hash_value}\n"

    # Agregar configuración de email si aplica
    if email_config:
        contenido_env += "\n# ============================================================================\n"
        contenido_env += "# CONFIGURACIÓN DE EMAIL\n"
        contenido_env += "# ============================================================================\n"
        for key, value in email_config.items():
            contenido_env += f"{key}={value}\n"

    # Guardar archivo
    env_path = Path(".env")

    if env_path.exists():
        print("\nEl archivo .env ya existe")
        sobrescribir = input("   ¿Sobrescribir? (s/n) [n]: ").strip().lower()
        if sobrescribir not in ('s', 'si', 'yes'):
            print("Operación cancelada")
            return False

    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(contenido_env)

        print(f"\nArchivo .env creado exitosamente: {env_path.absolute()}")

        # Guardar backup de contraseñas (para referencia)
        contraseñas_path = Path(".env.passwords.txt")
        with open(contraseñas_path, 'w', encoding='utf-8') as f:
            f.write("CONTRASEÑAS GENERADAS - GUARDAR EN LUGAR SEGURO\n")
            f.write(f"Fecha: {datetime.now().isoformat()}\n")
            f.write("="*70 + "\n\n")

            for usuario, _ in usuarios_sucursales:
                default = contraseñas_por_defecto[usuario]
                f.write(f"{usuario}: {default}\n")
            f.write(f"admin: {admin_contraseña}\n")

        print(f"Contraseñas guardadas en: {contraseñas_path.absolute()}")
        print("   IMPORTANTE: Elimina este archivo después de cambiar las contraseñas")

        return True

    except Exception as e:
        print(f"\nError al crear .env: {e}")
        return False


def validar_instalacion():
    """Valida que todas las dependencias estén instaladas."""
    print("\nValidando dependencias...")

    dependencias = [
        ("fastapi", "FastAPI"),
        ("sqlalchemy", "SQLAlchemy"),
        ("bcrypt", "bcrypt"),
        ("pydantic", "Pydantic"),
        ("python-dotenv", "python-dotenv"),
    ]

    faltantes = []
    for modulo, nombre in dependencias:
        try:
            __import__(modulo)
            print(f"  {nombre}")
        except ImportError:
            print(f"  {nombre}")
            faltantes.append(nombre)

    if faltantes:
        print(f"\nFaltan dependencias: {', '.join(faltantes)}")
        print("   Instalar con: pip install -r requirements.txt")
        return False

    return True


def main():
    """Función principal."""
    try:
        # Verificar dependencias
        if not validar_instalacion():
            print("\nPor favor instala las dependencias antes de continuar")
            return False

        # Crear .env
        if crear_archivo_env():
            print("\n" + "="*70)
            print("CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
            print("="*70)
            print("\nPróximos pasos:")
            print("  1. Revisar el archivo .env")
            print("  2. Ejecutar: python -m pytest (para validar)")
            print("  3. Ejecutar: python app.py (para iniciar el servidor)")
            print("  4. Acceder a: http://localhost:5000/login")
            print("\nIMPORTANTE:")
            print("  - Cambiar todas las contraseñas en producción")
            print("  - Usar HTTPS en producción")
            print("  - No comprometer el archivo .env")
            return True
        else:
            return False

    except KeyboardInterrupt:
        print("\n\nConfiguración cancelada por el usuario")
        return False
    except Exception as e:
        print(f"\nError durante la configuración: {e}")
        return False


if __name__ == "__main__":
    sys.exit(0 if main() else 1)