from inline_sql import sql, sql_val

query = sql^ """
SELECT pais.country_name as 'País', count(distinct id_sede) as 'sedes', cast(count(id_seccion) as float) /count(distinct id_sede) as 'secciones promedio', PBI_2023 as 'PBI per Cápita 2023 (US$)'
from 'TablasLimpias/tablas_propias/sede.csv' as sede join 'TablasLimpias/tablas_propias/pais.csv' as pais
ON sede.country_code = pais.country_code
left join 'TablasLimpias/tablas_propias/seccion.csv' as seccion on sede_id = id_sede
group by sede.country_code, PBI_2023, country_name
order by "sedes" desc, "País"
"""

query.to_csv("TablasLimpias/reportes/a.csv", index=False, encoding="utf-8")

print(query)