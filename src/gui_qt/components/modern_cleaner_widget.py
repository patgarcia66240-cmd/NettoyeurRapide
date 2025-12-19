"""
ModernCleanerWidget - Widget moderne de nettoyage inspiré de cleaner_page
"""

import os
import shutil
import tempfile
import glob
import time
from pathlib import Path
import threading
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QScrollArea, QSizePolicy,
                              QProgressBar, QTextEdit, QCheckBox, QGridLayout)
from PySide6.QtCore import Qt, Signal, QTimer, QThread, QSettings
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor

from .nav_button import NavButton
from .file_scanner_threads import FileScannerThread, FileCleanerThread
from .settings_dialog import SettingsDialog




class ModernCleanerWidget(QWidget):
    """Widget moderne de nettoyage avec design frameless et animations"""

    # Signaux
    scan_started = Signal()
    scan_completed = Signal()
    clean_started = Signal()
    clean_completed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scan_results = []
        self.is_scanning = False
        self.is_cleaning = False
        self.scanner_thread = None
        self.cleaner_thread = None

        # QSettings pour les paramètres (même organisation que settings_dialog)
        self.qsettings = QSettings("NettoyeurRapide", "CleaningSettings")

        # Paramètres de nettoyage - seront chargés depuis QSettings
        self.settings = {
            'safe_mode': True,
            'min_file_age_days': 30,
            'max_file_size_mb': 100,
            'delete_restore_points': False,
            'clear_recycle_bin': True,
        }

        # Charger les paramètres depuis QSettings
        self.load_settings_from_qsettings()

        self.settings_dialog = None
        self.setup_ui()
        self.setup_style()

    def _format_size(self, size_mb):
        """Formater la taille avec conversion MB/GB"""
        if size_mb >= 1000:
            size_gb = size_mb / 1024
            return f"{size_gb:.1f} GB"
        else:
            return f"{size_mb} MB"

    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header moderne
        self.setup_header(layout)

        # Barre d'outils
        self.setup_toolbar(layout)

        # Zone de contenu principale
        self.setup_content_area(layout)

        # Barre de progression
        self.setup_progress_bar(layout)

        # Zone de statistiques
        self.setup_stats_area(layout)

    def setup_header(self, parent_layout):
        """Configurer l'en-tête moderne avec ModernHeader"""
        # Utiliser le composant ModernHeader réutilisable
        from .modern_header import ModernHeader

        self.header = ModernHeader("🧹", "Nettoyage Intelligent")

        # Ajouter les boutons d'action rapides dans le header
        #self.btn_quick_scan = self.header.add_button("Analyse Rapide", "Lancer une analyse rapide des fichiers temporaires", "primary")
        #self.btn_deep_scan = self.header.add_button("Analyse Complète", "Lancer une analyse complète du système", "success")

        parent_layout.addWidget(self.header)

    def setup_toolbar(self, parent_layout):
        """Configurer la barre d'outils"""
        toolbar_frame = QFrame()
        toolbar_frame.setObjectName("modernToolbar")
        toolbar_frame.setFixedHeight(60)  # 10px de moins pour réduire l'espace
        toolbar_frame.setStyleSheet("""
            QFrame#modernToolbar {
                background: rgba(52, 73, 94, 0.1);
                border: none;
                border-bottom: 1px solid rgba(52, 73, 94, 0.2);
            }
        """)

        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(15, 10, 15, 10)  # Moins d'espace en haut
        toolbar_layout.setSpacing(10)

        # Boutons principaux avec NavButton
        self.btn_scan = NavButton("🔍 Lancer le Scan", self)
        self.btn_scan.set_primary()
        self.btn_scan.clicked.connect(self.start_scan)

        self.btn_select_all = NavButton("☑ Tout Sélectionner", self)
        self.btn_select_all.set_secondary()
        self.btn_select_all.clicked.connect(self.select_all)

        self.btn_deselect_all = NavButton("☐ Tout Désélectionner", self)
        self.btn_deselect_all.set_secondary()
        self.btn_deselect_all.clicked.connect(self.deselect_all)

        self.btn_clean = NavButton("🗑️ Nettoyer", self)
        self.btn_clean.set_accent()
        self.btn_clean.clicked.connect(self.start_cleaning)

        self.btn_settings = NavButton("⚙️", self)
        self.btn_settings.set_secondary()
        self.btn_settings.set_size("carre_xl")
        self.btn_settings.clicked.connect(self.show_settings)
        self.btn_settings.setToolTip("Paramètres de nettoyage")

        # Bouton scan aligné à gauche
        toolbar_layout.addWidget(self.btn_scan)

        # Espace flexible qui pousse les autres boutons à droite
        toolbar_layout.addStretch()

        # Group de boutons alignés à droite
        toolbar_layout.addWidget(self.btn_select_all)
        toolbar_layout.addWidget(self.btn_deselect_all)
        toolbar_layout.addWidget(self.btn_clean)
        toolbar_layout.addWidget(self.btn_settings)

        parent_layout.addWidget(toolbar_frame)

    def setup_content_area(self, parent_layout):
        """Configurer la zone de contenu principale"""
        content_frame = QFrame()
        content_frame.setObjectName("contentArea")
        content_frame.setStyleSheet("""
            QFrame#contentArea {
                background: rgba(44, 62, 80, 0.05);
                border: none;
            }
        """)

        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)

        # Zone des catégories (gauche)
        self.setup_categories_area(content_layout)

        # Zone des résultats (droite)
        self.setup_results_area(content_layout)

        parent_layout.addWidget(content_frame)

    def setup_categories_area(self, parent_layout):
        """Configurer la zone des catégories"""
        categories_frame = QFrame()
        categories_frame.setObjectName("categoriesFrame")
        categories_frame.setMaximumWidth(350)
        categories_frame.setStyleSheet("""
            QFrame#categoriesFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.95),
                    stop:1 rgba(245, 245, 245, 0.95));
                border: 1px solid rgba(189, 195, 199, 0.3);
                border-radius: 12px;
            }
        """)

        categories_layout = QVBoxLayout(categories_frame)
        categories_layout.setContentsMargins(15, 15, 15, 15)
        categories_layout.setSpacing(10)

        # Titre
        categories_title = QLabel("Catégories de Fichiers")
        categories_title.setStyleSheet("""
            color: #2c3e50;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 14px;
            font-weight: 600;
            background: transparent;
            padding-bottom: 5px;
            border-bottom: 2px solid rgba(52, 152, 219, 0.3);
            margin-bottom: 10px;
        """)
        categories_layout.addWidget(categories_title)

        # Zone scrollable pour les catégories
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
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

        self.categories_widget = QWidget()
        self.categories_layout = QVBoxLayout(self.categories_widget)
        self.categories_layout.setSpacing(8)

        # Ajouter des catégories par défaut
        self.add_default_categories()

        scroll_area.setWidget(self.categories_widget)
        categories_layout.addWidget(scroll_area)

        parent_layout.addWidget(categories_frame)

    def setup_results_area(self, parent_layout):
        """Configurer la zone des résultats"""
        results_frame = QFrame()
        results_frame.setObjectName("resultsFrame")
        results_frame.setStyleSheet("""
            QFrame#resultsFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.95),
                    stop:1 rgba(245, 245, 245, 0.95));
                border: 1px solid rgba(189, 195, 199, 0.3);
                border-radius: 12px;
            }
        """)

        results_layout = QVBoxLayout(results_frame)
        results_layout.setContentsMargins(15, 15, 15, 15)
        results_layout.setSpacing(10)

        # Titre
        results_title = QLabel("Résultats de l'Analyse")
        results_title.setStyleSheet("""
            color: #2c3e50;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 14px;
            font-weight: 600;
            background: transparent;
            padding-bottom: 5px;
            border-bottom: 2px solid rgba(231, 76, 60, 0.3);
            margin-bottom: 10px;
        """)
        results_layout.addWidget(results_title)

        # Zone des résultats
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet("""
            QTextEdit {
                background: rgba(236, 240, 241, 0.5);
                border: 1px solid rgba(189, 195, 199, 0.3);
                border-radius: 6px;
                color: #34495e;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                padding: 10px;
            }
            /* Scrollbar verticale moderne */
            QScrollBar:vertical {
                background: rgba(42, 42, 42, 0.279);
                width: 12px;
                border: none;
                border-radius: 6px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: rgba(64, 64, 64, 0.47);
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
        self.results_text.setPlaceholderText("Les résultats de l'analyse apparaîtront ici...")

        results_layout.addWidget(self.results_text)

        parent_layout.addWidget(results_frame)

    def setup_progress_bar(self, parent_layout):
        """Configurer la barre de progression"""
        progress_frame = QFrame()
        progress_frame.setObjectName("progressFrame")
        progress_frame.setFixedHeight(40)
        progress_frame.setStyleSheet("""
            QFrame#progressFrame {
                background: rgba(52, 73, 94, 0.05);
                border: none;
                border-top: 1px solid rgba(52, 73, 94, 0.1);
            }
        """)

        progress_layout = QHBoxLayout(progress_frame)
        progress_layout.setContentsMargins(20, 5, 20, 5)
        progress_layout.setSpacing(15)

        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("cleanerProgressBar")
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setFixedWidth(400)  # Largeur fixe
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setStyleSheet("""
            QProgressBar#cleanerProgressBar {
                background: rgba(189, 195, 199, 0.3);
                border: 1px solid rgba(52, 73, 94, 0.2);
                border-radius: 10px;
                text-align: center;
                color: #2c3e50;
                font-weight: 600;
                font-size: 12px;
            }
            QProgressBar#cleanerProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db,
                    stop:0.5 #2980b9,
                    stop:1 #3498db);
                border-radius: 9px;
            }
        """)

        # État
        self.status_label = QLabel("")
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

    def update_progress_with_text(self, value):
        """Mettre à jour la barre de progression avec un texte plus visible selon le pourcentage"""
        self.progress_bar.setValue(value)

        # Adapter la couleur du texte selon le pourcentage pour meilleure visibilité
        if value < 30:
            text_color = "#AFAFAF"  # Rouge pour le début
        elif value < 70:
            text_color = "#CFCFCF"  # Orange pour le milieu
        else:
            text_color = "#f3f7f4"  # Vert pour la fin

        # Mettre à jour le style avec des couleurs adaptatives
        self.progress_bar.setStyleSheet(f"""
            QProgressBar#cleanerProgressBar {{
                background: rgba(189, 195, 199, 0.3);
                border: 1px solid rgba(52, 73, 94, 0.2);
                border-radius: 10px;
                text-align: center;
                color: {text_color};
                font-weight: 700;
                font-size: 13px;
            }}
            QProgressBar#cleanerProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db,
                    stop:0.5 #2980b9,
                    stop:1 #3498db);
                border-radius: 9px;
            }}
        """)

    def setup_stats_area(self, parent_layout):
        """Configurer la zone de statistiques"""
        stats_frame = QFrame()
        stats_frame.setObjectName("statsFrame")
        stats_frame.setFixedHeight(60)
        stats_frame.setStyleSheet("""
            QFrame#statsFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(52, 152, 219, 0.1),
                    stop:0.5 rgba(41, 128, 185, 0.1),
                    stop:1 rgba(31, 97, 141, 0.1));
                border: none;
                border-top: 1px solid rgba(52, 73, 94, 0.2);
            }
        """)

        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(20, 0, 20, 0)
        stats_layout.setSpacing(30)

        # Statistiques
        self.files_found_label = QLabel("0 fichiers trouvés")
        self.files_found_label.setStyleSheet(self.get_stat_style())

        self.size_found_label = QLabel("0 MB")
        self.size_found_label.setStyleSheet(self.get_stat_style())

        self.categories_selected_label = QLabel("0 catégories sélectionnées")
        self.categories_selected_label.setStyleSheet(self.get_stat_style())

        stats_layout.addWidget(self.files_found_label)
        stats_layout.addWidget(self.size_found_label)
        stats_layout.addWidget(self.categories_selected_label)
        stats_layout.addStretch()

        # Initialiser le compteur de catégories sélectionnées après création du label
        self.update_categories_selected()

        parent_layout.addWidget(stats_frame)

    def get_stat_style(self):
        """Retourner le style pour les labels de statistiques"""
        return """
            color: white;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
            font-weight: 500;
            background: transparent;
            padding: 4px 15px;
        """

    def add_default_categories(self):
        """Ajouter les catégories de fichiers par défaut"""
        categories = [
            ("🗂️", "Fichiers Temporaires", True),
            ("📋", "Fichiers Cache", True),
            ("🗑️", "Corbeille", False),
            ("📦", "Logs Système", True),
            ("🧩", "Mises à Jour Windows", False),
            ("🌐", "Cache Navigateur", True),
            ("📱", "Fichiers de Récupération", False),
            ("🔄", "Points de Restauration", False),
        ]

        self.category_checkboxes = []
        for icon, name, checked in categories:
            checkbox = QCheckBox(f"{icon} {name}")
            checkbox.setChecked(checked)
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: #34495e;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 14px;
                    background: transparent;
                    padding: 4px;
                }
                QCheckBox::indicator {
                    width: 14px;
                    height: 14px;
                    border: 1px solid rgba(52, 152, 219, 0.6);
                    border-radius: 3px;
                    background: rgba(255, 255, 255, 0.8);
                }
                QCheckBox::indicator:checked {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #3498db,
                        stop:1 #2980b9);
                    border: 1px solid #2980b9;
                }
                QCheckBox::indicator:hover {
                    border: 1px solid #2980b9;
                }
            """)
            # Connecter le signal pour mettre à jour le compteur
            checkbox.stateChanged.connect(self.update_categories_selected)

            self.categories_layout.addWidget(checkbox)
            self.category_checkboxes.append(checkbox)

        self.categories_layout.addStretch()

    def setup_style(self):
        """Appliquer le style général"""
        self.setStyleSheet("""
            QPushButton#quickScanBtn, QPushButton#deepScanBtn {
                background: rgba(255, 255, 255, 0.2);
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 6px;
                padding: 8px 15px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton#quickScanBtn:hover, QPushButton#deepScanBtn:hover {
                background: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
        """)

        # Connecter les signaux
        #self.btn_quick_scan.clicked.connect(lambda: self.start_scan(quick=True))
        #self.btn_deep_scan.clicked.connect(lambda: self.start_scan(quick=False))

    def start_scan(self, quick=True):
        """Démarrer l'analyse réelle"""
        if self.is_scanning or self.is_cleaning:
            return

        self.is_scanning = True
        self.scan_started.emit()

        # Mettre à jour l'interface
        self.results_text.clear()
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        scan_type = "rapide" if quick else "complète"
        self.status_label.setText(f"Analyse {scan_type} en cours...")

        # Récupérer les catégories cochées
        categories = [cb.text() for cb in self.category_checkboxes if cb.isChecked()]

        if not categories:
            self.results_text.append("❌ Veuillez sélectionner au moins une catégorie à analyser")
            self.is_scanning = False
            self.progress_bar.setVisible(False)
            return

        # Créer et démarrer le thread de scanning
        self.scanner_thread = FileScannerThread(categories, quick)
        self.scanner_thread.progress_updated.connect(self.on_scan_progress)
        self.scanner_thread.scan_completed.connect(self.on_scan_completed)
        self.scanner_thread.start()

    def on_scan_progress(self, progress, category, files_count, size_mb):
        """Mettre à jour la progression du scan"""
        self.update_progress_with_text(progress)

        if files_count > 0:
            size_formatted = self._format_size(size_mb)
            self.results_text.append(f"✓ {category}: {files_count} fichiers, {size_formatted}")
        else:
            # Afficher même les catégories vides pendant l'analyse
            self.results_text.append(f"ℹ️ {category}: 0 fichier trouvé (catégorie vide)")

        scan_type = "rapide" if progress < 50 else "complète"
        self.status_label.setText(f"Analyse {scan_type} en cours... {progress}%")

    def on_scan_completed(self, results):
        """Appelé quand le scan est terminé"""
        self.scan_results = results
        self.complete_scan()

    def complete_scan(self):
        """Terminer l'analyse"""
        self.is_scanning = False
        self.update_progress_with_text(100)  # Vert pour le 100%
        self.status_label.setText("Analyse terminée")

        # Mettre à jour les statistiques
        total_files = sum(result[1] for result in self.scan_results)
        total_size = sum(result[2] for result in self.scan_results)
        size_formatted = self._format_size(total_size)
        self.files_found_label.setText(f"{total_files} fichiers trouvés")
        self.size_found_label.setText(size_formatted)

        self.results_text.append(f"\n🎉 Analyse terminée!")
        self.results_text.append(f"Total: {total_files} fichiers, {size_formatted} à nettoyer")

        self.scan_completed.emit()

        # Cacher la barre de progression après 2 secondes
        QTimer.singleShot(2000, lambda: self.progress_bar.setVisible(False))
        QTimer.singleShot(2000, lambda: self.status_label.setVisible(False))

    def select_all(self):
        """Sélectionner toutes les catégories"""
        for checkbox in self.category_checkboxes:
            checkbox.setChecked(True)
        self.update_categories_selected()

    def deselect_all(self):
        """Désélectionner toutes les catégories"""
        for checkbox in self.category_checkboxes:
            checkbox.setChecked(False)
        self.update_categories_selected()

    def update_categories_selected(self):
        """Mettre à jour le compteur de catégories sélectionnées"""
        count = sum(1 for cb in self.category_checkboxes if cb.isChecked())

        # Vérifier si le label existe avant de l'utiliser (évite l'erreur au démarrage)
        if hasattr(self, 'categories_selected_label'):
            self.categories_selected_label.setText(f"{count} catégories sélectionnées")

        # Remettre les fichiers trouvés à zéro quand on coche ou décoche une catégorie
        if hasattr(self, 'files_found_label'):
            self.files_found_label.setText("0 fichiers trouvés")

        # Vider les résultats de scan si on coche/décoche
        self.scan_results = {}

    def start_cleaning(self):
        """Démarrer le nettoyage"""
        if self.is_cleaning or self.is_scanning or not self.scan_results:
            return

        # Vérifier qu'au moins une catégorie est sélectionnée
        selected_categories = [cb for cb in self.category_checkboxes if cb.isChecked()]
        if not selected_categories:
            self.status_label.setText("Aucune catégorie sélectionnée")
            return

        self.is_cleaning = True
        self.clean_started.emit()

        # Afficher un avertissement de sécurité
        safe_mode = self.settings.get('safe_mode', True)
        mode_text = "SÉCURITÉ" if safe_mode else "RÉEL"
        self.results_text.append(f"\n🧹 Démarrage du nettoyage en mode {mode_text}...")
        if safe_mode:
            self.results_text.append("⚠️  Mode sécurité activé: uniquement les fichiers sûrs seront supprimés")
        else:
            self.results_text.append("🚨 Mode réel activé: SUPPRESSION PERMANENTE DES FICHIERS")

        self.results_text.append("📝 Liste des catégories sélectionnées:")
        for cb in selected_categories:
            self.results_text.append(f"   • {cb.text()}")

        self.results_text.append("\n" + "="*50)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Nettoyage en cours...")

        # Démarrer le nettoyage réel avec le thread
        category_names = [cb.text() for cb in selected_categories]
        self.cleaner_thread = FileCleanerThread(category_names, self.scan_results, self.settings)
        self.cleaner_thread.progress_updated.connect(self.on_cleaning_progress)
        self.cleaner_thread.cleaning_completed.connect(self.on_cleaning_completed)
        self.cleaner_thread.error_occurred.connect(self.on_cleaning_error)
        self.cleaner_thread.start()

    def on_cleaning_progress(self, progress, category, files_deleted, size_freed, files_details=""):
        """Mettre à jour la progression du nettoyage"""
        self.update_progress_with_text(progress)

        if files_deleted > 0:
            size_formatted = self._format_size(size_freed)
            message = f"✅ {category}: {files_deleted} fichiers supprimés, {size_formatted} libérés"
            if files_details:
                message += f"\n   📄 {files_details}"
            self.results_text.append(message)
        else:
            # Afficher même les catégories vides
            message = f"ℹ️ {category}: 0 fichier trouvé (catégorie vide)"
            self.results_text.append(message)

        self.status_label.setText(f"Nettoyage en cours... {progress}%")

    def on_cleaning_completed(self, results):
        """Appelé quand le nettoyage est terminé"""
        self.complete_cleaning_real(results)

    def on_cleaning_error(self, error_message):
        """Gérer les erreurs de nettoyage"""
        self.results_text.append(f"❌ Erreur: {error_message}")

    def complete_cleaning_real(self, results):
        """Terminer le nettoyage réel"""
        self.is_cleaning = False
        self.update_progress_with_text(100)
        self.status_label.setText("Nettoyage terminé")

        # Calculer l'espace libéré
        total_files = sum(result[1] for result in results)
        total_size = sum(result[2] for result in results)
        size_formatted = self._format_size(total_size)

        self.results_text.append(f"\n🎉 Nettoyage terminé avec succès!")
        self.results_text.append(f"📊 Résumé du nettoyage:")
        self.results_text.append(f"   • Fichiers supprimés: {total_files}")
        self.results_text.append(f"   • Espace libéré: {size_formatted}")
        self.results_text.append(f"   • Catégories traitées: {len(results)}")

        if self.settings['safe_mode']:
            self.results_text.append(f"\n⚠️  Le nettoyage a été effectué en mode sécurité")
            self.results_text.append(f"   Certains fichiers ont été préservés pour votre sécurité")
        else:
            self.results_text.append(f"\n🚨 Le nettoyage a été effectué en mode réel")
            self.results_text.append(f"   Les fichiers supprimés ne peuvent pas être restaurés")

        self.results_text.append(f"\n✅ Votre système est maintenant plus propre et plus rapide!")

        # Réinitialiser les résultats
        self.scan_results = []
        self.files_found_label.setText("0 fichiers trouvés")
        self.size_found_label.setText("0 MB")

        self.clean_completed.emit()

        # Cacher la barre de progression après 3 secondes
        QTimer.singleShot(3000, lambda: self.progress_bar.setVisible(False))

    def toggle_safe_mode(self):
        """Basculer entre mode sécurité et mode réel"""
        self.settings['safe_mode'] = not self.settings['safe_mode']
        mode = "SÉCURITÉ" if self.settings['safe_mode'] else "RÉEL"
        self.results_text.append(f"\n⚙️  Mode de nettoyage changé: {mode}")

        if self.settings['safe_mode']:
            self.results_text.append("✅ Mode sécurité activé - Protection maximale")
            self.results_text.append("   • Fichiers système protégés")
            self.results_text.append("   • Fichiers récents (<30j) préservés")
            self.results_text.append("   • Gros fichiers (>100MB) ignorés")
        else:
            self.results_text.append("🚨 Mode réel activé - Suppression permanente")
            self.results_text.append("   ⚠️  ATTENTION: Les suppressions sont irréversibles!")
            self.results_text.append("   • Tous les fichiers éligibles seront supprimés")

    def get_cleaning_mode(self):
        """Obtenir le mode de nettoyage actuel"""
        return "SÉCURITÉ" if self.settings.get('safe_mode', True) else "RÉEL"

    def show_settings(self):
        """Afficher la fenêtre de paramètres"""
        dialog = SettingsDialog(self.settings.copy(), self)
        dialog.settings_changed.connect(self.on_settings_changed)
        dialog.exec()

    def on_settings_changed(self, new_settings):
        """Gérer les changements de paramètres et les sauvegarder dans QSettings"""
        self.settings.update(new_settings)

        # Sauvegarder dans QSettings pour rester synchronisé
        try:
            self.qsettings.setValue('safe_mode', self.settings['safe_mode'])
            self.qsettings.setValue('min_file_age_days', self.settings['min_file_age_days'])
            self.qsettings.setValue('max_file_size_mb', self.settings['max_file_size_mb'])
            self.qsettings.setValue('delete_restore_points', self.settings['delete_restore_points'])
            self.qsettings.setValue('clear_recycle_bin', self.settings['clear_recycle_bin'])
            self.qsettings.sync()  # Forcer l'écriture immédiate
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des paramètres: {e}")

        # Afficher un message de confirmation
        self.status_label.setText("Paramètres sauvegardés")
        self.results_text.append(f"\n⚙️ Paramètres mis à jour:")
        self.results_text.append(f"   • Mode sécurité: {'Activé' if new_settings.get('safe_mode') else 'Désactivé'}")
        self.results_text.append(f"   • Âge minimum: {new_settings.get('min_file_age_days')} jours")
        self.results_text.append(f"   • Taille maximum: {new_settings.get('max_file_size_mb')} MB")
        self.results_text.append(f"   • Points de restauration: {'Suppression' if new_settings.get('delete_restore_points') else 'Préservés'}")
        self.results_text.append(f"   • Corbeille: {'Vidage' if new_settings.get('clear_recycle_bin') else 'Conservée'}")

    def get_settings(self):
        """Obtenir les paramètres actuels"""
        return self.settings.copy()

    def load_settings_from_qsettings(self):
        """Charger les paramètres depuis QSettings (même organisation que settings_dialog)"""
        try:
            # Charger depuis QSettings ou utiliser les valeurs par défaut
            self.settings['safe_mode'] = self.qsettings.value('safe_mode', True, type=bool)
            self.settings['min_file_age_days'] = self.qsettings.value('min_file_age_days', 30, type=int)
            self.settings['max_file_size_mb'] = self.qsettings.value('max_file_size_mb', 100, type=int)
            self.settings['delete_restore_points'] = self.qsettings.value('delete_restore_points', False, type=bool)
            self.settings['clear_recycle_bin'] = self.qsettings.value('clear_recycle_bin', True, type=bool)
        except Exception as e:
            print(f"Erreur lors du chargement des paramètres: {e}")

    def complete_cleaning(self):
        """Terminer le nettoyage"""
        self.is_cleaning = False
        self.update_progress_with_text(100)  # Vert pour le 100%
        self.status_label.setText("Nettoyage terminé")

        # Calculer l'espace libéré
        total_size = sum(result[2] for result in self.scan_results)
        size_formatted = self._format_size(total_size)
        self.results_text.append(f"\n🎉 Nettoyage terminé avec succès!")
        self.results_text.append(f"Espace libéré: {size_formatted}")
        self.results_text.append(f"Votre système est maintenant plus propre et plus rapide.")

        # Réinitialiser les résultats
        self.scan_results = []
        self.files_found_label.setText("0 fichiers trouvés")
        self.size_found_label.setText("0 MB")

        self.clean_completed.emit()

        # Cacher la barre de progression après 3 secondes
        QTimer.singleShot(3000, lambda: self.progress_bar.setVisible(False))

    def toggle_safe_mode(self):
        """Basculer entre mode sécurité et mode réel"""
        self.settings['safe_mode'] = not self.settings['safe_mode']
        mode = "SÉCURITÉ" if self.settings['safe_mode'] else "RÉEL"
        self.results_text.append(f"\n⚙️  Mode de nettoyage changé: {mode}")

        if self.settings['safe_mode']:
            self.results_text.append("✅ Mode sécurité activé - Protection maximale")
            self.results_text.append("   • Fichiers système protégés")
            self.results_text.append("   • Fichiers récents (<30j) préservés")
            self.results_text.append("   • Gros fichiers (>100MB) ignorés")
        else:
            self.results_text.append("🚨 Mode réel activé - Suppression permanente")
            self.results_text.append("   ⚠️  ATTENTION: Les suppressions sont irréversibles!")
            self.results_text.append("   • Tous les fichiers éligibles seront supprimés")

    def get_cleaning_mode(self):
        """Obtenir le mode de nettoyage actuel"""
        return "SÉCURITÉ" if self.settings.get('safe_mode', True) else "RÉEL"

    def show_settings(self):
        """Afficher la fenêtre de paramètres"""
        dialog = SettingsDialog(self.settings.copy(), self)
        dialog.settings_changed.connect(self.on_settings_changed)
        dialog.exec()

    def on_settings_changed(self, new_settings):
        """Gérer les changements de paramètres et les sauvegarder dans QSettings"""
        self.settings.update(new_settings)

        # Sauvegarder dans QSettings pour rester synchronisé
        try:
            self.qsettings.setValue('safe_mode', self.settings['safe_mode'])
            self.qsettings.setValue('min_file_age_days', self.settings['min_file_age_days'])
            self.qsettings.setValue('max_file_size_mb', self.settings['max_file_size_mb'])
            self.qsettings.setValue('delete_restore_points', self.settings['delete_restore_points'])
            self.qsettings.setValue('clear_recycle_bin', self.settings['clear_recycle_bin'])
            self.qsettings.sync()  # Forcer l'écriture immédiate
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des paramètres: {e}")

        # Afficher un message de confirmation
        self.status_label.setText("Paramètres sauvegardés")
        self.results_text.append(f"\n⚙️ Paramètres mis à jour:")
        self.results_text.append(f"   • Mode sécurité: {'Activé' if new_settings.get('safe_mode') else 'Désactivé'}")
        self.results_text.append(f"   • Âge minimum: {new_settings.get('min_file_age_days')} jours")
        self.results_text.append(f"   • Taille maximum: {new_settings.get('max_file_size_mb')} MB")
        self.results_text.append(f"   • Points de restauration: {'Suppression' if new_settings.get('delete_restore_points') else 'Préservés'}")
        self.results_text.append(f"   • Corbeille: {'Vidage' if new_settings.get('clear_recycle_bin') else 'Conservée'}")

    def get_settings(self):
        """Obtenir les paramètres actuels"""
        return self.settings.copy()