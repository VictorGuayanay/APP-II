# Diccionario de Datos - Sistema Carrocería Alvarado
## Base de Datos: CarroceriaAlvaradoDB

---

## 📋 Tabla 1: Usuarios

**Descripción:** Almacena información de los usuarios del sistema con credenciales de acceso.

| Campo | Tipo de Dato | Nulo | Clave | Descripción | Valores Válidos |
|-------|--------------|------|-------|-------------|-----------------|
| `id_usuario` | INT IDENTITY(1,1) | NO | PK | Identificador único del usuario | Auto-generado |
| `nombre` | NVARCHAR(255) | NO | - | Nombre completo del usuario | Texto alfanumérico |
| `email` | NVARCHAR(255) | NO | UNIQUE | Correo electrónico (login) | Formato email válido |
| `password_hash` | NVARCHAR(255) | NO | - | Contraseña encriptada con bcrypt | Hash bcrypt |
| `rol` | NVARCHAR(50) | NO | - | Rol del usuario en el sistema | 'Administrador', 'Supervisor', 'Empleado' |
| `estado` | BIT | NO | - | Estado activo/inactivo del usuario | 1 (activo), 0 (inactivo) |
| `fecha_creacion` | DATETIME | NO | - | Fecha y hora de creación del usuario | Timestamp automático |
| `intentos_fallidos` | INT | NO | - | Contador de intentos de login fallidos | 0-5 (máximo configurado) |
| `bloqueado_hasta` | DATETIME | SÍ | - | Fecha hasta la cual el usuario está bloqueado | NULL o fecha futura |

**Restricciones:**
- `email` debe ser único
- `rol` debe ser uno de los valores permitidos
- `intentos_fallidos` máximo 5 antes de bloqueo

---

## 📋 Tabla 2: Clientes

**Descripción:** Almacena información de los clientes que solicitan servicios de carrocería.

| Campo | Tipo de Dato | Nulo | Clave | Descripción | Valores Válidos |
|-------|--------------|------|-------|-------------|-----------------|
| `id_cliente` | INT IDENTITY(1,1) | NO | PK | Identificador único del cliente | Auto-generado |
| `nombre` | NVARCHAR(255) | NO | - | Nombre completo o razón social | Texto alfanumérico |
| `cedula_ruc` | NVARCHAR(20) | NO | UNIQUE | Cédula o RUC del cliente | 10 o 13 dígitos |
| `telefono` | NVARCHAR(20) | SÍ | - | Número de teléfono de contacto | Formato telefónico |
| `email` | NVARCHAR(255) | SÍ | - | Correo electrónico del cliente | Formato email válido o NULL |
| `direccion` | NVARCHAR(500) | SÍ | - | Dirección física del cliente | Texto libre o NULL |
| `fecha_registro` | DATETIME | NO | - | Fecha de registro en el sistema | Timestamp automático |
| `estado` | BIT | NO | - | Estado activo/inactivo | 1 (activo), 0 (inactivo) |

**Restricciones:**
- `cedula_ruc` debe ser único
- `cedula_ruc` debe tener 10 o 13 caracteres numéricos

---

## 📋 Tabla 3: Empleados

**Descripción:** Almacena información de los empleados que trabajan en las órdenes.

| Campo | Tipo de Dato | Nulo | Clave | Descripción | Valores Válidos |
|-------|--------------|------|-------|-------------|-----------------|
| `id_empleado` | INT IDENTITY(1,1) | NO | PK | Identificador único del empleado | Auto-generado |
| `nombre` | NVARCHAR(255) | NO | - | Nombre completo del empleado | Texto alfanumérico |
| `cedula` | NVARCHAR(10) | NO | UNIQUE | Cédula de identidad | 10 dígitos |
| `rol` | NVARCHAR(100) | NO | - | Especialidad o cargo del empleado | 'Pintor', 'Electricista', 'Enderezador', 'Tapicero', 'Mecánico' |
| `telefono` | NVARCHAR(20) | SÍ | - | Número de teléfono | Formato telefónico o NULL |
| `email` | NVARCHAR(255) | SÍ | - | Correo electrónico | Formato email válido o NULL |
| `costo_hora` | DECIMAL(10,2) | NO | - | Costo por hora de trabajo | Valor > 0, típicamente 5.00-20.00 |
| `fecha_contratacion` | DATE | SÍ | - | Fecha de ingreso a la empresa | Fecha válida o NULL |
| `estado` | BIT | NO | - | Estado activo/inactivo | 1 (activo), 0 (inactivo) |

