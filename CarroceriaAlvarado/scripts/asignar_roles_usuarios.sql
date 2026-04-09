-- ================================================================
-- SCRIPT: Asignar Roles a Usuarios Existentes
-- ================================================================
-- Este script asigna los roles correctos en la tabla Rol_Usuario
-- para los usuarios existentes
-- ================================================================

USE CarroceriaAlvaradoDB;
GO

PRINT 'Iniciando asignación de roles a usuarios existentes...';
PRINT '';

-- Ver los usuarios actuales y sus roles en Rol_Usuario
PRINT '===== USUARIOS y ROLES ACTUALES =====';
SELECT 
    u.id_usuario,
    u.username,
    u.email,
    CASE WHEN r.rol IS NULL THEN '(Sin rol asignado)' ELSE r.rol END AS rol,
    CASE WHEN ru.id_usuario IS NULL THEN 'NO' ELSE 'SÍ' END AS 'En Rol_Usuario'
FROM Usuarios u
LEFT JOIN Rol_Usuario ru ON u.id_usuario = ru.id_usuario
LEFT JOIN Rol r ON ru.id_rol = r.id_rol;

PRINT '';
PRINT '===== ASIGNANDO ROLES =====';

-- Los usuarios que vimos fueron:
-- Admin (id_usuario=20) → Administrador (id_rol=1)
-- victor (id_usuario=24) → Supervisor (id_rol=2)
-- kevin (id_usuario=25) → Administrador (id_rol=1)

-- Actualizar o insertar rol para Admin
IF EXISTS (SELECT 1 FROM Rol_Usuario WHERE id_usuario = 20)
    UPDATE Rol_Usuario SET id_rol = 1 WHERE id_usuario = 20
ELSE
    INSERT INTO Rol_Usuario (id_rol, id_usuario, usuario) VALUES (1, 20, 'Admin')

PRINT '✓ Rol Administrador asignado a user Admin (id=20)';

-- Actualizar o insertar rol para victor
IF EXISTS (SELECT 1 FROM Rol_Usuario WHERE id_usuario = 24)
    UPDATE Rol_Usuario SET id_rol = 2 WHERE id_usuario = 24
ELSE
    INSERT INTO Rol_Usuario (id_rol, id_usuario, usuario) VALUES (2, 24, 'victor')

PRINT '✓ Rol Supervisor asignado a user victor (id=24)';

-- Actualizar o insertar rol para kevin
IF EXISTS (SELECT 1 FROM Rol_Usuario WHERE id_usuario = 25)
    UPDATE Rol_Usuario SET id_rol = 1 WHERE id_usuario = 25
ELSE
    INSERT INTO Rol_Usuario (id_rol, id_usuario, usuario) VALUES (1, 25, 'kevin')

PRINT '✓ Rol Administrador asignado a user kevin (id=25)';

PRINT '';
PRINT '===== RESULTADO FINAL - USUARIOS CON ROLES =====';
SELECT 
    u.id_usuario,
    u.username,
    u.email,
    r.rol AS 'Rol Asignado',
    u.estado
FROM Usuarios u
LEFT JOIN Rol_Usuario ru ON u.id_usuario = ru.id_usuario
LEFT JOIN Rol r ON ru.id_rol = r.id_rol
ORDER BY u.id_usuario;

PRINT '';
PRINT '✓ Asignación de roles completada exitosamente';
GO
