import pandas as pd
'''
import numpy as np
from matplotlib import ticker   # Para agregar separador de miles
from matplotlib import rcParams # Para modificar el tipo de letra
import matplotlib.pyplot as plt # Para graficar series multiples
'''

gdp = pd.read_csv("./GDP.csv", skiprows=4)
'''
print(gdp.head())
print(gdp.columns) # country name, country code (? y 2023
'''

secciones = pd.read_csv("./lista-secciones.csv")
'''
print(secciones.head())
print(secciones.columns)
'''

sedesdatos = pd.read_csv("./lista-sedes-datos.csv")
'''
print(sedesdatos.head())
print(sedesdatos.columns)
'''

sedes = pd.read_csv("./lista-sedes.csv")
print(sedes.head())
print(sedes.columns)