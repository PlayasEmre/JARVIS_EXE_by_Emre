"""
JARVIS Discord Bot Plugin.
Full Discord control: send/receive messages, manage servers, voice channels.
"""

import asyncio
import json
import threading
from pathlib import Path

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "api_keys.json"
_bot_thread = None
_client = None
_channel_id = None
_loop = None
_incoming_messages = []

PLUGIN = {
    "name": "discord_bot",
    "description": (
        "Full Discord control. Send messages, read messages, list servers and channels, "
        "check who is online, react to messages, set status, and manage Discord. "
        "Use when the user asks anything about Discord: send a message, check Discord, "
        "who is online, list channels, start/stop the bot."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "One of: send, dm, start, stop, status, read, servers, channels, online, members, set_status, create_channel, delete_channel, rename_channel, create_role, kick, ban, nickname",
            },
            "message": {
                "type": "STRING",
                "description": "Message text to send",
            },
            "channel_name": {
                "type": "STRING",
                "description": "Channel name to send to (optional, uses default)",
            },
            "username": {
                "type": "STRING",
                "description": "Discord username or display name for DM (private message)",
            },
            "status_text": {
                "type": "STRING",
                "description": "Custom status text for set_status",
            },
        },
        "required": ["action"],
    },
}


def _load_config():
    try:
        return json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_config(data):
    try:
        existing = _load_config()
        existing.update(data)
        _CONFIG_PATH.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    except Exception:
        pass


def _send_sync(text: str, channel_name: str = "") -> str:
    global _client, _loop
    cfg = _load_config()
    channel_id = cfg.get("discord_channel_id", "")
    if not _client or not _loop or not channel_id:
        return "Discord Bot ist nicht aktiv. Starte den Bot zuerst mit action: start"
    try:
        target_id = int(channel_id)
        if channel_name and _client.guilds:
            found = False
            for guild in _client.guilds:
                for ch in guild.text_channels:
                    if ch.name.lower() == channel_name.lower():
                        target_id = ch.id
                        found = True
                        break
                if found:
                    break

        future = asyncio.run_coroutine_threadsafe(_send_message(target_id, text), _loop)
        future.result(timeout=10)
        return f"Discord-Nachricht gesendet: {text[:80]}"
    except Exception as e:
        return f"Discord-Fehler: {e}"


async def _send_message(channel_id: int, text: str):
    channel = _client.get_channel(channel_id)
    if channel:
        await channel.send(f"**[JARVIS]** {text}")


def _start_listener() -> str:
    global _bot_thread, _client, _loop
    cfg = _load_config()
    token = cfg.get("discord_bot_token", "")
    if not token:
        return ("Kein Discord Bot Token konfiguriert. So gehts:\n"
                "1. discord.com/developers/applications -> New Application\n"
                "2. Bot -> Reset Token -> kopieren\n"
                "3. Privileged Gateway Intents: Message Content Intent AN\n"
                "4. OAuth2 -> URL Generator -> bot -> Send Messages + Read Message History\n"
                "5. Bot mit Link zum Server einladen\n"
                "6. Token als 'discord_bot_token' in config/api_keys.json eintragen")
    if _bot_thread and _bot_thread.is_alive():
        return "Discord Bot läuft bereits."

    def _run_bot():
        global _client, _loop
        try:
            import discord

            intents = discord.Intents.default()
            intents.message_content = True
            intents.members = True
            intents.presences = True
            client = discord.Client(intents=intents)
            _client = client

            @client.event
            async def on_ready():
                print(f"[Discord] Bot eingeloggt als {client.user}")
                for guild in client.guilds:
                    for channel in guild.text_channels:
                        if channel.permissions_for(guild.me).send_messages:
                            _save_config({"discord_channel_id": str(channel.id)})
                            await channel.send(
                                "**[JARVIS]** Online und bereit, Emre Master!"
                            )
                            break
                    break

            @client.event
            async def on_message(message):
                if message.author == client.user:
                    return
                if client.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
                    user_text = message.content.replace(f"<@{client.user.id}>", "").strip()
                    _save_config({"discord_channel_id": str(message.channel.id)})
                    _incoming_messages.append({
                        "from": str(message.author),
                        "text": user_text,
                        "channel": str(message.channel),
                        "time": message.created_at.strftime("%H:%M"),
                    })
                    await message.channel.send(
                        f"**[JARVIS]** Nachricht empfangen, Emre Master wird benachrichtigt."
                    )

            _loop = asyncio.new_event_loop()
            asyncio.set_event_loop(_loop)
            _loop.run_until_complete(client.start(token))
        except Exception as e:
            print(f"[Discord] Bot-Fehler: {e}")

    _bot_thread = threading.Thread(target=_run_bot, daemon=True, name="discord-bot")
    _bot_thread.start()
    return "Discord Bot wird gestartet..."


