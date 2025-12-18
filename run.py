#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de lancement pour l'application NettoyeurRapide
Utilise l'environnement virtuel venv_pyside6
"""

import sys
import os
import subprocess

def main():
    # Vérifier si nous sommes dans le bon répertoire
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(script_dir, "venv_pyside6", "Scripts", "python.exe")

    if not os.path.exists(venv_python):
        print("Erreur: L'environnement virtuel n'a pas été trouvé!")
        print(f"Recherché: {venv_python}")
        return 1

    # Lancer l'application avec l'environnement virtuel
    try:
        main_script = os.path.join(script_dir, "main_qt.py")
        subprocess.run([venv_python, main_script], check=True)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors du lancement: {e}")
        return 1
    except FileNotFoundError:
        print(f"Erreur: Le script main_qt.py n'a pas été trouvé dans {script_dir}")
        return 1

if __name__ == "__main__":
    sys.exit(main())