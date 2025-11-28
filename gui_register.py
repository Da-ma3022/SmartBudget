import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib
from database import DB_NAME
from datetime import datetime

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def ventana_registro(root):
    ventana = tk.Toplevel(root)
    ventana.title("Crear Cuenta")
    ventana.geometry("400x350")
    ventana.configure(bg="#f7f7f7")
    ventana.grab_set()

    tk.Label(
        ventana,
        text="Registro de Usuario",
        font=("Arial", 18, "bold"),
        bg="#f7f7f7"
    ).pack(pady=10)

    tk.Label(ventana, text="Nuevo Usuario:", bg="#f7f7f7").pack()
    entry_user = tk.Entry(ventana)
    entry_user.pack(pady=5)

    tk.Label(ventana, text="Nueva Contraseña:", bg="#f7f7f7").pack()
    entry_pass = tk.Entry(ventana, show="*")
    entry_pass.pack(pady=5)

    def registrar():
        username = entry_user.get().strip()
        password = entry_pass.get().strip()

        if username == "" or password == "":
            messagebox.showwarning("Error", "Completa todos los campos")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Verificar duplicados
        cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
        if cursor.fetchone():
            messagebox.showerror("Error", "El usuario ya existe")
            conn.close()
            return

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            "INSERT INTO usuarios (username, password_hash, fecha_registro) VALUES (?, ?, ?)",
            (username, hash_password(password), fecha)
        )

        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Usuario registrado correctamente")
        ventana.destroy()

    tk.Button(
        ventana,
        text="Registrar",
        bg="#4CAF50",
        fg="white",
        width=20,
        command=registrar
    ).pack(pady=15)

