-- ================================================================
-- SCRIPT: Asignar Roles Faltantes a Usuarios
-- ================================================================
-- Asigna roles a usuarios que aún no tienen uno asignado
-- ================================================================

USE CarroceriaAlvaradoDB;
GO

PRINT '╔════════════════════════════════════════════════════════════╗';
PRINT '║         ASIGNANDO ROLES A USUARIOS FALTANTES               ║';
PRINT '╚════════════════════════════════════════════════════════════╝';
PRINT '';

-- Victor: Supervisor (id_rol = 2)
PRINT '[1/2] Asignando rol Supervisor a usuario victor (id=24)...';
IF NOT EXISTS (SELECT 1 FROM Rol_Usuario WHERE id_usuario = 24)
BEGIN
    INSERT INTO Rol_Usuario (id_rol, id_usuario, usuario) 
    VALUES (2, 24, 'victor');
    PRINT '✓ Victor (id=24) ahora tiene rol: Supervisor';
END
ELSE
BEGIN
    UPDATE Rol_Usuario SET id_rol = 2 WHERE id_usuario = 24;
    PRINT '✓ Rol de Victor (id=24) actualizado a: Supervisor';
END

-- Admin1: Administrador (id_rol = 1)
PRINT '[2/2] Asignando rol Administrador a usuario Admin1 (id=26)...';
IF NOT EXISTS (SELECT 1 FROM Rol_Usuario WHERE id_usuario = 26)
BEGIN
    INSERT INTO Rol_Usuario (id_rol, id_usuario, usuario) 
    VALUES (1, 26, 'Admin1');
    PRINT '✓ Admin1 (id=26) ahora tiene rol: Administrador';
END
ELSE
BEGIN
    UPDATE Rol_Usuario SET id_rol = 1 WHERE id_usuario = 26;
    PRINT '✓ Rol de Admin1 (id=26) actualizado a: Administrador';
END

PRINT '';
PRINT '╔════════════════════════════════════════════════════════════╗';
PRINT '║              ESTADO FINAL - USUARIO CON ROLES              ║';
PRINT '╚════════════════════════════════════════════════════════════╝';
PRINT '';

SELECT 
    u.id_usuario,
    u.username,
    u.email,
    COALESCE(r.rol, 'Empleado (Sin asignar)') AS rol_asignado,
    u.estado
FROM Usuarios u
LEFT JOIN Rol_Usuario ru ON u.id_usuario = ru.id_usuario
LEFT JOIN Rol r ON ru.id_rol = r.id_rol
ORDER BY u.id_usuario;

PRINT '';
PRINT '✓ Asignación de roles completada exitosamente';
PRINT '';
GO
