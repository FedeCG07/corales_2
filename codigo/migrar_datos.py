import os
import pandas as pd
import numpy as np

pbi_path = "TablasLimpias/datos_completos/PBI_2023.csv"
sedes_path = "TablasLimpias/datos_completos/sedes.csv"
secciones_path = "TablasLimpias/datos_completos/secciones.csv"
datos_path = "TablasLimpias/datos_completos/datos.csv"

OUT_DIR = "TablasLimpias/tablas_propias"

GRB_FIX = True   # Se encontró un error con el código de país GBR (Gran Bretaña) que está como GRB, esta variable sirve para corregirlo
GENERATE_PROBLEMS_CSV = True

# PBI
df_pbi = pd.read_csv(pbi_path, encoding="utf-8", low_memory=False)
# normalizar nombres de columnas (trim)
df_pbi.columns = [c.strip() for c in df_pbi.columns]

# normalizar valores
df_pbi["Country Code"] = df_pbi["Country Code"].astype(str).str.strip().str.upper()
df_pbi["PBI_2023"] = pd.to_numeric(df_pbi["PBI_2023"], errors="coerce")

# Sedes
sedes = pd.read_csv(sedes_path, encoding="utf-8", low_memory=False)
sedes.columns = [c.strip() for c in sedes.columns]

# normalizar
sedes["id_sede"] = sedes["id_sede"].astype(str).str.strip()
sedes["country_code"] = sedes["country_code"].astype(str).str.strip().str.upper()
sedes = sedes.drop_duplicates(subset=["id_sede"])

if GRB_FIX:
    sedes["country_code"] = sedes["country_code"].replace({"GRB": "GBR"})

sede_out = sedes[["id_sede", "nombre", "tipo", "country_code"]].copy()

# Datos
datos = pd.read_csv(datos_path, encoding="utf-8", low_memory=False)
datos.columns = [c.strip() for c in datos.columns]

# si existe la columna region_geografica la usamos
region_map = {}
if "region_geografica" in datos.columns:
    tmp = datos[["id_sede", "region_geografica"]].dropna().drop_duplicates()
    sede_region_map = dict(zip(tmp["id_sede"].astype(str), tmp["region_geografica"].astype(str)))
    # mapeamos sede -> país -> región
    for _, row in sede_out.iterrows():
        sid = str(row["id_sede"])
        cc = row["country_code"]
        if sid in sede_region_map and pd.notna(sede_region_map[sid]):
            region_map[cc] = sede_region_map[sid]

# Construir tabla pais
country_codes = [c for c in sede_out["country_code"].unique() if pd.notna(c) and c != ""]
pais_rows = []
problems = []

for cc in country_codes:
    row = {"country_code": cc}
    matched = df_pbi[df_pbi["Country Code"] == cc] if "Country Code" in df_pbi.columns else pd.DataFrame()
    if not matched.empty:
        r = matched.iloc[0]
        row["country_name"] = r.get("Country Name", None) if "Country Name" in df_pbi.columns else None
        row["PBI_2023"] = r.get("PBI_2023_imputed", r.get("PBI_2023", np.nan))
    else:
        row["country_name"] = None
        row["PBI_2023"] = np.nan

    # asignar región desde datos.csv si existe
    row["region"] = region_map.get(cc, None)
    pais_rows.append(row)

df_pais = pd.DataFrame(pais_rows, columns=["country_code", "country_name", "region", "PBI_2023"])

# Eliminar registro del Vaticano (VAT)
# Se encontró un problema con el registro del Pbi del vaticano, por lo que se elimina directamente del dataframe pais y se registra en el csv de problemas
if "VAT" in df_pais["country_code"].values:
    problems.append({
        "issue": "removed_vatican",
        "country_code": "VAT",
        "reason": "Vatican (VAT) eliminado por falta de PBI en la fuente."
    })
    df_pais = df_pais[df_pais["country_code"] != "VAT"].reset_index(drop=True)

