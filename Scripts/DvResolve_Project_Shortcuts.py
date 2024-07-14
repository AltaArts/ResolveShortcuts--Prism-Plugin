
######      TODO     ADD HEADER

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

        # Add the Resolve script path to sys.path
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
            print(f"Error: Configuration file '{self.settingsFile}' not found.")
            return None


    def startResolve(self, timeout=30):
        startTime = time.time()

        # Start Resolve
        subprocess.Popen(self.resolveExe)

        try:
            # Attempt to get the Resolve instance
            while self.resolve is None:
                try:
                    self.getResolve()
                    if self.resolve is not None:
                        print("Resolve is running.")
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


    def getResolve(self):
        try:
            import DaVinciResolveScript as dvr
        except ImportError:
            print("Failed to import DaVinciResolveScript")
            sys.exit(1)

        self.resolve = dvr.scriptapp("Resolve")


    def openResolveProject(self, projectLoadPath, timeout):
            
            self.startResolve(timeout)

            if not self.resolve:
                return

            if len(projectLoadPath) < 2:
                print("Invalid project path format.")
                return
            
            # Get the project manager
            self.pm = self.resolve.GetProjectManager()
            currDbName = self.pm.GetCurrentDatabase()["DbName"]

            path_components = projectLoadPath.split("\\")

            if len(path_components) < 2:
                print("Invalid project path format.")
                return
            
            projectDB = path_components[0]
            projectPath = "\\".join(path_components[1:])

            if currDbName != projectDB:
                print("Incorrect Resolve Database selected")
                return
            
            currProject = self.pm.GetCurrentProject()
            if currProject:
                self.pm.SaveProject()
            
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
            self.getResolve()
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

            parentFolders.reverse()  # Reverse the list to have the hierarchy from top to bottom

            # Construct the project path string
            projectPath = "\\".join(parentFolders) + "\\" + currProjectName

            projectPath = dbName + "\\" + projectPath
            projectPath = projectPath.replace("\\\\", "\\")

            return currProjectName, projectPath

        except Exception as e:
            print("Error:", e)
            return e


    def saveProjectShortcut(self, savePath):

        currProjectName, projectPath = self.getProjectPath()

        templateFile = os.path.join(self.pluginPath,
                                    "Scripts",
                                    "Template",
                                    "shortcutTemplate.vbs"
                                    )

        try:
            # Read the template file
            with open(templateFile, 'r') as file:
                content = file.read()

            # Replace the placeholder with the actual project path
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




### TESTING

    # projectPath = "db_c0a5659ba25442149ff8b6775a4be99f\Testing\Sub 1\Sub 2\ShortCutTests"
    # savePath = r"N:\Data\Projects\Random Practice\01_Production\Shots\090_TearsOfSteel\010_DollyInManSitting\Scenefiles\resolve\Comp\090_TearsOfSteel-010_DollyInManSitting_Comp_v002"

    # resolveShortcuts = ResolveProjectShortcuts()

    # resolveShortcuts.openResolveProject(projectPath, timeout=30)
    
    # returnPath = resolveShortcuts.saveProjectShortcut(savePath)

    # print(returnPath)


