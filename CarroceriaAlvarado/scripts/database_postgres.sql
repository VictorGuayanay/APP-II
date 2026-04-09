-- =====================================================
-- Base de Datos: CarroceriaAlvaradoDB - PostgreSQL
-- Descripción: Script COMPLETO para crear la base de datos
--              en PostgreSQL (migrado desde SQL Server)
-- Generado desde: scripts SQL + análisis completo de app.py
-- =====================================================

-- Crear la base de datos (ejecutar por separado si es necesario)
-- CREATE DATABASE "CarroceriaAlvaradoDB";

-- Conectarse a la base de datos antes de ejecutar el resto:
-- \c CarroceriaAlvaradoDB

-- =====================================================
-- TABLAS INDEPENDIENTES (sin foreign keys a otras tablas)
-- =====================================================

-- ==============================
-- Tabla: Usuarios
-- ==============================
CREATE TABLE Usuarios (
    id_usuario SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash BYTEA NOT NULL,
    rol VARCHAR(50) NOT NULL,
    estado SMALLINT NOT NULL DEFAULT 1,              -- 1=Activo, 0=Inactivo (BIT en SQL Server)
    intentos_fallidos INT NOT NULL DEFAULT 0,
    bloqueado SMALLINT NOT NULL DEFAULT 0,           -- 1=Bloqueado, 0=Desbloqueado
    reset_token TEXT,
    reset_token_expiry TIMESTAMP
);

-- ==============================
-- Tabla: Empleados
-- ==============================
CREATE TABLE Empleados (
    id_empleado SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    cedula VARCHAR(20) NOT NULL UNIQUE,
    rol VARCHAR(50) NOT NULL,
    telefono VARCHAR(15),
    fecha_contratacion DATE NOT NULL,
    estado SMALLINT NOT NULL DEFAULT 1,              -- 1=Activo, 0=Inactivo
    costo_hora DECIMAL(10, 2) NOT NULL DEFAULT 0.00 CHECK (costo_hora >= 0)
);

-- ==============================
-- Tabla: Clientes
-- ==============================
CREATE TABLE Clientes (
    id_cliente SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    cedula VARCHAR(20) NOT NULL UNIQUE,
    telefono VARCHAR(15),
    email VARCHAR(100),
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo'))
);

