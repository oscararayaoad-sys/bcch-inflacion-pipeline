"""
MAIN - Orquestador del pipeline de inflacion BCCh.
Ejecuta extract -> transform -> load en secuencia, con logging y reintentos.
"""
import time
import logging
from extract import get_series
from transform import procesar_series
from load import crear_engine, cargar_a_postgres

#Configuamos el logging.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/Users/OAD/Documents/bcentral-inflacion/bcch-inflacion-pipeline/logs/pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

#Series
SERIE_IPC = "G073.IPC.IND.2023.M"
SERIE_UF = "F073.UFF.PRE.Z.D"

def extraer_con_reintentos(codigo, nombre, intentos=3, espera=5):
    """
    Llama a get_series con reintentos entre fallos transitorios.
    
    Parametros:
        codigo (str): seriesId del BCCh.
        nombre (str): nombre legible de la serie, para los logs.
        intentos (int): cuantas veces intentar antes de rendirse.
        espera (int): segundos de pausa entre intentos.
    Devuelve:
        pd.DataFrame con la serie extraida.

    Lanza:
        La ultima excepcion si se agotan todos los intentos.
    """
    for intento in range(1, intentos + 1):
        try:
            df = get_series(codigo)
            logger.info(f"Extraccion de {nombre} completada: {df.shape[0]} filas")
            return df
        except Exception as e:
            logger.warning(f"Fallo al extraer {nombre} (intento {intento} de {intentos}): {e}")
            if intento < intentos:
                time.sleep(espera)
            else: 
                logger.error(f"Extraccion de {nombre} fallo tras {intentos} intentos")
                raise

                
def main():
    """
    Ejecuta el pipeline completo de principio a fin.
    """
    logger.info("=== Pipeline iniciado ===")

    try:
        #1. Extract
        df_ipc = extraer_con_reintentos(SERIE_IPC, "IPC")
        df_uf = extraer_con_reintentos(SERIE_UF, "UF")

        #2. Transform
        df_final = procesar_series(df_ipc, df_uf)
        logger.info(f"Transformacion completada: {df_final.shape}")

        #3. Load
        engine = crear_engine()
        n = cargar_a_postgres(df_final, engine)
        logger.info(f"Carga completada: {n} registros en inflacion_mensual")

        logger.info("=== Pipeline finalizado con exito ===")

    except Exception as e:
        logger.error(f"Pipeline abortado por un error: {e}")
        raise


if __name__ == "__main__":
    main()