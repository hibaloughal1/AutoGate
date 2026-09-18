"""
app.py — Interface Streamlit d'AutoGate.

Lancement :  streamlit run app.py

Trois onglets :
  1. Scanner             : upload d'une image -> détection, OCR, verdict
  2. Plaques autorisees  : gestion de la liste blanche
  3. Journal & Stats     : historique des passages + graphique
"""
import cv2
import numpy as np
import pandas as pd
import streamlit as st

from src import database, pipeline

st.set_page_config(page_title="AutoGate — LPR", page_icon="🚗", layout="wide")
database.init_db()

st.title("🚗 AutoGate — Contrôle d'accès par reconnaissance de plaques")

onglet_scan, onglet_plaques, onglet_journal = st.tabs(
    ["🔍 Scanner", "✅ Plaques autorisées", "📊 Journal & Statistiques"]
)

# ----------------------------------------------------------------------
# Onglet 1 : Scanner
# ----------------------------------------------------------------------
with onglet_scan:
    st.subheader("Déposer une photo de véhicule")
    fichier = st.file_uploader(
        "Image (jpg, png)", type=["jpg", "jpeg", "png"], key="upload"
    )

    if fichier is not None:
        # Décodage de l'image uploadée -> tableau OpenCV (BGR)
        octets = np.asarray(bytearray(fichier.read()), dtype=np.uint8)
        image = cv2.imdecode(octets, cv2.IMREAD_COLOR)

        resultat = pipeline.traiter(image)

        col1, col2 = st.columns(2)
        with col1:
            st.caption("Image d'origine")
            st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), use_container_width=True)
        with col2:
            st.caption("Détection")
            st.image(
                cv2.cvtColor(resultat["image_annotee"], cv2.COLOR_BGR2RGB),
                use_container_width=True,
            )

        # Verdict
        if resultat["verdict"] == "AUTORISE":
            st.success(f"✅ Accès autorisé — Plaque : **{resultat['plaque']}**")
        elif resultat["verdict"] == "REFUSE":
            lue = resultat["plaque"] or "(illisible)"
            st.error(f"⛔ Accès refusé — Plaque lue : **{lue}**")
        else:
            st.warning("⚠️ Aucune plaque détectée sur l'image.")

# ----------------------------------------------------------------------
# Onglet 2 : Plaques autorisées
# ----------------------------------------------------------------------
with onglet_plaques:
    st.subheader("Liste blanche")

    with st.expander("➕ Ajouter une plaque"):
        plaque = st.text_input("Plaque (ex : 12345-A-6)", key="add_plaque")
        proprio = st.text_input("Propriétaire", key="add_proprio")
        type_v = st.text_input("Type de véhicule", key="add_type")
        if st.button("Ajouter"):
            if plaque.strip():
                ok = database.ajouter_plaque(plaque, proprio, type_v)
                st.success("Plaque ajoutée.") if ok else st.info("Cette plaque existe déjà.")
            else:
                st.warning("Saisis au moins une plaque.")

    plaques = database.lister_plaques()
    if plaques:
        st.dataframe(pd.DataFrame(plaques), use_container_width=True, hide_index=True)
        a_supprimer = st.selectbox(
            "Supprimer une plaque", [p["plaque"] for p in plaques], key="del_select"
        )
        if st.button("Supprimer"):
            database.supprimer_plaque(a_supprimer)
            st.rerun()
    else:
        st.info("Aucune plaque autorisée pour le moment.")

# ----------------------------------------------------------------------
# Onglet 3 : Journal & Statistiques
# ----------------------------------------------------------------------
with onglet_journal:
    st.subheader("Historique des passages")

    stats = database.statistiques()
    if stats:
        c1, c2, c3 = st.columns(3)
        c1.metric("✅ Autorisés", stats.get("AUTORISE", 0))
        c2.metric("⛔ Refusés", stats.get("REFUSE", 0))
        c3.metric("⚠️ Sans plaque", stats.get("AUCUNE PLAQUE", 0))
        st.bar_chart(pd.DataFrame(
            {"nombre": list(stats.values())}, index=list(stats.keys())
        ))

    journal = database.lister_journal()
    if journal:
        st.dataframe(pd.DataFrame(journal), use_container_width=True, hide_index=True)
    else:
        st.info("Le journal est vide.")
