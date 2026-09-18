"""
detection.py — Localisation de la plaque dans une image (cœur du TP6).

Pipeline :
  1. Niveaux de gris
  2. Réduction du bruit (filtre bilatéral : lisse en gardant les bords)
  3. Détection de contours (Canny)
  4. Recherche des contours et tri par aire
  5. Recherche d'un quadrilatère au bon ratio largeur/hauteur (la plaque)
  6. Extraction de la ROI + image annotée
"""
import cv2
import numpy as np

from . import config as cfg


def pretraiter(image):
    """Convertit en gris, réduit le bruit et extrait les contours (Canny)."""
    gris = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Le filtre bilatéral lisse le bruit tout en préservant les bords nets
    gris = cv2.bilateralFilter(gris, 11, 17, 17)
    contours_img = cv2.Canny(gris, cfg.CANNY_SEUIL_BAS, cfg.CANNY_SEUIL_HAUT)
    return gris, contours_img


def _est_une_plaque(approx):
    """Teste si un contour approximé ressemble à une plaque.

    Critères : 4 sommets (rectangle) + ratio largeur/hauteur cohérent + aire suffisante.
    Retourne le rectangle englobant (x, y, w, h) si valide, sinon None.
    """
    if len(approx) != 4:
        return None
    x, y, w, h = cv2.boundingRect(approx)
    if h == 0:
        return None
    ratio = w / float(h)
    aire = w * h
    if cfg.RATIO_MIN <= ratio <= cfg.RATIO_MAX and aire >= cfg.AIRE_MIN:
        return (x, y, w, h)
    return None


def localiser_plaque(image):
    """Cherche la plaque dans l'image.

    Retourne un tuple (rect, contour) où :
      - rect    = (x, y, w, h) du rectangle englobant, ou None si rien trouvé
      - contour = le contour à 4 points (pour l'annotation), ou None
    """
    _, contours_img = pretraiter(image)
    contours, _ = cv2.findContours(
        contours_img.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    # On garde les plus grands contours (la plaque est généralement bien visible)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[: cfg.NB_CONTOURS_GARDES]

    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, cfg.APPROX_EPSILON * peri, True)
        rect = _est_une_plaque(approx)
        if rect is not None:
            return rect, approx
    return None, None


def extraire_roi(image, rect):
    """Découpe la zone de la plaque (ROI) à partir du rectangle englobant."""
    x, y, w, h = rect
    return image[y : y + h, x : x + w]


def annoter(image, rect, texte=None, autorise=None):
    """Dessine le rectangle de la plaque et un libellé sur une copie de l'image.

    autorise : True (vert) / False (rouge) / None (vert neutre).
    """
    sortie = image.copy()
    if rect is None:
        return sortie
    x, y, w, h = rect
    couleur = cfg.COULEUR_OK if autorise in (True, None) else cfg.COULEUR_KO
    cv2.rectangle(sortie, (x, y), (x + w, y + h), couleur, cfg.EPAISSEUR_TRAIT)
    if texte:
        cv2.putText(
            sortie, texte, (x, max(0, y - 10)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.9, couleur, 2, cv2.LINE_AA,
        )
    return sortie
