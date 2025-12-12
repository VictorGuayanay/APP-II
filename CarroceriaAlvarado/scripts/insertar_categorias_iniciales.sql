-- Script para insertar categorías iniciales de materiales
-- Base de datos: CarroceriaAlvaradoDB
-- Basado en las imágenes proporcionadas

USE CarroceriaAlvaradoDB;
GO

-- Insertar categorías iniciales
INSERT INTO CategoriaMateriales (codigo_prefijo, nombre_categoria, descripcion, estado)
VALUES 
    ('ACA', 'Accesorios', 'Accesorios varios para vehículos', 1),
    ('ACC', 'Accesorios Complementarios', 'Complementos y accesorios adicionales', 1),
    ('AIR', 'Aire y Neumáticos', 'Componentes de aire y neumáticos', 1),
    ('CAR', 'Carrocería', 'Partes y componentes de carrocería', 1),
    ('CAU', 'Cauchos', 'Cauchos, gomas y sellos', 1),
    ('ELE', 'Eléctrico', 'Componentes y accesorios eléctricos', 1),
    ('FER', 'Ferretería', 'Herramientas y materiales de ferretería', 1),
    ('PIN', 'Pinturas', 'Pinturas, lacas y barnices', 1);
GO

-- Verificar inserción
SELECT 
    id_categoria,
    codigo_prefijo,
    nombre_categoria,
    descripcion,
    estado,
    fecha_creacion
FROM CategoriaMateriales
ORDER BY codigo_prefijo;
GO

PRINT 'Categorías iniciales insertadas exitosamente';
PRINT 'Total de categorías: ' + CAST((SELECT COUNT(*) FROM CategoriaMateriales) AS VARCHAR);
