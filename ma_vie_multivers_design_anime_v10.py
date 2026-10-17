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
    2: ('Ivoire', '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'),
    3: ('Minuit', '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'),
    4: ('Flamme', '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'),
    5: ('Ombre', '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'),
    6: ('Orage', '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'),
    7: ('Tresses', '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'),
    8: ('Lune', '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'),
    9: ('Rebelle', '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'),
    10: ('Éclipse', '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'),
    11: ('Sable', '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'),
}

def portrait_anime_html(av, width=300, border=True):
    """Affiche une illustration anime détaillée choisie par le joueur."""
    av = av or {}
    try: idx = int(av.get("portrait_id", 0)) % len(PORTRAITS_ANIME)
    except (TypeError, ValueError): idx = 0
    label, data = PORTRAITS_ANIME[idx]
    outline = "border:1px solid rgba(95,165,255,.55);" if border else ""
    return (f'<img src="data:image/jpeg;base64,{data}" alt="Portrait anime {label}" '
            f'style="display:block;width:min(100%,{int(width)}px);aspect-ratio:1/1;object-fit:cover;object-position:center 28%;'
            f'border-radius:18px;{outline}box-shadow:0 14px 34px rgba(0,0,0,.28);margin:0 auto;"/>')

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
            av={"coupe":s["c_coupe"],"couleur":s["c_couleur"],"peau":s["c_peau"],"yeux":s["c_yeux"],"bouche":s["c_bouche"],"accessoire":s["c_accessoire"],"tenue":s["c_tenue"],"iris":s["c_iris"],"visage":s.get("c_visage","Manga")}
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
        # Birth story remains visible after age 0 as a permanent origin card.
        st.markdown("### 🍼 Histoire de ta naissance")
        parents = g.get('parents', [])
        parent_names = ' et '.join(str(x.get('nom','?')) for x in parents) if parents else 'une famille dont les détails restent inconnus'
        origin = g.get('origine_familiale') or ('une famille ' + str(g.get('famille','classe moyenne')))
        trait = accord_genre_texte(g.get('trait') or 'un trait encore à découvrir', g)
        birth = (f"Tu es née à **{g.get('ville','?')}**" if g.get("genre") == "Fille" else f"Tu es né à **{g.get('ville','?')}**" if g.get("genre") == "Garçon" else f"À ta naissance, tu arrives à **{g.get('ville','?')}**") + f", dans {origin}. Tes parents sont **{parent_names}**."
        if g.get('statut_parents'):
            birth += f" {g['statut_parents']}."
        birth += f" Ton trait inné est **{trait}**. Cette origine peut influencer tes opportunités, tes relations et les événements à venir."
        st.info(birth)
        if g.get('univers') == 'manga':
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
    st.markdown("### 🌍 Ce qui se passe dans le monde")
    news = g.get('actualites_monde', [])[-3:]
    if news:
        ncols = st.columns(min(3,len(news)))
        for i, item in enumerate(reversed(news)):
            with ncols[i]:
                with st.container(border=True):
                    st.caption(f"{'📰 Information' if item.get('type') == 'information' else '🌍 Événement'} · À {item.get('age',g.get('age',0))} ans")
                    st.markdown(f"**{item.get('titre','Actualité')}**")
                    st.write(item.get('texte',''))
    else:
        st.info("Ton histoire commence : les actualités du monde apparaîtront ici au fil des années.")
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
            libre_col, btn_col, info_col = st.columns([1.2, 1, 1.2], gap="small")
            with libre_col:
                st.metric("⏳ Temps libre", f"{g.get('actions',0)}/{ACTIONS_PAR_AN}")
            with btn_col:
                st.markdown("<div class='year-advance-wrap'>", unsafe_allow_html=True)
                st.button("⏭", key="advance_year_circle", on_click=next_year, type="primary",
                          use_container_width=True, disabled=not g.get("vivant", True), help="Passer à l’année suivante")
                st.markdown("<div class='year-advance-label'>PASSER L’ANNÉE</div></div>", unsafe_allow_html=True)
            with info_col:
                st.caption("Une année à la fois. Les événements importants apparaissent avant de continuer.")
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
