import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib
from database import DB_NAME
from gui_register import ventana_registro
from gui_home import ventana_principal

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def ventana_login(root):
    ventana = tk.Toplevel(root)
    ventana.title("SmartBudget - Login")
    ventana.geometry("400x350")
    ventana.configure(bg="#f7f7f7")
    ventana.grab_set()

    tk.Label(
        ventana,
        text="Bienvenido a SmartBudget",
        font=("Arial", 18, "bold"),
        bg="#f7f7f7"
    ).pack(pady=15)

    # USUARIO
    tk.Label(ventana, text="Usuario:", bg="#f7f7f7").pack()
    entry_user = tk.Entry(ventana)
    entry_user.pack(pady=5)

    # CONTRASEÑA
    tk.Label(ventana, text="Contraseña:", bg="#f7f7f7").pack()
    entry_pass = tk.Entry(ventana, show="*")
    entry_pass.pack(pady=5)

    def iniciar_sesion():
        username = entry_user.get().strip()
        password = entry_pass.get().strip()

        if username == "" or password == "":
            messagebox.showwarning("Error", "Ingresa usuario y contraseña")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM usuarios WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()

        if row is None:
            messagebox.showerror("Error", "Usuario no encontrado")
            return

        if hash_password(password) == row[0]:
            messagebox.showinfo("Bienvenido", f"Bienvenido {username}!")
            ventana.destroy()
            ventana_principal(root, username)
        else:
            messagebox.showerror("Error", "Contraseña incorrecta")

    tk.Button(
        ventana,
        text="Iniciar Sesión",
        bg="#4CAF50",
        fg="white",
        width=20,
        command=iniciar_sesion
    ).pack(pady=10)

    tk.Button(
        ventana,
        text="Crear Cuenta",
        bg="#2196F3",
        fg="white",
        width=20,
        command=lambda: ventana_registro(root)
    ).pack(pady=5)

