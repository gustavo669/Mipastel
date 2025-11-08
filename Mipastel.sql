-- =============================================
-- SISTEMA MI PASTEL - BASE DE DATOS COMPLETA
-- =============================================

-- Crear base de datos para Pasteles Normales
CREATE DATABASE MiPastel;
GO

USE MiPastel;
GO

-- Tabla para Pasteles Normales
CREATE TABLE PastelesNormales (
    id INT IDENTITY(10000, 1) PRIMARY KEY,
    sabor NVARCHAR(50) NOT NULL,
    tamano NVARCHAR(50) NOT NULL, 
    cantidad INT NOT NULL CHECK (cantidad > 0),
    precio DECIMAL(10,2) NOT NULL CHECK (precio >= 0),
    total DECIMAL(10,2) NOT NULL DEFAULT 0,
    sucursal NVARCHAR(100) NOT NULL,
    fecha DATETIME2 DEFAULT GETDATE(),
    detalles NVARCHAR(MAX) NULL,
    sabor_personalizado NVARCHAR(100) NULL
);
GO

-- Tabla de precios
CREATE TABLE PastelesPrecios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    sabor NVARCHAR(100) NOT NULL,
    tamano NVARCHAR(50) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    UNIQUE(sabor, tamano)
);
GO

-- Insertar precios
INSERT INTO PastelesPrecios (sabor, tamano, precio) VALUES
-- Fresas
('Fresas', 'Mini', 60.00),
('Fresas', 'Peque�o', 85.00),
('Fresas', 'Mediano', 125.00),
('Fresas', 'Grande', 155.00),
('Fresas', 'Extra grande', 185.00),
('Fresas', 'Media plancha', 325.00),

-- Frutas
('Frutas', 'Mini', 65.00),
('Frutas', 'Peque�o', 90.00),
('Frutas', 'Mediano', 130.00),
('Frutas', 'Grande', 160.00),
('Frutas', 'Extra grande', 195.00),
('Frutas', 'Media plancha', 335.00),

-- Chocolate
('Chocolate', 'Mini', 70.00),
('Chocolate', 'Peque�o', 105.00),
('Chocolate', 'Mediano', 140.00),
('Chocolate', 'Grande', 185.00),
('Chocolate', 'Extra grande', 245.00),
('Chocolate', 'Media plancha', 400.00),

-- Selva negra
('Selva negra', 'Mini', 65.00),
('Selva negra', 'Peque�o', 100.00),
('Selva negra', 'Mediano', 130.00),
('Selva negra', 'Grande', 180.00),
('Selva negra', 'Extra grande', 240.00),
('Selva negra', 'Media plancha', 390.00),

-- Oreo
('Oreo', 'Mini', 70.00),
('Oreo', 'Peque�o', 105.00),
('Oreo', 'Mediano', 140.00),
('Oreo', 'Grande', 185.00),
('Oreo', 'Extra grande', 245.00),
('Oreo', 'Media plancha', 400.00),

-- Chocofresa
('Chocofresa', 'Mini', 70.00),
('Chocofresa', 'Peque�o', 105.00),
('Chocofresa', 'Mediano', 140.00),
('Chocofresa', 'Grande', 185.00),
('Chocofresa', 'Extra grande', 245.00),
('Chocofresa', 'Media plancha', 400.00),

-- Tres Leches
('Tres Leches', 'Mini', 70.00),
('Tres Leches', 'Peque�o', 105.00),
('Tres Leches', 'Mediano', 140.00),
('Tres Leches', 'Grande', 185.00),
('Tres Leches', 'Extra grande', 245.00),
('Tres Leches', 'Media plancha', 400.00),

-- Tres leches con Ar�ndanos
('Tres leches con Ar�ndanos', 'Mini', 75.00),
('Tres leches con Ar�ndanos', 'Peque�o', 110.00),
('Tres leches con Ar�ndanos', 'Mediano', 145.00),
('Tres leches con Ar�ndanos', 'Grande', 190.00),
('Tres leches con Ar�ndanos', 'Extra grande', 255.00),
('Tres leches con Ar�ndanos', 'Media plancha', 420.00),

-- Fiesta
('Fiesta', 'Mini', 55.00),
('Fiesta', 'Peque�o', 70.00),
('Fiesta', 'Mediano', 100.00),
('Fiesta', 'Grande', 125.00),
('Fiesta', 'Extra grande', 175.00),
('Fiesta', 'Media plancha', 315.00);

-- =============================================
-- BASE DE DATOS PARA CLIENTES
-- =============================================

-- Crear base de datos para Pedidos de Clientes
CREATE DATABASE MiPastel_Clientes;
GO

USE MiPastel_Clientes;
GO

-- Tabla para Pedidos de Clientes
CREATE TABLE PastelesClientes (
    id INT IDENTITY(10000, 1) PRIMARY KEY,
    color NVARCHAR(50) NULL,
    sabor NVARCHAR(50) NOT NULL,
    tamano NVARCHAR(50) NOT NULL,
    cantidad INT NOT NULL CHECK (cantidad > 0),
    precio DECIMAL(10,2) NOT NULL CHECK (precio >= 0),
    total DECIMAL(10,2) NOT NULL DEFAULT 0,
    sucursal NVARCHAR(100) NOT NULL,
    fecha DATETIME2 DEFAULT GETDATE(),
    dedicatoria NVARCHAR(MAX) NULL,
    detalles NVARCHAR(MAX) NULL,
    sabor_personalizado NVARCHAR(100) NULL,
    foto_path NVARCHAR(500) NULL,
    fecha_entrega DATETIME2 NULL
);
GO

-- Trigger para el total
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
