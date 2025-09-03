import pandas as pd
import numpy as np
from matplotlib import ticker   # Para agregar separador de miles
from matplotlib import rcParams # Para modificar el tipo de letra
import matplotlib.pyplot as plt # Para graficar series multiples

gdp = pd.read_csv("./GDP.csv", skiprows=4)

print(gdp.head())