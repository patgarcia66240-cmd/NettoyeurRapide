"""
SystemInfoLabel - Composant pour afficher les informations système avec design moderne
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class SystemInfoLabel(QWidget):
    """Composant réutilisable pour afficher une information système avec icône et valeur"""

    def __init__(self, icon_text="", label_text="", value_text="", parent=None):
        super().__init__(parent)

        # Layout horizontal
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Icône
        self.icon_label = QLabel(icon_text)
        self.icon_label.setObjectName("systemIcon")
        self.icon_label.setFixedSize(16, 16)
        self.icon_label.setAlignment(Qt.AlignCenter)

        # Label (libellé)
        self.label = QLabel(label_text)
        self.label.setObjectName("systemLabel")
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Valeur
        self.value = QLabel(value_text)
        self.value.setObjectName("systemValue")
        self.value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Ajouter les widgets au layout
        layout.addWidget(self.icon_label)
        layout.addWidget(self.label)
        layout.addWidget(self.value)
        layout.addStretch()  # Pousser le contenu vers la gauche

        # Appliquer le style
        self.apply_style()

    def apply_style(self):
        """Appliquer le style moderne"""
        self.setStyleSheet("""
            QLabel#systemIcon {
                color: #4EC9B0;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                font-weight: bold;
                background: transparent;
                border: none;
            }

            QLabel#systemLabel {
                color: #CCCCCC;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11px;
                font-weight: 500;
                background: transparent;
                border: none;
            }

            QLabel#systemValue {
                color: #FFFFFF;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                font-weight: 600;
                background: transparent;
                border: none;
                padding-left: 5px;
            }
        """)

    def set_icon(self, icon_text):
        """Définir l'icône"""
        self.icon_label.setText(icon_text)

    def set_label(self, label_text):
        """Définir le libellé"""
        self.label.setText(label_text)

    def set_value(self, value_text):
        """Définir la valeur"""
        self.value.setText(value_text)

    def update_info(self, icon_text=None, label_text=None, value_text=None):
        """Mettre à jour plusieurs informations à la fois"""
        if icon_text is not None:
            self.set_icon(icon_text)
        if label_text is not None:
            self.set_label(label_text)
        if value_text is not None:
            self.set_value(value_text)

    def set_highlight(self, highlight=True):
        """Mettre en surbrillance ou non"""
        if highlight:
            self.setStyleSheet("""
                QLabel#systemIcon {
                    color: #4EC9B0;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 14px;
                    font-weight: bold;
                    background: transparent;
                    border: none;
                }

                QLabel#systemLabel {
                    color: #4EC9B0;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 12px;
                    font-weight: 600;
                    background: transparent;
                    border: none;
                }

                QLabel#systemValue {
                    color: #FFFFFF;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 14px;
                    font-weight: 700;
                    background: transparent;
                    border: none;
                    padding-left: 5px;
                }
            """)
        else:
            self.apply_style()