block_cipher = None

a = Analysis(
    ['src/main.py'],  # Main entry point
    pathex=['src'],   # Add source directory to Python path
    binaries=[],
    datas=[
        ('src/ui_design/*.ui', 'ui_design'),
        ('sat.spec', 'ui_logic'),   # For Linux compatibility; ui_logic folder must be present for path traversal 
        ('src/resources', 'resources'),
    ],

    hiddenimports=[
        'database.main_database',
        'database.default_database_details',
        'constants',
        'ui_logic.new_setup',
        'ui_logic.login',
        'ui_logic.dashboard_processing', 
        'ui_logic.password_change',
        'ui_logic.create_account',
        'ui_logic.question_processing',
        'ui_logic.survey_processing',
        'ui_logic.scores',
        'sqlalchemy.sql.default_comparator'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries, 
    a.zipfiles,
    a.datas,
    [],
    name='SAT',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/resources/logos/favicon.ico'
)
