-- =====================================================
-- Script para configurar SQL Server Authentication
-- Ejecutar en SQL Server Management Studio (SSMS)
-- =====================================================

USE CarroceriaAlvaradoDB;
GO

-- 1. Crear un login a nivel de servidor
CREATE LOGIN carroceria_user 
WITH PASSWORD = 'Carroceria2025!Secure';
GO

-- 2. Crear un usuario en la base de datos
CREATE USER carroceria_user 
FOR LOGIN carroceria_user;
GO

-- 3. Asignar permisos completos al usuario
ALTER ROLE db_owner ADD MEMBER carroceria_user;
GO

-- 4. Verificar que el usuario fue creado
SELECT 
    name AS UserName,
    type_desc AS UserType,
    create_date AS CreatedDate
FROM sys.database_principals
WHERE name = 'carroceria_user';
GO

PRINT 'Usuario SQL Server creado exitosamente';
PRINT 'Login: carroceria_user';
PRINT 'Password: Carroceria2025!Secure';
PRINT '';
PRINT 'IMPORTANTE: Cambia la contraseña por una más segura en producción';
GO
