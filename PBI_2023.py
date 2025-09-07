import pandas as pd
import numpy as np
import re
from read_csv_worldbank import leer_csv_worldbank

def limpiar_pbi(path_csv, output_csv):
    """
    Lee el CSV crudo del Banco Mundial, rellena 2023 con el último valor histórico
    disponible (1960-2022) cuando sea posible, elimina filas que siguen sin PBI_2023,
    y exporta un CSV con columnas ['Country Name','Country Code','PBI_2023'].
    Devuelve el dataframe limpio.
    """
    df = leer_csv_worldbank(path_csv)

    # Detectar la columna que representa 2023 (puede tener espacios)
    year_col_2023 = None
    for c in df.columns:
        if str(c).strip() == '2023':
            year_col_2023 = c
            break
    if year_col_2023 is None:
        for c in df.columns:
            if '2023' in str(c):
                year_col_2023 = c
                break
    if year_col_2023 is None:
        raise KeyError("No se encontró columna correspondiente a 2023 en el CSV.")

    # Identificar columnas año (1960..2024)
    year_cols = [c for c in df.columns if re.fullmatch(r'\s*(19\d{2}|20\d{2})\s*', str(c))]
    # Ordenarlas cronológicamente
    year_cols = sorted(year_cols, key=lambda x: int(str(x).strip()))

    # Crear columna numérica PBI_2023
    df['PBI_2023'] = pd.to_numeric(df[year_col_2023], errors='coerce')

    # Rellenar PBI_2023 faltante con el último valor disponible hasta 2022
    prev_years = [c for c in year_cols if int(str(c).strip()) <= 2022]
    if prev_years:
        prev_numeric = df[prev_years].apply(pd.to_numeric, errors='coerce')
        last_vals = prev_numeric.apply(lambda r: r.dropna().iloc[-1] if not r.dropna().empty else np.nan, axis=1)
        df['PBI_2023'] = df['PBI_2023'].fillna(last_vals)

    # Selección final: eliminar filas que aún no tengan PBI_2023
    df_clean = df.dropna(subset=['PBI_2023'])[['Country Name', 'Country Code', 'PBI_2023']].copy()
    # Normalizar tipos
    df_clean['PBI_2023'] = pd.to_numeric(df_clean['PBI_2023'], errors='coerce')

    # Exportar CSV limpio
    df_clean.to_csv(output_csv, index=False, encoding='utf-8')
    return df_clean

limpiar_pbi("TablasOriginales/World_GDP.csv", "TablasLimpias/PBI_2023.csv")