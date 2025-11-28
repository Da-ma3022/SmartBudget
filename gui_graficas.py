import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
from database import DB_NAME
import os

# Matplotlib import (may require installation)
try:
    import matplotlib
except Exception:
    matplotlib = None
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except Exception:
    Figure = None
    FigureCanvasTkAgg = None

# PDF export (fpdf2)
try:
    from fpdf import FPDF
except Exception:
    FPDF = None


def ventana_graficas(root, usuario):
    """Ventana de gráficas: totales, comparación y exportar PDF."""
    ventana = tk.Toplevel(root)
    ventana.title("SmartBudget - Gráficas")
    ventana.geometry("800x600")
    ventana.config(bg="white")
    ventana.grab_set()

    # Header
    tk.Label(ventana, text=f"Resumen y Gráficas - {usuario}", font=("Arial", 16, "bold"), bg="white").pack(pady=8)

    # Filtros: desde / hasta
    frm_filters = tk.Frame(ventana, bg="white")
    frm_filters.pack(pady=6)

    tk.Label(frm_filters, text="Desde (YYYY-MM-DD):", bg="white").grid(row=0, column=0, padx=4)
    entry_desde = tk.Entry(frm_filters, width=12)
    entry_desde.grid(row=0, column=1, padx=4)

    tk.Label(frm_filters, text="Hasta (YYYY-MM-DD):", bg="white").grid(row=0, column=2, padx=4)
    entry_hasta = tk.Entry(frm_filters, width=12)
    entry_hasta.grid(row=0, column=3, padx=4)

    def _parse_date(s):
        if not s:
            return None
        try:
            return datetime.strptime(s, "%Y-%m-%d")
        except Exception:
            return None

    # Area for totals
    frm_totals = tk.Frame(ventana, bg="white")
    frm_totals.pack(pady=6)
    lbl_ingresos = tk.Label(frm_totals, text="Ingresos: $0.00", font=("Arial", 12), bg="white")
    lbl_gastos = tk.Label(frm_totals, text="Gastos: $0.00", font=("Arial", 12), bg="white")
    lbl_balance = tk.Label(frm_totals, text="Balance: $0.00", font=("Arial", 12, "bold"), bg="white")
    lbl_ingresos.grid(row=0, column=0, padx=20)
    lbl_gastos.grid(row=0, column=1, padx=20)
    lbl_balance.grid(row=0, column=2, padx=20)

    # Placeholder for figure
    frm_fig = tk.Frame(ventana, bg="white")
    frm_fig.pack(fill="both", expand=True)

    fig_canvas = None
    fig = None

    def _draw_charts(desde=None, hasta=None):
        nonlocal fig_canvas, fig
        # Query totals and by-category
        q_params = [usuario]
        date_where = ""
        if desde:
            date_where += " AND date(g.fecha) >= date(?)"
            q_params.append(desde.strftime("%Y-%m-%d"))
        if hasta:
            date_where += " AND date(g.fecha) <= date(?)"
            q_params.append(hasta.strftime("%Y-%m-%d"))

        # Gastos total and by category
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(f"SELECT SUM(g.monto) FROM gastos g LEFT JOIN usuarios u ON g.usuario_id = u.id WHERE u.username = ? {date_where}", q_params)
        gasto_total = cursor.fetchone()[0] or 0.0

        cursor.execute(f"SELECT c.nombre, SUM(g.monto) FROM gastos g LEFT JOIN categorias c ON g.categoria_id = c.id LEFT JOIN usuarios u ON g.usuario_id = u.id WHERE u.username = ? {date_where} GROUP BY c.nombre ORDER BY SUM(g.monto) DESC", q_params)
        by_cat = cursor.fetchall()

        # Ingresos total (tabla ingresos) with same date range
        try:
            # build params for ingresos query separately because alias is i
            q_params_ing = [usuario]
            date_where_ing = ""
            if desde:
                date_where_ing += " AND date(i.fecha) >= date(?)"
                q_params_ing.append(desde.strftime("%Y-%m-%d"))
            if hasta:
                date_where_ing += " AND date(i.fecha) <= date(?)"
                q_params_ing.append(hasta.strftime("%Y-%m-%d"))
            cursor.execute(f"SELECT SUM(i.monto) FROM ingresos i LEFT JOIN usuarios u ON i.usuario_id = u.id WHERE u.username = ? {date_where_ing}", q_params_ing)
            ingresos_total = cursor.fetchone()[0] or 0.0
        except Exception:
            ingresos_total = 0.0

        conn.close()

        balance = ingresos_total - gasto_total

        lbl_ingresos.config(text=f"Ingresos: ${ingresos_total:.2f}")
        lbl_gastos.config(text=f"Gastos: ${gasto_total:.2f}")
        lbl_balance.config(text=f"Balance: ${balance:.2f}")

        # Draw matplotlib bars
        if Figure is None:
            # matplotlib not available
            for child in frm_fig.winfo_children():
                child.destroy()
            tk.Label(frm_fig, text="matplotlib no está instalado. Instala matplotlib para ver gráficos.", bg="white", fg="red").pack(pady=20)
            return

        # Create figure
        if fig_canvas:
            fig_canvas.get_tk_widget().destroy()

        fig = Figure(figsize=(9,4), dpi=100)
        # layout: 1 row, 3 cols
        ax_cat = fig.add_subplot(131)
        ax_month = fig.add_subplot(132)
        ax_comp = fig.add_subplot(133)

        # Category bar chart
        cats = [r[0] for r in by_cat]
        vals = [r[1] or 0.0 for r in by_cat]
        if not cats:
            cats = ['Sin datos']
            vals = [0]
        ax_cat.bar(cats, vals, color='tab:orange')
        ax_cat.set_title('Gasto por categoría')
        ax_cat.tick_params(axis='x', labelrotation=30)

        # Monthly totals (last 6 months) for gastos
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT strftime('%Y-%m', g.fecha) as ym, SUM(g.monto) FROM gastos g LEFT JOIN usuarios u ON g.usuario_id = u.id WHERE u.username = ? {date_where} GROUP BY ym ORDER BY ym DESC LIMIT 6", q_params)
            months = cursor.fetchall()
        except Exception:
            months = []
        conn.close()

        if months:
            # months are (ym, sum) ordered desc; reverse to chronological
            months = list(reversed(months))
            m_labels = [m[0] for m in months]
            m_vals = [m[1] or 0.0 for m in months]
        else:
            m_labels = ['Sin datos']
            m_vals = [0]

        ax_month.bar(m_labels, m_vals, color='tab:purple')
        ax_month.set_title('Totales por mes')
        ax_month.tick_params(axis='x', labelrotation=30)

        # Comparison chart
        labels = ['Ingresos', 'Gastos', 'Balance']
        comp = [ingresos_total, gasto_total, balance]
        colors = ['tab:green', 'tab:red', 'tab:blue']
        ax_comp.bar(labels, comp, color=colors)
        ax_comp.set_title('Comparación')

        # Add legends / grid for readability
        for a in (ax_cat, ax_month, ax_comp):
            a.grid(axis='y', linestyle='--', alpha=0.4)

        fig.tight_layout()
        fig_canvas = FigureCanvasTkAgg(fig, master=frm_fig)
        fig_canvas.draw()
        fig_canvas.get_tk_widget().pack(fill='both', expand=True)

    def _filtrar():
        desde = _parse_date(entry_desde.get().strip())
        hasta = _parse_date(entry_hasta.get().strip())
        if entry_desde.get().strip() and not desde:
            messagebox.showwarning('Fecha', 'Formato fecha desde inválido, usar YYYY-MM-DD')
            return
        if entry_hasta.get().strip() and not hasta:
            messagebox.showwarning('Fecha', 'Formato fecha hasta inválido, usar YYYY-MM-DD')
            return
        _draw_charts(desde, hasta)

    tk.Button(frm_filters, text='Filtrar', bg='#2196F3', fg='white', command=_filtrar).grid(row=0, column=4, padx=8)

    # Export PDF
    def _export_pdf():
        desde = _parse_date(entry_desde.get().strip())
        hasta = _parse_date(entry_hasta.get().strip())
        # Generate a temporary image of the figure
        if fig is None:
            messagebox.showwarning('Exportar', 'No hay gráfico para exportar. Filtra primero.')
            return
        img_path = 'temp_grafica.png'
        try:
            fig.savefig(img_path, dpi=150)
        except Exception as e:
            messagebox.showerror('Exportar', f'Error creando imagen del gráfico:\n{e}')
            return

        if FPDF is None:
            messagebox.showwarning('PDF', 'Para exportar a PDF instala fpdf2: pip install fpdf2', parent=ventana)
            return

        # compute totals again
        q_params = [usuario]
        date_where = ''
        if desde:
            date_where += ' AND date(g.fecha) >= date(?)'
            q_params.append(desde.strftime('%Y-%m-%d'))
        if hasta:
            date_where += ' AND date(g.fecha) <= date(?)'
            q_params.append(hasta.strftime('%Y-%m-%d'))
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(f"SELECT SUM(g.monto) FROM gastos g LEFT JOIN usuarios u ON g.usuario_id = u.id WHERE u.username = ? {date_where}", q_params)
        gasto_total = cursor.fetchone()[0] or 0.0
        conn.close()
        # compute ingresos_total as well
        q_params_ing = [usuario]
        date_where_ing = ''
        if desde:
            date_where_ing += ' AND date(i.fecha) >= date(?)'
            q_params_ing.append(desde.strftime('%Y-%m-%d'))
        if hasta:
            date_where_ing += ' AND date(i.fecha) <= date(?)'
            q_params_ing.append(hasta.strftime('%Y-%m-%d'))
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT SUM(i.monto) FROM ingresos i LEFT JOIN usuarios u ON i.usuario_id = u.id WHERE u.username = ? {date_where_ing}", q_params_ing)
            ingresos_total = cursor.fetchone()[0] or 0.0
        except Exception:
            ingresos_total = 0.0
        conn.close()
        balance = ingresos_total - gasto_total

        # Save PDF with detailed tables
        reports_dir = 'reports'
        try:
            os.makedirs(reports_dir, exist_ok=True)
        except Exception:
            pass
        # make a human-friendly filename: reporte-<usuario>-<YYYY-MM-DD_HHMMSS>.pdf
        safe_user = ''.join(c if (c.isalnum() or c in '-_') else '_' for c in usuario)
        filename = os.path.join(
            reports_dir,
            f"reporte-{safe_user}-{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.pdf",
        )
        try:
            # Fetch detailed rows for gastos and ingresos
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(f"SELECT g.fecha, g.descripcion, c.nombre, g.monto FROM gastos g LEFT JOIN categorias c ON g.categoria_id = c.id LEFT JOIN usuarios u ON g.usuario_id = u.id WHERE u.username = ? {date_where} ORDER BY g.fecha ASC", q_params)
            gastos_rows = cursor.fetchall()
            # ingresos details
            cursor.execute(f"SELECT i.fecha, i.descripcion, i.monto FROM ingresos i LEFT JOIN usuarios u ON i.usuario_id = u.id WHERE u.username = ? {date_where_ing} ORDER BY i.fecha ASC", q_params_ing)
            ingresos_rows = cursor.fetchall()
            conn.close()

            pdf = FPDF(unit='mm', format='A4')
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font('Helvetica', 'B', 16)
            pdf.cell(0, 10, f'Reporte de gastos - {usuario}', ln=True)
            pdf.set_font('Helvetica', size=10)
            pdf.cell(0, 6, f'Fecha de generación: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', ln=True)
            drange = 'Sin filtro'
            if desde or hasta:
                d1 = desde.strftime('%Y-%m-%d') if desde else 'inicio'
                d2 = hasta.strftime('%Y-%m-%d') if hasta else 'hoy'
                drange = f'{d1} a {d2}'
            pdf.cell(0, 6, f'Rango aplicado: {drange}', ln=True)
            pdf.ln(4)
            pdf.set_font('Helvetica', size=11)
            pdf.cell(0, 6, f'Total Ingresos: ${ingresos_total:.2f}', ln=True)
            pdf.cell(0, 6, f'Total Gastos: ${gasto_total:.2f}', ln=True)
            pdf.cell(0, 6, f'Balance final: ${balance:.2f}', ln=True)
            pdf.ln(6)

            # Detailed Gastos table
            pdf.set_font('Helvetica', 'B', 12)
            pdf.cell(0, 8, 'Gastos', ln=True)
            pdf.set_font('Helvetica', 'B', 10)
            # Column widths (mm): fecha 40, desc 80, categoria 40, monto 20 = 180 avail
            col_w = [40, 80, 40, 20]
            pdf.cell(col_w[0], 7, 'Fecha', border=1)
            pdf.cell(col_w[1], 7, 'Descripción', border=1)
            pdf.cell(col_w[2], 7, 'Categoría', border=1)
            pdf.cell(col_w[3], 7, 'Monto', border=1, ln=1)
            pdf.set_font('Helvetica', size=9)
            for fr, desc, cat, monto in gastos_rows:
                desc_text = (desc.replace('\n', ' ') if desc else '')
                if len(desc_text) > 60:
                    desc_text = desc_text[:57] + '...'
                pdf.cell(col_w[0], 6, fr, border=1)
                pdf.cell(col_w[1], 6, desc_text, border=1)
                pdf.cell(col_w[2], 6, (cat or ''), border=1)
                pdf.cell(col_w[3], 6, f"${float(monto):.2f}", border=1, ln=1, align='R')

            pdf.ln(4)

            # Detailed Ingresos table
            pdf.set_font('Helvetica', 'B', 12)
            pdf.cell(0, 8, 'Ingresos', ln=True)
            pdf.set_font('Helvetica', 'B', 10)
            # Column widths: fecha 40, desc 120, monto 20
            col_w_i = [40, 120, 20]
            pdf.cell(col_w_i[0], 7, 'Fecha', border=1)
            pdf.cell(col_w_i[1], 7, 'Descripción', border=1)
            pdf.cell(col_w_i[2], 7, 'Monto', border=1, ln=1)
            pdf.set_font('Helvetica', size=9)
            for fr, desc, monto in ingresos_rows:
                desc_text = (desc.replace('\n', ' ') if desc else '')
                if len(desc_text) > 90:
                    desc_text = desc_text[:87] + '...'
                pdf.cell(col_w_i[0], 6, fr, border=1)
                pdf.cell(col_w_i[1], 6, desc_text, border=1)
                pdf.cell(col_w_i[2], 6, f"${float(monto):.2f}", border=1, ln=1, align='R')
            # After tables, create a new page for the chart so it doesn't overlap
            try:
                pdf.add_page()
                page_w = 210
                margin = 15
                avail_w = page_w - 2 * margin
                # place image at top area of the new page
                x = margin
                y = pdf.get_y()
                # Limit image height to avoid overflow (approx 100mm)
                pdf.image(img_path, x=x, y=y, w=avail_w)
            except Exception:
                # If image fails, continue — tables are already written
                pass

            pdf.output(filename)
            # Remove temporary image if it exists
            try:
                if os.path.exists(img_path):
                    os.remove(img_path)
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror('PDF', f'Error generando PDF:\n{e}', parent=ventana)
            return

        messagebox.showinfo('PDF', f'Reporte guardado: {filename}', parent=ventana)

    tk.Button(ventana, text='Exportar PDF', bg='#4CAF50', fg='white', command=_export_pdf).pack(pady=6)

    # draw initial charts
    _draw_charts()

    def cerrar():
        ventana.destroy()

    tk.Button(ventana, text='Cerrar', bg='#d9534f', fg='white', command=cerrar).pack(pady=6)
