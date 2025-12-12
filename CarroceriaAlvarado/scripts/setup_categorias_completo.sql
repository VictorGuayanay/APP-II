-- Script CONSOLIDADO para crear sistema de categorías
-- Base de datos: CarroceriaAlvaradoDB
-- VERSIÓN CORREGIDA - Ejecutar este script

USE CarroceriaAlvaradoDB;
GO

-- ========================================
-- 1. CREAR TABLA CategoriaMateriales (si no existe)
-- ========================================

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'CategoriaMateriales')
BEGIN
    CREATE TABLE CategoriaMateriales (
        id_categoria INT PRIMARY KEY IDENTITY(1,1),
        codigo_prefijo VARCHAR(10) NOT NULL UNIQUE,
        nombre_categoria VARCHAR(100) NOT NULL,
        descripcion TEXT,
        estado BIT DEFAULT 1,
        fecha_creacion DATETIME DEFAULT GETDATE()
    );
    
    CREATE INDEX idx_codigo_prefijo ON CategoriaMateriales(codigo_prefijo);
    CREATE INDEX idx_estado_categoria ON CategoriaMateriales(estado);
    
    PRINT '✓ Tabla CategoriaMateriales creada';
END
ELSE
BEGIN
    PRINT '✓ Tabla CategoriaMateriales ya existe';
END
GO

-- ========================================
-- 2. MODIFICAR TABLA Materiales
-- ========================================

-- Agregar columna id_categoria
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('Materiales') AND name = 'id_categoria')
BEGIN
    ALTER TABLE Materiales ADD id_categoria INT NULL;
    PRINT '✓ Columna id_categoria agregada';
END
ELSE
BEGIN
    PRINT '✓ Columna id_categoria ya existe';
END
GO

-- Agregar columna codigo_material
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('Materiales') AND name = 'codigo_material')
BEGIN
    ALTER TABLE Materiales ADD codigo_material VARCHAR(20) NULL;
    PRINT '✓ Columna codigo_material agregada';
END
ELSE
BEGIN
    PRINT '✓ Columna codigo_material ya existe';
END
GO

-- Crear Foreign Key
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_Materiales_Categoria')
BEGIN
    ALTER TABLE Materiales
    ADD CONSTRAINT FK_Materiales_Categoria 
    FOREIGN KEY (id_categoria) REFERENCES CategoriaMateriales(id_categoria);
    PRINT '✓ Foreign Key creada';
END
ELSE
BEGIN
    PRINT '✓ Foreign Key ya existe';
END
GO

-- Crear constraint UNIQUE para codigo_material (SOLO SI NO EXISTE)
IF NOT EXISTS (
    SELECT * FROM sys.key_constraints 
    WHERE name = 'UQ_Materiales_Codigo' 
    AND parent_object_id = OBJECT_ID('Materiales')
)
BEGIN
    ALTER TABLE Materiales
    ADD CONSTRAINT UQ_Materiales_Codigo UNIQUE (codigo_material);
    PRINT '✓ Constraint UNIQUE creado';
END
ELSE
BEGIN
    PRINT '✓ Constraint UNIQUE ya existe';
END
GO

-- Crear índices
IF NOT EXISTS (
    SELECT * FROM sys.indexes 
    WHERE name = 'idx_codigo_material' 
    AND object_id = OBJECT_ID('Materiales')
)
BEGIN
    CREATE INDEX idx_codigo_material ON Materiales(codigo_material);
    PRINT '✓ Índice idx_codigo_material creado';
END
ELSE
BEGIN
    PRINT '✓ Índice idx_codigo_material ya existe';
END
GO

IF NOT EXISTS (
    SELECT * FROM sys.indexes 
    WHERE name = 'idx_id_categoria_material' 
    AND object_id = OBJECT_ID('Materiales')
)
BEGIN
    CREATE INDEX idx_id_categoria_material ON Materiales(id_categoria);
    PRINT '✓ Índice idx_id_categoria_material creado';
END
ELSE
BEGIN
    PRINT '✓ Índice idx_id_categoria_material ya existe';
END
GO

-- ========================================
-- 3. INSERTAR CATEGORÍAS INICIALES
-- ========================================

DECLARE @count INT;

