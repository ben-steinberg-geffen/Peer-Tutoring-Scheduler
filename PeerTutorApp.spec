# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=['.'],  # Assumes all your files are in the current directory
    binaries=[],
    datas=[
        ('templates', 'templates'),  # Include 'templates' folder
        ('static', 'static'),        # Include 'static' folder
        ('models.py', '.'),          # Include individual Python files
        ('auto_email.py', '.'),
        ('persistent_data.py', '.'),
        ('save_schedule_assignment.py', '.'),
        ('data', 'data'),            # Include the 'data' folder
        # Add any other folders/files your app needs
    ],
    # ... rest of the Analysis block ...
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PeerTutorApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
app = BUNDLE(
    exe,
    name='PeerTutorApp.app',
    icon=None,
    bundle_identifier=None,
)
