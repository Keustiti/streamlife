# -*- coding: utf-8 -*-
"""
🧬 MA VIE — Multivers anime façon BitLife (Streamlit)

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
COUPES = ["Court", "Long", "Afro", "Crête", "Queue de cheval", "Pointes (manga)", "Carré", "Chauve", "Frange", "Deux chignons", "Tresses", "Dreadlocks"]
YEUX = ["Ronds", "Souriants", "Manga", "Lunettes", "Fatigués"]
BOUCHES = ["Sourire", "Neutre", "Grand sourire", "Moue"]
ACCESSOIRES = ["Aucun", "Lunettes rondes", "Lunettes noires", "Boucles d’oreilles", "Bandeau ninja", "Couronne", "Masque", "Cicatrice"]
TENUES = ["Classique", "Sport", "Élégante", "Ninja", "Pirate", "Mage", "Héroïque"]
COULEURS_YEUX = ["Marron", "Bleu", "Vert", "Gris", "Violet", "Rouge", "Doré"]
COULEURS_YEUX_HEX = {"Marron":"#6b4226", "Bleu":"#38bdf8", "Vert":"#22c55e", "Gris":"#94a3b8", "Violet":"#a78bfa", "Rouge":"#ef4444", "Doré":"#facc15"}


def accessoire_svg(av):
    acc = av.get("accessoire", "Aucun")
    dessins = {
        "Lunettes rondes": '<circle cx="78" cy="104" r="13" fill="none" stroke="#111827" stroke-width="3"/><circle cx="122" cy="104" r="13" fill="none" stroke="#111827" stroke-width="3"/><path d="M91 104 L109 104" stroke="#111827" stroke-width="3"/>',
        "Lunettes noires": '<rect x="63" y="94" width="30" height="20" rx="6" fill="#111827"/><rect x="107" y="94" width="30" height="20" rx="6" fill="#111827"/><path d="M93 102 L107 102" stroke="#111827" stroke-width="3"/>',
        "Bandeau ninja": '<path d="M65 96 Q100 80 135 96" fill="none" stroke="#111827" stroke-width="5"/><path d="M65 91 L135 91" stroke="#ef4444" stroke-width="8"/>',
        "Cicatrice": '<path d="M68 120 L86 132" stroke="#991b1b" stroke-width="3"/><path d="M70 118 L88 130" stroke="#fecaca" stroke-width="1"/>',
        "Couronne": '<path d="M58 74 L65 52 L80 65 L100 42 L120 65 L135 52 L142 74Z" fill="#facc15" stroke="#fef3c7" stroke-width="2"/>',
        "Masque": '<path d="M44 104 Q100 140 156 104 L150 132 Q100 155 50 132Z" fill="#334155" stroke="#94a3b8" stroke-width="2"/>',
        "Boucles d’oreilles": '<circle cx="43" cy="125" r="4" fill="#facc15"/><circle cx="157" cy="125" r="4" fill="#facc15"/>'
    }
    return dessins.get(acc, "")



# Portraits anime illustrés embarqués : aucun fichier externe requis.
PORTRAITS_ANIME = {
    0: ('Nocturne', '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'),
    1: ('Raven', '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'),
    2: ('Aurore', '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'),
    3: ('Minuit', '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'),
    4: ('Flamme', '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'),
    5: ('Ombre', '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'),
    6: ('Cendre', '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'),
    7: ('Tresse', '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'),
    8: ('Argent', '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'),
    9: ('Rebelle', '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'),
    10: ('Éclipse', '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'),
    11: ('Sable', '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAcFBQYFBAcGBgYIBwcICxILCwoKCxYPEA0SGhYbGhkWGRgcICgiHB4mHhgZIzAkJiorLS4tGyIyNTEsNSgsLSz/2wBDAQcICAsJCxULCxUsHRkdLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCz/wAARCAFoAWgDASIAAhEBAxEB/8QAHAAAAQUBAQEAAAAAAAAAAAAAAAEDBAUGAgcI/8QARRAAAgEDAgQEAwYDBgMIAgMAAQIDAAQRBSESMUFRBhNhcSIygRQjQlKRobHB0QcVJDNickOC4RYlNFNjsvDxRJJkc8L/xAAaAQACAwEBAAAAAAAAAAAAAAAAAQIDBAUG/8QAKxEAAgICAgIBAwMFAQEAAAAAAAECEQMhEjEEQVETImFCcfAjMoGR8VKx/9oADAMBAAIRAxEAPwDwXNITRRXRMoUUUUAFFFFAC0UlLQAUUUUwClpKWgQUEZFFdhcbscfxpOvY0iRp9qJJDLKxWGP5sc2PRR61ZSPrGoW6RxQuLZdljhwF/wCtVTSSSCOGMNgbKi7kk8/rVrZ6Fc26+fd3ZslG4RG4pD9ByrHl+375P9jZi39kU69sj/3TqR2/u+4//SuG024i4xLYcRXnxHGP0q+GoXGQkbyeUv8A5rcTN70491JMMO+R2Gwqh+TkemkaF42NbTZnxpSvws0LRd0U5/epCWNovKFc/wCvnVow2zypwaZcyIHeMRxnk0p4QfpVTyy9ssWKK6RVvYRyLlYfiHIqcEexohTY+YuXG3EBji9x3q1isLSMnMskrdohgfrT0GqRaTfZjtndGHDLFcLlZB6HofWoc36LOC7ZUmPPyE5/Kef0pLSUWkzM+JIJPhlQjZh6juKvtafRXVLiyD5lXiCpsFPVWHQ+1U1xZvNELi3HGSN1H4h29xRGdrYnCnaCfw1F5zyW98kcfDxxRuCWY/lB7etWsmiXU/gySzuocXFuTNbgHJIzjA9Dn9qq7WbzbeFgSWhzGfbp/HFW9vrjIHj87JWER8R/Dk5Y/wAAPeiU8mt9Dhjxq9dkPTfAN3dgNPIsFsvzOvxMx649u9c3+t6D4edrTR7FLq4T4XmfcA+/Mn2qcNaueHhjLcB5Kx+EfSnra/LTATrAqnm/lDah5Jydz2vjoFihFVj0/nsyEvi3VLhiDLCqn8AjGP3phtRab/xEEEgPUJwH9RXqFjbaVqUYjuLFJnJILeThMd81D1H+z/R7klrZpLNj0Q5X9DV2PysMXUo0VZPEzSVxnZ5k6hwzQ5KruVPzL/UetRzvW0n/ALPdRtp1exvIZsH8XwEf1qFN/Z/4gVXkS0R1z8qOM/StcfKxv9Rjl4uVfpMtiip97o+oaacXlnNB6su360wLYtZPc8ajgkVOHqc9far1NNWjPxadNDFFFLVhASilooASk3rqkpAFFFGKADaiiigAoozRQAlFJS0AFFFFABRRRQAUUYpVTjdVDBeI4yeVDdbBKworp0aORkdSrKcEHpSChOwarsKWlC0/ZWNzqN0tvaQtNI22F5D3PSm2krY0m3SGVxzG5/hUiGwuZkEixMUYgBjtnfp3rRjw3a6QqG+dbu6IyIkP3a+561zcTeeTxHLAgDGwVR0A6ViyeQuoG3H4z7mRLay+wyv5cwc5x5ijBI7A9KkqgI22B396b4sHfb0FJ95K3CBt2H86xNtu2a0lFUjtpI0OAcnsKI3kmH3Ke7NyFdpAuCOnU96mxqIQpwOWQOgqDZNIctLcKnFIA5/O/L6CrQXVjKgjnt3uJAMcfH8v9KpJXaQksSaS6E0dkbWN44FbeaZzj/kH86g42WqVIm6jf2loQlkwklG5J+VaoL3xJr8WSWtpYe3lAgV0msHT9re5tbzh2KND/OmbvU1u2MhsFjU8/L5VOMa9FUp306JujajZ64GsLmJLK/Y5iZTiOY/l9D2pDPPpd0Y3VvIJ3PVWqjGlXVwxksbW4ljByCiHKH0NXzXE97aCS7iZLjHlzqy4PF0OPUU2knojFtrfZ1PeNcXqSSKgDkISi4yehPc1HCQpd3DZ+ANge/X96gGUwrLEz4MY40PUgHb96m6bDhhkcbgZy3yp6n1p1SC+TJfneWozC2D1J3p/iXAKvxE/hApHMELFpJVLn8THB/TpXaSuMNG8eDyyMg1AsRZact/HIHhDnrjPw/WtJHe8VuHnCwuPmBYECsnJdvJAFaNVcfiRiMj2qIrvG/GjFWqlw5Fynx6Nn/edrn4Z0dh0BzVX4h8QeIdGtxNHZQGzb/jRkvw/7u1QY9TXy+PyLaUr88TLwn3Uj+FT7PX1kkMJMNqjDASUFlPpmlFcXbVkpS5qlKjJT/2iaxPJ979nliPOJo8qagOmna27C2Uadet8Sws33Up7A/hNXXiXwb5hN3ptv5Uj7mBd439Ub+VZm58P6pbcRmtGURIGfcbDvXUxPDJXj+1nKyrNF1kXJfz/AEQZYpIJmilQxyIcMrDBBrmp6zrfxpDePiRRiO4PMdlfuPXpUSeCS2maGVCjocEVuhK9PswyiluPQ3S0YoqwgFJS0UgCkpcUlIAooooAKKKKAOaWkpaAAUtFFABSUtFMAoxRSigCdBdQSxrDfIXVRhZV+ZR2PcVPj0G3mQPFelkPI8INUVS7Rprb75ZjCh+vH7Cs2SDirg6NOOalqas0cemaTa8LfZnuGG/3j7Z9qkzanO8bRwiO3jbYrCoXNUttq5u3EJs5HYblkfGF7noK4Se4kY4ZY1ztjc496wTjK/vN8Zxr7OiwclUy749WNMqyyBfL4nY9AMAfWmlRQw5ySn8xzU1oxbxcAPEzj4iOeOwqBJbGIwzOV8tMMMLjp61MjjESBVH1rmGPgGSPiPP09KeXHM7gc6jZNI5AA2FcvKqZyfU+lJLL5abc/wCFVzyCW5FuRxud/L7erf0oSE3RL/vmGytZLpkLEHhhB/G3f2qjKXepyGa6lJ4jy/kBUq9jNzqAUDiSD4FA6seZqxtLcRMA274z7Cp6irK2nJ0+iPa6GioC+w58P9auNN0dJZiqRlUTd2H7AeppOIgVe217b6TZiF1LTH4mA7mqpydaL4RimQtaje2SGIXTQEL8MMR4Qg/mfWqOTX7i2uGhvYhdQTR+X5hHxc8g57ir6+8qSZppAGklwURj8uRtn+lRNQ0llVkk8uRcZcIRxIehI6VGLS7JzTfRQ3rx3L+TJGvEceXInr/I10ZJypt7BMhdmlJ2z6GrS9tItQiN0qCCWLhaQLyPRiB03Gf+aootYrnCZKcPJVOAPpVqaoocXZWvot0wLSHiJ6hs0tujaYpD3BVTuUYZH6VdxWv2UMoldwfw42FBjbOcb+1HK9BwS2hdJuba7PGcyRpvIiHDgU9ILSWUlUmjjPL4gxFRZEhA80RGK4UfDJEN/wD6p+3uBc2pby1FxH/mINgw/MKr/JauqZInTit0HEroOThQCfc03BFG0gikwFY4BI2Bpn7S8eWiIweYIyD796lC2+1Wv2m2bzEG0sf4oj/NexpPRJbLvR5WsZTZtxKp+a3fcf7k7j0p/UoZ/LeVLWHVbLG8Eg+8jPXhPUehpzSCmoaei3ChpITw8XUdiDVi0csR82ICRxsy8vMHb37VmcqZqUbieW3t/wCGbmZkbRbmxkGxaKTOP+U1V6raXEccExPnWgTginXcEdj2Poa3fiHwha61P9stJBC0owHIwEfsw7Hl6GsKrajoF7NaTxmJx8M0Egykg9R1HYiux42RT3Dtemcbycbg6mtP2irxRU+9tITCLyzz5BOHjY5aFux7g9DUHFdGMlJWc6UXF0xKSlxRUiIlFLSUgEopaKQCUUUUwEpaSloAKKKWgApKWigBKWiuowBh2GVB5fmPak3Q0rHY0WNBJIAc/Ivf1PpXdrb3Wq6jFaWyebPKcDJ2A6k9gBTEkjSOXbcnt/AVqrC1Oi6Z5eMahfL94escfRPTPM1RkyfSVvtl+LH9WVLpDV3BbabZmzs383cLJNj/ADW64/0jpURRuFjHEe/QU5I/mzBE3C7L69zUkBLZUBI+JgCa5rb7fZ0eK6XRxYxgSSFuSncnvUmNTI7SkNgn4cjp3rq3h4YVVkwOZz+I551LOyZzjO1Vt7LIoiuCOQzjme1cu5ChVGSP41MeM+Wy7KrYLlth6Cq+9u4baBuI5UbbbZ9MULYPRX3t8bVCqENKebc8H09ae0a28mye6cZllyRnn6frVbDby30ct3IvCG+GJew6mr2ZTFZCGPZjwovpVktKkVx2+TGrG2CcTv8AEUzlu55nH8KlxoQCzD4m3NKVVIDEgwNlHtmnarbLUjgOI3V8A8LA4710XZ2Lv8TE5Oe9csuSNutG+wAyTSGSIbkQSG6uBxrboZTnqQNqx8F3cHUn1Dzz57OXc9cnofStJrJFro9wHYAuUQ/U5NZfCsVdW35BsYqeNdsryvaRpbi+NzYNPAoUSgxTL+Q7HP1xUOxgkW4VpWJIHHjPLt9aiabNIk8lu+ySqUYHoeYNPakxKCGNiC+GbHPHQU6rQr5fcXQkdjmN8EeuQfenVkEi8uFhsw7VkbVptOvBIjFvzoN8j+ta+GEzxeemeEKCWHY96hJcScJchMhTnH6c6YeULMPwSAcSkcmHcelSri3ltziRCudweh9qQWYurXy3PBxsTFJ+Rx/I9aiqJuzgm1lVSYWZmHxMr8JDdRXdmr2U63VtcCIjY+cMAjsehFVafaYvtCywFZItmXOxYciPcU9Zai8cYeCTKtvg/Ep9MGm4/ARkr2bSzu4YLlvMh+ytIBxAHijz0INXatkA5yDWBj1f7WyRzE2siDEU8I2X0ZeRU1I0jxe0DGC8tW4RkmW3BKjHMleYrNLFLs0xyxWma6SBkmM8IBLfOnR/+tZPxzo9zeaWLq0hF0sJ4sY+9hXqB+ZfQ8q1VpqdpeRq8FwkgO4wcH9Kllo1+JnVSe5xUceSWKSkvROeOOWDi+meD2V79nlLMvHEw4JE/MvUe9F7a/ZLkxhuONgHjf8AMh5GvVdf8A6dq7Nc25+xXTblkHwt7r/SsFrfh3V9JsljvLfzIbdiI5o/iUq3Md+f8a7mHyoZJJrTOFm8WeJNPa9Mz1FHXmK6jR5pBHErSOeSqMmt9owUc0UrKyOytjKnGxzSUrtWDVaEopaSgAooooA5pRQOVLQAlL0oooAKWkpaYhUQu4XOM9e1dyspbCj4FGF9qWNjHE7BfmHAG7d66tbWa9uVgt0LyNyHb1PYVHVuT9E6dKK9ljoFtE8z3MyFxCyhF/M55D3q4uFZvNlduKZ+bdM9h6CuooItLs1s4WEkwJaSXHInnj+FNSPsoGw7Vycs+crOtih9OCiyPbwiIbbnqx612F82QO24Hyj+dLxM6FQBw9/5Vz5rR7MNzy4N81UWaHshA4SQo64wByPpXUl/5KoZHHGo2+Hc+uKiQTSXUjrERGi/NJ8x+lR5iLa4HD8b5zlznHqaKBypWiwaWSSJprqQqiDi4c8h/U1COly3lwks+VVhng7DoPfvUvT4HvmWR0Y26tx8TD/Mfv7DpVu6hXlyDxjEaj/UeZpXx6BR5K2VkiFLdeEAICBgduVSGRXvFTqrY/auNQKqgQHCoMk+3Km9LRwkTMSzKfiz3NHqx+6JBRmQOBsrAe9dxK0hwoLH0qZI0Ato0jXHl3JDHPzZG1Oz3UFvERkBj+FahZNIYKRQ7SMBwxE+7EgCpVtZpBD58xBY4x2GeVUCXDX12Zzsg4gg9Bt/E1YG6drQQk7KQQe3Wk0xqSZV+KgJEjiOQr3BJx6L/wBap44vIjIX44zzR9x9OxrQatC159lVI2kZnc4XnuAc0i+HbiTnwqcbEnn6H+tWRkkqZW8blK0UacMiB91ZRj1HpTkUnmRCaY4d+g5n2rUW3gq6kVi2FPCSDy36A1Lj8DTC3CmSPIXcZ3Y9s9AKHliCwzMU44kOWKf7Ty+taPwdeZWawMmSFwC2/wADbH9DXF54Znt+JJWTi/CuCFH9ar7C0vNI121uniHkl/LdozkYbbcdN8UNqcaBRlCSdG4nvLaOBVYccSkxMGGSCu2ag3F3CFEKgMpw8TLyBHSomoqU1GYZ2YhsetRCxUheh3HoapUUXOT6Jmr+RPDHLHlH4eLK8wORHrWTBbTLxoyv3b7jHI+oq8dyHBJyOWPeokdulxL9knCshPwcW2D0GegNWx0iue3omz2JS0t7yP44Z0DBh+E9QauPD9sgk8/hUpcqU9mHMH3pjwxNZwWr6e0kjFpWHkT4zH3HqKmXVpJovFNbhjbs6yBefAwPI+hFUyfcS+C6kPR6GlncSeWEa2l3Ecg+R/Q8wDTyvJawLIYwqDsol4P51ZNIkqZHysOVR4DwXhgJOXUyKfTkfrVHJvsvpLohjxKVkCebbygjKsDgH9+dSf79Jjy8UJTqS21NajoVrcM03krl1KycIwcfmH+ofvWMvn0xZW0vXbWW1mQfBfWfyyL0YpyPrirseOM3opyZHjVsudX1/wAKlzJPZ2s83RYowxP1FY3UvEDXKvDY2sWnWzbFYVAZx6tzpnUNElsYzNFPFe2LH7u5h+XPZhzU+hqtrseP4+NbTv8AnwcbP5GR6ar+fImBRQaWtxhEpDS0UAJRRRSAQUtApRTAMUnTlmuqOtAhOtLjPUU/FdPEApRJUH4JFyKs7bWbSIAmxSJu6KDVMpzj+my6EIS/VRGstJur2Ffh8qIMSZH2/Qda0NstvpNo0VqPjfZpG5t/87VBXWornj4eP4V4iWGABUP+8Yp5VXzOOR9lVR+wrn5JznprR0ccccNp7LATKOLB4m/nTfmCVzxMABsFB51X+fLPxBIzGFJXL/yFPRxscR8ZG2/CMfvVVFnKyRPN5a4HP8q86gus08oiIC5HEwBzgep61br9mj0yReH40fjUAc9sbmo8K+THxt/mOeJv6fShMTVj6eXZWOwwFHLuai21i16zTS54Sdh3PekcveSovF9387Dt2H6VbwYUIoGBnlUW6JJciYG+zwCJG4Y0GMD0qNc3pcCaUjjzls9duf6Yrq5lXhCnruazuqyTXMohjB4ZBz7jP9ajFWSlKh2GdtSKux+6MwUD83c1oFnihBj4QOOUHIqnjgWzS2jQbRnJ9T1NLczljCyjHHIpFNqxRfFbLGV/v3iQYDASD3FQbtpCipH88p4VPbufoKkmUNFFcAfIcMPTkabghZrmeaX8LFIx2HMn61FE38HUMYh4EQYVEKinwM0gX4h6iuvxAUAkLbZ8+A9mI/Y1q9HtxLOZHGQg296yFvKu75z5Um+OmG3/AGNbvR0C2hbqzVVkL8RYUUClrOXkW7tEu4SjgZ6HtWXu7MjzIXGDy/oa2OKrdYtg0InUfEmx9qnGVEWrMbcSt9w53LfCxrlhmuNWjkhsLnyhl0bzEH1ri0ulu7ZZVBB5Mp5qeoNaV1ZkfdMWTHxDO4GRUOZZUbzIyJFYZIPMe1S5dpEJ+Vjw+2a5iQ/ZVJ6EoRUuhd6Ilxc2kxW9u5JY5do5Ci5Gfwv9eVXVnrUv2XgS6luoiMZjIcgex3qoFoJWeMoWRlIYDnwnr9NjVSkDwzNE+VmhYqWXY7daOKkLm4m90e9W3igSR28p8x8bgg8eeo6Zq9mZI1WcMCYGyfY7EViNH1C7jjZrm+l8pXVB8IYgnrvzFXlveXEnELiFLjqkqH4SPas84bNWOdxNO8g7+1ZHxto51LTFltYwbm2JkVRzZPxAfxxV6GEtsvmDjGBnhPX0NO/ZDNGC0jBgcqwG47H3qEJPHJSXonOCyRcX7PGLDUZrGYyQnKuMSRtusi9iKLy1NuY3GDFOnmxkHI4c8vcHatN4u8MGyle+gVUDHikjGwz+Zf5jpWemuQ+kW9qy/HDK7q3+lhy/XevQYskclZIf5PPZMcsTeOf+CFRRRWsyCUUtJSGJiilooAOlLRRQAUYpaKYgpUVpHVEXiZjgDuaSnIZDAGkX5/lU9u5qMm0tDirexy6dYh9lhbiRD8bD/iN1+g5CpGj254p71h8Fqux/1tsKgxRPLIscaF2bYKBkmtZ9ibTtDhssAPK3m3DkZA9PfoKyZ5LHDgu2a/Hi8k+b6RU20RPPPCvM96kQjidyq78WBThxjCjAHIV3GOA788Zrn2b6G5ZUjXyi23EAf4k1xGrzkyYwOSA1wJPtFyIvLRoweIsRmpsLcS5EaKM7bc6HoFscggWNcD9e9czTiJ9n4SBz54z/ADrvzjEucqPpVU0z318kwYuiNgjoMDY4qKVkm66Hpp3mfyEfhyeEkbnep0FrGs3GF2RQielQrOAIY2I+IlmPvVogwozTb+AivbGbpdiR0Wo8UXmwW79FYVNkw3mj/QP41D0uZZ7G4AH+RMVHtzpLobWyQECs8fSQcWPXrRDKWiVCN88J+lOyLusg/Cc+460iRDz+LJ71EkPEYdT9KMfEp96VxgA9jTZLLeRoflZGP6YpDsh2jcOq3VuVwkh4g3diPiH8K9F0Ml9GtmYfEV+L3rGRWx8l5Co4jKzp9MD98GtL4Uulls5oc7q5dQex/wCoNV5Notx6Zf0tJmiqC8DTU0fmxMh/ECKdoA3oAw+rIFmgjxgyBVPr8WKi6jZvY6lJK6cHEQsoHI9nq71K0E/iCw/0sowPcnNW2s6cL20LhMuoOR+Zeoq5TqirjdmHvI/8K57DIpYwrWUjKP8AM4ZAfXrQfu2azkOSB8BP4l/qKTTQWtkjb8PEv6GrfRTWzm0YpqELKfxAH2POpOq6XBxxzTMY3LmAyr0I3UkdQRtXOn25bVIkPJX3+lWVwyatprQqMPMjcPpIhyP1FRb3aGladmTuhLZStBMOHrtyPYg1d6NqKlQtuA7qPvbbPxH/AFJ61VWl7b3sIsr4fAdo3Y4KHtnpRqmieVfiZS8bPhkdDgggftVjSf2yIRbj90TUXMDArdQOTBJ1GRwN2I6VbWGqJwiK4YI/IMdgay2k6pqFqsq3F8ZSFzGXjB4sc1bvVnNqFvdWqTT6a0PEM+ZF8SH+YrPKL6ZpjNPZpbiGG7t2hniWWJxurDINYvWP7PUmlabTZxCCP8mQZH0NT7TV7W0AaDiZTyBmyv6GuZ/GUMIPHJAh/LxZP6VLE8uOX9MjlWLJH+oYmfwjrsMhQ6e8mPxRkMDUO70e9sIGku4fs5zhUcjiY+1X+p+O7uYNHZtwA/jxj9BWVklkmlaSV2kdubMck12sLzzV5KRw86wQdY7f/wAOOm9GKDRWwyiYopaKQCUopKXNAhaKTIG5OBXVMBKQbk574pTt6VOsdInvPvJCLa3zvI43P+0dahOcYK5MlCEpuook6Jam6E0cEginBBaQ7COPqc+tW+o3b3Up4G+6Q8ztxHv/AEpAIYLUWtrH5UA3OfmkPdj1poqGwvQbmuRknzk5HXxwcIKJzCh+Zhv0HampJCxZQfmJGewHM0+0gRgoGWPSmRD5mVT4Yyd26n2qsmcWqccRKLjzG59lFTjwwxjPsB3qPLeW9qFhUgvjAUVXrdS3g4kz8bcHEegHanTYWo6Ory483ijRicnhZv4gU/YRCIqccPEWz+lNx2o8ouu44gAe++5qZOvkRA+jD9qH8CS9slpGFW323IOafOFAplW4o42H4VBpxySwA7ZqstGbmRY0mbO4i4qh6RZtZQsruS1yvmsD+Enp+lP3ERmuRCOcqY+gO9WEtuR5coU4DhB7HpTutAlbsi2cpuIMdVJRvcU/HH5bDi9s/wADVfpge31m9tpeUjeYnv1FXQAdcdRSegjtCGPKkU1IPvLaTGdyp+o/6U6jFW4W6Ul65ispmQcTpiRR7HeookX2kWMd5pEivsx2Vuxwd/3qBpObPW5AGIdVYmMdRn4v4Aj696vNFiKaPF3YFjVbHbM99c6hCuXEoCf6iBuPrkj6iqU+zQ10zTqQwBByDvSnaqW616x0lSjSeZlBJHGu7YPQ9sGs1qPi++u1YREWsf8ApO/60RxuQSyRibe5v7WyTiubiOIdid/0qjvfGVuiEWcTTP3b4VFYqFbjULgtFHJM7bF2O36mtLpvhbA+0am5MSjiMSbA+hPOrOEI9sqU5z/tRRXGr6pq96SI2Egk4ES3zkLjvVvY6T4mQrJHJLb/AO+bP7VeaFpi2589ESON1PCq89zV6E2pSyVpIccV7kzz3VNO1yKXzbi0imHFxLJCQCD129ajaTcpJNIrK0TJMBwuMYyOVejTwiW3eNuTDFef3Akj1rJ+SbCN/vXcH9KcZclTCUeLtFnboLa7nnK5x8K+hIqlN5c2NrJPbkcStxcJ5HvVveXAik8rAHEDLgc8kYH7VC8gNpl0xGTHGJMd8c/2px/JGXwinu/sFzqAuGbyIrxeNhj5W6kfzFaHStKuJIDCLlL+yYfCyHLxHoe+Kyc0H+Ge2B4jH9/Aw/Eh5gfT+FP2upSW7RywM6ScPzqeH/5tVkotrTKoyUXbRoWtvs8wYr99C2XjPUdcVdaQ8a28kCkMitxoe6tVRb6tPe6VLeXFwoeA4BkjDFuwzzp6xtbiFYr7ykQvnGWPAA3Q9qoknVM0Rau0UHjGOXSpQLQCO3unZ3AH4scv6VSFjrECg8P2+FdsDHnoOn+4fvXo/iCzt7rQ5vtaF0ReJvLHxD1X1Fec3Gmy2HBeW1xHcW6sGSZDgg9AV5g1v8WSlGupI5/lRlCd9xfoqqWpOocLXjSoAqTDzQB0zzH6/wAaj114vkkzkyXF0JS0UUxCGiiikM5roUg5V0KBBjNO25gQ4mh8xT1U4YU1S5pSipLY4ycXaL+1/u5cNbRxNJ0492H0NPszu/E5JPrWa4t8jIPenor25iJ4ZiQejb1hn4sntO/3N0PKitNV+xfs4RCT0puN2CEciTlientVU1/cJGkkjqWO6pjbHc09CJ7uJZJTiPhyQvL61lljcVbNKyKTpEp7lI24I4/Mc+v8aiyXNzNlePy1BwQu1OoscDszYTbAFR7sO8TPGCDnhUDqTSVDldECMHikuTuCeCP19au4bbyol6YXAHqeZqMtlwCFCciMcv51bBB5eSc4AX+tEmEInaxgRBANhiub4AiDPIyDP6U+NmFQ9QciCIDn5v8AKq1tlr6HrJ8wFTzXYeo6V3FNxXEi5/y8LRCoSWDcDjXyz7jcVFjv7RZG2bzPMJdiMAjOBS7H0T4IvO1VXGS0acCjuWrbT6Ur6EYI1+8RQwP+ob1hdP1qKw1WVjbNN5J/NjLd/ar0/wBoBjQhdPGfWSoTjJvRZCcUtlUtqbm5lA2kdRIjdQwOK7ilIbLjhY7MvYjnUOPxD/jJb026fAx4og2AFbqPrTj6tDf3gCwmCSQYI4sgsOVOmR5R9MnsOMdiORqLLKUlww2xgj0NSIGDxqwOQa6kgWVcHn0NKyTRptFnK+FomfeSOMo3qRkVImVdM8OrnHm42/3mqHw350dzcWs0oeNsMgzvsO3bG3/LWlvJhFGvHDxtn4DjIU96plpl8HaPPm0fUJpppSrRqSWy43bJ3wO/Wp1j4aEsqlgJ4+auT8JHfFXly0kjZweLO2eZqIhZLeQmR4LNCXdk+aQ9QvYVPk2iKhGLLaEafpqhV+9mHRVzj2A5Uxq9/MdOfgg8vjKpmVguxNYrUv7QLoK8Hh618iFR8crJlvestcR6lqo+16jqErICCzNkhRnc49KnDC3tlOTyEtR2eo3HiXTdLJgm1iCLy/h8uIcRFVs/9ounrtBe3jtnGfKGB671iYPDtlLPM1tcS3tur8KTKhTjHfB3Fanwx4CTWNFllmtlZop2jVjJwkgd6n9KHtkPrZGrrRbr44tiojW/trmTuVKVCnnguHjnWWPhNwGHxjcYwcVm/EfhODTr2KyhDx3DnLcT8Sovf3q6sPB1pp1naXBVpp2fIZ+wGTgdKi4wh0yyMsk+1oJZ/P1SQ5yTj6VPtpBFIEf5JQ0bfXb+dVECMmulCMh4+KpjDjnCcXdf1qLXoE+2ZaK7aCT7DP8ACbeRljfrGf6UWcRlSRYmzNFkyQ9QPzL3Hp0qNq8U13rEElohke/AAVerg8LD9q3GmeCNMtLQXWsatNb32eFZFYKin/T+arpzjFW/ZnhCU20vRQW02YvKJ+AsCRWx0/xBZycVhNiNl+EF/lcVmNRsXstUexuQnn8Ikjkj+SdDyYf0qTeWEcmnLfxOonhQebCebqOo9RVc0pUXY242bKGIQAIW4oW+UtuB6Z7V5r4s0FtG1dmjQ/ZJjxxN0HdfpVxb6rJZhQlyVVlDKCdiD6Gro+INOm0gjU/LlTPC3wZUds9jTwyngnySseeMM8OLdM8ykfKxpjeMEH6nNcDlV1qUfh3zWezubs5OeALkfqapm4S+VBAHLJ5128U+a0mjh5cfF7af7CGiiirikSilNFAzkV0K5FdUCCiilpiCukHxZK8QG7DOMiua7yBEoHzEkn6cqjLqvkcfkSVmkdpG3PP2HatSlmtlosFqvxSXGHZuw5k/yqg02GK4vFjncLHgk929B6mtIzyMmHGDyA/Ko5LXP8uSTUF6Oh4kW05v2NeXEBkqCe5FRHYQQhsBmJyB6mnbksqBVB+Pb2qJwPeP5aNgLs79Ix/WsaNcmFgDcTyFslXbBb2HIVYYC2YHoP403aSQ/a0ghwI4kJH9acckOUIATBA33O/Sk3slFaH2B/eq7VZPKjCp8brKGCjc71YSMMDibIOAAvI/WuLuNfIbhUAgruB2NJPY2rRBWyupeCSaThfiHCg3walNpVp5cs8zM+SSqqcbnkKtrOMCeORhlYfjbPc7Cq+V4v7yitgGmXz/APLT5mXn9KjybJcEuy1/7JW0OjR34aV5WAaYBvw+ntUe58JARrIpmliccSsjbEd6urjxGtnFwPLZ2agfIzcbY7Vnk8YaHbwzW11PdXKxP90IThCp3x9DUI82WSWNaZEbQoImYJxrKVK/E+efenYNIs2RZFiKOBjPFurCmLjxZoDg+Xpk655EtVhozWWp3EkemzPjZiH55I32qb5JWyEeDdKhImMcZmOwBxMB+FvzVYQsGwCQSdwRyIp6802aymHmBWEqN8S8iVGf1xmoN062oiaKMuHkAEa89+eP44qu76LeNdk/gxLHNG3BPGco/wDI+laazvRe2yuBwtyZfyntWSEqXMZCscEexH/WpmmpqFuJLuFvtAjOJYxsxGPmxUJKycXTNC9oks3G+4xjFU+v6Xc6oiafZs0ERI8+bHyL2Hc1cWOoW2oQmSB8ldmUjBU+tSt6gm0ybSkqKuDwp4f07R3sHb4ZoyGKjLn1J96p7LT/ALRaPb3mmEonwrwr8LqOvvWtBxyFLzqcsjl2QhjUejLw24sNOYWGktwJkhThRn1qVpuoanp1jDp8GnokzAyyTSNxZJO5AHar8YAxgYoJzSU2uiTgnpmX07Q5471rq/m+0yuxchxnBzt/9Va3sMj6rYwquQVkOPcBf51bQQrLJwlguxOTXelR+frz3chzbwRMsakdlJ/Umq3Jt2yyklSPOL9Vsr67u2GVgjKgfWojSFUjkx8xB/UVdXVl/eMF2gBIMRlb2AJ/jVLNIYtM8woXZkUKuOZI/lWiLszTVMj+F7d9Lht9VuCGi86UcLDeInbI/wB3L3q2uopfEEv2q4BUKuIYTyjTt6t3q01XTUns7LTLSdI5J4RK6n8aDcfXNOaCJrOb7CYuITHBjdf8pj+JT1FRlO3y9k4QpKPozmtWkb6DZyS8ZfTbjy1dTg+U4yB9CKe0+5S6ggP2f/Jk+8fOTwnuO3erS8tJZRqGkOoDNG4G3N1+Jf4Vl9L1JNN4bp/ihcBXX8wP/Wpq5RohKoSv0QL8W0xvtPwsclk7vbSsccaZyYz/ABFJ4YkSW6n0qY5g1GIx7/hcDKH3zTnizTlgu4L6E8dvdpkMOXEP+lVWmSGLWLOQbcMynP1rqY4KeG1/H/04+SThmp/xf8IzBlYq3zAkH3GxpKevHWS/uXX5Wmcj24jTNb49JmKWm0FFFFMQUUUUDOaWkpaBBS0Cg7jY4oELSDPEe3Su4UVzh5Vj9SM1bWdvYwlZS4uZFORnZR9KpyZowW0X48Mp9DmlaeYFF3OmH/4akcvX3qdJNwJkglicY9aakuWlOWO1Mo48pOKTOB1OSa5U5Ob5SOrCMca4xH1RXlDzS8J6KNzTNzfIGaEKGA34F5AdyajrcfaZT5IIVPh4iNyaIrQRR3PDkkruTzNRr5By+BzTBm+ml5s0YH6muDMWvFPzFJSD6CpNmgtYxM/ROM/pt+9VekycWo3UUm7OPMHvmn8sj1SL1M8QhI2Bzn06V3KS0Eq9QpoiXKI2csBwmuJsxyo5lKxseBsDlnkarLvR3/eccWjO07+WsjeY7dWGPhUetZ9p7/XgIrVRG8bcTSg8PtvU5vC1/qEUXFdArCzJwlfkGefrV/4akt9LSK21C0CRKx4pEX5vVh61JOK/cUoyn2tGQvPDE8F3Css3mrJGHLgHc9QM1Nh0m+0a6h1K10jz2jzwRzxeZGwIxll616hrWq+GtTsYrUznzY2DQtbx5Mbf/OYqFZJqd+rbrAo24sHJ9aU8rQY8EZXZjofDXlaIst8FikK54MfESTnlWyXwxpFzbWzwu5uERczwKY8HH71Z2ukxW4DOTLJ1ZqlGeKEEM2MDlWd5WzUsMUV11Awe0s3n8wESEyScwAh5/rWZS2ElzAZGysL8HEORY7fwzV3dQzapqHEUeMcPCg6omd2PqegqcYIYuGKKPgiiHCoI3Pcn1NRuidcmQLfTIbq0V3UpKuV409DXVul5pd2s8SefHnhkC82X27irGwUK9woPwkhgOxxv/CpJQE9j3FR5EuKI9xbRXEnmWdwbabmTGBv7rUmPzlVVf7wjm/LP0rpE4d9i3VsbmuxUbHQlLRiloAKKKTFAATgcifQVIs7o2ugXd5cqsTqkigDfBbYfXFR6nW2nG9S1a4P3Mbl1h/O3Rm9B2pMaKq30uTTPDVxdyr/irpOAKfwAjYfpk1QaHpss/iONZYOKKN2VT+HHBv8Axr0PUrWS9SK0UYQtxySflXsPU01aaclpqczgfAqBIx77sfqaSnSf5E1dHknivTrq08ZeU7uiLDGts4OMIBgfvzq+8PeIJoIfLu0MgjOGBH7g96e8bX+n6j4hitYXWWW1jKu67gMTnhz3quVDHASRvjerm+UUmQiuLbRsNQtYZtattUgYMMoZkPPB24h+teS63bJZQX0IUlYL1o1HYZOK9L4/JZbi4Yx21jbCS4Y/lAyF9ycV5XLq394T3iXS/wDjmZyf/LcnK/yFWeNGV2ukVeVKKXF+xq31B7rSX0pwGAbjg49+E9veqlxJE4+Aq3PfpXcEjW88crLngOSuefpXd1Ks1w0itxce52wAew9q7kIKMqXTOFOTlG32hiilpDWoyiUlLSUDCiiikMQUvSkFKKBC0opBS0xCikoooAdgPDLxkn4AW50sMv2eRZF/zVOVP5T3poZzjkDsfaulJV1cYyDneqJQttF0Z0ky50rF3hmz967Mx9amxqpilxvkkD1rnT+GPQ4pQgBHE2B70zFxyBuJc/DlMH4R/U1yH2zrxWkRdQuhFGluMvk/G45E9h6CoNhb3KasbswuLfDIHI2Jxyp+6TjK8R2DFifQCpJmnaysbeNONGQSFORJznGal0tEErdv0d6Bem5tp1k2dJCxz2NWz28d5YsmQVlXAP8AA1FdLZeO6ijMMjqVlVhghumR/OmNIupreB7O4H3kXxAd157VW97Ralx+2Rf+HL82kqrdMGRgI5Wx8rjqa2Emn2l1hpIw3I7de3vXn1lKJ5hLbupS4GAWG3EOX16Vs/DdzNMhtmCjyRh42OHj9vzL2NUZF7NOKWqZMtdHtrcoQvEyOXBxjc1ZAYpQuKXFZ7NAhFcFATnApyigQ0qLGGIGMnJPeq+VyXJO2etWbDKkVWSxnix1FSQI5sATeMF5Mv8AOtHcacUtkcY4gNx3rPQERXKsTjOQauHmkcAM5ONhSknY7GsYorkMrE8LK2Dg4OcGuhQIKKDRQAUUUtACitHp8SpZxHG5XnWdUZOK1EC8ECL2UVXJkvR22wrOeMtWbRfDN9eRn75YysX+47CtJjIqi1vT/t9/bRSqr20as7qd+InbFRjV7F6pHkXhOyutUWEQQtcSf5jY/iT0ya3dpprwXMRvYUadmxDaq3EXbux7DnVtpbaRplz/AHPp6wQSIOIwxjl7+tL4l1a08O2T6kkSNqdwvkW+eZ9fYczV7m5ypLsilwj2ZXx/rMf2eTSFcOtvie+dRgO/4Y/YV5PayH7UHbqwYj61p7uXztD1RWcyTACR2PNiTkk1k0bhdvzYx7V2fCgoxkcXzpuUojt0ALyfhG3mNj9abzQaK6cVSSOZJ22wpKWipCOaKDSUmMDRRRSGFApKWgQtKKQV1TEFFFFMQEZpUy+ABudsetctkDYZNd28nk3AlbPwnIUdTUJSa2kTjFN7ZfX4MGlRWyyCMKArsf4Dua4s5FVLeMZAaIhc9d6pprqWd+J2OByGc471LvHMVpZop4XEXFnqMmuZLA4pRfbOlHOm3JdI7uVLuYlGeI/Gew7VZaTaMJLaSVwzIWhGBsMbiuUCPlQACmAfYjIp+GSMSyRb8fmJMvYDHC2T0rLJ6o1wiuVj2oxLfTpDH8qgl3HUDp+tQJYoo7z7MjMLiJvuHPI7Z8s1oJrEWFiZS3mTuy5IG2ByUelUs9jMkM8koA+8WQP9ef0qEWWzj7HNGaE3b28iiNZTxKOXC3Uem9bKwaNJI471T5g2iukHCfZux/Y1RavpMlvPFdWqoyA8UoI3II3+hrQ6NessSwXI4oSMJIRkr/pb+RqqbvaLcceP2su0MnEo84OvqoyfqKeplLeJWDqig9CKerOX9BQaKSgQU3LCJN+RpyimBnNZtrwzwG1mSFkOW4lzxDtVvps7XFkrSDhkX4XHYipLxpIuHUEVxFAkHFw5+I5qV2qEN2+n2to3FBCI2xgkdffvUmuc0tRAWikpaBhS0ldCkA7bJ5lyi9zWoA2xWf0qPjv1PRd60QquXYxAKyEPijTpfFmq2kl0vHDIIQufl4R/M9a1lzcpZ2kt1J8kCNI3soz/ACr5ShaXVdfutQaR045WlLK2GyxyBmrsGL6l2UZs30mqV2e1alLpumeL21Ke64I3aOZHU/Cn4ZM99sY9axHiPxDNrWoXWrTKyQRjgt4j+CPPwj3Y7moFhKBKHlmuLmX4olilPFGUZdySeRB3qXcW0Z8P38K/FJFGpOeeO9bIxSceX4Rlcm1Jx/L/AMmesrtlMwckm5Rkf1yKgjdRnnjnXRznY4NIK7kcajK0cWWRyik/QYxRRRVxUFJS0UAcmkpTSVEYUUlFIYUopBS0ALSikpRUkRFpaSlpiCkNLRQByak3UiySRuCCPKRfYgcqjmuQuOuSefrUJRuSZNSpNEyG4aPzpeInhTJ9cHYVcWdyiXEc7fFbOOCb/wDrbr9DWczn4MkBuY74qxtZRHp10p/CuVHvtWHyMV3I2+Plqom7dWmgazIJnjAZDj4ZAORU9famJYVuLVo2BKMMMOvtVL4a8RyWoFjeg3Nqo+H88fqvcelai5itby3F1bRJfJ+ZW4Wx29/euXkhLFLizsYskcseSM+2ryaPJHbyiW4sgMNkZaIdweo9K0nhq/iacxLIsiMPhYbhlPI/yqJc+HLG8RSFmgbGeKNyCKjpoSaLbB7ESloiXIdslh1H86i+Ml+SS5J/g3+AF7UlQdMv1v7COZW4sjf+tTM1nLhaKSloEFJS0lABSGmrq5itYWlkYBVFVUF9NqD8aTRW8J+V5X4QfYDc+9NRb6BtLstXlVPmYL7mlSZH+Vs/Sq/7FHISJbyWb0tk4Af+Zt6jz6RHIP8ADxNExPzSTNJt7cqlxXtiu+kXgweooyOlUMXh7ULfJGu3kZbcLhSoHtUix0q9t7z7Rda3dXeP+GVCofcClS+Q38FvSiuRXQqJIudFiwskvf4RVsDUWxh8izReuMmpGKoeyRmP7R9SNj4HvkifhnugLePHP4uf7A14Lo0KLp4K/iYnP8K9V8f3n95apNbo2YNMhddvxTMvxf8A6jA96848N2xuobaIYC8PEx9K6GD7YGHPHlNFnYaexlhU85DlvQU1Zamo8QXlpdFVil4oQTtgdM07rNw9j9kAPC/meY2OynaqPXogNankTeOYiVSOoIrXhxfUe/aM2bJ9Jfb6aIUyeVPJETujFa4pWnmMZjMh4Tt6/rXI7V2IcqqRx5cb+0WkopKmRFpKKKAENJSmkNRGJRQaKQxK6FIKUUALRSUtMR1RSClzvUhC0UlFAgNFLSUwDrSmUheEA4YgGkpOH4SASM9ajJWiSdMeilMU8cg5qwNWkOr3Onaw7WcnC3FhkO6SehHf1qmLAH5lB96cWKeTMqQzSNniysZO9Zc+JTds0Yc0oKkem6frVrqtrwAmGc4V4WOGAJweE9ak6cTHpzpOzAxyOo8xviVAfhB+lee3MqfarcE8Jf4h0II329aL+e5vm45p5ZJXd5JlI4VOTsAfxVyPpKqOv9ZqVmk0DxLZWXiubSopw9vcHijYfKr9VB7V6ENwCOteKT2cdxAjxYidPiR1GCpFej+DfEY1rTTBckJqFr8Eyfm7MPQ1Vlx0uSLcOVt8ZGlopM0tZzSFRr97tLJ2sYo5bn8Cytwr9TUmjFAjOp4dutQjJ8QXgvjxcSwwgxxL6d2q3js4IFxHCi47CpdcSxmRMBivtUnJsaSQ0Zo4hlnVcdzXC3ULvhXz642pv+7RxHkKkRWyRb8zSpErHPWgUtA50hHQFSrCAz3iLj4Ruaiir7SLby7cysPifl7VGTpAiwFUXifX20q3SzsSr6pdAiFTuIx1kb0HTuad8R+ILfw7pvnyKZZ5W8u3t1PxTOeQHp3NYy1juDNLe3zia/uTxTOOQ7IvZRSjH2wbt0NXGkLBol03Ez8ELs7tzZiDkn1JrDeG4xbxWiH53QufbkBXrtyIrXwZqElwAVkt3LA+2wryJZpLa2tp7aIyyfd4Ubkqoya1YW5Joz56jJMTxU6yXCGNuLyJWhf0OAaqnlFzpsUZyZrduFR1ZDv+xrXN4bg12a/u4dUhtvtBjkWGVCQdvnyORHKqu88BaokvDY3FpqKgZLRyeXv2w3OupgnFQSumjlZ4Tc26tMy3EGJwDtRmrC98Pa1pwLXelXkKDm/lll/UVXZGcZ37cjXRjJS6Zz5Rce0LRRRUyIGkoNFIBKKKSokhDRSGikB1RSUuaAFpc1zS0wFpaSipERaWkzRTAcijkmlWKKNpJHOFVRkmrqDwhq0pBlSK2H/qNk/oK0fgWwWx0GXVXUfaL5jFCcbpEvMj3P8ACtElm7wGZMkA7jH/AMzWKed3SNcMCq5GFPgvg3kvz/yR/wBacHhWwX5pbhv+YCnNa1KW21owAspYBkbmCOwFLG0zLmSV2bnjkBVbnJ+yahFeiytba3tVVYYIV4RgHyxn6mpn2iTIHER7bVX2ilYwSxYtuSaduZRHDgll4wV41XPD64qtotTKfT4Y53vJHCsCTFk9Bk59qi+W0LGKUHiAyrfnXv796tNP0xYIwz54j+HoPXHentUSNNNklZR91hh6VBxtElKnZQbKG4eROcVAubq70q6j1OwkMU9ucFhyZexHUVKEwaVIOHdgTnt2B965kCTwvGfxAqQaqX5LHvo9D8MeMrTXYkimX7JfFcmJ9g/qp6itNXj+k2iX+g26Sg8UWVDKcMpB5g9KvNJ8Ta1o9wLPUIm1K2/4cy7SY7eprJPFt8TbDI6XI9Epag6brFlq0PHaTq5HzIdmX3FTaoarsvT+BaKSigApKWkoASlxRQKBkmzgNxcpGBnJ39BVtrWtWXh3SHvLxuCKP4VRfmkboqjqTURb2x8OaFNq2pyiGIDOTzI6ADqT2rzW5vL/AMZ68l7fKYYU/wDD23SCPue7nv0pRhydvpClKtLsm6c954h1mTxDqy8L4MdrBnKwJ6evc1eIokmVB1IFNpGsUaxoOFVGAKn6PambUUOPk+I1KTJRVEnxDpr3ukzIzcNrBbSuQDu7hTw/Qc68i0BVSbT0jYtwRl2PrjlXsmu3Ek2nXlnaHLeQ/my9EHCdvUmvJNHhitdHj1DkVZAfRSu/71f4v5MnldosZ1ksbxLiHBhcFGjzjBO+R9elTbOVrgBpI3jOcYcb+9KOGVACFZTvvuPepVu3lShv1roVRguy903ULzTQwtp2UMMFX+JT9DVtZWmgeKENjr2lWU9wf8uURiNm9MjkaoM7ZHKlVyjBlJVlOQR0NVyje12WKXpj2rf2GaHcsW0u+urA/lb71f61j9T/ALEvE1nxNZTWmooOQRuB/wBDXoFx4u1BkCiVYzjB4V3PrUVfE+qR8rosOzgGnDJnj7IyxYpejxLVNC1bRZmi1HTrm1YfnjJH6jaq4MCMgg+1fQKeO5+Jre7ihmQ7ESLs3tmqrUtF8Fa/NGsujvp00nz3Fq/Dwnvw8jWmPlSX98f9GeXjL9LPE6SvQvE39j+s6PavfaZMurWSrx/AMShe+Ov0rzvnvWqGSORXEzTxyhqQUUlFTKxc0ua5FKKAOqXNc0tMBc0ZrmlzTELT9pay397BZwDMtw4jX3JpitR4BtVk1ya+f5bKLiX1dth+2ahklxi2Sxx5SSPQZIIoUitYFCQ2yLCgHYDGfqaureIJbIg5Baz3m4GK0FpJ5lvGRndRXLkdRGb8S+G476SG4twFuoiWjzsG7r9azqQlSyuhR1PCysMFT2Neh3cLEqwGQBg1Ua1orahb/a7ZeG8jGMHlKv5T69jTi6IyV9GThuPJbgI+HP6VMVix51R3V9bWvE1xIIiDhlb5ge2O9dabevrEogjheKzVcu7HDSDsOwqwrstjdSSv5dpA055GQfIp9+tcT6W81o51C4LqFJMabL9T1qxRhFGqIoVVGAANhVPq97c+XJDLHHFGVJDljhwOnv6VFslRW20KLazRruC5Bb6bVWQyedJI3D8w4s+o5irGyTMbcUvmGX7wqNgNqWaAt5sUICO7IFwORFRktEovYvhuVAl3GpLAS8WPcVeFRIOW43waoPDKBNanVgFMkW69mU4NatoVPSsc9SN+HcEVz2sU8gnUvBcr8s0R4XHv3+tWNn4p1DTfg1WH7Zbr/wDkwL8aj/Un8xUeSMxvkcjQajp9k6ro2NhqFpqdsLiyuEniPVTy9x0qTXnT2RiuftVjO9ldc/Mi2Df7l5GrKz8bzWMgh1+2CpnC3luCUP8AuXmKreP/AMkudf3GzpKZtb22vrcT2lxHPE3JkYEUk97bWq8U9xFEvd3AquiwfxXXm2tpby31/MILO2HHK7csdvUmszqHj/w/p+R9s+0yD8MI4v35Vm77Vr/xbJE15EbTSoW44rUneVvzP/SprG33pFbyJaW2SdV1m88Zasl9cxtDp8J/wVoe3/mMO5rSabZ/ZLbBH3jbsf5VX6LY+dJ9ocfAnyjuavxGSac2ukShGts5HOr7w/CDHLI3+2qVoijYYYNaXSYvK05NsFjmqJvRajrU1RNFvVRQqi3k2Ax+E14rpFkG8PwKlzIDLGCwbDLn2r2nVT/3Lf8ApbS/+w14porzQadbLjzUManA2K5H71s8PakYfL00W+nQ3kFhEk0cRdBjAkGcdKkrdqGKypJER+Zdv1qTa2pncA7KOZq8sza2iMAgU98c63XRiqyvsbmO4gIR1fg2ODTxanrmwsb6RZOExSDcSwngb642PsaqzO1ne/Y7xwsp3ik5LMvcevcVG7JVQ/L84Nck7V0+4Fc0wK+dPvmQjKnfBpvzW05TKcvCu5HUVJuR999Ki3XHNGtrGoL3B4N+Sjqx9hUiN7PVvBuqPf6csKxfcQxIVlJ+Ytvj6CvF/wC17wlH4c8Tre2qcFnqfFIqgbJIPmHsc5/WvcvCsNtaeHbaK1B8sDmRgk8v5VT/ANqPh7/tH4Fu1jj47qz/AMTBgb5Ubj6jIrNiycMt+izLDnCj5jNFHPfoaK7ZyBRS0lLSAWikpaYBWi0zwPq+paamoMYLO1k3Rp2ILDuFHSmvCWhJrmsBbjK2VuPNuGHUdE9yf2r0TW72V9Mnl4MrCnEkS7AAcgKz5crTqJoxY01ykZO18D2gYfa9VaQ5+W3ixn6mrrQ7KysLK5NmsiQzTEr5pyxC7b/XNZy6vZ3sg/mESyAKiqcfEeQFaGBfIt44Ac+WoXPc9TVEm32y+KS6ROjmDylcbdPWtHpJ4rVRnPASMVk9136jer/Q7j70p0cZFVyWixMvSNsVyVGMYrrNFVEjJeLPBdtrmL2CJF1CPkx2Eo/K38jVJoloYLeUSKUlD8LqdiuOhr0jFVOr6Obh/ttnwrdqMMrfLMOzevY1OMvRFr2UAiBPf2qNrdnwWjgLlSvmISO1XenCG/ViuY3jPDLE2zIexH86najp6XWnNGB8SDK/0p8tjrR5tEzCAmJAXIyo5ZNP2sLqTLKAHPQHOO9N28bRXNxA4/yX4R6g7ipdWUVWVVoVXxVbzoDwyl0yRgE46VrOLIrO3BVL/T22B+0AD6itHFHxRg53rFnVSN/jO40clQwIPWmGTGccxUojHOuMZODyNUGqiIaRkWRSrKCDtuOdSXh6imGXHSmIz1/4YjYu9lcSWhbcqhPCfoKq18KSykfaLxpc9Bk/xrZNSBetWKckUvFBu6KfT/D9nY8LCJXkXkzDNXdravd3CxKOfM9qWOIyOFUEknFabTrBbOHcZkb5j29KrnP5LYY0tIft4EghSJBsoxWg0uwSFDcTjcDKg9PWquzh8y7QY2zmrjUZ/Ks2UHdvhFZJP0aUijlcz3bH8zVqYU8uFE/KAKzFhF5t9GP9QrTxSq7MudxSmNEfVl/7k1A//wAaX/2GvGtOXg021P8A6K/wr2PXpRF4c1Ju1rL/AO014/pZV9Fs8jOYV/hW7wupHO8ztFtZajJBGyrg46HrTV1rc0kgEeI1A3yMmoypwvwk5BFMXqADjHQYNb6MRfeGtQnu7vypiCrAkbYNaDVNGttZ09rW4XbPEjj5kb8wrHaAZEuoTF8x2r0NRwjeq5dkk9Hmz/b/AA9fJb3czNGGx8e6uvdT0PpVm2pwgfAC1aHxBpUGp2ZWaPjUjB7jsR615rqN9L4duBb3sDyxHaO4Q7MOx7GprZF6NG92s2H+XvVt4N0OTXtQfUXDC1H3UfqoO7fU7fSsjpkqeI3S0snbhk3nbG8adR7nkK9w0DTjYWUKhfKWNQqRryUetV5JcVSLMa5bLqGBYYljjUKqjAA6CuyNiCMg8xTijIrmeSK3i8yVuFcgZ96xdmiz5S8daGfDvjbUrBV4YRL5sI/9N/iH6bj6UVsf7eLFofGVpehTwT2agsBsCrEfzoru4J8sabOPmjxm0jy4GlpBS1cUi86ttE8OX2uuTAoit1OHuJPkHoO5q38L+EI7+yTVNUZltGJEUK7NNjr/ALa2pdREkMUawwRjCRoMKtZ55fUTTjxXuQxpunW2j2AsrTJUHieRvmkbualEgqQQCDsQetNg0orMaaM0nhwQ64JWcvCG/wAMrHZCeh9e1bfT9Cit8ST/AHkvboKrnRXQqyhlPMGnbbUp7BeGTjuLccjzdP6ik7Y4pI61uyEE4mX5ZOY9agaVdGK4AOxjb9qn3l0uoxMyMCg+XFURbybtJDsD8LULoH2egjBAI60tRdNn8+xjbOSvwmpdVEgrlhkY5UtAoGU+o6RJJdrfWMggu1GOIj4WH5WHVT+1PadqC3okjkjMF1DtNAx3Q9/VT0NWeKgajpouyk8En2e9hH3UwGf+Vh1U9qYjF+KbM6brMc8ajyrlgjenb96p7m8S3HxHL9FHOtL4ic6xp0lrJEbe+iGJIs/K3RlPVSeRryi31Nxfst83lhCQwxkkjvVsXoplplvdXpOo2Ekh3+0LwgdBXoMBBiFecJZyXTxajMpjQzIkCHnjO7GvQbR8qRWTO03o3eKmk7JJUMN6beMjlvTgO9dkZWsxtI/MU08WRtUjHXFckUxMhNFg05bWUt0+I0JHfoPrT6GJbxfOXiQ1oYwgjAjACdMUnKgUbI1jpsdoAxPHJ36D2qetcilBqp7LCbZyiBy56Ckv7kTkEfKoqLxUj7jHelW7HZL0shJTIfwITXAvniu/MB68qIT5dpK3ViFFRsZO9KrY70WPiW5WTwffyIdngYD6ivJtAmD6VaRnYiIAeteg6vK3/Zu6tz8pUn9jXmmkMP7ptip5JzHvW7w1SZz/ADHtF/KjCPjUbpv9KDGJE3GVYVza3olXgb5x+9c2s330lseabr6g1uMRM8N5TVfLK/FEwX9a3jNWT8MQrJdzXCr1IJ9RtWpzgVVJ7JRWhm/mEdhKScbYFYfXI4b7TpLWSIzNMeCOMc2c8setX/iO9SFOF34Y4xxue3apPg3w1Nd3SapqKmJnGIYTziQ//wCj17ClfFWx1ydFl/Z34Eh8PaTG0ih5m+N26u/f2HSt4EwK6iVY4lRF4VUYAFd4rLKXJ2XJUqR2pwBWb8S6oomjtVPy/E38q0FxIsFm8rHARcmvNLmV7u7mm3PExPtTxxt2OT0WOt+IItNm0y7ubUXVtNbPDOSAfLUMvxYPMDO9FZnxLdMdDiEmB5Dld+qupVh/Cir1iTK3No8VFKBvQKWuwcc9R0WUt4b0sE54bZAP0qaDmqzRUZNA08Eb+Qv8KE1uzW8aCRzGVOOJuWa57Oiui1AroVwrqyBlYMp6g5FHFURkqKCSYfApauzpt1zEZrmyvjbuA26dq0MMqyxh0bINRbaJJGZOkzrJ5ixvE/UqNj7iqq+s57UHzo24W/FjY1vw2KR1WRCrqGU8wRmkphxMv4U1LzOKB23J4fqP+lakVUyaPFBP59oqxtniKjkatEbjjDd+lD3saOsZpBs2KM0NsM0gFJrkmhXDrxA7UUgK/VdIj1OFSG8m5j3imA3U9j3HpXlt1okEHi+7+223BcMBKqH5CfxMvcda9j5VU6/odvrlkEc+VcRHihnUfFG38x3FO9UCq0zze/zJJaxgf8dT9BV/aZyPWq0WssF+YL2Lyry3z8P4WB/EvcfwqzhHCorLL4N8N7JwFdimw1SLMLJcANyqkuGSNzXJFTb6HhYSKMA7GmYoGlbAFFjog3EZePY4I3BqZpF/hfJkOBnHsaSa3ZMjHKoyxcM2QOdPTQumaJ2IAA5k4FdjlTMYLMCd+EY+tPCqiYtJ+MelLSDmaAHC33ar23NcZxQa5zmgCLqrA6bMvcEV43PLfeHPLGFmtrkeZHn8JzuK9f1U/wCDI7mse1jBf6Wttcxh0wR6g56Vqwz4bMnkY/qa9lNperJe+WSPKlb5RnYkc8VYSTNbMLpN2jOSO46is1eeG73T53jil4ogDNEw5sV6e+Kd0rWrnUbyGxkiVmmIXjG3uSK3ppq0c13F1I9b8IRFdI48YMh4v13q5u5UtbV5pCAqDJJqFaTRadocRGDIw+FKr4JLjxHOBOR/dsLb4GPtDjp/tH71W17LTrRdKfWr0avqClbRG47aJx/mH/zGHbsK3Oj5mvi2CEiX4R79arFccCryA7VoNDiC2jydXaqsnRZAswaXiqPcXMVrHxyuFX+NQIdbimmK4Cp+YtWdJstGfF2qLaaSY87sCxHoKieFrCEaA1zd8PEy5YnoMZqi8UXqalqUdt5nCs0qxDqcDcnFaaz0L7Q4lu1eO2GPLtc88cmf19KtkqikQXdmWj8NN4humWSP/u9XzxsPmwdsUV6MFVVCqoVRsABgCik8kvQ1FHxzyoxnI77U8lncyfhWId2O/wClSYtLjA4ppGcDnvgV23L4OMomzsfEGnR6BZzXF1HEwiCFebAjY7Vl9X1y3lupWsrdpEc5DSjhGfbtVbcSQp8NvEqj8+N6hsSdycmslUaeTaHrbWdXsbppYLl1ZtyvNT9K02m/2goeFNStuA8jJFy+oqh8yOO0ClVZyMAGqdbd5LkRk/UdqTQlJo9jsNSs9SjD2dxHMOyncfSrGC7msj5i8XCPmGP5V4y0UlvIk1s7RMvNkODWi0zx5qliFjvFW/iHJj8Mg+vWouJYp/J7FY6hBfRho3Ge2amV5daeIdNvJBNp119kuWOWtpjwhj6Hoa2GkeJUuPubrKSLzzzHv6etQcS1SsvmTJoVSvtShw6gqQQeooqIxaWuc0uaQEWcPbhnj+U7+1NQ6ijELIOE96nMAykHcHpVLe2xt5OJd425elSWwLpSGGQQR3FLgVn4LyS2OUOV7HlVrb30dyuFPC/5TQ1QhrWNFttZtgkpMc0Z4opk+aM/zHcVknjns7o2d4gS4UZBHyyr+ZfTuOlbmGTzEzjB5EdqjatpcOqWJilyGQ8cci/NG3cf061XKPIthNwZmVUmIHtTlvJ5c6sOhosi3nSWlyAtxEMnh+WRejr6dx0NI68DkdjWRqnTOhFpq0XUsQlhIPXeu4Y0RMKMZpixm82AAnddjUpcbjtVP4LRuWFXGcb1DW0XzwRtg8qsTXBUZzTsQijAwK7FIBjlXQFIBKQcs96H2U0oGwoEcOeFc0LsBXMpzIq/WuqAIuopx2xA5jes6IggwBsTmtPJh8qe2KzsoKSFDsVOKsiyMkVeqqfJjYMFKsTk+1RtM0y1OuxXaRBZFhy+Nue361N1IgokYIDPxBR3OK50COTUJZEswVlmbBY7iJF2yf3wK24ukzBmaTaLyOOXV7w2kbFYIwPPkHQdEHqevYVp4YUgiWOJQiIMKo5Adq4srCKxtlghXCL35k9SfU1Jxipt2VAuSwANaVr+LS7CKIfHNw54e3vWbVuE5HOkaQsckkn1qDjfY06HLy6lvJS8rlj07CoFzLHbRcbn0AHNj2Fc3uoxWvwZDSYyR0UdzUWxtLm/vUlnyZHPDGn5B/Wp1Qk7NR4P0ZE49Xu0D3cuRHncRL2X+ZrVmmLaBbe3SJdggAp8MpOAwJ96yyduy9KhOVFKRvRUCR8jvfIo+AcR9aiy3Ekvztt26U15bE7scem1doigcv1rruTZyUkjkDiI579a6EfCc9P3pykZuEZNRJWRrhtgMbLS26+UOIjLv07Uixl5yDuq7n37VJjX4uM/SgQ4BgYpqSANuuxp2igCBJGQcOtSrfU761UCK4Yhd1D78PsedOEAjBGRTT245qcelAG78K/2gjK2mo8MMp2BOyP7djXottew3SgxuM4yV6187XULfZycbg1ZaH4u1HSOBSxngXkrH4l9j/KoSiWRn8nv1LWN8PeO7XVFCl+JhzU7Ov06/StfDPHPGHjcMD2qpqi5Oxym5Y1ljKOMg05XNIZnrq3e1mKNup+U96ZBIOQcGtHcW8dzCY3HsexrPTwvbTGOQbjke471YnYmWGm3pExjlOePkfWreORX5H6dqyoO9XVrI1zAJEOJU2b1pNAjrUtHS/4ZEcwzoeJJVG6n+YPUdazzvJ58kNxGIrmLaRBy9GXup6Vr4Zg2x2YcxUPW9JXUrdZImWK8hH3Uh5eqt/pP7c6pnDkXY8jg/wAFLp0vBc8HRqtnJUq3TODWctpW+0cLI0U0b8Mkbc0bsf69RWlK8cRB6isMlTOlF2tBmkpuJ+OPf5hsfeu6iMWlpKXegBuRviVepNOVDR/NvzvkKNqkytwQs3pQwI6N5t47dFqRio1qPnPepQoYEc7XDD0qq1WNBMrD5yMmrK5bypuM8sVQ394F4p5ASWOFUc2PQCpwVvRCTSWyk1CWafVo9Ptsm4kizGMbbnBJ7ADet94e0SDRNMS3iGWxl3PNj3qo8M6G6zS6jdAG4mxkjkAOSD0H7mtUM10IqlRzJvlKzqkNIXVFJYgAdSaZivIbhnWMluDmcbUyI6TiqjUtVdFeO1GWA+J/y07ql4LaIlm+JtlXt61B060+1oJZAfJJyAf+Ie59P400vYhNK09pCt3c5ZmPEit/7j/Kt14ZsFaV7phsnwr71QKh4gAMk8q1JeXTtLjt4E+8IyzdjUMj1RZBDmq6oLUGKHBl6n8tUUGozwyFlc5PPNdiFHJM9wiHrk5NPi+0mwAKRPcOPxEYFQSpUkSsnWN/qEuAIeJe5oqsuPGE/DwwQJGOmd6KX05P0PmkfNgOc4oxwnPSiitxzjquWTiTi4wmflyP3oooGJ5TIqqgUp1IO5pwOOR+H32oooEKKWiikAUUUUAcyY4DnlUG4t+Al0Hw9RRRTAhxyvbXSyRsyMjZDKcH6GvU9L166MEcsLG4QqCCCFkx/Bv2ooqJOBqNL8Vw3T+VIcuvzDHC6+6mr6G4hnUGOQNnp1ooqEki6LseqPd2kd3FwNsw+Vu1FFVkjPzRSW0xjlXDDkehHcVFk1i4tL6106ykgiub5iBLP/lxqOZPrRRVvogd3Gu3mm6iqTXsGq2coU/aYI+Fo85B2BIIB9a1VvPxpwsQc8j0NFFQZNEDWtLNzGL60j4r63GCg289B+D/AHDmp+nWuLHVLK9tkkinU8Y5NsfbeiismeKqzZ40nbiIxEN8c/LN/GpGKKKzGsXrXE8nlQO/YbUUUkMiaapLOx9s09etwoq96KKfsEc2pG4771JAooqMuySKfVr1ACCwWOMZZjULQ9Ol1W8+23ClY12iQ/gU9T/qP7CiituCKqzB5MnaRslVYowoAVVFV+o67Y6co86eMMdwCwGaKK0xVmN6KaW/bUsSLIGiO68ByuP51ZwOmnaa087cC8z69hRRU2vQl8kC1tJdZuftt2pW3z8EZ/EOn0/jV8FxtiiioPsaHI5GikWRDhl3BxypJriWZi0kjOe5NFFKiSYw9xHD87hfeqrU/EljYW7SzuFRfxMcf/dFFTiiEnRg9Z/tDvZ04dMgFvGx4fPdcsPUDp9aKKKsopts/9k='),
}

def portrait_anime_html(av, width=300, border=True):
    """Affiche une illustration anime détaillée choisie par le joueur."""
    av = av or {}
    try: idx = int(av.get("portrait_id", 0)) % len(PORTRAITS_ANIME)
    except (TypeError, ValueError): idx = 0
    label, data = PORTRAITS_ANIME[idx]
    outline = "border:1px solid rgba(95,165,255,.55);" if border else ""
    # Teinte légère pilotée par la couleur sélectionnée ; le portrait illustré reste la base.
    hair = str(av.get("couleur", "Noir"))
    hue = {"Noir":0,"Brun":8,"Châtain":12,"Blond":38,"Blond platine":45,"Roux":-18,"Rouge":-28,"Bleu":165,"Violet":220,"Rose":275,"Vert":105,"Gris":0,"Blanc":0}.get(hair,0)
    sat = 1.0 if hair in ("Noir", "Gris", "Blanc") else 1.08
    filt = f"hue-rotate({hue}deg) saturate({sat})"
    return (f'<img src="data:image/jpeg;base64,{data}" alt="Portrait anime {label}" '
            f'style="display:block;width:min(100%,{int(width)}px);aspect-ratio:1/1;object-fit:cover;object-position:center 28%;'
            f'border-radius:18px;{outline}box-shadow:0 14px 34px rgba(0,0,0,.28);margin:0 auto;filter:{filt};"/>')

def avatar_svg(av, age=25, univ="real", badge="", taille=190):
    """Portrait SVG stylisé anime : grands yeux détaillés, mèches, ombres et tenue."""
    av = {**{"peau": "Beige", "couleur": "Noir", "coupe": "Court", "yeux": "Manga",
             "bouche": "Sourire", "accessoire": "Aucun", "tenue": "Classique", "iris": "Marron"}, **(av or {})}
    skin = SKINS.get(av.get("peau"), "#e8b98f")
    hc = HAIR_COLORS.get(av.get("couleur"), "#1b1b1b")
    if age >= 60:
        hc = "#d4d4d4"
    body = UNIVERS.get(univ, UNIVERS["real"])["couleur"]
    iris = COULEURS_YEUX_HEX.get(av.get("iris"), "#6b4226")
    tenue = av.get("tenue", "Classique")
    metier = str(av.get("metier", "")).lower()
    if any(x in metier for x in ("médec", "infirm", "chirurg")): tenue = "Soignant"
    elif any(x in metier for x in ("polic", "gendar", "militaire", "soldat")): tenue = "Uniforme"
    elif any(x in metier for x in ("cuisin", "chef")): tenue = "Cuisine"
    elif any(x in metier for x in ("enseign", "professeur")): tenue = "Professionnelle"
    if univ == "manga" and av.get("village") and av.get("accessoire", "Aucun") == "Aucun":
        av["accessoire"] = "Bandeau ninja"
    if univ == "manga" and av.get("saga_manga") == "onepiece" and age >= 16 and av.get("combats_gagnes", 0) >= 3:
        av["accessoire"] = "Cicatrice"
    clothes = {"Classique": body, "Sport":"#16a34a", "Élégante":"#7c3aed", "Ninja":"#334155", "Pirate":"#92400e",
               "Mage":"#6d28d9", "Héroïque":"#dc2626", "Soignant":"#e8f4f8", "Uniforme":"#1e3a8a",
               "Cuisine":"#f8fafc", "Professionnelle":"#475569"}
    shirt = clothes.get(tenue, body)
    ink = "#28202a"
    # Hair silhouettes are deliberately layered to look like illustrated anime hair rather than a flat cap.
    c = av.get("coupe", "Court")
    back = ""
    if c in ("Long", "Carré"):
        bottom = "190" if c == "Long" else "150"
        back = f'<path d="M43 91 Q31 31 100 26 Q169 31 157 91 L165 {bottom} Q148 {int(bottom)-4} 145 112 L55 112 Q52 {int(bottom)-4} 35 {bottom}Z" fill="{hc}" stroke="#080b16" stroke-width="3"/>'
    elif c == "Afro":
        back = f'<path d="M38 101 Q16 79 35 48 Q44 14 75 25 Q100 6 125 25 Q159 17 166 52 Q185 78 162 104Z" fill="{hc}" stroke="#080b16" stroke-width="3"/>'
    elif c == "Queue de cheval":
        back = f'<path d="M143 55 Q180 56 165 95 Q157 113 168 147 Q145 135 148 103Z" fill="{hc}" stroke="#080b16" stroke-width="3"/>'
    elif c == "Deux chignons":
        back = f'<circle cx="47" cy="50" r="21" fill="{hc}" stroke="#080b16" stroke-width="3"/><circle cx="153" cy="50" r="21" fill="{hc}" stroke="#080b16" stroke-width="3"/>'
    elif c in ("Tresses", "Dreadlocks"):
        w = 10 if c == "Tresses" else 13
        back = f'<path d="M43 63 Q27 94 35 130 T39 172 M58 54 Q45 95 53 139 T55 174 M142 54 Q155 95 147 139 T145 174 M157 63 Q173 94 165 130 T161 172" fill="none" stroke="{hc}" stroke-width="{w}" stroke-linecap="round"/><path d="M31 120 l9 5 M49 132 l9 5 M143 132 l9 5 M160 120 l9 5" stroke="#ffffff" stroke-opacity=".18" stroke-width="3"/>'
    # Face silhouette, neck and clothing
    face_shape = av.get("visage", "Ovale")
    if face_shape == "Rond":
        face = '<path d="M45 77 Q46 39 100 39 Q154 39 155 77 L148 120 Q139 158 100 164 Q61 158 52 120Z"'
    elif face_shape == "Anguleux":
        face = '<path d="M43 72 Q48 38 100 39 Q152 38 157 72 L146 119 L100 165 L54 119Z"'
    elif face_shape == "Doux":
        face = '<path d="M46 76 Q48 37 100 39 Q152 37 154 76 Q151 139 100 161 Q49 139 46 76Z"'
    else:
        face = '<path d="M43 75 Q47 37 100 38 Q153 37 157 75 L145 120 Q135 156 100 164 Q65 156 55 120Z"'
    ear = f'<ellipse cx="45" cy="103" rx="12" ry="17" fill="{skin}" stroke="#9b654b" stroke-opacity=".3" stroke-width="2"/><ellipse cx="155" cy="103" rx="12" ry="17" fill="{skin}" stroke="#9b654b" stroke-opacity=".3" stroke-width="2"/>'
    # Bangs / hairline shapes specific to each style.
    hair_front = {
        "Court": f'<path d="M39 91 Q31 35 100 28 Q168 34 161 91 L145 75 L130 84 L111 65 L92 82 L72 69 L55 91Z" fill="{hc}" stroke="#080b16" stroke-width="3"/>',
        "Long": f'<path d="M39 91 Q31 35 100 28 Q168 34 161 91 L145 75 L130 84 L111 65 L92 82 L72 69 L55 91Z" fill="{hc}" stroke="#080b16" stroke-width="3"/>',
        "Afro": f'<path d="M35 94 Q24 36 68 27 Q100 8 130 27 Q171 34 165 94 L145 72 L127 83 L105 64 L86 80 L67 71 L53 94Z" fill="{hc}" stroke="#080b16" stroke-width="3"/>',
        "Crête": f'<path d="M44 88 L48 51 L67 65 L76 18 L94 52 L111 7 L125 52 L146 28 L158 89 L137 76 L118 83 L99 66 L78 83 L60 76Z" fill="{hc}" stroke="#080b16" stroke-width="3"/>',
        "Queue de cheval": f'<path d="M39 91 Q31 35 100 28 Q168 34 161 91 L145 75 L130 84 L111 65 L92 82 L72 69 L55 91Z" fill="{hc}" stroke="#080b16" stroke-width="3"/>',
        "Pointes (manga)": f'<path d="M37 94 L28 42 L53 61 L58 18 L82 54 L100 5 L116 51 L142 20 L146 61 L169 39 L161 96 L143 76 L124 85 L104 65 L83 83 L62 73Z" fill="{hc}" stroke="#080b16" stroke-width="3"/>',
        "Carré": f'<path d="M39 91 Q31 35 100 28 Q168 34 161 91 L145 75 L130 84 L111 65 L92 82 L72 69 L55 91Z" fill="{hc}" stroke="#080b16" stroke-width="3"/>',
        "Chauve": f'<path d="M44 83 Q45 36 100 35 Q155 36 156 83 L145 68 Q100 54 55 68Z" fill="{hc}" stroke="#080b16" stroke-width="3"/>',
        "Frange": f'<path d="M39 91 Q31 35 100 28 Q168 34 161 91 L143 78 L123 91 L107 70 L88 92 L70 77 L55 91Z" fill="{hc}" stroke="#080b16" stroke-width="3"/>',
        "Deux chignons": f'<path d="M39 91 Q31 35 100 28 Q168 34 161 91 L145 75 L130 84 L111 65 L92 82 L72 69 L55 91Z" fill="{hc}" stroke="#080b16" stroke-width="3"/>',
        "Tresses": f'<path d="M39 91 Q31 35 100 28 Q168 34 161 91 L145 75 L130 84 L111 65 L92 82 L72 69 L55 91Z" fill="{hc}" stroke="#080b16" stroke-width="3"/>',
        "Dreadlocks": f'<path d="M39 91 Q31 35 100 28 Q168 34 161 91 L145 75 L130 84 L111 65 L92 82 L72 69 L55 91Z" fill="{hc}" stroke="#080b16" stroke-width="3"/>'
    }.get(c, f'<path d="M39 91 Q31 35 100 28 Q168 34 161 91 L145 75 L130 84 L111 65 L92 82 L72 69 L55 91Z" fill="{hc}" stroke="#080b16" stroke-width="3"/>')
    # Expressive anime eyes with iris gradients, multiple highlights, eyelids and lashes.
    eye_y = 100
    if av.get("yeux") == "Souriants":
        eyes = ''.join(f'<path d="M{x-15} 103 Q{x} 87 {x+15} 103" fill="none" stroke="{ink}" stroke-width="5" stroke-linecap="round"/><path d="M{x-12} 104 Q{x} 98 {x+12} 104" fill="none" stroke="#ffffff" stroke-opacity=".7" stroke-width="2"/>' for x in (76,124))
    elif av.get("yeux") == "Fatigués":
        eyes = ''.join(f'<path d="M{x-15} 99 Q{x} 91 {x+15} 99 Q{x+12} 116 {x} 117 Q{x-12} 116 {x-15} 99Z" fill="#fff" stroke="{ink}" stroke-width="3"/><ellipse cx="{x}" cy="107" rx="7" ry="9" fill="{iris}"/><circle cx="{x-2}" cy="103" r="3" fill="#fff"/><path d="M{x-15} 99 L{x+14} 101" stroke="{ink}" stroke-width="4" stroke-linecap="round"/><path d="M{x-9} 119 Q{x} 123 {x+9} 119" fill="none" stroke="#865e63" stroke-opacity=".5" stroke-width="2"/>' for x in (76,124))
    else:
        eyes = ''.join(f'<path d="M{x-16} 101 Q{x} 83 {x+16} 101 Q{x+13} 119 {x} 120 Q{x-13} 119 {x-16} 101Z" fill="#fffdf8" stroke="{ink}" stroke-width="3"/><ellipse cx="{x}" cy="105" rx="9" ry="12" fill="{iris}"/><ellipse cx="{x}" cy="108" rx="5.5" ry="8" fill="#171827"/><circle cx="{x-3}" cy="100" r="4" fill="#fff"/><circle cx="{x+4}" cy="111" r="2" fill="#fff" opacity=".85"/><path d="M{x-16} 101 Q{x-3} 87 {x+16} 101" fill="none" stroke="{ink}" stroke-width="4" stroke-linecap="round"/><path d="M{x-13} 97 l-4 -5 M{x+11} 96 l4 -4" stroke="{ink}" stroke-width="2.5" stroke-linecap="round"/>' for x in (76,124))
    brows = f'<path d="M59 83 Q73 77 89 81 M111 81 Q127 77 141 83" fill="none" stroke="{hc}" stroke-width="5" stroke-linecap="round"/><path d="M61 85 Q74 82 87 84 M113 84 Q126 82 139 85" fill="none" stroke="#ffffff" stroke-opacity=".18" stroke-width="1.5"/>'
    nose = '<path d="M100 105 Q93 119 100 122" fill="none" stroke="#8f5e4c" stroke-opacity=".8" stroke-width="2.4" stroke-linecap="round"/><ellipse cx="97" cy="123" rx="3" ry="1.5" fill="#8f5e4c" opacity=".45"/>'
    mouth_type = av.get("bouche", "Sourire")
    if mouth_type == "Neutre": mouth = '<path d="M86 141 L114 141" stroke="#81394a" stroke-width="4" stroke-linecap="round"/>'
    elif mouth_type == "Grand sourire": mouth = '<path d="M80 135 Q100 157 120 135 Q116 153 100 153 Q84 153 80 135Z" fill="#7b293b" stroke="#642334" stroke-width="2"/><path d="M85 138 Q100 145 115 138" fill="none" stroke="#fff4ee" stroke-width="3"/>'
    elif mouth_type == "Moue": mouth = '<path d="M86 145 Q100 132 114 145" fill="none" stroke="#81394a" stroke-width="4" stroke-linecap="round"/>'
    else: mouth = '<path d="M82 137 Q100 153 118 137" fill="none" stroke="#81394a" stroke-width="4.5" stroke-linecap="round"/><path d="M88 140 Q100 147 112 140" fill="none" stroke="#f3a6a0" stroke-width="1.5"/>'
    wrinkles = '<path d="M65 128 Q74 132 82 128 M118 128 Q126 132 135 128" fill="none" stroke="#7c5547" stroke-opacity=".3" stroke-width="2"/>' if age >= 55 else ""
    # Outfit details change with selected role.
    outfit_details = {
        "Ninja": '<path d="M70 177 L100 207 L130 177 L119 225 L81 225Z" fill="#e5e7eb"/><path d="M60 188 L140 188" stroke="#aab6c9" stroke-width="5"/><circle cx="100" cy="199" r="8" fill="#cbd5e1"/>',
        "Pirate": '<path d="M68 177 L100 201 L132 177 L122 225 L78 225Z" fill="#f3d9a5"/><path d="M53 185 L147 185" stroke="#7f1d1d" stroke-width="7"/><path d="M92 193 l8 7 l8 -7" fill="none" stroke="#facc15" stroke-width="3"/>',
        "Mage": '<path d="M70 175 L100 208 L130 175 L120 225 L80 225Z" fill="#c4b5fd"/><path d="M100 187 L106 198 L100 209 L94 198Z" fill="#facc15"/>',
        "Soignant": '<path d="M72 177 L100 205 L128 177 L121 225 L79 225Z" fill="#ffffff"/><path d="M100 190 v20 M90 200 h20" stroke="#0f766e" stroke-width="5"/>',
        "Uniforme": '<path d="M72 177 L100 204 L128 177 L121 225 L79 225Z" fill="#dbeafe"/><path d="M100 181 L100 225" stroke="#facc15" stroke-width="3"/><circle cx="112" cy="198" r="4" fill="#facc15"/>',
        "Cuisine": '<path d="M72 177 L100 205 L128 177 L121 225 L79 225Z" fill="#ffffff"/><path d="M89 188 l11 12 l11 -12" fill="none" stroke="#94a3b8" stroke-width="3"/>',
        "Professionnelle": '<path d="M72 177 L100 205 L128 177 L121 225 L79 225Z" fill="#e2e8f0"/><path d="M91 187 L100 202 L109 187" fill="none" stroke="#64748b" stroke-width="3"/>'
    }.get(tenue, '<path d="M72 177 L100 205 L128 177 L121 225 L79 225Z" fill="#ffffff" fill-opacity=".12"/>')
    s = 0.72 if age < 4 else (0.8 if age < 8 else (0.9 if age < 14 else 1.0))
    badge_svg = f'<text x="150" y="214" font-size="25">{badge}</text>' if badge else ""
    face_svg = face + f' fill="{skin}" stroke="#9b654b" stroke-opacity=".4" stroke-width="2.2"/>'
    # layered portrait with background glow and illustrated highlights
    svg = (f'<svg viewBox="0 0 200 225" width="{taille}" role="img" aria-label="Portrait illustré du personnage" xmlns="http://www.w3.org/2000/svg">'
           f'<defs><linearGradient id="abg{taille}{univ}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{body}"/><stop offset="1" stop-color="#111827"/></linearGradient>'
           f'<radialGradient id="aface{taille}{univ}" cx="38%" cy="25%" r="80%"><stop offset="0" stop-color="#fff" stop-opacity=".26"/><stop offset=".65" stop-color="#fff" stop-opacity=".04"/><stop offset="1" stop-color="#39252a" stop-opacity=".20"/></radialGradient>'
           f'<linearGradient id="acloth{taille}{univ}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{shirt}"/><stop offset="1" stop-color="#0b1020"/></linearGradient>'
           f'<filter id="glow{taille}{univ}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="5"/></filter></defs>'
           f'<circle cx="100" cy="108" r="97" fill="url(#abg{taille}{univ})" stroke="#ffffff" stroke-opacity=".24" stroke-width="2"/>'
           f'<circle cx="100" cy="108" r="86" fill="none" stroke="#ffffff" stroke-opacity=".12" stroke-dasharray="3 7"/>'
           f'<circle cx="100" cy="105" r="59" fill="{body}" opacity=".22" filter="url(#glow{taille}{univ})"/>'
           f'<g transform="translate(100 225) scale({s}) translate(-100 -225)">'
           f'{back}'
           f'<path d="M19 225 Q28 169 65 166 L82 161 L100 178 L118 161 L135 166 Q172 169 181 225Z" fill="url(#acloth{taille}{univ})" stroke="#ffffff" stroke-opacity=".16" stroke-width="2"/>'
           f'{outfit_details}'
           f'<path d="M78 170 L100 191 L122 170" fill="none" stroke="#ffffff" stroke-opacity=".36" stroke-width="3"/>'
           f'<rect x="83" y="145" width="34" height="35" rx="10" fill="{skin}" stroke="#9b654b" stroke-opacity=".22" stroke-width="2"/>'
           f'{ear}{face_svg}<path d="M53 107 Q58 146 83 156 Q100 164 117 156 Q142 146 147 107" fill="url(#aface{taille}{univ})"/>'
           f'<ellipse cx="64" cy="126" rx="10" ry="5" fill="#f47282" opacity=".28"/><ellipse cx="136" cy="126" rx="10" ry="5" fill="#f47282" opacity=".28"/>'
           f'<path d="M83 67 Q100 58 117 67" fill="none" stroke="#fff5e8" stroke-opacity=".38" stroke-width="4" stroke-linecap="round"/>'
           f'{wrinkles}{brows}{eyes}{nose}{mouth}{hair_front}'
           f'<path d="M54 92 Q61 80 68 78 M132 78 Q140 81 146 92" fill="none" stroke="#ffffff" stroke-opacity=".14" stroke-width="2"/>'
           f'</g><circle cx="100" cy="190" r="7" fill="#ffffff" opacity=".12"/><path d="M89 190 L100 202 L111 190" fill="none" stroke="#ffffff" stroke-opacity=".4" stroke-width="2"/>{badge_svg}'
           f'{accessoire_svg(av)}</svg>')
    return f'<div class="anime-avatar" style="text-align:center;line-height:0;max-width:100%;animation:float-avatar 4s ease-in-out infinite">{svg}</div>'


# ======================================================================
#  CRÉATION / ÉTAT DU JEU
# ======================================================================
def defauts():
    return {"id": uuid.uuid4().hex[:8], "nom": "Alex", "genre": "Non-binaire", "univers": "real", "ville": "Paris",
            "avatar": {"coupe": "Court", "couleur": "Noir", "peau": "Beige", "yeux": "Ronds", "bouche": "Sourire", "accessoire": "Aucun", "tenue": "Classique", "iris": "Marron"},
            "age": 0, "annee_naissance": datetime.now().year, "attirance": "Je préfère ne pas préciser", "origine_familiale": "", "statut_parents": "", "argent": 0, "edu": 0, "notes": 50, "domaine": "",
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


def new_game(nom, genre, univers, ville, av, attirance="Je préfère ne pas préciser"):
    g = defauts()
    g.update(nom=nom.strip() or "Alex", genre=genre, univers=univers, ville=ville, avatar=av, attirance=attirance)
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
    ne = "née" if genre == "Fille" else "né" if genre == "Garçon" else "à ta naissance"
    naissance = f"Tu es {ne} à {ville}" if genre != "Non-binaire" else f"À ta naissance, tu arrives à {ville}"
    log(g, f"👶 {naissance} ({UNIVERS[univers]['nom']}), dans une famille {famille}. Trait : {g['trait']}.")
    log(g, f"👨‍👩‍👧 Tes parents sont {g['parents'][0]['nom']} ({g['parents'][0]['role']}, {g['parents'][0]['personnalite'].lower()}) et {g['parents'][1]['nom']} ({g['parents'][1]['role']}, {g['parents'][1]['personnalite'].lower()}).")
    if g.get("fratrie"):
        log(g, "🧑‍🤝‍🧑 Tu as aussi " + ", ".join(f"{x['nom']} ({x['age']} ans)" for x in g["fratrie"]) + ".")
    if univers == "manga":
        if g.get("saga_manga") == "naruto":
            village = ville.split(" 🍃")[0].split(" 🏜️")[0].split(" 🌫️")[0].split(" ⚡")[0].split(" 🪨")[0].split(" 🌧️")[0].split(" 🎵")[0]
            g["origine_familiale"] = random.choice(["une famille de shinobi ordinaires", "une famille de civils du village", "une lignée connue du village", "une famille de shinobi récemment endeuillée"])
            special = random.choices(["Deux genin prometteurs", "Un jōnin respecté et une kunoichi", "Un chūnin et une civile", "Une famille liée au clan " + g.get("clan", "Sans clan"), "Un parent disparu en mission", "Une famille de shinobi sans renom"], [22,16,15,16,10,21])[0]
            if special.startswith("Une famille liée"):
                g["origine_familiale"] = special
            g["statut_parents"] = special
            log(g, f"🍃 ORIGINES NINJAS — Tu es né·e à {ville}. {g['parents'][0]['nom']} et {g['parents'][1]['nom']} sont : {special.lower()}.")
            log(g, f"📜 Ton foyer : {g['origine_familiale']}. Clan enregistré : {g.get('clan', 'Sans clan')}. Ton avenir peut te mener à l’Académie, aux examens chūnin ou au cœur des conflits du village.")
            if random.random() < 0.06:
                g["statut_parents"] = "Ta famille entretient un lien secret avec le Hokage"
                g["origine_familiale"] = "une famille liée au Hokage"
                log(g, f"👑 SECRET DE NAISSANCE — Ta famille entretient un lien secret avec le Hokage. Ton identité pourrait attirer l’attention de certaines familles du village.")
        elif g.get("saga_manga") == "jujutsu":
            g["origine_familiale"] = random.choice(["une famille de civils ignorant le monde occulte", "une lignée d’exorcistes mineure", "une famille protégée par un talisman ancien", "une famille touchée par une malédiction"])
            log(g, f"👁️ ORIGINES OCCULTES — Tu es né·e à {ville}, dans {g['origine_familiale']}. Les adultes autour de toi ne comprennent pas encore ce que tu percevras peut-être un jour.")
        elif g.get("saga_manga") == "onepiece":
            g["origine_familiale"] = random.choice(["une famille de marins", "une famille de commerçants du port", "une famille de pirates recherchés", "une famille de civils prise entre la Marine et les pirates"])
            log(g, f"🏴‍☠️ ORIGINES DES MERS — Tu es né·e à {ville}, dans {g['origine_familiale']}. La Marine, les pirates et les révolutionnaires pourraient un jour croiser ta route.")
        log(g, f"🌏 Ton destin commence dans la saga {g['saga_manga'].upper()} : les rencontres et les choix pourront te faire changer de voie.")
    else:
        g["origine_familiale"] = f"une famille {famille} de {ville}"
        log(g, f"🍼 TON HISTOIRE COMMENCE — Tu es né·e à {ville}, dans {g['origine_familiale']}. Tes parents, {p1} et {p2}, ont chacun leur caractère et leurs propres espoirs pour toi.")
    log(g, f"🧬 FICHE DE NAISSANCE — Prénom : {g['nom']} · Genre : {genre} · Attirance : {g.get('attirance', 'non précisée')} · Année : {g['annee_naissance']}.")
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
    g.setdefault("boss_actuel", None)
    g.setdefault("boss_victoires", 0)
    g.setdefault("boss_echecs", 0)
    g.setdefault("frustration_heritage", 0)
    g.setdefault("personnes_capturees", [])
    g.setdefault("crimes", 0)
    g.setdefault("armures_volees", 0)
    g.setdefault("argent_vole", 0)
    g.setdefault("fruits_recuperes", [])
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
    g["avatar"].setdefault("portrait_id", 0)
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
    # Boss narratifs : rencontre rare, avec conséquences transmises à la génération suivante.
    if not g.get("boss_actuel") and a >= 8 and random.random() < 0.11:
        saga = g.get("saga_manga", "naruto") if g.get("univers") == "manga" else "real" if g.get("univers") == "real" else "fantasy"
        bosses = {
            "naruto": [("Nukenin légendaire", 62, "Un nukenin attaque ton équipe et menace ton village."), ("Chasseur de dojutsu", 78, "Un chasseur de lignées convoite les yeux de ton clan."), ("Commandant de l'Akatsuki", 88, "Un membre de l'Akatsuki se dresse sur ta route.")],
            "jujutsu": [("Fléau de classe spéciale", 72, "Un fléau de classe spéciale ravage un quartier."), ("Exorciste renégat", 80, "Un exorciste renégat veut s'emparer de ta technique.")],
            "onepiece": [("Capitaine corsaire", 70, "Un capitaine redouté bloque ta route."), ("Chasseur de primes légendaire", 82, "Un chasseur de primes veut livrer ton équipage."), ("Empereur des mers", 96, "Un Empereur des mers te considère comme une menace.")],
            "real": [("Réseau criminel", 55, "Une enquête te place face à un réseau dangereux."), ("Rival impitoyable", 48, "Un rival tente de ruiner ta carrière et ta réputation.")],
            "fantasy": [("Dragon ancien", 90, "Un dragon ancien menace la région."), ("Seigneur des ombres", 84, "Le Seigneur des ombres te défie en duel.")]
        }
        nom, puissance, desc = random.choice(bosses.get(saga, bosses["fantasy"]))
        g["boss_actuel"] = {"nom": nom, "puissance": puissance, "description": desc, "age": a}
        log(g, f"🐉 BOSS — {nom} : {desc}")
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


def actualites_annee_courante(g):
    """Retourne uniquement les actualités enregistrées pour l'âge/année actuel·le."""
    age = int(g.get("age", 0))
    return [item for item in g.get("actualites_monde", [])
            if int(item.get("age", -1)) == age]


