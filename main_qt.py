import sys
import os
from PySide6.QtWidgets import QApplication

# Ajouter le répertoire src au chemin Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui_qt.main_window_ui import MainWindowUI

def main():
    app = QApplication(sys.argv)
    win = MainWindowUI()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
