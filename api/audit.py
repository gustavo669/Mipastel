import json
from typing import Dict, Any, Optional
from config.database import db_pool_normales, db_pool_clientes
from utils.logger import logger

def registrar_auditoria(
    usuario: str,
    accion: str,
    tabla: str,
    id_registro: int,
    datos_antes: Optional[Dict[str, Any]] = None,
    datos_despues: Optional[Dict[str, Any]] = None
):
    query = """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Auditoria')
        BEGIN
            CREATE TABLE Auditoria (
                id INT IDENTITY(1,1) PRIMARY KEY,
                usuario NVARCHAR(100),
                accion NVARCHAR(50),
                tabla NVARCHAR(100),
                id_registro INT,
                datos_antes NVARCHAR(MAX),
                datos_despues NVARCHAR(MAX),
                fecha DATETIME DEFAULT GETDATE()
            )
        END
        
        INSERT INTO Auditoria (usuario, accion, tabla, id_registro, datos_antes, datos_despues)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    
    try:
        db_pool = db_pool_normales if tabla in ['PastelesNormales', 'PastelesPrecios'] else db_pool_clientes
        
        with db_pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                usuario,
                accion,
                tabla,
                id_registro,
                json.dumps(datos_antes) if datos_antes else None,
                json.dumps(datos_despues) if datos_despues else None
            ))
            conn.commit()
            logger.info(f"Auditoría registrada: {usuario} - {accion} - {tabla} #{id_registro}")
    except Exception as e:
        logger.error(f"Error al registrar auditoría: {e}", exc_info=True)