def _get_servers() -> str:
    if not _client or not _client.guilds:
        return "Bot nicht verbunden oder kein Server."
    lines = []
    for guild in _client.guilds:
        lines.append(f"- {guild.name} ({guild.member_count} Mitglieder)")
    return "Discord Server:\n" + "\n".join(lines)


def _get_channels() -> str:
    if not _client or not _client.guilds:
        return "Bot nicht verbunden."
    lines = []
    for guild in _client.guilds:
        lines.append(f"**{guild.name}:**")
        for ch in guild.text_channels[:15]:
            lines.append(f"  # {ch.name}")
    return "\n".join(lines)


def _get_online() -> str:
    if not _client or not _client.guilds:
        return "Bot nicht verbunden."
    try:
        import discord
        lines = []
        for guild in _client.guilds:
            online = [m for m in guild.members if m.status != discord.Status.offline and not m.bot]
            if online:
                lines.append(f"**{guild.name}** ({len(online)} online):")
                for m in online[:20]:
                    activity = ""
                    if m.activity:
                        activity = f" — {m.activity.name}" if hasattr(m.activity, "name") else ""
                    lines.append(f"  - {m.display_name}{activity}")
        return "\n".join(lines) if lines else "Niemand online."
    except Exception as e:
        return f"Fehler: {e}"


def _get_members() -> str:
    if not _client or not _client.guilds:
        return "Bot nicht verbunden."
    lines = []
    for guild in _client.guilds:
        members = [m for m in guild.members if not m.bot]
        lines.append(f"**{guild.name}** ({len(members)} Mitglieder):")
        for m in members[:30]:
            status = str(m.status).replace("dnd", "nicht stören")
            lines.append(f"  - {m.display_name} ({m.name}) [{status}]")
    return "\n".join(lines) if lines else "Keine Mitglieder gefunden."


def _send_dm(username: str, text: str) -> str:
    if not _client or not _loop:
        return "Bot nicht aktiv. Starte den Bot zuerst."
    if not username:
        return "Kein Benutzername angegeben."
    if not text:
        return "Keine Nachricht angegeben."

    member = None
    uname = username.lower().strip()
    for guild in _client.guilds:
        for m in guild.members:
            if m.bot:
                continue
            if (m.display_name.lower() == uname or
                    m.name.lower() == uname or
                    uname in m.display_name.lower() or
                    uname in m.name.lower()):
                member = m
                break
        if member:
            break

    if not member:
        return f"Benutzer '{username}' nicht auf dem Server gefunden."

    try:
        async def _do_dm():
            dm_channel = await member.create_dm()
            await dm_channel.send(f"**[JARVIS]** {text}")

        future = asyncio.run_coroutine_threadsafe(_do_dm(), _loop)
        future.result(timeout=10)
        return f"Private Nachricht an {member.display_name} gesendet: {text[:80]}"
    except Exception as e:
        return f"DM-Fehler: {e}"


def _read_messages() -> str:
    global _incoming_messages
    if not _incoming_messages:
        return "Keine neuen Discord-Nachrichten."
    msgs = _incoming_messages.copy()
    _incoming_messages.clear()
    lines = [f"[{m['time']}] {m['from']}: {m['text']}" for m in msgs]
    return f"{len(msgs)} neue Nachrichten:\n" + "\n".join(lines)


def _set_status(text: str) -> str:
    if not _client or not _loop:
        return "Bot nicht aktiv."
    try:
        import discord
        activity = discord.Game(name=text) if text else None
        future = asyncio.run_coroutine_threadsafe(
            _client.change_presence(activity=activity), _loop)
        future.result(timeout=5)
        return f"Discord-Status gesetzt: {text}" if text else "Discord-Status entfernt."
    except Exception as e:
        return f"Status-Fehler: {e}"


def _find_guild():
    if not _client or not _client.guilds:
        return None
    return _client.guilds[0]


def _find_member(name: str):
    guild = _find_guild()
    if not guild:
        return None
    name_l = name.lower().strip()
    for m in guild.members:
        if m.bot:
            continue
        if (m.display_name.lower() == name_l or
                m.name.lower() == name_l or
                name_l in m.display_name.lower() or
                name_l in m.name.lower()):
            return m
    return None


