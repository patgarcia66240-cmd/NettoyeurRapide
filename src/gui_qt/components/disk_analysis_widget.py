"""
DiskAnalysisWidget - Widget complet d'analyse disque avec contrôle SMART
"""

import os
import sys
from datetime import datetime

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QSizePolicy,
                              QProgressBar, QTextEdit,
                              QComboBox, QTreeWidget, QTreeWidgetItem, QTabWidget,
                              QSpinBox, QFileDialog)
from PySide6.QtCore import Qt, Signal, QTimer, QRect
from PySide6.QtGui import QPixmap, QPainter, QColor, QPen, QFont

from .nav_button import NavButton

from core.smart_controller import SmartControllerThread
from core.disk_scanner import DiskScannerThread


class DiskAnalysisWidget(QWidget):
    """Widget complet d'analyse disque avec contrôle SMART et visualisations"""

    # Signaux
    scan_started = Signal()
    scan_completed = Signal(dict)
    smart_completed = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_disk = 'C:\\'
        self.scan_results = {}
        self.smart_results = {}
        self.scanner_thread = None
        self.smart_thread = None
        self.setup_ui()
        self.setup_style()
        self.refresh_disk_list()

        # État du tri pour l'onglet Types de fichiers
        self.sort_column = 0  # 0: Type, 1: Nombre, 2: Taille totale, 3: Taille moyenne
        self.sort_order = 0   # 0: croissant, 1: décroissant

    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header moderne
        self.setup_header(layout)

        # Zone de contrôle
        self.setup_control_panel(layout)

        # Zone d'onglets
        self.setup_tab_widget(layout)

        # Barre de progression
        self.setup_progress_bar(layout)

        # Zone de statistiques
        self.setup_stats_area(layout)

    def setup_header(self, parent_layout):
        """Configurer l'en-tête moderne"""
        header_frame = QFrame()
        header_frame.setObjectName("diskAnalysisHeader")
        header_frame.setFixedHeight(50)
        header_frame.setStyleSheet("""
            QFrame#diskAnalysisHeader {
                 background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(41, 128, 185, 0.95),
                    stop:0.5 rgba(52, 152, 219, 0.95),
                    stop:1 rgba(41, 128, 185, 0.95));
                border: none;
                border-bottom: 2px solid rgba(52, 73, 94, 0.3);
            }
        """)

        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 0, 20, 0)  # Moins d'espace à gauche
        header_layout.setSpacing(15)

        # Icône et titre
        self.header_icon = QLabel("💿")
        self.header_icon.setStyleSheet("""
            font-size: 24px;
            color: #FFFFFF;
            background: transparent;
        """)

        self.header_title = QLabel("Analyse Disque Avancée")
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

        # Espace flexible pour pousser les contrôles à droite
        header_layout.addStretch()

        # Sélecteur de disque
        self.disk_selector = QComboBox()
        self.disk_selector.setObjectName("diskSelector")
        self.disk_selector.setStyleSheet("""
            QComboBox {
                background: #ffffff;
                color: #2c3e50;
                border: 2px solid rgba(52, 152, 219, 0.6);
                border-radius: 6px;
                padding: 5px 10px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                font-weight: 500;
                min-width: 120px;
                selection-background-color: rgba(52, 152, 219, 0.8);
            }
            QComboBox:hover {
                border: 2px solid rgba(52, 152, 219, 0.9);
                background: #f8f9fa;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
                background: #ffffff;
            }
          
            QComboBox QAbstractItemView {
                background: #ffffff;
                border: 2px solid rgba(52, 152, 219, 0.8);
                selection-background-color: rgba(52, 152, 219, 0.9);
                selection-color: #ffffff;
                padding: 5px;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px 12px;
                border-bottom: 1px solid rgba(189, 195, 199, 0.3);
                color: #2c3e50;
            }
            QComboBox QAbstractItemView::item:hover {
                background: rgba(52, 152, 219, 0.1);
            }
            QComboBox QAbstractItemView::item:selected {
                background: rgba(52, 152, 219, 0.8);
                color: #ffffff;
            }
        """)
        self.disk_selector.currentTextChanged.connect(self.on_disk_changed)

        # Ajouter les contrôles à droite
        header_layout.addWidget(self.disk_selector)

        parent_layout.addWidget(header_frame)

    def setup_control_panel(self, parent_layout):
        """Configurer le panneau de contrôle"""
        control_frame = QFrame()
        control_frame.setObjectName("diskControlPanel")
        control_frame.setFixedHeight(70)
        control_frame.setStyleSheet("""
            QFrame#diskControlPanel {
                background: rgba(155, 89, 182, 0.1);
                border: none;
                border-bottom: 1px solid rgba(52, 73, 94, 0.2);
            }
        """)

        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(15, 8, 15, 8)  # Marges verticales équilibrées
        control_layout.setSpacing(15)
        control_layout.setAlignment(Qt.AlignVCenter)  # Aligner tout au centre vertical

        # Groupe gauche: Options d'analyse
        left_group = QWidget()
        left_layout = QHBoxLayout(left_group)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        left_layout.setAlignment(Qt.AlignVCenter)  # Centrer verticalement

        # Label et combo box pour le type
        type_label = QLabel("Type:")
        type_label.setFixedHeight(32)  # Forcer la même hauteur que les boutons
        type_label.setAlignment(Qt.AlignCenter)  # Centrer verticalement le texte
        type_label.setStyleSheet("""
            color: #dadde0;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
            font-weight: 500;
            min-width: 30px;
        """)

        self.scan_type_combo = QComboBox()
        self.scan_type_combo.setFixedHeight(32)  # Forcer la même hauteur que les boutons
        self.scan_type_combo.addItems(["Scan Rapide", "Scan Complet", "Scan par Type", "Scan Personnalisé"])
        self.scan_type_combo.setStyleSheet("""
            QComboBox {
                background: #ffffff;
                color: #2c3e50;
                border: 2px solid #2980b9;
                border-radius: 6px;
                padding: 6px 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                min-width: 150px;
            }
            QComboBox:hover {
                border: 2px solid #3498db;
                background: #f8f9fa;
            }
           
           
            QComboBox QAbstractItemView {
                background: #ffffff;
                border: 2px solid #2980b9;
                selection-background-color:#3498db;
                selection-color: #ffffff;
                padding: 5px;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px 12px;
                border-bottom: 1px solid rgba(189, 195, 199, 0.3);
                color: #2c3e50;
                background: transparent;
            }
            QComboBox QAbstractItemView::item:hover {
                background: rgba(52, 152, 219, 0.1);
            }
            QComboBox QAbstractItemView::item:selected {
                background: rgba(52, 152, 219, 0.8);
                color: #ffffff;
            }
        """)

        # Taille minimale pour les gros fichiers
        size_label = QLabel("Taille min:")
        size_label.setFixedHeight(32)  # Forcer la même hauteur que les boutons
        size_label.setAlignment(Qt.AlignCenter)  # Centrer verticalement le texte
        size_label.setStyleSheet("""
            color: #e2e5e7;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
            font-weight: 500;
            min-width: 70px;
        """)

        self.min_size_spin = QSpinBox()
        self.min_size_spin.setFixedHeight(32)  # Forcer la même hauteur que les boutons
        self.min_size_spin.setRange(1, 1000)
        self.min_size_spin.setValue(10)
        self.min_size_spin.setSuffix(" MB")
        self.min_size_spin.setStyleSheet("""
            QSpinBox {
                background: #ffffff;
                color: #2c3e50;
                border: 2px solid rgba(52, 152, 219, 0.6);
                border-radius: 6px;
                padding: 4px 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                min-width: 80px;
            }
            QSpinBox:hover {
                border: 2px solid rgba(52, 152, 219, 0.8);
                background: #f8f9fa;
            }
        """)

        left_layout.addWidget(type_label)
        left_layout.addWidget(self.scan_type_combo)
        left_layout.addWidget(size_label)
        left_layout.addWidget(self.min_size_spin)

        # Groupe droit: Boutons d'action
        right_group = QWidget()
        right_layout = QHBoxLayout(right_group)
        right_layout.setContentsMargins(0, 0, 0, 0)  # Pas de marge négative
        right_layout.setSpacing(8)
        right_layout.setAlignment(Qt.AlignVCenter)  # Centrer verticalement

        # Boutons d'action
        self.btn_scan = NavButton("🔍 Analyser", self)
        self.btn_scan.set_primary()
        self.btn_scan.sizeType = "small"
        self.btn_scan.clicked.connect(self.start_scan)

        self.btn_cancel = NavButton("❌ Annuler", self)
        self.btn_cancel.set_secondary()
        self.btn_cancel.sizeType = "small"
        self.btn_cancel.clicked.connect(self.cancel_scan)
        self.btn_cancel.setEnabled(False)

        self.btn_export = NavButton("📄 Exporter", self)
        self.btn_export.set_secondary()
        self.btn_export.sizeType = "small"
        self.btn_export.clicked.connect(self.export_results)

        right_layout.addWidget(self.btn_scan)
        right_layout.addWidget(self.btn_cancel)
        right_layout.addWidget(self.btn_export)

        # Ajouter les groupes au layout principal
        control_layout.addWidget(left_group)
        control_layout.addStretch()  # Espace flexible entre les groupes
        control_layout.addWidget(right_group)

        parent_layout.addWidget(control_frame)

    def setup_tab_widget(self, parent_layout):
        """Configurer le widget à onglets"""
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("diskAnalysisTabs")
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid rgba(189, 195, 199, 0.3);
                background: rgba(255, 255, 255, 0.95);
                border-radius: 8px;
            }
            QTabBar::tab {
                 background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(185, 185, 185, 0.7),
                stop:0.5 rgba(178, 180, 180, 0.6),
                stop:1 rgba(185, 185, 185, 0.7));
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db,
                    stop:1 #135e90);
                color: white;
            }
            QTabBar::tab:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6fa8ed,
                    stop:1 #306ea9);
                color: white;
            }
        """)

        # Onglet Vue d'ensemble
        self.setup_overview_tab()

        # Onglet Types de fichiers
        self.setup_file_types_tab()

        # Onglet Gros fichiers
        self.setup_large_files_tab()

        # Onglet Dossiers
        self.setup_directories_tab()

        # Onglet Contrôle SMART
        self.setup_smart_tab()

        parent_layout.addWidget(self.tab_widget)

    def setup_overview_tab(self):
        """Configurer l'onglet de vue d'ensemble"""
        overview_widget = QWidget()
        layout = QHBoxLayout(overview_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Visualisation graphique à gauche (plus grand)
        self.visualization_widget = QLabel("Aucune analyse effectuée")
        self.visualization_widget.setAlignment(Qt.AlignCenter)
        self.visualization_widget.setMinimumSize(400, 400)  # Taille minimale augmentée
        self.visualization_widget.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(236, 240, 241, 0.8),
                stop:0.5 rgba(189, 195, 199, 0.6),
                stop:1 rgba(159, 167, 168, 0.7));
            border: 1px solid rgba(189, 195, 199, 0.3);
            border-radius: 12px;
            color: #7f8c8d;
            font-size: 16px;
            padding: 4px;
        """)

        # Informations détaillées à droite
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            background: rgba(255, 255, 255, 0.7);
            border: 1px solid rgba(189, 195, 199, 0.3);
            border-radius: 8px;
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(15, 15, 15, 15)
        info_layout.setSpacing(10)

        info_title = QLabel("Informations Générales")
        info_title.setStyleSheet("""
            color: #2c3e50;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 16px;
            font-weight: 600;
            border-bottom: 2px solid rgba(155, 89, 182, 0.3);
            padding-bottom: 5px;
        """)
        info_title.setFixedHeight(30)

        self.overview_info = QTextEdit()
        self.overview_info.setReadOnly(True)
        self.overview_info.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.overview_info.setStyleSheet("""
            QTextEdit {
                background: transparent;
                border: none;
                color: #34495e;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }
        """)
        self.overview_info.setPlaceholderText("Lancez une analyse pour voir les informations...")

        info_layout.addWidget(info_title)
        info_layout.addWidget(self.overview_info)

        layout.addWidget(self.visualization_widget, 2)
        layout.addWidget(info_frame, 1)

        self.tab_widget.addTab(overview_widget, "📊 Vue d'ensemble")

    def setup_file_types_tab(self):
        """Configurer l'onglet des types de fichiers"""
        file_types_widget = QWidget()
        layout = QVBoxLayout(file_types_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Panneau de filtres en haut (simplifié avec seulement le filtre par type)
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background: rgba(52, 152, 219, 0.1);
                border: 1px solid rgba(52, 152, 219, 0.3);
                border-radius: 6px;
                padding: 5px;
            }
        """)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(10, 5, 10, 5)
        filter_layout.setSpacing(15)

        # Filtre par type de fichier
        type_label = QLabel("Filtrer par extension:")
        type_label.setStyleSheet("""
            color: #2c3e50;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
            font-weight: 500;
        """)

        self.file_type_filter = QComboBox()
        self.file_type_filter.setEditable(True)
        self.file_type_filter.addItem("Tous les types")
        self.file_type_filter.setMinimumWidth(120)
        self.file_type_filter.setStyleSheet("""
            QComboBox {
                background: #ffffff;
                color: #2c3e50;
                border: 2px solid rgba(57, 137, 187, 0.6);
                border-radius: 6px;
                padding: 5px 10px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                min-width: 120px;
            }
            QComboBox:hover {
                border: 2px solid rgba(89, 132, 182, 0.8);
                background: #f8f9fa;
            }
            QComboBox QLineEdit {
                background: #ffffff;
                border: none;
                padding: 2px;
                color: #2c3e50;
            }
          
            QComboBox QAbstractItemView {
                background: #ffffff;
                border: 2px solid rgba(89, 118, 182, 0.8);
                selection-background-color: rgba(89, 137, 182, 0.9);
                selection-color: #ffffff;
                padding: 5px;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px 12px;
                border-bottom: 1px solid rgba(189, 195, 199, 0.3);
                color: #2c3e50;
                background: transparent;
            }
            QComboBox QAbstractItemView::item:hover {
                background: rgba(155, 89, 182, 0.1);
            }
            QComboBox QAbstractItemView::item:selected {
                background: rgba(49, 116, 184, 0.9);
                color: #ffffff;
            }
        """)
        self.file_type_filter.currentTextChanged.connect(self.filter_file_types)

        # Bouton pour réinitialiser les filtres
        from .nav_button import NavButton
        self.btn_reset_filters = NavButton("🔄 Réinitialiser", self)
        self.btn_reset_filters.set_secondary()
        self.btn_reset_filters.sizeType = "small"
        self.btn_reset_filters.clicked.connect(self.reset_file_type_filters)

        # Indicateur de tri actuel
        self.sort_indicator = QLabel("Tri: Type ↑ | Taille ↓")
        self.sort_indicator.setStyleSheet("""
            color: #7f8c8d;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 11px;
            font-style: italic;
            padding: 2px 8px;
            background: rgba(255, 255, 255, 0.5);
            border-radius: 3px;
        """)

        # Ajouter les contrôles au layout
        filter_layout.addWidget(type_label)
        filter_layout.addWidget(self.file_type_filter)
        filter_layout.addStretch()
        filter_layout.addWidget(self.sort_indicator)
        filter_layout.addWidget(self.btn_reset_filters)

        # Tree widget pour les types de fichiers avec headers cliquables
        self.file_types_tree = QTreeWidget()
        self.file_types_tree.setHeaderLabels(["Type de fichier ↕", "Nombre ↕", "Taille totale ↕", "Taille moyenne"])
        self.file_types_tree.setSortingEnabled(False)  # Désactiver le tri automatique

        # Connecter le clic sur les headers
        self.file_types_tree.header().setSectionsClickable(True)
        self.file_types_tree.header().sectionClicked.connect(self.on_header_clicked)

        self.file_types_tree.setStyleSheet("""
            QTreeWidget {
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(189, 195, 199, 0.3);
                border-radius: 6px;
                color: #34495e;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                gridline-color: rgba(189, 195, 199, 0.2);
            }
            QTreeWidget::header {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(89, 153, 182, 0.8),
                    stop:1 rgba(68, 101, 173, 0.8));
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
            }
            QTreeWidget::header::section {
                background: transparent;
                color: white;
                padding: 5px 10px;
                border: none;
                font-weight: 600;
                font-size: 12px;
            }
            QTreeWidget::header::section:hover {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 3px;
            }
            QTreeWidget::item {
                padding: 5px;
                border-bottom: 1px solid rgba(189, 195, 199, 0.1);
            }
            QTreeWidget::item:selected {
                background: rgba(155, 89, 182, 0.2);
                color: #2c3e50;
            }
        """)

        layout.addWidget(filter_frame)
        layout.addWidget(self.file_types_tree)

        self.tab_widget.addTab(file_types_widget, "📁 Types de fichiers")

    def setup_large_files_tab(self):
        """Configurer l'onglet des gros fichiers"""
        large_files_widget = QWidget()
        layout = QVBoxLayout(large_files_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Filtres en haut
        filter_frame = QFrame()
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        label_ext=QLabel("Filtrer par extension:")
        label_ext.setStyleSheet("border:none; background:transparent; font-size:12px; color:#243240;")
        filter_layout.addWidget(label_ext)
        self.extension_filter = QComboBox()
        self.extension_filter.setEditable(True)
        self.extension_filter.addItem("Tous")
        self.extension_filter.setStyleSheet("""
            QComboBox {
                background: #ffffff;
                color: #243240;
                border: 2px solid rgba(56, 98, 222, 0.6);
                border-radius: 6px;
                padding: 5px 10px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                min-width: 120px;
            }
            QComboBox:hover {
                border: 2px solid rgba(60, 120, 231, 0.8);
                background: #f8f9fa;
            }
            QComboBox QLineEdit {
                background: #ffffff;
                border: none;
                padding: 2px;
                color: #2c3e50;
            }          
            
            QComboBox QAbstractItemView {
                background: #ffffff;
                border: 2px solid rgba(41, 74, 125, 0.8);
                selection-background-color: rgba(60, 146, 231, 0.9);
                selection-color: #ffffff;
                padding: 5px;
                outline: none;
                show-decoration-selected: 1;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px 12px;
                border-bottom: 1px solid rgba(189, 195, 199, 0.3);
                color: #2c3e50;
                background: transparent;
            }
            QComboBox QAbstractItemView::item:hover {
                background: rgba(60, 128, 231, 0.1);
            }
            QComboBox QAbstractItemView::item:selected {
                background: rgba(60, 114, 231, 0.9);
                color: #ffffff;
            }
        """)
        self.extension_filter.currentTextChanged.connect(self.filter_large_files)

        filter_layout.addWidget(self.extension_filter)
        filter_layout.addStretch()

        # Tree widget pour les gros fichiers
        self.large_files_tree = QTreeWidget()
        self.large_files_tree.setHeaderLabels(["Fichier", "Taille", "Chemin"])
        self.large_files_tree.setStyleSheet("""
            QTreeWidget {
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(189, 195, 199, 0.3);
                border-radius: 6px;
                color: #34495e;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
            }
            QTreeWidget::header {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(60, 208, 231, 0.8),
                    stop:1 rgba(56, 123, 218, 0.8));
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
            }
            QTreeWidget::item:selected {
                background: rgba(122, 168, 232, 0.2);
                color: #3e4953;
            }
        """)

        layout.addWidget(filter_frame)
        layout.addWidget(self.large_files_tree)

        self.tab_widget.addTab(large_files_widget, "💾 Gros fichiers")

    def setup_directories_tab(self):
        """Configurer l'onglet des dossiers"""
        directories_widget = QWidget()
        layout = QVBoxLayout(directories_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Tree widget pour les dossiers
        self.directories_tree = QTreeWidget()
        self.directories_tree.setHeaderLabels(["Dossier", "Taille", "Niveau"])
        self.directories_tree.setStyleSheet("""
            QTreeWidget {
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(189, 195, 199, 0.3);
                border-radius: 6px;
                color: #34495e;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }
            QTreeWidget::header {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(52, 152, 219, 0.8),
                    stop:1 rgba(41, 128, 185, 0.8));
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
            }
            QTreeWidget::item:selected {
                background: rgba(52, 152, 219, 0.2);
                color: #2c3e50;
            }
        """)

        layout.addWidget(self.directories_tree)

        self.tab_widget.addTab(directories_widget, "📂 Dossiers")

    def setup_smart_tab(self):
        """Configurer l'onglet de contrôle SMART"""
        smart_widget = QWidget()
        layout = QVBoxLayout(smart_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Information SMART
        smart_info_frame = QFrame()
        smart_info_frame.setStyleSheet("""
            background: rgba(255, 255, 255, 0.7);
            border: 1px solid rgba(189, 195, 199, 0.3);
            border-radius: 8px;
        """)
        smart_info_layout = QVBoxLayout(smart_info_frame)
        smart_info_layout.setContentsMargins(20, 20, 20, 20)
        smart_info_layout.setSpacing(15)

        # Layout horizontal pour le titre et le bouton
        title_button_layout = QHBoxLayout()
        title_button_layout.setContentsMargins(0, 0, 0, 0)
        title_button_layout.setSpacing(10)

        smart_title = QLabel("🔧 Informations SMART")
        smart_title.setStyleSheet("""
            color: #2c3e50;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 18px;
            font-weight: 600;
            border-bottom: 2px solid rgba(155, 89, 182, 0.3);
            padding-bottom: 5px;
        """)

        # Bouton SMART dans l'onglet
        self.btn_smart = QPushButton("🔧 Contrôle SMART")
        self.btn_smart.setObjectName("smartBtn")
        self.btn_smart.setCursor(Qt.PointingHandCursor)
        self.btn_smart.setStyleSheet("""
            QPushButton {
                background: #667eea;
                color: #ffffff;
                border: 1px solid #5a6fd8;
                border-radius: 8px;
                padding: 10px 20px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #764ba2;
                color: #ffffff;
                border: 1px solid #6b46c1;
            }
            QPushButton:pressed {
                background: #5a67d8;
                color: #ffffff;
                border: 1px solid #4c5cc5;
            }
        """)

        # Ajouter le titre et le bouton au layout
        title_button_layout.addWidget(smart_title)
        title_button_layout.addStretch()  # Espace flexible pour pousser le bouton à droite
        title_button_layout.addWidget(self.btn_smart)

        self.smart_info_text = QTextEdit()
        self.smart_info_text.setReadOnly(True)
        self.smart_info_text.setMaximumHeight(200)
        self.smart_info_text.setStyleSheet("""
            QTextEdit {
                background: transparent;
                border: none;
                color: #34495e;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                line-height: 1.5;
            }
        """)
        self.smart_info_text.setPlaceholderText("Cliquez sur 'Contrôle SMART' pour analyser l'état de santé du disque...")

        # Ajouter le layout titre+bouton puis le texte
        smart_info_layout.addLayout(title_button_layout)
        smart_info_layout.addWidget(self.smart_info_text)

        # État de santé
        health_frame = QFrame()
        health_frame.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(52, 152, 219, 0.1),
                stop:0.5 rgba(41, 128, 185, 0.1),
                stop:1 rgba(31, 97, 141, 0.1));
            border: 1px solid rgba(189, 195, 199, 0.3);
            border-radius: 8px;
        """)
        health_layout = QVBoxLayout(health_frame)
        health_layout.setContentsMargins(20, 20, 20, 20)

        health_title = QLabel("📊 État de Santé")
        health_title.setStyleSheet("""
            color: #2c3e50;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 16px;
            font-weight: 600;
        """)

        self.health_status_label = QLabel("Non analysé")
        self.health_status_label.setStyleSheet("""
            color: #7f8c8d;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 14px;
            font-weight: 500;
            padding: 10px;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 6px;
            text-align: center;
        """)

        health_layout.addWidget(health_title)
        health_layout.addWidget(self.health_status_label)

        layout.addWidget(smart_info_frame)
        layout.addWidget(health_frame)
        layout.addStretch()

        self.tab_widget.addTab(smart_widget, "🔧 Contrôle SMART")

    def setup_progress_bar(self, parent_layout):
        """Configurer la barre de progression"""
        progress_frame = QFrame()
        progress_frame.setObjectName("diskProgressFrame")
        progress_frame.setFixedHeight(40)
        progress_frame.setStyleSheet("""
            QFrame#diskProgressFrame {
                background: rgba(155, 89, 182, 0.05);
                border: none;
                border-top: 1px solid rgba(52, 73, 94, 0.1);
            }
        """)

        progress_layout = QHBoxLayout(progress_frame)
        progress_layout.setContentsMargins(20, 5, 20, 5)
        progress_layout.setSpacing(15)

        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("diskProgressBar")
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setFixedWidth(400)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar#diskProgressBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(189, 195, 199, 0.4),
                    stop:1 rgba(189, 195, 199, 0.2));
                border: 1px solid rgba(189, 195, 199, 0.3);
                border-radius: 10px;
                text-align: center;
                color: #e4e4e4;
                font-weight: 600;
                height: 20px;
            }
            QProgressBar#diskProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7c8ff5,
                    stop:0.5 #667eea,
                    stop:1 #5a6fd8);
                border-radius: 6px;
                margin: 2px;
            }
        """)

        # État
        self.status_label = QLabel("Prêt")
        self.status_label.setStyleSheet("""
            color: #7f8c8d;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
            background: transparent;
        """)

        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)
        progress_layout.addStretch()

        parent_layout.addWidget(progress_frame)

    def setup_stats_area(self, parent_layout):
        """Configurer la zone de statistiques"""
        stats_frame = QFrame()
        stats_frame.setObjectName("diskStatsFrame")
        stats_frame.setFixedHeight(80)
        stats_frame.setStyleSheet("""
            QFrame#diskStatsFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(155, 89, 182, 0.1),
                    stop:0.5 rgba(142, 68, 173, 0.1),
                    stop:1 rgba(155, 89, 182, 0.1));
                border: none;
                border-top: 1px solid rgba(52, 73, 94, 0.2);
            }
        """)

        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(20, 10, 20, 10)
        stats_layout.setSpacing(30)

        # Statistiques
        self.files_analyzed_label = QLabel("0 fichiers analysés")
        self.files_analyzed_label.setStyleSheet(self.get_stat_style())

        self.total_size_label = QLabel("0 MB")
        self.total_size_label.setStyleSheet(self.get_stat_style())

        self.scan_time_label = QLabel("--:--:--")
        self.scan_time_label.setStyleSheet(self.get_stat_style())

        self.disk_health_label = QLabel("État: Inconnu")
        self.disk_health_label.setStyleSheet(self.get_stat_style())

        stats_layout.addWidget(self.files_analyzed_label)
        stats_layout.addWidget(self.total_size_label)
        stats_layout.addWidget(self.scan_time_label)
        stats_layout.addWidget(self.disk_health_label)
        stats_layout.addStretch()

        parent_layout.addWidget(stats_frame)

    def get_stat_style(self):
        """Retourner le style pour les labels de statistiques"""
        return """
            color:rgba(255, 255, 255, 0.7);
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
            font-weight: 500;
            background: transparent;
            padding: 8px 15px;
            border-radius: 20px;
            border: none;
        """

    def setup_style(self):
        """Appliquer le style général"""
        # Connecter le bouton SMART
        self.btn_smart.clicked.connect(self.run_smart_check)

    def refresh_disk_list(self):
        """Rafraîchir la liste des disques disponibles"""
        self.disk_selector.clear()

        try:
            if sys.platform == 'win32':
                import string
                drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:")]
                for drive in drives:
                    self.disk_selector.addItem(f"Disque {drive[0]} ({drive})", drive)
            else:
                # Linux/Unix
                mounts = []
                with open('/proc/mounts', 'r') as f:
                    for line in f:
                        if line.startswith('/dev/'):
                            parts = line.split()
                            if len(parts) >= 2:
                                mounts.append(parts[1])

                for mount in mounts:
                    self.disk_selector.addItem(mount, mount)

            # Sélectionner le premier disque par défaut
            if self.disk_selector.count() > 0:
                self.current_disk = self.disk_selector.itemData(0)

        except Exception as e:
            # En cas d'erreur, ajouter des disques par défaut
            self.disk_selector.addItem("C:\\", "C:\\")
            if sys.platform != 'win32':
                self.disk_selector.addItem("/", "/")

    def on_disk_changed(self):
        """Gérer le changement de disque"""
        index = self.disk_selector.currentIndex()
        if index >= 0:
            self.current_disk = self.disk_selector.itemData(index)
            # Effacer les résultats précédents
            self.clear_results()

    def clear_results(self):
        """Effacer les résultats précédents"""
        self.scan_results = {}
        self.smart_results = {}
        self.file_types_tree.clear()
        self.large_files_tree.clear()
        self.directories_tree.clear()
        self.overview_info.clear()
        self.smart_info_text.clear()
        self.visualization_widget.setText("Aucune analyse effectuée")

    def start_scan(self):
        """Démarrer l'analyse du disque"""
        if self.scanner_thread and self.scanner_thread.isRunning():
            return

        self.scan_started.emit()
        self.clear_results()

        # Obtenir le type d'analyse
        scan_type_map = {
            "Scan Rapide": "quick",
            "Scan Complet": "full",
            "Scan par Type": "type",
            "Scan Personnalisé": "custom"
        }
        scan_type = scan_type_map.get(self.scan_type_combo.currentText(), "quick")

        # Gérer le scan personnalisé
        if scan_type == "custom":
            folder = QFileDialog.getExistingDirectory(self, "Sélectionner un dossier")
            if folder:
                self.current_disk = folder
            else:
                return

        # Mettre à jour l'interface
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText(f"Analyse {self.scan_type_combo.currentText().lower()} en cours...")
        self.btn_scan.setEnabled(False)
        self.btn_cancel.setEnabled(True)

        # Démarrer le thread d'analyse
        self.scanner_thread = DiskScannerThread(self.current_disk, scan_type)
        self.scanner_thread.progress_updated.connect(self.update_progress)
        self.scanner_thread.scan_completed.connect(self.on_scan_completed)
        self.scanner_thread.error_occurred.connect(self.on_scan_error)
        self.scanner_thread.start()

    def cancel_scan(self):
        """Annuler l'analyse en cours"""
        if self.scanner_thread and self.scanner_thread.isRunning():
            self.scanner_thread.cancel()
            self.status_label.setText("Annulation en cours...")

    def update_progress(self, value, message):
        """Mettre à jour la barre de progression"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)

    def on_scan_completed(self, results):
        """Gérer la fin de l'analyse"""
        self.scan_results = results
        self.progress_bar.setValue(100)
        self.status_label.setText("Analyse terminée")

        # Mettre à jour les onglets
        self.update_overview_tab()
        self.update_file_types_tab()
        self.update_large_files_tab()
        self.update_directories_tab()

        # Mettre à jour les statistiques
        self.update_stats()

        # Réactiver les boutons
        self.btn_scan.setEnabled(True)
        self.btn_cancel.setEnabled(False)

        # Cacher la barre de progression après 2 secondes
        QTimer.singleShot(2000, lambda: self.progress_bar.setVisible(False))

        self.scan_completed.emit(results)

    def on_scan_error(self, error_message):
        """Gérer les erreurs d'analyse"""
        self.status_label.setText(f"Erreur: {error_message}")
        self.btn_scan.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        QTimer.singleShot(2000, lambda: self.progress_bar.setVisible(False))
        self.error_occurred.emit(error_message)

    def update_overview_tab(self):
        """Mettre à jour l'onglet de vue d'ensemble"""
        if not self.scan_results:
            return

        # Mettre à jour le texte d'information
        info_text = f"""
📊 RÉSULTATS DE L'ANALYSE
═══════════════════════════════════════

📁 Fichiers analysés : {self.scan_results['total_files']:,}
💾 Espace total : {self.format_size(self.scan_results['total_size'])}
🕐 Date de l'analyse : {self.scan_results['scan_time']}

📈 TYPES DE FICHIERS TROUVÉS : {len(self.scan_results['file_types'])}
💎 GROS FICHIERS : {len(self.scan_results['large_files'])}
📂 DOSSIERS VOLUMINEUX : {len(self.scan_results['directories'])}

📋 RÉPARTITION PAR TYPE :
"""

        # Ajouter les 5 types de fichiers les plus importants
        sorted_types = sorted(
            self.scan_results['file_types'].items(),
            key=lambda x: x[1]['size'],
            reverse=True
        )[:5]

        for ext, data in sorted_types:
            percentage = (data['size'] / self.scan_results['total_size']) * 100
            info_text += f"   {ext or '(sans extension)'} : {data['count']} fichiers ({percentage:.1f}%)\n"

        self.overview_info.setText(info_text)

        # Créer une visualisation simple
        self.create_simple_visualization()

    def create_simple_visualization(self):
        """Créer une visualisation graphique simple"""
        if not self.scan_results or not self.scan_results['file_types']:
            return

        # Créer une image simple avec les types de fichiers (plus grand)
        width, height = 600, 500  # Taille augmentée pour un camembert plus grand
        pixmap = QPixmap(width, height)
        pixmap.fill(QColor(255, 255, 255))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Dessiner un camembert simple
        colors = [
            QColor(155, 89, 182),   # Violet
            QColor(52, 152, 219),   # Bleu
            QColor(46, 204, 113),   # Vert
            QColor(241, 196, 15),   # Jaune
            QColor(231, 76, 60),    # Rouge
            QColor(230, 126, 34),   # Orange
            QColor(149, 165, 166),  # Gris
        ]

        total_size = self.scan_results['total_size']
        sorted_types = sorted(
            self.scan_results['file_types'].items(),
            key=lambda x: x[1]['size'],
            reverse=True
        )[:7]

        start_angle = 0
        rect = QRect(50, 50, 350, 350)  # Cercle beaucoup plus grand

        for i, (ext, data) in enumerate(sorted_types):
            angle = int((data['size'] / total_size) * 360)
            if angle < 5:  # Angle minimum pour la visibilité
                angle = 5

            color = colors[i % len(colors)]
            painter.setBrush(color)
            painter.setPen(QPen(Qt.white, 2))
            painter.drawPie(rect, start_angle * 16, angle * 16)

            # Légende (ajustée pour le camembert plus grand)
            legend_rect = QRect(430, 50 + i * 32, 19, 19)  # Carrés de légende plus grands
            painter.drawRect(legend_rect)
            painter.fillRect(legend_rect, color)

            percentage = (data['size'] / total_size) * 100
            legend_text = f"{ext or 'Autres'} ({percentage:.1f}%)"
            painter.setPen(QColor(0, 0, 0))
            painter.setFont(QFont("Arial", 11))  # Police plus grande
            painter.drawText(460, 67 + i * 32, legend_text)  # Texte plus grand

            start_angle += angle

        painter.end()
        self.visualization_widget.setPixmap(pixmap)

    def update_file_types_tab(self):
        """Mettre à jour l'onglet des types de fichiers"""
        self.file_types_tree.clear()

        if not self.scan_results or not self.scan_results['file_types']:
            return

        # Stocker les données brutes pour le tri/filtrage
        self.current_file_types_data = self.scan_results['file_types'].copy()

        # Mettre à jour le filtre de types avec les extensions trouvées
        extensions = set()
        for ext in self.current_file_types_data.keys():
            if ext:
                extensions.add(ext)

        # Conserver l'élément "Tous les types"
        current_text = self.file_type_filter.currentText()
        self.file_type_filter.clear()
        self.file_type_filter.addItem("Tous les types")

        for ext in sorted(extensions):
            if ext not in [self.file_type_filter.itemText(i) for i in range(self.file_type_filter.count())]:
                self.file_type_filter.addItem(ext)

        # Restaurer la sélection précédente si possible
        index = self.file_type_filter.findText(current_text)
        if index >= 0:
            self.file_type_filter.setCurrentIndex(index)

        # Appliquer le tri et le filtrage actuels
        self.apply_file_type_filters()

    def on_header_clicked(self, column_index):
        """Gérer le clic sur les headers pour le tri"""
        if self.sort_column == column_index:
            # Inverser l'ordre de tri si même colonne
            self.sort_order = 1 - self.sort_order
        else:
            # Nouvelle colonne, ordre croissant par défaut
            self.sort_column = column_index
            self.sort_order = 0

        # Mettre à jour l'indicateur de tri
        self.update_sort_indicator()

        # Appliquer le tri
        self.apply_file_type_filters()

    def update_sort_indicator(self):
        """Mettre à jour l'indicateur de tri actuel"""
        columns = ["Type", "Nombre", "Taille totale", "Taille moyenne"]
        symbols = ["↑", "↓"]
        column_names = ["Type", "Nombre", "Taille", "Taille moy"]

        self.sort_indicator.setText(f"Tri: {column_names[self.sort_column]} {symbols[self.sort_order]}")

    def filter_file_types(self):
        """Filtrer les types de fichiers par extension"""
        self.apply_file_type_filters()

    def reset_file_type_filters(self):
        """Réinitialiser tous les filtres et tris"""
        self.file_type_filter.setCurrentIndex(0)  # "Tous les types"
        self.sort_column = 0  # Type
        self.sort_order = 0   # Croissant
        self.update_sort_indicator()
        self.apply_file_type_filters()

    def apply_file_type_filters(self):
        """Appliquer les filtres et tris actuels avec le tri par header"""
        if not hasattr(self, 'current_file_types_data') or not self.current_file_types_data:
            return

        # Filtrer par type de fichier
        filter_text = self.file_type_filter.currentText().strip().lower()
        filtered_data = {}

        if filter_text == "tous les types" or not filter_text:
            filtered_data = self.current_file_types_data.copy()
        else:
            for ext, data in self.current_file_types_data.items():
                if ext and ext.lower().startswith(filter_text):
                    filtered_data[ext] = data

        # Déterminer la clé de tri selon la colonne et l'ordre
        if self.sort_column == 0:  # Type de fichier
            if self.sort_order == 0:  # Croissant
                sort_key = lambda x: (x[0].lower() if x[0] else "", x[1]['size'])
            else:  # Décroissant
                sort_key = lambda x: ((-(ord(x[0][0].lower()) if x[0] and x[0][0].isalpha() else 999)), x[1]['size'])
        elif self.sort_column == 1:  # Nombre
            if self.sort_order == 0:  # Croissant
                sort_key = lambda x: x[1]['count']
            else:  # Décroissant
                sort_key = lambda x: -x[1]['count']
        elif self.sort_column == 2:  # Taille totale
            if self.sort_order == 0:  # Croissant
                sort_key = lambda x: x[1]['size']
            else:  # Décroissant
                sort_key = lambda x: -x[1]['size']
        else:  # Taille moyenne
            avg_size = lambda x: x[1]['size'] // max(x[1]['count'], 1)
            if self.sort_order == 0:  # Croissant
                sort_key = avg_size
            else:  # Décroissant
                sort_key = lambda x: -avg_size(x)

        # Trier les données
        sorted_data = sorted(filtered_data.items(), key=sort_key)

        # Vider le tree widget
        self.file_types_tree.clear()

        total_size = self.scan_results['total_size']

        # Ajouter les éléments triés
        for ext, data in sorted_data:
            item = QTreeWidgetItem([
                ext or "(sans extension)",
                f"{data['count']:,}",
                self.format_size(data['size']),
                self.format_size(data['size'] // max(data['count'], 1))
            ])

            # Colorier selon la taille
            percentage = (data['size'] / total_size) * 100
            if percentage > 10:
                item.setBackground(0, QColor(231, 76, 60, 50))  # Rouge clair
            elif percentage > 5:
                item.setBackground(0, QColor(241, 196, 15, 50))  # Jaune clair

            self.file_types_tree.addTopLevelItem(item)

        # Ajuster la largeur des colonnes
        for i in range(4):
            self.file_types_tree.resizeColumnToContents(i)

    def update_large_files_tab(self):
        """Mettre à jour l'onglet des gros fichiers"""
        self.large_files_tree.clear()
        self.extension_filter.clear()
        self.extension_filter.addItem("Tous")

        if not self.scan_results or not self.scan_results['large_files']:
            return

        # Collecter les extensions pour le filtre
        extensions = set()
        for file_path, size in self.scan_results['large_files']:
            ext = os.path.splitext(file_path)[1].lower()
            if ext:
                extensions.add(ext)
                if ext not in [self.extension_filter.itemText(i) for i in range(self.extension_filter.count())]:
                    self.extension_filter.addItem(ext)

        # Ajouter les fichiers
        for file_path, size in self.scan_results['large_files']:
            file_name = os.path.basename(file_path)
            item = QTreeWidgetItem([
                file_name,
                self.format_size(size),
                file_path
            ])
            self.large_files_tree.addTopLevelItem(item)

        # Ajuster la largeur des colonnes
        self.large_files_tree.resizeColumnToContents(0)
        self.large_files_tree.resizeColumnToContents(1)

    def filter_large_files(self):
        """Filtrer les gros fichiers par extension"""
        selected_ext = self.extension_filter.currentText()

        # Masquer/montrer les items selon le filtre
        for i in range(self.large_files_tree.topLevelItemCount()):
            item = self.large_files_tree.topLevelItem(i)
            file_path = item.text(2)
            ext = os.path.splitext(file_path)[1].lower()

            if selected_ext == "Tous" or ext == selected_ext.lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def update_directories_tab(self):
        """Mettre à jour l'onglet des dossiers"""
        self.directories_tree.clear()

        if not self.scan_results or not self.scan_results['directories']:
            return

        for dir_path, size in sorted(
            self.scan_results['directories'],
            key=lambda x: x[1],
            reverse=True
        )[:50]:  # Top 50
            # Calculer le niveau de profondeur
            level = dir_path.count(os.sep)

            item = QTreeWidgetItem([
                os.path.basename(dir_path) or dir_path,
                self.format_size(size),
                str(level)
            ])

            # Colorier selon la taille
            if size > 1024 * 1024 * 1024:  # > 1GB
                item.setBackground(0, QColor(231, 76, 60, 50))  # Rouge clair
            elif size > 100 * 1024 * 1024:  # > 100MB
                item.setBackground(0, QColor(241, 196, 15, 50))  # Jaune clair

            self.directories_tree.addTopLevelItem(item)

        # Ajuster la largeur des colonnes
        for i in range(3):
            self.directories_tree.resizeColumnToContents(i)

    def update_stats(self):
        """Mettre à jour les statistiques"""
        if self.scan_results:
            self.files_analyzed_label.setText(f"{self.scan_results['total_files']:,} fichiers analysés")
            self.scan_time_label.setText(self.format_size(self.scan_results['total_size']))
            self.scan_time_label.setText(self.scan_results['scan_time'])

        if self.smart_results:
            health = self.smart_results.get('health_status', 'Inconnu')
            color = "#2ecc71" if health in ["Bon", "Excellent"] else "#e74c3c"
            self.disk_health_label.setStyleSheet(self.get_stat_style().replace("#2c3e50", color))
            self.disk_health_label.setText(f"État: {health}")


    def run_smart_check(self):
        """Lancer le contrôle SMART"""
        if self.smart_thread and self.smart_thread.isRunning():
            return

        self.status_label.setText("Contrôle SMART en cours...")

        self.smart_thread = SmartControllerThread(self.current_disk)
        self.smart_thread.smart_data_received.connect(self.on_smart_completed)
        self.smart_thread.error_occurred.connect(self.on_smart_error)
        self.smart_thread.start()

    def on_smart_completed(self, smart_data):
        """Gérer la fin du contrôle SMART"""
        self.smart_results = smart_data

        # Mettre à jour l'onglet SMART avec les vraies données
        smart_info = f"""
📊 INFORMATIONS DU DISQUE
═══════════════════════════════════════

💽 Modèle : {smart_data.get('disk_model', 'Inconnu')}
🔑 Numéro de série : {smart_data.get('serial_number', 'Inconnu')}
🔧 Firmware : {smart_data.get('firmware_version', 'Inconnu')}
🔌 Interface : {smart_data.get('interface_type', 'Inconnu')}
📂 Périphérique : {smart_data.get('device_path', 'Inconnu')}

🏥 ÉTAT DE SANTÉ : {smart_data.get('health_status', 'Inconnu')}
🌡️ Température : {smart_data.get('temperature', 'Inconnu')}
⏱️ Heures de fonctionnement : {smart_data.get('power_on_hours', 'Inconnu')}
🔄 Cycles d'alimentation : {smart_data.get('power_cycles', 'Inconnu')}
"""

        # Ajouter les informations spécifiques NVMe si disponibles
        if smart_data.get('percent_used'):
            smart_info += f"📊 Usure NVMe : {smart_data.get('percent_used', 'Inconnu')}\n"
        if smart_data.get('data_written_gb'):
            smart_info += f"💾 Données écrites : {smart_data.get('data_written_gb', 'Inconnu')}\n"

        smart_info += f"""
⚠️ ERREURS MÉDIA : {smart_data.get('media_errors', '0')}

💡 RECOMMANDATIONS :
"""

        # Ajouter des recommandations selon l'état
        health = smart_data.get('health_status', '').lower()
        if 'bon' in health or 'excellent' in health:
            smart_info += "   • L'état du disque est bon\n   • Continuez vos sauvegardes régulières"
            if smart_data.get('data_source') == 'smartctl_real':
                smart_info += "\n   • ✅ Données SMART réelles obtenues via smartctl"
        elif 'attention' in health or 'avertissement' in health:
            smart_info += "   • Effectuez des sauvegardes immédiatement\n   • Envisagez le remplacement du disque"
            if smart_data.get('percent_used'):
                usage = smart_data.get('percent_used', '').replace('%', '')
                try:
                    if float(usage) > 80:
                        smart_info += "\n   • ⚠️ Usure élevée détectée"
                except:
                    pass
        else:
            smart_info += "   • Remplacez le disque rapidement\n   • Récupérez vos données importantes"

        # Ajouter un indicateur si smartctl n'est pas disponible
        if smart_data.get('data_source') != 'smartctl_real':
            smart_info += "\n\n❗ smartctl n'est pas installé - installez smartmontools pour des données SMART complètes"

        self.smart_info_text.setText(smart_info)

        # Mettre à jour le label d'état de santé
        health_status = smart_data.get('health_status', 'Inconnu')
        self.health_status_label.setText(health_status)

        # Colorer selon l'état
        if 'bon' in health_status.lower() or 'excellent' in health_status.lower():
            color = "#27ae60"
            icon = "✅"
        elif 'attention' in health_status.lower():
            color = "#f39c12"
            icon = "⚠️"
        else:
            color = "#e74c3c"
            icon = "❌"

        self.health_status_label.setStyleSheet(f"""
            color: {color};
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 16px;
            font-weight: 600;
            padding: 15px;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 8px;
            text-align: center;
            border: 2px solid {color};
        """)
        self.health_status_label.setText(f"{icon} {health_status}")

        self.status_label.setText("Contrôle SMART terminé")
        self.update_stats()
        self.smart_completed.emit(smart_data)

    def on_smart_error(self, error_message):
        """Gérer les erreurs du contrôle SMART"""
        self.status_label.setText(f"Erreur SMART: {error_message}")
        self.smart_info_text.setText(f"❌ Impossible d'obtenir les informations SMART\n\nErreur: {error_message}")
        self.error_occurred.emit(f"Erreur SMART: {error_message}")

    def export_results(self):
        """Exporter les résultats de l'analyse"""
        if not self.scan_results:
            self.status_label.setText("Aucun résultat à exporter")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter les résultats", f"disk_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Fichiers texte (*.txt);;Fichiers CSV (*.csv)"
        )

        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.export_to_csv(file_path)
                else:
                    self.export_to_txt(file_path)

                self.status_label.setText(f"Résultats exportés: {os.path.basename(file_path)}")
            except Exception as e:
                self.status_label.setText(f"Erreur lors de l'export: {str(e)}")

    def export_to_txt(self, file_path):
        """Exporter les résultats en format texte"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("RAPPORT D'ANALYSE DISQUE\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Disque analysé: {self.current_disk}\n")
            f.write(f"Date de l'analyse: {self.scan_results.get('scan_time', 'Inconnue')}\n")
            f.write(f"Type d'analyse: {self.scan_type_combo.currentText()}\n\n")

            f.write("STATISTIQUES GÉNÉRALES\n")
            f.write("-" * 30 + "\n")
            f.write(f"Fichiers analysés: {self.scan_results['total_files']:,}\n")
            f.write(f"Espace total: {self.format_size(self.scan_results['total_size'])}\n")
            f.write(f"Types de fichiers: {len(self.scan_results['file_types'])}\n\n")

            f.write("TYPES DE FICHIERS\n")
            f.write("-" * 30 + "\n")
            for ext, data in sorted(
                self.scan_results['file_types'].items(),
                key=lambda x: x[1]['size'],
                reverse=True
            ):
                f.write(f"{ext or '(sans extension)'}: {data['count']} fichiers, {self.format_size(data['size'])}\n")

            f.write("\nGROS FICHIERS\n")
            f.write("-" * 30 + "\n")
            for file_path, size in self.scan_results['large_files'][:20]:
                f.write(f"{self.format_size(size)} - {file_path}\n")

            if self.smart_results:
                f.write("\n\nINFORMATIONS SMART\n")
                f.write("=" * 30 + "\n")
                f.write(f"Modèle: {self.smart_results.get('disk_model', 'Inconnu')}\n")
                f.write(f"État de santé: {self.smart_results.get('health_status', 'Inconnu')}\n")
                f.write(f"Température: {self.smart_results.get('temperature', 'Inconnu')}\n")

    def export_to_csv(self, file_path):
        """Exporter les résultats en format CSV"""
        import csv

        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # En-tête
            writer.writerow(['Type', 'Chemin', 'Taille (octets)', 'Taille (format)'])

            # Types de fichiers
            for ext, data in self.scan_results['file_types'].items():
                writer.writerow(['Type', ext or '(sans extension)', data['size'], self.format_size(data['size'])])

            # Gros fichiers
            for file_path, size in self.scan_results['large_files']:
                writer.writerow(['Fichier', file_path, size, self.format_size(size)])

            # Dossiers
            for dir_path, size in self.scan_results['directories']:
                writer.writerow(['Dossier', dir_path, size, self.format_size(size)])

    def format_size(self, size_bytes):
        """Formatter une taille en octets vers une lisible"""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024.0 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f} {size_names[i]}"
