"""
pipeline.py — Orchestration : relie détection, OCR et base de données.

Fonction principale : traiter(image) -> dict de résultat complet.
"""
from . import detection, ocr, database


def traiter(image):
    """Traite une image de véhicule et renvoie le résultat complet.

    Retourne un dict :
      {
        "plaque": str | None,
        "rect": (x,y,w,h) | None,
        "image_annotee": ndarray,
        "autorise": bool,
        "verdict": str,
        "ocr_ok": bool,
      }
    """
    rect, _ = detection.localiser_plaque(image)

    if rect is None:
        verdict = "AUCUNE PLAQUE"
        image_annotee = detection.annoter(image, None)
        database.enregistrer_passage(None, verdict)
        return {
            "plaque": None, "rect": None, "image_annotee": image_annotee,
            "autorise": False, "verdict": verdict, "ocr_ok": False,
        }

    roi = detection.extraire_roi(image, rect)
    plaque, ocr_ok = ocr.lire_plaque(roi)

    autorise = ocr_ok and database.est_autorisee(plaque)
    verdict = "AUTORISE" if autorise else "REFUSE"

    libelle = f"{plaque} - {verdict}" if plaque else verdict
    image_annotee = detection.annoter(image, rect, libelle, autorise)

    database.enregistrer_passage(plaque or None, verdict)

    return {
        "plaque": plaque, "rect": rect, "image_annotee": image_annotee,
        "autorise": autorise, "verdict": verdict, "ocr_ok": ocr_ok,
    }
