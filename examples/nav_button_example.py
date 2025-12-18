"""
Exemple d'utilisation de NavButton
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QScrollArea
from PySide6.QtCore import Qt

from src.gui_qt.components.nav_button import NavButton


class NavButtonExample(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Configuration de l'interface"""
        self.setWindowTitle("NavButton Example")
        self.setGeometry(100, 100, 600, 400)

        # Widget principal
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # === Différents types de boutons ===

        # Boutons primaires
        primary_layout = QHBoxLayout()
        primary_layout.addWidget(QLabel("Primary:"))

        btn_primary_small = NavButton("Small Primary", self)
        btn_primary_small.sizeType = "small"
        btn_primary_small.set_primary()

        btn_primary_medium = NavButton("Medium Primary", self)
        btn_primary_medium.set_primary()

        btn_primary_large = NavButton("Large Primary", self)
        btn_primary_large.sizeType = "large"
        btn_primary_large.set_primary()

        primary_layout.addWidget(btn_primary_small)
        primary_layout.addWidget(btn_primary_medium)
        primary_layout.addWidget(btn_primary_large)

        # Boutons secondaires
        secondary_layout = QHBoxLayout()
        secondary_layout.addWidget(QLabel("Secondary:"))

        btn_secondary_small = NavButton("Small Secondary", self)
        btn_secondary_small.sizeType = "small"
        btn_secondary_small.set_secondary()

        btn_secondary_medium = NavButton("Medium Secondary", self)
        btn_secondary_medium.set_secondary()

        btn_secondary_large = NavButton("Large Secondary", self)
        btn_secondary_large.sizeType = "large"
        btn_secondary_large.set_secondary()

        secondary_layout.addWidget(btn_secondary_small)
        secondary_layout.addWidget(btn_secondary_medium)
        secondary_layout.addWidget(btn_secondary_large)

        # Boutons accent
        accent_layout = QHBoxLayout()
        accent_layout.addWidget(QLabel("Accent:"))

        btn_accent_small = NavButton("Small Accent", self)
        btn_accent_small.sizeType = "small"
        btn_accent_small.set_accent()

        btn_accent_medium = NavButton("Medium Accent", self)
        btn_accent_medium.set_accent()

        btn_accent_large = NavButton("Large Accent", self)
        btn_accent_large.sizeType = "large"
        btn_accent_large.set_accent()

        accent_layout.addWidget(btn_accent_small)
        accent_layout.addWidget(btn_accent_medium)
        accent_layout.addWidget(btn_accent_large)

        # === Coins carrés vs arrondis ===
        radius_layout = QHBoxLayout()
        radius_layout.addWidget(QLabel("Radius:"))

        btn_rounded = NavButton("Rounded", self)
        btn_rounded.rounded = True
        btn_rounded.set_primary()

        btn_square = NavButton("Square", self)
        btn_square.rounded = False
        btn_square.set_secondary()

        radius_layout.addWidget(btn_rounded)
        radius_layout.addWidget(btn_square)

        # === Boutons désactivés ===
        disabled_layout = QHBoxLayout()
        disabled_layout.addWidget(QLabel("Disabled:"))

        btn_disabled_primary = NavButton("Disabled Primary", self)
        btn_disabled_primary.set_primary()
        btn_disabled_primary.setEnabled(False)

        btn_disabled_secondary = NavButton("Disabled Secondary", self)
        btn_disabled_secondary.set_secondary()
        btn_disabled_secondary.setEnabled(False)

        disabled_layout.addWidget(btn_disabled_primary)
        disabled_layout.addWidget(btn_disabled_secondary)

        # Ajouter tous les layouts au layout principal
        layout.addLayout(primary_layout)
        layout.addLayout(secondary_layout)
        layout.addLayout(accent_layout)
        layout.addLayout(radius_layout)
        layout.addLayout(disabled_layout)

        # Ajouter un espace vide pour le scroll
        layout.addStretch()

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        self.setCentralWidget(scroll_area)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    example = NavButtonExample()
    example.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()