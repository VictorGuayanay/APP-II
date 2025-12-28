-- Script para crear tabla de Ventas Directas
-- Base de datos: CarroceriaAlvaradoDB

USE CarroceriaAlvaradoDB;
GO

-- Crear tabla Ventas_Directas
CREATE TABLE Ventas_Directas (
    id_venta INT PRIMARY KEY IDENTITY(1,1),
    fecha_venta DATETIME DEFAULT GETDATE(),
    id_material INT NOT NULL,
    nombre_material VARCHAR(200) NOT NULL,
    cantidad_vendida INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    porcentaje_ganancia INT NOT NULL,
    ganancia DECIMAL(10,2) NOT NULL,
    porcentaje_iva INT NOT NULL,
    valor_iva DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    forma_pago VARCHAR(50) NOT NULL,
    id_usuario INT NOT NULL,
    nombre_usuario VARCHAR(100),
    comprobante_generado BIT DEFAULT 0,
    FOREIGN KEY (id_material) REFERENCES Materiales(id_material),
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
);
GO

-- Crear índices para mejorar rendimiento
CREATE INDEX idx_fecha_venta ON Ventas_Directas(fecha_venta);
CREATE INDEX idx_forma_pago ON Ventas_Directas(forma_pago);
CREATE INDEX idx_id_material ON Ventas_Directas(id_material);
GO

PRINT 'Tabla Ventas_Directas creada exitosamente';
GO
