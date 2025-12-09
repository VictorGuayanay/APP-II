-- =============================================
-- Script: Crear Tabla Proveedores
-- Descripción: Tabla para gestionar proveedores de materiales
-- Fecha: 2025-12-08
-- =============================================

USE CarroceriaAlvaradoDB;
GO

-- Tabla: Proveedores
CREATE TABLE Proveedores (
    id_proveedor INT PRIMARY KEY IDENTITY(1,1),
    ruc VARCHAR(13) NOT NULL UNIQUE,
    nombre_proveedor VARCHAR(100) NOT NULL,
    razon_social VARCHAR(150) NOT NULL,
    direccion VARCHAR(255),
    descripcion TEXT,
    telefono VARCHAR(15),
    email VARCHAR(100),
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo')),
    fecha_registro DATE NOT NULL DEFAULT GETDATE()
);
GO

-- Crear índice para búsquedas por RUC
CREATE INDEX IDX_Proveedores_RUC ON Proveedores(ruc);
GO

-- Crear índice para búsquedas por nombre
CREATE INDEX IDX_Proveedores_Nombre ON Proveedores(nombre_proveedor);
GO

-- Comentarios de la tabla
EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'Tabla que almacena información de proveedores de materiales', 
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE',  @level1name = N'Proveedores';
GO

-- Insertar datos de ejemplo (opcional)
INSERT INTO Proveedores (ruc, nombre_proveedor, razon_social, direccion, descripcion, telefono, email)
VALUES 
    ('1234567890001', 'Proveedor ABC', 'ABC Suministros S.A.', 'Av. Principal 123, Riobamba', 'Proveedor de materiales de construcción', '032-123456', 'contacto@abc.com'),
    ('0987654321001', 'Distribuidora XYZ', 'XYZ Distribuciones Ltda.', 'Calle Secundaria 456, Riobamba', 'Distribuidor de herramientas y equipos', '032-654321', 'ventas@xyz.com');
GO

-- Verificar que la tabla se creó correctamente
SELECT * FROM Proveedores;
GO

PRINT 'Tabla Proveedores creada exitosamente';
GO
