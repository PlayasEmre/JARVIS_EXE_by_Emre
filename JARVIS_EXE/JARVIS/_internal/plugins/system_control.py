"""
JARVIS System Control Plugin.
Advanced system operations: screenshot, clipboard, window management, processes.
"""

import subprocess
import os
import json
from datetime import datetime
from pathlib import Path

PLUGIN = {
    "name": "system_control",
    "description": (
        "Advanced system control. Use when the user asks to take a screenshot, "
        "manage clipboard, list running processes, kill a process, open a program, "
        "check battery, disk space, or manage windows."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "One of: screenshot, processes, kill_process, open_app, disk_space, battery, lock_screen, empty_trash",
            },
            "target": {
                "type": "STRING",
                "description": "Process name to kill, app name/path to open",
            },
        },
        "required": ["action"],
    },
}


def run(parameters: dict, player=None, session_memory=None) -> str:
    action = parameters.get("action", "").lower()
    target = parameters.get("target", "")

    try:
        if action == "screenshot":
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = Path.home() / "Pictures" / f"jarvis_screenshot_{ts}.png"
            path.parent.mkdir(exist_ok=True)
            try:
                from PIL import ImageGrab
                img = ImageGrab.grab()
                img.save(str(path))
                return f"Screenshot gespeichert: {path}"
            except ImportError:
                subprocess.run(["powershell", "-c",
                                f"Add-Type -AssemblyName System.Windows.Forms;"
                                f"[System.Windows.Forms.Screen]::PrimaryScreen"],
                               capture_output=True)
                return "Pillow nicht installiert. Installiere es mit: pip install Pillow"

        elif action == "processes":
            result = subprocess.run(
                ["powershell", "-c",
                 "Get-Process | Sort-Object -Property CPU -Descending | "
                 "Select-Object -First 15 Name,CPU,WorkingSet | "
                 "Format-Table -AutoSize | Out-String"],
                capture_output=True, text=True, timeout=10)
            return f"Top-Prozesse:\n{result.stdout.strip()}"

        elif action == "kill_process":
            if not target:
                return "Welchen Prozess soll ich beenden?"
            result = subprocess.run(
                ["taskkill", "/im", f"{target}.exe" if not target.endswith(".exe") else target, "/f"],
                capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return f"Prozess '{target}' beendet."
            return f"Konnte '{target}' nicht beenden: {result.stderr.strip()}"

        elif action == "open_app":
            if not target:
                return "Welche App soll ich öffnen?"
            app_map = {
                "chrome": "chrome", "browser": "chrome",
                "notepad": "notepad", "editor": "notepad",
                "explorer": "explorer", "dateimanager": "explorer",
                "cmd": "cmd", "terminal": "cmd",
                "rechner": "calc", "calculator": "calc", "taschenrechner": "calc",
                "paint": "mspaint",
                "word": "winword", "excel": "excel", "powerpoint": "powerpnt",
                "spotify": "spotify",
                "discord": "discord",
                "steam": "steam",
                "task-manager": "taskmgr", "taskmanager": "taskmgr",
            }
            app = app_map.get(target.lower(), target)
            subprocess.Popen(["cmd", "/c", "start", app], creationflags=subprocess.CREATE_NO_WINDOW)
            return f"'{target}' wird geöffnet."

        elif action == "disk_space":
            result = subprocess.run(
                ["powershell", "-c",
                 "Get-PSDrive -PSProvider FileSystem | "
                 "Select-Object Name,@{N='Frei(GB)';E={[math]::Round($_.Free/1GB,1)}},"
                 "@{N='Gesamt(GB)';E={[math]::Round(($_.Used+$_.Free)/1GB,1)}} | "
                 "Format-Table -AutoSize | Out-String"],
                capture_output=True, text=True, timeout=10)
            return f"Speicherplatz:\n{result.stdout.strip()}"

        elif action == "battery":
            result = subprocess.run(
                ["powershell", "-c",
                 "(Get-WmiObject Win32_Battery | Select-Object EstimatedChargeRemaining,BatteryStatus).EstimatedChargeRemaining"],
                capture_output=True, text=True, timeout=10)
            charge = result.stdout.strip()
            if charge:
                return f"Akku: {charge}%"
            return "Kein Akku gefunden (Desktop-PC?)."

        elif action == "lock_screen":
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
            return "Bildschirm gesperrt."

        elif action == "empty_trash":
            subprocess.run(
                ["powershell", "-c", "Clear-RecycleBin -Force -Confirm:$false"],
                capture_output=True, timeout=10)
            return "Papierkorb geleert."

        else:
            return "Verwende: screenshot, processes, kill_process, open_app, disk_space, battery, lock_screen, empty_trash"

    except Exception as e:
        return f"System-Fehler: {e}"