def afficher_actualites_accueil(g):
    st.markdown("<div class='world-feed-title'>🌍 CE QUI SE PASSE DANS LE MONDE</div>", unsafe_allow_html=True)
    recentes = actualites_annee_courante(g)[-3:]
    if not recentes:
        st.caption("Aucune nouvelle marquante cette année pour le moment.")
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
                   frustration_heritage=parent.get("frustration_heritage", 0),
                   boss_victoires=parent.get("boss_victoires", 0), boss_echecs=parent.get("boss_echecs", 0),
                   parents=[{"nom": parent.get("nom", "Parent"), "role": "Parent", "age": parent.get("age", 0),
                             "relation": lien, "vivant": False, "personnalite": "Héritage familial", "confiance": lien}])
    nouveau["journal"] = parent.get("journal", [])[:] + [[enfant.get("age", 0), f"🧬 Génération {nouveau['generation']} : {nouveau['nom']} reprend le flambeau de {parent['nom']}. Lien parent-enfant : {lien}/100. Héritage : {fm(nouveau, nouveau['argent'])}."]]
    if nouveau.get("frustration_heritage", 0):
        nouveau["journal"].append([nouveau["age"], f"💢 Héritage émotionnel : un échec face à un boss hante encore la famille ({nouveau['frustration_heritage']} souvenir(s)). Tu peux tenter de réparer cet héritage."])
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
    s["c_portrait_id"] = random.choice(list(PORTRAITS_ANIME))
    s["c_couleur"] = random.choice(list(HAIR_COLORS))
    s["c_peau"] = random.choice(list(SKINS))
    s["c_yeux"] = random.choice(YEUX)
    s["c_bouche"] = random.choice(BOUCHES)
    s["c_accessoire"] = random.choice(ACCESSOIRES)
    s["c_tenue"] = random.choice(TENUES)
    s["c_iris"] = random.choice(COULEURS_YEUX)
    s["c_nom"] = random.choice(PRENOMS)
    s["c_genre"] = random.choice(["Garçon", "Fille", "Non-binaire"])