-- ==============================
-- Tabla: CategoriaMateriales
-- ==============================
CREATE TABLE CategoriaMateriales (
    id_categoria SERIAL PRIMARY KEY,
    codigo_prefijo VARCHAR(10) NOT NULL UNIQUE,
    nombre_categoria VARCHAR(100) NOT NULL,
    descripcion TEXT,
    estado BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_codigo_prefijo ON CategoriaMateriales(codigo_prefijo);
CREATE INDEX idx_estado_categoria ON CategoriaMateriales(estado);

-- ==============================
-- Tabla: Proveedores
-- ==============================
CREATE TABLE Proveedores (
    id_proveedor SERIAL PRIMARY KEY,
    ruc VARCHAR(13) NOT NULL UNIQUE,
    nombre_proveedor VARCHAR(100) NOT NULL,
    razon_social VARCHAR(150) NOT NULL,
    direccion VARCHAR(255),
    descripcion TEXT,
    telefono VARCHAR(15),
    email VARCHAR(100),
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo')),
    fecha_registro DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE INDEX idx_proveedores_ruc ON Proveedores(ruc);
CREATE INDEX idx_proveedores_nombre ON Proveedores(nombre_proveedor);

COMMENT ON TABLE Proveedores IS 'Tabla que almacena información de proveedores de materiales';

-- ==============================
-- Tabla: Unidades_de_Medida
-- ==============================
CREATE TABLE Unidades_de_Medida (
    id_unidad SERIAL PRIMARY KEY,
    nombre_unidad VARCHAR(50) NOT NULL UNIQUE,
    abreviatura VARCHAR(10) NOT NULL,
    descripcion VARCHAR(200),
    estado VARCHAR(20) DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================
-- Tabla: ReportesOperativos
-- ==============================
CREATE TABLE ReportesOperativos (
    id_reporte SERIAL PRIMARY KEY,
    fecha_generacion DATE NOT NULL DEFAULT CURRENT_DATE,
    tipo_reporte VARCHAR(50) NOT NULL CHECK (tipo_reporte IN ('Inventario', 'Ordenes', 'Empleados')),
    datos TEXT,
    estado_exportacion VARCHAR(20) NOT NULL DEFAULT 'Pendiente' CHECK (estado_exportacion IN ('Pendiente', 'Exportado'))
);

-- =====================================================
-- TABLAS CON DEPENDENCIAS (foreign keys)
-- =====================================================

-- ==============================
-- Tabla: Materiales
-- (depende de: CategoriaMateriales, Proveedores, Unidades_de_Medida, Usuarios)
-- ==============================
CREATE TABLE Materiales (
    id_material SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    cantidad INT NOT NULL DEFAULT 0 CHECK (cantidad >= 0),
    precio_unitario DECIMAL(10, 2) NOT NULL CHECK (precio_unitario >= 0),
    fecha_ultima_actualizacion DATE DEFAULT CURRENT_DATE,

    -- Sistema de doble precio
    precio_compra DECIMAL(10, 2),
    precio_venta DECIMAL(10, 2),
    porcentaje_ganancia INT,

    -- Datos adicionales
    ubicacion VARCHAR(100),
    numero_factura VARCHAR(50),

    -- Categoría y código
    id_categoria INT,
    codigo_material VARCHAR(20) UNIQUE,

    -- Proveedor
    id_proveedor INT,

    -- Unidad de medida
    id_unidad INT,

    -- Auditoría: último usuario que actualizó
    id_usuario_ultima_actualizacion INT,

    -- Foreign Keys
    CONSTRAINT fk_materiales_categoria FOREIGN KEY (id_categoria) REFERENCES CategoriaMateriales(id_categoria),
    CONSTRAINT fk_materiales_proveedores FOREIGN KEY (id_proveedor) REFERENCES Proveedores(id_proveedor) ON DELETE SET NULL,
    CONSTRAINT fk_materiales_unidades FOREIGN KEY (id_unidad) REFERENCES Unidades_de_Medida(id_unidad),
    CONSTRAINT fk_materiales_usuario_actualizacion FOREIGN KEY (id_usuario_ultima_actualizacion) REFERENCES Usuarios(id_usuario)
);

CREATE INDEX idx_codigo_material ON Materiales(codigo_material);
CREATE INDEX idx_id_categoria_material ON Materiales(id_categoria);
CREATE INDEX idx_materiales_proveedor ON Materiales(id_proveedor);

COMMENT ON COLUMN Materiales.id_proveedor IS 'ID del proveedor que suministra este material';

-- ==============================
-- Tabla: OrdenesTrabajo
-- (depende de: Clientes, Usuarios)
-- Nota: Los empleados se asignan a través de AsignacionesOrdenEmpleado
-- ==============================
CREATE TABLE OrdenesTrabajo (
    id_orden SERIAL PRIMARY KEY,
    id_cliente INT NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    descripcion VARCHAR(255) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'En Progreso' CHECK (estado IN ('En Progreso', 'Asignado', 'Completado', 'Finalizado', 'Cancelado')),
    prioridad VARCHAR(20) NOT NULL DEFAULT 'Media' CHECK (prioridad IN ('Baja', 'Media', 'Alta')),

    -- Columnas financieras
    subtotal_materiales DECIMAL(10, 2) DEFAULT 0.00,
    margen_ganancia INT DEFAULT 20 CHECK (margen_ganancia BETWEEN 5 AND 50),
    total_orden DECIMAL(10, 2) DEFAULT 0.00,

    -- IVA
    iva_porcentaje INT DEFAULT 0 CHECK (iva_porcentaje BETWEEN 0 AND 20),
    subtotal_con_margen DECIMAL(10, 2) DEFAULT 0.00,
    monto_iva DECIMAL(10, 2) DEFAULT 0.00,

    -- Mano de obra
    costo_mano_obra DECIMAL(10, 2) DEFAULT 0,

    -- Auditoría
    id_usuario_creador INT,
    fecha_ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_usuario_ultima_actualizacion INT,

    -- Foreign Keys
    CONSTRAINT fk_ordenes_cliente FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente),
    CONSTRAINT fk_ordenes_usuario_creador FOREIGN KEY (id_usuario_creador) REFERENCES Usuarios(id_usuario),
    CONSTRAINT fk_ordenes_usuario_actualizacion FOREIGN KEY (id_usuario_ultima_actualizacion) REFERENCES Usuarios(id_usuario)
);

-- ==============================
-- Tabla: AsignacionesOrdenEmpleado (TABLA PUENTE)
-- (depende de: OrdenesTrabajo, Empleados)
-- Permite asignar MÚLTIPLES empleados a una orden
-- ==============================
CREATE TABLE AsignacionesOrdenEmpleado (
    id_asignacion SERIAL PRIMARY KEY,
    id_orden INT NOT NULL,
    id_empleado INT NOT NULL,

    CONSTRAINT fk_asignacion_orden FOREIGN KEY (id_orden) REFERENCES OrdenesTrabajo(id_orden) ON DELETE CASCADE,
    CONSTRAINT fk_asignacion_empleado FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado),
    CONSTRAINT uq_asignacion_orden_empleado UNIQUE (id_orden, id_empleado)
);

CREATE INDEX idx_asignacion_orden ON AsignacionesOrdenEmpleado(id_orden);
CREATE INDEX idx_asignacion_empleado ON AsignacionesOrdenEmpleado(id_empleado);

-- ==============================
-- Tabla: DetalleOrdenMateriales
-- (depende de: OrdenesTrabajo, Materiales)
-- ==============================
CREATE TABLE DetalleOrdenMateriales (
    id_detalle SERIAL PRIMARY KEY,
    id_orden INT NOT NULL,
    id_material INT NOT NULL,
    cantidad_usada INT NOT NULL CHECK (cantidad_usada > 0),
    costo_total DECIMAL(10, 2) NOT NULL CHECK (costo_total >= 0),

    CONSTRAINT fk_detalle_orden FOREIGN KEY (id_orden) REFERENCES OrdenesTrabajo(id_orden),
    CONSTRAINT fk_detalle_material FOREIGN KEY (id_material) REFERENCES Materiales(id_material)
);

-- ==============================
-- Tabla: ComprobantesPago
-- (depende de: OrdenesTrabajo, Usuarios)
-- ==============================
CREATE TABLE ComprobantesPago (
    id_comprobante SERIAL PRIMARY KEY,
    id_orden INT NOT NULL,
    monto DECIMAL(10, 2) NOT NULL CHECK (monto >= 0),
    fecha_emision TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metodo_pago VARCHAR(50) NOT NULL,
    estado_pago VARCHAR(20) NOT NULL DEFAULT 'Pendiente' CHECK (estado_pago IN ('Pendiente', 'Pagado')),

    -- Auditoría
    id_usuario_registrador INT,
    fecha_ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_usuario_ultima_actualizacion INT,

    CONSTRAINT fk_comprobante_orden FOREIGN KEY (id_orden) REFERENCES OrdenesTrabajo(id_orden),
    CONSTRAINT fk_comprobante_usuario_registrador FOREIGN KEY (id_usuario_registrador) REFERENCES Usuarios(id_usuario),
    CONSTRAINT fk_comprobante_usuario_actualizacion FOREIGN KEY (id_usuario_ultima_actualizacion) REFERENCES Usuarios(id_usuario)
);

-- ==============================
-- Tabla: Ventas_Directas
-- (depende de: Clientes, Usuarios)
-- ==============================
CREATE TABLE Ventas_Directas (
    id_venta SERIAL PRIMARY KEY,
    fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Información del cliente
    tipo_cliente VARCHAR(50) NOT NULL,
    id_cliente INT,
    cliente_ruc_ci VARCHAR(20),
    cliente_nombre VARCHAR(200),
    cliente_telefono VARCHAR(20),
    cliente_email VARCHAR(100),

    -- Totales de la venta
    subtotal_general DECIMAL(10, 2) NOT NULL,
    ganancia_general DECIMAL(10, 2) NOT NULL,
    iva_general DECIMAL(10, 2) NOT NULL,
    total_general DECIMAL(10, 2) NOT NULL,

    -- Información de pago
    forma_pago VARCHAR(50) NOT NULL,

    -- Usuario que registró
    id_usuario INT NOT NULL,
    nombre_usuario VARCHAR(100),

    comprobante_generado BOOLEAN DEFAULT FALSE,

    CONSTRAINT fk_ventas_cliente FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente),
    CONSTRAINT fk_ventas_usuario FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
);

