"""
JARVIS Plugin: Tuya / Smart Life — Smart Home control.
Controls lights and switches via the local Tuya protocol (tinytuya).
"""

import json
import sys
from pathlib import Path

try:
    import tinytuya
    _TUYA_OK = True
except ImportError:
    tinytuya = None
    _TUYA_OK = False


def _base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


def _load_devices() -> list[dict]:
    path = _base_dir() / "config" / "tuya_devices.json"
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


def _find_device(name: str, devices: list[dict]) -> dict | None:
    name_l = name.lower()
    for d in devices:
        if name_l in d.get("name", "").lower():
            return d
    return devices[0] if devices else None


def _connect(dev: dict):
    d = tinytuya.BulbDevice(dev["id"], dev["ip"], dev["key"])
    d.set_version(float(dev.get("version", 3.3)))
    return d


def run(action="status", device_name="", brightness=100, color="", **kwargs):
    if not _TUYA_OK:
        return "tinytuya ist nicht installiert. Installiere es mit: pip install tinytuya"

    devices = _load_devices()
    if not devices:
        return ("Keine Tuya-Geraete konfiguriert. "
                "Erstelle config/tuya_devices.json mit: "
                '[{"name":"Licht","id":"...","ip":"...","key":"...","version":"3.3"}]')

    dev_cfg = _find_device(device_name, devices)
    if not dev_cfg:
        names = ", ".join(d.get("name", "?") for d in devices)
        return f"Geraet '{device_name}' nicht gefunden. Verfuegbar: {names}"

    try:
        d = _connect(dev_cfg)

        if action == "on":
            d.turn_on()
            return f"{dev_cfg['name']} eingeschaltet."

        if action == "off":
            d.turn_off()
            return f"{dev_cfg['name']} ausgeschaltet."

        if action == "brightness":
            val = max(10, min(1000, int(float(brightness) * 10)))
            d.set_brightness(val)
            return f"{dev_cfg['name']} Helligkeit auf {brightness}%."

        if action == "color":
            colors = {
                "rot": (255, 0, 0), "red": (255, 0, 0),
                "gruen": (0, 255, 0), "green": (0, 255, 0),
                "blau": (0, 0, 255), "blue": (0, 0, 255),
                "gelb": (255, 255, 0), "yellow": (255, 255, 0),
                "weiss": (255, 255, 255), "white": (255, 255, 255),
                "lila": (128, 0, 255), "purple": (128, 0, 255),
                "orange": (255, 128, 0),
                "pink": (255, 105, 180), "rosa": (255, 105, 180),
                "cyan": (0, 255, 255), "tuerkis": (0, 255, 255),
            }
            rgb = colors.get(color.lower())
            if not rgb:
                return f"Unbekannte Farbe: {color}. Verfuegbar: {', '.join(sorted(set(colors.keys())))}"
            d.set_colour(*rgb)
            return f"{dev_cfg['name']} Farbe auf {color}."

        if action == "status":
            data = d.status()
            return f"{dev_cfg['name']} Status: {json.dumps(data, indent=2)}"

        return f"Unbekannte Aktion: {action}. Verfuegbar: on, off, brightness, color, status"

    except Exception as e:
        return f"Tuya-Fehler: {e}"


PLUGIN = {
    "name": "tuya_control",
    "description": (
        "Smart Home control via Tuya/Smart Life. "
        "Turn lights on/off, set brightness, change colors. "
        "Use when the user wants to control smart home devices, lights, or switches."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "on | off | brightness | color | status",
            },
            "device_name": {
                "type": "STRING",
                "description": "Name of the device to control",
            },
            "brightness": {
                "type": "INTEGER",
                "description": "Brightness percentage 1-100 (for brightness action)",
            },
            "color": {
                "type": "STRING",
                "description": "Color name: rot/red, gruen/green, blau/blue, gelb/yellow, weiss/white, lila/purple, orange, pink/rosa, cyan/tuerkis",
            },
        },
        "required": ["action"],
    },
    "handler": run,
}
