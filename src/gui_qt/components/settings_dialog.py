"""
SettingsDialog - Boîte de dialogue pour les paramètres de nettoyage
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QSlider, QSpinBox, QCheckBox,
                              QFrame, QGridLayout, QGroupBox, QScrollArea,
                              QWidget, QSizePolicy, QSpacerItem, QPushButton)
from PySide6.QtCore import Qt, Signal, QSettings
from PySide6.QtGui import QFont, QIcon

try:
    from .nav_button import NavButton
except ImportError:
    # Pour l'exécution directe du fichier
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from gui_qt.components.nav_button import NavButton


class SettingsDialog(QDialog):
    """Boîte de dialogue de paramètres moderne et lisible"""

    settings_changed = Signal(dict)

    def __init__(self, settings=None, parent=None):
        super().__init__(parent)

        # QSettings pour sauvegarder les paramètres
        self.qsettings = QSettings("NettoyeurRapide", "CleaningSettings")

        # Paramètres par défaut
        self.settings = settings or {
            'min_file_age_days': 30,
            'max_file_size_kb': 100000,  # 100 MB en KB
            'safe_mode': True,
            'delete_restore_points': False,
            'clear_recycle_bin': True,
        }

        self.init_ui()
        self.load_settings_from_qsettings()
        self.setup_connections()

    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setFixedSize(620, 540)  # Taille augmentée pour l'header
        self.setModal(True)

        # Style principal MessageBox inspiré
        self.setStyleSheet("""
            QDialog {
                background: #363636;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: 1px solid #333333;
                border-radius: 12px;
            }
            QGroupBox {
                font-size: 14px;
                font-weight: 500;
                color: #ffffff;
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 20px;
                background: #4f4e4e;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                background: transparent;
                color: #ffffff;
                font-weight: 600;
            }
            QLabel {
                color: #cccccc;
                font-size: 13px;
                padding: 2px 0;
                background: transparent;
            }
            QLabel.section-title {
                color: #ffffff;
                font-size: 14px;
                font-weight: 600;
                padding: 8px 0;
            }
            QLabel.setting-label {
                color: #cccccc;
                font-size: 13px;
                font-weight: 500;
            }
            QLabel.setting-desc {
                color: #999999;
                font-size: 12px;
                margin-top: 2px;
            }
            /* Slider moderne */
            QSlider::groove:horizontal {
                height: 6px;
                border-radius: 3px;
                background: #404040;
                border: none;
            }
            QSlider::handle:horizontal {
                background: #0078d4;
                border: 2px solid #005a6e;
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            QSlider::handle:hover {
                background: #0096d6;
                border: 2px solid #0078d4;
            }
            QSpinBox {
                background: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px 12px;
                color: #ffffff;
                font-size: 13px;
                font-weight: normal;
                min-width: 80px;
                selection-background-color: #0078d4;
            }
            QSpinBox:focus {
                border: 1px solid #0078d4;
                outline: none;
            }
           
            QCheckBox {
                color: #ffffff;
                font-size: 13px;
                font-weight: normal;
                spacing: 8px;
                padding: 4px 0;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 1px solid #404040;
                background: #2a2a2a;
            }
            QCheckBox::indicator:hover {
                border: 1px solid #0078d4;
            }
            QCheckBox::indicator:checked {
                background: #0078d4;
                border: 1px solid #0078d4;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }
            QPushButton {
                background: #333333;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: normal;
                color: #ffffff;
                min-width: 80px;
            }
            QPushButton:hover {
                background: #404040;
                border: 1px solid #666666;
                color: #ffffff;
            }
            QPushButton:pressed {
                background: #2a2a2a;
                border: 1px solid #444444;
            }
            QPushButton.primary {
                background: #0078d4;
                border: 1px solid #0078d4;
                color: white;
            }
            QPushButton.primary:hover {
                background: #106ebe;
                border: 1px solid #106ebe;
            }
            QPushButton.secondary {
                background: #666666;
                border: 1px solid #666666;
                color: white;
            }
            QPushButton.secondary:hover {
                background: #777777;
                border: 1px solid #777777;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header personnalisé avec boutons de contrôle
        title_bar = self.create_title_bar()
        layout.addWidget(title_bar)

        # Conteneur principal avec marges
        main_container = QWidget()
        main_container.setStyleSheet("""
            QWidget {
                background: #1f1f1f;
                border: none;
                border-radius: 0px 0px 12px 12px;
            }
        """)
        main_layout = QVBoxLayout(main_container)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # Header titre
        header = self.create_header()
        main_layout.addWidget(header)

        # Zone de contenu scrollable avec taille minimum fixée
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.NoFrame)
        scroll_area.setMinimumHeight(300)  # Hauteur minimum pour le contenu
        scroll_area.setMaximumHeight(350)  # Hauteur maximum pour garantir la visibilité des boutons
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 8px;
            }
            QScrollArea > QWidget > QWidget {
                background: #1a1a1a;
            }
            /* Scrollbar verticale moderne */
            QScrollBar:vertical {
                background: #2a2a2a;
                width: 12px;
                border: none;
                border-radius: 6px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #404040;
                border: none;
                border-radius: 3px;
                min-height: 20px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: #505050;
            }
            QScrollBar::handle:vertical:pressed {
                background: #0078d4;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
                border: none;
                background: none;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
            /* Scrollbar horizontale (au cas où) */
            QScrollBar:horizontal {
                background: #2a2a2a;
                height: 12px;
                border: none;
                border-radius: 6px;
                margin: 0;
            }
            QScrollBar::handle:horizontal {
                background: #404040;
                border: none;
                border-radius: 2px;
                min-width: 20px;
                margin: 2px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #505050;
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0px;
                border: none;
                background: none;
            }
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(10)
        content_layout.setContentsMargins(6, 6, 6, 6)

        # Sections
        self.create_safety_section(content_layout)
        self.create_file_criteria_section(content_layout)
        self.create_advanced_section(content_layout)

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # Boutons avec marge supérieure pour l'espacement
        buttons = self.create_buttons()
        main_layout.addWidget(buttons)

        # Ajouter le conteneur principal au layout de la dialog
        layout.addWidget(main_container)

        # Rendre la fenêtre draggable depuis le header
        self.title_bar.mousePressEvent = self._title_bar_mouse_press
        self.title_bar.mouseMoveEvent = self._title_bar_mouse_move

    def create_title_bar(self):
        """Créer la barre de titre personnalisée avec boutons de contrôle"""
        title_bar = QFrame()
        title_bar.setFixedHeight(44)
        title_bar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a,
                    stop:1 #1f1f1f);
                border: 1px solid #333333;
                border-bottom: 1px solid #404040;
                border-radius: 12px 12px 0 0;
                margin: 0px;
                padding: 0px;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: 600;
                background: transparent;
                border: none;
                padding: 0px;
            }
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 6px;
                padding: 8px;
                margin: 4px;
                font-size: 16px;
                font-weight: bold;
                color: #cccccc;
                min-width: 16px;
                min-height: 16px;
                max-width: 16px;
                max-height: 16px;
            }
            QPushButton:hover {
                background: #404040;
                color: #ffffff;
            }
            QPushButton#close_btn:hover {
                background: #e74c3c;
                color: #ffffff;
            }
            QPushButton:pressed {
                background: #333333;
            }
        """)

        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(12, 0, 8, 4)
        layout.setSpacing(8)

        # Icône et titre
        icon_label = QLabel("⚙️")
        icon_label.setStyleSheet("font-size: 16px;")

        title_label = QLabel("Paramètres de Nettoyage")
        title_label.setStyleSheet("font-size: 14px; font-weight: 600;")

        # Espaceur
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Boutons de contrôle
        minimize_btn = QPushButton("−")
        minimize_btn.setObjectName("minimize_btn")
        minimize_btn.setToolTip("Réduire")
        minimize_btn.setFixedHeight(24)
        minimize_btn.setFixedWidth(24)
        minimize_btn.clicked.connect(self.showMinimized)

        close_btn = QPushButton("✕")
        close_btn.setObjectName("close_btn")
        close_btn.clicked.connect(self.reject)
        close_btn.setFixedHeight(24)
        close_btn.setFixedWidth(24)

        # Assembler le layout
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(spacer)
        layout.addWidget(minimize_btn)
        layout.addWidget(close_btn)

        # Stocker les références
        self.title_bar = title_bar
        self.minimize_btn = minimize_btn
        self.close_btn = close_btn

        return title_bar

    def _title_bar_mouse_press(self, event):
        """Gérer le clic sur la barre de titre pour déplacer la fenêtre"""
        if event.button() == Qt.LeftButton:
            self.title_bar_offset = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def _title_bar_mouse_move(self, event):
        """Gérer le mouvement de la souris pour déplacer la fenêtre"""
        if event.buttons() == Qt.LeftButton and hasattr(self, 'title_bar_offset'):
            self.move(event.globalPosition().toPoint() - self.title_bar_offset)
            event.accept()

    def create_header(self):
        """Créer l'en-tête"""
        header = QFrame()
        header.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Paramètres de Nettoyage")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("""
            QLabel {
                color: #f8fafc;
                background: transparent;
                padding: 0;
            }
        """)

        desc = QLabel("Configurez les options de nettoyage pour optimiser votre système")
        desc.setFont(QFont("Segoe UI", 11))
        desc.setStyleSheet("""
            QLabel {
                color: #94a3b8;
                background: transparent;
                padding: 0;
            }
        """)

        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addStretch()

        return header

    def create_safety_section(self, layout):
        """Créer la section sécurité"""
        group = QGroupBox("🔒 Sécurité")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(10)

        # Mode sécurité
        safety_widget = QWidget()
        safety_layout = QHBoxLayout(safety_widget)
        safety_layout.setContentsMargins(0, 0, 0, 0)

        left_layout = QVBoxLayout()
        left_layout.setSpacing(4)

        self.safe_mode_cb = QCheckBox("Activer le mode sécurité (recommandé)")
        self.safe_mode_cb.setFont(QFont("Segoe UI", 12, QFont.Medium))

        safe_desc = QLabel("Protège les fichiers système critiques et les répertoires importants")
        safe_desc.setStyleSheet("color: #64748b; font-size: 12px;")

        left_layout.addWidget(self.safe_mode_cb)
        left_layout.addWidget(safe_desc)

        safety_layout.addLayout(left_layout)
        safety_layout.addStretch()

        group_layout.addWidget(safety_widget)
        layout.addWidget(group)

    def create_file_criteria_section(self, layout):
        """Créer la section critères de fichiers"""
        group = QGroupBox("📁 Critères de Fichiers")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(12)

        # Âge minimum
        age_widget = QWidget()
        age_layout = QVBoxLayout(age_widget)
        age_layout.setContentsMargins(0, 0, 0, 0)

        age_label = QLabel("Âge minimum des fichiers")
        age_label.setFont(QFont("Segoe UI", 12, QFont.Medium))
        age_label.setStyleSheet("color: #e2e8f0;")

        age_desc = QLabel("Les fichiers plus récents que cet âge seront préservés")
        age_desc.setStyleSheet("color: #94a3b8; font-size: 12px;")

        age_control_layout = QHBoxLayout()
        age_control_layout.setSpacing(16)

        self.age_slider = QSlider(Qt.Horizontal)
        self.age_slider.setRange(1, 365)
        self.age_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                border-radius: 3px;
                background: #404040;
                border: 1px solid #333333;
            }
            QSlider::handle:horizontal {
                background: #0078d4;
                border: 2px solid #005a6e;
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            QSlider::handle:hover {
                background: #0096d6;
                border: 2px solid #0078d4;
            }
        """)

        self.age_spinbox = QSpinBox()
        self.age_spinbox.setRange(1, 365)
        self.age_spinbox.setSuffix(" jours")
        self.age_spinbox.setFixedWidth(100)

        age_control_layout.addWidget(self.age_slider, 1)
        age_control_layout.addWidget(self.age_spinbox)
        age_control_layout.addStretch()

        age_layout.addWidget(age_label)
        age_layout.addWidget(age_desc)
        age_layout.addLayout(age_control_layout)

        group_layout.addWidget(age_widget)

        # Taille maximum
        size_widget = QWidget()
        size_layout = QVBoxLayout(size_widget)
        size_layout.setContentsMargins(0, 0, 0, 0)

        size_label = QLabel("Taille maximum des fichiers")
        size_label.setFont(QFont("Segoe UI", 12, QFont.Medium))
        size_label.setStyleSheet("color: #e2e8f0;")

        size_desc = QLabel("Les fichiers plus volumineux que cette taille seront ignorés")
        size_desc.setStyleSheet("color: #94a3b8; font-size: 12px;")

        size_control_layout = QHBoxLayout()
        size_control_layout.setSpacing(16)

        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(1, 1000000)  # 1 KB à 1000 MB en KB
        self.size_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                border-radius: 3px;
                background: #404040;
                border: 1px solid #333333;
            }
            QSlider::handle:horizontal {
                background: #0078d4;
                border: 2px solid #005a6e;
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            QSlider::handle:hover {
                background: #0096d6;
                border: 2px solid #0078d4;
            }
        """)

        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(1, 1000000)  # 1 KB à 1000 MB en KB
        self.size_spinbox.setSuffix(" KB")
        self.size_spinbox.setFixedWidth(100)

        # Valeur par défaut: 100 MB = 100000 KB
        self.size_spinbox.setValue(100000)

        size_control_layout.addWidget(self.size_slider, 1)
        size_control_layout.addWidget(self.size_spinbox)
        size_control_layout.addStretch()

        size_layout.addWidget(size_label)
        size_layout.addWidget(size_desc)
        size_layout.addLayout(size_control_layout)

        group_layout.addWidget(size_widget)
        layout.addWidget(group)

    def create_advanced_section(self, layout):
        """Créer la section options avancées"""
        group = QGroupBox("⚡ Options Avancées")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(10)

        # Supprimer les points de restauration
        restore_widget = QWidget()
        restore_layout = QHBoxLayout(restore_widget)
        restore_layout.setContentsMargins(0, 0, 0, 0)

        restore_left = QVBoxLayout()
        restore_left.setSpacing(4)

        self.restore_points_cb = QCheckBox("Supprimer les points de restauration")
        self.restore_points_cb.setFont(QFont("Segoe UI", 12, QFont.Medium))
        self.restore_points_cb.setStyleSheet("""
            QCheckBox::indicator:checked {
                background: #d32f2f;
                border: 1px solid #d32f2f;
            }
        """)

        restore_desc = QLabel("⚠️ Attention : Cette action peut affecter la récupération système")
        restore_desc.setStyleSheet("color: #f59e0b; font-size: 12px; font-weight: 500;")

        restore_left.addWidget(self.restore_points_cb)
        restore_left.addWidget(restore_desc)

        restore_layout.addLayout(restore_left)
        restore_layout.addStretch()

        # Vider la corbeille
        recycle_widget = QWidget()
        recycle_layout = QHBoxLayout(recycle_widget)
        recycle_layout.setContentsMargins(0, 0, 0, 0)

        self.recycle_bin_cb = QCheckBox("Vider la corbeille")
        self.recycle_bin_cb.setFont(QFont("Segoe UI", 12, QFont.Medium))
        self.recycle_bin_cb.setStyleSheet("""
            QCheckBox::indicator:checked {
                background: #0078d4;
                border: 1px solid #0078d4;
            }
        """)

        recycle_layout.addWidget(self.recycle_bin_cb)
        recycle_layout.addStretch()

        group_layout.addWidget(restore_widget)
        group_layout.addWidget(recycle_widget)
        layout.addWidget(group)

    def create_buttons(self):
        """Créer les boutons d'action"""
        button_frame = QFrame()
        button_frame.setStyleSheet("background: transparent; border: none;")
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 10, 0, 10)  # Marge augmentée pour la visibilité
        button_layout.setSpacing(12)

        # Bouton par défaut avec NavButton
        self.default_btn = NavButton("Par défaut")
        self.default_btn.set_secondary()
        self.default_btn.set_size("medium")

        # Spacer
        button_layout.addStretch()

       
        

        self.save_btn = NavButton("Sauvegarder")
        self.save_btn.set_primary()
        self.save_btn.set_size("medium")

        button_layout.addWidget(self.default_btn)
        button_layout.addWidget(self.save_btn)

        return button_frame

    def setup_connections(self):
        """Configurer les connexions"""
        # Connecter les sliders et spinboxes pour l'âge
        self.age_slider.valueChanged.connect(self.age_spinbox.setValue)
        self.age_spinbox.valueChanged.connect(self.age_slider.setValue)

        # Connecter les sliders et spinboxes pour la taille
        self.size_slider.valueChanged.connect(self.on_size_slider_changed)
        self.size_spinbox.valueChanged.connect(self.on_size_spinbox_changed)

        # Connecter les boutons
        self.save_btn.clicked.connect(self.save_settings)
        self.default_btn.clicked.connect(self.reset_to_defaults)

    def load_settings_from_qsettings(self):
        """Charger les paramètres depuis QSettings"""
        # Charger depuis QSettings ou utiliser les valeurs par défaut
        self.settings['min_file_age_days'] = self.qsettings.value('min_file_age_days', 30, type=int)
        self.settings['max_file_size_kb'] = self.qsettings.value('max_file_size_kb', 100000, type=int)
        self.settings['safe_mode'] = self.qsettings.value('safe_mode', True, type=bool)
        self.settings['delete_restore_points'] = self.qsettings.value('delete_restore_points', False, type=bool)
        self.settings['clear_recycle_bin'] = self.qsettings.value('clear_recycle_bin', True, type=bool)

        # Mettre à jour l'interface
        if hasattr(self, 'age_spinbox'):
            self.age_spinbox.setValue(self.settings['min_file_age_days'])
        if hasattr(self, 'size_spinbox'):
            self.size_spinbox.setValue(self.settings['max_file_size_kb'])
            # Initialiser le suffixe correct
            self.size_spinbox.setSuffix(self.get_size_suffix(self.settings['max_file_size_kb']))
            # S'assurer que le slider est synchronisé
            if hasattr(self, 'size_slider'):
                self.size_slider.setValue(self.settings['max_file_size_kb'])
        if hasattr(self, 'safe_mode_cb'):
            self.safe_mode_cb.setChecked(self.settings['safe_mode'])
        if hasattr(self, 'restore_points_cb'):
            self.restore_points_cb.setChecked(self.settings['delete_restore_points'])
        if hasattr(self, 'recycle_bin_cb'):
            self.recycle_bin_cb.setChecked(self.settings['clear_recycle_bin'])

    def save_settings_to_qsettings(self):
        """Sauvegarder les paramètres dans QSettings"""
        self.qsettings.setValue('min_file_age_days', self.settings['min_file_age_days'])
        self.qsettings.setValue('max_file_size_kb', self.settings['max_file_size_kb'])
        self.qsettings.setValue('safe_mode', self.settings['safe_mode'])
        self.qsettings.setValue('delete_restore_points', self.settings['delete_restore_points'])
        self.qsettings.setValue('clear_recycle_bin', self.settings['clear_recycle_bin'])
        self.qsettings.sync()  # Forcer l'écriture immédiate

    def save_settings(self):
        """Sauvegarder les paramètres"""
        new_settings = {
            'min_file_age_days': self.age_spinbox.value(),
            'max_file_size_kb': self.size_spinbox.value(),
            'safe_mode': self.safe_mode_cb.isChecked(),
            'delete_restore_points': self.restore_points_cb.isChecked(),
            'clear_recycle_bin': self.recycle_bin_cb.isChecked(),
        }

        self.settings.update(new_settings)

        # Sauvegarder dans QSettings
        self.save_settings_to_qsettings()

        # Émettre le signal
        self.settings_changed.emit(new_settings.copy())

        # Feedback visuel
        self.save_btn.setText("✅ Sauvegardé!")


        # Remettre le texte original après 2 secondes
        from PySide6.QtCore import QTimer
        QTimer.singleShot(2000, self.reset_save_button)

    def reset_save_button(self):
        """Remettre le bouton sauvegarder à son état normal"""
        self.save_btn.setText("Sauvegarder")

    def format_size_display(self, size_kb):
        """Formater l'affichage de la taille avec l'unité appropriée"""
        if size_kb < 1024:
            return f"{size_kb} KB"
        elif size_kb < 1024 * 1024:
            size_mb = size_kb / 1024
            return f"{size_mb:.1f} MB"
        else:
            size_gb = size_kb / (1024 * 1024)
            return f"{size_gb:.1f} GB"

    def on_size_slider_changed(self, value_kb):
        """Gérer le changement du slider de taille"""
        # Mettre à jour le spinbox avec la valeur en KB
        self.size_spinbox.blockSignals(True)  # Éviter la boucle infinie
        self.size_spinbox.setValue(value_kb)
        self.size_spinbox.blockSignals(False)

        # Mettre à jour le suffixe du spinbox
        self.size_spinbox.setSuffix(self.get_size_suffix(value_kb))

    def on_size_spinbox_changed(self, value_kb):
        """Gérer le changement du spinbox de taille"""
        # Mettre à jour le slider
        self.size_slider.blockSignals(True)  # Éviter la boucle infinie
        self.size_slider.setValue(value_kb)
        self.size_slider.blockSignals(False)

        # Mettre à jour le suffixe du spinbox
        self.size_spinbox.setSuffix(self.get_size_suffix(value_kb))

    def get_size_suffix(self, size_kb):
        """Obtenir le suffixe approprié selon la taille"""
        if size_kb < 1024:
            return " KB"
        elif size_kb < 1024 * 1024:
            return " MB"
        else:
            return " GB"
        

    def reset_to_defaults(self):
        """Remettre aux valeurs par défaut"""
        defaults = {
            'min_file_age_days': 30,
            'max_file_size_kb': 100000,
            'safe_mode': True,
            'delete_restore_points': False,
            'clear_recycle_bin': True,
        }

        self.settings = defaults.copy()

        self.age_spinbox.setValue(defaults['min_file_age_days'])
        self.size_spinbox.setValue(defaults['max_file_size_kb'])
        self.safe_mode_cb.setChecked(defaults['safe_mode'])
        self.restore_points_cb.setChecked(defaults['delete_restore_points'])
        self.recycle_bin_cb.setChecked(defaults['clear_recycle_bin'])

        # Sauvegarder les valeurs par défaut dans QSettings
        self.save_settings_to_qsettings()

       

    def get_settings(self):
        """Obtenir les paramètres actuels"""
        return self.settings.copy()


# Point d'entrée pour tester cette classe spécifiquement
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setApplicationName("NettoyeurRapide - Test Settings")

    # Créer et afficher la boîte de dialogue des paramètres
    dialog = SettingsDialog()
    dialog.show()

    # Exécuter l'application
    sys.exit(app.exec())