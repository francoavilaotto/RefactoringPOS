import pandas as pd
import os
import sys


if getattr(sys, 'frozen', False):
    BASE_PATH = os.path.dirname(sys.executable)
else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(BASE_PATH, "data")
ARCHIVO_PRODUCTOS = os.path.join(DATA_PATH, "productos_sin_codigo.xlsx")

def cargar_productos():
    if not os.path.exists(ARCHIVO_PRODUCTOS):
        
        df = pd.DataFrame(columns=["Producto", "PrecioUnitario", "Tipo"])
        os.makedirs(DATA_PATH, exist_ok=True)
        df.to_excel(ARCHIVO_PRODUCTOS, index=False, engine="openpyxl")
        return df  
    
    df = pd.read_excel(ARCHIVO_PRODUCTOS, engine="openpyxl")
    
    for col in ["Producto", "PrecioUnitario", "Tipo"]:
        if col not in df.columns:
            df[col] = None
    
    return df
