"""
JARVIS Self-Development Plugin.
Allows JARVIS to read, modify, and create its own code — plugins, actions, config.
When the user asks for a new feature, JARVIS generates the code and installs it live.
"""

import json
import importlib
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PLUGINS_DIR = BASE_DIR / "plugins"
ACTIONS_DIR = BASE_DIR / "actions"
CONFIG_DIR = BASE_DIR / "config"

PLUGIN = {
    "name": "self_dev",
    "description": (
        "Self-development: JARVIS can read, modify, and create its own code. "
        "Use when the user asks to add a new feature, create a plugin, modify behavior, "
        "list installed plugins/actions, show source code, or improve JARVIS itself."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": (
                    "One of: list_plugins, list_actions, read_file, write_file, "
                    "create_plugin, create_action, modify_file, delete_plugin, "
                    "reload_plugins, show_structure, get_capabilities"
                ),
            },
            "file_path": {
                "type": "STRING",
                "description": "Relative path within JARVIS (e.g. 'plugins/my_plugin.py')",
            },
            "content": {
                "type": "STRING",
                "description": "File content to write",
            },
            "name": {
                "type": "STRING",
                "description": "Name for new plugin/action",
            },
            "description": {
                "type": "STRING",
                "description": "Description for new plugin/action",
            },
        },
        "required": ["action"],
    },
}


def _safe_path(rel_path):
    """Resolve relative path, ensure it stays within JARVIS directory."""
    target = (BASE_DIR / rel_path).resolve()
    try:
        target.relative_to(BASE_DIR)
    except ValueError:
        return None
    return target


def _list_plugins():
    plugins = []
    for f in sorted(PLUGINS_DIR.glob("*.py")):
        if f.name.startswith("__"):
            continue
        name = f.stem
        desc = ""
        try:
            text = f.read_text(encoding="utf-8")
            for line in text.split("\n"):
                if '"description"' in line or "'description'" in line:
                    desc = line.split(":", 1)[-1].strip().strip('",\'')[:80]
                    break
        except Exception:
            pass
        plugins.append(f"  {name}: {desc}" if desc else f"  {name}")
    return "Installierte Plugins:\n" + "\n".join(plugins) if plugins else "Keine Plugins gefunden."


def _list_actions():
    actions = []
    for f in sorted(ACTIONS_DIR.glob("*.py")):
        if f.name.startswith("__"):
            continue
        actions.append(f"  {f.stem}")
    return "Installierte Actions:\n" + "\n".join(actions) if actions else "Keine Actions gefunden."


def _show_structure():
    lines = ["JARVIS Verzeichnisstruktur:\n"]
    for item in sorted(BASE_DIR.iterdir()):
        if item.name.startswith(".") or item.name == "__pycache__":
            continue
        if item.is_dir():
            count = len(list(item.glob("*.py")))
            lines.append(f"  {item.name}/ ({count} .py Dateien)")
        else:
            lines.append(f"  {item.name} ({item.stat().st_size} bytes)")
    return "\n".join(lines)


def _read_file(rel_path):
    p = _safe_path(rel_path)
    if not p:
        return "Fehler: Pfad ausserhalb von JARVIS."
    if not p.exists():
        return f"Datei nicht gefunden: {rel_path}"
    try:
        text = p.read_text(encoding="utf-8")
        if len(text) > 8000:
            return f"Datei: {rel_path} ({len(text)} Zeichen)\n\n" + text[:8000] + "\n\n[... gekuerzt]"
        return f"Datei: {rel_path}\n\n{text}"
    except Exception as e:
        return f"Lese-Fehler: {e}"


def _write_file(rel_path, content):
    p = _safe_path(rel_path)
    if not p:
        return "Fehler: Pfad ausserhalb von JARVIS."
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Datei geschrieben: {rel_path} ({len(content)} Zeichen)"
    except Exception as e:
        return f"Schreib-Fehler: {e}"


def _create_plugin(name, description, content=None):
    if not name:
        return "Fehler: Plugin-Name fehlt."
    from actions.code_helper import safety_check
    blocked = safety_check(f"{name} {description or ''} {content or ''}")
    if blocked:
        return blocked
    safe_name = name.lower().replace(" ", "_").replace("-", "_")
    path = PLUGINS_DIR / f"{safe_name}.py"
    if path.exists():
        return f"Plugin {safe_name} existiert bereits. Verwende 'modify_file' zum Aendern."

    if not content:
        content = f'''"""
JARVIS Plugin: {name}
{description or ''}
"""


PLUGIN = {{
    "name": "{safe_name}",
    "description": "{description or name}",
    "parameters": {{
        "type": "OBJECT",
        "properties": {{
            "action": {{
                "type": "STRING",
                "description": "Die auszufuehrende Aktion",
            }},
            "input": {{
                "type": "STRING",
                "description": "Eingabe-Parameter",
            }},
        }},
        "required": ["action"],
    }},
}}


def run(action="help", input="", **kwargs):
    if action == "help":
        return "{name}: {description or 'Neues Plugin'}"

    return f"Aktion {{action}} ausgefuehrt."
'''

    try:
        path.write_text(content, encoding="utf-8")
        return (
            f"Plugin erstellt: plugins/{safe_name}.py\n"
            f"Verwende 'reload_plugins' um es zu aktivieren."
        )
    except Exception as e:
        return f"Fehler beim Erstellen: {e}"


