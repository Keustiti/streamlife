# -*- coding: utf-8 -*-
"""
🧬 MA VIE — Simulateur de vie façon BitLife (Streamlit)

Lancer :   pip install streamlit
           streamlit run ma_vie.py

Fonctionnalités : création de personnage (coupe, visage, peau, yeux...), 4 univers
(réel, manga, fantasy, cyberpunk) avec leurs villes, études, jobs étudiants, métiers
classiques et rares (acteur, rappeur, streameur, ninja, bandit...), amour, enfants,
crime & prison, événements aléatoires à choix, succès, sauvegardes (disque + export JSON).
"""
import json
import random
import re
import uuid
from datetime import datetime
from pathlib import Path

import streamlit as st

SAVE_DIR = Path("saves")
ACTIONS_PAR_AN = 4

# ======================================================================
#  DONNÉES : UNIVERS, VILLES, MÉTIERS
# ======================================================================
UNIVERS = {
    "real": {
        "nom": "🌍 Monde réel", "devise": "€", "couleur": "#3b82f6", "force": "Force",
        "desc": "Une vie moderne : études, boulot, followers et factures.",
        "villes": {
            "Paris": {"cout": 1.35, "crime": 0.35, "desc": "Capitale, opportunités… et loyers."},
            "Strasbourg": {"cout": 1.0, "crime": 0.2, "desc": "Ville européenne, calme et étudiante."},
            "Marseille": {"cout": 0.95, "crime": 0.45, "desc": "Soleil, mer et tempérament."},
            "New York": {"cout": 1.6, "crime": 0.4, "desc": "La ville qui ne dort jamais."},
            "Tokyo": {"cout": 1.3, "crime": 0.1, "desc": "Néons, sushis et technologie."},
            "Los Angeles": {"cout": 1.5, "crime": 0.4, "desc": "Hollywood, plages et rêves de gloire."},
            "Dubaï": {"cout": 1.4, "crime": 0.1, "desc": "Gratte-ciel et luxe."},
            "Dakar": {"cout": 0.6, "crime": 0.25, "desc": "Énergie, musique et vie de quartier."},
        },
    },
    "manga": {
        "nom": "🍥 Monde manga", "devise": "ryō", "couleur": "#f97316", "force": "Chakra / Force",
        "desc": "Villages ninjas, pirates, héros et démons. Tout peut arriver.",
        "villes": {
            "Village de la Feuille 🍃": {"cout": 0.9, "crime": 0.2, "desc": "Village caché, berceau des ninjas."},
            "Tokyo Shōnen": {"cout": 1.2, "crime": 0.3, "desc": "Mégalopole pleine de héros pro."},
            "Port de la Grand Line 🏴‍☠️": {"cout": 1.0, "crime": 0.5, "desc": "Rendez-vous des pirates."},
            "Académie des Héros": {"cout": 1.1, "crime": 0.15, "desc": "Là où se forment les futurs numéro 1."},
        },
    },
    "fantasy": {
        "nom": "🐉 Fantasy médiévale", "devise": "pièces d'or", "couleur": "#8b5cf6", "force": "Force / Magie",
        "desc": "Royaumes, dragons, magie et auberges douteuses.",
        "villes": {
            "Royaume d'Aldoria 👑": {"cout": 1.1, "crime": 0.25, "desc": "Capitale royale et chevaliers."},
            "Cité des Elfes": {"cout": 1.3, "crime": 0.1, "desc": "Forêts enchantées et tours de mages."},
            "Forteresse des Nains ⛏️": {"cout": 0.9, "crime": 0.2, "desc": "Forges, bière et trésors."},
            "Port-Corsaire": {"cout": 0.8, "crime": 0.55, "desc": "Contrebande et aventuriers."},
        },
    },
    "cyber": {
        "nom": "🤖 Cyberpunk 2077", "devise": "crédits", "couleur": "#06b6d4", "force": "Force / Cyber",
        "desc": "Mégacorpos, implants, hackers et néons sous la pluie.",
        "villes": {
            "Néo-Tokyo": {"cout": 1.5, "crime": 0.4, "desc": "Mégalopole high-tech."},
            "Night District": {"cout": 1.1, "crime": 0.6, "desc": "Clubs, gangs et mercenaires."},
            "Station Helios 🛰️": {"cout": 1.8, "crime": 0.15, "desc": "Orbite des ultra-riches."},
            "Les Bas-Fonds": {"cout": 0.6, "crime": 0.7, "desc": "Survie et marché noir."},
        },
    },
}

LABELS = {"sante": "Santé", "bonheur": "Bonheur", "intelligence": "Intelligence", "apparence": "Apparence",
          "force": "Force", "karma": "Karma", "celebrite": "Célébrité"}
ICONES = {"sante": "❤️", "bonheur": "😊", "intelligence": "🧠", "apparence": "✨",
          "force": "💪", "karma": "☯️", "celebrite": "⭐"}

EDU_NOMS = ["Aucun", "Primaire", "Collège", "Lycée (non terminé)", "Baccalauréat / fin d'études",
            "Licence", "Master", "Doctorat"]
DOMAINES = ["Médecine", "Droit", "Informatique", "Sciences", "Commerce", "Lettres", "Arts & Spectacle"]
NIVEAUX_UNIV = {4: ("Licence", 3, 5), 5: ("Master", 2, 6), 6: ("Doctorat", 3, 7)}  # edu -> (nom, durée, edu obtenue)

PRENOMS = ["Léa", "Hugo", "Emma", "Lucas", "Chloé", "Nathan", "Inès", "Yanis", "Manon", "Karim", "Sakura",
           "Ren", "Aiko", "Kenji", "Mira", "Elias", "Zoé", "Noah", "Amara", "Tariq", "Jade", "Milo", "Yuna", "Sacha"]

DEF_GRADES = ["Débutant", "Confirmé", "Senior", "Responsable"]
DEF_MULT = [1, 1.5, 2.4, 4]
JOBS = {}


def add(key, nom, emoji, age, edu, sal, cat="Métier", univ="all", chance=0.8, atouts=None, domaine=None,
        grades=None, mult=None, risque=0.0, crime=False, fame=0, variable=False, statmin=None):
    JOBS[key] = dict(nom=nom, emoji=emoji, age=age, edu=edu, sal=sal, cat=cat, univ=univ, chance=chance,
                     atouts=atouts or [], domaine=domaine, grades=grades or DEF_GRADES, mult=mult or DEF_MULT,
                     risque=risque, crime=crime, fame=fame, variable=variable, statmin=statmin)


R, M, F, C = ["real"], ["manga"], ["fantasy"], ["cyber"]
JE = "Job étudiant"
# --- Jobs étudiants
add("livreur_pizza", "Livreur de pizzas", "🍕", 14, 0, 4500, JE, R)
add("babysitter", "Baby-sitter", "👶", 14, 0, 2500, JE, R)
add("caissier", "Caissier·ère", "🛒", 16, 1, 6500, JE, R)
add("serveur", "Serveur·se", "🍽️", 16, 1, 7000, JE, ["real", "cyber"])
add("tuteur", "Tuteur·rice (cours particuliers)", "📚", 17, 3, 5500, JE, R, statmin=("intelligence", 60))
add("dango", "Vendeur de dangos", "🍡", 10, 0, 2500, JE, M)
add("coursier_parchemins", "Coursier de parchemins", "📜", 11, 0, 3000, JE, M)
add("palefrenier", "Palefrenier", "🐴", 12, 0, 3000, JE, F)
add("aide_auberge", "Aide d'auberge", "🍺", 14, 0, 3500, JE, F)
add("livreur_drone", "Livreur de drones", "🚁", 14, 0, 5000, JE, C)
add("cuistot_ramen", "Cuistot de bar à ramen", "🍜", 15, 0, 5200, JE, C)
# --- Métiers classiques
add("ouvrier_btp", "Ouvrier du BTP", "🧱", 16, 2, 26000, univ=R, risque=0.03)
add("employe", "Employé de bureau", "🏢", 18, 4, 30000, univ=["real", "cyber"])
add("plombier", "Plombier", "🔧", 16, 2, 33000, univ=R)
add("agriculteur", "Agriculteur / Fermier", "🚜", 16, 1, 24000)
add("chef", "Chef cuisinier", "👨‍🍳", 18, 3, 38000, atouts=["intelligence"], chance=0.7)
add("policier", "Policier", "👮", 20, 4, 34000, univ=R, statmin=("force", 45), risque=0.04)
add("pompier", "Pompier", "🚒", 20, 4, 31000, univ=R, statmin=("force", 55), risque=0.05)
add("infirmier", "Infirmier·ère", "🩺", 21, 5, 36000, univ=["real", "cyber"], domaine=["Médecine"])
add("medecin", "Médecin", "🧑‍⚕️", 25, 6, 85000, univ=R, domaine=["Médecine"])
add("ripperdoc", "Ripperdoc (chirurgien cyber)", "🦾", 22, 5, 70000, univ=C, domaine=["Médecine"])
add("avocat", "Avocat·e", "⚖️", 25, 6, 72000, univ=R, domaine=["Droit"])
add("dev", "Développeur·se", "💻", 21, 5, 52000, univ=["real", "cyber"], domaine=["Informatique"])
add("enseignant", "Enseignant·e", "🍎", 22, 5, 36000, univ=["real", "cyber"], domaine=["Lettres", "Sciences"])
add("sensei", "Sensei de l'académie", "📖", 20, 4, 30000, univ=M, atouts=["intelligence"])
add("ingenieur", "Ingénieur·e", "🛠️", 23, 6, 56000, univ=["real", "cyber"], domaine=["Sciences", "Informatique"])
add("comptable", "Comptable", "📊", 22, 5, 40000, univ=R, domaine=["Commerce"])
add("pilote", "Pilote de ligne", "✈️", 24, 5, 90000, univ=R, domaine=["Sciences"], statmin=("intelligence", 65))
add("entrepreneur", "Entrepreneur·se", "🚀", 18, 0, 15000, chance=0.5, atouts=["intelligence"],
    grades=["Auto-entrepreneur", "PME", "Licorne", "Empire"], mult=[1, 2.5, 8, 30], variable=True)
add("pilote_drone", "Pilote de drones de combat", "🎯", 16, 2, 28000, univ=C, statmin=("intelligence", 50), risque=0.04)
add("forgeron", "Forgeron", "🔨", 16, 1, 23000, univ=F + M, statmin=("force", 45))
add("alchimiste", "Alchimiste", "⚗️", 18, 2, 26000, univ=F, statmin=("intelligence", 55))
# --- Métiers rares ✨
RA = "Métier rare"
add("acteur", "Acteur·rice", "🎭", 16, 0, 9000, RA, chance=0.06, atouts=["apparence", "intelligence"],
    grades=["Figurant", "Second rôle", "Tête d'affiche", "Légende d'Hollywood"], mult=[1, 3, 15, 100], fame=3, variable=True)
add("rappeur", "Rappeur·se", "🎤", 14, 0, 6000, RA, ["real", "cyber", "manga"], chance=0.08, atouts=["apparence", "intelligence"],
    grades=["Rappeur de rue", "Mixtape virale", "Album platine", "Légende du hip-hop"], mult=[1, 4, 20, 120], fame=4, variable=True)
add("streameur", "Streameur·se", "🎮", 14, 0, 5000, RA, ["real", "cyber", "manga"], chance=0.2, atouts=["apparence", "bonheur"],
    grades=["Petit stream", "Partenaire Twitch", "Star du live", "Roi du streaming"], mult=[1, 3, 15, 80], fame=3, variable=True)
add("influenceur", "Influenceur·se", "📱", 14, 0, 4000, RA, ["real", "cyber"], chance=0.25, atouts=["apparence"],
    grades=["Micro-influenceur", "Créateur reconnu", "Star des réseaux", "Icône mondiale"], mult=[1, 3, 12, 60], fame=3, variable=True)
add("mannequin", "Mannequin", "📸", 16, 0, 12000, RA, ["real", "cyber"], chance=0.15, atouts=["apparence"],
    statmin=("apparence", 70), grades=["Débutant·e", "Fashion Week", "Égérie", "Top model mondial"], mult=[1, 3, 12, 50], fame=3, variable=True)
add("footballeur", "Footballeur pro", "⚽", 16, 0, 20000, RA, R, chance=0.06, atouts=["force", "sante"], statmin=("force", 65),
    grades=["Centre de formation", "Pro D2", "Ligue 1", "Ballon d'Or"], mult=[1, 6, 30, 150], fame=3, risque=0.06, variable=True)
add("mangaka", "Mangaka", "✏️", 16, 0, 14000, RA, ["real", "manga"], chance=0.1, atouts=["intelligence", "bonheur"],
    grades=["Assistant", "Série publiée", "Best-seller", "Légende du manga"], mult=[1, 3, 12, 60], fame=2, variable=True)
add("idole", "Idole de J-pop", "🌟", 14, 0, 10000, RA, ["manga", "real"], chance=0.1, atouts=["apparence", "bonheur"],
    statmin=("apparence", 65), grades=["Trainee", "Groupe local", "Centre du groupe", "Idole nationale"], mult=[1, 3, 15, 70], fame=4, variable=True)
add("astronaute", "Astronaute", "🧑‍🚀", 28, 7, 95000, RA, R, chance=0.08, atouts=["intelligence", "sante"], domaine=["Sciences"],
    grades=["Candidat", "Astronaute", "Commandant", "Légende de l'espace"], mult=[1, 1.5, 2.5, 4], fame=3, risque=0.03)
add("hacker", "Hacker", "🕶️", 16, 0, 25000, RA, ["real", "cyber"], chance=0.12, atouts=["intelligence"], statmin=("intelligence", 70),
    grades=["Script kiddie", "Black hat", "Cyber-mercenaire", "Fantôme du Net"], mult=[1, 2, 6, 20], risque=0.08, crime=True, variable=True)
add("bandit", "Bandit", "🕵️", 16, 0, 14000, RA, chance=0.45, atouts=["force", "intelligence"],
    grades=["Petite frappe", "Braqueur", "Lieutenant", "Parrain"], mult=[1, 2, 5, 15], risque=0.12, crime=True, variable=True)
add("ninja", "Ninja", "🥷", 12, 0, 20000, RA, M, chance=0.35, atouts=["force", "intelligence"], statmin=("force", 50),
    grades=["Genin", "Chūnin", "Jōnin", "Kage"], mult=[1, 2, 4, 12], risque=0.08, fame=2)
add("chasseur_demons", "Chasseur de démons", "🗡️", 14, 0, 22000, RA, M, chance=0.25, atouts=["force"], statmin=("force", 55),
    grades=["Recrue", "Épéiste", "Pourfendeur d'élite", "Pilier"], mult=[1, 2, 4, 10], risque=0.1, fame=2)
add("pirate", "Pirate", "🏴‍☠️", 14, 0, 12000, RA, M, chance=0.4, atouts=["force", "intelligence"],
    grades=["Mousse", "Second", "Capitaine", "Roi des pirates"], mult=[1, 2, 6, 40], risque=0.1, crime=True, fame=2, variable=True)
