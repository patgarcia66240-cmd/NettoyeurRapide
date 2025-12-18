#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gestion des programmes au démarrage (Windows)
- Lecture Run / Run-
- Lecture dossiers Startup
- Activation / désactivation réelle (registre + fichiers)
- Suppression avec sauvegarde JSON
- Export JSON
- Filtre de recherche
"""

import os
import json
import winreg
import subprocess
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QProgressBar,
    QLineEdit, QFileDialog, QMessageBox, QPlainTextEdit, QSizePolicy
)
from .modern_header import ModernHeader
from PySide6.QtCore import Qt, QTimer, Signal, QThread, QEvent
from PySide6.QtGui import QBrush, QColor

# Plus besoin du delegate - le CSS gère le hover et la sélection

# =====================================================================
#  THREAD : scan des éléments de démarrage
# =====================================================================

class StartupScannerThread(QThread):
    progress = Signal(int, str)
    completed = Signal(list)
    error = Signal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            items = self.scan_startup_items()
            self.progress.emit(100, "Analyse terminée")
            self.completed.emit(items)
        except Exception as e:
            self.error.emit(str(e))

    # -----------------------------------------------------------------

    def scan_startup_items(self):
        """Scan complet des programmes au démarrage."""
        items = []

        # Registres : Run (activé) / Run- (désactivé)
        registry_defs = [
            # HKCU Run / Run-
            (winreg.HKEY_CURRENT_USER,
             r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
             "HKCU", True,
             r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run-"),
            (winreg.HKEY_CURRENT_USER,
             r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run-",
             "HKCU", False,
             r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),

            # HKLM Run / Run-
            (winreg.HKEY_LOCAL_MACHINE,
             r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
             "HKLM", True,
             r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run-"),
            (winreg.HKEY_LOCAL_MACHINE,
             r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run-",
             "HKLM", False,
             r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),

            # HKCU RunOnce (exécuté une seule fois au prochain démarrage)
            (winreg.HKEY_CURRENT_USER,
             r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce",
             "HKCU", True,
             None),  # RunOnce n'a pas d'équivalent Run-

            # HKLM RunOnce (exécuté une seule fois au prochain démarrage)
            (winreg.HKEY_LOCAL_MACHINE,
             r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce",
             "HKLM", True,
             None),

            # Wow6432Node (applications 32-bit sur système 64-bit)
            (winreg.HKEY_LOCAL_MACHINE,
             r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Run",
             "HKLM32", True,
             r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Run-"),
            (winreg.HKEY_LOCAL_MACHINE,
             r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Run-",
             "HKLM32", False,
             r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Run"),

            # HKCU Policies (programmes imposés par les stratégies)
            (winreg.HKEY_CURRENT_USER,
             r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run",
             "HKCU Policy", True,
             None),

            # HKLM Policies (programmes imposés par les stratégies système)
            (winreg.HKEY_LOCAL_MACHINE,
             r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run",
             "HKLM Policy", True,
             None),
        ]

        # Dossiers Startup
        user_startup = os.path.expanduser(
            "~/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"
        )
        sys_startup = os.path.join(
            os.environ.get("PROGRAMDATA", "C:/ProgramData"),
            "Microsoft/Windows/Start Menu/Programs/Startup"
        )

        folder_defs = [
            (user_startup, False, "Startup utilisateur"),
            (sys_startup, True, "Startup système"),
        ]

        total_steps = len(registry_defs) + len(folder_defs)
        step = 0

        # --- Lecture registre ---
        for hive, path, hive_label, enabled, opposite_path in registry_defs:
            step += 1
            self.progress.emit(
                int(step / total_steps * 100),
                f"Lecture registre {hive_label} ({'Run' if enabled else 'Run-'})..."
            )
            try:
                with winreg.OpenKey(hive, path) as key:
                    count = winreg.QueryInfoKey(key)[1]
                    for i in range(count):
                        name, value, _ = winreg.EnumValue(key, i)
                        if not value:
                            continue

                        # Filtrer les éléments inutiles
                        name_lower = name.lower()
                        value_lower = value.lower()

                        # Ignorer les éléments liés au bureau
                        if ('desktop' in name_lower or 'desktop' in value_lower or
                            'bureau' in name_lower or 'bureau' in value_lower):
                            continue

                        # Ignorer les éléments vides ou système inutiles
                        if name_lower.strip() == '' or value_lower.strip() == '':
                            continue

                        # Vérifier l'état réel du programme
                        real_enabled = self._check_real_program_status(name, value, enabled)

                        item_data = {
                            "name": name,
                            "path": value,
                            "enabled": real_enabled,
                            "source": f"{hive_label} {os.path.basename(path)}",
                            "source_type": "registry",
                            "hive": hive_label,
                            "reg_path": path,
                        }
                        # Ajouter reg_opposite_path seulement s'il existe (pas pour RunOnce ou Policies)
                        if opposite_path:
                            item_data["reg_opposite_path"] = opposite_path
                        items.append(item_data)
            except OSError:
                # clé absente => ignorer
                continue

        # --- Lecture dossiers Startup ---
        for folder, is_system, label in folder_defs:
            step += 1
            self.progress.emit(
                int(step / total_steps * 100),
                f"Lecture {label}..."
            )
            if not os.path.isdir(folder):
                continue

            for fname in os.listdir(folder):
                full = os.path.join(folder, fname)
                if not os.path.isfile(full):
                    continue

                # Filtrer les éléments inutiles
                fname_lower = fname.lower()
                if ('desktop' in fname_lower or 'bureau' in fname_lower):
                    continue

                # Gestion du .disabled
                if fname.endswith(".disabled"):
                    enabled = False
                    base_name = fname[:-9]  # remove ".disabled"
                else:
                    enabled = True
                    base_name = fname

                items.append({
                    "name": os.path.splitext(base_name)[0],
                    "path": full,
                    "enabled": enabled,
                    "source": label,
                    "source_type": "folder",
                    "folder_path": folder,
                    "is_system": is_system,
                })

        return items

    def _check_real_program_status(self, name: str, path: str, registry_enabled: bool) -> bool:
        """Vérifier l'état réel d'un programme au démarrage"""
        try:
            # Si le registre dit déjà désactivé, c'est probablement correct
            if not registry_enabled:
                return False

            # Vérifications spécifiques pour certains programmes connus
            name_lower = name.lower()
            path_lower = path.lower()

            # OneDrive : vérification spéciale
            if 'onedrive' in name_lower or 'onedrive' in path_lower:
                return self._check_onedrive_status()

            # Microsoft Teams : vérification spéciale
            if 'teams' in name_lower or 'teams' in path_lower:
                return self._check_teams_status()

            # Pour les autres programmes, vérification basique
            return self._check_generic_startup_status(path)

        except Exception:
            # En cas d'erreur, revenir à l'état du registre
            return registry_enabled

    def _check_onedrive_status(self) -> bool:
        """Vérifier si OneDrive est réellement activé au démarrage"""
        try:
            # Vérifier la clé spécifique de démarrage approuvé
            approved_key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"

            for hive in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
                try:
                    with winreg.OpenKey(hive, approved_key_path) as key:
                        # Chercher OneDrive dans cette clé
                        count = winreg.QueryInfoKey(key)[1]
                        for i in range(count):
                            name, value, _ = winreg.EnumValue(key, i)
                            if 'onedrive' in name.lower():
                                # La valeur est généralement un binaire indicant l'état
                                # Si présent ici, c'est généralement désactivé (0x02 = désactivé)
                                return False
                except OSError:
                    continue

            # Si pas trouvé dans StartupApproved, vérifier s'il est dans Run normal
            run_key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            for hive in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
                try:
                    with winreg.OpenKey(hive, run_key_path) as key:
                        count = winreg.QueryInfoKey(key)[1]
                        for i in range(count):
                            name, value, _ = winreg.EnumValue(key, i)
                            if 'onedrive' in name.lower():
                                # Si trouvé dans Run mais pas dans StartupApproved = activé
                                return True
                except OSError:
                    continue

            return False

        except Exception:
            return False  # Par défaut, considérer comme désactivé si détection échoue

    def _check_teams_status(self) -> bool:
        """Vérifier si Microsoft Teams est réellement activé au démarrage"""
        try:
            # Même logique que OneDrive
            approved_key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"

            for hive in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
                try:
                    with winreg.OpenKey(hive, approved_key_path) as key:
                        count = winreg.QueryInfoKey(key)[1]
                        for i in range(count):
                            name, value, _ = winreg.EnumValue(key, i)
                            if 'teams' in name.lower():
                                return False
                except OSError:
                    continue

            return True

        except Exception:
            return True

    def _check_generic_startup_status(self, path: str) -> bool:
        """Vérification générique pour les programmes"""
        try:
            # Vérifier si le fichier existe et n'est pas désactivé
            if os.path.isfile(path) and not path.endswith('.disabled'):
                return True
            return False
        except Exception:
            return True


# =====================================================================
#  WIDGET PRINCIPAL
# =====================================================================

class StartupWidget(QWidget):
    """
    Widget de gestion des programmes au démarrage (Windows)
    """

    status = Signal(str, str)  # message, type ('success', 'error', 'info', ...)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = []   # liste de dict
        self.thread = None
        self.backup_path = os.path.join(
            os.path.expanduser("~"), "startup_manager_backup.json"
        )
        self.setup_ui()
        QTimer.singleShot(500, self.load_items)

    # -----------------------------------------------------------------

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(0)

        # Header moderne avec le composant réutilisable
        header = ModernHeader("⚡", "Nettoyeur Rapide Pro")

        # Ajouter les boutons directement dans le header
        self.btn_refresh = header.add_button("🔄 Actualiser", "Actualiser la liste des programmes", "primary")
        self.btn_export = header.add_button("💾 Export JSON", "Exporter la liste en format JSON", "success")

        layout.addWidget(header)

        # Barre de recherche (les boutons sont maintenant dans le header)
        search_toolbar = QHBoxLayout()

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filtrer (nom, créateur, source)...")

        search_toolbar.addWidget(QLabel("🔍"))
        search_toolbar.addWidget(self.search_edit)
        search_toolbar.addStretch()

        layout.addLayout(search_toolbar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Nom", "Créateur", "Source", "Action", "Supprimer"
        ])
        self.table.setMouseTracking(True)
        self.table.viewport().setMouseTracking(True)
        self.table.viewport().installEventFilter(self)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Nom
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Créateur
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Source
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # Action - largeur fixe
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # Supprimer - largeur fixe
        # Définir les largeurs fixes après avoir appliqué le mode
        header.resizeSection(3, 100)  # Largeur pour la colonne Action
        header.resizeSection(4, 90)   # Largeur pour la colonne Supprimer

        # Configuration de la hauteur des lignes
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.verticalHeader().setMinimumSectionSize(36)

        # Activer la sélection de ligne entière
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)

        # Style de la table
        self.table.setStyleSheet("""
    QTableWidget {
        background-color: #ffffff;
        gridline-color: #cccccc;
        border: none;
        border-radius: 8px;
        outline: none;
        font-size: 12px;
        font-family: 'Segoe UI', Arial, sans-serif;
        color: #000000;
        selection-background-color: #2196f3;
        selection-color: #ffffff;
    }

    QHeaderView::section {
        background-color: #2c3e50;
        color: #ffffff;
        font-weight: bold;
        padding: 6px 8px;
        border: 1px solid #1a252f;
        font-size: 11px;
        letter-spacing: 0.3px;
    }

    /* Style pour toute la ligne */
    QTableWidget::item {
        border: none;
        padding: 4px 2px;
        border-radius: 4px;
        margin: 1px;
        background-color: #ffffff;
        color: #000000;
    }

    /* Style pour les lignes au survol */
    QTableWidget::item:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #e3f2fd, stop:1 #bbdefb);
        border: none;
        color: #000000;
    }

    /* Style pour la sélection (même couleur que le hover) */
    QTableWidget::item:selected {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #e3f2fd, stop:1 #bbdefb);
        border: none;
        color: #000000;
    }

    /* Style pour les lignes sélectionnées mais non actives */
    QTableWidget::item:selected:!active {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #e3f2fd, stop:1 #bbdefb);
        border: none;
        color: #000000;
    }

    /* Style pour le focus (même couleur que hover) */
    QTableWidget::item:focus {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #e3f2fd, stop:1 #bbdefb);
        border: none;
        color: #000000;
    }

    /* Style pour les conteneurs de widgets pour qu'ils n'interfèrent pas avec le hover */
    QTableWidget QWidget {
        background-color: transparent;
        border: none;
    }

    /* Forcer le hover sur les lignes avec des widgets */
    QTableWidget > QScrollBar,
    QTableWidget > QScrollBar::handle,
    QTableWidget > QScrollBar::add-line,
    QTableWidget > QScrollBar::sub-line {
        background: #e0e0e0;
    }

    /* S'assurer que le hover fonctionne même quand il y a des widgets */
    QTableWidget::item:hover,
    QTableWidget::item:selected,
    QTableWidget::item:focus {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #e3f2fd, stop:1 #bbdefb);
    }

    /* Boutons spécifiques au survol de la ligne */
    QTableWidget::item:hover QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #81c784, stop:1 #a5d6a7);
        border: 2px solid #66bb6a;
    }

    QTableWidget::item:selected QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #81c784, stop:1 #a5d6a7);
        border: 2px solid #66bb6a;
    }

    QScrollBar:vertical {
        background: #e0e0e0;
        width: 14px;
        border-radius: 7px;
        border: 1px solid #bdbdbd;
    }
    QScrollBar::handle:vertical {
        background: #757575;
        border-radius: 7px;
        min-height: 20px;
        border: 1px solid #616161;
    }
    QScrollBar::handle:vertical:hover {
        background: #616161;
    }
