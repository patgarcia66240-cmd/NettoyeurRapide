"""
DiskAnalyzer - Module pour analyser l'utilisation du disque
"""

import os
import shutil
import platform
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Generator
from collections import defaultdict, Counter
import mimetypes

class DiskAnalyzer:
    """Classe pour analyser l'utilisation du disque"""

    def __init__(self):
        """Initialisation de l'analyseur de disque"""
        self.system = platform.system()
        self.large_files_cache = {}
        self.file_types_cache = {}

    @staticmethod
    def format_size(n: int) -> str:
        """Formater une taille en octets en format lisible"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if n < 1024.0:
                return f"{n:.1f} {unit}"
            n /= 1024.0
        return f"{n:.1f} PB"

    def analyze_directory(self, path: str, max_depth: int = 3) -> Dict:
        """Analyser un répertoire pour obtenir les statistiques d'utilisation"""
        if not os.path.exists(path):
            return {}

        try:
            total_size = 0
            file_count = 0
            dir_count = 0
            file_types = Counter()
            largest_files = []

            for root, dirs, files in os.walk(path):
                # Limiter la profondeur
                current_depth = root[len(path):].count(os.sep)
                if current_depth > max_depth:
                    continue

                dir_count += len(dirs)

                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        file_count += 1

                        # Types de fichiers
                        file_ext = os.path.splitext(file)[1].lower()
                        if not file_ext:
                            file_ext = 'no_extension'
                        file_types[file_ext] += 1

                        # Plus grands fichiers
                        if len(largest_files) < 100 or file_size > largest_files[-1]['size']:
                            largest_files.append({
                                'path': file_path,
                                'name': file,
                                'size': file_size,
                                'size_formatted': self.format_size(file_size),
                                'extension': file_ext
                            })
                            largest_files.sort(key=lambda x: x['size'], reverse=True)
                            if len(largest_files) > 100:
                                largest_files.pop()

                    except (OSError, PermissionError):
                        continue

            return {
                'path': path,
                'name': os.path.basename(path),
                'total_size': total_size,
                'size_formatted': self.format_size(total_size),
                'file_count': file_count,
                'dir_count': dir_count,
                'file_types': dict(file_types.most_common()),
                'largest_files': largest_files[:50],  # Top 50
                'analyzed_at': time.time()
            }

        except (OSError, PermissionError):
            return {}

    def get_directory_size(self, path: str) -> int:
        """Obtenir la taille d'un répertoire"""
        total_size = 0

        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                    except (OSError, PermissionError):
                        continue
        except (OSError, PermissionError):
            pass

        return total_size

    def get_largest_files(self, path: str, limit: int = 50, min_size: int = 1024*1024) -> List[Dict]:
        """Obtenir les plus grands fichiers dans un répertoire"""
        cache_key = f"{path}_{limit}_{min_size}"

        # Vérifier le cache
        if cache_key in self.large_files_cache:
            cache_time, cached_files = self.large_files_cache[cache_key]
            if time.time() - cache_time < 300:  # Cache de 5 minutes
                return cached_files[:limit]

        largest_files = []

        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)

                        if file_size >= min_size:
                            largest_files.append({
                                'path': file_path,
                                'name': file,
                                'size': file_size,
                                'size_formatted': self.format_size(file_size),
                                'directory': root,
                                'extension': os.path.splitext(file)[1].lower()
                            })

                    except (OSError, PermissionError):
                        continue

        except (OSError, PermissionError):
            pass

        # Trier par taille
        largest_files.sort(key=lambda x: x['size'], reverse=True)

        # Mettre en cache
        self.large_files_cache[cache_key] = (time.time(), largest_files)

        return largest_files[:limit]

    def get_file_types_distribution(self, path: str) -> Dict[str, Dict]:
        """Obtenir la distribution des types de fichiers"""
        cache_key = f"{path}_types"

        # Vérifier le cache
        if cache_key in self.file_types_cache:
            cache_time, cached_types = self.file_types_cache[cache_key]
            if time.time() - cache_time < 600:  # Cache de 10 minutes
                return cached_types

        file_stats = defaultdict(lambda: {'count': 0, 'size': 0})

        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)
                        file_ext = os.path.splitext(file)[1].lower()

                        if not file_ext:
                            file_ext = 'no_extension'

                        file_stats[file_ext]['count'] += 1
                        file_stats[file_ext]['size'] += file_size

                    except (OSError, PermissionError):
                        continue

        except (OSError, PermissionError):
            pass

        # Calculer les pourcentages et formater
        total_files = sum(stats['count'] for stats in file_stats.values())
        total_size = sum(stats['size'] for stats in file_stats.values())

        result = {}
        for ext, stats in file_stats.items():
            result[ext] = {
                'count': stats['count'],
                'size': stats['size'],
                'size_formatted': self.format_size(stats['size']),
                'count_percentage': (stats['count'] / total_files * 100) if total_files > 0 else 0,
                'size_percentage': (stats['size'] / total_size * 100) if total_size > 0 else 0,
                'description': self._get_file_type_description(ext)
            }

        # Mettre en cache
        self.file_types_cache[cache_key] = (time.time(), result)

        return dict(sorted(result.items(), key=lambda x: x[1]['size'], reverse=True))

    def get_disk_usage(self, path: str) -> Dict:
        """Obtenir l'utilisation du disque pour un chemin donné"""
        try:
            if self.system == "Windows":
                # Utiliser os.statvfs n'est pas disponible sur Windows
                drive = os.path.splitdrive(os.path.abspath(path))[0] + '\\'

                # Utiliser shutil.disk_usage qui fonctionne sur Windows
                total, used, free = shutil.disk_usage(drive)

                return {
                    'drive': drive,
                    'total': total,
                    'used': used,
                    'free': free,
                    'total_formatted': self.format_size(total),
                    'used_formatted': self.format_size(used),
                    'free_formatted': self.format_size(free),
                    'usage_percentage': (used / total * 100) if total > 0 else 0
                }
            else:
                # Linux/Mac
                stat = os.statvfs(path)
                total = stat.f_blocks * stat.f_frsize
                free = stat.f_bfree * stat.f_frsize
                used = total - free

                return {
                    'path': path,
                    'total': total,
                    'used': used,
                    'free': free,
                    'total_formatted': self.format_size(total),
                    'used_formatted': self.format_size(used),
                    'free_formatted': self.format_size(free),
                    'usage_percentage': (used / total * 100) if total > 0 else 0
                }

        except (OSError, PermissionError):
            return {
                'path': path,
                'total': 0,
                'used': 0,
                'free': 0,
                'total_formatted': '0 B',
                'used_formatted': '0 B',
                'free_formatted': '0 B',
                'usage_percentage': 0
            }

    def get_directory_tree(self, path: str, max_depth: int = 2, min_size: int = 1024*1024) -> List[Dict]:
        """Obtenir une arborescence des répertoires avec leurs tailles"""
        if not os.path.exists(path) or not os.path.isdir(path):
            return []

        directories = []

        try:
            for root, dirs, files in os.walk(path):
                current_depth = root[len(path):].count(os.sep)
                if current_depth >= max_depth:
                    continue

                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    try:
                        dir_size = self.get_directory_size(dir_path)

                        if dir_size >= min_size:
                            directories.append({
                                'path': dir_path,
                                'name': dir_name,
                                'size': dir_size,
                                'size_formatted': self.format_size(dir_size),
                                'depth': current_depth + 1,
                                'parent': root
                            })
                    except (OSError, PermissionError):
                        continue

        except (OSError, PermissionError):
            pass

        return sorted(directories, key=lambda x: x['size'], reverse=True)

    def find_duplicate_files(self, path: str, min_size: int = 1024) -> Dict[str, List[Dict]]:
        """Trouver les fichiers en double basés sur leur taille et contenu"""
        if not os.path.exists(path):
            return {}

        # Grouper les fichiers par taille
        size_groups = defaultdict(list)

        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)

                        if file_size >= min_size:
                            size_groups[file_size].append({
                                'path': file_path,
                                'name': file,
                                'size': file_size
                            })
                    except (OSError, PermissionError):
                        continue

        except (OSError, PermissionError):
            pass

        # Vérifier les doublons potentiels (même taille)
        duplicates = {}
        for size, files in size_groups.items():
            if len(files) > 1:
                # Pour une vérification plus précise, on pourrait vérifier le hash
                # mais pour l'instant, on se base sur la taille
                duplicates[f"size_{size}"] = files

        return duplicates

    def get_drive_list(self) -> List[Dict]:
        """Obtenir la liste des disques disponibles"""
        drives = []

        if self.system == "Windows":
            import win32api
            import win32file

            # Obtenir les lettres de lecteur
            drives_list = win32api.GetLogicalDriveStrings()
            drives_list = drives_list.split('\000')[:-1]  # Supprimer le dernier élément vide

            for drive in drives_list:
                try:
                    if win32file.GetDriveType(drive) != win32file.DRIVE_NO_ROOT_DIR:
                        total, used, free = shutil.disk_usage(drive)
                        drives.append({
                            'letter': drive,
                            'name': self._get_drive_name(drive),
                            'total': total,
                            'used': used,
                            'free': free,
                            'total_formatted': self.format_size(total),
                            'used_formatted': self.format_size(used),
                            'free_formatted': self.format_size(free),
                            'usage_percentage': (used / total * 100) if total > 0 else 0
                        })
                except:
                    continue
        else:
            # Linux/Mac - points de montage principaux
            mount_points = ['/', '/home', '/var', '/tmp', '/usr']
            for mount in mount_points:
                if os.path.exists(mount):
                    try:
                        total, used, free = shutil.disk_usage(mount)
                        drives.append({
                            'path': mount,
                            'name': mount,
                            'total': total,
                            'used': used,
                            'free': free,
                            'total_formatted': self.format_size(total),
                            'used_formatted': self.format_size(used),
                            'free_formatted': self.format_size(free),
                            'usage_percentage': (used / total * 100) if total > 0 else 0
                        })
                    except:
                        continue

        return drives

    def _get_file_type_description(self, extension: str) -> str:
        """Obtenir une description pour un type de fichier"""
        type_descriptions = {
            '.txt': 'Fichier texte',
            '.pdf': 'Document PDF',
            '.doc': 'Document Word',
            '.docx': 'Document Word',
            '.xls': 'Feuille de calcul Excel',
            '.xlsx': 'Feuille de calcul Excel',
            '.jpg': 'Image JPEG',
            '.jpeg': 'Image JPEG',
            '.png': 'Image PNG',
            '.gif': 'Image GIF',
            '.mp4': 'Vidéo MP4',
            '.avi': 'Vidéo AVI',
            '.mkv': 'Vidéo MKV',
            '.mp3': 'Audio MP3',
            '.wav': 'Audio WAV',
            '.zip': 'Archive ZIP',
            '.rar': 'Archive RAR',
            '.7z': 'Archive 7-Zip',
            '.exe': 'Exécutable Windows',
            '.dll': 'Bibliothèque Windows',
            '.log': 'Fichier journal',
            '.tmp': 'Fichier temporaire',
            'no_extension': 'Sans extension'
        }
        return type_descriptions.get(extension.lower(), f'Fichier {extension}')

    def _get_drive_name(self, drive: str) -> str:
        """Obtenir le nom d'un lecteur Windows"""
        try:
            import win32api
            import win32file

            # Obtenir le nom du volume
            volume_name_buffer = win32file.GetVolumeInformation(drive)[0]
            if volume_name_buffer:
                return f"{drive} ({volume_name_buffer})"
            return drive
        except:
            return drive

    def clear_cache(self):
        """Vider les caches"""
        self.large_files_cache.clear()
        self.file_types_cache.clear()