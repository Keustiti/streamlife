# -*- coding: utf-8 -*-
"""
🧬 MA VIE — Simulateur de vie façon BitLife (Streamlit)

Lancer :   pip install streamlit
           streamlit run ma_vie.py

Fonctionnalités : création de personnage (coupe, visage, peau, yeux...), 3 univers
(réel, manga, fantasy) avec leurs villes, études, jobs étudiants, métiers
classiques et rares (acteur, rappeur, streameur, ninja, bandit...), amour, enfants,
crime & prison, événements aléatoires à choix, succès, sauvegardes (disque + export JSON).
"""
import json
import html
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
            "Village du Sable 🏜️": {"cout": 0.9, "crime": 0.25, "desc": "Suna : marionnettistes, Kazekage et tempêtes de sable."},
            "Village de la Brume 🌫️": {"cout": 0.95, "crime": 0.35, "desc": "Kiri : épéistes, secrets et missions périlleuses."},
            "Village de la Foudre ⚡": {"cout": 1.0, "crime": 0.3, "desc": "Kumo : ninjas rapides et puissance électrique."},
            "Village de la Roche 🪨": {"cout": 0.9, "crime": 0.25, "desc": "Iwa : techniques de terre et rivalités anciennes."},
            "Village de la Pluie 🌧️": {"cout": 0.8, "crime": 0.55, "desc": "Ame : espions, conflits et alliances fragiles."},
            "Village du Son 🎵": {"cout": 0.85, "crime": 0.6, "desc": "Oto : expériences interdites et ninjas déserteurs."},
            "Tokyo – École d'exorcisme 👁️": {"cout": 1.2, "crime": 0.35, "desc": "Jujutsu : fléaux, énergie occulte et exorcistes."},
            "Kyoto – École d'exorcisme 🏯": {"cout": 1.0, "crime": 0.25, "desc": "Une école rivale où la tradition compte autant que la force."},
            "Grand Line – Port libre 🏴‍☠️": {"cout": 1.0, "crime": 0.6, "desc": "Pirates, fruits du démon et chasseurs de primes."},
            "Marineford ⚓": {"cout": 1.1, "crime": 0.25, "desc": "La grande base de la Marine, où se décide l'équilibre des mers."},
            "Baltigo – Île rebelle 🔥": {"cout": 0.85, "crime": 0.65, "desc": "Un refuge de révolutionnaires et de dissidents."},
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
add("heros_pro", "Héros professionnel", "🦸", 15, 0, 30000, RA, ["real", "manga"], chance=0.2, atouts=["force", "karma"], statmin=("force", 60),
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
add("justicier_armure", "Justicier·ère en armure", "🦾", 18, 2, 52000, RA, ["real", "manga"], chance=0.16, atouts=["intelligence", "force"], statmin=("intelligence", 60), grades=["Prototype secret", "Protecteur urbain", "Sentinelle nationale", "Légende blindée"], mult=[1, 2, 5, 14], risque=0.08, fame=3)
add("tisseur_urbain", "Héros·ïne tisseur·se urbain·e", "🕸️", 16, 0, 36000, RA, ["real", "manga", "cyber"], chance=0.22, atouts=["force", "karma"], statmin=("force", 55), grades=["Vigilant de quartier", "Sauveur des toits", "Protecteur de la ville", "Mythe urbain"], mult=[1, 2, 4, 11], risque=0.09, fame=3)
add("heros_energie", "Héros·ïne à énergie cosmique", "☄️", 18, 0, 60000, RA, ["real", "manga"], chance=0.12, atouts=["force", "sante"], statmin=("force", 75), grades=["Éveillé·e", "Gardien·ne solaire", "Défenseur·se planétaire", "Légende cosmique"], mult=[1, 2, 6, 18], risque=0.12, fame=5)
add("metamorphe", "Métamorphe / change-forme", "🦎", 15, 0, 30000, RA, ["real", "manga", "cyber"], chance=0.2, atouts=["apparence", "intelligence"], grades=["Pouvoir instable", "Agent secret", "Héros reconnu", "Maître des formes"], mult=[1, 2, 4, 12], risque=0.06, fame=3)
add("telepathe", "Télépathe protecteur·rice", "🧠", 16, 0, 34000, RA, ["real", "manga"], chance=0.18, atouts=["intelligence", "karma"], statmin=("intelligence", 65), grades=["Esprit éveillé", "Médiateur mental", "Bouclier psychique", "Gardien des consciences"], mult=[1, 2, 5, 13], risque=0.05, fame=3)
add("chasseur_anomalies", "Chasseur·se d'anomalies", "🌀", 18, 0, 42000, RA, ["real", "fantasy", "manga"], chance=0.2, atouts=["force", "intelligence"], grades=["Recrue", "Intervenant·e", "Chef·fe d'unité", "Légende du paranormal"], mult=[1, 2, 5, 12], risque=0.1, fame=3)
add("inventeur_gadgets", "Inventeur·rice de gadgets héroïques", "🛠️", 18, 4, 48000, RA, ["real", "cyber", "manga"], chance=0.2, atouts=["intelligence"], statmin=("intelligence", 65), grades=["Bricoleur·se", "Génie indépendant", "Fournisseur des héros", "Architecte de légendes"], mult=[1, 2, 5, 15], risque=0.04, fame=2)
add("gardien_dimension", "Gardien·ne des dimensions", "🪄", 20, 0, 50000, RA, ["real", "manga", "fantasy"], chance=0.12, atouts=["intelligence", "karma"], statmin=("intelligence", 70), grades=["Apprenti·e du portail", "Sentinelle dimensionnelle", "Maître des failles", "Gardien·ne éternel·le"], mult=[1, 2, 6, 18], risque=0.1, fame=4)
add("heroine_soins", "Héros·ïne aux pouvoirs régénérants", "💚", 16, 0, 32000, RA, ["real", "manga", "fantasy"], chance=0.22, atouts=["sante", "karma"], grades=["Secouriste masqué·e", "Guérisseur·se de terrain", "Sauveur·se national·e", "Phare d'espoir"], mult=[1, 2, 4, 10], risque=0.04, fame=3)



# Carrières de haut niveau dans l'univers manga. Les rangs se débloquent par mérite.
add("anbu", "Membre de l'ANBU", "🎭", 18, 2, 42000, "Métier rare", univ=M, chance=0.28,
    atouts=["force", "intelligence"], statmin=("force", 60),
    grades=["Recrue ANBU", "Opérateur", "Chef d'équipe", "Commandant ANBU"], mult=[1, 1.7, 2.8, 4.5], risque=0.12, fame=2)
add("sensei_ninja", "Sensei ninja", "🍃", 22, 2, 38000, "Métier", univ=M, chance=0.55,
    atouts=["intelligence"], statmin=("intelligence", 55),
    grades=["Instructeur", "Sensei", "Maître d'équipe", "Directeur d'académie"], mult=[1, 1.5, 2.3, 3.5], fame=1)
add("kage", "Kage du village", "影", 28, 2, 85000, "Métier rare", univ=M, chance=0.03,
    atouts=["force", "intelligence", "karma"], statmin=("force", 80),
    grades=["Candidat", "Conseiller", "Kage", "Légende des villages"], mult=[1, 1.5, 2.5, 4], risque=0.08, fame=5)
add("medecin_ninja", "Médecin ninja", "🩺", 18, 2, 39000, "Métier", univ=M, chance=0.55,
    atouts=["intelligence"], statmin=("intelligence", 60),
    grades=["Apprenti médical", "Ninja médecin", "Chef d'unité médicale", "Maître guérisseur"], mult=[1, 1.5, 2.4, 3.8], fame=1)
add("ninja_chercheur", "Chercheur en techniques", "📜", 18, 3, 41000, "Métier", univ=M, chance=0.45,
    atouts=["intelligence"], statmin=("intelligence", 65),
    grades=["Assistant", "Chercheur", "Maître des sceaux", "Directeur de recherche"], mult=[1, 1.6, 2.5, 4], fame=1)

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
        elif k == "chakra":
            g["chakra"] = clamp(g.get("chakra", 50) + v)
        elif k == "bijuu_maitrise":
            g["bijuu_maitrise"] = max(0, min(100, g.get("bijuu_maitrise", 0) + v))
        elif k == "famille_relations":
            g["famille_relations"] = clamp(g.get("famille_relations", 60) + v)
        elif k == "reputation":
            g["reputation"] = clamp(g.get("reputation", 50) + v)
        elif k == "performance_metier":
            g["performance_metier"] = clamp(g.get("performance_metier", 0) + v)
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
           f'<defs><linearGradient id="bg-{univ}" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="{body}" stop-opacity=".95"/><stop offset="100%" stop-color="#111827" stop-opacity=".95"/></linearGradient>'
           f'<linearGradient id="skin-{univ}" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#ffffff" stop-opacity=".28"/><stop offset="100%" stop-color="#000000" stop-opacity=".12"/></linearGradient>'
           f'<linearGradient id="shirt-{univ}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{body}"/><stop offset="100%" stop-color="#111827"/></linearGradient></defs>'
           f'<circle cx="100" cy="110" r="98" fill="url(#bg-{univ})" stroke="#ffffff" stroke-opacity=".18" stroke-width="2"/>'
           f'<circle cx="100" cy="110" r="88" fill="none" stroke="#ffffff" stroke-opacity=".10" stroke-dasharray="3 7"/>'
           f'<g transform="translate(100 225) scale({s}) translate(-100 -225)">'
           f'{back}<circle cx="43" cy="108" r="10" fill="{skin}"/><circle cx="157" cy="108" r="10" fill="{skin}"/>'
           f'<path d="M20 225 Q30 168 100 165 Q170 168 180 225Z" fill="url(#shirt-{univ})" stroke="#ffffff" stroke-opacity=".12" stroke-width="2"/>'
           f'<path d="M67 177 L100 205 L133 177" fill="none" stroke="#ffffff" stroke-opacity=".3" stroke-width="3"/>'
           f'<rect x="82" y="148" width="36" height="30" rx="8" fill="{skin}"/>'
           f'<circle cx="100" cy="105" r="58" fill="{skin}" stroke="#ffffff" stroke-opacity=".24" stroke-width="2"/>'
           f'<circle cx="100" cy="105" r="57" fill="url(#skin-{univ})"/>'
           f'<ellipse cx="65" cy="125" rx="9" ry="4" fill="#fb7185" opacity=".18"/><ellipse cx="135" cy="125" rx="9" ry="4" fill="#fb7185" opacity=".18"/>'
           f'<path d="M88 74 Q100 68 112 74" fill="none" stroke="#ffffff" stroke-opacity=".24" stroke-width="3" stroke-linecap="round"/>'
           f'{wrinkles}{brows}{eyes}{nose}{mouth}{front}</g>'
           f'<circle cx="100" cy="190" r="7" fill="#ffffff" opacity=".12"/><path d="M89 190 L100 202 L111 190" fill="none" stroke="#ffffff" stroke-opacity=".4" stroke-width="2"/>{badge_svg}</svg>')
    return f'<div style="text-align:center; animation:float-avatar 4s ease-in-out infinite">{svg}</div>'


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
            "journal": [], "evt": None, "vivant": True, "cause": "", "succes": [], "historique_metiers": [], "jetons": 0, "inventaire": [], "inventaire_objets": [], "defis_reclames": [],
            "amis": [], "famille_relations": 65, "reputation": 50, "generation": 1, "heritage_parent": "",
            "parents": [], "fratrie": [], "relation_parents": 70,
            "origine_heroique": "Aucune", "performance_metier": 0, "taches_metier": 0, "recompense_vie": False,
            "identite_secrete": True, "suspicion": 0, "enfants_eloignes": [], "historique_choix": [],
            "consequences_differees": [], "chronologie_famille": [], "rivalites": [],
            "pouvoirs": [], "niveau_pouvoir": 0, "reputation_heroique": 0,
            "chakra": 50, "jutsu": [], "rang_ninja": "Aspirant", "victoires_combat": 0, "clan": "", "bijuu": "", "bijuu_maitrise": 0, "sharingans_voles": 0, "akatsuki": False, "ami_vexe": None,
            "faction_manga": "Indépendant·e", "notoriete_manga": 0, "fruit_demon": "",
            "energie_occulte": 0, "techniques_maudites": [], "agence_heros": "",
            "faction_fantasy": "Aucune", "renommee_fantasy": 0, "statut_ninja": "Village",
            "armure_niveau": 0, "entrainement_heroique": 0, "radio_lue": [], "journal_actualites": [], "secrets": [],
            "actualites_monde": [], "etat_monde": {}, "monnaie_monde": "Euro", "alliance_monde": [],
            "missions_reussies": 0, "missions_echouees": 0, "progression_grade": 0, "performance_metier": 35, "succes_reclames": [], "evenements_vus": [],
            "prix_marche": {}, "objets_uniques": [], "titres": [], "prime_recherchee": 0, "marche_noir_debloque": False, "coffres_ouverts": 0,
            "maj": ""}


def new_game(nom, genre, univers, ville, av):
    g = defauts()
    g.update(nom=nom.strip() or "Alex", genre=genre, univers=univers, ville=ville, avatar=av)
    if univers == "manga":
        g["saga_manga"] = (
            "jujutsu" if "exorcisme" in ville.lower() else
            "onepiece" if any(x in ville.lower() for x in ("grand line", "marineford", "baltigo", "port libre")) else
            "naruto"
        )
        g["clan"] = random.choices(
            ["Uchiha", "Hyûga", "Senju", "Uzumaki", "Nara", "Akimichi", "Aburame", "Sans clan"],
            [0.10, 0.12, 0.10, 0.16, 0.12, 0.12, 0.10, 0.18]
        )[0]
        if g["clan"] == "Uchiha":
            g["jutsu"] = ["Sharingan"]
        elif g["clan"] == "Hyûga":
            g["jutsu"] = ["Byakugan"]
        if g.get("saga_manga") != "naruto":
            g["clan"] = "Sans clan"
            g["jutsu"] = []
    famille = random.choices(["modeste", "classe moyenne", "aisée"], [0.35, 0.5, 0.15])[0]
    g["famille"], g["fam"] = famille, {"modeste": 0, "classe moyenne": 1, "aisée": 2}[famille]
    noms_disponibles = [n for n in PRENOMS if n != g["nom"]]
    p1, p2 = random.sample(noms_disponibles, 2)
    age_parent = random.randint(22, 38)
    g["parents"] = [
        {"nom": p1, "role": "Mère", "age": age_parent, "relation": random.randint(55, 90), "vivant": True,
         "personnalite": random.choice(["Protectrice", "Exigeante", "Drôle", "Réservée", "Ambitieuse", "Très affectueuse"]), "confiance": random.randint(45, 85)},
        {"nom": p2, "role": "Père", "age": age_parent + random.randint(-3, 5), "relation": random.randint(55, 90), "vivant": True,
         "personnalite": random.choice(["Protecteur", "Exigeant", "Drôle", "Réservé", "Ambitieux", "Très affectueux"]), "confiance": random.randint(45, 85)},
    ]
    nb_fratrie = random.choices([0, 1, 2, 3], [0.30, 0.40, 0.22, 0.08])[0]
    g["fratrie"] = [{"nom": random.choice([n for n in PRENOMS if n not in [g["nom"], p1, p2]]),
                     "age": random.randint(0, 12), "relation": random.randint(45, 85)} for _ in range(nb_fratrie)]
    S = g["stats"]
    for k in ("sante", "bonheur"):
        S[k] = random.randint(55, 95)
    for k in ("intelligence", "apparence", "force"):
        S[k] = random.randint(25, 85)
    g["trait"] = random.choice(["Surdoué·e", "Athlète né·e", "Charismatique", "Chanceux·se", "Rebelle", "Courageux·se"])
    amis_noms = random.sample([n for n in PRENOMS if n != g["nom"] and n not in [p1, p2]], 2)
    g["amis"] = [{"nom": n, "relation": random.randint(45, 75),
                   "personnalite": random.choice(["Loyal·e", "Drôle", "Compétitif·ve", "Sensible", "Ambitieux·se"]),
                   "statut": "ami·e", "confiance": random.randint(40, 80), "souvenirs": []} for n in amis_noms]
    boost = {"Surdoué·e": ("intelligence", 15), "Athlète né·e": ("force", 15), "Charismatique": ("apparence", 15),
             "Courageux·se": ("sante", 8), "Rebelle": ("karma", -10), "Chanceux·se": ("bonheur", 8)}[g["trait"]]
    S[boost[0]] = clamp(S[boost[0]] + boost[1])
    g["notes"] = clamp(S["intelligence"] + random.randint(-10, 10))
    ne = "née" if genre == "Fille" else "né"
    log(g, f"👶 Tu es {ne} à {ville} ({UNIVERS[univers]['nom']}), dans une famille {famille}. Trait : {g['trait']}.")
    log(g, f"👨‍👩‍👧 Tes parents sont {g['parents'][0]['nom']} ({g['parents'][0]['role']}, {g['parents'][0]['personnalite'].lower()}) et {g['parents'][1]['nom']} ({g['parents'][1]['role']}, {g['parents'][1]['personnalite'].lower()}).")
    if g.get("fratrie"):
        log(g, "🧑‍🤝‍🧑 Tu as aussi " + ", ".join(f"{x['nom']} ({x['age']} ans)" for x in g["fratrie"]) + ".")
    if univers == "manga":
        log(g, f"🌏 Ton destin commence dans la saga {g['saga_manga'].upper()} : les rencontres et les choix pourront te faire changer de voie.")
    maj_succes(g)
    return g


def reparer(data):
    """Complète une ancienne sauvegarde avec les champs manquants."""
    g = defauts()
    stats = {**g["stats"], **data.get("stats", {})}
    g.update(data)
    g["stats"] = stats
    # Migration des anciennes sauvegardes : l'univers cyberpunk a été retiré.
    if g.get("univers") == "cyber":
        g["univers"] = "real"
        g["ville"] = "Paris"
        g.setdefault("journal", []).append([g.get("age", 0), "🔄 Ancienne partie cyberpunk convertie vers le monde réel."])
    g.setdefault("origine_heroique", "Aucune")
    g.setdefault("faction_manga", "Indépendant·e")
    g.setdefault("notoriete_manga", 0)
    g.setdefault("fruit_demon", "")
    g.setdefault("energie_occulte", 0)
    g.setdefault("techniques_maudites", [])
    g.setdefault("agence_heros", "")
    g.setdefault("faction_fantasy", "Aucune")
    g.setdefault("renommee_fantasy", 0)
    g.setdefault("statut_ninja", "Village")
    g.setdefault("actualites_monde", [])
    g.setdefault("etat_monde", {})
    g.setdefault("monnaie_monde", "Euro" if g.get("univers") == "real" else "Ryō" if g.get("univers") == "manga" else "Couronne")
    g.setdefault("alliance_monde", [])
    g.setdefault("inventaire_objets", [])
    g.setdefault("missions_reussies", 0)
    g.setdefault("missions_echouees", 0)
    g.setdefault("progression_grade", 0)
    g.setdefault("prix_marche", {})
    g.setdefault("objets_uniques", [])
    g.setdefault("titres", [])
    g.setdefault("prime_recherchee", 0)
    g.setdefault("marche_noir_debloque", False)
    g.setdefault("coffres_ouverts", 0)
    g.setdefault("performance_metier", 35)
    g.setdefault("succes_reclames", [])
    g.setdefault("evenements_vus", [])
    g.setdefault("clan", "")
    g.setdefault("bijuu", "")
    g.setdefault("bijuu_maitrise", 0)
    g.setdefault("sharingans_voles", 0)
    g.setdefault("akatsuki", False)
    g.setdefault("ami_vexe", None)
    if g.get("univers") == "manga" and not g.get("saga_manga"):
        ville = g.get("ville", "")
        g["saga_manga"] = "jujutsu" if "exorcisme" in ville.lower() else "onepiece" if any(x in ville.lower() for x in ("grand line", "marineford", "baltigo", "port libre")) else "naruto"
    g.setdefault("chakra", 50)
    g.setdefault("jutsu", [])
    g.setdefault("rang_ninja", "Aspirant")
    g.setdefault("victoires_combat", 0)
    g.setdefault("armure_niveau", 0)
    g.setdefault("entrainement_heroique", 0)
    g.setdefault("radio_lue", [])
    g.setdefault("journal_actualites", [])
    g.setdefault("performance_metier", 0)
    g.setdefault("taches_metier", 0)
    g.setdefault("taches_metier", 0)
    g["avatar"] = {**defauts()["avatar"], **data.get("avatar", {})}
    for key in ("parents", "fratrie", "amis", "enfants", "historique_choix", "enfants_eloignes", "inventaire", "defis_reclames", "consequences_differees", "chronologie_famille", "rivalites", "pouvoirs", "secrets"):
        g.setdefault(key, [])
    g.setdefault("niveau_pouvoir", 0)
    g.setdefault("reputation_heroique", 0)
    for personne in g.get("amis", []):
        personne.setdefault("personnalite", "Loyal·e")
        personne.setdefault("statut", "ami·e")
        personne.setdefault("confiance", personne.get("relation", 50))
        personne.setdefault("souvenirs", [])
    for personne in g.get("parents", []) + g.get("fratrie", []):
        personne.setdefault("personnalite", "Bienveillant·e")
        personne.setdefault("confiance", personne.get("relation", 60))
    for parent in g.get("parents", []):
        parent.setdefault("vivant", True)
        parent.setdefault("relation", 65)
    for enfant in g.get("enfants", []):
        enfant.setdefault("relation", 65)
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


# Métiers/factions supplémentaires de l'univers manga.
add("marine", "Officier·ère de la Marine", "⚓", 16, 0, 18000, RA, M, chance=0.45,
    atouts=["force", "karma"], grades=["Recrue", "Lieutenant·e", "Vice-amiral·e", "Amiral·e"], mult=[1, 2, 5, 12], fame=2)
add("revolutionnaire", "Combattant·e révolutionnaire", "🔥", 16, 0, 14000, RA, M, chance=0.42,
    atouts=["force", "intelligence"], grades=["Recrue", "Agent·e", "Commandant·e", "Chef·fe révolutionnaire"], mult=[1, 2, 5, 12], risque=0.12, fame=3)
add("exorciste_jujutsu", "Exorciste de Jujutsu", "👁️", 15, 0, 22000, RA, M, chance=0.4,
    atouts=["force", "intelligence"], grades=["Élève", "Exorciste de grade 2", "Grade 1", "Spécial"], mult=[1, 2, 5, 14], risque=0.12, fame=3)
add("chasseur_primes", "Chasseur·se de primes", "🎯", 16, 0, 16000, RA, M, chance=0.5,
    atouts=["force", "intelligence"], grades=["Pisteur·se", "Chasseur·se", "Terreur des pirates", "Légende"], mult=[1, 2, 5, 15], risque=0.08, fame=3)

ORIGINES_METIERS = {
    "heros_pro": ["Armure technologique", "Mutation métamorphe", "Arachnide urbain", "Énergie cosmique", "Télépathie", "Magie", "Vigilante entraîné"],
    "justicier_armure": ["Armure technologique"],
    "tisseur_urbain": ["Arachnide urbain"],
    "heros_energie": ["Énergie cosmique"],
    "metamorphe": ["Mutation métamorphe"],
    "telepathe": ["Télépathie"],
    "chasseur_anomalies": ["Vigilante entraîné", "Magie", "Énergie cosmique"],
    "gardien_dimension": ["Magie", "Énergie cosmique"],
    "heroine_soins": ["Magie", "Énergie cosmique"],
}

# ======================================================================
#  MÉTIERS : conditions, chance, salaire
# ======================================================================
def manques(g, key):
    j, m = JOBS[key], []
    origines = ORIGINES_METIERS.get(key)
    if origines and g.get("origine_heroique", "Aucune") not in origines:
        m.append("origine incompatible (personnage : " + g.get("origine_heroique", "Aucune") + "); origine requise : " + " / ".join(origines))
    if key in ("ninja", "anbu", "sensei_ninja", "medecin_ninja", "ninja_chercheur", "kage") and g.get("saga_manga", "naruto") != "naruto":
        m.append("être dans la saga Naruto (village ninja)")
    if key in ("pirate", "marine", "revolutionnaire", "chasseur_primes") and g.get("saga_manga", "naruto") != "onepiece":
        m.append("être dans la saga One Piece (Grand Line)")
    if key == "marine" and g.get("faction_manga") != "Marine":
        m.append("avoir choisi de rejoindre la Marine lors d'un événement de recrutement")
    if key == "revolutionnaire" and g.get("faction_manga") != "Révolutionnaires":
        m.append("avoir rejoint les révolutionnaires lors d'un événement")
    if key == "pirate" and g.get("faction_manga") not in ("Pirates", "Empereur des mers"):
        m.append("avoir rejoint un équipage pirate")
    if key == "exorciste_jujutsu" and (g.get("saga_manga") != "jujutsu" or g.get("energie_occulte", 0) < 15):
        m.append("être dans la saga Jujutsu et avoir éveillé l'énergie occulte")
    if key == "anbu" and (g.get("metier") not in ("ninja", "chasseur_demons") or g.get("victoires_combat", 0) < 3):
        m.append("être déjà ninja et avoir au moins 3 victoires en combat")
    if key == "sensei_ninja" and (g.get("metier") not in ("ninja", "anbu") or g.get("victoires_combat", 0) < 2):
        m.append("avoir une expérience de ninja et au moins 2 victoires")
    if key == "kage" and (g.get("metier") not in ("ninja", "anbu", "sensei_ninja") or g.get("victoires_combat", 0) < 8 or g["stats"]["karma"] < 60):
        m.append("avoir un parcours de ninja, 8 victoires et un karma ≥ 60")
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
    # Une vie longue et équilibrée rapporte des jetons bonus à dépenser dans la boutique.
    if not g.get("recompense_vie", False):
        bonus = 0
        if g.get("age", 0) >= 60: bonus += 15
        if g.get("stats", {}).get("bonheur", 0) >= 70: bonus += 10
        if g.get("stats", {}).get("karma", 0) >= 70: bonus += 10
        if g.get("famille_relations", 0) >= 75: bonus += 10
        if g.get("succes"): bonus += min(20, len(g["succes"]) * 2)
        if bonus:
            g["jetons"] = g.get("jetons", 0) + bonus
            log(g, f"🌟 Belle vie : +{bonus} jetons bonus pour tes accomplissements. Ils seront transmis à l'héritier.")
        g["recompense_vie"] = True
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
def programmer_consequence(g, delai, titre, texte, effets=None):
    """Programme une retombée narrative pour un âge futur."""
    g.setdefault("consequences_differees", []).append({
        "age_declenchement": g.get("age", 0) + max(1, int(delai)),
        "titre": titre, "texte": texte, "effets": effets or {}
    })
    g.setdefault("historique_choix", []).append({"age": g.get("age", 0), "evenement": titre, "choix": "Conséquence programmée"})


def appliquer_consequences(g):
    restantes=[]
    for c in g.get("consequences_differees", []):
        if g.get("age", 0) >= c.get("age_declenchement", 10**9):
            for cle, valeur in c.get("effets", {}).items():
                if cle == "argent":
                    g["argent"] += int(valeur)
                elif cle in g.get("stats", {}):
                    g["stats"][cle] = clamp(g["stats"][cle] + valeur)
                elif cle == "famille_relations":
                    g[cle] = clamp(g.get(cle, 60) + valeur)
                elif cle == "reputation":
                    g[cle] = clamp(g.get(cle, 50) + valeur)
            log(g, f"⏳ CONSÉQUENCE — {c['titre']} : {c['texte']}")
            g.setdefault("chronologie_famille", []).append({"age": g["age"], "titre": c["titre"], "texte": c["texte"]})
        else:
            restantes.append(c)
    g["consequences_differees"] = restantes


def verifier_pouvoirs(g):
    metier = g.get("metier")
    profils = {
        "heros_pro": ["Force surhumaine", "Instinct héroïque"],
        "justicier_armure": ["Armure high-tech", "Gadgets tactiques"],
        "tisseur_urbain": ["Adhérence murale", "Réflexes augmentés", "Filins de déplacement"],
        "heros_energie": ["Projection d'énergie", "Vol cosmique"],
        "metamorphe": ["Métamorphose", "Imitation vocale"],
        "telepathe": ["Télépathie", "Bouclier mental"],
        "chasseur_anomalies": ["Sens des anomalies", "Arsenal spécialisé"],
        "gardien_dimension": ["Portails dimensionnels", "Manipulation des sceaux"],
        "heroine_soins": ["Régénération", "Onde de soin"],
    }
    if metier in profils:
        nouveaux = [p for p in profils[metier] if p not in g.setdefault("pouvoirs", [])]
        if nouveaux:
            g["pouvoirs"].extend(nouveaux)
            log(g, "✨ Pouvoirs débloqués : " + ", ".join(nouveaux))