# Secciones
sec = pd.read_csv(secciones_path, encoding="utf-8", low_memory=False)
sec.columns = [c.strip() for c in sec.columns]

sec["sede_id"] = sec["sede_id"].astype(str).str.strip()
sec["nombre"] = sec["nombre"].fillna("Sección desconocida").astype(str).str.strip()

# eliminar duplicados dentro de la misma sede
sec_nodup = sec.drop_duplicates(subset=["sede_id", "nombre"]).copy()

# generar id_seccion si no existe
if "id_seccion" not in sec_nodup.columns:
    sec_nodup = sec_nodup.reset_index(drop=True)
    sec_nodup.insert(0, "id_seccion", range(1, len(sec_nodup) + 1))
else:
    # asegurar id_seccion es str/int coherente
    sec_nodup["id_seccion"] = sec_nodup["id_seccion"].astype(str).str.strip()

# validar FK: sede_id existe en sedes
valid_sede_ids = set(sede_out["id_sede"].astype(str).tolist())
secciones_final_rows = []
for _, r in sec_nodup.iterrows():
    sid = r.get("sede_id")
    sid_str = str(sid) if pd.notna(sid) else None
    if sid_str is None or sid_str not in valid_sede_ids:
        problems.append({
            "issue": "seccion_fk_invalid",
            "id_seccion": r.get("id_seccion"),
            "sede_id": sid,
            "nombre": r.get("nombre")
        })
        # descartada
    else:
        secciones_final_rows.append({
            "id_seccion": r.get("id_seccion"),
            "sede_id": sid,
            "nombre": r.get("nombre")
        })

df_seccion = pd.DataFrame(secciones_final_rows, columns=["id_seccion", "sede_id", "nombre"])

# Datos
datos = pd.read_csv(datos_path, encoding="utf-8", low_memory=False)
datos.columns = [c.strip() for c in datos.columns]

# normalizar ids y valores
datos["id_sede"] = datos["id_sede"].astype(str).str.strip()
datos["valor"] = datos["valor"].astype(str).str.strip()

# validar FK: id_sede existe en sedes
datos_final_rows = []
for _, r in datos.iterrows():
    sid = r.get("id_sede")
    sid_str = str(sid) if pd.notna(sid) else None
    if sid_str is None or sid_str not in valid_sede_ids:
        problems.append({
            "issue": "datos_fk_invalid",
            "id_dato": r.get("id_dato"),
            "id_sede": sid,
            "tipo_dato": r.get("tipo_dato"),
            "valor": r.get("valor")
        })
        # descartado
    else:
        datos_final_rows.append({
            "id_dato": r.get("id_dato"),
            "id_sede": sid,
            "tipo_dato": r.get("tipo_dato"),
            "valor": r.get("valor")
        })

df_dato_extra = pd.DataFrame(datos_final_rows, columns=["id_dato", "id_sede", "tipo_dato", "valor"])

# eliminar duplicados exactos en dato_extra (misma sede, tipo y valor)
df_dato_extra = df_dato_extra.drop_duplicates(subset=["id_sede", "tipo_dato", "valor"])

# Guardar CSVs finales
sede_out.to_csv(os.path.join(OUT_DIR, "sede.csv"), index=False, encoding="utf-8")
df_seccion.to_csv(os.path.join(OUT_DIR, "seccion.csv"), index=False, encoding="utf-8")
df_dato_extra.to_csv(os.path.join(OUT_DIR, "dato_extra.csv"), index=False, encoding="utf-8")
df_pais.to_csv(os.path.join(OUT_DIR, "pais.csv"), index=False, encoding="utf-8")

# Guardar reporte de problemas
if GENERATE_PROBLEMS_CSV:
    if problems:
        df_problems = pd.DataFrame(problems)
    else:
        df_problems = pd.DataFrame(columns=["issue"])
    df_problems.to_csv(os.path.join(OUT_DIR, "problemas_calidad.csv"), index=False, encoding="utf-8")
