-- ============================================================
-- Script: Índices de optimización - Carrocería Alvarado
-- Base de Datos: SQL Server (CarroceriaAlvaradoDB)
-- Fecha: 2026-04-11
-- Descripción: Índices en columnas frecuentemente consultadas
--              para mejorar el rendimiento en producción
-- ============================================================

USE CarroceriaAlvaradoDB;
GO

-- ============================================================
-- TABLA: Usuarios
-- ============================================================
-- El login busca por username y email constantemente
-- (UNIQUE ya crea un índice implícito, pero lo explicitamos)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_usuarios_username' AND object_id = OBJECT_ID('Usuarios'))
    CREATE INDEX idx_usuarios_username ON Usuarios(username);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_usuarios_email' AND object_id = OBJECT_ID('Usuarios'))
    CREATE INDEX idx_usuarios_email ON Usuarios(email);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_usuarios_estado' AND object_id = OBJECT_ID('Usuarios'))
    CREATE INDEX idx_usuarios_estado ON Usuarios(estado, bloqueado);
GO

-- ============================================================
-- TABLA: OrdenesTrabajo
-- ============================================================
-- El dashboard filtra órdenes por estado frecuentemente
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_ordenes_estado' AND object_id = OBJECT_ID('OrdenesTrabajo'))
    CREATE INDEX idx_ordenes_estado ON OrdenesTrabajo(estado);
GO

-- La visión general busca las más recientes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_ordenes_fecha_inicio' AND object_id = OBJECT_ID('OrdenesTrabajo'))
    CREATE INDEX idx_ordenes_fecha_inicio ON OrdenesTrabajo(fecha_inicio DESC);
GO

-- El dashboard de vencimiento filtra por fecha_fin
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_ordenes_fecha_fin' AND object_id = OBJECT_ID('OrdenesTrabajo'))
    CREATE INDEX idx_ordenes_fecha_fin ON OrdenesTrabajo(fecha_fin);
GO

-- ============================================================
-- TABLA: Materiales
-- ============================================================
-- Las alertas de stock bajo consultan cantidad constantemente
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_materiales_cantidad' AND object_id = OBJECT_ID('Materiales'))
    CREATE INDEX idx_materiales_cantidad ON Materiales(cantidad);
GO

-- Búsquedas por código de material
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_materiales_codigo' AND object_id = OBJECT_ID('Materiales'))
    CREATE INDEX idx_materiales_codigo ON Materiales(codigo_material);
GO

-- ============================================================
-- TABLA: ComprobantesPago
-- ============================================================
-- Los comprobantes se buscan por orden
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_comprobantes_orden' AND object_id = OBJECT_ID('ComprobantesPago'))
    CREATE INDEX idx_comprobantes_orden ON ComprobantesPago(id_orden);
GO

-- Filtro por estado_pago en reportes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_comprobantes_estado' AND object_id = OBJECT_ID('ComprobantesPago'))
    CREATE INDEX idx_comprobantes_estado ON ComprobantesPago(estado_pago);
GO

-- ============================================================
-- TABLA: Ventas_Directas
-- ============================================================
-- Los reportes filtran por fecha
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_ventas_fecha' AND object_id = OBJECT_ID('Ventas_Directas'))
    CREATE INDEX idx_ventas_fecha ON Ventas_Directas(fecha_venta DESC);
GO

PRINT 'Índices creados o verificados correctamente.';
GO
