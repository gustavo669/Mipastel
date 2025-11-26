CREATE DATABASE MiPastel;
GO

USE MiPastel;
GO

CREATE TABLE PastelesNormales (
                                  id INT IDENTITY(10000, 1) PRIMARY KEY,
                                  sabor NVARCHAR(50) NOT NULL,
                                  tamano NVARCHAR(50) NOT NULL,
                                  cantidad INT NOT NULL CHECK (cantidad > 0),
                                  precio DECIMAL(10,2) NOT NULL CHECK (precio >= 0),
                                  total DECIMAL(10,2) NOT NULL DEFAULT 0,
                                  sucursal NVARCHAR(100) NOT NULL,
                                  fecha DATETIME2 DEFAULT GETDATE(),
                                  fecha_entrega DATETIME2 NULL,
                                  detalles NVARCHAR(MAX) NULL,
                                  sabor_personalizado NVARCHAR(100) NULL,

                                  fecha_formateada AS FORMAT(fecha, 'dd-MM-yyyy'),
                                  fecha_hora_formateada AS FORMAT(fecha, 'dd-MM-yyyy HH:mm'),
                                  fecha_entrega_formateada AS FORMAT(fecha_entrega, 'dd-MM-yyyy'),
                                  fecha_entrega_hora_formateada AS FORMAT(fecha_entrega, 'dd-MM-yyyy HH:mm')
);
GO

CREATE INDEX idx_fecha_sucursal ON PastelesNormales(fecha, sucursal);
GO

CREATE TRIGGER TR_CalcularTotalNormal
    ON PastelesNormales
    AFTER INSERT, UPDATE
    AS
BEGIN
    SET NOCOUNT ON;

    UPDATE pn
    SET total = i.cantidad * i.precio
    FROM PastelesNormales pn
             INNER JOIN inserted i ON pn.id = i.id
    WHERE i.cantidad > 0;
END;
GO

CREATE TABLE PastelesPrecios (
                                 id INT IDENTITY(1,1) PRIMARY KEY,
                                 sabor NVARCHAR(100) NOT NULL,
                                 tamano NVARCHAR(50) NOT NULL,
                                 precio DECIMAL(10,2) NOT NULL CHECK (precio > 0),
                                 UNIQUE(sabor, tamano)
);
GO