""")

        layout.addWidget(self.table)

        # Progress
        self.progress_frame = QFrame()
        self.progress_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #3498db;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        pf_layout = QVBoxLayout(self.progress_frame)
        self.progress_label = QLabel("Prêt")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_bar = QProgressBar()
        pf_layout.addWidget(self.progress_label)
        pf_layout.addWidget(self.progress_bar)
        layout.addWidget(self.progress_frame)
        self.progress_frame.setVisible(False)

        # Connexions
        self.btn_refresh.clicked.connect(self.load_items)
        self.btn_export.clicked.connect(self.export_json)
        self.search_edit.textChanged.connect(self.apply_filter)

    # =================================================================
    #  CHARGEMENT / PROGRESSION
    # =================================================================

    def get_creator_info(self, program_name: str, program_path: str) -> str:
        """Détecte le créateur/éditeur d'un programme"""
        program_name_lower = program_name.lower()
        program_path_lower = program_path.lower()

        # Proton (détection prioritaire pour éviter conflit avec Microsoft Azure)
        proton_keywords = [
            'proton', 'protonvpn', 'proton mail', 'proton drive'
        ]
        if any(keyword in program_name_lower for keyword in proton_keywords):
            return "Proton"

        # Microsoft
        microsoft_keywords = [
            'microsoft', 'onedrive', 'office', 'teams', 'outlook', 'word',
            'excel', 'powerpoint', 'skype', 'edge', 'windows', 'defender',
            'azure', 'visual studio', 'vscode', 'mspaint'
        ]
        if any(keyword in program_name_lower or keyword in program_path_lower for keyword in microsoft_keywords):
            return "Microsoft"

        # Google
        google_keywords = [
            'google', 'chrome', 'drive', 'gmail', 'earth', 'docs',
            'photos', 'backup and sync', 'meet'
        ]
        if any(keyword in program_name_lower or keyword in program_path_lower for keyword in google_keywords):
            return "Google"

        # Apple
        apple_keywords = [
            'apple', 'icloud', 'itunes', 'bonjour', 'safari', 'quicktime'
        ]
        if any(keyword in program_name_lower or keyword in program_path_lower for keyword in apple_keywords):
            return "Apple"

        # Adobe
        adobe_keywords = [
            'adobe', 'acrobat', 'reader', 'photoshop', 'illustrator',
            'creative cloud', 'dreamweaver', 'flash'
        ]
        if any(keyword in program_name_lower or keyword in program_path_lower for keyword in adobe_keywords):
            return "Adobe"

        # Mozilla
        mozilla_keywords = [
            'mozilla', 'firefox', 'thunderbird'
        ]
        if any(keyword in program_name_lower or keyword in program_path_lower for keyword in mozilla_keywords):
            return "Mozilla"

        # Valve
        valve_keywords = [
            'steam', 'valve'
        ]
        if any(keyword in program_name_lower or keyword in program_path_lower for keyword in valve_keywords):
            return "Valve"

        # Epic Games
        epic_keywords = [
            'epic', 'epic games', 'unreal'
        ]
        if any(keyword in program_name_lower or keyword in program_path_lower for keyword in epic_keywords):
            return "Epic Games"

        # WhatsApp
        whatsapp_keywords = [
            'whatsapp'
        ]
        if any(keyword in program_name_lower or keyword in program_path_lower for keyword in whatsapp_keywords):
            return "Meta"  # WhatsApp appartient à Meta

        # Discord
        discord_keywords = [
            'discord'
        ]
        if any(keyword in program_name_lower or keyword in program_path_lower for keyword in discord_keywords):
            return "Discord"

        # Xbox
        xbox_keywords = [
            'xbox', 'xbox game bar'
        ]
        if any(keyword in program_name_lower or keyword in program_path_lower for keyword in xbox_keywords):
            return "Microsoft"  # Xbox appartient à Microsoft

        # Spotify
        spotify_keywords = [
            'spotify'
        ]
        if any(keyword in program_name_lower or keyword in program_path_lower for keyword in spotify_keywords):
            return "Spotify"

        # Dropbox
        dropbox_keywords = [
            'dropbox'
        ]
        if any(keyword in program_name_lower or keyword in program_path_lower for keyword in dropbox_keywords):
            return "Dropbox"

        # Zoom
        zoom_keywords = [
            'zoom'
        ]
        if any(keyword in program_name_lower or keyword in program_path_lower for keyword in zoom_keywords):
            return "Zoom"

        # NVIDIA
        nvidia_keywords = [
            'nvidia', 'geforce', 'shadowplay'
        ]
        if any(keyword in program_name_lower or keyword in program_path_lower for keyword in nvidia_keywords):
            return "NVIDIA"

        # AMD
        amd_keywords = [
            'amd', 'radeon', 'adrenalin'
        ]
        if any(keyword in program_name_lower or keyword in program_path_lower for keyword in amd_keywords):
            return "AMD"

        # Intel
        intel_keywords = [
            'intel', 'quick sync'
        ]
        if any(keyword in program_name_lower or keyword in program_path_lower for keyword in intel_keywords):
            return "Intel"

        # Dell
        dell_keywords = [
            'dell', 'dell supportassist'
        ]
        if any(keyword in program_name_lower or keyword in program_path_lower for keyword in dell_keywords):
            return "Dell"

        # HP
        hp_keywords = [
            'hp', 'hewlett packard', 'support assistant'
        ]
        if any(keyword in program_name_lower or keyword in program_path_lower for keyword in hp_keywords):
            return "HP"

        
        # Try to get from file properties
        try:
            if os.path.isfile(program_path):
                # Look for company name in executable properties
                import subprocess
                result = subprocess.run(['powershell', '-Command',
                    f'(Get-Item "{program_path}").VersionInfo.CompanyName'],
                    capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    company = result.stdout.strip()
                    if company and company != '':
                        return company
        except Exception:
            pass

        # Try to extract from path
        if 'program files' in program_path_lower:
            if 'microsoft' in program_path_lower:
                return "Microsoft"
            elif 'google' in program_path_lower:
                return "Google"
            elif 'adobe' in program_path_lower:
                return "Adobe"

        # Default fallback
        return "Inconnu"

    def load_items(self):
        """Lancer le thread de scan."""
        if self.thread and self.thread.isRunning():
            return

        self.table.setEnabled(False)
        self.progress_frame.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Analyse en cours...")

        self.thread = StartupScannerThread()
        self.thread.progress.connect(self.update_progress)
        self.thread.completed.connect(self.on_items_loaded)
        self.thread.error.connect(self.on_error)
        self.thread.start()

    def update_progress(self, value, msg):
        self.progress_bar.setValue(value)
        self.progress_label.setText(msg)

    def on_items_loaded(self, items):
        self.items = items
        self.populate_table()
        self.progress_frame.setVisible(False)
        self.table.setEnabled(True)

    def on_error(self, msg):
        self.progress_frame.setVisible(False)
        self.table.setEnabled(True)
        self.status.emit(f"Erreur: {msg}", "error")

    # =================================================================
    #  AFFICHAGE TABLE
    # =================================================================

    def populate_table(self):
        self.table.setRowCount(len(self.items))

        for row, item in enumerate(self.items):
            # --- NOM ---
            name_item = QTableWidgetItem(item["name"])
            font = name_item.font()
            font.setBold(True)
            name_item.setFont(font)
            name_item.setForeground(QBrush(QColor("#000000")))
            self.table.setItem(row, 0, name_item)

            # --- CRÉATEUR ---
            creator = self.get_creator_info(item["name"], item["path"])
            creator_item = QTableWidgetItem(creator)
            creator_item.setForeground(QBrush(QColor("#000000")))
            self.table.setItem(row, 1, creator_item)

            # --- SOURCE ---
            source_item = QTableWidgetItem(item["source"])
            color = QColor("#006666")
            if "HKCU" in item["source"]:
                color = QColor("#0066cc")
            elif "HKLM" in item["source"]:
                color = QColor("#9932cc")

            source_item.setForeground(QBrush(color))
            self.table.setItem(row, 2, source_item)

            # --- BOUTON ACTIVER / DÉSACTIVER ---
            # Vérifier si l'élément peut être désactivé
            can_toggle = item.get("source_type") == "registry" and "reg_opposite_path" in item

            if can_toggle:
                btn_toggle = QPushButton("Marche" if item["enabled"] else "Stop")
                btn_toggle.setStyleSheet(self.button_style(item["enabled"]))
                btn_toggle.setFixedHeight(28)
                btn_toggle.clicked.connect(lambda checked=False, r=row: self.toggle_item_state(r))
            else:
                # Éléments non-désactivables (RunOnce, Policies, etc.)
                btn_toggle = QPushButton("Non modifiable")
                btn_toggle.setStyleSheet("""
                    QPushButton {
                        background-color: #6c757d;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-weight: bold;
                        font-size: 10px;
                    }
                    QPushButton:hover {
                        background-color: #5a6268;
                    }
                """)
                btn_toggle.setEnabled(False)
                btn_toggle.setFixedHeight(28)

            # Créer un widget conteneur pour que le bouton prenne toute la cellule
            btn_container = QWidget()
            btn_container.setStyleSheet("background-color: transparent;")
            btn_layout = QVBoxLayout(btn_container)
            btn_layout.setContentsMargins(1, 1, 1, 1)  # Marges minimales
            btn_layout.setSpacing(0)

            # Le bouton prend toute la largeur disponible
            btn_toggle.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn_layout.addWidget(btn_toggle)

            self.table.setCellWidget(row, 3, btn_container)

            # --- BOUTON SUPPRIMER ---
            btn_del = QPushButton("Supprimer")
            btn_del.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-weight: bold;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            btn_del.setFixedHeight(28)
            btn_del.clicked.connect(lambda checked=False, r=row: self.delete_item(r))

            # Créer un widget conteneur pour que le bouton prenne toute la cellule
            del_container = QWidget()
            del_container.setStyleSheet("background-color: transparent;")
            del_layout = QVBoxLayout(del_container)
            del_layout.setContentsMargins(1, 1, 1, 1)  # Marges minimales
            del_layout.setSpacing(0)

            # Le bouton prend toute la largeur disponible
            btn_del.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            del_layout.addWidget(btn_del)

            self.table.setCellWidget(row, 4, del_container)

        # Hauteur des lignes (augmentée pour bien loger les boutons)
        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, 40)

        # réapplique le filtre courant
        self.apply_filter(self.search_edit.text())

    # =================================================================
    #  STYLES BOUTONS
    # =================================================================

    def button_style(self, enabled: bool) -> str:
        if enabled:
            # Marche - dégradé vert
            return """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #4caf50, stop:1 #81c784);
                    color: white;
                    border: 1px solid #388e3c;
                    border-radius: 4px;
                    padding: 5px 10px;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #66bb6a, stop:1 #a5d6a7);
                    border: 1px solid #4caf50;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #388e3c, stop:1 #66bb6a);
                }
            """
        else:
            # Stop - dégradé rouge/orange
            return """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #f44336, stop:1 #ff9800);
                    color: white;
                    border: 1px solid #d32f2f;
                    border-radius: 4px;
                    padding: 5px 10px;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #ef5350, stop:1 #ffa726);
                    border: 1px solid #f44336;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #d32f2f, stop:1 #f57c00);
                }
            """

    # =================================================================
    #  ACTIVATION / DÉSACTIVATION
    # =================================================================

    def toggle_item_state(self, row: int):
        if row < 0 or row >= len(self.items):
            return

        item = self.items[row]

        try:
            if item.get("source_type") == "registry":
                self._toggle_registry_item(item)
            elif item.get("source_type") == "folder":
                self._toggle_folder_item(item)
            else:
                raise RuntimeError("Type de source inconnu")

            # Mise à jour UI - récupérer le bouton depuis le conteneur
            btn_container = self.table.cellWidget(row, 3)
            if btn_container and btn_container.layout():
                btn = btn_container.layout().itemAt(0).widget()
                if isinstance(btn, QPushButton):
                    btn.setText("Marche" if item["enabled"] else "Stop")
                    btn.setStyleSheet(self.button_style(item["enabled"]))

            self.status.emit(
                f"{item['name']} {'mis en marche' if item['enabled'] else 'arrêté'}",
                "success"
            )

        except Exception as e:
            self.status.emit(f"Erreur lors du changement d'état: {e}", "error")

    # ---------- registre ----------

    def _get_hive_handle(self, hive_label: str):
        if hive_label == "HKCU":
            return winreg.HKEY_CURRENT_USER
        if hive_label == "HKLM":
            return winreg.HKEY_LOCAL_MACHINE
        raise ValueError(f"Hive inconnu: {hive_label}")

    def _toggle_registry_item(self, item: dict):
        hive = self._get_hive_handle(item["hive"])
        src_path = item["reg_path"]
        name = item["name"]

        # Vérifier si l'élément peut être désactivé (a un opposite_path)
        if "reg_opposite_path" not in item:
            raise RuntimeError(f"Impossible de désactiver {name}: RunOnce et Policies ne peuvent pas être désactivés")

        dst_path = item["reg_opposite_path"]

        # Lecture valeur depuis src
        with winreg.OpenKey(hive, src_path, 0, winreg.KEY_READ | winreg.KEY_WRITE) as src_key:
            value_data, value_type = winreg.QueryValueEx(src_key, name)

        # Écriture dans la clé opposée (création si besoin)
        with winreg.CreateKey(hive, dst_path) as dst_key:
            winreg.SetValueEx(dst_key, name, 0, value_type, value_data)

        # Suppression dans la clé d'origine
        with winreg.OpenKey(hive, src_path, 0, winreg.KEY_SET_VALUE) as src_key:
            winreg.DeleteValue(src_key, name)

        # Mise à jour de la structure
        item["enabled"] = not item["enabled"]
        item["reg_path"], item["reg_opposite_path"] = (
            item["reg_opposite_path"],
            item["reg_path"],
        )
        item["source"] = f"{item['hive']} {os.path.basename(item['reg_path'])}"

    # ---------- dossier Startup ----------

    def _toggle_folder_item(self, item: dict):
        current_path = item["path"]
        if current_path.endswith(".disabled"):
            # activer : enlever le suffixe
            new_path = current_path[:-9]
        else:
            # désactiver : ajouter le suffixe
            new_path = current_path + ".disabled"

        if os.path.exists(current_path):
            os.rename(current_path, new_path)
        else:
            # si le fichier n'existe plus, on marque simplement comme désactivé
            new_path = current_path

        item["path"] = new_path
        item["enabled"] = not item["enabled"]

        # mettre à jour l'affichage du chemin
        # (on recherche la ligne correspondant à cet item)
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).text() == item["name"]:
                # Le chemin n'est plus affiché dans la table, donc pas besoin de mettre à jour
                break

    # =================================================================
    #  SUPPRESSION AVEC BACKUP
    # =================================================================

    def delete_item(self, row: int):
        if row < 0 or row >= len(self.items):
            return

        item = self.items[row]

        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Supprimer « {item['name']} » du démarrage ?\n"
            f"(Une sauvegarde sera enregistrée dans {os.path.basename(self.backup_path)})",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        try:
            # Backup JSON
            self._backup_action(item, "delete")

            if item.get("source_type") == "registry":
                self._delete_registry_item(item)
            elif item.get("source_type") == "folder":
                self._delete_folder_item(item)

            # Supprimer de la liste et recharger la table
            del self.items[row]
            self.populate_table()

            self.status.emit(f"{item['name']} supprimé du démarrage", "success")

        except Exception as e:
            self.status.emit(f"Erreur lors de la suppression: {e}", "error")

    def _delete_registry_item(self, item: dict):
        hive = self._get_hive_handle(item["hive"])
        name = item["name"]

        # on essaie de supprimer dans les deux clés (Run et Run-)
        for path in [item.get("reg_path"), item.get("reg_opposite_path")]:
            if not path:
                continue
            try:
                with winreg.OpenKey(hive, path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, name)
            except OSError:
                # déjà absent : ignorer
                continue

    def _delete_folder_item(self, item: dict):
        path = item["path"]
        if os.path.exists(path):
            os.remove(path)

    # =================================================================
    #  BACKUP JSON
    # =================================================================

    def _backup_action(self, item: dict, action: str):
        entry = dict(item)
        entry["action"] = action
        entry["timestamp"] = datetime.now().isoformat(timespec="seconds")

        data = []
        if os.path.exists(self.backup_path):
            try:
                with open(self.backup_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = []

        data.append(entry)
        with open(self.backup_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # =================================================================
    #  EXPORT JSON MANUEL
    # =================================================================

    def export_json(self):
        if not self.items:
            self.status.emit("Aucun élément à exporter", "info")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter la liste des programmes",
            os.path.join(os.path.expanduser("~"), "startup_programs.json"),
            "Fichiers JSON (*.json)"
        )
        if not filename:
            return

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.items, f, ensure_ascii=False, indent=2)
            self.status.emit(f"Liste exportée dans {filename}", "success")
        except Exception as e:
            self.status.emit(f"Erreur export JSON: {e}", "error")

    # =================================================================
    #  FILTRE
    # =================================================================

    def apply_filter(self, text: str):
        text = (text or "").lower().strip()

        # Filtre vide = afficher tout
        if text == "":
            for row in range(self.table.rowCount()):
                self.table.setRowHidden(row, False)
            return

        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0)
            creator_item = self.table.item(row, 1)
            source_item = self.table.item(row, 2)

            # Sécurité : items jamais None
            name = name_item.text().lower() if name_item else ""
            creator = creator_item.text().lower() if creator_item else ""
            source = source_item.text().lower() if source_item else ""

            visible = (text in name) or (text in creator) or (text in source)
            self.table.setRowHidden(row, not visible)

    def eventFilter(self, obj, event):
        """Gérer le hover sur toute la ligne - version simplifiée"""
        if event.type() == QEvent.Type.MouseMove and obj == self.table.viewport():
            pos = event.position()
            row = self.table.rowAt(pos.y())

            if row >= 0 and not self.table.isRowHidden(row):
                # Appliquer le style hover uniquement à la ligne survolée
                self.table.selectRow(row)
                # Forcer la mise à jour du style
                self.table.viewport().update()

        elif event.type() == QEvent.Type.Leave and obj == self.table.viewport():
            # Effacer la sélection quand la souris quitte
            self.table.clearSelection()
            self.table.viewport().update()

        return super().eventFilter(obj, event)

