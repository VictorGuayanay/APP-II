-- Script para verificar la estructura de la tabla Empleados
USE CarroceriaAlvaradoDB;
GO

-- Ver la estructura completa de la tabla Empleados
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'Empleados'
ORDER BY ORDINAL_POSITION;
GO
