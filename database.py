"""
Módulo de conexión a bases de datos SQL Server
Configuración para Mi Pastel - VERSIÓN COMPLETA v2.0
"""
import pyodbc
import logging
from typing import List, Dict, Any, Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== CONFIGURACIÓN ====================
SERVER = '(localdb)\\MSSQLLocalDB'
DRIVER = '{ODBC Driver 17 for SQL Server}'
DB_NORMALES = 'MiPastel'
DB_CLIENTES = 'MiPastel_Clientes'

# ==================== TABLA DE PRECIOS ====================
PRECIOS_PASTELES = {
    "Fresas": {"Mini": 60.00, "Pequeño": 85.00, "Mediano": 125.00, "Grande": 155.00, "Extra grande": 185.00, "Media plancha": 325.00},
    "Frutas": {"Mini": 65.00, "Pequeño": 90.00, "Mediano": 130.00, "Grande": 160.00, "Extra grande": 195.00, "Media plancha": 335.00},
    "Chocolate": {"Mini": 70.00, "Pequeño": 105.00, "Mediano": 140.00, "Grande": 185.00, "Extra grande": 245.00, "Media plancha": 400.00},
    "Selva negra": {"Mini": 65.00, "Pequeño": 100.00, "Mediano": 130.00, "Grande": 180.00, "Extra grande": 240.00, "Media plancha": 390.00},
    "Oreo": {"Mini": 70.00, "Pequeño": 105.00, "Mediano": 140.00, "Grande": 185.00, "Extra grande": 245.00, "Media plancha": 400.00},
    "Chocofresa": {"Mini": 70.00, "Pequeño": 105.00, "Mediano": 140.00, "Grande": 185.00, "Extra grande": 245.00, "Media plancha": 400.00},
    "Tres Leches": {"Mini": 70.00, "Pequeño": 105.00, "Mediano": 140.00, "Grande": 185.00, "Extra grande": 245.00, "Media plancha": 400.00},
    "Tres leches con Arándanos": {"Mini": 75.00, "Pequeño": 110.00, "Mediano": 145.00, "Grande": 190.00, "Extra grande": 255.00, "Media plancha": 420.00},
    "Fiesta": {"Mini": 55.00, "Pequeño": 70.00, "Mediano": 100.00, "Grande": 125.00, "Extra grande": 175.00, "Media plancha": 315.00},
    "Ambiente": {"Mini": 60.00, "Pequeño": 85.00, "Mediano": 125.00, "Grande": 155.00, "Extra grande": 185.00, "Media plancha": 325.00},
    "Zanahoria": {"Mini": 70.00, "Pequeño": 105.00, "Mediano": 140.00, "Grande": 185.00, "Extra grande": 245.00, "Media plancha": 400.00},
    "Boda": {"Mini": 80.00, "Pequeño": 120.00, "Mediano": 160.00, "Grande": 210.00, "Extra grande": 280.00, "Media plancha": 450.00},
    "Quince Años": {"Mini": 80.00, "Pequeño": 120.00, "Mediano": 160.00, "Grande": 210.00, "Extra grande": 280.00, "Media plancha": 450.00},
    "Otro": {"Mini": 60.00, "Pequeño": 85.00, "Mediano": 125.00, "Grande": 155.00, "Extra grande": 185.00, "Media plancha": 325.00}
}