add("heros_pro", "Héros professionnel", "🦸", 15, 0, 30000, RA, M, chance=0.2, atouts=["force", "karma"], statmin=("force", 60),
    grades=["Stagiaire", "Rang C", "Rang S", "Numéro 1"], mult=[1, 2, 6, 20], risque=0.07, fame=4)
add("chevalier", "Chevalier", "🛡️", 16, 0, 22000, RA, F, chance=0.4, atouts=["force", "karma"], statmin=("force", 50),
    grades=["Écuyer", "Chevalier", "Capitaine", "Paladin royal"], mult=[1, 2, 4, 10], risque=0.06, fame=2)
add("mage", "Mage", "🔮", 16, 0, 26000, RA, F, chance=0.3, atouts=["intelligence"], statmin=("intelligence", 65),
    grades=["Apprenti", "Mage", "Archimage", "Grand sorcier"], mult=[1, 2, 5, 15], risque=0.03, fame=2)
add("aventurier", "Aventurier", "⚔️", 14, 0, 12000, RA, F, chance=0.6, atouts=["force", "sante"],
    grades=["Rang bronze", "Rang argent", "Rang or", "Légende"], mult=[1, 2.5, 7, 25], risque=0.1, fame=2, variable=True)
add("barde", "Barde", "🪕", 14, 0, 8000, RA, F, chance=0.2, atouts=["apparence", "bonheur"],
    grades=["Troubadour", "Barde de cour", "Barde royal", "Légende vivante"], mult=[1, 3, 12, 50], fame=3, variable=True)
add("chasseur_dragons", "Chasseur de dragons", "🐉", 18, 0, 30000, RA, F, chance=0.1, atouts=["force"], statmin=("force", 70),
    grades=["Pisteur", "Tueur de wyvernes", "Dragonnier", "Fléau des dragons"], mult=[1, 2, 5, 12], risque=0.15, fame=4)
add("mercenaire", "Mercenaire", "🔫", 18, 0, 30000, RA, C, chance=0.4, atouts=["force", "intelligence"],
    grades=["Recrue", "Mercenaire", "Vétéran", "Légende de la nuit"], mult=[1, 2, 5, 15], risque=0.1, crime=True, variable=True)
add("netrunner", "Netrunner", "🧠", 16, 0, 38000, RA, C, chance=0.2, atouts=["intelligence"], statmin=("intelligence", 65),
    grades=["Pirate de quartier", "Netrunner", "Maître du réseau", "Dieu du Net"], mult=[1, 2, 5, 14], risque=0.06)
# --- Super-héros et justiciers originaux (inspirés du genre, sans reprendre les héros connus)
add("justicier_armure", "Justicier·ère en armure", "🦾", 18, 2, 52000, RA, ["real", "cyber"], chance=0.16, atouts=["intelligence", "force"], statmin=("intelligence", 60), grades=["Prototype secret", "Protecteur urbain", "Sentinelle nationale", "Légende blindée"], mult=[1, 2, 5, 14], risque=0.08, fame=3)
add("tisseur_urbain", "Héros·ïne tisseur·se urbain·e", "🕸️", 16, 0, 36000, RA, ["real", "manga", "cyber"], chance=0.22, atouts=["force", "karma"], statmin=("force", 55), grades=["Vigilant de quartier", "Sauveur des toits", "Protecteur de la ville", "Mythe urbain"], mult=[1, 2, 4, 11], risque=0.09, fame=3)
add("heros_energie", "Héros·ïne à énergie cosmique", "☄️", 18, 0, 60000, RA, ["manga", "cyber"], chance=0.12, atouts=["force", "sante"], statmin=("force", 75), grades=["Éveillé·e", "Gardien·ne solaire", "Défenseur·se planétaire", "Légende cosmique"], mult=[1, 2, 6, 18], risque=0.12, fame=5)
add("metamorphe", "Métamorphe / change-forme", "🦎", 15, 0, 30000, RA, ["real", "manga", "cyber"], chance=0.2, atouts=["apparence", "intelligence"], grades=["Pouvoir instable", "Agent secret", "Héros reconnu", "Maître des formes"], mult=[1, 2, 4, 12], risque=0.06, fame=3)
add("telepathe", "Télépathe protecteur·rice", "🧠", 16, 0, 34000, RA, ["real", "manga"], chance=0.18, atouts=["intelligence", "karma"], statmin=("intelligence", 65), grades=["Esprit éveillé", "Médiateur mental", "Bouclier psychique", "Gardien des consciences"], mult=[1, 2, 5, 13], risque=0.05, fame=3)
add("chasseur_anomalies", "Chasseur·se d'anomalies", "🌀", 18, 0, 42000, RA, ["real", "cyber", "fantasy"], chance=0.2, atouts=["force", "intelligence"], grades=["Recrue", "Intervenant·e", "Chef·fe d'unité", "Légende du paranormal"], mult=[1, 2, 5, 12], risque=0.1, fame=3)
add("inventeur_gadgets", "Inventeur·rice de gadgets héroïques", "🛠️", 18, 4, 48000, RA, ["real", "cyber", "manga"], chance=0.2, atouts=["intelligence"], statmin=("intelligence", 65), grades=["Bricoleur·se", "Génie indépendant", "Fournisseur des héros", "Architecte de légendes"], mult=[1, 2, 5, 15], risque=0.04, fame=2)
add("gardien_dimension", "Gardien·ne des dimensions", "🪄", 20, 0, 50000, RA, ["manga", "fantasy", "cyber"], chance=0.12, atouts=["intelligence", "karma"], statmin=("intelligence", 70), grades=["Apprenti·e du portail", "Sentinelle dimensionnelle", "Maître des failles", "Gardien·ne éternel·le"], mult=[1, 2, 6, 18], risque=0.1, fame=4)
add("heroine_soins", "Héros·ïne aux pouvoirs régénérants", "💚", 16, 0, 32000, RA, ["real", "manga", "fantasy"], chance=0.22, atouts=["sante", "karma"], grades=["Secouriste masqué·e", "Guérisseur·se de terrain", "Sauveur·se national·e", "Phare d'espoir"], mult=[1, 2, 4, 10], risque=0.04, fame=3)


# ======================================================================
#  OUTILS
# ======================================================================
class Refus(Exception):
    """Action impossible : on ne consomme pas de temps libre."""


def clamp(v, lo=0, hi=100):
    return max(lo, min(hi, int(round(v))))


def devise(g):
    return UNIVERS[g["univers"]]["devise"]


def fm(g, n):
    return f"{int(n):,}".replace(",", " ") + " " + devise(g)


def log(g, txt):
    g["journal"].append([g["age"], txt])


def chg(g, **kw):
    for k, v in kw.items():
        if k == "argent":
            g["argent"] += int(v)
        elif k == "notes":
            g["notes"] = clamp(g["notes"] + v)
        else:
            g["stats"][k] = clamp(g["stats"][k] + v)


def res(g, texte, **kw):
    chg(g, **kw)
    return texte


def payer(g, montant):
    if g["argent"] < montant:
        raise Refus(f"💸 Il te faut {fm(g, montant)} pour ça.")
    g["argent"] -= int(montant)


def ville_info(g):
    return UNIVERS[g["univers"]]["villes"][g["ville"]]


def titre_metier(g):
    if not g["metier"]:
        return "Retraité·e" if g["retraite"] else ("Étudiant·e" if (g["en_ecole"] or g["etudes_en_cours"]) else "Sans emploi")
    j = JOBS[g["metier"]]
    return f"{j['emoji']} {j['nom']} — {j['grades'][g['grade']]}"


# ======================================================================
#  AVATAR (SVG généré)
# ======================================================================
SKINS = {"Clair": "#f6d5b8", "Beige": "#e8b98f", "Mat": "#c68a5c", "Brun": "#8d5a3b", "Foncé": "#5a3825",
         "Bleuté (manga)": "#b8d8f0"}
HAIR_COLORS = {"Noir": "#1b1b1b", "Brun": "#5a3825", "Blond": "#e6c86e", "Roux": "#c2531b", "Blanc": "#ececec",
               "Bleu": "#2f6fed", "Rose": "#f06fb0", "Vert": "#2fbf71"}
COUPES = ["Court", "Long", "Afro", "Crête", "Queue de cheval", "Pointes (manga)", "Carré", "Chauve"]
YEUX = ["Ronds", "Souriants", "Manga", "Lunettes", "Fatigués"]
BOUCHES = ["Sourire", "Neutre", "Grand sourire", "Moue"]


def avatar_svg(av, age=25, univ="real", badge="", taille=190):
    skin = SKINS.get(av["peau"], "#e8b98f")
    hc = HAIR_COLORS.get(av["couleur"], "#1b1b1b")
    if age >= 60:
        hc = "#d4d4d4"
    body = UNIVERS[univ]["couleur"]
    top = f'<path d="M42 98 Q38 36 100 34 Q162 36 158 98 Q135 62 100 64 Q65 62 42 98Z" fill="{hc}"/>'
    back = front = ""
    c = av["coupe"]
    if c == "Court":
        front = top
    elif c == "Long":
        back = f'<path d="M36 100 Q32 30 100 28 Q168 30 164 100 L168 205 L32 205Z" fill="{hc}"/>'
        front = top
    elif c == "Afro":
        back = f'<circle cx="100" cy="78" r="72" fill="{hc}"/>'
        front = top
    elif c == "Carré":
        back = f'<path d="M36 100 Q32 30 100 28 Q168 30 164 100 L162 150 L38 150Z" fill="{hc}"/>'
        front = top
    elif c == "Crête":
        front = f'<polygon points="84,52 88,8 100,26 112,4 116,52" fill="{hc}"/>'
    elif c == "Queue de cheval":
        back = f'<ellipse cx="166" cy="78" rx="13" ry="30" fill="{hc}"/>'
        front = top
    elif c == "Pointes (manga)":
        front = (f'<polygon points="42,98 36,44 62,66 66,16 92,56 108,10 124,56 148,26 158,98 130,64 100,68 70,64" '
                 f'fill="{hc}"/>')
    ink = "#222"
    y = av["yeux"]
    if y == "Ronds":
        eyes = "".join(f'<circle cx="{x}" cy="104" r="8" fill="#fff" stroke="#333"/><circle cx="{x}" cy="104" r="4" fill="{ink}"/>'
                       for x in (78, 122))
    elif y == "Souriants":
        eyes = "".join(f'<path d="M{x-9} 106 Q{x} 95 {x+9} 106" fill="none" stroke="{ink}" stroke-width="3" stroke-linecap="round"/>'
                       for x in (78, 122))
    elif y == "Manga":
        eyes = "".join(f'<ellipse cx="{x}" cy="104" rx="10" ry="13" fill="#fff" stroke="#333"/>'
                       f'<ellipse cx="{x}" cy="106" rx="7" ry="10" fill="{hc if age < 60 else "#4a6"}"/>'
                       f'<circle cx="{x-2}" cy="101" r="3" fill="#fff"/>' for x in (78, 122))
    elif y == "Lunettes":
        eyes = ("".join(f'<circle cx="{x}" cy="104" r="12" fill="#fff6" stroke="#222" stroke-width="3"/>'
                        f'<circle cx="{x}" cy="104" r="3.5" fill="{ink}"/>' for x in (78, 122))
                + '<line x1="90" y1="104" x2="110" y2="104" stroke="#222" stroke-width="3"/>')
    else:  # Fatigués
        eyes = "".join(f'<circle cx="{x}" cy="106" r="3.5" fill="{ink}"/><path d="M{x-9} 101 L{x+9} 101" stroke="{ink}" stroke-width="3"/>'
                       f'<path d="M{x-8} 114 Q{x} 118 {x+8} 114" fill="none" stroke="#0004" stroke-width="2"/>' for x in (78, 122))
    brows = f'<path d="M66 90 L90 88 M110 88 L134 90" stroke="{hc if hc != "#ececec" else "#999"}" stroke-width="4" stroke-linecap="round"/>'
    nose = '<path d="M100 108 Q94 124 102 125" fill="none" stroke="#0005" stroke-width="2"/>'
    b = av["bouche"]
    if b == "Sourire":
        mouth = '<path d="M82 136 Q100 152 118 136" fill="none" stroke="#7a2a2a" stroke-width="3.5" stroke-linecap="round"/>'
    elif b == "Neutre":
        mouth = '<line x1="85" y1="141" x2="115" y2="141" stroke="#7a2a2a" stroke-width="3.5" stroke-linecap="round"/>'
    elif b == "Grand sourire":
        mouth = '<path d="M80 132 Q100 162 120 132Z" fill="#fff" stroke="#7a2a2a" stroke-width="3"/>'
    else:
        mouth = '<path d="M86 146 Q100 132 114 146" fill="none" stroke="#7a2a2a" stroke-width="3.5" stroke-linecap="round"/>'
    wrinkles = ('<path d="M70 120 Q76 124 82 120 M118 120 Q124 124 130 120" fill="none" stroke="#0003" stroke-width="2"/>'
                if age >= 55 else "")
    s = 0.72 if age < 4 else (0.8 if age < 8 else (0.9 if age < 14 else 1.0))
    badge_svg = f'<text x="150" y="214" font-size="34">{badge}</text>' if badge else ""
    svg = (f'<svg viewBox="0 0 200 225" width="{taille}" xmlns="http://www.w3.org/2000/svg">'
           f'<g transform="translate(100 225) scale({s}) translate(-100 -225)">'
           f'{back}<circle cx="43" cy="108" r="10" fill="{skin}"/><circle cx="157" cy="108" r="10" fill="{skin}"/>'
           f'<path d="M20 225 Q30 168 100 165 Q170 168 180 225Z" fill="{body}"/>'
           f'<rect x="82" y="148" width="36" height="30" fill="{skin}"/>'
           f'<circle cx="100" cy="105" r="58" fill="{skin}"/>{wrinkles}{brows}{eyes}{nose}{mouth}{front}</g>{badge_svg}</svg>')
    return f'<div style="text-align:center">{svg}</div>'


# ======================================================================
#  CRÉATION / ÉTAT DU JEU
# ======================================================================
def defauts():
    return {"id": uuid.uuid4().hex[:8], "nom": "Alex", "genre": "Non-binaire", "univers": "real", "ville": "Paris",
            "avatar": {"coupe": "Court", "couleur": "Noir", "peau": "Beige", "yeux": "Ronds", "bouche": "Sourire"},
            "age": 0, "annee_naissance": datetime.now().year, "argent": 0, "edu": 0, "notes": 50, "domaine": "",
            "en_ecole": False, "etudes_en_cours": None, "metier": None, "grade": 0, "annees_metier": 0,
            "dernier_salaire": 0, "retraite": 0, "partenaire": None, "enfants": [], "casier": 0, "prison": 0,
            "chez_parents": True, "fam": 1, "famille": "classe moyenne", "trait": "", "actions": ACTIONS_PAR_AN,
            "stats": {"sante": 70, "bonheur": 70, "intelligence": 50, "apparence": 50, "force": 50, "karma": 50, "celebrite": 0},
            "journal": [], "evt": None, "vivant": True, "cause": "", "succes": [], "historique_metiers": [], "jetons": 0, "inventaire": [], "defis_reclames": [],
            "amis": [], "famille_relations": 65, "reputation": 50, "generation": 1, "heritage_parent": "",
            "identite_secrete": True, "suspicion": 0, "enfants_eloignes": [], "historique_choix": [],
            "maj": ""}


