# **ResolveShortcuts for Prism Pipeline 2**
A plugin to be used with version 2 of Prism Pipeline 

Prism automates and simplifies the workflow of animation and VFX projects.

You can find more information on the website:

https://prism-pipeline.com/



## **Overview**

The ResolveShortcuts plugin adds the ability to save a shortcut to a project located in Davinci Resolve's internal database.  The shortcut file will be saved in the scenefiles alongside other versioned scenefiles.  This allows the abilty to directly open the project from Prism's Project Browser mimicking other DCC scenefiles without having to start Resolve, and navigate its Project Manager to find the project.

The shortcut file is just a small Visual Basic script file (.vbs) that contains the "path" to the project that will start Resolve and open the project.

A shortcut can be saved into Prism by opening the Prism Project Browser from the Resolve Prism tool, and right clicking.  This opens the default Prism menu, with the added item "Save Shortcut to Resolve Project".

## **Notes**

- Two things need to be enabled for the plugin to function: the "Enabled" checkbox and the environment variable set.
- This does not handle versioning as would be normal for scenefiles.  The shortcut just points to the project in Resolve.
- The shortcut files are small Visual Basic script files and thus the system's security preferences must allow .vbs scripts to run.
- The plugin will attempt to set the required filepaths during first run of the plugin.  This assumes that Resolve is installed in the default location.  If the plugin is moved on the system or Resolve is not installed into the default location, the correct filepaths must be set in the settings.  The plugin directory must be named "ResolveShortcuts".
- It seems that Resolve's API to change databases is not working correctly.  So if a shortcut is trying to reach a project that is on another database to what Resolve is on currently, it will not work.  The solution is to navigate Resolve to the desired database and then the shortcuts will work.
- Shortcuts work for both local and Cloud databases.
- To aid is use, tooltips are provided throughout.
  
<br/>

## **Installation**

This plugin is for Windows only, as Prism2 only supports Windows at this time.

You can either download the latest stable release version from: [Latest Release](https://github.com/AltaArts/ResolveShortcuts--Prism-Plugin/releases/latest)

or download the current code zipfile from the green "Code" button above or on [[Github](https://github.com/AltaArts/Gimp_Integration--Prism-Plugin)]

Copy the directory named "ResolveShortcuts" to a directory of your choice, or a Prism2 plugin directory.

Prism's default plugin directories are: *{installation path}\Plugins\Apps* and *{installation Path}\Plugins\Custom*.

You can add the additional plugin search paths in Prism2 settings.  Go to Settings->Plugins and click the gear icon.  This opens a dialogue and you may add additional search paths at the bottom.

Once added, restart Prism or reload plugins.

<br/>

## **Usage**

### **Creating Shortcut**

To save a shortcut, open the Project Browser from the Prism tool inside Resolve.  Navigate to the desired Department/Task, and right click in the scenefiles area.  This opens the right-click menu with various Prism options, with the added "Save Shortcut to Resolve Project" item (the shortcut item will not be in Standalone or other DCC intergrations).  This will generate the .vbs file and save it in the Prism project structure.  The shortcut file will have a comment in its Description noting the Resolve project.

![RCL Item](https://github.com/user-attachments/assets/69817b5d-b838-45f2-850d-7ecf1f5ce7c4)

### **Opening a Resolve Project**
Shortcuts are located in the Scenefiles tab as any other DCC.  Double-clicking the shortcut will open Resolve and navigate to the project.

![Shortcut Scenefile](https://github.com/user-attachments/assets/4ca36043-2fa6-4e04-8bc5-d3a4838267b6)

The shortcut file is generated from a .vbs file named "shortcutTemplate.vbs" in the Template directory.  The shortcut .vbs file is utilized to be able to be run by just double-clicking.  The script will read the environment variable to get the plugin directory location, and then send a command line command to run a python script (DvResolve_Project_Shortcuts.py) with the project path as an argument.  The python script will start Resolve, wait for the API to initialize, and then navigate to the project and open it.

![VBS](https://github.com/user-attachments/assets/8e53fe28-4eb9-4c06-acc3-a6e41bdedc03)

<br/>

### **Settings**

Settings for ResolveShortcuts are located in Prism's:   Settings->User->ResolveShortcuts.  The settings will be greyed-out and the shortcut functions will not be active until it is both enabled, and the environmant variable is set.

![Settings](https://github.com/user-attachments/assets/65e10a15-f318-4b70-9907-5c1d63dd48bb)

#### *Environment Variable*:

The environment variable "DVR_shortcuts_path" must be set to point to the ResolveShortcuts plugin directory.  A button is provided in the settings to automatically set the variable (or remove if needed).  Using the button will set the variable, and then exit Prism.   The variable may also be manually set using Prism's environment or the standard systems settings.


![Enviro Set 2](https://github.com/user-attachments/assets/16430231-a1bf-489b-9d1a-69022b1824e6) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
![Enviro Remove](https://github.com/user-attachments/assets/bcffb2b4-e4c5-4f8a-9c97-67e287bb03eb)

#### *File Paths*:

Various filepaths must be set correctly for shortcuts to function.  The paths will be set during the first run of the plugin and will be saved to the config file.  This assumes that Resolve is installed in the default location [Program Files] and [ProgramData].  If this is not the case or the plugin is moved, the correct paths can be set in settings.

- "DaVinciResolveScript.py" is the python module for Resolve's API that enables scripts to function inside Resolve.
- It is suggested to use the python.exe that is included with the Prism install.  Any instance of python.exe may work, but the same version must be used.

 A Reset button is provided to reset the paths to the automatically generated locations that are set at first run.

 ![Reset](https://github.com/user-attachments/assets/75aadeec-8e11-4fd7-b4d0-b04dd96c0281)


#### *Shortcut Icon*:

By default in Prism, the .vbs file type does not have an associated icon.  The plugin adds the association to a custom Resolve icon to differentiate the shortcut.  This should work in most cases, but if desired the shortcut icon can be disabled in the settings.

![Icon Box](https://github.com/user-attachments/assets/0566cea6-bdc2-4ce4-ab21-b06eb1a28459)


<br/><br/>


## **Issues / Suggestions**

For any bug reports or suggestions, please add an issue to the GitHub repo.
