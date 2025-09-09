from inline_sql import sql, sql_val

query = sql^ """
SELECT country_name as 'País', sede.id_sede as 'Sede', tipo_dato as 'Red Social', valor as 'URL'
from 'TablasLimpias/tablas_propias/pais.csv' as pais join 'TablasLimpias/tablas_propias/sede.csv' as sede
on pais.country_code = sede.country_code
join 'TablasLimpias/tablas_propias/dato_extra.csv' as dato
on sede.id_sede = dato.id_sede
order by country_name
"""

query.to_csv("TablasLimpias/reportes/d.csv", index=False, encoding="utf-8")

print(query)