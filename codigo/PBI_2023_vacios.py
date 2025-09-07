import pandas as pd
import numpy as np
import re
from read_csv_worldbank import leer_csv_worldbank

def vacios_pbi(path_csv, output_csv_vacios):
    """
    Lee el CSV (mismo proceso de detección de encabezado y relleno parcial),
    y exporta a CSV todos los registros que tengan Country Code vacío o PBI_2023 vacío.
    No imprime nada; devuelve el DataFrame de vacíos.
    """
    df = leer_csv_worldbank(path_csv)

    # detectar columna 2023 y columnas año (misma lógica que en limpiar_pbi)
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

    year_cols = [c for c in df.columns if re.fullmatch(r'\s*(19\d{2}|20\d{2})\s*', str(c))]
    year_cols = sorted(year_cols, key=lambda x: int(str(x).strip()))
    df['PBI_2023'] = pd.to_numeric(df[year_col_2023], errors='coerce')

    prev_years = [c for c in year_cols if int(str(c).strip()) <= 2022]
    if prev_years:
        prev_numeric = df[prev_years].apply(pd.to_numeric, errors='coerce')
        last_vals = prev_numeric.apply(lambda r: r.dropna().iloc[-1] if not r.dropna().empty else np.nan, axis=1)
        df['PBI_2023'] = df['PBI_2023'].fillna(last_vals)

    # detectar nombre exacto de country code (case-insensitive)
    country_code_col = None
    for c in df.columns:
        if str(c).strip().lower() == 'country code':
            country_code_col = c
            break
    if country_code_col is None:
        for c in df.columns:
            if 'country' in str(c).lower() and 'code' in str(c).lower():
                country_code_col = c
                break
    if country_code_col is None:
        raise KeyError("No se encontró columna 'Country Code' en el CSV.")

    vacios = df[df[country_code_col].isna() | df['PBI_2023'].isna()][['Country Name', country_code_col, 'PBI_2023']].copy()
    vacios.columns = ['Country Name', 'Country Code', 'PBI_2023']
    vacios.to_csv(output_csv_vacios, index=False, encoding='utf-8')
    return vacios

vacios_pbi("TablasOriginales/World_GDP.csv", "TablasLimpias/datos_faltantes/PBI_faltante.csv")