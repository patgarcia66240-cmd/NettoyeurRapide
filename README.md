# NettoyeurRapide

Application de nettoyage de disque développée en Python avec PySide6, offrant une analyse complète et un contrôle SMART avancé.

## 🚀 Fonctionnalités

- **Analyse de disque** : Scan rapide, complet ou personnalisé
- **Contrôle SMART** : Données réelles avec smartctl (NVMe/ATA/SATA)
- **Interface moderne** : Design élégant et responsive
- **Filtres avancés** : Tri par type, taille, extension
- **Export des résultats** : Formats texte et CSV
- **Visualisations** : Graphiques camembert et statistiques

## 📋 Prérequis

### Python
- Python 3.8 ou supérieur
- PySide6

### Pour les données SMART (optionnel)
- smartmontools (smartctl)
- Téléchargement : https://sourceforge.net/projects/smartmontools/files/smartmontools/

### Dépendances
```bash
pip install PySide6
```

## 🛠️ Installation

1. **Cloner le repository** :
```bash
git clone https://github.com/patgarcia66240-cmd/NettoyeurRapide.git
cd NettoyeurRapide
```

2. **Installer les dépendances** :
```bash
pip install -r requirements.txt
```

3. **Exécuter l'application** :
```bash
python run.py
```

## 📖 Utilisation

1. **Sélectionner un disque** via le menu déroulant
2. **Choisir le type d'analyse** :
   - Scan Rapide
   - Scan Complet
   - Scan par Type
   - Scan Personnalisé
3. **Lancer l'analyse** avec le bouton "🔍 Analyser"
4. **Explorer les onglets** :
   - Vue d'ensemble
   - Types de fichiers
   - Gros fichiers
   - Dossiers
   - Contrôle SMART

## 🔧 Fonctionnalités techniques

### Analyse de disque
- Scan récursif des dossiers
- Identification des types de fichiers
- Calcul des tailles et statistiques
- Gestion des gros fichiers

### Contrôle SMART
- Support NVMe et ATA/SATA
- Données SMART structurées
- Analyse de la santé du disque
- Recommandations personnalisées

### Interface utilisateur
- Widgets modernes avec PySide6
- Headers cliquables pour le tri
- Filtres temps réel
- Thème sombre élégant

## 📊 Captures d'écran

*(Ajouter des captures d'écran de l'application)*

## 🤝 Contribuer

1. Forker le repository
2. Créer une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commiter les changements (`git commit -m 'Ajouter une fonctionnalité'`)
4. Pousser vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrer une Pull Request

## 📝 License

Ce projet est sous license MIT.

## 📞 Support

Pour toute question ou rapport de bug, veuillez ouvrir une issue sur GitHub.

## 🙏 Crédits

Développé avec ❤️ par patgarcia66240-cmd - 2025
