"""
StartupManager - Module pour gérer les programmes au démarrage
"""

class StartupManager:
    """Classe pour gérer les programmes au démarrage"""

    def __init__(self):
        """Initialisation du gestionnaire de démarrage"""
        pass

    def get_startup_programs(self):
        """Obtenir la liste des programmes au démarrage"""
        return []

    def disable_startup_program(self, program_name):
        """Désactiver un programme au démarrage"""
        return False

    def enable_startup_program(self, program_name):
        """Activer un programme au démarrage"""
        return False

    def remove_startup_program(self, program_name):
        """Supprimer un programme du démarrage"""
        return False

    def add_startup_program(self, program_path, program_name):
        """Ajouter un programme au démarrage"""
        return False