# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
import os

block_cipher = None
BASE = os.path.abspath('.')

a = Analysis(
    ['main.py'],
    pathex=[BASE],
    binaries=[],
    datas=[
        ('dashboard', 'dashboard'),
        ('actions', 'actions'),
        ('core', 'core'),
        ('memory', 'memory'),
        ('plugins', 'plugins'),
        ('config/__init__.py', 'config'),
        ('config/jarvis.ico', 'config'),
        ('config/alexa_skill_model.json', 'config'),
        ('requirements.txt', '.'),
        ('INSTALL.md', '.'),
    ],
    hiddenimports=[
        'config',
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'fastapi',
        'google.genai',
        'google.genai.live',
        'PIL',
        'cv2',
        'numpy',
        'sounddevice',
        'psutil',
        'cryptography',
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtMultimedia',
        'PyQt6.QtMultimediaWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='JARVIS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon='config/jarvis.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='JARVIS',
)
