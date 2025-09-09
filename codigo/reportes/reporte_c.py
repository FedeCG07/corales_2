from inline_sql import sql, sql_val

query = sql^ """
SELECT country_name as 'País', count(distinct tipo_dato) as 'Cantidad Redes Sociales'
from 'TablasLimpias/tablas_propias/dato_extra.csv' as dato left join 'TablasLimpias/tablas_propias/sede.csv' as sede
on dato.id_sede = sede.id_sede
join 'TablasLimpias/tablas_propias/pais.csv' as pais
on sede.country_code = pais.country_code
group by pais.country_code, country_name
order by "País"
"""

query.to_csv("TablasLimpias/reportes/c.csv", index=False, encoding="utf-8")

print(query)