def passer_annee(g):
    if not g["vivant"]:
        return
    S, V = g["stats"], ville_info(g)
    g["age"] += 1
    a = g["age"]
    g["actions"] = ACTIONS_PAR_AN
    log(g, f"🎂 Tu as {a} ans.")
    appliquer_consequences(g)
    verifier_pouvoirs(g)

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
        if j["cat"] != JE and g["grade"] < min(3, len(j["grades"])-1):
            # La promotion dépend des résultats réels : l'ancienneté seule ne suffit plus.
            base = 4 if g.get("performance_metier", 35) < 35 else (10 if g.get("performance_metier", 35) < 60 else 18)
            g["progression_grade"] = min(100, g.get("progression_grade", 0) + base + S["intelligence"] // 20)
            if g["annees_metier"] % 2 == 0 and g.get("progression_grade", 0) >= 65 and g.get("performance_metier", 35) >= 55:
                g["grade"] += 1
                g["progression_grade"] = 0
                g["performance_metier"] = max(45, g.get("performance_metier", 35) - 10)
                log(g, f"📈 Promotion ! Tes résultats et tes missions te font devenir {j['grades'][g['grade']]}.")
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

    # --- Parents : vieillissement et relations
    for parent in g.get("parents", []):
        if parent.get("vivant", True):
            parent["age"] = parent.get("age", 35) + 1
            parent["relation"] = clamp(parent.get("relation", 65) + random.choice([-3, -1, 0, 1, 2]))
            if parent["age"] >= 82 and random.random() < 0.08:
                parent["vivant"] = False
                log(g, f"🕯️ {parent['nom']}, ton/ta {parent.get('role', 'parent').lower()}, est décédé·e à {parent['age']} ans.")
    for membre in g.get("fratrie", []):
        membre["age"] = membre.get("age", 0) + 1
        membre["relation"] = clamp(membre.get("relation", 60) + random.choice([-2, -1, 0, 1, 2]))
    if g.get("famille_relations", 65) < 30:
        for parent in g.get("parents", []):
            parent["relation"] = clamp(parent.get("relation", 50) - 1)

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
        ami.setdefault("personnalite", "Loyal·e")
        ami["relation"] = clamp(ami.get("relation", 50) + random.randint(-3, 2))
        ami["confiance"] = clamp(ami.get("confiance", ami["relation"]) + random.randint(-2, 2))
        if ami.get("statut", "ami·e") == "ami·e" and ami["relation"] < 18:
            ami["statut"] = "ennemi·e"
            g.setdefault("rivalites", []).append({"nom": ami["nom"], "origine": "Amitié brisée", "age": a, "intensite": 1})
            log(g, f"💥 Rupture : {ami['nom']} n'est plus ton ami·e. Votre relation devient une rivalité.")
        elif ami.get("statut") == "ennemi·e" and ami["relation"] > 75:
            ami["statut"] = "ami·e"
            log(g, f"🕊️ Après des années de tension, {ami['nom']} et toi faites la paix.")
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

    # --- Actualités de fond : une brève informative apparaît chaque année.
    # Titres et jalons de vie débloqués par les actes du personnage.
    titres = g.setdefault("titres", [])
    def donner_titre(code, nom):
        if code not in titres:
            titres.append(code)
            log(g, f"🏆 Nouveau titre débloqué : {nom} !")
    if g.get("missions_reussies", 0) >= 10: donner_titre("professionnel_confirme", "Professionnel confirmé")
    if g.get("coffres_ouverts", 0) >= 10: donner_titre("chasseur_tresors", "Chasseur de trésors")
    if g.get("argent", 0) >= 10000000: donner_titre("fortune", "Grande fortune")
    if g.get("reputation", 50) >= 90: donner_titre("legende", "Légende vivante")
    if g.get("univers") == "manga" and g.get("saga_manga") == "onepiece" and g.get("notoriete_manga", 0) >= 80:
        donner_titre("legende_mer", "Légende des mers")
    actualiser_economie_mondiale(g)
    generer_breve_informative(g)

    # --- Mort, événement, succès
    if g["vivant"]:
        mort_check(g)
    if g["vivant"] and random.random() < 0.6:
        tirer_evenement(g)
    maj_succes(g)



# ======================================================================
#  SYSTEMES SPECIFIQUES : MANGA, COMBAT, HEROÏSME ET ACTUALITES
# ======================================================================
JUTSU = {
    "Boule de feu": {"cout": 12, "puissance": 24, "min": 20, "desc": "Une technique de feu offensive."},
    "Clone d'ombre": {"cout": 16, "puissance": 30, "min": 35, "desc": "Des clones perturbent l'adversaire."},
    "Rafale de vent": {"cout": 10, "puissance": 20, "min": 15, "desc": "Une attaque rapide de vent."},
    "Mur de terre": {"cout": 14, "puissance": 12, "min": 25, "desc": "Une défense qui réduit les dégâts reçus."},
    "Pas éclair": {"cout": 18, "puissance": 34, "min": 45, "desc": "Un déplacement ultra-rapide."},
    "Sceau de soin": {"cout": 20, "puissance": -18, "min": 50, "desc": "Restaure une partie de la santé."},
    "Rasengan": {"cout": 28, "puissance": 48, "min": 70, "desc": "Une sphère de chakra concentré."},
    "Invocation": {"cout": 24, "puissance": 40, "min": 60, "desc": "Une créature invoquée aide au combat."},
    "Chidori": {"cout": 30, "puissance": 52, "min": 65, "desc": "Une charge électrique concentrée. Très puissante, mais risquée."},
    "Katon : Dragon de feu": {"cout": 26, "puissance": 46, "min": 55, "desc": "Un dragon de flammes balaie le terrain."},
    "Suiton : Prison aqueuse": {"cout": 22, "puissance": 34, "min": 45, "desc": "Une sphère d'eau immobilise l'adversaire."},
    "Suiton : Dragon aqueux": {"cout": 28, "puissance": 45, "min": 60, "desc": "Un dragon d'eau frappe l'ennemi."},
    "Futon : Lame de vent": {"cout": 25, "puissance": 44, "min": 55, "desc": "Une lame de vent traverse la défense."},
    "Doton : Rempart géant": {"cout": 20, "puissance": 18, "min": 40, "desc": "Un rempart absorbe une partie des dégâts."},
    "Raiton : Éclair noir": {"cout": 32, "puissance": 55, "min": 72, "desc": "Un éclair noir explose au contact."},
    "Rasenshuriken": {"cout": 42, "puissance": 68, "min": 88, "desc": "Une spirale de chakra tranchante dévaste la zone."},
    "Multi-clonage": {"cout": 25, "puissance": 42, "min": 58, "desc": "Une vague de clones submerge l'adversaire."},
    "Régénération mystique": {"cout": 30, "puissance": -30, "min": 75, "desc": "Une technique médicale avancée restaure la santé."},
    "Byakugan": {"cout": 18, "puissance": 32, "min": 40, "desc": "Technique héréditaire Hyûga : vision presque à 360°.", "clan": "Hyûga"},
    "Paume du Hakke": {"cout": 24, "puissance": 44, "min": 55, "desc": "Style Hyûga qui perturbe le flux de chakra.", "clan": "Hyûga"},
    "Soixante-quatre paumes": {"cout": 35, "puissance": 60, "min": 78, "desc": "Enchaînement héréditaire du clan Hyûga.", "clan": "Hyûga"},
    "Sharingan": {"cout": 20, "puissance": 36, "min": 45, "desc": "Dōjutsu Uchiha : lecture des mouvements.", "clan": "Uchiha"},
    "Mangekyō Sharingan": {"cout": 42, "puissance": 70, "min": 85, "desc": "Éveil rare du Mangekyō. Son usage a un prix.", "clan": "Uchiha"},
    "Amaterasu": {"cout": 45, "puissance": 74, "min": 90, "desc": "Des flammes noires qui ne s'éteignent presque jamais.", "clan": "Uchiha"},
    "Susanoo": {"cout": 50, "puissance": 82, "min": 95, "desc": "Un avatar de chakra protège et frappe.", "clan": "Uchiha"},
    "Expansion corporelle": {"cout": 22, "puissance": 38, "min": 45, "desc": "Technique secrète du clan Akimichi.", "clan": "Akimichi"},
    "Possession des ombres": {"cout": 25, "puissance": 40, "min": 48, "desc": "Technique secrète du clan Nara.", "clan": "Nara"},
    "Manipulation des insectes": {"cout": 20, "puissance": 34, "min": 42, "desc": "Les insectes du clan Aburame traquent et harcèlent.", "clan": "Aburame"},
    "Mokuton : Racines entravantes": {"cout": 32, "puissance": 56, "min": 72, "desc": "Des racines immobilisent l'adversaire.", "clan": "Senju"},
    "Mokuton : Forêt profonde": {"cout": 48, "puissance": 78, "min": 92, "desc": "Une forêt surgit et submerge le champ de bataille.", "clan": "Senju"},
    "Sceau maudit": {"cout": 35, "puissance": 62, "min": 70, "desc": "Une puissance dangereuse augmente la force, au prix de la santé."},
    "Libération du sceau": {"cout": 38, "puissance": 66, "min": 80, "desc": "Tu libères une réserve de chakra scellée."},
    "Mode ermite": {"cout": 40, "puissance": 72, "min": 88, "desc": "Tu absorbes l'énergie naturelle pour dépasser tes limites."},
    "Orbe tourbillonnant géant": {"cout": 38, "puissance": 64, "min": 82, "desc": "Une version massive du Rasengan."},
    "Poing divergent": {"cout": 12, "puissance": 24, "min": 15, "desc": "L'énergie occulte frappe après l'impact physique.", "saga": "jujutsu"},
    "Éclair noir": {"cout": 28, "puissance": 52, "min": 45, "desc": "Une distorsion de l'énergie occulte décuple l'impact.", "saga": "jujutsu"},
    "Manipulation du sang": {"cout": 26, "puissance": 46, "min": 48, "desc": "Tu contrôles ton sang comme une arme.", "saga": "jujutsu"},
    "Discours maudit": {"cout": 30, "puissance": 48, "min": 55, "desc": "Tes paroles imposent un ordre dangereux à l'adversaire.", "saga": "jujutsu"},
    "Technique des dix ombres": {"cout": 35, "puissance": 58, "min": 68, "desc": "Tu invoques des shikigami depuis les ombres.", "saga": "jujutsu"},
    "Extension du territoire": {"cout": 48, "puissance": 78, "min": 88, "desc": "Tu imposes ton domaine et bouleverses les règles du combat.", "saga": "jujutsu"},
    "Technique inverse": {"cout": 32, "puissance": -28, "min": 60, "desc": "Tu inverses l'énergie occulte pour réparer les blessures.", "saga": "jujutsu"},
    "Infini": {"cout": 38, "puissance": 62, "min": 78, "desc": "Une barrière spatiale ralentit tout ce qui approche.", "saga": "jujutsu"},
    "Pourpre": {"cout": 52, "puissance": 88, "min": 96, "desc": "La collision de forces opposées efface tout sur son passage.", "saga": "jujutsu"},
    "Maximum : Uzumaki maudit": {"cout": 42, "puissance": 72, "min": 82, "desc": "Tu concentres des fléaux en une attaque dévastatrice.", "saga": "jujutsu"},
    "Rasengan en spirale": {"cout": 26, "puissance": 43, "min": 52, "desc": "Une variante plus rapide du Rasengan.", "saga": "naruto"},
    "Kage Bunshin supérieur": {"cout": 32, "puissance": 50, "min": 65, "desc": "Une technique de clonage avancée.", "saga": "naruto"},
    "Kirin": {"cout": 46, "puissance": 76, "min": 90, "desc": "Tu guides la foudre naturelle sur ton adversaire.", "saga": "naruto"},
    "Sceau des huit trigrammes": {"cout": 35, "puissance": 52, "min": 72, "desc": "Un sceau complexe bloque le flux d'énergie.", "saga": "naruto"},
    "Téléportation du dieu du tonnerre": {"cout": 40, "puissance": 70, "min": 88, "desc": "Tu te déplaces instantanément entre des sceaux.", "saga": "naruto"},
}
# Les techniques historiques non taguées appartiennent à la voie Naruto.
for _nom_technique, _donnees_technique in JUTSU.items():
    _donnees_technique.setdefault("saga", "naruto")

ACTUALITES = [
    {"id":"village_examens", "titre":"Les examens de sélection approchent", "texte":"L'académie annonce des épreuves ouvertes aux ninjas méritants.", "univers":"manga", "choix":[("S'entraîner pour l'examen", "chakra"), ("Aider les plus jeunes", "karma")]},
    {"id":"village_menace", "titre":"Une menace près des frontières", "texte":"Des éclaireurs signalent des mouvements suspects près du village.", "univers":"manga", "choix":[("Proposer une patrouille", "force"), ("Transmettre les informations", "intelligence")]},
    {"id":"village_hokage", "titre":"Le conseil cherche un nouveau leader", "texte":"Le village débat de ses priorités et de son prochain dirigeant.", "univers":"manga", "choix":[("Défendre la paix", "karma"), ("Présenter ses exploits", "celebrite")]},
    {"id":"hero_armure", "titre":"Une nouvelle technologie fait débat", "texte":"Des ingénieurs dévoilent un module d'armure expérimental.", "univers":"real", "choix":[("Étudier le prototype", "intelligence"), ("Faire une démonstration publique", "celebrite")]},
    {"id":"hero_civils", "titre":"Une intervention héroïque fait la une", "texte":"Les habitants attendent une réponse après un incident en centre-ville.", "univers":"real", "choix":[("Secourir les civils", "karma"), ("Enquêter discrètement", "intelligence")]},
    {"id":"general_scandale", "titre":"Un scandale secoue la ville", "texte":"Une affaire locale divise l'opinion. Chacun attend de voir comment tu réagis.", "univers":"all", "choix":[("Aider les personnes touchées", "karma"), ("Chercher la vérité", "intelligence")]},
]

def apprendre_jutsu(g, nom):
    if g.get("univers") != "manga":
        raise Refus("Les jutsu ne sont disponibles que dans l'univers manga.")
    if nom not in JUTSU:
        raise Refus("Technique inconnue.")
    if nom in g.setdefault("jutsu", []):
        raise Refus("Tu connais déjà cette technique.")
    tech = JUTSU[nom]
    if tech.get("saga") and tech["saga"] != g.get("saga_manga", "naruto"):
        raise Refus(f"Cette technique appartient à la saga {tech['saga']} et n'est pas enseignée dans ton école.")
    ressource = "energie_occulte" if tech.get("saga") == "jujutsu" else "chakra"
    clan_requis = tech.get("clan")
    if clan_requis and g.get("clan") != clan_requis:
        if not (clan_requis == "Uchiha" and g.get("sharingans_voles", 0) > 0 and nom in ("Sharingan", "Mangekyō Sharingan")):
            raise Refus(f"Cette technique héréditaire est réservée au clan {clan_requis}.")
    if g.get(ressource, 0) < tech["min"]:
        nom_ressource = "énergie occulte" if ressource == "energie_occulte" else "chakra"
        raise Refus(f"Il faut au moins {tech['min']} points d'{nom_ressource} pour apprendre cette technique.")
    if g["stats"]["intelligence"] < 35 and nom in ("Clone d'ombre", "Rasengan", "Invocation"):
        raise Refus("Ton intelligence doit atteindre 35 pour maîtriser cette technique.")
    g[ressource] = clamp(g.get(ressource, 0) + 3)
    g["jutsu"].append(nom)
    g["niveau_pouvoir"] = g.get("niveau_pouvoir", 0) + 1
    log(g, f"📜 Nouveau jutsu appris : {nom}.")
    return f"📜 Tu maîtrises désormais {nom}."

def entrainement_chakra(g):
    if g.get("univers") != "manga":
        raise Refus("Cet entraînement est réservé à l'univers manga.")
    gain = random.randint(8, 16)
    if g.get("saga_manga") == "jujutsu":
        g["energie_occulte"] = min(100, g.get("energie_occulte", 0) + gain)
        ressource = "énergie occulte"
    else:
        g["chakra"] = clamp(g.get("chakra", 50) + gain)
        ressource = "chakra"
    chg(g, force=random.randint(1, 3), bonheur=2)
    log(g, f"🌊 Entraînement : +{gain} {ressource}.")
    return f"🌊 Entraînement réussi : +{gain} {ressource} et un peu de force."

def combat_jutsu(g, nom):
    if g.get("univers") != "manga":
        raise Refus("Les combats de jutsu sont réservés à l'univers manga.")
    if nom not in g.get("jutsu", []):
        raise Refus("Tu dois d'abord apprendre ce jutsu.")
    tech = JUTSU[nom]
    if tech.get("saga") and tech["saga"] != g.get("saga_manga", "naruto"):
        raise Refus("Cette technique n'appartient pas à ta voie actuelle.")
    ressource = "energie_occulte" if tech.get("saga") == "jujutsu" else "chakra"
    nom_ressource = "énergie occulte" if ressource == "energie_occulte" else "chakra"
    if g.get(ressource, 0) < tech["cout"]:
        raise Refus(f"Pas assez d'{nom_ressource} : {tech['cout']} requis.")
    g[ressource] -= tech["cout"]
    if nom in ("Mangekyō Sharingan", "Amaterasu", "Susanoo", "Sceau maudit"):
        chg(g, sante=-random.randint(2, 7), bonheur=-1)
    if nom == "Mode ermite":
        g["chakra"] = clamp(g["chakra"] + 8)
    puissance = tech["puissance"] + g["stats"]["force"] // 5 + g.get("niveau_pouvoir", 0) * 2
    if puissance < 0:
        soin = abs(puissance)
        chg(g, sante=soin)
        resultat = f"💚 {nom} soigne {soin} points de santé."
    else:
        score = puissance + random.randint(-12, 15)
        if score >= 30:
            g["victoires_combat"] = g.get("victoires_combat", 0) + 1
            chg(g, force=2, celebrite=2, karma=1)
            g[ressource] = clamp(g.get(ressource, 0) + 3)
            if g.get("saga_manga") == "onepiece":
                g["notoriete_manga"] = min(100, g.get("notoriete_manga", 0) + 3)
            resultat = f"⚔️ Victoire avec {nom} ! Puissance {score}. Tu gagnes de l'expérience et de la réputation."
        else:
            chg(g, sante=-random.randint(4, 12), bonheur=-2)
            resultat = f"🥋 Le combat est difficile. {nom} touche partiellement (puissance {score}) et tu es blessé·e."
    log(g, resultat)
    return resultat

def entrainer_hero(g):
    if g.get("univers") != "real":
        raise Refus("Cet entraînement est réservé aux héros du monde réel.")
    if g.get("metier") not in ORIGINES_METIERS:
        raise Refus("Il faut exercer un métier héroïque pour s'entraîner ici.")
    gain = random.randint(5, 12)
    g["entrainement_heroique"] = g.get("entrainement_heroique", 0) + gain
    chg(g, force=random.randint(1, 3), sante=2)
    if g.get("origine_heroique") == "Armure technologique":
        g["armure_niveau"] = min(10, g.get("armure_niveau", 0) + 1)
        resultat = f"🦾 Entraînement terminé : +{gain} maîtrise et armure niveau {g['armure_niveau']}."
    else:
        g["niveau_pouvoir"] = g.get("niveau_pouvoir", 0) + 1
        resultat = f"⚡ Entraînement terminé : +{gain} maîtrise. Niveau de pouvoir {g['niveau_pouvoir']}."
    log(g, resultat)
    return resultat

def ameliorer_armure(g):
    if g.get("origine_heroique") != "Armure technologique":
        raise Refus("Seuls les personnages à armure technologique peuvent l'améliorer.")
    prix = 5000 + g.get("armure_niveau", 0) * 2500
    payer(g, prix)
    g["armure_niveau"] = min(10, g.get("armure_niveau", 0) + 1)
    g["entrainement_heroique"] = g.get("entrainement_heroique", 0) + 5
    log(g, f"🦾 Armure améliorée au niveau {g['armure_niveau']} pour {fm(g, prix)}.")
    return f"🦾 Armure améliorée au niveau {g['armure_niveau']}."

def actualite_choix(g, choix, reaction):
    item = next((x for x in ACTUALITES if x["id"] == choix), None)
    if not item:
        raise Refus("Actualité introuvable.")
    if item["univers"] not in ("all", g["univers"]):
        raise Refus("Cette actualité ne concerne pas ton univers.")
    option = next((x for x in item["choix"] if x[0] == reaction), None)
    if not option:
        raise Refus("Réaction invalide.")
    stat = option[1]
    if stat == "chakra":
        g["chakra"] = clamp(g.get("chakra", 50) + 8)
    else:
        chg(g, **{stat: 5})
    g.setdefault("radio_lue", []).append(item["id"])
    g.setdefault("journal_actualites", []).append({"age":g["age"], "titre":item["titre"], "choix":reaction})
    return f"📻 Tu réagis à l'actualité « {item['titre']} » : {reaction}. Ton choix influence la suite de ta vie."


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

event("parents_secret", "Un secret de famille", "📦 En rangeant le grenier, tu trouves une lettre qui pourrait changer ta vision de tes parents.",
      lambda g: g["age"] >= 10 and any(p.get("vivant", True) for p in g.get("parents", [])),
      [("En parler avec eux", lambda g: (g.update(famille_relations=clamp(g.get("famille_relations",65)+8)) or res(g, "💬 La conversation est difficile, mais vous vous comprenez mieux.", bonheur=5, karma=2))),
       ("Garder la lettre pour toi", lambda g: res(g, "🤐 Tu gardes le secret. Il te reste en tête.", bonheur=-2))])
event("ami_demande_aide", "Un ami a besoin de toi", "🫂 Un ami proche traverse une période compliquée et te demande de l'aide.",
      lambda g: g["age"] >= 8 and bool(g.get("amis")),
      [("Être présent·e", lambda g: (g["amis"][0].update(relation=clamp(g["amis"][0].get("relation",50)+15)) or res(g, "❤️ Tu l'écoutes et votre amitié se renforce.", bonheur=5, karma=3))),
       ("Prétexter être trop occupé·e", lambda g: (g["amis"][0].update(relation=clamp(g["amis"][0].get("relation",50)-12)) or res(g, "📵 Ton ami se sent abandonné. Il sera moins enclin à t'aider à l'avenir.", bonheur=-3, karma=-2)))])
event("opportunite_etudes", "Une opportunité inattendue", "🎓 Un professeur te propose de participer à un concours qui pourrait ouvrir des portes.",
      lambda g: 10 <= g["age"] <= 24 and (g.get("en_ecole") or g.get("etudes_en_cours")),
      [("Accepter le défi", lambda g: res(g, "🏅 Tu t'investis et tu progresses.", notes=8, intelligence=3, bonheur=4)),
       ("Refuser pour te reposer", lambda g: res(g, "🌿 Tu prends du temps pour toi.", bonheur=3))])
event("erreur_publique", "Une erreur fait le tour des réseaux", "📱 Une vidéo embarrassante de toi devient virale. Tu peux répondre ou laisser passer la vague.",
      lambda g: g["age"] >= 13 and g["stats"]["celebrite"] >= 10,
      [("Répondre avec humour", lambda g: res(g, "😅 Tu désamorces la situation et gagnes un peu de sympathie.", celebrite=3, bonheur=2)),
       ("T'énerver publiquement", lambda g: res(g, "🔥 La polémique enfle et ta réputation en prend un coup.", celebrite=5, bonheur=-10, karma=-4)),
       ("Ignorer et prendre du recul", lambda g: res(g, "🧘 Tu laisses la polémique retomber.", bonheur=3, celebrite=-2))])


# Histoires à embranchements et conséquences qui se déclenchent plusieurs années plus tard.
def ev_travail_sacrifie(g):
    programmer_consequence(g, 4, "Le prix de l'ambition", "Des années plus tard, un proche te reproche les moments manqués.", {"famille_relations": -12, "bonheur": -5})
    return res(g, "💼 Tu acceptes une promotion exigeante. Tu gagnes en carrière, mais le temps passé loin des tiens pourrait te coûter cher.", bonheur=4, intelligence=2)

def ev_choix_scolaire(g):
    programmer_consequence(g, 3, "Le concours oublié", "Un ancien professeur se souvient de ton choix et te recommande (ou non) pour une opportunité.", {"intelligence": 5, "reputation": 4})
    return res(g, "🎓 Tu choisis de participer à un concours scolaire. Cette décision pourrait ouvrir une porte dans quelques années.", notes=10, intelligence=3, bonheur=-2)

def ev_secret_amis(g):
    g.setdefault("secrets", []).append({"titre": "Secret confié à un ami", "age": g.get("age",0), "confiance": 1})
    ami = max(g.get("amis", [{"nom":"un proche", "relation":50}]), key=lambda x: x.get("relation",50))
    if g.get("amis"):
        ami["confiance"] = clamp(ami.get("confiance",50)+12)
    programmer_consequence(g, 5, "Un secret refait surface", "Une confidence ancienne refait surface et teste les liens de confiance.", {"famille_relations": -4, "bonheur": -3})
    return res(g, "🤫 Tu confies un secret à quelqu'un. Vous vous rapprochez, mais cette confiance sera mise à l'épreuve plus tard.", bonheur=3, karma=2)

def ev_rivalite_ecole(g):
    rival_nom = random.choice([n for n in PRENOMS if n != g.get("nom")])
    g.setdefault("rivalites", []).append({"nom": rival_nom, "origine": "Rivalité scolaire", "age": g.get("age",0), "intensite": 1})
    g.setdefault("chronologie_famille", []).append({"age": g.get("age",0), "titre": "Rivalité scolaire", "texte": f"{rival_nom} devient ton rival après une compétition scolaire."})
    programmer_consequence(g, 2, "Retrouvailles avec un rival", f"Tu recroises {rival_nom}. La rivalité peut devenir une alliance ou repartir de plus belle.", {"intelligence": 2})
    return res(g, f"🏆 {rival_nom} et toi vous disputez la première place. Une rivalité commence.", bonheur=-2, intelligence=2)

def ev_pouvoir_eveille(g):
    if not g.get("pouvoirs"):
        verifier_pouvoirs(g)
    if not g.get("pouvoirs"):
        g["pouvoirs"] = [random.choice(["Réflexes augmentés", "Vision nocturne", "Télékinésie limitée", "Bouclier d'énergie"])]
    pouvoir = random.choice(g["pouvoirs"])
    g["niveau_pouvoir"] = clamp(g.get("niveau_pouvoir", 0)+8)
    return res(g, f"⚡ Ton pouvoir {pouvoir.lower()} s'intensifie. Tu dois apprendre à le maîtriser sans mettre tes proches en danger.", force=3, bonheur=4, celebrite=2)

event("ambition_carriere", "Une promotion qui coûte cher", "💼 Une promotion importante exige de longs horaires et des déplacements. Ta famille risque d'en pâtir.",
      lambda g: bool(g.get("metier")) and g.get("age",0) >= 20 and bool(g.get("partenaire") or g.get("enfants")) and g.get("grade",0) < 3,
      [("Accepter le sacrifice", ev_travail_sacrifie), ("Privilégier tes proches", lambda g: (g.update(famille_relations=clamp(g.get("famille_relations",60)+8)) or res(g, "🏡 Tu refuses la promotion pour préserver ton équilibre. Tes proches apprécient ce choix.", bonheur=5)))])
event("choix_scolaire_rival", "La compétition scolaire", "📚 Un concours se prépare et un autre élève semble prêt à tout pour gagner.",
      lambda g: 10 <= g.get("age",0) <= 20 and (g.get("en_ecole") or g.get("etudes_en_cours")),
      [("Jouer pour gagner", ev_rivalite_ecole), ("L'aider à progresser", lambda g: res(g, "🤝 Tu aides ton concurrent. Il pourrait devenir un allié plus tard.", karma=5, bonheur=3, notes=4))])
event("secret_ami", "Une confidence risquée", "🤐 Un ami te demande si tu peux garder un secret lourd de conséquences.",
      lambda g: g.get("age",0) >= 12 and bool(g.get("amis")),
      [("Garder le secret", ev_secret_amis), ("En parler à un adulte de confiance", lambda g: (programmer_consequence(g,2,"La confiance mise à l'épreuve","Ton ami découvre que tu as demandé de l'aide, mais comprend finalement tes raisons.",{"bonheur":2}) or res(g,"🛡️ Tu cherches de l'aide pour éviter que la situation dégénère.", karma=4)))])
event("eveil_pouvoir", "Un pouvoir se réveille", "⚡ Pendant une situation stressante, tu sens une capacité inhabituelle se manifester.",
      lambda g: g.get("metier") in ("heros_pro", "justicier_armure", "tisseur_urbain", "heros_energie", "metamorphe", "telepathe", "chasseur_anomalies", "gardien_dimension", "heroine_soins") and g.get("age",0) >= 16,
      [("T'entraîner à le maîtriser", ev_pouvoir_eveille), ("Le cacher au monde", lambda g: (g.update(suspicion=clamp(g.get("suspicion",0)+5)) or res(g,"🕶️ Tu caches cette évolution. Tu évites l'attention, mais tu progresses moins vite.", bonheur=-1)))])


# ----------------------------------------------------------------------
# PACK NARRATIF ÉTENDU : conséquences à long terme, manga et métiers
# ----------------------------------------------------------------------
def ev_refuser_aide(g):
    nom = random.choice(PRENOMS)
    delai = random.randint(3, 7)
    g["ami_vexe"] = {"nom": nom, "age_retour": g.get("age", 0) + delai, "retour_declenche": False}
    programmer_consequence(g, delai, "Une vieille rancune", f"{nom} n'a jamais oublié que tu as refusé de l'aider. Vous vous reverrez peut-être dans de mauvaises circonstances.", {"bonheur": -2})
    return res(g, f"🚪 Tu refuses d'aider {nom}. Il/elle encaisse en silence, mais son regard a changé. Cette histoire n'est peut-être pas terminée.", karma=-5, bonheur=1)

def ev_aider_ami(g):
    nom = random.choice(PRENOMS)
    programmer_consequence(g, random.randint(2, 5), "Une dette d'amitié", f"{nom} se souvient que tu étais là au pire moment. Un jour, cette aide pourrait te revenir.", {"bonheur": 4, "karma": 3})
    return res(g, f"🤝 Tu aides {nom}. Tu y laisses du temps ou de l'argent, mais cette personne n'oubliera pas ton geste.", karma=6, bonheur=3, argent=-random.randint(0, 700))

def ev_revanche_ami(g):
    rival = (g.get("ami_vexe") or {}).get("nom", random.choice(PRENOMS))
    return res(g, f"🩸 {rival} réapparaît, des années après ton refus. Il/elle t'a attiré·e dans un endroit isolé pour régler ses comptes.", bonheur=-4)

def ev_revanche_se_defendre(g):
    rival = (g.get("ami_vexe") or {}).get("nom", "ton ancien ami")
    g["ami_vexe"] = None
    if g["stats"]["force"] + random.randint(-15, 20) >= 55:
        return res(g, f"🥊 Tu repousses {rival} et prends le dessus. La confrontation se termine, mais tu garderas cette cicatrice en mémoire.", force=4, sante=-4, celebrite=2)
    return res(g, f"💥 {rival} te blesse avant de s'enfuir. Tu portes plainte, mais la confiance est brisée.", sante=-18, bonheur=-8, karma=2)

def ev_revanche_excuses(g):
    rival = (g.get("ami_vexe") or {}).get("nom", "ton ancien ami")
    g["ami_vexe"] = None
    if g["stats"]["karma"] >= 55 or random.random() < .35:
        return res(g, f"🕊️ Tu présentes des excuses sincères à {rival}. Il/elle baisse sa garde et accepte de tourner la page.", karma=8, bonheur=5)
    return res(g, f"😠 {rival} refuse tes excuses et s'en va en promettant de ne plus jamais te faire confiance.", bonheur=-5, karma=2)

def ev_revanche_police(g):
    rival = (g.get("ami_vexe") or {}).get("nom", "ton ancien ami")
    g["ami_vexe"] = None
    return res(g, f"🚨 Tu appelles les secours et la police. {rival} est interpellé·e après une lutte. Tu es entendu·e comme témoin.", sante=-2, karma=4, bonheur=-1)

def ev_bijuu_naissance(g):
    biju = random.choice(["Shukaku", "Matatabi", "Isobu", "Son Gokū", "Kokuō", "Saiken", "Chōmei", "Gyūki", "Kurama"])
    g["bijuu"] = biju
    g["bijuu_maitrise"] = 0
    g["chakra"] = clamp(g.get("chakra", 50) + 15)
    g.setdefault("secrets", []).append("Hôte d'un bijū depuis la naissance")
    return res(g, f"🦊 DESTIN IMPOSSIBLE : tu es né·e avec {biju} scellé en toi. Le village veut te protéger… ou te contrôler. Ce secret pourrait changer toute ta vie.", bonheur=-8, force=5, celebrite=3)

def ev_bijuu_scellage(g):
    biju = random.choice(["Shukaku", "Matatabi", "Isobu", "Son Gokū", "Kokuō", "Saiken", "Chōmei", "Gyūki", "Kurama"])
    g["bijuu"] = biju
    g["bijuu_maitrise"] = 5
    g["chakra"] = clamp(g.get("chakra", 50) + 25)
    g.setdefault("secrets", []).append(f"{biju} scellé à l'âge {g.get('age', 0)}")
    programmer_consequence(g, 2, "Le bijū se manifeste", f"{biju} teste tes limites pendant ton sommeil. Il veut négocier sa liberté.", {"sante": -4, "force": 4})
    return res(g, f"🔒 SCELLEMENT D'URGENCE ! Après une attaque, des ninjas scellent {biju} en toi. Tu survis, mais tu entends désormais une voix derrière tes pensées.", bonheur=-6, force=8, celebrite=5)

def ev_bijuu_apaiser(g):
    g["bijuu_maitrise"] = min(100, g.get("bijuu_maitrise", 0) + 25)
    g["chakra"] = clamp(g.get("chakra", 50) + 12)
    return res(g, f"🦊 Tu ne cherches pas à dominer {g.get('bijuu', 'le bijū')} : tu lui parles. Pour la première fois, il t'écoute.", karma=8, bonheur=7)

def ev_bijuu_dominer(g):
    g["bijuu_maitrise"] = min(100, g.get("bijuu_maitrise", 0) + 35)
    g["chakra"] = clamp(g.get("chakra", 50) + 20)
    return res(g, "⚡ Tu imposes ta volonté au bijū. Sa puissance répond à ton chakra, mais une colère sourde grandit en toi.", force=8, karma=-5, bonheur=-2)

def ev_bijuu_refuser(g):
    g["bijuu_maitrise"] = max(0, g.get("bijuu_maitrise", 0) - 5)
    return res(g, "⛓️ Tu refuses de lui parler et renforces les sceaux. Le village est rassuré, mais la créature garde rancune.", karma=2, bonheur=-3)

def ev_vol_sharingan(g):
    if g.get("sharingans_voles", 0) > 0:
        raise Refus("Tu portes déjà un dōjutsu volé.")
    g["sharingans_voles"] = 1
    g["jutsu"] = list(dict.fromkeys(g.get("jutsu", []) + ["Sharingan"]))
    g["chakra"] = clamp(g.get("chakra", 50) + 5)
    g.setdefault("secrets", []).append("Sharingan volé")
    programmer_consequence(g, random.randint(2, 5), "Le clan cherche son œil", "Des shinobi ont retrouvé la trace du dōjutsu volé. Ils viennent réclamer justice.", {"bonheur": -4, "karma": -3})
    return res(g, "👁️ Tu voles un Sharingan sur un champ de bataille. Le pouvoir est réel, mais le clan de sa victime finira peut-être par te retrouver.", karma=-12, celebrite=4)

def ev_sharingan_refuser(g):
    return res(g, "🛑 Tu refuses de profaner un corps. Un témoin transmet ton geste à un ninja médecin : ta réputation gagne en respect.", karma=8, celebrite=2)

def ev_akatsuki_rejoindre(g):
    g["akatsuki"] = True
    g["secrets"] = list(dict.fromkeys(g.get("secrets", []) + ["Membre de l'Akatsuki"]))
    g["reputation"] = clamp(g.get("reputation", 50) - 12)
    programmer_consequence(g, 2, "Le prix de la cape noire", "Une mission de l'Akatsuki a laissé des témoins. Les chasseurs de déserteurs se rapprochent.", {"sante": -5, "karma": -5})
    return res(g, "☁️ Tu rejoins l'Akatsuki. Une cape noire à nuages rouges t'est remise. Tu obtiens des missions dangereuses et des ennemis à vie.", force=7, celebrite=8, karma=-10)

def ev_akatsuki_refuser(g):
    programmer_consequence(g, 2, "L'Akatsuki n'aime pas les refus", "Un recruteur de l'Akatsuki estime que tu en sais trop et envoie quelqu'un te surveiller.", {"bonheur": -3})
    return res(g, "🌑 Tu refuses l'offre et gardes ton allégeance au village. Le recruteur disparaît sans un mot. Son silence est inquiétant.", karma=5, bonheur=2)

def ev_clan_heritage(g):
    clan = g.get("clan", "")
    if clan == "Uchiha":
        nom = "Sharingan"
    elif clan == "Hyûga":
        nom = "Byakugan"
    else:
        nom = {"Senju": "Mokuton : Racines entravantes", "Nara": "Possession des ombres", "Akimichi": "Expansion corporelle", "Aburame": "Manipulation des insectes", "Uzumaki": "Sceau maudit"}.get(clan, "Rafale de vent")
    if nom in JUTSU and nom not in g.setdefault("jutsu", []):
        g["jutsu"].append(nom)
    g["chakra"] = clamp(g.get("chakra", 50) + 8)
    return res(g, f"🧬 Ton héritage se révèle : le clan {clan} t'enseigne {nom}. Une technique que seuls les tiens peuvent transmettre.", force=3, bonheur=5)

def ev_biju_negociation(g):
    g["bijuu_maitrise"] = min(100, g.get("bijuu_maitrise", 0) + 15)
    return res(g, f"🦊 Tu proposes un pacte à {g.get('bijuu', 'la créature')}. Il accepte une trêve fragile : vous avez chacun quelque chose à gagner.", karma=5, chakra=8)

def ev_mission_ninja(g):
    roll = g["stats"]["intelligence"] + g["stats"]["force"] + random.randint(-25, 25)
    if roll >= 105:
        gain = random.randint(2500, 12000)
        g["chakra"] = clamp(g.get("chakra", 50) + 10)
        return res(g, f"🥷 Mission de rang élevé réussie ! Rapport remis au Hokage, récompense de {fm(g, gain)} et réputation en hausse.", argent=gain, celebrite=6, karma=3)
    return res(g, "💢 La mission tourne mal. Tu ramènes l'équipe au village, mais tu es blessé·e et l'objectif est perdu.", sante=-12, bonheur=-4)

def ev_metier_succes(g, job_key):
    job = JOBS[job_key]
    gain = max(300, int(job["sal"] * random.uniform(.08, .25)))
    g["performance_metier"] = clamp(g.get("performance_metier", 0) + random.randint(8, 18))
    return res(g, f"{job['emoji']} Dans ton poste de {job['nom'].lower()}, tu gères une situation délicate avec sang-froid. Ton responsable le remarque : prime exceptionnelle de {fm(g, gain)}.", argent=gain, celebrite=2, bonheur=4)

def ev_metier_crise(g, job_key):
    job = JOBS[job_key]
    g["performance_metier"] = clamp(g.get("performance_metier", 0) - random.randint(5, 14))
    if random.random() < .35:
        g["historique_metiers"].append({"age": g["age"], "metier": job["nom"], "evenement": "Incident professionnel"})
        return res(g, f"🚨 Incident au travail : dans ton poste de {job['nom'].lower()}, une erreur est médiatisée. Tu dois regagner la confiance de ton équipe.", celebrite=-3, bonheur=-5, karma=-2)
    return res(g, f"⚠️ Journée noire comme {job['nom'].lower()} : imprévu, pression et reproches. Tu peux rebondir, mais ta performance baisse.", bonheur=-4, sante=-3)

def ev_metier_choix_reparer(g, job_key):
    job = JOBS[job_key]
    g["performance_metier"] = clamp(g.get("performance_metier", 0) + 12)
    return res(g, f"🧰 Tu assumes l'erreur dans ton poste de {job['nom'].lower()}, proposes une solution et restes après les heures. Ta réputation professionnelle remonte.", karma=4, bonheur=-1, celebrite=2)

def ev_metier_choix_cacher(g, job_key):
    job = JOBS[job_key]
    if random.random() < .45:
        g["performance_metier"] = clamp(g.get("performance_metier", 0) - 10)
        return res(g, f"🫥 Tu caches l'incident dans ton poste de {job['nom'].lower()}. Pour l'instant, personne ne remarque rien… mais une trace subsiste.", karma=-4, bonheur=2)
    return res(g, f"🔎 La vérité éclate dans ton poste de {job['nom'].lower()}. Tu dois expliquer pourquoi tu as dissimulé l'erreur.", karma=-8, celebrite=-4, bonheur=-6)

def ev_metier_opportunite(g, job_key):
    job = JOBS[job_key]
    g["performance_metier"] = clamp(g.get("performance_metier", 0) + 10)
    if g.get("grade", 0) < 3 and random.random() < .45:
        g["grade"] += 1
        promotion = f" Tu obtiens même une promotion : {job['grades'][g['grade']]}."
    else:
        promotion = ""
    return res(g, f"🌟 Une opportunité rare se présente dans ton métier de {job['nom'].lower()} : tu prends une initiative que personne n'avait osé proposer.{promotion}", argent=random.randint(500, 5000), intelligence=2, celebrite=3)

# Retombées de l'amitié : le refus d'aider peut devenir une vraie scène de confrontation.
event("ami_refuse_aide", "Un ami a besoin de toi", "📱 Un ami te demande de l'aide au pire moment : il a des dettes, des ennuis ou besoin que tu témoignes pour lui. Tu es déjà débordé·e.", lambda g: g.get("age", 0) >= 12 and not g.get("ami_vexe") and random.random() < .55, [("L'aider malgré tout", ev_aider_ami), ("Refuser et partir", ev_refuser_aide)])
event("ami_revanche", "Une silhouette dans la ruelle", "🌧️ Une silhouette t'attend à la sortie. Le visage est familier : une vieille rancune vient de refaire surface.", lambda g: bool(g.get("ami_vexe")) and g.get("age", 0) >= (g.get("ami_vexe") or {}).get("age_retour", 999) and g.get("ami_vexe", {}).get("retour_declenche", False) is False, [("Te défendre", ev_revanche_se_defendre), ("Présenter tes excuses", ev_revanche_excuses), ("Appeler la police", ev_revanche_police)])
event("bijuu_naissance", "Le secret dans ton chakra", "🌙 Depuis ta naissance, les médecins ont remarqué une seconde présence dans ton chakra. À l'adolescence, le secret éclate : un bijū dort en toi.", lambda g: g.get("univers") == "manga" and g.get("saga_manga", "naruto") == "naruto" and g.get("age", 0) <= 2 and not g.get("bijuu") and random.random() < .08, [("Accepter le destin", ev_bijuu_naissance), ("Le faire sceller ailleurs", lambda g: res(g, "🏥 Des spécialistes extraient la présence avant qu'elle ne s'éveille. Tu évites ce destin, mais ton chakra reste ordinaire.", chakra=-8, sante=-4))])
event("bijuu_scellage", "Le scellement du dernier recours", "🔥 Une attaque ravage le village. Un bijū est sur le point de s'échapper ; les sceaux s'effondrent et les anciens n'ont qu'une solution : te choisir comme réceptacle.", lambda g: g.get("univers") == "manga" and g.get("saga_manga", "naruto") == "naruto" and g.get("age", 0) >= 8 and not g.get("bijuu") and random.random() < .12, [("Accepter le scellement", ev_bijuu_scellage), ("Refuser et fuir", lambda g: res(g, "🏃 Tu refuses et aides les civils à évacuer. Le village est sauvé de justesse, mais certains te reprochent d'avoir fui ton devoir.", karma=4, sante=-8, bonheur=-4))])
event("bijuu_voix", "La voix derrière le sceau", "🦊 Dans tes rêves, le bijū t'offre un choix : apprendre à vous comprendre, le dominer par la force ou renforcer le sceau.", lambda g: g.get("univers") == "manga" and g.get("saga_manga", "naruto") == "naruto" and bool(g.get("bijuu")) and g.get("age", 0) >= 10 and random.random() < .35, [("L'écouter", ev_bijuu_apaiser), ("Le dominer", ev_bijuu_dominer), ("Renforcer le sceau", ev_bijuu_refuser)])
event("sharingan_vole", "Un œil sur le champ de bataille", "👁️ Après une bataille, tu découvres un Sharingan encore intact. Le prendre serait une transgression grave, mais ce pouvoir pourrait changer ton destin.", lambda g: g.get("univers") == "manga" and g.get("saga_manga", "naruto") == "naruto" and g.get("age", 0) >= 14 and g.get("sharingans_voles", 0) == 0 and g.get("clan") != "Uchiha" and random.random() < .20, [("Voler le Sharingan", ev_vol_sharingan), ("Respecter le défunt", ev_sharingan_refuser)])
event("akatsuki_recrutement", "Une cape aux nuages rouges", "☁️ Un inconnu t'attend sur un toit, une cape noire brodée de nuages rouges sur les épaules. « Le village te limite. Avec nous, tu pourrais changer le monde. »", lambda g: g.get("univers") == "manga" and g.get("saga_manga", "naruto") == "naruto" and g.get("age", 0) >= 16 and not g.get("akatsuki") and (g.get("victoires_combat", 0) >= 1 or g.get("stats", {}).get("force", 0) >= 60) and random.random() < .35, [("Rejoindre l'Akatsuki", ev_akatsuki_rejoindre), ("Refuser l'offre", ev_akatsuki_refuser)])
event("heritage_clan", "L'héritage oublié du clan", "🧬 Un ancien rouleau apparaît dans les archives de ta famille. Il porte le sceau de ton clan et une technique que l'on croyait perdue.", lambda g: g.get("univers") == "manga" and g.get("saga_manga", "naruto") == "naruto" and g.get("age", 0) >= 8 and g.get("clan") in ("Uchiha", "Hyûga", "Senju", "Uzumaki", "Nara", "Akimichi", "Aburame") and random.random() < .3, [("Étudier le rouleau", ev_clan_heritage), ("Le remettre aux archives", lambda g: res(g, "📚 Tu confies le rouleau aux anciens. Ils te remercient et promettent de te former plus tard.", karma=4, intelligence=3))])
event("mission_ninja_rare", "Mission classée confidentielle", "📜 Le conseil te confie une mission sans détails : récupérer un rouleau avant qu'une organisation ennemie ne l'obtienne. Ton équipe te regarde, en attendant ta décision.", lambda g: g.get("univers") == "manga" and g.get("saga_manga", "naruto") == "naruto" and g.get("age", 0) >= 12 and g.get("metier") in ("ninja", "anbu", "sensei_ninja", "medecin_ninja", "ninja_chercheur", "kage") and random.random() < .35, [("Accepter la mission", ev_mission_ninja), ("Refuser sans explication", lambda g: res(g, "🫥 Tu refuses la mission. Le conseil respecte ta prudence, mais ta loyauté sera réévaluée.", karma=-2, bonheur=1))])

# Deux événements narratifs par métier : réussite/opportunité et crise à choix.
# Ils sont générés depuis la liste réelle des métiers afin de couvrir chaque poste disponible.
for _job_key, _job in list(JOBS.items()):
    def _cond_metier(g, key=_job_key):
        return g.get("metier") == key and g.get("age", 0) >= 16
    def _choix_metier_succes(g, key=_job_key):
        return ev_metier_succes(g, key)
    def _choix_metier_reparer(g, key=_job_key):
        return ev_metier_choix_reparer(g, key)
    def _choix_metier_cacher(g, key=_job_key):
        return ev_metier_choix_cacher(g, key)
    def _choix_metier_opportunite(g, key=_job_key):
        return ev_metier_opportunite(g, key)
    event(f"metier_{_job_key}_crise", f"Une crise dans ton métier : {_job['nom']}", f"🚨 Dans ton poste de {_job['nom'].lower()}, une situation imprévue menace ta réputation. Une erreur a été repérée ; tu peux l'assumer ou tenter de la dissimuler.", _cond_metier, [("Assumer et réparer", _choix_metier_reparer), ("Cacher les preuves", _choix_metier_cacher)])
    event(f"metier_{_job_key}_chance", f"Une occasion inattendue : {_job['nom']}", f"✨ Dans ton poste de {_job['nom'].lower()}, un événement exceptionnel te donne l'occasion de te démarquer. Un client, un collègue ou un supérieur te propose de prendre les choses en main.", _cond_metier, [("Saisir l'occasion", _choix_metier_opportunite), ("Rester prudent·e", lambda g, key=_job_key: res(g, f"Tu évites les risques dans ton poste de {JOBS[key]['nom'].lower()}, mais la chance passe à quelqu'un d'autre.", bonheur=1, intelligence=1))])
    event(f"metier_{_job_key}_promotion", f"Une promotion possible : {_job['nom']}", f"📈 Dans ton poste de {_job['nom'].lower()}, une place se libère. Ton supérieur te demande si tu veux prendre plus de responsabilités.", _cond_metier, [("Accepter les responsabilités", lambda g, key=_job_key: ev_metier_opportunite(g, key)), ("Refuser pour préserver ton équilibre", lambda g: res(g, "Tu refuses la promotion pour préserver ton temps libre. Tu te sens plus serein·e.", bonheur=4, sante=2))])
    event(f"metier_{_job_key}_conflit", f"Un conflit au travail : {_job['nom']}", f"🤝 Dans ton poste de {_job['nom'].lower()}, un désaccord éclate avec un collègue ou un partenaire. Tu dois choisir comment désamorcer la situation.", _cond_metier, [("Chercher un compromis", lambda g: res(g, "Tu prends le temps d'écouter les deux parties. La tension baisse et ton professionnalisme est remarqué.", reputation=4, karma=3)), ("Imposer ton point de vue", lambda g: res(g, "Tu imposes ta décision. Le problème est réglé rapidement, mais certains collègues t'en veulent.", reputation=-2, force=2))])
    event(f"metier_{_job_key}_formation", f"Une formation inattendue : {_job['nom']}", f"📚 Une formation courte est proposée dans ton domaine. Elle peut améliorer tes compétences ou simplement te faire perdre du temps.", _cond_metier, [("Suivre la formation", lambda g: res(g, "Tu suis la formation et en ressors avec de nouvelles compétences.", intelligence=4, reputation=2)), ("Décliner", lambda g: res(g, "Tu déclines la formation pour te concentrer sur tes tâches habituelles.", bonheur=2))])



event("accident_temoin", "Le témoin d'un accident", "🚗 Tu arrives sur les lieux d'un accident. Une personne est blessée, un conducteur prend la fuite et plusieurs passants filment la scène. Ton choix sera raconté de différentes façons.", lambda g: g.get("age", 0) >= 12 and random.random() < .45, [("Porter secours", lambda g: res(g, "🚑 Tu aides les blessés jusqu'à l'arrivée des secours. Un témoin te remercie publiquement.", karma=7, bonheur=4, sante=-1)), ("Filmer pour les réseaux", lambda g: res(g, "📱 Ta vidéo devient virale, mais les commentaires t'accusent d'avoir regardé au lieu d'aider.", celebrite=5, karma=-8, bonheur=-3)), ("Partir sans intervenir", lambda g: (programmer_consequence(g, 4, "Le passé revient", "Une enquête retrouve ton visage sur une caméra. On te demande pourquoi tu n'as pas témoigné.", {"bonheur": -3}) or res(g, "🚶 Tu pars. Tu essaies d'oublier, mais une caméra a peut-être capté ton passage.", karma=-4)))])
event("heritage_inattendu", "Un héritage inattendu", "✉️ Un notaire t'apprend qu'un parent éloigné t'a laissé quelque chose. Mais la succession est contestée par un autre membre de la famille.", lambda g: g.get("age", 0) >= 18 and random.random() < .18, [("Accepter le compromis", lambda g: res(g, "⚖️ Tu signes un compromis et reçois une part de l'héritage, sans conflit interminable.", argent=random.randint(3000, 25000), famille_relations=3)), ("Contester la succession", lambda g: (programmer_consequence(g, 2, "Audience successorale", "Le litige revient devant le tribunal. Tu devras choisir entre une paix familiale et une victoire financière.", {"argent": 8000}) or res(g, "📂 Tu engages une procédure. Les frais s'accumulent, mais tu refuses de céder.", argent=-2000, intelligence=2)))])
event("message_anonyme", "Un message à 03 h 17", "📩 Un numéro inconnu t'envoie une photo de toi prise de loin, suivie d'une phrase : « Tu ne sais pas ce que tu as déclenché. »", lambda g: g.get("age", 0) >= 14 and random.random() < .3, [("Remonter la piste", lambda g: res(g, "🔎 Tu identifies un ancien contact qui cherchait à t'intimider. Tu gardes les preuves et changes tes habitudes.", intelligence=4, bonheur=-2, karma=2)), ("Bloquer le numéro", lambda g: (programmer_consequence(g, 3, "Le numéro inconnu rappelle", "Le même contact réapparaît avec une information compromettante.", {"bonheur": -4}) or res(g, "📵 Tu bloques le numéro et refuses d'entrer dans son jeu.", bonheur=2)))])
event("ami_dette", "La dette d'un proche", "💸 Un proche te demande une grosse somme, en jurant que ce n'est que pour quelques semaines. Tu as économisé cet argent pour un projet personnel.", lambda g: g.get("age", 0) >= 18 and g.get("argent", 0) >= 1500 and random.random() < .25, [("Prêter l'argent", lambda g: (programmer_consequence(g, 2, "Remboursement promis", "Ton proche revient avec une partie de la somme… ou une nouvelle excuse.", {"argent": random.choice([-1200, 800])}) or res(g, "🤝 Tu lui prêtes une partie de tes économies. La confiance est désormais en jeu.", argent=-1500, karma=4)), ("Refuser", lambda g: res(g, "🧱 Tu refuses de mettre ton projet en danger. Le proche dit comprendre, mais prend ses distances.", karma=-2, bonheur=-2)))])
event("erreur_virale", "Une vidéo de toi devient virale", "📹 Une vidéo sortie de son contexte explose sur les réseaux. Les inconnus te jugent avant même d'écouter ta version.", lambda g: g.get("age", 0) >= 13 and random.random() < .3, [("Répondre calmement", lambda g: res(g, "🎙️ Tu publies une réponse posée et les réactions se divisent. Tu gagnes en maturité, sans convaincre tout le monde.", celebrite=3, intelligence=2, bonheur=-1)), ("Répliquer violemment", lambda g: res(g, "💥 Ta réponse fait encore plus de vues, mais le conflit enfle et tes proches te demandent de t'arrêter.", celebrite=7, karma=-6, bonheur=-5)), ("Ignorer", lambda g: res(g, "🔕 Tu refuses de nourrir le drama. La polémique finit par passer, mais certaines personnes gardent leur version.", bonheur=3))])
event("offre_risque", "L'offre qui paraît trop belle", "🧾 Un inconnu promet de doubler ton argent en quelques jours. Il te montre des captures d'écran et insiste pour que tu décides ce soir.", lambda g: g.get("age", 0) >= 18 and g.get("argent", 0) >= 500 and random.random() < .25, [("Investir une petite somme", lambda g: res(g, "📉 L'investissement s'effondre : tu perds une partie de tes économies. Tu as appris à vérifier les promesses.", argent=-min(g["argent"], 500), intelligence=3, bonheur=-3)), ("Tout refuser", lambda g: res(g, "🛡️ Tu refuses et signales l'offre. Quelques jours plus tard, d'autres victimes racontent leur histoire.", karma=5, intelligence=2))])
event("secret_famille", "La vérité dans une vieille boîte", "📦 En rangeant le grenier, tu trouves des lettres qui contredisent tout ce qu'on t'a raconté sur ta famille. Quelqu'un te supplie de ne pas les lire.", lambda g: g.get("age", 0) >= 15 and random.random() < .22, [("Lire les lettres", lambda g: res(g, "🕯️ Tu découvres un secret ancien. Tu comprends mieux un proche, mais tu ne peux plus faire comme si tu ne savais rien.", intelligence=4, bonheur=-4, karma=1)), ("Les rendre sans les lire", lambda g: (programmer_consequence(g, 5, "Le secret se fissure", "Un autre membre de la famille révèle enfin une partie de l'histoire.", {"famille_relations": 5}) or res(g, "🤐 Tu respectes la demande. La confiance est préservée, mais les questions restent.", famille_relations=4, karma=3)))])
event("urgence_hopital", "Une nuit aux urgences", "🏥 Une personne que tu connais est transportée à l'hôpital. On te demande de prendre une décision rapidement, sans garantie sur le résultat.", lambda g: g.get("age", 0) >= 16 and random.random() < .2, [("Rester auprès d'elle", lambda g: res(g, "🫶 Tu restes toute la nuit. La personne se stabilise et se souvient de ta présence.", bonheur=5, karma=4, sante=-2)), ("Rentrer te reposer", lambda g: res(g, "🌙 Tu rentres pour être en état d'aider demain. Tu culpabilises, mais tu n'es pas infaillible.", sante=3, bonheur=-2))])
event("chantage", "Le chantage", "🕶️ Quelqu'un prétend avoir une preuve compromettante contre toi et réclame de l'argent. Tu ignores si la preuve est réelle.", lambda g: g.get("age", 0) >= 16 and g.get("argent", 0) >= 500 and random.random() < .22, [("Payer pour gagner du temps", lambda g: (programmer_consequence(g, 2, "Le maître-chanteur revient", "Le maître-chanteur réclame encore plus et menace de publier les preuves.", {"bonheur": -6}) or res(g, "💸 Tu paies, mais tu comprends vite que le silence s'achète rarement une seule fois.", argent=-500, bonheur=-2)), ("Refuser et conserver les preuves", lambda g: res(g, "📂 Tu refuses de payer et conserves les messages. La personne hésite quand elle comprend que tu peux porter plainte.", karma=3, intelligence=3)))])
event("sauvetage_heroique_urgence", "Un choix sous les décombres", "🚨 Une explosion secoue le quartier. Tu entends quelqu'un appeler à l'aide, tandis que des témoins te crient de reculer.", lambda g: g.get("univers") in ("real", "cyber") and g.get("age", 0) >= 16 and random.random() < .24, [("Entrer pour secourir", lambda g: res(g, "🦸 Tu sors une personne des décombres avant l'arrivée des secours. Ton courage est salué, mais tu es blessé·e.", karma=8, celebrite=4, sante=-8)), ("Coordonner les secours", lambda g: res(g, "📞 Tu sécurises la zone et guides les secours. Plusieurs vies sont sauvées grâce à ton sang-froid.", intelligence=3, karma=6, celebrite=2)), ("Ne pas prendre de risque", lambda g: res(g, "🛑 Tu gardes tes distances et alertes les secours. Tu évites une blessure, même si certains te jugent.", sante=2, bonheur=-1))])
event("manga_dilemme_prisonnier", "Le prisonnier connaît ton nom", "⛓️ Un ninja ennemi capturé affirme connaître l'emplacement d'un repaire secret. Il demande la liberté en échange des informations et semble connaître un secret sur ton clan.", lambda g: g.get("univers") == "manga" and g.get("age", 0) >= 12 and random.random() < .3, [("Négocier un échange", lambda g: res(g, "📜 Tu obtiens une piste utile sans libérer complètement le prisonnier. Le conseil garde un œil sur toi.", intelligence=4, karma=2, celebrite=2)), ("Le livrer aux interrogateurs", lambda g: res(g, "🔒 Les informations arrivent, mais le prisonnier te maudit. Une organisation ennemie pourrait s'en souvenir.", celebrite=3, karma=-4)), ("Le laisser s'échapper", lambda g: (programmer_consequence(g, 3, "Une dette de sang", "Le ninja libéré revient pour te remercier… ou t'entraîner dans un piège.", {"bonheur": -4}) or res(g, "🌫️ Tu le laisses partir. Tu espères qu'il tiendra parole.", karma=3, bonheur=1)))])


# ----------------------------------------------------------------------
# Recrutement héroïque, Jujutsu Kaisen, One Piece et vie sociale
# ----------------------------------------------------------------------
def ev_recruteur_araignee(g):
    g["origine_heroique"] = "Arachnide urbain"
    g["agence_heros"] = "Initiative des Gardiens"
    g["pouvoirs"] = list(dict.fromkeys(g.get("pouvoirs", []) + ["Sens du danger", "Adhérence murale", "Réflexes surhumains"]))
    g["niveau_pouvoir"] = max(g.get("niveau_pouvoir", 0), 10)
    programmer_consequence(g, 1, "L'invitation de l'agence", "Une recruteuse de l'Initiative des Gardiens t'invite à passer les tests officiels. Tu peux maintenant postuler à une carrière héroïque.", {"celebrite": 2})
    return res(g, "🕷️ Après une morsure étrange et une nuit de fièvre, tes réflexes deviennent impossibles. Une recruteuse t'observe et te propose de passer les tests de l'Initiative des Gardiens.", force=5, intelligence=2, bonheur=-2)

def ev_recruteur_armure(g):
    g["origine_heroique"] = "Armure technologique"
    g["agence_heros"] = "Initiative des Gardiens"
    g["pouvoirs"] = list(dict.fromkeys(g.get("pouvoirs", []) + ["Ingénierie", "Gadgets tactiques"]))
    g["niveau_pouvoir"] = max(g.get("niveau_pouvoir", 0), 8)
    programmer_consequence(g, 1, "Prototype confidentiel", "Un ingénieur de l'Initiative des Gardiens te recontacte pour un entretien et une candidature officielle.", {"intelligence": 2})
    return res(g, "🦾 Tu aides à sauver des civils lors d'un accident technologique. Une ingénieure milliardaire te propose un prototype d'armure et une place dans son programme de héros.", intelligence=6, celebrite=2)

def ev_recruteur_mutation(g):
    g["origine_heroique"] = "Mutation métamorphe"
    g["agence_heros"] = "Initiative des Gardiens"
    g["pouvoirs"] = list(dict.fromkeys(g.get("pouvoirs", []) + ["Mutation instable", "Métamorphose partielle"]))
    g["niveau_pouvoir"] = max(g.get("niveau_pouvoir", 0), 8)
    return res(g, "🧬 Un pouvoir se manifeste devant témoins. L'Initiative des Gardiens t'offre un accompagnement, à condition que tu apprennes à maîtriser tes capacités.", force=3, bonheur=-3, celebrite=1)

def ev_refuser_recrutement(g):
    programmer_consequence(g, 3, "Le recruteur revient", "L'Initiative des Gardiens n'a pas oublié ton potentiel. Une nouvelle crise pourrait te forcer à choisir.", {"bonheur": 1})
    return res(g, "🚪 Tu refuses l'offre. Tu gardes ta liberté, mais la porte de l'agence pourrait se rouvrir plus tard.", bonheur=2)

def ev_jjk_eveil(g):
    techniques = ["Poing divergent", "Manipulation du sang", "Technique des dix ombres", "Discours maudit", "Éclair noir"]
    tech = random.choice(techniques)
    if tech not in g.setdefault("techniques_maudites", []):
        g["techniques_maudites"].append(tech)
    if tech in JUTSU and tech not in g.setdefault("jutsu", []):
        g["jutsu"].append(tech)
    g["energie_occulte"] = min(100, g.get("energie_occulte", 0) + random.randint(20, 35))
    return res(g, f"👁️ Tu vois enfin les fléaux que personne d'autre ne distingue. Ton énergie occulte s'éveille et tu découvres : {tech}. L'école de Jujutsu pourrait te recruter.", intelligence=4, force=3, bonheur=-3)

def ev_jjk_recrutement(g):
    g["saga_manga"] = "jujutsu"
    g["ville"] = "Tokyo – École d'exorcisme 👁️"
    g["energie_occulte"] = max(20, g.get("energie_occulte", 0))
    return res(g, "🏯 Un exorciste de grade 1 te remet une invitation pour l'école de Tokyo. Tu peux désormais postuler comme exorciste de Jujutsu.", intelligence=3, karma=4)

def ev_fruit_demon(g):
    fruit = random.choice(["Gomu Gomu (fruit du caoutchouc)", "Mera Mera (fruit du feu)", "Ope Ope (fruit de l'opération)", "Bara Bara (fruit de la fragmentation)", "Suna Suna (fruit du sable)", "Hie Hie (fruit de la glace)", "Tori Tori (modèle phénix)", "Yami Yami (fruit des ténèbres)", "Goro Goro (fruit de la foudre)"])
    g["fruit_demon"] = fruit
    g["pouvoirs"] = list(dict.fromkeys(g.get("pouvoirs", []) + [fruit]))
    g["niveau_pouvoir"] = max(g.get("niveau_pouvoir", 0), 12)
    g["notoriete_manga"] = min(100, g.get("notoriete_manga", 0) + 8)
    return res(g, f"🍈 Tu manges un fruit du démon : **{fruit}**. Une capacité incroyable s'éveille… mais tu ne pourras plus nager. La Marine et les pirates pourraient bientôt entendre parler de toi.", force=5, celebrite=3, bonheur=4)

def ev_refuser_fruit(g):
    return res(g, "🍈 Tu refuses de manger ce fruit inconnu et le vends à un collectionneur. Tu préfères ne pas risquer de perdre la capacité de nager.", argent=random.randint(2500, 9000), intelligence=2)

def ev_recrutement_pirate(g):
    g["faction_manga"] = "Pirates"
    g["saga_manga"] = "onepiece"
    g["notoriete_manga"] = min(100, g.get("notoriete_manga", 0) + 8)
    return res(g, "🏴‍☠️ Un capitaine te propose une place à bord. Tu hisses les voiles et deviens pirate. Tes actes feront grimper ta prime et ta notoriété.", force=3, bonheur=4, karma=-3)

def ev_recrutement_marine(g):
    g["faction_manga"] = "Marine"
    g["saga_manga"] = "onepiece"
    g["notoriete_manga"] = min(100, g.get("notoriete_manga", 0) + 3)
    return res(g, "⚓ Tu prêtes serment à la Marine. Tu peux désormais postuler dans ses rangs et gravir les grades en protégeant les civils.", karma=5, intelligence=2)

def ev_recrutement_revolution(g):
    g["faction_manga"] = "Révolutionnaires"
    g["saga_manga"] = "onepiece"
    g["notoriete_manga"] = min(100, g.get("notoriete_manga", 0) + 5)
    return res(g, "🔥 Tu rejoins l'armée révolutionnaire. Tu aides à libérer des territoires sous le joug des tyrans, mais le Gouvernement mondial te recherche.", karma=6, celebrite=2)

def ev_rester_independant(g):
    g["faction_manga"] = "Indépendant·e"
    return res(g, "🧭 Tu refuses de prêter allégeance. Tu gardes le choix de rejoindre plus tard un équipage, la Marine ou les révolutionnaires.", intelligence=2, bonheur=2)

def ev_notoriete_empereur(g):
    g["notoriete_manga"] = min(100, g.get("notoriete_manga", 0) + random.randint(15, 25))
    if g.get("faction_manga") == "Pirates" and g["notoriete_manga"] >= 80:
        g["faction_manga"] = "Empereur des mers"
        return res(g, "👑 Le monde entier parle de toi. Après des victoires et des territoires conquis, la presse te proclame Empereur des mers. Ta prime explose et les autres Empereurs te surveillent.", celebrite=12, force=8, karma=-3)
    return res(g, "📰 Ta prime augmente et ton nom circule sur les mers. Tu n'es pas encore Empereur, mais plusieurs équipages commencent à te prendre au sérieux.", celebrite=5, force=3)

event("recrutement_agence_heroique", "Une recruteuse de l'Initiative des Gardiens", "🚨 Une équipe masquée vient de sauver la ville. Une recruteuse te remarque après un acte courageux, une invention ou un incident étrange. Elle te propose plusieurs voies : pouvoirs, armure ou entraînement officiel.", lambda g: g.get("univers") == "real" and g.get("age", 0) >= 12 and g.get("origine_heroique", "Aucune") == "Aucune" and g.get("stats", {}).get("karma", 0) >= 35 and random.random() < .32, [("🕷️ Accepter une mutation arachnide", ev_recruteur_araignee), ("🦾 Rejoindre le programme d'armure", ev_recruteur_armure), ("🧬 Suivre le programme mutant", ev_recruteur_mutation), ("🚪 Refuser l'offre", ev_refuser_recrutement)])
event("jjk_eveil_occult", "Le fléau sous le pont", "👁️ Sous un pont, une silhouette monstrueuse se nourrit de la peur des passants. Tu es la seule personne à la voir. Une voix te crie de ne surtout pas la regarder dans les yeux.", lambda g: g.get("univers") == "manga" and g.get("saga_manga") == "jujutsu" and g.get("age", 0) >= 8 and g.get("energie_occulte", 0) < 25 and random.random() < .55, [("Affronter le fléau", ev_jjk_eveil), ("Fuir et appeler à l'aide", lambda g: res(g, "🏃 Tu échappes au fléau et préviens les exorcistes. Une équipe arrive, mais l'incident te hante.", bonheur=-2, karma=3)), ("Sauver un autre élève", lambda g: (ev_jjk_eveil(g) + " Tu sauves aussi un élève, qui te doit désormais la vie."))])
event("jjk_recrutement_ecole", "Une invitation scellée", "🏯 Un exorciste remarque ton énergie occulte. Il te propose de rejoindre l'école de Jujutsu, mais t'avertit que les missions peuvent être mortelles.", lambda g: g.get("univers") == "manga" and g.get("energie_occulte", 0) >= 15 and g.get("metier") != "exorciste_jujutsu" and random.random() < .35, [("Accepter", ev_jjk_recrutement), ("Refuser pour l'instant", lambda g: (programmer_consequence(g, 2, "L'école rappelle", "L'école de Jujutsu te recontacte après une nouvelle apparition de fléau.", {"intelligence": 2}) or res(g, "📩 Tu refuses pour le moment, mais l'invitation reste valable.", bonheur=1)))])
event("onepiece_fruit_demon", "Un fruit étrange dans une caisse", "🍈 Après une tempête, une caisse s'échoue près du port. À l'intérieur, un fruit aux motifs impossibles. Un marin t'avertit : certains fruits donnent des pouvoirs, mais maudissent les mers.", lambda g: g.get("univers") == "manga" and g.get("saga_manga") == "onepiece" and not g.get("fruit_demon") and g.get("age", 0) >= 8 and random.random() < .45, [("Le manger", ev_fruit_demon), ("Le vendre", ev_refuser_fruit)])
event("onepiece_faction_choice", "Trois drapeaux à l'horizon", "⚓ Un capitaine pirate, une officière de la Marine et un agent révolutionnaire veulent te recruter. Chacun promet un avenir différent et te demande une réponse avant le lever du soleil.", lambda g: g.get("univers") == "manga" and g.get("saga_manga") == "onepiece" and g.get("age", 0) >= 14 and g.get("faction_manga", "Indépendant·e") == "Indépendant·e" and random.random() < .5, [("Rejoindre les pirates", ev_recrutement_pirate), ("Servir la Marine", ev_recrutement_marine), ("Rejoindre les révolutionnaires", ev_recrutement_revolution), ("Rester indépendant·e", ev_rester_independant)])
event("onepiece_empereur", "Le monde tremble devant ta prime", "📰 Après une série de batailles, de sauvetages et de territoires disputés, les journaux du monde entier parlent de toi. Les autres puissances veulent savoir si tu vas te cacher ou revendiquer ton influence.", lambda g: g.get("univers") == "manga" and g.get("saga_manga") == "onepiece" and g.get("faction_manga") in ("Pirates", "Empereur des mers") and g.get("notoriete_manga", 0) >= 35 and random.random() < .5, [("Défier les puissances", ev_notoriete_empereur), ("Protéger ton équipage", lambda g: res(g, "🛡️ Tu consolides tes alliances et protèges ton équipage. La notoriété progresse moins vite, mais tes alliés te font confiance.", karma=3, bonheur=4, celebrite=2))])
event("famille_sortie", "Tes parents te proposent une sortie", "🏡 Un de tes parents te propose une sortie au restaurant. Il/elle veut passer du temps avec toi, mais tu avais prévu autre chose.", lambda g: g.get("age", 0) >= 3 and any(p.get("vivant", True) for p in g.get("parents", [])) and random.random() < .3, [("Accepter la sortie", lambda g: (interaction_pnj(g, "parent", next((i for i,p in enumerate(g.get("parents",[])) if p.get("vivant",True)),0), "restaurant") if g.get("argent",0) >= int(250*ville_info(g)["cout"]) else res(g, "🥪 Vous improvisez un pique-nique. Ton parent apprécie que tu aies accepté.", bonheur=4, famille_relations=4))), ("Refuser poliment", lambda g: (programmer_consequence(g, 2, "Une invitation déclinée", "Ton parent se demande si tu as encore envie de passer du temps en famille.", {"famille_relations": -3}) or res(g, "📱 Tu déclines l'invitation. Ton parent comprend, mais semble déçu.", bonheur=1)))])
event("parent_colere", "Tes parents sont furieux", "📣 Un bulletin scolaire, une promesse oubliée ou un mensonge a mis le feu aux poudres. Tes parents veulent des explications.", lambda g: g.get("age", 0) >= 6 and any(p.get("vivant", True) for p in g.get("parents", [])) and (g.get("notes", 50) < 35 or g.get("stats", {}).get("karma", 50) < 25) and random.random() < .4, [("Assumer et promettre de faire mieux", lambda g: (g.update(famille_relations=clamp(g.get("famille_relations",65)+4)) or res(g, "🗣️ Tu reconnais tes erreurs. La dispute n'est pas oubliée, mais le ton redescend.", karma=3, bonheur=-1))), ("Répondre avec insolence", lambda g: (g.update(famille_relations=clamp(g.get("famille_relations",65)-10)) or res(g, "🚪 Tu claques la porte. Tes parents sont blessés et pourraient se montrer plus stricts.", karma=-4, bonheur=-4))), ("Mentir", lambda g: (programmer_consequence(g, 2, "Le mensonge éclate", "Tes parents découvrent la vérité et la confiance en prend un coup.", {"famille_relations": -8}) or res(g, "🤥 Tu inventes une excuse. Pour l'instant, ils te croient.", karma=-3, bonheur=1)))])
event("dispute_fratrie", "Une dispute avec ton frère ou ta sœur", "🎮 Une affaire de chambre, de jalousie ou de console tourne au conflit. Ton frère ou ta sœur te provoque devant tout le monde.", lambda g: g.get("age", 0) >= 5 and bool(g.get("fratrie")) and random.random() < .32, [("En parler calmement", lambda g: (g["fratrie"][0].update(relation=clamp(g["fratrie"][0].get("relation",60)+6)) or res(g, "💬 Vous finissez par vous comprendre. Vous n'êtes pas d'accord sur tout, mais vous vous rapprochez.", bonheur=2, karma=2))), ("Riposter", lambda g: (g["fratrie"][0].update(relation=clamp(g["fratrie"][0].get("relation",60)-12)) or res(g, "💢 La dispute dégénère et chacun va se plaindre aux parents.", bonheur=-3, karma=-2))), ("L'ignorer", lambda g: res(g, "🎧 Tu t'éloignes. La tension retombe, mais le problème n'est pas vraiment réglé.", bonheur=1))])
event("sortie_amis", "Une invitation de dernière minute", "📲 Tes amis organisent une sortie ce soir. L'un veut aller au cinéma, l'autre veut explorer un lieu interdit. Tu dois choisir avec qui partir.", lambda g: g.get("age", 0) >= 8 and bool(g.get("amis")) and random.random() < .35, [("Sortie tranquille", lambda g: (g["amis"][0].update(relation=clamp(g["amis"][0].get("relation",50)+10)) or res(g, "🍕 Vous mangez ensemble, riez et prenez des photos. Un souvenir de plus dans votre histoire.", bonheur=5, karma=2))), ("Suivre l'idée risquée", lambda g: (g["amis"][0].update(relation=clamp(g["amis"][0].get("relation",50)+6)) or res(g, "🌃 L'aventure tourne presque mal, mais vous vous en sortez. Votre amitié devient plus intense.", bonheur=3, force=2, karma=-2))), ("Rester chez toi", lambda g: (programmer_consequence(g, 2, "Tu as manqué la sortie", "Tes amis reparlent de cette soirée et se demandent si tu t'éloignes d'eux.", {"bonheur": -2}) or res(g, "🏠 Tu restes chez toi. Tu te reposes, mais tu rates un moment qui comptera pour eux.", sante=2)))])


def ev_fantasy_guilde(g, faction):
    g["faction_fantasy"] = faction
    g["renommee_fantasy"] = min(100, g.get("renommee_fantasy", 0) + 10)
    return res(g, f"🏰 Tu rejoins {faction}. On te confie tes premières missions et tes choix détermineront si tu deviens une légende ou une menace pour le royaume.", force=3, intelligence=3, celebrite=2)

def ev_fantasy_renoncer(g):
    return res(g, "🧭 Tu refuses de rejoindre une faction. Tu restes libre, mais les guildes ne te feront pas automatiquement confiance.", bonheur=2, intelligence=2)

def ev_fantasy_renommee(g):
    g["renommee_fantasy"] = min(100, g.get("renommee_fantasy", 0) + random.randint(10, 18))
    if g["renommee_fantasy"] >= 80 and g.get("faction_fantasy") == "Ordre des chevaliers":
        return res(g, "👑 Tes exploits te valent le titre de Champion·ne du royaume. Le souverain t'offre un domaine et te confie la défense de la couronne.", argent=12000, celebrite=12, karma=5)
    return res(g, f"📜 Une nouvelle chanson raconte tes exploits. Ta renommée atteint {g['renommee_fantasy']}/100.", argent=random.randint(500, 4000), celebrite=4, karma=2)

event("fantasy_choix_faction", "Trois factions te font une offre", "🏰 Dans une auberge, trois émissaires t'abordent : un chevalier royal, une archimage et un capitaine corsaire. Chacun affirme que le royaume a besoin de toi. Tu dois choisir ton allégeance.", lambda g: g.get("univers") == "fantasy" and g.get("age", 0) >= 12 and g.get("faction_fantasy", "Aucune") == "Aucune" and random.random() < .5, [("Rejoindre l'ordre des chevaliers", lambda g: ev_fantasy_guilde(g, "Ordre des chevaliers")), ("Rejoindre le cercle des mages", lambda g: ev_fantasy_guilde(g, "Cercle des mages")), ("Devenir corsaire", lambda g: ev_fantasy_guilde(g, "Corsaires")), ("Refuser les trois offres", ev_fantasy_renoncer)])
event("fantasy_dragon_pacte", "Le dragon te propose un pacte", "🐉 Un dragon ancien bloque le col et connaît ton nom. Il te propose une alliance : puissance et richesse contre une faveur future. Les villageois te supplient de le tuer.", lambda g: g.get("univers") == "fantasy" and g.get("age", 0) >= 14 and random.random() < .28, [("Signer le pacte", lambda g: (programmer_consequence(g, 4, "La faveur du dragon", "Le dragon réclame le service promis. Refuser pourrait transformer un allié en ennemi.", {"bonheur": -3}) or res(g, "🐲 Tu signes le pacte. Le dragon te donne une écaille enchantée et une part de son trésor.", argent=10000, force=5, celebrite=4, karma=-3))), ("Défendre les villageois", lambda g: res(g, "🛡️ Tu affrontes le dragon pour protéger le col. Le combat est terrible, mais les habitants se souviendront de ton courage.", force=5, karma=8, sante=-10, celebrite=5)), ("Négocier sans serment", lambda g: res(g, "🗣️ Tu obtiens un passage sûr sans céder ton avenir. Le dragon respecte ta prudence.", intelligence=4, karma=3))])
event("fantasy_renommee", "Une couronne sans héritier", "👑 Le souverain est malade et les grandes maisons se disputent la succession. Tes actes passés sont évoqués devant le conseil. On te demande de soutenir un candidat ou de réclamer une place pour toi.", lambda g: g.get("univers") == "fantasy" and g.get("age", 0) >= 18 and g.get("renommee_fantasy", 0) >= 25 and random.random() < .35, [("Soutenir le peuple", lambda g: (g.update(renommee_fantasy=min(100,g.get("renommee_fantasy",0)+10)) or res(g, "📣 Tu défends une succession qui protège les villages. Le peuple scande ton nom.", karma=7, celebrite=5))), ("Soutenir un noble puissant", lambda g: res(g, "💰 Le noble te récompense et promet une place à la cour. Certains te trouvent opportuniste.", argent=9000, karma=-4, celebrite=3)), ("Réclamer le pouvoir", ev_fantasy_renommee)])


def ev_jjk_vow(g):
    g["energie_occulte"] = min(100, g.get("energie_occulte", 0) + 18)
    chg(g, force=5, bonheur=-3)
    programmer_consequence(g, 3, "Le prix du pacte", "Le pacte occulte que tu as accepté réclame son prix. Une nouvelle condition apparaît.", {"sante": -4})
    return "🩸 Tu conclus un pacte contraignant : ta puissance augmente, mais une règle inconnue pèsera sur tes choix futurs."

def ev_jjk_refuser_vow(g):
    chg(g, karma=4, bonheur=2)
    return "🛑 Tu refuses de sacrifier une partie de toi-même pour plus de puissance. L'exorciste respecte ta décision."

def ev_naruto_mission_village(g, choix):
    if choix == "alliance":
        g["reputation"] = clamp(g.get("reputation", 50) + 8)
        return res(g, "🤝 Tu proposes une alliance entre villages. Les anciens restent méfiants, mais une nouvelle route diplomatique s'ouvre.", karma=6, intelligence=3)
    if choix == "defection":
        g["statut_ninja"] = "Déserteur·se"
        g["reputation"] = clamp(g.get("reputation", 50) - 10)
        programmer_consequence(g, 2, "Chasse aux déserteurs", "Ton ancien village envoie une équipe pour te ramener ou t'éliminer.", {"bonheur": -3, "sante": -4})
        return res(g, "🌑 Tu abandonnes ton village. Tu gagnes en liberté, mais ton bandeau devient un symbole de trahison.", karma=-8, celebrite=5)
    return res(g, "🍃 Tu restes fidèle à ton village et refuses de laisser les tensions te manipuler.", karma=4, bonheur=2)

def ev_onepiece_noyade(g):
    if g.get("fruit_demon"):
        return res(g, f"🌊 Tu tombes à l'eau avec ton fruit du démon ({g['fruit_demon']}). Ton corps devient lourd et tu ne peux plus nager. Un allié doit te sauver.", sante=-12, bonheur=-4, karma=2)
    return res(g, "🌊 Tu plonges pour secourir un marin tombé à la mer. Tu le ramènes à bord et gagnes le respect de l'équipage.", karma=5, force=2, bonheur=3)

event("jjk_pacte_contraignant", "Le pacte contraignant", "🩸 Un exorciste blessé t'explique qu'un pacte peut décupler ton énergie occulte, mais que toute promesse rompue aura un prix. Il te propose un pacte personnel.", lambda g: g.get("univers") == "manga" and g.get("saga_manga") == "jujutsu" and g.get("energie_occulte", 0) >= 15 and random.random() < .28, [("Accepter le pacte", ev_jjk_vow), ("Refuser", ev_jjk_refuser_vow)])
event("naruto_conseil_villages", "Le conseil des cinq villages", "🍃 Une crise menace l'équilibre entre les villages cachés. Des émissaires te demandent de défendre ton village, de négocier une alliance ou de quitter le système ninja.", lambda g: g.get("univers") == "manga" and g.get("saga_manga", "naruto") == "naruto" and g.get("age", 0) >= 12 and random.random() < .3, [("Rester loyal·e", lambda g: ev_naruto_mission_village(g, "loyal")), ("Négocier une alliance", lambda g: ev_naruto_mission_village(g, "alliance")), ("Déserter", lambda g: ev_naruto_mission_village(g, "defection"))])
event("onepiece_eau", "Un homme à la mer", "🌊 Une vague énorme emporte un membre de l'équipage. Le navire tangue, les cordages claquent et tout le monde crie des ordres contradictoires.", lambda g: g.get("univers") == "manga" and g.get("saga_manga") == "onepiece" and g.get("age", 0) >= 8 and random.random() < .3, [("Plonger pour le sauver", ev_onepiece_noyade), ("Lancer une bouée", lambda g: res(g, "🪢 Tu jettes une bouée et coordonnes le sauvetage. L'homme est ramené à bord sans que tu risques ta vie.", karma=4, intelligence=2)), ("Protéger le navire", lambda g: res(g, "⚓ Tu sécurises les voiles et évites que le navire se retourne. L'homme est sauvé par un autre marin, mais tu as protégé tout l'équipage.", force=2, karma=2))])


# ----------------------------------------------------------------------
# Actualités mondiales dynamiques : crises, guerres, paix et bouleversements
# ----------------------------------------------------------------------
def actualite_monde(g, titre, texte):
    """Conserve les grands événements du monde dans la chronologie de la partie."""
    item = {"age": g.get("age", 0), "titre": titre, "texte": texte, "type": "evenement"}
    g.setdefault("actualites_monde", []).append(item)
    g["actualites_monde"] = g["actualites_monde"][-30:]
    log(g, f"🌍 ACTUALITÉ MONDIALE — {titre} : {texte}")
    g.setdefault("chronologie_famille", []).append({"age": g.get("age", 0), "titre": titre, "texte": texte})


WORLD_EVENT_IDS = {
    "monde_guerre", "monde_paix", "monde_devise", "monde_independance", "monde_attentat", "monde_gang", "monde_arrestations", "monde_president",
    "naruto_hokage_mort", "naruto_akatsuki_war", "naruto_kazekage_manipule", "naruto_peace_treaty",
    "jjk_fléau_majeur", "jjk_crise_ecole", "onepiece_offensive_marine", "onepiece_independence",
    "fantasy_guerre", "fantasy_paix", "fantasy_dragon_capitale", "fantasy_nouvelle_monnaie",
}

# Certains métiers sont directement concernés : l'événement devient une mission
# à laquelle le personnage doit participer, sans lui donner automatiquement
# le pouvoir de décider de la politique de tout le monde.
ROLE_EVENTS = {
    "monde_attentat": {"policier", "heros_pro", "heros_energie", "heroine_soins", "chasseur_anomalies", "gardien_dimension"},
    "monde_gang": {"policier", "detective", "enqueteur", "justicier_armure"},
    "monde_arrestations": {"policier", "detective", "enqueteur"},
    "naruto_hokage_mort": {"ninja", "sensei_ninja", "medecin_ninja", "ninja_chercheur"},
    "naruto_akatsuki_war": {"ninja", "sensei_ninja", "medecin_ninja", "ninja_chercheur"},
    "naruto_kazekage_manipule": {"ninja", "sensei_ninja", "ninja_chercheur"},
    "naruto_peace_treaty": {"ninja", "sensei_ninja"},
    "jjk_fléau_majeur": {"exorciste_jujutsu"},
    "jjk_crise_ecole": {"exorciste_jujutsu"},
    "onepiece_offensive_marine": {"pirate", "marine", "revolutionnaire", "chasseur_primes"},
    "onepiece_independence": {"pirate", "marine", "revolutionnaire"},
    "fantasy_guerre": {"chevalier", "mage", "corsaire"},
    "fantasy_paix": {"chevalier", "mage", "corsaire"},
    "fantasy_dragon_capitale": {"chevalier", "mage", "corsaire"},
}

def importance_personnage(g):
    """Mesure narrative de l'influence du personnage (pas une statistique affichée)."""
    score = 0
    metier = g.get("metier")
    if metier and metier in JOBS:
        score += int(g.get("grade", 0)) * 18
        if JOBS[metier].get("cat") == "Métier rare":
            score += 8
    score += max(0, int(g.get("reputation", 50)) - 50) // 2
    score += max(0, int(g.get("stats", {}).get("celebrite", 0)) - 35) // 2
    if g.get("faction_manga") in ("Empereur des mers", "Chef·fe révolutionnaire"):
        score += 35
    if g.get("rang_ninja") in ("Jōnin", "Kage"):
        score += 25
    if g.get("faction_fantasy") in ("Ordre des Chevaliers", "Cercle des Mages") and g.get("renommee_fantasy", 0) >= 60:
        score += 15
    return score

def est_concerne_par_evenement(g, eid):
    metier = g.get("metier")
    if metier in ROLE_EVENTS.get(eid, set()):
        # Les missions de métier concernent le personnage même à un grade modeste.
        return True, "mission"
    if importance_personnage(g) >= 35:
        return True, "influence"
    return False, "spectateur"

def generer_breve_informative(g):
    """Ajoute une brève d'actualité de fond chaque année, sans choix à faire."""
    univers = g.get("univers", "real")
    saga = g.get("saga_manga", "naruto")
    breves = {
        "real": [
            ("Économie", "Les économistes débattent d'une hausse des prix et des mesures pour soutenir les ménages."),
            ("Diplomatie", "Deux pays annoncent de nouvelles négociations commerciales après plusieurs mois de tensions."),
            ("Science", "Une équipe de recherche annonce une avancée médicale qui devra encore être confirmée par d'autres études."),
            ("Politique", "Un projet de réforme divise les partis et fait la une des journaux."),
            ("Société", "Une mobilisation citoyenne attire l'attention sur le logement et le coût de la vie."),
            ("Climat", "Des intempéries perturbent les transports dans plusieurs régions et les autorités appellent à la prudence."),
            ("Culture", "Un événement culturel international attire des visiteurs et fait rayonner plusieurs artistes."),
            ("Justice", "Une décision de justice relance le débat public sur les libertés et les responsabilités."),
        ],
        "naruto": [
            ("Vie des villages", "Les villages cachés renouvellent leurs accords commerciaux et renforcent les patrouilles aux frontières."),
            ("Conseil des Kage", "Les Kage débattent d'un partage de renseignements pour prévenir une nouvelle crise."),
            ("Missions ninja", "Une hausse des missions de rang C est signalée dans plusieurs villages."),
            ("Clans", "Un différend entre deux clans est soumis à une médiation afin d'éviter une escalade."),
            ("Sécurité", "Des rumeurs circulent sur des déplacements suspects près d'une frontière, sans confirmation officielle."),
        ],
        "jujutsu": [
            ("Monde occulte", "Les écoles d'exorcisme signalent une variation de l'énergie occulte dans plusieurs régions."),
            ("Conseil des anciens", "Les dirigeants débattent de nouvelles règles pour les exorcistes après plusieurs incidents."),
            ("Fléaux", "Des apparitions mineures sont signalées, mais aucune menace de classe spéciale n'est confirmée."),
            ("Écoles", "Tokyo et Kyoto organisent un échange d'informations entre leurs équipes."),
        ],
        "onepiece": [
            ("Grand Line", "Des routes maritimes changent après des tempêtes et plusieurs équipages cherchent un passage sûr."),
            ("Gouvernement mondial", "Le Gouvernement mondial annonce de nouvelles mesures de contrôle des ports."),
            ("Primes", "De nouvelles affiches de primes circulent dans les ports, sans changement concernant ton équipage."),
            ("Révolutionnaires", "Des rumeurs d'activité révolutionnaire circulent sur plusieurs îles, sans confirmation officielle."),
            ("Commerce maritime", "Les marchands signalent une hausse du prix des vivres sur certaines routes."),
        ],
        "fantasy": [
            ("Vie des royaumes", "Les guildes négocient des droits de passage et des tarifs pour les caravanes."),
            ("Cour royale", "Le conseil royal débat d'une réforme des impôts et du financement des remparts."),
            ("Magie", "Des érudits publient un rapport sur des phénomènes magiques inhabituels, encore inexpliqués."),
            ("Routes commerciales", "Des marchands signalent des bandits sur une route secondaire et recommandent une escorte."),
            ("Diplomatie", "Deux royaumes échangent des ambassadeurs pour éviter un conflit frontalier."),
        ],
    }
    key = saga if univers == "manga" else univers
    titre, texte = random.choice(breves.get(key, breves["real"]))
    item = {"age": g.get("age", 0), "titre": titre, "texte": texte, "type": "information"}
    g.setdefault("actualites_monde", []).append(item)
    g["actualites_monde"] = g["actualites_monde"][-30:]


def afficher_actualites_accueil(g):
    st.markdown("<div class='world-feed-title'>🌍 CE QUI SE PASSE DANS LE MONDE</div>", unsafe_allow_html=True)
    recentes = g.get("actualites_monde", [])[-3:]
    if not recentes:
        st.caption("Les nouvelles du monde apparaîtront ici au fil de ta vie.")
    else:
        for item in reversed(recentes):
            type_item = item.get("type", "evenement")
            badge = "📰 Information" if type_item == "information" else ("🚨 Participation requise" if type_item == "mission" else "🌍 Événement mondial")
            with st.container(border=True):
                st.markdown(f"<div style='color:#93c5fd;font-size:.76rem;font-weight:800;letter-spacing:.04em;margin-bottom:4px'>{badge} · À {item.get('age', g.get('age', 0))} ans</div>", unsafe_allow_html=True)
                st.markdown(f"**{item['titre']}**")
                st.write(item["texte"])
    score = importance_personnage(g)
    if score < 35 and not (g.get("metier") in set().union(*ROLE_EVENTS.values())):
        st.caption("Tu es spectateur·rice des grandes décisions : les dirigeants, chefs et hauts gradés décident. Tu peux suivre les conséquences dans les actualités.")
    elif score >= 35:
        st.caption("Ton influence te permet parfois de peser sur les décisions du monde.")
    else:
        st.caption("Ton métier peut t'impliquer directement dans certaines missions, même si tu ne décides pas de la stratégie globale.")


def ev_real_war(g, choice):
    g.setdefault("etat_monde", {})["conflit_international"] = True
    actualite_monde(g, "Une guerre éclate entre deux puissances", "Les frontières se ferment, les marchés chutent et une crise humanitaire s'aggrave.")
    if choice == "aide":
        return res(g, "🕊️ Tu aides une association humanitaire. Le danger reste loin de toi, mais la crise te touche profondément.", karma=8, bonheur=-2, celebrite=2, argent=-min(g.get("argent",0), 300))
    if choice == "manif":
        return res(g, "📣 Tu participes à une manifestation pour un cessez-le-feu. Le débat divise le pays.", karma=5, bonheur=2, reputation=3)
    return res(g, "🛡️ Tu évites les zones de rassemblement et suis les consignes de sécurité. Tu te protèges, sans pouvoir ignorer les nouvelles.", bonheur=1, sante=2)

def ev_real_peace(g, choice):
    g.setdefault("etat_monde", {})["conflit_international"] = False
    actualite_monde(g, "Accord de paix historique", "Après des négociations tendues, les belligérants signent un cessez-le-feu et ouvrent des couloirs humanitaires.")
    if choice == "celebrer":
        return res(g, "🕊️ Tu célèbres l'accord et soutiens les associations de reconstruction.", bonheur=8, karma=5, reputation=2)
    return res(g, "📰 Tu restes prudent·e : un accord est signé, mais sa mise en œuvre prendra du temps.", intelligence=2, bonheur=2)

def ev_real_currency(g, choice):
    old = g.get("monnaie_monde", "Euro")
    new = "Nouvel euro" if old != "Nouvel euro" else "Euro"
    g["monnaie_monde"] = new
    actualite_monde(g, "Réforme monétaire annoncée", f"Une réforme monétaire est votée. La devise de référence de ta partie passe de {old} à {new}; les prix et les contrats seront progressivement convertis.")
    if choice == "epargner":
        return res(g, "🏦 Tu places une partie de ton argent sur un compte sécurisé pendant la transition.", bonheur=1, intelligence=3)
    if choice == "investir":
        return res(g, "📈 Tu diversifies tes placements. Le risque est réel, mais tu pourrais profiter de la transition.", argent=random.randint(-500, 1200), intelligence=2)
    return res(g, "🛒 Tu gardes tes habitudes et surveilles les prix. Les commerçants affichent les deux montants pendant quelques mois.", bonheur=1)

def ev_real_independence(g, choice):
    g.setdefault("etat_monde", {})["mouvement_independance"] = True
    actualite_monde(g, "Un territoire déclare son indépendance", "Un vote contesté et des manifestations massives ouvrent une crise constitutionnelle. Les pays étrangers hésitent à reconnaître le nouvel État.")
    if choice == "dialogue":
        return res(g, "🤝 Tu soutiens des négociations et le respect des civils.", karma=6, intelligence=3, bonheur=1)
    if choice == "manif":
        return res(g, "📣 Tu participes à un rassemblement pacifique. Les opinions sont très divisées.", reputation=2, karma=2, bonheur=2)
    return res(g, "📰 Tu suis la situation à distance et attends de voir si l'indépendance sera reconnue.", intelligence=2)

def ev_real_attack(g, choice):
    actualite_monde(g, "Attentat déjoué après une alerte", "Une attaque visant un lieu public est déjouée. Le pays est sous le choc et les autorités renforcent la sécurité.")
    if choice == "secours":
        return res(g, "🚑 Tu donnes un coup de main aux secours en suivant leurs instructions.", karma=7, bonheur=-3, celebrite=1)
    if choice == "alerter":
        return res(g, "📞 Tu transmets une information utile aux autorités. Elle contribue à sécuriser le périmètre.", karma=5, intelligence=2)
    return res(g, "🏠 Tu t'éloignes de la zone et vérifies que tes proches sont en sécurité.", bonheur=-2, sante=2)

def ev_real_gang(g, choice):
    g.setdefault("etat_monde", {})["nouveau_gang"] = "Les Loups Gris"
    actualite_monde(g, "Un nouveau gang fait parler de lui", "Le groupe des Loups Gris est impliqué dans des extorsions et des trafics. Les habitants réclament davantage de sécurité.")
    if choice == "signaler":
        return res(g, "📞 Tu transmets discrètement des informations à une association de quartier ou aux autorités.", karma=5, intelligence=2)
    if choice == "aider":
        g["casier"] = max(1, g.get("casier", 0))
        return res(g, "⚠️ Tu acceptes de rendre un service au gang. Tu gagnes un peu d'argent, mais tu entres dans leur radar.", argent=1200, karma=-8, bonheur=2)
    return res(g, "🚶 Tu évites le groupe et préviens tes proches de rester prudents.", karma=2, sante=1)

def ev_real_arrests(g, choice):
    actualite_monde(g, "Grande opération policière", "Une enquête coordonnée conduit à plusieurs arrestations dans le milieu criminel. Des perquisitions ont lieu dans plusieurs villes.")
    if g.get("casier", 0) > 0 or (g.get("metier") and JOBS.get(g["metier"], {}).get("crime")):
        if choice == "cooperer":
            g["suspicion"] = max(0, g.get("suspicion", 0) - 10)
            return res(g, "🚔 Tu coopères avec les enquêteurs. Cela peut réduire les soupçons, sans garantir l'absence de poursuites.", karma=4, bonheur=-2)
        if choice == "fuir":
            g["suspicion"] = min(100, g.get("suspicion", 0) + 15)
            return res(g, "🏃 Tu prends la fuite et attires davantage l'attention des enquêteurs.", karma=-4, bonheur=-3)
        return res(g, "⚖️ Tu prends conseil avant de répondre aux enquêteurs.", intelligence=2, bonheur=-1)
    return res(g, "🛡️ Tu n'es pas visé·e par l'enquête. Tu espères que ces arrestations aideront le quartier à retrouver son calme.", bonheur=2, karma=2)

def ev_real_president(g, choice):
    actualite_monde(g, "Polémique au sommet de l'État", "Une décision présidentielle controversée provoque une crise politique, des manifestations et une motion de censure.")
    if choice == "protester":
        return res(g, "📣 Tu participes à une manifestation pacifique pour demander des comptes aux dirigeants.", karma=4, reputation=2, bonheur=2)
    if choice == "soutenir":
        return res(g, "🗳️ Tu défends la décision et débats avec ton entourage. Le pays reste profondément divisé.", intelligence=2, reputation=-1)
    return res(g, "📰 Tu t'informes auprès de plusieurs sources avant de te faire un avis.", intelligence=3, bonheur=1)

event("monde_guerre", "La guerre éclate à l'étranger", "🌍 Deux puissances entrent en guerre après l'échec de négociations. Les frontières se ferment et une crise humanitaire se profile. Comment réagis-tu ?", lambda g: g.get("univers") == "real" and not g.get("etat_monde", {}).get("conflit_international") and g.get("age",0) >= 10 and random.random() < .09, [("Aider les civils", lambda g: ev_real_war(g,"aide")), ("Manifester pour la paix", lambda g: ev_real_war(g,"manif")), ("Protéger tes proches", lambda g: ev_real_war(g,"securite"))])
event("monde_paix", "Un accord de paix historique", "🕊️ Après plusieurs années de tensions, les négociations aboutissent à un cessez-le-feu. Le monde retient son souffle : la paix tiendra-t-elle ?", lambda g: g.get("univers") == "real" and g.get("etat_monde", {}).get("conflit_international") and random.random() < .28, [("Célébrer l'accord", lambda g: ev_real_peace(g,"celebrer")), ("Rester prudent·e", lambda g: ev_real_peace(g,"prudent"))])
event("monde_devise", "Une nouvelle devise est annoncée", "💱 Une réforme monétaire inattendue est annoncée. Les banques, les entreprises et les ménages doivent s'adapter à une nouvelle devise de référence.", lambda g: g.get("univers") == "real" and not g.get("etat_monde", {}).get("reforme_monetaire_vue") and g.get("age",0) >= 16 and random.random() < .055, [("Sécuriser ton épargne", lambda g: (g.setdefault("etat_monde",{}).__setitem__("reforme_monetaire_vue",True) or ev_real_currency(g,"epargner"))), ("Investir avec prudence", lambda g: (g.setdefault("etat_monde",{}).__setitem__("reforme_monetaire_vue",True) or ev_real_currency(g,"investir"))), ("Attendre", lambda g: (g.setdefault("etat_monde",{}).__setitem__("reforme_monetaire_vue",True) or ev_real_currency(g,"attendre")))])
event("monde_independance", "Un territoire proclame son indépendance", "🏳️ Un territoire déclare son indépendance après un référendum contesté. La reconnaissance internationale est incertaine et des manifestations éclatent.", lambda g: g.get("univers") == "real" and not g.get("etat_monde", {}).get("mouvement_independance") and g.get("age",0) >= 12 and random.random() < .07, [("Soutenir le dialogue", lambda g: ev_real_independence(g,"dialogue")), ("Participer à une manifestation pacifique", lambda g: ev_real_independence(g,"manif")), ("Suivre la situation", lambda g: ev_real_independence(g,"distance"))])
event("monde_attentat", "Alerte sécuritaire majeure", "🚨 Une alerte annonce qu'un attentat visant un lieu public a été déjoué. Les autorités demandent d'éviter le secteur et de signaler tout danger sans s'exposer.", lambda g: g.get("univers") == "real" and g.get("age",0) >= 10 and random.random() < .075, [("Aider les secours", lambda g: ev_real_attack(g,"secours")), ("Transmettre une information", lambda g: ev_real_attack(g,"alerter")), ("S'éloigner et prévenir tes proches", lambda g: ev_real_attack(g,"rester") )])
event("monde_gang", "Un nouveau gang inquiète la ville", "🐺 Le gang des Loups Gris gagne du terrain dans certains quartiers. Des commerçants subissent des extorsions et les habitants se demandent comment réagir.", lambda g: g.get("univers") == "real" and not g.get("etat_monde", {}).get("nouveau_gang_vu") and g.get("age",0) >= 14 and random.random() < .09, [("Signaler les faits", lambda g: (g.setdefault("etat_monde",{}).__setitem__("nouveau_gang_vu",True) or ev_real_gang(g,"signaler"))), ("Accepter un service risqué", lambda g: (g.setdefault("etat_monde",{}).__setitem__("nouveau_gang_vu",True) or ev_real_gang(g,"aider"))), ("Éviter le groupe", lambda g: (g.setdefault("etat_monde",{}).__setitem__("nouveau_gang_vu",True) or ev_real_gang(g,"eviter")))])
event("monde_arrestations", "Vague d'arrestations", "🚔 Une vaste opération policière vise un réseau criminel. Les arrestations font la une et les habitants s'interrogent sur les conséquences pour leur quartier.", lambda g: g.get("univers") == "real" and g.get("age",0) >= 14 and random.random() < .08, [("Coopérer si tu es interrogé·e", lambda g: ev_real_arrests(g,"cooperer")), ("Prendre la fuite si tu es impliqué·e", lambda g: ev_real_arrests(g,"fuir")), ("Demander conseil", lambda g: ev_real_arrests(g,"conseil"))])
event("monde_president", "La décision présidentielle fait scandale", "🏛️ Une réforme controversée annoncée par le président déclenche des manifestations et une crise politique. Les citoyens se divisent sur la suite à donner.", lambda g: g.get("univers") == "real" and g.get("age",0) >= 16 and random.random() < .09, [("Manifester pacifiquement", lambda g: ev_real_president(g,"protester")), ("Défendre la décision", lambda g: ev_real_president(g,"soutenir")), ("Vérifier les informations", lambda g: ev_real_president(g,"informer"))])

def ev_naruto_hokage(g, choice):
    actualite_monde(g, "Le Hokage est mort", "Le village est en deuil. Le conseil doit choisir un successeur alors que des factions tentent de profiter du vide du pouvoir.")
    g.setdefault("etat_monde", {})["hokage_vacant"] = True
    if choice == "proteger":
        return res(g, "🍃 Tu aides à protéger les habitants et les bâtiments officiels.", karma=7, force=2, celebrite=2)
    if choice == "enquete":
        g["suspicion"] = min(100, g.get("suspicion",0)+3)
        return res(g, "🔎 Tu enquêtes sur les circonstances de la mort. Tu découvres des indices, mais tu te fais aussi des ennemis.", intelligence=5, karma=2)
    return res(g, "👑 Tu soutiens un candidat modéré au poste de Hokage et appelles au calme.", karma=4, reputation=3)

def ev_naruto_akatsuki(g, choice):
    actualite_monde(g, "L'Akatsuki déclare la guerre", "L'organisation annonce qu'elle va capturer les bijū. Les villages cachés renforcent leurs défenses et rappellent leurs shinobi.")
    g.setdefault("etat_monde", {})["guerre_akatsuki"] = True
    if choice == "combattre":
        return res(g, "⚔️ Tu rejoins une équipe de défense. La mission est dangereuse, mais tu gagnes le respect des autres ninjas.", force=5, karma=5, sante=-5, celebrite=4)
    if choice == "espionner":
        g["suspicion"] = min(100, g.get("suspicion", 0) + 3)
        return res(g, "🕵️ Tu acceptes une mission de renseignement. Tu récoltes des informations sans affronter directement l'organisation.", intelligence=5, karma=2)
    return res(g, "🏃 Tu aides les civils à se mettre à l'abri plutôt que de combattre.", karma=6, bonheur=-2)

def ev_naruto_kazekage(g, choice):
    actualite_monde(g, "Le Kazekage pourrait être manipulé", "Des décisions incohérentes du Kazekage alimentent les soupçons. Certains pensent qu'un conseiller contrôle ses décisions, d'autres dénoncent une rumeur fabriquée.")
    if choice == "enquete":
        return res(g, "🔎 Tu découvres des traces de genjutsu et avertis les autorités de Suna.", intelligence=5, karma=5, celebrite=2)
    if choice == "accuser":
        return res(g, "📣 Tu accuses publiquement un conseiller. Si tu as raison, tu peux empêcher un complot; sinon, tu risques de déclencher une crise diplomatique.", reputation=-3, intelligence=2, karma=1)
    return res(g, "🤝 Tu encourages une médiation discrète entre les conseillers et le Kazekage.", karma=4, bonheur=1)

def ev_naruto_peace(g, choice):
    g.setdefault("etat_monde", {})["guerre_akatsuki"] = False
    actualite_monde(g, "Les villages signent un pacte de paix", "Après des combats et des pertes, les cinq grands villages s'engagent à partager leurs renseignements et à protéger les civils.")
    if choice == "diplomatie":
        return res(g, "🤝 Tu participes à une mission diplomatique et contribues à maintenir l'alliance.", karma=6, intelligence=3, celebrite=2)
    return res(g, "🎉 Tu célèbres la trêve avec tes camarades, tout en sachant qu'une paix durable demande du travail.", bonheur=6, karma=2)

event("naruto_hokage_mort", "Le Hokage est mort", "🍃 Une nouvelle bouleverse Konoha : le Hokage a été tué lors d'une mission. Le village est placé en état d'alerte.", lambda g: g.get("univers") == "manga" and g.get("saga_manga","naruto") == "naruto" and not g.get("etat_monde",{}).get("hokage_vacant") and g.get("age",0) >= 8 and random.random() < .07, [("Protéger les habitants", lambda g: ev_naruto_hokage(g,"proteger")), ("Enquêter", lambda g: ev_naruto_hokage(g,"enquete")), ("Soutenir un successeur", lambda g: ev_naruto_hokage(g,"successeur"))])
event("naruto_akatsuki_war", "L'Akatsuki déclare la guerre", "☁️ L'Akatsuki annonce qu'elle passera à l'offensive pour capturer les bijū. Les villages doivent choisir entre coopération, espionnage et évacuation.", lambda g: g.get("univers") == "manga" and g.get("saga_manga","naruto") == "naruto" and not g.get("etat_monde",{}).get("guerre_akatsuki") and g.get("age",0) >= 10 and random.random() < .09, [("Combattre", lambda g: ev_naruto_akatsuki(g,"combattre")), ("Espionner l'organisation", lambda g: ev_naruto_akatsuki(g,"espionner")), ("Évacuer les civils", lambda g: ev_naruto_akatsuki(g,"civils"))])
event("naruto_kazekage_manipule", "Le Kazekage est-il manipulé ?", "🏜️ Le Kazekage prend une décision qui pourrait déclencher une guerre. Des indices laissent penser qu'il est manipulé par un conseiller ou un genjutsu.", lambda g: g.get("univers") == "manga" and g.get("saga_manga","naruto") == "naruto" and g.get("age",0) >= 10 and random.random() < .08, [("Enquêter discrètement", lambda g: ev_naruto_kazekage(g,"enquete")), ("Accuser publiquement", lambda g: ev_naruto_kazekage(g,"accuser")), ("Chercher une médiation", lambda g: ev_naruto_kazekage(g,"mediation"))])
event("naruto_peace_treaty", "Un pacte de paix entre villages", "🕊️ Après une période de tensions, les cinq grands villages se réunissent pour signer un pacte de paix. Une seule provocation pourrait tout faire échouer.", lambda g: g.get("univers") == "manga" and g.get("saga_manga","naruto") == "naruto" and (g.get("etat_monde",{}).get("guerre_akatsuki") or random.random() < .08) and g.get("age",0) >= 10, [("Participer à la diplomatie", lambda g: ev_naruto_peace(g,"diplomatie")), ("Célébrer la trêve", lambda g: ev_naruto_peace(g,"celebrer"))])

def ev_jjk_incident(g, choice):
    actualite_monde(g, "Incident de fléau de classe spéciale", "Une barrière s'effondre et un fléau de classe spéciale piège des civils dans un quartier. Les exorcistes sont appelés en urgence.")
    g.setdefault("etat_monde", {})["barriere_jjk"] = True
    if choice == "exorciser":
        return res(g, "👁️ Tu affrontes le fléau avec les autres exorcistes. Tu en ressors épuisé·e, mais tu sauves des civils.", force=5, intelligence=3, sante=-8, celebrite=5, karma=6)
    if choice == "evacuer":
        return res(g, "🚨 Tu aides à évacuer le quartier pendant que les exorcistes combattent.", karma=7, bonheur=-2)
    return res(g, "📡 Tu transmets les informations à l'école et gardes tes distances.", intelligence=3, karma=2)

def ev_jjk_school(g, choice):
    actualite_monde(g, "L'école de Jujutsu ferme temporairement", "Après une attaque et des désaccords entre dirigeants, les cours sont suspendus. Les élèves doivent choisir entre rester loyaux, enquêter ou se mettre à l'abri.")
    if choice == "enquete":
        return res(g, "🔎 Tu découvres une piste qui relie l'incident à un réseau de fléaux.", intelligence=5, karma=3)
    if choice == "loyal":
        return res(g, "🏯 Tu aides les enseignants à protéger les élèves et les archives.", karma=5, force=2)
    return res(g, "🧳 Tu quittes temporairement le campus et évites de devenir une cible.", sante=3, bonheur=-1)

event("jjk_fléau_majeur", "Un fléau de classe spéciale apparaît", "👁️ Une barrière mystérieuse enferme un quartier. Les civils sont pris au piège et les exorcistes doivent intervenir.", lambda g: g.get("univers") == "manga" and g.get("saga_manga") == "jujutsu" and g.get("age",0) >= 8 and not g.get("etat_monde",{}).get("barriere_jjk") and random.random() < .1, [("Combattre le fléau", lambda g: ev_jjk_incident(g,"exorciser")), ("Évacuer les civils", lambda g: ev_jjk_incident(g,"evacuer")), ("Transmettre les informations", lambda g: ev_jjk_incident(g,"informer"))])
event("jjk_crise_ecole", "Crise à l'école d'exorcisme", "🏯 Une attaque force l'école à suspendre ses activités. Des rumeurs évoquent une trahison interne.", lambda g: g.get("univers") == "manga" and g.get("saga_manga") == "jujutsu" and g.get("age",0) >= 12 and random.random() < .075, [("Enquêter", lambda g: ev_jjk_school(g,"enquete")), ("Protéger les élèves", lambda g: ev_jjk_school(g,"loyal")), ("Quitter le campus", lambda g: ev_jjk_school(g,"partir"))])

def ev_onepiece_war(g, choice):
    actualite_monde(g, "La Marine lance une offensive majeure", "Une opération massive vise plusieurs équipages pirates. Les ports sont surveillés et les primes augmentent.")
    if choice == "combattre":
        g["notoriete_manga"] = min(100, g.get("notoriete_manga",0)+12)
        return res(g, "⚔️ Tu prends part à une bataille navale et échappes de peu à la capture.", force=5, celebrite=6, karma=-3, sante=-6)
    if choice == "sauver":
        return res(g, "🛟 Tu abandonnes le butin pour sauver des civils et des marins blessés.", karma=7, bonheur=2, celebrite=3)
    return res(g, "🏴‍☠️ Tu évites le blocus et changes de route. Ton équipage est sauf, mais l'occasion de te faire connaître passe.", intelligence=2, bonheur=1)

def ev_onepiece_independence(g, choice):
    actualite_monde(g, "Une île réclame son indépendance", "Une île sous contrôle du Gouvernement mondial proclame son autonomie. La Marine, les révolutionnaires et les pirates cherchent à influencer l'issue.")
    if choice == "revolution":
        g["notoriete_manga"] = min(100, g.get("notoriete_manga",0)+8)
        return res(g, "🔥 Tu aides les habitants à organiser leur défense et leur ravitaillement.", karma=6, celebrite=4)
    if choice == "marine":
        return res(g, "⚓ Tu soutiens une transition négociée sous supervision de la Marine.", karma=3, intelligence=3)
    return res(g, "🧭 Tu refuses de te mêler du conflit et protèges ton équipage.", bonheur=2)

event("onepiece_offensive_marine", "La Marine lance une offensive", "⚓ Une opération de grande ampleur vise les équipages pirates. Les ports sont bouclés et plusieurs capitaines sont arrêtés.", lambda g: g.get("univers") == "manga" and g.get("saga_manga") == "onepiece" and g.get("age",0) >= 12 and g.get("faction_manga") in ("Pirates","Empereur des mers") and random.random() < .12, [("Combattre la Marine", lambda g: ev_onepiece_war(g,"combattre")), ("Sauver les blessés", lambda g: ev_onepiece_war(g,"sauver")), ("Fuir le blocus", lambda g: ev_onepiece_war(g,"fuir"))])
event("onepiece_independence", "Une île proclame son indépendance", "🏝️ Une île refuse de payer le tribut au Gouvernement mondial et proclame son autonomie. Plusieurs factions se disputent son avenir.", lambda g: g.get("univers") == "manga" and g.get("saga_manga") == "onepiece" and g.get("age",0) >= 12 and random.random() < .09, [("Aider les révolutionnaires", lambda g: ev_onepiece_independence(g,"revolution")), ("Soutenir la médiation de la Marine", lambda g: ev_onepiece_independence(g,"marine")), ("Rester neutre", lambda g: ev_onepiece_independence(g,"neutre"))])

def ev_fantasy_war(g, choice):
    actualite_monde(g, "La guerre des Trois Couronnes", "Trois royaumes rompent leur alliance. Les routes commerciales ferment, les réfugiés affluent et les seigneurs cherchent des alliés.")
    g.setdefault("etat_monde", {})["guerre_fantasy"] = True
    if choice == "defendre":
        return res(g, "🛡️ Tu rejoins la défense des villages et escortes les réfugiés.", force=4, karma=7, sante=-5, celebrite=4)
    if choice == "diplomatie":
        return res(g, "🕊️ Tu négocies un passage sûr pour les civils. Les seigneurs restent méfiants, mais la route est ouverte.", intelligence=5, karma=6)
    return res(g, "🏠 Tu te mets à l'abri pendant que les armées avancent.", sante=2, bonheur=-2)

def ev_fantasy_peace(g, choice):
    g.setdefault("etat_monde", {})["guerre_fantasy"] = False
    actualite_monde(g, "Les Trois Couronnes signent une trêve", "Les souverains acceptent une trêve fragile et créent un conseil chargé de régler les différends.")
    if choice == "fete":
        return res(g, "🎉 Tu participes aux festivités et aides à reconstruire les villages.", bonheur=7, karma=4, celebrite=2)
    return res(g, "📜 Tu aides à rédiger les termes de la trêve et réclames des garanties pour les civils.", intelligence=4, karma=5)

def ev_fantasy_dragon(g, choice):
    actualite_monde(g, "Un dragon attaque la capitale", "Un dragon ancien attaque les remparts. La cour hésite entre payer un tribut, organiser la défense ou négocier.")
    if choice == "combattre":
        return res(g, "🐉 Tu participes à la défense de la capitale. La victoire est incertaine, mais ton courage est remarqué.", force=6, sante=-8, celebrite=5, karma=4)
    if choice == "negocier":
        return res(g, "🗣️ Tu négocies un tribut temporaire contre le retrait du dragon.", intelligence=4, argent=-min(g.get("argent",0),500), karma=1)
    return res(g, "🚪 Tu évacues les habitants par les tunnels sous la ville.", karma=7, bonheur=-2)

def ev_fantasy_coin(g, choice):
    old = g.get("monnaie_monde", "Couronne")
    g["monnaie_monde"] = "Couronne royale"
    actualite_monde(g, "Une nouvelle monnaie est frappée", f"Le royaume abandonne l'ancienne monnaie ({old}) au profit de la Couronne royale. Les guildes doivent convertir leurs contrats.")
    if choice == "echanger":
        return res(g, "🪙 Tu échanges tes pièces avant la date limite et évites une perte de valeur.", intelligence=3, bonheur=2)
    return res(g, "📦 Tu conserves tes anciennes pièces comme objets de collection. Certaines perdent de leur valeur.", bonheur=1, argent=-min(g.get("argent",0),200))

event("fantasy_guerre", "La guerre des Trois Couronnes", "⚔️ Trois royaumes entrent en guerre après la rupture d'un traité. Les routes deviennent dangereuses et les réfugiés affluent.", lambda g: g.get("univers") == "fantasy" and not g.get("etat_monde",{}).get("guerre_fantasy") and g.get("age",0) >= 10 and random.random() < .1, [("Défendre les villages", lambda g: ev_fantasy_war(g,"defendre")), ("Négocier un passage sûr", lambda g: ev_fantasy_war(g,"diplomatie")), ("Se mettre à l'abri", lambda g: ev_fantasy_war(g,"abri"))])
event("fantasy_paix", "La trêve des Trois Couronnes", "🕊️ Après des mois de conflit, les souverains acceptent une trêve fragile. Les guildes cherchent des médiateurs.", lambda g: g.get("univers") == "fantasy" and g.get("etat_monde",{}).get("guerre_fantasy") and random.random() < .3, [("Aider à reconstruire", lambda g: ev_fantasy_peace(g,"fete")), ("Rédiger les garanties", lambda g: ev_fantasy_peace(g,"garanties"))])
event("fantasy_dragon_capitale", "Un dragon attaque la capitale", "🐉 Un dragon ancien brise les portes de la capitale. La population fuit tandis que le conseil royal débat d'une réponse.", lambda g: g.get("univers") == "fantasy" and g.get("age",0) >= 10 and random.random() < .075, [("Combattre le dragon", lambda g: ev_fantasy_dragon(g,"combattre")), ("Négocier", lambda g: ev_fantasy_dragon(g,"negocier")), ("Évacuer les habitants", lambda g: ev_fantasy_dragon(g,"evacuer"))])
event("fantasy_nouvelle_monnaie", "Le royaume change de monnaie", "🪙 Le conseil royal annonce que les anciennes pièces seront bientôt remplacées. Les commerçants craignent une hausse des prix.", lambda g: g.get("univers") == "fantasy" and not g.get("etat_monde",{}).get("nouvelle_monnaie_vue") and g.get("age",0) >= 12 and random.random() < .065, [("Échanger ses pièces", lambda g: (g.setdefault("etat_monde",{}).__setitem__("nouvelle_monnaie_vue",True) or ev_fantasy_coin(g,"echanger"))), ("Garder les anciennes pièces", lambda g: (g.setdefault("etat_monde",{}).__setitem__("nouvelle_monnaie_vue",True) or ev_fantasy_coin(g,"garder")))])


# Missions de carrière récurrentes : plusieurs missions par métier, avec une vraie
# jauge de performance qui accélère ou freine l'accès au grade suivant.
def mission_carriere(g, job_key, mission_type, choix):
    job = JOBS[job_key]
    g.setdefault("performance_metier", 35)
    g.setdefault("progression_grade", 0)
    g.setdefault("missions_reussies", 0)
    g.setdefault("missions_echouees", 0)
    titre = {
        "urgence": "une intervention urgente",
        "enquete": "un dossier délicat",
        "equipe": "une mission d'équipe",
        "objectif": "un objectif difficile",
        "ethique": "un dilemme professionnel",
    }.get(mission_type, "une mission importante")
    if choix == "reussir":
        gain = random.randint(8, 15)
        if "heros" in job_key or job_key in ("policier", "exorciste_jujutsu", "ninja", "marine"):
            g["reputation"] = clamp(g.get("reputation", 50) + 2)
        if "pirate" in job_key or job_key in ("bandit", "mercenaire"):
            g["prime_recherchee"] = min(100000000, g.get("prime_recherchee", 0) + random.randint(10000, 100000))
        g["performance_metier"] = clamp(g["performance_metier"] + gain)
        g["progression_grade"] = min(100, g["progression_grade"] + random.randint(10, 18))
        g["missions_reussies"] += 1
        prime = max(100, int(job["sal"] * random.uniform(.03, .12)))
        if g["performance_metier"] >= 100 and g.get("grade", 0) < min(3, len(job["grades"])-1):
            g["performance_metier"] = 55
            g["grade"] += 1
            g["progression_grade"] = 0
            log(g, f"🎖️ Promotion obtenue après tes missions : {job['grades'][g['grade']]}.")
            return res(g, f"✅ Tu réussis {titre} dans ton poste de {job['nom'].lower()}. Tes résultats dépassent les attentes : promotion au grade {job['grades'][g['grade']]} et prime de {fm(g, prime)}.", argent=prime, celebrite=3, bonheur=8, reputation=5)
        return res(g, f"✅ Mission réussie : {titre} dans ton poste de {job['nom'].lower()}. Ta performance progresse (+{gain}) et ton dossier de promotion avance.", argent=prime, celebrite=2, bonheur=4, reputation=3)
    # Flop : l'échec reste jouable, mais fait reculer le parcours professionnel.
    perte = random.randint(10, 18)
    g["performance_metier"] = clamp(g["performance_metier"] - perte)
    if "heros" in job_key or job_key in ("policier", "exorciste_jujutsu", "ninja", "marine"):
        g["reputation"] = clamp(g.get("reputation", 50) - 4)
    if "pirate" in job_key or job_key in ("bandit", "mercenaire"):
        g["prime_recherchee"] = max(0, g.get("prime_recherchee", 0) - random.randint(1000, 15000))
    g["progression_grade"] = max(0, g["progression_grade"] - random.randint(12, 25))
    g["missions_echouees"] += 1
    chg(g, reputation=-random.randint(2, 7), bonheur=-3)
    consequence = ""
    if g["performance_metier"] < 20 and g.get("grade", 0) > 0 and random.random() < .25:
        g["grade"] -= 1
        consequence = f" Ton grade est rétrogradé : tu redeviens {job['grades'][g['grade']]}. "
    elif g["performance_metier"] < 35:
        consequence = " Ton supérieur reporte ta promotion et te place sous surveillance."
    return res(g, f"❌ Échec : {titre} dans ton poste de {job['nom'].lower()}. La performance baisse de {perte} points et ton dossier de promotion recule.{consequence}", celebrite=-2, bonheur=-2)

def condition_mission_carriere(g, job_key, kind):
    if g.get("metier") != job_key or g.get("age", 0) < max(16, JOBS[job_key]["age"]):
        return False
    # Les missions arrivent plus souvent aux personnages qui travaillent déjà,
    # mais les résultats ne sont jamais garantis.
    return random.random() < 0.28

for _job_key, _job in list(JOBS.items()):
    # Des situations contextualisées selon le secteur du métier, pour éviter que les
    # 72 professions reçoivent exactement les mêmes scénarios génériques.
    def missions_adaptees(job_key, job):
        k = (job_key + " " + job["nom"]).lower()
        if any(x in k for x in ("médec", "infirm", "chirurg", "soin", "vétér", "secour", "exorciste")):
            secteur = [("urgence", "Urgence critique", "Un cas critique arrive sans prévenir. Tu dois prioriser les personnes à aider, coordonner l'équipe et éviter une erreur irréversible."), ("enquete", "Diagnostic délicat", "Des symptômes ou des indices se contredisent. Il faut vérifier les faits avant de choisir un traitement ou une intervention."), ("equipe", "Relève sous tension", "Le service manque de personnel et la relève est débordée. Tu dois répartir les tâches sans compromettre la sécurité."), ("objectif", "Protocole à respecter", "Un contrôle évalue tes gestes, tes dossiers et le respect du protocole. Une décision rapide ne doit pas sacrifier la qualité."), ("ethique", "Confidentialité en jeu", "Une personne influente réclame des informations privées. Tu dois protéger la confidentialité tout en gérant la pression.")]
        elif any(x in k for x in ("police", "policier", "gendar", "détect", "enquête", "justice", "avocat", "juge", "pompier", "armée", "militaire", "héros", "ninja", "marine", "pirate", "mercenaire", "bandit")):
            secteur = [("urgence", "Intervention à haut risque", "Un incident dégénère sur le terrain. Il faut protéger les civils, sécuriser la zone et décider si tu demandes des renforts."), ("enquete", "Piste contradictoire", "Deux témoins donnent des versions opposées. Tu dois recouper les indices sans accuser la mauvaise personne."), ("equipe", "Opération coordonnée", "Une opération dépend de plusieurs équipiers. Un désaccord menace le plan et tu dois rétablir la coordination."), ("objectif", "Cible prioritaire", "Une cible ou un objectif prioritaire est repéré, mais le temps manque. Ta préparation et ton sang-froid seront déterminants."), ("ethique", "Ordre contestable", "Un supérieur te donne un ordre discutable. Tu peux obéir, demander des explications ou défendre les personnes exposées.")]
        elif any(x in k for x in ("prof", "enseign", "éduc", "formateur", "coach", "chercheur", "scient", "étudiant")):
            secteur = [("urgence", "Crise dans le groupe", "Un conflit éclate pendant une séance et menace de faire dérailler le programme. Tu dois calmer la situation et garder le groupe engagé."), ("enquete", "Résultat inexplicable", "Un résultat ou un travail semble incohérent. Tu dois rechercher la cause sans tirer de conclusion hâtive."), ("equipe", "Projet collectif", "Un projet commun prend du retard parce que les rôles sont mal répartis. Tu dois relancer la coopération."), ("objectif", "Échéance importante", "Une évaluation ou une présentation approche. Tu dois organiser les priorités et livrer un résultat solide."), ("ethique", "Équité et favoritisme", "On te demande de favoriser une personne au détriment des autres. Tu dois choisir une réponse juste et défendable.")]
        elif any(x in k for x in ("commerce", "vendeur", "commercial", "entrepreneur", "patron", "gestion", "banquier", "financ", "comptable", "marketing", "influenceur", "artiste", "musicien", "acteur", "écrivain", "journaliste", "cuisin", "chef", "artisan")):
            secteur = [("urgence", "Client ou commande en crise", "Une commande importante est compromise à la dernière minute. Tu dois trouver une solution sans perdre la confiance du client."), ("enquete", "Anomalie dans les comptes", "Un écart apparaît dans les chiffres ou les informations du projet. Tu dois vérifier son origine avant de prendre une décision."), ("equipe", "Livraison en équipe", "Un projet dépend de plusieurs personnes qui n'avancent pas au même rythme. Tu dois clarifier les responsabilités."), ("objectif", "Contrat décisif", "Une opportunité peut faire décoller ton activité, mais les délais et le budget sont serrés. Il faut négocier et livrer."), ("ethique", "Réputation en danger", "Une méthode douteuse pourrait rapporter davantage à court terme. Tu dois choisir entre le gain immédiat et la confiance à long terme.")]
        else:
            secteur = [("urgence", "Incident sur le lieu de travail", "Un incident imprévu perturbe ton service. Tu dois agir vite, prévenir les bonnes personnes et limiter les conséquences."), ("enquete", "Problème à résoudre", "Une anomalie dans ton travail exige de vérifier les faits, d'identifier la cause et de proposer une solution fiable."), ("equipe", "Coopération difficile", "Ton équipe doit atteindre un objectif commun malgré un désaccord et des moyens limités."), ("objectif", "Mission prioritaire", "On te confie une mission importante avec une échéance courte. Ton organisation et la qualité du résultat seront évaluées."), ("ethique", "Dilemme au travail", "Une situation oppose facilité et responsabilité. Ta décision aura des conséquences sur les personnes concernées et ta réputation.")]
        return secteur

    for _mission_kind, _mission_title, _mission_desc in missions_adaptees(_job_key, _job):
        def _mission_cond(g, key=_job_key, kind=_mission_kind):
            return condition_mission_carriere(g, key, kind)
        def _mission_win(g, key=_job_key, kind=_mission_kind):
            return mission_carriere(g, key, kind, "reussir")
        def _mission_fail(g, key=_job_key, kind=_mission_kind):
            return mission_carriere(g, key, kind, "echouer")
        event(f"mission_{_job_key}_{_mission_kind}", f"{_mission_title} — {_job['nom']}", f"🎯 { _mission_desc } Ton résultat influencera ta performance et tes chances d'avancement.", _mission_cond, [("Prendre la mission au sérieux", _mission_win), ("Mal gérer / échouer", _mission_fail)])



# ----------------------------------------------------------------------
# Inventaire d'équipement, trésors et marché des univers manga
# ----------------------------------------------------------------------
OBJETS_MARCHE = [
    {"id":"kunai", "nom":"Lot de kunai", "emoji":"🗡️", "rarete":"C", "prix":1800, "vente":900, "univers":"naruto", "type":"arme", "desc":"Des armes ninja simples pour les missions."},
    {"id":"shuriken_ombre", "nom":"Shuriken de l'ombre", "emoji":"✴️", "rarete":"B", "prix":12000, "vente":6000, "univers":"naruto", "type":"arme", "desc":"Un shuriken renforcé, précis et équilibré."},
    {"id":"parchemin_jutsu", "nom":"Parchemin de jutsu", "emoji":"📜", "rarete":"S", "prix":850000, "vente":425000, "univers":"naruto", "type":"parchemin", "desc":"Permet d'apprendre une technique Naruto prédéfinie que tu ne connais pas encore."},
    {"id":"lame_classe_s", "nom":"Lame ninja de classe S", "emoji":"⚔️", "rarete":"S", "prix":2500000, "vente":1250000, "univers":"naruto", "type":"arme", "desc":"Une arme exceptionnelle qui augmente ta force."},
    {"id":"outil_maudit", "nom":"Outil maudit", "emoji":"🗡️", "rarete":"A", "prix":95000, "vente":47500, "univers":"jujutsu", "type":"arme", "desc":"Une arme imprégnée d'énergie occulte."},
    {"id":"parchemin_maudit", "nom":"Archive de technique maudite", "emoji":"📕", "rarete":"S", "prix":1200000, "vente":600000, "univers":"jujutsu", "type":"parchemin", "desc":"Apprend une technique maudite prédéfinie."},
    {"id":"relique_speciale", "nom":"Relique de classe spéciale", "emoji":"👁️", "rarete":"SS", "prix":8500000, "vente":4250000, "univers":"jujutsu", "type":"relique", "desc":"Une relique extrêmement rare qui augmente l'énergie occulte et la force."},
    {"id":"sabre_marin", "nom":"Sabre de marin", "emoji":"⚓", "rarete":"B", "prix":15000, "vente":7500, "univers":"onepiece", "type":"arme", "desc":"Un sabre fiable pour les combats en mer."},
    {"id":"lame_legendaire", "nom":"Lame légendaire de classe S", "emoji":"🗡️", "rarete":"S", "prix":3000000, "vente":1500000, "univers":"onepiece", "type":"arme", "desc":"Une lame rare qui renforce considérablement la force."},
    {"id":"fruit_demon_ss", "nom":"Fruit du démon", "emoji":"🍈", "rarete":"SS", "prix":25000000, "vente":12500000, "univers":"onepiece", "type":"fruit", "desc":"Fruit du démon très recherché. Le pouvoir obtenu est prédéfini aléatoirement et empêche de nager."},
    {"id":"cristal_mana", "nom":"Cristal de mana", "emoji":"🔮", "rarete":"A", "prix":90000, "vente":45000, "univers":"fantasy", "type":"relique", "desc":"Renforce la réserve magique."},
]

def univers_objets(g):
    if g.get("univers") != "manga":
        return "fantasy" if g.get("univers") == "fantasy" else "real"
    return g.get("saga_manga", "naruto")

def objet_def(objet_id):
    return next((o for o in OBJETS_MARCHE if o["id"] == objet_id), None)

def possede_objet(g, objet_id):
    return any(o.get("id") == objet_id for o in g.get("inventaire_objets", []))

def facteur_prix_marche(g, obj):
    """Prix dynamique : karma, réputation, pénurie et spécialité de vendeur."""
    karma = int(g.get("stats", {}).get("karma", 50))
    reputation = int(g.get("reputation", 50))
    # karma is commonly stored around 0-100; normalize to neutral 50
    facteur_karma = 1.0 - max(-0.15, min(0.15, (karma - 50) / 100 * 0.30))
    facteur_rep = 1.0 - max(-0.10, min(0.10, (reputation - 50) / 100 * 0.20))
    prix_monde = g.get("prix_marche", {}).get(obj["id"], 1.0)
    facteur_vendeur = 1.0
    if g.get("marche_noir_debloque") and obj["univers"] in ("naruto", "jujutsu", "onepiece") and obj["rarete"] in ("S", "SS"):
        facteur_vendeur = 0.94
    return max(0.65, min(1.45, facteur_karma * facteur_rep * prix_monde * facteur_vendeur))

def prix_achat_actuel(g, obj):
    return max(1, int(obj["prix"] * facteur_prix_marche(g, obj)))

def prix_vente_actuel(g, obj):
    return max(1, int(obj["vente"] * facteur_prix_marche(g, obj) * (1.05 if g.get("reputation", 50) >= 75 else 1.0)))

def actualiser_economie_mondiale(g):
    """Les pénuries et les événements modifient les prix de référence au fil des ans."""
    prix = g.setdefault("prix_marche", {})
    for obj in OBJETS_MARCHE:
        ancien = prix.get(obj["id"], 1.0)
        prix[obj["id"]] = round(max(0.70, min(1.65, ancien * random.uniform(0.94, 1.07))), 3)
    etat = g.setdefault("etat_monde", {})
    if etat.get("conflit_international") or etat.get("guerre_akatsuki") or etat.get("guerre_fantasy"):
        for obj in OBJETS_MARCHE:
            if obj["type"] == "arme":
                prix[obj["id"]] = min(1.65, round(prix.get(obj["id"], 1.0) * 1.12, 3))
    if random.random() < 0.08:
        obj = random.choice(OBJETS_MARCHE)
        prix[obj["id"]] = min(1.65, round(prix.get(obj["id"], 1.0) * 1.25, 3))
        actualite_monde(g, "Pénurie sur le marché", f"Une pénurie touche les stocks de {obj['nom']}. Son prix augmente temporairement.")

def acheter_objet_marche(g, objet_id):
    obj = objet_def(objet_id)
    if not obj: raise Refus("Objet introuvable sur le marché.")
    if obj["univers"] != univers_objets(g): raise Refus("Cet objet n'est pas disponible dans ton univers.")
    if obj["id"] == "fruit_demon_ss" and g.get("fruit_demon"): raise Refus("Tu possèdes déjà un fruit du démon.")
    if obj["type"] == "parchemin" and not any(o["id"] == obj["id"] for o in g.get("inventaire_objets", [])):
        pass
    prix = prix_achat_actuel(g, obj)
    if g.get("argent", 0) < prix: raise Refus(f"Il te manque {fm(g, prix - g.get('argent', 0))}.")
    g["argent"] -= prix
    g.setdefault("inventaire_objets", []).append({"id":obj["id"], "nom":obj["nom"], "rarete":obj["rarete"], "type":obj["type"], "prix_achat":prix})
    if obj["rarete"] == "SS" and obj["id"] not in g.setdefault("objets_uniques", []):
        g["objets_uniques"].append(obj["id"])
    log(g, f"🛒 Achat au marché : {obj['nom']} ({obj['rarete']}) pour {fm(g, prix)}.")
    return f"🛒 Tu achètes {obj['nom']} pour {fm(g, prix)}."

def vendre_objet_marche(g, index):
    inventaire = g.setdefault("inventaire_objets", [])
    if index < 0 or index >= len(inventaire): raise Refus("Objet introuvable dans ton inventaire.")
    item = inventaire[index]
    definition = objet_def(item.get("id"))
    prix = prix_vente_actuel(g, definition) if definition else max(100, int(item.get("prix_achat", 1000) * .5))
    g["argent"] += prix
    inventaire.pop(index)
    log(g, f"💰 Vente : {item.get('nom', 'objet')} pour {fm(g, prix)}.")
    return f"💰 Tu vends {item.get('nom', 'objet')} pour {fm(g, prix)}."

def appliquer_objet(g, index):
    inv = g.setdefault("inventaire_objets", [])
    if index < 0 or index >= len(inv): raise Refus("Objet introuvable.")
    item = inv[index]
    obj = objet_def(item.get("id"))
    if not obj: raise Refus("Cet objet ne peut pas être utilisé.")
    if obj["type"] == "parchemin":
        if obj["univers"] == "naruto":
            connus = set(g.get("jutsu", []))
            choix = [x for x in JUTSU if JUTSU[x].get("saga", "naruto") == "naruto" and x not in connus]
            if not choix: raise Refus("Tu connais déjà tous les jutsu disponibles.")
            technique = random.choice(choix); g.setdefault("jutsu", []).append(technique)
        else:
            connus = set(g.get("techniques_maudites", []))
            choix = [x for x in JUTSU if JUTSU[x].get("saga") == "jujutsu" and x not in connus]
            if not choix: raise Refus("Tu connais déjà toutes les techniques maudites disponibles.")
            technique = random.choice(choix); g.setdefault("techniques_maudites", []).append(technique)
        inv.pop(index)
        log(g, f"📜 Parchemin utilisé : tu apprends {technique}.")
        return f"📜 Tu apprends la technique **{technique}** !"
    if obj["type"] == "fruit":
        if g.get("fruit_demon"): raise Refus("Tu possèdes déjà un fruit du démon.")
        fruit = random.choice(["Gomu Gomu", "Mera Mera", "Ope Ope", "Bara Bara", "Suna Suna", "Hie Hie", "Tori Tori modèle phénix", "Goro Goro", "Yami Yami"])
        g["fruit_demon"] = fruit; g.setdefault("pouvoirs", []).append(fruit); inv.pop(index)
        log(g, f"🍈 Tu manges un fruit du démon : {fruit}. Tu ne peux désormais plus nager.")
        return f"🍈 Tu obtiens le pouvoir **{fruit}**. Attention : tu ne peux plus nager."
    if obj["type"] == "arme":
        if item.get("équipé"): raise Refus("Cette arme est déjà équipée.")
        item["équipé"] = True
        bonus = 12 if obj["rarete"] == "S" else (7 if obj["rarete"] == "A" else 3)
        if item.get("id") in ("lame_classe_s", "lame_legendaire"):
            bonus += 5
        chg(g, force=bonus)
        log(g, f"⚔️ Tu équipes {obj['nom']} : +{bonus} force.")
        return f"⚔️ {obj['nom']} équipée : +{bonus} force."
    if obj["type"] == "relique":
        if obj["univers"] == "jujutsu": g["energie_occulte"] = min(100, g.get("energie_occulte", 0) + 20); chg(g, force=5)
        else: g["energie_magique"] = min(100, g.get("energie_magique", 0) + 20); chg(g, intelligence=5)
        inv.pop(index)
        log(g, f"🔮 Tu utilises {obj['nom']} et sens son énergie augmenter.")
        return f"🔮 Tu absorbes l'énergie de {obj['nom']}."
    raise Refus("Cet objet ne peut pas être utilisé.")

def ev_coffre_tresor(g, choix):
    saga = univers_objets(g)
    g["coffres_ouverts"] = g.get("coffres_ouverts", 0) + 1
    if choix == "inspecter":
        if random.random() < .25:
            g["stats"]["sante"] = clamp(g["stats"]["sante"] - random.randint(3, 12))
            return res(g, "🪤 Tu repères le piège à temps, mais tu te blesses légèrement en le neutralisant.", sante=-4, intelligence=2)
        return res(g, "🔍 Tu examines le coffre avec prudence et désamorces son mécanisme.", intelligence=2, karma=2)
    if random.random() < .28:
        degats = random.randint(8, 22)
        return res(g, f"💥 Le coffre était piégé ! Tu subis {degats} dégâts et le mécanisme détruit le contenu.", sante=-degats, bonheur=-3)
    # Chest loot: mostly common, rarely high rarity SS items.
    roll = random.random()
    if g.get("reputation", 50) >= 80:
        roll = min(0.999, roll + 0.05)
    if saga == "naruto":
        pool = ["kunai", "shuriken_ombre", "parchemin_jutsu", "lame_classe_s"]
    elif saga == "jujutsu":
        pool = ["outil_maudit", "parchemin_maudit", "relique_speciale"]
    else:
        pool = ["sabre_marin", "lame_legendaire", "fruit_demon_ss"]
    if roll < .52: pool = [x for x in pool if objet_def(x)["rarete"] in ("B","C","A")] or pool
    elif roll < .88: pool = [x for x in pool if objet_def(x)["rarete"] in ("S","A")] or pool
    else: pool = [x for x in pool if objet_def(x)["rarete"] == "SS"] or pool
    objet_id = random.choice(pool)
    obj = objet_def(objet_id)
    g.setdefault("inventaire_objets", []).append({"id":obj["id"], "nom":obj["nom"], "rarete":obj["rarete"], "type":obj["type"], "prix_achat":0})
    log(g, f"🎁 Coffre ouvert : tu trouves {obj['nom']} (classe {obj['rarete']}) !")
    return res(g, f"🎁 Dans le coffre, tu trouves **{obj['nom']} — classe {obj['rarete']}** ! Consulte ton inventaire pour l'utiliser ou le revendre.", bonheur=4, celebrite=1)

def ev_vol_objet(g, choix):
    inv = g.setdefault("inventaire_objets", [])
    if not inv:
        return res(g, "Tu n'avais aucun objet à perdre, mais tu as été secoué par l'incident.", bonheur=-2)
    candidats = [i for i,x in enumerate(inv) if not x.get("équipé")]
    if not candidats:
        return res(g, "Tu gardes ton équipement, mais le voleur s'enfuit. Tu renforces ta vigilance.", reputation=1)
    idx = random.choice(candidats)
    item = inv[idx]
    if choix == "poursuivre" and g.get("stats", {}).get("force", 0) >= 55:
        return res(g, f"Tu rattrapes le voleur et récupères {item['nom']} !", force=1, reputation=2)
    if choix == "negocier" and g.get("stats", {}).get("karma", 50) >= 55 and random.random() < .65:
        return res(g, f"Tu convaincs le voleur de rendre {item['nom']}.", karma=2, reputation=1)
    inv.pop(idx)
    return res(g, f"Le voleur s'échappe avec {item['nom']}. Tu pourras en chercher un autre ou en racheter un.", bonheur=-5, karma=-1)

event("vol_inventaire", "Un voleur vise ton équipement", "🕵️ Dans une foule agitée, quelqu'un tente de dérober un objet de ton inventaire. Tu peux le poursuivre, négocier ou laisser tomber.", lambda g: g.get("age", 0) >= 12 and bool(g.get("inventaire_objets")) and random.random() < .06, [("Le poursuivre", lambda g: ev_vol_objet(g,"poursuivre")), ("Négocier", lambda g: ev_vol_objet(g,"negocier")), ("Laisser tomber", lambda g: res(g, "Tu évites l'affrontement, mais le voleur s'éloigne avec ton bien.", bonheur=-2, karma=1))])

def ev_vendeur_collectionneur(g, choix):
    rares = [x for x in g.get("inventaire_objets", []) if x.get("rarete") in ("S","SS")]
    if not rares:
        return res(g, "Le collectionneur cherche des objets de classe S ou SS, mais tu n'en possèdes aucun pour le moment.", reputation=1)
    item = rares[0]
    obj = objet_def(item.get("id"))
    prix = int((obj["vente"] if obj else item.get("prix_achat", 1000)*.5) * 1.35)
    if choix == "vendre":
        g["argent"] += prix
        g["inventaire_objets"].remove(item)
        return res(g, f"Tu vends {item['nom']} au collectionneur pour {fm(g,prix)}, au-dessus du prix de revente habituel.", reputation=2)
    return res(g, "Tu gardes ton objet rare. Le collectionneur te laisse sa carte et pourrait revenir plus tard.", reputation=1, bonheur=2)

event("collectionneur_rare", "Un collectionneur recherche une relique", "💎 Un collectionneur itinérant propose de payer plus cher que le marché pour un objet de classe S ou SS.", lambda g: g.get("age", 0) >= 16 and any(x.get("rarete") in ("S","SS") for x in g.get("inventaire_objets", [])) and random.random() < .12, [("Vendre l'objet rare", lambda g: ev_vendeur_collectionneur(g,"vendre")), ("Le conserver", lambda g: ev_vendeur_collectionneur(g,"garder"))])

event("coffre_tresor", "Un coffre mystérieux", "🧰 Lors d'une mission ou d'une exploration, tu découvres un coffre ancien. Il peut contenir un objet banal, un parchemin rare, une arme de classe S ou un trésor SS… mais certains coffres sont piégés.", lambda g: g.get("univers") == "manga" and g.get("age", 0) >= 8 and random.random() < .22, [("Inspecter le mécanisme", lambda g: ev_coffre_tresor(g,"inspecter")), ("Ouvrir le coffre", lambda g: ev_coffre_tresor(g,"ouvrir"))])



EVENTS_BY_ID = {e["id"]: e for e in EVENTS}


def tirer_evenement(g):
    eligibles = [e for e in EVENTS if e["cond"](g)]
    if not eligibles:
        return
    urgents = [e for e in eligibles if e["id"] in ("ami_revanche", "bijuu_voix", "sharingan_vole", "akatsuki_recrutement", "recrutement_agence_heroique", "famille_sortie", "parent_colere", "dispute_fratrie", "sortie_amis", "onepiece_faction_choice", "onepiece_fruit_demon", "jjk_eveil_occult",
        "monde_guerre", "monde_paix", "monde_devise", "monde_independance", "monde_attentat", "monde_gang", "monde_arrestations", "monde_president",
        "naruto_hokage_mort", "naruto_akatsuki_war", "naruto_kazekage_manipule", "naruto_peace_treaty",
        "jjk_fléau_majeur", "jjk_crise_ecole", "onepiece_offensive_marine", "onepiece_independence",
        "fantasy_guerre", "fantasy_paix", "fantasy_dragon_capitale", "fantasy_nouvelle_monnaie")]
    metiers = [e for e in eligibles if e["id"].startswith("metier_")]
    manga = [e for e in eligibles if e["id"] in ("bijuu_naissance", "bijuu_scellage", "heritage_clan", "mission_ninja_rare", "bijuu_voix", "sharingan_vole", "akatsuki_recrutement") or e["id"].startswith(("jjk_", "onepiece_", "naruto_"))]
    autres = [e for e in eligibles if e not in metiers and e not in urgents and e not in manga]
    # Priorité aux conséquences déjà annoncées, puis au contenu propre à l'univers et au métier.
    if urgents and random.random() < .72:
        e = random.choice(urgents)
    elif g.get("univers") == "manga" and manga and random.random() < .68:
        saga = g.get("saga_manga", "naruto")
        saga_events = [x for x in manga if (saga == "jujutsu" and x["id"].startswith("jjk_")) or (saga == "onepiece" and x["id"].startswith("onepiece_")) or (saga == "naruto" and (x["id"].startswith("naruto_") or x["id"] in ("bijuu_naissance", "bijuu_scellage", "heritage_clan", "mission_ninja_rare", "bijuu_voix", "sharingan_vole", "akatsuki_recrutement")))]
        e = random.choice(saga_events or (manga if saga == "naruto" else (autres or eligibles)))
    elif metiers and random.random() < .68:
        e = random.choice(metiers)
    else:
        e = random.choice(autres or eligibles)
    if e["id"] in WORLD_EVENT_IDS:
        concerne, mode = est_concerne_par_evenement(g, e["id"])
        if not concerne:
            actualite_monde(g, e["titre"], e["texte"])
            g["actualites_monde"][-1]["type"] = "evenement"
            log(g, f"📰 Tu apprends la nouvelle : {e['titre']}. Tu n'as pas de rôle décisionnaire à ce niveau.")
            g["evt"] = None
            return
        g["evt"] = {"id": e["id"], "texte": e["texte"], "mode": mode}
        if mode == "mission":
            g["evt"]["participation_obligatoire"] = True
    else:
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


def action_temps_famille(g, cible):
    if cible == "parents":
        personnes = [p for p in g.get("parents", []) if p.get("vivant", True)]
        if not personnes:
            raise Refus("Tu n'as plus de parent vivant avec qui passer du temps.")
        personne = min(personnes, key=lambda x: x.get("relation", 65))
        gain = 15 if "affectueuse" in personne.get("personnalite", "").lower() or "affectueux" in personne.get("personnalite", "").lower() else 10
        personne["relation"] = clamp(personne.get("relation", 65) + gain)
        personne["confiance"] = clamp(personne.get("confiance", 60) + 6)
        g["famille_relations"] = clamp(g.get("famille_relations", 65) + 5)
        g.setdefault("chronologie_famille", []).append({"age": g.get("age", 0), "titre": "Temps passé en famille", "texte": f"Tu as passé du temps avec {personne['nom']}."})
        return f"☕ Tu passes un bon moment avec {personne['nom']} ({personne.get('personnalite', 'personnalité inconnue')}). Votre relation s'améliore."
    if cible == "fratrie":
        if not g.get("fratrie"):
            raise Refus("Tu n'as pas de frère ou sœur enregistré·e.")
        personne = min(g["fratrie"], key=lambda x: x.get("relation", 60))
        personne["relation"] = clamp(personne.get("relation", 60) + 12)
        return f"🎮 Tu partages un moment avec {personne['nom']}. Votre lien se renforce."
    if cible == "amis":
        if not g.get("amis"):
            raise Refus("Tu n'as pas encore d'ami·e proche.")
        personne = min(g["amis"], key=lambda x: x.get("relation", 50))
        if personne.get("statut") == "ennemi·e":
            personne["relation"] = clamp(personne.get("relation", 20) + 8)
            if personne["relation"] >= 45:
                personne["statut"] = "ami·e"
                log(g, f"🕊️ Tu as renoué avec {personne['nom']}.")
            return f"🤝 Tu proposes une trêve à {personne['nom']}. La rivalité peut s'apaiser."
        bonus = 14 if personne.get("personnalite") in ("Loyal·e", "Sensible") else 9
        personne["relation"] = clamp(personne.get("relation", 50) + bonus)
        personne.setdefault("souvenirs", []).append({"age": g.get("age", 0), "texte": "Vous avez passé du temps ensemble."})
        return f"🍕 Tu sors avec {personne['nom']} ({personne.get('personnalite', 'personnalité inconnue')}). Votre amitié se renforce."
    enfants = [e for e in g.get("enfants", []) if e.get("age", 0) < 18]
    if not enfants:
        raise Refus("Tu n'as pas d'enfant mineur avec qui passer du temps.")
    enfant = min(enfants, key=lambda x: x.get("relation", 65))
    enfant["relation"] = clamp(enfant.get("relation", 65) + 12)
    return f"❤️ Tu consacres du temps à {enfant['nom']}. Votre relation s'améliore."


def action(aid, cout=1, prison_ok=False):
    def deco(fn):
        ACTIONS[aid] = (fn, cout, prison_ok)
        return fn
    return deco


ENTRAINEMENTS = {
    "real": ("🥋 Cours d'arts martiaux", "Tu t'inscris à un dojo."),
    "manga": ("🌊 S'entraîner sous une cascade", "Tu médites sous l'eau glacée, en canalisant ton chakra."),
    "fantasy": ("📖 Étudier la magie", "Tu plonges dans un grimoire poussiéreux."),
}


@action("temps_parents")
def a_temps_parents(g):
    return action_temps_famille(g, "parents")

@action("temps_fratrie")
def a_temps_fratrie(g):
    return action_temps_famille(g, "fratrie")

@action("temps_amis")
def a_temps_amis(g):
    return action_temps_famille(g, "amis")

@action("temps_enfant")
def a_temps_enfant(g):
    return action_temps_famille(g, "enfant")



@action("entrainement_chakra")
def a_entrainement_chakra(g):
    return entrainement_chakra(g)

@action("apprendre_jutsu")
def a_apprendre_jutsu(g, nom):
    return apprendre_jutsu(g, nom)

@action("combat_jutsu")
def a_combat_jutsu(g, nom):
    return combat_jutsu(g, nom)

@action("entrainement_hero")
def a_entrainement_hero(g):
    return entrainer_hero(g)

@action("ameliorer_armure")
def a_ameliorer_armure(g):
    return ameliorer_armure(g)

@action("actualite_choix")
def a_actualite_choix(g, choix, reaction):
    return actualite_choix(g, choix, reaction)

@action("notoriete_action")
def a_notoriete_action(g):
    if g.get("saga_manga") != "onepiece" or g.get("faction_manga") not in ("Pirates", "Empereur des mers"):
        raise Refus("Cette action est réservée aux pirates et Empereurs des mers.")
    gain = random.randint(8, 16)
    g["notoriete_manga"] = min(100, g.get("notoriete_manga", 0) + gain)
    chg(g, celebrite=3, force=2, karma=-2)
    if g["notoriete_manga"] >= 80:
        g["faction_manga"] = "Empereur des mers"
        return f"👑 Ta notoriété atteint {g['notoriete_manga']}/100 : le monde te reconnaît comme Empereur des mers !"
    return f"📰 Ton équipage accomplit un exploit retentissant : +{gain} de notoriété ({g['notoriete_manga']}/100)."

def interaction_pnj(g, genre, index=0, choix="sortie"):
    """Interaction directe avec un PNJ, consommant une action annuelle."""
    if genre == "parent":
        personnes = [p for p in g.get("parents", []) if p.get("vivant", True)]
    elif genre == "fratrie":
        personnes = g.get("fratrie", [])
    else:
        personnes = g.get("amis", [])
    if not personnes:
        raise Refus("Il n'y a personne avec qui faire cette interaction.")
    if index >= len(personnes):
        index = 0
    p = personnes[index]
    nom = p.get("nom", "cette personne")
    relation = p.get("relation", 60)
    if choix == "restaurant":
        prix = int(250 * ville_info(g)["cout"])
        if g["argent"] < prix:
            raise Refus(f"Il te faut {fm(g, prix)} pour inviter {nom}.")
        g["argent"] -= prix
        p["relation"] = clamp(relation + 14)
        if genre == "parent":
            g["famille_relations"] = clamp(g.get("famille_relations", 65) + 7)
        chg(g, bonheur=6, karma=2)
        return f"🍽️ Tu invites {nom} au restaurant. Vous parlez de vos souvenirs et votre lien se renforce."
    if choix == "dispute":
        p["relation"] = clamp(relation - random.randint(8, 16))
        if genre == "parent":
            g["famille_relations"] = clamp(g.get("famille_relations", 65) - 5)
        if genre == "ami":
            p["statut"] = "ennemi·e" if p["relation"] < 25 else p.get("statut", "ami·e")
            programmer_consequence(g, random.randint(2, 5), "Une dispute qui n'est pas oubliée", f"{nom} se souvient de votre dispute. Vos chemins pourraient se recroiser au pire moment.", {"bonheur": -2})
        chg(g, bonheur=-4, karma=-2)
        return f"💢 Tu te disputes avec {nom}. Des mots ont dépassé ta pensée ; la relation baisse."
    if choix == "excuses":
        p["relation"] = clamp(relation + 10)
        chg(g, bonheur=3, karma=3)
        return f"🕊️ Tu présentes des excuses à {nom}. Ce n'est pas magique, mais la conversation apaise les tensions."
    if choix == "sortie":
        p["relation"] = clamp(relation + random.randint(8, 15))
        chg(g, bonheur=6)
        if genre == "ami":
            p.setdefault("souvenirs", []).append(f"Sortie à {g.get('age', 0)} ans")
            if random.random() < .15:
                g["reputation"] = clamp(g.get("reputation", 50) + 2)
        return f"🎉 Tu sors avec {nom}. Vous partagez une histoire qui deviendra peut-être un souvenir important."
    if choix == "secret":
        p["relation"] = clamp(relation + 6)
        p["confiance"] = clamp(p.get("confiance", 50) + 12)
        programmer_consequence(g, random.randint(2, 4), "Une confidence à garder", f"{nom} t'a confié un secret. Un jour, il faudra peut-être choisir entre loyauté et vérité.", {"karma": 2})
        return f"🤫 Tu te confies à {nom}. La confiance augmente, mais tu portes désormais son secret."
    raise Refus("Interaction inconnue.")

@action("pnj_parent_resto")
def a_pnj_parent_resto(g, index=0):
    return interaction_pnj(g, "parent", index, "restaurant")

@action("pnj_parent_dispute")
def a_pnj_parent_dispute(g, index=0):
    return interaction_pnj(g, "parent", index, "dispute")

@action("pnj_parent_excuses")
def a_pnj_parent_excuses(g, index=0):
    return interaction_pnj(g, "parent", index, "excuses")

@action("pnj_fratrie_sortie")
def a_pnj_fratrie_sortie(g, index=0):
    return interaction_pnj(g, "fratrie", index, "sortie")

@action("pnj_fratrie_dispute")
def a_pnj_fratrie_dispute(g, index=0):
    return interaction_pnj(g, "fratrie", index, "dispute")

@action("pnj_ami_sortie")
def a_pnj_ami_sortie(g, index=0):
    return interaction_pnj(g, "ami", index, "sortie")

@action("pnj_ami_secret")
def a_pnj_ami_secret(g, index=0):
    return interaction_pnj(g, "ami", index, "secret")

@action("pnj_ami_dispute")
def a_pnj_ami_dispute(g, index=0):
    return interaction_pnj(g, "ami", index, "dispute")

@action("pnj_ami_excuses")
def a_pnj_ami_excuses(g, index=0):
    return interaction_pnj(g, "ami", index, "excuses")

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



TACHES_METIER = {
    "justicier_armure": ["Tester un gadget", "Réparer l'armure", "Neutraliser une menace"],
    "tisseur_urbain": ["Patrouiller les toits", "Sauver un passant", "Enquêter sur un criminel"],
    "heros_energie": ["Protéger un quartier", "Stabiliser une source d'énergie", "Entraîner ses pouvoirs"],
    "metamorphe": ["Contrôler sa transformation", "Mission d'infiltration", "Entraîner ses formes"],
    "telepathe": ["Entraîner sa concentration", "Protéger un esprit", "Résoudre un conflit"],
    "heros_pro": ["Sauver des civils", "Entraînement de terrain", "Enquêter sur une menace"],
    "policier": ["Résoudre une enquête", "Aider les habitants", "Préparer un rapport"],
    "pompier": ["Exercice de secours", "Intervention d'urgence", "Vérifier le matériel"],
    "medecin": ["Prendre en charge un patient", "Formation médicale", "Améliorer le service"],
    "infirmier": ["Soigner un patient", "Coordonner les soins", "Préparer le matériel"],
    "enseignant": ["Préparer un cours", "Aider un élève", "Créer un projet scolaire"],
    "dev": ["Livrer une fonctionnalité", "Corriger un bug complexe", "Documenter le projet"],
    "avocat": ["Préparer un dossier", "Défendre un client", "Étudier la jurisprudence"],
    "chef": ["Créer un plat", "Gérer le service", "Former un collègue"],
    "entrepreneur": ["Signer un contrat", "Améliorer l'entreprise", "Fidéliser un client"],
}
TACHES_DEFAUT = ["Accomplir une mission", "Se former", "Aider un collègue"]

@action("tache_metier")
def a_tache_metier(g, choix=None):
    if not g.get("metier"):
        raise Refus("Tu dois avoir un emploi pour réaliser une tâche professionnelle.")
    options = TACHES_METIER.get(g["metier"], TACHES_DEFAUT)
    if choix not in options:
        raise Refus("Cette tâche ne correspond pas à ton métier actuel.")
    g["performance_metier"] = min(100, g.get("performance_metier", 0) + random.randint(7, 12))
    g["taches_metier"] = g.get("taches_metier", 0) + 1
    chg(g, bonheur=2, intelligence=1)
    if g["metier"] in ORIGINES_METIERS:
        g["niveau_pouvoir"] = min(100, g.get("niveau_pouvoir", 0) + 2)
    log(g, f"🛠️ Travail accompli : {choix}. Performance professionnelle : {g['performance_metier']}/100.")
    return f"🛠️ {choix} : tu as fait tes preuves. Performance +, total {g['performance_metier']}/100."

@action("promotion")
def a_promotion(g):
    if not g["metier"] or JOBS[g["metier"]]["cat"] == JE:
        raise Refus("Pas de promotion possible ici.")
    if g.get("taches_metier", 0) < 2 or g.get("performance_metier", 0) < 15:
        raise Refus("Avant de demander une augmentation, réalise au moins 2 tâches professionnelles et atteins 15 points de performance.")
    if g["grade"] >= 3:
        raise Refus("🏆 Tu es déjà au sommet !")
    if random.random() < 0.15 + g["stats"]["intelligence"] / 300 + 0.04 * g["annees_metier"]:
        g["grade"] += 1
        g["performance_metier"] = max(0, g.get("performance_metier", 0) - 12)
        g["taches_metier"] = max(0, g.get("taches_metier", 0) - 1)
        chg(g, bonheur=6)
        log(g, f"📈 Augmentation obtenue après {g.get('taches_metier', 0)} tâche(s) professionnelle(s) restante(s).")
        return f"📈 Promotion : {JOBS[g['metier']]['grades'][g['grade']]} ! Ton salaire augmente."
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
    {"id": "chakra_plus", "nom": "Réserve de chakra", "emoji": "🌀", "prix": 35, "desc": "Augmente durablement ta réserve de chakra de 10 (univers Naruto)."},
    {"id": "clan_heritage", "nom": "Parchemin d'héritage", "emoji": "📜", "prix": 45, "desc": "Débloque une chance d'héritage de clan lors d'un événement Naruto."},
    {"id": "aide_hero", "nom": "Soutien de l'Initiative", "emoji": "🦸", "prix": 40, "desc": "Renforce ton entraînement héroïque et ta réputation auprès de l'agence."},
    {"id": "chance", "nom": "Talisman de chance", "emoji": "🍀", "prix": 30, "desc": "Une fois acheté, augmente légèrement la chance lors des événements futurs."},
    {"id": "real_reflexes", "nom": "Réflexes surhumains", "emoji": "⚡", "prix": 45, "desc": "Univers réel : améliore force et santé, comme un entraînement intensif."},
    {"id": "real_armure", "nom": "Prototype d'armure", "emoji": "🦾", "prix": 65, "desc": "Univers réel : débloque une amélioration technologique héroïque."},
    {"id": "jjk_energie", "nom": "Réserve d'énergie occulte", "emoji": "👁️", "prix": 40, "desc": "Jujutsu Kaisen : augmente l'énergie occulte."},
    {"id": "jjk_technique", "nom": "Manuel de technique maudite", "emoji": "📕", "prix": 55, "desc": "Jujutsu Kaisen : débloque une technique maudite prédéfinie."},
    {"id": "onepiece_haki", "nom": "Entraînement au Haki", "emoji": "🌊", "prix": 45, "desc": "One Piece : augmente la force et la notoriété."},
    {"id": "onepiece_fruit", "nom": "Fruit du démon mystérieux", "emoji": "🍈", "prix": 70, "desc": "One Piece : attribue un fruit du démon aléatoire prédéfini."},
    {"id": "fantasy_mana", "nom": "Cristal de mana", "emoji": "🔮", "prix": 40, "desc": "Fantasy : augmente ta réserve magique et ton intelligence."},
    {"id": "fantasy_dragon", "nom": "Écaille de dragon", "emoji": "🐉", "prix": 60, "desc": "Fantasy : débloque un pouvoir draconique."},
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
    {"id": "survivant", "nom": "Tenir bon", "desc": "Atteindre 50 ans en étant vivant", "recompense": 25, "test": lambda g: g.get("age", 0) >= 50 and g.get("vivant", True)},
    {"id": "longue_vie", "nom": "Une vie bien remplie", "desc": "Atteindre 80 ans", "recompense": 40, "test": lambda g: g.get("age", 0) >= 80},
    {"id": "diplome", "nom": "Diplôme en poche", "desc": "Obtenir au moins un diplôme supérieur", "recompense": 20, "test": lambda g: g.get("edu", 0) >= 5},
    {"id": "famille_nombreuse", "nom": "Transmettre la vie", "desc": "Avoir au moins 3 enfants", "recompense": 25, "test": lambda g: len(g.get("enfants", [])) >= 3},
    {"id": "fortune_riche", "nom": "Fortune solide", "desc": "Posséder 100 000 unités de monnaie", "recompense": 30, "test": lambda g: g.get("argent", 0) >= 100000},
    {"id": "ami_ennemi", "nom": "Rivalité légendaire", "desc": "Avoir au moins une rivalité enregistrée", "recompense": 15, "test": lambda g: bool(g.get("rivalites", []))},
    {"id": "manga_technique", "nom": "Maîtrise technique", "desc": "Apprendre au moins une technique de ton univers manga", "recompense": 18, "test": lambda g: g.get("univers") == "manga" and bool(g.get("jutsu") or g.get("techniques_maudites"))},
    {"id": "pirate_notoriete", "nom": "Une prime qui fait trembler", "desc": "Atteindre 60 de notoriété", "recompense": 25, "test": lambda g: g.get("saga_manga") == "onepiece" and g.get("notoriete_manga", 0) >= 60},
    {"id": "heroique", "nom": "Héros reconnu", "desc": "Atteindre 50 de réputation héroïque", "recompense": 25, "test": lambda g: g.get("reputation_heroique", 0) >= 50},
    {"id": "premier_enfant", "nom": "Nouvelle génération", "desc": "Avoir ton premier enfant", "recompense": 20, "test": lambda g: len(g.get("enfants", [])) >= 1},
    {"id": "missions_10", "nom": "Professionnel·le confirmé·e", "desc": "Réussir 10 missions ou événements de métier", "recompense": 30, "test": lambda g: g.get("missions_reussies", 0) >= 10},
    {"id": "missions_25", "nom": "Vétéran·e", "desc": "Réussir 25 missions ou événements de métier", "recompense": 55, "test": lambda g: g.get("missions_reussies", 0) >= 25},
    {"id": "premiere_action", "nom": "Premier pas", "desc": "Effectuer ta première action personnelle", "recompense": 5, "test": lambda g: g.get("age", 0) >= 1 and g.get("actions", 4) < 4},
    {"id": "premier_ami", "nom": "Le début d'une amitié", "desc": "Avoir au moins un ami", "recompense": 8, "test": lambda g: len(g.get("amis", [])) >= 1},
    {"id": "trois_amis", "nom": "Bande soudée", "desc": "Avoir trois amis", "recompense": 15, "test": lambda g: len(g.get("amis", [])) >= 3},
    {"id": "premier_metier", "nom": "Premier contrat", "desc": "Travailler pendant au moins un an", "recompense": 12, "test": lambda g: bool(g.get("metier")) and g.get("annees_metier", 0) >= 1},
    {"id": "premier_achat", "nom": "Premier achat boutique", "desc": "Acheter un article dans la boutique", "recompense": 8, "test": lambda g: bool(g.get("inventaire", []))},
    {"id": "survivre_crise", "nom": "Garder son sang-froid", "desc": "Vivre un événement mondial et rester en vie", "recompense": 12, "test": lambda g: bool(g.get("actualites_monde")) and g.get("vivant", True)},
    {"id": "dix_evenements", "nom": "Une vie mouvementée", "desc": "Voir dix événements dans ta chronologie", "recompense": 20, "test": lambda g: len(g.get("evenements_vus", [])) >= 10},
    {"id": "univers_maitrise", "nom": "Pouvoir éveillé", "desc": "Débloquer au moins un pouvoir", "recompense": 15, "test": lambda g: bool(g.get("pouvoirs", [])) or bool(g.get("jutsu", [])) or bool(g.get("techniques_maudites", [])) or bool(g.get("fruit_demon", ""))},
]

