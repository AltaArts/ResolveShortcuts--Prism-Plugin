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

import sys
import os
import time
import subprocess
import argparse


class ResolveProjectShortcuts(object):
    def __init__(self):
        self.pluginPath = os.path.dirname(os.path.dirname(__file__))
        self.settingsFile = os.path.join(self.pluginPath, "ResolveShortcuts_Config.txt")
        self.resolve = None
        self.pm = None
        self.currProject = None

        self.resolveExe, dvr_script_path = self.loadSettings()

        # Add the Resolve API script to sys.path
        sys.path.append(dvr_script_path)


    def loadSettings(self):
        dvr_script_path = None
        resolveEXE = None

        # Read the config file - Have to use plain text for the .vbs file parse
        try:
            with open(self.settingsFile, 'r') as file:
                lines = file.readlines()

            # Parse each line and extract key-value pairs
            for line in lines:
                keyValue = line.strip().split('=')
                if len(keyValue) == 2:
                    key = keyValue[0].strip()
                    value = keyValue[1].strip()

                    if key == 'dvr_script_path':
                        dvr_script_path = value
                    elif key == 'resolve_exe':
                        resolveEXE = value

            return resolveEXE, dvr_script_path

        except FileNotFoundError:
            print(f"ERROR: Configuration file '{self.settingsFile}' not found.")
            return None
        
        except Exception as e:
            print("ERROR: Config file formatting error.")


    # Continuously attempt to get the Resolve instance
    def startResolve(self, timeout=30):
        startTime = time.time()

        # Start Resolve
        subprocess.Popen(self.resolveExe)

        try:
            #   Starts loop
            while self.resolve is None:
                try:
                    self.getResolve()
                    if self.resolve is not None:
                        print("Resolve is running.")
                        #   Breakout once it is loaded
                        break

                except Exception as e:
                    # Check if timeout exceeded
                    if time.time() - startTime > timeout:
                        print("Timeout reached while waiting for Resolve to initialize.")
                        return
                    
                    print(f"Error: {e}")
                    time.sleep(1)

            if self.resolve is None:
                print("Could not initialize Resolve instance.")
                return
            
        except Exception as e:
            print("Error:", e)


    #   Imports DVR API Script
    def getResolve(self):
        try:
            import DaVinciResolveScript as dvr

        except ImportError:
            print("Failed to import DaVinciResolveScript")
            sys.exit(1)

        #   Instantiate the API
        self.resolve = dvr.scriptapp("Resolve")


    def openResolveProject(self, projectLoadPath, timeout):
        #   Starts Resolve and imports the API    
        self.startResolve(timeout)

        if not self.resolve:
            return
        #   Checks if arg path is misformatted
        if len(projectLoadPath) < 2:
            print("Invalid project path format.")
            return
        
        # Get the project manager
        self.pm = self.resolve.GetProjectManager()
        currDbName = self.pm.GetCurrentDatabase()["DbName"]

        #   Splits arg path into dirs and Project name
        path_components = projectLoadPath.split("\\")

        if len(path_components) < 2:
            print("Invalid project path format.")
            return
        
        projectDB = path_components[0]
        projectPath = "\\".join(path_components[1:])

        #   Since the API call to change DB's does not seem to work,
        #   can only check if the database match
        if currDbName != projectDB:
            print("Incorrect Resolve Database selected")
            return

        #   Saves the currently open project if it is not the
        #   default name.  Is useful if there is a project already open.
        try: 
            currProjectName = self.pm.GetCurrentProject().GetName()
            if currProjectName != "Untitled Project":
                self.pm.SaveProject()
        except AttributeError:
            pass
        
        #   Navigates to the root folder to start since there is no way
        #   to go directly to a dir path
        self.pm.GotoRootFolder()
        
        folders = projectPath.split("\\")
        projectName = folders[-1]
        folderPath = "\\".join(folders[:-1])

        # Navigate to the folder path
        if folderPath:
            self.pm.GotoRootFolder()
            for folderName in folderPath.split("\\"):
                if folderName.strip():
                    if not self.pm.OpenFolder(folderName):
                        print(f"Failed to open folder: {folderName}")
                        return

        # Load the project
        if not self.pm.LoadProject(projectName):
            print(f"Failed to load project: {projectName}")
        else:
            print(f"Project {projectName} loaded successfully.")


    def getProjectPath(self):
        try:
            #   Get the API
            self.getResolve()

            #   Gets the various names
            self.pm = self.resolve.GetProjectManager()
            db = self.pm.GetCurrentDatabase()
            dbName = db["DbName"]

            currProjectName = self.pm.GetCurrentProject().GetName()
            currentFolder = self.pm.GetCurrentFolder()

            # Get parent folders recursively
            parentFolders = []
            while currentFolder:
                parentFolders.append(currentFolder)
                self.pm.GotoParentFolder()
                previousFolder = currentFolder
                currentFolder = self.pm.GetCurrentFolder()
                if currentFolder == previousFolder:
                    break  # Reached the root folder

            # Reverse the list of sub dirs
            parentFolders.reverse()

            # Construct the project path string
            projectPath = "\\".join(parentFolders) + "\\" + currProjectName

            #   Add DB name to path
            projectPath = dbName + "\\" + projectPath
            projectPath = projectPath.replace("\\\\", "\\")

            return currProjectName, projectPath

        except Exception as e:
            print("Error:", e)
            return e


    def saveProjectShortcut(self, savePath):
        currProjectName, projectPath = self.getProjectPath()

        #   Gets the template .vbs from plugin folder
        templateFile = os.path.join(self.pluginPath,
                                    "Scripts",
                                    "Template",
                                    "shortcutTemplate.vbs"
                                    )
        try:
            # Read the template file
            with open(templateFile, 'r') as file:
                content = file.read()

            # Replace the placeholder with the project path
            modifiedContent = content.replace("PROJECT_PATH_REPLACE", projectPath)

            # Save the modified content to the new file
            with open(savePath, 'w') as file:
                file.write(modifiedContent)

            result = f"Saved shortcut to {currProjectName}"

        except Exception as e:
            result = f"Error while saving shortcut: {e}"
        
        return currProjectName, result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resolve Project Shortcuts")

    parser.add_argument("mode",
                        choices=["load", "save"],
                        help="Mode: 'load' to load a project or 'save' to save a project shortcut"
                        )
    
    parser.add_argument("path", help="Path to project or file")
    
    args = parser.parse_args()

    resolveShortcuts = ResolveProjectShortcuts()

    if args.mode == "load":
        projectPath = args.path

        # Call the function to load the project in Resolve with a timeout of 30 seconds
        resolveShortcuts.openResolveProject(projectPath, timeout=30)

    elif args.mode == "save":
        savePath = args.path

        resolveShortcuts.saveProjectShortcut(savePath)