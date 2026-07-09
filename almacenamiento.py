"""
Utilidades compartidas para guardar archivos de datos (Excel) de forma segura.

Resuelve dos problemas que ya causaron pérdida de datos en este proyecto:

1. Guardado atómico: si el proceso se corta a mitad de un wb.save()/to_excel()
   (corte de luz, cierre forzado, antivirus, sincronización de OneDrive/Drive),
   el archivo final NUNCA queda a medio escribir. Se escribe primero a un
   archivo temporal y solo se reemplaza el archivo real si el guardado
   terminó sin errores (os.replace es atómico a nivel de sistema operativo).

2. Backups rotativos: además del guardado atómico, se guarda una copia con
   timestamp antes de cada escritura, como red de seguridad independiente
   de OneDrive/Drive. Se conservan solo los últimos N backups por archivo.
"""

import os
import shutil
import tempfile
from datetime import datetime


def guardado_atomico(func_escribir, ruta_final):
    """
    Ejecuta func_escribir(ruta_temp) para generar el contenido del archivo,
    y solo si termina sin excepciones, reemplaza el archivo final.

    func_escribir: función que recibe una ruta (str) y escribe el archivo ahí.
    ruta_final: ruta del archivo real que se quiere actualizar.
    """
    directorio = os.path.dirname(ruta_final)
    os.makedirs(directorio, exist_ok=True)

    base = os.path.splitext(os.path.basename(ruta_final))[0]
    ext = os.path.splitext(ruta_final)[1]

    fd, ruta_temp = tempfile.mkstemp(prefix=f"{base}_tmp_", suffix=ext, dir=directorio)
    os.close(fd)

    try:
        func_escribir(ruta_temp)
        os.replace(ruta_temp, ruta_final)
    except Exception:
        if os.path.exists(ruta_temp):
            try:
                os.remove(ruta_temp)
            except OSError:
                pass
        raise


def hacer_backup(ruta_archivo, carpeta_backups=None, max_backups=20):
    """
    Copia el archivo actual a una carpeta de backups con timestamp en el
    nombre, y borra los backups más viejos si se supera max_backups.

    No debe interrumpir el flujo principal de guardado: si el backup falla
    (disco lleno, permisos, etc.) solo se avisa por consola, no se lanza
    excepción hacia arriba.
    """
    if not os.path.exists(ruta_archivo):
        return

    if carpeta_backups is None:
        carpeta_backups = os.path.join(os.path.dirname(ruta_archivo), "backups")

    try:
        os.makedirs(carpeta_backups, exist_ok=True)

        nombre_base = os.path.splitext(os.path.basename(ruta_archivo))[0]
        ext = os.path.splitext(ruta_archivo)[1]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destino = os.path.join(carpeta_backups, f"{nombre_base}_{timestamp}{ext}")

        shutil.copy2(ruta_archivo, destino)

        prefijo = nombre_base + "_"
        backups = sorted(
            f for f in os.listdir(carpeta_backups)
            if f.startswith(prefijo) and f.endswith(ext)
        )
        for viejo in backups[:-max_backups]:
            try:
                os.remove(os.path.join(carpeta_backups, viejo))
            except OSError:
                pass

    except Exception as e:
        print(f"Advertencia: no se pudo crear backup de '{ruta_archivo}': {e}")