**Restricciones:**
- `cedula` debe ser único
- `costo_hora` debe ser mayor a 0
- `rol` debe coincidir con especialidades definidas

---

## 📋 Tabla 4: Unidades_de_Medida

**Descripción:** Catálogo de unidades de medida para materiales.

| Campo | Tipo de Dato | Nulo | Clave | Descripción | Valores Válidos |
|-------|--------------|------|-------|-------------|-----------------|
| `id_unidad` | INT IDENTITY(1,1) | NO | PK | Identificador único de la unidad | Auto-generado |
| `nombre` | NVARCHAR(50) | NO | UNIQUE | Nombre de la unidad de medida | 'Unidad', 'Metro', 'Litro', 'Kilogramo', 'Caja', etc. |
| `abreviatura` | NVARCHAR(10) | NO | - | Abreviatura de la unidad | 'ud', 'm', 'L', 'kg', 'cj', etc. |
| `descripcion` | NVARCHAR(255) | SÍ | - | Descripción adicional | Texto libre o NULL |

**Restricciones:**
- `nombre` debe ser único

---

## 📋 Tabla 5: Materiales

**Descripción:** Inventario de materiales disponibles para usar en órdenes de trabajo.

| Campo | Tipo de Dato | Nulo | Clave | Descripción | Valores Válidos |
|-------|--------------|------|-------|-------------|-----------------|
| `id_material` | INT IDENTITY(1,1) | NO | PK | Identificador único del material | Auto-generado |
| `nombre` | NVARCHAR(255) | NO | - | Nombre descriptivo del material | Texto alfanumérico |
| `descripcion` | NVARCHAR(MAX) | SÍ | - | Descripción detallada del material | Texto libre o NULL |
| `cantidad_stock` | INT | NO | - | Cantidad disponible en inventario | Entero >= 0 |
| `precio_unitario` | DECIMAL(10,2) | NO | - | Precio por unidad del material | Valor >= 0 |
| `id_unidad` | INT | SÍ | FK | Unidad de medida del material | Referencia a Unidades_de_Medida |
| `ubicacion` | NVARCHAR(255) | SÍ | - | Ubicación física en bodega | Texto libre o NULL |
| `factura` | NVARCHAR(100) | SÍ | - | Número de factura de compra | Texto alfanumérico o NULL |
| `umbral_stock_bajo` | INT | NO | - | Cantidad mínima antes de alerta | Entero >= 0, típicamente 10 |
| `estado` | BIT | NO | - | Estado activo/inactivo | 1 (activo), 0 (inactivo) |

**Restricciones:**
- `cantidad_stock` >= 0
- `precio_unitario` >= 0
- `umbral_stock_bajo` >= 0
- FK: `id_unidad` → `Unidades_de_Medida(id_unidad)`

---

## 📋 Tabla 6: OrdenesTrabajo

**Descripción:** Órdenes de trabajo solicitadas por clientes.

| Campo | Tipo de Dato | Nulo | Clave | Descripción | Valores Válidos |
|-------|--------------|------|-------|-------------|-----------------|
| `id_orden` | INT IDENTITY(1,1) | NO | PK | Identificador único de la orden | Auto-generado |
| `id_cliente` | INT | NO | FK | Cliente que solicita el trabajo | Referencia a Clientes |
| `fecha_inicio` | DATE | NO | - | Fecha de inicio del trabajo | Fecha válida |
| `fecha_fin` | DATE | SÍ | - | Fecha de finalización del trabajo | Fecha >= fecha_inicio o NULL |
| `descripcion` | NVARCHAR(MAX) | NO | - | Descripción del trabajo a realizar | Texto libre |
| `estado` | NVARCHAR(50) | NO | - | Estado actual de la orden | 'Asignado', 'En Proceso', 'Finalizado', 'Cancelado' |
| `subtotal_materiales` | DECIMAL(10,2) | NO | - | Suma de costos de materiales | Valor >= 0 |
| `margen_ganancia` | INT | NO | - | Porcentaje de margen de ganancia | 5-50 (%) |
| `iva_porcentaje` | INT | NO | - | Porcentaje de IVA aplicado | 0, 10, 12, 15 (%) |
| `subtotal_con_margen` | DECIMAL(10,2) | NO | - | Subtotal materiales + margen | Calculado |
| `monto_iva` | DECIMAL(10,2) | NO | - | Monto del IVA calculado | Calculado |
| `total_orden` | DECIMAL(10,2) | NO | - | Total final a cobrar | Calculado |
| `costo_mano_obra` | DECIMAL(10,2) | NO | - | Costo total de mano de obra | Calculado y persistido |
| `id_usuario_creador` | INT | NO | FK | Usuario que creó la orden | Referencia a Usuarios |
| `fecha_ultima_actualizacion` | DATETIME | NO | - | Última modificación | Timestamp automático |
| `id_usuario_ultima_actualizacion` | INT | NO | FK | Usuario que hizo última modificación | Referencia a Usuarios |

