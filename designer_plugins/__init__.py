"""
Plugins Qt Designer pour les widgets personnalisés
"""

from .nav_button_plugin import NavButtonPlugin

# Liste des plugins à charger
designer_plugins = [
    NavButtonPlugin,
]

# Enregistrer les plugins
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection

for plugin_class in designer_plugins:
    QPyDesignerCustomWidgetCollection.addCustomWidget(plugin_class())