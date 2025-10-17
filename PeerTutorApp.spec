# -*- mode: python ; coding: utf-8 -*-
# to run: pyinstaller PeerTutorApp.spec

a = Analysis(
    ['app.py'],
    pathex=['.'],  
    binaries=[],
    datas=[
        ('templates', 'templates'),  
        ('static', 'static'),        
        ('models.py', '.'),          
        ('auto_email.py', '.'),
        ('persistent_data.py', '.'),
        ('save_schedule_assignment.py', '.'),
        ('data', 'data'),           
    ],
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
