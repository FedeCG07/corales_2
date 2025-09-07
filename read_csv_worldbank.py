import pandas as pd

def leer_csv_worldbank(path_csv):
    """
    Detecta la fila de encabezado buscando 'Country Name' y 'Country Code',
    y devuelve el DataFrame leído (sin columnas 'Unnamed').
    """
    header_row = None
    with open(path_csv, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if 'Country Name' in line and 'Country Code' in line:
                header_row = i
                break
    if header_row is None:
        raise RuntimeError("No se encontró la fila de encabezado con 'Country Name' y 'Country Code'.")

    # Leer con skiprows para que la primera fila tras skip sea el header
    df = pd.read_csv(path_csv, skiprows=header_row, header=0, encoding='utf-8', engine='python')
    # Eliminar columnas basura tipo Unnamed
    df = df.loc[:, ~df.columns.str.contains(r'^Unnamed', na=False)]
    return df