def new_game(nom, genre, univers, ville, av):
    g = defauts()
    g.update(nom=nom.strip() or "Alex", genre=genre, univers=univers, ville=ville, avatar=av)
    famille = random.choices(["modeste", "classe moyenne", "aisée"], [0.35, 0.5, 0.15])[0]
    g["famille"], g["fam"] = famille, {"modeste": 0, "classe moyenne": 1, "aisée": 2}[famille]
    S = g["stats"]
    for k in ("sante", "bonheur"):
        S[k] = random.randint(55, 95)
    for k in ("intelligence", "apparence", "force"):
        S[k] = random.randint(25, 85)
    g["trait"] = random.choice(["Surdoué·e", "Athlète né·e", "Charismatique", "Chanceux·se", "Rebelle", "Courageux·se"])
    g["amis"] = [{"nom": random.choice([n for n in PRENOMS if n != g["nom"]]), "relation": random.randint(45, 75)} for _ in range(2)]
    boost = {"Surdoué·e": ("intelligence", 15), "Athlète né·e": ("force", 15), "Charismatique": ("apparence", 15),
             "Courageux·se": ("sante", 8), "Rebelle": ("karma", -10), "Chanceux·se": ("bonheur", 8)}[g["trait"]]
    S[boost[0]] = clamp(S[boost[0]] + boost[1])
    g["notes"] = clamp(S["intelligence"] + random.randint(-10, 10))
    ne = "née" if genre == "Fille" else "né"
    log(g, f"👶 Tu es {ne} à {ville} ({UNIVERS[univers]['nom']}), dans une famille {famille}. Trait : {g['trait']}.")
    maj_succes(g)
    return g


def reparer(data):
    """Complète une ancienne sauvegarde avec les champs manquants."""
    g = defauts()
    stats = {**g["stats"], **data.get("stats", {})}
    g.update(data)
    g["stats"] = stats
    g["avatar"] = {**defauts()["avatar"], **data.get("avatar", {})}
    return g


