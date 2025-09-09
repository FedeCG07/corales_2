import pandas as pd
import re
from itertools import count

def choose_country_code(df):
    """Devuelve el nombre de la columna ISO3 si existe, si no devuelve None."""
    for c in df.columns:
        if str(c).strip().lower() == "pais_iso_3" or "pais_iso_3" in c.lower():
            return c
    # fallback por nombres en castellano/inglés
    for c in df.columns:
        if "pais_iso" in c.lower():
            return c
    return None

def normalize_url(u):
    """Si es un link lo normaliza agregandole el inicio si no lo tuviera"""
    if pd.isna(u):
        return None
    s = str(u).strip()
    if s == "":
        return None
    # si no tiene scheme pero parece dominio, anteponer https://
    if not re.match(r'^https?://', s, flags=re.I):
        if re.search(r'\.[a-z]{2,}', s):  # contiene un .com .org .ar etc.
            s = "https://" + s.lstrip("/")
        else:
            # no parece URL, devolver None
            return None
    return s

def detect_social_type(url_or_token):
    t = str(url_or_token).lower()
    if "instagram" in t or "ig.com" in t:
        return "instagram"
    if "facebook" in t or "fb.com" in t:
        return "facebook"
    if "twitter" in t or "x.com" in t or t.startswith("x "):
        return "twitter"
    if "youtube" in t or "youtu.be" in t:
        return "youtube"
    # si contiene solo nombre de red sin url:
    if "instagram" == t or "facebook" == t or "twitter" == t or "youtube" == t:
        return t
    # fallback: si contiene www o .com -> intentar inferir por dominio
    if re.search(r'instagram|facebook|twitter|x\.com|youtube|youtu', t):
        return ("instagram" if "insta" in t else
                "facebook" if "facebook" in t else
                "twitter" if ("twitter" in t or "x.com" in t) else
                "youtube" if "youtube" in t or "youtu" in t else None)
    return None

# SEDES
sedes_raw = pd.read_csv("TablasOriginales/lista-sedes.csv", encoding="utf-8", low_memory=False)
# normalizo nombres de columnas (sin perder los originales)
sedes_raw.columns = [c.strip() for c in sedes_raw.columns]

# identificar columna ISO3
col_iso3_sedes = choose_country_code(sedes_raw)
if col_iso3_sedes is None:
    # intentar columnas de nombre de país
    pref_country = None
    for c in sedes_raw.columns:
        if "pais_castellano" in c.lower() or "pais_ingles" in c.lower():
            pref_country = c
            break
    col_country = pref_country
else:
    col_country = col_iso3_sedes

# renombrar columnas relevantes si existen
col_id = None
for cand in ["sede_id", "id", "Id", "ID"]:
    if cand in sedes_raw.columns:
        col_id = cand
        break

# nombre de sede preferido
nombre_col = None
for cand in ["sede_desc_castellano", "sede_desc_ingles", "nombre", "sede_name"]:
    if cand in sedes_raw.columns:
        nombre_col = cand
        break

tipo_col = None
for cand in ["sede_tipo", "tipo", "tipo_sede"]:
    if cand in sedes_raw.columns:
        tipo_col = cand
        break

# construir dataframe limpio de sedes
sedes = sedes_raw.copy()
# renombramos a nombres estandar
if col_id:
    sedes = sedes.rename(columns={col_id: "id_sede"})
else:
    # generar id_sede si no existe
    sedes.insert(0, "id_sede", range(1, len(sedes)+1))

if nombre_col:
    sedes = sedes.rename(columns={nombre_col: "nombre"})
else:
    sedes["nombre"] = sedes["id_sede"].astype(str)

if tipo_col:
    sedes = sedes.rename(columns={tipo_col: "tipo"})
else:
    sedes["tipo"] = None

# country_code: preferimos ISO3 si existe
if col_country:
    sedes = sedes.rename(columns={col_country: "country_code"})
else:
    sedes["country_code"] = None

# quitar duplicados por id_sede si existen
sedes = sedes.drop_duplicates(subset=["id_sede"])

# seleccionar columnas finales (si existen)
final_cols = [c for c in ["id_sede", "nombre", "tipo", "country_code"] if c in sedes.columns]
sedes_clean = sedes[final_cols].copy()
sedes_clean.to_csv("TablasLimpias/datos_completos/sedes.csv", index=False, encoding="utf-8")