class DatabaseManager:
    """Gestor principal de operaciones de base de datos"""

    @staticmethod
    def obtener_pasteles_normales(fecha_inicio: str = None, fecha_fin: str = None, sucursal: str = None) -> List[Dict[str, Any]]:
        """Obtiene todos los pasteles normales con filtros opcionales"""
        try:
            conn = get_conn_normales()
            cursor = conn.cursor()

            query = """
                SELECT id, sabor, tamano, precio, cantidad, sucursal, fecha, detalles, sabor_personalizado
                FROM PastelesNormales 
                WHERE 1=1
            """
            params = []

            if fecha_inicio and fecha_fin:
                query += " AND fecha BETWEEN ? AND ?"
                params.extend([fecha_inicio, fecha_fin])

            if sucursal and sucursal != "Todas":
                query += " AND sucursal = ?"
                params.append(sucursal)

            query += " ORDER BY fecha DESC, id DESC"

            cursor.execute(query, params)
            resultados = cursor.fetchall()
            conn.close()

            pasteles = []
            for row in resultados:
                pasteles.append({
                    'id': row[0],
                    'sabor': row[1] or '',
                    'tamano': row[2] or '',
                    'precio': float(row[3]) if row[3] else 0.0,
                    'cantidad': row[4] or 0,
                    'sucursal': row[5] or '',
                    'fecha': row[6].strftime('%Y-%m-%d %H:%M') if row[6] else '',
                    'detalles': row[7] or '',
                    'sabor_personalizado': row[8] or ''
                })
            return pasteles
        except Exception as e:
            logger.error(f"Error al obtener pasteles normales: {e}")
            raise Exception(f"Error al obtener pasteles normales: {e}")

    @staticmethod
    def obtener_pedidos_clientes(fecha_inicio: str = None, fecha_fin: str = None, sucursal: str = None) -> List[Dict[str, Any]]:
        """Obtiene todos los pedidos de clientes con filtros opcionales"""
        try:
            conn = get_conn_clientes()
            cursor = conn.cursor()

            query = """
                SELECT id, color, sabor, tamano, cantidad, precio, total, sucursal, 
                       fecha, dedicatoria, detalles, sabor_personalizado
                FROM PastelesClientes 
                WHERE 1=1
            """
            params = []

            if fecha_inicio and fecha_fin:
                query += " AND fecha BETWEEN ? AND ?"
                params.extend([fecha_inicio, fecha_fin])

            if sucursal and sucursal != "Todas":
                query += " AND sucursal = ?"
                params.append(sucursal)

            query += " ORDER BY fecha DESC, id DESC"

            cursor.execute(query, params)
            resultados = cursor.fetchall()
            conn.close()

            pedidos = []
            for row in resultados:
                pedidos.append({
                    'id': row[0],
                    'color': row[1] or '',
                    'sabor': row[2] or '',
                    'tamano': row[3] or '',
                    'cantidad': row[4] or 0,
                    'precio': float(row[5]) if row[5] else 0.0,
                    'total': float(row[6]) if row[6] else 0.0,
                    'sucursal': row[7] or '',
                    'fecha': row[8].strftime('%Y-%m-%d %H:%M') if row[8] else '',
                    'dedicatoria': row[9] or '',
                    'detalles': row[10] or '',
                    'sabor_personalizado': row[11] or ''
                })
            return pedidos
        except Exception as e:
            logger.error(f"Error al obtener pedidos clientes: {e}")
            raise Exception(f"Error al obtener pedidos clientes: {e}")

    @staticmethod
    def obtener_precios() -> List[Dict[str, Any]]:
        """Obtiene la configuración de precios"""
        try:
            conn = get_conn_normales()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, sabor, tamano, precio 
                FROM PastelesPrecios 
                ORDER BY sabor, tamano
            """)
            resultados = cursor.fetchall()
            conn.close()

            precios = []
            for row in resultados:
                precios.append({
                    'id': row[0],
                    'sabor': row[1],
                    'tamano': row[2],
                    'precio': float(row[3]) if row[3] else 0.0
                })
            return precios
        except Exception as e:
            logger.error(f"Error al obtener precios: {e}")
            raise Exception(f"Error al obtener precios: {e}")

    @staticmethod
    def actualizar_precios(precios_data: List[Dict[str, Any]]) -> bool:
        """Actualiza los precios en la base de datos"""
        try:
            conn = get_conn_normales()
            cursor = conn.cursor()

            for precio in precios_data:
                cursor.execute("""
                    UPDATE PastelesPrecios 
                    SET precio = ? 
                    WHERE id = ?
                """, (precio['precio'], precio['id']))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error al actualizar precios: {e}")
            raise Exception(f"Error al actualizar precios: {e}")

    @staticmethod
    def obtener_precio_automatico(sabor: str, tamano: str) -> float:
        """Obtiene el precio automático para un sabor y tamaño"""
        try:
            conn = get_conn_normales()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT precio FROM PastelesPrecios 
                WHERE sabor = ? AND tamano = ?
            """, (sabor, tamano))

            resultado = cursor.fetchone()
            conn.close()

            if resultado:
                return float(resultado[0])
            return 0.0
        except Exception as e:
            logger.error(f"Error al obtener precio automático: {e}")
            return 0.0

    @staticmethod
    def registrar_pedido_cliente(pedido_data: Dict[str, Any]) -> bool:
        """Registra un nuevo pedido de cliente"""
        try:
            conn = get_conn_clientes()
            cursor = conn.cursor()

            # Calcular total
            total = pedido_data['precio'] * pedido_data['cantidad']

            cursor.execute("""
                INSERT INTO PastelesClientes 
                (color, sabor, tamano, cantidad, precio, total, sucursal, dedicatoria, detalles, fecha)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """, (
                pedido_data.get('color', ''),
                pedido_data['sabor'],
                pedido_data['tamano'],
                pedido_data['cantidad'],
                pedido_data['precio'],
                total,
                pedido_data['sucursal'],
                pedido_data.get('dedicatoria', ''),
                pedido_data.get('detalles', '')
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error al registrar pedido: {e}")
            raise Exception(f"Error al registrar pedido: {e}")

    @staticmethod
    def registrar_pastel_normal(pastel_data: Dict[str, Any]) -> bool:
        """Registra un nuevo pastel normal"""
        try:
            conn = get_conn_normales()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO PastelesNormales 
                (sabor, tamano, cantidad, precio, sucursal, detalles, fecha)
                VALUES (?, ?, ?, ?, ?, ?, GETDATE())
            """, (
                pastel_data['sabor'],
                pastel_data['tamano'],
                pastel_data['cantidad'],
                pastel_data['precio'],
                pastel_data['sucursal'],
                pastel_data.get('detalles', '')
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error al registrar pastel normal: {e}")
            raise Exception(f"Error al registrar pastel normal: {e}")

    @staticmethod
    def eliminar_pastel_normal(pastel_id: int) -> bool:
        """Elimina un pastel normal por ID"""
        try:
            conn = get_conn_normales()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM PastelesNormales WHERE id = ?", (pastel_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error al eliminar pastel normal: {e}")
            raise Exception(f"Error al eliminar pastel normal: {e}")

    @staticmethod
    def eliminar_pedido_cliente(pedido_id: int) -> bool:
        """Elimina un pedido de cliente por ID"""
        try:
            conn = get_conn_clientes()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM PastelesClientes WHERE id = ?", (pedido_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error al eliminar pedido cliente: {e}")
            raise Exception(f"Error al eliminar pedido cliente: {e}")

    @staticmethod
    def obtener_estadisticas(fecha_inicio: str = None, fecha_fin: str = None) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema"""
        try:
            stats = {}

            # Estadísticas pasteles normales
            conn_normales = get_conn_normales()
            cursor_normales = conn_normales.cursor()

            query_normales = "SELECT COUNT(*), SUM(cantidad), SUM(precio * cantidad) FROM PastelesNormales WHERE 1=1"
            params = []

            if fecha_inicio and fecha_fin:
                query_normales += " AND fecha BETWEEN ? AND ?"
                params.extend([fecha_inicio, fecha_fin])

            cursor_normales.execute(query_normales, params)
            result_normales = cursor_normales.fetchone()
            conn_normales.close()

            stats['normales_count'] = result_normales[0] or 0
            stats['normales_cantidad'] = result_normales[1] or 0
            stats['normales_ingresos'] = float(result_normales[2] or 0)

            # Estadísticas pedidos clientes
            conn_clientes = get_conn_clientes()
            cursor_clientes = conn_clientes.cursor()

            query_clientes = "SELECT COUNT(*), SUM(cantidad), SUM(total) FROM PastelesClientes WHERE 1=1"
            params_clientes = []

            if fecha_inicio and fecha_fin:
                query_clientes += " AND fecha BETWEEN ? AND ?"
                params_clientes.extend([fecha_inicio, fecha_fin])

            cursor_clientes.execute(query_clientes, params_clientes)
            result_clientes = cursor_clientes.fetchone()
            conn_clientes.close()

            stats['clientes_count'] = result_clientes[0] or 0
            stats['clientes_cantidad'] = result_clientes[1] or 0
            stats['clientes_ingresos'] = float(result_clientes[2] or 0)

            # Totales
            stats['total_pedidos'] = stats['normales_count'] + stats['clientes_count']
            stats['total_ingresos'] = stats['normales_ingresos'] + stats['clientes_ingresos']

            return stats

        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            return {}

# ==================== FUNCIONES DE CONEXIÓN ====================

def get_conn_normales():
    """Obtiene una conexión a la base de datos de Pasteles Normales"""
    try:
        conn_string = (
            f"DRIVER={DRIVER};"
            f"SERVER={SERVER};"
            f"DATABASE={DB_NORMALES};"
            "Trusted_Connection=yes;"
        )
        conn = pyodbc.connect(conn_string)
        logger.debug(f"Conexión exitosa a {DB_NORMALES}")
        return conn
    except pyodbc.Error as e:
        logger.error(f"Error al conectar a {DB_NORMALES}: {e}")
        raise

def get_conn_clientes():
    """Obtiene una conexión a la base de datos de Pedidos de Clientes"""
    try:
        conn_string = (
            f"DRIVER={DRIVER};"
            f"SERVER={SERVER};"
            f"DATABASE={DB_CLIENTES};"
            "Trusted_Connection=yes;"
        )
        conn = pyodbc.connect(conn_string)
        logger.debug(f"Conexión exitosa a {DB_CLIENTES}")
        return conn
    except pyodbc.Error as e:
        logger.error(f"Error al conectar a {DB_CLIENTES}: {e}")
        raise

def obtener_precio_db(sabor, tamano):
    """Obtiene el precio desde la base de datos MiPastel"""
    try:
        conn = get_conn_normales()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT precio FROM PastelesPrecios
            WHERE sabor = ? AND tamano = ?
        """, (sabor, tamano))
        row = cursor.fetchone()
        conn.close()
        return float(row[0]) if row else 0.0
    except Exception as e:
        logger.error(f"Error al obtener precio desde BD: {e}")
        return 0.0

# ==================== INICIALIZACIÓN DE BASE DE DATOS ====================

def inicializar_tabla_precios():
    """Inicializa la tabla de precios con los valores por defecto"""
    try:
        conn = get_conn_normales()
        cursor = conn.cursor()

        # Verificar si la tabla existe
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='PastelesPrecios' AND xtype='U')
            CREATE TABLE PastelesPrecios (
                id INT IDENTITY(1,1) PRIMARY KEY,
                sabor NVARCHAR(100) NOT NULL,
                tamano NVARCHAR(50) NOT NULL,
                precio DECIMAL(10,2) NOT NULL,
                UNIQUE(sabor, tamano)
            )
        """)

        # Insertar o actualizar precios
        for sabor, tamanos in PRECIOS_PASTELES.items():
            for tamano, precio in tamanos.items():
                cursor.execute("""
                    MERGE PastelesPrecios AS target
                    USING (VALUES (?, ?, ?)) AS source (sabor, tamano, precio)
                    ON target.sabor = source.sabor AND target.tamano = source.tamano
                    WHEN MATCHED THEN
                        UPDATE SET precio = source.precio
                    WHEN NOT MATCHED THEN
                        INSERT (sabor, tamano, precio) VALUES (source.sabor, source.tamano, source.precio);
                """, (sabor, tamano, precio))

        conn.commit()
        conn.close()
        print("✅ Tabla de precios inicializada correctamente")

    except Exception as e:
        print(f"❌ Error al inicializar tabla de precios: {e}")

def actualizar_esquema():
    """Actualiza el esquema de las bases de datos con los nuevos campos"""
    try:
        # Actualizar tabla PastelesNormales
        conn1 = get_conn_normales()
        cur1 = conn1.cursor()

        # Verificar si las columnas ya existen
        cur1.execute("""
            IF NOT EXISTS (SELECT * FROM sys.columns 
                          WHERE object_id = OBJECT_ID('PastelesNormales') 
                          AND name = 'sabor_personalizado')
            BEGIN
                ALTER TABLE PastelesNormales ADD sabor_personalizado NVARCHAR(100) NULL
            END
        """)

        cur1.execute("""
            IF NOT EXISTS (SELECT * FROM sys.columns 
                          WHERE object_id = OBJECT_ID('PastelesNormales') 
                          AND name = 'detalles')
            BEGIN
                ALTER TABLE PastelesNormales ADD detalles NVARCHAR(MAX) NULL
            END
        """)

        conn1.commit()
        conn1.close()
        print("✅ Esquema de PastelesNormales actualizado")

        # Actualizar tabla PastelesClientes
        conn2 = get_conn_clientes()
        cur2 = conn2.cursor()

        cur2.execute("""
            IF NOT EXISTS (SELECT * FROM sys.columns 
                          WHERE object_id = OBJECT_ID('PastelesClientes') 
                          AND name = 'sabor_personalizado')
            BEGIN
                ALTER TABLE PastelesClientes ADD sabor_personalizado NVARCHAR(100) NULL
            END
        """)

        cur2.execute("""
            IF NOT EXISTS (SELECT * FROM sys.columns 
                          WHERE object_id = OBJECT_ID('PastelesClientes') 
                          AND name = 'detalles')
            BEGIN
                ALTER TABLE PastelesClientes ADD detalles NVARCHAR(MAX) NULL
            END
        """)

        cur2.execute("""
            IF NOT EXISTS (SELECT * FROM sys.columns 
                          WHERE object_id = OBJECT_ID('PastelesClientes') 
                          AND name = 'dedicatoria')
            BEGIN
                ALTER TABLE PastelesClientes ADD dedicatoria NVARCHAR(MAX) NULL
            END
        """)

        conn2.commit()
        conn2.close()
        print("✅ Esquema de PastelesClientes actualizado")

    except Exception as e:
        print(f"❌ Error al actualizar esquema: {e}")

def test_connections():
    """Prueba las conexiones a ambas bases de datos"""
    try:
        print("🔍 Probando conexión a MiPastel...")
        conn1 = get_conn_normales()

        # Probar consulta simple
        cursor1 = conn1.cursor()
        cursor1.execute("SELECT COUNT(*) FROM PastelesNormales")
        count1 = cursor1.fetchone()[0]
        conn1.close()
        print(f"✅ Conexión exitosa a MiPastel (registros: {count1})")

        print("🔍 Probando conexión a MiPastel_Clientes...")
        conn2 = get_conn_clientes()

        # Probar consulta simple
        cursor2 = conn2.cursor()
        cursor2.execute("SELECT COUNT(*) FROM PastelesClientes")
        count2 = cursor2.fetchone()[0]
        conn2.close()
        print(f"✅ Conexión exitosa a MiPastel_Clientes (registros: {count2})")

        print("\n✅ Todas las conexiones funcionan correctamente")
        return True
    except Exception as e:
        print(f"\n❌ Error de conexión: {e}")
        print("\n💡 Verifica:")
        print("   1. SQL Server está corriendo")
        print("   2. Las bases de datos existen")
        print(f"   3. El servidor '{SERVER}' es correcto")
        print(f"   4. El driver '{DRIVER}' está instalado")
        return False

def inicializar_sistema():
    """Inicializa todo el sistema de base de datos"""
    print("🧁 Inicializando sistema de base de datos...")

    if test_connections():
        print("🔄 Actualizando esquema...")
        actualizar_esquema()

        print("💰 Inicializando tabla de precios...")
        inicializar_tabla_precios()

        print("✅ Sistema de base de datos inicializado correctamente")
        return True
    else:
        print("❌ No se pudo inicializar el sistema de base de datos")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧁 Mi Pastel - Sistema de Base de Datos v2.0")
    print("=" * 60)
    print()

    print("⚙️ Configuración actual:")
    print(f"   • Servidor: {SERVER}")
    print(f"   • Driver: {DRIVER}")
    print(f"   • BD Normales: {DB_NORMALES}")
    print(f"   • BD Clientes: {DB_CLIENTES}")
    print()

    # Inicializar sistema completo
    inicializar_sistema()

    print()
    print("=" * 60)