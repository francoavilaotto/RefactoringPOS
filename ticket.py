from datetime import datetime
from escpos.printer import Win32Raw
from tkinter import messagebox
import os
import win32print
import sys

if getattr(sys, 'frozen', False):
    BASE_PATH = os.path.dirname(sys.executable)
else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

def detectar_impresora_termica():
    impresoras = win32print.EnumPrinters(2)

    impresoras_virtuales = [
        "ONENOTE",
        "PDF",
        "XPS",
        "FAX"
    ]

    for impresora in impresoras:
        nombre = impresora[2].upper()

        if any(v in nombre for v in impresoras_virtuales):
            continue

        return impresora[2]

    return None

def obtener_numero_ticket():
    carpeta = os.path.join(BASE_PATH, "data")
    os.makedirs(carpeta, exist_ok=True)

    ruta = os.path.join(carpeta, "contador_ticket.txt")

    if not os.path.exists(ruta):
        with open(ruta, "w") as f:
            f.write("0")

    with open(ruta, "r") as f:
        numero = int(f.read())

    numero += 1

    with open(ruta, "w") as f:
        f.write(str(numero))

    return numero

def guardar_ticket_txt(numero, items, total, pago, vuelto):
    fecha = datetime.now()
    fecha_carpeta = fecha.strftime("%Y-%m-%d")

    carpeta = os.path.join(BASE_PATH, "tickets_backup", fecha_carpeta)
    os.makedirs(carpeta, exist_ok=True)

    nombre_archivo = f"{numero:06d}.txt"
    ruta = os.path.join(carpeta, nombre_archivo)

    with open(ruta, "w", encoding="utf-8") as f:
        f.write("MINIMARKET RHINO\n")
        f.write(f"TICKET N°: {numero:06d}\n")
        f.write("CUIT: 27-42051588-5\n")
        f.write("IVA: Avila Ottonello Eliana\n")
        f.write("Dirección: Av. Ramírez de Velasco 694\n")
        f.write("--------------------------------\n")
        f.write("TICKET NO FISCAL\n")
        f.write(fecha.strftime("%d/%m/%Y %H:%M") + "\n")
        f.write("--------------------------------\n")

        for i in items:
            subtotal = i["Precio"] * i.get("Cantidad", 1)
            nombre = i["Producto"]
            cantidad = i.get("Cantidad", 1)

            f.write(f"{nombre}\n")
            f.write(f"{cantidad} x ${i['Precio']:,.0f}   ${subtotal:,.0f}\n")

        f.write("--------------------------------\n")
        f.write(f"TOTAL: ${total:,.0f}\n")
        f.write(f"PAGO: ${pago:,.0f}\n")
        f.write(f"VUELTO: ${vuelto:,.0f}\n")
        f.write("\nGracias por su compra\n")

    return ruta

def generar_ticket(numero, items, total, pago, vuelto):
    fecha = datetime.now()

    try:
        nombre_impresora = detectar_impresora_termica()
        if not nombre_impresora:
            messagebox.showerror(
                            "Error de impresión",
                "No se encontró impresora térmica conectada."
            )
            return

        p = Win32Raw(nombre_impresora)

        p.set(align='center', width=2, height=2)
        p.text("MINIMARKET RHINO\n")
        p.set(align='center')
        p.text(f"TICKET N°: {numero:06d}\n")
        p.text("CUIT: 27-42051588-5\n")
        p.text("IVA: Avila Ottonello Eliana\n")
        p.text("Dirección: Av. Ramírez de Velasco 694\n")
        p.text("--------------------------------\n")
        p.text("TICKET NO FISCAL\n")
        p.text(fecha.strftime("%d/%m/%Y %H:%M") + "\n")
        p.text("--------------------------------\n")
        p.set(align='left')

        for i in items:
            subtotal = i["Precio"] * i.get("Cantidad", 1)

            nombre = i["Producto"][:20]
            p.text(nombre + "\n")

            linea = f"{i.get('Cantidad',1)} x ${i['Precio']:,.0f}"
            subtotal_txt = f"${subtotal:,.0f}"
            espacios = 42 - len(linea) - len(subtotal_txt)
            linea += " " * max(1, espacios) + subtotal_txt + "\n"
            p.text(linea)

        p.text("--------------------------------\n")

        p.set(align='right', width=2, height=2)
        p.text(f"TOTAL: ${total:,.0f}\n")

        p.set(align='left', width=1, height=1)
        p.text(f"PAGO: ${pago:,.0f}\n")
        p.text(f"VUELTO: ${vuelto:,.0f}\n")

        p.text("\nGracias por su compra\n\n\n")

        p.cut()
        p.close()

    except Exception as e:
        print("Error de impresión:", e)
        raise
