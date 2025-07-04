# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Frontend HTML
        ('frontend/simulador_conectado.html', 'frontend'),
        # Backend files
        ('backend/simulador_backend_python.py', 'backend'),
        ('backend/simulador_backend_python.exe', 'backend'),  # Si existe
        ('backend/templates/*.html', 'backend/templates'),    # Templates de Flask
        
    ],
    hiddenimports=[
        'flask',
        'flask.templating',
        'flask.json',
        'werkzeug',
        'werkzeug.serving',
        'requests',
        'webview',
        'threading',
        'subprocess',
        'pathlib',
        'logging',
        'signal',
        'atexit',
    ],
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
    name='SimuladorCPU',  
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Cambiar a False para aplicación sin consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)