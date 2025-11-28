import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime
from database import DB_NAME


def ventana_registrar_ingreso(root, usuario):
    ventana = tk.Toplevel(root)
    ventana.title("Registrar Ingreso")
    ventana.geometry("400x320")
    ventana.config(bg="white")
    ventana.grab_set()

    tk.Label(ventana, text="Registrar nuevo ingreso", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

    tk.Label(ventana, text="Descripción:", bg="white").pack()
    entry_desc = tk.Entry(ventana, width=34)
    entry_desc.pack(pady=6)

    tk.Label(ventana, text="Monto ($):", bg="white").pack()
    entry_monto = tk.Entry(ventana, width=34)
    entry_monto.pack(pady=6)

    fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tk.Label(ventana, text=f"Fecha: {fecha_str}", bg="white").pack(pady=4)

    def guardar_ingreso():
        descripcion = entry_desc.get().strip()
        monto = entry_monto.get().strip()
        if descripcion == "" or monto == "":
            messagebox.showwarning("Error", "Completa todos los campos", parent=ventana)
            return
        try:
            monto_f = float(monto)
        except:
            messagebox.showwarning("Error", "Monto inválido", parent=ventana)
            return

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            # obtener id de usuario
            cursor.execute("SELECT id FROM usuarios WHERE username = ?", (usuario,))
            r = cursor.fetchone()
            if not r:
                messagebox.showerror("Error", "Usuario no encontrado en BD", parent=ventana)
                conn.close()
                return
            user_id = r[0]
            cursor.execute("INSERT INTO ingresos (descripcion, monto, fecha, usuario_id) VALUES (?, ?, ?, ?)",
                           (descripcion, monto_f, fecha_str, user_id))
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando ingreso:\n{e}", parent=ventana)
            return

        messagebox.showinfo("Éxito", "Ingreso registrado correctamente", parent=ventana)
        ventana.destroy()

    tk.Button(ventana, text="Guardar Ingreso", bg="#4CAF50", fg="white", width=20, command=guardar_ingreso).pack(pady=12)

    return ventana
