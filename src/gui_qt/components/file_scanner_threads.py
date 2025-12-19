#!/usr/bin/env python3
"""
Classes de threads pour le scan et nettoyage de fichiers
"""

import os
import sys
import time
import glob
import subprocess
from PySide6.QtCore import QThread, Signal


class FileScannerThread(QThread):
    """Thread pour scanner les fichiers en arrière-plan"""
    progress_updated = Signal(int, str, int, int, str)  # progress, category, files_count, size_mb, details
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
            self.progress_updated.emit(progress, category, files_count, size_mb, "")

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

    def __init__(self, categories, scan_results, settings=None):
        super().__init__()
        self.categories = categories
        self.scan_results = scan_results

        # Paramètres par défaut si non fournis
        default_settings = {
            'safe_mode': True,
            'min_file_age_days': 30,
            'max_file_size_mb': 100,
            'delete_restore_points': False,
            'clear_recycle_bin': True,
        }
        self.settings = settings or default_settings

        self.is_running = True
        self.deleted_files = []  # Liste des fichiers supprimés pour restauration potentielle

    def run(self):
        """Nettoyer les fichiers réels"""
        results = []
        total_categories = len(self.categories)

        self.progress_updated.emit(0, "Initialisation", 0, 0, "")
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
        clear_recycle = self.settings.get('clear_recycle_bin', True)
        if not clear_recycle:
            return 0, 0, ["Vidage de la corbeille désactivé"]

        files_deleted = 0
        size_freed = 0

        try:
            if os.name == "nt":
                # Windows: utiliser PowerShell pour vider la corbeille
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
                        safe_mode = self.settings.get('safe_mode', True)
                        deleted, freed = self._clean_directory(recycle_path, "*", safe=safe_mode)
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
        safe_mode = self.settings.get('safe_mode', True)
        delete_restore = self.settings.get('delete_restore_points', False)

        if safe_mode or not delete_restore:
            self.error_occurred.emit("Suppression des points de restauration désactivée")
            return 0, 0, ["Mode sécurité: Points de restauration préservés"]  # Mode sécurité: liste informative

        try:
            if os.name == "nt":
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
            # Protection améliorée des répertoires système critiques
            if self._is_system_critical_path(file_path):
                return False

            # Autoriser les répertoires de nettoyage utilisateur
            if self._is_user_cleanable_path(file_path):
                pass  # Continuer les autres vérifications
            else:
                # Pour ProgramData, vérifications plus strictes
                if self._is_restricted_programdata_path(file_path):
                    return False

            # Ne supprimer que les fichiers selon l'âge minimum configuré
            try:
                file_age = (time.time() - os.path.getmtime(file_path)) / (24 * 3600)  # jours
                min_age = self.settings.get('min_file_age_days', 30)
                if file_age < min_age:
                    return False
            except OSError:
                return False

            # Ne supprimer que les fichiers selon la taille maximum configurée
            try:
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                max_size = self.settings.get('max_file_size_mb', 100)
                if file_size > max_size:
                    return False
            except OSError:
                return False

        return True

    def _is_system_critical_path(self, file_path):
        """Vérifier si le chemin est un répertoire système critique"""
        file_path_lower = file_path.lower()

        # Répertoires système absolument critiques
        critical_paths = [
            r"\windows",           # C:\Windows
            r"\windows\system32",  # C:\Windows\System32
            r"\windows\syswow64",  # C:\Windows\SysWOW64
            r"\program files",     # C:\Program Files
            r"\program files (x86)", # C:\Program Files (x86)
        ]

        for critical_path in critical_paths:
            if file_path_lower.find(critical_path) == 1:  # Après la lettre du lecteur
                return True

        return False

    def _is_user_cleanable_path(self, file_path):
        """Vérifier si le chemin est dans les répertoires utilisateur autorisés pour le nettoyage"""
        file_path_lower = file_path.lower()

        # Chemins utilisateur autorisés pour le nettoyage
        user_cleanable_patterns = [
            r"\users\*\appdata\local\temp",      # C:\Users\username\AppData\Local\Temp
            r"\users\*\appdata\local\microsoft\windows\inetcache",  # Cache navigateur
            r"\users\*\appdata\local\microsoft\windows\explorer",   # Explorer cache
            r"\users\*\appdata\roaming\microsoft\windows\recent",  # Fichiers récents
            r"\users\*\appdata\local\google\chrome",    # Chrome cache
            r"\users\*\appdata\local\microsoft\edge",    # Edge cache
            r"\users\*\appdata\roaming\mozilla\firefox", # Firefox cache
        ]

        for pattern in user_cleanable_patterns:
            # Remplacer '*' par le nom d'utilisateur actuel
            username = os.path.basename(os.path.expanduser("~"))
            actual_pattern = pattern.replace("*", username).lower()
            if actual_pattern in file_path_lower:
                return True

        return False

    def _is_restricted_programdata_path(self, file_path):
        """Vérifier si le chemin ProgramData est restreint"""
        file_path_lower = file_path.lower()

        # ProgramData : autoriser seulement certains sous-répertoires de nettoyage
        allowed_programdata_patterns = [
            r"\programdata\microsoft\windows\wer",       # Windows Error Reporting
            r"\programdata\microsoft\windows\start menu", # Menu démarrer vieux fichiers
        ]

        # Si c'est dans ProgramData
        if r"\programdata" in file_path_lower:
            # Vérifier si c'est un chemin autorisé
            for allowed_pattern in allowed_programdata_patterns:
                if allowed_pattern in file_path_lower:
                    return False  # Autorisé

            # Autres chemins ProgramData sont interdits
            return True

        return False

    def stop(self):
        """Arrêter le nettoyage"""
        self.is_running = False