-- Esquema de la base de datos del pipeline de inflacion BCCh.
-- Crea la tabla destino de la etapa Load.
--
-- Uso:
--   1. Crear la base:   CREATE DATABASE bcch_inflacion;
--   2. Conectarse a ella y ejecutar este archivo:
--      psql -U postgres -d bcch_inflacion -f sql/schema.sql

CREATE TABLE inflacion_mensual (
    mes DATE PRIMARY KEY,                        -- llave primaria: un registro por mes (habilita el upsert idempotente)
    ipc_valor NUMERIC NOT NULL,                  -- IPC empalmado, base 2023=100
    uf_valor NUMERIC NOT NULL,                   -- UF, cierre mensual (en pesos)
    indice_ipc NUMERIC NOT NULL,                 -- IPC normalizado a base 100 = enero 2015
    indice_uf NUMERIC NOT NULL,                  -- UF normalizada a base 100 = enero 2015
    ipc_var_anual NUMERIC,                       -- variacion interanual del IPC (%); NULL en los primeros 12 meses
    fecha_actualizacion TIMESTAMP DEFAULT NOW()  -- auditoria: momento de la ultima carga/actualizacion
);