CREATE INDEX idx_fecha_venta ON Ventas_Directas(fecha_venta);
CREATE INDEX idx_tipo_cliente ON Ventas_Directas(tipo_cliente);
CREATE INDEX idx_forma_pago ON Ventas_Directas(forma_pago);

-- ==============================
-- Tabla: Detalle_Venta_Directa
-- (depende de: Ventas_Directas, Materiales)
-- ==============================
CREATE TABLE Detalle_Venta_Directa (
    id_detalle SERIAL PRIMARY KEY,
    id_venta INT NOT NULL,
    id_material INT NOT NULL,
    nombre_material VARCHAR(200) NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    porcentaje_ganancia INT NOT NULL,
    ganancia DECIMAL(10, 2) NOT NULL,
    porcentaje_iva INT NOT NULL,
    valor_iva DECIMAL(10, 2) NOT NULL,
    total DECIMAL(10, 2) NOT NULL,

    CONSTRAINT fk_detalle_venta FOREIGN KEY (id_venta) REFERENCES Ventas_Directas(id_venta) ON DELETE CASCADE,
    CONSTRAINT fk_detalle_venta_material FOREIGN KEY (id_material) REFERENCES Materiales(id_material)
);

CREATE INDEX idx_id_venta_detalle ON Detalle_Venta_Directa(id_venta);

-- =====================================================
-- DATOS INICIALES
-- =====================================================

