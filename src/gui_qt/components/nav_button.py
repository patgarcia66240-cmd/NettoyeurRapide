"""
NavButton - Bouton de navigation stylisé compatible Qt Designer
"""

from PySide6.QtWidgets import QPushButton, QStyleOptionButton
from PySide6.QtCore import Qt, Property, QSize
from PySide6.QtGui import QPainter, QPalette


class NavButton(QPushButton):
    """Bouton de navigation moderne avec support pour Qt Designer"""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

        # Valeurs par défaut
        self._nav_type = "primary"  # primary, secondary, accent
        self._size = "medium"       # small, medium, large
        self._icon_position = "left"  # left, right, top, bottom
        self._rounded = True

        # Appliquer le style initial
        self.update_style()

    # === Propriétés Qt Designer ===

    @Property(str)
    def navType(self):
        """Type de navigation pour Qt Designer"""
        return self._nav_type

    @navType.setter
    def navType(self, value):
        if value in ["primary", "secondary", "accent"]:
            self._nav_type = value
            self.update_style()

    @Property(str)
    def sizeType(self):
        """Taille du bouton pour Qt Designer"""
        return self._size

    @sizeType.setter
    def sizeType(self, value):
        if value in ["small", "medium", "large"]:
            self._size = value
            self.update_style()

    @Property(str)
    def iconPosition(self):
        """Position de l'icône pour Qt Designer"""
        return self._icon_position

    @iconPosition.setter
    def iconPosition(self, value):
        if value in ["left", "right", "top", "bottom"]:
            self._icon_position = value
            self.update_style()

    @Property(bool)
    def rounded(self):
        """Coins arrondis pour Qt Designer"""
        return self._rounded

    @rounded.setter
    def rounded(self, value):
        self._rounded = value
        self.update_style()

    def update_style(self):
        """Appliquer le style en fonction des propriétés"""
        style = self.get_current_style()
        self.setStyleSheet(style)
        self.update_geometry()

    def get_current_style(self):
        """Générer le CSS en fonction des propriétés actuelles"""
        # Définir les couleurs et tailles selon le type
        styles = {
            "primary": {
                "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3B7DA9, stop:1 #3BA9CD)",
                "hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5FD9C0, stop:1 #4CB9AD)",
                "pressed": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3E9A8C, stop:1 #2B897D)",
                "border": "#3B7DA9",
                "text": "#FFFFFF"
            },
            "secondary": {
                "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2D2D30, stop:1 #1E1E1E)",
                "hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3E3E42, stop:1 #2F2F32)",
                "pressed": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1D1D20, stop:1 #0E0E10)",
                "border": "#3E3E42",
                "text": "#FFFFFF"
            },
            "accent": {
                "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #007ACC, stop:1 #005A9E)",
                "hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1088DC, stop:1 #0066AE)",
                "pressed": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0066BC, stop:1 #004A8E)",
                "border": "#005A9E",
                "text": "#FFFFFF"
            }
        }

        sizes = {
            "small": {
                "width": "100px",
                "height": "28px",
                "padding": "0 4px ",
                "font": "11px"
            },
            "medium": {
                "height": "36px",
                "padding": "4px 16px",
                "font": "12px"
            },
            "large": {
                "height": "44px",
                "padding": "12px 24px",
                "font": "13px"
            }
        }

        current_style = styles[self._nav_type]
        current_size = sizes[self._size]
        border_radius = "8px" if self._rounded else "2px"

        return f"""
            QPushButton {{
                background: {current_style["bg"]};
                border: 1px solid {current_style["border"]};
                border-radius: {border_radius};
                color: {current_style["text"]};
                padding: {current_size["padding"]};
                min-height: {current_size["height"]};
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: {current_size["font"]};
                font-weight: 500;
                text-align: center;
            }}

            QPushButton:hover {{
                background: {current_style["hover"]};
                border: 1px solid {current_style["border"]};
            }}

            QPushButton:pressed {{
                background: {current_style["pressed"]};
                border: 1px solid {current_style["border"]};
            }}

            QPushButton:disabled {{
                background: #2D2D30;
                border: 1px solid #3E3E42;
                color: #666666;
            }}
        """

    def update_geometry(self):
        """Mettre à jour les dimensions selon la taille"""
        sizes = {
            "small": QSize(80, 28),
            "medium": QSize(100, 36),
            "large": QSize(120, 44)
        }

        self.setMinimumSize(sizes[self._size])
        self.setMaximumHeight(int(sizes[self._size].height()))

    # === Méthodes utilitaires ===

    def set_primary(self):
        """Définir comme bouton primaire"""
        self.navType = "primary"

    def set_secondary(self):
        """Définir comme bouton secondaire"""
        self.navType = "secondary"

    def set_accent(self):
        """Définir comme bouton accent"""
        self.navType = "accent"

    def set_size(self, size):
        """Définir la taille du bouton"""
        self.sizeType = size