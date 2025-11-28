import tkinter as tk
from database import crear_base_datos
from gui_login import ventana_login

def main():
    # Ventana raíz oculta
    root = tk.Tk()
    root.withdraw()

    # Crear base de datos y tablas
    crear_base_datos()  

    # Abrir ventana de login
    ventana_login(root)

    # Bucle principal de Tkinter
    root.mainloop()    
    
if __name__ == "__main__":
    main()
