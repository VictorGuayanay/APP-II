-- ================================================================
-- SCRIPT: Verificar estructura de tablas Rol y Rol_Usuario
-- ================================================================

USE CarroceriaAlvaradoDB;
GO

PRINT '===== ESTRUCTURA TABLA Rol =====';
SELECT 
    COLUMN_NAME AS 'Columna',
    DATA_TYPE AS 'Tipo'
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'Rol'
ORDER BY ORDINAL_POSITION;

PRINT '';
PRINT '===== DATOS EN TABLA Rol =====';
SELECT * FROM Rol;

PRINT '';
PRINT '===== ESTRUCTURA TABLA Rol_Usuario =====';
SELECT 
    COLUMN_NAME AS 'Columna',
    DATA_TYPE AS 'Tipo'
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'Rol_Usuario'
ORDER BY ORDINAL_POSITION;

PRINT '';
PRINT '===== DATOS EN TABLA Rol_Usuario =====';
SELECT * FROM Rol_Usuario;

PRINT '';
PRINT '===== ESTRUCTURA TABLA Usuarios =====';
SELECT 
    COLUMN_NAME AS 'Columna',
    DATA_TYPE AS 'Tipo'
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'Usuarios'
ORDER BY ORDINAL_POSITION;

PRINT '';
PRINT '===== VISTA COMPLETA: Usuarios + Roles =====';
SELECT 
    u.id_usuario,
    u.username,
    u.email,
    r.rol,
    u.estado
FROM Usuarios u
LEFT JOIN Rol_Usuario ru ON u.id_usuario = ru.id_usuario
LEFT JOIN Rol r ON ru.id_rol = r.id_rol;

GO
