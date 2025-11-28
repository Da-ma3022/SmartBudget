import tkinter as tk


def ventana_principal(root, usuario):
    """Muestra la ventana principal.

    Si `root` es la instancia de `Tk` y está oculta, la deiconifica y la usa
    como ventana principal. En caso contrario crea un `Toplevel`.
    """
    use_root = False
    try:
        is_tk = isinstance(root, tk.Tk)
    except Exception:
        is_tk = False

    try:
        viewable = root.winfo_viewable()
    except Exception:
        viewable = False

    if is_tk and not viewable:
        ventana = root
        ventana.deiconify()
        # Si reutilizamos la ventana raíz, limpiar widgets previos
        try:
            for child in ventana.winfo_children():
                child.destroy()
        except Exception:
            pass
        use_root = True
        ventana.title("SmartBudget - Panel Principal")
        ventana.geometry("500x450")
        ventana.config(bg="white")
    else:
        ventana = tk.Toplevel(root)
        ventana.title("SmartBudget - Panel Principal")
        ventana.geometry("500x450")
        ventana.config(bg="white")

    tk.Label(
        ventana,
        text=f"¡Bienvenido, {usuario}!",
        font=("Arial", 20, "bold"),
        bg="white"
    ).pack(pady=20)

    # Botón Registrar gasto (import local para evitar ciclos de import)
    def _abrir_registrar_gasto():
        try:
            from gui_gastos import ventana_registrar_gasto as _vrg
        except Exception as e:
            # mostrar error en consola si no se puede importar
            print('Error importando gui_gastos:', e)
            return
        _vrg(root, usuario)

    tk.Button(
        ventana,
        text="Registrar gasto",
        width=20,
        bg="#4CAF50",
        fg="white",
        font=("Arial", 12, "bold"),
        command=_abrir_registrar_gasto
    ).pack(pady=10)

    # Botón Historial (abre ventana de historial)
    def _abrir_historial():
        try:
            from gui_historial import ventana_historial as _vh
        except Exception as e:
            print('Error importando gui_historial:', e)
            return
        _vh(root, usuario)

    tk.Button(
        ventana,
        text="Historial de gastos",
        width=20,
        bg="#2196F3",
        fg="white",
        font=("Arial", 12, "bold"),
        command=_abrir_historial
    ).pack(pady=10)

    # Botón Registrar ingreso
    def _abrir_registrar_ingreso():
        try:
            from gui_ingresos import ventana_registrar_ingreso as _vri
        except Exception as e:
            print('Error importando gui_ingresos:', e)
            return
        _vri(root, usuario)

    tk.Button(
        ventana,
        text="Registrar ingreso",
        width=20,
        bg="#2E8B57",
        fg="white",
        font=("Arial", 12, "bold"),
        command=_abrir_registrar_ingreso
    ).pack(pady=6)

    # Botón Historial de ingresos
    def _abrir_historial_ingresos():
        try:
            from gui_historial_ingresos import ventana_historial_ingresos as _vhi
        except Exception as e:
            print('Error importando gui_historial_ingresos:', e)
            return
        _vhi(root, usuario)

    tk.Button(
        ventana,
        text="Historial de ingresos",
        width=20,
        bg="#66BB6A",
        fg="white",
        font=("Arial", 12, "bold"),
        command=_abrir_historial_ingresos
    ).pack(pady=6)

    # Botón Gráficas
    def _abrir_graficas():
        try:
            from gui_graficas import ventana_graficas as _vg
        except Exception as e:
            print('Error importando gui_graficas:', e)
            return
        _vg(root, usuario)

    tk.Button(
        ventana,
        text="Gráficas",
        width=20,
        bg="#9C27B0",
        fg="white",
        font=("Arial", 12, "bold"),
        command=_abrir_graficas
    ).pack(pady=10)

    def cerrar_sesion():
        # Si estamos usando la ventana raíz, withdraw para ocultarla
        if use_root:
            ventana.withdraw()
            from gui_login import ventana_login
            ventana.after(10, lambda: ventana_login(root))
        else:
            ventana.destroy()
            from gui_login import ventana_login   # import dentro para evitar ciclos
            ventana.after(10, lambda: ventana_login(root))

    tk.Button(
        ventana,
        text="Cerrar Sesión",
        bg="#d9534f",
        fg="white",
        font=("Arial", 12, "bold"),
        width=15,
        command=cerrar_sesion
    ).pack(pady=20)

    # Para `Toplevel` hacemos modal y forcemos foco; para `root` no es necesario
    if not use_root:
        ventana.transient(root)
        ventana.grab_set()
        ventana.focus_force()
