-- Script para agregar columna costo_mano_obra a la tabla Ordenes_de_Trabajo
-- Ejecutar este script en SQL Server Management Studio

USE CarroceriaAlvaradoDB;
GO

-- 1. Agregar la columna costo_mano_obra
ALTER TABLE Ordenes_de_Trabajo
ADD costo_mano_obra DECIMAL(10, 2) DEFAULT 0;
GO

-- 2. Actualizar órdenes existentes con el costo calculado
-- Nota: Este cálculo asume que las fechas y empleados están correctamente asignados
UPDATE ot
SET ot.costo_mano_obra = ISNULL(
    (
        SELECT SUM(
            DATEDIFF(day, ot.fecha_inicio, ISNULL(ot.fecha_fin, GETDATE())) * 8 * e.costo_hora
        )
        FROM Empleados_Asignados ea
        JOIN Empleados e ON ea.id_empleado = e.id_empleado
        WHERE ea.id_orden = ot.id_orden
    ), 0
)
FROM Ordenes_de_Trabajo ot
WHERE ot.costo_mano_obra IS NULL OR ot.costo_mano_obra = 0;
GO

-- 3. Verificar que la columna se agregó correctamente
SELECT TOP 10 
    id_orden,
    fecha_inicio,
    fecha_fin,
    costo_mano_obra,
    total_orden
FROM Ordenes_de_Trabajo
ORDER BY id_orden DESC;
GO

PRINT 'Columna costo_mano_obra agregada exitosamente';
