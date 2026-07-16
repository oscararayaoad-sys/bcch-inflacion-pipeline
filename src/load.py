"""
Etapa 3 - LOAD
Carga idempotente a PostgreSQL (INSERT ... ON CONFLICT) y carga incremental.
Usa SQLAlchemy para la conexion.
"""
import pandas as pd
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def crear_engine():
    """
    Crea el engine de conexion a PostgreSQL usando credenciales del .env .

    Devuelve:
    sqlalchemy.Enginge listo para abrir conexiones.
    """
    pg_user = os.getenv("PG_USER")
    pg_password = os.getenv("PG_PASSWORD")
    pg_host = os.getenv("PG_HOST")
    pg_port = os.getenv("PG_PORT")
    pg_db = os.getenv("PG_DATABASE")

    conection_string = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
    return create_engine(conection_string)

def cargar_a_postgres(df, engine):
    """
    Carga idempotente del DataFrame a la tabla inflacion_mensual. Actualiza meses pre-existentes
    
    Parametros:
        df (pd.DataFrame): tabla procesada con las 5 columnas del pipeline.
        engine (sqlalchemy.Engine): conexion creada por crear_engine().
        
    Devuelve:
        ing: cantidad de registros cargados o actualizados.
    """
    upsert_query = text("""
        INSERT INTO inflacion_mensual (mes, ipc_valor, uf_valor, indice_ipc, indice_uf, ipc_var_anual)
        VALUES (:mes, :ipc_valor, :uf_valor, :indice_ipc, :indice_uf, :ipc_var_anual)
        ON CONFLICT (mes)
        DO UPDATE SET
            ipc_valor = EXCLUDED.ipc_valor,
            uf_valor = EXCLUDED.uf_valor,
            indice_ipc = EXCLUDED.indice_ipc,
            indice_uf = EXCLUDED.indice_uf,
            ipc_var_anual = EXCLUDED.ipc_var_anual,
            fecha_actualizacion = NOW()      
""")
    registros = df.to_dict(orient="records")

    with engine.connect() as conn:
        conn.execute(upsert_query, registros)
        conn.commit()
    
    return len(registros)


if __name__ == "__main__":
    #Bloque no ejecutable sin 'python load.py'; se ignora al importar.
    df_final = pd.read_csv("C:/Users/OAD/Documents/bcentral-inflacion/bcch-inflacion-pipeline/data/processed/inflacion_procesada.csv", parse_dates=["mes"])

    engine = crear_engine()
    n = cargar_a_postgres(df_final, engine)

    print(f"Cargados/actualizados {n} registros en inflacion_mensual.")