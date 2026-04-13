-- ============================================================
-- Script: Nuevas tablas para seguridad y configuración
-- Base de Datos: SQL Server (CarroceriaAlvaradoDB)
-- Fecha: 2026-04-11
-- Tablas:
--   1. Configuraciones  (BE-03: persistencia de configuraciones)
--   2. TokensRevocados  (SEC-09: blacklist de tokens JWT)
-- ============================================================

USE CarroceriaAlvaradoDB;
GO

-- ============================================================
-- TABLA: Configuraciones
-- Almacena parámetros del sistema que antes solo vivían en RAM.
-- Permite que los cambios del panel admin sobrevivan reinicios.
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Configuraciones')
BEGIN
    CREATE TABLE Configuraciones (
        id_config       INT IDENTITY(1,1) PRIMARY KEY,
        clave           VARCHAR(100) NOT NULL UNIQUE,  -- Ej: 'reset_token_expiry_minutes'
        valor           VARCHAR(255) NOT NULL,          -- Ej: '15'
        descripcion     VARCHAR(500),
        activo          BIT NOT NULL DEFAULT 1,
        fecha_actualizacion DATETIME NOT NULL DEFAULT GETDATE()
    );
    PRINT 'Tabla Configuraciones creada.';
END
ELSE
    PRINT 'Tabla Configuraciones ya existe.';
GO

-- Insertar valores iniciales si la tabla está vacía
IF NOT EXISTS (SELECT 1 FROM Configuraciones)
BEGIN
    INSERT INTO Configuraciones (clave, valor, descripcion) VALUES
        ('reset_token_expiry_minutes', '15',
         'Tiempo en minutos que dura el enlace de restablecimiento de contraseña'),
        ('max_failed_login_attempts', '5',
         'Número máximo de intentos fallidos de login antes de bloquear la cuenta'),
        ('global_low_stock_threshold', '10',
         'Cantidad mínima de stock por debajo de la cual se genera una alerta');
    PRINT 'Valores iniciales de Configuraciones insertados.';
END
GO

-- ============================================================
-- TABLA: TokensRevocados
-- Blacklist de tokens JWT. Al hacer logout, el token se agrega
-- aquí para que no pueda reutilizarse aunque sea válido.
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'TokensRevocados')
BEGIN
    CREATE TABLE TokensRevocados (
        id_revocacion       INT IDENTITY(1,1) PRIMARY KEY,
        token_hash          VARCHAR(50) NOT NULL,          -- Hash del token (no el token completo)
        id_usuario          INT,                           -- Usuario que hizo logout (para trazabilidad)
        fecha_revocacion    DATETIME NOT NULL DEFAULT GETDATE(),
        fecha_expiracion    DATETIME,                      -- Expiración original del token

        CONSTRAINT fk_tokens_usuario FOREIGN KEY (id_usuario)
            REFERENCES Usuarios(id_usuario) ON DELETE SET NULL
    );
    PRINT 'Tabla TokensRevocados creada.';
END
ELSE
    PRINT 'Tabla TokensRevocados ya existe.';
GO

-- Índice para búsquedas rápidas por hash de token
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_tokens_hash' AND object_id = OBJECT_ID('TokensRevocados'))
    CREATE INDEX idx_tokens_hash ON TokensRevocados(token_hash);
GO

-- Índice para limpiar tokens expirados periódicamente
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_tokens_expiracion' AND object_id = OBJECT_ID('TokensRevocados'))
    CREATE INDEX idx_tokens_expiracion ON TokensRevocados(fecha_expiracion);
GO

-- ============================================================
-- TAREA DE MANTENIMIENTO: Limpiar tokens expirados
-- Ejecutar periódicamente (cron, SQL Agent, etc.)
-- Elimina tokens cuya fecha_expiracion ya pasó
-- ============================================================
-- DELETE FROM TokensRevocados WHERE fecha_expiracion < GETDATE();
-- GO

PRINT 'Script de nuevas tablas ejecutado correctamente.';
GO
