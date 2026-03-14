import pygame
import os
import sys # <-- Add this

WIDTH, HEIGHT = 1280, 720
FPS = 15
CELL_SIZE = 60

BG_COLOR = (45, 52, 54)
GRID_COLOR = (255, 255, 255) 
UI_BG = (223, 230, 233)
TEXT_COLOR = (45, 52, 54)
BTN_COLOR = (116, 185, 255)
BTN_HOVER = (9, 132, 227)

# --- NEW PYINSTALLER ASSET LOGIC ---
def get_resource_path():
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return base_path

ASSETS_DIR = os.path.join(get_resource_path(), 'assets')
IMG_DIR = os.path.join(ASSETS_DIR, 'images')
SND_DIR = os.path.join(ASSETS_DIR, 'sounds')