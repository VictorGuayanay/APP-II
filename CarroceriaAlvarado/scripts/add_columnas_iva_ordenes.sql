-- Script para agregar columnas de IVA a la tabla OrdenesTrabajo
USE CarroceriaAlvaradoDB;
GO

-- Agregar columna iva_porcentaje si no existe
IF NOT EXISTS (
    SELECT * FROM sys.columns 
    WHERE object_id = OBJECT_ID(N'dbo.OrdenesTrabajo') 
    AND name = 'iva_porcentaje'
)
BEGIN
    ALTER TABLE OrdenesTrabajo
    ADD iva_porcentaje INT DEFAULT 0 CHECK (iva_porcentaje BETWEEN 0 AND 20);
    PRINT 'Columna iva_porcentaje agregada.';
END
ELSE
BEGIN
    PRINT 'La columna iva_porcentaje ya existe.';
END
GO

-- Agregar columna subtotal_con_margen si no existe
IF NOT EXISTS (
    SELECT * FROM sys.columns 
    WHERE object_id = OBJECT_ID(N'dbo.OrdenesTrabajo') 
    AND name = 'subtotal_con_margen'
)
BEGIN
    ALTER TABLE OrdenesTrabajo
    ADD subtotal_con_margen DECIMAL(10, 2) DEFAULT 0.00;
    PRINT 'Columna subtotal_con_margen agregada.';
END
ELSE
BEGIN
    PRINT 'La columna subtotal_con_margen ya existe.';
END
GO

-- Agregar columna monto_iva si no existe
IF NOT EXISTS (
    SELECT * FROM sys.columns 
    WHERE object_id = OBJECT_ID(N'dbo.OrdenesTrabajo') 
    AND name = 'monto_iva'
)
BEGIN
    ALTER TABLE OrdenesTrabajo
    ADD monto_iva DECIMAL(10, 2) DEFAULT 0.00;
    PRINT 'Columna monto_iva agregada.';
END
ELSE
BEGIN
    PRINT 'La columna monto_iva ya existe.';
END
GO

-- Verificar estructura actualizada
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'OrdenesTrabajo'
AND COLUMN_NAME IN ('subtotal_materiales', 'margen_ganancia', 'iva_porcentaje', 'subtotal_con_margen', 'monto_iva', 'total_orden')
ORDER BY ORDINAL_POSITION;
GO

PRINT 'Actualización de columnas de IVA completada.';
GO
