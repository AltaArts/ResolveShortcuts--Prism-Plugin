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
#   A PlugIn that adds the ability to save a shortcut to a project that
#   is located in the Resolve database.  This will create a .vbs file that contains
#   the project path, and simple code to start Resolve and navigate to the project.
#   Prism's ProjectBrowser launched from Resolve will contain a right-click menu
#   item to save the shortcut.
#
####################################################


import os
import glob
import logging
import subprocess
import tempfile

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from PrismUtils.Decorators import err_catcher_plugin as err_catcher

logger = logging.getLogger(__name__)



class Prism_ResolveShortcuts_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin
        self.shortcutsEnabled = False
        self.useIcon = False

        #   Settings File
        self.pluginLocation = os.path.dirname(os.path.dirname(__file__))
        self.settingsFile = os.path.join(self.pluginLocation, "ResolveShortcuts_Config.txt")

        self.loadSettings()

        #   Callbacks
        logger.debug("Loading callbacks")
        self.core.registerCallback("userSettings_loadUI", self.userSettings_loadUI, plugin=self)
        self.core.registerCallback("onUserSettingsSave", self.saveSettings, plugin=self)
        self.core.registerCallback("getIconPathForFileType", self.setIcon, plugin=self)
        #   Add RCL menu item only in Resolve
        if self.core.appPlugin.pluginName == "Resolve":
            self.core.registerCallback("openPBFileContextMenu", self.addShortcutItem, plugin=self)


    # if returns true, the plugin will be loaded by Prism
    @err_catcher(name=__name__)
    def isActive(self):
        return True


    #   Will use the custom icon for .vbs files if enabled
    @err_catcher(name=__name__)
    def setIcon(self, extension):
        if self.shortcutsEnabled and self.useIcon:
            try:
                if extension == ".vbs":
                    icon = os.path.join(self.pluginLocation, "UserInterfaces", "ResolveShortcuts.ico")
                    logger.debug("Loaded ResolveShortcut Icon")
                    return icon
            except FileNotFoundError:
                logger.warning("ResolveShortcut Icon missing")
            except Exception as e:
                logger.warning(f"ERROR: {e}")

        return None


    #   Load settings from plain text file due to using .vbs for the shortcut file.
    @err_catcher(name=__name__)
    def loadSettings(self):
        #   Parses plain text into dict
        if os.path.isfile(self.settingsFile):
            try:
                self.configData = {}
                with open(self.settingsFile, 'r') as file:
                    for line in file:
                        line = line.strip()
                        if '=' in line:
                            key, value = line.split('=', 1)
                            self.configData[key.strip()] = value.strip()
                logger.debug("Config loaded")
            except:
                logger.warning("Setting file is corrupt")
                self.makeSettings()
        else:
            logger.warning(f"Settings file {self.settingsFile} not found.")
            self.makeSettings()

        #   Sets enabled variable
        self.shortcutsEnabled = False
        if "shortcuts_enabled" in self.configData:
            if self.configData["shortcuts_enabled"] == "True":
                self.shortcutsEnabled = True
                logger.debug("ResolveShortcuts is ENABLED")
        else:
            logger.debug("ResolveShortcuts is DISABLED")

        #   Set icon variable
        if "use_icon" in self.configData:
            if self.configData["use_icon"] == "True":
                self.useIcon = True
            else:
                self.useIcon = False


    #   Makes the config file using default/auto values
    @err_catcher(name=__name__)
    def makeSettings(self):
        logger.warning("Creating settings file.")
        self.configData = {
                        "current_plugin_version": self.version,
                        "python_exe_path": self.getPrismPython(),
                        "plugin_path": self.pluginLocation,
                        "dvr_script_path": self.getResolveAPILoc(),
                        "resolve_exe": self.getResolveLoc(),
                        "shortcuts_enabled": "False",
                        "use_icon": "True"
                        }
        try:
            with open(self.settingsFile, 'w') as file:
                for key, value in self.configData.items():
                    value = value.replace("\\", "/")
                    file.write(f"{key}={value}\n")
            logger.info(f"Settings saved to {self.settingsFile}")

        except Exception as e:
            logger.error(f"Failed to save settings to {self.settingsFile}: {e}")


    #   Finds the path to Python included with Prism
    @err_catcher(name=__name__)
    def getPrismPython(self):
        prismRoot = self.core.prismRoot
        #   For different version of Prism which may use different Pythons
        pythonPaths = ["Python311", "Python39"]

        for path in pythonPaths:
            prismPythonPath = os.path.join(prismRoot, path, "python.exe")
            prismPythonPath = os.path.normpath(prismPythonPath)

            if os.path.exists(prismPythonPath):
                return prismPythonPath

        return None


    #   Since Resolve.exe does not seem to be found in winreg, this uses common install locations
    #   Not perfect, but the user can specify the loc in Prims Settings
    @err_catcher(name=__name__)
    def getResolveLoc(self):
        commonPaths = [os.path.join("C:\\", "Program Files", "Blackmagic Design", "DaVinci Resolve", "Resolve.exe"),
                       os.path.join("C:\\", "Program Files (x86)", "Blackmagic Design", "DaVinci Resolve", "Resolve.exe"),
                       os.path.join("C:\\", "Program Files", "DaVinci Resolve", "Resolve.exe"),
                       os.path.join("C:\\", "Program Files (x86)", "DaVinci Resolve", "Resolve.exe"),
                       os.path.join("D:\\", "Program Files", "Blackmagic Design", "DaVinci Resolve", "Resolve.exe"),
                       os.path.join("D:\\", "Program Files (x86)", "Blackmagic Design", "DaVinci Resolve", "Resolve.exe"),
                       os.path.join("D:\\", "Program Files", "DaVinci Resolve", "Resolve.exe"),
                       os.path.join("E:\\", "Program Files", "DaVinci Resolve", "Resolve.exe")]
        
        for path in commonPaths:
            if os.path.isfile(path):
                return path
            else:
                return os.path.join("C:\\", "Program Files", "Blackmagic Design", "DaVinci Resolve", "Resolve.exe")
            

    #   Uses the default Davinci install location
    @err_catcher(name=__name__)
    def getResolveAPILoc(self):
        resolveAPIpath = os.path.join(os.environ["PROGRAMDATA"],
                                      "Blackmagic Design",
                                      "DaVinci Resolve",
                                      "Support",
                                      "Developer",
                                      "Scripting",
                                      "Modules"
                                      )
        return resolveAPIpath


    #   Save settings to plain text file due to using .vbs for the shortcut file.
    @err_catcher(name=__name__)
    def saveSettings(self, origin=None):
        pData = {"current_plugin_version": self.version,
                 "python_exe_path": self.e_prismPython.text(),
                 "plugin_path": self.e_pluginLoc.text(),
                 "dvr_script_path": self.e_resolveApiScript.text(),
                 "resolve_exe": self.e_resolveEXE.text(),
                 "shortcuts_enabled": str(self.chb_enableShortcutFunctions.isChecked()),
                 "use_icon": str(self.chb_useIcon.isChecked())
                 }

        try:
            with open(self.settingsFile, 'w') as file:
                for key, value in pData.items():
                    value = value.replace("\\", "/")
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

        lo_resolveShortcuts.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # ENABLE SHORTCUT FUNCTIONS CHECKBOX
        lo_topBar = QHBoxLayout()
        
        self.chb_enableShortcutFunctions = QCheckBox("Enable Resolve Shortcut Functions")
        lo_topBar.addWidget(self.chb_enableShortcutFunctions)

        lo_topBar.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        l_enviroVarSet = QLabel("Enviro Variable is:")
        lo_topBar.addWidget(l_enviroVarSet)

        self.l_enviroStatus = QLabel("NOT SET    ")
        lo_topBar.addWidget(self.l_enviroStatus)

        self.but_setEnviroVar = QPushButton("Set    ")
        self.but_setEnviroVar.clicked.connect(self.setEnviroVar)
        lo_topBar.addWidget(self.but_setEnviroVar)

        self.but_removeEnviroVar = QPushButton("Remove")
        self.but_removeEnviroVar.clicked.connect(self.removeEnviroVar)
        lo_topBar.addWidget(self.but_removeEnviroVar)

        lo_topBar.addItem(QSpacerItem(60, 20, QSizePolicy.Fixed, QSizePolicy.Minimum))

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
        but_browseResolveEXE.clicked.connect(lambda: self.browseFiles(target=self.e_resolveEXE,
                                                                      type="file",
                                                                      title="Select the Resolve Executable"
                                                                      ))
        lo_resolveEXE.addWidget(but_browseResolveEXE)
        lo_resolveConfig.addLayout(lo_resolveEXE)

        l_resolveExample = QLabel("             (example:  C:/Program Files/Blackmagic Design/DaVinci Resolve/Resolve.exe)")
        lo_resolveConfig.addWidget(l_resolveExample)


        lo_resolveConfig.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))


        # RESOLVE API SECTION
        l_dvrScriptPath = QLabel("Directory containing Davinci Resolve Python API Script:")
        lo_resolveConfig.addWidget(l_dvrScriptPath)

        lo_resolveApiScript = QHBoxLayout()
        self.e_resolveApiScript = QLineEdit()
        lo_resolveApiScript.addWidget(self.e_resolveApiScript)

        but_browseResolveApiScript = QPushButton("Browse")
        but_browseResolveApiScript.clicked.connect(lambda: self.browseFiles(target=self.e_resolveApiScript,
                                                                            type="folder",
                                                                            title="Select the API Directory"
                                                                            ))
        lo_resolveApiScript.addWidget(but_browseResolveApiScript)
        lo_resolveConfig.addLayout(lo_resolveApiScript)

        l_apiScriptExample = QLabel("             (example:  C:/ProgramData/Blackmagic Design/DaVinci Resolve/Support/Developer/Scripting/Modules)")
        lo_resolveConfig.addWidget(l_apiScriptExample)


        lo_resolveConfig.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))


        # PRISM PYTHON SECTION
        l_prismPython = QLabel("Prism's Python Executable:")
        lo_resolveConfig.addWidget(l_prismPython)

        lo_prismPython = QHBoxLayout()
        self.e_prismPython = QLineEdit()
        lo_prismPython.addWidget(self.e_prismPython)

        but_browsePrismPython = QPushButton("Browse")
        but_browsePrismPython.clicked.connect(lambda: self.browseFiles(target=self.e_prismPython,
                                                                       type="file",
                                                                       title="Select Prism's Python.exe"
                                                                       ))
        lo_prismPython.addWidget(but_browsePrismPython)
        lo_resolveConfig.addLayout(lo_prismPython)

        l_prismPythonExample = QLabel("             (example:  C:/Prism2/Python311/python.exe)")
        lo_resolveConfig.addWidget(l_prismPythonExample)


        lo_resolveConfig.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))


        # PLUGIN LOCATION SECTION
        l_pluginLoc = QLabel("Resolve Shortcuts Plugin Location:")
        lo_resolveConfig.addWidget(l_pluginLoc)

        lo_pluginLoc = QHBoxLayout()
        self.e_pluginLoc = QLineEdit()
        lo_pluginLoc.addWidget(self.e_pluginLoc)

        but_browsePluginLoc = QPushButton("Browse")
        but_browsePluginLoc.clicked.connect(lambda: self.browseFiles(target=self.e_pluginLoc, 
                                                                     type="folder", 
                                                                     title="Select Shortcuts Plugin Directory"
                                                                     ))
        lo_pluginLoc.addWidget(but_browsePluginLoc)
        lo_resolveConfig.addLayout(lo_pluginLoc)

        l_pluginLocExample = QLabel("             (example:  C:/ProgramData/Prism2/plugins/CustomPlugins/ResolveShortcuts)")
        lo_resolveConfig.addWidget(l_pluginLocExample)


        lo_resolveConfig.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))


        # BOTTOM BAR
        lo_btmBar = QHBoxLayout()

        self.chb_useIcon = QCheckBox("Associate Icon with shortcut filetype")
        lo_btmBar.addWidget(self.chb_useIcon)

        lo_btmBar.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        l_reset = QLabel("Reset Locations to default:  ")
        lo_btmBar.addWidget(l_reset)

        but_reset = QPushButton("Reset")
        but_reset.clicked.connect(self.resetPaths)
        lo_btmBar.addWidget(but_reset)
        lo_btmBar.addItem(QSpacerItem(60, 20, QSizePolicy.Fixed, QSizePolicy.Minimum))
        lo_resolveConfig.addLayout(lo_btmBar)

        lo_resolveShortcuts.addWidget(self.gb_resolveConfig)

        # Add an expanding spacer at the bottom
        lo_resolveShortcuts.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        #   Tooltips
        tip = "Globally enable the Resolve Shortcuts functionality."
        self.chb_enableShortcutFunctions.setToolTip(tip)

        tip = ("Status of the system environment variable (DVR_shortcuts_path).\n"
               "The enviro variable must be set to use the shortcut functions.\n\n"
               "To manually set via Prism enviroment or system:\n\n"
               "KEY:        'DVR_shortcuts_path'\n"
               "VALUE:    '[path/to/ResolveShortcuts] plugin dir'")
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

        tip = ("Associate custom icon to shortcut scenefiles (.vbs)\n"
               "Prism must be restarted for change to be visible.")
        self.chb_useIcon.setToolTip(tip)

        tip = "Force regeneration of the default paths."
        l_reset.setToolTip(tip)
        but_reset.setToolTip(tip)

        self.loadSettings()
        self.loadValues()
        self.refreshUI()

        self.chb_enableShortcutFunctions.toggled.connect(self.refreshUI)

        # Add Tab to User Settings
        origin.addTab(origin.w_resolveShortcuts, "Resolve Shortcuts")


    #   Loads config values into Settings UI
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

        self.chb_enableShortcutFunctions.setChecked(self.shortcutsEnabled)
        self.chb_useIcon.setChecked(self.useIcon)


    #   File browser
    @err_catcher(name=__name__)
    def browseFiles(self, target, type='file', title='Select File or Folder'):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        #   Get current prh in box to use for default loc
        currentPath = target.text()

        if type == 'file':
            filePath, _ = QFileDialog.getOpenFileName(None,
                                                      title,
                                                      currentPath,
                                                      "All Files (*);;Python Files (*.py)",
                                                      options=options
                                                      )
        elif type == 'folder':
            filePath = QFileDialog.getExistingDirectory(None,
                                                        title,
                                                        currentPath,
                                                        options=options
                                                        )
        else:
            print("Invalid type specified. Use 'file' or 'folder'.")
            return

        if filePath:
            target.setText(filePath)
            

    @err_catcher(name=__name__)
    def resetPaths(self):
        text = ("Do you want to reset all Resolve Shortcut settings to\n"
                "their default values?")
        title = "Reset Settings"
        result = self.core.popupQuestion(text=text, title=title)

        if result == "Yes":
            logger.debug("Resetting ResolveShortcuts settings to default values.")

            self.makeSettings()
            self.loadValues()


    #   Configures Settings UI elements
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

        
    #   Checks if required enviro variable exists
    @err_catcher(name=__name__)
    def checkEnviroVar(self):
        return 'DVR_shortcuts_path' in os.environ


    #   Set required enviro var and exits Prism
    @err_catcher(name=__name__)
    def setEnviroVar(self):
            text = ("Prism will need to shutdown for the environment\n"
                    "variable to be set.  Afterwards you will need to\n"
                     "manually restart Prism.\n\n"
                     "Do you want to set the variable?"
                     )
            title = "Set Environment Variable"
            result = self.core.popupQuestion(text=text, title=title)

            if result == "Yes":
                try:
                    self.saveSettings()
                    logger.debug("Setting 'DVR_shortcuts_path' environment variable")
                    logger.debug("Prism will exit")
                    subprocess.run(['setx', 'DVR_shortcuts_path', self.pluginLocation], check=True)
                    self.core.PrismTray.exitTray()

                except Exception as e:
                    self.core.popup("Failed to set environment variable.")
                    logger.error("Failed to set environment variable.")
                    logger.error(e)

        
    #   Removes enviro var
    @err_catcher(name=__name__)
    def removeEnviroVar(self):
            text = ("Prism will need to shutdown for the environment\n"
                    "variable to be set.  Afterwards you will need to\n"
                     "manually restart Prism.\n\n"
                     "Do you want to set the variable?"
                     )
            title = "Set Environment Variable"
            result = self.core.popupQuestion(text=text, title=title)

            if result == "Yes":
                try:
                    self.saveSettings()
                    logger.debug("Removing 'DVR_shortcuts_path' environment variable")
                    logger.debug("Prism will exit")
                    subprocess.run(['setx', 'DVR_shortcuts_path', ""], check=True)
                    self.core.PrismTray.exitTray()

                except Exception as e:
                    self.core.popup("Failed to remove environment variable.")
                    logger.error("Failed to remove environment variable.")
                    logger.error(e)


    #   Adds right-click menu item
    @err_catcher(name=__name__)
    def addShortcutItem(self, origin, rcmenu, filePath):
        if self.shortcutsEnabled:
            shortcutAct = QAction("Save Shortcut to Resolve Project", rcmenu)
            shortcutAct.triggered.connect(lambda: self.saveShortcut(origin))
            rcmenu.addAction(shortcutAct)


    #   Builds and saves shortcut (.vbs file)
    @err_catcher(name=__name__)
    def saveShortcut(self, origin):
        #   Imports bridge script with the Resolve API
        try:
            from DvResolve_Project_Shortcuts import ResolveProjectShortcuts
            logger.debug("Imported ResolveShortcuts")

        except Exception as e:
            logger.warning("Failed to import ResolveShortcuts module")
            self.core.popup("Failed to import ResolveShortcuts module")
        
        #   Get details and save path data
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
        preview = None

        #   Instantiates and calls the save from the bridge script
        shortcuts = ResolveProjectShortcuts()
        currProjName, saveResult = shortcuts.saveProjectShortcut(savePath)

        if saveResult is True:
            thumbDir = tempfile.TemporaryDirectory()
            thumbName = "PrismThumbImage"

            #   Adds custom description item
            detailData = {}
            detailData["description"] = f'Shortcut to   "{currProjName}"   Resolve project'

            thumbResult = shortcuts.getThumbnail(thumbDir.name, thumbName)

            if thumbResult is True:
                try:
                    pattern = os.path.join(thumbDir.name, thumbName + "_*.jpg")
                    matching_files = glob.glob(pattern)

                    if matching_files:
                        thumbNail = matching_files[0]
                        pixMap = self.core.media.getPixmapFromPath(thumbNail)
                        preview = self.core.media.scalePixmap(pixMap,
                                                            self.core.scenePreviewWidth,
                                                            self.core.scenePreviewHeight,
                                                            fitIntoBounds=False,
                                                            crop=True
                                                            )
                    fullResult = (f"Saved shortcut to '{currProjName}'\n"
                                  "with thumbnail.")
                except:
                    fullResult = (f"Saved shortcut to '{currProjName}'\n"
                                  "without thumbnail.")
            else:
                fullResult = (f"Saved shortcut to '{currProjName}'\n"
                              "without thumbnail.")

            #   Saves the details to the versioninfo.json
            # origin.core.saveSceneInfo(savePath, detailData, preview=None)
            origin.core.saveSceneInfo(savePath, detailData, preview=preview)
            origin.refreshScenefiles()
            
        else:
            fullResult = f"Failed to save shortcut to {currProjName}:\n\n{saveResult}"

        logger.debug(fullResult)
        self.core.popup(fullResult)