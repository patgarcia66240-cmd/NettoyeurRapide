"""
ThreadManager - Gestion des threads pour les opérations longues
"""

from PySide6.QtCore import QThread, Signal, QObject
from typing import Any, Callable, Optional
import time
from enum import Enum

class WorkerType(Enum):
    SCAN = "scan"
    CLEAN = "clean"
    ANALYZE = "analyze"
    STARTUP = "startup"

class WorkerSignals(QObject):
    """
    Signaux pour la communication entre le worker et l'interface
    """
    # Signaux de progression
    progress = Signal(int)  # 0-100
    status = Signal(str)   # Message de statut

    # Signaux de résultats
    finished = Signal(object)  # Résultat final
    error = Signal(str)        # Message d'erreur

    # Signaux spécifiques
    files_found = Signal(list)  # Liste des fichiers trouvés
    space_saved = Signal(int)   # Espace économisé (bytes)

    # Signaux de contrôle
    started = Signal()
    stopped = Signal()

class BaseWorker(QThread):
    """
    Classe de base pour les workers threadés
    """

    def __init__(self, worker_type: WorkerType):
        super().__init__()
        self.worker_type = worker_type
        self.signals = WorkerSignals()
        self._is_running = False
        self._should_stop = False

        # Paramètres de l'opération
        self.params = {}

    def setup(self, **kwargs):
        """Configuration des paramètres pour l'opération"""
        self.params.update(kwargs)

    def run(self):
        """Exécution principale du thread"""
        self._is_running = True
        self._should_stop = False
        self.signals.started.emit()

        try:
            result = self._execute()
            if not self._should_stop:
                self.signals.finished.emit(result)
        except Exception as e:
            if not self._should_stop:
                self.signals.error.emit(str(e))
        finally:
            self._is_running = False
            self.signals.stopped.emit()

    def stop(self):
        """Arrêt propre du thread"""
        self._should_stop = True
        self.wait(5000)  # Attendre max 5 secondes

    def is_running(self) -> bool:
        """Vérifie si le thread est en cours d'exécution"""
        return self._is_running

    def _execute(self):
        """Méthode à implémenter dans les classes filles"""
        raise NotImplementedError

class ScanWorker(BaseWorker):
    """
    Worker pour le scan des fichiers temporaires
    """

    def __init__(self, scanner):
        super().__init__(WorkerType.SCAN)
        self.scanner = scanner

    def _execute(self):
        paths = self.params.get('paths', [])
        scan_types = self.params.get('scan_types', ['temp', 'cache', 'browser'])

        self.signals.status.emit("Recherche des fichiers temporaires...")

        found_files = []
        total_steps = len(paths) * len(scan_types)
        current_step = 0

        for path in paths:
            if self._should_stop:
                return []

            self.signals.status.emit(f"Analyse de: {path}")

            # Scan des fichiers temporaires
            if 'temp' in scan_types:
                temp_files = self.scanner.scan_temp_files([path])
                found_files.extend(temp_files)
                current_step += 1
                self.signals.progress.emit(int((current_step / total_steps) * 100))
                self.signals.files_found.emit(temp_files)

            if self._should_stop:
                return []

            # Scan des caches
            if 'cache' in scan_types:
                cache_files = self.scanner.scan_system_cache()
                found_files.extend(cache_files)
                current_step += 1
                self.signals.progress.emit(int((current_step / total_steps) * 100))
                self.signals.files_found.emit(cache_files)

            if self._should_stop:
                return []

            # Scan des caches navigateurs
            if 'browser' in scan_types:
                browser_files = self.scanner.scan_browser_cache()
                found_files.extend(browser_files)
                current_step += 1
                self.signals.progress.emit(int((current_step / total_steps) * 100))
                self.signals.files_found.emit(browser_files)

        self.signals.status.emit(f"Scan terminé: {len(found_files)} fichiers trouvés")
        return found_files

class CleanWorker(BaseWorker):
    """
    Worker pour le nettoyage des fichiers
    """

    def __init__(self, cleaner):
        super().__init__(WorkerType.CLEAN)
        self.cleaner = cleaner

    def _execute(self):
        files_to_clean = self.params.get('files', [])

        if not files_to_clean:
            self.signals.error.emit("Aucun fichier à nettoyer")
            return []

        self.signals.status.emit(f"Nettoyage de {len(files_to_clean)} fichiers...")

        cleaned_files = []
        total_space_saved = 0

        for i, file_path in enumerate(files_to_clean):
            if self._should_stop:
                break

            self.signals.status.emit(f"Nettoyage: {file_path}")

            # Nettoyer le fichier
            result = self.cleaner.clean_files([file_path])
            if result:
                cleaned_files.extend(result)
                total_space_saved += self.cleaner.get_space_saved()

            # Mettre à jour la progression
            progress = int(((i + 1) / len(files_to_clean)) * 100)
            self.signals.progress.emit(progress)

            # Petite pause pour ne pas surcharger le système
            time.sleep(0.01)

        self.signals.space_saved.emit(total_space_saved)
        self.signals.status.emit(f"Nettoyage terminé: {len(cleaned_files)} fichiers supprimés")
        return cleaned_files

