"""
SettingsWidget - Page de paramètres pour configurer le nettoyage
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QSlider, QSpinBox, QCheckBox, QPushButton,
                              QFrame, QGridLayout, QGroupBox, QProgressBar)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor


class SettingsWidget(QWidget):
    """Widget de paramètres avec design moderne"""

    # Signaux pour communiquer les changements
    settings_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = {
            'min_file_age_days': 30,      # Âge minimum en jours
            'max_file_size_mb': 100,      # Taille maximum en MB
            'safe_mode': True,           # Mode sécurité
            'delete_restore_points': False,  # Supprimer les points de restauration
            'clear_recycle_bin': True,   # Vider la corbeille
        }
        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Header
        self.create_header()

        # Conteneur principal
        main_frame = QFrame()
        main_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 41, 59, 0.95),
                    stop:1 rgba(51, 65, 85, 0.95));
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 16px;
                padding: 20px;
                margin: 8px;
            }
        """)

        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setSpacing(25)

        # Sections de paramètres
        self.create_safety_settings(frame_layout)
        self.create_file_criteria_settings(frame_layout)
        self.create_advanced_settings(frame_layout)

        # Bouton de sauvegarde
        self.create_save_button(frame_layout)

        layout.addWidget(main_frame)
        layout.addStretch()

    def create_header(self):
        """Créer l'en-tête"""
        header_layout = QHBoxLayout()

        title = QLabel("⚙️ Paramètres")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("""
            QLabel {
                color: #f8fafc;
                padding: 10px 0px;
                border: none;
            }
        """)

        subtitle = QLabel("Configurez les options de nettoyage")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet("""
            QLabel {
                color: #94a3b8;
                border: none;
            }
        """)

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_layout.addStretch()

        self.layout().addLayout(header_layout)

    def create_safety_settings(self, layout):
        """Créer la section sécurité"""
        group = QGroupBox("🔒 Sécurité")
        group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        group.setStyleSheet("""
            QGroupBox {
                color: #f1f5f9;
                border: 2px solid rgba(148, 163, 184, 0.3);
                border-radius: 12px;
                margin-top: 10px;
                padding-top: 10px;
                background: rgba(15, 23, 42, 0.8);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background: transparent;
            }
        """)

        safety_layout = QVBoxLayout(group)
        safety_layout.setSpacing(15)

        # Mode sécurité
        self.safe_mode_cb = QCheckBox("Mode sécurité (recommandé)")
        self.safe_mode_cb.setChecked(self.settings['safe_mode'])
        self.safe_mode_cb.setFont(QFont("Segoe UI", 10))
        self.safe_mode_cb.setStyleSheet("""
            QCheckBox {
                color: #e2e8f0;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #64748b;
                background: rgba(30, 41, 59, 0.9);
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #10b981, stop:1 #059669);
                border: 2px solid #10b981;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }
        """)

        safe_desc = QLabel("Protège les fichiers système et les répertoires critiques")
        safe_desc.setFont(QFont("Segoe UI", 9))
        safe_desc.setStyleSheet("color: #94a3b8; margin-left: 26px;")

        safety_layout.addWidget(self.safe_mode_cb)
        safety_layout.addWidget(safe_desc)

        layout.addWidget(group)

    def create_file_criteria_settings(self, layout):
        """Créer la section critères de fichiers"""
        group = QGroupBox("📁 Critères de nettoyage")
        group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        group.setStyleSheet("""
            QGroupBox {
                color: #f1f5f9;
                border: 2px solid rgba(148, 163, 184, 0.3);
                border-radius: 12px;
                margin-top: 10px;
                padding-top: 10px;
                background: rgba(15, 23, 42, 0.8);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background: transparent;
            }
        """)

        criteria_layout = QGridLayout(group)
        criteria_layout.setSpacing(20)

        # Âge minimum
        age_label = QLabel("Âge minimum des fichiers:")
        age_label.setFont(QFont("Segoe UI", 10))
        age_label.setStyleSheet("color: #e2e8f0;")

        self.age_slider = QSlider(Qt.Horizontal)
        self.age_slider.setRange(1, 365)
        self.age_slider.setValue(self.settings['min_file_age_days'])
        self.age_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #64748b;
                height: 8px;
                background: rgba(51, 65, 85, 0.9);
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3b82f6, stop:1 #2563eb);
                border: 2px solid #3b82f6;
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """)

        self.age_spinbox = QSpinBox()
        self.age_spinbox.setRange(1, 365)
        self.age_spinbox.setValue(self.settings['min_file_age_days'])
        self.age_spinbox.setSuffix(" jours")
        self.age_spinbox.setStyleSheet("""
            QSpinBox {
                background: rgba(30, 41, 59, 0.9);
                border: 1px solid #64748b;
                border-radius: 6px;
                padding: 5px 10px;
                color: #e2e8f0;
                font-size: 10px;
            }
        """)

        age_unit = QLabel("(jours)")
        age_unit.setStyleSheet("color: #94a3b8; font-size: 10px;")

        criteria_layout.addWidget(age_label, 0, 0, 1, 2)
        criteria_layout.addWidget(self.age_slider, 1, 0, 1, 1)
        criteria_layout.addWidget(self.age_spinbox, 1, 1, 1, 1)

        # Taille maximum
        size_label = QLabel("Taille maximum des fichiers:")
        size_label.setFont(QFont("Segoe UI", 10))
        size_label.setStyleSheet("color: #e2e8f0;")

        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(1, 1000)
        self.size_slider.setValue(self.settings['max_file_size_mb'])
        self.size_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #64748b;
                height: 8px;
                background: rgba(51, 65, 85, 0.9);
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8b5cf6, stop:1 #7c3aed);
                border: 2px solid #8b5cf6;
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """)

        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(1, 1000)
        self.size_spinbox.setValue(self.settings['max_file_size_mb'])
        self.size_spinbox.setSuffix(" MB")
        self.size_spinbox.setStyleSheet("""
            QSpinBox {
                background: rgba(30, 41, 59, 0.9);
                border: 1px solid #64748b;
                border-radius: 6px;
                padding: 5px 10px;
                color: #e2e8f0;
                font-size: 10px;
            }
        """)

        size_unit = QLabel("(méga-octets)")
        size_unit.setStyleSheet("color: #94a3b8; font-size: 10px;")

        criteria_layout.addWidget(size_label, 2, 0, 1, 2)
        criteria_layout.addWidget(self.size_slider, 3, 0, 1, 1)
        criteria_layout.addWidget(self.size_spinbox, 3, 1, 1, 1)

        layout.addWidget(group)

    def create_advanced_settings(self, layout):
        """Créer la section avancée"""
        group = QGroupBox("⚡ Options avancées")
        group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        group.setStyleSheet("""
            QGroupBox {
                color: #f1f5f9;
                border: 2px solid rgba(148, 163, 184, 0.3);
                border-radius: 12px;
                margin-top: 10px;
                padding-top: 10px;
                background: rgba(15, 23, 42, 0.8);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background: transparent;
            }
        """)

        advanced_layout = QVBoxLayout(group)
        advanced_layout.setSpacing(15)

        # Supprimer les points de restauration
        self.restore_points_cb = QCheckBox("Supprimer les points de restauration (⚠️ Dangereux)")
        self.restore_points_cb.setChecked(self.settings['delete_restore_points'])
        self.restore_points_cb.setFont(QFont("Segoe UI", 10))
        self.restore_points_cb.setStyleSheet("""
            QCheckBox {
                color: #e2e8f0;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #64748b;
                background: rgba(30, 41, 59, 0.9);
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ef4444, stop:1 #dc2626);
                border: 2px solid #ef4444;
            }
        """)

        restore_desc = QLabel("⚠️ Attention : Cette action peut affecter la récupération système")
        restore_desc.setFont(QFont("Segoe UI", 9))
        restore_desc.setStyleSheet("color: #fbbf24; margin-left: 26px;")

        # Vider la corbeille
        self.recycle_bin_cb = QCheckBox("Vider la corbeille")
        self.recycle_bin_cb.setChecked(self.settings['clear_recycle_bin'])
        self.recycle_bin_cb.setFont(QFont("Segoe UI", 10))
        self.recycle_bin_cb.setStyleSheet("""
            QCheckBox {
                color: #e2e8f0;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #64748b;
                background: rgba(30, 41, 59, 0.9);
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #06b6d4, stop:1 #0891b2);
                border: 2px solid #06b6d4;
            }
        """)

        advanced_layout.addWidget(self.restore_points_cb)
        advanced_layout.addWidget(restore_desc)
        advanced_layout.addWidget(self.recycle_bin_cb)

        layout.addWidget(group)

    def create_save_button(self, layout):
        """Créer le bouton de sauvegarde"""
        button_layout = QHBoxLayout()

        # Bouton par défaut
        default_btn = QPushButton("🔄 Par défaut")
        default_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        default_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6b7280, stop:0.5 #4b5563, stop:1 #374151);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7b8288, stop:0.5 #5b6573, stop:1 #475160);
            }
        """)

        # Bouton sauvegarder
        self.save_btn = QPushButton("💾 Sauvegarder")
        self.save_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #22c55e, stop:0.5 #16a34a, stop:1 #15803d);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #34d399, stop:0.5 #22c55e, stop:1 #16a34a);
            }
        """)

        button_layout.addWidget(default_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

    def setup_connections(self):
        """Configurer les connexions"""
        # Connecter les sliders et spinboxes pour l'âge
        self.age_slider.valueChanged.connect(self.age_spinbox.setValue)
        self.age_spinbox.valueChanged.connect(self.age_slider.setValue)

        # Connecter les sliders et spinboxes pour la taille
        self.size_slider.valueChanged.connect(self.size_spinbox.setValue)
        self.size_spinbox.valueChanged.connect(self.size_slider.setValue)

        # Connecter le bouton sauvegarder
        self.save_btn.clicked.connect(self.save_settings)

        # Connecter le bouton par défaut
        self.parent().findChild(QPushButton) if self.parent() else None

    def save_settings(self):
        """Sauvegarder les paramètres"""
        self.settings.update({
            'min_file_age_days': self.age_spinbox.value(),
            'max_file_size_mb': self.size_spinbox.value(),
            'safe_mode': self.safe_mode_cb.isChecked(),
            'delete_restore_points': self.restore_points_cb.isChecked(),
            'clear_recycle_bin': self.recycle_bin_cb.isChecked(),
        })

        # Émettre le signal avec les nouveaux paramètres
        self.settings_changed.emit(self.settings.copy())

        # Visual feedback
        self.save_btn.setText("✅ Sauvegardé!")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #10b981, stop:0.5 #059669, stop:1 #047857);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 10px;
            }
        """)

        # Remettre le texte original après 2 secondes
        from PySide6.QtCore import QTimer
        QTimer.singleShot(2000, self.reset_save_button)

    def reset_save_button(self):
        """Remettre le bouton sauvegarder à son état normal"""
        self.save_btn.setText("💾 Sauvegarder")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #22c55e, stop:0.5 #16a34a, stop:1 #15803d);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #34d399, stop:0.5 #22c55e, stop:1 #16a34a);
            }
        """)

    def get_settings(self):
        """Obtenir les paramètres actuels"""
        return self.settings.copy()

    def reset_to_defaults(self):
        """Remettre aux valeurs par défaut"""
        defaults = {
            'min_file_age_days': 30,
            'max_file_size_mb': 100,
            'safe_mode': True,
            'delete_restore_points': False,
            'clear_recycle_bin': True,
        }

        self.settings = defaults.copy()

        # Mettre à jour l'interface
        self.age_spinbox.setValue(defaults['min_file_age_days'])
        self.size_spinbox.setValue(defaults['max_file_size_mb'])
        self.safe_mode_cb.setChecked(defaults['safe_mode'])
        self.restore_points_cb.setChecked(defaults['delete_restore_points'])
        self.recycle_bin_cb.setChecked(defaults['clear_recycle_bin'])