def acheter_article(g, article_id):
    article = next((a for a in BOUTIQUE if a["id"] == article_id), None)
    if not article: raise Refus("Article introuvable.")
    if article_id in g.get("inventaire", []): raise Refus("Tu possèdes déjà cet article.")
    restrictions = {
        "real_reflexes": g.get("univers") == "real",
        "real_armure": g.get("univers") == "real",
        "jjk_energie": g.get("univers") == "manga" and g.get("saga_manga") == "jujutsu",
        "jjk_technique": g.get("univers") == "manga" and g.get("saga_manga") == "jujutsu",
        "onepiece_haki": g.get("univers") == "manga" and g.get("saga_manga") == "onepiece",
        "onepiece_fruit": g.get("univers") == "manga" and g.get("saga_manga") == "onepiece",
        "fantasy_mana": g.get("univers") == "fantasy",
        "fantasy_dragon": g.get("univers") == "fantasy",
    }
    if article_id in restrictions and not restrictions[article_id]:
        raise Refus("Cet article est réservé à un autre univers.")
    if article_id == "onepiece_fruit" and g.get("fruit_demon"):
        raise Refus("Tu possèdes déjà un fruit du démon.")
    if article_id == "jjk_technique" and not any(JUTSU[x].get("saga") == "jujutsu" and x not in g.get("techniques_maudites", []) for x in JUTSU):
        raise Refus("Tu connais déjà toutes les techniques maudites disponibles.")
    if g.get("jetons", 0) < article["prix"]: raise Refus(f"Il te manque {article['prix'] - g.get('jetons', 0)} jeton(s).")
    g["jetons"] -= article["prix"]
    g.setdefault("inventaire", []).append(article_id)
    if article_id == "couronne": chg(g, celebrite=5)
    elif article_id == "porte_bonheur": chg(g, karma=5)
    elif article_id == "chakra_plus":
        if g.get("univers") != "manga" or g.get("saga_manga") != "naruto":
            g["inventaire"].remove(article_id)
            g["jetons"] += article["prix"]
            raise Refus("Cette amélioration est réservée à l'univers Naruto.")
        g["chakra"] = min(100, g.get("chakra", 50) + 10)
    elif article_id == "clan_heritage":
        if g.get("univers") != "manga" or g.get("saga_manga") != "naruto":
            g["inventaire"].remove(article_id)
            g["jetons"] += article["prix"]
            raise Refus("Cet héritage est réservé à l'univers Naruto.")
        g["chance_heritage_clan"] = True
    elif article_id == "aide_hero":
        g["entrainement_heroique"] = min(100, g.get("entrainement_heroique", 0) + 15)
        g["reputation_heroique"] = min(100, g.get("reputation_heroique", 0) + 8)
    elif article_id == "chance":
        g["bonus_chance_evenements"] = min(5, g.get("bonus_chance_evenements", 0) + 1)
    elif article_id == "kit_soins": chg(g, sante=12)
    elif article_id == "energie": chg(g, bonheur=8)
    elif article_id == "real_reflexes":
        if g.get("univers") != "real": raise Refus("Réservé à l'univers réel.")
        chg(g, force=8, sante=4)
    elif article_id == "real_armure":
        if g.get("univers") != "real": raise Refus("Réservé à l'univers réel.")
        g["armure_niveau"] = min(5, g.get("armure_niveau", 0) + 1)
        if "Armure prototype" not in g.setdefault("pouvoirs", []): g["pouvoirs"].append("Armure prototype")
        g["origine_heroique"] = "Technologie"
    elif article_id == "jjk_energie":
        if g.get("univers") != "manga" or g.get("saga_manga") != "jujutsu": raise Refus("Réservé à Jujutsu Kaisen.")
        g["energie_occulte"] = min(100, g.get("energie_occulte", 0) + 20)
    elif article_id == "jjk_technique":
        if g.get("univers") != "manga" or g.get("saga_manga") != "jujutsu": raise Refus("Réservé à Jujutsu Kaisen.")
        choix = [x for x in JUTSU if JUTSU[x].get("saga") == "jujutsu" and x not in g.get("techniques_maudites", [])]
        if not choix: raise Refus("Tu connais déjà toutes les techniques maudites disponibles.")
        technique = random.choice(choix)
        g.setdefault("techniques_maudites", []).append(technique)
    elif article_id == "onepiece_haki":
        if g.get("univers") != "manga" or g.get("saga_manga") != "onepiece": raise Refus("Réservé à One Piece.")
        chg(g, force=8, celebrite=3)
        g["notoriete_manga"] = min(100, g.get("notoriete_manga", 0) + 8)
    elif article_id == "onepiece_fruit":
        if g.get("univers") != "manga" or g.get("saga_manga") != "onepiece": raise Refus("Réservé à One Piece.")
        if g.get("fruit_demon"): raise Refus("Tu possèdes déjà un fruit du démon.")
        g["fruit_demon"] = random.choice(["Gomu Gomu", "Mera Mera", "Ope Ope", "Bara Bara", "Suna Suna", "Hie Hie", "Tori Tori modèle phénix", "Goro Goro"])
        g.setdefault("pouvoirs", []).append(g["fruit_demon"])
    elif article_id == "fantasy_mana":
        if g.get("univers") != "fantasy": raise Refus("Réservé à l'univers fantasy.")
        g["energie_magique"] = min(100, g.get("energie_magique", 0) + 20)
        chg(g, intelligence=4)
    elif article_id == "fantasy_dragon":
        if g.get("univers") != "fantasy": raise Refus("Réservé à l'univers fantasy.")
        if "Sang draconique" not in g.setdefault("pouvoirs", []): g["pouvoirs"].append("Sang draconique")
        g["niveau_pouvoir"] = min(100, g.get("niveau_pouvoir", 0) + 10)
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
                   argent=max(0, int(parent.get("argent", 0) * taux_heritage)), jetons=parent.get("jetons", 0), generation=parent.get("generation", 1)+1,
                   heritage_parent=parent.get("nom", ""), famille="héritage familial", fam=parent.get("fam", 1),
                   famille_relations=clamp(parent.get("famille_relations", 60)+5), amis=[dict(a) for a in parent.get("amis", [])],
                   chronologie_famille=parent.get("chronologie_famille", [])[:],
                   historique_choix=parent.get("historique_choix", [])[:],
                   rivalites=parent.get("rivalites", [])[:], secrets=parent.get("secrets", [])[:],
                   pouvoirs=parent.get("pouvoirs", [])[:], niveau_pouvoir=max(0, parent.get("niveau_pouvoir", 0)//2),
                   reputation=clamp(parent.get("reputation", 50)//2),
                   parents=[{"nom": parent.get("nom", "Parent"), "role": "Parent", "age": parent.get("age", 0),
                             "relation": lien, "vivant": False, "personnalite": "Héritage familial", "confiance": lien}])
    nouveau["journal"] = parent.get("journal", [])[:] + [[enfant.get("age", 0), f"🧬 Génération {nouveau['generation']} : {nouveau['nom']} reprend le flambeau de {parent['nom']}. Lien parent-enfant : {lien}/100. Héritage : {fm(nouveau, nouveau['argent'])}."]]
    nouveau["avatar"] = dict(parent.get("avatar", defauts()["avatar"]))
    nouveau["stats"] = {k: clamp(v + random.randint(-8, 8)) for k, v in parent.get("stats", {}).items()}
    nouveau["stats"]["sante"] = max(45, nouveau["stats"]["sante"])
    nouveau["stats"]["celebrite"] = max(0, nouveau["stats"]["celebrite"] // 2)
    nouveau["trait"] = random.choice(["Surdoué·e", "Athlète né·e", "Charismatique", "Chanceux·se", "Rebelle", "Courageux·se"])
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
    verifier_pouvoirs(g)
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
    if e["id"] == "ami_revanche" and g.get("ami_vexe"):
        g["ami_vexe"]["retour_declenche"] = True
    mode_evenement = g.get("evt", {}).get("mode")
    participation_obligatoire = g.get("evt", {}).get("participation_obligatoire", False)
    g["evt"] = None
    txt = accord_genre_texte(fn(g), g)
    g.setdefault("historique_choix", []).append({"age": g["age"], "evenement": e["titre"], "choix": label})
    if e["id"] not in g.setdefault("evenements_vus", []):
        g["evenements_vus"].append(e["id"])
    if participation_obligatoire or e["id"].startswith("metier_") or e["id"].startswith("mission_"):
        # Les handlers de mission mettent déjà à jour les réussites/échecs.
        if not e["id"].startswith("mission_"):
            g["missions_reussies"] = g.get("missions_reussies", 0) + 1
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
    g["origine_heroique"] = "Aucune"
    pouvoirs_origine = {
        "Armure technologique": ["Ingénierie", "Gadgets tactiques"],
        "Mutation métamorphe": ["Métamorphose"],
        "Arachnide urbain": ["Sens du danger", "Agilité surhumaine"],
        "Énergie cosmique": ["Projection d'énergie"],
        "Télépathie": ["Télépathie"], "Magie": ["Sens magique"],
        "Vigilante entraîné": ["Arts martiaux", "Discrétion"], "Aucune": []}
    g["pouvoirs"] = pouvoirs_origine[g["origine_heroique"]][:]
    set_game(g)
    sauver(g)


# ======================================================================
#  INTERFACE
# ======================================================================
CSS = """
<style>

/* Interface plus nette, contrastée et inspirée des jeux de simulation */
:root { color-scheme: dark; }
.stApp {background: radial-gradient(ellipse at 15% 0%, #182b4d 0%, #0b1220 44%, #080d18 100%); color:#f1f5f9;}
.block-container {max-width: 1450px; padding-top: 1rem; padding-bottom: 2.5rem; color:#f1f5f9;}
.stMarkdown, .stCaption, label, p, li, [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {color:#e2e8f0;}
[data-testid="stCaptionContainer"] p {color:#aab8cc !important;}
h1,h2,h3,h4 {color:#f8fafc !important;}
div[data-testid="stVerticalBlockBorderWrapper"] {background:linear-gradient(145deg,#17243a,#111a2a); border:1px solid #334155; box-shadow:0 10px 30px #02061766; border-radius:16px;}
.stAlert {background:#162b47; border:1px solid #315780; color:#f8fafc;}
.stButton > button {color:#f8fafc; font-weight:700; background:linear-gradient(135deg,#243b5b,#1e293b); border:1px solid #506782;}
.stButton > button:hover {color:#fff; border-color:#60a5fa; background:linear-gradient(135deg,#1d4ed8,#6d28d9);}
button[kind="primary"] {color:white !important; background:linear-gradient(100deg,#7c3aed,#2563eb,#0891b2) !important; border:0; box-shadow:0 8px 24px #2563eb55;}
.world-feed-title {font-size:1.1rem; font-weight:900; color:#f8fafc; letter-spacing:.06em; padding:10px 12px; border-left:4px solid #38bdf8; background:linear-gradient(90deg,#0e749055,transparent); border-radius:8px; margin:12px 0;}
.avatar-profile-card {position:relative; overflow:hidden; min-height:250px; border-radius:24px; background:radial-gradient(circle at 50% 38%,#334e76 0%,#1c2b43 48%,#111827 100%); border:1px solid #526987; box-shadow:0 16px 34px #02061777; display:flex; flex-direction:column; align-items:center; justify-content:center; padding:10px 8px 14px; margin-bottom:12px;}
.avatar-halo {position:absolute; width:195px; height:195px; border-radius:50%; top:22px; background:linear-gradient(135deg,#f97316,#ea580c,#7c2d12); box-shadow:0 0 0 8px #f9731620,0 0 45px #f9731640;}
.avatar-art {z-index:1; position:relative; animation:float-avatar 4s ease-in-out infinite; filter:drop-shadow(0 12px 14px #02061799);}
.avatar-status {z-index:2; margin-top:-2px; padding:5px 10px; border-radius:999px; background:#0f172aee; border:1px solid #475569; color:#cbd5e1; font-size:.7rem; font-weight:800; letter-spacing:.08em;}
.avatar-status span {display:inline-block; width:7px; height:7px; border-radius:50%; background:#22c55e; margin-right:6px; box-shadow:0 0 8px #22c55e;}
.challenge-stamp {display:inline-block; border:1px solid #22c55e; border-radius:6px; color:#86efac; background:#14532d88; padding:3px 7px; font-size:.68rem; font-weight:900; letter-spacing:.05em;}
.challenge-stamp-ready {border-color:#fbbf24; color:#fde68a; background:#78350f88;}

div[data-testid="stTabs"] div[role="tablist"] {gap:.35rem; border-bottom:1px solid #64748b44;}
div[data-testid="stTabs"] button[role="tab"] {border-radius:10px 10px 0 0; padding:.55rem .8rem; font-weight:650; white-space:nowrap;}
div[data-testid="stVerticalBlockBorderWrapper"] {box-shadow:0 6px 22px #02061710; border-radius:16px;}
@media (max-width: 760px) {
  .block-container {padding-left:.65rem !important; padding-right:.65rem !important;}
  div[data-testid="stTabs"] div[role="tablist"] {overflow-x:auto; flex-wrap:nowrap; scrollbar-width:thin;}
  div[data-testid="stTabs"] button[role="tab"] {min-width:max-content; font-size:.88rem; padding:.5rem .65rem;}
  div[data-testid="stHorizontalBlock"] {flex-wrap:wrap !important; gap:.45rem !important;}
  div[data-testid="stHorizontalBlock"] > div {min-width:100% !important; flex:1 1 100% !important;}
  .stButton button {min-height:44px; width:100%;}
  [data-testid="stMetric"] {padding:.45rem; background:#64748b0c; border-radius:12px;}
}

.block-container {padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1500px; animation: page-in .45s ease-out both;}
@keyframes page-in {from {opacity:0; transform:translateY(8px)} to {opacity:1; transform:translateY(0)}}
@keyframes float-avatar {0%,100% {transform:translateY(0)} 50% {transform:translateY(-5px)}}
@keyframes card-in {from {opacity:0; transform:scale(.985)} to {opacity:1; transform:scale(1)}}
@keyframes action-pop {0% {opacity:0; transform:translateY(10px) scale(.97)} 65% {transform:translateY(-2px) scale(1.01)} 100% {opacity:1; transform:translateY(0) scale(1)}}
@keyframes money-burst {0% {transform:scale(.35) rotate(-18deg); opacity:0} 55% {transform:scale(1.25) rotate(8deg); opacity:1} 100% {transform:scale(1) rotate(0)}}
@keyframes combat-shake {0%,100% {transform:translateX(0)} 20% {transform:translateX(-5px) rotate(-1deg)} 40% {transform:translateX(5px) rotate(1deg)} 60% {transform:translateX(-3px)} 80% {transform:translateX(3px)}}
@keyframes gun-flash {0%,100% {filter:brightness(1); box-shadow:0 0 0 transparent} 35% {filter:brightness(1.65); box-shadow:0 0 24px #f97316aa}}
@keyframes heart-float {0% {transform:translateY(7px) scale(.7);opacity:0} 45% {opacity:1} 100% {transform:translateY(-8px) scale(1.1);opacity:0}}
.action-effect {display:flex; align-items:center; gap:.8rem; border:1px solid #64748b55; border-radius:14px; padding:.85rem 1rem; margin:.45rem 0 .8rem; animation:action-pop .42s cubic-bezier(.2,.8,.2,1) both; background:linear-gradient(110deg,#64748b12,#a78bfa12);}
.action-effect .effect-icon {font-size:2rem; display:inline-block; min-width:2.2rem; text-align:center; animation:money-burst .65s ease-out both;}
.action-effect.combat {animation:combat-shake .48s ease-out, action-pop .42s ease-out; border-color:#ef444477; background:linear-gradient(100deg,#ef44441b,#f9731610);}
.action-effect.money {border-color:#eab30888; background:linear-gradient(100deg,#eab30822,#22c55e10);}
.action-effect.gun {animation:gun-flash .55s ease-out, action-pop .42s ease-out; border-color:#f9731688; background:linear-gradient(100deg,#f9731622,#ef444410);}
.action-effect.magic {border-color:#8b5cf688; background:linear-gradient(100deg,#8b5cf622,#06b6d410);}
.action-effect.love {border-color:#ec489988; background:linear-gradient(100deg,#ec489922,#f472b610);}
.stButton button {transition:transform .12s ease, filter .12s ease, box-shadow .12s ease;}
.stButton button:active {transform:scale(.97); filter:brightness(1.15); box-shadow:0 0 0 3px #a78bfa33;}

div[data-testid="stVerticalBlockBorderWrapper"] {animation:card-in .35s ease-out both;}
div[data-testid="stTabs"] button[role="tab"] {font-weight:700; transition:all .18s ease;}
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {border-bottom:2px solid #a78bfa; color:#c4b5fd;}
.stProgress > div > div > div > div {transition:width .6s ease-in-out;}
@media (prefers-reduced-motion: reduce) {*, *::before, *::after {animation:none !important; transition:none !important;}}
/* Responsive mobile layout */
@media (max-width: 768px) {
  .block-container {padding: .65rem .7rem 2rem !important;}
  [data-testid="stHorizontalBlock"] {flex-wrap: wrap !important; gap: .65rem !important;}
  [data-testid="stHorizontalBlock"] > [data-testid="column"] {min-width: min(100%, 280px) !important; flex: 1 1 100% !important;}
  div[data-testid="stTabs"] [data-baseweb="tab-list"] {display:flex !important; flex-wrap:nowrap !important; overflow-x:auto !important; overflow-y:hidden !important; gap:.25rem !important; scrollbar-width:thin; -webkit-overflow-scrolling:touch;}
  div[data-testid="stTabs"] button[role="tab"] {flex:0 0 auto !important; white-space:nowrap !important; padding:.55rem .7rem !important; font-size:.88rem !important;}
  .stButton > button {min-height:2.7rem; white-space:normal; line-height:1.2;}
  div[data-testid="stMetricValue"] {font-size:1.15rem;}
  [data-testid="stSidebar"] {min-width:0;}
  h1 {font-size:1.8rem !important;} h2 {font-size:1.45rem !important;} h3 {font-size:1.2rem !important;}
  div[data-testid="stVerticalBlockBorderWrapper"] {border-radius:13px;}
}
@media (max-width: 420px) {
  .block-container {padding-left:.45rem !important; padding-right:.45rem !important;}
  div[data-testid="stTabs"] button[role="tab"] {font-size:.8rem !important; padding:.5rem .55rem !important;}
  [data-testid="stProgressBar"] {min-width:0;}
}
div[data-testid="stMetricValue"] {font-size: 1.35rem; font-weight: 750;}
[data-testid="stAppViewContainer"] {background: linear-gradient(135deg, #0b1020 0%, #111b35 55%, #17112b 100%);}
[data-testid="stHeader"] {background: transparent;}
[data-testid="stSidebar"] {background: linear-gradient(180deg, #111827, #1e1b4b);}
[data-testid="stVerticalBlockBorderWrapper"] {border-radius: 16px; border-color: #47556966; background: linear-gradient(145deg, #ffffff08, #ffffff02);}
.stButton > button {border-radius: 11px; border: 1px solid #64748b88; transition: all .15s ease;}
.stButton > button:hover {border-color: #a78bfa; transform: translateY(-1px);}
button[kind="primary"] {background: linear-gradient(90deg, #7c3aed, #2563eb); border: 0;}
[data-testid="stProgressBar"] > div > div {background: linear-gradient(90deg, #06b6d4, #8b5cf6);}
h1, h2, h3 {letter-spacing: -.025em;}
/* Finition visuelle : surfaces plus lisibles, focus clavier et cartes plus vivantes */
.stApp {background-image: radial-gradient(circle at 88% 8%, #7c3aed18, transparent 28%), radial-gradient(circle at 4% 42%, #06b6d412, transparent 24%), linear-gradient(135deg,#080d18 0%,#101a30 52%,#17112b 100%);}
[data-testid="stMetric"] {background:linear-gradient(145deg,#1e293b99,#0f172a88); border:1px solid #64748b44; border-radius:14px; padding:.7rem .8rem; box-shadow:inset 0 1px #ffffff08;}
[data-testid="stMetricLabel"] {font-weight:700; letter-spacing:.02em;}
.stProgress > div {background:#ffffff0c; border-radius:999px; padding:2px;}
.stProgress > div > div > div > div {border-radius:999px; background:linear-gradient(90deg,#06b6d4,#3b82f6,#a78bfa);}
.stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"], .stRadio [role="radiogroup"] {border-radius:12px;}
.stButton > button:focus-visible {outline:3px solid #67e8f9 !important; outline-offset:2px;}
hr {border-color:#64748b44;}
[data-testid="stExpander"] {border:1px solid #64748b55; border-radius:14px; overflow:hidden;}
[data-testid="stNotification"] {border-radius:14px;}
</style>
"""


def ecran_accueil():
    st.title("🧬 MA VIE")
    st.markdown('''<div style="padding:18px 20px;border-radius:18px;background:linear-gradient(110deg,#6d28d944,#2563eb33,#0891b233);border:1px solid #a78bfa55;margin-bottom:16px"><h3 style="margin:0">Chaque vie écrit la suivante.</h3><span>Famille · Amitiés · Rivalités · Pouvoirs · Secrets · Héritage</span></div>''', unsafe_allow_html=True)
    st.caption("Une vie. Des choix. Des conséquences. Une histoire qui peut traverser les générations.")
    t1, t2 = st.tabs(["✨ Nouvelle vie", "📂 Charger une partie"])
    s = st.session_state
    for k, v in {"c_nom": "Alex", "c_genre": "Non-binaire", "c_univ": "real", "c_coupe": "Court", "c_couleur": "Noir",
                 "c_peau": "Beige", "c_yeux": "Ronds", "c_bouche": "Sourire", "c_origine_heroique": "Aucune"}.items():
        s.setdefault(k, v)
    with t1:
        c1, c2, c3 = st.columns([1.2, 1, 1])
        with c1:
            st.text_input("Prénom", key="c_nom")
            st.radio("Genre", ["Garçon", "Fille", "Non-binaire"], key="c_genre", horizontal=True)
            st.selectbox("Univers", list(UNIVERS), key="c_univ", format_func=lambda k: UNIVERS[k]["nom"])
            univ = s["c_univ"]
            st.caption(UNIVERS[univ]["desc"])
            st.info("🦸 Les pouvoirs ne se choisissent plus à la naissance : des événements, rencontres et décisions peuvent t'ouvrir les portes de l'Initiative des Gardiens.")
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
    avatar = avatar_svg(g["avatar"], g["age"], g["univers"], j["emoji"] if j else "", 220)
    st.markdown(f"""
    <div class="avatar-profile-card">
      <div class="avatar-halo"></div>
      <div class="avatar-art">{avatar}</div>
      <div class="avatar-status"><span></span> EN VIE · ANNÉE {g.get('age', 0)}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"### {g['nom']}")
    st.caption(f"{g['age']} ans · {g['genre']} · {g['ville']} · {UNIVERS[g['univers']]['nom']}")
    st.caption(f"🧬 Génération {g.get('generation', 1)} · 🪙 {g.get('jetons', 0)} jetons")
    parents_vivants = [p for p in g.get("parents", []) if p.get("vivant", True)]
    if parents_vivants:
        st.caption("👨‍👩‍👧 Parents : " + " · ".join(f"{p.get('role','Parent')} {p.get('nom','?')}" for p in parents_vivants))
    if g.get("fratrie"):
        st.caption("🧑‍🤝‍🧑 Fratrie : " + ", ".join(p.get("nom", "?") for p in g["fratrie"]))
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


def accord_genre_texte(texte, g):
    """Adapte les formes inclusives courantes au genre choisi dans la partie."""
    if not isinstance(texte, str):
        return texte
    genre = g.get("genre", "Non-binaire")
    if genre == "Garçon":
        remplacements = {
            "méchant·e": "méchant", "méchant.e": "méchant", "méchante ou méchant": "méchant",
            "seul·e": "seul", "seul.e": "seul", "blessé·e": "blessé", "blessé.e": "blessé",
            "prêt·e": "prêt", "prêt.e": "prêt", "né·e": "né", "né.e": "né",
            "inquiet·ète": "inquiet", "inquiet.e": "inquiet", "professionnel·le": "professionnel", "professionnel.le": "professionnel",
            "ami·e": "ami", "ami.e": "ami", "ennemi·e": "ennemi", "ennemi.e": "ennemi",
            "loyal·e": "loyal", "loyal.e": "loyal", "candidat·e": "candidat", "candidat.e": "candidat",
        }
    elif genre == "Fille":
        remplacements = {
            "méchant·e": "méchante", "méchant.e": "méchante", "méchante ou méchant": "méchante",
            "seul·e": "seule", "seul.e": "seule", "blessé·e": "blessée", "blessé.e": "blessée",
            "prêt·e": "prête", "prêt.e": "prête", "né·e": "née", "né.e": "née",
            "inquiet·ète": "inquiète", "inquiet.e": "inquiète", "professionnel·le": "professionnelle", "professionnel.le": "professionnelle",
            "ami·e": "amie", "ami.e": "amie", "ennemi·e": "ennemie", "ennemi.e": "ennemie",
            "loyal·e": "loyale", "loyal.e": "loyale", "candidat·e": "candidate", "candidat.e": "candidate",
        }
    else:
        return texte
    # Les variantes les plus longues sont remplacées d'abord pour éviter les collisions.
    for source, cible in sorted(remplacements.items(), key=lambda item: len(item[0]), reverse=True):
        texte = texte.replace(source, cible)
    return texte


def bloc_evenement(g):
    e = EVENTS_BY_ID[g["evt"]["id"]]
    with st.container(border=True):
        mode = g["evt"].get("mode")
        if g["evt"].get("participation_obligatoire"):
            st.subheader(accord_genre_texte(f"🚨 Mission obligatoire : {e['titre']}", g))
            st.info(accord_genre_texte("Ton métier t'oblige à intervenir. Tu dois choisir comment participer, mais tu ne décides pas seul·e de la stratégie globale.", g))
        elif mode == "influence":
            st.subheader(accord_genre_texte(f"🏛️ Décision ouverte aux personnages influents : {e['titre']}", g))
            st.info("Ton rang ou ton influence te permet de prendre part aux choix.")
        else:
            st.subheader(accord_genre_texte(f"📣 {e['titre']}", g))
        st.write(accord_genre_texte(g["evt"]["texte"], g))
        cols = st.columns(len(e["choix"]))
        for i, (label, _fn) in enumerate(e["choix"]):
            cols[i].button(accord_genre_texte(label, g), key=f"evt_{i}", on_click=resolve_event, args=(i,), use_container_width=True)


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
        st.markdown("#### 🛠️ Missions de ton métier")
        st.progress(g.get("performance_metier", 0) / 100, text=f"Performance professionnelle : {g.get('performance_metier', 0)}/100")
        st.progress(g.get("progression_grade", 0) / 100, text=f"Progression vers le grade suivant : {g.get('progression_grade', 0)}/100")
        st.caption(f"Missions réussies : {g.get('missions_reussies', 0)} · Échecs : {g.get('missions_echouees', 0)} · Tâches pratiques : {g.get('taches_metier', 0)}.")
        st.caption("Les missions réussies améliorent tes évaluations. Un échec fait baisser la performance et peut reporter une promotion, voire entraîner une rétrogradation si tes résultats restent mauvais.")
        options_taches = TACHES_METIER.get(g["metier"], TACHES_DEFAUT)
        choix_tache = st.selectbox("Mission disponible", options_taches, key="choix_tache_metier")
        btn("Réaliser la mission (1 action)", "tache_metier", "b_tache_metier", choix=choix_tache)
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
                if key in ORIGINES_METIERS:
                    st.caption("🧬 Origine requise : " + " / ".join(ORIGINES_METIERS[key]))
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
    st.divider()
    st.markdown("#### 🫂 Entretenir ses relations")
    rel1, rel2 = st.columns(2)
    with rel1:
        btn("☕ Voir un parent", "temps_parents", "fam_parents", disabled=not any(p.get("vivant", True) for p in g.get("parents", [])))
        btn("🎮 Voir la fratrie", "temps_fratrie", "fam_fratrie", disabled=not bool(g.get("fratrie")))
    with rel2:
        btn("🍕 Voir un·e ami·e", "temps_amis", "fam_amis", disabled=not bool(g.get("amis")))
        btn("❤️ Temps avec un enfant", "temps_enfant", "fam_enfant", disabled=not any(e.get("age", 0) < 18 for e in g.get("enfants", [])))


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



def tab_univers_specifique(g):
    if g["univers"] == "manga":
        saga = g.get("saga_manga", "naruto")
        titre_saga = {"naruto": "🍥 Naruto — voie du ninja", "jujutsu": "👁️ Jujutsu Kaisen — voie des exorcistes", "onepiece": "🏴‍☠️ One Piece — la route des mers"}.get(saga, "🍥 Monde manga")
        st.markdown(f"## {titre_saga}")
        st.caption("Ton lieu de départ influence les événements, les factions, les techniques et les personnes que tu peux rencontrer.")
        if saga == "naruto":
            st.markdown(f"**Clan :** {g.get('clan') or 'Inconnu'} · **Organisation :** {'Akatsuki ☁️' if g.get('akatsuki') else g.get('statut_ninja', 'Village ninja')}")
            if g.get("bijuu"):
                st.warning(f"🦊 Bijū scellé : **{g['bijuu']}** · maîtrise {g.get('bijuu_maitrise', 0)}/100")
            if g.get("sharingans_voles", 0):
                st.info(f"👁️ Dōjutsu volé(s) : {g['sharingans_voles']} — attention aux conséquences.")
            st.progress(g.get("chakra", 50) / 100, text=f"🔵 Chakra : {g.get('chakra', 50)}/100")
            st.metric("Victoires en combat", g.get("victoires_combat", 0))
            st.metric("Rang actuel", g.get("rang_ninja", "Aspirant"))
        elif saga == "jujutsu":
            st.progress(g.get("energie_occulte", 0) / 100, text=f"👁️ Énergie occulte : {g.get('energie_occulte', 0)}/100")
            st.metric("Exorcismes / combats gagnés", g.get("victoires_combat", 0))
            st.caption("Les fléaux, pactes contraignants et techniques maudites peuvent modifier ta destinée.")
        else:
            st.markdown(f"**Faction :** {g.get('faction_manga', 'Indépendant·e')} · **Notoriété :** {g.get('notoriete_manga', 0)}/100")
            st.progress(g.get("notoriete_manga", 0) / 100, text="Prime / notoriété")
            if g.get("fruit_demon"):
                st.warning(f"🍈 Fruit du démon : **{g['fruit_demon']}** · tu ne peux plus nager.")
            st.metric("Victoires en combat", g.get("victoires_combat", 0))
        c1, c2 = st.columns(2)
        with c1:
            btn("👁️ S'entraîner à l'énergie occulte" if saga == "jujutsu" else "🌊 S'entraîner au chakra", "entrainement_chakra", "manga_chakra")
            btn("⚔️ Combat d'entraînement", "combat_jutsu", "manga_combat", nom=(g.get("jutsu") or ["Boule de feu"])[0], disabled=not bool(g.get("jutsu")))
        with c2:
            jutsu_noms = [n for n, d in JUTSU.items() if n not in g.get("jutsu", []) and (not d.get("saga") or d.get("saga") == g.get("saga_manga", "naruto")) and g.get("energie_occulte" if d.get("saga") == "jujutsu" else "chakra", 0) >= d["min"] and (not d.get("clan") or d.get("clan") == g.get("clan") or (d.get("clan") == "Uchiha" and g.get("sharingans_voles", 0) > 0 and n in ("Sharingan", "Mangekyō Sharingan")))]
            if jutsu_noms:
                choix = st.selectbox("Technique à apprendre", jutsu_noms, key="manga_apprendre")
                btn("📜 Apprendre ce jutsu", "apprendre_jutsu", "manga_apprendre_btn", nom=choix)
            else:
                st.info("Aucun nouveau jutsu accessible. Entraîne ton chakra pour débloquer des techniques.")
        if g.get("jutsu"):
            st.markdown("### 📜 Tes jutsu")
            cols = st.columns(2)
            for i, nom in enumerate(g["jutsu"]):
                with cols[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"**⚡ {nom}**")
                        st.caption(JUTSU[nom]["desc"])
                        btn(f"Utiliser {nom}", "combat_jutsu", f"jutsu_{i}", nom=nom)
        if g.get("saga_manga", "naruto") == "naruto":
            st.markdown("### 🥷 Carrières et rangs")
            st.write("Les carrières de ninja se débloquent selon l'âge, les notes, la force, l'intelligence et les victoires.")
        vic = g.get("victoires_combat", 0)
        if g.get("saga_manga", "naruto") == "naruto" and g.get("metier") in ("ninja", "anbu", "sensei_ninja", "medecin_ninja", "ninja_chercheur", "kage"):
            rang = "Genin"
            if g.get("age", 0) >= 15: rang = "Chūnin"
            if vic >= 5: rang = "Jōnin"
            if g.get("metier") == "anbu" and vic >= 4: rang = "ANBU"
            if g.get("metier") == "sensei_ninja": rang = "Sensei"
            if g.get("metier") == "kage" and vic >= 8 and g["stats"]["karma"] >= 60: rang = "Kage"
            g["rang_ninja"] = rang
            st.success(f"Rang de ninja reconnu : **{rang}**")
        elif g.get("saga_manga", "naruto") == "naruto":
            st.caption("Conseil : commence comme ninja, gagne des combats et développe tes compétences pour viser l'ANBU, le poste de sensei ou le titre de Kage.")
        st.divider()
        saga = g.get("saga_manga", "naruto")
        if saga == "onepiece":
            st.markdown("### 🏴‍☠️ Grand Line — factions et notoriété")
            st.markdown(f"**Faction :** {g.get('faction_manga', 'Indépendant·e')} · **Notoriété :** {g.get('notoriete_manga', 0)}/100")
            st.progress(g.get("notoriete_manga", 0)/100, text="Notoriété / prime")
            if g.get("fruit_demon"):
                st.warning(f"🍈 Fruit du démon : **{g['fruit_demon']}** · tu as perdu la capacité de nager.")
            st.caption("Tes actes peuvent te faire rejoindre les pirates, la Marine ou les révolutionnaires. Une notoriété élevée peut faire de toi un Empereur des mers.")
            if g.get("faction_manga") in ("Pirates", "Empereur des mers"):
                btn("📰 Déclencher une action de notoriété", "notoriete_action", "manga_notoriete")
        elif saga == "jujutsu":
            st.markdown("### 👁️ Jujutsu Kaisen — énergie occulte")
            st.progress(g.get("energie_occulte", 0)/100, text=f"Énergie occulte : {g.get('energie_occulte', 0)}/100")
            if g.get("techniques_maudites"):
                st.markdown("**Techniques maudites connues :** " + " · ".join(g["techniques_maudites"]))
            if g.get("energie_occulte", 0) >= 15:
                btn("🏯 Postuler à l'école d'exorcisme", "postuler", "jjk_apply", cle="exorciste_jujutsu")
            st.caption("Les fléaux, les rivalités entre écoles et les techniques maudites se débloquent à travers les événements.")
        else:
            st.markdown("### 🍃 Villages cachés de Naruto")
            st.caption(f"Village actuel : **{g.get('ville', 'Village de la Feuille')}** · Clan : **{g.get('clan') or 'Inconnu'}** · Statut : **{g.get('statut_ninja', 'Village')}**")
            st.caption("Tu peux voyager vers d'autres villages, nouer des alliances, devenir déserteur, rejoindre l'Akatsuki ou viser le rang de Kage.")
    elif g["univers"] == "real":
        st.markdown("## 🦸 Initiative des Gardiens — Agence de héros")
        if g.get("origine_heroique", "Aucune") != "Aucune" or g.get("metier") in ORIGINES_METIERS:
            st.success(f"Potentiel détecté : **{g.get('origine_heroique', 'Aucune')}** · Agence : **{g.get('agence_heros') or 'Initiative des Gardiens'}**")
            if g.get("metier") not in ORIGINES_METIERS:
                st.caption("Avoir un potentiel ne donne pas automatiquement un poste : il faut encore réussir les tests et postuler.")
                c1, c2 = st.columns(2)
                with c1:
                    btn("📝 Postuler à l'agence", "postuler", "hero_agency_apply", cle="heros_pro")
                with c2:
                    specialized = {"Armure technologique": "justicier_armure", "Arachnide urbain": "tisseur_urbain", "Énergie cosmique": "heros_energie", "Mutation métamorphe": "metamorphe", "Télépathie": "telepathe", "Magie": "gardien_dimension", "Vigilante entraîné": "chasseur_anomalies"}.get(g.get("origine_heroique"))
                    if specialized:
                        btn("🎯 Candidater au programme spécialisé", "postuler", "hero_special_apply", cle=specialized)
            st.progress(min(100, g.get("entrainement_heroique", 0)) / 100, text=f"Maîtrise : {min(100, g.get('entrainement_heroique', 0))}/100")
            if g.get("origine_heroique") == "Armure technologique":
                st.metric("Niveau de l'armure", g.get("armure_niveau", 0))
                btn("🦾 Améliorer l'armure", "ameliorer_armure", "hero_armure_upgrade")
            btn("🏋️ S'entraîner aux pouvoirs", "entrainement_hero", "hero_training")
            st.markdown("### Capacités")
            for pouvoir in g.get("pouvoirs", []):
                st.write(f"⚡ {pouvoir}")
        else:
            st.info("Tu n'as pas encore de pouvoir ou de contact héroïque. Des choix et événements peuvent te faire remarquer par l'Initiative des Gardiens. Tu peux aussi choisir une origine héroïque à la création.")
    else:
        st.markdown("## 🐉 Destinée de fantasy")
        st.markdown(f"**Faction :** {g.get('faction_fantasy', 'Aucune')} · **Renommée :** {g.get('renommee_fantasy', 0)}/100")
        st.progress(g.get("renommee_fantasy", 0) / 100, text="Renommée dans le royaume")
        st.caption("Des choix peuvent te faire rejoindre l'ordre des chevaliers, le cercle des mages ou les corsaires. Tes actes peuvent t'amener jusqu'au titre de Champion·ne du royaume.")
        st.info("Continue ta vie, noue des alliances et réponds aux événements pour découvrir les factions et les quêtes de cet univers.")

def tab_actualites(g):
    st.markdown("## 📻 Radio & actualités")
    st.caption("Les bulletins évoluent selon ton univers. Tes réactions sont conservées dans l'historique.")
    if g.get("actualites_monde"):
        st.markdown("### 🌍 Chronologie des grands événements")
        for item in reversed(g["actualites_monde"][-12:]):
            with st.container(border=True):
                etiquette = "Information" if item.get("type") == "information" else ("Mission" if item.get("type") == "mission" else "Événement mondial")
                st.caption(f"{etiquette} · À {item.get('age', 0)} ans")
                st.markdown(f"**{item['titre']}**")
                st.write(item["texte"])
        if g.get("monnaie_monde"):
            st.caption(f"Devise de référence dans ta partie : **{g['monnaie_monde']}**")
    else:
        st.info("Les grands événements mondiaux apparaîtront ici au fil de ta vie.")
    eligibles = [x for x in ACTUALITES if x["univers"] in ("all", g["univers"])]
    for item in eligibles:
        with st.container(border=True):
            st.markdown(f"### 📰 {item['titre']}")
            st.write(item["texte"])
            c1, c2 = st.columns([3, 1])
            with c1:
                choix = st.selectbox("Ta réaction", [x[0] for x in item["choix"]], key=f"actu_{item['id']}")
            with c2:
                btn("Réagir", "actualite_choix", f"react_{item['id']}", choix=item["id"], reaction=choix)
    if g.get("journal_actualites"):
        st.markdown("### 🗞️ Tes réactions précédentes")
        for item in g["journal_actualites"][-10:]:
            st.write(f"Âge {item['age']} · **{item['titre']}** — {item['choix']}")


def tab_inventaire_marche(g):
    st.markdown("## 🎒 Inventaire & marché")
    st.caption("Les objets trouvés dans les coffres peuvent être utilisés ou revendus. Les objets SS sont extrêmement rares et très chers.")
    st.markdown(f"### 💰 Argent disponible : **{fm(g, g.get('argent', 0))}**")
    sous = st.tabs(["🎒 Mon inventaire", "🛒 Marché"])
    with sous[0]:
        inv = g.setdefault("inventaire_objets", [])
        if not inv:
            st.info("Ton inventaire est vide. Explore ton univers pour trouver des coffres ou achète des objets au marché.")
        for i, item in enumerate(list(inv)):
            with st.container(border=True):
                c1,c2,c3 = st.columns([3,1,1])
                with c1:
                    st.markdown(f"**{item.get('nom','Objet')}**")
                    st.caption(f"Classe {item.get('rarete','C')} · {item.get('type','objet').capitalize()}" + (" · Équipé" if item.get("équipé") else ""))
                obj = objet_def(item.get("id"))
                if obj and obj["type"] in ("parchemin","fruit","relique") and c2.button("Utiliser", key=f"obj_use_{i}"):
                    try: flash(appliquer_objet(g,i))
                    except Refus as e: flash(str(e))
                    if st.session_state.get("autosave"): sauver(g)
                    st.rerun()
                if c3.button("Vendre", key=f"obj_sell_{i}"):
                    try: flash(vendre_objet_marche(g,i))
                    except Refus as e: flash(str(e))
                    if st.session_state.get("autosave"): sauver(g)
                    st.rerun()
    with sous[1]:
        univers = univers_objets(g)
        st.caption("Les objets affichés correspondent à ton univers. Les classes S sont rares ; les objets SS sont des trésors exceptionnels.")
        st.caption(f"Réputation : {g.get('reputation', 50)}/100 · Karma : {g.get('stats', {}).get('karma', 50)}/100. Ces valeurs influencent les prix.")
        if g.get("reputation", 50) < 30 or g.get("prime_recherchee", 0) >= 50000:
            if st.button("🕶️ Débloquer / visiter le marché noir", key="market_black_market"):
                g["marche_noir_debloque"] = True
                flash("Le contact te donne accès à un marché clandestin. Certains objets rares y sont moins chers, mais les risques augmentent.")
                st.rerun()
        if g.get("marche_noir_debloque"):
            st.info("Marché noir accessible : équipement rare disponible à prix réduit, mais les opérations risquées peuvent attirer la police ou la Marine.")
        for obj in OBJETS_MARCHE:
            if obj["univers"] != univers: continue
            with st.container(border=True):
                c1,c2 = st.columns([3,1])
                with c1:
                    st.markdown(f"**{obj['emoji']} {obj['nom']}** · Classe **{obj['rarete']}**")
                    st.write(obj["desc"])
                    prix_actuel = prix_achat_actuel(g, obj)
                    vente_actuelle = prix_vente_actuel(g, obj)
                    st.caption(f"Achat : {fm(g,prix_actuel)} · Revente : {fm(g,vente_actuelle)} · Prix de base : {fm(g,obj['prix'])}")
                if c2.button(f"Acheter · {prix_achat_actuel(g,obj):,}".replace(",", " "), key=f"market_{obj['id']}"):
                    try: flash(acheter_objet_marche(g,obj["id"]))
                    except Refus as e: flash(str(e))
                    if st.session_state.get("autosave"): sauver(g)
                    st.rerun()


def tab_defis_boutique(g):
    st.markdown(f"### 🏅 Défis & récompenses  ·  **🪙 {g.get('jetons', 0)} jetons**")
    st.caption("Les jetons sont une monnaie fictive : termine les défis une seule fois par personnage pour les dépenser ici.")
    st.markdown("#### 🎯 Défis & accomplissements")
    st.caption("Les défis sont de petits objectifs ; les accomplissements récompensent les grandes étapes de ta vie.")
    for d in DEFIS:
        done = d["id"] in g.get("defis_reclames", [])
        ok = d["test"](g)
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"**{'🏆' if done else '✨' if ok else '🔒'} {d['nom']}**")
                st.caption(d["desc"] + f" · Récompense : 🪙 {d['recompense']}")
                if done:
                    st.markdown("<span class='challenge-stamp'>✓ DÉFI ACCOMPLI</span>", unsafe_allow_html=True)
                elif ok:
                    st.markdown("<span class='challenge-stamp challenge-stamp-ready'>PRÊT À RÉCLAMER</span>", unsafe_allow_html=True)
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
    st.markdown("#### 🏡 Famille d’origine")
    if g.get("age", 0) == 0:
        st.info("👶 Tu viens de naître. Voici les personnes qui t'élèvent et les liens dont ton histoire va dépendre.")
    parents = g.get("parents", [])
    if parents:
        cols = st.columns(min(2, len(parents)))
        for i, parent in enumerate(parents):
            with cols[i % len(cols)]:
                icon = "👩" if parent.get("role") == "Mère" else "👨"
                statut = f"{parent.get('age', '?')} ans" if parent.get("vivant", True) else "🕯️ Décédé·e"
                st.markdown(f"**{icon} {parent['nom']}** · {parent.get('role', 'Parent')}")
                st.caption(f"{statut} · {parent.get('personnalite', 'Bienveillant·e')}")
                st.progress(parent.get("relation", 65) / 100, text=f"Lien : {parent.get('relation', 65)}/100")
                if parent.get("vivant", True):
                    b1, b2, b3 = st.columns(3)
                    b1.button("🍽️ Restau", key=f"parent_resto_{i}", on_click=run_action, args=("pnj_parent_resto",), kwargs={"index": i}, use_container_width=True)
                    b2.button("💢 Dispute", key=f"parent_dispute_{i}", on_click=run_action, args=("pnj_parent_dispute",), kwargs={"index": i}, use_container_width=True)
                    b3.button("🕊️ Excuses", key=f"parent_excuses_{i}", on_click=run_action, args=("pnj_parent_excuses",), kwargs={"index": i}, use_container_width=True)
    else:
        st.caption("Cette ancienne sauvegarde ne contient pas les informations sur tes parents.")
    if g.get("fratrie"):
        st.markdown("**🧑‍🤝‍🧑 Frères et sœurs**")
        for i, membre in enumerate(g["fratrie"]):
            st.progress(membre.get("relation", 60) / 100, text=f"{membre['nom']} · {membre.get('age', 0)} ans · lien {membre.get('relation', 60)}/100")
            b1, b2 = st.columns(2)
            b1.button("🎮 Sortie ensemble", key=f"fratrie_sortie_{i}", on_click=run_action, args=("pnj_fratrie_sortie",), kwargs={"index": i}, use_container_width=True)
            b2.button("💢 Se disputer", key=f"fratrie_dispute_{i}", on_click=run_action, args=("pnj_fratrie_dispute",), kwargs={"index": i}, use_container_width=True)
    if g.get("amis"):
        for i, ami in enumerate(g["amis"]):
            statut = ami.get("statut", "ami·e")
            symbole = "⚔️" if statut == "ennemi·e" else "🫂"
            st.progress(ami.get("relation", 50) / 100, text=f"{symbole} {ami['nom']} · {statut} · {ami.get('personnalite', 'Loyal·e')} · {ami.get('relation', 50)}/100")
            b1, b2, b3 = st.columns(3)
            b1.button("🍕 Sortie", key=f"ami_sortie_{i}", on_click=run_action, args=("pnj_ami_sortie",), kwargs={"index": i}, use_container_width=True)
            b2.button("🤫 Secret", key=f"ami_secret_{i}", on_click=run_action, args=("pnj_ami_secret",), kwargs={"index": i}, use_container_width=True)
            b3.button("💢 Dispute", key=f"ami_dispute_{i}", on_click=run_action, args=("pnj_ami_dispute",), kwargs={"index": i}, use_container_width=True)
    else:
        st.info("Tu n'as pas encore d'ami proche.")
    if g.get("partenaire"):
        st.progress(g["partenaire"].get("relation", 50) / 100, text=f"❤️ {g['partenaire']['nom']} · couple {g['partenaire'].get('relation', 50)}/100")
    if g.get("enfants"):
        st.markdown("#### Enfants et héritiers")
        for e in g["enfants"]:
            st.caption(f"🧒 {e['nom']} · {e['age']} ans · lien {e.get('relation', 65)}/100" + (" · relation fragile" if e.get("relation", 65) < 35 else ""))
    if g.get("rivalites"):
        st.markdown("#### ⚔️ Rivalités en cours")
        for rival in g["rivalites"][-8:]:
            st.caption(f"{rival.get('nom','Rival')} · {rival.get('origine','Conflit')} · depuis {rival.get('age',0)} ans")
    if g.get("pouvoirs"):
        st.markdown("#### 🦸 Pouvoirs et aptitudes")
        st.caption(" · ".join(g["pouvoirs"]))
        st.progress(g.get("niveau_pouvoir", 0)/100, text=f"Maîtrise des pouvoirs : {g.get('niveau_pouvoir',0)}/100")
    if g.get("consequences_differees"):
        st.markdown("#### ⏳ Histoires en attente")
        for c in sorted(g["consequences_differees"], key=lambda x: x.get("age_declenchement",999)):
            st.caption(f"À {c.get('age_declenchement')} ans · **{c.get('titre')}** — {c.get('texte')}")
    if g.get("chronologie_famille"):
        st.markdown("#### 📖 Chronologie des liens")
        for c in reversed(g["chronologie_famille"][-10:]):
            st.caption(f"Âge {c.get('age','?')} · **{c.get('titre','Souvenir')}** — {c.get('texte','')}")


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
    st.markdown("### 🏆 Titres & collection")
    if g.get("titres"):
        st.write(" · ".join(g["titres"]))
    else:
        st.caption("Aucun titre pour le moment. Accomplis des missions, explore des coffres ou bâtis ta réputation.")
    st.caption(f"Coffres ouverts : {g.get('coffres_ouverts', 0)} · Objets rares acquis : {len(g.get('objets_uniques', []))} · Prime/recherche : {fm(g, g.get('prime_recherchee', 0))}")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Famille d'origine :** {g['famille']}")
        if g.get("parents"):
            st.markdown("**Parents :** " + " et ".join(f"{p['nom']} ({p.get('role','Parent')})" for p in g["parents"]))
        if g.get("fratrie"):
            st.markdown("**Fratrie :** " + ", ".join(f"{p['nom']} ({p.get('age',0)} ans)" for p in g["fratrie"]))
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
        st.markdown(f"**🧬 Origine héroïque innée :** {g.get('origine_heroique', 'Aucune')}")
        if g.get("pouvoirs"):
            st.markdown("**🦸 Pouvoirs :** " + " · ".join(g["pouvoirs"]))
        if g.get("consequences_differees"):
            st.markdown(f"**⏳ Histoires à venir :** {len(g['consequences_differees'])}")
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


def afficher_effet_action(message):
    msg = str(message or "")
    low = msg.lower()
    if any(x in low for x in ("coup de feu", "fusil", "balle", "tir ", "arme à feu", "braquage", "menottes", "explosion")):
        classe, emoji = "gun", "💥"
    elif any(x in low for x in ("combat", "jutsu", "chakra", "victoire", "attaque", "duel", "blessé", "sharingan", "bijū", "biju")):
        classe, emoji = "combat", "⚔️"
    elif any(x in low for x in ("argent", "€", "prime", "salaire", "paie", "payé", "gain", "jackpot", "héritage", "million")):
        classe, emoji = "money", "💸"
    elif any(x in low for x in ("amour", "ami", "famille", "mariage", "cœur", "coeur", "relation")):
        classe, emoji = "love", "💗"
    elif any(x in low for x in ("pouvoir", "magie", "sort", "invocation", "bijū", "biju", "sceau")):
        classe, emoji = "magic", "✨"
    else:
        classe, emoji = "general", "✨"
    st.markdown(f'<div class="action-effect {classe}"><span class="effect-icon">{emoji}</span><span>{html.escape(msg)}</span></div>', unsafe_allow_html=True)


def ecran_jeu(g):
    sidebar(g)
    gauche, droite = st.columns([1, 2.4])
    with gauche:
        panneau_perso(g)
    with droite:
        msg = st.session_state.get("flash")
        if msg:
            afficher_effet_action(msg)
        if not g["vivant"]:
            bloc_mort(g)
        else:
            if g["evt"]:
                bloc_evenement(g)
            c1, c2 = st.columns([2, 1])
            c1.button("➡️ ANNÉE SUIVANTE", on_click=next_year, type="primary", use_container_width=True, disabled=bool(g["evt"]))
            c2.metric("⏳ Temps libre", f"{g['actions']}/{ACTIONS_PAR_AN}")
        afficher_actualites_accueil(g)
        st.markdown(f"<div style='padding:9px 12px;border-radius:12px;background:linear-gradient(90deg,#92400e33,#ca8a0433);border:1px solid #f59e0b55;margin:.4rem 0 1rem'>🪙 <b>{g.get('jetons', 0)} jetons</b> · Termine les défis de vie pour gagner de la monnaie fictive, puis dépense-la dans la mini-boutique.</div>", unsafe_allow_html=True)
        defis_disponibles = sum(1 for d in DEFIS if d["id"] not in g.get("defis_reclames", []) and d["test"](g))
        label_defis = f"🏅 Défis & boutique  +{defis_disponibles}" if defis_disponibles else "🏅 Défis & boutique"
        tabs = st.tabs(["🎯 Actions", "🍥 Manga / 🦸 Héros", "🎒 Inventaire & marché", "📻 Actualités", label_defis, "👥 Relations", "📜 Journal", "🪪 Profil"])
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
            tab_univers_specifique(g)
        with tabs[2]:
            tab_inventaire_marche(g)
        with tabs[3]:
            tab_actualites(g)
        with tabs[4]:
            tab_defis_boutique(g)
        with tabs[5]:
            tab_relations(g)
        with tabs[6]:
            tab_journal(g)
        with tabs[7]:
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
