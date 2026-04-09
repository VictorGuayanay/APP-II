-- ================================================================
-- SCRIPT: Agregar columna 'rol' a tabla Usuarios
-- ================================================================
-- Este script agrega SOLO la columna 'rol' que falta
-- Ejecútalo en SQL Server Management Studio
-- ================================================================

USE CarroceriaAlvaradoDB;
GO

PRINT 'Iniciando actualización de tabla Usuarios...';
PRINT '';

-- Verificar si la columna 'rol' ya existe
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Usuarios' AND COLUMN_NAME = 'rol')
BEGIN
    PRINT '✓ Agregando columna rol a tabla Usuarios...';
    ALTER TABLE Usuarios ADD rol NVARCHAR(50) NOT NULL DEFAULT 'Empleado';
    PRINT '✓ Columna rol agregada exitosamente';
    PRINT '  - Valor por defecto: Empleado';
END
ELSE
BEGIN
    PRINT '✓ Columna rol ya existe en la tabla Usuarios';
END

PRINT '';
PRINT '===== ESTRUCTURA ACTUALIZADA DE LA TABLA Usuarios =====';
SELECT 
    COLUMN_NAME AS 'Columna',
    DATA_TYPE AS 'Tipo',
    IS_NULLABLE AS 'Permite NULL'
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'Usuarios'
ORDER BY ORDINAL_POSITION;

PRINT '';
PRINT '===== USUARIOS ACTUALES =====';
SELECT id_usuario, username, email, rol, estado FROM Usuarios;

PRINT '';
PRINT '✓ Actualización completada';
GO
