# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/__main__.py'],
    pathex=['.'],
    binaries=[],
    datas=[('README.md', '.')],
    hiddenimports=['PIL._tkinter_finder', 'pystray._base', 'src.version', 'src.metrics', 'src.tray', 'src.tray_qt', 'src.profile_window', 'src.app', 'pystray._appindicator', 'pystray._gtk', 'pystray._xorg'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='l3p',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