-- Unidades de Medida
INSERT INTO Unidades_de_Medida (nombre_unidad, abreviatura, descripcion) VALUES
    ('Unidad', 'Ud', 'Unidad individual'),
    ('Kilogramo', 'kg', 'Unidad de masa'),
    ('Gramo', 'g', 'Unidad de masa'),
    ('Litro', 'L', 'Unidad de volumen'),
    ('Mililitro', 'ml', 'Unidad de volumen'),
    ('Metro', 'm', 'Unidad de longitud'),
    ('Centímetro', 'cm', 'Unidad de longitud'),
    ('Metro cuadrado', 'm²', 'Unidad de área'),
    ('Metro cúbico', 'm³', 'Unidad de volumen'),
    ('Caja', 'Caja', 'Empaque de múltiples unidades'),
    ('Paquete', 'Paq', 'Empaque de múltiples unidades'),
    ('Galón', 'Gal', 'Unidad de volumen'),
    ('Pieza', 'Pza', 'Unidad individual');

-- Categorías de Materiales
INSERT INTO CategoriaMateriales (codigo_prefijo, nombre_categoria, descripcion, estado) VALUES
    ('ACA', 'Accesorios', 'Accesorios varios para vehículos', TRUE),
    ('ACC', 'Accesorios Complementarios', 'Complementos y accesorios adicionales', TRUE),
    ('AIR', 'Aire y Neumáticos', 'Componentes de aire y neumáticos', TRUE),
    ('CAR', 'Carrocería', 'Partes y componentes de carrocería', TRUE),
    ('CAU', 'Cauchos', 'Cauchos, gomas y sellos', TRUE),
    ('ELE', 'Eléctrico', 'Componentes y accesorios eléctricos', TRUE),
    ('FER', 'Ferretería', 'Herramientas y materiales de ferretería', TRUE),
    ('PIN', 'Pinturas', 'Pinturas, lacas y barnices', TRUE);

-- Proveedores de ejemplo
INSERT INTO Proveedores (ruc, nombre_proveedor, razon_social, direccion, descripcion, telefono, email) VALUES
    ('1234567890001', 'Proveedor ABC', 'ABC Suministros S.A.', 'Av. Principal 123, Riobamba', 'Proveedor de materiales de construcción', '032-123456', 'contacto@abc.com'),
    ('0987654321001', 'Distribuidora XYZ', 'XYZ Distribuciones Ltda.', 'Calle Secundaria 456, Riobamba', 'Distribuidor de herramientas y equipos', '032-654321', 'ventas@xyz.com');

-- =====================================================
-- RESUMEN DE TABLAS (14 tablas en total)
-- =====================================================
-- 1.  Usuarios                    - Usuarios del sistema con auth y bloqueo
-- 2.  Empleados                   - Empleados con costo por hora
-- 3.  Clientes                    - Clientes de la carrocería
-- 4.  CategoriaMateriales         - Categorías para clasificar materiales
-- 5.  Proveedores                 - Proveedores de materiales
-- 6.  Unidades_de_Medida          - Unidades de medida (kg, m, etc.)
-- 7.  ReportesOperativos          - Reportes generados por el sistema
-- 8.  Materiales                  - Inventario de materiales con doble precio
-- 9.  OrdenesTrabajo              - Órdenes de trabajo con financieros e IVA
-- 10. AsignacionesOrdenEmpleado   - Tabla puente: empleados ↔ órdenes (N:M)
-- 11. DetalleOrdenMateriales      - Materiales usados por orden
-- 12. ComprobantesPago            - Comprobantes de pago por orden
-- 13. Ventas_Directas             - Ventas directas de materiales
-- 14. Detalle_Venta_Directa       - Detalle de productos por venta directa

-- =====================================================
-- NOTAS DE MIGRACIÓN SQL Server → PostgreSQL
-- =====================================================
-- 1.  IDENTITY(1,1)   → SERIAL (auto-incremento)
-- 2.  GETDATE()       → CURRENT_DATE / CURRENT_TIMESTAMP
-- 3.  BIT             → SMALLINT (0/1) o BOOLEAN según uso en el backend
-- 4.  VARBINARY       → BYTEA
-- 5.  NVARCHAR        → VARCHAR (PostgreSQL ya soporta Unicode)
-- 6.  DATETIME        → TIMESTAMP
-- 7.  GO              → eliminado (no existe en PostgreSQL)
-- 8.  USE database    → \c database (comando psql)
-- 9.  sp_addextendedproperty → COMMENT ON
-- 10. @@IDENTITY      → usar RETURNING id_columna en INSERT
-- 11. TOP (n)         → LIMIT n
-- 12. ISNULL()        → COALESCE()
-- 13. DATEDIFF()      → uso de operadores de fecha nativos
-- 14. SELECT @@IDENTITY → INSERT ... RETURNING id_columna
