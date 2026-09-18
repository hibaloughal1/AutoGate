# 🚗 AutoGate — Contrôle d'accès par reconnaissance de plaques

Projet de **Vision Industrielle** (ENSA Agadir) — système complet de reconnaissance
de plaques d'immatriculation (LPR – *License Plate Recognition*) sur **images fixes**,
avec base de données, journal des accès et interface graphique.

Le projet prolonge le **TP6** (détection + OCR de plaques) en ajoutant la couche
« système réel » : décision d'accès, base de données persistante, historique horodaté
et tableau de bord statistique.

---

## 🎯 Fonctionnement

1. L'utilisateur dépose une **photo de véhicule** dans l'interface.
2. Le système **détecte la plaque** (contours + filtrage par ratio d'aspect).
3. Il **isole la plaque** (ROI) et la **lit** par OCR (Tesseract).
4. Il **compare** le texte lu à la base de plaques autorisées.
5. Il affiche un **verdict** (✅ Accès autorisé / ⛔ Refusé) et **enregistre** l'événement.

---

## 🧩 Pipeline de vision (cœur du TP6)

| Étape | Traitement | Fonction OpenCV |
|------|-------------|-----------------|
| 1 | Niveaux de gris | `cv2.cvtColor` |
| 2 | Détection de contours | `cv2.Canny` |
| 3 | Recherche des contours | `cv2.findContours` |
| 4 | Tri par aire + filtrage par ratio largeur/hauteur | `cv2.contourArea`, `cv2.approxPolyDP` |
| 5 | Extraction de la ROI (plaque) | découpe du rectangle englobant |
| 6 | Pré-traitement OCR (seuillage, morphologie) | `cv2.threshold`, `cv2.morphologyEx` |
| 7 | Lecture des caractères | `pytesseract` (`--psm 7`) |
| 8 | Nettoyage du texte (regex format plaque) | — |

---

## 📁 Structure du projet

```
autogate/
├── app.py                  # Point d'entrée de l'interface (Streamlit)
├── requirements.txt        # Dépendances Python
├── .gitignore
├── README.md
├── src/
│   ├── __init__.py
│   ├── config.py           # Constantes et seuils (ratio, aire, seuil OCR…)
│   ├── detection.py        # Pipeline OpenCV : détection + extraction de la plaque
│   ├── ocr.py              # OCR Tesseract + nettoyage du texte
│   ├── pipeline.py         # Orchestration détection → OCR → décision
│   └── database.py         # Couche SQLite (plaques autorisées + journal)
├── data/
│   └── images/             # Images de test (photos de véhicules)
├── db/                     # Base de données SQLite générée à l'exécution
├── tests/
│   └── test_detection.py   # Tests unitaires du pipeline
└── docs/
    └── architecture.md     # Schéma et description de l'architecture
```

---

## 🛠️ Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/hibaloughal1/AutoGate.git
cd AutoGate

# 2. (Optionnel) Environnement virtuel
python -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\activate

# 3. Dépendances Python
pip install -r requirements.txt

# 4. Moteur Tesseract (requis par pytesseract)
#   Ubuntu/Debian : sudo apt install tesseract-ocr
#   macOS         : brew install tesseract
#   Windows       : installeur UB-Mannheim
```

---

## ▶️ Lancement

```bash
streamlit run app.py
```

L'interface s'ouvre dans le navigateur avec 3 onglets :

- **Scanner** — upload d'une image, affichage du résultat et du verdict.
- **Plaques autorisées** — ajout / suppression dans la base.
- **Journal & Statistiques** — historique des passages et graphique autorisés / refusés.

---

## 🗄️ Base de données (SQLite)

- `plaques_autorisees` : plaque, propriétaire, type de véhicule.
- `journal` : plaque lue, date/heure, verdict, image associée.

---

## 🧪 Tests

```bash
pytest tests/
```

---

## 🚀 Améliorations possibles

- Filtrage couleur de la plaque (selon le pays).
- Correction de perspective de la plaque (`cv2.warpPerspective`).
- Support vidéo / webcam en temps réel.
- Remplacer Tesseract par un OCR dédié (EasyOCR) pour les cas difficiles.

---

## 📚 Contexte

Projet réalisé dans le cadre des TP de Vision Industrielle — ENSA Agadir.
Basé sur les techniques des **TP5** (Hough / ROI), **TP6** (LPR) et **TP7** (analyse de zones).

## 📝 Licence

Projet académique — usage pédagogique.
