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
#   This PlugIn adds the ability to save a shortcut to a project that
#   is located in the Resolve database.  This will create a .vbs file that contains
#   the project path, and simple code to start Resolve and navigate to the project.
#
####################################################


import os
import logging
import subprocess

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from PrismUtils.Decorators import err_catcher_plugin as err_catcher

logger = logging.getLogger(__name__)                #   TODO  add logging



class Prism_ResolveShortcuts_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin

        self.resolvePlugin = self.core.getPlugin("Resolve")                     #   TODO    NEEDED???

        #   Global Settings File
        self.pluginLocation = os.path.dirname(os.path.dirname(__file__))
        self.settingsFile = os.path.join(self.pluginLocation, "ResolveShortcuts_Config.txt")

        #   Callbacks
        logger.debug("Loading callbacks")
        self.core.registerCallback("userSettings_loadUI", self.userSettings_loadUI, plugin=self, priority=40)
        self.core.registerCallback("onUserSettingsSave", self.saveSettings, plugin=self)

        #   Add RCL menu item only in Resolve
        if self.core.appPlugin.pluginName == "Resolve":
            self.core.registerCallback("openPBFileContextMenu", self.addShortcutItem, plugin=self)

        self.loadSettings()



    # if returns true, the plugin will be loaded by Prism
    @err_catcher(name=__name__)
    def isActive(self):
        return True

    #   Load settings from plain text file due to using .vbs for the shortcut file.
    @err_catcher(name=__name__)
    def loadSettings(self):

                                                            #   TODO  IF FILE CORRUPT OR DOES NOT EXIST

        self.configData = {}
        if os.path.isfile(self.settingsFile):
            with open(self.settingsFile, 'r') as file:
                for line in file:
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', 1)
                        self.configData[key.strip()] = value.strip()
        else:
            logger.warning(f"Settings file {self.settingsFile} not found.")

    #   Save settings to plain text file due to using .vbs for the shortcut file.
    @err_catcher(name=__name__)
    def saveSettings(self, origin):
        pData = {
            "python_exe_path": self.e_prismPython.text(),
            "plugin_path": self.e_pluginLoc.text(),
            "dvr_script_path": self.e_resolveApiScript.text(),
            "resolve_exe": self.e_resolveEXE.text(),
            "shortcuts_enabled": str(self.chb_enableShortcutFunctions.isChecked())
            }

        try:
            with open(self.settingsFile, 'w') as file:
                for key, value in pData.items():
                    file.write(f"{key}={value}\n")
            logger.info(f"Settings saved to {self.settingsFile}")

        except Exception as e:
            logger.error(f"Failed to save settings to {self.settingsFile}: {e}")



    # #   Called with Callback
    @err_catcher(name=__name__)
    def userSettings_loadUI(self, origin):      #   ADDING "ResolveShortcuts" TO SETTINGS

        # Create a Widget
        origin.w_resolveShortcuts = QWidget()
        lo_resolveShortcuts = QVBoxLayout(origin.w_resolveShortcuts)

        origin.w_resolveShortcuts.setLayout(lo_resolveShortcuts)

        # Make Spacers
        fixed_20_Vspacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        fixed_30_Vspacer = QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed)
        fixed_40_Vspacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed)
        expanding_Vspacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        fixed_60_Hspacer = QSpacerItem(60, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)
        expanding_Hspacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        lo_resolveShortcuts.addItem(fixed_20_Vspacer)

        # ENABLE SHORTCUT FUNCTIONS CHECKBOX
        lo_topBar = QHBoxLayout()
        
        self.chb_enableShortcutFunctions = QCheckBox("Enable Resolve Shortcut Functions")
        lo_topBar.addWidget(self.chb_enableShortcutFunctions)

        lo_topBar.addItem(expanding_Hspacer)

        l_enviroVarSet = QLabel("Enviro Variable:  ")
        lo_topBar.addWidget(l_enviroVarSet)

        self.l_enviroStatus = QLabel("NOT SET")
        lo_topBar.addWidget(self.l_enviroStatus)

        self.but_setEnviroVar = QPushButton("Set")
        self.but_setEnviroVar.clicked.connect(self.setEnviroVar)
        lo_topBar.addWidget(self.but_setEnviroVar)

        self.but_removeEnviroVar = QPushButton("Remove")
        self.but_removeEnviroVar.clicked.connect(self.removeEnviroVar)
        lo_topBar.addWidget(self.but_removeEnviroVar)

        lo_resolveShortcuts.addLayout(lo_topBar)

        # RESOLVE CONFIG GROUP BOX
        self.gb_resolveConfig = QGroupBox()
        lo_resolveConfig = QVBoxLayout(self.gb_resolveConfig)

        # RESOLVE EXE SECTION
        l_resolveExecutable = QLabel("DaVinci Resolve executable:")
        lo_resolveConfig.addWidget(l_resolveExecutable)

        lo_resolveEXE = QHBoxLayout()
        self.e_resolveEXE = QLineEdit()
        lo_resolveEXE.addWidget(self.e_resolveEXE)

        but_browseResolveEXE = QPushButton("Browse")
        but_browseResolveEXE.clicked.connect(lambda: self.browseFiles(target=self.e_resolveEXE, type="file", title="Select the Resolve Executable"))
        lo_resolveEXE.addWidget(but_browseResolveEXE)
        lo_resolveConfig.addLayout(lo_resolveEXE)

        l_resolveExample = QLabel("             (example:  C:/Program Files/Blackmagic Design/DaVinci Resolve/Resolve.exe)")
        lo_resolveConfig.addWidget(l_resolveExample)


        lo_resolveConfig.addItem(fixed_20_Vspacer)


        # RESOLVE API SECTION
        l_dvrScriptPath = QLabel("Directory containing Davinci Resolve Python API Script:")
        lo_resolveConfig.addWidget(l_dvrScriptPath)

        lo_resolveApiScript = QHBoxLayout()
        self.e_resolveApiScript = QLineEdit()
        lo_resolveApiScript.addWidget(self.e_resolveApiScript)

        but_browseResolveApiScript = QPushButton("Browse")
        but_browseResolveApiScript.clicked.connect(lambda: self.browseFiles(target=self.e_resolveApiScript, type="folder", title="Select the API Directory"))
        lo_resolveApiScript.addWidget(but_browseResolveApiScript)
        lo_resolveConfig.addLayout(lo_resolveApiScript)

        l_apiScriptExample = QLabel("             (example:  C:/ProgramData/Blackmagic Design/DaVinci Resolve/Support/Developer/Scripting/Modules)")
        lo_resolveConfig.addWidget(l_apiScriptExample)


        lo_resolveConfig.addItem(fixed_20_Vspacer)


        # PRISM PYTHON SECTION
        l_prismPython = QLabel("Prism's Python Executable:")
        lo_resolveConfig.addWidget(l_prismPython)

        lo_prismPython = QHBoxLayout()
        self.e_prismPython = QLineEdit()
        lo_prismPython.addWidget(self.e_prismPython)

        but_browsePrismPython = QPushButton("Browse")
        but_browsePrismPython.clicked.connect(lambda: self.browseFiles(target=self.e_prismPython, type="file", title="Select Prism's Python.exe"))
        lo_prismPython.addWidget(but_browsePrismPython)
        lo_resolveConfig.addLayout(lo_prismPython)

        l_prismPythonExample = QLabel("             (example:  C:/Prism2/Python311/python.exe)")
        lo_resolveConfig.addWidget(l_prismPythonExample)


        lo_resolveConfig.addItem(fixed_20_Vspacer)


        # PLUGIN LOCATION SECTION
        l_pluginLoc = QLabel("Resolve Shortcuts Plugin Location:")
        lo_resolveConfig.addWidget(l_pluginLoc)

        lo_pluginLoc = QHBoxLayout()
        self.e_pluginLoc = QLineEdit()
        lo_pluginLoc.addWidget(self.e_pluginLoc)

        but_browsePluginLoc = QPushButton("Browse")
        but_browsePluginLoc.clicked.connect(lambda: self.browseFiles(target=self.e_pluginLoc, type="folder", title="Select Shortcuts Plugin Directory"))
        lo_pluginLoc.addWidget(but_browsePluginLoc)
        lo_resolveConfig.addLayout(lo_pluginLoc)

        l_pluginLocExample = QLabel("             (example:  C:/ProgramData/Prism2/plugins/CustomPlugins/ResolveShortcuts)")
        lo_resolveConfig.addWidget(l_pluginLocExample)


        lo_resolveConfig.addItem(fixed_20_Vspacer)


        # RESET SECTION
        lo_reset = QHBoxLayout()
        lo_reset.addItem(expanding_Hspacer)

        l_reset = QLabel("Reset Locations to default:  ")
        lo_reset.addWidget(l_reset)

        but_reset = QPushButton("Reset")
        but_reset.clicked.connect(self.resetPaths)
        lo_reset.addWidget(but_reset)
        lo_reset.addItem(fixed_60_Hspacer)
        lo_resolveConfig.addLayout(lo_reset)

        lo_resolveShortcuts.addWidget(self.gb_resolveConfig)

        # Add an expanding spacer at the bottom
        lo_resolveShortcuts.addItem(expanding_Vspacer)

        #   Tooltips
        tip = "Globally enable the Resolve Shortcuts functionality."
        self.chb_enableShortcutFunctions.setToolTip(tip)

        tip = ("Status of the system environment variable (DVR_shortcuts_path).\n"
               "The enviro variable must be set to use the shortcut functions." )
        l_enviroVarSet.setToolTip(tip)
        self.l_enviroStatus.setToolTip(tip)

        tip = ("Add the required system environment variable.\n"
               "Prism will automatically exit and must be manually restarted.")
        self.but_setEnviroVar.setToolTip(tip)

        tip = ("Remove the system environment variable.\n"
               "Prism will automatically exit and must be manually restarted.")
        self.but_removeEnviroVar.setToolTip(tip)

        tip = ("Location of Davinci Resolve's main executable.\n\n"
               "Should be automantically set during plugin load.")
        l_resolveExecutable.setToolTip(tip)
        self.e_resolveEXE.setToolTip(tip)
        but_browseResolveEXE.setToolTip(tip)

        tip = ("Location of the Resolve API script that is included\n"
               "with Davinci Resolve.\n"
               "(DaVinciResolveScript.py)\n\n"
               "Should be automantically set during plugin load.")
        l_dvrScriptPath.setToolTip(tip)
        self.e_resolveApiScript.setToolTip(tip)
        but_browseResolveApiScript.setToolTip(tip)

        tip = ("Location of Prism's Python executable (python.exe)\n"
               "Note:  Other python3 exe's might work.\n\n"
               "Should be automantically set during plugin load.")
        l_prismPython.setToolTip(tip)
        self.e_prismPython.setToolTip(tip)
        but_browsePrismPython.setToolTip(tip)

        tip = ("Location of Resolve Shortcuts plugin directory.\n\n"
               "Should be automantically set during plugin load.")
        l_pluginLoc.setToolTip(tip)
        self.e_pluginLoc.setToolTip(tip)

        tip = "Force regeneration of the default paths."
        l_reset.setToolTip(tip)
        but_reset.setToolTip(tip)

        self.loadValues()
        self.refreshUI()

        self.chb_enableShortcutFunctions.toggled.connect(self.refreshUI)

        # Add Tab to User Settings
        origin.addTab(origin.w_resolveShortcuts, "Resolve Shortcuts")


    @err_catcher(name=__name__)
    def loadValues(self):

        if "resolve_exe" in self.configData:
            self.e_resolveEXE.setText(self.configData["resolve_exe"])

        if "dvr_script_path" in self.configData:
            self.e_resolveApiScript.setText(self.configData["dvr_script_path"])

        if "python_exe_path" in self.configData:
            self.e_prismPython.setText(self.configData["python_exe_path"])

        if "plugin_path" in self.configData:
            self.e_pluginLoc.setText(self.configData["plugin_path"])

        if "shortcuts_enabled" in self.configData:
            if self.configData["shortcuts_enabled"] == "True":
                checked = True
            else:
                checked = False
            self.chb_enableShortcutFunctions.setChecked(checked)






    #   File browser
    @err_catcher(name=__name__)
    def browseFiles(self, target, type='file', title='Select File or Folder'):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        if type == 'file':
            filePath, _ = QFileDialog.getOpenFileName(None, title, "", "All Files (*);;Python Files (*.py)", options=options)
        elif type == 'folder':
            filePath = QFileDialog.getExistingDirectory(None, title, "", options=options)
        else:
            print("Invalid type specified. Use 'file' or 'folder'.")
            return

        if filePath:
            target.setText(filePath)


    @err_catcher(name=__name__)
    def refreshUI(self, *args):
        set = self.checkEnviroVar()

        if set:
            self.l_enviroStatus.setText("SET")
            self.but_setEnviroVar.hide()
            self.but_removeEnviroVar.show()
        else:
            self.l_enviroStatus.setText("NOT SET")
            self.but_setEnviroVar.show()
            self.but_removeEnviroVar.hide()

        enabled = self.chb_enableShortcutFunctions.isChecked()
        
        if set and enabled:
            self.gb_resolveConfig.setEnabled(True)
        else:
            self.gb_resolveConfig.setEnabled(False)
        

    @err_catcher(name=__name__)
    def checkEnviroVar(self):
        return 'DVR_shortcuts_path' in os.environ


    @err_catcher(name=__name__)
    def setEnviroVar(self):
        try:
            text = ("Prism will need to shutdown for the environment\n"
                    "variable to be set.  Afterwards you will need to\n"
                     "manually restart Prism.\n\n"
                     "Do you want to set the variable?"
                     )
            title = "Set Environment Variable"
            result = self.core.popupQuestion(text=text, title=title)

            if result == "Yes":
                subprocess.run(['setx', 'DVR_shortcuts_path', self.pluginLocation], check=True)
                self.core.PrismTray.exitTray()

        except Exception as e:
            self.core.popup("Failed")
        

    @err_catcher(name=__name__)
    def removeEnviroVar(self):
        try:
            text = ("Prism will need to shutdown for the environment\n"
                    "variable to be set.  Afterwards you will need to\n"
                     "manually restart Prism.\n\n"
                     "Do you want to set the variable?"
                     )
            title = "Set Environment Variable"
            result = self.core.popupQuestion(text=text, title=title)

            if result == "Yes":
                subprocess.run(['setx', 'DVR_shortcuts_path', ""], check=True)
                self.core.PrismTray.exitTray()

        except Exception as e:
            self.core.popup("Failed")


    @err_catcher(name=__name__)
    def resetPaths(self):
        pass
 


    @err_catcher(name=__name__)
    def addShortcutItem(self, origin, rcmenu, filePath):
        #   Adds Right Click Item
        shortcutAct = QAction("Save Shortcut to Resolve Project", rcmenu)
        shortcutAct.triggered.connect(lambda: self.saveShortcut(origin))
        rcmenu.addAction(shortcutAct)


    @err_catcher(name=__name__)
    def saveShortcut(self, origin):
        try:
            from DvResolve_Project_Shortcuts import ResolveProjectShortcuts
        except Exception as e:
            self.core.popup("Failed")
        
        entity = origin.getCurrentEntity()
        curDep = origin.getCurrentDepartment()
        curTask = origin.getCurrentTask()
        savePath = origin.core.generateScenePath(entity=entity,
                                                 department=curDep,
                                                 task=curTask,
                                                 comment=None,
                                                 extension=".vbs",
                                                 # location=location
                                                 )


        #   TODO Thumbnail


        shortcuts = ResolveProjectShortcuts()
        currProjectName, result = shortcuts.saveProjectShortcut(savePath)

        detailData = {}
        detailData["description"] = f'Shortcut to   "{currProjectName}"   Resolve project'

        origin.core.saveSceneInfo(savePath, detailData, preview=None)

        origin.refreshScenefiles()

        self.core.popup(result)
