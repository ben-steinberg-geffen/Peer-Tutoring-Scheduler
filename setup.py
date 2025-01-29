from setuptools import setup

APP = ['interface.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['PyQt5'],
    'includes': ['pandas'],
    'iconfile': 'MyIcon.icns',  # Optional: if you have an icon file
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)