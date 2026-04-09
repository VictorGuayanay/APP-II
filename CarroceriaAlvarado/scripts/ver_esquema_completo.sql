-- ================================================================
-- ESQUEMA COMPLETO DE LA BASE DE DATOS: CarroceriaAlvaradoDB
-- ================================================================
-- Este script muestra la estructura completa de la BD
-- ================================================================

USE CarroceriaAlvaradoDB;
GO

PRINT '╔════════════════════════════════════════════════════════════════╗';
PRINT '║        ESQUEMA COMPLETO - CarroceriaAlvaradoDB                ║';
PRINT '╚════════════════════════════════════════════════════════════════╝';
PRINT '';

-- ================================================================
-- LISTAR TODAS LAS TABLAS
-- ================================================================
PRINT '📋 TABLAS EN LA BASE DE DATOS:';
PRINT '═════════════════════════════════════════════════════════════════';

SELECT 
    TABLE_NAME AS 'Tabla'
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;

PRINT '';
PRINT '';

-- ================================================================
-- ESTRUCTURA DE CADA TABLA (DETALLADA)
-- ================================================================

DECLARE @table_name NVARCHAR(128);
DECLARE @table_cursor CURSOR;

SET @table_cursor = CURSOR FOR
SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_NAME;

OPEN @table_cursor;
FETCH NEXT FROM @table_cursor INTO @table_name;

WHILE @@FETCH_STATUS = 0
BEGIN
    PRINT '──────────────────────────────────────────────────────────────';
    PRINT 'TABLA: ' + @table_name;
    PRINT '──────────────────────────────────────────────────────────────';
    
    DECLARE @sql NVARCHAR(MAX) = '
    SELECT 
        COLUMN_NAME AS ''Columna'',
        DATA_TYPE AS ''Tipo Dato'',
        CHARACTER_MAXIMUM_LENGTH AS ''Longitud'',
        IS_NULLABLE AS ''Permite NULL'',
        COLUMNPROPERTY(OBJECT_ID(''' + @table_name + '''), COLUMN_NAME, ''IsIdentity'') AS ''Es Identity'',
        COLUMN_DEFAULT AS ''Valor Defecto''
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = ''' + @table_name + '''
    ORDER BY ORDINAL_POSITION';
    
    EXEC sp_executesql @sql;
    
    PRINT '';
    PRINT '';
    
    FETCH NEXT FROM @table_cursor INTO @table_name;
END;

CLOSE @table_cursor;
DEALLOCATE @table_cursor;

-- ================================================================
-- RELACIONES / FOREIGN KEYS
-- ================================================================
PRINT '──────────────────────────────────────────────────────────────';
PRINT '🔗 FOREIGN KEYS (RELACIONES ENTRE TABLAS):';
PRINT '──────────────────────────────────────────────────────────────';

SELECT 
    CONSTRAINT_NAME AS 'Restricción',
    TABLE_NAME AS 'Tabla Origen',
    COLUMN_NAME AS 'Columna Origen',
    REFERENCED_TABLE_NAME AS 'Tabla Destino',
    REFERENCED_COLUMN_NAME AS 'Columna Destino'
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE REFERENCED_TABLE_NAME IS NOT NULL
ORDER BY TABLE_NAME, CONSTRAINT_NAME;

PRINT '';
PRINT '';

-- ================================================================
-- ÍNDICES
-- ================================================================
PRINT '──────────────────────────────────────────────────────────────';
PRINT '⚡ ÍNDICES:';
PRINT '──────────────────────────────────────────────────────────────';

SELECT 
    i.name AS 'Índice',
    t.name AS 'Tabla',
    c.name AS 'Columna'
FROM sys.indexes i
JOIN sys.tables t ON i.object_id = t.object_id
JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
WHERE t.schema_id = SCHEMA_ID('dbo')
ORDER BY t.name, i.name;

PRINT '';
PRINT '';

-- ================================================================
-- DATOS ACTUALES EN TABLAS PRINCIPALES
-- ================================================================
PRINT '──────────────────────────────────────────────────────────────';
PRINT '📊 DATOS ACTUALES:';
PRINT '──────────────────────────────────────────────────────────────';

PRINT '';
PRINT 'Tabla: Rol';
PRINT '─────────────────────────────────────────────────────────────';
SELECT * FROM Rol;

PRINT '';
PRINT 'Tabla: Usuarios';
PRINT '─────────────────────────────────────────────────────────────';
SELECT * FROM Usuarios;

PRINT '';
PRINT 'Tabla: Rol_Usuario';
PRINT '─────────────────────────────────────────────────────────────';
SELECT * FROM Rol_Usuario;

PRINT '';
PRINT '╔════════════════════════════════════════════════════════════════╗';
PRINT '║                  FIN DEL ESQUEMA                               ║';
PRINT '╚════════════════════════════════════════════════════════════════╝';

GO
