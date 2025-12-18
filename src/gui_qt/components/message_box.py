"""
MessageBoxPersonnalise - Composant de boîte de dialogue personnalisé avec style moderne
"""

from PySide6.QtWidgets import (QMessageBox, QDialog, QVBoxLayout, QHBoxLayout,
                              QLabel, QPushButton, QFrame, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon


class MessageBoxPersonnalise(QDialog):
    """
    Boîte de dialogue personnalisée avec fond dégradé gris et texte blanc
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Information")
        self.setModal(True)
        self.setFixedSize(450, 150)
        self.result = None

        # Configuration frameless
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # Configuration du style
        self._setup_ui()
        self._apply_style()
        self._make_draggable()

    def _setup_ui(self):
        """Configuration de l'interface utilisateur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Conteneur principal avec fond dégradé
        self.main_container = QFrame()
        self.main_container.setObjectName("messageBoxContainer")
        container_layout = QVBoxLayout(self.main_container)
        container_layout.setContentsMargins(30, 25, 30, 20)
        container_layout.setSpacing(20)

        # Contenu principal
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(15)

        # Icône
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(48, 48)
        self.icon_label.setAlignment(Qt.AlignCenter)

        # Zone de texte
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(5)

        self.title_label = QLabel("Titre")
        self.title_label.setObjectName("messageBoxTitle")
        self.title_label.setWordWrap(True)

        self.message_label = QLabel("Message")
        self.message_label.setObjectName("messageBoxText")
        self.message_label.setWordWrap(True)
        self.message_label.setOpenExternalLinks(False)

        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.message_label)

        content_layout.addWidget(self.icon_label)
        content_layout.addLayout(text_layout)
        content_layout.addStretch()

        container_layout.addLayout(content_layout)

        # Séparateur
        separator = QFrame()
        separator.setObjectName("messageBoxSeparator")
        separator.setFixedHeight(1)
        container_layout.addWidget(separator)

        # Boutons
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 10, 0, 20)
        buttons_layout.setSpacing(10)

        self.buttons = []
        # Centrer les boutons avec des espaces égaux de chaque côté
        buttons_layout.addStretch()
        buttons_layout.addStretch()  # Ajouter un deuxième stretch pour équilibrer

        container_layout.addLayout(buttons_layout)

        layout.addWidget(self.main_container)

    def _apply_style(self):
        """Appliquer le style moderne avec fond dégradé gris"""
        self.setStyleSheet("""
            QDialog {
                background: transparent;
                border: none;
            }

            QFrame#messageBoxContainer {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3A3A3A, stop:0.3 #2D2D2D, stop:0.7 #3A3A3A, stop:1 #2D2D2D);
                border: 2px solid #555555;
                border-radius: 16px;
            }

            QLabel#messageBoxTitle {
                color: #FFFFFF;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
                font-weight: 600;
                background: transparent;
                border: none;
                padding: 0;
            }

            QLabel#messageBoxText {
                color: #E0E6ED;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                font-weight: 400;
                line-height: 1.4;
                background: transparent;
                border: none;
                padding: 0;
            }

            QFrame#messageBoxSeparator {
                background: #555555;
                border: none;
                margin: 5px 0;
            }

            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #007ACC, stop:0.5 #005A9E, stop:1 #004578);
                color: #FFFFFF;
                border: 1px solid #4096FF;
                border-radius: 8px;
                padding: 10px 24px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                font-weight: 600;
                min-width: 90px;
                min-height: 30px;
            }

            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #106EBE, stop:0.5 #007ACC, stop:1 #005A9E);
                border: 1px solid #60A5FA;
            }

            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00305A, stop:0.5 #002540, stop:1 #001A20);
                border: 1px solid #4096FF;
            }

            QPushButton:default {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #28A745, stop:0.5 #1E7E34, stop:1 #155724);
                border: 1px solid #40A463;
            }

            QPushButton:default:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #34CE57, stop:0.5 #28A745, stop:1 #1E7E34);
                border: 1px solid #60B580;
            }
        """)

    def set_icon(self, icon_type):
        """Définir l'icône selon le type"""
        icon_mapping = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'critical': '❌',
            'question': '❓'
        }

        icon_text = icon_mapping.get(icon_type, 'ℹ️')
        self.icon_label.setText(icon_text)
        self.icon_label.setStyleSheet("""
            QLabel {
                font-size: 32px;
                background: transparent;
                border: none;
                color: #FFFFFF;
            }
        """)

    def _make_draggable(self):
        """Rendre la fenêtre draggable - utiliser eventFilter au lieu de remplacer les méthodes"""
        from PySide6.QtCore import QEvent

        # Créer un filtre d'événements personnalisé
        self.drag_filter = self.createEventFilter()

        # Installer le filtre sur tous les widgets pertinents
        self.installEventFilter(self.drag_filter)

        # Installer aussi sur le conteneur principal
        if hasattr(self, 'main_container'):
            self.main_container.installEventFilter(self.drag_filter)

    def createEventFilter(self):
        """Créer un filtre d'événements pour gérer le drag"""
        from PySide6.QtCore import QObject, QEvent

        class DragFilter(QObject):
            def __init__(self, dialog):
                super().__init__()
                self.dialog = dialog

            def eventFilter(self, obj, event):
                if event.type() == QEvent.MouseButtonPress:
                    if event.button() == Qt.LeftButton:
                        # Vérifier si le clic est sur un bouton
                        clicked_widget = self.dialog.childAt(event.pos())
                        if clicked_widget and isinstance(clicked_widget, QPushButton):
                            # Ne pas intercepter, laisser le bouton gérer
                            return False

                        # Commencer le drag
                        self.dialog.drag_pos = event.pos()
                        return True

                elif event.type() == QEvent.MouseMove:
                    if event.buttons() == Qt.LeftButton and hasattr(self.dialog, 'drag_pos'):
                        # Calculer la différence
                        diff = event.pos() - self.dialog.drag_pos
                        # Appliquer le déplacement
                        new_pos = self.dialog.pos() + diff
                        self.dialog.move(new_pos)
                        return True

                elif event.type() == QEvent.MouseButtonRelease:
                    if event.button() == Qt.LeftButton and hasattr(self.dialog, 'drag_pos'):
                        delattr(self.dialog, 'drag_pos')
                        return True

                return False

        return DragFilter(self)

    def set_title(self, title):
        """Définir le titre"""
        self.title_label.setText(title)

    def set_text(self, text):
        """Définir le message"""
        self.message_label.setText(text)

    def add_button(self, text, button_type="normal", is_default=False):
        """Ajouter un bouton personnalisé"""
        button = QPushButton(text)
        button.setObjectName("messageBoxButton")

        if is_default:
            button.setDefault(True)

        # Connecter le bouton pour fermer la boîte de dialogue
        button.clicked.connect(lambda: self._on_button_clicked(text))

        # Ajouter au layout et à la liste des boutons
        container = self.main_container.layout()
        buttons_layout = container.itemAt(container.count() - 1).layout()
        # Insérer le bouton entre les deux stretches
        # Les boutons s'accumuleront au centre avec l'espacement défini
        buttons_layout.insertWidget(len(self.buttons) + 1, button)

        self.buttons.append((text, button_type))

        return button

    def _on_button_clicked(self, button_text):
        """Gérer le clic sur un bouton"""
        self.result = button_text
        self.accept()

    @staticmethod
    def show_information(parent, title, text, buttons=None):
        """Afficher une boîte de dialogue d'information"""
        msg_box = MessageBoxPersonnalise(parent)
        msg_box.setWindowTitle("Information")
        msg_box.set_icon('info')
        msg_box.set_title(title)
        msg_box.set_text(text)

        if buttons is None:
            buttons = ["OK"]

        for i, button_text in enumerate(buttons):
            is_default = (i == len(buttons) - 1)  # Le dernier bouton est par défaut
            msg_box.add_button(button_text, "info", is_default)

        msg_box.exec()
        return msg_box.result

    @staticmethod
    def show_warning(parent, title, text, buttons=None):
        """Afficher une boîte de dialogue d'avertissement"""
        msg_box = MessageBoxPersonnalise(parent)
        msg_box.setWindowTitle("Avertissement")
        msg_box.set_icon('warning')
        msg_box.set_title(title)
        msg_box.set_text(text)

        if buttons is None:
            buttons = ["OK"]

        for i, button_text in enumerate(buttons):
            is_default = (i == len(buttons) - 1)
            msg_box.add_button(button_text, "warning", is_default)

        msg_box.exec()
        return msg_box.result

    @staticmethod
    def show_critical(parent, title, text, buttons=None):
        """Afficher une boîte de dialogue d'erreur critique"""
        msg_box = MessageBoxPersonnalise(parent)
        msg_box.setWindowTitle("Erreur")
        msg_box.set_icon('critical')
        msg_box.set_title(title)
        msg_box.set_text(text)

        if buttons is None:
            buttons = ["OK"]

        for i, button_text in enumerate(buttons):
            is_default = (i == len(buttons) - 1)
            msg_box.add_button(button_text, "critical", is_default)

        msg_box.exec()
        return msg_box.result

    @staticmethod
    def show_question(parent, title, text, buttons=None):
        """Afficher une boîte de dialogue de question"""
        msg_box = MessageBoxPersonnalise(parent)
        msg_box.setWindowTitle("Confirmation")
        msg_box.set_icon('question')
        msg_box.set_title(title)
        msg_box.set_text(text)

        if buttons is None:
            buttons = ["Oui", "Non"]

        for i, button_text in enumerate(buttons):
            is_default = (button_text.lower() in ['non', 'annuler', 'cancel'])
            msg_box.add_button(button_text, "question", is_default)

        msg_box.exec()
        return msg_box.result