# ======================================================================
#  SAUVEGARDES
# ======================================================================
def sauver(g):
    try:
        SAVE_DIR.mkdir(exist_ok=True)
        g["maj"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        (SAVE_DIR / f"{g['id']}.json").write_text(json.dumps(g, ensure_ascii=False, indent=1), encoding="utf-8")
        return True
    except Exception:
        return False


def lister_saves():
    out = []
    if SAVE_DIR.exists():
        for p in sorted(SAVE_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                out.append((p, d))
            except Exception:
                pass
    return out


def set_game(g):
    st.session_state["g"] = g
    st.session_state["flash"] = None
    for k in [k for k in st.session_state.keys() if str(k).startswith("coif_")]:
        del st.session_state[k]


# ======================================================================
#  MÉTIERS : conditions, chance, salaire
# ======================================================================
def manques(g, key):
    j, m = JOBS[key], []
    if g["age"] < j["age"]:
        m.append(f"{j['age']} ans minimum")
    if g["edu"] < j["edu"]:
        m.append(f"diplôme : {EDU_NOMS[j['edu']]}")
    if j["domaine"] and g["domaine"] not in j["domaine"]:
        m.append("domaine : " + " / ".join(j["domaine"]))
    if j["statmin"] and g["stats"][j["statmin"][0]] < j["statmin"][1]:
        m.append(f"{LABELS[j['statmin'][0]]} ≥ {j['statmin'][1]}")
    if j["cat"] == "Métier" and (g["en_ecole"] or g["etudes_en_cours"]):
        m.append("terminer tes études")
    if j["cat"] == "Job étudiant" and g["age"] > 30:
        m.append("trop âgé·e pour un job étudiant")
    if g["age"] >= 70:
        m.append("âge de la retraite")
    return m


def chance_embauche(g, key):
    j = JOBS[key]
    p = j["chance"]
    if j["atouts"]:
        avg = sum(g["stats"][a] for a in j["atouts"]) / len(j["atouts"])
        p += 0.5 * (avg - 50) / 100
    if not j["crime"]:
        p -= 0.1 * min(g["casier"], 3)
    return max(0.02, min(0.95, p))


def salaire(g):
    j = JOBS[g["metier"]]
    s = j["sal"] * j["mult"][g["grade"]]
    if j["variable"]:
        s *= random.uniform(0.15, 2.0)
    return int(s)


def arrestation(g, ans, raison):
    g["prison"] = ans
    g["casier"] += 1
    g["metier"], g["grade"], g["annees_metier"] = None, 0, 0
    g["reputation"] = clamp(g.get("reputation", 50) - 12)
    g["famille_relations"] = clamp(g.get("famille_relations", 60) - 5)
    chg(g, bonheur=-15, karma=-5)
    log(g, f"🚔 {raison} Condamné·e à {ans} an(s) de prison. Ta réputation et tes liens familiaux en prennent un coup.")


def mourir(g, cause):
    g["vivant"] = False
    g["cause"] = cause
    g["evt"] = None
    log(g, f"💀 Tu es mort·e à {g['age']} ans, {cause}.")


def mort_check(g):
    a, S = g["age"], g["stats"]
    p = 0.0003 * (1.105 ** max(0, a - 30))
    if S["sante"] < 30:
        p += (30 - S["sante"]) / 100 * 0.25
    if S["sante"] <= 0:
        p = 1
    if random.random() < p:
        if S["sante"] <= 10:
            cause = "emporté·e par une santé défaillante"
        elif a >= 75:
            cause = "paisiblement, de vieillesse"
        elif g["metier"] and JOBS[g["metier"]]["crime"]:
            cause = "lors d'un règlement de comptes"
        else:
            cause = random.choice(["d'une maladie soudaine", "dans un accident"])
        mourir(g, cause)


# ======================================================================
#  PASSAGE D'UNE ANNÉE
# ======================================================================
def passer_annee(g):
    if not g["vivant"]:
        return
    S, V = g["stats"], ville_info(g)
    g["age"] += 1
    a = g["age"]
    g["actions"] = ACTIONS_PAR_AN
    log(g, f"🎂 Tu as {a} ans.")

    # --- Corps & esprit
    if a > 35:
        S["sante"] = clamp(S["sante"] - random.choice([0, 1, 1, 2]) - (a - 35) // 25)
    else:
        S["sante"] = clamp(S["sante"] + random.randint(0, 2))
    if a > 30:
        S["apparence"] = clamp(S["apparence"] - random.choice([0, 0, 1]) - (1 if a > 50 else 0))
    if a > 40:
        S["force"] = clamp(S["force"] - random.choice([0, 1, 1, 2]))
    if a < 25:
        S["intelligence"] = clamp(S["intelligence"] + random.choice([0, 0, 1]))
    S["bonheur"] = clamp(S["bonheur"] + (50 - S["bonheur"]) * 0.1 + random.randint(-4, 4))
    S["celebrite"] = clamp(S["celebrite"] - 2)

    # --- École
    if a == 6:
        g["en_ecole"] = True
        log(g, "🏫 Première rentrée à l'école !")
    if g["en_ecole"] or g["etudes_en_cours"]:
        g["notes"] = clamp(g["notes"] + (S["intelligence"] - g["notes"]) * 0.15 + random.randint(-5, 5))
    if g["en_ecole"]:
        if a == 11:
            g["edu"] = max(g["edu"], 1)
            log(g, "🎒 Tu entres au collège.")
        elif a == 15:
            g["edu"] = max(g["edu"], 2)
            log(g, "📚 Tu entres au lycée.")
        elif a == 18:
            g["en_ecole"] = False
            if g["notes"] >= 35:
                g["edu"] = 4
                mention = "avec mention 🏅" if g["notes"] >= 70 else ""
                log(g, f"🎓 Diplôme de fin d'études obtenu {mention}!")
            else:
                g["edu"] = 3
                log(g, "😞 Tu rates ton diplôme de fin d'études.")
        if 7 <= a <= 17 and g["en_ecole"]:
            n = g["notes"]
            bulletin = "excellent" if n >= 75 else "bon" if n >= 55 else "moyen" if n >= 40 else "catastrophique"
            log(g, f"📝 Bulletin {bulletin} ({n}/100).")

    ec = g["etudes_en_cours"]
    if ec:
        g["argent"] -= int(1500 * V["cout"])
        ec["restant"] -= 1
        if ec["restant"] <= 0:
            if random.random() < 0.35 + g["notes"] / 150:
                g["edu"], g["domaine"] = ec["edu"], ec["domaine"]
                log(g, f"🎓 {ec['nom']} en {ec['domaine']} obtenu·e !")
                g["etudes_en_cours"] = None
            else:
                ec["restant"] = 1
                log(g, "📉 Tu rates tes examens : tu redoubles.")
                chg(g, bonheur=-6)

    # --- Argent entrant
    revenu = 0
    if 10 <= a < 18:
        revenu += int(random.randint(100, 500) * (1 + g["fam"]))

    # --- Prison ou travail
    if g["prison"] > 0:
        g["prison"] -= 1
        chg(g, bonheur=-4)
        log(g, "⛓️ Encore une année derrière les barreaux." if g["prison"] > 0 else "🔓 Tu es libéré·e !")
    elif g["metier"]:
        j = JOBS[g["metier"]]
        g["annees_metier"] += 1
        inc = salaire(g)
        revenu += inc
        g["dernier_salaire"] = inc
        if j["fame"]:
            S["celebrite"] = clamp(S["celebrite"] + j["fame"] + random.randint(0, 2))
        if j["cat"] != JE and g["grade"] < 3 and g["annees_metier"] % 2 == 0:
            p = 0.25 + S["intelligence"] / 400 if j["cat"] == "Métier" else 0.15 + S["celebrite"] / 300
            if random.random() < p:
                g["grade"] += 1
                log(g, f"📈 Promotion ! Tu deviens {j['grades'][g['grade']]}.")
                chg(g, bonheur=6)
        if random.random() < j["risque"]:
            if j["crime"] and random.random() < 0.55 - S["intelligence"] / 300:
                arrestation(g, random.randint(1, 6), f"Coup de filet dans ton activité de {j['nom'].lower()} !")
            else:
                dmg = random.randint(8, 30)
                chg(g, sante=-dmg)
                log(g, f"🤕 Accident du travail ({j['nom']}) : −{dmg} santé.")
                if S["sante"] <= 0 or (S["sante"] < 25 and random.random() < 0.05):
                    mourir(g, f"en pleine mission ({j['nom'].lower()})")
        if g["vivant"] and g["prison"] == 0 and g["metier"]:
            if j["cat"] == JE and a > 27:
                log(g, f"👋 Tu quittes ton job étudiant ({j['nom']}).")
                g["metier"], g["grade"], g["annees_metier"] = None, 0, 0
            elif a >= (70 if j["cat"] == "Métier rare" else 64):
                g["retraite"] = int(g["dernier_salaire"] * 0.45)
                log(g, f"🏖️ Retraite ! Pension : {fm(g, g['retraite'])}/an.")
                g["metier"], g["grade"], g["annees_metier"] = None, 0, 0
            elif j["cat"] == "Métier" and random.random() < 0.03 and S["bonheur"] < 60:
                log(g, "📦 Tu es licencié·e (restructuration).")
                g["metier"], g["grade"], g["annees_metier"] = None, 0, 0
                chg(g, bonheur=-10)
    if g["retraite"] and not g["metier"]:
        revenu += g["retraite"]

    # --- Aides sociales / bourses
    if a >= 18 and not g["metier"] and not g["retraite"] and g["prison"] == 0 and g["argent"] < 3000:
        revenu += 5000
        log(g, f"🏛️ Aides sociales / bourse : +{fm(g, 5000)}.")

    # --- Enfants & partenaire : les relations gardent la trace des choix passés
    for e in g["enfants"]:
        e["age"] += 1
        e.setdefault("relation", 65)
        e.setdefault("influence_parent", 0)
        # Les carrières risquées et les absences répétées abîment les liens.
        if g.get("metier") in ("heros_pro", "justicier_armure", "tisseur_urbain", "heros_energie",
                               "metamorphe", "telepathe", "chasseur_anomalies", "gardien_dimension",
                               "heroine_soins", "mercenaire", "bandit", "pirate") and e["age"] < 18:
            e["relation"] = clamp(e["relation"] - random.choice([0, 0, 1, 2]))
        elif g.get("metier") and g["metier"] in JOBS and JOBS[g["metier"]]["crime"]:
            e["influence_parent"] = clamp(e["influence_parent"] + 2)
            if g.get("reputation", 50) < 35:
                e["relation"] = clamp(e["relation"] - 1)
        elif g.get("famille_relations", 60) >= 70:
            e["relation"] = clamp(e["relation"] + random.choice([0, 1, 2]))
        if e["age"] >= 18 and e["relation"] < 20 and e["nom"] not in g.get("enfants_eloignes", []):
            g.setdefault("enfants_eloignes", []).append(e["nom"])
            log(g, f"💔 {e['nom']} prend ses distances après des années de relation difficile. Cette rupture pèsera sur l'héritage familial.")
    g["famille_relations"] = clamp(g.get("famille_relations", 60) + random.randint(-2, 2))
    for ami in g.get("amis", []):
        ami["relation"] = clamp(ami.get("relation", 50) + random.randint(-3, 2))
    p = g["partenaire"]
    if p:
        p["age"] += 1
        p["relation"] = clamp(p["relation"] + random.randint(-8, 3))
        if p["relation"] < 15 and random.random() < 0.5:
            if p["marie"]:
                perte = int(max(0, g["argent"]) * 0.35)
                g["argent"] -= perte
                log(g, f"💔 {p['nom']} demande le divorce. Pension et partage : −{fm(g, perte)}.")
            else:
                log(g, f"💔 {p['nom']} rompt avec toi.")
            g["partenaire"] = None
            chg(g, bonheur=-12)

    # --- Dépenses
    if a < 18 or g["prison"] > 0:
        dep = 0
    else:
        if g["chez_parents"] and a >= 24:
            g["chez_parents"] = False
            log(g, "🏠 Il est temps de quitter le nid : tu prends ton indépendance.")
        dep = (1200 if g["chez_parents"] else 13000) * V["cout"]
        dep += 2500 * V["cout"] * len([e for e in g["enfants"] if e["age"] < 18])
        if g["partenaire"]:
            dep += 1500
    dep = int(dep)
    g["argent"] += revenu - dep
    if g["argent"] < 0:
        g["argent"] = int(g["argent"] * 1.06)
        chg(g, bonheur=-3)
    if revenu or dep:
        log(g, f"💶 Bilan : +{fm(g, revenu)} / −{fm(g, dep)} → solde {fm(g, g['argent'])}.")

    # --- Mort, événement, succès
    if g["vivant"]:
        mort_check(g)
    if g["vivant"] and random.random() < 0.6:
        tirer_evenement(g)
    maj_succes(g)


# ======================================================================
#  ÉVÉNEMENTS À CHOIX
# ======================================================================
EVENTS = []


def event(eid, titre, texte, cond, choix):
    EVENTS.append(dict(id=eid, titre=titre, texte=texte, cond=cond, choix=choix))


def nouveau_partenaire(g):
    age = g["age"] + random.randint(-3, 3)
    age = max(18, age) if g["age"] >= 18 else min(17, max(14, age))
    g["partenaire"] = {"nom": random.choice(PRENOMS), "age": age, "relation": random.randint(45, 70), "marie": False}
    return g["partenaire"]


def ev_amour(g):
    p = 0.3 + g["stats"]["apparence"] / 200 + g["stats"]["bonheur"] / 500
    if random.random() < p:
        nom = nouveau_partenaire(g)["nom"]
        return res(g, f"💘 {nom} dit OUI ! Vous êtes ensemble.", bonheur=12)
    return res(g, "💔 Râteau monumental… ça pique.", bonheur=-8)


def ev_harcelement(g):
    if g["stats"]["force"] + random.randint(-20, 20) > 50:
        return res(g, "💪 Tu tiens tête à ton harceleur. Il ne t'embête plus.", bonheur=8)
    return res(g, "😣 Ça tourne mal : tu y laisses des plumes.", sante=-8, bonheur=-6)


def ev_triche(g):
    if random.random() < 0.5:
        return res(g, "😏 Personne n'a rien vu : bonne note !", notes=8, karma=-3)
    return res(g, "😱 Tu te fais prendre ! Convocation des parents.", notes=-10, bonheur=-5, karma=-4)


def ev_loterie(g):
    p = 1 / 300 if "Chanceux" in g["trait"] else 1 / 1000
    if random.random() < p:
        gain = random.randint(250000, 1000000)
        return res(g, f"🎰 JACKPOT !!! Tu gagnes {fm(g, gain)} !", argent=gain, bonheur=25)
    return res(g, "🎟️ Perdu… ce sera pour la prochaine fois.", argent=-10)


def ev_duel(g):
    if g["stats"]["force"] + random.randint(-25, 25) > 55:
        return res(g, "🔥 Duel gagné ! Tu gagnes en confiance… et en puissance.", force=5, celebrite=3, bonheur=5)
    return res(g, "😵 Tu perds le duel, humilié·e devant tout le monde.", sante=-10, bonheur=-6)


def ev_dragon(g):
    force = (g["stats"]["force"] + g["stats"]["intelligence"]) / 2
    if force + random.randint(-25, 25) > 55:
        gain = random.randint(10000, 40000)
        return res(g, f"🐉 Tu terrasses le dragon ! Le royaume te récompense : {fm(g, gain)}.", argent=gain, celebrite=15, bonheur=10)
    return res(g, "🔥 Le dragon te carbonise à moitié… tu survis de justesse.", sante=-35, bonheur=-8)


def ev_negocier_dragon(g):
    if g["stats"]["intelligence"] + random.randint(-25, 25) > 60:
        return res(g, "🗣️ Le dragon accepte un pacte : plus de ravages, et un joli trésor.", argent=8000, karma=5, celebrite=6)
    return res(g, "🗣️ Le dragon rit… et te chasse à coups de queue.", sante=-12)


def ev_potion(g):
    if random.random() < 0.55:
        return res(g, "🧪 Potion de vitalité ! Tu te sens revivre.", sante=15, argent=-500)
    return res(g, "🤢 C'était de la tisane périmée…", sante=-10, argent=-500)


def ev_hack(g):
    if random.random() < 0.55:
        gain = random.randint(20000, 100000)
        return res(g, f"💻 Tu siphonnes {fm(g, gain)} sans laisser de trace.", argent=gain, karma=-8)
    arrestation(g, random.randint(1, 3), "La mégacorpo te remonte jusqu'à toi !")
    return "🚔 Les agents corpo débarquent : tu es arrêté·e."


def ev_police_fuir(g):
    if random.random() < 0.5:
        return res(g, "🏃 Tu files par une fenêtre. Tu leur échappes de justesse !", bonheur=3)
    arrestation(g, random.randint(1, 4), "La police te rattrape !")
    return "🚔 Menottes aux poignets."


def ev_police_corrompre(g):
    if g["argent"] < 5000:
        arrestation(g, random.randint(1, 3), "Tu n'as même pas de quoi payer le pot-de-vin !")
        return "Ça se termine en cellule."
    return res(g, "🤝 Quelques billets plus tard, le dossier disparaît.", argent=-5000, karma=-3)


def ev_police_rendre(g):
    arrestation(g, random.randint(1, 2), "Tu te rends sans résistance.")
    return "Peine réduite pour bonne coopération."


def ev_mariage(g):
    g["partenaire"]["marie"] = True
    return res(g, f"💍 Tu épouses {g['partenaire']['nom']} ! Quelle fête !", bonheur=15, argent=-2000)


def ev_enfant(g):
    nom = random.choice(PRENOMS)
    g["enfants"].append({"nom": nom, "age": 0, "relation": 70, "influence_parent": 0})
    return res(g, f"👶 {nom} vient au monde ! Quelle joie !", bonheur=15)


def ev_negocier(g):
    if random.random() < 0.3 + g["stats"]["intelligence"] / 250 and g["grade"] < 3:
        g["grade"] += 1
        return res(g, f"💼 Ton patron cède : tu deviens {JOBS[g['metier']]['grades'][g['grade']]} !", bonheur=8)
    return res(g, "🙅 Refus poli. Tu repars la queue entre les jambes.", bonheur=-4)


def a_job_normal(g):
    return bool(g["metier"]) and g["prison"] == 0 and JOBS[g["metier"]]["cat"] == "Métier"


LIBRE = lambda g: g["prison"] == 0 and g["age"] >= 5  # noqa: E731
event("chiot", "Un chiot errant", "🐶 Un chiot errant te suit depuis l'école. Il a l'air affamé.",
      lambda g: 5 <= g["age"] <= 14 and g["prison"] == 0,
      [("Le ramener à la maison", lambda g: res(g, "🐶 Il devient ton meilleur ami !", bonheur=10)),
       ("L'ignorer", lambda g: res(g, "😔 Tu te retournes… il a disparu.", karma=-3, bonheur=-2))])
event("harcelement", "Harcèlement", "😠 Un camarade te harcèle depuis des semaines.",
      lambda g: 8 <= g["age"] <= 17 and g["prison"] == 0,
      [("Te défendre", ev_harcelement),
       ("En parler à un adulte", lambda g: res(g, "🧑‍🏫 L'adulte intervient. Ça aide.", bonheur=4, karma=2)),
       ("Ignorer", lambda g: res(g, "😞 Ça continue…", bonheur=-8))])
event("triche", "Contrôle surprise", "📝 Gros contrôle demain… et tu vois la copie de ton voisin du coin de l'œil.",
      lambda g: 11 <= g["age"] <= 17 and g["en_ecole"],
      [("Copier", ev_triche),
       ("Réviser honnêtement", lambda g: res(g, "📖 Tu bosses sérieusement.", notes=5, intelligence=2, karma=2))])
event("premier_amour", "Un coup de cœur", "💘 Quelqu'un te plaît vraiment…",
      lambda g: 14 <= g["age"] <= 25 and not g["partenaire"] and g["prison"] == 0,
      [("Te déclarer", ev_amour), ("Rester ami·e", lambda g: res(g, "🙂 Tu gardes ça pour toi.", bonheur=-1))])
event("soiree", "Soirée douteuse", "🍻 En soirée, on te propose quelque chose de louche.",
      lambda g: 15 <= g["age"] <= 40 and g["prison"] == 0,
      [("Refuser", lambda g: res(g, "😌 Tu gardes la tête froide.", karma=3)),
       ("Essayer", lambda g: res(g, "🤪 Grosse soirée… gros lendemain.", bonheur=6, sante=-8, karma=-2))])
event("heritage", "Héritage surprise", "📬 Un parent éloigné te lègue un petit pécule.",
      lambda g: 25 <= g["age"] <= 80,
      [("Accepter", lambda g: res(g, "💰 Cadeau du ciel !", argent=random.randint(5000, 60000), bonheur=5))])
event("accident", "Accident", "🚑 Tu es victime d'un accident.",
      lambda g: g["age"] >= 8,
      [("Aller à l'hôpital", lambda g: res(g, "🏥 Rien de grave, mais ça coûte cher.", argent=-random.randint(300, 3000), sante=-5)),
       ("Serrer les dents", lambda g: res(g, "😖 Ça aurait dû être soigné…", sante=-15))])
event("loterie", "Ticket de loterie", "🎟️ Un ticket à gratter à 10 pièces te fait de l'œil.",
      lambda g: g["age"] >= 18 and g["prison"] == 0,
      [("Tenter ta chance", ev_loterie), ("Passer ton chemin", lambda g: "🙂 Tu gardes ton argent.")])
event("portefeuille", "Portefeuille trouvé", "👛 Tu trouves un portefeuille bien garni par terre.",
      lambda g: g["age"] >= 10 and g["prison"] == 0,
      [("Le rendre", lambda g: res(g, "😇 Le propriétaire te remercie chaleureusement.", karma=8, bonheur=3, argent=50)),
       ("Le garder", lambda g: res(g, "😈 Tu empoches l'argent.", argent=random.randint(200, 800), karma=-8))])
event("heures_sup", "Heures sup", "⏰ Ton patron te demande de faire des heures supplémentaires.", a_job_normal,
      [("Accepter", lambda g: res(g, "💼 Tu bosses dur, tu es payé·e.", argent=2000, sante=-3, bonheur=-3)),
       ("Refuser", lambda g: res(g, "😌 Tu profites de ta soirée.", bonheur=2))])
event("burnout", "Épuisement", "🔥 Tu es à bout de forces au travail.",
      lambda g: a_job_normal(g) and (g["stats"]["sante"] < 55 or g["stats"]["bonheur"] < 35),
      [("Prendre un congé", lambda g: res(g, "🌴 Tu te ressources.", sante=10, bonheur=8, argent=-1000)),
       ("Continuer quand même", lambda g: res(g, "😵 Tu t'enfonces…", sante=-12, bonheur=-6))])
event("maladie", "Un souci de santé", "🩺 Tu ne te sens pas bien depuis un moment.",
      lambda g: g["age"] > 30 and g["stats"]["sante"] < 50,
      [("Consulter", lambda g: res(g, "💊 Un traitement et ça va mieux.", argent=-500, sante=12)),
       ("Attendre que ça passe", lambda g: res(g, "😷 Ça empire.", sante=-10))])
event("negociation", "Moment de vérité", "💬 Tu sens que c'est le moment de demander plus à ton patron.",
      lambda g: a_job_normal(g) and g["grade"] < 3 and g["annees_metier"] >= 1,
      [("Négocier une promotion", ev_negocier), ("Rester discret·e", lambda g: "🙂 Tu continues ton chemin.")])
event("viral", "Vidéo virale", "📱 Une vidéo de toi explose sur les réseaux !",
      lambda g: g["univers"] in ("real", "cyber", "manga") and 14 <= g["age"] <= 60 and g["prison"] == 0,
      [("Surfer sur la vague", lambda g: res(g, "🚀 Des milliers de nouveaux fans !", celebrite=12, bonheur=5, argent=500)),
       ("Rester discret·e", lambda g: res(g, "🫥 La vague passe.", bonheur=1))])
event("casting", "Un agent te repère", "🎬 Un agent te propose un casting.",
      lambda g: 14 <= g["age"] <= 35 and g["stats"]["apparence"] >= 55 and g["prison"] == 0,
      [("Accepter le casting", lambda g: (res(g, "🌟 Tu es pris·e ! Premiers cachets.", celebrite=10, argent=3000, bonheur=6)
                                          if random.random() < 0.4 else res(g, "😕 Ils ont pris quelqu'un d'autre.", bonheur=-3))),
       ("Refuser", lambda g: "🙂 Tu passes ton chemin.")])
event("rival", "Un rival te défie", "🥊 Ton rival te défie en duel devant tout le monde !",
      lambda g: g["univers"] == "manga" and 10 <= g["age"] <= 35 and g["prison"] == 0,
      [("Accepter le duel", ev_duel), ("Décliner", lambda g: res(g, "😬 On te traite de poltron.", bonheur=-3))])
event("parchemin", "Parchemin interdit", "📜 Tu découvres un parchemin interdit : un pouvoir immense… à quel prix ?",
      lambda g: g["univers"] == "manga" and 12 <= g["age"] <= 40,
      [("L'étudier", lambda g: res(g, "⚡ Tu gagnes un pouvoir énorme, mais ton âme s'assombrit.", force=12, karma=-8, sante=-6)),
       ("Le brûler", lambda g: res(g, "🔥 Sage décision.", karma=5))])
event("dragon", "Un dragon attaque !", "🐲 Un dragon menace le village !",
      lambda g: g["univers"] == "fantasy" and 18 <= g["age"] <= 60 and g["prison"] == 0,
      [("L'affronter", ev_dragon), ("Négocier", ev_negocier_dragon),
       ("Fuir", lambda g: res(g, "🏃 Tu te sauves, mais la honte te suit.", bonheur=-6, karma=-2))])
event("marchand", "Marchand de potions", "🧙 Un marchand ambulant te vante sa potion miracle.",
      lambda g: g["univers"] == "fantasy" and g["age"] >= 12,
      [("Acheter (500)", ev_potion), ("Refuser", lambda g: "🙂 Tu passes ton chemin.")])
event("implant", "Implant cybernétique", "🦾 Un ripperdoc te propose un implant militaire gratuit.",
      lambda g: g["univers"] == "cyber" and g["age"] >= 16,
      [("Accepter", lambda g: res(g, "⚙️ Bras renforcé ! Mais le corps proteste…", force=12, sante=-8, apparence=-3)),
       ("Refuser", lambda g: "🙂 Tu restes humain·e.")])
event("faille", "Faille dans la banque", "🏦 Tu repères une faille béante dans le système d'une banque.",
      lambda g: g["univers"] == "cyber" and g["stats"]["intelligence"] >= 55 and g["age"] >= 16 and g["prison"] == 0,
      [("Pirater", ev_hack),
       ("Signaler la faille", lambda g: res(g, "🏅 La banque te remercie (et te paye).", karma=10, argent=2000))])
event("descente", "Descente de police !", "🚨 La police débarque dans ta planque !",
      lambda g: bool(g["metier"]) and g["prison"] == 0 and JOBS[g["metier"]]["crime"],
      [("Fuir", ev_police_fuir), ("Corrompre (5000)", ev_police_corrompre), ("Te rendre", ev_police_rendre)])
event("demande", "Demande en mariage", "💍 Ton/ta partenaire s'agenouille et te demande en mariage !",
      lambda g: bool(g["partenaire"]) and not g["partenaire"]["marie"] and g["partenaire"]["relation"] >= 70 and g["age"] >= 20,
      [("Dire oui", ev_mariage),
       ("Refuser", lambda g: (g["partenaire"].update(relation=max(0, g["partenaire"]["relation"] - 25)) or
                              res(g, "😬 Silence gêné.", bonheur=-5)))])
event("bebe", "Bébé en route", "🤰 Vous attendez un enfant !",
      lambda g: bool(g["partenaire"]) and g["partenaire"]["marie"] and 20 <= g["age"] <= 42 and len(g["enfants"]) < 4,
      [("L'accueillir avec joie", ev_enfant), ("Pas maintenant…", lambda g: res(g, "🕰️ Ce sera pour plus tard.", bonheur=-2))])
# Événements supplémentaires : relations, réputation et vie héroïque
def ev_sauver_inconnu(g):
    g["reputation"] = clamp(g.get("reputation", 50) + 12)
    if random.random() < 0.65:
        return res(g, "🦸 Tu sauves un inconnu. La vidéo devient virale et ta réputation grimpe !", karma=8, celebrite=7, bonheur=6)
    if g.get("partenaire"):
        g["partenaire"]["relation"] = clamp(g["partenaire"]["relation"] - 5)
    return res(g, "🚑 Tu sauves la personne, mais tu rentres blessé·e et en retard.", karma=8, sante=-10, bonheur=2)

def ev_identite_secrete(g):
    if g.get("partenaire"):
        g["partenaire"]["relation"] = clamp(g["partenaire"].get("relation", 50) + 8)
    g["famille_relations"] = clamp(g.get("famille_relations", 60) + 5)
    return res(g, "🤝 Tu révèles une partie de la vérité à tes proches. Ils comprennent mieux tes absences.", bonheur=5, karma=3)

def ev_rival_heroique(g):
    if g["stats"]["force"] + g["stats"]["intelligence"] > 115:
        g["reputation"] = clamp(g.get("reputation", 50) + 10)
        return res(g, "⚡ Tu déjoues le piège de ton rival sans mettre les civils en danger.", celebrite=8, karma=5, bonheur=5)
    g["reputation"] = clamp(g.get("reputation", 50) - 8)
    return res(g, "💥 Le duel tourne mal : dégâts matériels et réputation en baisse.", sante=-12, bonheur=-5, karma=-4)

def ev_ami_besoin(g):
    if g.get("amis"):
        ami = max(g["amis"], key=lambda x: x.get("relation", 50))
        ami["relation"] = clamp(ami.get("relation", 50) + 12)
    return res(g, "🫂 Tu mets tes projets de côté pour aider un ami. Il s'en souviendra.", bonheur=7, karma=5)

def ev_famille_conflit(g):
    g["famille_relations"] = clamp(g.get("famille_relations", 60) - 12)
    return res(g, "💢 Une dispute éclate. Si tu ne prends pas le temps de renouer, le lien risque de s'abîmer.", bonheur=-6, karma=-2)

event("sauvetage_heroique", "Un sauvetage risqué", "🚨 Un accident éclate près de toi. Tu peux intervenir, mais quelqu'un pourrait découvrir ton identité.",
      lambda g: g.get("metier") in ("heros_pro", "justicier_armure", "tisseur_urbain", "heros_energie", "metamorphe", "telepathe", "chasseur_anomalies", "gardien_dimension", "heroine_soins") and g["age"] >= 16 and g["prison"] == 0,
      [("Intervenir", ev_sauver_inconnu), ("Attendre les secours", lambda g: res(g, "🚑 Les secours prennent le relais. Tu évites le risque, mais tu te demandes si tu aurais pu aider.", bonheur=-1, karma=1))])
event("identite_secrete", "Le secret devient lourd", "🎭 Tes proches se demandent pourquoi tu disparais souvent et rentres blessé·e.",
      lambda g: g.get("metier") in ("heros_pro", "justicier_armure", "tisseur_urbain", "heros_energie", "metamorphe", "telepathe", "chasseur_anomalies", "gardien_dimension", "heroine_soins") and (g.get("partenaire") or g.get("enfants")),
      [("Faire confiance à tes proches", ev_identite_secrete), ("Garder le secret", lambda g: (g.update(suspicion=clamp(g.get("suspicion", 0)+10)) or res(g, "🤐 Tu gardes le secret. Il reste protégé, mais la pression et les soupçons grandissent.", bonheur=-3, karma=1)))])
event("rival_heroique", "Un rival te provoque", "⚔️ Un autre justicier t'accuse de voler la vedette et te provoque en public.",
      lambda g: g.get("metier") in ("heros_pro", "justicier_armure", "tisseur_urbain", "heros_energie", "metamorphe", "telepathe", "chasseur_anomalies", "gardien_dimension", "heroine_soins") and g["age"] >= 16,
      [("Relever le défi", ev_rival_heroique), ("Désamorcer le conflit", lambda g: res(g, "🕊️ Tu refuses le spectacle et proposes une coopération.", karma=5, bonheur=3))])
event("ami_besoin", "Un ami a besoin de toi", "📱 Un ami traverse une période difficile et te demande du temps.",
      lambda g: bool(g.get("amis")) and g["age"] >= 8,
      [("Être présent·e", ev_ami_besoin), ("Refuser par manque de temps", lambda g: (g["amis"][0].update(relation=clamp(g["amis"][0].get("relation", 50)-10)) or res(g, "📵 Tu déclines. Ton ami le prend mal.", bonheur=-2)))])
event("conflit_famille", "Une dispute familiale", "🏠 Un désaccord ancien revient sur la table pendant un repas de famille.",
      lambda g: g["age"] >= 12 and g.get("famille_relations", 60) < 80,
      [("Écouter et chercher un compromis", lambda g: (g.update(famille_relations=clamp(g.get("famille_relations", 60)+10)) or res(g, "💬 Vous trouvez un terrain d'entente. Les liens se réparent.", bonheur=4, karma=3))), ("Partir en claquant la porte", ev_famille_conflit)])

# --- Intrigues à conséquences durables
def ev_reveler_identite(g):
    g["identite_secrete"] = False
    g["reputation"] = clamp(g.get("reputation", 50) + 15)
    g["suspicion"] = 100
    g["famille_relations"] = clamp(g.get("famille_relations", 60) - 18)
    if g.get("partenaire"):
        g["partenaire"]["relation"] = clamp(g["partenaire"].get("relation", 50) - 15)
    for enfant in g.get("enfants", []):
        enfant["relation"] = clamp(enfant.get("relation", 65) - 12)
    g.setdefault("historique_choix", []).append({"age": g["age"], "evenement": "Identité révélée", "choix": "Assumer publiquement"})
    return res(g, "📸 Ton identité est révélée. Ta réputation grimpe, mais ta famille devient une cible médiatique : les liens se fragilisent durablement.", celebrite=12, bonheur=-8, karma=2)

def ev_proteger_identite(g):
    g["suspicion"] = clamp(g.get("suspicion", 0) + 15)
    if g.get("partenaire"):
        g["partenaire"]["relation"] = clamp(g["partenaire"].get("relation", 50) - 5)
    g.setdefault("historique_choix", []).append({"age": g["age"], "evenement": "Identité menacée", "choix": "Protéger le secret"})
    return res(g, "🕶️ Tu brouilles les pistes. Ton identité reste cachée, mais les mensonges et les absences pèsent sur tes proches.", bonheur=-3, karma=1)

def ev_enfant_reputation(g):
    candidats = [e for e in g.get("enfants", []) if e.get("age", 0) >= 10]
    if not candidats:
        return res(g, "🏫 L'école parle de ta famille, mais tes enfants sont encore trop jeunes pour comprendre.", bonheur=-1)
    enfant = min(candidats, key=lambda e: e.get("relation", 65))
    enfant["relation"] = clamp(enfant.get("relation", 65) - 12)
    enfant["influence_parent"] = clamp(enfant.get("influence_parent", 0) + 10)
    g["famille_relations"] = clamp(g.get("famille_relations", 60) - 5)
    return res(g, f"🏫 À cause de ta réputation, {enfant['nom']} subit des remarques à l'école. Il/elle t'en veut de ne pas l'avoir protégé·e.", bonheur=-6, karma=-2)

def ev_reparer_lien_enfant(g):
    candidats = [e for e in g.get("enfants", []) if e.get("relation", 65) < 75]
    if not candidats:
        return res(g, "💞 Tes enfants se sentent proches de toi. Ce moment renforce la confiance.", bonheur=4)
    enfant = min(candidats, key=lambda e: e.get("relation", 65))
    enfant["relation"] = clamp(enfant.get("relation", 65) + 18)
    g["famille_relations"] = clamp(g.get("famille_relations", 60) + 6)
    return res(g, f"❤️ Tu prends enfin du temps pour {enfant['nom']}. La confiance revient, mais elle devra être entretenue.", bonheur=7, karma=3)

event("identite_menacee", "Ton identité est en danger", "📸 Un journaliste a presque découvert qui se cache derrière ton costume. Tu peux assumer ton identité ou protéger le secret, au risque d'éloigner tes proches.",
      lambda g: g.get("metier") in ("heros_pro", "justicier_armure", "tisseur_urbain", "heros_energie", "metamorphe", "telepathe", "chasseur_anomalies", "gardien_dimension", "heroine_soins") and g.get("identite_secrete", True) and (g["stats"]["celebrite"] >= 15 or g.get("reputation", 50) >= 65),
      [("Révéler ton identité au public", ev_reveler_identite), ("Protéger le secret", ev_proteger_identite)])

event("reputation_enfant", "La réputation de la famille", "🏫 Ton passé fait parler de lui et un de tes enfants en subit les conséquences à l'école.",
      lambda g: bool([e for e in g.get("enfants", []) if e.get("age", 0) >= 10]) and (g.get("casier", 0) > 0 or g.get("reputation", 50) < 30),
      [("Écouter ton enfant et l'aider", ev_reparer_lien_enfant), ("Minimiser le problème", ev_enfant_reputation)])

def ev_absence_aggravee(g):
    enfant = min(g["enfants"], key=lambda e: e.get("relation", 65))
    enfant["relation"] = clamp(enfant.get("relation", 65) - 10)
    return res(g, "🚪 La discussion tourne court. Ton enfant se referme et le lien s'abîme encore.", bonheur=-5, karma=-2)

event("enfant_eloignement", "Tu as été trop absent·e", "💬 Un enfant te reproche d'avoir toujours fait passer ton travail ou tes ambitions avant lui/elle.",
      lambda g: any(e.get("age", 0) >= 8 and e.get("relation", 65) < 60 for e in g.get("enfants", [])),
      [("Prendre du temps pour réparer le lien", ev_reparer_lien_enfant),
       ("Dire que ton travail passe d'abord", ev_absence_aggravee)])

EVENTS_BY_ID = {e["id"]: e for e in EVENTS}


def tirer_evenement(g):
    eligibles = [e for e in EVENTS if e["cond"](g)]
    if eligibles:
        e = random.choice(eligibles)
        g["evt"] = {"id": e["id"], "texte": e["texte"]}


def maj_succes(g):
    S = g["stats"]
    j = JOBS.get(g["metier"]) if g["metier"] else None
    conds = [
        ("🎓 Diplômé·e du supérieur", g["edu"] >= 5), ("🧑‍🎓 Docteur·e", g["edu"] >= 7),
        ("💰 Millionnaire", g["argent"] >= 1_000_000), ("⭐ Superstar", S["celebrite"] >= 80),
        ("🚔 Casier judiciaire", g["casier"] >= 1), ("💍 Marié·e", bool(g["partenaire"] and g["partenaire"]["marie"])),
        ("👨‍👩‍👧 Parent", bool(g["enfants"])), ("👑 Sommet de carrière", bool(j) and g["grade"] == 3),
        ("🌟 Métier rare", bool(j) and j["cat"] == "Métier rare"), ("🏴‍☠️ Hors-la-loi", bool(j) and j["crime"]),
        ("🧓 Centenaire", g["age"] >= 100), ("🏖️ Retraite paisible", g["retraite"] > 0),
        ("🧠 Génie", S["intelligence"] >= 95), ("💪 Colosse", S["force"] >= 95),
    ]
    for nom, ok in conds:
        if ok and nom not in g["succes"]:
            g["succes"].append(nom)
            log(g, f"🏆 Succès débloqué : {nom}")


# ======================================================================
#  ACTIONS
# ======================================================================
ACTIONS = {}


def action(aid, cout=1, prison_ok=False):
    def deco(fn):
        ACTIONS[aid] = (fn, cout, prison_ok)
        return fn
    return deco


ENTRAINEMENTS = {
    "real": ("🥋 Cours d'arts martiaux", "Tu t'inscris à un dojo."),
    "manga": ("🌊 S'entraîner sous une cascade", "Tu médites sous l'eau glacée, en canalisant ton chakra."),
    "fantasy": ("📖 Étudier la magie", "Tu plonges dans un grimoire poussiéreux."),
    "cyber": ("🦾 Installer un implant", "Un ripperdoc t'installe un module de combat."),
}


@action("gym")
def a_gym(g):
    chg(g, force=random.randint(3, 7), sante=random.randint(1, 4), apparence=1, bonheur=2)
    return "🏋️ Séance de sport intense : tu te sens plus fort·e."


@action("lire")
def a_lire(g):
    chg(g, intelligence=random.randint(2, 4), bonheur=1)
    return "📖 Tu lis un bon livre : +intelligence."


@action("meditation")
def a_med(g):
    chg(g, bonheur=random.randint(3, 6), sante=1)
    return "🧘 Méditation : l'esprit apaisé."


@action("fete")
def a_fete(g):
    if g["age"] < 15:
        raise Refus("🚫 Trop jeune pour faire la fête.")
    chg(g, bonheur=random.randint(6, 10), sante=-random.randint(1, 4))
    return "🎉 Soirée mémorable (le lendemain est plus dur)."


@action("voyage")
def a_voyage(g):
    payer(g, int(2500 * ville_info(g)["cout"]))
    chg(g, bonheur=random.randint(10, 16))
    return "✈️ Voyage inoubliable !"


@action("medecin_visite")
def a_med_visite(g):
    payer(g, 150)
    chg(g, sante=random.randint(8, 16))
    return "🩺 Visite chez le médecin : ça va mieux."


@action("chirurgie")
def a_chirurgie(g):
    if g["age"] < 18:
        raise Refus("🚫 Réservé aux adultes.")
    payer(g, 8000)
    if random.random() < 0.12:
        chg(g, apparence=-10, sante=-10)
        return "😱 Opération ratée… tu ne ressembles plus à grand-chose."
    chg(g, apparence=random.randint(6, 14))
    return "💉 Retouches réussies : tu rayonnes."


@action("benevolat")
def a_benevolat(g):
    chg(g, karma=random.randint(5, 9), bonheur=3)
    return "🤝 Tu donnes de ton temps : karma en hausse."


@action("entrainement")
def a_entrainement(g):
    u = g["univers"]
    if u == "real":
        chg(g, force=random.randint(3, 6), intelligence=1)
    elif u == "manga":
        chg(g, force=random.randint(5, 9), sante=-2)
    elif u == "fantasy":
        chg(g, intelligence=random.randint(3, 6), force=2)
    else:
        chg(g, force=random.randint(5, 10), sante=-4)
    return ENTRAINEMENTS[u][1]


@action("coiffeur")
def a_coiffeur(g):
    payer(g, 40)
    g["avatar"]["coupe"] = st.session_state["coif_coupe"]
    g["avatar"]["couleur"] = st.session_state["coif_couleur"]
    chg(g, apparence=2, bonheur=3)
    return "💇 Nouveau look ! Tu te trouves canon."


@action("demenager")
def a_demenager(g):
    nv = st.session_state["coif_ville"]
    if nv == g["ville"]:
        raise Refus("🏠 Tu vis déjà ici.")
    payer(g, int(1500 * UNIVERS[g["univers"]]["villes"][nv]["cout"]))
    g["ville"] = nv
    chg(g, bonheur=3)
    return f"📦 Tu déménages à {nv}."


@action("independance")
def a_independance(g):
    if not g["chez_parents"]:
        raise Refus("🏠 Tu es déjà indépendant·e.")
    if g["age"] < 18:
        raise Refus("🚫 Il faut être majeur·e.")
    g["chez_parents"] = False
    chg(g, bonheur=5)
    return "🏠 Tu prends ton indépendance (les factures aussi !)."


# --- Études
@action("etudier")
def a_etudier(g):
    if not (g["en_ecole"] or g["etudes_en_cours"]):
        raise Refus("🎓 Tu n'étudies pas en ce moment.")
    chg(g, notes=random.randint(5, 10), intelligence=1, bonheur=-2)
    return "✏️ Tu bûches sérieusement."


@action("secher")
def a_secher(g):
    if not g["en_ecole"]:
        raise Refus("🎓 Tu n'es pas à l'école.")
    chg(g, notes=-random.randint(4, 8), bonheur=4, karma=-2)
    return "🛹 Tu sèches les cours."


@action("arreter_ecole", cout=0)
def a_arreter(g):
    if not g["en_ecole"] and not g["etudes_en_cours"]:
        raise Refus("🎓 Tu n'étudies pas en ce moment.")
    if g["etudes_en_cours"]:
        g["etudes_en_cours"] = None
        return "📕 Tu abandonnes tes études supérieures."
    if g["age"] < 16:
        raise Refus("🚫 Obligatoire jusqu'à 16 ans.")
    g["en_ecole"] = False
    chg(g, bonheur=3, karma=-2)
    return "📕 Tu quittes l'école."


@action("inscrire")
def a_inscrire(g):
    dom = st.session_state["f_domaine"]
    if g["age"] < 18 or g["en_ecole"] or g["etudes_en_cours"] or g["edu"] not in NIVEAUX_UNIV or g["prison"] > 0:
        raise Refus("🎓 Inscription impossible pour le moment.")
    nom, duree, edu_obt = NIVEAUX_UNIV[g["edu"]]
    p = 0.55 + g["notes"] / 200 - (0.2 if dom == "Médecine" else 0)
    if random.random() > p:
        chg(g, bonheur=-6)
        return f"📨 Candidature en {nom} ({dom}) refusée…"
    g["etudes_en_cours"] = {"nom": nom, "domaine": dom, "restant": duree, "edu": edu_obt}
    return f"🎓 Inscrit·e en {nom} de {dom} ({duree} ans)."


# --- Carrière
@action("postuler")
def a_postuler(g, cle=None):
    j = JOBS[cle]
    m = manques(g, cle)
    if m or g["prison"] > 0:
        raise Refus("🔒 Conditions non remplies : " + ", ".join(m))
    if random.random() < chance_embauche(g, cle):
        if g["metier"]:
            g["historique_metiers"].append(JOBS[g["metier"]]["nom"])
        g["metier"], g["grade"], g["annees_metier"] = cle, 0, 0
        chg(g, bonheur=8)
        return f"🎉 Embauché·e : {j['emoji']} {j['nom']} !"
    chg(g, bonheur=-4)
    return f"❌ Candidature refusée pour {j['nom']}."


@action("demission", cout=0)
def a_demission(g):
    if not g["metier"]:
        raise Refus("Tu n'as pas d'emploi.")
    nom = JOBS[g["metier"]]["nom"]
    g["historique_metiers"].append(nom)
    g["metier"], g["grade"], g["annees_metier"] = None, 0, 0
    return f"👋 Tu quittes ton poste ({nom})."


@action("promotion")
def a_promotion(g):
    if not g["metier"] or JOBS[g["metier"]]["cat"] == JE:
        raise Refus("Pas de promotion possible ici.")
    if g["grade"] >= 3:
        raise Refus("🏆 Tu es déjà au sommet !")
    if random.random() < 0.15 + g["stats"]["intelligence"] / 300 + 0.04 * g["annees_metier"]:
        g["grade"] += 1
        chg(g, bonheur=6)
        return f"📈 Promotion : {JOBS[g['metier']]['grades'][g['grade']]} !"
    chg(g, bonheur=-3)
    return "🙅 Pas de promotion cette fois."


# --- Amour & famille
@action("rencontrer")
def a_rencontrer(g):
    if g["age"] < 14:
        raise Refus("🚫 Trop jeune pour ça.")
    if g["partenaire"]:
        raise Refus("💞 Tu as déjà un·e partenaire.")
    if random.random() < 0.35 + g["stats"]["apparence"] / 200 + g["stats"]["bonheur"] / 500:
        p = nouveau_partenaire(g)
        chg(g, bonheur=10)
        return f"💘 Tu rencontres {p['nom']} ({p['age']} ans). Étincelle !"
    chg(g, bonheur=-2)
    return "🙁 Aucune rencontre intéressante cette fois."


@action("ensemble")
def a_ensemble(g):
    if not g["partenaire"]:
        raise Refus("💞 Pas de partenaire.")
    g["partenaire"]["relation"] = clamp(g["partenaire"]["relation"] + random.randint(6, 14))
    g["famille_relations"] = clamp(g.get("famille_relations", 60) + 1)
    chg(g, bonheur=4)
    return f"🥰 Moment complice avec {g['partenaire']['nom']}."


@action("cadeau")
def a_cadeau(g):
    if not g["partenaire"]:
        raise Refus("💞 Pas de partenaire.")
    payer(g, 200)
    g["partenaire"]["relation"] = clamp(g["partenaire"]["relation"] + 9)
    return f"🎁 Cadeau offert à {g['partenaire']['nom']}."


@action("mariage")
def a_mariage(g):
    p = g["partenaire"]
    if not p or p["marie"] or g["age"] < 18:
        raise Refus("💍 Impossible pour le moment.")
    if p["relation"] < 60:
        raise Refus("💔 La relation n'est pas assez solide (≥ 60).")
    payer(g, 3000)
    if random.random() < p["relation"] / 100 + 0.1:
        p["marie"] = True
        chg(g, bonheur=15)
        return f"💍 {p['nom']} dit OUI ! Mariage somptueux."
    chg(g, bonheur=-10)
    p["relation"] = clamp(p["relation"] - 15)
    return f"😢 {p['nom']} refuse…"


@action("enfant")
def a_enfant(g):
    p = g["partenaire"]
    if not p or p["relation"] < 45 or not (18 <= g["age"] <= 50):
        raise Refus("👶 Il faut un·e partenaire stable (≥ 45) et avoir entre 18 et 50 ans.")
    if len(g["enfants"]) >= 5:
        raise Refus("👨‍👩‍👧‍👦 Ta famille est déjà bien grande !")
    if random.random() < 0.5:
        nom = random.choice(PRENOMS)
        g["enfants"].append({"nom": nom, "age": 0, "relation": 70, "influence_parent": 0})
        chg(g, bonheur=12)
        return f"👶 {nom} est né·e !"
    return "🤞 Pas de bébé cette année…"


@action("rompre")
def a_rompre(g):
    p = g["partenaire"]
    if not p:
        raise Refus("💞 Pas de partenaire.")
    if p["marie"]:
        perte = int(max(0, g["argent"]) * 0.35)
        g["argent"] -= perte
        txt = f"📄 Divorce avec {p['nom']} : −{fm(g, perte)}."
    else:
        txt = f"💔 Tu quittes {p['nom']}."
    g["partenaire"] = None
    g["famille_relations"] = clamp(g.get("famille_relations", 60) - 8)
    for ami in g.get("amis", []):
        ami["relation"] = clamp(ami.get("relation", 50) - 2)
    chg(g, bonheur=-8)
    return txt


@action("parents")
def a_parents(g):
    g["famille_relations"] = clamp(g.get("famille_relations", 60) + random.randint(7, 12))
    chg(g, bonheur=3, karma=1)
    return "📞 Tu passes du temps en famille : les liens se renforcent."


# --- Argent & risques
@action("casino")
def a_casino(g):
    mise = int(st.session_state["mise"])
    if mise <= 0 or mise > g["argent"]:
        raise Refus("🎰 Mise invalide (ou fonds insuffisants).")
    r = random.random()
    seuil = 0.55 if "Chanceux" in g["trait"] else 0.46
    if r < 0.02:
        g["argent"] += mise * 10
        return f"🎰 JACKPOT ! +{fm(g, mise * 10)} !"
    if r < seuil:
        g["argent"] += mise
        return f"🎰 Tu gagnes {fm(g, mise)} !"
    g["argent"] -= mise
    chg(g, bonheur=-3)
    return f"🎰 Tu perds {fm(g, mise)}…"


@action("bourse")
def a_bourse(g):
    mise = int(st.session_state["mise"])
    if mise <= 0 or mise > g["argent"]:
        raise Refus("📈 Montant invalide (ou fonds insuffisants).")
    f = max(-0.7, min(1.2, random.gauss(0.03, 0.25)))
    delta = int(mise * f)
    g["argent"] += delta
    return f"📈 Investissement : {'+' if delta >= 0 else ''}{fm(g, delta)} ({f:+.0%})."


@action("vol_etalage")
def a_vol(g):
    if g["age"] < 10:
        raise Refus("🚫 Trop jeune.")
    chg(g, karma=-5)
    if random.random() < 0.3:
        g["casier"] += 1
        g["argent"] -= 300
        chg(g, bonheur=-5)
        return "🚨 Pris·e la main dans le sac ! Amende de 300 + casier."
    gain = random.randint(20, 200)
    g["argent"] += gain
    return f"🕶️ Tu empoches l'équivalent de {fm(g, gain)}."


@action("cambriolage")
def a_cambriolage(g):
    if g["age"] < 16:
        raise Refus("🚫 Trop jeune.")
    p = 0.5 - g["stats"]["intelligence"] / 400 + (ville_info(g)["crime"] - 0.3) * -0.2
    chg(g, karma=-10)
    if random.random() < p:
        arrestation(g, random.randint(1, 3), "Tu es pris·e en flagrant délit !")
        return "🚔 Direction la prison."
    gain = random.randint(1500, 12000)
    g["argent"] += gain
    return f"🏚️ Cambriolage réussi : +{fm(g, gain)}."


@action("braquage")
def a_braquage(g):
    if g["age"] < 18:
        raise Refus("🚫 Réservé aux adultes (vraiment).")
    p = 0.7 - g["stats"]["intelligence"] / 300
    chg(g, karma=-20)
    if random.random() < p:
        arrestation(g, random.randint(4, 12), "Le braquage tourne mal !")
        return "🚔 Les sirènes retentissent…"
    gain = random.randint(40000, 250000)
    g["argent"] += gain
    return f"🏦 BRAQUAGE RÉUSSI : +{fm(g, gain)} !"


# --- Prison
@action("p_muscu", prison_ok=True)
def a_p_muscu(g):
    chg(g, force=random.randint(3, 6), apparence=1)
    return "💪 Tu fais des pompes dans ta cellule."


@action("p_etudes", prison_ok=True)
def a_p_etudes(g):
    chg(g, intelligence=random.randint(2, 4), karma=2)
    return "📚 Tu étudies à la bibliothèque de la prison."


@action("p_conduite", prison_ok=True)
def a_p_conduite(g):
    chg(g, karma=3)
    if random.random() < 0.25 and g["prison"] > 1:
        g["prison"] -= 1
        return "😇 Bonne conduite : peine réduite d'un an !"
    return "😇 Tu te fais discret·e. Le directeur note ton comportement."


@action("p_evasion", prison_ok=True)
def a_p_evasion(g):
    if random.random() < 0.08:
        g["prison"] = 0
        g["casier"] += 2
        chg(g, bonheur=10, karma=-10)
        return "🏃 ÉVASION RÉUSSIE ! Tu es libre (mais recherché·e)…"
    g["prison"] += 2
    chg(g, bonheur=-8)
    return "🚨 Évasion ratée : +2 ans de prison."


# ======================================================================
#  DÉFIS, MINI-BOUTIQUE ET HÉRITAGE DE GÉNÉRATION
# ======================================================================
BOUTIQUE = [
    {"id": "cape", "nom": "Cape héroïque", "emoji": "🦸", "prix": 30, "desc": "Une cape stylée pour ton avatar."},
    {"id": "lunettes", "nom": "Lunettes futuristes", "emoji": "🥽", "prix": 25, "desc": "Le look d'un génie masqué."},
    {"id": "couronne", "nom": "Couronne de légende", "emoji": "👑", "prix": 60, "desc": "+5 de célébrité à l'achat."},
    {"id": "porte_bonheur", "nom": "Porte-bonheur", "emoji": "🍀", "prix": 20, "desc": "+5 de karma à l'achat."},
    {"id": "kit_soins", "nom": "Kit de soins", "emoji": "🧰", "prix": 35, "desc": "+12 santé à l'achat."},
    {"id": "energie", "nom": "Boisson énergisante", "emoji": "⚡", "prix": 15, "desc": "+8 bonheur à l'achat."},
]
DEFIS = [
    {"id": "sport", "nom": "Prendre soin de soi", "desc": "Atteindre 60 en force", "recompense": 12, "test": lambda g: g["stats"]["force"] >= 60},
    {"id": "etudes", "nom": "Esprit brillant", "desc": "Atteindre 60 en intelligence", "recompense": 12, "test": lambda g: g["stats"]["intelligence"] >= 60},
    {"id": "karma", "nom": "Faire le bien", "desc": "Atteindre 65 en karma", "recompense": 15, "test": lambda g: g["stats"]["karma"] >= 65},
    {"id": "amitie", "nom": "Ami fidèle", "desc": "Avoir un ami avec 70 de relation", "recompense": 15, "test": lambda g: any(a.get("relation", 0) >= 70 for a in g.get("amis", []))},
    {"id": "famille", "nom": "Rester soudé", "desc": "Atteindre 75 de relation familiale", "recompense": 15, "test": lambda g: g.get("famille_relations", 0) >= 75},
    {"id": "fortune", "nom": "Premier pactole", "desc": "Posséder 10 000 en argent", "recompense": 18, "test": lambda g: g["argent"] >= 10000},
    {"id": "carriere", "nom": "Trouver sa voie", "desc": "Décrocher un métier", "recompense": 10, "test": lambda g: bool(g.get("metier"))},
    {"id": "heros", "nom": "Devenir une légende", "desc": "Atteindre 25 de célébrité", "recompense": 20, "test": lambda g: g["stats"]["celebrite"] >= 25},
]

def acheter_article(g, article_id):
    article = next((a for a in BOUTIQUE if a["id"] == article_id), None)
    if not article: raise Refus("Article introuvable.")
    if article_id in g.get("inventaire", []): raise Refus("Tu possèdes déjà cet article.")
    if g.get("jetons", 0) < article["prix"]: raise Refus(f"Il te manque {article['prix'] - g.get('jetons', 0)} jeton(s).")
    g["jetons"] -= article["prix"]
    g.setdefault("inventaire", []).append(article_id)
    if article_id == "couronne": chg(g, celebrite=5)
    elif article_id == "porte_bonheur": chg(g, karma=5)
    elif article_id == "kit_soins": chg(g, sante=12)
    elif article_id == "energie": chg(g, bonheur=8)
    log(g, f"🛍️ Achat : {article['nom']} (-{article['prix']} jetons).")

def reprendre_vie_enfant(g, index):
    if g.get("vivant") or not g.get("enfants"):
        return False
    if index < 0 or index >= len(g["enfants"]): return False
    parent = g
    enfant = parent["enfants"][index]
    lien = enfant.get("relation", 65)
    taux_heritage = 0.25 if lien < 20 else (0.45 if lien < 40 else 0.65)
    nouveau = defauts()
    nouveau.update(nom=enfant["nom"], genre=random.choice(["Garçon", "Fille", "Non-binaire"]), univers=parent["univers"],
                   ville=parent["ville"], age=enfant.get("age", 0), annee_naissance=datetime.now().year-enfant.get("age", 0),
                   argent=max(0, int(parent.get("argent", 0) * taux_heritage)), generation=parent.get("generation", 1)+1,
                   heritage_parent=parent.get("nom", ""), famille="héritage familial", fam=parent.get("fam", 1),
                   famille_relations=clamp(parent.get("famille_relations", 60)+5), amis=parent.get("amis", [])[:])
    nouveau["avatar"] = dict(parent.get("avatar", defauts()["avatar"]))
    nouveau["stats"] = {k: clamp(v + random.randint(-8, 8)) for k, v in parent.get("stats", {}).items()}
    nouveau["stats"]["sante"] = max(45, nouveau["stats"]["sante"])
    nouveau["stats"]["celebrite"] = max(0, nouveau["stats"]["celebrite"] // 2)
    nouveau["trait"] = random.choice(["Surdoué·e", "Athlète né·e", "Charismatique", "Chanceux·se", "Rebelle", "Courageux·se"])
    nouveau["journal"] = parent.get("journal", [])[:] + [[enfant.get("age", 0), f"🧬 Génération {nouveau['generation']} : {nouveau['nom']} reprend le flambeau de {parent['nom']}. Lien parent-enfant : {lien}/100. Héritage : {fm(nouveau, nouveau['argent'])}."]]
    if lien < 20:
        nouveau["journal"].append([nouveau["age"], "⚖️ Le lien était très abîmé : l'héritage reçu est réduit. Cette génération commence avec une relation familiale fragile."])
        nouveau["famille_relations"] = clamp(nouveau["famille_relations"] - 15)
    set_game(nouveau)
    sauver(nouveau)
    return True


# ======================================================================
#  CALLBACKS
# ======================================================================
def flash(msg):
    st.session_state["flash"] = msg


def run_action(aid, **kw):
    g = st.session_state["g"]
    fn, cout, prison_ok = ACTIONS[aid]
    if not g["vivant"]:
        return
    if g["evt"]:
        flash("⚠️ Règle d'abord l'événement en cours.")
        return
    if g["prison"] > 0 and not prison_ok:
        flash("⛓️ Impossible depuis la prison.")
        return
    if g["actions"] < cout:
        flash("⏳ Plus de temps libre cette année : passe à l'année suivante.")
        return
    try:
        txt = fn(g, **kw)
    except Refus as r:
        flash(str(r))
        return
    g["actions"] -= cout
    log(g, txt)
    flash(txt)
    if g["stats"]["sante"] <= 0 and g["vivant"]:
        mourir(g, "d'épuisement")
    maj_succes(g)
    if st.session_state.get("autosave"):
        sauver(g)


def next_year():
    g = st.session_state["g"]
    if g["evt"]:
        flash("⚠️ Règle d'abord l'événement en cours.")
        return
    passer_annee(g)
    flash(None)
    if st.session_state.get("autosave"):
        sauver(g)


def resolve_event(i):
    g = st.session_state["g"]
    e = EVENTS_BY_ID[g["evt"]["id"]]
    label, fn = e["choix"][i]
    g["evt"] = None
    txt = fn(g)
    g.setdefault("historique_choix", []).append({"age": g["age"], "evenement": e["titre"], "choix": label})
    log(g, f"📣 {e['titre']} — {label} → {txt}")
    flash(txt)
    if g["stats"]["sante"] <= 0 and g["vivant"]:
        mourir(g, "des suites de cet événement")
    maj_succes(g)
    if st.session_state.get("autosave"):
        sauver(g)


def claim_challenge(challenge_id):
    g = st.session_state["g"]
    d = next((x for x in DEFIS if x["id"] == challenge_id), None)
    if not d or challenge_id in g.get("defis_reclames", []): return
    if not d["test"](g):
        flash("🎯 Défi pas encore validé : continue ta progression !")
        return
    g.setdefault("defis_reclames", []).append(challenge_id)
    g["jetons"] = g.get("jetons", 0) + d["recompense"]
    log(g, f"🏅 Défi terminé : {d['nom']} (+{d['recompense']} jetons).")
    flash(f"🏅 Défi terminé ! +{d['recompense']} jetons.")
    if st.session_state.get("autosave"): sauver(g)

def buy_item(article_id):
    g = st.session_state["g"]
    try:
        acheter_article(g, article_id)
        flash("🛍️ Achat réussi !")
    except Refus as r:
        flash(str(r))
    if st.session_state.get("autosave"): sauver(g)

def inherit_child(index):
    if reprendre_vie_enfant(st.session_state["g"], index):
        flash("🧬 Nouvelle génération lancée ! L'histoire continue.")


def charger_slot(chemin):
    try:
        data = json.loads(Path(chemin).read_text(encoding="utf-8"))
        set_game(reparer(data))
    except Exception:
        flash("❌ Impossible de lire cette sauvegarde.")


def charger_upload():
    f = st.session_state.get("upl")
    if f is None:
        return
    try:
        set_game(reparer(json.loads(f.getvalue().decode("utf-8"))))
    except Exception:
        flash("❌ Fichier de sauvegarde invalide.")


def supprimer_slot(chemin):
    try:
        Path(chemin).unlink()
    except Exception:
        pass


def menu_principal():
    g = st.session_state.get("g")
    if g:
        sauver(g)
    st.session_state["g"] = None


def randomiser():
    s = st.session_state
    s["c_coupe"] = random.choice(COUPES)
    s["c_couleur"] = random.choice(list(HAIR_COLORS))
    s["c_peau"] = random.choice(list(SKINS))
    s["c_yeux"] = random.choice(YEUX)
    s["c_bouche"] = random.choice(BOUCHES)
    s["c_nom"] = random.choice(PRENOMS)
    s["c_genre"] = random.choice(["Garçon", "Fille", "Non-binaire"])


def creer_partie():
    s = st.session_state
    univ = s["c_univ"]
    av = {"coupe": s["c_coupe"], "couleur": s["c_couleur"], "peau": s["c_peau"], "yeux": s["c_yeux"], "bouche": s["c_bouche"]}
    g = new_game(s["c_nom"], s["c_genre"], univ, s[f"c_ville_{univ}"], av)
    set_game(g)
    sauver(g)


# ======================================================================
#  INTERFACE
# ======================================================================
CSS = """
<style>
.block-container {padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1500px;}
div[data-testid="stMetricValue"] {font-size: 1.35rem; font-weight: 750;}
[data-testid="stAppViewContainer"] {background: linear-gradient(135deg, #0b1020 0%, #111b35 55%, #17112b 100%);}
[data-testid="stHeader"] {background: transparent;}
[data-testid="stSidebar"] {background: linear-gradient(180deg, #111827, #1e1b4b);}
[data-testid="stVerticalBlockBorderWrapper"] {border-radius: 16px; border-color: #47556966;}
.stButton > button {border-radius: 11px; border: 1px solid #64748b88; transition: all .15s ease;}
.stButton > button:hover {border-color: #a78bfa; transform: translateY(-1px);}
button[kind="primary"] {background: linear-gradient(90deg, #7c3aed, #2563eb); border: 0;}
[data-testid="stProgressBar"] > div > div {background: linear-gradient(90deg, #06b6d4, #8b5cf6);}
h1, h2, h3 {letter-spacing: -.025em;}
</style>
"""


def ecran_accueil():
    st.title("🧬 MA VIE · LEGACY")
    st.caption("Une vie. Des choix. Des conséquences. Une histoire qui peut traverser les générations.")
    t1, t2 = st.tabs(["✨ Nouvelle vie", "📂 Charger une partie"])
    s = st.session_state
    for k, v in {"c_nom": "Alex", "c_genre": "Non-binaire", "c_univ": "real", "c_coupe": "Court", "c_couleur": "Noir",
                 "c_peau": "Beige", "c_yeux": "Ronds", "c_bouche": "Sourire"}.items():
        s.setdefault(k, v)
    with t1:
        c1, c2, c3 = st.columns([1.2, 1, 1])
        with c1:
            st.text_input("Prénom", key="c_nom")
            st.radio("Genre", ["Garçon", "Fille", "Non-binaire"], key="c_genre", horizontal=True)
            st.selectbox("Univers", list(UNIVERS), key="c_univ", format_func=lambda k: UNIVERS[k]["nom"])
            univ = s["c_univ"]
            st.caption(UNIVERS[univ]["desc"])
            villes = list(UNIVERS[univ]["villes"])
            st.selectbox("Ville de naissance", villes, key=f"c_ville_{univ}",
                         format_func=lambda v: f"{v} — {UNIVERS[univ]['villes'][v]['desc']}")
        with c2:
            st.selectbox("Coupe", COUPES, key="c_coupe")
            st.selectbox("Couleur de cheveux", list(HAIR_COLORS), key="c_couleur")
            st.selectbox("Teint", list(SKINS), key="c_peau")
            st.selectbox("Yeux", YEUX, key="c_yeux")
            st.selectbox("Bouche", BOUCHES, key="c_bouche")
        with c3:
            av = {"coupe": s["c_coupe"], "couleur": s["c_couleur"], "peau": s["c_peau"], "yeux": s["c_yeux"], "bouche": s["c_bouche"]}
            st.markdown(avatar_svg(av, 25, univ, taille=210), unsafe_allow_html=True)
            st.button("🎲 Aléatoire", on_click=randomiser, use_container_width=True)
        st.button("🚀 Commencer ma vie", on_click=creer_partie, type="primary", use_container_width=True)
    with t2:
        saves = lister_saves()
        if not saves:
            st.info("Aucune sauvegarde sur le disque. Tu peux aussi importer un fichier .json exporté.")
        for p, d in saves:
            j = JOBS.get(d.get("metier") or "", None)
            c1, c2, c3 = st.columns([4, 1, 1])
            c1.markdown(f"**{d.get('nom','?')}** — {d.get('age',0)} ans — {UNIVERS.get(d.get('univers'),{}).get('nom','?')} — "
                        f"{(j['nom'] if j else '—')} {'💀' if not d.get('vivant', True) else ''}  \n"
                        f"<small>Dernière sauvegarde : {d.get('maj','?')}</small>", unsafe_allow_html=True)
            c2.button("▶️ Charger", key=f"ld_{p.name}", on_click=charger_slot, args=(str(p),))
            c3.button("🗑️", key=f"rm_{p.name}", on_click=supprimer_slot, args=(str(p),))
        st.divider()
        st.file_uploader("Importer une sauvegarde (.json)", type="json", key="upl")
        st.button("📥 Charger ce fichier", on_click=charger_upload)
    if s.get("flash"):
        st.error(s["flash"])


def panneau_perso(g):
    j = JOBS.get(g["metier"]) if g["metier"] else None
    st.markdown(avatar_svg(g["avatar"], g["age"], g["univers"], j["emoji"] if j else "", 200), unsafe_allow_html=True)
    st.markdown(f"### {g['nom']}")
    st.caption(f"{g['age']} ans · {g['genre']} · {g['ville']} · {UNIVERS[g['univers']]['nom']}")
    st.caption(f"🧬 Génération {g.get('generation', 1)} · 🪙 {g.get('jetons', 0)} jetons")
    if g.get("heritage_parent"):
        st.caption(f"Héritage de {g['heritage_parent']}")
    st.markdown(f"**{titre_metier(g)}**")
    if g["prison"] > 0:
        st.error(f"⛓️ En prison ({g['prison']} an(s) restant(s))")
    st.metric("💰 Argent", fm(g, g["argent"]))
    for k in LABELS:
        label = LABELS[k] if k != "force" else UNIVERS[g["univers"]]["force"]
        st.progress(g["stats"][k] / 100, text=f"{ICONES[k]} {label} : {g['stats'][k]}")
    if g["en_ecole"]:
        st.caption(f"🏫 Notes : {g['notes']}/100")
    if g["etudes_en_cours"]:
        ec = g["etudes_en_cours"]
        st.caption(f"🎓 {ec['nom']} en {ec['domaine']} — {ec['restant']} an(s) restant(s) · notes {g['notes']}/100")


def bloc_evenement(g):
    e = EVENTS_BY_ID[g["evt"]["id"]]
    with st.container(border=True):
        st.subheader(f"📣 {e['titre']}")
        st.write(g["evt"]["texte"])
        cols = st.columns(len(e["choix"]))
        for i, (label, _fn) in enumerate(e["choix"]):
            cols[i].button(label, key=f"evt_{i}", on_click=resolve_event, args=(i,), use_container_width=True)


def btn(label, aid, key, disabled=False, **kw):
    st.button(label, key=key, on_click=run_action, args=(aid,), kwargs=kw, disabled=disabled, use_container_width=True)


def tab_etudes(g):
    if g["en_ecole"] or g["etudes_en_cours"]:
        st.write("Tes études en ce moment :")
        c1, c2, c3 = st.columns(3)
        with c1:
            btn("✏️ Étudier dur", "etudier", "b_etudier")
        with c2:
            btn("🛹 Sécher les cours", "secher", "b_secher", disabled=not g["en_ecole"])
        with c3:
            btn("📕 Arrêter (irréversible)", "arreter_ecole", "b_arreter")
    elif g["age"] >= 18 and g["edu"] in NIVEAUX_UNIV:
        nom, duree, _ = NIVEAUX_UNIV[g["edu"]]
        st.write(f"Tu peux t'inscrire en **{nom}** ({duree} ans, ~{fm(g, 1500 * ville_info(g)['cout'])}/an).")
        st.selectbox("Domaine", DOMAINES, key="f_domaine")
        btn(f"🎓 Candidater en {nom}", "inscrire", "b_inscrire")
    else:
        st.info("Aucune étude disponible pour l'instant." if g["age"] >= 6 else "Tu es encore bien trop petit·e !")
    st.caption(f"Diplôme actuel : {EDU_NOMS[g['edu']]}" + (f" · domaine : {g['domaine']}" if g["domaine"] else ""))


def tab_carriere(g):
    if g["age"] < 10:
        st.info("Reviens quand tu seras plus grand·e !")
        return
    if g["metier"]:
        j = JOBS[g["metier"]]
        st.success(f"Poste actuel : {titre_metier(g)} · {g['annees_metier']} an(s) · ~{fm(g, j['sal'] * j['mult'][g['grade']])}/an")
        c1, c2 = st.columns(2)
        with c1:
            btn("📈 Demander une promotion", "promotion", "b_promo")
        with c2:
            btn("👋 Démissionner", "demission", "b_demission")
    filtre = st.radio("Filtrer", ["Tous", "Jobs étudiants", "Métiers", "Métiers rares ✨"], horizontal=True, key="f_job")
    cats = {"Tous": None, "Jobs étudiants": "Job étudiant", "Métiers": "Métier", "Métiers rares ✨": "Métier rare"}[filtre]
    ouverts, verrouilles = [], []
    for key, j in JOBS.items():
        if j["univ"] != "all" and g["univers"] not in j["univ"]:
            continue
        if cats and j["cat"] != cats:
            continue
        (verrouilles if manques(g, key) else ouverts).append(key)

    def carte(key, ouvert):
        j = JOBS[key]
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**{j['emoji']} {j['nom']}** · _{j['cat']}_")
                st.caption(f"Salaire de départ ~{fm(g, j['sal'])}/an · {' → '.join(j['grades'])}"
                           + (" · 🚨 illégal" if j["crime"] else ""))
                if ouvert:
                    st.caption(f"🎯 Chances : {chance_embauche(g, key):.0%}")
                else:
                    st.caption("🔒 Il te faut : " + ", ".join(manques(g, key)))
            with c2:
                if ouvert:
                    btn("Postuler", "postuler", f"job_{key}", cle=key)

    for key in ouverts:
        carte(key, True)
    if not ouverts:
        st.info("Aucun poste disponible avec ce filtre pour l'instant.")
    if verrouilles:
        with st.expander(f"🔒 Postes verrouillés ({len(verrouilles)})"):
            for key in verrouilles:
                carte(key, False)


def tab_perso(g):
    c1, c2 = st.columns(2)
    ent = ENTRAINEMENTS[g["univers"]][0]
    with c1:
        btn("🏋️ Salle de sport", "gym", "b_gym")
        btn("📖 Lire un livre", "lire", "b_lire")
        btn("🧘 Méditer", "meditation", "b_med")
        btn("🤝 Bénévolat", "benevolat", "b_bene")
        btn(ent, "entrainement", "b_ent")
    with c2:
        btn("🎉 Faire la fête", "fete", "b_fete")
        btn("✈️ Voyager", "voyage", "b_voy")
        btn("🩺 Voir un médecin (150)", "medecin_visite", "b_doc")
        btn("💉 Chirurgie esthétique (8 000)", "chirurgie", "b_chir")
        btn("🏠 Prendre mon indépendance", "independance", "b_indep")
    st.divider()
    st.markdown("**💇 Coiffeur (40) — change ta coupe**")
    st.session_state.setdefault("coif_coupe", g["avatar"]["coupe"])
    st.session_state.setdefault("coif_couleur", g["avatar"]["couleur"])
    a, b = st.columns(2)
    a.selectbox("Coupe", COUPES, key="coif_coupe")
    b.selectbox("Couleur", list(HAIR_COLORS), key="coif_couleur")
    btn("💇 Changer de look", "coiffeur", "b_coif")
    st.markdown("**📦 Déménager**")
    villes = list(UNIVERS[g["univers"]]["villes"])
    st.session_state.setdefault("coif_ville", g["ville"])
    if st.session_state["coif_ville"] not in villes:
        st.session_state["coif_ville"] = g["ville"]
    st.selectbox("Nouvelle ville", villes, key="coif_ville")
    btn("📦 Déménager", "demenager", "b_dem")


def tab_amour(g):
    p = g["partenaire"]
    if p:
        st.success(f"{'💍 Marié·e à' if p['marie'] else '❤️ En couple avec'} **{p['nom']}** ({p['age']} ans) — relation {p['relation']}/100")
    else:
        st.info("Tu es célibataire.")
    for e in g["enfants"]:
        st.caption(f"👶 {e['nom']} ({e['age']} an{'s' if e['age'] > 1 else ''})")
    c1, c2 = st.columns(2)
    with c1:
        btn("💘 Rencontrer quelqu'un", "rencontrer", "b_renc", disabled=bool(p))
        btn("🥰 Passer du temps ensemble", "ensemble", "b_ens", disabled=not p)
        btn("🎁 Offrir un cadeau (200)", "cadeau", "b_cad", disabled=not p)
        btn("📞 Voir la famille", "parents", "b_par")
    with c2:
        btn("💍 Demander en mariage (3 000)", "mariage", "b_mar", disabled=not p or p["marie"])
        btn("👶 Essayer d'avoir un enfant", "enfant", "b_enf", disabled=not p)
        btn("💔 Rompre / divorcer", "rompre", "b_romp", disabled=not p)


def tab_argent(g):
    st.markdown(f"Solde : **{fm(g, g['argent'])}**")
    mx = int(max(10, min(max(g["argent"], 10), 200000)))
    if st.session_state.get("mise", 0) > mx:
        st.session_state["mise"] = mx
    st.slider("Montant engagé", 0, mx, min(100, mx), key="mise")
    c1, c2 = st.columns(2)
    with c1:
        btn("🎰 Casino", "casino", "b_cas", disabled=g["age"] < 18)
    with c2:
        btn("📈 Investir en bourse", "bourse", "b_bou", disabled=g["age"] < 18)
    st.divider()
    st.markdown("**🕶️ Le côté obscur** (karma ↓, prison possible)")
    c1, c2, c3 = st.columns(3)
    with c1:
        btn("🛍️ Vol à l'étalage", "vol_etalage", "b_vol")
    with c2:
        btn("🏚️ Cambriolage", "cambriolage", "b_camb")
    with c3:
        btn("🏦 Braquage de banque", "braquage", "b_braq")


def tab_defis_boutique(g):
    st.markdown(f"### 🏅 Défis & récompenses  ·  **🪙 {g.get('jetons', 0)} jetons**")
    st.caption("Les jetons sont une monnaie fictive : termine les défis une seule fois par personnage pour les dépenser ici.")
    st.markdown("#### Défis disponibles")
    for d in DEFIS:
        done = d["id"] in g.get("defis_reclames", [])
        ok = d["test"](g)
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"**{'✅' if done else '🎯' if ok else '🔒'} {d['nom']}**")
                st.caption(d["desc"] + f" · Récompense : 🪙 {d['recompense']}")
            with c2:
                if done: st.button("Réclamé", key=f"defi_{d['id']}", disabled=True, use_container_width=True)
                else: st.button("Réclamer", key=f"defi_{d['id']}", on_click=claim_challenge, args=(d["id"],), disabled=not ok, use_container_width=True)
    st.divider()
    st.markdown("#### 🛍️ Mini-boutique")
    cols = st.columns(3)
    for i, article in enumerate(BOUTIQUE):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"### {article['emoji']} {article['nom']}")
                st.caption(article["desc"])
                st.markdown(f"**🪙 {article['prix']} jetons**")
                owned = article["id"] in g.get("inventaire", [])
                st.button("Déjà acheté" if owned else "Acheter", key=f"shop_{article['id']}", on_click=buy_item, args=(article["id"],), disabled=owned or g.get("jetons", 0) < article["prix"], use_container_width=True)
    if g.get("inventaire"):
        st.caption("Dans ton inventaire : " + ", ".join(next(a["emoji"]+" "+a["nom"] for a in BOUTIQUE if a["id"] == i) for i in g["inventaire"]))

def tab_relations(g):
    st.markdown("### 👨‍👩‍👧‍👦 Famille & entourage")
    rel = g.get("famille_relations", 60)
    st.progress(rel / 100, text=f"Lien avec ta famille : {rel}/100")
    st.caption("Tes liens évoluent avec le temps et tes choix. Une relation faible peut rendre les moments difficiles plus durs.")
    if g.get("amis"):
        for ami in g["amis"]:
            st.progress(ami.get("relation", 50) / 100, text=f"🫂 {ami['nom']} · amitié {ami.get('relation', 50)}/100")
    else:
        st.info("Tu n'as pas encore d'ami proche.")
    if g.get("partenaire"):
        st.progress(g["partenaire"].get("relation", 50) / 100, text=f"❤️ {g['partenaire']['nom']} · couple {g['partenaire'].get('relation', 50)}/100")
    if g.get("enfants"):
        st.markdown("#### Enfants et héritiers")
        for e in g["enfants"]:
            st.caption(f"🧒 {e['nom']} · {e['age']} ans · lien {e.get('relation', 65)}/100" + (" · relation fragile" if e.get("relation", 65) < 35 else ""))


def tab_prison(g):
    st.error(f"⛓️ Tu es en prison : {g['prison']} an(s) restant(s).")
    c1, c2 = st.columns(2)
    with c1:
        btn("💪 Muscu en cellule", "p_muscu", "b_pm")
        btn("📚 Étudier", "p_etudes", "b_pe")
    with c2:
        btn("😇 Bonne conduite", "p_conduite", "b_pc")
        btn("🏃 Tenter une évasion (8 %)", "p_evasion", "b_pv")


def tab_journal(g):
    with st.container(height=520):
        courant = None
        for age, txt in reversed(g["journal"][-250:]):
            if age != courant:
                st.markdown(f"##### Âge {age}")
                courant = age
            st.markdown(f"- {txt}")


def tab_profil(g):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Famille d'origine :** {g['famille']}")
        st.markdown(f"**Trait :** {g['trait']}")
        st.markdown(f"**Diplôme :** {EDU_NOMS[g['edu']]}")
        st.markdown(f"**Casier judiciaire :** {g['casier']} condamnation(s)")
        if g["retraite"]:
            st.markdown(f"**Pension :** {fm(g, g['retraite'])}/an")
        if g["historique_metiers"]:
            st.markdown("**Anciens métiers :** " + ", ".join(g["historique_metiers"]))
    with c2:
        st.markdown(f"**🏆 Succès ({len(g['succes'])})**")
        for s in g["succes"]:
            st.markdown(f"- {s}")
        if not g["succes"]:
            st.caption("Aucun pour l'instant…")
        st.markdown("**🧭 Conséquences de tes choix**")
        hero_jobs = ("heros_pro", "justicier_armure", "tisseur_urbain", "heros_energie", "metamorphe", "telepathe", "chasseur_anomalies", "gardien_dimension", "heroine_soins")
        if g.get("identite_secrete", True) and g.get("metier") in hero_jobs:
            st.caption(f"Identité héroïque protégée · suspicion {g.get('suspicion', 0)}/100")
        elif not g.get("identite_secrete", True):
            st.caption("⚠️ Identité héroïque publique : tes proches peuvent subir les retombées.")
        st.caption(f"Réputation : {g.get('reputation', 50)}/100 · Génération : {g.get('generation', 1)}")
        if g.get("enfants_eloignes"):
            st.warning("Liens familiaux rompus : " + ", ".join(g["enfants_eloignes"]))
        if g.get("historique_choix"):
            with st.expander("Voir les décisions marquantes"):
                for choix in g["historique_choix"][-20:]:
                    st.write(f"Âge {choix['age']} · **{choix['evenement']}** — {choix['choix']}")


def bloc_mort(g):
    st.error(f"💀 {g['nom']} est mort·e à {g['age']} ans, {g['cause']}.")
    st.markdown(f"**Dernier métier :** {titre_metier(g)} · **Fortune :** {fm(g, g['argent'])} · "
                f"**Enfants :** {len(g['enfants'])} · **Succès :** {len(g['succes'])}")
    if g.get("enfants"):
        st.markdown("### 🧬 L'histoire peut continuer")
        st.write("Choisis l'un de tes enfants pour prendre sa place. Tu garderas une partie de l'héritage et tu commenceras une nouvelle génération.")
        for i, enfant in enumerate(g["enfants"]):
            st.button(f"👑 Continuer avec {enfant['nom']} ({enfant['age']} ans)", key=f"heritier_{i}", on_click=inherit_child, args=(i,), type="primary", use_container_width=True)
    st.button("🔄 Nouvelle vie", on_click=menu_principal, type="secondary")


def sidebar(g):
    sb = st.sidebar
    sb.header("💾 Sauvegarde")
    sb.checkbox("Sauvegarde auto (disque)", key="autosave", value=True)
    if sb.button("Sauvegarder maintenant", use_container_width=True):
        sb.success("Sauvegardé ✅" if sauver(g) else "Écriture disque impossible : utilise l'export.")
    sb.download_button("⬇️ Exporter (.json)", data=json.dumps(g, ensure_ascii=False, indent=1),
                       file_name=f"ma_vie_{g['nom']}_{g['age']}ans.json", mime="application/json", use_container_width=True)
    sb.caption("Sur Streamlit Cloud le disque est temporaire : exporte ta partie pour la garder.")
    sb.button("🏠 Menu principal", on_click=menu_principal, use_container_width=True)


def ecran_jeu(g):
    sidebar(g)
    gauche, droite = st.columns([1, 2.4])
    with gauche:
        panneau_perso(g)
    with droite:
        msg = st.session_state.get("flash")
        if msg:
            st.info(msg)
        if not g["vivant"]:
            bloc_mort(g)
        else:
            if g["evt"]:
                bloc_evenement(g)
            c1, c2 = st.columns([2, 1])
            c1.button("➡️ ANNÉE SUIVANTE", on_click=next_year, type="primary", use_container_width=True, disabled=bool(g["evt"]))
            c2.metric("⏳ Temps libre", f"{g['actions']}/{ACTIONS_PAR_AN}")
        tabs = st.tabs(["🎯 Actions", "🏅 Défis & boutique", "👥 Relations", "📜 Journal", "🪪 Profil"])
        with tabs[0]:
            if not g["vivant"]:
                st.caption("Plus d'actions possibles…")
            elif g["prison"] > 0:
                tab_prison(g)
            else:
                sous = st.tabs(["🎓 Études", "💼 Carrière", "🏃 Vie perso", "❤️ Amour & famille", "💰 Argent & risques"])
                with sous[0]:
                    tab_etudes(g)
                with sous[1]:
                    tab_carriere(g)
                with sous[2]:
                    tab_perso(g)
                with sous[3]:
                    tab_amour(g)
                with sous[4]:
                    tab_argent(g)
        with tabs[1]:
            tab_defis_boutique(g)
        with tabs[2]:
            tab_relations(g)
        with tabs[3]:
            tab_journal(g)
        with tabs[4]:
            tab_profil(g)


def main():
    st.set_page_config(page_title="Ma Vie — Simulateur de vie", page_icon="🧬", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    st.session_state.setdefault("g", None)
    g = st.session_state["g"]
    if g is None:
        ecran_accueil()
    else:
        ecran_jeu(g)


if __name__ == "__main__":
    main()
