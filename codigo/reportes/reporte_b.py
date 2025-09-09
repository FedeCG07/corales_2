from inline_sql import sql, sql_val

query = sql^ """
SELECT region as 'Región Geográfica', count(distinct sede.country_code) as 'Paises con Sedes Argentinas', sum(PBI_2023)/count(distinct sede.country_code) as 'Promedio PBI per Cápita 2023 (US$)'
from 'TablasLimpias/tablas_propias/pais.csv' as pais right join 'TablasLimpias/tablas_propias/sede.csv' as sede
on pais.country_code = sede.country_code
group by region
order by "Promedio PBI per Cápita 2023 (US$)" desc
"""

query.to_csv("TablasLimpias/reportes/b.csv", index=False, encoding="utf-8")

print(query)