INSERT INTO PastelesPrecios (sabor, tamano, precio) VALUES
                                                        ('Fresas', 'Mini', 60.00),
                                                        ('Fresas', 'Pequeño', 85.00),
                                                        ('Fresas', 'Mediano', 125.00),
                                                        ('Fresas', 'Grande', 155.00),
                                                        ('Fresas', 'Extra grande', 185.00),
                                                        ('Fresas', 'Media plancha', 325.00),
                                                        ('Frutas', 'Mini', 65.00),
                                                        ('Frutas', 'Pequeño', 90.00),
                                                        ('Frutas', 'Mediano', 130.00),
                                                        ('Frutas', 'Grande', 160.00),
                                                        ('Frutas', 'Extra grande', 195.00),
                                                        ('Frutas', 'Media plancha', 335.00),
                                                        ('Chocolate', 'Mini', 70.00),
                                                        ('Chocolate', 'Pequeño', 105.00),
                                                        ('Chocolate', 'Mediano', 140.00),
                                                        ('Chocolate', 'Grande', 185.00),
                                                        ('Chocolate', 'Extra grande', 245.00),
                                                        ('Chocolate', 'Media plancha', 400.00),
                                                        ('Selva negra', 'Mini', 65.00),
                                                        ('Selva negra', 'Pequeño', 100.00),
                                                        ('Selva negra', 'Mediano', 130.00),
                                                        ('Selva negra', 'Grande', 180.00),
                                                        ('Selva negra', 'Extra grande', 240.00),
                                                        ('Selva negra', 'Media plancha', 390.00),
                                                        ('Oreo', 'Mini', 70.00),
                                                        ('Oreo', 'Pequeño', 105.00),
                                                        ('Oreo', 'Mediano', 140.00),
                                                        ('Oreo', 'Grande', 185.00),
                                                        ('Oreo', 'Extra grande', 245.00),
                                                        ('Oreo', 'Media plancha', 400.00),
                                                        ('Chocofresa', 'Mini', 70.00),
                                                        ('Chocofresa', 'Pequeño', 105.00),
                                                        ('Chocofresa', 'Mediano', 140.00),
                                                        ('Chocofresa', 'Grande', 185.00),
                                                        ('Chocofresa', 'Extra grande', 245.00),
                                                        ('Chocofresa', 'Media plancha', 400.00),
                                                        ('Tres Leches', 'Mini', 70.00),
                                                        ('Tres Leches', 'Pequeño', 105.00),
                                                        ('Tres Leches', 'Mediano', 140.00),
                                                        ('Tres Leches', 'Grande', 185.00),
                                                        ('Tres Leches', 'Extra grande', 245.00),
                                                        ('Tres Leches', 'Media plancha', 400.00),
                                                        ('Tres leches con Arándanos', 'Mini', 75.00),
                                                        ('Tres leches con Arándanos', 'Pequeño', 110.00),
                                                        ('Tres leches con Arándanos', 'Mediano', 145.00),
                                                        ('Tres leches con Arándanos', 'Grande', 190.00),
                                                        ('Tres leches con Arándanos', 'Extra grande', 255.00),
                                                        ('Tres leches con Arándanos', 'Media plancha', 420.00),
                                                        ('Fiesta', 'Mini', 55.00),
                                                        ('Fiesta', 'Pequeño', 70.00),
                                                        ('Fiesta', 'Mediano', 100.00),
                                                        ('Fiesta', 'Grande', 125.00),
                                                        ('Fiesta', 'Extra grande', 175.00),
                                                        ('Fiesta', 'Media plancha', 315.00);
GO

CREATE DATABASE MiPastel_Clientes;
GO

USE MiPastel_Clientes;
GO

CREATE TABLE PastelesClientes (
                                  id INT IDENTITY(10000, 1) PRIMARY KEY,
                                  color NVARCHAR(50) NULL,
                                  sabor NVARCHAR(50) NOT NULL,
                                  tamano NVARCHAR(50) NOT NULL,
                                  cantidad INT NOT NULL CHECK (cantidad > 0),
                                  precio DECIMAL(10,2) NOT NULL CHECK (precio > 0),
                                  total DECIMAL(10,2) NOT NULL DEFAULT 0,
                                  sucursal NVARCHAR(100) NOT NULL,
                                  fecha DATETIME2 DEFAULT GETDATE(),
                                  dedicatoria NVARCHAR(MAX) NULL,
                                  detalles NVARCHAR(MAX) NULL,
                                  sabor_personalizado NVARCHAR(100) NULL,
                                  foto_path NVARCHAR(500) NULL,
                                  fecha_entrega DATETIME2 NULL,

                                  fecha_formateada AS FORMAT(fecha, 'dd-MM-yyyy'),
                                  fecha_hora_formateada AS FORMAT(fecha, 'dd-MM-yyyy HH:mm'),
                                  fecha_entrega_formateada AS FORMAT(fecha_entrega, 'dd-MM-yyyy'),
                                  fecha_entrega_hora_formateada AS FORMAT(fecha_entrega, 'dd-MM-yyyy HH:mm')
);
GO

CREATE INDEX idx_fecha_sucursal_clientes ON PastelesClientes(fecha, sucursal);
GO

CREATE TRIGGER TR_CalcularTotalCliente
    ON PastelesClientes
    AFTER INSERT, UPDATE
    AS
BEGIN
    SET NOCOUNT ON;

    UPDATE pc
    SET total = i.cantidad * i.precio
    FROM PastelesClientes pc
             INNER JOIN inserted i ON pc.id = i.id
    WHERE i.cantidad > 0;
END;
GO
