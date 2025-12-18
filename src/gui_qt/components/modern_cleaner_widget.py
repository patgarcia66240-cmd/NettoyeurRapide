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
from PySide6.QtCore import Qt, Signal, QTimer, QThread
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor

from .nav_button import NavButton


class FileScannerThread(QThread):
    """Thread pour scanner les fichiers en arrière-plan"""
    progress_updated = Signal(int, str, int, int)  # progress, category, files_count, size_mb
    scan_completed = Signal(list)  # results list

    def __init__(self, categories, quick_scan=True):
        super().__init__()
        self.categories = categories
        self.quick_scan = quick_scan
        self.is_running = True

    def run(self):
        """Scanner les fichiers réels"""
        results = []
        total_categories = len(self.categories)

        for i, category in enumerate(self.categories):
            if not self.is_running:
                break

            # Normaliser la catégorie en retirant les 2 premiers caractères (émoticône + espace)
            category_clean = category[2:].strip() if len(category) > 2 else category.strip()

            if "Temporaires" in category_clean or "tempora" in category_clean.lower():
                files_count, size_mb = self.scan_temp_files()
            elif "Cache" in category_clean:
                files_count, size_mb = self.scan_cache_files()
            elif "Logs" in category_clean or "Log" in category_clean:
                files_count, size_mb = self.scan_log_files()
            elif "Corbeille" in category_clean:
                files_count, size_mb = self.scan_recycle_bin()
            elif "Navigateur" in category_clean:
                files_count, size_mb = self.scan_browser_cache()
            elif "Mises à Jour" in category_clean or "Windows" in category_clean:
                files_count, size_mb = self.scan_windows_updates()
            elif "Récupération" in category_clean:
                files_count, size_mb = self.scan_recovery_files()
            elif "Restauration" in category_clean:
                files_count, size_mb = self.scan_restore_points()
            else:
                files_count, size_mb = 0, 0

            # Toujours ajouter les résultats, même si 0 fichier trouvé
            results.append((category, files_count, size_mb))

            # Émettre le progrès
            progress = int(((i + 1) / total_categories) * 100)
            self.progress_updated.emit(progress, category, files_count, size_mb)

            # Délai pour ne pas surcharger le système
            self.msleep(500 if self.quick_scan else 1000)

        self.scan_completed.emit(results)

    def scan_temp_files(self):
        """Scanner les fichiers temporaires"""
        temp_paths = [
            os.environ.get("TEMP", ""),
            os.environ.get("TMP", ""),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp"),
            "/tmp",
            "/var/tmp"
        ]

        total_files = 0
        total_size = 0

        for temp_path in temp_paths:
            if os.path.exists(temp_path):
                try:
                    for root, dirs, files in os.walk(temp_path):
                        if not self.is_running:
                            break
                        # Limiter la profondeur pour les scans rapides
                        depth = root.count(os.sep) - temp_path.count(os.sep)
                        if self.quick_scan and depth > 2:
                            continue

                        for file in files:
                            try:
                                file_path = os.path.join(root, file)
                                if os.path.isfile(file_path):
                                    file_size = os.path.getsize(file_path) // (1024 * 1024)  # MB
                                    total_files += 1
                                    total_size += file_size
                            except (OSError, PermissionError):
                                continue
                except (OSError, PermissionError):
                    continue

        return total_files, total_size

    def scan_cache_files(self):
        """Scanner les fichiers cache"""
        cache_paths = [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "INetCache"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Explorer"),
            os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Recent"),
            os.path.expanduser("~/.cache"),
        ]

        total_files = 0
        total_size = 0

        for cache_path in cache_paths:
            if os.path.exists(cache_path):
                try:
                    for file in os.listdir(cache_path):
                        if not self.is_running:
                            break
                        try:
                            file_path = os.path.join(cache_path, file)
                            if os.path.isfile(file_path):
                                file_size = os.path.getsize(file_path) // (1024 * 1024)  # MB
                                total_files += 1
                                total_size += file_size
                        except (OSError, PermissionError):
                            continue
                except (OSError, PermissionError):
                    continue

        return total_files, total_size

    def scan_log_files(self):
        """Scanner les fichiers logs"""
        log_patterns = [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "INetCookies", "*.txt"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "History", "*.dat"),
            os.path.join(os.environ.get("TEMP", ""), "*.log"),
            os.path.expanduser("~/.local/share/recently-used.xbel*"),
            "/var/log/*.log" if os.name != "nt" else "",
        ]

        total_files = 0
        total_size = 0

        for pattern in log_patterns:
            if pattern:
                try:
                    for file_path in glob.glob(pattern):
                        if not self.is_running:
                            break
                        try:
                            if os.path.isfile(file_path):
                                file_size = os.path.getsize(file_path) // (1024 * 1024)  # MB
                                total_files += 1
                                total_size += file_size
                        except (OSError, PermissionError):
                            continue
                except (OSError, PermissionError):
                    continue

        return total_files, total_size

    def scan_recycle_bin(self):
        """Scanner la corbeille"""
        try:
            if os.name == "nt":
                # Windows: utiliser PowerShell pour obtenir des informations précises sur la corbeille
                import subprocess
                try:
                    # Commande PowerShell pour obtenir la taille et le nombre de fichiers dans la corbeille
                    ps_command = """
                    $shell = New-Object -ComObject Shell.Application
                    $recycle = $shell.NameSpace(10)
                    $count = 0
                    $size = 0
                    $recycle.Items() | ForEach-Object {
                        $count++
                        $size += $_.Size
                    }
                    Write-Output "$count,$size"
                    """

                    result = subprocess.run(
                        ["powershell", "-Command", ps_command],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )

                    if result.returncode == 0 and result.stdout.strip():
                        parts = result.stdout.strip().split(',')
                        if len(parts) == 2:
                            file_count = int(parts[0])
                            size_bytes = int(parts[1])
                            size_mb = max(1, size_bytes // (1024 * 1024))  # Au moins 1 MB si non vide
                            return file_count, size_mb
                except (subprocess.TimeoutExpired, ValueError, subprocess.SubprocessError):
                    pass

                # Alternative: scanner directement les dossiers de la corbeille
                system_drive = os.environ.get("SystemDrive", "C:")
                recycle_base = os.path.join(system_drive, "$Recycle.Bin")

                if os.path.exists(recycle_base):
                    total_files = 0
                    total_size = 0

                    for item in os.listdir(recycle_base):
                        item_path = os.path.join(recycle_base, item)
                        if os.path.isdir(item_path) and not item.startswith("."):
                            try:
                                for root, dirs, files in os.walk(item_path):
                                    if not self.is_running:
                                        break
                                    for file in files:
                                        try:
                                            file_path = os.path.join(root, file)
                                            if os.path.isfile(file_path) and not file.endswith(".ini"):
                                                file_size = os.path.getsize(file_path) // (1024 * 1024)
                                                total_files += 1
                                                total_size += file_size
                                        except (OSError, PermissionError):
                                            continue
                            except (OSError, PermissionError):
                                continue

                    if total_files > 0:
                        return total_files, max(1, total_size)  # Au moins 1 MB si fichiers trouvés

            else:
                # Linux recycle bin
                recycle_paths = [
                    os.path.expanduser("~/.local/share/Trash/files"),
                    os.path.expanduser("~/.Trash")
                ]
                for recycle_path in recycle_paths:
                    if os.path.exists(recycle_path):
                        total_files = 0
                        total_size = 0
                        for file in os.listdir(recycle_path):
                            if not self.is_running:
                                break
                            try:
                                file_path = os.path.join(recycle_path, file)
                                if os.path.isfile(file_path):
                                    file_size = os.path.getsize(file_path) // (1024 * 1024)
                                    total_files += 1
                                    total_size += file_size
                            except (OSError, PermissionError):
                                continue
                        return total_files, total_size
        except Exception:
            pass

        return 0, 0

    def scan_browser_cache(self):
        """Scanner le cache des navigateurs"""
        browser_paths = [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "User Data", "Default", "Cache"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "User Data", "Default", "Code Cache"),
            os.path.join(os.environ.get("APPDATA", ""), "Mozilla", "Firefox", "Profiles"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Edge", "User Data", "Default", "Cache"),
        ]

        total_files = 0
        total_size = 0

        for browser_path in browser_paths:
            if os.path.exists(browser_path):
                try:
                    if "Firefox" in browser_path:
                        # Firefox profiles
                        for profile in os.listdir(browser_path):
                            profile_path = os.path.join(browser_path, profile)
                            if os.path.isdir(profile_path):
                                cache_path = os.path.join(profile_path, "cache2")
                                if os.path.exists(cache_path):
                                    for root, dirs, files in os.walk(cache_path):
                                        if not self.is_running:
                                            break
                                        if self.quick_scan and len(files) > 100:  # Limiter pour les scans rapides
                                            total_files += len(files)
                                            continue
                                        for file in files:
                                            try:
                                                file_path = os.path.join(root, file)
                                                if os.path.isfile(file_path):
                                                    file_size = os.path.getsize(file_path) // (1024 * 1024)
                                                    total_files += 1
                                                    total_size += file_size
                                            except (OSError, PermissionError):
                                                continue
                    else:
                        # Chrome/Edge
                        for root, dirs, files in os.walk(browser_path):
                            if not self.is_running:
                                break
                            if self.quick_scan and len(files) > 100:  # Limiter pour les scans rapides
                                total_files += len(files)
                                continue
                            for file in files:
                                try:
                                    file_path = os.path.join(root, file)
                                    if os.path.isfile(file_path):
                                        file_size = os.path.getsize(file_path) // (1024 * 1024)
                                        total_files += 1
                                        total_size += file_size
                                except (OSError, PermissionError):
                                    continue
                except (OSError, PermissionError):
                    continue

        return total_files, total_size

    def scan_windows_updates(self):
        """Scanner les fichiers de mises à jour Windows"""
        update_paths = [
            os.path.join(os.environ.get("WINDIR", ""), "SoftwareDistribution", "Download"),
            os.path.join(os.environ.get("WINDIR", ""), "SoftwareDistribution", "DataStore"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "WinStore"),
        ]

        total_files = 0
        total_size = 0

        for update_path in update_paths:
            if os.path.exists(update_path):
                try:
                    for root, dirs, files in os.walk(update_path):
                        if not self.is_running:
                            break
                        if self.quick_scan and len(files) > 50:  # Limiter pour les scans rapides
                            total_files += len(files)
                            continue
                        for file in files:
                            try:
                                file_path = os.path.join(root, file)
                                if os.path.isfile(file_path):
                                    file_size = os.path.getsize(file_path) // (1024 * 1024)
                                    total_files += 1
                                    total_size += file_size
                            except (OSError, PermissionError):
                                continue
                except (OSError, PermissionError):
                    continue

        return total_files, total_size

    def scan_recovery_files(self):
        """Scanner les fichiers de récupération"""
        recovery_paths = [
            os.path.join(os.environ.get("WINDIR", ""), "Minidump"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "WER"),
            os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "WER"),
        ]

        total_files = 0
        total_size = 0

        for recovery_path in recovery_paths:
            if os.path.exists(recovery_path):
                try:
                    for file in os.listdir(recovery_path):
                        if not self.is_running:
                            break
                        try:
                            file_path = os.path.join(recovery_path, file)
                            if os.path.isfile(file_path):
                                file_size = os.path.getsize(file_path) // (1024 * 1024)
                                total_files += 1
                                total_size += file_size
                        except (OSError, PermissionError):
                            continue
                except (OSError, PermissionError):
                    continue

        return total_files, total_size

    def scan_restore_points(self):
        """Scanner les points de restauration"""
        try:
            if os.name == "nt":
                import subprocess
                try:
                    # Commande PowerShell pour lister les points de restauration
                    ps_command = """
                    try {
                        $restorePoints = Get-ComputerRestorePoint | Select-Object Description, CreationTime, RestorePointType
                        if ($restorePoints) {
                            $count = $restorePoints.Count
                            Write-Output "$count"
                            $restorePoints | ForEach-Object {
                                Write-Output "POINT: $($_.Description) - $($_.CreationTime)"
                            }
                        } else {
                            Write-Output "0"
                            Write-Output "Aucun point de restauration trouvé"
                        }
                    } catch {
                        Write-Output "0"
                        Write-Output "Erreur: Points de restauration non accessibles"
                    }
                    """

                    result = subprocess.run(
                        ["powershell", "-Command", ps_command],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )

                    if result.returncode == 0 and result.stdout.strip():
                        lines = result.stdout.strip().split('\n')
                        if lines and lines[0].strip().isdigit():
                            restore_count = int(lines[0])

                            if restore_count > 0:
                                # Estimer la taille: environ 100MB par point de restauration
                                estimated_size_mb = max(100, restore_count * 100)
                                return restore_count, estimated_size_mb
                            else:
                                return 0, 0

                except (subprocess.TimeoutExpired, ValueError, subprocess.SubprocessError):
                    pass

                # Alternative: vérifier si la protection du système est activée
                try:
                    ps_check = """
                    try {
                        $protection = Get-ComputerRestorePoint -Status
                        if ($protection) {
                            Write-Output "1"
                        } else {
                            Write-Output "0"
                        }
                    } catch {
                        # Vérifier si la protection système est activée
                        try {
                            $sysRestore = Get-WmiObject -Class Win32_ComputerSystem -Property SystemRestore
                            if ($sysRestore) {
                                Write-Output "1"
                            } else {
                                Write-Output "0"
                            }
                        } catch {
                            Write-Output "0"
                        }
                    }
                    """

                    result = subprocess.run(
                        ["powershell", "-Command", ps_check],
                        capture_output=True,
                        text=True,
                        timeout=15
                    )

                    if result.returncode == 0 and "1" in result.stdout:
                        # Protection système activée mais impossible de compter les points
                        return 1, 200  # Estimation conservatrice

                except Exception:
                    pass

            else:
                # Linux: vérifier les snapshots et backups
                try:
                    # Vérifier Timeshift (outil de restauration Linux)
                    result = subprocess.run(
                        ["which", "timeshift"],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        # Timeshift est installé, tenter de lister les snapshots
                        try:
                            snapshot_result = subprocess.run(
                                ["timeshift", "--list"],
                                capture_output=True,
                                text=True,
                                timeout=10
                            )
                            if snapshot_result.returncode == 0:
                                # Compter les snapshots
                                snapshots = len([line for line in snapshot_result.stdout.split('\n') if line.strip()])
                                if snapshots > 0:
                                    return snapshots, snapshots * 50  # ~50MB par snapshot
                        except Exception:
                            return 1, 100  # Timeshift présent mais impossible de lister
                except Exception:
                    pass

        except Exception:
            pass

        return 0, 0

    def stop(self):
        """Arrêter le scan"""
        self.is_running = False


class FileCleanerThread(QThread):
    """Thread pour nettoyer les fichiers en arrière-plan"""
    progress_updated = Signal(int, str, int, int, str)  # progress, category, files_deleted, size_freed, files_details
    cleaning_completed = Signal(list)  # results list
    error_occurred = Signal(str)  # error message

    def __init__(self, categories, scan_results, safe_mode=True):
        super().__init__()
        self.categories = categories
        self.scan_results = scan_results
        self.safe_mode = safe_mode  # Mode de sécurité pour éviter les suppressions accidentelles
        self.is_running = True
        self.deleted_files = []  # Liste des fichiers supprimés pour restauration potentielle

    def run(self):
        """Nettoyer les fichiers réels"""
        results = []
        total_categories = len(self.categories)

        self.progress_updated.emit(0, "Initialisation", 0, 0)
        self.msleep(1000)  # Pause pour sécurité

        for i, category in enumerate(self.categories):
            if not self.is_running:
                break

            # Normaliser la catégorie
            category_clean = category[2:].strip() if len(category) > 2 else category.strip()

            files_deleted = 0
            size_freed = 0
            files_details = ""

            try:
                if "Temporaires" in category_clean or "tempora" in category_clean.lower():
                    files_deleted, size_freed, file_list = self.clean_temp_files()
                elif "Cache" in category_clean:
                    files_deleted, size_freed, file_list = self.clean_cache_files()
                elif "Logs" in category_clean or "Log" in category_clean:
                    files_deleted, size_freed, file_list = self.clean_log_files()
                elif "Corbeille" in category_clean:
                    files_deleted, size_freed, file_list = self.clean_recycle_bin()
                elif "Navigateur" in category_clean:
                    files_deleted, size_freed, file_list = self.clean_browser_cache()
                elif "Mises à Jour" in category_clean or "Windows" in category_clean:
                    files_deleted, size_freed, file_list = self.clean_windows_updates()
                elif "Récupération" in category_clean:
                    files_deleted, size_freed, file_list = self.clean_recovery_files()
                elif "Restauration" in category_clean:
                    files_deleted, size_freed, file_list = self.clean_restore_points()
                else:
                    files_deleted, size_freed, file_list = 0, 0, []

                # Toujours générer les détails des fichiers, même si aucun fichier n'a été supprimé
                files_details = self._format_files_details(file_list)

                results.append((category, files_deleted, size_freed))

            except Exception as e:
                self.error_occurred.emit(f"Erreur lors du nettoyage de {category_clean}: {str(e)}")

            # Émettre la progression
            progress = int(((i + 1) / total_categories) * 100)
            self.progress_updated.emit(progress, category, files_deleted, size_freed, files_details)

            # Pause entre les catégories pour sécurité
            self.msleep(1000)

        self.cleaning_completed.emit(results)

    def _format_files_details(self, file_list):
        """Formater les détails des fichiers: 5 premiers noms + ellipsis si plus de fichiers"""
        if not file_list:
            return ""

        # Prendre les 5 premiers fichiers
        first_five = file_list[:5]
        details = ", ".join([os.path.basename(f) for f in first_five if f])

        # Ajouter ellipsis s'il y a plus de 5 fichiers
        if len(file_list) > 5:
            details += f" ... et {len(file_list) - 5} autres"

        return details

    def clean_temp_files(self):
        """Nettoyer les fichiers temporaires"""
        temp_paths = [
            os.environ.get("TEMP", ""),
            os.environ.get("TMP", ""),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp"),
        ]
        return self._clean_directory_list(temp_paths, "*.tmp", safe=True)

    def clean_cache_files(self):
        """Nettoyer les fichiers cache"""
        cache_paths = [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "INetCache"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Explorer"),
            os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Recent"),
            os.path.expanduser("~/.cache"),
        ]
        return self._clean_directory_list(cache_paths, "*", safe=True)

    def clean_log_files(self):
        """Nettoyer les fichiers logs"""
        log_patterns = [
            os.path.join(os.environ.get("TEMP", ""), "*.log"),
            os.path.expanduser("~/.local/share/recently-used.xbel*"),
        ]
        return self._clean_file_patterns(log_patterns, safe=True)

    def clean_recycle_bin(self):
        """Vider la corbeille"""
        files_deleted = 0
        size_freed = 0

        try:
            if os.name == "nt":
                # Windows: utiliser PowerShell pour vider la corbeille
                import subprocess
                result = subprocess.run(
                    ["powershell", "-Command", "Clear-RecycleBin -Force"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    # Estimation (impossible d'obtenir les chiffres exacts)
                    files_deleted = 50  # Estimation
                    size_freed = 100  # Estimation en MB
            else:
                # Linux: vider les corbeilles utilisateur
                recycle_paths = [
                    os.path.expanduser("~/.local/share/Trash/files"),
                    os.path.expanduser("~/.Trash")
                ]
                for recycle_path in recycle_paths:
                    if os.path.exists(recycle_path):
                        deleted, freed = self._clean_directory(recycle_path, "*", safe=True)
                        files_deleted += deleted
                        size_freed += freed
        except Exception as e:
            self.error_occurred.emit(f"Erreur lors du vidage de la corbeille: {str(e)}")

        return files_deleted, size_freed, []  # Pas de liste détaillée disponible pour la corbeille

    def clean_browser_cache(self):
        """Nettoyer le cache des navigateurs"""
        browser_paths = [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "User Data", "Default", "Cache"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "User Data", "Default", "Code Cache"),
            os.path.join(os.environ.get("APPDATA", ""), "Mozilla", "Firefox", "Profiles"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Edge", "User Data", "Default", "Cache"),
        ]
        return self._clean_directory_list(browser_paths, "*", safe=True)

    def clean_windows_updates(self):
        """Nettoyer les fichiers de mises à jour Windows"""
        update_paths = [
            os.path.join(os.environ.get("WINDIR", ""), "SoftwareDistribution", "Download"),
        ]
        return self._clean_directory_list(update_paths, "*", safe=True)

    def clean_recovery_files(self):
        """Nettoyer les fichiers de récupération"""
        recovery_paths = [
            os.path.join(os.environ.get("WINDIR", ""), "Minidump"),
        ]
        return self._clean_directory_list(recovery_paths, "*.dmp", safe=True)

    def clean_restore_points(self):
        """Nettoyer les points de restauration (attention!)"""
        # Suppression des points de restauration - DANGEREUX
        if self.safe_mode:
            self.error_occurred.emit("Suppression des points de restauration désactivée en mode sécurité")
            return 0, 0, ["Mode sécurité: Points de restauration préservés"]  # Mode sécurité: liste informative

        try:
            if os.name == "nt":
                import subprocess
                try:
                    # D'abord lister les points de restauration pour les détails
                    list_command = """
                    try {
                        $points = Get-ComputerRestorePoint | Select-Object Description, CreationTime | Sort-Object CreationTime -Descending
                        if ($points) {
                            $points | ForEach-Object {
                                Write-Output "POINT: $($_.Description) - $($_.CreationTime)"
                            }
                        } else {
                            Write-Output "Aucun point de restauration trouvé"
                        }
                    } catch {
                        Write-Output "Points de restauration non accessibles"
                    }
                    """

                    list_result = subprocess.run(
                        ["powershell", "-Command", list_command],
                        capture_output=True,
                        text=True,
                        timeout=15
                    )

                    # Collecter les détails des points
                    restore_details = []
                    if list_result.returncode == 0:
                        for line in list_result.stdout.strip().split('\n'):
                            line = line.strip()
                            if line and line.startswith("POINT:"):
                                # Formater pour l'affichage
                                restore_details.append(line.replace("POINT: ", ""))

                    # Supprimer le point de restauration le plus ancien pour plus de sécurité
                    delete_command = """
                    try {
                        $oldestPoint = Get-ComputerRestorePoint | Sort-Object CreationTime | Select-Object -First 1
                        if ($oldestPoint) {
                            Remove-ComputerRestorePoint -RestorePoint $oldestPoint.SequenceNumber -Force
                            Write-Output "1"
                        } else {
                            Write-Output "0"
                        }
                    } catch {
                        Write-Output "0"
                    }
                    """

                    delete_result = subprocess.run(
                        ["powershell", "-Command", delete_command],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )

                    if delete_result.returncode == 0 and delete_result.stdout.strip() == "1":
                        return 1, 100, restore_details or ["Point de restauration supprimé"]
                    else:
                        return 0, 0, restore_details or ["Aucun point de restauration supprimé"]

                except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                    return 0, 0, ["Erreur lors de l'accès aux points de restauration"]
        except Exception as e:
            self.error_occurred.emit(f"Erreur lors de la suppression des points de restauration: {str(e)}")

        return 0, 0, []  # Erreur: aucun fichier traité

    def _clean_directory_list(self, directories, pattern="*", safe=True):
        """Nettoyer une liste de répertoires"""
        total_deleted = 0
        total_freed = 0
        all_files = []

        for directory in directories:
            if not self.is_running:
                break
            if os.path.exists(directory):
                deleted, freed, files = self._clean_directory(directory, pattern, safe)
                total_deleted += deleted
                total_freed += freed
                all_files.extend(files)

        return total_deleted, total_freed, all_files

    def _clean_directory(self, directory, pattern="*", safe=True):
        """Nettoyer un répertoire spécifique"""
        files_deleted = 0
        size_freed = 0
        deleted_files_list = []

        try:
            for root, dirs, files in os.walk(directory, topdown=False):
                if not self.is_running:
                    break

                # Supprimer les fichiers
                for file in files:
                    if not self.is_running:
                        break
                    try:
                        file_path = os.path.join(root, file)
                        if self._should_delete_file(file_path, safe):
                            size_before = os.path.getsize(file_path)
                            os.remove(file_path)
                            files_deleted += 1
                            size_freed += size_before // (1024 * 1024)  # MB
                            self.deleted_files.append(file_path)
                            deleted_files_list.append(file_path)
                    except (OSError, PermissionError) as e:
                        continue  # Ignorer les fichiers verrouillés

                # Supprimer les répertoires vides
                for dir_name in dirs:
                    if not self.is_running:
                        break
                    try:
                        dir_path = os.path.join(root, dir_name)
                        if os.path.isdir(dir_path) and not os.listdir(dir_path):
                            os.rmdir(dir_path)
                    except (OSError, PermissionError):
                        continue

        except (OSError, PermissionError):
            pass

        return files_deleted, size_freed, deleted_files_list

    def _clean_file_patterns(self, patterns, safe=True):
        """Nettoyer les fichiers correspondant aux patterns"""
        files_deleted = 0
        size_freed = 0
        deleted_files_list = []

        for pattern in patterns:
            if not self.is_running:
                break
            try:
                for file_path in glob.glob(pattern):
                    if not self.is_running:
                        break
                    if self._should_delete_file(file_path, safe):
                        try:
                            size_before = os.path.getsize(file_path)
                            os.remove(file_path)
                            files_deleted += 1
                            size_freed += size_before // (1024 * 1024)
                            self.deleted_files.append(file_path)
                            deleted_files_list.append(file_path)
                        except (OSError, PermissionError):
                            continue
            except Exception:
                continue

        return files_deleted, size_freed, deleted_files_list

    def _should_delete_file(self, file_path, safe=True):
        """Vérifier si un fichier peut être supprimé en toute sécurité"""
        if not os.path.exists(file_path):
            return False

        # Vérifications de sécurité
        if safe:
            # Ne jamais supprimer les fichiers système critiques
            system_paths = [
                "Windows", "System32", "Program Files", "Program Files (x86)",
                "ProgramData", "Users", "Documents and Settings"
            ]

            for sys_path in system_paths:
                if sys_path.lower() in file_path.lower():
                    return False

            # Ne supprimer que les fichiers récents (< 30 jours) pour la sécurité
            try:
                file_age = (time.time() - os.path.getmtime(file_path)) / (24 * 3600)  # jours
                if file_age < 30:
                    return False
            except OSError:
                return False

            # Ne supprimer que les fichiers petits (< 100MB) pour la sécurité
            try:
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                if file_size > 100:
                    return False
            except OSError:
                return False

        return True

    def stop(self):
        """Arrêter le nettoyage"""
        self.is_running = False


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
        self.safe_mode = True  # Mode de sécurité par défaut
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
        self.btn_quick_scan = self.header.add_button("Analyse Rapide", "Lancer une analyse rapide des fichiers temporaires", "primary")
        self.btn_deep_scan = self.header.add_button("Analyse Complète", "Lancer une analyse complète du système", "success")

        parent_layout.addWidget(self.header)

    def setup_toolbar(self, parent_layout):
        """Configurer la barre d'outils"""
        toolbar_frame = QFrame()
        toolbar_frame.setObjectName("modernToolbar")
        toolbar_frame.setFixedHeight(70)
        toolbar_frame.setStyleSheet("""
            QFrame#modernToolbar {
                background: rgba(52, 73, 94, 0.1);
                border: none;
                border-bottom: 1px solid rgba(52, 73, 94, 0.2);
            }
        """)

        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(15, 10, 15, 10)
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

        # Espace flexible
        toolbar_layout.addStretch()

        toolbar_layout.addWidget(self.btn_scan)
        toolbar_layout.addWidget(self.btn_select_all)
        toolbar_layout.addWidget(self.btn_deselect_all)
        toolbar_layout.addWidget(self.btn_clean)

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
            QScrollBar:vertical {
                background: rgba(189, 195, 199, 0.2);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(52, 152, 219, 0.6);
                border-radius: 4px;
                min-height: 20px;
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
        self.btn_quick_scan.clicked.connect(lambda: self.start_scan(quick=True))
        self.btn_deep_scan.clicked.connect(lambda: self.start_scan(quick=False))

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
        mode_text = "SÉCURITÉ" if self.safe_mode else "RÉEL"
        self.results_text.append(f"\n🧹 Démarrage du nettoyage en mode {mode_text}...")
        if self.safe_mode:
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
        self.cleaner_thread = FileCleanerThread(category_names, self.scan_results, self.safe_mode)
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

        if self.safe_mode:
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
        self.safe_mode = not self.safe_mode
        mode = "SÉCURITÉ" if self.safe_mode else "RÉEL"
        self.results_text.append(f"\n⚙️  Mode de nettoyage changé: {mode}")

        if self.safe_mode:
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
        return "SÉCURITÉ" if self.safe_mode else "RÉEL"

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
        self.safe_mode = not self.safe_mode
        mode = "SÉCURITÉ" if self.safe_mode else "RÉEL"
        self.results_text.append(f"\n⚙️  Mode de nettoyage changé: {mode}")

        if self.safe_mode:
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
        return "SÉCURITÉ" if self.safe_mode else "RÉEL"