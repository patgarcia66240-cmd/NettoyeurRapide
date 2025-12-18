"""
TempScanner - Module pour scanner les fichiers temporaires
"""

import os
import tempfile
import glob
import platform
from pathlib import Path
from typing import List, Dict, Generator
import stat

class TempScanner:
    """Classe pour scanner les fichiers temporaires et autres fichiers inutiles"""

    def __init__(self):
        """Initialisation du scanner"""
        self.system = platform.system()
        self.temp_extensions = {'.tmp', '.temp', '.bak', '.old', '.log', '.dmp', '.swp'}
        self.cache_dirs = set()
        self.exclude_patterns = {'*.lock', '*.pid', 'System Volume Information', '$Recycle.Bin'}

    @staticmethod
    def format_size(n: int) -> str:
        """Formater une taille en octets en format lisible"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if n < 1024.0:
                return f"{n:.1f} {unit}"
            n /= 1024.0
        return f"{n:.1f} PB"

    def get_system_temp_dirs(self) -> List[str]:
        """Obtenir les répertoires temporaires système"""
        temp_dirs = []

        if self.system == "Windows":
            # Temp Windows
            temp_dirs.extend([
                os.environ.get('TEMP', 'C:\\Windows\\Temp'),
                os.environ.get('TMP', 'C:\\Windows\\Temp'),
                'C:\\Windows\\Temp',
                'C:\\Windows\\Prefetch'
            ])

            # Temp utilisateur
            user_temp = tempfile.gettempdir()
            if user_temp not in temp_dirs:
                temp_dirs.append(user_temp)

            # Dossiers cache utilisateur
            if 'LOCALAPPDATA' in os.environ:
                local_appdata = os.environ['LOCALAPPDATA']
                temp_dirs.extend([
                    os.path.join(local_appdata, 'Temp'),
                    os.path.join(local_appdata, 'Microsoft', 'Windows', 'INetCache'),
                    os.path.join(local_appdata, 'Microsoft', 'Windows', 'Explorer')
                ])

            if 'APPDATA' in os.environ:
                appdata = os.environ['APPDATA']
                temp_dirs.extend([
                    os.path.join(appdata, 'Microsoft', 'Windows', 'Recent')
                ])

        else:  # Linux/Mac
            temp_dirs.extend([
                '/tmp',
                '/var/tmp',
                tempfile.gettempdir()
            ])

            # Cache utilisateur
            home = os.path.expanduser('~')
            temp_dirs.extend([
                os.path.join(home, '.cache'),
                os.path.join(home, '.local', 'share', 'Trash'),
                '/var/log'
            ])

        # Filtrer les dossiers qui existent
        return [d for d in temp_dirs if os.path.exists(d) and os.path.isdir(d)]

    def scan_browser_cache(self) -> List[Dict]:
        """Scanner les caches des navigateurs"""
        cache_files = []

        if self.system == "Windows":
            if 'LOCALAPPDATA' in os.environ:
                local_appdata = os.environ['LOCALAPPDATA']

                # Chrome
                chrome_cache_base = os.path.join(local_appdata, 'Google', 'Chrome', 'User Data')
                if os.path.exists(chrome_cache_base):
                    for profile in os.listdir(chrome_cache_base):
                        if profile.startswith('Profile') or profile == 'Default':
                            cache_path = os.path.join(chrome_cache_base, profile, 'Cache')
                            if os.path.exists(cache_path):
                                cache_files.extend(self._scan_directory(cache_path, 'Chrome Cache'))

                # Firefox
                firefox_cache_base = os.path.join(local_appdata, 'Mozilla', 'Firefox', 'Profiles')
                if os.path.exists(firefox_cache_base):
                    for profile in os.listdir(firefox_cache_base):
                        profile_path = os.path.join(firefox_cache_base, profile)
                        if os.path.isdir(profile_path):
                            cache_files.extend(self._scan_directory(profile_path, 'Firefox Cache'))

                # Edge
                edge_cache_base = os.path.join(local_appdata, 'Microsoft', 'Edge', 'User Data')
                if os.path.exists(edge_cache_base):
                    for profile in os.listdir(edge_cache_base):
                        if profile.startswith('Profile') or profile == 'Default':
                            cache_path = os.path.join(edge_cache_base, profile, 'Cache')
                            if os.path.exists(cache_path):
                                cache_files.extend(self._scan_directory(cache_path, 'Edge Cache'))

        else:  # Linux/Mac
            home = os.path.expanduser('~')
            cache_home = os.path.join(home, '.cache')

            # Chrome/Chromium
            for browser in ['google-chrome', 'chromium', 'google-chrome-beta']:
                browser_cache = os.path.join(cache_home, browser)
                if os.path.exists(browser_cache):
                    cache_files.extend(self._scan_directory(browser_cache, f'{browser} Cache'))

            # Firefox
            firefox_cache = os.path.join(home, '.mozilla', 'firefox')
            if os.path.exists(firefox_cache):
                cache_files.extend(self._scan_directory(firefox_cache, 'Firefox Cache'))

        return cache_files

    def scan_system_cache(self) -> List[Dict]:
        """Scanner les caches système"""
        cache_files = []

        if self.system == "Windows":
            # Windows Update cache
            win_update_cache = 'C:\\Windows\\SoftwareDistribution\\Download'
            if os.path.exists(win_update_cache):
                cache_files.extend(self._scan_directory(win_update_cache, 'Windows Update Cache'))

            # Windows prefetch
            prefetch_dir = 'C:\\Windows\\Prefetch'
            if os.path.exists(prefetch_dir):
                cache_files.extend(self._scan_directory(prefetch_dir, 'Windows Prefetch'))

            # Windows Error Reporting
            error_reporting = 'C:\\ProgramData\\Microsoft\\Windows\\WER\\ReportArchive'
            if os.path.exists(error_reporting):
                cache_files.extend(self._scan_directory(error_reporting, 'Windows Error Reports'))

        else:  # Linux
            # Package cache
            package_caches = ['/var/cache/apt/archives', '/var/cache/yum', '/var/cache/dnf']
            for cache_dir in package_caches:
                if os.path.exists(cache_dir):
                    cache_files.extend(self._scan_directory(cache_dir, 'Package Cache'))

            # Log files
            log_dirs = ['/var/log', '/home', '/tmp']
            for log_dir in log_dirs:
                if os.path.exists(log_dir):
                    cache_files.extend(self._scan_directory(log_dir, 'System Logs', include_patterns=['*.log']))

        return cache_files

    def scan_temp_files(self, paths: List[str]) -> List[Dict]:
        """Scanner les chemins pour trouver les fichiers temporaires"""
        temp_files = []

        for path in paths:
            if not os.path.exists(path):
                continue

            if os.path.isdir(path):
                temp_files.extend(self._scan_directory(path, 'Temp Files'))
            else:
                if self._is_temp_file(path):
                    file_info = self._get_file_info(path, 'Temp File')
                    if file_info:
                        temp_files.append(file_info)

        return temp_files

    def scan_user_temp_dirs(self) -> List[Dict]:
        """Scanner les répertoires temporaires utilisateur"""
        temp_files = []

        # Scanner le dossier temp de l'utilisateur
        user_temp = tempfile.gettempdir()
        if os.path.exists(user_temp):
            temp_files.extend(self._scan_directory(user_temp, 'User Temp'))

        # Scanner les dossiers récents
        if self.system == "Windows":
            recent = os.path.join(os.environ.get('APPDATA', ''), 'Microsoft', 'Windows', 'Recent')
            if os.path.exists(recent):
                temp_files.extend(self._scan_directory(recent, 'Recent Files'))

        return temp_files

    def _scan_directory(self, directory: str, source: str,
                       include_patterns: List[str] = None) -> List[Dict]:
        """Scanner un répertoire pour trouver les fichiers temporaires"""
        files = []

        try:
            for entry in os.scandir(directory):
                if entry.is_file():
                    # Vérifier si c'est un fichier temporaire
                    if self._is_temp_file(entry.path):
                        if include_patterns:
                            # Vérifier les patterns d'inclusion
                            if any(glob.fnmatch.fnmatch(entry.name, pattern) for pattern in include_patterns):
                                file_info = self._get_file_info(entry.path, source)
                                if file_info:
                                    files.append(file_info)
                        else:
                            file_info = self._get_file_info(entry.path, source)
                            if file_info:
                                files.append(file_info)
                elif entry.is_dir() and not entry.name.startswith('.'):
                    # Récursif pour les sous-dossiers (limite de profondeur)
                    try:
                        sub_files = self._scan_directory(entry.path, source, include_patterns)
                        files.extend(sub_files)
                    except (PermissionError, OSError):
                        # Ignorer les dossiers sans permission
                        continue

        except (PermissionError, OSError):
            # Ignorer les dossiers sans permission
            pass

        return files

    def _is_temp_file(self, filepath: str) -> bool:
        """Vérifier si un fichier est temporaire"""
        filename = os.path.basename(filepath)
        file_ext = os.path.splitext(filename)[1].lower()

        # Vérifier l'extension
        if file_ext in self.temp_extensions:
            return True

        # Vérifier les patterns de noms de fichiers
        temp_patterns = [
            '~',  # Fichiers temporaires Windows
            'tmp',  # Fichiers temporaires
            'temp',  # Fichiers temporaires
            '.lock',  # Fichiers de verrouillage
            '.pid',  # Fichiers PID
        ]

        for pattern in temp_patterns:
            if pattern in filename.lower():
                return True

        # Vérifier les attributs de fichier caché/temporaire (Windows)
        if self.system == "Windows":
            try:
                import win32api
                import win32con
                attrs = win32api.GetFileAttributes(filepath)
                if attrs & (win32con.FILE_ATTRIBUTE_TEMPORARY | win32con.FILE_ATTRIBUTE_HIDDEN):
                    return True
            except:
                pass

        return False

    def _get_file_info(self, filepath: str, source: str) -> Dict:
        """Obtenir les informations d'un fichier"""
        try:
            stat_info = os.stat(filepath)
            return {
                'path': filepath,
                'name': os.path.basename(filepath),
                'size': stat_info.st_size,
                'size_formatted': self.format_size(stat_info.st_size),
                'modified': stat_info.st_mtime,
                'source': source,
                'type': 'file'
            }
        except (OSError, PermissionError):
            return None

    def get_total_size(self, files: List[Dict]) -> int:
        """Calculer la taille totale des fichiers"""
        return sum(file.get('size', 0) for file in files)

    def filter_by_size(self, files: List[Dict], min_size: int = 0) -> List[Dict]:
        """Filtrer les fichiers par taille minimale"""
        return [f for f in files if f.get('size', 0) >= min_size]

    def filter_by_age(self, files: List[Dict], days_old: int = 0) -> List[Dict]:
        """Filtrer les fichiers par âge (en jours)"""
        import time
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        return [f for f in files if f.get('modified', 0) <= cutoff_time]