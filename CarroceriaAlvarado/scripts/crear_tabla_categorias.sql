-- Script para crear tabla de Categorías de Materiales
-- Base de datos: CarroceriaAlvaradoDB

USE CarroceriaAlvaradoDB;
GO

-- Crear tabla CategoriaMateriales
CREATE TABLE CategoriaMateriales (
    id_categoria INT PRIMARY KEY IDENTITY(1,1),
    codigo_prefijo VARCHAR(10) NOT NULL UNIQUE,  -- Ej: 'ACA', 'ELE', 'FER'
    nombre_categoria VARCHAR(100) NOT NULL,      -- Ej: 'Accesorios', 'Eléctrico'
    descripcion TEXT,
    estado BIT DEFAULT 1,                        -- 1=Activo, 0=Inactivo
    fecha_creacion DATETIME DEFAULT GETDATE()
);
GO

-- Crear índices
CREATE INDEX idx_codigo_prefijo ON CategoriaMateriales(codigo_prefijo);
CREATE INDEX idx_estado_categoria ON CategoriaMateriales(estado);
GO

PRINT 'Tabla CategoriaMateriales creada exitosamente';
