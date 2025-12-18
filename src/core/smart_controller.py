#!/usr/bin/env python3
"""
SmartControllerThread - Thread pour le contrôle SMART des disques avec données réelles
"""

import sys
from PySide6.QtCore import QThread, Signal

from .smart_data import read_windows_ssd, check_smartctl_available, get_health_status, WindowsSsdHealth


class SmartControllerThread(QThread):
    """Thread pour le contrôle SMART des disques avec données réelles"""
    smart_data_received = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, disk_path):
        super().__init__()
        self.disk_path = disk_path

    def run(self):
        """Effectuer le contrôle SMART"""
        try:
            smart_data = self.get_smart_info()
            self.smart_data_received.emit(smart_data)
        except Exception as e:
            self.error_occurred.emit(f"Erreur SMART: {str(e)}")

    def get_smart_info(self):
        """Obtenir les informations SMART du disque avec smartctl"""
        # Vérifier si smartctl est disponible
        if not check_smartctl_available():
            raise RuntimeError("smartctl n'est pas installé. Veuillez installer smartmontools pour obtenir des données SMART réelles.\n\nTéléchargement: https://sourceforge.net/projects/smartmontools/files/smartmontools/")

        try:
            # Obtenir la lettre du lecteur
            if self.disk_path and len(self.disk_path) >= 2 and self.disk_path[1] == ':':
                drive_letter = self.disk_path[0:2]
            else:
                drive_letter = 'C:'  # Défaut

            # Lire les données SMART avec smartctl
            ssd_health = read_windows_ssd(drive_letter)

            # Convertir en format compatible avec l'interface existante
            smart_info = {
                'disk_model': ssd_health.model or 'Modèle inconnu',
                'serial_number': ssd_health.serial or 'Série inconnue',
                'health_status': get_health_status(ssd_health),
                'temperature': f"{ssd_health.temperature_c}°C" if ssd_health.temperature_c else 'Inconnue',
                'power_on_hours': str(ssd_health.power_on_hours) if ssd_health.power_on_hours else 'Inconnu',
                'power_cycles': str(ssd_health.power_cycles) if ssd_health.power_cycles else 'Inconnu',
                'firmware_version': ssd_health.firmware or 'Inconnu',
                'interface_type': ssd_health.protocol or 'Inconnu',
                'device_path': ssd_health.device,

                # NVMe specific
                'percent_used': f"{ssd_health.percent_used}%" if ssd_health.percent_used is not None else None,
                'data_written_gb': f"{ssd_health.data_written_gb} GB" if ssd_health.data_written_gb is not None else None,
                'media_errors': str(ssd_health.media_errors) if ssd_health.media_errors is not None else '0',

                # ATA/SATA specific (pour compatibilité)
                'reallocated_sectors': ssd_health.media_errors if ssd_health.media_errors is not None else 0,
                'pending_sectors': 0,

                # Métadonnées
                'smart_passed': ssd_health.smart_passed,
                'data_source': 'smartctl_real',
            }

            return smart_info

        except Exception as e:
            # Si smartctl échoue, retourner une erreur informative
            if "n'est pas installé" in str(e):
                raise e
            elif "Permission denied" in str(e) or "Access is denied" in str(e):
                raise RuntimeError("Permission refusée. Veuillez exécuter l'application en tant qu'administrateur pour accéder aux données SMART.")
            elif "No such device" in str(e) or "not found" in str(e):
                raise RuntimeError(f"Périphérique non trouvé: {self.disk_path}")
            else:
                raise RuntimeError(f"Erreur lors de la lecture SMART: {str(e)}")