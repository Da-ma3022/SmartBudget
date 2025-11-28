import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import DB_NAME
from datetime import datetime

def ventana_registrar_gasto(root, usuario):

    ventana = tk.Toplevel(root)
    ventana.title("Registrar Gasto")
    ventana.geometry("400x380")
    ventana.config(bg="white")
    ventana.grab_set()

    # Título
    tk.Label(
        ventana,
        text="Registrar nuevo gasto",
        font=("Arial", 16, "bold"),
        bg="white"
    ).pack(pady=10)

    # Fecha (autocompletada)
    fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tk.Label(ventana, text=f"Fecha: {fecha_str}", bg="white").pack(pady=3)

    # Descripción
    tk.Label(ventana, text="Descripción:", bg="white").pack()
    entry_desc = tk.Entry(ventana, width=30)
    entry_desc.pack(pady=5)

    # Categoría
    tk.Label(ventana, text="Categoría:", bg="white").pack()
    combo_categoria = ttk.Combobox(ventana, width=27)
    combo_categoria.pack(pady=5)

    # Cargar categorías desde BD
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM categorias")
    categorias = [c[0] for c in cursor.fetchall()]
    conn.close()
    combo_categoria["values"] = categorias

    # Monto
    tk.Label(ventana, text="Monto ($):", bg="white").pack()
    entry_monto = tk.Entry(ventana, width=30)
    entry_monto.pack(pady=5)

    # Guardar gasto
    def guardar_gasto():
        descripcion = entry_desc.get().strip()
        categoria = combo_categoria.get().strip()
        monto = entry_monto.get().strip()

        if descripcion == "" or categoria == "" or monto == "":
            messagebox.showwarning("Error", "Completa todos los campos", parent=ventana)
            return

        try:
            monto = float(monto)
        except:
            messagebox.showwarning("Error", "Monto inválido", parent=ventana)
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # obtener id de usuario
        cursor.execute("SELECT id FROM usuarios WHERE username = ?", (usuario,))
        user_id = cursor.fetchone()[0]

        # obtener id de categoria
        cursor.execute("SELECT id FROM categorias WHERE nombre = ?", (categoria,))
        cat_id = cursor.fetchone()[0]

        # insertar gasto (usamos la fecha calculada)
        cursor.execute("""
            INSERT INTO gastos (descripcion, categoria_id, monto, fecha, usuario_id)
            VALUES (?, ?, ?, ?, ?)
        """, (descripcion, cat_id, monto, fecha_str, user_id))

        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Gasto registrado correctamente", parent=ventana)
        ventana.destroy()

    tk.Button(
        ventana,
        text="Guardar Gasto",
        bg="#4CAF50",
        fg="white",
        width=20,
        command=guardar_gasto
    ).pack(pady=20)

    # Devolver la ventana para que el llamador pueda esperar su cierre
    return ventana
