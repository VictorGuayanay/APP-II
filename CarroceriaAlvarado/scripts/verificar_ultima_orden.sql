-- Script para verificar si los datos financieros se guardaron correctamente
-- Ejecuta este script en SQL Server Management Studio

-- Ver las últimas 5 órdenes con sus datos financieros
SELECT TOP 5
    id_orden,
    id_cliente,
    fecha_inicio,
    fecha_fin,
    descripcion,
    estado,
    subtotal_materiales,
    margen_ganancia,
    total_orden,
    fecha_ultima_actualizacion
FROM OrdenesTrabajo
ORDER BY id_orden DESC;

-- Ver materiales de la última orden
DECLARE @ultima_orden INT = (SELECT TOP 1 id_orden FROM OrdenesTrabajo ORDER BY id_orden DESC);

SELECT 
    dom.id_detalle,
    dom.id_orden,
    dom.id_material,
    m.nombre AS nombre_material,
    dom.cantidad_usada,
    dom.costo_total
FROM DetalleOrdenMateriales dom
JOIN Materiales m ON dom.id_material = m.id_material
WHERE dom.id_orden = @ultima_orden;

-- Ver empleados asignados a la última orden con su costo_hora
SELECT 
    aoe.id_orden,
    e.id_empleado,
    e.nombre,
    e.rol,
    e.costo_hora
FROM AsignacionesOrdenEmpleado aoe
JOIN Empleados e ON aoe.id_empleado = e.id_empleado
WHERE aoe.id_orden = @ultima_orden;
