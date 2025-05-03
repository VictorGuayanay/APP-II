-- Crear la base de datos
CREATE DATABASE CarroceriaAlvaradoDB;
GO

-- Usar la base de datos
USE CarroceriaAlvaradoDB;
GO

-- Tabla: Usuarios
CREATE TABLE Usuarios (
    id_usuario INT PRIMARY KEY IDENTITY(1,1),
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARBINARY(255) NOT NULL,
    rol VARCHAR(50) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo'))
);
GO

-- Tabla: Materiales
CREATE TABLE Materiales (
    id_material INT PRIMARY KEY IDENTITY(1,1),
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    cantidad INT NOT NULL DEFAULT 0 CHECK (cantidad >= 0),
    precio_unitario DECIMAL(10, 2) NOT NULL CHECK (precio_unitario >= 0),
    fecha_ultima_actualizacion DATE DEFAULT GETDATE()
);
GO

-- Tabla: Empleados
CREATE TABLE Empleados (
    id_empleado INT PRIMARY KEY IDENTITY(1,1),
    nombre VARCHAR(100) NOT NULL,
    cedula VARCHAR(20) NOT NULL UNIQUE,
    rol VARCHAR(50) NOT NULL,
    telefono VARCHAR(15),
    fecha_contratacion DATE NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo'))
);
GO

-- Tabla: Clientes
CREATE TABLE Clientes (
    id_cliente INT PRIMARY KEY IDENTITY(1,1),
    nombre VARCHAR(100) NOT NULL,
    cedula VARCHAR(20) NOT NULL UNIQUE,
    telefono VARCHAR(15),
    email VARCHAR(100),
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo'))
);
GO

-- Tabla: OrdenesTrabajo
CREATE TABLE OrdenesTrabajo (
    id_orden INT PRIMARY KEY IDENTITY(1,1),
    id_cliente INT NOT NULL,
    id_empleado INT NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    descripcion VARCHAR(255) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'En Progreso' CHECK (estado IN ('En Progreso', 'Completado', 'Cancelado')),
    prioridad VARCHAR(20) NOT NULL DEFAULT 'Media' CHECK (prioridad IN ('Baja', 'Media', 'Alta')),
    FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente),
    FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
);
GO

-- Tabla: DetalleOrdenMateriales
CREATE TABLE DetalleOrdenMateriales (
    id_detalle INT PRIMARY KEY IDENTITY(1,1),
    id_orden INT NOT NULL,
    id_material INT NOT NULL,
    cantidad_usada INT NOT NULL CHECK (cantidad_usada > 0),
    costo_total DECIMAL(10, 2) NOT NULL CHECK (costo_total >= 0),
    FOREIGN KEY (id_orden) REFERENCES OrdenesTrabajo(id_orden),
    FOREIGN KEY (id_material) REFERENCES Materiales(id_material)
);
GO

-- Tabla: ComprobantesPago
CREATE TABLE ComprobantesPago (
    id_comprobante INT PRIMARY KEY IDENTITY(1,1),
    id_orden INT NOT NULL,
    monto DECIMAL(10, 2) NOT NULL CHECK (monto > 0),
    fecha_emision DATE NOT NULL DEFAULT GETDATE(),
    metodo_pago VARCHAR(50) NOT NULL CHECK (metodo_pago IN ('Efectivo', 'Tarjeta', 'Transferencia')),
    estado_pago VARCHAR(20) NOT NULL DEFAULT 'Pendiente' CHECK (estado_pago IN ('Pendiente', 'Pagado')),
    FOREIGN KEY (id_orden) REFERENCES OrdenesTrabajo(id_orden)
);
GO

-- Tabla: ReportesOperativos
CREATE TABLE ReportesOperativos (
    id_reporte INT PRIMARY KEY IDENTITY(1,1),
    fecha_generacion DATE NOT NULL DEFAULT GETDATE(),
    tipo_reporte VARCHAR(50) NOT NULL CHECK (tipo_reporte IN ('Inventario', 'Ordenes', 'Empleados')),
    datos TEXT,
    estado_exportacion VARCHAR(20) NOT NULL DEFAULT 'Pendiente' CHECK (estado_exportacion IN ('Pendiente', 'Exportado'))
);
GO