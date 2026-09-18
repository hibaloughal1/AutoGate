"""
database.py — Couche de persistance SQLite pour AutoGate.

Deux tables :
  - plaques_autorisees : liste blanche (plaque, propriétaire, type)
  - journal            : historique des passages (plaque lue, date, verdict)
"""
import sqlite3
from datetime import datetime

from . import config as cfg


def _connexion():
    cfg.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(cfg.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crée les tables si elles n'existent pas."""
    with _connexion() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS plaques_autorisees (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                plaque      TEXT UNIQUE NOT NULL,
                proprietaire TEXT,
                type_vehicule TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS journal (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                plaque    TEXT,
                date_heure TEXT NOT NULL,
                verdict   TEXT NOT NULL
            )
            """
        )


# --- Gestion de la liste blanche ---

def ajouter_plaque(plaque, proprietaire="", type_vehicule=""):
    """Ajoute une plaque autorisée. Retourne True si ajoutée, False si déjà présente."""
    try:
        with _connexion() as conn:
            conn.execute(
                "INSERT INTO plaques_autorisees (plaque, proprietaire, type_vehicule) VALUES (?, ?, ?)",
                (plaque.upper().strip(), proprietaire, type_vehicule),
            )
        return True
    except sqlite3.IntegrityError:
        return False


def supprimer_plaque(plaque):
    with _connexion() as conn:
        cur = conn.execute(
            "DELETE FROM plaques_autorisees WHERE plaque = ?", (plaque.upper().strip(),)
        )
        return cur.rowcount > 0


def lister_plaques():
    with _connexion() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM plaques_autorisees ORDER BY plaque"
        )]


def est_autorisee(plaque):
    with _connexion() as conn:
        cur = conn.execute(
            "SELECT 1 FROM plaques_autorisees WHERE plaque = ?", (plaque.upper().strip(),)
        )
        return cur.fetchone() is not None


# --- Journal ---

def enregistrer_passage(plaque, verdict):
    with _connexion() as conn:
        conn.execute(
            "INSERT INTO journal (plaque, date_heure, verdict) VALUES (?, ?, ?)",
            (plaque, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), verdict),
        )


def lister_journal(limite=100):
    with _connexion() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM journal ORDER BY id DESC LIMIT ?", (limite,)
        )]


def statistiques():
    """Retourne un dict {verdict: nombre} sur l'ensemble du journal."""
    with _connexion() as conn:
        rows = conn.execute(
            "SELECT verdict, COUNT(*) AS n FROM journal GROUP BY verdict"
        )
        return {r["verdict"]: r["n"] for r in rows}
