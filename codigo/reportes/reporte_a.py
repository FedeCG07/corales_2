from inline_sql import sql, sql_val

query = sql^ """
SELECT "Country Name" as 'País', count(distinct id_sede) as 'sedes', cast(count(id_seccion) as float) /count(distinct id_sede) as 'secciones promedio', PBI_2023 as 'PBI per Cápita 2023 (US$)'
from 'TablasLimpias/datos_completos/sedes.csv' join 'TablasLimpias/datos_completos/PBI_2023.csv' 
ON country_code = "Country Code"
left join 'TablasLimpias/datos_completos/secciones.csv' on sede_id = id_sede
group by country_code, PBI_2023, "Country Name"
order by "sedes" desc, "País"
"""

print(query)