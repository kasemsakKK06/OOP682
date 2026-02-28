# utils.py – Utility functions for the SaraAdventure game

"""Utility module providing helper functions for loading images and sounds,
and playing sound effects safely. This centralizes asset handling and makes
the main code cleaner.
"""

import os
import pygame
from typing import Dict

# Cache dictionaries to avoid loading the same asset multiple times
_image_cache: Dict[str, pygame.Surface] = {}
_sound_cache: Dict[str, pygame.mixer.Sound] = {}


def load_image(path: str) -> pygame.Surface:
    """Load an image from the given path and cache it.

    Args:
        path: Absolute or relative path to the image file.

    Returns:
        A pygame.Surface with per-pixel alpha if possible.
    """
    if path in _image_cache:
        return _image_cache[path]
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image file not found: {path}")
    image = pygame.image.load(path).convert_alpha()
    _image_cache[path] = image
    return image


def load_sound(path: str) -> pygame.mixer.Sound:
    """Load a sound file and cache it.

    Args:
        path: Absolute or relative path to the sound file.

    Returns:
        A pygame.mixer.Sound object.
    """
    if path in _sound_cache:
        return _sound_cache[path]
    if not os.path.exists(path):
        raise FileNotFoundError(f"Sound file not found: {path}")
    sound = pygame.mixer.Sound(path)
    _sound_cache[path] = sound
    return sound


def play_sound(sound: pygame.mixer.Sound, loops: int = 0) -> None:
    """Play a sound effect.

    Args:
        sound: The pygame.mixer.Sound object to play.
        loops: Number of extra times to repeat (0 = play once).
    """
    if sound:
        sound.play(loops=loops)
