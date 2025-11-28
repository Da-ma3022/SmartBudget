import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import DB_NAME


def ventana_historial(root, usuario):
    ventana = tk.Toplevel(root)
    ventana.title("Historial de Gastos")
    ventana.geometry("700x400")
    ventana.config(bg="white")
    ventana.grab_set()

    tk.Label(
        ventana,
        text=f"Historial de gastos - {usuario}",
        font=("Arial", 16, "bold"),
        bg="white",
    ).pack(pady=10)

    # Treeview
    cols = ("fecha", "descripcion", "categoria", "monto")
    tree = ttk.Treeview(ventana, columns=cols, show="headings")
    tree.heading("fecha", text="Fecha")
    tree.heading("descripcion", text="Descripción")
    tree.heading("categoria", text="Categoría")
    tree.heading("monto", text="Monto")
    tree.column("fecha", width=150)
    tree.column("descripcion", width=300)
    tree.column("categoria", width=120)
    tree.column("monto", width=80, anchor="e")

    vsb = ttk.Scrollbar(ventana, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)

    tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
    vsb.pack(side="left", fill="y", pady=10)

    # (La carga de datos se hace en refresh_data para permitir refrescos posteriores)


    def refresh_data():
        for it in tree.get_children():
            tree.delete(it)

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT g.id, g.fecha, g.descripcion, c.nombre, g.monto
                FROM gastos g
                LEFT JOIN categorias c ON g.categoria_id = c.id
                LEFT JOIN usuarios u ON g.usuario_id = u.id
                WHERE u.username = ?
                ORDER BY g.fecha DESC
            """,
                (usuario,),
            )
            rows = cursor.fetchall()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error leyendo la base de datos:\n{e}", parent=ventana)
            ventana.destroy()
            return

        total = 0.0
        for r in rows:
            gid, fecha, descripcion, categoria, monto = r
            total += float(monto)
            tree.insert(
                "",
                "end",
                iid=str(gid),
                values=(fecha, descripcion, categoria, f"{monto:.2f}"),
            )

        lbl_total.config(text=f"Total mostrado: ${total:.2f}")

        try:
            ventana.lift()
            ventana.focus_force()
        except Exception:
            pass

        try:
            def _show_toast(msg="Actualizado", timeout=1200):
                toast = tk.Label(
                    ventana,
                    text=msg,
                    bg="#222",
                    fg="white",
                    padx=10,
                    pady=4,
                    font=("Arial", 10, "bold"),
                )
                toast.place(relx=0.72, rely=0.02)
                ventana.after(timeout, lambda: toast.destroy())

            _show_toast()
        except Exception:
            pass


    # Botones: Nuevo, Editar, Eliminar
    frm_buttons = tk.Frame(ventana, bg="white")
    frm_buttons.pack(side="right", fill="y", padx=8, pady=10)


    def _nuevo_gasto():
        try:
            from gui_gastos import ventana_registrar_gasto as _vrg
        except Exception as e:
            messagebox.showerror(
                "Error", f"No se puede abrir registrar gasto:\n{e}", parent=ventana
            )
            return

        v = _vrg(ventana, usuario)
        if v is not None:
            v.wait_window()
            refresh_data()


    def _editar_gasto():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning(
                "Selecciona", "Selecciona un gasto para editar", parent=ventana
            )
            return
        gid = sel[0]

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT descripcion, categoria_id, monto, fecha FROM gastos WHERE id = ?",
                (gid,),
            )
            row = cursor.fetchone()
            conn.close()
        except Exception as e:
            messagebox.showerror(
                "Error", f"Error leyendo la base de datos:\n{e}", parent=ventana
            )
            return

        if not row:
            messagebox.showerror("Error", "Gasto no encontrado", parent=ventana)
            refresh_data()
            return

        descripcion_act, categoria_id_act, monto_act, fecha_act = row

        win = tk.Toplevel(ventana)
        win.title("Editar Gasto")
        win.geometry("400x360")
        win.config(bg="white")
        win.grab_set()

        tk.Label(win, text="Editar gasto", font=("Arial", 14, "bold"), bg="white").pack(pady=8)
        tk.Label(win, text="Descripción:", bg="white").pack()
        e_desc = tk.Entry(win, width=40)
        e_desc.insert(0, descripcion_act)
        e_desc.pack(pady=4)

        tk.Label(win, text="Categoría:", bg="white").pack()
        combo = ttk.Combobox(win, width=37)
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre FROM categorias ORDER BY nombre")
            cats = cursor.fetchall()
            conn.close()
        except Exception:
            cats = []

        combo["values"] = [name for cid, name in cats]

        current_cat_name = None
        for cid, name in cats:
            if cid == categoria_id_act:
                current_cat_name = name
                break
        if current_cat_name:
            combo.set(current_cat_name)
        combo.pack(pady=4)

        tk.Label(win, text="Monto ($):", bg="white").pack()
        e_monto = tk.Entry(win, width=40)
        e_monto.insert(0, str(monto_act))
        e_monto.pack(pady=4)


        def _guardar_edicion():
            nueva_desc = e_desc.get().strip()
            nueva_cat = combo.get().strip()
            nuevo_monto = e_monto.get().strip()
            if nueva_desc == "" or nueva_cat == "" or nuevo_monto == "":
                messagebox.showwarning(
                    "Error", "Completa todos los campos", parent=win
                )
                return
            try:
                nuevo_monto_f = float(nuevo_monto)
            except Exception:
                messagebox.showwarning("Error", "Monto inválido", parent=win)
                return

            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM categorias WHERE nombre = ?", (nueva_cat,))
                r = cursor.fetchone()
                if not r:
                    messagebox.showerror("Error", "Categoría no válida", parent=win)
                    conn.close()
                    return
                new_cat_id = r[0]
                cursor.execute(
                    "UPDATE gastos SET descripcion = ?, categoria_id = ?, monto = ? WHERE id = ?",
                    (nueva_desc, new_cat_id, nuevo_monto_f, gid),
                )
                conn.commit()
                conn.close()
            except Exception as e:
                messagebox.showerror(
                    "Error", f"Error actualizando la base de datos:\n{e}", parent=win
                )
                return
            win.destroy()
            refresh_data()

        tk.Button(
            win, text="Guardar cambios", bg="#4CAF50", fg="white", command=_guardar_edicion
        ).pack(pady=12)


    def _eliminar_gasto():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning(
                "Selecciona", "Selecciona un gasto para eliminar", parent=ventana
            )
            return
        gid = sel[0]
        if not messagebox.askyesno(
            "Confirmar",
            "¿Eliminar el gasto seleccionado? Esta acción no se puede deshacer.",
            parent=ventana,
        ):
            return
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM gastos WHERE id = ?", (gid,))
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error eliminando el gasto:\n{e}", parent=ventana)
            return
        refresh_data()


    tk.Button(
        frm_buttons,
        text="Nuevo gasto",
        width=18,
        bg="#4CAF50",
        fg="white",
        command=_nuevo_gasto,
    ).pack(pady=6)
    tk.Button(
        frm_buttons,
        text="Editar gasto",
        width=18,
        bg="#2196F3",
        fg="white",
        command=_editar_gasto,
    ).pack(pady=6)
    tk.Button(
        frm_buttons,
        text="Eliminar gasto",
        width=18,
        bg="#d9534f",
        fg="white",
        command=_eliminar_gasto,
    ).pack(pady=6)

    # Label total
    lbl_total = tk.Label(
        ventana, text="Total mostrado: $0.00", font=("Arial", 12, "bold"), bg="white"
    )
    lbl_total.pack(side="bottom", pady=6)

    # Cargar datos inicialmente
    refresh_data()


    def cerrar():
        ventana.destroy()


    tk.Button(ventana, text="Cerrar", command=cerrar, bg="#d9534f", fg="white").pack(pady=8)
