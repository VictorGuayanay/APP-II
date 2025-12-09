-- =============================================
-- Script: Agregar relación Proveedor a Materiales
-- Descripción: Migración para vincular materiales con proveedores
-- Fecha: 2025-12-08
-- =============================================

USE CarroceriaAlvaradoDB;
GO

-- Paso 1: Agregar columna id_proveedor a la tabla Materiales
PRINT 'Agregando columna id_proveedor a tabla Materiales...';
ALTER TABLE Materiales
ADD id_proveedor INT NULL;
GO

-- Paso 2: Agregar foreign key constraint
PRINT 'Creando foreign key constraint...';
ALTER TABLE Materiales
ADD CONSTRAINT FK_Materiales_Proveedores 
FOREIGN KEY (id_proveedor) REFERENCES Proveedores(id_proveedor)
ON DELETE SET NULL;  -- Si se elimina un proveedor, los materiales quedan sin proveedor
GO

-- Paso 3: Crear índice para mejorar búsquedas por proveedor
PRINT 'Creando índice en id_proveedor...';
CREATE INDEX IDX_Materiales_Proveedor ON Materiales(id_proveedor);
GO

-- Paso 4: Agregar comentario a la columna
EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'ID del proveedor que suministra este material', 
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE',  @level1name = N'Materiales',
    @level2type = N'COLUMN', @level2name = N'id_proveedor';
GO

-- Verificación
PRINT 'Verificando cambios...';
SELECT 
    COLUMN_NAME, 
    DATA_TYPE, 
    IS_NULLABLE,
    CHARACTER_MAXIMUM_LENGTH
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'Materiales' AND COLUMN_NAME = 'id_proveedor';
GO

-- Verificar foreign key
SELECT 
    fk.name AS ForeignKeyName,
    tp.name AS ParentTable,
    cp.name AS ParentColumn,
    tr.name AS ReferencedTable,
    cr.name AS ReferencedColumn
FROM sys.foreign_keys AS fk
INNER JOIN sys.tables AS tp ON fk.parent_object_id = tp.object_id
INNER JOIN sys.tables AS tr ON fk.referenced_object_id = tr.object_id
INNER JOIN sys.foreign_key_columns AS fkc ON fk.object_id = fkc.constraint_object_id
INNER JOIN sys.columns AS cp ON fkc.parent_column_id = cp.column_id AND fkc.parent_object_id = cp.object_id
INNER JOIN sys.columns AS cr ON fkc.referenced_column_id = cr.column_id AND fkc.referenced_object_id = cr.object_id
WHERE fk.name = 'FK_Materiales_Proveedores';
GO

PRINT 'Migración completada exitosamente!';
PRINT 'NOTA: Los materiales existentes tienen id_proveedor = NULL';
PRINT 'Puedes asignar proveedores manualmente desde la interfaz de edición.';
GO
