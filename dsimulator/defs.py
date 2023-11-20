"""
Definitions and constants are placed here.

All paths and file locations should be defined here.
"""

import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
RES_DIR = os.path.join(ROOT_DIR, 'res')
SAVE_FILE = os.path.expanduser('~/.dsimulator/save.db')
