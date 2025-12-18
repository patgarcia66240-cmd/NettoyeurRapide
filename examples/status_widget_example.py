"""
Exemple d'utilisation du StatusWidget
"""

import sys
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

from src.gui_qt.components.status_widget import StatusWidget


class StatusWidgetExample(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.status_widget = None

    def setup_ui(self):
        """Configuration de l'interface exemple"""
        self.setWindowTitle("StatusWidget Example")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        # Boutons de test
        btn_success = QPushButton("Show Success Status")
        btn_success.clicked.connect(self.show_success)
        btn_success.setMinimumHeight(40)

        btn_warning = QPushButton("Show Warning Status")
        btn_warning.clicked.connect(self.show_warning)
        btn_warning.setMinimumHeight(40)

        btn_error = QPushButton("Show Error Status")
        btn_error.clicked.connect(self.show_error)
        btn_error.setMinimumHeight(40)

        btn_info = QPushButton("Show Info Status")
        btn_info.clicked.connect(self.show_info)
        btn_info.setMinimumHeight(40)

        btn_multiple = QPushButton("Show Multiple Messages")
        btn_multiple.clicked.connect(self.show_multiple)
        btn_multiple.setMinimumHeight(40)

        layout.addWidget(btn_success)
        layout.addWidget(btn_warning)
        layout.addWidget(btn_error)
        layout.addWidget(btn_info)
        layout.addWidget(btn_multiple)

        self.setLayout(layout)

    def show_success(self):
        """Afficher un statut de succès"""
        if self.status_widget:
            self.status_widget.close()

        self.status_widget = StatusWidget()
        self.status_widget.set_status("Operation completed successfully!", "success", auto_close=3000)
        self.status_widget.show_at_position(corner="bottom-right", margin=20)
        self.status_widget.animate_fade_in()

    def show_warning(self):
        """Afficher un statut d'avertissement"""
        if self.status_widget:
            self.status_widget.close()

        self.status_widget = StatusWidget()
        self.status_widget.set_status("Please save your changes", "warning", auto_close=4000)
        self.status_widget.show_at_position(corner="bottom-right", margin=20)
        self.status_widget.animate_fade_in()

    def show_error(self):
        """Afficher un statut d'erreur"""
        if self.status_widget:
            self.status_widget.close()

        self.status_widget = StatusWidget()
        self.status_widget.set_status("Failed to connect to server", "error")
        self.status_widget.show_at_position(corner="bottom-right", margin=20)
        self.status_widget.animate_fade_in()

    def show_info(self):
        """Afficher un statut d'information"""
        if self.status_widget:
            self.status_widget.close()

        self.status_widget = StatusWidget()
        self.status_widget.set_status("New update available", "info", auto_close=3000)
        self.status_widget.show_at_position(corner="bottom-right", margin=20)
        self.status_widget.animate_fade_in()

    def show_multiple(self):
        """Afficher plusieurs messages en rotation"""
        if self.status_widget:
            self.status_widget.close()

        self.status_widget = StatusWidget()
        self.status_widget.add_message("Downloading files...", "info")
        self.status_widget.add_message("Processing data...", "info")
        self.status_widget.add_message("Almost done...", "warning")
        self.status_widget.add_message("Complete!", "success")

        self.status_widget.set_status("Downloading files...", "info")
        self.status_widget.show_at_position(corner="bottom-right", margin=20)
        self.status_widget.animate_fade_in()
        self.status_widget.start_rotation(interval=2000)

        # Connecter le signal de fermeture
        self.status_widget.close_requested.connect(self.status_widget.close)


def main():
    app = QApplication(sys.argv)

    # Appliquer un style moderne
    app.setStyle("Fusion")

    example = StatusWidgetExample()
    example.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()