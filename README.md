# **ResolveShortcuts for Prism Pipeline 2**
A plugin to be used with version 2 of Prism Pipeline 

Prism automates and simplifies the workflow of animation and VFX projects.

You can find more information on the website:

https://prism-pipeline.com/



## **Overview**

The ResolveShortcuts plugin adds the ability to save a shortcut to a project located in Davinci Resolve's internal database.  The shortcut file will be saved in the scenefiles alongside other versioned scenefiles.  This allows the abilty to directly open the project from Prism's Project Browser mimicing other DCC scenefiles.

The shortcut file is just a small Visual Basic script file (.vbs) that contains the "path" to the project.  This script will read the plugins config file, and call a python script that will start Resolve and open the project.

A shortcut can be saved into Prism by opening the Prism Project Browser from the Resolve Prism tool, and right clicking.  This opens the default Prism menu, with the added item "Save Shortcut to Resolve Project".

## **Notes**

- Two things need to be enabled for the plugin to function:  The "Enabled" checkbox and the enviroment variable set.
- This does not handle versioning as would be normal for scenefiles.  The shortcut just points to the project in Resolve.
- The shortcut files are small Visual Basic script files and thus the system's security preferneces must allow .bs scripts to run.
- The plugin will attempt to set the required filepaths during first run of the plugin.  This assumes that Resolve is installed in the default location.  But if the plugin is moved on the system or Resolve is not installed into the default location, the correct filepaths must be set in the settings.  The plugin directory must be named "ResolveShortcuts".
- It seems that Resolves API to change databases is not working correctly.  So if a shortcut is trying to reach a project that is on another database than what Resolve is on currently, it will not work.  The solution is to navigate Resolve to the desired database and then the shortcuts will work.
- This works for both local and Cloud databases.
- Gimp saves .exr's in full-float 32bit zip compression only.  
- To aid is use, tooltips are provided throughout.
<br/><br/>

## **Installation**

This plugin is for Windows only, as Prism2 only supports Windows at this time.

TODO  You can either download the latest stable release version from: [Latest Release](https://github.com/AltaArts/Gimp_Integration--Prism-Plugin/releases/latest)

TODO  or download the current code zipfile from the green "Code" button above or on [Github](https://github.com/AltaArts/Gimp_Integration--Prism-Plugin)

Copy the directory named "ResolveShortcuts" to a directory of your choice, or a Prism2 plugin directory.

Prism's default plugin directories are: *{installation path}\Plugins\Apps* and *{installation Path}\Plugins\Custom*.

You can add the additional plugin search paths in Prism2 settings.  Go to Settings->Plugins and click the gear icon.  This opens a dialogue and you may add additional search paths at the bottom.

Once added, select the "Add existing plugin" (plus icon) and navigate to where you saved the plugin folder.

![Add Existing Plugin](https://github.com/AltaArts/Gimp_Integration--Prism-Plugin/assets/86539171/d86e3b34-d172-4cd8-b238-147ff6a25106)<br/><br/>

![Select Plugin Folder](https://github.com/AltaArts/Gimp_Integration--Prism-Plugin/assets/86539171/31ad18bf-4658-4da2-ad65-3c5500a7b284)

Afterwards, you can select the Plugin autoload as desired:

![AutoLoad](https://github.com/AltaArts/Gimp_Integration--Prism-Plugin/assets/86539171/1f0295c3-709d-4937-88fb-3d63d43d779c)


<br/>

## **Usage**

### **Opening Project**
Shortcuts are located in the Scenefiles tab as any other DCC.  Double-clicking the shortcut will open Resolve and navigate to the project.

<br/>

### **Creating Shortcut**

To save a shortcut, open the Project Browser from the Prism tool inside Resolve.  Then navigate to the desired Department/Task, and right click in the scenefiles area.  This opens the right-click menu with various Prism options, with the added "Save Shortcut to Resolve Project" item.  This will generate the .vbs file and save it in the Prism project structure.  The shortcut file will have a comment in its Description noting the Resolve project.

![Gimp Error Console](https://github.com/AltaArts/Gimp_Integration--Prism-Plugin/assets/86539171/67df98e5-ae36-4a11-a60d-dbd3bbfdb3c5)

There are three level of message display, but all messages will always be saved in the log.  With "Log Only", no messages will be displayed in the Gimp UI.  "Minimal" will display some messages that may be useful to the user such as "Starting Server".  "All" will display all messages in the UI. 

![Log Menu](https://github.com/AltaArts/Gimp_Integration--Prism-Plugin/assets/86539171/f0de1aef-72b2-4b4c-bc5f-495414f321a6)

Keep in mind that having "All" messages displayed will show many messages and slightly slow the interface, thus it is suggested to have the message level at "Minimal".  If the Error Console is docked in a widow with other tabs, new messages will move the focus to the Error Console so it is suggested to have the Error Console docked into its own window.

![Suggested UI](https://github.com/AltaArts/Gimp_Integration--Prism-Plugin/assets/86539171/30882315-8770-4f04-a863-afea2f504e82)



The Gimp log may be viewed by opening the directory with the "open Log" button in Settings->DCCs->Gimp.  The log will update until it reaches the max size limit set in settings, and then will be renamed to "_OLD" with a maximum of those two files.  By default, the logs are saved in the Gimp plugin directory and you can change the save location in the settings.
<br/><br/>

### **Exporting**

To export (save) images we use the StateManager via a custom Gimp_Render state.  Various output image formats are supported, with more being added.  The current image's details will be displayed along with format-specific settings for each state.  A user has the option to scale the resulting image, or change the color mode and bit depth of the resulting export.  These changes will not alter the scenefile.

![Gimp Render](https://github.com/AltaArts/Gimp_Integration--Prism-Plugin/assets/86539171/5d989db8-205d-4484-b5e6-d64528bad250)

If the lowest layer of the scenefile image has an alpha channel, and the export format is not an alpha format (not RGBA or GRAYA), then an option will be displayed to select the desired background to be used.

![AlphaFill](https://github.com/AltaArts/Gimp_Integration--Prism-Plugin/assets/86539171/fe812ace-7ff5-4862-9915-b5a6ef12ed3e)


A user may export to .psd using the StateManager.  By default the resulting .psd will be saved in the selected Identifier in Media tab.  There is also and option to export the .psd as a scenefile under the Scenefiles tab.

![SM psd](https://github.com/AltaArts/Gimp_Integration--Prism-Plugin/assets/86539171/08b12333-d439-4690-b0cc-1cc29c9a311d)

This will export the .psd next to the .xcf using the same version number and details.

![PSD Version](https://github.com/AltaArts/Gimp_Integration--Prism-Plugin/assets/86539171/185bc704-922c-41df-81e0-315f7da7ee2a)


<br/><br/>


## **Issues / Suggestions**

For any bug reports or suggestions, please add to the GitHub repo.
