-- Script para agregar columnas ubicacion y numero_factura a la tabla Materiales
-- Ejecutar este script en SQL Server Management Studio o Azure Data Studio

USE [nombre_de_tu_base_de_datos]; -- Reemplaza con el nombre de tu base de datos
GO

-- Agregar columna ubicacion
IF NOT EXISTS (
    SELECT * FROM sys.columns 
    WHERE object_id = OBJECT_ID(N'[dbo].[Materiales]') 
    AND name = 'ubicacion'
)
BEGIN
    ALTER TABLE [dbo].[Materiales]
    ADD ubicacion NVARCHAR(100) NULL;
    PRINT 'Columna ubicacion agregada exitosamente';
END
ELSE
BEGIN
    PRINT 'La columna ubicacion ya existe';
END
GO

-- Agregar columna numero_factura
IF NOT EXISTS (
    SELECT * FROM sys.columns 
    WHERE object_id = OBJECT_ID(N'[dbo].[Materiales]') 
    AND name = 'numero_factura'
)
BEGIN
    ALTER TABLE [dbo].[Materiales]
    ADD numero_factura NVARCHAR(50) NULL;
    PRINT 'Columna numero_factura agregada exitosamente';
END
ELSE
BEGIN
    PRINT 'La columna numero_factura ya existe';
END
GO

-- Verificar que las columnas se agregaron correctamente
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'Materiales'
AND COLUMN_NAME IN ('ubicacion', 'numero_factura');
GO
