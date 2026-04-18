import time
import subprocess

def test_old():
    command = r"""
$items = Get-CimInstance Win32_Process |
  Where-Object { $_.CommandLine -and $_.CommandLine -like '*--user-data-dir*' } |
  Select-Object ProcessId, Name, CommandLine
if ($items) {
  $items | ConvertTo-Json -Compress -Depth 3
}
"""
    t0 = time.time()
    subprocess.run(["powershell", "-NoProfile", "-Command", command], capture_output=True)
    return time.time() - t0

def test_new():
    command = r"""
$items = Get-CimInstance -Query "SELECT ProcessId, CommandLine FROM Win32_Process WHERE Name = 'chrome.exe'" |
  Where-Object { $_.CommandLine -and $_.CommandLine -like '*--user-data-dir*' } |
  Select-Object ProcessId, CommandLine
if ($items) {
  $items | ConvertTo-Json -Compress -Depth 3
}
"""
    t0 = time.time()
    subprocess.run(["powershell", "-NoProfile", "-Command", command], capture_output=True)
    return time.time() - t0

def test_wmic():
    t0 = time.time()
    subprocess.run(['wmic', 'process', 'where', "name='chrome.exe'", 'get', 'ProcessId,CommandLine', '/format:csv'], capture_output=True)
    return time.time() - t0

print(f"Old method: {test_old():.3f}s")
print(f"New method: {test_new():.3f}s")
print(f"WMIC method: {test_wmic():.3f}s")
