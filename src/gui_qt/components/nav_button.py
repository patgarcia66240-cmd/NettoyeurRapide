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
        if value in ["small", "medium", "large", "carre_md", "carre_xl"]:
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
        self.setStyleSheet(style )
        self.update_geometry()

    def get_current_style(self):
        """Générer le CSS en fonction des propriétés actuelles"""
        # Définir les couleurs et tailles selon le type
        styles = {
            "primary": {
                "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3B7DA9, stop:1 #3BA9CD)",
                "hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #22669d, stop:1 #3d9288)",
                "pressed": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #29538e, stop:1 #2B897D)",
                "border": "#92B5CB",
                "text": "#FFFFFF"
            },
            "secondary": {
                "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #46464a, stop:1 #5f5f5f)",
                "hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3E3E42, stop:1 #2F2F32)",
                "pressed": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2c2c2e, stop:1 #3e3e41)",
                "border": "#B8B8B9",
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
                "height": "30px",
                "padding": "0 4px",
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
            }, 
            "carre_md": {
                "height": "36px",
                "width": "36px",
                "font": "12px",
                "padding": "0px"
            },
            "carre_xl": {
                "height": "44px",
                "width": "44px",
                "font": "12px",
                "padding": "0px"
            },
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
                background: #69696d;
                border: 1px solid #bcbcbc;
                color: #eae8e8;
            }}

            /* Style pour les tooltips */
            QToolTip {{
                background: #12447e;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                font-weight: normal;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
            }}
        """

    def update_geometry(self):
        """Mettre à jour les dimensions selon la taille"""
        sizes = {
            "small": QSize(120, 32),
            "medium": QSize(100, 36),
            "large": QSize(120, 44),
            "carre_md": QSize(36, 36),
            "carre_xl": QSize(44, 44),
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

    # === Méthodes pour les tooltips ===

    def set_tooltip(self, text):
        """Définir le tooltip du bouton"""
        self.setToolTip(text)
        return self  # Pour le chaînage

    def set_tooltip_with_shortcut(self, text, shortcut):
        """Définir un tooltip avec raccourci clavier"""
        tooltip_text = f"{text} ({shortcut})"
        self.setToolTip(tooltip_text)
        return self

    def set_rich_tooltip(self, title, description, shortcut=None):
        """Définir un tooltip riche avec titre, description et optionnellement un raccourci"""
        if shortcut:
            tooltip_html = f"""
            <b style="color: #ffffff;">{title}</b><br>
            <span style="color: #e0e0e0;">{description}</span><br>
            <small style="color: #a0a0a0;"><i>Raccourci: {shortcut}</i></small>
            """
        else:
            tooltip_html = f"""
            <b style="color: #ffffff;">{title}</b><br>
            <span style="color: #e0e0e0;">{description}</span>
            """
        self.setToolTip(tooltip_html)
        return self

    def set_action_tooltip(self, action_name, description=None):
        """Définir un tooltip pour une action (avec raccourcis suggérés)"""
        # Raccourcis courants selon le type d'action
        shortcuts = {
            "nouveau": "Ctrl+N",
            "ouvrir": "Ctrl+O",
            "sauvegarder": "Ctrl+S",
            "quitter": "Ctrl+Q",
            "analyser": "F5",
            "nettoyer": "Ctrl+D",
            "paramètres": "Ctrl+P",
            "aide": "F1",
            "actualiser": "F5",
            "supprimer": "Del",
            "copier": "Ctrl+C",
            "coller": "Ctrl+V",
            "annuler": "Ctrl+Z",
        }

        action_lower = action_name.lower()
        shortcut = shortcuts.get(action_lower, "")

        if description:
            return self.set_tooltip_with_shortcut(f"{action_name}: {description}", shortcut)
        else:
            return self.set_tooltip_with_shortcut(action_name, shortcut)

    def clear_tooltip(self):
        """Supprimer le tooltip du bouton"""
        self.setToolTip("")
        return self

    def has_tooltip(self):
        """Vérifier si le bouton a un tooltip"""
        return bool(self.toolTip())