-- ACA
SELECT @count = COUNT(*) FROM CategoriaMateriales WHERE codigo_prefijo = 'ACA';
IF @count = 0
BEGIN
    INSERT INTO CategoriaMateriales (codigo_prefijo, nombre_categoria, descripcion, estado)
    VALUES ('ACA', 'Accesorios', 'Accesorios varios para vehículos', 1);
    PRINT '✓ Categoría ACA insertada';
END

-- ACC
SELECT @count = COUNT(*) FROM CategoriaMateriales WHERE codigo_prefijo = 'ACC';
IF @count = 0
BEGIN
    INSERT INTO CategoriaMateriales (codigo_prefijo, nombre_categoria, descripcion, estado)
    VALUES ('ACC', 'Accesorios Complementarios', 'Complementos y accesorios adicionales', 1);
    PRINT '✓ Categoría ACC insertada';
END

-- AIR
SELECT @count = COUNT(*) FROM CategoriaMateriales WHERE codigo_prefijo = 'AIR';
IF @count = 0
BEGIN
    INSERT INTO CategoriaMateriales (codigo_prefijo, nombre_categoria, descripcion, estado)
    VALUES ('AIR', 'Aire y Neumáticos', 'Componentes de aire y neumáticos', 1);
    PRINT '✓ Categoría AIR insertada';
END

-- CAR
SELECT @count = COUNT(*) FROM CategoriaMateriales WHERE codigo_prefijo = 'CAR';
IF @count = 0
BEGIN
    INSERT INTO CategoriaMateriales (codigo_prefijo, nombre_categoria, descripcion, estado)
    VALUES ('CAR', 'Carrocería', 'Partes y componentes de carrocería', 1);
    PRINT '✓ Categoría CAR insertada';
END

-- CAU
SELECT @count = COUNT(*) FROM CategoriaMateriales WHERE codigo_prefijo = 'CAU';
IF @count = 0
BEGIN
    INSERT INTO CategoriaMateriales (codigo_prefijo, nombre_categoria, descripcion, estado)
    VALUES ('CAU', 'Cauchos', 'Cauchos, gomas y sellos', 1);
    PRINT '✓ Categoría CAU insertada';
END

-- ELE
SELECT @count = COUNT(*) FROM CategoriaMateriales WHERE codigo_prefijo = 'ELE';
IF @count = 0
BEGIN
    INSERT INTO CategoriaMateriales (codigo_prefijo, nombre_categoria, descripcion, estado)
    VALUES ('ELE', 'Eléctrico', 'Componentes y accesorios eléctricos', 1);
    PRINT '✓ Categoría ELE insertada';
END

-- FER
SELECT @count = COUNT(*) FROM CategoriaMateriales WHERE codigo_prefijo = 'FER';
IF @count = 0
BEGIN
    INSERT INTO CategoriaMateriales (codigo_prefijo, nombre_categoria, descripcion, estado)
    VALUES ('FER', 'Ferretería', 'Herramientas y materiales de ferretería', 1);
    PRINT '✓ Categoría FER insertada';
END

-- PIN
SELECT @count = COUNT(*) FROM CategoriaMateriales WHERE codigo_prefijo = 'PIN';
IF @count = 0
BEGIN
    INSERT INTO CategoriaMateriales (codigo_prefijo, nombre_categoria, descripcion, estado)
    VALUES ('PIN', 'Pinturas', 'Pinturas, lacas y barnices', 1);
    PRINT '✓ Categoría PIN insertada';
END

PRINT '✓ Categorías iniciales verificadas/insertadas';
GO

-- ========================================
-- 4. VERIFICACIÓN FINAL
-- ========================================

PRINT '';
PRINT '========================================';
PRINT 'RESUMEN DE INSTALACIÓN';
PRINT '========================================';

SELECT 
    id_categoria,
    codigo_prefijo,
    nombre_categoria,
    estado,
    fecha_creacion
FROM CategoriaMateriales
ORDER BY codigo_prefijo;

DECLARE @totalCategorias INT;
SELECT @totalCategorias = COUNT(*) FROM CategoriaMateriales;

PRINT '';
PRINT 'Total de categorías: ' + CAST(@totalCategorias AS VARCHAR);
PRINT '';
PRINT '✓ Script completado exitosamente';
PRINT '✓ Sistema de categorización listo para usar';
