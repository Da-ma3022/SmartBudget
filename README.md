SmartBudget
Aplicación de escritorio en Python para gestionar gastos, ingresos, reportes y visualizar estadísticas de manera sencilla e intuitiva.
SmartBudget fue desarrollado como un proyecto escolar y tiene como objetivo ayudar al usuario a llevar un control básico de sus finanzas personales mediante un sistema fácil de usar, con interfaz gráfica y base de datos local.
Características principales
-Registro de usuarios (login y registro)
-Gestión de gastos
-Gestión de ingresos
-Historial completo de movimientos
-Gráficas de gastos/ingresos
-Generación de reportes en PDF
-Base de datos local (SQLite)
-Interfaz gráfica desarrollada con Tkinter
-Código modular (cada pantalla en un archivo independiente)
Estructura del proyecto
SmartBudget/
│
├── app.py                     # Archivo principal que inicia la app
├── database.py                # Conexión y funciones para la base de datos
├── gastos.db                  # Base de datos SQLite ya inicializada
│
├── gui_login.py               # Pantalla de inicio de sesión
├── gui_register.py            # Pantalla de registro de usuarios
├── gui_home.py                # Menú principal
├── gui_gastos.py              # Gestión de gastos
├── gui_ingresos.py            # Gestión de ingresos
├── gui_historial.py           # Historial general
├── gui_historial_ingresos.py  # Historial de ingresos
├── gui_graficas.py            # Gráficas y estadísticas
│
├── reports/                   # Carpeta con los reportes PDF generados
├── __pycache__/               # Archivos internos de Python
└── test_import_gui_gastos.py  # Archivo de prueba

Requisitos
Asegúrate de tener instalado:
Python 3.10+
Librerías estándar (Tkinter ya viene con Python)
ReportLab (para generar PDF)
Instala reportlab así:     pip install reportlab

Cómo ejecutar el proyecto
Clona el repositorio: git clone https://github.com/Da-ma3022/SmartBudget.git
Entra al proyecto:  cd SmartBudget2
Ejecuta el archivo principal:
python app.py
¡Listo! Se abrirá la ventana principal de SmartBudget.
Base de datos inicial
El proyecto incluye el archivo gastos.db, que ya contiene:
Tablas creadas
Estructura lista
Usuario de prueba (para login)
Datos iniciales de ejemplo
Usuario de prueba
Puedes entrar al sistema con un usuario existente, por ejemplo:
Usuario: Eva
Contraseña: 123eva





Reportes
La aplicación genera reportes en formato PDF y los guarda automáticamente en la carpeta:
reports/
Estos archivos incluyen:
Gastos
Ingresos
Totales
Fechas
Cálculos automáticos


Interfaz gráfica
La app utiliza:
Tkinter (ventanas, botones, formularios)
ReportLab (PDFs)
Matplotlib (si agregas gráficas más avanzadas)
Diseñada para ser clara, limpia y fácil de usar.
Estado del proyecto
Primera versión terminada
Mejoras futuras (opcional):
Mejor diseño visual
Soporte para más categorías
Exportar a Excel
Multiusuario avanzado
Edición de movimientos
Desarrollado por...
Damariz Celeste Gonzalez Mozqueda
Proyecto académico · 2025
Universidad De Guadalajara CUTONALA
Este proyecto es de uso académico y personal.
