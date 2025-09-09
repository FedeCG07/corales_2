import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

PAIS_CSV = "TablasLimpias/tablas_propias/pais.csv"
SEDE_CSV = "TablasLimpias/tablas_propias/sede.csv"
SECCION_CSV = "TablasLimpias/tablas_propias/seccion.csv"

OUT_DIR = "Graficos"

pais = pd.read_csv(PAIS_CSV, encoding="utf-8", low_memory=False)
sede = pd.read_csv(SEDE_CSV, encoding="utf-8", low_memory=False)
seccion = pd.read_csv(SECCION_CSV, encoding="utf-8", low_memory=False)

pais.columns = [c.strip() for c in pais.columns]
sede.columns = [c.strip() for c in sede.columns]
seccion.columns = [c.strip() for c in seccion.columns]

pais["country_code"] = pais["country_code"].astype(str).str.strip().str.upper()
pais["region"] = pais["region"].astype(str).str.strip()
pais["PBI_2023"] = pd.to_numeric(pais["PBI_2023"], errors="coerce")

sede["id_sede"] = sede["id_sede"].astype(str).str.strip()
sede["country_code"] = sede["country_code"].astype(str).str.strip().str.upper()
seccion["sede_id"] = seccion["sede_id"].astype(str).str.strip()

# sedes por país
sedes_por_pais = sede.groupby("country_code", as_index=False).agg(cantidad_sedes=("id_sede", "nunique"))

# secciones por sede
secciones_por_sede = seccion.groupby("sede_id", as_index=False).agg(cant_secciones_sede=("id_seccion", "count"))

# secciones por país (sumando por sede)
secciones_sede_con_pais = secciones_por_sede.merge(sede[["id_sede", "country_code"]],
                                                   left_on="sede_id", right_on="id_sede", how="left")
secciones_por_pais = secciones_sede_con_pais.groupby("country_code", as_index=False).agg(
    secciones_totales=("cant_secciones_sede", "sum")
)

# unir stats por país y calcular promedio
pais_stats = sedes_por_pais.merge(secciones_por_pais, on="country_code", how="left")
pais_stats = pais_stats.merge(pais[["country_code", "country_name", "region", "PBI_2023"]],
                              on="country_code", how="left")
pais_stats["secciones_totales"] = pais_stats["secciones_totales"].fillna(0)
pais_stats["secciones_promedio"] = pais_stats.apply(
    lambda r: (r["secciones_totales"] / r["cantidad_sedes"]) if r["cantidad_sedes"] and r["cantidad_sedes"] != 0 else 0,
    axis=1
)

# configurar seaborn (paleta copada)
sns.set_theme(style="whitegrid")
palette = "Set2"

# A) Cantidad de sedes por región (barras)-
sede_con_region = sede.merge(pais[["country_code", "region"]], on="country_code", how="left")
sedes_por_region = sede_con_region.groupby("region", as_index=False).agg(cantidad_sedes_region=("id_sede", "nunique"))
sedes_por_region = sedes_por_region.sort_values("cantidad_sedes_region", ascending=False).reset_index(drop=True)

plt.figure(figsize=(10, 6))
ax = sns.barplot(data=sedes_por_region, x="region", y="cantidad_sedes_region", palette=palette)
ax.set_title("Cantidad de sedes por región geográfica")
ax.set_xlabel("Región")
ax.set_ylabel("Cantidad de sedes")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "a_sedes_por_region_seaborn.png"))
plt.show()

# B) PBI por región (solo países con sedes)
# elegir países donde hay al menos una sede
paises_con_sede = sedes_por_pais["country_code"].unique().tolist()
pais_filtrado = pais[pais["country_code"].isin(paises_con_sede)].copy()

# preparar DataFrame: columnas region, PBI_2023
box_df = pais_filtrado[["region", "PBI_2023"]].dropna(subset=["region"])

# si hay rows con PBI_2023 NaN quedan fuera del boxplot (no aportan)
box_df = box_df.dropna(subset=["PBI_2023"])

# ordenar regiones por mediana de PBI (solo regiones con datos)
region_order = box_df.groupby("region")["PBI_2023"].median().sort_values().index.to_list()

plt.figure(figsize=(12, 7))
ax = sns.boxplot(data=box_df, x="region", y="PBI_2023", order=region_order, palette=palette)

plt.title("Distribución del PBI per cápita 2023 por región (países con sede)")
plt.xlabel("Región (ordenada por mediana de PBI)")
plt.ylabel("PBI per cápita 2023 (US$)")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "b_boxplots_pbi_por_region_seaborn.png"))
plt.show()

# C) Scatter PBI vs cantidad de sedes por país y regresión
scatter_df = pais_stats.dropna(subset=["PBI_2023", "cantidad_sedes"]).copy()
scatter_df = scatter_df[scatter_df["cantidad_sedes"] > 0]

plt.figure(figsize=(12, 8))
if not scatter_df.empty:
    ax = sns.scatterplot(data=scatter_df, x="PBI_2023", y="cantidad_sedes", hue="region", palette=palette, legend="full")
    try:
        sns.regplot(data=scatter_df, x="PBI_2023", y="cantidad_sedes", scatter=False, ci=None)
    except Exception:
        pass
    ax.set_xlabel("PBI per cápita 2023 (US$)")
    ax.set_ylabel("Cantidad de sedes")
    ax.set_title("Relación entre PBI per cápita 2023 y cantidad de sedes por país")
    plt.legend(title="Región", bbox_to_anchor=(1.05, 1), loc='upper left')
else:
    ax = plt.gca()
    ax.text(0.5, 0.5, "No hay suficientes datos para el scatter", ha="center", va="center")
    ax.axis("off")

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "c_scatter_pbi_vs_sedes_seaborn.png"))
plt.show()
