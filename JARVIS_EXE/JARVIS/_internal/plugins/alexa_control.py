"""
JARVIS Alexa Control Plugin.
Communicates via a custom Alexa Skill — works locally and on VPS.
JARVIS exposes /api/alexa-skill endpoint, Alexa Skill sends requests to it.
"""

import json
import logging
from pathlib import Path

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "api_keys.json"
_log = logging.getLogger("jarvis.alexa")

PLUGIN = {
    "name": "alexa_control",
    "description": (
        "Control Amazon Alexa devices. Use when the user asks to play music on Alexa, "
        "set Alexa volume, ask Alexa something, make Alexa announce something, "
        "control smart home devices via Alexa, set Alexa timer, or anything Alexa-related."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "One of: speak, play_music, volume, pause, resume, stop, announce, routine, status, setup",
            },
            "text": {
                "type": "STRING",
                "description": "Text to speak/announce, music query, or command text",
            },
            "device": {
                "type": "STRING",
                "description": "Alexa device name",
            },
            "volume": {
                "type": "STRING",
                "description": "Volume level 0-10",
            },
        },
        "required": ["action"],
    },
}

_pending_response: str | None = None


def _load_config():
    try:
        return json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def set_pending_response(text: str):
    global _pending_response
    _pending_response = text


def get_and_clear_response() -> str | None:
    global _pending_response
    r = _pending_response
    _pending_response = None
    return r


def build_alexa_response(text: str, end_session: bool = False, reprompt: str = "") -> dict:
    resp = {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": text,
            },
            "shouldEndSession": end_session,
        },
    }
    if not end_session:
        resp["response"]["reprompt"] = {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt or "Kann ich noch etwas für dich tun?",
            }
        }
    return resp


def handle_skill_request(body: dict, command_callback=None) -> dict:
    req_type = body.get("request", {}).get("type", "")

    if req_type == "LaunchRequest":
        return build_alexa_response(
            "Jarvis ist bereit. Was kann ich für dich tun?",
            end_session=False,
        )

    if req_type == "SessionEndedRequest":
        return build_alexa_response("Bis später.", end_session=True)

    if req_type == "IntentRequest":
        intent = body.get("request", {}).get("intent", {})
        intent_name = intent.get("name", "")

        if intent_name in ("AMAZON.StopIntent", "AMAZON.CancelIntent"):
            return build_alexa_response("Alles klar, bis später.", end_session=True)

        if intent_name == "AMAZON.HelpIntent":
            return build_alexa_response(
                "Du kannst mir einen Befehl geben. Zum Beispiel: "
                "Frag Jarvis wie das Wetter wird. Oder: Sag Jarvis spiel Musik.",
                end_session=False,
            )

        if intent_name == "JarvisCommandIntent":
            slots = intent.get("slots", {})
            command = slots.get("command", {}).get("value", "")
            if not command:
                return build_alexa_response(
                    "Ich habe dich nicht verstanden. Was soll ich tun?",
                    end_session=False,
                )

            _log.info("Alexa command: %s", command)

            if command_callback:
                try:
                    result = command_callback(command)
                    if result:
                        if len(result) > 600:
                            result = result[:597] + "..."
                        return build_alexa_response(result, end_session=False)
                except Exception as e:
                    _log.error("Command error: %s", e)
                    return build_alexa_response(
                        f"Fehler bei der Verarbeitung: {e}", end_session=False
                    )

            return build_alexa_response(f"Befehl empfangen: {command}", end_session=False)

        return build_alexa_response("Das habe ich nicht verstanden.")

    return build_alexa_response("Unbekannte Anfrage.")


def run(parameters: dict, player=None, session_memory=None) -> str:
    action = parameters.get("action", "").lower()
    text = parameters.get("text", "")

    if action == "setup":
        cfg = _load_config()
        skill_id = cfg.get("alexa_skill_id", "")
        ngrok_url = cfg.get("ngrok_url", "")

        lines = [
            "Alexa Skill Setup — So geht's:",
            "",
            "1. Gehe zu: https://developer.amazon.com/alexa/console/ask",
            "2. Erstelle einen neuen Skill:",
            "   - Name: JARVIS",
            "   - Sprache: Deutsch",
            "   - Typ: Custom / Benutzerdefiniert",
            "   - Hosting: eigener Endpoint (HTTPS)",
            "",
            "3. Im Skill-Editor unter 'Interaction Model' → 'JSON Editor':",
            "   Lade die Datei: config/alexa_skill_model.json",
            "",
            "4. Unter 'Endpoint' → HTTPS:",
        ]
        if ngrok_url:
            lines.append(f"   URL: {ngrok_url}/api/alexa-skill")
        else:
            lines.append("   URL: https://DEINE-URL/api/alexa-skill")
            lines.append("   (Nutze ngrok oder deine VPS-Domain)")
        lines += [
            "   SSL: 'My development endpoint is a sub-domain of a domain that has a wildcard certificate'",
            "",
            "5. Skill testen im 'Test'-Tab oder direkt auf deinem Echo",
            "",
            "Dann sagst du: 'Alexa, frag Jarvis ...'",
        ]
        if skill_id:
            lines.append(f"\nSkill-ID: {skill_id}")
        return "\n".join(lines)

    if action == "status":
        cfg = _load_config()
        skill_id = cfg.get("alexa_skill_id", "")
        ngrok_url = cfg.get("ngrok_url", "")
        lines = ["Alexa Skill Status:"]
        if skill_id:
            lines.append(f"  Skill-ID: {skill_id}")
        else:
            lines.append("  Skill: Nicht konfiguriert")
        if ngrok_url:
            lines.append(f"  Endpoint: {ngrok_url}/api/alexa-skill")
        else:
            lines.append("  Endpoint: Nicht konfiguriert")
        return "\n".join(lines)

    if action in ("speak", "announce", "play_music", "volume", "pause", "resume", "stop", "routine"):
        return (
            f"Alexa-Befehl '{action}' wird über den Alexa Skill gesteuert. "
            "Sage auf deinem Echo: 'Alexa, sag Jarvis " + (text or action) + "'"
        )

    return (
        "Verfügbare Aktionen: speak, announce, play_music, volume, "
        "pause, resume, stop, routine, status, setup"
    )
