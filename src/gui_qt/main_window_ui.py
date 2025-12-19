#!/usr/bin/env python3
"""
Classe MainWindow qui utilise Ui_MainWindow générée par Qt Designer
"""

import sys
import os

# Ajouter le répertoire src au chemin Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (QApplication, QMainWindow,
                              QLabel, QHBoxLayout, QVBoxLayout, QWidget, QPushButton)
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QFont, QCursor

# Import de la classe UI générée
from gui_qt.ui_mainform import Ui_MainWindow

# Core imports
from core.temp_scanner import TempScanner
from core.cleaner import Cleaner
from core.disk_analyzer import DiskAnalyzer
from core.startup_manager import StartupManager
from core.thread_manager import ThreadManager, WorkerType

# Widgets imports
from gui_qt.components.modern_cleaner_widget import ModernCleanerWidget
from gui_qt.components.disk_analysis_widget import DiskAnalysisWidget
from gui_qt.components.windows_widget import WindowsWidget
from gui_qt.components.startup_widget import StartupWidget


class MainWindowUI(QMainWindow):
    """
    Classe principale qui utilise Ui_MainWindow générée par Qt Designer
    """

    def __init__(self):
        super().__init__()

        # Configuration frameless
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowModality(Qt.ApplicationModal)

        # Variables pour le déplacement de la fenêtre
        self._drag_pos = QPoint()

        # Initialiser l'interface utilisateur générée
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Ajuster les marges pour que le header soit au niveau du bord supérieur
        self.centralwidget = self.findChild(QWidget, "centralwidget")
        if self.centralwidget:
            # Enlever la marge supérieure du layout principal
            main_layout = self.centralwidget.layout()
            if main_layout:
                main_layout.setContentsMargins(0, 0, 3, 0)  # gauche, haut, droite, bas

        # Ajuster les marges du widget parent du header
        widget_2 = self.ui.header.parent()
        if widget_2 and widget_2.layout():
            widget_2.layout().setContentsMargins(4, 0, 4, 0)  # Enlever la marge supérieure

        # Services principaux
        self.scanner = TempScanner()
        self.cleaner = Cleaner()
        self.disk_analyzer = DiskAnalyzer()
        self.startup_manager = StartupManager()

        # Gestionnaire de threads pour les opérations longues
        self.thread_manager = ThreadManager()

        # Configuration de l'interface
        self._setup_ui()
        self._setup_title_bar()
        self._setup_connections()
        self._setup_initial_state()
        self._apply_frameless_style()

        # Timer pour les mises à jour périodiques
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_status)
        self.update_timer.start(1000)  # Mise à jour chaque seconde

    def _setup_ui(self):
        """Configuration supplémentaire de l'interface"""
        # Définir le titre de la fenêtre
        self.setWindowTitle("NettoyeurRapide Pro")

        # Configurer les boutons de navigation
        self.ui.btnNavClean.setCheckable(True)
        self.ui.btnNavDisk.setCheckable(True)
        self.ui.btnNavStart.setCheckable(True)
        self.ui.btnNavWin.setCheckable(True)

        # Bouton de navigation actif par défaut
        self.ui.btnNavClean.setChecked(True)

        # Style pour les boutons cochés
        self._update_nav_button_style(self.ui.btnNavClean, True)
        self._update_nav_button_style(self.ui.btnNavDisk, False)
        self._update_nav_button_style(self.ui.btnNavStart, False)
        self._update_nav_button_style(self.ui.btnNavWin, False)

    def _setup_title_bar(self):
        """Configurer les contrôles de fenêtre dans le header existant"""
        # Masquer la barre de menu et la barre de statut par défaut
        self.ui.menubar.hide()
        self.ui.statusbar.hide()

        # Utiliser le widget header existant
        self.title_bar = self.ui.header
        self.title_bar.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
        self.title_bar.setFixedHeight(32)  # Conserver la hauteur du header

        # Créer un layout horizontal pour le header
        if not self.title_bar.layout():
            header_layout = QHBoxLayout(self.title_bar)
        else:
            header_layout = self.title_bar.layout()

        header_layout.setContentsMargins(10, 0, 10, 0)
        header_layout.setSpacing(10)

        # Logo et titre
        self.title_label = QLabel("🧹 NettoyeurRapide Pro")
        self.title_label.setStyleSheet("""
            color: #ecf0f1;
            font-size: 14px;
            font-weight: bold;
            background: transparent;
            border: none;
                                       
        """)
        header_layout.addWidget(self.title_label)

        # Espace flexible
        header_layout.addStretch()

        # Boutons de contrôle de fenêtre (style compact et moderne)
        self.minimize_btn = self._create_header_control_button("−", "#3498db")
        self.maximize_btn = self._create_header_control_button("□", "#2ecc71")
        self.close_btn = self._create_header_control_button("✕", "#e74c3c")

        header_layout.addWidget(self.minimize_btn)
        header_layout.addWidget(self.maximize_btn)
        header_layout.addWidget(self.close_btn)

        # Style du header
        self.title_bar.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(44, 62, 80, 255), stop:1 rgba(52, 73, 94, 255));
                border: none;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)

        # Maintenant configurer les infos système séparément
        self._setup_system_info()

        # Ajouter les widgets modernes au stack widget
        self._setup_modern_cleaner()
        self._setup_disk_analysis()
        self._setup_windows_widget()
        self._setup_startup_widget()

        # Configurer les autres composants
        self._setup_connections()
        self._setup_initial_state()

        # Déboguer la structure après tout être configuré
        QTimer.singleShot(1500, self._debug_stackwidget_structure)

        # Corriger l'alignement des boutons de navigation après l'initialisation complète
        #self._fix_navigation_layout()

    def _setup_modern_cleaner(self):
        """Configurer et ajouter le ModernCleanerWidget au stack widget"""
        from gui_qt.components.modern_cleaner_widget import ModernCleanerWidget

        # Créer le widget moderne de nettoyage
        self.modern_cleaner_widget = ModernCleanerWidget()

        # Remplacer le cleaner_page existant dans le stack widget
        current_index = self.ui.stackedWidget.indexOf(self.ui.cleaner_page)
        if current_index >= 0:
            self.ui.stackedWidget.removeWidget(self.ui.cleaner_page)
            self.ui.stackedWidget.insertWidget(current_index, self.modern_cleaner_widget)
        else:
            # Si pour une raison quelconque cleaner_page n'est pas trouvé, ajouter à la fin
            self.ui.stackedWidget.addWidget(self.modern_cleaner_widget)

        # Connecter les signaux du widget moderne
        self.modern_cleaner_widget.scan_started.connect(
            lambda: self._update_status_message("Analyse en cours...", "info")
        )
        self.modern_cleaner_widget.scan_completed.connect(
            lambda: self._show_scan_complete_message()
        )
        self.modern_cleaner_widget.clean_started.connect(
            lambda: self._update_status_message("Nettoyage en cours...", "warning")
        )
        self.modern_cleaner_widget.clean_completed.connect(
            lambda: self._update_status_message("Nettoyage terminé avec succès", "success")
        )

    def _setup_disk_analysis(self):
        """Configurer et ajouter le DiskAnalysisWidget au stack widget"""
        from gui_qt.components.disk_analysis_widget import DiskAnalysisWidget

        # Créer le widget d'analyse disque
        self.disk_analysis_widget = DiskAnalysisWidget()

        # Remplacer le disk_page existant dans le stack widget
        current_index = self.ui.stackedWidget.indexOf(self.ui.disk_page)
        if current_index >= 0:
            self.ui.stackedWidget.removeWidget(self.ui.disk_page)
            self.ui.stackedWidget.insertWidget(current_index, self.disk_analysis_widget)
        else:
            # Si pour une raison quelconque disk_page n'est pas trouvé, ajouter à la position 1
            self.ui.stackedWidget.insertWidget(1, self.disk_analysis_widget)

        # Connecter les signaux du widget d'analyse disque
        self.disk_analysis_widget.scan_started.connect(
            lambda: self._update_status_message("Analyse disque en cours...", "info")
        )
        self.disk_analysis_widget.scan_completed.connect(
            lambda: self._update_status_message("Analyse disque terminée", "success")
        )
        self.disk_analysis_widget.smart_completed.connect(
            lambda: self._update_status_message("Contrôle SMART terminé", "success")
        )
        self.disk_analysis_widget.error_occurred.connect(
            lambda: self._update_status_message("Erreur lors de l'analyse disque", "error")
        )

    def _setup_windows_widget(self):
        """Configurer et intégrer le WindowsWidget dans win_page"""
        from gui_qt.components.windows_widget import WindowsWidget

        # Créer le widget Windows
        self.windows_widget = WindowsWidget()

        # Debug: afficher l'état avant l'intégration
        print(f"Intégration du WindowsWidget dans win_page...")

        # Créer un layout pour la win_page si elle n'en a pas
        if self.ui.win_page.layout() is None:
            from PySide6.QtWidgets import QVBoxLayout
            layout = QVBoxLayout(self.ui.win_page)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            print("Création d'un layout pour win_page")
        else:
            print("win_page a déjà un layout")

        # Intégrer le WindowsWidget dans win_page
        self.ui.win_page.layout().addWidget(self.windows_widget)

        # Debug: vérifier l'intégration
        print(f"WindowsWidget intégré dans win_page")
        print(f"win_page contient maintenant {self.ui.win_page.layout().count()} widgets")

        # Connecter les signaux du widget Windows
        self.windows_widget.status_updated.connect(
            lambda message, msg_type: self._update_status_message(message, msg_type)
        )
        self.windows_widget.operation_started.connect(
            lambda operation: self._update_status_message(f"Début: {operation}...", "info")
        )
        self.windows_widget.operation_completed.connect(
            lambda operation: self._update_status_message(f"Terminé: {operation}", "success")
        )

    def _setup_startup_widget(self):
        """Configurer et intégrer le StartupWidget dans start_page"""
        from gui_qt.components.startup_widget import StartupWidget

        # Créer le widget de démarrage
        self.startup_widget = StartupWidget()

        # Debug: afficher l'état avant l'intégration
        print(f"Intégration du StartupWidget dans start_page...")

        # Créer un layout pour la start_page si elle n'en a pas
        if self.ui.start_page.layout() is None:
            from PySide6.QtWidgets import QVBoxLayout
            layout = QVBoxLayout(self.ui.start_page)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            print("Création d'un layout pour start_page")
        else:
            print("start_page a déjà un layout")

        # Intégrer le StartupWidget dans start_page
        self.ui.start_page.layout().addWidget(self.startup_widget)

        # Debug: vérifier l'intégration
        print(f"StartupWidget intégré dans start_page")
        print(f"start_page contient maintenant {self.ui.start_page.layout().count()} widgets")

        # Connecter les signaux du widget de démarrage
        self.startup_widget.status.connect(
            lambda message, msg_type: self._update_status_message(message, msg_type)
        )

    def _create_header_control_button(self, text, color):
        """Créer un bouton de contrôle pour le header"""
        btn = QPushButton(text)
        btn.setFixedSize(28, 22)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: #ecf0f1;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color};
                color: white;
            }}
            QPushButton:pressed {{
                background-color: {color};
                color: white;
            }}
        """)
        return btn

    def _setup_system_info(self):
        """Configurer les informations système dans le widget prévu"""
        # Utiliser le SystemInfoWidget autonome pour remplacer le contenu de systeminfoswidget
        from gui_qt.components.system_info_widget import SystemInfoWidget

        # Créer le widget autonome d'informations système
        self.system_info_widget = SystemInfoWidget()
        self.system_info_widget.set_update_interval(2)  # Mise à jour toutes les 2 secondes

        # Remplacer le contenu du systeminfoswidget
        system_layout = self.ui.systeminfoswidget.layout()
        if system_layout is None:
            # Créer un layout vertical s'il n'existe pas
            system_layout = QVBoxLayout(self.ui.systeminfoswidget)

        # Vider le layout existant
        while system_layout.count():
            child = system_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Ajouter le nouveau widget
        system_layout.addWidget(self.system_info_widget)

        # Garder les références pour compatibilité avec le code existant
        self.system_info_labels = {
            'cpu': self.system_info_widget.cpu_info,
            'memory': self.system_info_widget.memory_info,
            'disk': self.system_info_widget.disk_info
        }

        # Ajouter le widget d'état du disque en dessous dans le parent
        from gui_qt.components.disk_status_widget import DiskStatusWidget

        # Créer le widget de disque
        self.disk_status_widget = DiskStatusWidget()

        # Ajouter au layout parent (dessous de systeminfoswidget)
        # systeminfoswidget a une hauteur fixe, le disque sera ajouté en dessous
        parent_layout = self.ui.statsinfoswidget.layout()
        if parent_layout is None:
            # Créer un layout vertical s'il n'existe pas
            parent_layout = QVBoxLayout(self.ui.statsinfoswidget)

        parent_layout.addWidget(self.disk_status_widget)

        # Style du widget système
        self.ui.systeminfoswidget.setStyleSheet("""
            QWidget {
                background: transparent;            }
        """)
        self.ui.statsinfoswidget.setStyleSheet("""
            QWidget {
                background: transparent;            }
        """)

    def _create_system_info_labels(self, layout):
        """Créer les informations système avec SystemInfoWidget autonome"""
        try:
            from gui_qt.components.system_info_widget import SystemInfoWidget

            # Créer le widget autonome d'informations système
            self.system_info_widget = SystemInfoWidget()

            # Configurer le widget si nécessaire
            self.system_info_widget.set_update_interval(2)  # Mise à jour toutes les 2 secondes
            self.system_info_widget.set_critical_thresholds(cpu_threshold=80, memory_threshold=85, disk_threshold=90)

            # Ajouter au layout
            layout.addWidget(self.system_info_widget)

            # Garder les références pour compatibilité avec le code existant
            self.system_info_labels = {
                'cpu': self.system_info_widget.cpu_info,
                'memory': self.system_info_widget.memory_info,
                'disk': self.system_info_widget.disk_info
            }

        except Exception as e:
            # En cas d'erreur, créer un widget simple
            from gui_qt.components.system_info_label import SystemInfoLabel
            error_info = SystemInfoLabel("⚠", "Infos système", f"Erreur: {str(e)}")
            error_info.set_highlight(False)
            layout.addWidget(error_info)

            # Créer des références vides pour éviter les erreurs
            self.system_info_labels = {}

    def _apply_frameless_style(self):
        """Appliquer le style frameless à la fenêtre"""
        # Container principal avec coins arrondis
        central_widget = self.centralWidget()
        central_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2c3e50, stop:1 #34495e);
                border: 2px solid #1a252f;
                border-radius: 15px;
            }
        """)

        # Améliorer le conteneur de navigation avec un fond stylisé
        if hasattr(self.ui, 'widget_10'):
            self.ui.widget_10.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(30, 41, 59, 0.95),
                        stop:1 rgba(51, 65, 85, 0.95));
                    border: 1px solid rgba(148, 163, 184, 0.2);
                    border-radius: 16px;
                    margin: 8px;
                    padding: 12px 8px;
                }
            """)

        # Améliorer aussi le widget parent si nécessaire
        if hasattr(self.ui, 'widget'):
            self.ui.widget.setStyleSheet("""
                QWidget {
                    background: transparent;
                    border: none;
                }
            """)

        # Rendre la fenêtre draggable depuis le header
        self.title_bar.mousePressEvent = self._title_bar_mouse_press
        self.title_bar.mouseMoveEvent = self._title_bar_mouse_move

        # Connecter les boutons de contrôle
        self.minimize_btn.clicked.connect(self.showMinimized)
        self.maximize_btn.clicked.connect(self._toggle_maximize)
        self.close_btn.clicked.connect(self.close)

        # Mettre à jour les informations système périodiquement
        self._update_system_info()

    def _setup_connections(self):
        """Configurer les connexions des signaux"""
        # Créer et ajouter le bouton Windows

        # Navigation entre les pages (Windows est dans win_page à l'index 0)
        if hasattr(self.ui, 'btnNavWin'):
            self.ui.btnNavWin.clicked.connect(lambda: self._navigate_to_page(0))
        else:
            print("ERREUR: btnNavWin n'existe pas!")

        # Mettre à jour les autres boutons pour naviguer vers les bons index
        # Ordre: 0=Windows, 1=Nettoyage, 2=Analyse Disque, 3=Démarrage
        self.ui.btnNavClean.clicked.connect(lambda: self._navigate_to_page(1))
        self.ui.btnNavDisk.clicked.connect(lambda: self._navigate_to_page(2))
        self.ui.btnNavStart.clicked.connect(lambda: self._navigate_to_page(3))

        # Ajout des messages de débogage
        self.ui.btnNavClean.clicked.connect(lambda: print("Navigation vers Nettoyage (index 1)"))
        self.ui.btnNavDisk.clicked.connect(lambda: print("Navigation vers Analyse Disque (index 2)"))
        self.ui.btnNavStart.clicked.connect(lambda: print("Navigation vers Démarrage (index 3)"))

        # Boutons d'action de la page de nettoyage
        """ self.ui.btnScan.clicked.connect(self._on_scan_clicked)
        self.ui.btnSelectAll.clicked.connect(self._on_select_all_clicked)
        self.ui.btnUnSelectAll.clicked.connect(self._on_unselect_all_clicked)
         self.ui.btnClean.clicked.connect(self._on_clean_clicked)"""

    def _setup_initial_state(self):
        """Configurer l'état initial de l'interface"""
        # Afficher la première page (nettoyage)
        self.ui.widget_9.setStyleSheet("background: transparent; border: none;")
        self.ui.stackedWidget.setStyleSheet("""
            background: transparent;
            border: none;
            margin-top: 0px;  /* Réduction de l'espace en haut */
            padding-top: 0px;
        """)

        self.ui.stackedWidget.setCurrentIndex(1)  # Index 1 = Nettoyage
        self.ui.lblTitreNav.setText("Nettoyage")
        self.ui.lblTitreNav.setStyleSheet("color: #ecf0f1; font-size: 16px; font-weight: light; border: none;")

        # Message de statut initial
        self.ui.lblStatus.setText("Prêt")
        self.ui.lblStatus1.setText("")
        self.ui.lblStatus2.setText("")
        self.ui.lblStatus.setStyleSheet("border: none; color: #3498db; font-size: 11px;")
        self.ui.lblStatus1.setStyleSheet("border: none; color: #ecf0f1; font-size: 11px;")
        self.ui.lblStatus2.setStyleSheet("border: none; color: #ecf0f1; font-size: 11px;")

    def _navigate_to_page(self, page_index):
        """Naviguer vers une page spécifique"""
        # Mettre à jour le stack widget
        self.ui.stackedWidget.setCurrentIndex(page_index)


        # Mettre à jour le titre (nouvel ordre: 0=Windows, 1=Nettoyage, 2=Analyse Disque, 3=Démarrage)
        titles = ["Windows", "Nettoyage", "Analyse Disque", "Démarrage"]
        if page_index < len(titles):
            self.ui.lblTitreNav.setText(titles[page_index])

        # Mettre à jour l'état des boutons de navigation
        # Index 0 = Windows, Index 1 = Nettoyage, Index 2 = Analyse Disque, Index 3 = Démarrage
        self.ui.btnNavClean.setChecked(page_index == 1)
        self.ui.btnNavDisk.setChecked(page_index == 2)
        self.ui.btnNavStart.setChecked(page_index == 3)
        if hasattr(self.ui, 'btnNavWin'):
            self.ui.btnNavWin.setChecked(page_index == 0)

        # Mettre à jour le style des boutons
        self._update_nav_button_style(self.ui.btnNavClean, page_index == 1)
        self._update_nav_button_style(self.ui.btnNavDisk, page_index == 2)
        self._update_nav_button_style(self.ui.btnNavStart, page_index == 3)
        if hasattr(self.ui, 'btnNavWin'):
            self._update_nav_button_style(self.ui.btnNavWin, page_index == 0)

    def _navigate_to_page_debug(self, page_index, page_name):
        """Naviguer vers une page spécifique avec débogage"""
        print(f"Navigation demandée vers {page_name} (index {page_index})")
        self._navigate_to_page(page_index)

    def _update_nav_button_style(self, button, is_checked):
        """Mettre à jour le style d'un bouton de navigation avec dégradé moderne"""
        if is_checked:
            # Bouton actif avec dégradé bleu vif
            button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4A90E2,
                        stop:0.5 #357ABD,
                        stop:1 #2968A3);
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 12px 16px;
                    font-weight: bold;
                    font-size: 13px;
                    text-align: center;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #5BA0F2,
                        stop:0.5 #458ACD,
                        stop:1 #3978B3);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #3978B3,
                        stop:0.5 #2968A3,
                        stop:1 #1E5893);
                }
            """)
        else:
            # Bouton inactif avec dégradé subtil
            button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #6B7280,
                        stop:0.5 #4B5563,
                        stop:1 #374151);
                    color: #E5E7EB;
                    border: 1px solid #4B5563;
                    border-radius: 12px;
                    padding: 12px 16px;
                    font-weight: 600;
                    font-size: 13px;
                    text-align: center;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #7B8288,
                        stop:0.5 #5B6573,
                        stop:1 #475160);
                    color: white;
                    border: 1px solid #5B6573;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #5B6268,
                        stop:0.3 #3B4253,
                        stop:1 #2B3143);
                }
            """)

    def _clean_completed(self):
        """Appelé lorsque le nettoyage est terminé"""
        self.ui.lblStatus.setText("Nettoyage terminé")
        self.ui.lblStatus1.setText("Espace libéré: 2.3 GB")
        self.ui.lblStatus2.setText("")
        self.ui.btnClean.setEnabled(True)

        from gui_qt.components.message_box import MessageBoxPersonnalise
        MessageBoxPersonnalise.show_information(self, "Succès",
                                              "Nettoyage terminé avec succès!\nEspace libéré: 2.3 GB")

    def _update_status(self):
        """Mettre à jour les informations de statut"""
        # Mettre à jour les informations système
        self._update_system_info()

    def _update_status_message(self, message, status_type="info"):
        """Mettre à jour le message de statut avec style"""
        self.ui.lblStatus.setText(message)

        # Appliquer le style selon le type
        if status_type == "success":
            self.ui.lblStatus.setStyleSheet("""
                border: 1px solid #27ae60;
                color: #2ecc71;
                background: rgba(39, 174, 96, 0.1);
                font-size: 11px;
                border-radius: 4px;
                padding: 2px 8px;
            """)
        elif status_type == "warning":
            self.ui.lblStatus.setStyleSheet("""
                border: 1px solid #f39c12;
                color: #f1c40f;
                background: rgba(243, 156, 18, 0.1);
                font-size: 11px;
                border-radius: 4px;
                padding: 2px 8px;
            """)
        elif status_type == "error":
            self.ui.lblStatus.setStyleSheet("""
                border: 1px solid #c0392b;
                color: #e74c3c;
                background: rgba(192, 57, 43, 0.1);
                font-size: 11px;
                border-radius: 4px;
                padding: 2px 8px;
            """)
        elif status_type == "info":  # info
            self.ui.lblStatus.setStyleSheet("""
                border: 1px solid #3498db;
                color: #3498db;
                background: rgba(52, 152, 219, 0.1);
                font-size: 11px;
                border-radius: 4px;
                padding: 2px 8px;
            """)
        else:  # idle
            self.ui.lblStatus.setStyleSheet("""
                border: none;
                color: #3498db;
                background: transparent;
                font-size: 11px;
                padding: 2px 8px;
            """)

    def _update_system_info(self):
        """Mettre à jour les informations système dans le header"""
        # Le SystemInfoWidget autonome gère les mises à jour automatiquement
        # Cette méthode est conservée pour compatibilité mais ne fait rien
        pass

    def _title_bar_mouse_press(self, event):
        """Gérer le clic de souris sur la barre de titre (header gauche)"""
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
            self.title_bar.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))

    def _title_bar_mouse_move(self, event):
        """Gérer le mouvement de souris pour déplacer la fenêtre"""
        if event.buttons() == Qt.LeftButton and not self._drag_pos.isNull():
            diff = event.globalPosition().toPoint() - self._drag_pos
            new_pos = self.pos() + diff
            self.move(new_pos)
            self._drag_pos = event.globalPosition().toPoint()

    def _toggle_maximize(self):
        """Basculer entre mode maximisé et normal"""
        if self.isMaximized():
            self.showNormal()
            self.maximize_btn.setText("□")
        else:
            self.showMaximized()
            self.maximize_btn.setText("❐")

    def mouseReleaseEvent(self, event):
        """Gérer le relâchement de la souris"""
        self.title_bar.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
        super().mouseReleaseEvent(event)

    def changeEvent(self, event):
        """Gérer les changements d'état de la fenêtre"""
        if event.type() == event.Type.WindowStateChange:
            if self.isMaximized():
                self.maximize_btn.setText("❐")
                self.centralWidget().setStyleSheet("""
                    QWidget {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #2c3e50, stop:1 #34495e);
                        border: 2px solid #1a252f;
                        border-radius: 0px;
                    }
                """)
                # Style pour le header maximisé
                self.title_bar.setStyleSheet("""
                    QWidget {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 rgba(44, 62, 80, 255), stop:1 rgba(52, 73, 94, 255));
                        border: none;
                        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    }
                """)
            else:
                self.maximize_btn.setText("□")
                self.centralWidget().setStyleSheet("""
                    QWidget {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #2c3e50, stop:1 #34495e);
                        border: 2px solid #1a252f;
                        border-radius: 15px;
                    }
                """)
                # Style pour le header normal
                self.title_bar.setStyleSheet("""
                    QWidget {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 rgba(44, 62, 80, 255), stop:1 rgba(52, 73, 94, 255));
                        border: none;
                        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    }
                """)
        if event.type() == event.Type.WindowStateChange:
            if self.isMaximized():
                self.maximize_btn.setText("❐")
                self.centralWidget().setStyleSheet("""
                    QWidget {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #2c3e50, stop:1 #34495e);
                        border: 2px solid #1a252f;
                        border-radius: 0px;
                    }
                """)
                # Style pour le header maximisé
                self.title_bar.setStyleSheet("""
                    QWidget {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 rgba(44, 62, 80, 255), stop:1 rgba(52, 73, 94, 255));
                        border: none;
                        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    }
                """)
            else:
                self.maximize_btn.setText("□")
                self.centralWidget().setStyleSheet("""
                    QWidget {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #2c3e50, stop:1 #34495e);
                        border: 2px solid #1a252f;
                        border-radius: 15px;
                    }
                """)
                # Style pour le header normal
                self.title_bar.setStyleSheet("""
                    QWidget {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 rgba(44, 62, 80, 255), stop:1 rgba(52, 73, 94, 255));
                        border: none;
                        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    }
                """)
        super().changeEvent(event)

    def closeEvent(self, event):
        """Gérer la fermeture de l'application"""
        # Arrêter tous les workers actifs
        self.thread_manager.stop_all_workers()

        # Arrêter le timer
        if self.update_timer.isActive():
            self.update_timer.stop()

        # Arrêter les mises à jour du widget de disque
        if hasattr(self, 'disk_status_widget'):
            self.disk_status_widget.stop_updates()

        # Arrêter les mises à jour du widget d'infos système
        if hasattr(self, 'system_info_widget'):
            self.system_info_widget.stop_updates()

        # Confirmer la fermeture
        from gui_qt.components.message_box import MessageBoxPersonnalise
        reply = MessageBoxPersonnalise.show_question(self, "Quitter",
                                                   "Êtes-vous sûr de vouloir quitter NettoyeurRapide?",
                                                   ["Oui", "Non"])

        if reply == "Oui":
            event.accept()
        else:
            event.ignore()

    def _create_windows_nav_button(self):
        """Créer et ajouter le bouton de navigation Windows"""
        from PySide6.QtWidgets import QPushButton
        from PySide6.QtCore import QSize
        from PySide6.QtGui import QFont

        print("Création du bouton Windows...")

        # Créer le bouton Windows
        self.btnNavWin = QPushButton("🪟 Windows")
        self.btnNavWin.setObjectName("btnNavWin")
        self.btnNavWin.setMinimumSize(QSize(0, 70))

        # Configurer la police
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        self.btnNavWin.setFont(font)

        print(f"Bouton Windows créé: {self.btnNavWin.objectName()}")

        # Style initial inactif (sera mis à jour par _update_nav_button_style)
        self.btnNavWin.setChecked(False)

        # Ajouter le bouton au layout de navigation existant (après les autres boutons)
        if hasattr(self.ui, 'widget_10') and hasattr(self.ui.widget_10, 'verticalLayout_5'):
            print("Bouton ajouté à widget_10.verticalLayout_5")
            self.ui.widget_10.verticalLayout_5.addWidget(self.btnNavWin)
        else:
            # Fallback: chercher le layout de navigation et ajouter le bouton
            print("Recherche du layout de navigation...")
            found = False
            for i in range(self.ui.widget.layout().count()):
                widget = self.ui.widget.layout().itemAt(i).widget()
                if hasattr(widget, 'verticalLayout_5'):
                    print(f"Bouton ajouté à verticalLayout_5 du widget {i}")
                    widget.verticalLayout_5.addWidget(self.btnNavWin)
                    found = True
                    break
            if not found:
                print("ATTENTION: Layout de navigation non trouvé, le bouton Windows n'est pas ajouté!")

    def _debug_stackwidget_structure(self):
        """Déboguer la structure du stackedWidget"""
        print("\n=== STRUCTURE DU STACKEDWIDGET ===")
        print(f"Nombre total de widgets: {self.ui.stackedWidget.count()}")

        for i in range(self.ui.stackedWidget.count()):
            widget = self.ui.stackedWidget.widget(i)
            #print(f"Index {i}: {widget.__class__.__name__}")
            

        print("================================\n")

    def _show_scan_complete_message(self):
        """Afficher 'Analyse terminée' pendant 2 secondes puis 'Prêt'"""
        # Afficher le message de scan terminé
        self._update_status_message("Analyse terminée", "success")
        # Après 2 secondes, afficher 'Prêt'
        QTimer.singleShot(2000, lambda: self._update_status_message("Prêt", "idle"))

    def _fix_navigation_layout(self):
        """Améliorer l'espacement et l'alignement des boutons de navigation"""
        # Obtenir le layout vertical qui contient les boutons de navigation
        nav_layout = self.ui.widget_10.layout()
        if nav_layout and hasattr(nav_layout, 'objectName') and nav_layout.objectName() == "verticalLayout_5":
            # Marges optimales pour les boutons avec dégradé
            nav_layout.setContentsMargins(8, 8, 8, 8)  # Marges uniformes

            # Espacement entre les boutons pour un effet aéré
            nav_layout.setSpacing(8)

        # S'assurer que le style du widget_10 est bien appliqué
        if hasattr(self.ui, 'widget_10'):
            current_style = self.ui.widget_10.styleSheet() or ""
            if "margin-top: -10px;" in current_style:
                # Remplacer l'ancienne marge négative
                current_style = current_style.replace("margin-top: -10px;", "")
            self.ui.widget_10.setStyleSheet(current_style)


# Point d'entrée pour tester cette classe spécifiquement
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("NettoyeurRapide")
    app.setOrganizationName("NettoyeurRapide")

    window = MainWindowUI()
    window.show()

    sys.exit(app.exec())