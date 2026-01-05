-- Script corregido para agregar columna costo_mano_obra a la tabla OrdenesTrabajo
-- Ejecutar este script en SQL Server Management Studio

USE CarroceriaAlvaradoDB;
GO

-- 1. Agregar la columna costo_mano_obra (nombre correcto de tabla: OrdenesTrabajo)
ALTER TABLE OrdenesTrabajo
ADD costo_mano_obra DECIMAL(10, 2) DEFAULT 0;
GO

-- 2. Actualizar órdenes existentes con el costo calculado
UPDATE ot
SET ot.costo_mano_obra = ISNULL(
    (
        SELECT SUM(
            DATEDIFF(day, ot.fecha_inicio, ISNULL(ot.fecha_fin, GETDATE())) * 8 * e.costo_hora
        )
        FROM AsignacionesOrdenEmpleado ea
        JOIN Empleados e ON ea.id_empleado = e.id_empleado
        WHERE ea.id_orden = ot.id_orden
    ), 0
)
FROM OrdenesTrabajo ot
WHERE ot.costo_mano_obra IS NULL OR ot.costo_mano_obra = 0;
GO

-- 3. Verificar que la columna se agregó correctamente
SELECT TOP 10 
    id_orden,
    fecha_inicio,
    fecha_fin,
    costo_mano_obra,
    total_orden
FROM OrdenesTrabajo
ORDER BY id_orden DESC;
GO

PRINT 'Columna costo_mano_obra agregada exitosamente a OrdenesTrabajo';
