class Venta:
    def __init__(self):
        self.items = []

    def agregar_producto(self, producto, cantidad=1):
        codigo=str(producto["Codigo"])

        for item in self.items:
            if item["Codigo"] == codigo:
                item["Cantidad"] += cantidad
                return

        self.items.append({
            "Codigo": codigo,
            "Producto": producto["Producto"],
            "Precio": producto["Precio"],
            "Cantidad": cantidad
        })

    def aumentar_cantidad(self, codigo):
        codigo=str(codigo)
        for item in self.items:
            if item["Codigo"] == codigo:
                item["Cantidad"] += 1
                return

    def disminuir_cantidad(self, codigo):
        codigo=str(codigo)
        for item in self.items:
            if item["Codigo"] == codigo:
                item["Cantidad"] -= 1
                if item["Cantidad"] <= 0:
                    self.eliminar_producto(codigo)
                return
        print(type(item["Codigo"]), item["Codigo"])


    def eliminar_producto(self, codigo):
        codigo=str(codigo)
        self.items = [i for i in self.items if i["Codigo"] != codigo]

    def calcular_total(self):
        return sum(i["Precio"] * i["Cantidad"] for i in self.items)

    def limpiar(self):
        self.items.clear()
