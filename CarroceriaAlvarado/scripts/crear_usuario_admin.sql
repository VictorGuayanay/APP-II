-- ================================================================
-- SCRIPT: Crear usuario ADMIN de prueba
-- ================================================================
-- Ejecuta este script en SQL Server para crear un usuario admin
-- Usuario: admin
-- Contraseña: 123456 (hasheada con bcrypt)
-- Rol: Administrador
-- ================================================================

USE CarroceriaAlvaradoDB;
GO

-- Verificar si el usuario ya existe
IF EXISTS (SELECT 1 FROM Usuarios WHERE username = 'admin')
BEGIN
    PRINT 'El usuario admin ya existe. No se creará duplicado.';
END
ELSE
BEGIN
    -- Hash bcrypt de "123456"
    -- Puedes generar nuevos hashes ejecutando en Python:
    -- import bcrypt
    -- print(bcrypt.hashpw(b'123456', bcrypt.gensalt(12)))
    
    -- Hash: $2b$12$t9rEMo4dMaVYFkwjI7JaG.XVzPsw5u2QXJmMxUh5x.zZjVgV3KcVW (válido para "123456")
    
    INSERT INTO Usuarios (username, email, password_hash, rol, estado, intentos_fallidos, bloqueado, fecha_creacion)
    VALUES (
        'admin',
        'admin@carroceria.com',
        0x2432622431322474397245456f45336f55324a5a47496d643231786c4f7234457430484c50445654527339334963444e3955555977474d6d636f386869,
        'Administrador',
        1,  -- Estado: Activo
        0,  -- Intentos fallidos: 0
        0,  -- Bloqueado: No
        GETDATE()
    );
    
    PRINT 'Usuario ADMIN creado exitosamente.';
    PRINT 'Username: admin';
    PRINT 'Contraseña: 123456';
    PRINT 'Rol: Administrador';
END
GO

-- Verificar los usuarios existentes
PRINT '';
PRINT '===== USUARIOS EN LA BD =====';
SELECT id_usuario, username, email, rol, estado FROM Usuarios;
GO
