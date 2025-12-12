-- Script para agregar el campo costo_hora a la tabla Empleados
-- Fecha: 2025-12-11
-- Descripción: Agrega columna para almacenar el costo por hora de trabajo de cada empleado

USE CarroceriaAlvaradoDB;
GO

-- Verificar si la columna ya existe antes de agregarla
IF NOT EXISTS (
    SELECT * FROM sys.columns 
    WHERE object_id = OBJECT_ID(N'dbo.Empleados') 
    AND name = 'costo_hora'
)
BEGIN
    ALTER TABLE Empleados
    ADD costo_hora DECIMAL(10, 2) NOT NULL DEFAULT 0.00 
        CHECK (costo_hora >= 0);
    
    PRINT 'Columna costo_hora agregada exitosamente a la tabla Empleados.';
END
ELSE
BEGIN
    PRINT 'La columna costo_hora ya existe en la tabla Empleados.';
END
GO
