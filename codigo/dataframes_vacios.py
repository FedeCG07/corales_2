import pandas as pd

# Tabla País
df_pais = pd.DataFrame(columns=[
    "country_code",   # PK
    "country_name",
    "region",
    "PBI_2023"
])
df_pais.to_csv("TablasLimpias/tablas_propias/pais.csv", index=False, encoding="utf-8")

# Tabla Sede
df_sede = pd.DataFrame(columns=[
    "id_sede",   # PK
    "nombre",
    "tipo",
    "pais",      # FK -> Pais.country_name o country_code
    "ciudad"
])
df_sede.to_csv("TablasLimpias/tablas_propias/sede.csv", index=False, encoding="utf-8")

# Tabla Sección
df_seccion = pd.DataFrame(columns=[
    "id_seccion",   # PK
    "id_sede",      # FK -> Sede.id_sede
    "nombre"
])
df_seccion.to_csv("TablasLimpias/tablas_propias/seccion.csv", index=False, encoding="utf-8")

# Tabla DatoExtra (para redes sociales y otros contactos)
df_dato_extra = pd.DataFrame(columns=[
    "id_dato",     # PK
    "id_sede",     # FK -> Sede.id_sede
    "tipo_dato",   # (facebook, twitter, instagram)
    "valor"        # URL/número/email
])
df_dato_extra.to_csv("TablasLimpias/tablas_propias/dato_extra.csv", index=False, encoding="utf-8")
