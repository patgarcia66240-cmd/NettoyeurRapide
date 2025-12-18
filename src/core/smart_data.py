#!/usr/bin/env python3
"""
Module pour la gestion des données SMART avec smartctl
"""

import subprocess
import json
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class WindowsSsdHealth:
    """Structure de données pour les informations SMART du disque"""
    device: str
    model: Optional[str] = None
    serial: Optional[str] = None
    firmware: Optional[str] = None
    protocol: Optional[str] = None
    temperature_c: Optional[int] = None
    power_on_hours: Optional[int] = None
    power_cycles: Optional[int] = None
    percent_used: Optional[int] = None       # NVMe
    data_written_gb: Optional[int] = None    # NVMe
    media_errors: Optional[int] = None
    smart_passed: Optional[bool] = None


def check_smartctl_available():
    """Vérifier si smartctl est disponible"""
    try:
        result = subprocess.run(
            ["smartctl", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def get_device_path_for_drive(drive_letter: str) -> str:
    """Obtenir le chemin du périphérique pour une lettre de lecteur Windows"""
    if sys.platform != 'win32':
        return drive_letter

    try:
        # Méthode PowerShell pour trouver le disque physique
        ps_cmd = f'powershell "Get-PhysicalDisk | Where-Object {{$_.FriendlyName -like \'*{drive_letter}*\' -or $_.DeviceID -like \'*{drive_letter}*\'}} | Select-Object DeviceID | ConvertTo-Json"'
        result = subprocess.run(ps_cmd, shell=True, capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                if isinstance(data, dict) and 'DeviceID' in data:
                    return f"\\\\.\\{data['DeviceID']}"
            except json.JSONDecodeError:
                pass

        # Alternative : essayer directement avec la lettre
        return f"\\\\.\\PhysicalDrive{ord(drive_letter.upper()) - ord('A')}"

    except Exception:
        # Dernière alternative : retourner un format standard
        return f"\\\\.\\PhysicalDrive0"


def read_windows_ssd(device: str) -> WindowsSsdHealth:
    """
    Lire les informations SMART en utilisant smartctl
    device: chemin du périphérique ou lettre de lecteur
    """

    # Si c'est une lettre de lecteur, convertir en chemin de périphérique
    if len(device) == 1 and device.isalpha():
        device_path = get_device_path_for_drive(device)
    else:
        device_path = device

    try:
        # Exécuter smartctl avec format JSON
        result = subprocess.run(
            ["smartctl", "-a", "-j", device_path],
            capture_output=True,
            text=True,
            timeout=30
        )

        # smartctl retourne 0 (succès) ou 2 (warning mais données disponibles)
        if result.returncode not in range(0, 2):
            raise RuntimeError(f"smartctl failed: {result.stderr.strip()}")

        # Parser la sortie JSON
        data = json.loads(result.stdout)

        # Extraire les informations générales
        model = data.get("model_name")
        serial = data.get("serial_number")
        firmware = data.get("firmware_version")
        protocol = data.get("device", {}).get("protocol")

        # Température
        temperature_c = None
        temp_data = data.get("temperature", {})
        if isinstance(temp_data, dict):
            temperature_c = temp_data.get("current")
        elif isinstance(temp_data, (int, float)):
            temperature_c = int(temp_data)

        # Heures de fonctionnement et cycles
        power_on_hours = None
        power_cycles = data.get("power_cycle_count")

        time_data = data.get("power_on_time", {})
        if isinstance(time_data, dict):
            power_on_hours = time_data.get("hours")

        # Statut SMART
        smart_passed = None
        smart_status = data.get("smart_status", {})
        if isinstance(smart_status, dict):
            smart_passed = smart_status.get("passed")

        # Informations spécifiques NVMe
        nvme_data = data.get("nvme_smart_health_information_log", {})
        percent_used = nvme_data.get("percentage_used")
        media_errors = nvme_data.get("media_errors")

        # Calculer les données écrites (en GB)
        data_units_written = nvme_data.get("data_units_written")
        data_written_gb = None
        if isinstance(data_units_written, int):
            # data_units_written est en unités de 512KB, convertir en GB
            data_written_gb = int(data_units_written * 512_000 / 1e9)

        # Informations ATA/SATA (secteurs réalloués, etc.)
        reallocated_sectors = None
        pending_sectors = None

        ata_smart = data.get("ata_smart_attributes", {}).get("table", [])
        if isinstance(ata_smart, list):
            for attr in ata_smart:
                attr_id = attr.get("id")
                if attr_id == 5:  # Reallocated Sectors Count
                    reallocated_sectors = attr.get("raw", {}).get("value")
                elif attr_id == 197:  # Current Pending Sector Count
                    pending_sectors = attr.get("raw", {}).get("value")

        return WindowsSsdHealth(
            device=device_path,
            model=model,
            serial=serial,
            firmware=firmware,
            protocol=protocol,
            temperature_c=temperature_c,
            power_on_hours=power_on_hours,
            power_cycles=power_cycles,
            percent_used=percent_used,
            data_written_gb=data_written_gb,
            media_errors=media_errors,
            smart_passed=smart_passed
        )

    except json.JSONDecodeError as e:
        raise RuntimeError(f"Erreur de parsing JSON smartctl: {e}")
    except subprocess.TimeoutExpired:
        raise RuntimeError("Timeout lors de l'exécution de smartctl")
    except FileNotFoundError:
        raise RuntimeError("smartctl n'est pas installé. Veuillez installer smartmontools.")
    except Exception as e:
        raise RuntimeError(f"Erreur lors de la lecture SMART: {str(e)}")


def get_health_status(ssd_health: WindowsSsdHealth) -> str:
    """
    Déterminer le statut de santé à partir des informations SMART
    """
    if ssd_health.smart_passed is False:
        return "Dégradé"
    elif ssd_health.smart_passed is True:
        # Vérifier les indicateurs d'alerte
        if ssd_health.percent_used and ssd_health.percent_used > 80:
            return "Attention"
        if ssd_health.media_errors and ssd_health.media_errors > 0:
            return "Attention"
        if ssd_health.temperature_c and ssd_health.temperature_c > 70:
            return "Attention"
        return "Bon"
    else:
        return "Inconnu"