"""
Etapa 2 - TRANSFORM
Limpieza y trabajo de series temporales con pandas:
datetime index, resample() para alinear frecuencias (IPC mensual + UF diaria),
variacion interanual (pct_change) y media movil (rolling).
"""

import pandas as pd
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

def procesar_series(df_ipc, df_uf):
    """
    Alinea IPC y UF a frecuencua mensual y calcula indice en base a 100
    
    Parametros:
        df_ipc(pd.DataFrame): IPC (serie cruda), columnas ['fecha', 'valor'] (mensual).
        df_uf (pd.DataFrame): UF (serie cruda), columnas ['fecha', 'valor'] (diaria).
    Devuelve:
        pd.DataFrame con ['mes', 'ipc_valor', 'uf_valor', 'indice_ipc', 'indice_uf'].
    """

    #UF diaria a mensual (ultimo valor de cada mes).
    uf_mensual = df_uf.set_index("fecha")["valor"].resample("ME").last()
    uf_mensual = uf_mensual.reset_index()
    uf_mensual.columns = ["fecha", "uf_valor"]

    #Formateamos columnas de fechas.
    df_ipc["mes"] = df_ipc["fecha"].dt.to_period("M")
    uf_mensual["mes"] = uf_mensual["fecha"].dt.to_period("M")

    #Merge.
    df_final = df_ipc.merge(uf_mensual, on="mes", how="inner", suffixes=("_ipc", "_uf"))
    df_final = df_final.rename(columns={"valor": "ipc_valor"})
    df_final = df_final[["mes", "ipc_valor", "uf_valor"]]

    #Indice en base a 100 (¿Cuanto vale hoy lo que valia 100 al inicio?)
    base_ipc = df_final["ipc_valor"].iloc[0]
    base_uf = df_final["uf_valor"].iloc[0]
    df_final["indice_ipc"] = (df_final["ipc_valor"] / base_ipc) * 100
    df_final["indice_uf"] = (df_final["uf_valor"] / base_uf) * 100

    #Variacion interanual IPC
    df_final["ipc_var_anual"] = df_final["ipc_valor"].pct_change(periods=12) * 100

    #Correccion de error posterior (transformacion involuntaria de fechas)
    df_final["mes"] = df_final["mes"].dt.to_timestamp()

    return df_final

if __name__ == "__main__":
    #Bloque no ejecutable sin 'python transform.py'; se ignora al importar.
    df_ipc = pd.read_csv(RAIZ / "data" / "raw" / "ipc_raw.csv", parse_dates=["fecha"])
    df_uf = pd.read_csv(RAIZ / "data" / "raw" / "ipc_raw.csv", parse_dates=["fecha"])

    df_final = procesar_series(df_ipc, df_uf)

    df_final.to_csv(RAIZ / "data" / "processed" / "inflacion_procesada.csv", index=False)
    print(f"Procesado: {df_final.shape}, guardado en data/processed/inflacion_procesada.csv")