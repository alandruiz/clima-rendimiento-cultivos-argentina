import glob
import os

import pandas as pd


def cargar_y_consolidar_cultivos(
    ruta_raw,
    ruta_interim,
    nombre_final="cultivos_consolidado.csv",
    encoding="latin-1",
    excluir=None,
):
    """
    Lee todas las series históricas de cultivos (.csv) en `ruta_raw`, las
    concatena en un solo DataFrame y guarda el resultado consolidado en
    `ruta_interim` (codificado en UTF-8, ya prolijo para trabajar en adelante).

    No modifica ni borra nada en `ruta_raw`: los datos crudos se leen
    tal cual están y se dejan intactos, como corresponde a una fuente de
    verdad. La corrección de codificación ocurre solo en memoria, al leer.

    Parameters
    ----------
    encoding : str
        Codificación real de los archivos crudos. Se usa un valor fijo,
        verificado manualmente contra los datos (latin-1: decodifica
        correctamente "Tucumán", "Córdoba", "Neuquén", etc.), en vez de
        autodetección. La autodetección (charset_normalizer) había
        devuelto codificaciones asiáticas (gb18030, cp949) para estos
        archivos, que en realidad están en español, y esa detección
        incorrecta fue la causa de la corrupción de texto detectada en
        la auditoría.
    excluir : set[str], opcional
        Nombres de archivo (sin extensión) a omitir de la consolidación,
        por si en el futuro se agregan series redundantes a `ruta_raw`.
    """
    excluir = excluir or set()
    dataframes = {}

    for archivo in glob.glob(os.path.join(ruta_raw, "*.csv")):
        nombre = os.path.basename(archivo).replace(".csv", "")
        if nombre in excluir:
            continue
        dataframes[nombre] = pd.read_csv(archivo, encoding=encoding)

    df_concat = pd.concat(dataframes.values(), ignore_index=True)

    os.makedirs(ruta_interim, exist_ok=True)
    salida = os.path.join(ruta_interim, nombre_final)
    df_concat.to_csv(salida, encoding="utf-8", index=False)
    print(
        f"✅ Dataset consolidado guardado en: {salida} "
        f"({df_concat.shape[0]} filas, {df_concat.shape[1]} columnas)"
    )

    return df_concat
