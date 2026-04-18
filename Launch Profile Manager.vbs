' Launch Profile Manager - Silent (No CMD Window)
' This VBScript launches the GUI without showing any console window.
Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

strScriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)
objShell.CurrentDirectory = strScriptDir

' Try pythonw first (no console), fall back to python with hidden window
Dim pythonwPath
pythonwPath = ""

' Check if pythonw is available
On Error Resume Next
objShell.Run "cmd /c where pythonw > """ & strScriptDir & "\__pycheck.tmp"" 2>&1", 0, True
On Error GoTo 0

If objFSO.FileExists(strScriptDir & "\__pycheck.tmp") Then
    Dim f
    Set f = objFSO.OpenTextFile(strScriptDir & "\__pycheck.tmp", 1)
    If Not f.AtEndOfStream Then
        pythonwPath = Trim(f.ReadLine)
    End If
    f.Close
    objFSO.DeleteFile strScriptDir & "\__pycheck.tmp"
End If

If pythonwPath <> "" And InStr(LCase(pythonwPath), "pythonw") > 0 Then
    ' Use pythonw (completely silent)
    objShell.Run """" & pythonwPath & """ """ & strScriptDir & "\profile_launcher_gui.py""", 0, False
Else
    ' Fallback: use python with hidden window (0 = hidden)
    objShell.Run "python """ & strScriptDir & "\profile_launcher_gui.py""", 0, False
End If
