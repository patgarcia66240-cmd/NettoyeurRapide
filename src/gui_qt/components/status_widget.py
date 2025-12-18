"""
StatusWidget - Composant de barre de statut intégré pour l'application
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class StatusIconWithLabel(QWidget):
    """Composant réutilisable pour afficher une icône de statut avec un label"""

    def __init__(self, icon_text="✓", label_text="", parent=None):
        super().__init__(parent)

        # Layout horizontal
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Icône de statut
        self.status_icon = QLabel(icon_text)
        self.status_icon.setObjectName("statusIcon")
        self.status_icon.setFixedSize(16, 16)
        self.status_icon.setAlignment(Qt.AlignCenter)

        # Message de statut
        self.status_label = QLabel(label_text)
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Ajouter les widgets au layout
        layout.addWidget(self.status_icon)
        layout.addWidget(self.status_label)

    def set_icon(self, icon_text):
        """Définir le texte de l'icône"""
        self.status_icon.setText(icon_text)

    def set_label(self, label_text):
        """Définir le texte du label"""
        self.status_label.setText(label_text)

    def set_status(self, icon_text, label_text):
        """Définir à la fois l'icône et le label"""
        self.set_icon(icon_text)
        self.set_label(label_text)


class StatusWidget(QWidget):
    """Composant de statut intégré avec design moderne"""

    def __init__(self, parent_layout=None, parent=None):
        """
        Initialiser le StatusWidget

        Args:
            parent_layout: Le layout parent dans lequel ajouter le widget
            parent: Le widget parent (optionnel si parent_layout est fourni)
        """
        super().__init__(parent)
        self.parent_layout = parent_layout
        self.setup_ui()
        self.setup_style()

        # Si un layout parent est fourni, s'ajouter à ce layout
        if self.parent_layout:
            self.parent_layout.addWidget(self)

    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        # Pas de layout interne - le widget sera géré par le layout parent
        # Créer directement le conteneur de statut comme widget principal
        self.status_container = QFrame()
        self.status_container.setObjectName("statusContainer")
        self.status_container.setFixedHeight(36)

        # Layout du conteneur
        container_layout = QHBoxLayout(self.status_container)
        container_layout.setContentsMargins(12, 6, 12, 6)
        container_layout.setSpacing(0)
        container_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Utiliser le composant réutilisable StatusIconWithLabel
        self.status_content = StatusIconWithLabel("✓", "Prêt")

        # Ajouter le composant au conteneur
        container_layout.addWidget(self.status_content)

        # Garder les références pour compatibilité
        self.status_icon = self.status_content.status_icon
        self.status_label = self.status_content.status_label

        # Configurer ce widget pour utiliser le conteneur comme widget principal
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.status_container)

        # Définir la taille fixe (plus petit)
        self.setFixedHeight(52)

    def setup_style(self):
        """Appliquer le style moderne par défaut (success)"""
        self._apply_status_style("#2ecc71", "#27ae60")

    def _apply_status_style(self, primary_color, secondary_color):
        """Appliquer le style pour un type de statut spécifique"""
        self.setStyleSheet(f"""
            QFrame#statusContainer {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {primary_color},
                    stop:0.3 {secondary_color},
                    stop:0.7 {primary_color},
                    stop:1 {secondary_color});
                border: none;
                border-radius: 16px;
            }}

            QLabel#statusIcon {{
                background: rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                color: #FFFFFF;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 9px;
                font-weight: bold;
            }}

            QLabel#statusLabel {{
                color: #FFFFFF;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10px;
                font-weight: 500;
                background: transparent;
                border: none;
            }}
        """)

    def set_status(self, message, status_type="success"):
        """Définir le statut avec un message et un type

        Args:
            message (str): Message à afficher
            status_type (str): Type de statut ("success", "warning", "error", "info")
        """
        self.status_label.setText(message)

        # Mettre à jour l'icône et le style selon le type
        if status_type == "success":
            self.status_icon.setText("✓")
            self._apply_status_style("#2ecc71", "#27ae60")
        elif status_type == "warning":
            self.status_icon.setText("⚠")
            self._apply_status_style("#f39c12", "#e67e22")
        elif status_type == "error":
            self.status_icon.setText("✕")
            self._apply_status_style("#e74c3c", "#c0392b")
        elif status_type == "info":
            self.status_icon.setText("ℹ")
            self._apply_status_style("#3498db", "#2980b9")