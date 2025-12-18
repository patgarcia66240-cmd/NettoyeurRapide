"""
SystemInfoWidget - Composant autonome pour les informations système
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from .system_info_label import SystemInfoLabel


class SystemInfoWidget(QWidget):
    """Composant autonome qui gère les informations système avec mise à jour automatique"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_timer()
        self.update_info()  # Mise à jour initiale

    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 10, 5, 10)
        layout.setSpacing(10)

        # Titre
        self.title_label = QLabel("📊 Informations Système")
        self.title_label.setObjectName("systemTitle")
        self.title_label.setStyleSheet("""
            QLabel#systemTitle {
                color: #ecf0f1;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                background: transparent;
                border: none;
                margin-bottom: 6px;
            }
        """)
        layout.addWidget(self.title_label)

        # Conteneur pour les informations
        self.info_container = QWidget()
        self.info_container.setStyleSheet("border: none; background: transparent;")
        info_layout = QVBoxLayout(self.info_container)
        info_layout.setContentsMargins(5, 0, 0, 10)
        info_layout.setSpacing(6)

        # CPU
        self.cpu_info = SystemInfoLabel("💻", "CPU", "0.0%")
        info_layout.addWidget(self.cpu_info)

        # RAM
        self.memory_info = SystemInfoLabel("🧠", "RAM", "0.0%")
        info_layout.addWidget(self.memory_info)

        # Disque
        self.disk_info = SystemInfoLabel("💾", "Disque", "0.0%")
        info_layout.addWidget(self.disk_info)

        layout.addWidget(self.info_container)

    def setup_timer(self):
        """Configurer le timer pour les mises à jour automatiques"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_info)
        self.update_timer.start(2000)  # Mise à jour toutes les 2 secondes

    def update_info(self):
        """Mettre à jour toutes les informations système"""
        try:
            import psutil
            import platform

            # Mettre à jour CPU
            try:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                self.cpu_info.set_value(f"{cpu_percent:.1f}%")

                # Mettre en surbrillance si CPU élevé
                if cpu_percent > 80:
                    self.cpu_info.set_highlight(True)
                else:
                    self.cpu_info.set_highlight(False)
            except Exception:
                self.cpu_info.set_value("N/A")
                self.cpu_info.set_highlight(False)

            # Mettre à jour RAM
            try:
                memory = psutil.virtual_memory()
                self.memory_info.set_value(f"{memory.percent:.1f}%")

                # Mettre en surbrillance si RAM élevée
                if memory.percent > 85:
                    self.memory_info.set_highlight(True)
                else:
                    self.memory_info.set_highlight(False)
            except Exception:
                self.memory_info.set_value("N/A")
                self.memory_info.set_highlight(False)

            # Mettre à jour Disque
            try:
                disk = psutil.disk_usage('C:\\' if platform.system() == 'Windows' else '/')
                self.disk_info.set_value(f"{disk.percent:.1f}%")

                # Mettre en surbrillance si disque presque plein
                if disk.percent > 90:
                    self.disk_info.set_highlight(True)
                else:
                    self.disk_info.set_highlight(False)
            except Exception:
                self.disk_info.set_value("N/A")
                self.disk_info.set_highlight(False)

        except Exception:
            # psutil non disponible ou autre erreur
            self.show_error_state()

    def show_error_state(self):
        """Afficher un état d'erreur si les informations système ne sont pas disponibles"""
        self.cpu_info.set_value("Indisponible")
        self.cpu_info.set_highlight(False)

        self.memory_info.set_value("Indisponible")
        self.memory_info.set_highlight(False)

        self.disk_info.set_value("Indisponible")
        self.disk_info.set_highlight(False)

    def set_update_interval(self, seconds):
        """Définir l'intervalle de mise à jour en secondes"""
        self.update_timer.setInterval(seconds * 1000)

    def start_updates(self):
        """Démarrer les mises à jour automatiques"""
        self.update_timer.start()

    def stop_updates(self):
        """Arrêter les mises à jour automatiques"""
        self.update_timer.stop()

    def get_cpu_info(self):
        """Obtenir les informations CPU actuelles"""
        return {
            'percent': float(self.cpu_info.value.text().replace('%', '')) if 'N/A' not in self.cpu_info.value.text() else None,
            'highlighted': hasattr(self.cpu_info, '_highlighted')
        }

    def get_memory_info(self):
        """Obtenir les informations RAM actuelles"""
        return {
            'percent': float(self.memory_info.value.text().replace('%', '')) if 'N/A' not in self.memory_info.value.text() else None,
            'highlighted': hasattr(self.memory_info, '_highlighted')
        }

    def get_disk_info(self):
        """Obtenir les informations disque actuelles"""
        return {
            'percent': float(self.disk_info.value.text().replace('%', '')) if 'N/A' not in self.disk_info.value.text() else None,
            'highlighted': hasattr(self.disk_info, '_highlighted')
        }

    def set_critical_thresholds(self, cpu_threshold=80, memory_threshold=85, disk_threshold=90):
        """Définir les seuils critiques pour la surbrillance"""
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold

    def set_title(self, title):
        """Définir le titre du widget"""
        self.title_label.setText(title)

    def set_style_mode(self, mode="default"):
        """Définir le style du widget

        Args:
            mode (str): "default", "compact", "minimal"
        """
        if mode == "compact":
            self.title_label.hide()
            self.info_container.layout().setSpacing(2)
        elif mode == "minimal":
            self.title_label.hide()
            # Cacher les icônes pour un style minimal
            for info_widget in [self.cpu_info, self.memory_info, self.disk_info]:
                info_widget.icon_label.hide()
        else:  # default
            self.title_label.show()
            self.info_container.layout().setSpacing(6)
            for info_widget in [self.cpu_info, self.memory_info, self.disk_info]:
                info_widget.icon_label.show()

    def closeEvent(self, event):
        """Nettoyage lors de la fermeture"""
        self.stop_updates()
        super().closeEvent(event)