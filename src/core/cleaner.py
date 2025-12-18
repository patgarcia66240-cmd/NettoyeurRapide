"""
Cleaner - Module pour nettoyer les fichiers temporaires
"""

import os
import shutil
import tempfile
import platform
import stat
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import time

class Cleaner:
    """Classe pour nettoyer les fichiers temporaires et autres fichiers inutiles"""

    def __init__(self):
        """Initialisation du nettoyeur"""
        self.system = platform.system()
        self.space_saved = 0
        self.files_cleaned = 0
        self.errors = []

    @staticmethod
    def format_size(n: int) -> str:
        """Formater une taille en octets en format lisible"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if n < 1024.0:
                return f"{n:.1f} {unit}"
            n /= 1024.0
        return f"{n:.1f} PB"

    def clean_files(self, file_paths: List[str]) -> List[Dict]:
        """Nettoyer les fichiers spécifiés"""
        cleaned_files = []
        self.space_saved = 0
        self.files_cleaned = 0
        self.errors = []

        for file_path in file_paths:
            try:
                result = self._clean_file_or_directory(file_path)
                if result:
                    cleaned_files.append(result)
                    self.space_saved += result.get('size', 0)
                    self.files_cleaned += 1
            except Exception as e:
                self.errors.append({
                    'path': file_path,
                    'error': str(e)
                })

        return cleaned_files

    def clean_temp_files(self, paths: List[str] = None) -> List[Dict]:
        """Nettoyer les fichiers temporaires dans les chemins spécifiés"""
        if paths is None:
            # Obtenir les dossiers temporaires par défaut
            paths = self._get_default_temp_paths()

        cleaned_files = []

        for path in paths:
            if os.path.exists(path):
                result = self._clean_directory_safe(path)
                cleaned_files.extend(result)

        return cleaned_files

    def clean_browser_cache(self) -> List[Dict]:
        """Nettoyer les caches des navigateurs"""
        cleaned_files = []

        if self.system == "Windows":
            if 'LOCALAPPDATA' in os.environ:
                local_appdata = os.environ['LOCALAPPDATA']

                # Chrome
                chrome_cache_base = os.path.join(local_appdata, 'Google', 'Chrome', 'User Data')
                cleaned_files.extend(self._clean_chrome_cache(chrome_cache_base))

                # Firefox
                firefox_cache_base = os.path.join(local_appdata, 'Mozilla', 'Firefox', 'Profiles')
                cleaned_files.extend(self._clean_firefox_cache(firefox_cache_base))

                # Edge
                edge_cache_base = os.path.join(local_appdata, 'Microsoft', 'Edge', 'User Data')
                cleaned_files.extend(self._clean_chrome_cache(edge_cache_base))  # Edge utilise la même structure

        else:  # Linux/Mac
            home = os.path.expanduser('~')
            cache_home = os.path.join(home, '.cache')

            # Chrome/Chromium
            for browser in ['google-chrome', 'chromium']:
                browser_cache = os.path.join(cache_home, browser)
                if os.path.exists(browser_cache):
                    cleaned_files.extend(self._clean_directory_safe(browser_cache))

            # Firefox
            firefox_cache = os.path.join(home, '.mozilla', 'firefox')
            if os.path.exists(firefox_cache):
                cleaned_files.extend(self._clean_firefox_cache(firefox_cache))

        return cleaned_files

    def clean_system_cache(self) -> List[Dict]:
        """Nettoyer les caches système"""
        cleaned_files = []

        if self.system == "Windows":
            # Windows Update cache (avec confirmation implicite car c'est temporaire)
            win_update_cache = 'C:\\Windows\\SoftwareDistribution\\Download'
            if os.path.exists(win_update_cache):
                cleaned_files.extend(self._clean_directory_safe(win_update_cache))

            # Windows prefetch
            prefetch_dir = 'C:\\Windows\\Prefetch'
            if os.path.exists(prefetch_dir):
                cleaned_files.extend(self._clean_directory_safe(prefetch_dir))

            # Windows Error Reporting
            error_reporting = 'C:\\ProgramData\\Microsoft\\Windows\\WER\\ReportArchive'
            if os.path.exists(error_reporting):
                cleaned_files.extend(self._clean_directory_safe(error_reporting))

        else:  # Linux
            # Package cache (plus ancien que 7 jours)
            import time
            cutoff_time = time.time() - (7 * 24 * 60 * 60)

            package_caches = ['/var/cache/apt/archives', '/var/cache/yum', '/var/cache/dnf']
            for cache_dir in package_caches:
                if os.path.exists(cache_dir):
                    cleaned_files.extend(self._clean_old_files(cache_dir, cutoff_time))

        return cleaned_files

    def clean_recycle_bin(self) -> List[Dict]:
        """Vider la corbeille"""
        cleaned_files = []

        if self.system == "Windows":
            try:
                import win32com.client
                shell = win32com.client.Dispatch("Shell.Application")
                recycle_bin = shell.NameSpace(10)  # 10 = corbeille

                items_count = recycle_bin.Items().Count
                if items_count > 0:
                    # Obtenir la taille avant de vider
                    total_size = 0
                    for item in recycle_bin.Items():
                        try:
                            total_size += item.Size
                        except:
                            continue

                    # Vider la corbeille
                    recycle_bin.Items().InvokeVerb("EmptyRecycleBin")

                    cleaned_files.append({
                        'path': 'Recycle Bin',
                        'name': f'{items_count} items',
                        'size': total_size,
                        'size_formatted': self.format_size(total_size),
                        'type': 'directory'
                    })

                    self.space_saved += total_size
                    self.files_cleaned += items_count

            except Exception as e:
                self.errors.append({
                    'path': 'Recycle Bin',
                    'error': f"Impossible de vider la corbeille: {str(e)}"
                })

        return cleaned_files

    def get_space_saved(self) -> int:
        """Obtenir l'espace économisé par le nettoyage"""
        return self.space_saved

    def get_files_cleaned_count(self) -> int:
        """Obtenir le nombre de fichiers nettoyés"""
        return self.files_cleaned

    def get_errors(self) -> List[Dict]:
        """Obtenir la liste des erreurs"""
        return self.errors

    def _clean_file_or_directory(self, path: str) -> Optional[Dict]:
        """Nettoyer un fichier ou un répertoire"""
        try:
            if os.path.isfile(path):
                return self._delete_file(path)
            elif os.path.isdir(path):
                return self._delete_directory(path)
        except Exception as e:
            self.errors.append({
                'path': path,
                'error': str(e)
            })
            return None

    def _delete_file(self, file_path: str) -> Dict:
        """Supprimer un fichier"""
        try:
            # Obtenir la taille avant suppression
            file_size = os.path.getsize(file_path)

            # Rendre le fichier accessible en écriture (Windows)
            if self.system == "Windows":
                try:
                    import win32api
                    import win32con
                    attrs = win32api.GetFileAttributes(file_path)
                    if attrs & win32con.FILE_ATTRIBUTE_READONLY:
                        win32api.SetFileAttributes(file_path, attrs & ~win32con.FILE_ATTRIBUTE_READONLY)
                except:
                    pass

            # Supprimer le fichier
            os.remove(file_path)

            return {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': file_size,
                'size_formatted': self.format_size(file_size),
                'type': 'file'
            }

        except Exception as e:
            raise Exception(f"Impossible de supprimer le fichier {file_path}: {str(e)}")

    def _delete_directory(self, dir_path: str) -> Dict:
        """Supprimer un répertoire et son contenu"""
        try:
            total_size = 0
            file_count = 0

            # Calculer la taille et le nombre de fichiers
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                        file_count += 1
                    except:
                        continue

            # Supprimer le répertoire
            shutil.rmtree(dir_path, ignore_errors=True)

            return {
                'path': dir_path,
                'name': os.path.basename(dir_path),
                'size': total_size,
                'size_formatted': self.format_size(total_size),
                'file_count': file_count,
                'type': 'directory'
            }

        except Exception as e:
            raise Exception(f"Impossible de supprimer le répertoire {dir_path}: {str(e)}")

    def _clean_directory_safe(self, dir_path: str) -> List[Dict]:
        """Nettoyer un répertoire de manière sécurisée"""
        cleaned_files = []

        try:
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)

                try:
                    result = self._clean_file_or_directory(item_path)
                    if result:
                        cleaned_files.append(result)
                except Exception:
                    # Continuer même si un fichier ne peut pas être supprimé
                    continue

        except (PermissionError, OSError):
            # Ignorer les erreurs de permission sur le répertoire parent
            pass

        return cleaned_files

    def _clean_old_files(self, dir_path: str, cutoff_time: float) -> List[Dict]:
        """Nettoyer les fichiers plus anciens que cutoff_time"""
        cleaned_files = []

        try:
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)

                try:
                    stat_info = os.stat(item_path)
                    if stat_info.st_mtime < cutoff_time:
                        result = self._clean_file_or_directory(item_path)
                        if result:
                            cleaned_files.append(result)
                except Exception:
                    continue

        except (PermissionError, OSError):
            pass

        return cleaned_files

    def _clean_chrome_cache(self, chrome_base: str) -> List[Dict]:
        """Nettoyer le cache Chrome/Edge"""
        cleaned_files = []

        if not os.path.exists(chrome_base):
            return cleaned_files

        try:
            for profile in os.listdir(chrome_base):
                if profile.startswith('Profile') or profile == 'Default':
                    profile_path = os.path.join(chrome_base, profile)

                    # Cache principaux
                    cache_dirs = ['Cache', 'Code Cache', 'GPUCache']
                    for cache_dir in cache_dirs:
                        cache_path = os.path.join(profile_path, cache_dir)
                        if os.path.exists(cache_path):
                            cleaned_files.extend(self._clean_directory_safe(cache_path))

                    # Fichiers de session temporaires
                    session_files = ['Current Session', 'Current Tabs', 'Last Session', 'Last Tabs']
                    for session_file in session_files:
                        session_path = os.path.join(profile_path, session_file)
                        if os.path.exists(session_path):
                            try:
                                result = self._delete_file(session_path)
                                cleaned_files.append(result)
                            except Exception:
                                continue

        except (PermissionError, OSError):
            pass

        return cleaned_files

    def _clean_firefox_cache(self, firefox_base: str) -> List[Dict]:
        """Nettoyer le cache Firefox"""
        cleaned_files = []

        if not os.path.exists(firefox_base):
            return cleaned_files

        try:
            for profile in os.listdir(firefox_base):
                profile_path = os.path.join(firefox_base, profile)

                if os.path.isdir(profile_path):
                    # Cache Firefox
                    cache_dirs = ['cache2', 'startupCache', 'thumbnails']
                    for cache_dir in cache_dirs:
                        cache_path = os.path.join(profile_path, cache_dir)
                        if os.path.exists(cache_path):
                            cleaned_files.extend(self._clean_directory_safe(cache_path))

                    # Fichiers de recovery
                    recovery_files = ['recovery.bak', 'recovery.jsonlz4.bak']
                    for recovery_file in recovery_files:
                        recovery_path = os.path.join(profile_path, recovery_file)
                        if os.path.exists(recovery_path):
                            try:
                                result = self._delete_file(recovery_path)
                                cleaned_files.append(result)
                            except Exception:
                                continue

        except (PermissionError, OSError):
            pass

        return cleaned_files

    def _get_default_temp_paths(self) -> List[str]:
        """Obtenir les chemins temporaires par défaut"""
        paths = []

        if self.system == "Windows":
            paths.extend([
                os.environ.get('TEMP', ''),
                os.environ.get('TMP', ''),
                'C:\\Windows\\Temp'
            ])

            if 'LOCALAPPDATA' in os.environ:
                local_appdata = os.environ['LOCALAPPDATA']
                paths.extend([
                    os.path.join(local_appdata, 'Temp'),
                    os.path.join(local_appdata, 'Microsoft', 'Windows', 'INetCache')
                ])

        else:  # Linux/Mac
            paths.extend([
                '/tmp',
                '/var/tmp',
                tempfile.gettempdir()
            ])

            home = os.path.expanduser('~')
            paths.extend([
                os.path.join(home, '.cache'),
                os.path.join(home, '.local', 'share', 'Trash')
            ])

        # Filtrer les chemins qui existent
        return [p for p in paths if p and os.path.exists(p)]

    def reset_stats(self):
        """Réinitialiser les statistiques"""
        self.space_saved = 0
        self.files_cleaned = 0
        self.errors = []