-- Script para agregar columnas de categoría a tabla Materiales
-- Base de datos: CarroceriaAlvaradoDB

USE CarroceriaAlvaradoDB;
GO

-- Agregar columna id_categoria
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('Materiales') AND name = 'id_categoria')
BEGIN
    ALTER TABLE Materiales
    ADD id_categoria INT NULL;
    
    PRINT 'Columna id_categoria agregada a Materiales';
END
ELSE
BEGIN
    PRINT 'Columna id_categoria ya existe en Materiales';
END
GO

-- Agregar columna codigo_material
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('Materiales') AND name = 'codigo_material')
BEGIN
    ALTER TABLE Materiales
    ADD codigo_material VARCHAR(20) NULL;
    
    PRINT 'Columna codigo_material agregada a Materiales';
END
ELSE
BEGIN
    PRINT 'Columna codigo_material ya existe en Materiales';
END
GO

-- Crear Foreign Key hacia CategoriaMateriales
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_Materiales_Categoria')
BEGIN
    ALTER TABLE Materiales
    ADD CONSTRAINT FK_Materiales_Categoria 
    FOREIGN KEY (id_categoria) REFERENCES CategoriaMateriales(id_categoria);
    
    PRINT 'Foreign Key FK_Materiales_Categoria creada';
END
ELSE
BEGIN
    PRINT 'Foreign Key FK_Materiales_Categoria ya existe';
END
GO

-- Crear constraint UNIQUE para codigo_material
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'UQ_Materiales_Codigo' AND object_id = OBJECT_ID('Materiales'))
BEGIN
    ALTER TABLE Materiales
    ADD CONSTRAINT UQ_Materiales_Codigo UNIQUE (codigo_material);
    
    PRINT 'Constraint UNIQUE para codigo_material creado';
END
ELSE
BEGIN
    PRINT 'Constraint UNIQUE para codigo_material ya existe';
END
GO

-- Crear índices
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_codigo_material' AND object_id = OBJECT_ID('Materiales'))
BEGIN
    CREATE INDEX idx_codigo_material ON Materiales(codigo_material);
    PRINT 'Índice idx_codigo_material creado';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_id_categoria_material' AND object_id = OBJECT_ID('Materiales'))
BEGIN
    CREATE INDEX idx_id_categoria_material ON Materiales(id_categoria);
    PRINT 'Índice idx_id_categoria_material creado';
END
GO

PRINT 'Script completado exitosamente';
