"""
py2app setup script for 动物习作AI智能助教
Build: python3 setup.py py2app
"""

from setuptools import setup

APP = ['app.py']
APP_NAME = '动物习作AI智能助教'

DATA_FILES = [
    ('templates', ['templates/index.html']),
    ('static/css', ['static/css/style.css']),
    ('static/js', ['static/js/main.js']),
]

OPTIONS = {
    'argv_emulation': False,
    'includes': [
        'flask', 'jinja2', 'markupsafe', 'werkzeug',
        'mock_responses', 'config',
    ],
    'packages': ['flask', 'jinja2', 'werkzeug'],
    'iconfile': None,
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleIdentifier': 'com.huimin.animal-writing-assistant',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0',
        'NSHighResolutionCapable': True,
    },
    'site_packages': True,
}

setup(
    name=APP_NAME,
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
