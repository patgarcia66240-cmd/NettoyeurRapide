#!/usr/bin/env python3
"""
DiskScannerThread - Thread pour scanner les disques en arrière-plan
"""

import os
from PySide6.QtCore import QThread, Signal


class DiskScannerThread(QThread):
    """Thread pour scanner les disques en arrière-plan"""
    progress_updated = Signal(int, str)
    scan_completed = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, disk_path, scan_type="quick"):
        super().__init__()
        self.disk_path = disk_path
        self.scan_type = scan_type
        self.is_cancelled = False

    def run(self):
        try:
            results = self.scan_directory()
            if not self.is_cancelled:
                self.scan_completed.emit(results)
        except Exception as e:
            if not self.is_cancelled:
                self.error_occurred.emit(str(e))

    def scan_directory(self):
        """Scanner un répertoire et retourner les résultats"""
        results = {
            'total_files': 0,
            'total_size': 0,
            'file_types': {},
            'large_files': [],
            'directories': [],
            'scan_time': None
        }

        try:
            from datetime import datetime
            results['scan_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            max_depth = 2 if self.scan_type == "quick" else 10

            # Émettre progression initiale
            self.progress_updated.emit(0, "Début de l'analyse...")

            self._scan_recursive(self.disk_path, results, 0, max_depth)

            # Trier les gros fichiers
            self.progress_updated.emit(90, "Tri des résultats...")
            results['large_files'].sort(key=lambda x: x[1], reverse=True)
            results['large_files'] = results['large_files'][:20]  # Top 20

            self.progress_updated.emit(100, "Analyse terminée")

        except Exception as e:
            raise Exception(f"Erreur lors du scan: {str(e)}")

        return results

    def _scan_recursive(self, path, results, depth, max_depth):
        """Scanner récursivement les répertoires"""
        if self.is_cancelled or depth > max_depth:
            return

        try:
            items = os.listdir(path)
            total_items = len(items)

            for i, item in enumerate(items):
                if self.is_cancelled:
                    return

                item_path = os.path.join(path, item)
                try:
                    if os.path.isfile(item_path):
                        self._process_file(item_path, results)
                    elif os.path.isdir(item_path):
                        dir_size = self._get_directory_size(item_path)
                        if dir_size > 1024 * 1024:  # > 1MB
                            results['directories'].append((item_path, dir_size))

                        if depth < max_depth:
                            self._scan_recursive(item_path, results, depth + 1, max_depth)
                except (PermissionError, OSError):
                    continue

                # Émettre progression toutes les 50 fichiers ou à la fin du dossier
                if i % 50 == 0 or i == total_items - 1:
                    progress = min(85, int((i + 1) / total_items * 85))  # Max 85% avant le tri
                    current_dir = os.path.basename(path) or path
                    self.progress_updated.emit(progress, f"Analyse de {current_dir} ({i+1}/{total_items})...")

        except (PermissionError, OSError):
            pass

    def _process_file(self, file_path, results):
        """Traiter un fichier individuel"""
        try:
            size = os.path.getsize(file_path)
            results['total_files'] += 1
            results['total_size'] += size

            # Extension du fichier
            ext = os.path.splitext(file_path)[1].lower()
            if not ext:
                ext = "sans_extension"

            if ext not in results['file_types']:
                results['file_types'][ext] = {'count': 0, 'size': 0}

            results['file_types'][ext]['count'] += 1
            results['file_types'][ext]['size'] += size

            # Ajouter aux gros fichiers
            if size > 10 * 1024 * 1024:  # > 10MB
                results['large_files'].append((file_path, size))

        except (PermissionError, OSError):
            pass

    def _get_directory_size(self, path):
        """Obtenir la taille d'un répertoire"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (PermissionError, OSError):
                        continue
        except (PermissionError, OSError):
            pass
        return total_size

    def cancel(self):
        """Annuler le scan"""
        self.is_cancelled = True