-- =====================================================
-- Script: Agregar Sistema de Precios de Compra y Venta
-- Fecha: 2025-12-08
-- Descripción: Agrega columnas para precio de compra, 
--              precio de venta y porcentaje de ganancia
-- =====================================================

USE CarroceriaAlvaradoDB;
GO

-- Verificar si las columnas ya existen antes de agregarlas
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('Materiales') AND name = 'precio_compra')
BEGIN
    ALTER TABLE Materiales
    ADD precio_compra DECIMAL(10, 2) NULL;
    PRINT 'Columna precio_compra agregada exitosamente.';
END
ELSE
BEGIN
    PRINT 'Columna precio_compra ya existe.';
END
GO

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('Materiales') AND name = 'precio_venta')
BEGIN
    ALTER TABLE Materiales
    ADD precio_venta DECIMAL(10, 2) NULL;
    PRINT 'Columna precio_venta agregada exitosamente.';
END
ELSE
BEGIN
    PRINT 'Columna precio_venta ya existe.';
END
GO

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('Materiales') AND name = 'porcentaje_ganancia')
BEGIN
    ALTER TABLE Materiales
    ADD porcentaje_ganancia INT NULL;
    PRINT 'Columna porcentaje_ganancia agregada exitosamente.';
END
ELSE
BEGIN
    PRINT 'Columna porcentaje_ganancia ya existe.';
END
GO

-- Migrar datos existentes: precio_unitario -> precio_compra
-- Usar 20% como porcentaje de ganancia por defecto
UPDATE Materiales
SET precio_compra = precio_unitario,
    porcentaje_ganancia = 20,
    precio_venta = ROUND(precio_unitario * 1.20, 2)
WHERE precio_compra IS NULL;
GO

PRINT 'Datos migrados exitosamente.';
PRINT 'Verificando resultados...';
GO

-- Verificar la migración
SELECT TOP 5
    id_material,
    nombre,
    precio_unitario AS precio_unitario_antiguo,
    precio_compra,
    porcentaje_ganancia,
    precio_venta,
    ROUND(precio_compra * (1 + CAST(porcentaje_ganancia AS DECIMAL) / 100), 2) AS precio_venta_calculado
FROM Materiales
ORDER BY id_material;
GO

PRINT '=====================================================';
PRINT 'Migración completada exitosamente.';
PRINT 'NOTA: precio_unitario se mantiene por compatibilidad.';
PRINT 'Se sincronizará automáticamente con precio_compra.';
PRINT '=====================================================';
GO