def creer_partie():
    s = st.session_state
    univ = s["c_univ"]
    av = {"coupe": s["c_coupe"], "couleur": s["c_couleur"], "peau": s["c_peau"], "yeux": s["c_yeux"], "bouche": s["c_bouche"], "accessoire": s["c_accessoire"], "tenue": s["c_tenue"], "iris": s["c_iris"], "visage": s.get("c_visage", "Manga"), "portrait_id": int(s.get("c_portrait_id", 0))}
    g = new_game(s["c_nom"], s["c_genre"], univ, s[f"c_ville_{univ}"], av, s.get("c_attirance", "Je préfère ne pas préciser"))
    g["origine_heroique"] = "Aucune"
    heritage = s.get("c_origine_speciale", "Aléatoire")
    if heritage and heritage != "Aléatoire":
        g["heritage_choisi"] = heritage
        if univ == "manga":
            if heritage == "Famille de shinobi":
                g["origine_familiale"] = "une famille de shinobi"
                g["statut_parents"] = "Deux genin prometteurs"
            elif heritage == "Clan prestigieux":
                g["origine_familiale"] = "une lignée de clan prestigieux"
            elif heritage == "Descendance secrète":
                g["origine_familiale"] = "une descendance secrète"
            elif heritage == "Famille de pirates":
                g["origine_familiale"] = "une famille de pirates"
            elif heritage == "Lignée inconnue":
                g["origine_familiale"] = "une lignée inconnue"
        else:
            g["origine_familiale"] = heritage.lower()
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
 .year-advance-wrap {display:flex; flex-direction:column; align-items:center; justify-content:center; gap:.35rem; padding:.25rem 0 .6rem;}
