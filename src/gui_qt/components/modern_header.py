#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Composant Header moderne réutilisable
- Header avec dégradé bleu
- Icône et titre personnalisables
- Boutons optionnels à droite
- Style cohérent sur tous les widgets
"""

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QWidget
from PySide6.QtCore import Qt


class ModernHeader(QFrame):
    """
    Header moderne réutilisable avec dégradé bleu et boutons optionnels
    """

    def __init__(self, icon: str, title: str, parent=None):
        super().__init__(parent)
        self.icon_text = icon
        self.title_text = title
        self.right_buttons = []
        self.setup_ui()

    def setup_ui(self):
        """Configurer l'en-tête moderne"""
        self.setObjectName("modernHeader")
        self.setFixedHeight(50)
        self.setStyleSheet("""
            QFrame#modernHeader {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(41, 128, 185, 0.95),
                    stop:0.5 rgba(52, 152, 219, 0.95),
                    stop:1 rgba(41, 128, 185, 0.95));
                border: none;
                border-bottom: 2px solid rgba(52, 73, 94, 0.3);
            }
        """)

        header_layout = QHBoxLayout(self)
        header_layout.setContentsMargins(10, 0, 20, 0)  # Moins d'espace à gauche
        header_layout.setSpacing(15)

        # Icône et titre
        self.header_icon = QLabel(self.icon_text)
        self.header_icon.setStyleSheet("""
            font-size: 24px;
            color: #FFFFFF;
            background: transparent;
        """)

        self.header_title = QLabel(self.title_text)
        self.header_title.setStyleSheet("""
            color: #FFFFFF;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 18px;
            font-weight: 600;
            background: transparent;
        """)

        # Ajouter l'icône et le titre à gauche
        header_layout.addWidget(self.header_icon)
        header_layout.addWidget(self.header_title)

        # Espace flexible pour pousser les boutons à droite
        header_layout.addStretch()

        # Conteneur pour les boutons à droite
        self.right_buttons_container = QWidget()
        self.right_buttons_container.setStyleSheet("background: transparent;")
        self.right_buttons_layout = QHBoxLayout(self.right_buttons_container)
        self.right_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.right_buttons_layout.setSpacing(8)

        header_layout.addWidget(self.right_buttons_container)

    def set_icon(self, icon: str):
        """Changer l'icône du header"""
        self.icon_text = icon
        self.header_icon.setText(icon)

    def set_title(self, title: str):
        """Changer le titre du header"""
        self.title_text = title
        self.header_title.setText(title)

    def add_button(self, text: str, tooltip: str = None, style: str = "default") -> QPushButton:
        """
        Ajouter un bouton à droite du header

        Args:
            text: Texte du bouton
            tooltip: Texte au survol (optionnel)
            style: Style du bouton ("default", "primary", "success", "warning", "danger")

        Returns:
            QPushButton: Le bouton créé
        """
        button = QPushButton(text)

        if tooltip:
            button.setToolTip(tooltip)

        # Appliquer le style selon le type
        if style == "primary":
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(52, 152, 219, 0.8);
                    color: white;
                    border: 1px solid rgba(41, 128, 185, 0.9);
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: 500;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: rgba(41, 128, 185, 0.9);
                }
                QPushButton:pressed {
                    background-color: rgba(52, 73, 94, 0.8);
                }
            """)
        elif style == "success":
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(46, 204, 113, 0.8);
                    color: white;
                    border: 1px solid rgba(39, 174, 96, 0.9);
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: 500;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: rgba(39, 174, 96, 0.9);
                }
                QPushButton:pressed {
                    background-color: rgba(34, 153, 84, 0.8);
                }
            """)
        elif style == "warning":
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(241, 196, 15, 0.8);
                    color: white;
                    border: 1px solid rgba(243, 156, 18, 0.9);
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: 500;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: rgba(243, 156, 18, 0.9);
                }
                QPushButton:pressed {
                    background-color: rgba(211, 84, 0, 0.8);
                }
            """)
        elif style == "danger":
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(231, 76, 60, 0.8);
                    color: white;
                    border: 1px solid rgba(192, 57, 43, 0.9);
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: 500;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: rgba(192, 57, 43, 0.9);
                }
                QPushButton:pressed {
                    background-color: rgba(155, 89, 182, 0.8);
                }
            """)
        else:  # default
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.2);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: 500;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.3);
                    border: 1px solid rgba(255, 255, 255, 0.5);
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 0.1);
                }
            """)

        self.right_buttons_layout.addWidget(button)
        self.right_buttons.append(button)

        return button

    def clear_buttons(self):
        """Supprimer tous les boutons à droite"""
        for button in self.right_buttons:
            self.right_buttons_layout.removeWidget(button)
            button.deleteLater()
        self.right_buttons.clear()

    def remove_button(self, button: QPushButton):
        """Supprimer un bouton spécifique"""
        if button in self.right_buttons:
            self.right_buttons_layout.removeWidget(button)
            self.right_buttons.remove(button)
            button.deleteLater()