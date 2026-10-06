# JARVIS Mark LV — Installation

**Ein persönlicher KI-Assistent von FatihMakes.**
Sprachsteuerung, Chat, Smart Home, Discord, Alexa — alles in einem.

---

## Was du brauchst

- **Windows 10/11** (macOS und Linux gehen auch)
- **Python 3.11 oder 3.12** — [python.org/downloads](https://www.python.org/downloads/)
- **Gemini API Key** (kostenlos) — [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

---

## Installation (5 Minuten)

### Schritt 1: JARVIS herunterladen

Lade den Ordner `Mark-LV-main` herunter und entpacke ihn.

### Schritt 2: Setup ausführen

Öffne ein Terminal im JARVIS-Ordner und führe aus:

```bash
python setup.py
```

Das installiert alle Abhängigkeiten automatisch.

### Schritt 3: API-Key eintragen

Öffne die Datei `config/api_keys.json` und trage deinen Gemini API-Key ein:

```json
{
    "gemini_api_key": "DEIN_GEMINI_API_KEY_HIER",
    "os_system": "windows",
    "user_name": "Dein Name",
    "dashboard_pin": "JARVIS"
}
```

Alles andere (Discord, Alexa, etc.) ist optional — nur `gemini_api_key` muss rein.

### Schritt 4: JARVIS starten

```bash
python main.py
```

Fertig! JARVIS öffnet sich mit der Hologramm-UI.

---

## Handy-App (optional)

JARVIS hat eine Android-App für Steuerung per Handy.

1. Übertrage `JARVIS.apk` auf dein Handy
2. Installiere die APK (Unbekannte Quellen erlauben)
3. Gib deine PC-IP-Adresse ein (z.B. `192.168.0.XXX`)
4. Port: `8000`
5. PIN: `JARVIS` (oder was du in `dashboard_pin` gesetzt hast)

Die App funktioniert über WLAN im gleichen Netzwerk.

---

## Von unterwegs steuern (optional)

Damit JARVIS auch unterwegs erreichbar ist, brauchst du ngrok:

1. Registriere dich auf [ngrok.com](https://ngrok.com) (kostenlos)
2. Installiere ngrok und starte es:

```bash
ngrok http 8000
```

3. Die angezeigte URL (z.B. `https://abc-xyz.ngrok-free.dev`) in der App als Server-Adresse eingeben
4. Port: `443`

---

## Alexa-Steuerung (optional)

JARVIS kann über Amazon Echo gesteuert werden.

1. Gehe zu [developer.amazon.com/alexa/console/ask](https://developer.amazon.com/alexa/console/ask)
2. Erstelle einen neuen Skill:
   - Name: **JARVIS**
   - Sprache: **Deutsch**
   - Typ: **Custom**
   - Hosting: **Eigener Endpoint (HTTPS)**
3. Im **JSON Editor** die Datei `config/alexa_skill_model.json` hochladen
4. Unter **Endpoint** → HTTPS:
   - URL: `https://DEINE-NGROK-URL/api/alexa-skill`
   - SSL: *My development endpoint is a sub-domain of a domain that has a wildcard certificate*
5. **Build** klicken und testen

Dann sagst du: **"Alexa, öffne mein jarvis"**

---

## Discord Bot (optional)

1. Erstelle einen Bot auf [discord.com/developers](https://discord.com/developers/applications)
2. Kopiere den Bot-Token
3. In `config/api_keys.json` eintragen:

```json
{
    "discord_bot_token": "DEIN_BOT_TOKEN",
    "discord_channel_id": "DEINE_CHANNEL_ID"
}
```

4. Bot in deinen Server einladen
5. JARVIS sagen: "Starte den Discord Bot"

---

## Alle Funktionen

| Funktion | Beschreibung |
|----------|-------------|
| **Sprachassistent** | Echtzeit-Gespräch über Mikrofon (Gemini Live) |
| **Dashboard** | Web-Interface unter `http://IP:8000` |
| **Handy-App** | Native Android-App mit Chat und Spracherkennung |
| **Alexa** | Steuerung über Amazon Echo |
| **Discord** | Bot liest/sendet Nachrichten, verwaltet Server |
| **PC-Steuerung** | Programme öffnen, Screenshot, Prozesse, Speicherplatz |
| **Smart Home** | Tuya/Smart Life Geräte steuern |
| **Web-Suche** | Googelt für dich und fasst Ergebnisse zusammen |
| **Browser** | Öffnet Webseiten, füllt Formulare aus |
| **Dateien** | PDF, Word, Excel, PowerPoint lesen und erstellen |
| **Gedächtnis** | Merkt sich deinen Namen, Vorlieben, Projekte |
| **Selbst-Entwicklung** | Kann sich selbst neue Plugins schreiben |
| **Wake Word** | "Hey Jarvis" zum Aufwecken (optional) |
| **Hologramm** | 3D-Avatar im Iron-Man-Stil |

---

## Fehlerbehebung

**JARVIS startet nicht?**
- Prüfe ob Python 3.11+ installiert ist: `python --version`
- Führe `python setup.py` nochmal aus

**Handy verbindet nicht?**
- PC und Handy müssen im gleichen WLAN sein
- Firewall: Port 8000 freigeben
- IP-Adresse prüfen: `ipconfig` im Terminal

**Kein Ton?**
- Mikrofon und Lautsprecher in den Windows-Einstellungen prüfen
- JARVIS neu starten

---

*JARVIS Mark LV — by FatihMakes*
