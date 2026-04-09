-- ================================================================
-- SCRIPT: Verificar estructura actual de la tabla Usuarios
-- ================================================================
-- Este script muestra qué columnas existen en la tabla Usuarios
-- Ejecuta esto primero para ver qué hace falta
-- ================================================================

USE CarroceriaAlvaradoDB;
GO

PRINT '===== ESTRUCTURA ACTUAL DE LA TABLA Usuarios =====';
SELECT 
    COLUMN_NAME AS 'Columna',
    DATA_TYPE AS 'Tipo de Dato',
    IS_NULLABLE AS 'Permite NULL',
    COLUMN_DEFAULT AS 'Valor Defecto'
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'Usuarios'
ORDER BY ORDINAL_POSITION;

PRINT '';
PRINT '===== DATOS ACTUALES EN Usuarios =====';
SELECT * FROM Usuarios;

PRINT '';
PRINT '===== RESUMEN =====';
DECLARE @total_columns INT = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Usuarios');
PRINT 'Total de columnas en la tabla: ' + CAST(@total_columns AS VARCHAR);
GO
