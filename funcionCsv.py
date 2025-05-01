"""
@author: Mixcoalt
"""

import sqlite3
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import uuid
import os
import csv

# ===== DATABASE ===== #

def conector():
    conexion = sqlite3.connect("reporteCsv.db")
    return conexion

def create_table():
    conexion = conector()
    cursor = conexion.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reportes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora  TEXT,    
            nombre_cliente TEXT,
            clave_cliente TEXT,
            nombre_negocio TEXT,
            detalles TEXT,
            codigo_reporte TEXT UNIQUE,
            estado TEXT,
            fecha_close TEXT
        )          
    ''')
    conexion.commit()
    conexion.close()

# ===== FUNCIONES DE IDENTIFICADOR Y GUARDADO ===== #

def generar_id_reportes(prefijo="REP"):
    fecha = datetime.now().strftime("%d%m%Y")
    parte_unica = str(uuid.uuid4())[:4]
    return f"{prefijo}-{fecha}-{parte_unica}" 

def guardar_reporte(nombre_cliente, clave_cliente, nombre_negocio, detalles, codigo_reporte):
    conexion = conector()
    cursor = conexion.cursor()
    cursor.execute('''
        INSERT INTO reportes (fecha_hora, nombre_cliente, clave_cliente, nombre_negocio, detalles, codigo_reporte, estado, fecha_close)            
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)        
    ''', (
        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        nombre_cliente,
        clave_cliente,
        nombre_negocio,
        detalles,
        codigo_reporte,
        "Pendiente",
        ""
    ))
    conexion.commit()
    conexion.close()

    # Exportar a CSV
    exportar_a_csv(nombre_cliente, clave_cliente, nombre_negocio, detalles, codigo_reporte)

def exportar_a_csv(nombre_cliente, clave_cliente, nombre_negocio, detalles, codigo_reporte, estado="Pendiente"):
    ruta_csv = "reportes_exportados.csv"
    existe_archivo = os.path.isfile(ruta_csv)

    with open(ruta_csv, mode='a', newline='', encoding='utf-8') as archivo:
        escritor = csv.writer(archivo)

        if not existe_archivo:
            escritor.writerow([
                "Fecha y Hora", "Nombre Cliente", "Clave Cliente", 
                "Nombre Negocio", "Detalles", "Código Reporte", 
                "Estado", "Fecha de Cierre"
            ])

        escritor.writerow([
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            nombre_cliente,
            clave_cliente,
            nombre_negocio,
            detalles,
            codigo_reporte,
            estado,
            ""
        ])

def actualizar_reporte_completo(codigo_reporte):
    conexion = conector()
    cursor = conexion.cursor()
    cursor.execute('''
        UPDATE reportes
        SET estado = "Completado",
            fecha_close = ?
        WHERE codigo_reporte = ?          
    ''', (
        datetime.now().strftime("%d/%m/%Y-%H:%M:%S"),
        codigo_reporte
    ))
    
    cambios = cursor.rowcount
    conexion.commit()
    conexion.close()

    if cambios > 0:
        actualizar_csv(codigo_reporte)
    return cambios > 0

def actualizar_csv(codigo_reporte):
    ruta_csv = "reportes_exportados.csv"
    if not os.path.exists(ruta_csv):
        return

    filas_actualizadas = []
    actualizado = False

    with open(ruta_csv, mode='r', newline='', encoding='utf-8') as archivo:
        lector = csv.reader(archivo)
        encabezados = next(lector)
        for fila in lector:
            if fila[5] == codigo_reporte:
                fila[6] = "Completado"
                fila[7] = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
                actualizado = True
            filas_actualizadas.append(fila)

    if actualizado:
        with open(ruta_csv, mode='w', newline='', encoding='utf-8') as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(encabezados)
            escritor.writerows(filas_actualizadas)

# ==== FUNCIONES PARA LA VENTANA ==== #

def generar_reporte():
    nombre = entry_nombre.get()
    clave_cliente = entry_claveCliente.get()
    nombre_negocio = entry_nombreNegocio.get()
    detalles = text_detalles.get("1.0", tk.END).strip()

    if not nombre or not clave_cliente or not nombre_negocio or not detalles:
        messagebox.showwarning("Campos vacíos", "Por favor llena todos los campos.")
        return

    codigo = generar_id_reportes()
    guardar_reporte(nombre, clave_cliente, nombre_negocio, detalles, codigo)

    messagebox.showinfo("Éxito", f"✅ El reporte de: {nombre} se ha guardado correctamente")
    entry_nombre.delete(0, tk.END)
    entry_claveCliente.delete(0, tk.END)
    entry_nombreNegocio.delete(0, tk.END)
    text_detalles.delete("1.0", tk.END)

def marcar_completado():
    codigo = entry_codigo.get()
    if not codigo:
        messagebox.showwarning("Código vacío", "Por favor ingresa un código de reporte válido")
        return

    actualizado = actualizar_reporte_completo(codigo)

    if actualizado:
        messagebox.showinfo("Reporte completado", f"✅ El reporte {codigo} ha sido completado con éxito")
        entry_codigo.delete(0, tk.END)
    else:
        messagebox.showerror("Código no encontrado", "El código de reporte no existe")

# ==== FUNCION PLACEHOLDER ==== #

def set_placeholder(entry, placeholder_text):
    entry.insert(0, placeholder_text)
    entry.config(fg='grey')

    def on_focus_in(event):
        if entry.get() == placeholder_text:
            entry.delete(0, 'end')
            entry.config(fg='black')

    def on_focus_out(event):
        if entry.get() == '':
            entry.insert(0, placeholder_text)
            entry.config(fg='grey')

    entry.bind('<FocusIn>', on_focus_in)
    entry.bind('<FocusOut>', on_focus_out)

# ===== UI (INTERFAZ GRÁFICA) ===== #

create_table()


ventana = tk.Tk()
ventana.title("ComerGest")
ventana.iconbitmap(os.path.join(os.path.dirname(__file__), "favicon.ico"))
ventana.geometry("500x550")
ventana.resizable(False, False)

tk.Label(ventana, text="Nombre de Cliente: ").pack(pady=(10, 0))
entry_nombre = tk.Entry(ventana, width=40)
entry_nombre.pack()
set_placeholder(entry_nombre, "Ej: Juan Perez")

tk.Label(ventana, text="Clave Cliente: ").pack(pady=(10, 0))
entry_claveCliente = tk.Entry(ventana, width=40)
entry_claveCliente.pack()
set_placeholder(entry_claveCliente, "Ej: 123456789")

tk.Label(ventana, text="Nombre del Negocio: ").pack(pady=(10, 0))
entry_nombreNegocio = tk.Entry(ventana, width=40)
entry_nombreNegocio.pack()
set_placeholder(entry_nombreNegocio, "Ej: El buen sabor")

tk.Label(ventana, text="Detalles del Reporte: ").pack(pady=(10, 0))
text_detalles = tk.Text(ventana, height=6, width=40)
text_detalles.pack()

tk.Button(ventana, text="Generar Reporte", command=generar_reporte, bg="#4CAF50", fg="white").pack(pady=10)

tk.Label(ventana, text="Código de Reporte a cerrar: ").pack(pady=(10, 0))
entry_codigo = tk.Entry(ventana, width=40)
entry_codigo.pack()
set_placeholder(entry_codigo, "Ej: REP-20250501-1234")

tk.Button(ventana, text="Marcar Reporte como Completo", command=marcar_completado, bg="#FF5733", fg="white").pack(pady=20)

ventana.mainloop()
