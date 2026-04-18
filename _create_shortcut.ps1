$WshShell = New-Object -ComObject WScript.Shell
$Desktop = [Environment]::GetFolderPath('Desktop')
$ShortcutPath = Join-Path $Desktop "Anti-Detect Browser Manager.lnk"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "wscript.exe"
$Shortcut.Arguments = "`"D:\Portable Anti-Detect Browsers\Launch Profile Manager.vbs`""
$Shortcut.WorkingDirectory = "D:\Portable Anti-Detect Browsers"
$Shortcut.IconLocation = "D:\Portable Anti-Detect Browsers\app_icon.ico, 0"
$Shortcut.Description = "Launch Portable Anti-Detect Browser Manager with AI Fingerprint Engine"
$Shortcut.WindowStyle = 7
$Shortcut.Save()

Write-Host "Desktop shortcut created: $ShortcutPath"
