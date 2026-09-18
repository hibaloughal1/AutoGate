# Architecture d'AutoGate

## Vue d'ensemble

```
Image  ─►  detection.py  ─►  ocr.py  ─►  database.py  ─►  Verdict + Journal
           (TP6 : ROI)       (lecture)   (liste blanche)
                    \____________ pipeline.py ____________/
                                     │
                                  app.py (Streamlit)
```

## Modules

| Fichier          | Rôle |
|------------------|------|
| `src/config.py`  | Constantes et seuils (Canny, ratio plaque, OCR…). |
| `src/detection.py` | Pipeline OpenCV : gris → bilatéral → Canny → contours → quadrilatère au bon ratio → ROI. |
| `src/ocr.py`     | Pré-traitement de la ROI (agrandissement, Otsu, morphologie) + Tesseract + nettoyage texte. |
| `src/database.py`| SQLite : table `plaques_autorisees` (liste blanche) et `journal` (historique). |
| `src/pipeline.py`| Orchestration des trois étapes ci-dessus + décision. |
| `app.py`         | Interface Streamlit (3 onglets : Scanner / Plaques / Journal). |

## Flux de décision

1. `detection.localiser_plaque` renvoie le rectangle de la plaque (ou None).
2. `detection.extraire_roi` découpe la zone.
3. `ocr.lire_plaque` lit et nettoie le texte.
4. `database.est_autorisee` compare à la liste blanche.
5. Verdict `AUTORISE` / `REFUSE` / `AUCUNE PLAQUE`, puis enregistrement au journal.

## Choix techniques

- **Filtre bilatéral** plutôt qu'un flou gaussien simple : lisse le bruit tout en
  gardant les bords nets, ce qui aide Canny à isoler le contour de la plaque.
- **Filtrage par ratio largeur/hauteur** : élimine les faux rectangles (vitres,
  logos) que le seul critère « 4 côtés » laisserait passer.
- **Seuillage Otsu** avant l'OCR : choisit automatiquement le seuil, robuste aux
  variations de luminosité.
