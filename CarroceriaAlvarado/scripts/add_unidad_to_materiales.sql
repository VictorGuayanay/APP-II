-- =====================================================
-- Script: Agregar Unidad de Medida a Materiales
-- Descripción: Agrega columna id_unidad a tabla Materiales
--              y crea relación con Unidades_de_Medida
-- Fecha: 2025-12-08
-- =====================================================

USE CarroceriaAlvaradoDB;
GO

-- 1. Verificar que existe la tabla Unidades_de_Medida
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Unidades_de_Medida')
BEGIN
    PRINT 'ERROR: La tabla Unidades_de_Medida no existe.';
    PRINT 'Por favor, ejecute primero el script create_unidades_medida.sql';
    RETURN;
END
GO

-- 2. Agregar columna id_unidad a Materiales si no existe
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('Materiales') AND name = 'id_unidad')
BEGIN
    ALTER TABLE Materiales
    ADD id_unidad INT NULL;
    
    PRINT 'Columna id_unidad agregada a tabla Materiales.';
END
ELSE
BEGIN
    PRINT 'La columna id_unidad ya existe en la tabla Materiales.';
END
GO

-- 3. Crear clave foránea si no existe
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_Materiales_Unidades')
BEGIN
    ALTER TABLE Materiales
    ADD CONSTRAINT FK_Materiales_Unidades
    FOREIGN KEY (id_unidad) REFERENCES Unidades_de_Medida(id_unidad);
    
    PRINT 'Clave foránea FK_Materiales_Unidades creada exitosamente.';
END
ELSE
BEGIN
    PRINT 'La clave foránea FK_Materiales_Unidades ya existe.';
END
GO

-- 4. Migrar datos existentes: Asignar unidad "Unidad" por defecto
DECLARE @id_unidad_default INT;
SELECT @id_unidad_default = id_unidad FROM Unidades_de_Medida WHERE nombre_unidad = 'Unidad';

IF @id_unidad_default IS NOT NULL
BEGIN
    UPDATE Materiales
    SET id_unidad = @id_unidad_default
    WHERE id_unidad IS NULL;
    
    DECLARE @materiales_actualizados INT = @@ROWCOUNT;
    PRINT 'Materiales actualizados con unidad por defecto: ' + CAST(@materiales_actualizados AS NVARCHAR(10));
END
ELSE
BEGIN
    PRINT 'ADVERTENCIA: No se encontró la unidad "Unidad" para asignar por defecto.';
END
GO

-- 5. Verificar migración
SELECT 
    m.id_material,
    m.nombre,
    m.cantidad,
    u.nombre_unidad,
    u.abreviatura
FROM Materiales m
LEFT JOIN Unidades_de_Medida u ON m.id_unidad = u.id_unidad
ORDER BY m.id_material;
GO

-- 6. Estadísticas
PRINT '==============================================';
PRINT 'Estadísticas de migración:';
PRINT 'Total de materiales: ' + CAST((SELECT COUNT(*) FROM Materiales) AS NVARCHAR(10));
PRINT 'Materiales con unidad asignada: ' + CAST((SELECT COUNT(*) FROM Materiales WHERE id_unidad IS NOT NULL) AS NVARCHAR(10));
PRINT 'Materiales sin unidad: ' + CAST((SELECT COUNT(*) FROM Materiales WHERE id_unidad IS NULL) AS NVARCHAR(10));
PRINT '==============================================';
GO

PRINT 'Script completado exitosamente.';
GO
