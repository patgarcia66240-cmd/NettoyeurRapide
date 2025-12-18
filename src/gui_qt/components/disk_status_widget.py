"""
DiskStatusWidget - Composant pour afficher l'état intelligent du disque
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QFrame, QProgressBar, QSizePolicy)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from .system_info_label import SystemInfoLabel


class DiskStatusWidget(QWidget):
    """Composant pour afficher l'état détaillé du disque avec design moderne"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.disk_path = 'C:\\'  # Par défaut pour Windows

        # Définir la politique de taille pour s'étendre verticalement
        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        self.setup_ui()
        self.setup_timer()
        self.update_disk_info()  # Mise à jour initiale

    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)  # Marges minimales
        layout.setSpacing(2)  # Espacement minimal
        layout.setAlignment(Qt.AlignTop)  # Aligner tout le contenu vers le haut

        # Conteneur principal avec style
        self.main_container = QFrame()
        self.main_container.setObjectName("diskStatusContainer")
        self.main_container.setStyleSheet("""
            QFrame#diskStatusContainer {
                background: transparent;
                border:none;
            }
        """)

        container_layout = QVBoxLayout(self.main_container)
        container_layout.setContentsMargins(6, 4, 6, 4)  # Marges optimisées
        container_layout.setSpacing(3)  # Espacement optimisé
        container_layout.setAlignment(Qt.AlignTop)  # Aligner le contenu vers le haut

        # Titre avec icône
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 10)
        title_layout.setSpacing(8)

        self.title_icon = QLabel("💾")
        self.title_icon.setStyleSheet("""
            font-size: 14px;
            color: #4EC9B0;
            background: transparent;
            border: none;
        """)

        self.title_label = QLabel("État du Disque")
        self.title_label.setStyleSheet("""
            color: #ecf0f1;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
            font-weight: 600;
            background: transparent;
            border: none;
                                       
        """)

        title_layout.addWidget(self.title_icon)
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        container_layout.addLayout(title_layout)

        # Espace total du disque
        self.total_space_label = QLabel("Total: -- GB")
        self.total_space_label.setStyleSheet("""
            color: #bdc3c7;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 11px;
            background: transparent;
            border: none;
        """)
        container_layout.addWidget(self.total_space_label)

        # Barre de progression stylisée
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("diskProgressBar")
        self.progress_bar.setFixedHeight(6)  # Réduire la hauteur
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar#diskProgressBar {
                background: rgba(52, 73, 94, 0.6);
                border: none;
                border-radius: 4px;
            }

            QProgressBar#diskProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4EC9B0,
                    stop:0.7 #3BA99D,
                    stop:1 #2E7D8A);
                border-radius: 4px;
            }
        """)
        container_layout.addWidget(self.progress_bar)

        # Informations détaillées
        self.details_layout = QVBoxLayout()
        self.details_layout.setContentsMargins(0, 10, 0, 2)  # Ajouter un peu d'espace vertical
        self.details_layout.setSpacing(3)  # Espacement réduit

        # Espace utilisé
        self.used_info = SystemInfoLabel("📁", "Occupé", "0 GB")
        self.details_layout.addWidget(self.used_info)

        # Espace libre
        self.free_info = SystemInfoLabel("✅", "Libre", "0 GB")
        self.details_layout.addWidget(self.free_info)

        # Pourcentage
        self.percentage_info = SystemInfoLabel("📊", "Utilisation", "0%")
        self.details_layout.addWidget(self.percentage_info)

        container_layout.addLayout(self.details_layout)

        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("""
            background-color: rgba(62, 62, 66, 0.5);
            max-height: 1px;
            border: none;
        """)
        container_layout.addWidget(separator)

        # État intelligent
        self.status_info = SystemInfoLabel("ℹ️", "État", "Analyse...")
        self.status_info.set_highlight(False)
        container_layout.addWidget(self.status_info)

        # S'assurer que le conteneur principal prend toute la place disponible
        self.main_container.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        # Aligner le conteneur vers le haut sans stretches
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(self.main_container)

    def setup_timer(self):
        """Configurer le timer pour les mises à jour automatiques"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_disk_info)
        self.update_timer.start(5000)  # Mise à jour toutes les 5 secondes

    def update_disk_info(self):
        """Mettre à jour les informations du disque"""
        try:
            import psutil

            # Obtenir les informations du disque
            disk_usage = psutil.disk_usage(self.disk_path)
            total_gb = disk_usage.total / (1024**3)  # Convertir en GB
            used_gb = disk_usage.used / (1024**3)
            free_gb = disk_usage.free / (1024**3)
            percent_used = (used_gb / total_gb) * 100

            # Mettre à jour les labels
            self.total_space_label.setText(f"Total: {total_gb:.1f} GB")
            self.progress_bar.setValue(int(percent_used))

            self.used_info.set_value(f"{used_gb:.1f} GB")
            self.free_info.set_value(f"{free_gb:.1f} GB")
            self.percentage_info.set_value(f"{percent_used:.1f}%")

            # Mettre à jour l'état intelligent
            self.update_smart_status(percent_used, free_gb)

        except Exception as e:
            self.show_error_state(f"Erreur: {str(e)}")

    def update_smart_status(self, percent_used, free_gb):
        """Mettre à jour l'état intelligent du disque"""
        status_text = ""
        status_color = None
        highlight = False

        if percent_used >= 95:
            status_text = "Critique - Plein"
            status_color = "#e74c3c"
            highlight = True
        elif percent_used >= 90:
            status_text = "Urgent - Presque plein"
            status_color = "#f39c12"
            highlight = True
        elif percent_used >= 75:
            status_text = "Attention - Espace faible"
            status_color = "#f39c12"
            highlight = False
        elif percent_used >= 50:
            status_text = "Normal - Espace suffisant"
            status_color = "#2ecc71"
            highlight = False
        else:
            status_text = "Excellent - Beaucoup d'espace"
            status_color = "#27ae60"
            highlight = False

        # Ajouter l'espace libre à l'état
        status_text += f" ({free_gb:.1f} GB libre)"

        # Mettre à jour le statut
        self.status_info.set_label("État")
        self.status_info.set_value(status_text)
        self.status_info.set_highlight(highlight)

        # Mettre à jour l'icône selon l'état
        if percent_used >= 90:
            self.status_info.set_icon("⚠️")
        elif percent_used >= 75:
            self.status_info.set_icon("⚡")
        else:
            self.status_info.set_icon("✅")

        # Changer la couleur de la barre de progression selon l'état
        self.update_progress_bar_color(status_color)

    def update_progress_bar_color(self, color):
        """Mettre à jour la couleur de la barre de progression"""
        self.progress_bar.setStyleSheet(f"""
            QProgressBar#diskProgressBar {{
                background: rgba(52, 73, 94, 0.6);
                border: none;
                border-radius: 4px;
            }}

            QProgressBar#diskProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color},
                    stop:0.7 {color});
                border-radius: 4px;
            }}
        """)

    def show_error_state(self, error_message="Indisponible"):
        """Afficher un état d'erreur"""
        self.total_space_label.setText("Total: -- GB")
        self.progress_bar.setValue(0)
        self.used_info.set_value("-- GB")
        self.free_info.set_value("-- GB")
        self.percentage_info.set_value("-- %")
        self.status_info.set_label("Erreur")
        self.status_info.set_value(error_message)
        self.status_info.set_icon("❌")
        self.status_info.set_highlight(False)

    def set_disk_path(self, path):
        """Définir le chemin du disque à surveiller"""
        self.disk_path = path
        self.update_disk_info()  # Mise à jour immédiate

    def get_disk_info(self):
        """Obtenir les informations actuelles du disque"""
        try:
            import psutil
            disk_usage = psutil.disk_usage(self.disk_path)
            total_gb = disk_usage.total / (1024**3)
            used_gb = disk_usage.used / (1024**3)
            free_gb = disk_usage.free / (1024**3)
            percent_used = (used_gb / total_gb) * 100

            return {
                'total_gb': total_gb,
                'used_gb': used_gb,
                'free_gb': free_gb,
                'percent_used': percent_used,
                'status': self.get_status_from_percent(percent_used)
            }
        except Exception:
            return None

    def get_status_from_percent(self, percent):
        """Obtenir le statut à partir du pourcentage"""
        if percent >= 95:
            return "critical"
        elif percent >= 90:
            return "urgent"
        elif percent >= 75:
            return "warning"
        elif percent >= 50:
            return "normal"
        else:
            return "excellent"

    def set_update_interval(self, seconds):
        """Définir l'intervalle de mise à jour en secondes"""
        self.update_timer.setInterval(seconds * 1000)

    def start_updates(self):
        """Démarrer les mises à jour automatiques"""
        self.update_timer.start()

    def stop_updates(self):
        """Arrêter les mises à jour automatiques"""
        self.update_timer.stop()

    def closeEvent(self, event):
        """Nettoyage lors de la fermeture"""
        self.stop_updates()
        super().closeEvent(event)