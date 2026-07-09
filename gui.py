import tkinter as tk
from tkinter import ttk
from inventario import cargar_inventario, guardar_inventario
from ventas import Venta
from ticket import generar_ticket, obtener_numero_ticket, guardar_ticket_txt
from datetime import datetime
from ventas_balance import ventas_por_mes, total_por_mes, ventas_por_fecha, guardar_venta, resumen_por_fecha
from productos_sin_codigo import cargar_productos
from tkinter import messagebox
import os
import sys

COLOR_FONDO = "#0f6d6a"
COLOR_PANEL = "#e6e6e6"
COLOR_BLANCO = "#ffffff"
COLOR_VERDE = "#22c55e"
COLOR_ROJO = "#ef4444"

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class KioscoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RHINO - Sistema de Ventas")
        self.root.state("zoomed") 
        self.root.configure(bg=COLOR_FONDO)
        self.root.iconbitmap(resource_path("rhino.ico"))
                
        self.df = cargar_inventario()
        self.venta = Venta()
        self.df_sin_codigo = cargar_productos()
        self.nombres_productos = self.df_sin_codigo["Producto"].tolist()
        self.crear_estilos()
        self.crear_layout()
        self.root.bind("<F2>", lambda e: self.entry_codigo.focus())
        self.root.bind("<F3>", lambda e: self.entry_pago.focus())
        self.root.bind("<F4>", lambda e: self.finalizar())
        self.root.bind("<Delete>", lambda e: self.limpiar_producto())
        self.root.bind("<plus>", lambda e: self.boton_mas())
        self.root.bind("<minus>", lambda e: self.boton_menos())
        self.root.bind("<Escape>", lambda e: self.cancelar_venta())
        self.ventana_historial = None
        self.actualizar_historial_func = None
        self.usuario = None
        self.root.after(100, self.login)

    def login(self):
        ventana_login = tk.Toplevel(self.root)
        ventana_login.title("Inicio de Sesión")

        ancho = 300
        alto = 200

        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()

        x = (pantalla_ancho // 2) - (ancho // 2)
        y = (pantalla_alto // 2) - (alto // 2)

        ventana_login.geometry(f"{ancho}x{alto}+{x}+{y}")
        ventana_login.configure(bg=COLOR_PANEL)
        ventana_login.resizable(False, False)
        ventana_login.transient(self.root)
        ventana_login.grab_set()
        ventana_login.focus_force()

        
        def cerrar_login():
            self.root.destroy()

        ventana_login.protocol("WM_DELETE_WINDOW", cerrar_login)

        tk.Label(ventana_login,
                text="Usuario",
                bg=COLOR_PANEL,
                font=("Segoe UI", 10)).pack(pady=(20,5))

        entry_user = tk.Entry(ventana_login, font=("Segoe UI", 11))
        entry_user.pack()
        

        tk.Label(ventana_login,
                text="Contraseña",
                bg=COLOR_PANEL,
                font=("Segoe UI", 10)).pack(pady=(15,5))

        entry_pass = tk.Entry(ventana_login, show="*", font=("Segoe UI", 11))
        entry_pass.pack()

        entry_user.focus()
        entry_pass.bind("<Up>", lambda e: entry_user.focus())
        entry_user.bind("<Down>", lambda e: entry_pass.focus())

        def validar():
            usuario = entry_user.get().strip()
            password = entry_pass.get().strip()

            usuarios = {
                "sofia": "2205",
                "eli": "3105",
                "nahuel": "1308",
                "usuario": "0000"
            }
 
            if usuario in usuarios and usuarios[usuario] == password:
                self.usuario = usuario
                ventana_login.destroy()
            else:
                messagebox.showerror("Error","Usuario o contraseña incorrectos")

        btn_ingresar = tk.Button(ventana_login,
                text="Ingresar",
                bg="#1f2937",
                fg="white",
                font=("Segoe UI", 10, "bold"),
                command=validar)
        btn_ingresar.pack(pady=20)
        ventana_login.bind("<Return>", lambda event: btn_ingresar.invoke())

        

        ventana_login.wait_window()  
        
    def crear_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Treeview",
                        background=COLOR_BLANCO,
                        fieldbackground=COLOR_BLANCO,
                        rowheight=28)

        style.configure("Treeview.Heading",
                        font=("Segoe UI", 10, "bold"))
        
    def crear_layout(self):
        top_panel = tk.Frame(self.root, bg=COLOR_PANEL, height=120)
        top_panel.pack(fill="x", padx=15, pady=15)

        tk.Label(top_panel, text="Código",
                 bg=COLOR_PANEL, font=("Segoe UI", 10)).place(x=20, y=20)

        self.entry_codigo = tk.Entry(top_panel, font=("Segoe UI", 11), width=25)
        self.entry_codigo.place(x=20, y=45)
        self.entry_codigo.bind("<Return>", self.leer_codigo)

        tk.Label(top_panel, text="Cantidad",
                 bg=COLOR_PANEL, font=("Segoe UI", 10)).place(x=250, y=20)

        self.entry_cantidad = tk.Entry(top_panel, font=("Segoe UI", 11), width=10)
        self.entry_cantidad.insert(0, "1")
        self.entry_cantidad.place(x=250, y=45)

        btn_mas = tk.Button(top_panel, text="+",
                            bg=COLOR_VERDE, fg="white",
                            font=("Segoe UI", 14, "bold"),
                            width=4, height=1,
                            command=self.boton_mas)
        btn_mas.place(x=350, y=40)

        btn_menos = tk.Button(top_panel, text="-",
                              bg=COLOR_ROJO, fg="white",
                              font=("Segoe UI", 14, "bold"),
                              width=4, height=1,
                              command=self.boton_menos)
        btn_menos.place(x=420, y=40)

        btn_limpiar = tk.Button(top_panel, text="Limpiar",
                                bg="#d1d5db",
                                font=("Segoe UI", 10),
                                width=10,
                                command=self.limpiar_producto)
        btn_limpiar.place(x=500, y=42)

        center_panel = tk.Frame(self.root, bg=COLOR_FONDO)
        center_panel.pack(fill="both", expand=True, padx=15, pady=10)
   
        tk.Label(top_panel, text="Producto sin código",
                bg=COLOR_PANEL, font=("Segoe UI", 10)).place(x=700, y=20)

        self.combobox_sin_codigo = ttk.Combobox(top_panel, values=self.nombres_productos, width=25, state="readonly")
        self.combobox_sin_codigo.place(x=700, y=45)

        tk.Label(top_panel, text="Cantidad/Gramos",
                bg=COLOR_PANEL, font=("Segoe UI", 10)).place(x=900, y=20)

        self.entry_cantidad_manual = tk.Entry(top_panel, width=10, font=("Segoe UI", 11))
        self.entry_cantidad_manual.place(x=900, y=45)
        self.entry_cantidad_manual.insert(0, "1")

        tk.Button(top_panel, text="Agregar",
                bg=COLOR_VERDE, fg="white",
                font=("Segoe UI", 10, "bold"),
                command=self.agregar_producto_sin_codigo).place(x=1000, y=42)

        self.tree = ttk.Treeview(
            center_panel,
            columns=("Codigo", "Producto", "Precio", "Cantidad", "Subtotal", "Estado"),
            show="headings",
            height=15
        )

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=150)

        self.tree.pack(side="left", fill="both", expand=True)

        right_panel = tk.Frame(center_panel, bg=COLOR_PANEL)
        right_panel.pack(side="right", fill="y", padx=(10,0))

        tk.Label(right_panel, text="TOTAL",
                 bg=COLOR_PANEL,
                 font=("Segoe UI", 12, "bold")).pack(pady=20)

        self.lbl_total = tk.Label(right_panel,
                                  text="$0",
                                  bg=COLOR_PANEL,
                                  font=("Segoe UI", 26, "bold"))
        self.lbl_total.pack(pady=10)
        
        self.lbl_vuelto = tk.Label(right_panel,
                           text="Vuelto: $0",
                           bg=COLOR_PANEL,
                           font=("Segoe UI", 12, "bold"))
        self.lbl_vuelto.pack(pady=5)
        
        tk.Label(right_panel, text="Paga con",
                 bg=COLOR_PANEL,
                 font=("Segoe UI", 10)).pack(pady=(15,5))

        self.entry_pago = tk.Entry(right_panel,
                                   font=("Segoe UI", 12),
                                   width=15)
        self.entry_pago.bind("<KeyRelease>", self.calcular_vuelto)
        self.entry_pago.pack()

        tk.Label(right_panel, text="Método de Pago",
                bg=COLOR_PANEL,
                font=("Segoe UI", 10)).pack()

        self.combo_metodo = ttk.Combobox(
            right_panel,
            values=["Efectivo", "Transferencia", "Debito"],
            state="readonly"
        )
        self.combo_metodo.pack()
        self.combo_metodo.set("Efectivo")
        self.combo_metodo.bind("<<ComboboxSelected>>", self.cambiar_metodo_pago)

        tk.Label(right_panel, text="Plataforma",
                bg=COLOR_PANEL,
                font=("Segoe UI", 10)).pack()

        self.combo_plataforma = ttk.Combobox(
            right_panel,
            values=["Mercado Pago", "Santander", "Naranja X", "PersonalPay", "Uala", "Modo", "BNA+", "Brubank", "Lemon Cash", "Otra"],
            state="readonly"
        )
        self.combo_plataforma.pack()

        btn_frame = tk.Frame(right_panel, bg=COLOR_PANEL)
        btn_frame.pack(side="bottom", pady=5)

        tk.Button(btn_frame,
                text="Registrar Venta",
                bg="#1f2937",
                fg="white",
                font=("Segoe UI", 11, "bold"),
                width=18,
                height=2,
                command=self.finalizar).pack(pady=5)

        tk.Button(btn_frame,
                text="Historial / Cierre",
                bg="#374151",
                fg="white",
                font=("Segoe UI", 10, "bold"),
                width=18,
                command=self.abrir_historial).pack(pady=5)

        tk.Button(btn_frame,
                text="Imprimir Ticket",
                bg="#065f46",
                fg="white",
                font=("Segoe UI", 10, "bold"),
                width=18,
                command=self.imprimir_ticket).pack(pady=5)

        self.entry_cantidad.bind("<Return>", lambda e: self.entry_codigo.focus())
        self.entry_cantidad.bind("<Return>", self.leer_codigo)

    def boton_mas(self):
        codigo = str(self.entry_codigo.get().strip())
        
        seleccion = self.tree.selection()
        if seleccion:
            codigo = str(self.tree.item(seleccion[0])["values"][0])

        if not codigo:
            return
        
        self.df["Codigo"]=self.df["Codigo"].astype(str)
        prod = self.df[self.df["Codigo"] == codigo]
        if prod.empty:
            return

        prod = prod.iloc[0]

        try:
            cantidad = int(self.entry_cantidad.get())
        except:
            cantidad = 1

        if cantidad <= 0:
            cantidad = 1

        cantidad_actual_en_venta = 0
        for item in self.venta.items:
            if str(item["Codigo"]) == codigo:
                cantidad_actual_en_venta = item["Cantidad"]
                break

        if cantidad_actual_en_venta + cantidad > prod["Cantidad"]:
            messagebox.showerror("Error","No hay suficiente stock")
            return

        self.venta.agregar_producto(prod, cantidad)
        self.actualizar_tabla()
        self.entry_codigo.focus()

    def boton_menos(self):
        seleccion = self.tree.selection()

        if seleccion:
            codigo = self.tree.item(seleccion[0])["values"][0]
        else:
            codigo = self.entry_codigo.get().strip()
        if not codigo:
            return

        self.venta.disminuir_cantidad(codigo)
        self.actualizar_tabla()
        self.entry_codigo.focus()
        print(type(codigo), codigo)

    def limpiar_producto(self):
        seleccion = self.tree.selection()

        if seleccion:
            codigo = self.tree.item(seleccion[0])["values"][0]
        else:
            codigo = self.entry_codigo.get().strip()

        if not codigo:
            return

        self.venta.eliminar_producto(codigo)
        self.actualizar_tabla()
        self.entry_codigo.focus()

    def leer_codigo(self, event):
        codigo = str(self.entry_codigo.get().strip())
        self.entry_codigo.delete(0, tk.END)

        try:
            cantidad = int(self.entry_cantidad.get())
        except:
            cantidad = 1

        if cantidad <= 0:
            cantidad = 1

        prod = self.df[self.df["Codigo"] == codigo]

        if prod.empty:
            messagebox.showerror("Error","Producto no encontrado")
            return

        prod = prod.iloc[0]

        if prod["Cantidad"] <= 0:
            messagebox.showerror("Error","Producto sin stock")
            return

        self.venta.agregar_producto(prod, cantidad)
        self.actualizar_tabla()
        
        self.entry_cantidad.delete(0, tk.END)
        self.entry_cantidad.insert(0, "1")
        self.entry_codigo.focus()   
        
    def actualizar_tabla(self):
        indice_seleccionado = None
        seleccion = self.tree.selection()

        if seleccion:
            indice_seleccionado = self.tree.index(seleccion[0])

                
        for i in self.tree.get_children():
            self.tree.delete(i)

        for item in self.venta.items:
            subtotal = item["Precio"] * item.get("Cantidad",1)
            cantidad_mostrar = f"{item.get('CantidadGramos', item.get('Cantidad', 1))} g" \
                if item.get("Tipo") == "Peso" else item.get("Cantidad", 1)

           
            df_prod = self.df[self.df["Codigo"] == item["Codigo"]]
            dias_para_vencer = df_prod["DiasParaVencer"].iloc[0] if not df_prod.empty else None

            estado="✔ OK"
            if dias_para_vencer is not None:
                if dias_para_vencer <=0: 
                    estado="✘ Vencido"
                elif dias_para_vencer <=7:
                    estado="● Por vencer"
            
            row_id = self.tree.insert(
                "",
                tk.END,
                values=(
                    item["Codigo"],
                    item["Producto"],
                    f"${item['Precio']:,.0f}",
                    cantidad_mostrar,
                    f"${subtotal:,.0f}",
                    estado
                )
            )

            if dias_para_vencer is not None:
                if dias_para_vencer <= 0:
                    self.tree.item(row_id, tags=("vencido",))
                elif dias_para_vencer <= 7:
                    self.tree.item(row_id, tags=("por_vencer",))

       
        self.tree.tag_configure("vencido", background="#f87171")      
        self.tree.tag_configure("por_vencer", background="#facc15")
        
        hijos = self.tree.get_children()
        if indice_seleccionado is not None and hijos:
            if indice_seleccionado < len(hijos):
                self.tree.selection_set(hijos[indice_seleccionado])
                self.tree.focus(hijos[indice_seleccionado])

        self.lbl_total.config(
            text=f"${self.venta.calcular_total():,.0f}"
        )

    def finalizar(self):
        metodo = self.combo_metodo.get()
        plataforma = self.combo_plataforma.get()

        if not self.venta.items:
            return

        total = self.venta.calcular_total()

        
        numero_ticket = obtener_numero_ticket()

        if metodo == "Efectivo":
            try:
                pago = float(self.entry_pago.get())
            except:
                return

            if pago < total:
                return

            vuelto = pago - total
        else:
            pago = total
            vuelto = 0

        
        for item in self.venta.items:
            df_prod = self.df[self.df["Codigo"] == item["Codigo"]]
            if not df_prod.empty:
                idx = df_prod.index[0]
                self.df.at[idx, "Cantidad"] -= item.get("Cantidad", 1)

        guardar_inventario(self.df)

        
        self.ultima_venta = {
            "numero": numero_ticket,
            "items": self.venta.items.copy(),
            "total": total,
            "pago": pago,
            "vuelto": vuelto,
            "metodo": metodo,
            "plataforma": plataforma,
            "usuario": self.usuario
        }

        guardar_ticket_txt(
        numero_ticket,
        self.venta.items,
        total,
        pago,
        vuelto
    )


        
        guardar_venta(numero_ticket, total, pago, vuelto, self.usuario, metodo, plataforma)

        if self.actualizar_historial_func:
            self.actualizar_historial_func()

        
        self.venta.limpiar()
        self.actualizar_tabla()

        self.entry_pago.config(state="normal")
        self.entry_pago.delete(0, tk.END)
        self.lbl_vuelto.config(text="Vuelto: $0")

        self.combo_metodo.set("Efectivo")
        self.combo_plataforma.set("")
        self.combo_plataforma.config(state="disabled")

        self.entry_codigo.focus_set()
    
    def cancelar_venta(self):
        if not self.venta.items:
            return

        self.venta.limpiar()
        self.actualizar_tabla()
        self.entry_pago.delete(0, tk.END)
        self.entry_codigo.focus()

    def calcular_vuelto(self, event=None):
        try:
            pago = float(self.entry_pago.get())
        except:
            self.lbl_vuelto.config(text="Vuelto: $0")
            return

        total = self.venta.calcular_total()
        vuelto = pago - total

        if vuelto < 0:
            self.lbl_vuelto.config(text="Vuelto: $0")
        else:
            self.lbl_vuelto.config(text=f"Vuelto: ${vuelto:,.0f}")
        
        self.entry_pago.bind("<Return>", lambda e: self.finalizar())

    def abrir_historial(self):
        if self.ventana_historial is not None:
      
            try:
                self.ventana_historial.deiconify()
                self.ventana_historial.lift()
                return
            except tk.TclError:
               
                self.ventana_historial = None

        self.ventana_historial = tk.Toplevel(self.root)
        ventana = self.ventana_historial
        ventana.title("Historial de Ventas")
        ventana.geometry("900x620")
        ventana.configure(bg=COLOR_FONDO)

       
        top_panel = tk.Frame(ventana, bg=COLOR_PANEL, height=100)
        top_panel.pack(fill="x", padx=15, pady=15)

        
        tk.Label(top_panel, text="Fecha (YYYY-MM-DD)",
                bg=COLOR_PANEL, font=("Segoe UI", 10)).place(x=20, y=20)

        entry_fecha = tk.Entry(top_panel, font=("Segoe UI", 11), width=15)
        entry_fecha.place(x=20, y=45)

        hoy = datetime.now()
        entry_fecha.insert(0, hoy.strftime("%Y-%m-%d"))

        
        tk.Label(top_panel, text="Año",
                bg=COLOR_PANEL, font=("Segoe UI", 10)).place(x=250, y=20)

        entry_anio = tk.Entry(top_panel, font=("Segoe UI", 11), width=8)
        entry_anio.place(x=250, y=45)
        entry_anio.insert(0, hoy.year)

        
        tk.Label(top_panel, text="Mes",
                bg=COLOR_PANEL, font=("Segoe UI", 10)).place(x=330, y=20)

        entry_mes = tk.Entry(top_panel, font=("Segoe UI", 11), width=5)
        entry_mes.place(x=330, y=45)
        entry_mes.insert(0, hoy.month)

       
        center_panel = tk.Frame(ventana, bg=COLOR_FONDO)
        center_panel.pack(fill="both", expand=True, padx=15)

        tree = ttk.Treeview(
            center_panel,
            columns=("ID", "Hora", "Usuario", "Metodo", "Plataforma", "Total"),
            show="headings",
            height=12
        )

        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=140)

        tree.pack(fill="both", expand=True)

        
        bottom_panel = tk.Frame(ventana, bg=COLOR_PANEL)
        bottom_panel.pack(fill="x", padx=15, pady=10)

        
        resumen_frame = tk.Frame(bottom_panel, bg=COLOR_PANEL)
        resumen_frame.pack(fill="both", expand=True, padx=20, pady=10)

        
        lbl_efectivo = tk.Label(resumen_frame, bg=COLOR_PANEL, font=("Segoe UI", 12))
        lbl_efectivo.grid(row=0, column=0, sticky="w")

        lbl_transferencia = tk.Label(resumen_frame, bg=COLOR_PANEL, font=("Segoe UI", 12))
        lbl_transferencia.grid(row=1, column=0, sticky="w")

        lbl_debito = tk.Label(resumen_frame, bg=COLOR_PANEL, font=("Segoe UI", 12))
        lbl_debito.grid(row=2, column=0, sticky="w")

       
        lbl_total = tk.Label(resumen_frame,
                            bg=COLOR_PANEL,
                            font=("Segoe UI", 20, "bold"))

        lbl_total.grid(row=0, column=2, rowspan=3, padx=90)

        def cargar_datos():
            fecha = entry_fecha.get().strip()

            for i in tree.get_children():
                tree.delete(i)

            df = ventas_por_fecha(fecha)

            for _, row in df.iterrows():
                tree.insert("", tk.END, values=(
                    row["ID"],
                    row["Hora"],
                    row["Usuario"],
                    row["MetodoDePago"],
                    row["Plataforma"],
                    f"${row['Total']:,.0f}"
                ))

            efectivo, transferencia, debito, total = resumen_por_fecha(fecha)
            lbl_efectivo.config(text=f"Efectivo: ${efectivo:,.0f}")
            lbl_transferencia.config(text=f"Transferencia: ${transferencia:,.0f}")
            lbl_debito.config(text=f"Débito: ${debito:,.0f}")
            lbl_total.config(text=f"TOTAL DEL DÍA: ${total:,.0f}")

        def cargar_mes():
            anio = entry_anio.get().strip()
            mes = entry_mes.get().strip()

            for i in tree.get_children():
                tree.delete(i)

            df = ventas_por_mes(anio, mes)

            for _, row in df.iterrows():
                tree.insert("", tk.END, values=(
                    row["ID"],
                    row["Hora"],
                    row["Usuario"],
                    row["MetodoDePago"],
                    row["Plataforma"],
                    f"${row['Total']:,.0f}",
                ))

            total_mes = total_por_mes(anio, mes)
            lbl_total.config(text=f"TOTAL DEL MES: ${total_mes:,.0f}")

        
        self.actualizar_historial_func = cargar_datos

        
        tk.Button(top_panel,
                text="Ver Día",
                bg="#1f2937",
                fg="white",
                font=("Segoe UI", 10, "bold"),
                command=cargar_datos).place(x=120, y=42)

        tk.Button(top_panel,
                text="Ver Mes",
                bg="#374151",
                fg="white",
                font=("Segoe UI", 10, "bold"),
                command=cargar_mes).place(x=400, y=42)
        
        def on_cerrar_historial():
        
            self.ventana_historial.withdraw()

        self.ventana_historial.protocol("WM_DELETE_WINDOW", on_cerrar_historial)

        cargar_datos()

    def agregar_producto_sin_codigo(self):
        seleccionado = self.combobox_sin_codigo.get()
        if not seleccionado:
            messagebox.showerror("Error","Seleccione un producto")
            return

        try:
            cantidad = float(self.entry_cantidad_manual.get())
            if cantidad <= 0:
                cantidad = 1
        except:
            cantidad = 1

        producto = self.df_sin_codigo[self.df_sin_codigo["Producto"] == seleccionado].iloc[0]

        if producto.get("Tipo") == "Peso":  
            precio_calculado = cantidad * producto["PrecioUnitario"] / 100
            cantidad_en_venta = 1 
            self.venta.agregar_producto({
                "Codigo": f"SINCOD-{seleccionado}",
                "Producto": seleccionado,
                "Precio": precio_calculado,
                "Tipo": "Peso",
                "CantidadGramos": cantidad
            }, cantidad_en_venta)
        else: 
            precio_calculado = producto["PrecioUnitario"]
            cantidad_en_venta = int(cantidad)  
            self.venta.agregar_producto({
                "Codigo": f"SINCOD-{seleccionado}",
                "Producto": seleccionado,
                "Precio": precio_calculado,
                "Tipo": "Unidad",
            }, cantidad_en_venta)

        self.actualizar_tabla()

       
        self.entry_cantidad_manual.delete(0, tk.END)
        self.entry_cantidad_manual.insert(0, "1")
        self.combobox_sin_codigo.set("")

    def imprimir_ticket(self):
        if not hasattr(self, "ultima_venta") or not self.ultima_venta:
            messagebox.showwarning("Aviso", "No hay venta para imprimir")
            return
        try:
            generar_ticket(
                self.ultima_venta["numero"],
                self.ultima_venta["items"],
                self.ultima_venta["total"],
                self.ultima_venta["pago"],
                self.ultima_venta["vuelto"]
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo imprimir:\n{e}")

    def cambiar_metodo_pago(self, event=None):
        metodo = self.combo_metodo.get()

        if metodo == "Efectivo":
            self.entry_pago.config(state="normal")
            self.entry_pago.delete(0, tk.END)   
            self.entry_pago.insert(0, "")      
            self.entry_pago.focus_set()         
            self.combo_plataforma.set("")
            self.combo_plataforma.config(state="disabled")
            self.lbl_vuelto.config(text="Vuelto: $0")   
        else:
            total = self.venta.calcular_total()

            self.entry_pago.config(state="normal")
            self.entry_pago.delete(0, tk.END)
            self.entry_pago.insert(0, str(total))
            self.entry_pago.config(state="disabled")

            self.combo_plataforma.config(state="readonly")
            self.lbl_vuelto.config(text="Vuelto: $0")

