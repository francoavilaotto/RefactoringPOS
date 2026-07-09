import tkinter as tk
from inventario import crear_excel_base
from gui import KioscoGUI
from ventas_balance import crear_excel_ventas

if __name__ == "__main__":
    crear_excel_base()
    crear_excel_ventas()
    root = tk.Tk()
    app = KioscoGUI(root)
    root.mainloop()
