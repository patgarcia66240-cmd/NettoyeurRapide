#!/usr/bin/env python3
"""
Point d'entrée principal pour l'application NettoyeurRapide
"""

import sys
import os

# Ajouter le répertoire src au chemin Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from gui_qt.main_window_ui import MainWindowUI

def main():
    """Fonction principale"""
    app = QApplication(sys.argv)
    app.setApplicationName("NettoyeurRapide")
    app.setOrganizationName("NettoyeurRapide")

    # Créer la fenêtre principale
    window = MainWindowUI()
    window.show()

    # Exécuter l'application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()