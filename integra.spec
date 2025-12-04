# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('src/assets/*', 'assets'),
        ('src/utils/*.svg', 'utils'),
    ],
    hiddenimports=[
        'models',
        'models.database',
        'models.client',
        'ui',
        'ui.main_window',
        'ui.client_list_view',
        'ui.client_form_dialog',
        'ui.about_dialog',
        'ui.simple_update_dialog',
        'controllers',
        'controllers.client_controller',
        'utils',
        'utils.simple_updater',
        'utils.version',
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
    name='Integra Client Manager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Integra Client Manager',
)

app = BUNDLE(
    coll,
    name='Integra Client Manager.app',
    icon='src/assets/app_icon.ico',
    bundle_identifier='com.integra.clientmanager',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'All Files',
                'CFBundleTypeOSTypes': ['****'],
                'CFBundleTypeRole': 'Viewer'
            }
        ]
    },
)