class AnalyzeWorker(BaseWorker):
    """
    Worker pour l'analyse de disque
    """

    def __init__(self, analyzer):
        super().__init__(WorkerType.ANALYZE)
        self.analyzer = analyzer

    def _execute(self):
        path = self.params.get('path', 'C:\\')

        self.signals.status.emit(f"Analyse de: {path}")

        # Obtenir l'utilisation du disque
        disk_usage = self.analyzer.get_disk_usage(path)

        if self._should_stop:
            return None

        self.signals.progress.emit(25)
        self.signals.status.emit("Analyse des plus grands fichiers...")

        # Analyser les plus grands fichiers
        large_files = self.analyzer.get_largest_files(path, limit=50)

        if self._should_stop:
            return None

        self.signals.progress.emit(50)
        self.signals.status.emit("Analyse des types de fichiers...")

        # Analyser la distribution des types de fichiers
        file_types = self.analyzer.get_file_types_distribution(path)

        if self._should_stop:
            return None

        self.signals.progress.emit(75)
        self.signals.status.emit("Calcul de la taille du répertoire...")

        # Calculer la taille totale
        total_size = self.analyzer.get_directory_size(path)

        self.signals.progress.emit(100)

        result = {
            'disk_usage': disk_usage,
            'large_files': large_files,
            'file_types': file_types,
            'total_size': total_size
        }

        self.signals.status.emit(f"Analyse terminée: {self.analyzer.format_size(total_size)}")
        return result

class StartupWorker(BaseWorker):
    """
    Worker pour la gestion des programmes au démarrage
    """

    def __init__(self, startup_manager):
        super().__init__(WorkerType.STARTUP)
        self.startup_manager = startup_manager

    def _execute(self):
        action = self.params.get('action', 'list')

        if action == 'list':
            self.signals.status.emit("Récupération des programmes au démarrage...")
            startup_programs = self.startup_manager.get_startup_programs()
            self.signals.progress.emit(100)
            self.signals.status.emit(f"{len(startup_programs)} programmes trouvés")
            return startup_programs

        elif action == 'disable':
            program_name = self.params.get('program_name')
            if not program_name:
                self.signals.error.emit("Nom du programme manquant")
                return False

            self.signals.status.emit(f"Désactivation de: {program_name}")
            result = self.startup_manager.disable_startup_program(program_name)
            self.signals.progress.emit(100)

            if result:
                self.signals.status.emit(f"{program_name} désactivé avec succès")
            else:
                self.signals.error.emit(f"Impossible de désactiver {program_name}")

            return result

        elif action == 'enable':
            program_name = self.params.get('program_name')
            if not program_name:
                self.signals.error.emit("Nom du programme manquant")
                return False

            self.signals.status.emit(f"Activation de: {program_name}")
            result = self.startup_manager.enable_startup_program(program_name)
            self.signals.progress.emit(100)

            if result:
                self.signals.status.emit(f"{program_name} activé avec succès")
            else:
                self.signals.error.emit(f"Impossible d'activer {program_name}")

            return result

class ThreadManager(QObject):
    """
    Gestionnaire centralisé des threads
    """

    def __init__(self):
        super().__init__()
        self.active_workers = {}

    def create_scan_worker(self, scanner) -> ScanWorker:
        """Crée un worker pour le scan"""
        worker = ScanWorker(scanner)
        self.active_workers[id(worker)] = worker
        worker.signals.stopped.connect(lambda: self._cleanup_worker(id(worker)))
        return worker

    def create_clean_worker(self, cleaner) -> CleanWorker:
        """Crée un worker pour le nettoyage"""
        worker = CleanWorker(cleaner)
        self.active_workers[id(worker)] = worker
        worker.signals.stopped.connect(lambda: self._cleanup_worker(id(worker)))
        return worker

    def create_analyze_worker(self, analyzer) -> AnalyzeWorker:
        """Crée un worker pour l'analyse"""
        worker = AnalyzeWorker(analyzer)
        self.active_workers[id(worker)] = worker
        worker.signals.stopped.connect(lambda: self._cleanup_worker(id(worker)))
        return worker

    def create_startup_worker(self, startup_manager) -> StartupWorker:
        """Crée un worker pour la gestion du démarrage"""
        worker = StartupWorker(startup_manager)
        self.active_workers[id(worker)] = worker
        worker.signals.stopped.connect(lambda: self._cleanup_worker(id(worker)))
        return worker

    def stop_all_workers(self):
        """Arrête tous les workers actifs"""
        for worker in list(self.active_workers.values()):
            if worker.is_running():
                worker.stop()

    def _cleanup_worker(self, worker_id):
        """Nettoie un worker terminé"""
        if worker_id in self.active_workers:
            del self.active_workers[worker_id]