def _server_action(action: str, name: str, message: str = "") -> str:
    if not _client or not _loop:
        return "Bot nicht aktiv. Starte den Bot zuerst."
    guild = _find_guild()
    if not guild:
        return "Kein Server verbunden."

    try:
        import discord

        if action == "create_channel":
            if not name:
                return "Wie soll der Channel heißen?"
            channel_type = "voice" if "voice" in message.lower() or "sprach" in message.lower() else "text"

            async def _create():
                if channel_type == "voice":
                    ch = await guild.create_voice_channel(name)
                    return f"Voice-Channel '#{ch.name}' erstellt."
                else:
                    ch = await guild.create_text_channel(name)
                    return f"Text-Channel '#{ch.name}' erstellt."

            future = asyncio.run_coroutine_threadsafe(_create(), _loop)
            return future.result(timeout=10)

        elif action == "delete_channel":
            if not name:
                return "Welchen Channel soll ich löschen?"

            async def _delete():
                for ch in guild.channels:
                    if ch.name.lower() == name.lower().strip():
                        await ch.delete()
                        return f"Channel '#{name}' gelöscht."
                return f"Channel '{name}' nicht gefunden."

            future = asyncio.run_coroutine_threadsafe(_delete(), _loop)
            return future.result(timeout=10)

        elif action == "rename_channel":
            if not name or not message:
                return "Alter Name und neuer Name nötig."

            async def _rename():
                for ch in guild.channels:
                    if ch.name.lower() == name.lower().strip():
                        await ch.edit(name=message)
                        return f"Channel umbenannt: #{name} → #{message}"
                return f"Channel '{name}' nicht gefunden."

            future = asyncio.run_coroutine_threadsafe(_rename(), _loop)
            return future.result(timeout=10)

        elif action == "create_role":
            if not name:
                return "Wie soll die Rolle heißen?"

            async def _role():
                role = await guild.create_role(name=name, mentionable=True)
                return f"Rolle '{role.name}' erstellt."

            future = asyncio.run_coroutine_threadsafe(_role(), _loop)
            return future.result(timeout=10)

        elif action == "kick":
            member = _find_member(name)
            if not member:
                return f"Benutzer '{name}' nicht gefunden."
            reason = message or "Kicked by JARVIS"

            async def _kick():
                await guild.kick(member, reason=reason)
                return f"{member.display_name} wurde gekickt. Grund: {reason}"

            future = asyncio.run_coroutine_threadsafe(_kick(), _loop)
            return future.result(timeout=10)

        elif action == "ban":
            member = _find_member(name)
            if not member:
                return f"Benutzer '{name}' nicht gefunden."
            reason = message or "Banned by JARVIS"

            async def _ban():
                await guild.ban(member, reason=reason)
                return f"{member.display_name} wurde gebannt. Grund: {reason}"

            future = asyncio.run_coroutine_threadsafe(_ban(), _loop)
            return future.result(timeout=10)

        elif action == "nickname":
            member = _find_member(name)
            if not member:
                return f"Benutzer '{name}' nicht gefunden."
            if not message:
                return "Welcher Nickname?"

            async def _nick():
                await member.edit(nick=message)
                return f"Nickname von {member.name} geändert zu: {message}"

            future = asyncio.run_coroutine_threadsafe(_nick(), _loop)
            return future.result(timeout=10)

        return f"Unbekannte Server-Aktion: {action}"
    except Exception as e:
        return f"Server-Fehler: {e}"


def run(parameters: dict, player=None, session_memory=None) -> str:
    action = parameters.get("action", "").lower()
    message = parameters.get("message", "")

    if action == "send":
        if not message:
            return "Keine Nachricht angegeben."
        channel_name = parameters.get("channel_name", "")
        return _send_sync(message, channel_name)
    elif action == "start":
        return _start_listener()
    elif action == "stop":
        global _client, _bot_thread, _loop
        if _client and _loop:
            try:
                future = asyncio.run_coroutine_threadsafe(_client.close(), _loop)
                future.result(timeout=5)
            except Exception:
                pass
            _client = None
            _bot_thread = None
            _loop = None
            return "Discord Bot gestoppt."
        return "Discord Bot war nicht aktiv."
    elif action == "status":
        cfg = _load_config()
        has_token = bool(cfg.get("discord_bot_token"))
        running = _bot_thread and _bot_thread.is_alive()
        return (f"Discord Bot: {'aktiv' if running else 'inaktiv'}, "
                f"Token: {'gesetzt' if has_token else 'fehlt'}")
    elif action == "read":
        return _read_messages()
    elif action == "servers":
        return _get_servers()
    elif action == "channels":
        return _get_channels()
    elif action == "online":
        return _get_online()
    elif action == "members":
        return _get_members()
    elif action == "dm":
        username = parameters.get("username", "")
        if not username:
            return "Welchem Benutzer soll ich schreiben?"
        if not message:
            return "Keine Nachricht angegeben."
        return _send_dm(username, message)
    elif action == "set_status":
        return _set_status(parameters.get("status_text", message))
    elif action in ("create_channel", "delete_channel", "rename_channel",
                     "create_role", "kick", "ban", "nickname"):
        target = parameters.get("username", "") or parameters.get("channel_name", "")
        return _server_action(action, target, message)
    else:
        return "Verwende: send, dm, create_channel, delete_channel, rename_channel, create_role, kick, ban, nickname, members, online, set_status"
