"""
Configuration centralisée du projet AutoGate.
Tous les seuils et chemins sont regroupés ici pour faciliter les réglages.
"""
from pathlib import Path

# --- Chemins du projet ---
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "autogate.db"
IMAGES_DIR = BASE_DIR / "data" / "images"

# --- Détection des contours (Canny) ---
CANNY_SEUIL_BAS = 30
CANNY_SEUIL_HAUT = 200

# --- Filtrage des candidats "plaque" ---
NB_CONTOURS_GARDES = 15          # on ne garde que les N plus grands contours
APPROX_EPSILON = 0.018           # tolérance de approxPolyDP (x * périmètre)
RATIO_MIN = 2.0                  # ratio largeur/hauteur minimal d'une plaque
RATIO_MAX = 6.0                  # ratio largeur/hauteur maximal d'une plaque
AIRE_MIN = 500                   # aire minimale d'un candidat (en pixels)

# --- Pré-traitement OCR ---
OCR_AGRANDISSEMENT = 3           # facteur d'agrandissement de la ROI avant OCR
OCR_CONFIG = "--psm 7"           # PSM 7 = une seule ligne de texte

# --- Format de plaque (nettoyage du texte OCR) ---
# Caractères autorisés dans une plaque (lettres + chiffres + tiret)
CARACTERES_AUTORISES = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-"
LONGUEUR_MIN_PLAQUE = 4          # en dessous, on considère la lecture invalide

# --- Couleurs d'annotation (BGR) ---
COULEUR_OK = (0, 255, 0)         # vert : plaque détectée / accès autorisé
COULEUR_KO = (0, 0, 255)         # rouge : accès refusé
EPAISSEUR_TRAIT = 3
