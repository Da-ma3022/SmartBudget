import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import DB_NAME


def ventana_historial_ingresos(root, usuario):
    ventana = tk.Toplevel(root)
    ventana.title("Historial de Ingresos")
    ventana.geometry("700x400")
    ventana.config(bg="white")
    ventana.grab_set()

    tk.Label(ventana, text=f"Historial de ingresos - {usuario}", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

    cols = ("fecha", "descripcion", "monto")
    tree = ttk.Treeview(ventana, columns=cols, show="headings")
    tree.heading("fecha", text="Fecha")
    tree.heading("descripcion", text="Descripción")
    tree.heading("monto", text="Monto")
    tree.column("fecha", width=180)
    tree.column("descripcion", width=360)
    tree.column("monto", width=100, anchor="e")

    vsb = ttk.Scrollbar(ventana, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)

    tree.pack(side="left", fill="both", expand=True, padx=(10,0), pady=10)
    vsb.pack(side="left", fill="y", pady=10)

    frm_buttons = tk.Frame(ventana, bg="white")
    frm_buttons.pack(side="right", fill="y", padx=8, pady=10)

    def refresh():
        for it in tree.get_children():
            tree.delete(it)
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT g.id, g.fecha, g.descripcion, g.monto FROM ingresos g LEFT JOIN usuarios u ON g.usuario_id = u.id WHERE u.username = ? ORDER BY g.fecha DESC", (usuario,))
            rows = cursor.fetchall()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error leyendo BD:\n{e}", parent=ventana)
            ventana.destroy()
            return
        total = 0.0
        for r in rows:
            gid, fecha, desc, monto = r
            total += float(monto)
            tree.insert("", "end", iid=str(gid), values=(fecha, desc, f"{monto:.2f}"))
        lbl_total.config(text=f"Total mostrado: ${total:.2f}")
        # Mantener la ventana de historial de ingresos al frente y con foco
        try:
            ventana.lift()
            ventana.focus_force()
        except Exception:
            pass
        # Toast de "Actualizado"
        try:
            def _show_toast(msg="Actualizado", timeout=1200):
                toast = tk.Label(ventana, text=msg, bg="#222", fg="white", padx=10, pady=4, font=("Arial", 10, "bold"))
                toast.place(relx=0.68, rely=0.02)
                ventana.after(timeout, lambda: toast.destroy())
            _show_toast()
        except Exception:
            pass

    def nuevo():
        try:
            from gui_ingresos import ventana_registrar_ingreso as _vri
        except Exception as e:
            messagebox.showerror("Error", f"No se puede abrir registrar ingreso:\n{e}", parent=ventana)
            return
        # abrir el registro como hijo de esta ventana de historial de ingresos
        v = _vri(ventana, usuario)
        if v is not None:
            v.wait_window()
            refresh()

    def eliminar():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Selecciona", "Selecciona un ingreso para eliminar", parent=ventana)
            return
        gid = sel[0]
        if not messagebox.askyesno("Confirmar", "Eliminar ingreso seleccionado?", parent=ventana):
            return
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ingresos WHERE id = ?", (gid,))
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error eliminando:\n{e}", parent=ventana)
            return
        refresh()

    tk.Button(frm_buttons, text="Nuevo ingreso", width=18, bg="#4CAF50", fg="white", command=nuevo).pack(pady=6)
    def editar():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Selecciona", "Selecciona un ingreso para editar", parent=ventana)
            return
        gid = sel[0]
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT descripcion, monto, fecha FROM ingresos WHERE id = ?", (gid,))
            row = cursor.fetchone()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error leyendo BD:\n{e}", parent=ventana)
            return
        if not row:
            messagebox.showerror("Error", "Ingreso no encontrado", parent=ventana)
            refresh()
            return

        descripcion_act, monto_act, fecha_act = row

        win = tk.Toplevel(ventana)
        win.title("Editar Ingreso")
        win.geometry("400x320")
        win.config(bg="white")
        win.grab_set()

        tk.Label(win, text="Editar ingreso", font=("Arial", 14, "bold"), bg="white").pack(pady=8)
        tk.Label(win, text="Descripción:", bg="white").pack()
        e_desc = tk.Entry(win, width=36)
        e_desc.insert(0, descripcion_act)
        e_desc.pack(pady=6)

        tk.Label(win, text="Monto ($):", bg="white").pack()
        e_monto = tk.Entry(win, width=36)
        e_monto.insert(0, str(monto_act))
        e_monto.pack(pady=6)

        def _guardar():
            nd = e_desc.get().strip()
            nm = e_monto.get().strip()
            if nd == "" or nm == "":
                messagebox.showwarning("Error", "Completa todos los campos", parent=win)
                return
            try:
                nmf = float(nm)
            except:
                messagebox.showwarning("Error", "Monto inválido", parent=win)
                return
            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("UPDATE ingresos SET descripcion = ?, monto = ? WHERE id = ?", (nd, nmf, gid))
                conn.commit()
                conn.close()
            except Exception as e:
                messagebox.showerror("Error", f"Error actualizando:\n{e}", parent=win)
                return
            win.destroy()
            refresh()

        tk.Button(win, text="Guardar cambios", bg="#4CAF50", fg="white", command=_guardar).pack(pady=10)

    tk.Button(frm_buttons, text="Editar ingreso", width=18, bg="#2196F3", fg="white", command=editar).pack(pady=6)
    tk.Button(frm_buttons, text="Eliminar ingreso", width=18, bg="#d9534f", fg="white", command=eliminar).pack(pady=6)

    lbl_total = tk.Label(ventana, text="Total mostrado: $0.00", font=("Arial", 12, "bold"), bg="white")
    lbl_total.pack(side="bottom", pady=6)

    refresh()

    def cerrar():
        ventana.destroy()

    tk.Button(ventana, text="Cerrar", command=cerrar, bg="#d9534f", fg="white").pack(pady=8)