**Restricciones:**
- `fecha_fin` >= `fecha_inicio` (si no es NULL)
- `margen_ganancia` entre 5 y 50
- `iva_porcentaje` entre 0 y 20
- `subtotal_materiales` >= 0
- `total_orden` >= 0
- `costo_mano_obra` >= 0
- FK: `id_cliente` → `Clientes(id_cliente)`
- FK: `id_usuario_creador` → `Usuarios(id_usuario)`
- FK: `id_usuario_ultima_actualizacion` → `Usuarios(id_usuario)`

**Cálculos:**
```
subtotal_con_margen = subtotal_materiales × (1 + margen_ganancia/100)
monto_iva = subtotal_con_margen × (iva_porcentaje/100)
total_orden = subtotal_con_margen + monto_iva
costo_mano_obra = Σ(días_laborales × 8 horas × costo_hora_empleado)
```

---

## 📋 Tabla 7: AsignacionesOrdenEmpleado

**Descripción:** Relación muchos a muchos entre órdenes y empleados asignados.

| Campo | Tipo de Dato | Nulo | Clave | Descripción | Valores Válidos |
|-------|--------------|------|-------|-------------|-----------------|
| `id_asignacion` | INT IDENTITY(1,1) | NO | PK | Identificador único de la asignación | Auto-generado |
| `id_orden` | INT | NO | FK | Orden de trabajo | Referencia a OrdenesTrabajo |
| `id_empleado` | INT | NO | FK | Empleado asignado | Referencia a Empleados |
| `fecha_asignacion` | DATETIME | NO | - | Fecha de asignación | Timestamp automático |

**Restricciones:**
- Combinación (`id_orden`, `id_empleado`) debe ser única
- FK: `id_orden` → `OrdenesTrabajo(id_orden)` ON DELETE CASCADE
- FK: `id_empleado` → `Empleados(id_empleado)`

---

## 📋 Tabla 8: DetalleOrdenMateriales

**Descripción:** Materiales utilizados en cada orden de trabajo.

| Campo | Tipo de Dato | Nulo | Clave | Descripción | Valores Válidos |
|-------|--------------|------|-------|-------------|-----------------|
| `id_detalle` | INT IDENTITY(1,1) | NO | PK | Identificador único del detalle | Auto-generado |
| `id_orden` | INT | NO | FK | Orden de trabajo | Referencia a OrdenesTrabajo |
| `id_material` | INT | NO | FK | Material utilizado | Referencia a Materiales |
| `cantidad_usada` | DECIMAL(10,2) | NO | - | Cantidad del material utilizado | Valor > 0 |
| `costo_total` | DECIMAL(10,2) | NO | - | Costo total (cantidad × precio_unitario) | Valor >= 0 |
| `fecha_registro` | DATETIME | NO | - | Fecha de registro del uso | Timestamp automático |

**Restricciones:**
- `cantidad_usada` > 0
- `costo_total` >= 0
- FK: `id_orden` → `OrdenesTrabajo(id_orden)` ON DELETE CASCADE
- FK: `id_material` → `Materiales(id_material)`

**Cálculo:**
```
costo_total = cantidad_usada × precio_unitario (del material)
```

---

## 🔗 Diagrama de Relaciones

```
Usuarios (1) ──────┬──────> (N) OrdenesTrabajo [id_usuario_creador]
                   └──────> (N) OrdenesTrabajo [id_usuario_ultima_actualizacion]

Clientes (1) ─────────────> (N) OrdenesTrabajo

OrdenesTrabajo (1) ───────> (N) AsignacionesOrdenEmpleado
                    └──────> (N) DetalleOrdenMateriales

Empleados (1) ────────────> (N) AsignacionesOrdenEmpleado

Materiales (1) ───────────> (N) DetalleOrdenMateriales

Unidades_de_Medida (1) ──> (N) Materiales
```