# SECCIONES
secciones_raw = pd.read_csv("TablasOriginales/lista-secciones.csv", encoding="utf-8", low_memory=False)
secciones_raw.columns = [c.strip() for c in secciones_raw.columns]

# columnas esperadas
if "sede_id" not in secciones_raw.columns:
    # intentar variantes
    for cand in ["id_sede","SedeId","sedeId"]:
        if cand in secciones_raw.columns:
            secciones_raw = secciones_raw.rename(columns={cand:"sede_id"})
            break

# usar 'tipo_seccion' como nombre de la sección; si no existe, crear desde otros campos
section_name_col = None
for cand in ["tipo_seccion", "nombre", "seccion", "section_type"]:
    if cand in secciones_raw.columns:
        section_name_col = cand
        break

if section_name_col:
    secciones_raw = secciones_raw.rename(columns={section_name_col:"nombre_seccion"})
else:
    secciones_raw["nombre_seccion"] = None

# eliminar duplicados dentro de misma sede
secciones_raw["nombre_seccion"] = secciones_raw["nombre_seccion"].fillna("Sección desconocida")
secciones_nodup = secciones_raw.drop_duplicates(subset=["sede_id", "nombre_seccion"]).copy()

# generar id_seccion
start = 1
secciones_nodup = secciones_nodup.reset_index(drop=True)
secciones_nodup.insert(0, "id_seccion", range(1, len(secciones_nodup)+1))

secciones_clean = secciones_nodup[["id_seccion", "sede_id", "nombre_seccion"]].rename(columns={"nombre_seccion":"nombre"})
secciones_clean.to_csv("TablasLimpias/datos_completos/secciones.csv", index=False, encoding="utf-8")





# DATOS (redes sociales)
datos_raw = pd.read_csv("TablasOriginales/lista-sedes-datos.csv", encoding="utf-8", low_memory=False)
datos_raw.columns = [c.strip() for c in datos_raw.columns]

# preferimos columna 'redes_sociales' si existe
redes_col = "redes_sociales"

# también tomamos 'sitio_web'
sitio_col = "sitio_web"

# aseguramos que exista region_geografica
region_col = "region_geografica" if "region_geografica" in datos_raw.columns else None

# Construir lista de filas resultantes
rows = []
id_counter = count(1)
for idx, r in datos_raw.iterrows():
    sid = r.get("sede_id", None)
    region = r.get(region_col, None) if region_col else None
    # 1) parse redes_sociales campo (si existe)
    if redes_col and pd.notna(r.get(redes_col)):
        raw = str(r.get(redes_col))
        # split por '//' que parece ser el separador en el CSV
        parts = [p.strip() for p in re.split(r'//|\n|;|\|', raw) if p and p.strip()]
        for part in parts:
            # limpiar comillas y espacios extra
            token = part.strip().strip(',')
            url = normalize_url(token)
            tipo = detect_social_type(token) or ( "otro" if url else None )
            if url:
                rows.append({
                    "id_dato": next(id_counter),
                    "id_sede": sid,
                    "tipo_dato": tipo or "red_social",
                    "valor": url,
                    "region_geografica": region
                })
            else:
                # si token no es URL pero contiene "instagram" o "facebook", podemos construir URL
                tipo_guess = detect_social_type(token)
                if tipo_guess:
                    # intentar formar https://{token} si no tiene domain
                    guess = token
                    if not re.search(r'\.', token):
                        guess = "https://" + token
                    guess = normalize_url(guess)
                    if guess:
                        rows.append({
                            "id_dato": next(id_counter),
                            "id_sede": sid,
                            "tipo_dato": tipo_guess,
                            "valor": guess,
                            "region_geografica": region
                        })
    # también incluir sitio_web si existe y es URL válida
    if sitio_col and pd.notna(r.get(sitio_col)):
        url = normalize_url(r.get(sitio_col))
        if url:
            rows.append({
                "id_dato": next(id_counter),
                "id_sede": sid,
                "tipo_dato": "sitio_web",
                "valor": url,
                "region_geografica": region
            })

# crear dataframe resultado
if rows:
    datos_clean = pd.DataFrame(rows, columns=["id_dato", "id_sede", "tipo_dato", "valor", "region_geografica"])
else:
    datos_clean = pd.DataFrame(columns=["id_dato", "id_sede", "tipo_dato", "valor", "region_geografica"])

datos_clean.to_csv("TablasLimpias/datos_completos/datos.csv", index=False, encoding="utf-8")
