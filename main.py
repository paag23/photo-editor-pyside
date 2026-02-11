# main.py

''' 
Responsabilidad única:
    Crear la aplicación Qt y lanzar la ventana principal.
Notas importantes:
    - main.py no procesa imágenes
    - No contiene lógica de negocio
    - Solo orquesta el arranque 
'''

import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
