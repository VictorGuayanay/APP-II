-- Script para verificar y corregir el valor por defecto de la columna estado
-- en la tabla Empleados

USE CarroceriaAlvarado;
GO

-- 1. Verificar la definición actual de la columna estado
SELECT 
    c.name AS ColumnName,
    t.name AS DataType,
    c.max_length AS MaxLength,
    c.is_nullable AS IsNullable,
    dc.definition AS DefaultValue
FROM sys.columns c
INNER JOIN sys.types t ON c.user_type_id = t.user_type_id
LEFT JOIN sys.default_constraints dc ON c.default_object_id = dc.object_id
WHERE c.object_id = OBJECT_ID('Empleados')
AND c.name = 'estado';
GO

-- 2. Si el valor por defecto NO es 1, eliminarlo y crear uno nuevo
IF EXISTS (
    SELECT 1 
    FROM sys.default_constraints dc
    INNER JOIN sys.columns c ON dc.parent_object_id = c.object_id AND dc.parent_column_id = c.column_id
    WHERE c.object_id = OBJECT_ID('Empleados') AND c.name = 'estado'
    AND dc.definition != '((1))'
)
BEGIN
    -- Obtener el nombre del constraint
    DECLARE @ConstraintName NVARCHAR(200);
    SELECT @ConstraintName = dc.name
    FROM sys.default_constraints dc
    INNER JOIN sys.columns c ON dc.parent_object_id = c.object_id AND dc.parent_column_id = c.column_id
    WHERE c.object_id = OBJECT_ID('Empleados') AND c.name = 'estado';
    
    -- Eliminar el constraint existente
    IF @ConstraintName IS NOT NULL
    BEGIN
        DECLARE @SQL NVARCHAR(500);
        SET @SQL = 'ALTER TABLE Empleados DROP CONSTRAINT ' + @ConstraintName;
        EXEC sp_executesql @SQL;
        PRINT 'Constraint anterior eliminado: ' + @ConstraintName;
    END
    
    -- Crear nuevo constraint con valor por defecto = 1
    ALTER TABLE Empleados 
    ADD CONSTRAINT DF_Empleados_Estado DEFAULT 1 FOR estado;
    
    PRINT 'Nuevo constraint creado: DF_Empleados_Estado con valor por defecto = 1';
END
ELSE
BEGIN
    PRINT 'La columna estado ya tiene el valor por defecto correcto (1)';
END
GO

-- 3. Actualizar todos los empleados existentes que tengan estado = 0 a estado = 1
-- (OPCIONAL - solo si quieres activar todos los empleados inactivos)
-- DESCOMENTA LAS SIGUIENTES LÍNEAS SI QUIERES ACTIVAR TODOS LOS EMPLEADOS:

-- UPDATE Empleados 
-- SET estado = 1 
-- WHERE estado = 0;
-- PRINT 'Empleados actualizados a estado activo';

-- 4. Verificar el resultado
SELECT 
    c.name AS ColumnName,
    t.name AS DataType,
    dc.definition AS DefaultValue
FROM sys.columns c
INNER JOIN sys.types t ON c.user_type_id = t.user_type_id
LEFT JOIN sys.default_constraints dc ON c.default_object_id = dc.object_id
WHERE c.object_id = OBJECT_ID('Empleados')
AND c.name = 'estado';
GO

PRINT 'Script completado exitosamente';
