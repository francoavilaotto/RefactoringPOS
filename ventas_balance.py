import pandas as pd
import os
from datetime import datetime
import sys

if getattr(sys, 'frozen', False):
    BASE_PATH = os.path.dirname(sys.executable)
else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(BASE_PATH, "data")
VENTAS_PATH = os.path.join(DATA_PATH, "ventas.xlsx")

COLUMNAS_VENTAS = [
    "ID",
    "Fecha",
    "Hora",
    "Usuario",
    "MetodoDePago",
    "Plataforma",
    "Total",
    "Pago",
    "Vuelto"
]

def crear_excel_ventas():
    if os.path.exists(VENTAS_PATH):
        return

    os.makedirs(DATA_PATH, exist_ok=True)

    df = pd.DataFrame(columns=COLUMNAS_VENTAS)
    df.to_excel(VENTAS_PATH, index=False, engine="openpyxl")


def cargar_ventas():
    if not os.path.exists(VENTAS_PATH):
        crear_excel_ventas()

    df = pd.read_excel(VENTAS_PATH, engine="openpyxl")

    for col in COLUMNAS_VENTAS:
        if col not in df.columns:
            df[col] = None

    df = df[COLUMNAS_VENTAS]
    return df


def guardar_venta(numero_ticket, total, pago, vuelto, usuario, metodo, plataforma):
    df = cargar_ventas()

    nuevo_id = 1 if df.empty else df["ID"].max() + 1

    ahora = datetime.now()

    nueva_venta = {
        "ID": nuevo_id,
        "NumeroTicket": numero_ticket,
        "Fecha": ahora.strftime("%Y-%m-%d"),
        "Hora": ahora.strftime("%H:%M:%S"),
        "Usuario": usuario,
        "MetodoDePago": metodo,
        "Plataforma": plataforma,
        "Total": total,
        "Pago": pago,
        "Vuelto": vuelto
    }

    df = pd.concat([df, pd.DataFrame([nueva_venta])], ignore_index=True)

    df.to_excel(VENTAS_PATH, index=False, engine="openpyxl")



def total_por_dia(fecha):
    df = cargar_ventas()
    ventas_dia = df[df["Fecha"] == fecha]
    return ventas_dia["Total"].sum()


def total_por_mes(anio, mes):
    df = cargar_ventas()

    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

    ventas_mes = df[
        (df["Fecha"].dt.year == anio) &
        (df["Fecha"].dt.month == mes)
    ]

    return ventas_mes["Total"].sum()

def ventas_por_fecha(fecha):
    df = cargar_ventas()
    return df[df["Fecha"] == fecha]


def total_por_fecha(fecha):
    df = cargar_ventas()
    ventas = df[df["Fecha"] == fecha]
    return ventas["Total"].sum()

def ventas_por_mes(anio, mes):
    df = cargar_ventas()
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

    filtrado = df[
        (df["Fecha"].dt.year == int(anio)) &
        (df["Fecha"].dt.month == int(mes))
    ]

    return filtrado


def total_por_mes(anio, mes):
    df = ventas_por_mes(anio, mes)
    return df["Total"].sum()

def ingresos_por_plataforma(plataforma, anio, mes):

    df = pd.read_excel(VENTAS_PATH, engine="openpyxl")
    df["Fecha"] = pd.to_datetime(df["Fecha"])

    df = df[
        (df["Plataforma"] == plataforma) &
        (df["MetodoDePago"] != "Efectivo") &
        (df["Fecha"].dt.year == int(anio)) &
        (df["Fecha"].dt.month == int(mes))
    ]

    return df

def resumen_por_fecha(fecha):
    df = cargar_ventas()
    df_filtrado = df[df["Fecha"] == fecha]

    efectivo = df_filtrado[df_filtrado["MetodoDePago"] == "Efectivo"]["Total"].sum()
    transferencia = df_filtrado[df_filtrado["MetodoDePago"] == "Transferencia"]["Total"].sum()
    debito = df_filtrado[df_filtrado["MetodoDePago"] == "Debito"]["Total"].sum()

    total = df_filtrado["Total"].sum()

    return efectivo, transferencia, debito, total

