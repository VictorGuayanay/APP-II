-- Script para verificar y agregar columnas financieras a la tabla OrdenesTrabajo
USE CarroceriaAlvaradoDB;
GO

-- Verificar estructura actual de OrdenesTrabajo
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'OrdenesTrabajo'
ORDER BY ORDINAL_POSITION;
GO

-- Agregar columnas financieras si no existen
IF NOT EXISTS (
    SELECT * FROM sys.columns 
    WHERE object_id = OBJECT_ID(N'dbo.OrdenesTrabajo') 
    AND name = 'subtotal_materiales'
)
BEGIN
    ALTER TABLE OrdenesTrabajo
    ADD subtotal_materiales DECIMAL(10, 2) DEFAULT 0.00;
    PRINT 'Columna subtotal_materiales agregada.';
END
ELSE
BEGIN
    PRINT 'La columna subtotal_materiales ya existe.';
END
GO

IF NOT EXISTS (
    SELECT * FROM sys.columns 
    WHERE object_id = OBJECT_ID(N'dbo.OrdenesTrabajo') 
    AND name = 'margen_ganancia'
)
BEGIN
    ALTER TABLE OrdenesTrabajo
    ADD margen_ganancia INT DEFAULT 20 CHECK (margen_ganancia BETWEEN 5 AND 50);
    PRINT 'Columna margen_ganancia agregada.';
END
ELSE
BEGIN
    PRINT 'La columna margen_ganancia ya existe.';
END
GO

IF NOT EXISTS (
    SELECT * FROM sys.columns 
    WHERE object_id = OBJECT_ID(N'dbo.OrdenesTrabajo') 
    AND name = 'total_orden'
)
BEGIN
    ALTER TABLE OrdenesTrabajo
    ADD total_orden DECIMAL(10, 2) DEFAULT 0.00;
    PRINT 'Columna total_orden agregada.';
END
ELSE
BEGIN
    PRINT 'La columna total_orden ya existe.';
END
GO

PRINT 'Verificación y actualización de columnas financieras completada.';
GO
