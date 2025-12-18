"""
Plugin Qt Designer pour NavButton
"""

from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from PySide6.QtDesigner import QPyDesignerCustomWidgetPlugin

from src.gui_qt.components.nav_button import NavButton


class NavButtonPlugin(QPyDesignerCustomWidgetPlugin):
    """Plugin Qt Designer pour NavButton"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initialized = False

    def initialize(self, core):
        """Initialiser le plugin"""
        if self.initialized:
            return

        self.initialized = True

    def isInitialized(self):
        """Vérifier si le plugin est initialisé"""
        return self.initialized

    def createWidget(self, parent):
        """Créer une instance du widget"""
        return NavButton(parent)

    def name(self):
        """Nom du widget dans Designer"""
        return "NavButton"

    def group(self):
        """Groupe dans Designer"""
        return "Custom Widgets"

    def toolTip(self):
        """Info-bulle dans Designer"""
        return "Bouton de navigation moderne"

    def whatsThis(self):
        """Description dans Designer"""
        return "Un bouton de navigation stylisé avec différents types et tailles"

    def isContainer(self):
        """Le widget contient-il d'autres widgets"""
        return False

    def icon(self):
        """Icône dans Designer"""
        return QIcon()

    def domXml(self):
        """XML pour Designer"""
        return """
        <widget class="NavButton" name="navButton">
            <property name="geometry">
                <rect>
                    <x>0</x>
                    <y>0</y>
                    <width>100</width>
                    <height>36</height>
                </rect>
            </property>
            <property name="navType">
                <string>primary</string>
            </property>
            <property name="sizeType">
                <string>medium</string>
            </property>
            <property name="iconPosition">
                <string>left</string>
            </property>
            <property name="rounded">
                <bool>true</bool>
            </property>
            <property name="text">
                <string>Button</string>
            </property>
        </widget>
        """

    def includeFile(self):
        """Fichier à inclure"""
        return "src/gui_qt/components/nav_button.py"


# Enregistrer le plugin
plugin_instance = NavButtonPlugin()