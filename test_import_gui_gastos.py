import importlib
import traceback
try:
    mod = importlib.import_module('gui_gastos')
    print('Imported gui_gastos OK')
    print('Has ventana_registrar_gasto?', hasattr(mod, 'ventana_registrar_gasto'))
    print('Attributes:', [a for a in dir(mod) if 'ventana' in a.lower()])
except Exception as e:
    traceback.print_exc()