---

## 📊 Resumen de Tablas

| Tabla | Registros Típicos | Propósito Principal |
|-------|-------------------|---------------------|
| `Usuarios` | 5-20 | Autenticación y autorización |
| `Clientes` | 100-1000+ | Gestión de clientes |
| `Empleados` | 10-50 | Recursos humanos |
| `Unidades_de_Medida` | 10-20 | Catálogo de unidades |
| `Materiales` | 50-500 | Inventario de materiales |
| `OrdenesTrabajo` | 500-5000+ | Órdenes de servicio |
| `AsignacionesOrdenEmpleado` | 500-10000+ | Asignación de recursos |
| `DetalleOrdenMateriales` | 1000-20000+ | Consumo de materiales |

---

## 🔒 Integridad Referencial

### Cascadas Configuradas

| Tabla Padre | Tabla Hija | Acción ON DELETE |
|-------------|------------|------------------|
| `OrdenesTrabajo` | `AsignacionesOrdenEmpleado` | CASCADE |
| `OrdenesTrabajo` | `DetalleOrdenMateriales` | CASCADE |
| `Clientes` | `OrdenesTrabajo` | RESTRICT |
| `Empleados` | `AsignacionesOrdenEmpleado` | RESTRICT |
| `Materiales` | `DetalleOrdenMateriales` | RESTRICT |
| `Usuarios` | `OrdenesTrabajo` | RESTRICT |
| `Unidades_de_Medida` | `Materiales` | RESTRICT |

**Nota:** RESTRICT previene eliminación si existen registros relacionados.

---

## 📝 Índices Recomendados

### Índices de Performance

```sql
-- Búsquedas frecuentes por email
CREATE INDEX IX_Usuarios_Email ON Usuarios(email);
CREATE INDEX IX_Clientes_Email ON Clientes(email);

-- Búsquedas por cédula/RUC
CREATE INDEX IX_Clientes_CedulaRuc ON Clientes(cedula_ruc);
CREATE INDEX IX_Empleados_Cedula ON Empleados(cedula);

-- Filtros por estado
CREATE INDEX IX_OrdenesTrabajo_Estado ON OrdenesTrabajo(estado);
CREATE INDEX IX_Materiales_Estado ON Materiales(estado);

-- Búsquedas por fecha
CREATE INDEX IX_OrdenesTrabajo_FechaInicio ON OrdenesTrabajo(fecha_inicio);
CREATE INDEX IX_OrdenesTrabajo_FechaFin ON OrdenesTrabajo(fecha_fin);

-- Foreign keys (automáticos en SQL Server)
-- Ya existen índices en todas las columnas FK
```

---

## ✅ Validaciones de Negocio

### A Nivel de Base de Datos

```sql
-- Validación de margen de ganancia
ALTER TABLE OrdenesTrabajo 
ADD CONSTRAINT CK_MargenGanancia 
CHECK (margen_ganancia >= 5 AND margen_ganancia <= 50);

-- Validación de IVA
ALTER TABLE OrdenesTrabajo 
ADD CONSTRAINT CK_IVA 
CHECK (iva_porcentaje >= 0 AND iva_porcentaje <= 20);

-- Validación de fechas
ALTER TABLE OrdenesTrabajo 
ADD CONSTRAINT CK_Fechas 
CHECK (fecha_fin IS NULL OR fecha_fin >= fecha_inicio);

-- Validación de stock
ALTER TABLE Materiales 
ADD CONSTRAINT CK_Stock 
CHECK (cantidad_stock >= 0);

-- Validación de costo hora
ALTER TABLE Empleados 
ADD CONSTRAINT CK_CostoHora 
CHECK (costo_hora > 0);
```

---

## 🎯 Valores por Defecto

| Tabla | Campo | Valor Default |
|-------|-------|---------------|
| `Usuarios` | `estado` | 1 (activo) |
| `Usuarios` | `intentos_fallidos` | 0 |
| `Clientes` | `estado` | 1 (activo) |
| `Empleados` | `estado` | 1 (activo) |
| `Materiales` | `estado` | 1 (activo) |
| `Materiales` | `umbral_stock_bajo` | 10 |
| `OrdenesTrabajo` | `estado` | 'Asignado' |
| `OrdenesTrabajo` | `margen_ganancia` | 20 |
| `OrdenesTrabajo` | `iva_porcentaje` | 0 |
| `OrdenesTrabajo` | `costo_mano_obra` | 0 |
