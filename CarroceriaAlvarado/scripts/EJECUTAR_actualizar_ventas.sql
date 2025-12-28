-- Script para verificar y actualizar la tabla Ventas_Directas
-- Ejecutar este script en SQL Server Management Studio

USE CarroceriaAlvaradoDB;
GO

-- Verificar si la tabla existe y eliminarla (SOLO PARA DESARROLLO)
IF OBJECT_ID('Detalle_Venta_Directa', 'U') IS NOT NULL
    DROP TABLE Detalle_Venta_Directa;
GO

IF OBJECT_ID('Ventas_Directas', 'U') IS NOT NULL
    DROP TABLE Ventas_Directas;
GO

-- Crear tabla Ventas_Directas con la estructura correcta
CREATE TABLE Ventas_Directas (
    id_venta INT PRIMARY KEY IDENTITY(1,1),
    fecha_venta DATETIME DEFAULT GETDATE(),
    
    -- Información del cliente
    tipo_cliente VARCHAR(50) NOT NULL, -- 'Registrado', 'Temporal', 'Consumidor Final'
    id_cliente INT NULL,
    cliente_ruc_ci VARCHAR(20),
    cliente_nombre VARCHAR(200),
    cliente_telefono VARCHAR(20),
    cliente_email VARCHAR(100),
    
    -- Totales de la venta
    subtotal_general DECIMAL(10,2) NOT NULL,
    ganancia_general DECIMAL(10,2) NOT NULL,
    iva_general DECIMAL(10,2) NOT NULL,
    total_general DECIMAL(10,2) NOT NULL,
    
    -- Información de pago
    forma_pago VARCHAR(50) NOT NULL,
    
    -- Usuario que registró
    id_usuario INT NOT NULL,
    nombre_usuario VARCHAR(100),
    
    comprobante_generado BIT DEFAULT 0,
    
    FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente),
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
);
GO

-- Crear tabla Detalle_Venta_Directa
CREATE TABLE Detalle_Venta_Directa (
    id_detalle INT PRIMARY KEY IDENTITY(1,1),
    id_venta INT NOT NULL,
    id_material INT NOT NULL,
    nombre_material VARCHAR(200) NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    porcentaje_ganancia INT NOT NULL,
    ganancia DECIMAL(10,2) NOT NULL,
    porcentaje_iva INT NOT NULL,
    valor_iva DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    
    FOREIGN KEY (id_venta) REFERENCES Ventas_Directas(id_venta) ON DELETE CASCADE,
    FOREIGN KEY (id_material) REFERENCES Materiales(id_material)
);
GO

-- Crear índices
CREATE INDEX idx_fecha_venta ON Ventas_Directas(fecha_venta);
CREATE INDEX idx_tipo_cliente ON Ventas_Directas(tipo_cliente);
CREATE INDEX idx_forma_pago ON Ventas_Directas(forma_pago);
CREATE INDEX idx_id_venta_detalle ON Detalle_Venta_Directa(id_venta);
GO

PRINT 'Tablas de ventas creadas exitosamente';
PRINT 'IMPORTANTE: Ejecuta este script en SQL Server Management Studio';
GO
