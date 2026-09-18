"""
ocr.py — Lecture des caractères de la plaque (étape OCR du TP6).

Le pré-traitement (agrandissement + seuillage Otsu + morphologie) améliore
nettement la précision de Tesseract sur de petites ROI.
"""
import cv2
import numpy as np

from . import config as cfg

try:
    import pytesseract
    _OCR_DISPONIBLE = True
except ImportError:
    _OCR_DISPONIBLE = False


def pretraiter_roi(roi):
    """Prépare la ROI de la plaque pour l'OCR.

    Étapes : agrandissement -> gris -> seuillage Otsu -> nettoyage morphologique.
    Retourne une image binaire (texte noir sur fond blanc).
    """
    # Agrandir aide Tesseract sur les petites plaques
    roi = cv2.resize(
        roi, None,
        fx=cfg.OCR_AGRANDISSEMENT, fy=cfg.OCR_AGRANDISSEMENT,
        interpolation=cv2.INTER_CUBIC,
    )
    gris = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if roi.ndim == 3 else roi
    gris = cv2.GaussianBlur(gris, (3, 3), 0)
    # Otsu choisit automatiquement le seuil ; INV pour avoir le texte en blanc
    _, binaire = cv2.threshold(
        gris, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )
    noyau = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    binaire = cv2.morphologyEx(binaire, cv2.MORPH_OPEN, noyau)
    # On repasse en texte noir sur fond blanc (préférence de Tesseract)
    return cv2.bitwise_not(binaire)


def nettoyer_texte(texte):
    """Garde uniquement les caractères valides d'une plaque, en majuscules."""
    texte = texte.upper().strip()
    return "".join(c for c in texte if c in cfg.CARACTERES_AUTORISES)


def lire_plaque(roi):
    """Lit le texte de la ROI et le nettoie.

    Retourne (texte, ok) où ok=False si l'OCR est indisponible ou la lecture trop courte.
    """
    if not _OCR_DISPONIBLE:
        return "", False
    image_ocr = pretraiter_roi(roi)
    brut = pytesseract.image_to_string(image_ocr, config=cfg.OCR_CONFIG)
    texte = nettoyer_texte(brut)
    ok = len(texte) >= cfg.LONGUEUR_MIN_PLAQUE
    return texte, ok
