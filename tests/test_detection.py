"""
Tests unitaires basiques du pipeline AutoGate.
Lancement :  pytest tests/
"""
import numpy as np
import cv2

from src import detection, ocr


def _image_avec_rectangle():
    """Crée une image blanche avec un rectangle noir au ratio d'une plaque."""
    img = np.full((300, 600, 3), 255, dtype=np.uint8)
    # Rectangle 220x60 -> ratio ~3.6, dans la plage plaque
    cv2.rectangle(img, (150, 120), (370, 180), (0, 0, 0), 3)
    return img


def test_localiser_plaque_trouve_un_rectangle():
    img = _image_avec_rectangle()
    rect, contour = detection.localiser_plaque(img)
    assert rect is not None
    x, y, w, h = rect
    ratio = w / h
    assert 2.0 <= ratio <= 6.0


def test_localiser_plaque_image_vide():
    img = np.full((300, 600, 3), 255, dtype=np.uint8)
    rect, _ = detection.localiser_plaque(img)
    assert rect is None


def test_nettoyer_texte():
    assert ocr.nettoyer_texte(" 12345-a-6 \n") == "12345-A-6"
    assert ocr.nettoyer_texte("ab#12!") == "AB12"


def test_extraire_roi_dimensions():
    img = _image_avec_rectangle()
    roi = detection.extraire_roi(img, (150, 120, 220, 60))
    assert roi.shape[0] == 60 and roi.shape[1] == 220
