-- =====================================================
-- Script: Crear Tabla Unidades_de_Medida
-- Descripción: Crea la tabla de unidades de medida y 
--              agrega datos iniciales comunes
-- Fecha: 2025-12-08
-- =====================================================

USE CarroceriaAlvaradoDB;
GO

-- 1. Crear tabla Unidades_de_Medida
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Unidades_de_Medida')
BEGIN
    CREATE TABLE Unidades_de_Medida (
        id_unidad INT IDENTITY(1,1) PRIMARY KEY,
        nombre_unidad NVARCHAR(50) NOT NULL UNIQUE,
        abreviatura NVARCHAR(10) NOT NULL,
        descripcion NVARCHAR(200),
        estado NVARCHAR(20) DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo')),
        fecha_creacion DATETIME DEFAULT GETDATE()
    );
    PRINT 'Tabla Unidades_de_Medida creada exitosamente.';
END
ELSE
BEGIN
    PRINT 'La tabla Unidades_de_Medida ya existe.';
END
GO

-- 2. Insertar unidades de medida comunes
IF NOT EXISTS (SELECT * FROM Unidades_de_Medida WHERE nombre_unidad = 'Unidad')
BEGIN
    INSERT INTO Unidades_de_Medida (nombre_unidad, abreviatura, descripcion) VALUES
    ('Unidad', 'Ud', 'Unidad individual'),
    ('Kilogramo', 'kg', 'Unidad de masa'),
    ('Gramo', 'g', 'Unidad de masa'),
    ('Litro', 'L', 'Unidad de volumen'),
    ('Mililitro', 'ml', 'Unidad de volumen'),
    ('Metro', 'm', 'Unidad de longitud'),
    ('Centímetro', 'cm', 'Unidad de longitud'),
    ('Metro cuadrado', 'm²', 'Unidad de área'),
    ('Metro cúbico', 'm³', 'Unidad de volumen'),
    ('Caja', 'Caja', 'Empaque de múltiples unidades'),
    ('Paquete', 'Paq', 'Empaque de múltiples unidades'),
    ('Galón', 'Gal', 'Unidad de volumen'),
    ('Pieza', 'Pza', 'Unidad individual');
    
    PRINT 'Unidades de medida insertadas exitosamente.';
END
ELSE
BEGIN
    PRINT 'Las unidades de medida ya existen.';
END
GO

-- 3. Verificar datos insertados
SELECT 
    id_unidad,
    nombre_unidad,
    abreviatura,
    descripcion,
    estado
FROM Unidades_de_Medida
ORDER BY id_unidad;
GO

PRINT '==============================================';
PRINT 'Script completado exitosamente.';
PRINT 'Total de unidades creadas: ' + CAST((SELECT COUNT(*) FROM Unidades_de_Medida) AS NVARCHAR(10));
PRINT '==============================================';
GO