def _create_action(name, description, content=None):
    if not name:
        return "Fehler: Action-Name fehlt."
    from actions.code_helper import safety_check
    blocked = safety_check(f"{name} {description or ''} {content or ''}")
    if blocked:
        return blocked
    safe_name = name.lower().replace(" ", "_").replace("-", "_")
    path = ACTIONS_DIR / f"{safe_name}.py"
    if path.exists():
        return f"Action {safe_name} existiert bereits."

    if not content:
        content = f'''"""
JARVIS Action: {name}
{description or ''}
"""

import subprocess
import sys
from pathlib import Path


def run(args: dict) -> str:
    """
    Wird von JARVIS aufgerufen.
    args enthaelt die Parameter der Anfrage.
    """
    return "{name}: Aktion ausgefuehrt."
'''

    try:
        path.write_text(content, encoding="utf-8")
        return f"Action erstellt: actions/{safe_name}.py"
    except Exception as e:
        return f"Fehler beim Erstellen: {e}"


def _modify_file(rel_path, content):
    p = _safe_path(rel_path)
    if not p or not p.exists():
        return f"Datei nicht gefunden: {rel_path}"
    try:
        backup = p.with_suffix(p.suffix + ".bak")
        backup.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
        p.write_text(content, encoding="utf-8")
        return f"Datei geaendert: {rel_path} (Backup: {backup.name})"
    except Exception as e:
        return f"Fehler: {e}"


def _delete_plugin(name):
    safe_name = name.lower().replace(" ", "_").replace("-", "_")
    path = PLUGINS_DIR / f"{safe_name}.py"
    if not path.exists():
        return f"Plugin {safe_name} nicht gefunden."
    if safe_name in ("discord_bot", "alexa_control", "system_control", "self_dev"):
        return f"Kern-Plugin {safe_name} kann nicht geloescht werden."
    try:
        backup = path.with_suffix(".py.bak")
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        path.unlink()
        return f"Plugin {safe_name} geloescht (Backup: {backup.name})"
    except Exception as e:
        return f"Fehler: {e}"


def _reload_plugins():
    count = 0
    for f in PLUGINS_DIR.glob("*.py"):
        if f.name.startswith("__"):
            continue
        mod_name = f"plugins.{f.stem}"
        try:
            if mod_name in sys.modules:
                importlib.reload(sys.modules[mod_name])
            else:
                importlib.import_module(mod_name)
            count += 1
        except Exception as e:
            return f"Fehler beim Laden von {f.stem}: {e}"
    return f"{count} Plugins neu geladen."


def _get_capabilities():
    caps = []
    caps.append("=== JARVIS Self-Development ===\n")
    caps.append("JARVIS kann seinen eigenen Code lesen und aendern:")
    caps.append("  - Neue Plugins erstellen (plugins/ Ordner)")
    caps.append("  - Neue Actions erstellen (actions/ Ordner)")
    caps.append("  - Bestehenden Code lesen und modifizieren")
    caps.append("  - Plugins hot-reloaden ohne Neustart")
    caps.append("  - Verzeichnisstruktur anzeigen")
    caps.append("")
    caps.append("Sage z.B.:")
    caps.append('  "Erstelle ein Plugin das Witze erzaehlt"')
    caps.append('  "Zeig mir den Code von discord_bot"')
    caps.append('  "Fuege eine neue Funktion hinzu die..."')
    caps.append('  "Welche Plugins sind installiert?"')
    caps.append('  "Aendere das Wetter-Plugin so dass..."')
    return "\n".join(caps)


def run(action="get_capabilities", file_path="", content="", name="", description="", **kwargs):
    if action == "list_plugins":
        return _list_plugins()
    if action == "list_actions":
        return _list_actions()
    if action == "show_structure":
        return _show_structure()
    if action == "read_file":
        return _read_file(file_path)
    if action == "write_file":
        return _write_file(file_path, content)
    if action == "create_plugin":
        return _create_plugin(name, description, content)
    if action == "create_action":
        return _create_action(name, description, content)
    if action == "modify_file":
        return _modify_file(file_path, content)
    if action == "delete_plugin":
        return _delete_plugin(name)
    if action == "reload_plugins":
        return _reload_plugins()
    if action == "get_capabilities":
        return _get_capabilities()
    return f"Unbekannte Aktion: {action}. Verwende 'get_capabilities' fuer Hilfe."