.year-advance-wrap div[data-testid="stButton"] button {width:76px!important;height:76px!important;min-height:76px!important;border-radius:50%!important;font-size:1.8rem!important;padding:0!important;box-shadow:0 0 0 5px rgba(56,189,248,.12),0 8px 25px rgba(0,0,0,.25)!important;}
.year-advance-label {font-size:.68rem;font-weight:800;letter-spacing:.08em;color:#a5dfff;text-align:center;}
@media(max-width:700px){.year-advance-wrap div[data-testid="stButton"] button{width:64px!important;height:64px!important;min-height:64px!important;font-size:1.5rem!important;}}

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
/* Responsive mobile layout: keep content readable and controls tappable. */
@media (max-width: 768px) {
  .block-container {padding-left:.45rem !important;padding-right:.45rem !important;max-width:100vw !important;}
  h1 {font-size:1.65rem !important;} h2 {font-size:1.35rem !important;} h3 {font-size:1.15rem !important;}
  div[data-testid="stHorizontalBlock"] {flex-wrap:wrap !important;gap:.55rem !important;}
  div[data-testid="stHorizontalBlock"] > div {min-width:min(100%, 280px) !important;flex:1 1 100% !important;width:100% !important;}
  div[data-testid="stTabs"] div[role="tablist"] {overflow-x:auto !important;flex-wrap:nowrap !important;scrollbar-width:thin;}
  div[data-testid="stTabs"] button[role="tab"] {min-width:max-content !important;font-size:.82rem !important;padding:.5rem .58rem !important;}
  .stButton>button {min-height:44px !important;width:100% !important;white-space:normal !important;}
  [data-testid="stMetric"] {padding:.45rem !important;}
  .avatar-profile-card {min-height:190px !important;padding:8px !important;}
  .avatar-art svg {max-width: min(72vw, 230px) !important;height:auto !important;}
  .world-feed-title {font-size:.95rem !important;}
  [data-testid="stVerticalBlockBorderWrapper"] {border-radius:12px !important;}
}
@media (max-width: 420px) {
  .block-container {padding-top:.5rem !important;}
  div[data-testid="stTabs"] button[role="tab"] {font-size:.76rem !important;padding:.45rem .5rem !important;}
  .stMarkdown p, .stCaption {font-size:.9rem;}
}
/* Existing mobile refinements */
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
.challenge-preview {padding:.65rem .75rem;margin:.4rem 0;border:1px solid #64748b55;border-radius:12px;background:linear-gradient(120deg,#7c3aed18,#0891b218);}
.challenge-preview span {color:#cbd5e1;font-size:.88rem;}
@media (max-width: 768px) { .challenge-preview {padding:.7rem;} .avatar-profile-card {min-height:220px;} }

/* Navigation hybride : menu compact et mise en page mobile */
@media (max-width: 700px) {
  .block-container {padding-left: .65rem !important; padding-right: .65rem !important; padding-top: .7rem !important;}
  div[data-testid="stHorizontalBlock"] {gap: .55rem; flex-wrap: wrap;}
  div[data-testid="stMetric"] {padding: .45rem .55rem;}
  div[data-testid="stButton"] button {min-height: 2.7rem; white-space: normal;}
  h1 {font-size: 1.65rem !important;} h2 {font-size: 1.35rem !important;} h3 {font-size: 1.12rem !important;}
}

/* Créateur refondu : cartes de création, aperçu vivant et galerie de coiffures */
.creation-hero{display:flex;justify-content:space-between;align-items:center;padding:22px 24px;margin:0 0 18px;border:1px solid #315a86;border-radius:20px;background:linear-gradient(115deg,#122746 0%,#172554 55%,#3b0764 100%);box-shadow:0 16px 40px #02061755}
.creation-hero h1{margin:.25rem 0;font-size:clamp(1.7rem,3vw,2.7rem);font-weight:900;letter-spacing:-.04em}.creation-hero p{margin:0;color:#cbd5e1}.eyebrow,.live-preview-label{font-size:.72rem;font-weight:900;letter-spacing:.16em;color:#67e8f9}.creation-orb{display:grid;place-items:center;width:68px;height:68px;border-radius:22px;font-size:2.4rem;color:#fef08a;background:linear-gradient(145deg,#7c3aed,#0891b2);box-shadow:0 0 36px #38bdf855}
.creation-section-title{font-weight:900;letter-spacing:.09em;color:#93c5fd;font-size:.78rem;border-bottom:1px solid #334155;padding:13px 0 8px;margin:8px 0 10px}.creation-preview{position:relative;overflow:hidden;text-align:center;padding:24px 12px 20px;border-radius:22px;border:1px solid #3b82f6;background:radial-gradient(ellipse at 50% 18%,#254a7a 0%,#15243b 50%,#0b1220 100%);box-shadow:0 18px 44px #02061777;margin:8px 0 14px}.preview-backdrop{position:absolute;left:50%;top:42px;transform:translateX(-50%);width:220px;height:220px;border-radius:50%;border:1px solid #93c5fd55;background:linear-gradient(135deg,#2563eb55,#7c3aed33);box-shadow:0 0 0 10px #60a5fa0b}.creation-preview>div:not(.preview-backdrop){position:relative;z-index:1}.creation-preview h2{margin:8px 0 0;font-size:1.8rem}.creation-preview p{color:#cbd5e1;margin:.2rem 0 .8rem}.preview-chips{display:flex;justify-content:center;flex-wrap:wrap;gap:6px}.preview-chips span{font-size:.72rem;padding:5px 9px;border:1px solid #64748b88;background:#0f172acc;border-radius:999px;color:#dbeafe}.lore-preview{padding:12px 14px;margin:8px 0;border-radius:12px;border:1px solid #334155;background:linear-gradient(110deg,#172b46,#111827);color:#cbd5e1;font-size:.9rem}.lore-preview b{color:#f8fafc}.creation-section-title+div{scroll-margin-top:12px}
@media(max-width:760px){.creation-hero{padding:16px;border-radius:15px}.creation-orb{width:48px;height:48px;font-size:1.7rem}.creation-preview{padding:14px 8px}.creation-preview svg{max-width:78vw!important;height:auto!important}.creation-hero h1{font-size:1.65rem}.creation-section-title{margin-top:14px}}


.portrait-choice img {width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:10px}
@media(max-width:760px){.creation-preview img{max-width:220px!important}.creation-preview{padding:14px!important}}
</style>
"""


def ecran_accueil():
    st.markdown("""<div class='creation-hero'><div><div class='eyebrow'>NOUVELLE PARTIE · MULTIVERS</div><h1>Crée ton personnage</h1><p>Personnalise son apparence, son histoire et son destin.</p></div><div class='creation-orb'>✦</div></div>""", unsafe_allow_html=True)
    s = st.session_state
    defaults = {"c_nom":"Alex", "c_genre":"Non-binaire", "c_univ":"real", "c_coupe":"Pointes (manga)", "c_couleur":"Noir", "c_peau":"Beige", "c_yeux":"Manga", "c_bouche":"Sourire", "c_accessoire":"Aucun", "c_tenue":"Classique", "c_iris":"Marron", "c_attirance":"Hétérosexuel·le", "c_origine_heroique":"Aucune", "c_portrait_id":0}
    for k,v in defaults.items(): s.setdefault(k,v)
    t1,t2=st.tabs(["✨ Nouvelle vie", "📂 Charger une partie"])
    with t1:
        left, right = st.columns([1.45, 1], gap="large")
        with left:
            st.markdown("<div class='creation-section-title'>01 · APPARENCE</div>",unsafe_allow_html=True)
            st.markdown("**Choisis un visage ET une coiffure illustrés**")
            st.caption("Chaque vignette est un vrai portrait dessiné. En la sélectionnant, tu changes l’illustration affichée dans la fiche de ton personnage.")
            pcols = st.columns(4)
            for pid, (pname, pdata) in PORTRAITS_ANIME.items():
                with pcols[pid % 4]:
                    selected = int(s.get("c_portrait_id", 0)) == pid
                    border_color = "#38bdf8" if selected else "#334155"
                    st.markdown(f'<div style="padding:3px;border-radius:12px;border:2px solid {border_color};background:#101a30"><img src="data:image/jpeg;base64,{pdata}" alt="Portrait {pname}" style="width:100%;aspect-ratio:1/1;object-fit:cover;object-position:center 28%;border-radius:8px"/><div style="font-size:12px;text-align:center;padding:4px;color:#e5edf9">{pname}</div></div>', unsafe_allow_html=True)
                    if st.button("✓ Sélectionné" if selected else "Choisir", key=f"portrait_pick_{pid}", use_container_width=True):
                        st.session_state["c_portrait_id"] = pid
                        st.rerun()
            a1,a2=st.columns(2)
            with a1:
                st.selectbox("Couleur des cheveux (fiche)", list(HAIR_COLORS), key="c_couleur")
                st.selectbox("Teint (fiche)", list(SKINS), key="c_peau")
            with a2:
                st.selectbox("Couleur des yeux (fiche)", COULEURS_YEUX, key="c_iris")
                st.selectbox("Tenue de départ", TENUES, key="c_tenue")
            st.caption("Le portrait illustré correspond au visage et à la coiffure choisis. Les autres options décrivent le personnage dans sa fiche.")
            st.markdown("<div class='creation-section-title'>02 · IDENTITÉ</div>",unsafe_allow_html=True)
            st.text_input("Prénom",key="c_nom")
            st.radio("Genre",["Garçon","Fille","Non-binaire"],key="c_genre",horizontal=True)
            st.selectbox("Attirance",["Hétérosexuel·le","Homosexuel·le","Bisexuel·le","Pansexuel·le","Asexuel·le","En questionnement","Je préfère ne pas préciser"],key="c_attirance")
            st.markdown("<div class='creation-section-title'>03 · ORIGINE</div>",unsafe_allow_html=True)
            st.selectbox("Univers",list(UNIVERS),key="c_univ",format_func=lambda k:UNIVERS[k]["nom"])
            univ=s["c_univ"]
            st.caption(UNIVERS[univ]["desc"])
            villes=list(UNIVERS[univ]["villes"])
            st.selectbox("Lieu de naissance",villes,key=f"c_ville_{univ}",format_func=lambda v:f"{v} — {UNIVERS[univ]['villes'][v]['desc']}")
            if univ == "manga":
                st.selectbox("Héritage / origine spéciale",["Aléatoire", "Aucune", "Famille de shinobi", "Clan prestigieux", "Descendance secrète", "Famille de pirates", "Lignée inconnue"],key="c_origine_speciale")
            else:
                st.selectbox("Origine familiale",["Aléatoire", "Famille modeste", "Classe moyenne", "Famille aisée", "Famille célèbre", "Origines mystérieuses", "Héritage exceptionnel"],key="c_origine_speciale")
            st.markdown("<div class='creation-section-title'>04 · PERSONNALITÉ</div>",unsafe_allow_html=True)
            st.info("🎲 Ton trait inné sera tiré au sort à la naissance. Tu le découvriras dans ton histoire : pas besoin de tout choisir avant de commencer.")
            st.selectbox("Accessoire",ACCESSOIRES,key="c_accessoire")
            st.info("🧬 Les pouvoirs et les grands destins se découvrent au fil des événements, des rencontres et des décisions.")
        with right:
            av={"coupe":s["c_coupe"],"couleur":s["c_couleur"],"peau":s["c_peau"],"yeux":s["c_yeux"],"bouche":s["c_bouche"],"accessoire":s["c_accessoire"],"tenue":s["c_tenue"],"iris":s["c_iris"],"visage":s.get("c_visage","Manga"),"portrait_id":int(s.get("c_portrait_id",0))}
            st.markdown("<div class='live-preview-label'>APERÇU EN DIRECT</div>",unsafe_allow_html=True)
            st.markdown(f"<div class='creation-preview'><div class='preview-backdrop'></div>{portrait_anime_html(av, 300)}<h2>{s['c_nom'] or 'Alex'}</h2><p>{UNIVERS[s['c_univ']]['nom']} · {s['c_genre']}</p><div class='preview-chips'><span>{PORTRAITS_ANIME[int(s.get('c_portrait_id',0)) % len(PORTRAITS_ANIME)][0]}</span><span>{s['c_tenue']}</span><span>{s['c_iris']} · yeux</span></div></div>",unsafe_allow_html=True)
            if st.button("🎲 Générer une apparence",on_click=randomiser,use_container_width=True): pass
            st.markdown("<div class='creation-section-title'>TON HISTOIRE COMMENCE ICI</div>",unsafe_allow_html=True)
            st.markdown("<div class='lore-preview'>👶 <b>Naissance</b><br>Ton origine, ta famille et ton trait inné façonneront tes premières années.</div><div class='lore-preview'>🌍 <b>Un monde vivant</b><br>Les événements importants pourront changer ton destin et celui de tes descendants.</div><div class='lore-preview'>🏆 <b>Des défis à relever</b><br>Chaque génération pourra laisser une trace dans l'histoire familiale.</div>",unsafe_allow_html=True)
        st.button("🚀 Commencer ma vie",on_click=creer_partie,type="primary",use_container_width=True)
    with t2:
        saves=lister_saves()
        if not saves: st.info("Aucune sauvegarde sur le disque. Tu peux aussi importer un fichier .json exporté.")
        for p,d in saves:
            j=JOBS.get(d.get("metier") or "",None)
            c1,c2,c3=st.columns([4,1,1])
            c1.markdown(f"**{d.get('nom','?')}** — {d.get('age',0)} ans — {UNIVERS.get(d.get('univers'),{}).get('nom','?')} — {(j['nom'] if j else '—')} {'💀' if not d.get('vivant',True) else ''}  \n<small>Dernière sauvegarde : {d.get('maj','?')}</small>",unsafe_allow_html=True)
            c2.button("▶️ Charger",key=f"ld_{p.name}",on_click=charger_slot,args=(str(p),))
            c3.button("🗑️",key=f"rm_{p.name}",on_click=supprimer_slot,args=(str(p),))
        st.divider(); st.file_uploader("Importer une sauvegarde (.json)",type="json",key="upl"); st.button("📥 Charger ce fichier",on_click=charger_upload)
    if s.get("flash"): st.error(s["flash"])


def panneau_perso(g):
    j = JOBS.get(g["metier"]) if g["metier"] else None
    avatar = portrait_anime_html(g.get("avatar", {}), 220)
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
        # En non-binaire, privilégier les tournures neutres quand elles sont fréquentes,
        # et conserver l'inclusif pour les mots où une reformulation n'est pas sûre.
        neutres = {
            "né·e": "né·e", "né.e": "né·e", "seul·e": "sans compagnie", "seul.e": "sans compagnie",
            "blessé·e": "blessé·e", "blessé.e": "blessé·e", "prêt·e": "prêt·e", "prêt.e": "prêt·e",
            "méchant·e": "malveillant·e", "méchant.e": "malveillant·e", "fatigué·e": "fatigué·e", "fatigué.e": "fatigué·e",
            "heureux·se": "heureux·se", "heureux.se": "heureux·se", "inquiet·ète": "inquiet·ète", "inquiet.e": "inquiet·ète",
            "athlète né·e": "athlète de naissance", "athlète né.e": "athlète de naissance",
            "courageux·se": "courageux·se", "courageux.se": "courageux·se", "ambitieux·se": "ambitieux·se", "ambitieux.se": "ambitieux·se",
            "ami·e": "personne amie", "ami.e": "personne amie", "ennemi·e": "personne ennemie", "ennemi.e": "personne ennemie",
            "Tu es né·e": "À ta naissance", "Tu es né.e": "À ta naissance",
        }
        for source, cible in sorted(neutres.items(), key=lambda item: len(item[0]), reverse=True):
            texte = texte.replace(source, cible)
        return texte
    # Remplacements courants + variantes .e et ·e ; les plus longues d'abord.
    for source, cible in sorted(remplacements.items(), key=lambda item: len(item[0]), reverse=True):
        texte = texte.replace(source, cible)
    # Gérer aussi les variantes courantes non présentes dans le dictionnaire historique.
    extra = {
        "Garçon": {"athlète né·e":"athlète né", "athlète né.e":"athlète né", "curieux·se":"curieux", "curieux.se":"curieux", "ambitieux·se":"ambitieux", "ambitieux.se":"ambitieux", "chanceux·se":"chanceux", "chanceux.se":"chanceux", "courageux·se":"courageux", "courageux.se":"courageux", "né·e":"né", "né.e":"né", "mort·e":"mort", "mort.e":"mort", "retraité·e":"retraité", "retraité.e":"retraité"},
        "Fille": {"athlète né·e":"athlète née", "athlète né.e":"athlète née", "curieux·se":"curieuse", "curieux.se":"curieuse", "ambitieux·se":"ambitieuse", "ambitieux.se":"ambitieuse", "chanceux·se":"chanceuse", "chanceux.se":"chanceuse", "courageux·se":"courageuse", "courageux.se":"courageuse", "né·e":"née", "né.e":"née", "mort·e":"morte", "mort.e":"morte", "retraité·e":"retraitée", "retraité.e":"retraitée"}
    }
    for source, cible in sorted(extra.get(genre, {}).items(), key=lambda item: len(item[0]), reverse=True):
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



def action_crime(g, action, cible="Rival inconnu"):
    """Actions fictives de jeu : conséquences claires, sans détail opérationnel réel."""
    if g.get("age", 0) < 12:
        raise Refus("Tu es trop jeune pour entreprendre cette action dans l'histoire.")
    g.setdefault("crimes", 0)
    if action == "capturer":
        if g.get("univers") != "manga" or g.get("saga_manga") not in ("naruto", "jujutsu", "onepiece"):
            raise Refus("La capture de personnages est disponible dans les univers d'aventure.")
        if g.get("stats", {}).get("force", 0) + g.get("stats", {}).get("intelligence", 0) < 70:
            raise Refus("Ta force et ta stratégie sont insuffisantes : entraîne-toi avant de tenter une capture.")
        personne = random.choice(["éclaireur rival", "mercenaire", "informateur", "combattant adverse"])
        g.setdefault("personnes_capturees", []).append({"nom": personne, "age": g["age"], "cible": cible})
        g["crimes"] += 1; g["stats"]["karma"] = clamp(g["stats"].get("karma",50)-8)
        log(g, f"⛓️ Tu as capturé {personne}. Cela pourrait déclencher une riposte.")
        return f"⛓️ {personne.capitalize()} capturé·e. Les factions adverses s'en souviendront."
    if action == "depouiller":
        if g.get("univers") == "manga" and g.get("saga_manga") == "naruto":
            butin = random.choice(["parchemin rare", "équipement ninja", "armure légère"])
            g["inventaire_objets"].append({"id":"butin_"+str(random.randint(10000,99999)),"nom":butin,"rarete":"B","type":"équipement","prix_achat":0})
            g["armures_volees"] = g.get("armures_volees",0) + (1 if "armure" in butin else 0)
        else:
            butin = random.choice(["arme", "armure", "sac de pièces"])
            if butin == "sac de pièces":
                gain = random.randint(250, 2500); g["argent"] = g.get("argent",0)+gain; g["argent_vole"] = g.get("argent_vole",0)+gain
            else:
                g["inventaire_objets"].append({"id":"butin_"+str(random.randint(10000,99999)),"nom":butin.capitalize()+" récupérée", "rarete":"B","type":"équipement","prix_achat":0})
        g["crimes"] += 1; g["stats"]["karma"] = clamp(g["stats"].get("karma",50)-10); g["reputation"] = max(0,g.get("reputation",50)-5)
        log(g, f"🗡️ Tu as dépouillé un adversaire et récupéré : {butin}.")
        return f"🗡️ Butin récupéré : {butin}. Ta réputation baisse et une riposte est possible."
    if action == "yeux":
        if not (g.get("univers") == "manga" and g.get("saga_manga") == "naruto"):
            raise Refus("Cette action est propre à l'univers Naruto.")
        if g.get("stats",{}).get("karma",50) > 35 and not g.get("akatsuki"):
            raise Refus("Cette voie sombre exige un choix moral majeur ou une affiliation criminelle.")
        g["sharingans_voles"] = g.get("sharingans_voles",0)+1
        g["chakra"] = clamp(g.get("chakra",50)+8); g["crimes"] += 1; g["stats"]["karma"] = clamp(g["stats"].get("karma",50)-18)
        g.setdefault("secrets",[]).append("A volé un dōjutsu — secret dangereux")
        log(g,"👁️ Tu as obtenu un dōjutsu volé. Le clan de la victime pourrait chercher vengeance.")
        return "👁️ Dōjutsu récupéré. Tu gagnes en puissance, mais tu risques une vendetta."
    if action == "cellules":
        if not (g.get("univers") == "manga" and g.get("saga_manga") == "naruto"):
            raise Refus("Le vol de cellules Senju est propre à l'univers Naruto.")
        g["cellules_senju"] = g.get("cellules_senju",0)+1; g["chakra"] = clamp(g.get("chakra",50)+12); g["crimes"] += 1
        g["stats"]["karma"] = clamp(g["stats"].get("karma",50)-16); g.setdefault("secrets",[]).append("Cellules Senju implantées")
        log(g,"🧬 Des cellules Senju ont été implantées. Leur maîtrise et leurs conséquences restent incertaines.")
        return "🧬 Cellules Senju obtenues : chakra renforcé, mais risque de rejet et d'enquête."
    if action == "fruit":
        if not (g.get("univers") == "manga" and g.get("saga_manga") == "onepiece"):
            raise Refus("La récupération d'un fruit du démon est propre à One Piece.")
        if g.get("fruit_demon"):
            raise Refus("Tu possèdes déjà un fruit du démon : tu ne peux pas en récupérer un autre.")
        fruit = random.choice(["Gomu Gomu no Mi", "Mera Mera no Mi", "Bara Bara no Mi", "Suna Suna no Mi", "Hie Hie no Mi"])
        g["fruit_demon"] = fruit; g.setdefault("fruits_recuperes",[]).append(fruit); g["crimes"] += 1
        g["stats"]["karma"] = clamp(g["stats"].get("karma",50)-15)
        log(g,f"🍈 Tu as récupéré le fruit du démon {fruit}. Des rivaux convoitent désormais ton pouvoir.")
        return f"🍈 Fruit récupéré : {fruit}. Tu ne peux plus nager et tu attires les convoitises."
    raise Refus("Action inconnue.")


def combattre_boss(g, strategie):
    boss = g.get("boss_actuel")
    if not boss: raise Refus("Aucun boss ne t'attend pour le moment.")
    stats = g.get("stats",{})
    puissance_joueur = stats.get("force",50)*.45 + stats.get("intelligence",50)*.25 + stats.get("sante",50)*.20 + stats.get("apparence",50)*.10
    bonus = {"prudente": 8, "agressive": 2, "tactique": 12}.get(strategie,0)
    if g.get("univers")=="manga": puissance_joueur += g.get("chakra",g.get("energie_occulte",0))*.12 + len(g.get("jutsu",[]))*1.4
    if strategie == "tactique": puissance_joueur += stats.get("intelligence",50)*.08
    score = puissance_joueur + bonus + random.randint(-18,18)
    if score >= boss["puissance"]:
        g["boss_victoires"] = g.get("boss_victoires",0)+1; g["stats"]["bonheur"] = clamp(stats.get("bonheur",50)+16); g["stats"]["celebrite"] = clamp(stats.get("celebrite",0)+8)
        if g.get("univers")=="manga" and g.get("saga_manga")=="onepiece": g["notoriete_manga"] = clamp(g.get("notoriete_manga",0)+15)
        log(g,f"🏆 VICTOIRE — Tu as vaincu {boss['nom']}. Cette réussite devient un héritage familial.")
        msg=f"🏆 Tu vaincs {boss['nom']} ! Bonheur et réputation progressent."
    else:
        g["boss_echecs"] = g.get("boss_echecs",0)+1; g["frustration_heritage"] = g.get("frustration_heritage",0)+1
        g["stats"]["sante"] = clamp(stats.get("sante",50)-random.randint(8,18)); g["stats"]["bonheur"] = clamp(stats.get("bonheur",50)-12)
        for enfant in g.get("enfants",[]): enfant["relation"] = max(0,enfant.get("relation",50)-5)
        log(g,f"💢 DÉFAITE — {boss['nom']} t'a vaincu. Cette humiliation marque ta famille ; l'enfant qui prendra la relève pourra hériter d'une frustration à surmonter.")
        msg=f"💢 Tu échoues face à {boss['nom']}. Blessures, baisse de moral et frustration transmise à la génération suivante."
    g["boss_actuel"] = None
    return msg


def tab_crimes_boss(g):
    st.markdown("## ⚔️ Confrontations, captures et choix sombres")
    st.caption("Ces actions sont des mécaniques fictives de simulation. Elles peuvent rapporter du butin, mais créent des ennemis, font baisser le karma et peuvent laisser des conséquences familiales.")
    boss = g.get("boss_actuel")
    if boss:
        st.error(f"### 🐉 {boss['nom']} — niveau de menace {boss['puissance']}/100\n\n{boss['description']}")
        c1,c2,c3 = st.columns(3)
        for col, strategie, label in [(c1,"prudente","🛡️ Défense prudente"),(c2,"tactique","🧠 Stratégie"),(c3,"agressive","⚔️ Assaut direct")]:
            with col:
                if st.button(label,key="boss_"+strategie,use_container_width=True):
                    try: flash(combattre_boss(g,strategie))
                    except Refus as e: flash(str(e))
                    if st.session_state.get("autosave"): sauver(g)
                    st.rerun()
    else:
        st.info("Aucun boss actif. Les confrontations majeures apparaissent parfois en avançant dans les années.")
    st.markdown("### 🎯 Actions disponibles")
    if g.get("age",0) < 12:
        st.warning("Ces actions se débloquent à partir de 12 ans dans l'histoire.")
        return
    univers = g.get("univers")
    saga = g.get("saga_manga")
    options = [("capturer","⛓️ Capturer un adversaire"),("depouiller","🗡️ Dépouiller un adversaire")]
    if univers == "manga" and saga == "naruto": options += [("yeux","👁️ Voler un dōjutsu"),("cellules","🧬 Récupérer des cellules Senju")]
    if univers == "manga" and saga == "onepiece": options += [("fruit","🍈 Tenter de récupérer un fruit du démon")]
    cibles = st.selectbox("Cible / contexte", ["Rival inconnu","Éclaireur d'une faction ennemie","Adversaire blessé après un combat","Garde d'un convoi"], key="crime_cible")
    choix = st.selectbox("Action", options, format_func=lambda x:x[1], key="crime_action")
    if st.button("⚠️ Tenter l'action", type="primary", key="crime_go", use_container_width=True):
        try: flash(action_crime(g,choix[0],cibles))
        except Refus as e: flash(str(e))
        if st.session_state.get("autosave"): sauver(g)
        st.rerun()
    st.markdown("### 📚 Conséquences à long terme")
    st.write(f"Captures : {len(g.get('personnes_capturees',[]))} · Crimes : {g.get('crimes',0)} · Boss vaincus : {g.get('boss_victoires',0)} · Échecs : {g.get('boss_echecs',0)}")
    if g.get("frustration_heritage",0): st.warning(f"💢 Frustration familiale héritée : {g['frustration_heritage']}. La prochaine génération pourra chercher à dépasser cet échec.")
    if g.get("personnes_capturees"):
        with st.expander("Personnes capturées"):
            for p in g["personnes_capturees"]: st.write(f"• {p['nom']} — capturé·e à {p['age']} ans ({p['cible']})")


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
        st.markdown(f'''<div style="padding:18px 20px;border:1px solid #38bdf855;border-left:5px solid #38bdf8;border-radius:14px;background:linear-gradient(120deg,#0c4a6e66,#17255499);margin:8px 0 16px"><div style="font-size:1.15rem;font-weight:850;letter-spacing:.04em">🍼 TON HISTOIRE COMMENCE</div><p style="margin:.55rem 0">Tu es né·e en {g.get('annee_naissance', datetime.now().year)} à <b>{g.get('ville','?')}</b>, dans {g.get('origine_familiale') or ('une famille ' + g.get('famille','classe moyenne'))}.</p><p style="margin:.35rem 0">👨‍👩‍👧 Parents : <b>{' et '.join(p.get('nom','?') for p in g.get('parents',[]))}</b>. {g.get('statut_parents') or 'Ils vont façonner tes premières années.'}</p><p style="margin:.35rem 0">🧬 Genre : {g.get('genre','Non-binaire')} · Attirance : {g.get('attirance','non précisée')} · Trait inné : {g.get('trait','à découvrir')}.</p><p style="margin:.35rem 0">🎲 Ton histoire n’est pas écrite : les événements et tes choix détermineront la suite.</p></div>''' , unsafe_allow_html=True)
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



def tab_apercu(g):
    """Tableau de bord narratif inspiré de la maquette, utilisable sur mobile."""
    st.markdown("## ✨ Le fil de ta vie")
    st.caption("Les informations importantes de ton personnage, réunies au même endroit.")
    left, right = st.columns([1, 1.65], gap="medium")
    with left:
        j = JOBS.get(g.get("metier") or "")
        avatar = portrait_anime_html(g.get("avatar", {}), 260)
        st.markdown(f"<div class='avatar-profile-card'><div class='avatar-halo'></div><div class='avatar-art'>{avatar}</div><div class='avatar-status'><span></span>{'EN VIE' if g.get('vivant', True) else 'FIN DE VIE'} · {g.get('age', 0)} ANS</div></div>", unsafe_allow_html=True)
        st.markdown(f"### {g.get('nom','Alex')}")
        st.caption(f"{g.get('age',0)} ans · {g.get('genre','')} · {UNIVERS.get(g.get('univers'),{}).get('nom',g.get('univers',''))}")
        st.caption(f"💗 Attirance : {g.get('attirance','Non précisée')}")
        st.markdown(f"**{titre_metier(g)}**")
        stats = g.get('stats', {})
        cols = st.columns(2)
        for idx, (key, label, emoji) in enumerate([('sante','Santé','❤️'),('bonheur','Bonheur','✨'),('intelligence','Intelligence','🧠'),('force','Force','⚡')]):
            with cols[idx % 2]:
                val = int(stats.get(key, 0))
                st.progress(max(0,min(100,val))/100, text=f"{emoji} {label} · {val}/100")
        st.metric("🪙 Jetons", g.get('jetons', 0))
    with right:
        # La fiche détaillée de naissance n'est affichée que durant l'année 0 ; elle reste ensuite dans le Journal de vie.
        parents = g.get('parents', [])
        parent_names = ' et '.join(str(x.get('nom','?')) for x in parents) if parents else 'une famille dont les détails restent inconnus'
        origin = g.get('origine_familiale') or ('une famille ' + str(g.get('famille','classe moyenne')))
        trait = accord_genre_texte(g.get('trait') or 'un trait encore à découvrir', g)
        birth = (f"Tu es née à **{g.get('ville','?')}**" if g.get("genre") == "Fille" else f"Tu es né à **{g.get('ville','?')}**" if g.get("genre") == "Garçon" else f"À ta naissance, tu arrives à **{g.get('ville','?')}**") + f", dans {origin}. Tes parents sont **{parent_names}**."
        if g.get('statut_parents'):
            birth += f" {g['statut_parents']}."
        birth += f" Ton trait inné est **{trait}**. Cette origine peut influencer tes opportunités, tes relations et les événements à venir."
        if int(g.get('age', 0)) == 0:
            st.markdown("### 🍼 Histoire de ta naissance")
            st.info(birth)
        if g.get('univers') == 'manga' and int(g.get('age', 0)) == 0:
            saga = g.get('saga_manga','naruto')
            if saga == 'naruto':
                st.caption(f"🍃 Clan : {g.get('clan') or 'sans clan connu'} · Rang : {g.get('rang_ninja','Aspirant')} · Chakra : {g.get('chakra',50)}/100")
            elif saga == 'onepiece':
                st.caption(f"🏴‍☠️ Faction : {g.get('faction_manga','Indépendant·e')} · Notoriété : {g.get('notoriete_manga',0)} · Fruit du démon : {g.get('fruit_demon') or 'aucun'}")
            elif saga == 'jujutsu':
                st.caption(f"👁️ Énergie occulte : {g.get('energie_occulte',0)} · Techniques : {', '.join(g.get('techniques_maudites',[])) or 'à découvrir'}")
        st.markdown("### 👨‍👩‍👧‍👦 Famille & entourage")
        st.progress(max(0,min(100,int(g.get('famille_relations',65))))/100, text=f"Lien familial · {g.get('famille_relations',65)}/100")
        if parents:
            pc = st.columns(min(2,len(parents)))
            for i, parent in enumerate(parents[:2]):
                with pc[i]:
                    st.markdown(f"**{'👩' if parent.get('role') == 'Mère' else '👨'} {parent.get('nom','?')}** · {parent.get('role','Parent')}")
                    st.caption(f"{parent.get('age','?')} ans · {parent.get('personnalite','Personnalité inconnue')}")
                    st.progress(max(0,min(100,int(parent.get('relation',65))))/100, text=f"Lien · {parent.get('relation',65)}/100")
        if g.get('fratrie'):
            st.caption("🧑‍🤝‍🧑 Fratrie : " + ' · '.join(f"{x.get('nom','?')} ({x.get('age',0)} ans)" for x in g['fratrie'][:5]))
        elif not parents:
            st.caption("Les détails familiaux seront affichés ici lorsqu’ils seront disponibles.")
        st.markdown("### ⚡ Actions rapides")
        st.caption("Ouvre seulement la rubrique dont tu as besoin. Les menus restent sur cette page.")
        with st.expander("🏃 Sport, santé & vie quotidienne"):
            q1, q2, q3 = st.columns(3)
            with q1: btn("🏋️ Salle de sport", "gym", "home_quick_gym")
            with q2: btn(ENTRAINEMENTS[g.get("univers", "real")][0], "entrainement", "home_quick_training")
            with q3: btn("🩺 Médecin (150)", "medecin_visite", "home_quick_doc")
            q4, q5, q6 = st.columns(3)
            with q4: btn("📖 Lire", "lire", "home_quick_read")
            with q5: btn("🧘 Méditer", "meditation", "home_quick_meditate")
            with q6: btn("🎉 Sortir", "fete", "home_quick_party")
        with st.expander("🎓 Études"):
            tab_etudes(g)
        with st.expander("💼 Carrière & missions"):
            tab_carriere(g)
        with st.expander("❤️ Amour & famille"):
            tab_amour(g)
            st.markdown("**Entretenir les liens**")
            r1, r2 = st.columns(2)
            with r1: btn("☕ Voir un parent", "temps_parents", "home_quick_parent", disabled=not any(x.get("vivant", True) for x in g.get("parents", [])))
            with r2: btn("🎮 Voir la fratrie", "temps_fratrie", "home_quick_sibling", disabled=not bool(g.get("fratrie")))
        with st.expander("💰 Argent & risques"):
            tab_argent(g)
        with st.expander("🧭 Vie personnelle & déménagement"):
            tab_perso(g)
    # Bouton de progression placé après les actions rapides pour éviter de remonter en haut.
    st.markdown("""<style>
    div[data-testid="stButton"] button[kind="primary"]#advance_year_circle {border-radius:999px!important;min-height:76px!important;width:76px!important;height:76px!important;font-size:1.55rem!important;background:linear-gradient(135deg,#7c3aed,#0891b2)!important;border:2px solid #7dd3fc!important;box-shadow:0 0 24px #38bdf855!important;margin:auto!important;display:block!important}
    .year-advance-label{text-align:center;color:#cbd5e1;font-weight:850;font-size:.72rem;letter-spacing:.08em;margin-top:5px}
    </style>""", unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,1,1])
    with c2:
        st.button("⏭", key="advance_year_circle", on_click=next_year, type="primary", disabled=not g.get("vivant", True), help="Passer à l’année suivante")
        st.markdown("<div class='year-advance-label'>PASSER L’ANNÉE</div>", unsafe_allow_html=True)
    st.markdown("### 🌍 Ce qui se passe dans le monde")
    # L'accueil ne montre que les nouvelles de l'année actuelle, jamais les anciennes.
    news = actualites_annee_courante(g)[-3:]
    if news:
        ncols = st.columns(min(3,len(news)))
        for i, item in enumerate(reversed(news)):
            with ncols[i]:
                with st.container(border=True):
                    st.caption(f"{'📰 Information' if item.get('type') == 'information' else '🌍 Événement'} · À {item.get('age',g.get('age',0))} ans")
                    st.markdown(f"**{item.get('titre','Actualité')}**")
                    st.write(item.get('texte',''))
    else:
        st.info("Aucune actualité pour cette année. Passe l’année pour découvrir les nouvelles suivantes.")
    st.caption("📖 Le récapitulatif complet de ta vie est disponible dans **Journal de vie**.")


def ecran_jeu(g):
    """Accueil narratif façon BitLife + menu hamburger pour les autres rubriques."""
    sidebar(g)
    st.session_state.setdefault("nav_page", "🏠 Ma vie")
    st.session_state.setdefault("menu_open_hint", False)

    # Barre compacte : menu des sections, identité et année en cours.
    head1, head2, head3 = st.columns([1.1, 2.2, 1.2])
    with head1:
        with st.popover("☰ Menu", use_container_width=True):
            st.caption("Choisis une rubrique")
            pages = [
                "🏠 Ma vie", "🎯 Actions", "🎓 Études", "💼 Carrière & missions",
                "❤️ Amour & famille", "💰 Argent & risques", "🌌 Univers & pouvoirs",
                "⚔️ Crimes & boss", "🎒 Inventaire & marché", "🌍 Actualités du monde",
                "🏅 Défis & boutique", "👥 Relations", "📖 Journal de vie", "🪪 Profil & statistiques"
            ]
            for page in pages:
                if st.button(page, key="nav_" + page, use_container_width=True,
                             type="primary" if st.session_state.get("nav_page") == page else "secondary"):
                    st.session_state["nav_page"] = page
                    st.rerun()
    with head2:
        st.markdown(f"### 🧬 {g.get('nom','Alex')} · {g.get('age',0)} ans")
        st.caption(f"{UNIVERS.get(g.get('univers'),{}).get('nom',g.get('univers',''))} · {titre_metier(g)}")
    with head3:
        st.metric("🪙 Jetons", g.get("jetons", 0))
    st.divider()

    page = st.session_state.get("nav_page", "🏠 Ma vie")
    msg = st.session_state.get("flash")
    if msg:
        afficher_effet_action(msg)

    if page == "🏠 Ma vie":
        # Priorité visuelle aux événements qui attendent une décision, comme BitLife.
        if not g.get("vivant", True):
            bloc_mort(g)
        elif g.get("evt"):
            st.markdown("## 🔔 Un événement demande ton attention")
            st.caption("Choisis une réponse pour poursuivre ton histoire.")
            bloc_evenement(g)
        else:
            st.markdown("## 📅 Une nouvelle année t'attend")
            st.caption("Tes décisions façonnent ta vie. Les événements importants apparaîtront ici en priorité.")
            st.metric("⏳ Temps libre cette année", f"{g.get('actions',0)}/{ACTIONS_PAR_AN}")
        # La page d'accueil réunit les panneaux demandés : avatar, naissance, famille, défis et actualités.
        tab_apercu(g)
        st.markdown(f"### 🗓️ Récapitulatif de l’année — {g.get('age', 0)} an{'s' if g.get('age', 0) != 1 else ''}")
        # Only show events from the current age/year. The full timeline lives in Journal de vie.
        recap = [(age, txt) for age, txt in g.get("journal", []) if age == g.get("age", 0)]
        if recap:
            for age, txt in reversed(recap[-5:]):
                with st.container(border=True):
                    st.write(txt)
        else:
            st.info("Aucun événement marquant enregistré pour cette année. Tu peux faire une action ou passer à l’année suivante.")
        with st.expander("📖 Ouvrir le journal de vie complet"):
            tab_journal(g)
    elif page == "🎯 Actions":
        if not g.get("vivant", True):
            bloc_mort(g)
        elif g.get("prison", 0) > 0:
            tab_prison(g)
        else:
            sous = st.tabs(["🎓 Études", "💼 Carrière", "🏃 Vie perso", "❤️ Amour", "💰 Argent"])
            with sous[0]: tab_etudes(g)
            with sous[1]: tab_carriere(g)
            with sous[2]: tab_perso(g)
            with sous[3]: tab_amour(g)
            with sous[4]: tab_argent(g)
    elif page == "🎓 Études": tab_etudes(g)
    elif page == "💼 Carrière & missions": tab_carriere(g)
    elif page == "❤️ Amour & famille": tab_amour(g)
    elif page == "💰 Argent & risques": tab_argent(g)
    elif page == "🌌 Univers & pouvoirs": tab_univers_specifique(g)
    elif page == "⚔️ Crimes & boss": tab_crimes_boss(g)
    elif page == "🎒 Inventaire & marché": tab_inventaire_marche(g)
    elif page == "🌍 Actualités du monde": tab_actualites(g)
    elif page == "🏅 Défis & boutique": tab_defis_boutique(g)
    elif page == "👥 Relations": tab_relations(g)
    elif page == "📖 Journal de vie": tab_journal(g)
    elif page == "🪪 Profil & statistiques": tab_profil(g)


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
