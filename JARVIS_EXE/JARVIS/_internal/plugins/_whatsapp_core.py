"""
WhatsApp Desktop driver for JARVIS.
Finds the WhatsApp window, opens a conversation, and sends a message reliably.
"""

import subprocess
import time
import platform

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.05
    _HAS_GUI = True
except ImportError:
    _HAS_GUI = False

_WIN = platform.system() == "Windows"
_HIDE = {"creationflags": subprocess.CREATE_NO_WINDOW} if _WIN else {}


class WhatsAppTransport:
    def __init__(self, hwnd=None):
        self._hwnd = hwnd

    def send_message_to(self, contact: str, message: str):
        if not _HAS_GUI:
            return False, "pyautogui not installed"

        try:
            if not self._activate_window():
                return False, "WhatsApp window not found or could not be activated"

            time.sleep(0.8)

            # Click search bar (Ctrl+F in WhatsApp Desktop opens search)
            pyautogui.hotkey("ctrl", "f")
            time.sleep(0.5)

            # Clear any existing text and type contact name
            pyautogui.hotkey("ctrl", "a")
            time.sleep(0.1)

            # Type contact name character by character for reliability
            for ch in contact:
                pyautogui.typewrite(ch, interval=0.03) if ch.isascii() else pyautogui.write(ch)
            time.sleep(1.2)

            # Press Enter to select first matching contact
            pyautogui.press("enter")
            time.sleep(0.8)

            # Press Escape to close search if it stayed open
            pyautogui.press("escape")
            time.sleep(0.3)

            # Click message input area — it's at the bottom of the window
            # Use Tab to navigate to message input
            pyautogui.hotkey("ctrl", "f")
            time.sleep(0.2)
            pyautogui.press("escape")
            time.sleep(0.3)

            # Type the message using clipboard for Unicode support
            try:
                import pyperclip
                pyperclip.copy(message)
                pyautogui.hotkey("ctrl", "v")
            except ImportError:
                pyautogui.typewrite(message, interval=0.02)

            time.sleep(0.3)
            pyautogui.press("enter")
            time.sleep(0.5)

            return True, None

        except Exception as e:
            return False, str(e)

    def _activate_window(self):
        if not _WIN:
            return False
        try:
            result = subprocess.run(
                ["powershell", "-c",
                 "Get-Process | Where-Object {$_.MainWindowTitle -like '*WhatsApp*'} | "
                 "Select-Object -First 1 -ExpandProperty Id"],
                capture_output=True, text=True, timeout=5, **_HIDE)
            pid = result.stdout.strip()
            if not pid:
                # Try to start WhatsApp
                subprocess.Popen(
                    ["cmd", "/c", "start", "whatsapp:"],
                    **_HIDE)
                time.sleep(3)
                result = subprocess.run(
                    ["powershell", "-c",
                     "Get-Process | Where-Object {$_.MainWindowTitle -like '*WhatsApp*'} | "
                     "Select-Object -First 1 -ExpandProperty Id"],
                    capture_output=True, text=True, timeout=5, **_HIDE)
                pid = result.stdout.strip()
                if not pid:
                    return False

            subprocess.run(
                ["powershell", "-c",
                 f"$sig = '[DllImport(\"user32.dll\")] public static extern bool SetForegroundWindow(IntPtr hWnd);';"
                 f"$type = Add-Type -MemberDefinition $sig -Name WinAPI -PassThru;"
                 f"$proc = Get-Process -Id {pid};"
                 f"$type::SetForegroundWindow($proc.MainWindowHandle)"],
                capture_output=True, timeout=5, **_HIDE)
            time.sleep(0.5)
            return True
        except Exception:
            return False


_instance = None


def get():
    global _instance
    if _instance is None:
        _instance = WhatsAppTransport()
    return _instance, None
