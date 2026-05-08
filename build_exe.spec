# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller打包配置 - 用于生成Windows独立EXE"""

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates/index.html', 'templates'),
        ('static/css/style.css', 'static/css'),
        ('static/js/main.js', 'static/js'),
        ('config.py', '.'),
        ('mock_responses.py', '.'),
    ],
    hiddenimports=['flask', 'jinja2', 'markupsafe', 'werkzeug', 'mock_responses'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas', 'PIL', 'cv2'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='动物习作AI智能助教',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,        # True=显示控制台窗口, False=隐藏
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico',  # 可替换为自定义图标
)
