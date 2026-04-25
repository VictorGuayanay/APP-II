-- ============================================================
-- Script: Crear tabla OrdenesReposicion
-- Sistema: Carrocerías Alvarado
-- Fecha: 2026-04-25
-- Descripción: Tabla para gestionar el ciclo de reposición
--   de materiales con stock bajo.
-- ============================================================

IF NOT EXISTS (
    SELECT * FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_NAME = 'OrdenesReposicion'
)
BEGIN
    CREATE TABLE OrdenesReposicion (
        id_orden_reposicion     INT IDENTITY(1,1) PRIMARY KEY,
        id_material             INT NOT NULL,
        cantidad_solicitada     INT NOT NULL,
        cantidad_recibida       INT DEFAULT 0,
        estado                  VARCHAR(20) NOT NULL DEFAULT 'Pendiente',
                                -- Valores: 'Pendiente', 'Recibida', 'Cancelada'
        id_proveedor            INT NULL,
        notas                   NVARCHAR(500) NULL,
        fecha_creacion          DATETIME NOT NULL DEFAULT GETDATE(),
        fecha_recepcion         DATETIME NULL,
        id_usuario_creador      INT NOT NULL,
        id_usuario_receptor     INT NULL,

        CONSTRAINT FK_OR_Material
            FOREIGN KEY (id_material)
            REFERENCES Materiales(id_material),

        CONSTRAINT FK_OR_Proveedor
            FOREIGN KEY (id_proveedor)
            REFERENCES Proveedores(id_proveedor),

        CONSTRAINT FK_OR_Creador
            FOREIGN KEY (id_usuario_creador)
            REFERENCES Usuarios(id_usuario),

        CONSTRAINT FK_OR_Receptor
            FOREIGN KEY (id_usuario_receptor)
            REFERENCES Usuarios(id_usuario),

        CONSTRAINT CHK_OR_Estado
            CHECK (estado IN ('Pendiente', 'Recibida', 'Cancelada')),

        CONSTRAINT CHK_OR_CantidadSolicitada
            CHECK (cantidad_solicitada > 0),

        CONSTRAINT CHK_OR_CantidadRecibida
            CHECK (cantidad_recibida >= 0)
    );

    PRINT 'Tabla OrdenesReposicion creada exitosamente.';
END
ELSE
BEGIN
    PRINT 'La tabla OrdenesReposicion ya existe. No se realizaron cambios.';
END
