' THIS IS A SHORTCUT FILE TO A PROJECT IN DAVINCI RESOLVE
' IT WILL OPEN THE PROJECT AT THE BELOW PATH

' Generated with version [VERSION_REPLACE] of the ResolveShortcuts Prism Plugin 

' SHORTCUT PROJECT PATH INFO
'vvvvvvvvvvvvvvvvvvvvvvvvvvvvv
projectPath = "PROJECT_PATH_REPLACE"
' ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

' CONFIG AND RUN CODE
Dim fso, file, config, lines, line, keyValue, pythonExe, scriptPath, projectPath, objShell

' Create FileSystemObject
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the PRISM_DVR_SHORTCUTS_PATH environment variable
dvrShortcutsPath = GetEnv("PRISM_DVR_SHORTCUTS_PATH")
If dvrShortcutsPath = "" Then
    WScript.Echo "ERROR: PRISM_DVR_SHORTCUTS_PATH environment variable is not set."
    WScript.Quit
End If

' Build the path to the configuration file
configFilePath = dvrShortcutsPath & "\ResolveShortcuts_Config.txt"

' Check if the config file exists
If Not fso.FileExists(configFilePath) Then
    WScript.Echo "ERROR: Configuration file not found at " & configFilePath
    WScript.Quit
End If

' Open the configuration file
Set file = fso.OpenTextFile(configFilePath, 1)
config = file.ReadAll
file.Close

' Split the configuration into lines
lines = Split(config, vbCrLf)

' Parse each line and extract key-value pairs
For Each line In lines
    keyValue = Split(line, "=")
    If UBound(keyValue) = 1 Then
        Select Case Trim(keyValue(0))
            Case "python_exe_path"
                pythonExe = Trim(keyValue(1))
            Case "plugin_path"
                pluginPath = Trim(keyValue(1))
        End Select
    End If
Next



' Construct the full script path
scriptPath = pluginPath & "\Scripts\DvResolve_Project_Shortcuts.py"

Set objShell = CreateObject("WScript.Shell")

mode = "load"

' Get the current script's path and name
strScriptFullName = WScript.ScriptFullName
strScriptName = fso.GetFileName(WScript.ScriptFullName)

' Run the command
command = pythonExe & " """ & scriptPath & """ " & mode & " """ & projectPath & """ """ & strScriptName & """"
objShell.Run command, 0, False

Set objShell = Nothing

' Function to get environment variable
Function GetEnv(varName)
    On Error Resume Next
    GetEnv = WScript.CreateObject("WScript.Shell").Environment("Process").Item(varName)
    On Error GoTo 0
End Function
