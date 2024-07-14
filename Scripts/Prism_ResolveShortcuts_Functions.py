# -*- coding: utf-8 -*-
#
####################################################
#
# PRISM - Pipeline for animation and VFX projects
#
# www.prism-pipeline.com
#
# contact: contact@prism-pipeline.com
#
####################################################
#
#
# Copyright (C) 2016-2023 Richard Frangenberg
# Copyright (C) 2023 Prism Software GmbH
#
# Licensed under GNU LGPL-3.0-or-later
#
# This file is part of Prism.
#
# Prism is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Prism is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Prism.  If not, see <https://www.gnu.org/licenses/>.
#
####################################################
####################################################
#
#         RESOLVE SHORTCUTS PLUGIN
#           by Joshua Breckeen
#                Alta Arts
#
#   This PlugIn adds an additional tab to the Prism Settings menu to 
#   allow a user to choose a directory that contains scene presets.                 #   TODO
#
####################################################


import os
import json
import logging
import subprocess

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from PrismUtils.Decorators import err_catcher_plugin as err_catcher

logger = logging.getLogger(__name__)



class Prism_ResolveShortcuts_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin

        self.resolvePlugin = self.core.getPlugin("Resolve")                     #   TODO

        #   Global Settings File
        self.pluginLocation = os.path.dirname(os.path.dirname(__file__))
        self.settingsFile = os.path.join(self.pluginLocation, "ResolveShortcuts_Config.json")

        #   Callbacks
        logger.debug("Loading callbacks")
        self.core.registerCallback("userSettings_loadUI", self.userSettings_loadUI, plugin=self, priority=40)
        # self.core.registerCallback("onUserSettingsSave", self.saveSettings, plugin=self)

        # self.core.popup(f"plugin:  {self.plugin.pluginName}")                                      #    TESTING

        # if self.plugin.pluginName == "Resolve":
        self.core.registerCallback("openPBFileContextMenu", self.addShortcutItem, plugin=self)

        # if self.plugin.pluginName == "Standalone":
        self.setEnviroVars()


    # if returns true, the plugin will be loaded by Prism
    @err_catcher(name=__name__)
    def isActive(self):
        return True


    @err_catcher(name=__name__)
    def setEnviroVars(self):
        try:
            subprocess.run(['setx', 'DVR_shortcuts_path', self.pluginLocation], check=True)
        except Exception as e:
            self.core.popup("Failed")



    # #   Called with Callback
    @err_catcher(name=__name__)
    def userSettings_loadUI(self, origin):      #   ADDING "ResolveShortcuts" TO SETTINGS

        # Create a Widget
        origin.w_resolveShortcuts = QWidget()
        lo_resolveShortcuts = QVBoxLayout(origin.w_resolveShortcuts)

        origin.w_resolveShortcuts.setLayout(lo_resolveShortcuts)

        #   Send To Menu UI List
        # w_resolveShortcuts = QGroupBox("Resolve Shortcuts")
        # w_resolveShortcuts = QVBoxLayout()
        # w_resolveShortcuts.setLayout(w_resolveShortcuts)


        # self.chb_enableShortcuts = QCheckBox("Enable Resolve Shortcut Functions")

        #   Makes ReadOnly


        # try:
        #     logger.debug("Loading Menu data")

        #     #   Loads Settings File
        #     pData = self.loadSettings()

        #     if "Ignore Default Presets" in pData:
        #         ignorePresets = pData["Ignore Default Presets"]
        #         self.chb_defaultPresets.setChecked(ignorePresets)

        #     if "Paths" in pData:
        #         scenePresetsList = pData["Paths"]

        #     #   Populates lists from Settings File Data
        #     for item in scenePresetsList:
        #         rowPosition = self.tw_scenePresets.rowCount()
        #         self.tw_scenePresets.insertRow(rowPosition)
        #         self.tw_scenePresets.setItem(rowPosition, 0, QTableWidgetItem(item))

        # except Exception as e:
        #     logger.warning(f"Unable to load Scene Preset data:\n{e}")

        # #   Tooltips
        # tip = ("Directories that will hold Preset Scene Files.\n\n"
        #         "These will be available to all projects in addition to the ones\n"
        #         "included in the Project's Pipeline folder."
        #         )
        # self.tw_scenePresets.setToolTip(tip)

        # tip = ("Disables the default Prism scene presets that come with DCC plugins.\n"
        #        "This does not delete the presets from the plugin directories.\n"
        #        "Presets contained in each projects preset dir will still be visable.")
        # self.chb_defaultPresets.setToolTip(tip)

        # tip = "Opens dialogue to choose directory to add."
        # b_addScenePresets.setToolTip(tip)

        # tip = "Remove selected directory."
        # b_removeScenePresets.setToolTip(tip)



        # Add Tab to User Settings
        origin.addTab(origin.w_resolveShortcuts, "Resolve Shortcuts")



    @err_catcher(name=__name__)
    def addShortcutItem(self, origin, rcmenu, filePath):

        #   Adds Right Click Item
        shortcutAct = QAction("Save Project Shortcut", rcmenu)
        shortcutAct.triggered.connect(lambda: self.saveShortcut())
        rcmenu.addAction(shortcutAct)



    @err_catcher(name=__name__)
    def saveShortcut(self):

        try:
            from DvResolve_Project_Shortcuts import ResolveProjectShortcuts
        except Exception as e:
            self.core.popup("Failed")

        # path = r"N:\\Data\\Projects\\Random Practice\\01_Production\\Shots\\090_TearsOfSteel\\010_DollyInManSitting\\Scenefiles\\resolve\\Comp\\090_TearsOfSteel-010_DollyInManSitting_Comp_v002.vbs"

        savePath = self.core.saveScene(prismReq=False)

        self.core.popup(savePath)

        shortcuts = ResolveProjectShortcuts()
        result = shortcuts.saveProjectShortcut(savePath)

        self.core.popup(result)


    def getCurrentFileName(self, origin, path):

        return "C:\DUMMY.txt"
    

    # @err_catcher(name=__name__)
    # def loadSettings(self):
    #     #   Loads Global Settings File JSON
    #     try:
    #         with open(self.settingsFile, "r") as json_file:
    #             pData = json.load(json_file)
    #             return pData
            
    #     except FileNotFoundError:
    #         logger.debug("Settings File not found, creating new")
    #         pData = self.createSettings()
    #         return pData
        
    #     except Exception as e:
    #         logger.warning(f"Settings file is corrupt, creating new")
    #         pData = self.createSettings()
    #         return pData


    # @err_catcher(name=__name__)
    # def createSettings(self):
    #     #   Deletes settings file if corrupt
    #     if os.path.exists(self.settingsFile):
    #         os.remove(self.settingsFile)

    #     #   Makes default pData
    #     pData = {}
    #     pData["Ignore Default Presets"] = False

    #     paths = []
    #     pData["Paths"] = paths

    #     #   Saves to settings JSON File
    #     with open(self.settingsFile, "w") as json_file:
    #         json.dump(pData, json_file, indent=4)
        
    #     return pData


    # @err_catcher(name=__name__)
    # def saveSettings(self, origin=None):

    #     pData = {}

    #     ignorePresets = self.chb_defaultPresets.isChecked()

    #     pData["Ignore Default Presets"] = ignorePresets

    #     paths = []
    #     #   Populates data[] from UI List
    #     for row in range(self.tw_scenePresets.rowCount()):
    #         pathItem = self.tw_scenePresets.item(row, 0)

    #         if pathItem:
    #             location = pathItem.text()
    #             paths.append(location)

    #     pData["Paths"] = paths

    #     #   Saves to Global JSON File
    #     with open(self.settingsFile, "w") as json_file:
    #         json.dump(pData, json_file, indent=4)
