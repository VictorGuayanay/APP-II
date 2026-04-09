-- ================================================================
-- SCRIPT DE MIGRACIÓN: Actualizar tabla Usuarios
-- ================================================================
-- Este script agrega las columnas faltantes a la tabla Usuarios
-- si es que fueron creadas con un schema antiguo
-- ================================================================

USE CarroceriaAlvaradoDB;
GO

-- Verificar si la columna 'email' existe, si no, agregarla
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Usuarios' AND COLUMN_NAME = 'email')
BEGIN
    ALTER TABLE Usuarios ADD email NVARCHAR(255) UNIQUE;
    PRINT 'Columna email agregada a la tabla Usuarios';
END
ELSE
BEGIN
    PRINT 'Columna email ya existe en la tabla Usuarios';
END
GO

-- Verificar si la columna 'intentos_fallidos' existe
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Usuarios' AND COLUMN_NAME = 'intentos_fallidos')
BEGIN
    ALTER TABLE Usuarios ADD intentos_fallidos INT NOT NULL DEFAULT 0;
    PRINT 'Columna intentos_fallidos agregada a la tabla Usuarios';
END
ELSE
BEGIN
    PRINT 'Columna intentos_fallidos ya existe en la tabla Usuarios';
END
GO

-- Verificar si la columna 'bloqueado' existe
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Usuarios' AND COLUMN_NAME = 'bloqueado')
BEGIN
    ALTER TABLE Usuarios ADD bloqueado BIT NOT NULL DEFAULT 0;
    PRINT 'Columna bloqueado agregada a la tabla Usuarios';
END
ELSE
BEGIN
    PRINT 'Columna bloqueado ya existe en la tabla Usuarios';
END
GO

-- Verificar si la columna 'estado' está como NVARCHAR(50), si no, modificarla
IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Usuarios' AND COLUMN_NAME = 'estado')
BEGIN
    DECLARE @col_type VARCHAR(max) = (SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Usuarios' AND COLUMN_NAME = 'estado');
    
    IF @col_type != 'bit' AND @col_type != 'int'
    BEGIN
        -- Si es varchar, necesitamos convertir
        ALTER TABLE Usuarios 
        ADD estado_new BIT NOT NULL DEFAULT 1;
        
        UPDATE Usuarios SET estado_new = CASE WHEN estado = 'Activo' THEN 1 ELSE 0 END;
        
        ALTER TABLE Usuarios DROP COLUMN estado;
        
        EXEC sp_rename 'Usuarios.estado_new', 'estado', 'COLUMN';
        
        PRINT 'Columna estado convertida de VARCHAR a BIT';
    END
END
GO

-- Verificar si la columna 'rol' existe con el tipo correcto
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Usuarios' AND COLUMN_NAME = 'rol')
BEGIN
    ALTER TABLE Usuarios ADD rol NVARCHAR(50) NOT NULL DEFAULT 'Empleado';
    PRINT 'Columna rol agregada a la tabla Usuarios';
END
ELSE
BEGIN
    PRINT 'Columna rol ya existe en la tabla Usuarios';
END
GO

-- Agregar columnas de reset de contraseña si no existen
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Usuarios' AND COLUMN_NAME = 'reset_token')
BEGIN
    ALTER TABLE Usuarios ADD reset_token NVARCHAR(MAX) NULL;
    PRINT 'Columna reset_token agregada a la tabla Usuarios';
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Usuarios' AND COLUMN_NAME = 'reset_token_expiry')
BEGIN
    ALTER TABLE Usuarios ADD reset_token_expiry DATETIME NULL;
    PRINT 'Columna reset_token_expiry agregada a la tabla Usuarios';
END
GO

-- Agregar columna fecha_creacion si no existe
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Usuarios' AND COLUMN_NAME = 'fecha_creacion')
BEGIN
    ALTER TABLE Usuarios ADD fecha_creacion DATETIME NOT NULL DEFAULT GETDATE();
    PRINT 'Columna fecha_creacion agregada a la tabla Usuarios';
END
GO

-- Mostrar la estructura final de la tabla
PRINT '';
PRINT '===== ESTRUCTURA FINAL DE LA TABLA Usuarios =====';
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'Usuarios' 
ORDER BY ORDINAL_POSITION;

-- Mostrar datos de ejemplo
PRINT '';
PRINT '===== USUARIOS ACTUALES =====';
SELECT * FROM Usuarios;
GO
