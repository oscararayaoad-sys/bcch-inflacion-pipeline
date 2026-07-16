"""
Etapa 1 - EXTRACT
Extraccion de series desde la API REST de la BDE del Banco Central de Chile.
"""
import pandas as pd
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_series(codigo, desde="2015-01-01", hasta="2025-12-31"):
    """
    Extrae una serie temporal desde la API del Banco central de Chile.
    
    Parametros:
        codigo(str): seriesId del BCCh
        desde(str): fecha inicial (YYYY-MM-DD)
        hasta(str): fecha final (YYYY-MM-DD)
    Devuelve:
        pd.DataFrame con ["fecha", "valor"], raw sin procesar.
    Lanza:
        ValueError si la API rechaza la peticion (Codigo != 0).
    """
    usuario = os.getenv("BCCH_USER")
    password = os.getenv("BCCH_PASS") 

    url =  "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"
    params = {
        "user": usuario,
        "pass": password,
        "function": "GetSeries",
        "timeseries": codigo,
        "firstdate": desde,
        "lastdate": hasta,
    }

    respuesta = requests.get(url, params=params, timeout=30)
    datos = respuesta.json()

    #Chequeo explicito
    if datos.get("Codigo") != 0:
        raise ValueError(
            f"La API del BCCh rechazo la serie '{codigo}': {datos.get('Descripcion')}"
        )

    observaciones = datos["Series"]["Obs"]
    df = pd.DataFrame(observaciones)
    df["fecha"] = pd.to_datetime(df["indexDateString"], format="%d-%m-%Y")
    df["valor"] = df["value"].astype(float)
    df = df [["fecha", "valor"]].sort_values("fecha").reset_index(drop=True)

    return df

if __name__ == "__main__":
    #Bloque no ejecutable sin 'python extract.py'; se ignora al importar.
    df_ipc = get_series("G073.IPC.IND.2023.M")
    df_uf = get_series("F073.UFF.PRE.Z.D")

    df_ipc.to_csv("C:/Users/OAD/Documents/bcentral-inflacion/bcch-inflacion-pipeline/data/raw/ipc_raw.csv", index=False)
    df_uf.to_csv("C:/Users/OAD/Documents/bcentral-inflacion/bcch-inflacion-pipeline/data/raw/uf_raw.csv", index=False)
    
    print(f"IPC extraido: {df_ipc.shape}, guardado en data/raw/ipc_raw.csv")
    print(f"UF extraido: {df_uf.shape}, guardado en data/raw/uf_raw.csv")