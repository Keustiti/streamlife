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
    2: ('Neige', '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'),
    3: ('Sora', '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'),
    4: ('Akane', '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'),
    5: ('Kuro', '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'),
    6: ('Boucles', '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'),
    7: ('Tresses', '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAQDAwMDAgQDAwMEBAQFBgoGBgUFBgwICQcKDgwPDg4MDQ0PERYTDxAVEQ0NExoTFRcYGRkZDxIbHRsYHRYYGRj/2wBDAQQEBAYFBgsGBgsYEA0QGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBj/wAARCAFAAUADASIAAhEBAxEB/8QAHAAAAAcBAQAAAAAAAAAAAAAAAAECBAUGBwMI/8QAQhAAAgEDAgQEBAQEBQIFBAMAAQIDAAQRBSEGEjFBE1FhcQcUIoEyQpGhFSNSsTNiwdHhQ/AIFlOCkhckcvE0Y7L/xAAbAQABBQEBAAAAAAAAAAAAAAACAAEDBAUGB//EADQRAAICAQQBAwIEBgIBBQAAAAABAgMRBBIhMUEFE1EiYTJxscEjQoGRofAU0TMGFVLh8f/aAAwDAQACEQMRAD8A8TctDGKOj963jNCHShgUdFSEF26UMUr7CipCBjIodtqPGKPG9OITg4ocppWKOlgQkA0YGDSsUKcbIKIrvQrtbW8t3ewWcGPFnkWJM9ASep9utIc5E8i5qQ0rTI9SgNzeX8dlaZIVmGWkx1KjyHnTHiI6XaXken6daCZwg57mR2Luc9cA4HT7VX5ppI3RQ20eQiFs8o61Wt1Krntayl9yxCjjJYLpNOW68Oxa4dFJBd2A59+oB6e1Rl3qXhF4omUuNgwGB+nY0LIQmFpbgq2dgWpR0uK4bxEMm++ETYVRd0+XF9ll1p44I+TULm5gjteY8qjlAG2d+p9adx21oYwJD4svck0ylteWV1X6GR+XlY7+9OLE3dxceBbIGwD9OB0FQr7hYEzae8DK7hhCx2b/AEzTyO/t7MGFbYjA8+p9amdKiilY2t8gjLnHhuMKft51G6rplpZ6rIFmSaInClHDcp8j602cBqHGUNF1MSyMsiqFIPft5Uu0nElv8pBbF0XdpP6vU+Vc3s4eUHwSS24A2wPOnFhLBa2jQb+JzEnzbypZyJJplh4O1xOGOJo7+SBriAAxzxRtyvynup7MOopXGU6zazLqml3cU9hqLtKGiTwjzjZlkXsw/Q9RVdhthHOLq4fEjnAQHHXz/wBq0HR7mLi3gO84buLaBxp0LXNj4cQSSPl/EOcdcjPXrgVHN7HvLFSdkXX/AGKJpSW0l+wvr9bJAhKsYy/M3ZTjoD51qvCfBGk6xo7Lf8PyxMSeS7ln5GkB6FVzt+lY5cxLaTGKK7Wcd+VCDj18jVv4Yh1y/mW805hqBjIWS3mkBI8gQTuPIila5YzGWB9NsUsSjkd8X8B6hwpcCRm+YsXbEc46qeyuOx9ehqqHY4q68aX+q2VxHoFxBJY6bKqzCESCRS56kP8AmUH8vaqS5K3EkEnKsqHDDNaOg1MpQ22Pko+oaeELG6lhfHw/+gdaUBSFKggZGT09a6CtBNPoz2muwsZoAEUrAoY70sDBctDAo+tFSEDvRdTR9qLrTCD6UQA70eN6FIQnpR+tJ60r0pCBQxR4wKGKcQXTahijxigfSlgQOtGKAoDrTjB+9CjoDbenED3obChtjFE2yk4pMWDrFbzzQzSxIPDhAMkrnlRM9AT5nypOnXtvaaiNRkv4MWRWZUiBPik5HKCcbinq6sbDgprS2K+LPdzCTI84woP2BOKrq2sAhy6hz0APWqd9zg1tZbqqTXKGKXjG4eVwWdhgHPSktayvmUfmOwzua6/JhLpcM6gjmyq8xFS8dhDLDzjUIgUHTlwR9qzG/ktRi2Qqx3EKqHQFUbnALVLWupkF2DHwwoz6muL6OxbnJYhwcM3p3pr4E1tDkMPCLD8QpJjuLiSq25v1juEtoVCHZRsT9643jLpgkNvFLFJMAMn8o6nFP4tUtouZI48nl/6S/SG/2ptLKZNMeKRGdpGGJT1YjsAf70+AuMHG3W7uQknzbc2zLzb4NPdXhW81KOPltkfkDPJGnIWYjfI/2qLSK906QSMpUE/hcgq33HQ1MW+nXOo6Q+olWJ5jz8qkhD2BONvvQt47His8EnJodjNwTNqEnNz20iW6EEgkkZ3qmvFNC/j2rA+Gc5BzVytrS7n0O909CDE8QklaQkLEVOz5HfqPXNQlnp8M1gyR5jkYEc3mfXzFBB98ktsd2MLwMZpfnJIrULgsA7kb49BUro2ja5Ndy6fYmc/MR4IVinigbhfU57VFW0UsN87CVYpCOQAjJ28v0q0cNa5PputWc17M7i2nWdZD1KhhzA/bNHLOOCOtLctxM8WaRpWmW2i30lhGW1PT47p1Q/hfdHIx6jOPeq5pVylnrwe1nlsYieXx4ss6Dzx3HmKvPEljovF9jc8W8N3LeOt8wm02Qfy0RmzHyL+XPcDY57VTEOhSagG5bixnD5+XkxJFzA7rnqBntUMJfThlmyOJ5WPsXjWOX/yQ6cRRDVvEPPa3WnlQmMbSc56HOxXA9ayOPUby3vSGMayscmUoOZvua1nTuFP4vwFq2XitYbORbuGTn/lZYYdQd8L02rML/TopJ0jluFiQFiZiCwUAZ6Drvj9aajHKFq930yNr+GtzacQcPHRteu9K1EOGMenSpi5VV6sDjlbzAB5vKqH8QOGrLhnihINKuPHsLqEXFuxbJUZwVz3we9L+C1pHNxtHc3GoQLNbqWt7SQ/W74/Goxg8oz61c59O+Hmvalqdxqt7e2oS5aMTJKUFu5P1RuhBC/UMq3Rs42NPVf8A8e5y5x5Qc6f+Vp0uE/DbMfHWj9SKe65ZWuncSXdjY3y3tvE+I51GOdfUdj2NM66OuanFSXTOdsg65OMu0F0osUo9aI470WABNDej6UP702BBYodaM0MbUwhGMb0rHrRDrSqcQX9qPbrQod+lOhAoY3o/tQApxAxvR0dAj0p0hsg7Yod96GKKnwMGcKpY9ACafa6lhomjQW5t1udQuIVlmlkY4iB3AQDp5Z6neo6WSNYyrMASCMdznbpTPU5pb+5lklDI4CREsfpARQPv0qvfcoRa8ssUQzyNrm+ia6aWK3SCIAEQo7MOYjfdiST50uzuUmdEJ+psk+h8qYR2vOWLyAIDjI3yfSnEkC28QQIUnyCMHdff/aslybeWXUsEtzRQnb6pHOMD8qjzps1qLi6aUO6OfzgZFMxqLCFUkUF0YtzeeeoNTFgyi3ErsCX3z29qZ8hrklNFu0kuGs9VWMCFSxuAMrjHcdT5Yrnr2m28MsccZD2pUTREIU5gfMHcYprapBFExYytKGJZgf7VYeHrvT9Zu4tN1qxDKi8trJITzuO6kjrjqB71XknW96LUP4iVb7KYNUhtEliijPiLspxsTRqWmgguWyCuGaTrt/8AupfV9OhXX7yxt4QIopSoGM4AqM025sraSaCW3WTMbxRmQk7sRhx6jG3vUillZRXcdssM6i5tJ2KCRLgtsVPUj2pzpHE2oWUU2iWzkWNwUlniU7O6jAJ/760wntLeS5SKFAZnORy7cvqaVHaz2t2zfLq3ibhh+YjtTtJ8MSlJPKLneXOnLwNcCEzTSvMpdHHhhCdlZsfiUdh0yd6ixcJb6WJHhB5VyMDr/wA044ZnSbXbB7zwbW0Z3S4W6bAZcdN/M4xUrrem6RFcX0kWlBYYYw0QRzyzE9MDpj2qtlVy2vyXtrshvWFjgr2qrps9s94sARWUNHj8S7efmTUQtw8ls0coUsQAGHeud9Jd/KGN4ikCnCkdAfI0i61B5NJtVt4zzQRiN5ioBH+UefvVlFKUssud/wANa9pnwlfirSLu3fT7rlt7yOCYNPbgNzK0iD8IJGA3tnrTFuD+INX1GaaygSTJV+d5VjLkqDkA9c5pejXurcO8LRai8KtCLnw3ibdZI3TLRyDurDP3FSMmrXUsdvcWEDQWVszQWspH1MowQreZUHHqKhluT4J4quS5yPuGL5dHbX7XXorqPT2svAubXlIZpCw5Fx2bbr5VUp4bee8tXKzGzuJeQqhBkG+6DzbpvWg/xgcUcPXOlagiJeLH40Vyq/j8MZ5W8zjODWbWGh6hxDqoXTLm3toRIEjlvJxAryHoFz1Y+nShreG2+GSXR+mMY8r/ACaBb8NcXaLpo1vR9HsbCK2ImMcDLNcKo7yHdjt1/tS/iBrmmRaFba3p+l2q3HEds8F9KQSwCYOAOnMGxv1xiofRZtc+G3xbtLfWRNH4c6C4VjzLcQOcMR2YEE71Ccd6hYaiYbXSpOWK2nmDW56oecqCPdQtJQzJNjysUa5JLD+H/vwVuykmneaeZi8jvlidznHeno2rnw9qlmmsW+n63Abmwdwjcg/mRE7cy43PtWv8Y/CO00ng6fX9IuZQbZPFlt5clXTbJUncEZzitSr1CuvbVNYM3/2+y6MrK3nHa8mSdKHWh0PWhWqzLC69KHajoYNCxwqFHvRGhEJFK7UQpQohBAbUdDtRinSEFijxR4Ao+oosDZC+1HijoY9KdDMTikSEpE7+QJrrinWnWEeoXbRXFwtvbRoZZ5m/Kg8h3Y9AKabUU2x64uUlFHDipXsrsaNptuqwW6RO1wi5kuJGXm5i3Xvso7CqpcyTTSkGNlI6r1q0Wl+LmHUJULGSKBLa3d+qozchkP8Am5dvTNJt4rOW+MUQEcUcfI2OuM/386y9Q1bLenwzRgsLBX7d8PCg+rByQBmpBI4LvUCpuETlH0g7F2+9PbWwSK3Nzb4YsSeXuBnt/tXJbCG4uC9y+Yz9TEfiPovqaqNEqR3Th5v4gltcTWUbSdBI31H7Co640+40zVBa3yukUeWTPRhnYjzFOYbK5sNRF3bSurhS6HOXwOq57nFSk91Z8Q6BHHqF/JDf27uYvEQsrIexwPTrUL3ReX0SpRkmksMhjcTSEtbMT9PXGzHyqStbkhXuPESNoFErAthk8sfeouWQ2sqwsA+31FDnA9DS7edbO5ilRxIq7HI3KHqD50b5AUmmX1NUstX4fdr+5t7O8bAFyY8iQeZA/MKgNU4RvktV1KzEV7ZoOcXFs3MFA3II6ipPRND0/VYZLlNTisORgApAYOp747eVObLWOH9C1xf4fc6g8ZJS4jZAyTDHYdj6+VVcuDah/YvtKxJ2/wB8mfeJdaddR3skWVuYy0TZ/LnGf2qR8S9n0QGMCM/iDN1JB7eVXnV9KsOJNK+Z4atmYW68klqY+VowfJfL2qnz2epWlva209lLD4oKpI4IBxU9dqmueGVrKHW+OV8jeyun1KJhPCFKHlYNuCatvCuqWSvHpd3AUtZW5VPNzeEx6EZ6DzFVV01Cwge5aKBwp+ob5I86snA+kQ6lqBur26jt4rblkKs2DIx6AZ7UF+NjbJNLuViUeyO4nv7KSeawtoJY0EnhhpV5S2D1x2FQF9DLYRRSRxp4IYc2+cnOd/0qf47066tOIJrm5VgPEEqt/Uue1QNzdTXFk3NbFI5cKgc7nfqaOl/SsEWoT9ySZb0160jsnspYVlSeMDwCvMDg8ykj0NTOuGy0fQLPR5LuO4und76VlGB9fTA8sdKq+kix4enS9lBncEJKW7o2xA8hUhxC2m3+kWF3NMHnMXhkDoqqSAc+dR28zj8FiqWK5fP7Efb6zatbX3JMyStbtHCpyC7Mcbewzmm8Vw1vZW8w1OOaW0ZZIrc/VyANkjPYf3qGmRLfllE6TYB/A2So7AmudnM85mgWFQ0g+nkG536Gp1DyVXa+iywcdXevcW6fdcT3nzNrZ34uBCVAIUyBiqehx06Co3WbOa61a91q1j5Iri7kkMX/AKfO5IX2wQKTLwqNM0KHUbppBcNcKBgjkUZ+pT/mG1WLSdO1TUb9tIs9M+dN7mL8RXwznaTPkOp9qj+mKyiVKc/pn2O/h5aLq+v23DOoabDa30AknsdRjj8OeGVTzBX/AKl9+mauvxDvuKn0q5gsY557PUrRGvY1Jc2zRNhwg7AnGcdqXxXqGk/Dziqy122sm1JrtBGLoSARoyhVlIx1Y4z7U/4w4jsdA4h0zWLhrl9PllEqm2H1Yljw37hTiqm9ynGaRowrjCEq5Sx8v7MwbOTnOfajq7fE2PQhxPbXGkJGktzb+PcrEMISW+lgOxIzn2ql4NdVprverU8YyctqqPYtdec4E96FGaKpmiuCiINHRUI4KUOuKIUob04gYFAChR4zRIEGKMYHahijosCBijounWh3zRJAh0axNLHPzSiG2WImd8ZPLnYKO7E7D7miFdtQv7WDha0smi3mlme4lHUEYCfoP71W1UlGGH5LGmi3LK8ERb3cdrp0jrEAlwpgkPUxkMGQ/ptTT+IrySfLpyuVwWPlTF53iYiOUHPXl6Gl29tK1yo5SSw6AZzmsZzb4L6+xIjV2htYwkPN9PXPSuNpfl5TLM4UhiT2ABpwmh3bvHBbOskjAlkH/THmT0xTiXheaXU1t7HN0eRfEYYC83fB8qjc0iRQm/B1e+WS4tJI8mLmK8xGM5FKvXLPHy87R9GCHGPX1rnqGiXttZLptrLBfMh8RvljzGE+RptHa3fyqo/iRXMRIKv9JKmkpJodxknhok9Gnj0vWkujCJY+jR7Yb3z1B71HTFp7ueRbdIzzlmjUYCAnoPSpC1sdTexM3y6MAeVjjdT6+VRzTTxagxntwBb/AFSZ8uw+9Ctrba7CluUUn0ObKCUXpW4jaGFcEIQRzZ/0p1fxXMfJcx2XOCQDITggeeKTc6nNqWq28sMT3LCMFvDG252B8qjtT12+ubh7Xk8IKSjAHJJ96JcgtpIlbLVzaahGtlfPFcZwskTYx6E+vlU7xve31xqUOtfMePaywgW6jbwWAw0ZXs2d89xiqBHbIGTlcrkcx5u2OtaDw7rFssb6XqiidbgD5e4VQTHNjCn2boaisW170WKZbk65PCZTDqN7qMluDG+VLeKAMAj2qWjkteSOK1mYsTgxt2+x6Vxt7wy6vcvfxrDM0hBHQKRsV/ahKqTawX5W+lQ8ZHfzBo8kK4LoNY8fgG/sZgl1fWiK8Ek0fP4cLNytv/UuRjPY1SJJ4Z7dYZsLNE6kj+oA9RUho2vzWuoTQwxJd20sfLcw/wBSnyPn1qL1PS5U4sewtEedhyiFQMlg2429jUda2Sa/qTWzdkU/6Dizmub8tFHbNNNO7eFCBlnzsFxUlxZbJarZWS2wtGhtEWW3Bz4b43Unzq1aLw7pvBtzDrOq6kbi9WPKWkYGVcjrn0qvavd22ranPdTaZEHkOSTK3+neg9zfPMekSOpwral2yo6fZXV9dLaWNu0oP4sDCr6k9BV50rRLXTdHdJLqBb8MxikVeZRnYUUeo22qW6afoVo2nQ2kHPcKuGiABwzlhvjJG5qI1a6vbaZ7GdDGyjc9iPMHy9aJylPjoGEIVrd2PtN0jU9Shv8ASLeJ5bGPF3PNgtyOoOSG8z3q5aFqM8XBH/l+zmttMv7q3Iinc8rXAY7c0n5WxsO1ZqeO9cv7EWF1eTG2QBBCoEcZA2GQoGfvXK+v5ptPjmJj/kRhfpOC6g7Z8yKTrcuJDwvjDmJabkqdAteENYhnhubPVYpfl7jYrExwwB8vX1plxRxJqV0+qabqcsL2sKyx26RphYvqHIF9sf3qs6jxpqGq6JDpt4BMLcgwTSfVJEO6h+vKf6Tt5VGX2ovfeHEoI/M+e7UahzyQyv4xEf2l9PqM89xOcsOVRv0ULgD9qd4q76dwmOJ/hm/Elk9sdRhyWit0EYeNV+pGUfnGCQe4NUkbjI3B3FbWgtjOvbHtdmZraJ1z3S6lymJ6UMUeM0O1XcFMIik486VQ9qBocSKV2ohSvvTjgHWjogKVRoEHtR0Xej3ztTjAoHpR0RohgicL6edMdY54LVFlGPGXxEQ/iHkxHbI6frU5o+njUtReN2CxQQPdS57qg2H3YgVX2kjvtLd7qQyXTSMW335vM+lUta/p2lrTRx9Q1u9Pjgt4gn1M/hnJ82GSBUhb8togS5ilTJA8QZVlXv70xuHiu1gctiSNEj5AfLbP3q3Q2YfTkW7/AJzv2Y/tWNa0maVMWyOS1vzDLBZzK1tNIE5kOOduwPceeKIvf2WhsiFgHYqzLvy+n3qctbKGQOF8O1YAYkU/SR5MO/vT+EaRFZMk8UkkYAjZEIxJvt17etV3ZgtRqzznBQY5poJAYeaNm6lSRUxYqdUuUiub2NHYiNGky7+2B2qfudD0u/wbNFsnjGBGxyH/APd2NTPAXD8seueK9ukccRyWcAsfLBprLoqLl5Cp08nNRfRP6bwVb6Tpkl7f6o6RwxF5HVMEKBkjfYj0NZfqNrDqWo3l1N9COniLCn0gbYUH2H71q3xRvJLbgmG3t3Crc3AST1VVLY+5ArHoHurseOqrHG+FXnO7f9motHmSdkn2T+oOMZKmK6JDh/QrjU9KNhZTrasqczuQdyTgL+3WpL/6Xa7ZujS2svgN/iPGvich/qwNyvn3HWrz8OeD5LLxNQ1BgzM4IVfw5HQDzx1z51py5Bz3qvdrZRm1B8FvT+mxlWnYsM84ahwDq9pqAiuYTGM/ypgMx8x6Bj2B8/1qLm0u+0m98C4tZbaRDnlIP0nzHp616lcJJGUdAykYKsMg0yv9I03U4RHe2kcgX8LYwy+xoI69/wAyDn6VD+VmD67othqemWWtR3K+NqCsxtmGMyIeV8N2PQ1W1As3EMiMOQbE7ke9ehtT4K0XUdKlsfB8FWk8VGQf4bkYLAeuBkVWL74ftLaRi5VHlwYpZkG+R+CX+wYeVS1ayOOSG/0+T5S5Mis47ayuWmjyBIxYr5LWn3cWmaDoUHFYsorjUprZIxIGPIw7N74xnHtVGu+FtT0ziC2hmti387wgh6Eg7r9wcirLxzDHp1jp+i2PLHa2seBHgs4br9THbbNS2yjOUUn2V6FKuE211+pTLq/meV7iQmSWQl3LHH3/AOKiW1ZZLeR55FiVm5VUbsRT9IpHOIrYO3csdvuaZ6hB/M8ONIJJPzGNcKvpnuatRx0UZ7uzvpetT6ckj6XKIxNGYpDjOUbYqVPnV30LUbG74eksWW2mu3X5aKKUD6SRnZj+UgdOxGKz7R1VLm4lnQq4Ubny71Ptqh1W0XRpkjLlvEtZlUK6SKCQCR1UjIobq9y4JNPa4PkPUIILH6Lu2FspPLuBy5+1Vua1gkvY7K1kMkbkyMgOcAdhTmW5+dA8TnZNizzsTj/mpvgnQ9H4j45trO6v3sZJZcxXUTANGQM55TsVGN6dZhFtjNKyajEh9IstNlv5fnIh4EMbSLGq/wCI+CFB9Aar9xZSWM8MlwpCyDmyDuR3+9XPinQ7+0v7zWNPuVudOluGgW6hj8MEjoSv5ebqPOrJb/DiOC+0C/eRr7QpLb56a6ugEEbLuyED8p2wPel7iXLG9iUntS6FcK6fd6Vw3dXujand2VtdQSxTpfxcpgcRF1YjoVZcgMKoi/4a4BA5RgHtVk404yfiHVXs9P50s8qskhO8wQcq+wxnaq72rV9LrkoynLyUfU7Itxqj/KJoseVKxQrVZlicUDQNA4oGOJXpmlCkilUhxVHiiA2o6NIFgowDQAoCiEHiiI2o6DE8hIG+Ns+dOMcl1Wawnnhtd5ri2NvzdkBYEn3wNqgJbeSC4aOJjyyd+4HerDxVPp9trdvBpuHtrKMWzS/+s/V3/wDkTj2qMc+O7NF9SkhFIGebzxWJdL3pv7Gko+3HBG8vLewlRj6wP3rSoIw6qkzqqjcN1K1UL/hrXbHSoNUutGu4LcyAmd0wAD0yOo+9Wi3uUK+DHguBlves61pv6WX6IyjxJYO7KpZURDgnP1fmrvGoihl8VC3MOQL2znufSuiNzR8wAXAxlRuaLlyvKzADGy+VQNltLBzlRCwlBZ4D0B6ofI/71pPBNhGmhSTiJELtksrlsgDvVN0nhvWtSuC1tbsIsYMr/QmPL1rRrVIeGuDJjqlzBFDDExllAwoBGPud6qaiaxtT5L2kqae9rCMZ4+4uudduxbQRiPTYWfwdvrkbBHMT2B3wKZaNY3WqX9vbWkLGKN0MspGFUDB5Qe5PlTOc2l+n8iXlhhl2ZxglQf8Aatc+GumrLw3bTvGQiMzrkdct9P7b1btktPV9KKWnreqv+t/cvunQC10yGAjDIo5vfqadikKuBXQCsE6UOgKFGBSEEelIIpRU0CPKkIZ3Fha3TIZ4Fco6yKcbgjpTG64a0m8vDdXVsJ5M5USHKp7L0qa5aGKJTa6BcU+0Ue9+Gelaldiaa8ucd0GAD7AbAVU9U+FWpwLJLZ+CY1yRiQZA9q2MnArm5JBzuKmhqbI9Mgs0lU+0eXL7T9S0fV45ruCZYGzEGkxytnsKGg2ijV7sNerA6wSLZTNuqSsNuby2yAexIrQviXoqTaTdkOYzav48Xl7H9azrSILiOWRjGwlBLYxnG3X2FbFNnuwyc7qqfZtwuhjdaZJFYxvNqAZsA+EqklfTbvTjh910+7e6+pJmUxo8hxyKdmYeuNq1zU+BBNw7AdNuPDkMaknlB58gHOfWsm17TJ9IvCszBp4znMbiTGPPypU3xt4yFqtJKhqWC8cPca6dYXM2m31quo6VeR+DdWpGzgfhZfJh2NSUvGScV3GqcPpcG3tJdNe3t4RskCrgqPfbc1kI1OF9R+YTxhIVJJkwAu3YChp97axKfmLuSJJj/OaHeQr/AEL79yaklXFvPkhhqZJY8F20/hkanwda6hpheWU2U1xIrDcSwviRB/lKlSPUVADBGQdiMirVpvxKjsdKntNK0uC2YWvylhEPq8FWP1ux/Mcbk9zVWVAqKo6AYFa3pfuYkprjwZ/qLqexwfOOROKI7daVRHzrVZmCT1pBpZpJFCx0JpQohR0wTFb9qMDFCjo0AAClUnGKUKJIYFKMdu1jdTXFyIxCgZYx+KVicBR5AdSfKk96a6vZ3K29q75T5mJpI07sgOzHyBI2qDVWe3W2uyaiG6Yynt/GscE/UxCr75q6cKxw6HZya69kty8RFtZQttzynqft51T9PWS6gWQsU5BhAPPuf9K2O00GI2Wk6W8XiXNpGGKjoZZBk59hXP6yXs0JP+f9F/2bvp1Tvvco/wAn6v8A1knw1xA/EKzaXrtlBDO6H+WrFo506EDPcdx96ofEXD95w5xdHZoq/IT5a2mI+or3Qn+of2q3a2LnSdP5NFSPx7KQTPKy5aVl/Eo8hjIqwXtrp3F3Dtss6/yZTHcRONynQ/7g1iQs9uW5fhZ0F1PvQ2P8S8mYrE+yrk+oq2cEaOLu8kvrmNJYoDyqDuC//Aqn+MLe8uIVAIjuJIwM7ABiMD7VsvDFtHa8K2g5cNKnitkAHJ/4xU+qscYceSpo61OznwSSPyqF6AdqpvxQvLWXga60oOXunCXHhp1REcEu3kvYeZqy6np0l3C3gare2TY6wOB+xFYBxhb61a8W6pGNZmvpI+WJ5HOGdeUHlONts9KraSpTmnnrkteoXyrrccd8HDSbZJtZtLRYVljmnVWjboR1Oa9I6VaCy0qG3C4woJ9zXnnhfilNM1dGfTRPBHgqrDl3xuwPn2rf+Hdf07iWxNzYSfUv+JC340+3l61P6hubTxwV/SnBJrPLJdTS6HJigNjWWbIdHSR6CjJpCB13odqLPbNDOKcQqkmgTRZphCCKAXtSu9LUDuKfIjLfiwzRabzRj+UZ4VmPpv8A64rPdM1htL1gXNqVNyVMaBhlTzAqQw7jB3rVeOr+ystH1S4v4BPbiMo0WM85Oyj9cb+lYzw6Y7TXY7i8Zp0jt5ByKMmRyuFX2JI3rY0b/hPKMD1GP8eOH3/g9D6XaCCy0/TA/iGNI4c+eAKzb442cGk/FXwJNPtJLV0Vx4a+G+CN1LDrvuM1qfANjLd63pkVzlmijEkvuqj/AF2qr/EXT9P174waob6K4itOZIHkZOdeZV2ZcHv0xVDTy238+EaWtjv0yS7bRkuq6Jaatwf/ABDR9NltbezCw3ks8qszzEkgIOpHLVDsrZ5tRWaK2Lxo4PIRkHB6H3rc+M7e10HhOeaK3ihaeE8oIwwIHKv/ALt/2rL9CF9o+nJqVuYsvKpgmbDch35sKe/vWzps2L6V30c9q4Rrkt3xyOtT0YaNxJd23hhBlXjX+lHUOB9s4+1cM7Uuaaa5uJLi4leaaRizyOcsxPcmkYGOldTp63XVGEu0jn75xnZKUVhN8BUDR96I9KkIxJG9JNKNINCx0JU0oUkbClA70KHFih9qAo6NDA60faiA3pVGCxEgLRsgOCVIz5bU01HXJrrXIrydCT4McSRDsqrygD7jNSdmbI6rCl/MIrcc0khJ6qoyVHqdh9zUMyie8VwgT+YxwB0XqB9qzNZNTsjWu/8AsvaeLhW5v/cFj4T0433EunWQjBV5Q8gHYD6mrc9JjKarPdXEMa4J5GByWLdSfLAwMVh3C+o/wri2wvZCBEkoWT/8W2P961y5e7ttB1KHxGaaOdo1kJ3KuQVb9DWJ69Fq6MfGODof/T0l7M35zz/bj9zpr2p8HxyS3d349xMNnitScSEdj2JrhwbrFvq1pdBNPGnpbz4jts55EO6/61D3WhywRQtbI03hocjIBB/q3p/wZYTTtLrLyMIZF8KJQf8AEAO7n07D71jOMVDhm1ul7iyUTUNPI4+u7K1V18a8I8PO+7ZyD9zW3KPCjVAdlAUfYYrObfTCfjBdTJGY1hlMjAfUPwjB3881okH1kA0epnlRX2INHXtc38sYTa/Yw3rW0kn8xN2QEc4HnynfHqKwVFkl1e4SSVmluZmdJJTu5Zj9RNaf8WeHrW84aXUt0uYGVInQfUSxxy58jWUaJpXEGrhk0QuJLEYYM+++emfarWiitjlEpepSlvjCSNd0HhPR77hpLGZY7mOBAkcsbDnHmykbjeqbrGm65wPqJvbCW4MKnK3CDlZfRx/r0qHXjHiHhPUG0nXtMtp3QKxX/DkAIyCHT0q4ad8StG1mz+Un1LwmdeU2uqjmX2WUf60LhbW23ymH7mnuSintkv6E3wt8XtP1Hw7TXuS1mOALlP8ADY/5h+X+1aRHNFNEskUiyIwyrqcgj0NeceIOGkS5+c06NbMv+HJElvL6Bx+E+9M9C4w4n4SvvCV5YB3tpwWjf29PUUE9JCxbquH8BQ11lL23LK+T07neiJzVJ4W+JGk8QrFb3S/IXj/Tyu2Y2byVvP0NXMnHWs+dcoPEkatdsbFug8i870KTnajoSQPPrQpPehnakIV/3iiZ+VTiiyaQcnIpCKN8QbWxfhO/N9KI45LZnyTj+YD9GPXOKxjhrSbrXdbjsbYnndVMhH/SUHLH7VsnxLsXv+HpoohzG1Rblk8wp3/Y5qj8C2E44ttrizna3t5ysU0idx+ML7NjFaulntok0zD11e/UxTXB6X+HlrDY6fqeszKeS2g5QcZOFHMf7Cs60qO0uru91i7lVZGlaRo5TiQl99h3GMVpdjplzP8ABvUUjlkimuYpJgYjyk435c+RAxWF67xRYaZw/dXYVpT9KQkbczMMhQD2Hf0rN06c5Sx2zW1UlCMd3SKr8UuJE1jiS00UQwtBYDmmZWwJZG3IOOmBgVTrmOCW6gktoTBFGueTplj6eg796bQxrPdC8MkrzOWeUuuwYnse9PcbV2vpuiUYqT8HC6/WSnNr5EjNKAzQwO1CtrBliTselA0ZpNCwhJ60k9etKJ9aQcd6BjoTSxSBSwKEcVjAoCi7UoYo0CGN+tHRCjJCqWOwG+aMZnPUbIDQ01JuvzHIPVAME/8AypMARwrooEYBwSN2J6n2ptI8895LaXRZViB5IidlB3/5pxah/lIy3UoM1k6VKy+U3+Zf1DcKlFHflByO1bFwrqUGu8Io07s8sAFlfADfA3jlHtWPKrswVFLOxCqo6kk4A/UiprhriG44Q+KVxpWpjw7N3/h9zEeiEdHPqGO/vUfrtKsqTX4l0WvQtR7Fzz+F8P8AY0jimC6gsVsLmMMsmV+YU/Q4x+x9KecF3oOjfwhzGZrJVQch3aM/hYjseoqYawFxp0un3zi4gJ5VzsQvbfzHY1T+HeDOI9E+KsWqiaO70mVHt5JFYK6pjK869znuK5GLTg02dhZuViklnPH5Fl/h7JxVc35GPFiAGO+Nt6mLfY07khGRsKbhOQeoqFy3FiMFAp/xP1X5bh2DSkt+eS8bn8Q9I1Qg7epOKonw316bh/jtdS1BEOnXXNDOgGWCr+fH+Un7jNTXxV1xkvrLSfAwIh8y0p6tzZUKv6En7VYOCOE4I+EWkucSyXx8c5UfysjYD1HWtGuap06yuzJsg9Rqmk+hXxA4Q0/VPiE2oW6W3yWo2kU0FxbkESco5XAI7jY48jWY3nwz4id70TWNq6M6mK4hT+aVXP4VBA3BGc+VbNb8IWlqg8B3SUuHLK3KvN3bHTNSiaLJ4sfzUsd9Chy0E0jpHIMbBgmD1361EtY0+HwSy9PhKP1x5PP+lcH/ABA0rRrvVNOWY2KM0YiwSLhRszKh2IH/AOqsWkrpnEekq8dqpgRQl1YS/UYW6eJGeoBPUdq9GWuuxNZx2V5w/YRwRxhE+VchVx0AUjYe1UqfhbTbbimXVdMiYQXhxPbOoPhNj8asOx6FfPejs1MJLK7Ao0k63tf4fuZS/Aq28/iafMzRk58GQ7/Zv96u/CN7rFrZx2Gqq55M+GGPM5GNl89j3NT78NwIzqskmM/QD+UeXrUjYWzQQCOTBK7Bh3FV7NRvjiXJar0qrluhwd0DMoJGD3FdQu3SjACim17fwWNo9xcSBEXuT+1Ve+i3nHZ1YhWA8+lcpLiKNSZJY0A6lmAFY/xVxNxJqN7NHbOLKzwVVhKEJHq1U8aHrl9GCZxLk5JRndT7nGKuw0ixmUsGfZrmniEGz0JPrui2ic1zq1lH6GZf96hLj4j8HwJldXSc9OWBGY1j8PBV9cb3d2sTHqI4Af7sKexcDaVZuLjUrrUZYEGZFW3Cg+5UkgUa09C7lkB6nUy6gkvud+M/iRaatb3en2FncqLgqjSSMBlBuRgb77VBcM8UzaYqyzxBo/HjHKmzHlJJxn0NS2vaZwrZcP8AzWlxQx3EcsbAsWEhGcHZvenfBsVtqWrTRTQRyW9uuX51BDOei/puatxdcanhcFCSunqI5ksnqjRuMOG7j4H3HE+nXayWFnZSNIG+lo2VD9DDs2SP1rxFdXeo8TanFpenR3V24VnWKCNpC0jbuyqBnYbfatr+LNjpvCfAujcE8MWs8XEHFXJNf20UreGYVb+WDH0BLd/JTU7o1zwn8DNAhSw05NY4ouIlS6dJORsk53b8i56KNyBms/SzWnXuQWXJ8L8vk0NXXPVy9uTwo9v7/CPPiRrDGIlUqE+nBGCMefrR4qf461K01f4na5qVlAkMNxdFwkf4eblXnI925qgPSvQ9NY7KozaxlLg4PUVKq2VaecNrIRFDfzo8bUR6VKyISfPNJOMUrtSTQMIQaSelKPWkn9KjYSCFKFJFKGaZCFCjHSiFHRoEOj8aKApLOOaNXUsPMZ6Uk0me7trbSbwSBWnlRY4wR+FScuw/QCo9TZsqbJKIbrF/vRzv7e3u9UkvHLfzCAFB/Eeuf0pwCMAAYA6Uys4ZUdhMc8oHhrnPKDvTzG1RenV7a93ySaye6ePgcWt++mahb6lDGskltKsyo3QkZ/tnP2qE1DUP/MOsXeo3RbxpmBZuuTjHN7mpa3ggmllN0f5ENvJcOvdwo2Qe5I+2agOZLZhO4AV035RtzDtVb1GzMlEm0kWoZfRvfw44pXiXhNbSS8Rb7TraR7rDYd0iX6SCQQCwwObB3HrV00ye7PD1vcXSN4zRc5BXkJG5GV7EjBx2rzRwhrcul6bqsdjcw213OsZUysFEqKx548kY3yDjviprVPi7xikTWFvqNmVjAi+agi5jJgYyCf8AauZv0Tl+BHSab1NRWbW+j0PbXIubZJl/C4BFHJGScr3qrfDLVJNa+G2n3czc0yhopG82Vuv7irpHGM5NZk1sk4vwblU/cipLyYj8R7O7/wDqGguCDHLAnyrHpGucN+jHJ+1a5w/p0ek8MWdgk0k3hx7ySHJJO9ZXxxI2r/GiDR7qQwxI0cCIBkmPHOW/9x29MVscQBhUqMDAwKs6mT9uuL+Cpo4r3bZL5wKxvXRRikgYpY6VSNAGN6UpKtzDqPOgBRgU+RgpGaRyznJ9qQdq6VzYUwjm78qkk4A3JqoPpd3xReG7ncRwxMRFGxyqeuO7etXDwY7mSO1lLKs0ixEr1wTTWzs3sby8gOAolIAA9aOE9vXYMobu+jPNR4F1rVNRFnotqskqthr28HLFF/8Aiv5z7VSdU+GfEqazqVtqGo3Nw9pL4ZIDZYEAqwU9AR0Ar0FIgkjKNupGCM9qg73R7hrx72yunjuXQI7yEuXVR9KksdwPWrdeqaWPJQu0SnLL5Xwee5OEpdSgtpbDRtT0/wAG3ENx4xMxuZwTzSIMAopGPp3x5mp7hD4X6pr2kXt3JfXdrGkxghxE2JcD6iQcbZ2rTzYJPdJDxXLqkdofqf8AhCBZJQNyCScqPber1qfxb4ZsNC8PR9M1S7nWMJFbPalPpxgZYk7eo3NXIaly5Zn2aGEXiOTyxxpo/EPD0cOm6tfvd2uT4H1kgEeh3GP0rQvgXH81r6R3GialcaVBGbq5mLIqRBAS0jsfybdOvSoLji5n4g1i2u9XEkWoXTh44OUcqQ5xk+RJ2AH3q/y8RWXD/wD4YEsLBEbVdcmkjuUT8RijflIOOgY4GPLNDqJ761FLt4D0tKrvc934V/qIG513UuKPiTqXG6xeHqV/mPTQ4yNPs1HKj4/qI6e+alrpLSx0XT9Skt1d7KGe/lEhLF3VcAuepJcin/wltY7vijS7XWbOIXMz80sqfm5VJCkdNvTyrl8QdKTh7hmXS7+4igkvppreFWcDmjiBkJ9ixUVT3KVir8ft/wDhqxj7dTsb57/r/wDbMTVndi8m7sSzHzJ3P7ml4pEe6KcYOK6V6TFYWEeaNtvLCoj0ozSelJiQk0RoHrQqNhCKS1KbrSfvUbYQkUsGuYO1LFCmOxYpWa5g0oGpECwyNqZ39k9zZtKDyhHWMMehZux+29PcUJbmCPSrm2mJ+t45E27g4P7GquubVTx9ixpFF2fV8P8AQ4WkfhWwDNzOfxNnOT0pxuTTW2deR4Qc+ExT/anS7dKsadp1xx8EFqxN5A9rPPDKLYgMsTFsnACdDn9h71BP9Vj8mQOckDJ8h39+1WWCcpDcQlD4cpjzJjYMM4Un16j2qBurZTrbIWwq/wAw/esnWvNr4NHTxSrRFzw8kOQOm1ARZ08Y6gc1SSvFdXKRxgFVLNy48hTOQlLTH+TBFV9mFuY7ks4N/wDgsRa8OX2muxyjxXKqT+WRN/3FaYZMbiss+HfPZa5aRSLyLe6eI1PcsmHA/QmtTEYzua5fU/8AkbO10ixUo/Bm95bLff8AiFhQQnK2fMzsOhCHBH61pcUXhRLH15QBWR3PEt7b/wDiEgjktlHJL8gEG+YmH4vc5z9q2I770Woi0oZ+EBpJRbnj/wCTE8tAClZotqrFzIYFCh2odqQgmNc2zSzmkEUgjvpVu1xxJbgEcsKvOw+3Kp/Vqca1A0WqFh0kUN9+hp3wpGJNQ1KbA/lW6IPPdiT/AP5pXEPhmWDB+vlJx6UGfrwFj6MkFihybbiumKFGR4E8i8hBUEHrmmh0yzaeIraRcyseQhd1z1xTzFOtMge41NEhUvN0jQDOWPQ+wpm8chY8GIfE+DSouPNPOhX0d1fxE2N1aKh5YZF+pPqOx6nIHTFDR4dPmjSJLk3dzBMyysv+GAB9IXsTzFiaa/EW0064+NWs6Zo0pu7aR41Pyv1HxwAJFUjvzZB96veicIWlnwXcarql3aaDp1kzRyB/qeIr15sfmPQDcmtGc4xqgm+/3MmmEp6iySS4/twL4fjGnXh1j5lLaOCN8XDnCR7YeQn+lB+5AFZRxtxBZcX8SxX4u5RpttG0VhHKCXdFOAcdmdssfIYptx/8SJOKZJNF0fx4NDhwWMoCyXZX8JcDZVHZB7nJqF0iyuZ+EpdQKoLa0nSFCR9TGTOd/IYq/wCnaVQtVlnDfH5Z/coep6/3a3TVzFc/nj9heD96FFnfFCu2yccA9NqQdqUTSSaFjoTtRHYUfeiJoGEhBJ70VGRmk5wKjY4hfwildqSBtilgZoRwA0sHNJOFH1ED3oRFpZfDhjkkbyVT/en9yMeWxKEpdI6ZNcLmMTQNGSBnofKu58OPIurq3tmH5CTI/wCi9K6xz6dbWtxMupPKcK2I4wrAg7DJ7HNVb9bXtajyWatLNvMuBtbQLFAqLvgbnzPnXYsij6nUe5pkt9pw55PkpTJj6S78wJ9RSP4jO64URRj/ACRgUEdfiKUYjvSJvLkSU+pI+lW+nRuOUTyTyKPzNgBSfQDOPc1DJHdX2rSrzDw0AVmxuR2FNUNzJrbyRq8pT63x/SBualYbmCCW6nQ8ys4xjq2BWffdKyW5luqEYrb4GaMtjfXalC0gXkXHT3Nc/D8S4m5Y8oyjCk/hyR/rTYyPd6sZX+nnYkgenan1rD8xxFp8CDd50X96UrXsUX0ho0py3Lyb7Ei6bZ2N8I+ZrMpIoHkFw37E1eobhZoVlicNGwDKwOxB6VTQDLbmFhtjFL4QvmsdQfhy+fCkl7Jz3HVovcdR6e1czOO5ZO0jLbJLwyN4v0m4t/iJpXENpAHEuIJsDcspyPYkZ39K0xH5lznOd6Z3fJGI2MBm/mDAAzynzp0gPSgnNyik/A8K1CUmvJ1G5o+9EKPGaiJQUOlHgZoHpSEcWuIVnEDSqJDuFJ3NdhKqRupTJYYz5VymjjlTlkRWGQdx0IqF1yPV76RNO02Q2yOMzXWN1X+lfU+dOlkTeC0cK6xY29xrELyEsyxhSBkHAYEZ89643Vy91dtNJ1PQeQ8qiNH0qLSLI28UryE45nb+wqQAxTOKTbQ+54wxQpWPSiBpYpDoRjbJqS1XWRwL8Np9aCA6vfn5fTYPzNK2yn2Xdz7Cuug6UNS1DmnZY7SAeLPI5wqqN9z9qwH4g/F5te+LUmo2mmvdaBYxtaafynlxv9Uw7b4/SjpplfPbFZS7ItTqYaeKc3jPCIr4Yz3mmfFcKYUvLlrmS2zIM85Z/rcHscBiD9qHHvHl1xjrEkUEXyWiwTO1rZrsWbODNL/VIcfboKr8OuSvLPeWYnhu5pEunt4iPDZBKGCu3XcjOB96jZJmmuZZ5OUNJI0jcowMliTj03rrvTNNCV7usjlpcfY4v1DVTjQqa5cNvP3IS7gUao6xOFMmObyUnzq46jI9hpttodqwW18GOZ1A/GwzynP3JqpuAs0qts3OST556VeBoM11wNNxLcz5uEEToiMChgJ5cHyYHB+9HmC1KlLrP+fAFSm9PKMO8f48lf360ecigdqLNdAYwRpNGTvScnNC2EgjRE0Rz2oGo2x0FSW60ZpJ65oGwsDm00u+uwCkYjQ9Hl2z7Dqakjo1laoGvrxj7MEH+9RGscRXqgR2reGZGJBHUL5VCma5mfmlmZ2PdjmsaV05vs01CuHSyWw3mgWjc8EcbuNhgFj+9Ik4gQpiOAj3IAFV1E3ySSfM10A+qo9vyH7j8CZWXnJbdicmuGFO4BHoa6yKd26iuDvyjGCT2A6mkAGd9gKQz8uwPvRL8wwUhOQ9+ak/INKxaSU79h0pvyET2irFPpkiwfTcOzeJJ5qAOVR981H2NoRqkhP4UHMPIE/9mnGjxzadIrurC3mZkjcnqw61zmkln1S5tbfARn5nby2qJ5yydYwmQsb51P6DlS5A+9WfhG3+a+I2kRn8IfxP/iCagpraOKVg6qGRuXPSrX8MrZZ/iLbsgGI4mbI9cCgubVcn9iTTLNsY/dG+x6bz2ocHD+XnVX162dblJEZo5VIdHXqjqdmFXpW25RUTr9h49l4yKOZT9XtWBXJqXJ19kE4jrhvWxremFpVEd5AfDuYgfwt2Yf5WG4+47VPqPprKbe5udI1aLVrNC8kY5JYQcePF1K+46r6+9abYX1rqWmw31lKJYJl5kb08j5EdCKa2G15XRHXPPD7HRNN7vULHToVm1C8htY2YIHmblUk9Bmu2a5y28N1CYbmCKaM9UlUMD9jUa+5I8+Dol3aSRh47u3dTuCsqnP70bTRf+qn61CzcLcPl/Ej0e0jbpmNOX+1cE4atFV3tZZIiMYVpif8A4g0WI/IopssIIbGDkedButV5IOILPMdrLDcDP5hgge1MZuKNa0q4DavoVxJZl+T5m0xKR68o3xSUG+hSaj2XEAYoEY6dKa2N7Bf2EV5auXhlHMjFSpI9juKeLv1oWsCT8iRmutvHLcXCQQoXkc8qqO9Kht5LidYIUZ5HOFVRuTVH+IXxVs+CoJ+HuD7mG94kdTHdaihDxaeD1VD0aT16CnhXKx7YLkCy6NUd83wI+OXxGt+HtBb4YcO3Qa+uAG1q7iP+Gp3EAI7n83kNu9eerQyy3q2sb458qFJ2O3T79KYXizNM9zJNJLJIS0skjczMx3LE9zmlwxma9jTn5AcMz/0jHWug01Cohtj35OY1WoepscpLjwvsW7h4acsOvSalAk3g2LLFOhOTOMBcfrge1QibIOhxtkVadCsoNM+F99rMxjeUTROiORhjzEcvrtvUHc6ppV7vcac1vJ2mtmGR7joauaPU+1KXGUVtZpvchDnDx+rITUYmkljSEN4jghSO/pVlhu7rS+C00KORpILpvEZ26hQclB/7sVF3dstvFbXcF7b3MRfAZTyupx0ZT096eaJC+s6Xq11MzLDa25a2P+cHJ/UbGjtuhK5Wfy5RHTVONbrX4mmv6DYnPvRZNJUjGaM9K6HJioInHSiO9A+9JzQNjg60RoE0RoWEETSSdqBO9EajYRGXYdijnBVcjPcZpMeeYe9PGVTlW3B7U1ZPCZg5AC758x51io0hznA2o2blXOdzTEXcKD/Ez6UtZpLhWePlWNert/YeZpZQjsySyxsUwABksTso9ab20W5lkc8q7lj1pcMDspMjnlO5GetHfHwrLkUY5jge1C/kcC3sLjphvKlRSOX5uij96ZW9sZJAXBCjfPnT1pEQcpGP9KSEkP2l/iOnJbp9Lwx8qkdmBJz980306ZILKSabZ+c8+fMVw0kvFctdswMDSeG3pnoaeWmlx3+uSq4LIJSxXO2B1zULWM5J4tvDXZCyTtcStK5yWOa0b4PQg8QXN2y7KY4gfckms61BYoNXuYYlKxrKwVfIZ6VsHwmsfB4YW8IAM10XHsNhUOrn/Ca+Sz6bBy1C+xr4GDmluge3ZWGRijxnpS1CkEYrn2zrUijarZtCyyqPpfIOOzCm2ga7/wCXdVcXDH+F3L/zh2gc7eKP8p6N+vnVvlsFu7W4tWwCfqU+TdqpF5bGOV1dBjdXUj9QatVyU1tZTtg4vdE1cYYBgQQRkEbg0XtVE4N4g+Sli4dv5D4LbWM7nOP/AOlj5j8p7jbtV771XnBweGTQmprKEsOdSMkZ7iou4h1WF827rMvYMM1L4yM0g0KYRE2lzqpmAkswDnBZWK4H3qWQlV5VJHttQAoz+lJ8iy15Oqr+tLkMEFnNd3VzDa2sC801xO3KkY8yf9OtV3iDivTeG40W78S4u5BmGwt8GWX1PZF/zH7ZrMeI5eIeNZIxrGoLBZxtzpptrkQRe56u3mx+2Klrpc+W8IgsvUOEssV8RPjTeyWj6FwOJbOxuQY5dVYcs9yOhEf/AKaevU+lZID4UCopP4hv577mu/FnPbcUm1jbnFqixkcnKFONx/zXIqJIonXfnYYrc01Ma4fSjm9TdO2yW99HDUrhsERnAH4ge+e1O+H7T+IW97M5I+Wi5kVT1bsT6Co/UrdlUSIcqPxDvnzp/pGotBGLeKEL40QjkkHZQd9vM1M+uCuuJ/USVxq0TcEadoo5/Hhu5riQHoFKhUHv1qHaQ4yDVy4rtrZ/h3wzJbxwx3hkuc7YMiZHXz3qjEzRvyTwsmehPQ/elTJNcfL/AFCvi4ySfwv0FSczuqheZnPIPv3q8NA1p8PrW50+MyWKP4GoKDh1ycqc+TdM/aqPKzIqyKcMpDAmrDbXGrLwXeqIGSynkiWViR0ByoA8iaVi5Q1MsZ/IeQabbahGW0q+Bcdbecbj700u7S9sv/5VrJGv9YHMv6iouKeSCdZonKOpyGFWI8YziHl+TRwV3DN371ar1V1b4eV9yGVFNi5WH9iHDhhkHI8xQztUit9w3qj/AMyCTT7g/ni/Dn1HQ1zvdKurK3FzzR3Fqek8R2/9w7Vfq1sZ8S4ZSs0ko8x5Qx32omoGiO1WsldBHypJpRNJNAxzlCQ0gzvtSL21W4g5AeUjofL/AIpNu48UU6P1CsRmkQMVpgnxuoOOUU8jj5ysYGFHbyrtLDznK7ONgT0PoaXbR5QsRhs4K+VJcCwdEUFgB0pGpoHsC2N0Oa7KvLLijuYzJZyKp3KmkxyNt2CWWCckn9KaXM+UwD9XQ0iORVgwzHOc0mKAzzH8q0LfhCyWDQI7a60iS1kJyWPOPLPQilaX8zbS3tqZ2iKHDyr1wN9veo/Rop7a6nug+I4APEGPxAnH/NSWp3UcKTQBMtOSzMPLtUbXgni8JMgLe0utS1AxQK0sr8z5J+5JNei/h/pps+FYLYoMxxId/M7ms94U0mzThJJobeVLq7kEMzzLgkZyQv8Alx+tbJw9GqWTNjHMcD7Vm6y3ctq8G16Zpvb+t9tEopPKK7Qn6q4EhTjyrrEw5xvWYzbTFxpyXb+u9V/ifTBkXsa/S/0yY7HsasrY8VWHUjFCWFJ4HhmXKOMEUoy2vI0o5WDJLq3SaF7eUMAe6nBUjoQexB6GrnwbxS+pc2i6rIP4pAvMsnQXUY/6gH9Q6MPPfvUDrmnS2F80ZGQOjf1Dsar91afMeHIkstvcQt4kNxC3LJE3mp/071dcVZHkoNuEso2vp3oAjPWset/iRxho5EOr6VbaxCDgXFufCkYeo6ZqZtPi5YTxAvw3raynbkWNWGffNQvTWLnBItXW+Hw/yNM5dsiqDxBx1I9xLpfCpjmnU8k2pOOaGA9wg/6j/sPWoDWuKNc4kja0aJ9J0w7PbpJmeceTsPwr/lFMYYwkaRQosaLsqKMACjroxzIGd+7iPR3tLACWWd5pbm5lbmnup25pJD6n/TpT6QxWlq8pH0xgufYDJ/tXW0t5HIjijZ2P5VGTUdx6J9F+G19fShEkuHFlCCdyW3Yj1Cj96kzmSXyC0oQcvgxOW/e91C5u5CxkmlaRs79TQ5yijlcovMCR2pin0uCNsU6m3hHLvzbCtxLjByu5vLHF3c89s7Ku+OgORS7aSOCxhhKH5kHPMD+U9AfXvTcRRmJYWblYkKWAz1qa+WiuJ7OSML4bMImOOm4xmgaSDWZcjniKz1NrfR9RmB/h89pyWRB/CEOHB8m5t/YimVnfGKZIbnDRseUkjOKtfHvEemPw/ofC9gEkewLSyyofpUuMcvv3Pl0rPrl+aUKNgOtBR9UOVgk1KULHteeiw6rpNmLU3Ub+DykcyD8Lb9vI1w1HVrhNDk0y3idLSadX52yCSo/Djy710bnvODzNz/XEy4GfxMDsPvVr4UgtbzQdWsNSsJGee2cqPCyCwBKkk/gINKb2rL8D1xc5bY8ZM9hkLjDdRXcNTNWeCbw7iNopFG/NtmnQ6ZByDU6K2DhKpWYlSRncVe+DJGl0UxuOdWcqVYZBPcexqleE88iQRrzSOwVQPOtD0mNdNtYIIwFaEjcdznrQWPjBNRlSyVXU7b5HWbm1C8qI+UXyU7gU0JqxcXIDfQXQAzIGV28yDkf3NVs1raWblWsmbqq1C1pANFQz3oVOVyOjblPtT+NwyAimLKQ2a7275PLmsZmkORvkY2onVtpY8c/Qj+of996MUeKEdHPxk2bJyTjHfPlXfm2x2rhJArOs23iIcjP5vQ0tJFkTIztsQeoNIdFblUpdSIezEU7hHIi469aGpRFdSLDGHAajHTNKKBJrR7+wt1uYrmHmM4CsS2MLjBwO9HZaa01rc3DS5YK0MZO+w7/fpTDSbKG+1bFyvPDGhZlzjPYU8W8/hNvdW0weUxsRDgbHI2ye1Ry7eCxB5S3dGt6WsN5bWVxBKJIVgUpynIzgD9sYrQ7KD5e2jiHVV3968/8Aw54mOl6lBpt44+TmcBWb/pOf9Cf0Neg7VyxOR96xNXXKuW1nTaG6N0Ny78hTfTIfWlQv9Qo7kDwww7U2ikHiAZqt2i7nBKuP5asB+E5zXTO1JQc9vjzFBN0GetRhDHV9MTUrEpgeKu6E/wBqzu8tHt5nicFSD36itWx61Da5osepQmWLC3CjY9n9D/vUtVu14fRFbXuWV2Zm8St+IZ96XFGsSYG58zTu5tJYLgxTRsjqcFWHSuQjOQMHJ2HrVzOSnjAIYDNMEQZLHYVOafoLXM5EZARDymQ9PXHnUjoOkp4BuHBAIwvmfM1PpEsMISNQqqNgO1V7LX0izXUu2N4obXS7Xw4Ey7bZ7uayv/xD36Wt9w/wujZa0tmupsd3kP8AxWraSFu+KbczNiCEtM2egCjP96xvjjS5eOeIuINaU/8A3KXZhtiT1RFA5fbr96LS491Sl4IdepSocIdv9uTHec996cRS80Sx78wbIPpUzNwzI+jS31mXMtspN1aSjEicpAZlx1UEj13qvoeSVTnvW8pZOSw12On5wo8MkPkYx51JW3zTTpZklFmYyFx3AG4H3qKadUboc5yCKmDqCNp+nnDRTwZTAGeZT3+9KQcGh5xXocGicQ/L2zE208Ed1Fk5KhxuCfQ5qAOzcp6ipTWP4jNrdw2oRyxTQlYWR/yqF+kfpUZNE5+pW36b09be1DW43PCwOjLJLZiyQqFMniDJx9XLitV4N1SIcIXDSsWZIsykDJxy9/WseUvJyqoPMTj2NaZwmI7fSbuLxGy/1MoXblA23981FqEnEsaOTU+CI4j0pbiz+YjUFkH1Y8vMeoqjtcXds3hlwQOmRkVpXFHLHpaojBed8EeYqp6bpqXl8ss8fPGpyq9nPr6UcX9OSK5fXhErw3YypbjUbpQJXGI1x+EefuasCNgikAHlVc5wOwxTbULsWNkZurHZR603ZKsRQOLCp0+0/q+YP7oaqx6VKlpNS4fsllnKOb3l8QjPUEf61HXdvNaXJguIyjj9CPMHuK0NHNJODfJQ1kXJqaXByoUXaj6VfKI0kUq2CKJDhwelSLQq6/UNqay2xXdPqA/WsfJpYO6nIpVcYXDLgncV2B3oRIMj9K4vGVfxIsBv2I8jXbak4pDkZqCiSJJ8YKHDA9RmkRwtJESCMjbFPbq18e3YAkHsRXGxBUPDIMMvalkbA3tBcDV4khk8KTJ+o9h396n7i6toLe7eeMO8gQeGenNjH6d6j3Ph3ETRsiOzFQ7DONqcXlh81oj6xM/LyRYVY/6gcb+lRy75Ja87XgbWUMbMyncYrafh7xg9+ltoN8WN1ECEmP8A1kA7/wCYfvWIWEpZmwewqVt7u5s7uK6tJmhniYPHIp3Vh3oNRQroYffgk0mqlp57l15PTsgDoVPQ1FhismemKb8G8U2nFWiGQFY76ABbmDpyk/mH+U9v0p3eIY528s7VgbXCTjLs6yE1ZFTi+GTFjMGhxncV1i+nnTbZifbO9ROmzHxCmdjUnzFbkbfiG9RSWGTrlHU5LUWRSutNbp2QAqD50yHK/wAV3lhGiROoe5G/MPyD1/2qB0XT5dS1BZZOYA7gH8iefua76laNNrDPJHzlm5lJ339qt2laetjZhSP5rbuf9KsuShDCKu1znljqONUjVFUBQMADtTbUJxDbEZwSP2p6VquaxOXuRCpyScYqCCyyeTwhoLyWJZ5o3KZjKEjuD1FVjT1EdrcLgczXUrN7ls/2q5alpy2+gvhSX+ks333FVsWwhDSBdpDzE+ZxirFbWGV7E8or2r6dH438ViHhXCKY3cdGjb6W5gOoAJrNeIuErvSp5pIIpPCjcq8Mg/mQ+jefvWxX29lKqgZ5D/aqvqd5b2NpczukKgRo6JHKJQSyjAJH5idyDuOhq/TbLHBk6rTwlLnjgySKFpFL/lXGas9vbMZvmUWNlCFED9ye/p71GXKeDAsQxzucnG25qQ0+5MqeHEkjGAZccvTHb3rQfCMevs7cTazFqfECckcsYjgjicSLgmQD6if7CoWUgDPSkXF0b6/nuOTkDvzAZ6URYyR8uPr6Yp4LbFIGybnJtgtJU8ZY2R25nLDl/bNXnTdRMOnTMzIojjK8wH1PnoCfTrVQtLNob0huoQfvT1He6f5VHMcOSZXH5h5ClKKfYVc3Bjwy3WvXweRn8CP6QfP0H+pqdsY4IkxFykrtt0HpUObhY4Pl7bCJjl28vKpPR4z8gzeb7UzXAcJZZJZ2zVP1y9N1qJjViY4/pG/U9zVk1Cc22nyP+Y/SvuaprRs2XwSPOngvI1r8EzpSwX+jTaU8vhSf4kbnb6gcirFd2UWoaesF0f5gUYlHVWx1H+1VrQdPM92LqQfyoztn8zVbc7b0MuHwSV8x5RSbqyuLG5MFwoDdQw6OPMVyqwcSIDDbSk7hin2Iz/pVeO3etfTWOyvL7MnU1queF0CO7VgAxGPMV2yGFVkSSoeaPOKfW2oFMB8rnz6VmZyWyV5Q3UYI70oDeucciTfUpw3cV0yc044DRZ7GlUlhTCDDcrVzngWRuaL6GH4T5entRM5CkDejimDjAbOKQ+SLvbjlHhOh8QHdWGw9anoZ2s+GWW4iMpEbFowfxqeje3nTC9tUu4wOYI4OAx7U8vIbKPSPEmWRZoIDAUQlck9Mjy71HMlq4yyG05+WTlOwbYVLAVA2wJxvjFTMcnNFzVIQol9D1m84f1uPVbB8TR7FSfpkU9UbzB/Y71uumaxY8S6JFqVix5XHK8bH6omHVW9R+/WvO5bAzipzhfiS54a1kXsIaW2kAW4gB/xF8x/mHb9Kp6vTK1bo9o0dBrfYltl+F/4NysmaO9XPnipi4cqY5T+EHBqt22p2d/aQalp8yzQS/Urj9wR2I7irKUWWyYHO4yMVhzTT5OohJNcHdG5lBB260U0Ykj5a42MniQHGMqcY9KdjpUeMMPJHR2CfMCZ1BdenpT1djXXlB7UllxSzkYTMwW2dicYFVawQ32uvOy5jjOf9qldeuTBpojUjmkOBSdEt0j0/xAPqkOc+najjxFsGXLSHN5GLiwkiYEgjt51UpoWFphxylc8p7H0q6lKj9R8GCxkkZQSdgMdSaUJY4Hksma61LNFpc3ggGV1Krk4A2JJJ7YAJrO9b1P8Ai+tyzxy+JZq2YCIRDzDAAYoOh/8A3UzxprUOpX/8Ps3Jt4GPiupwJH6co81HfzNVcjbAre0lW2OZHLa+/fPbF8Ij78/zMg/hGaktImuLpoltLfmluJQjKNt/MntUTduqSPzHO/8A2KmuFZrt0aztAi82X5jtyDvk1Ys6yUqX9WCO1NUTWLpViaPEhUq2MgjY9Nq4WKiTVAOYAAZx/VjtXfXPFtdcuYrpEEmQ2UOQwI6j3qPsIZLm4JGVGd2Hb29adPhAy4kyWzJPfyOhYRt9G3Vsdcf71YzaacnCFzNMGjvoZFiREbCrncbd8/tTOzslS2eYMUVAqA+Zzso/cmmM4Mt7LM35m2Hl2oe2Sp7VlrsQrHNW3TE5NLiQjBI5j96qsS88oUdc4qdu78WsK28LASlcZPRR/vRS54BraXJz1e7iR/DP1kDAUdB6mo6zsbnUph4mY4Aewx+lHCtqH57iQyHOTipP+NwQrywWxwBgZOKXK6FlN5kyXgtUggWKJQqKMAUJ5I7aIyTSKijqWOKrN3xPdRoTzJCvoMmo2FbzXNbgsruSaESsAgfZmz069M+dBtfkP3V0iV1jUba/gtvlZS4V3ycY7AVFdKv118JjbWqy6ZqfNOq4MM4+hj35SNx96pWp6bqOjXny2qWclrJ25x9Lex6Gr+jvr27U+SprNPapb5R4IOa18GUgfhO4pLwZTlYdakJENwmCMEdDXFI33Vwciq+AiMjmntz9JzjsakbfVFfAfY+tc7m328QDcdajmiZZPwnB6bUL4EWOOVZBlT9q6daraTTxNlSakoNSyAJRj1O1IfI9kTAJUe4rjGCp5lpxHIky5RgaQYzFJuDyE9cdKQhZZVZWJ25t66ai0k1jzM/M6qEBbry/058vLypbW1lILcSi4hTlxcSIfELHfDKvbsMfepC+0yG1v7mxZzIsLCMI+zk4zuMdt8/agbWSWMZYeCs6eqMkscgwyt9xTpEZCQTlT0NcLyC4gu/HT6QMK+R1HZjXUymLHjRsoP5hup+9Hkiaw8DiNgwKnqKIMULAAHYj29a45LgPF9RHl3pbFvAMvKdsbYpCJ7hTiafQNTBkLyafMR8xEu/L/nX1H7ivRGkXdpqWmRXFlcxXETKCHibmH/FebdPh05dAupZ4JmuedFjkVsIik7ll6822BjbB3q2fDziCz0rXP4Te4js7t8RTg8pglPTf+lunoazddpt6c49o2fTNZ7bVc3w/8GzQEW2qvAc4c4H9x/rUly4qt6imo283jSc80an/ABeX64yD+Ydx6ipy1vUvLdXxysRkr/qPMVjM6LKO/Ng4oMwIC922FcnYjeom51NbWSW9mz8vAOUAbl2Pl/ako56BckhjxBIZdXWAA8kQAP3/AOKm1eK2tw2Qsarse2Kg7C2vOJ9Ua5WF7S3YjmGfqb79hVkk4MsfAWOWOWUdlLtj9M0csJJMGOW8obJq+mmIvJdLHgZIfY1lHH/HgupJNM0aXplZJ0OyDuAf6j+1H8RNe0Ownk0Hh61SW6GVurwMXWHzSPzfzboOg3rMSwVQioQPLFaWi0cf/JIx/UPUWv4Vb/NiQAowBgCkO4DiIH6iM+wpMkr+J4MSkyHqSNlpCwGORnPMzEbsRWsc+Rs6eIxGe9TWiyXFlLBJZoGE45ACcbjrk9qhXZucoiF2wTgDpT/SbgxabcmbnZW+iNE2IYjrnsOmaCZJU8MLiL5i713mcxySMAmYmypx5VKaPpv1xWsQy7kDPmfOozTbUqXlZST+HOP1qcs52tnMwJUqNm8qW3C4EmpSywtYvTaSpp8MnOgkyu2DuR19ab6hLG2oyGIbHr79DTSSWO+nWbwi7iQtlsjAHQfenNxK9zMJWiijAHKqRLyqoHlSisMOcspnOJnjk8RT9XY+VExLMWY5J6k0GcKD2qNn1PB5IU5z0z2oyDI+eVYlLMwUDuaZy6qXPhWqc7H8x6fpTC4WeQr4jFnY7KOgFS2l6YAheQEeZx19BTCXIzis5buVOcmSWQhVB8zsK0/jDQDpK6Lb2j/zYoAvMeolTGSD6+XpVBjVoLzk5TlTtV0Op3Oqw6VHcO0kkTsoZupHqftUdie5NdFmhx2yi+3j9TQbHiBLnTYJrlCHZAXaMcyc3fBHrUjqGsWnEZJ1G2sbwFRE3Og+vG31DufWsp0vULnS7maDmYxc5yvlv1qz2+q2NyMvyZ7hhg1VnplnJpVax4wf/9k='),
    8: ('Argent', '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'),
    9: ('Undercut', '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'),
    10: ('Violet', '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAQDAwMDAgQDAwMEBAQFBgoGBgUFBgwICQcKDgwPDg4MDQ0PERYTDxAVEQ0NExoTFRcYGRkZDxIbHRsYHRYYGRj/2wBDAQQEBAYFBgsGBgsYEA0QGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBj/wAARCAFAAUADASIAAhEBAxEB/8QAHAAAAQUBAQEAAAAAAAAAAAAABQECAwQGBwAI/8QAQxAAAgEDAgQEAwYEAgoDAAMBAQIDAAQRBSEGEjFBEyJRYQdxgRQyQpGhsSNSwdEVYggkM0NTcoLh8PEWkqIlNLLC/8QAGgEAAgMBAQAAAAAAAAAAAAAAAQIABAUDBv/EADERAAICAQMCBAQFBQEBAAAAAAABAgMRBCExEkEFEyJRYXGR8DKBobHRFCNCweEzUv/aAAwDAQACEQMRAD8A+KRS96Tal9a3jNPd969Xu9eyTUILSg0nbavdqOCC0opBTgKOApHgKdjFeA3p2PWpgI07dKbmnN/6pVBByQPb2ofIHzGgc3QZpfDYKcnf1A6VPBDNc3Igt4XmlbokYyaIXunx6IYhrGJJ3HMLKB9wPV2/D8hvRaSWZHSuuU3mK29wNBY3F/deDa20tzJ3Vctj59hRc6C+nWhku9eg02Q9IYJCzfXlNRXmo6lc24hjWPTLPtbweQH5nq31oaLaM7qrOe7dB+fU1TndHiKL8KlHnd/QJNrkjxyQX2o6lqUWAFSNhAG/5m6mh+SZea0FxEv/AA5G58fUUogiReeQ4UepwK891IU5LOD/AKiMCuDbfJ1+Y9riZIx4jI2fwnfFHtL40URLa6zbCUKhjhvOskWRgc3865xkGsfNBqjdZX+SACrTxvHZxKs5mk5csrpjB9M0FNrgaMmuAp/jxsl+1JbW/wBrwyqyjDQSgbn5dxQVZ5riAmaVmY58zH8I/wC+aqOs3OZ3icDHK+R27H6U6KWLwTznMaKvMB+L2/Olc2+RHILafq19p0MiWc8kcMuz4OA/yH9aaNXuknJtZZopmG4hBLEe46fU0GF1eXM7eAMk7c2NlHtRTS9K1CW7WGGQtNOeQIGxznsMmplvgMXJ7IvW2s6zDLytK0/P+CVRIfz7Vp9FuoNRmNvqWgwsDs0kb+BIme4zWWWKaNyrPIrKcFc8pBqXmz98lj6scmnTaO0JuPJqb/gC+S3a40u9W+XqI5l5JcfPoTWPu7O5spgt3ay27E4HOnLn5HvRK21K9spA1tc3CgdkkII+Wdq6LocllxJorW2ozpdZ+95eR19yOx9x1rtC5rZglo6r36PS/qjlBklMYUyMw9H8wqIRqzkEhCfun8PyPpXSdT+HULh2sLtYnA/hgp5W/wCb39xWJ1HQNY0pyNQsXSPtKnnQ/Uf1qxGUZcbMo36S+n8ayvv6AsqVyrDBGxBphFWkt5Zn5IhztykgZ64GcCq+xrp8GUmu64G49qQjFSHYb9qYd96mAYG49K9jalpOlTAoleNLivUCDcV7A9KXrtSY7VCHqWvGvd6hD1er1eokFpRXgKcB6UQiDOcV5Dzc2AQQcYNSBQcYr3ICc46UWmuApo8AetPwTsBk/tUkaRscBpQcEheTm/Udveiunw6AoR766u7kfeMcEZUE+7Hek82PD2O8NNKW6awCra1ubq48C2gknlO3JGvMa1encCysvj63epZxLu0cZBYD/Mx2WpJeMtO0+0a30XTY4ANiWwoHzxuazeo8RXWqoPtl27oD5YYxyr+Xf611eo09a/8Ap/RFiOmhHeW5oL7XrWyhbT+GIY7K1+6bsrmWX3Hes08wjkaSNHMrHzTynmkY+3pVZ5pGxhfDzsFByx+Zp8S8gyxyf2+VZ1uolZyWfkSiIM/PKeZj6nNOPT09PenQld3deYD7q+p/tSNktnqT6VzQ2CEQRl+eXzt2z0HyFPkcKuB9AKbM4iwH+8eijcmg+oXFzPKbSzHmH+0fPT2zSuWAN4JLvWILZyhHjOPwKfKPmahHFd8AqPDbvEv+6ZNsfPrSW3Dy8niXcp+S1bfS7GGIBEjVsZJl8xFc/W9xfWM/xKG7JkhDKv8AIxyU9vcVTks4Wl5lbliJy0Y7H29qmSztnuf4U6o3coMADvR+0OlvoVxcNbxyqi8sZb72B3HzPemSzyFR6uQFJdCwk8IKsccWA2Bux/lH96jh4puLW8WeG2g8hyqOMjPrUs2jT6iZLxZcqw5lTG/N6UDmsLuGTkktpFPypJOS4Ek5Lg1dnrltrE+J4zDNnLBTuw78pPf2NEL+zW01KWG1u0vYEbyTIvIWGM/dPf1FYBZZLedWVPDdDnfrmtql1HLpC6hkhMAtgZx2OflTVz6uTpCfUt+SQDlKl1IVtxjuPb3opZ6ja6bfxXkE15GI2BEygMCO4Ze1DrUxXYCmfEb7rIu4B9f71I8E1lcNHIvK46jqCPX3BrodU2t0by545swqT2uZIXHnyh8hojacWaW1oJLgv4bjOQnOpH9v2rl6SyQT+LaqACPPEd1I+XpV7Sr46ZMqXltKbK4POPDbDIf5429R3B69DQyy1DVTzua3U7fgrUQLiG5gtJT5lltn5MH15elY2+0W3iuHa01e1uUVC7rECX+YX961us8C2WvWkGp8NXsImZMyQsOWOc/zAfgfsR0zXP1+0WF7geJb3MD428rIwqxVmfDKOtkq3/crWH3RHLLG0fhQoeU7l26t/YVB23o9JBZ6xZPPbIINVTzSWyDCXK92jH4XHUp36j0oEPzqzDHHcybU8p9uwmKQ0/HrSEelOcxle96UgU39qUU9SEZpw3r3Q1CCV72rxNeFEgoG9OA3xXgKcBRQUJingUg608CnSIeArxONu9Kdh79vc15VPXqTUw3sg4xux4AKFR0PX3+dWLTSYLwPeX0jWum25zPcLszekaern9KuaVpyz+Lc3CD7NCpMkrnyIf8A/o+3QUP1LUpNVnjhgQw2EG1vF0+bn1Y0lzjVDLW74LVNTl65FfUbtdS1DmtbKO1gUBIbeMfcUdMnufU00RrbR8xHPI2wHv6VIBHbxkDdu+OpqNEdrxnc5IGMdlPpWW228su4HonJ55Dlj/5gVIEaRsY+QpeXHzqVJBCgIPnP6VMDpBFbaCC05ZzmV/wruVHpSSwG3tuZ05OY+VfxN9arQ37rPGURAy75Yc31qzOLi5vCkreYrlwPwL2X5nqafY6LHYDXZMa5U81zMeUMPwjvj5UkNpHbwc8mF5eij+tSFQZmlJyB5EPsKYImvD5yRCP/AN/9qU547kKzXNzJi2wFGxlPRfl6mmX9ueRVSQBV3ZmO7GiLlYY+VV2A2UCqJti8qyzN1OTnoBQaA0QfYjb6NI+5muGWNc9gTTbeaQC5+yoDDBF4Qk9CT1+pq1cXAuUtigIXxSwHsqkirWjJCdEEBUBnYFvfehjfYiW+ECYNSuxHJBK7EfeB6EgdRRKOaNy1tMecEeUn8Q/vTtU08FiY1CuNwQOor0NuJrKPnGCowD6EVEmtgqLTwUL/AE6Oa2bmXLx/iHUqe/0q7wcg+2TaZeEeExVgT0wTyt+4q34azWxH3WwV/vVDQ1I4lhjPVldD+X/aiopSTIliaZUv7W74b1aZrZue3WQo8edhg4/9GtTp99b63pCQlh4i/wCwc9VPeM+x/f51Wvkie4kEoDq+VYH17igItm0W5+027O9qxxLH3UdiPlQx0P4BXoe3AVcMhwfX6iiel6jFAjWt/b/abGU/xIs4ZT/Oh7N+9VBIjtzuqyhxnPrnuKY6Iic8ZYgdQaYdPDyjdcMTPpmsrpvjm4068Be1uV28w7H0bsRVri/hhNZH2tQkOoAYW5GyTjssno3o351ltBv4FJt1uzCWZXQTfdWQdGBHT0PrXVLWcXVmjSIAWXzp137/AEqJuLyi/VGN1bhLg4M8VxaXbRyK8M8T4KnZkYf1plw5lnaYqAzbvgYBPr9a7DxTwha63bfaLMJBfxrhX7SD+Vv6HtXJbm3uLC9mtL2FoZV8ro3b39x71frsU1nuYOr0c9NLD3i+5Tx6001PcW81rcPb3CckqHDL9M/sQaixXVYayig008Mjx7UhFPIpDQaAM7Yr29e+VIaUmD2Kcor2BmnKKYguK8xCoXOSAM7DJpQDTwBTJBEAyAwOx3qQDIpnhqfu5HsDUqv4eEFtBKeuZAcj03BqNyXYeMYvl4EZAp8x36EHt7UV0/R3PLcalJ9itjuDJ5ZHH+UHoPc/Sq8OqXFtHiCzsreQf76KLzj5Fs4PvVaKBL+4ubrUZ5VihwXkeTmZmPRR6sf0pXZ5aW2SxXXXKWc5Dms63ZyWaaXpca/ZE9Put6ADuO/uazgEjyE5YHuf7U5p/Fk8K1gEMQ9N2P8AzN/apgnLFyrjODjJxVK+2V0uqReSIVGWyi7KcL8+5qVUCjABzSAcoACgbbD0p5ZUQsT06muOA4PFcLzDc5xUDOA5UbkdT6f9/aklllICAeGzeY535B6n3pYkAHiYwiDKA9z6mgRl6wVYSZivPIMcqnu/bPsOtGB9nsdJuHlk57jlLlz1LUDjDKgBOT3PvSXM/gWill8RmYFVJ+8fwj5Z3+lMng6RlhFcqzyCJyeblHOB+Efy/M96tKAo5QNgNvaiml6ay2sruOa4ZCRzfiY9TVa5tJreQeMuC3TJGTUxgHS1uVuVdzjJO1Vb1B4HKTgEZY+ijc/2q8W8P722aq+GNQhlxnkZSu3oP7n9qDFYLsJGu7RJSuDzygfVRirlgGSQR9ABkVBpcDW8MsJ38KfBPsRRCGLEgPQod/f/AMxQQIrZBJXRhHz7sMg5pPsyl5Am2RzAD16GoOakWZo5AQcZyPn7U506vcYw5Gz0B2+tUrNDHxdHOo2EbyEe+MVdlYPE4/F1BqGNkBknXr4YXPpk70rFxuipBembU9Rt5DmTxBcKP0YftV51Dp90Eeh70DtIJf8A5J9ucERO7AHsR93+tH1P8MH0YqfpQjutxYboH20q2k40188rEtbsfTun0NXVkPUfI5qhqtsZrJnjyJYm8SMjrVmwYX1gLtMgkeYf5u9RbbBjzgc8TR8s0WTEx5T6o3of6V1Hhy6j1PTbaZJmt5h/AkZOiSY2JHQqw7eornVlNHbzt40XiwSLyyxfzL7ehHUH1rT8Psula/FAsxn07UYyscwGMkbrn0YHqKOC3ppdMje/aLi2k5LyAqQM80eWDD1A6keo6j9ap6xw5pHFenLJ4ieKoxFdQkMV9j6j2NEkni1PSmgu0DdUkAOCGHcHse4Ncq1e017hO9e5t76SWIzlRKGKNykZQsRsSdx8x71Itp7F3U2KEPXHMe4L4k0rVNL1iRdUUuxA5Z1B5JAAFBB+QGxoP79q2kHxDvZEii1TTYrzlJ3bALZGCDjr9RVC7v8AhG9YyHQ72xc9fskw5Sf+U7Vdqskl0uJ5y+imbc67Off+TMkU0irtx/hwBFqt6fQzMg/RRVIr5gxOSK7Zb7FGUUu+RhBBphNSP1phHaoKPxThSU4fKiiCgb1IozTQPengCnSIPUUsakgse52+XalA5hgdTsKWEMUC8jcw2xjfPt606aTBhtD1iaWQRxgFjk5boANyT7Cq0tmylVEhAOXXxNjy93b0z/YVoYUTSI5XulV5Qn8ROoBP3Yv6tQSeZrtmJywc80kneQ9gPRR2FVdY1snyaOnp6I78sijeNVwikIvqNz7n3NK3mcNKMknZfSmPIIwFzj0Hc1ALgrcHxGBCpzMqjpnoPmaoNlnOCea5W3UvJux6AdTSKJTGskq5kc+VOyimw2pe6EtwQXA5m9FHpXr2eWWQWtsh8SQbnpyJ7ntmgT4nvER2JXzhmwP85/sKn2LLGR+IEk9zUcNutuFUEPK2wHYf9qsBS1w7E/dHLn1Pc1ApPuPUkkAfiOM1Vik+2X5uR/sojyxj1PrS3jmK1IVvO2IlPuep/KpreBIrdI0GABU5YXuwnYXQivElmY8sYJ69vQVbieK6luLqfdyv3fQeg/QUJA2GRgHeniQpsD94cv8AejkdSwR3CSG2nuXX+GoPmOwJ9B8qJaJZeLoPMoAynKPoP/dC9avnOjrAQoUkRqqjGST+9XrG6aCyFmuw5sHft6VFjJItdRRt7b+JeOPus4Qj35cj9qfbxyTXLqilmILYHfpmr0JjS51JCQVkVJFPbIHb8jVpDb/aJZ7BgxQJcIo68rDDL/56UcBUMgcgjdsgZIBx3Hao5QS0ZH839K0UNpFq9hcFGIzOzxn02A/Wh76XJE0QkZQWk8Mgj7pwaGCSrfYFnOarxKyaAiu38S4blQewO1E7mwuYX8Ir5mPKpG4JNR3FuxnW3jTIiTCE7Z5T5iPrtQaFcWhos0eKO2QHqqjHrkYpQhBdCNudt/Q5or9heCUzrKjpA6Esvc5HT5ZocziSeZkOR4r/AP8Ao0wXHHJSdjkhuo2IqXhjFpJqkMic0CKszp3MTHlcj3XIYfKvXELECUD2b+lFuFbKC54iSCSQA3NvcWjoe2UyM/Mil7krjmawDdVjm0nUihIflIkjcdHHY1sdGslbVIIUJ/w3Ul8e3P8AwZsZIHp3oFcomrcBrORy3emMIZs9Sh25v2/KtH8PbxLjRWsJgDJZy5XPYHof3qPctURXm4990bXSrY/ZZJ5yFflaJz2MsfT/AOy/tTNV0qHVdKlgeMSCSMry/wAwO+M9j0IPqKqWWsxTalfaa6tGZCcc386fiH0INEbOQvbxsMrzAhl/lcdcexxmkaNNdMlg4jqmlT6TdCGVudWHPHKuwkXOM+xzsR2NDgxyQc5B3PrXTfiBp6R6HNcLCnL4ouFlJwVJ8roP+bZvoa5jy+YktjA/OtOixzjl8o8frdN5FvQuHuhCT1pp3NPYEbU0iu7RTRGRTDmpT0phxSNBHCnAe9IPanCiQUsqrzMQAO5qQdajKuw8rDp0IyDSxxOjqwRAO6hiAamZLhBST7liKOa4nMFvE8su3kQZ/P0ojFeRaTMxYi6v418vKcxwHp17t+1DpL3UVhaG2aOCFuscPlLfNupoJdlogHeN+UD0yM1xs1Mq91Hf4luqFa3zkL3F0ZsePMhAyQvNtv1+Z96pTaiEHh2+Hc7AAbUKglkuCXVMRKcHPc+lErS1Cjnzlj+I1ndbm8stpt8E0EZCNNcHnkI3PoPQUtlCWzPKNyfEx79vypJxlkt1/Fu2PSo7u9SG2LYLLnlCj8benyFF4QdkStel7tbS2jDl92djgYq8F8KLLyF2PoMZPyoXY4Hi30vMuQBluwHoPSrtqs1xP9okyARhE/lHv71ExovJPbRMHaeQeZug9B6U8lUx7ZdqV35Iy35D1qnfGRLJwp88nLGD7k703Az2Qkam6mhklH3Bz49Wb+wq8pznHQd6iA5ERB99+nsPWp1XlUKOgqESPE4UknYU0MTMQeijH16mlkISPLdOv5b1DJILWwad+oHMfcmoQHXU/wBr4jtbbI8OJ8kerAZ/SjCHdsetVbLhu+t7Wz4gvf4a3LOsMbDzOMZLn0GTsKuqp83zNJVJSy0RQlH8SK15PKkySZyPKT7hf/dT2NzJa3HPHgOAYR74PMP0p8kSyABhkYINUUHKjO7Y5VDb+qnB/Q03DJumG7e7axvWltX/AIUh8QIem/UfQ1fuNWhu0Lm3KOjJKADnPL1/SgPMC3IM8y5YD1XuPp1qKSeVCBHjmPTPT5n2ps4OnmNILahrERuWuo5E8CDyxnrzSMOv0FQfbmkkjPhnl5h4ZbYhcg4PzOT9aAW3NceECoCjIRR03Pmf5mjTEu+4xjbFDqbB5jluXb65b7HKpZVZ7gEqnQAb/wBBVLQwlzBcWrgBmBljY9jUFyRHbTSE7hP1Ow/eo7RvBnyMjHk/IVM7kcsy3NLLb2o4XklhTDSRB8scnIOf6UF0nUTBx5FfMvInjxT4HZeblJ/WvPPL9kRQ5CcrRkD55/rVK4Ux6haEHHkET++d/wBwKktwynumuwTs7lLfj/ULO4//AKl7JLayDsAzHB+hwau8MSTaRqeqmYESQ24ZkzjJV8H+9Z3V5gNRnvEOR47eYe9GpLpQsd6qsDc2UiSt/M+Bn+h+tDuNXLEs+wf1+eXT531WzOSjxXae4+6y/UVp9K1q0vYAYHJjnIljI6oD6j2Ox+dYezuv8T4P+zynmlhjaJs+hGV/VcVBworXumXdjDM0F1bSeJbyjqhI2+YPQiiy3C5qaa4Z0vUba01jTrjRtRXAkXt167OvyNcb1DSrrTNbk0y6X+KrcoboHB6MPY1uNF4sh1hRY6nix1KBynMdl5x1wf6Ud1PQ4OJrMBlSPUrQgoc9e/KT/Kf0rpRb0P4M5a7TR1cFKH4lx/Bx50ZXZDsVJU/MbVGR3q3e211aXstvewNDOrnxI2GCDnP5e9VW2rUW6TPLyWG0RtTG6U9qY3zpGBDhT1xTBT160UgkijFSgjvUQNOBrohWJO4SM5z8h1PsKCXUd3dOFVCSxCADYDPajkKlsyk/e6ewqy0cbWDSSlljjJzjYuxGAo+mST2HzqpqK+qPXJ/Is0Lql0rtyA4bZF5IITzIhxzfzHuf/O1EERY88vRepP6mmxxiJAwAVfbp9KrSzsZvBB/hoOaQ+3pWfjBpcCkeLM8jEqhHmb0HYCqSxvf3aykBYh5YVPYDvV5o3uIFjB+/u5HYelKWgtGZ3deYL90HoKXHuDpzyWREHYQ+F/DTHKT0J9TVyPkCuiE+UYPuT1oLY3Ut9deOMrFGTyL64HU0bskwh5+pGTTJ54Hi88DpYl8o7qc1TuwviR858seZMfoKJheaVvQnAFCrwc+uGP8ABCgZ/c9h+dRvCGlwWLUM4aaQAE7Aegqzy5NJbxFYFX23+dW4LG7vJjDaqOflLszfdjQdXb2H69KEpKKyxoxb2RRkhErLg9G5cfqf2FH+HuGl4i1lEuIy1lbuGdAP9q/4U+XrVLT9MN1dQ2mm+JO08hKPIMEj+ZvQY3r6M+G3BlvpOnw3sygld4Qw3Zu8h/pVHXatVQwuWX9DpPNl1S4RyH4jRNa3GnWkicjRtIGTGOUgKMVhU8wY57mup/GS3QcYxjuZpT+aqa5NZTB7PxXPSR1/JsCumgeaYs56/wD9399iwo8u9UJ1AmYSDIJJ/wCkjDD+tXwfKAaH6nGxsZXj8siKWBHtVxlKRVt7thLFbl2Fwg3f+UjYH61YuI5GgUIjB5zysTsI1HUD2NULhk+ywajJG4V15TFgjnftv/L396uWskoVZbsEycuPE32H8pHp70iYqfYuRQpGuB19aflixJO+aUMG6DB9KinkMUbY+9jYe56U4xR1G75YY1UF/EmA5V3JC7n9ato7SxpKUKnm3HpQqaR4+J7W2XmEaRlc9mOMmiSj/VInXrsTSxeRFyy0BnCMcLnJofqEpBSTO4kVv1q8zbbGhWqNiGNgdiRn86L4DJ7E13GZrOVB1aYkVatLln0u2tpZMRsD9HAwD+W1VbtzFEnL1U+J896e0ZXTJJE6ROGB/wCagFPfIX0OYQaiIJfIkh8JvbJ2P0NFuFrT7LxlcKyEeMhX25kO4/8APWs5bK80bwxlmuoU5wv/ABExnb3X9RWz0DnlknmO7QTxz57hJY8N+ozUyi3Ru18AN8SdIn0zVYNf0/ypMyx3IIyhJ+6x/bPyqDSuKNS0u7W4Ew5oV5SsmXVk64yN8enpW91SJeIPhxcxPH/EktmKD0Zdx+q/rXIrZ+a3Q53AA+h3H9q60xjKTizhrpzosU6+HudAvuIeE+MLJf8AFubTr1RhLgDOPbP4h7Gsff6RLaK8sV3a3lsvSa3lB2916ih+AAVB6ftTeUdcDPrirsKpQXplsZd+qjdvOO/uthpYE4AP5U1hvUhzj1qM9a7NFIWnDOaaKcKKCP3OK9NzfZ35Tg8p3qKSYwkHwnZMbsu+PpSLd20uVkkZUI35RzMfYDt9aE7YRTTYYVym9kFbK2kvJ47WDHMVyWPRVA3Y+1Vbq5MrJ4vKI4l5IoF6Ad2b3PX3qKXVZFsjaWERtoG2cg5kk/5m/oKHm4MYyzBPdqpajUqeyNGilVRw+WXQs0zBgrFO56CmLDFbxvJcyKzu3MQOny96G3HizGNeZxzHOSTnHr7U27mEcYhjGHYYz6CqnUdurG4lzqlxc3AtrT+Gh25u59/aqVzOnhi2gyVJ8znrIf7UetOEdYn4Rk1xUhgt5m8OJ5pOUyAdQo75O1B9O0+ZtcW3vInh8DzyiRcFQPUGq/X1PCYJwmsOS5NFpdoLazRDjIUZ+Z3NEo2IZkX2JqlBceJYCdUzzsSo9d8CiEcPhxAE5dt2b1NWV7HWK9hI3YSY5Cdyc560Fku5Trl1m2PhmQZY98DYUeRR9ojGOpNWNG0q6vZVtrOEzXNxMwRB3Of0HrS2SUVlnSNbm0kD01WBEUGHLk4AVq3elTaHqGiR8NaPceFqupty3Mt4PDEaKpdjn+XAwB3JzQ8cO3EeuPoVraR39y0yxYKA88oG5z2UfsKOcT/CH7DwhJrdrey/aUdIBE+DHcyH73J3UDfHXOKpX3Ql0xk8Z4LtdNsOpxWcc/8ACz8I+H21fiS4uJRi2t4gXx35jso+ePyzX0TBFyRBVUAAYAFfJvBfG3FPBc08tqsTWN1IrCK6iykoQcuzjdT1runDPxu4Q1qSOy1Ito9623LcHMTH2f8AvWbrqLJzc0sovaHVVxrVb2fxML8b4mt+J7aYjZmJ/wDwP7VxkwPZWRt5FMb8/Nh9j5iGH6EV3r47LBcx6fdROkiOxCuhDA+TGxFcl+J2lzWHEF5bQLl8wsB7CNT/AEq9oLMVxi/iVNfXmcp/IEPlVJGMj1O1Qc0jldxltguNz8h/U1aAMiZBAyM5A3qK3CgK4UlmPU9cVp8mc0UIIJBb3Fzdcz+JLgxk55QDgEe4q8xH2Vgy5bG22zZrz58EodszY/XNSgcriMjyE5X2PpUxgEUDwJbUKsg5kPQjYg+1I82JFZXBx/EYSLg7dB+dFUtJb28SK3j8RywjRP5mP/n71LoPD8r8RR2Ui/aVNyZGfGeZQf6nAFc5zURo1uTSXc9xDo8tppGgzy4MqtJ4u2MM683/AGoWwEdtGCcdBXVviVoL6Vp9vbzsrP5JSQOhJwR9OlcvvlCqi4By4GK4aKzrr6viWtdSq7ML2X8ELbAnNDL4GSCNc7B1B+tFpQBExPQA1RMQZYw3VpA+PlVtooyXYhnJku5lx0jK1cteaXhq4J7NGCPkcU2KMFZHOOZydzV3T4B/8d1kd4uWQfVhUwGKy/qVY2kTVI5YnKOsYkVh1BAzXSODprXUll1CDlHixpHLCP8Aduuc/Q52rnUcfJBNdkbC1CL7sxwP0qxoN5PpdveX8XMTAYmeNWx4iFuUj+ooZwdqbPLlvwdb0i3ZNGhRkwRzZU/8xrj2sWJ0viO+sERkjhmbkU91O4/Q11TS9Zt31eMxylre/hE0Oezrsy/PG+PY1m/iLYAapbaoqYWZPCcj+Zdx+mfyrvRFOayN4lHq0/VH/EwjAqwB9cD8qT51JLjlB9CMVF1FaaWOTzLeeBp6Uw044prUGQX5U5TmmilXrUQSQV5oYZGy8SMfUivLTwK6JJ8i5wQva23JjwlBbbO+3vUf2HT/AA3lBBlgdWER6sCDkk+xx+dWdmkYdOXy7+++aKTWMNtwfNJORHPfcvghuoQN1/c/lVW2pOMmkvv/AKXNMpSl8jPJEzP4jDmZthjv8qks9I+361FbqhnlckmNDsqgZYk+wp1zOoOIVKIF5FA2OB6ntmj3AMd3Jc6hd21gJ5GRbSJ/ECRxFmy3Meu4AG1Y98umLZqUVqyyMGHoo7u3SLVrgQqbZeZLSc/wYYsfdB7Njfm9ayXGGrrrt9d6hptpKIgiq8hXB5B0LfPNbviCy+wqX1u4jnliAkW0hUiFWP3R/nb5/lWdstD59Ov4tXfw4Zba4uuWI4keRVyEz6d8e1UqZpLrNPVVSk/Lj9/wAbUpHYWkX4uQEAfKi6+Zd/Ss5ZOZL20Vu8B/PArRxbxhgO1aUXkzIblS7u3tAsv2WSRUbLch6DHWrvDvHumcP2StDZXtxqEgIkn8UIFBz5U9B79aYwUSLzjIYb477g1pb3hm30bXNM1+8tYPsV8jLdFI9kBb7yjsQMdKqauUdoS4Zb08LN51vgzugfEi00bWnur6PVlR08PxbZ18QAnLbt3NdHv/AIt6LxHplpYabxEDFArMLXVIvCZSFOMMNifrXuPeALK74EsNWsJrKO1e7DyyY8jBhhCGHbJArlWvcHro94j3ujTXaSo8KC3YpyykeRicHIB7d6D0fmf3PYEdRfWmlujuHB2lade/CSwh1bSJjG8JkF7aEXKHmJOXQeZcfWsJr3w/hMctxoeoRYOQCvnj+RHVTWU0/TuNuFdbsYeF7/UrWa4dY0t5Ty5cgZBHQr71rrPi+71vig8P8TaZ/hXESkol5bjlWdh2cdGBqnbTbRNyT+/kXK7arYqq6OHx9sxcy8Raa1tYXzzxQRyc/hu3NExHQr6Vp+IeIbfi/iC01R7M20roiXEIPMuR5cqe6kGtNr9mjaEBcW5DLLGJYnH3fOAQfY9qi1TgaysNKGr2UhiUxzAWxGQCrhgQfkCMU/8AUQklJrD3A9HZBuMXmOxz/kMFuRjdAV39jimxR/wMjIyNqvanEftrwgeSTEhb0HQj67VHgY2HtWrF5RQcdwdKv+sqPWQN/wDmppjywnYn0x1z2qFuf/E7dMeUhs/MdP0NaLRNO0q91i2j1nV4NMt3PM00m/Ig6tjuT0UfWlnNRTbFhByeEEuGLBdE4M1TiXVVZLpI/stgjDAkkkHmlX1wDgH1zW0+CPD8Wo6rcapcJzxWvKFZh1Ybgfnv9BQP4rcT8JazDpGl8MXwnsNPhCIkYIAKnGGJ7cuTn3ra8GfEX4Z8McH2enRcQgyFPEncWz+aQ7t27dPpWRdOyVLaTzL9EadSrhal1LEV9WL8atP57KOdCBywkknvhx/evn3VLedmilj3jhkVpD8zgV2f4p/ETgvX+HIYtK12Kefn5PD8N1JBIPce1cpa+0peHdZt7m8SK9bwWgiYHzhWycH136V20HVXS8ruc9dKFs1h9v5Blyn8B8jqMUNBafV3ROkaEDHqdqKXciraPIDkAc39aoaMn+rvdv1kctn2HStTlmW1l4J+QRjk/l2ohpQSS1u7YnzXoNunzVC/9KponMpYgEsCBn371ZDjTbvQHYEhriSdgO6/c/bNRj14Tz9+xSecHR7WAdW/isPYbL/U0U02y59J1qN1KkWinB/5wRUUWj+JxX/hsbB1M2FcdOTqD+VH0jNxPxELdchuWBcewyR+lRHSEMvftt+hnINSnseJRpbOI0imWa3n7RuVBwf8p3H1roXEUK67wPPLCP4sGJeT+Vl+8v5ZrlN5P4+ryyjBEkURI9+Ugith8PdYuG4qj0m6dpba5iaMq2+cLsD+2a7KtqCsiznRqoyslprP8tl+ZjpSoIQ+bO/yHrTc5o1qGm6ZOzT6Dc5XmPNZ3B5ZYyCRgZ2YUFYGMkSeQjYhtsVoRsUtzEtonU8Pj3XDGnPypjdakI96Y1MzihBTl3NIKcoqII9RXvHRZORmIb3FOUbU8DI3rok+wrIUcG5csAU8uR1Le2KfqE97e3KyM5VmITxH3YDpgDoB7VIkSpIzqACwAOO+KcvK06L15SGI9PSuL0+cubO8L2l0QWP3BcunN9tVJ3dlZG3J6kHFdT+G9vptp8NFvbudII5dSbxZm2CBBtXNNW1Bom5QnMFZ+RfUltz8q1/wfuYdR1Z+D9XvWjW4kF1p8Zx4YulOQG9cgbDpmvO6+PoeOzN/w6ahfH3a/U3PEEN/f3tjGlh4VjGv2wQzeWVidkdx22yQvUDrWH1zSrhrmfVWuJ1+zzcgUnyJF90gDuTneuzazaTTawl7JGYzcRhWDfglTZlPv3rF6p9gseMtEsdalP8AhUl+Lq45UyRGm4Df5ecgk+lZdF3ZG5qasrql9+xzG80q70KdF1O3WOZOUhR1CE4399xRRICLFyPvBWx88Vs/jDpL/wCOXV/EitBlopGU/wDEHMhHsTWB0+8lm02NJVKyhBzA99tj9cVr6W5TrUmZF1SqscAxouktqlp4cystwtr4ij1YEZ/Q13m24YseIOF7Cxv4hJDDEYpEzvzbA/Lp+tcs0+1udNj0DXxEzWbr4c2B23Un/wCpz9K7Xw9/qmtalYknExS9i9CrAI2P+pR/9hWRrrXJpr77GzoqlBOL++5mY/hzq9jpVxpmnauqaddEiXTpBzwgE/hB6EADp3pLDhfiZ2NvObKYQuYjJJuwx0PvkEe9dI3zXkjVJXkVcNJjmPrgYqvXr76/wyLTohnKRl+HdCfS+JRrHEGjLrFxbkxWTKwRIEPV+U9WOevaoOOvh/ofG8S3NrYvpd/HNzLIVA5CBsQR1UntW269a8MCjPXXWPMpHJ6WvOWjnmucKvN8PLq4ntjFqENqxaLn5x5N9m7jbIPXBxVTjmG0svhzZXkEZZWkC8uf+LGcfqa6RdyWa6dcy3k0cNskbCaSU8qouNySa4Pe2nEXHVpE8KvZ6NpVoYYpmyPFZFPmUd2bA37Cpp92nJ4SYNRJxWIrLaOeapI73SxxjaLDFsffI6gew7+9L4WJAfwsNvnWr44FgIuG4dLTmhtbCONY0GWctlpCfU5ySfWgggWW3BjIIIyp/at+izrjlrBi2V9MsZyCLq1mLwyQRhmWdQQTgYfy7+gziid9wzb2Vq95e6qwkA8xEYIz2VR+lSaPeWP/AMhs1vYC8Rl8CeFjjKuCp/LIIPtVPiu8ku759P062e7ntuYC7HMYQijdgPxP2J6Cud05+YoRJGMFBykDtP0O2u55oZ9UWON15WKoSS53Kj2GwJ9aOad8MxfXKWttxDCik7B/Lj86ylrxHxzZxPJYXVvp8SlSB4aoNzgAEjf1NaK7+IvxDspJbW5utF1eCPAaeC2SaJts7OAM+9c7Iajt9/oJXPT49cX9/mGuNPhVY8McJJqRutRu71p44YASvhyOx6YHsM0HsuBdPu9F1ia5E7X8EatGwkwoYpzHI7jbFD5OPb64ks9R1Dh821rAz8kthIyI82Mc+GyMqOgHrWl4U4ws9T4j1GKJnnW6iUt4wEcgOCCQOjYz/WuPVbGGJPc7Q/prLPStntg5rf21ykCrA4McmECdCM0U5Vt7dbUpycqY5gcjbrTXHiaosLbC1Ys//MCQo/rXrpyynH4sfWtWvjJnuOGx0LeJMiIN2YKB6Z6VS4k1F31LSGXl5YrYcnL0IEhGfripbwta6dLOr8rRpsR1LnYUPuYklh0Fm72fJ9VkOf3oSe4sm+lx++TXQ3EOmXf+KpKXmaOS2MeP9nJgFfoVJ/KtjwzpZtdBtVlB8aaQyyZ6kkd/of1rnJ1K3s+JZhdQePaSyfxI875XHKR7g/oa6XpeqWcvgWUN2ZbkKZnRlwy5OTkdsZAAqZNHTuMpM5beafDZzKI3LeIGdgfwnmIx+lW9Aum03iLT71W5MXKZPqud/pvU+v2c0XEN9I6qluJmCeYZx1wB8yaEs5ecPgKAQFA/CAa0qY9Vaj9Tzt7dN7njDT2/ks6zCsfEOoRBRhbqUD5cxoeyL1K5PvvV/U5ludYvJ1OVkmZgR3zVMirUV6Vkq2v+5LHGWRGmtTj8qY1KxEeFPWm09etRBJV61IBvUQYKfNsPWpkOe1dYvIr2HAYFMQNHdyS4AXlUBj6jNPZgFydvnVKaSNpAilpQxywU5wPT60t1kYLceqLctiqts03jzu55eQyEuem+359afZTPaTNqFpIY7iCRJIpB1Rgcg/nV1YbnUblLRVVRK3+zBwMAZ8x9ABVSW3ENg64KOzcrrnoc4/tWNbF8tGrU0uGfUumcX2HGXAUPE8djFM7gRarZc3LyTIMF0PY9x6g1n+NeF5tMtW4osRNfwpamKWErl0jO5Ix1HY1yL4TcYLw3xiLPUH//AIrUGW3ulbpG+fJJj2Ox9jX05qPEunaPqNpZXMckj3Eixjk7AnGQPxAZGcdARXmLqZUW9MVs/wBj1On1MdRR1TeGtn8ziOgXc3GnwtuILiOVLi0kigJcHzorc0Ryeux5foKD23D0n+C3uqJGz/ZXW3lX/hqTlXPsDkV9K8Q6UJbZEhRFkOIvKuMYYEdPlWU0/R7K1471WyeENZazat5MeUSofOv1U5Hyp69V0p4+Y0tJnp6nl8Z/YtcJaNa6v8HdNt9gwiIDEdGDHr+31ovwy5+ynSrtSt9p/wDCPP8AeMR+42e425T7qKr8EabcabpVzoM8j89nMWglH44m+6cd/Q+9aJrGFdUhu7iD/WVQxJMuccp6r8vnVK2Xqa7F2telN8llV2/vUgXaniOnBD2ridBuNqhmMyAeBB4xJwRzhce9WwmRSBMUUxWZy84cXVJUu+JLtZoYW8RLQHlt0I6Fh+Mj1O3tQzWFnniu9M0ZGWK5PObhY+ZsEYYRp74HmOAM1tZEDxlWUEHqCM1Ujt0gleVM87dSe9dFa+WIoI5MvAX2PWbe8vlmit5iU5GYFww3VCRsobfYelc71WzuNM1q6FtB/qAmk5WPZQ+PL7Anf2xX0jqdpFdWNyLl5DEYycKcFSvmDA+oIBFB+I/hu8XBFja8plvUtVuhK4x4jvvKh+fN+1W6Na4y6pP4HC7SqS6YnGrfhz/EfhtqGsRwpLJFeK7dzhANj7dj7GupSabPe2lrJpMtnHHdae6wRSxfwwjoAyjG+QOnyoX8M7CKLTNZ0iaFvDuMS8rjfIzFIvzBA/MVqOD4JrXSn0G+Q/aNMlKRsw+9E2Sjj2IyPpU1Fzcm88f7FoqUYrK5X6o5hqvBkdtpceia/p5vbVFBjurRSp26EjqGqTSuBdL4rurXQeFtMkJz4U92WKJZj+Zwd3PsK7oLaNk5XQMp6gjNAdQ4N0q4xJAZreVSzK0chUlj3JG/WrdXjM4xxJb+5LdHGXGPoUtV+EfC/CfBMGnTymeGCNhm6CqX6lic7DJr5Q1bhZrnX7ifhtFit0Zn5lYqiqN+ZCd+XbqetfRt18Oby9ktv8X16+vLY8wnjllaQoceUxlicb9c1h/iO2i8IaYujWS5nnTnkBOWKD1P+Y/oKMNV5s1GPJQnoI11uVvCOQ2EeolnkvJlleQh25hhvQEn5VPIysC7EYB/PeraB/sgd95ZTzN8z/QCqV2ypfW9nj7/AJ29lH962UlFGS1hA/iC5HiWmnhss7eNJ9egqxb2r3cOlhFJFvdMreyMOb8sg1PxSNKVNNTT7IpcwvIs9w+eafCg5+QJwKXQnMrLCGIM3NGfyyP7VyjLryydGLOlso2en3OtcRRqNoZbtYOY+rsT+wzW90PWbGfje/uWfHKXgU9eeJSArD1Ixv7UB8ZtM4et5bGIi4tbwmSR18od1Iz7kdPpQe1WW1mieElGjIZHB3yKsVUSnuhLNRHTNe/IZ4wAj431DYHnZZAR3BUf2oGXODgZPpWr4tudN1OaxlB8C+ks0lViMRygkgoT2YEHGdu1ZMROsuZFKldgp7VpUSzBR7mbrq8XOa4e/wDwk26DpTTTvnTTXdlMjIqNqkPvUbe1c5BQ7FOXGabSg0AkuFZeVgCPQ14xZYFZHXHZTgGkWpQafpUuQdTQ0pHsTCWPqSX/AHqCadI84TJPQKR+vp9ahvLoRp4zGQJuI1Q45j3JPpQVtQnkb+Jhm6bVnW6pQbjD6lqFWUnIOLqhsSLiNgkyqfMp5iM9h6fOq9s8t9pk7vKzylicsc79aDszSEIxGSdlovp7LbaS8jZC85JqlGTk8yZcr3eOwttarNLKSNpoww/Y/rXXeE/ipb6VothqPHEV1O0NwLNBC2ROsC8waRe5DFBkdcDNcntG8SxhnQFd2UD2J6Uk1xf+XTxcP9kmcyPDtgtj898DI74rlbSrI4Z3rtlVvE7PxT/pJWt7bi30LS5ldnXM82wUcwyfnjNd8Gn299FZ38cQKri5jCnHMSm36NXwNe2zIJY8dGDL8jX3R8KNVOs/Bfh+8lOZltRBKD1DxnlIPvgCsXXaaNKTibnhutsvnJWGjk0+GZ4LqNnt549w6gZweqsO4NWGGTmpTTcVmmvkjxTgB3peWl9qhMnu1ex6UtePT2qAyRsMGoHQnoKnkdEjMjnCgZJqtZ3lvfRs9s5YKeVgylSD7g70BkyvqKNFpswZCOZMDPcHb+tdL4qjh/8AjbLIAMEBPywf0rnOp3ESm3tp5QDNIqklgCFDAnAJ3PYAVoNb1htVuQUVkiXZVJyfnQeXgPLyZCLTUtOIEu0tgfEDoZE2xzEE8w7klRvV+axhku47xSY7iMcokXupOSpHcVa5aWny+QYXA0tjtTTvsKcRmqd612lswtWiik7PMpZV98DrQCkJqt9aaRw5d3t1byXDIv8ADhjH3z/mP4VHc/QZNfOfxGmRLV4NRsQ15qcq3s17crySpCn3Ujj6ohPQtuQOlfR98NC4B4eg4y4uu7nWtXuB4em6ZskbSdf4cQ7jqXOeUe9fMnE9zLrvFd7xHxZG1zzTGW4tYmx4jDpCp7Koxzf3q/oYrq6u37/Iz9bNyj0I59Y6ibvU3C7Nykoh6KPf51o9W0zT7Xiq0t7eMtyWqfaJicmSQ+Yn22wMCm/4C0Fqt9BHGst1OjmFBgBXfPIvsBWhkswI21aSMPO13JqCxfie0gXzsP8AKWx9BWpZqN087GbTp30tSW+z/I59xb4knEyKyKi26C1Kp2cbvn3ya9YWZi0i61HmdZYnWOEg9GJyWoULu6u0nllk5DcM00pO/U8309KMxX8UnDEEIDoxmBZCP5V3b6k7Vo6WrLUTNttjmVj+LCV3fx3HCaxTRrDcyXokdVGz4By6+3r6GhBfJ2GAKMXhD/D+yZAocajKuWG+DGCR8s0AaRiORFPiHsfw+9a+nxBOPxMzWt2yjJ+yLl3P9okiTAKQQrCPfGSf1b9KqSRI+CcjHocU5F5IwvMTjueprxNdowSikyrKblLI07U0kU4mmE71GKhrVG1PY7bVGx2rkxhQdqetRjA3p4JqAJVO3amS8zcsKEhpG5QR2Hc/lTQxWYjOzDP5VNaJz3Mkx/APDX27k/sKSdnpaXJ1rh1SWShrKqZkiUeVIsAelA4sCLnPWi1zI0upOx6ZwB7VRhtSZWBUhVY75/asWe8i6egjI8xA5j6Df5Vf1Blj05bMHzBQWxSpGkQ5sEkdAcAD5461GI2mn5cZLHAY+vf9KKWFg6x2WAjp8Qh0qJDvjzfnvSyqDeWrEYJzt9KgnvFTU4LKNt98/PGAKu3MJAhuO8TD8jsadcHVY4QJ1hG8IuOocLn2NfXvwem+z2Op6MSABJHfxKP5ZEAf/wDS/rXynfQrNYkEYLOjfTnAr6M0TVm4c16y1RV5rePFvdgDJ8BgASP+U4b5A1k+KLOEavhcemUpfL/Z27GDXsUiyLIgdHV1YZDKcgg9CPalB9awcm6ePWm0pzXu1EAnfNeO4pCw6Zr2agT3KD1FRFREzScvbfA3IFWARjpTWPpUCjFQcKyahxD/AI/rLsbnnDxqesag5VF/lX1xue9bFck5peXNKBg0W88kPcu29eKnrTs04UCJkQABo5oHDUvEFxIBci1jhAYzmMPyt22Ox+tDIbaW4uEhhQu7nlUDua6TZ2OnaDwww1IxiGJDNcyucKABkk+wApW8EnLETifxw1XRuFuE5TpFpPxDxLd/6tFqE/8AEkLdoYcDCr+JggAAGO9fOnw/4Q4q4gR7vUdDvVkiJjeS8Aggiwcnc7nfJOBX0FrNxe8U6bq3xTfTmbTbK3kTRtMQYkS2U+aQjs7nzHuFxTbXi/Q9I+Dz8QcZz2drbiSS0mhgcy+NIP8AdRA7uxBGw6dyKt12ThXiKy+Ct5cHJOcsbZx2+bOTpw5HacSTvrl1Zy6bp8H2l7q1kP2XfbleUjYgjcDJPQda5vx78QLfXrL/AAjQ4vA0yNi8tyY/Dlvn7ZH4Ih0WP6nenccfEm+4/wBS+zG2TTNAs9rPSYMBE7Kz42d/0HascunlpUiZcKnnb39K3tH4dZJRssW/Yw9f4jHDhW9u/wAf+FdFf7UkLIPClQo3r0yTV6KSNoEdd1dcgD9qn+zxkOT99YyB/wBRxVYiO25v4bBc5BUZwfl6V6KuryrG+x56yzzIRT75LjzymzSzMn8GJ2kVf87AAn8gBVVlZsZc4B6AV5WIBLZYdQQN/qKdnNWVFYwVpSbeRo2Xc596QmlOKYTRYqPGmGlY0wmkYRrUxqcaY3eubGHDpS57/tUfNtT1360pBk8hETSeH90ZxzYJ9s9qu26m20xV/EBv7sf/AHVJik13Fac2SW5nA7Ab1NqVwYoVjU4Zjn5VSuxFuSLlLbWWDZCpvW5Tkc3WnxLi6lBP3gGA/Sq6nDZp91OYIfHVAzAcvX1qgnjc7RLLlMkNIqDGct0qkNS8IMIIiHAwrsc49T86Hfa7idyHlbfsKnEDLGXYYAGanXngPV7EmlK0vEELHLEZck/KtSjidpYm3A8poLolty2zTk4ebyIfRR95qJ6NMk6zzbANMQPkOlda9l8zrXsse4245zc2ScpxLIID8+YEV9L2+kyvpBvwgMQcofb5j0r55tEN1xBbWMUfjTi+haNM4ySdhnt6V9W8OGKfhcp1WQsHU9VPQqfQg1j+KSxJG94RHKkU+C+I30vVI+GNVk/1Wdsabcsdg3U27H17oe427V0bIzXFdd04M01hdIzRk9VOCMbqwPYjqD2NbDgfiy41Ff8AAdcmDarAnNHORj7bEPxj/OPxD696ybIZXUjVjLD6WbvPvTc0wHG9SbEVyGYB1PTOIbjU2u9L4sksIuUAWjWcc0ee5yd96HPpnHYPMeKrSQY+59hWMfmprWEb1FcSyRRcyRBwPeipP7SDFJGSM3FenqJJ3juiCSwiDIce2chvltTn44W3gW4vdPuYIvxO8Z8vzxkgfSi8mqQAfxYZoWzuSOYfmKswSWN9A8RSKdehJG4/rTZXdHTbHI/StZ03WrUz6ddRzKhw4UglD7+lEBWPvfh5oMmujW9GuNR0TU8jmurCbl8Ud1kQ+VgfcVr1BCgE5OOtK0uxxy+4pzSc2KdvWh4Z4cfUpxfXKEWsZ6H8Z/tSt4GW27DnBmieFCNVukw7D+Ep/CPWvnb/AEuvjKbeI/Cnha95bqQCTWriI/7FOqwZ/mOxb0GB610P47/HzTPhXobaJoksN5xbdR4trUHK2akf7aX0x+Fe59q+Br24ub+6lubmeS6vbqVpZp5Dl5XY5ZifWtHw7Ru1+bPhcGJ4jq2swi9/2OmcMfGz4gWGg3WnWzW+oLFbsSZCEYr93cdG6jIHas1x9r9zr3EbXj3kk6RRx21uhYckTcgEhjA2A5s79T3NZVY0iVuZQwXoPlUU9yRrS2/aBeUj/N3/ALVtV6auuXUluzNs1Vk4qM3klgdrfUliQxtgAiNzy5OOoPr86MCfleR3DRZZU5ZNiDjpWavRz38j9jgD8qlgeaa1kgcGRQVePm3ww7fIirlepnVhLjOShZBTbTNA7MzoQds+b3Hb9aWqOlSwXUht2kFs+MqfwN7EHpRGe2urZOeWAtH/AMSLzD+4rUp1tcnvs2UZ6aaWVukRMKYcV4SK4yrA/KkJq3lPgrjSaaTtS5pp33pGFCE7bUw0rU0nNc2xsDWJ6Uw05jTDnFc2wjObBA3JPQDcmrVvaXE28oMEff8AnP8AardtaR2qkqeeQ/ekPX6egqLU7t7SwaSP758q/P1qpO149i5ChLeRFEIRq0iQKFjgQR/9R3O/c9KG3Upmunc+uB8qfbv9n0TnJPiTsTnv86rA5qpOWYpHU9jvTpozcWjRg7kYHzpQOanxnDj0NcCIFafFmVmYbrtj3ohPE7xGMsyrkMVAznFKYvB1HmAwsm/1qw+FGWzv6DOaCWEFFZL3lsilvH4aAcignLH1JP8ASrmmfwtB5zsCGcn5UHtFkub4WyL0Jx/3rUahbrY8PlY1LBY/D29+9dIe51ry8y9iXh6aRfiRoVyhzFNNCzH2V819jwaRFHq7ajBLJCZf9vEuCkx7MR2b3HWvjTgx2n1GwtUgeaZGkCleq4GV/WvsrhXWYtd4L0/U49mkiCyL3V12YH6isXxRPKkeg8Hx0tfmVeJtKjuIUuI1AYDlJ/asJcWxfkkile3uYHEsE8f3oZB0YfsR3G1dUvIjPYyRnPTO1YfWdOa3kWdUwjnB9M/+qzqp9jWshlGs4R4pGv2L214kcGrWoH2mBT5WB6Sp6o36HY1o8muL8tzb3sGo6fOLe/tiWhnIyBnqjDujdCPr1FdP4W4kteJdMeRY/s17bsI7uzZstC+Ox7qeqt3HvQshjdcCQl2YbAyM0p227V7HLSZ2rmOQva28p80Sn6UsdrDCuI0A96k6npS5qAGcvKdqdk9qQkd6ocUcYcIfDjRk1nje+MZcZtdLg81zdHthey+52qJNvC5I5KK6pPCNjw9w8+oMb6/YW9hF5nkc8oIHueg965/8R/8ASMtzJNwV8Goob+8hBjudddf9TsQBuUP+8YflXIeJ/iFx/wDGlBFeiThjgsHEelWrlZbtR08RupH6UG4lubXhb4b6gun28drFHAYoo4xgczeUfM71Zr0+Guvd+xTstdicltBfV/I4hNPfatr19qWoX8uoXdxcM0t3KxZ5d/vEn1qZyttDJcH8I5VH/nvSWESwWaKwwzDce1VtUlPNFAOgHOfmelemilGKPMvaOQjpah7uyeTBUsHbPfGT/ShRspbzUpZYSVnMjNnqDv3FSR3TJYR+GclSUPtnpUD3ObppkBRiebA2we+KktxJNdKJb8LDdcrqyMVBKsOh7jPeqpNaXTNftpvDtdUt0f8ACJioP5io9Z0OISPNpycjDdoB0Yeqf2pM+5JV9XqiwDGSV3xmr9pqd9ZMDbXLqB+EnI/Kh6nGD61JmmOSbXAfi1XTdQfOoQ/ZZ+n2iDYH5ipTZyshks54r6Mbkwnzge6/2rKuCM4pInmhnEtvI6SLuGQ4IrrXdOr8LBNRs/GjRqVdcg9OvtTTRGxMnEWifaXREv4jyiZRjxdujevzoYH5lzgg9wex9K06NUrVvsypdQ69+zEY0w7mlJzTc11bOIjUw9KcdhTSaRshbbVrZenO3yFU76+jvLNohGVPUE+tD6932rJlbJ7M0cjnfm5F5uYIgUdsUg60wDDfOpBXMBImwrx67UoG1KB86gSV0E1vjOD2PoaWJzJHv5WGzD0NJDkgrSkchEy9Ds4H70Ak2lQD/FHjhhzJktzD0NHfD57eaGQA5bk39hQmyujBdgIeXxRyFx27ii8f8xbf1NdFwXKcdJHwVC1rx1cSQDBtQsuR2IYV9T29vPw/Idf0eFrzSL8Ce8sYhl4nI/20Q7/5l79RXzr8PbMajba/qFuuS86pGx/EFFfQXw81WS+4UjtXY+JasYyO+O39RWHr3l59jb8MjitL33RsLS9s9RsY7u0lEsMq5VgCMj5Hp8qqTWCX2ny2b45hkKfQjpV2G2hSRpFjCu3UjvUixlblnHcCsrjg18+5y26ja2uGidSrKSrA9jQ37TqWmatFrmhyImowLycjnEdzHnJhk9j2P4TvW94v0nmT/EoE6+WUD17GsM6779atQkmivOJ1ThjivTeLdDF/p5eORG8O4tZdpbaQdUcfsehG9Fy2Divn6e31PTtaGu8Oam+maoF8N3C88Vwo6LKn4h6HqKmP+kBrnD5EHGHBhfBx9r0+bySD1AOw/OlencvwbnP+oVa/u7fHsd+Q5pzALG0jMiIilnd2CqgHUknYD3riUX+k1wRJEOTRddeY9IljQkn0yDWa1zW+NPipL4OsCTh7hYNkaVA/8a5x0Mrd/l09qi00/wDLZAerre1fqf3ybjiT42GbUZdC+FNnFrWpJ5ZtcuF/1O0PrGD99h6nb51hrLhQJqk2vcSXs3EGuznmmvrw8+/ogPQf+bVodM06x0rT0stOtY7a3QeWOMY+p9T71YA8STI6Kdq6rEFiH/RVU5PqteX+i+/c9GgVFQAbDpWK+MlnJYcKaJb3DKjaldNKISPN4cQ+8fYswH0rsnDnDw8ZL/UY/KPNHEw6+5/tXAf9IzWpNQ+MS6dFNlNPsY4AgP3XfLt+4p9J670l23E8Ql0adt99jmcV0k17csD/AA448Kf3NVbhhc2pmx5g2f8ApI/of3qG1I53jzjxUKD59qgPMEIViB3rfb2PLOeUTQSKnMkilo3GGA6/Me9M+tMVvbFO5sjFATI5TjzbVuuHjNNp7G486A4j5hnFYJsgZAzXQtBctokIIxy+WlZ2o/ECOJdD5ebUrJNus0a//wCh/Ws7GweMMK6WSDsRkHrnvWG13S20q98e3jLWkxyAP923cfKgmG2vHqQNkXy1XBI3U4PrVlZo5UwpBqBLeae+S1hGWlOFpyv8jbcHh/8AAA7MT/EOARjHyqjq0IttcuFXZZCJl/6uv6g1pbSMQWUUIVV5FC4XpsKE8SRbW1yBk8xiJ9iMj9R+tdNNPpsTO2orzTj2AR6UleJGKTNa7ZkniajO4zTjTGpWAodelL2qtBcK/kOze/erPasbk0D1OAycUnfangeYHFQhKBsKkVCFzSKvMelTADpUCiCNsP1qVm5X9m3FV5QVlNSIfFQo3XsaASWNkiVkYYjY5U/yN/aphc3us6tbaVo0ZknuIzGy4xyuepJ9AN81WTzqVYbjYitl8LpbOz4k1CxlhQXVzbs1tOepCglox8+v0rndNwg2izp15k1W3hM6H8JtCg07Q4bJpFl8WeTmkAwHOcZHttW50ZX4f40uIFQ+HOpk5B3IPmH9aEcIacbSPTYkyBGE69ck5P71seKYo7TiXTr44TMwBPrlSCKwrZ9U2n3PVU1qFcUuxq4Jo5YhIjAqRkEVLnLA+lZ/R5ivIN+VwDg9qOnpn0NU2sFkdIiyxNFIoZGGGB7iuca/okmmX5Kgm3kOUb+h9xXSwBVe8tbe9tHtrlA0bfofUU0JdLA1k5BLDsc7+tCri1jkBVgGVtmRlDBq2Gt6Lc6XMVYc8Df7OXsfY+hoGLdSctufSrUZZ3RwlDswTp2g6dbXX2i10+1t37yJEAfpR1YwuABgUi7H0oppel3GpXAihG3dj0UVHLuyRglsigVcgBRkk4FbHQeGxCqXl7H5xukbdvc+9XNP0OzgvlnSPmEHlRm3537t9Ogo3zADc1XsszsjvGGORmMPg9D1r4X441l9d+LGuau/++v5AO+FU8o/QV9mcRa1HYcA6/qyvym2tZOQ/wCYqQK+DkYuA5Ylm8xPv1rR8Lh6pSZjeOWYUIfmOx1BHfBFKOmKaRgZGd+tKDtWyedJRGrgY2NQS88Ew5h5T1NTxE8y47GrFwgeLJHzoE5KyDxJUj68zYrd6E2dOZR+F6xGnW7C5aTOUTyqD6mttw8wNvOv+YUGdaeQsM1Q1mPxdFnXl5iBzD2IPWp2v7MXZtvHTxB1BP6VR126EWlGMHzSnl+nelRZk1hmGvLM+G13bnDru4Hp6itFwpZSlP8AEp0Bd/JED6d2qlp9lJqWpi2TaJf9q39K20MKRAKi4VRyqB2FR7FeuGXksDeh+vRluHpmHVCr/kavh/QVXvGju7C9t0O4RkI9Dy5op4eTvJZi0Y44yaaTTp7a5tFjW5X76gq67q+3Y/0qLOa2ozU11IwpRcXhik1Gd6caaaIpnSHRw3KRjeiMUiyIGU5FVirOPOdvQV5FaJuaP6g9DWKlg0C8KsICUG31qlFKJBt1HUelX7ZgU5D1piE0a4Wn49q8BtS4qDEE65HMO1RRnlkB6VbI8tV3jwpx1G4oAJmGG8Uf9Q9qlhmnt7qG7tJTHPC4kicdmH9O1RI2VBpMiM/5D+lBrOzGTw8n078PtWj4g0rT9ThQKZSBJGP926nDL9DW717To7m7W/cNJIm0YY+WIdyB6n1r57+BvEA0/wCIUeh3UrC31EMIAT5UuAMj/wCwBHzFfTM8fi2zKO4rzurrdVuD2GhvV9Sk+e4CtW5HB6EVpEIaMH1FZsryPijdlLz2oHUrtVeRcRaRjyDPWl3qKIEAqTkgnHyqYH2pQEE8Ec8DQzIskbbFWGQayOo8ImIST2Uw8MDmMch6D2NbVuVU5m6CsJxTrVzfFtP0wjwAeWRzsGI659h6dzTV5zsR4xuA4IBc3IijwRnl5s9fl/eui6XaR2enLFCnKMfe7sfU1luFdIQz+IwJSPd2bq7VuVAI2prHl4BFYQxAEAQDAGwofrV2LXT2wfO/lFEyuB0rGa9dtc6n4SHKx+UfPvSRWWMmYn4jX14vwl1awtw0kl2VjSMdWZiFAH518oP4trcvFKjIyEqyMMFSOor664ztPE07TIQ3lN1C7fMPXPePfhra8QJJqekBLfU+rKdln+fo3vWpo7lWsPuYvimknc+qPK7HDFkRx5Tv6GlGRv8AnUV7YXmm372d9byW88Zw0cgwRXlkKoOcZB6GtZSyecezwyzEfOPnRB8LGxI7dKFWjA3oGcg70XxzyqvYeY/0ps5Ih9tH4UAXv1Pzo1Z3hstFuZkxzlgq/PFCRtvTJZCYxHny5zioMnjgifLHmJJJ3zTgbu9ljtUdpGAwCTkIPWo2LvIIYRlz+QHqaNwtFolr4aYe9fdid+T3Pv7UGSKzzwGtK06DTbH7OjZdh5/WiHbFCtFVzZNcSuXeVs5PpRRSaUtRe2wyVxFC8hx5VJoRoU7TXl14hy0mGP8AWrmryH7F4CY5pDv7KOtBLFpLe+V4sux25R3ooScsSRobaJJ7GfT7uJXjifwxnuvUH571ltS0+XTrrkbLRP8A7OT19j71r1JKgkcpO5pLi2hu7V7e4XmRuvqPce9PVa63lC3Uq2OHyYSkJq1fWcthetbSnmwOZX/mX1+dVTkVrQkpLqRjyi4ywwX4TqMkGkxjrRQ28a7nLfOqF0vLcbDYisll/BWkVkHjxHDL19xVm1uw5GPK47UsSK8ZFUBAyzuoJDLkilexDRxuHQEd6koJZahyuFk2P70ZVldeZTsaKYUKflUEkqpJykb1MTVS8UlBIPwmoEmU+Q46DpUgIcY65HSqtvIr7DbPUelTJlJiPqKBCzZzz2VwkttO8E8bB4ZlO8bA5Uj5GvsT4f8AGVtxtwTBqilUvY/4F7AOscwG/wBG+8PnXxsfN1rYfDHjeTgbjqO6uZnOkXhWC/XryrnyyfNSfyzVPW6fzYZXKNHw7V+RZiX4WfU+oRGORpAMLmptKm8xQ9DvVi+WObTGeN1kRkDo6nIYdQQfQihmmH+N7g5rB7HrEHEfF+8Td0Dg/oanobqUn2d7a9GcI3Iw9jRFSGUMNwRnNKQSdea3ZQcZGKw0mmXBvTHjctjArdkZGKgFugn8XlHMKMZYARafZJY2KW6YyN2PqauqKaBjenqfNjuN8UMkKGtXy6fpTy5HOfKnzrGxIzcruMtJuM+lFdYdta4ni02BsxRHDEf/AKP9Kdb2Ym4icBcRQdB8ugp1hIKMvxpaSpHDBCcyR8kgJ9myf0zQ5RzbjpW24p08y26XKLlweU/0rJNF4ZxjFdYS9ODlOPqyZ7iXhLRuJrILqNorTIMJMp5XX2Bri+vcBNpJmt7W7+0iRh4SuvKwOCV398MPpX0G5xsM1heJoBP/AInOkbF4YEkTb8SuWyPyP51c01kk8Z2MzX0Vzj1NbnB7a1mtdTaK6ieF0ByjjBFFYEIQs3Vjk0T4pvodU4oY27BoYo1jVh32y36nFUdgvyrWg24ps89OKjJxi8o8xCrucVVLPJJyR4Ldyei0rPJcP4ceyjq3p/3qdUjt4sIPr6n3pjmzyBbZcIcv1LHrn1pMs75JJYncnvTMknJqzYxeLfRp75ok52NbYoIrCFB2UVZzUKMAoHYClV+c7Dy+vrSFxFK6SW5mZUXbGAx6Yqazs4rYbbuerHrVnFJlUHM7BQO5OBUBjuTYGKXOKGT65p9uCDKZCOyDNZ3UuMpSTDp0YjPeRvMfpUA7IruEeJyv2i0bHnKuCfbagQOatapdPeXFvI+ziAc4HZjuapbgbVp6XKrRl6lp2PBOdzUMsKyEZ6CnI4Iwdj+9S4qgWQUMwXBU/wDuppIhyeJ3LCn3kBdOdfvL+1I5P2AEdcA1CAu8tzDNnBGe3pUlnqDwEJISV9fSik9uL2z3+9jIPvQCRGjcqw3FI9uAGljmSVAysCD6UrrzAqehFBbaR+QNC3LIOo7NRK1vknbwpPJKPwt3ohyVgGhmIx0NXpJE8BJwdh1pl3BlfFHbqKpq4aN4H+624okCasGGVOa8V5um39a3PCOh/D6/4Av4tVh1WTXorNr17yGbkW3A+6qIdn7c3NjOdjWEEvLjmYMD0cDHN9O1IpZHcXFJn0F8EuPlutFbgnV7j/WbZC1g0h3lh7xg9ynb2PtXVLQiK6jPTPlNfGlneTWeoW97ZzNDcwSCWKVeqMOhr6g4P450rirhyG+aeG1vIyEurd3ClJPbPVT1B+nasfXabol1x4Z6PwvWeZHyp8r9UdA1CPxdImTGTy7e3vTNGuGn01Q2eaPy71dQLJbgHcMv5ig2lk2usT2jk4f7ufUf3H7VmrdYNdh8D60hG9LSE1CCVTv70WGizXhA5iMIPUnYVLPIeeOBPvStjHt3oDxPcNNeQ2EfRMMQP5jsKMVlk7E3DFosVo984zJMcAn0z/U0TtrcRiR9uZ3JJFSW8K29rHCowqKFFU7O78PUJdPmwuGJQ+oO9R7sPCLssayoVdQR6GsdrultBcNPGhaJtzj8JrbFQaE61PHbadIz45mBVR6mjB4Yr3OeyxhVZicAAkk9qynEJj0/gPWtbMmFZT4Z5+cHblUqfQk5xRriDWYLKAW0dwq3c7CONF8z5JxkL1OBmuc/FbX7yLRdO4UbTZLCF0Fy3jOPEdFJCcyj7uTk71p6Wtvcx/ELlDZdjmNouE5j1xin8xuMxxnCdC/9BUUStMvKMiPuf5qtEpDGMYAHQdK2DzmTwVY0ESAADtTJMZHL096Qyqz/AHtzSOdht8qgDw60U0pQjPMw3Gw+dC0GDV2K9a3hCxIOb+Zt8fKoGLw8s0YIYBpGCIBvnbP/AGqObWLGEbSeIf5U/vWYlnmmbMsjP8zVaaeKFcuwHsOtDB0dvsHp+IJWOLeNUHq25oRd6hJI/wDHnZ2PRAc/pQeTUJ5n8O3XlzsD3qxHAYohg8zfiJ70Vvwc3Nvkr3M8zzrHJ5Yz2B6/M1qNB0O3vdMY3cAMZb+GRsfcg1FaaIt3w5c3MiHxh5oPp1/PpXuGtVMFz9l/BKRy5/C3Y/0oND1rDXV3LsvC1xGSbS5Eqk55Z9m/+3ehV1bXNi/Ld28kXoWHlPyPSuhMUXmJPJjs22fl602VlKGORAyHYqwyD9K7V3yht2Gs0sJ78M//2Q=='),
    11: ('Miel', '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')
}


# Illustrations de progression par âge, intégrées au fichier pour fonctionner sans dossier externe.
PORTRAITS_EVOLUTION_AGE = {
    0: ('bébé', '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'),
    1: ('petit enfant', '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'),
    2: ('enfant', '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAQDAwQDAwQEBAQFBQQFBwsHBwYGBw4KCggLEA4RERAOEA8SFBoWEhMYEw8QFh8XGBsbHR0dERYgIh8cIhocHRz/2wBDAQUFBQcGBw0HBw0cEhASHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBz/wAARCACeAIEDASIAAhEBAxEB/8QAHAAAAgIDAQEAAAAAAAAAAAAABQYEBwACAwEI/8QARBAAAgEDAgMFBgIGCAQHAAAAAQIDBAURACEGEjETIkFRYQcUMnGBkVKhFSNCYrHBFjNTVHKC0eGSovDxFzREc5OU0v/EABkBAAMBAQEAAAAAAAAAAAAAAAIDBAUBAP/EAC4RAAICAQMDAQUJAQAAAAAAAAECAAMRBBIhEzFBUQUUcYHwIjJSYZGhsdHhFf/aAAwDAQACEQMRAD8AomBQ6yFtz1yfHUeUbHptrtSuRG4xnOuMqZ+WmAnMqIG0SIgJJGPy1J5AB0GtEGCdbluYELudHmLAxODJlsDprrHA0h5UXJCljnoFHUk+AHnrWOGeeeOGJC8srBEUftMTgD7nTdf6WksfD1voqOZJ2rZZXqqtOkxiIQKp/AH5yB44BO+MA74IUdzDSvILHsIkhnIyVCenjjUy3UNXcZXjpoTMY1LuRgLGv4mY4Cj1JA0Ws3CN04jnjit1FLKrsAZypEMe/wATP0AHpv5aZ6zhuoq6eut1FWUVu4ZssoFXWVswjSafH9bKRkljvyRjJVcbZJOl2XAHaDzGJSxG4jiV/URSxSuiRwyKu3aJICh+RxvrnuiEzKI8HqSMEeh/loZxJxFSUVU1NaK03GNdnq1gMKk+SBzk/MgfLUemvtDLEDI0kb+JmQn/AJtxp6gkZiXYA4htSki8ysrDzUgjXGdMkbahxy0VTJzQTRCb8UTAE/MeP1GiSIX6jB0YgEZg8lC7JtzgZIxvjz1tGu/QfbXt4AgpxOqjto2AjH4iTjl+upNtjjrBzgnlHUeIPkddLcQQuTidGCQwBmGXfoPIahdTozVQLIgGOnTUeGhG7N4eGhV+IT184EH8snm/31mi3ug/D+Ws0fVg9GdKb4W15NgAk63QcinGupp2eljqdmheR4gw8HXGVPrgg/IjUxPMoxxBTEqc6JRNFXe6qs0MVSkKU/ZTHkEnLkKyue7kjGQcbjqc6NcO8FT8RGWplnWgs1MrPUV8w7qKvxcufiI8+g8d8AjLzx+lv7a28B256OljU9tdXj56yYdObnI/VqfDofl00tny21OSP0HxhisBdz8A/qfh/cmCzNb66AXSrpbQEYSF6mdFfAycqoySdtj03B0Pu/EtFbGtVv4Tho7nWUrzRwwSRtXOA78wbAUR5yOnextrnwD7Mblx7c55q+aemt1O3NWVTAtKzYzyLzdXI8+g3PgNWZx3LbPZJwikVmpoaW73BTFTiPdolHxuW6sVzjmPVztgLjS7HXqBM7m9PHzjaa2NZs+6vqe/yiyntZ4wsrNT8Wy21QUZRTJiKrgyCAVEWVRhnIDD7apasr6qvp6K0QViPTwyMyRyyiJHmc96QlsKCcAZJ6DUM88sjuSZZGJLM7Hc+ZPideCi7TMsr86qNgBgH0A8tV10JX90cyK3UvZwSSPzPMKcT2ePh+VKeqWVisKrB7o8bI7jaRpG335wcKB0x4aA08sTtyKzxOemdt9F1pFejkpH8DzgjzPj9xjUNKBgCjASgbFW+IfXx01FIHJiXIZsgYnB45UcLJyHPR3YBfrnodEaO5zUDf8AmQI8YKwzBvsCMa4NzNG8LbyIMrzftD1/hoQVKOoxzwyDmTJwR6A6OD2lgW2gjuXJXPW+9sm6pzZEZ9R5/QDRugoewuCcuy1CsGH7y7g/bI1XNCXpys9M7l12yDyyL6Z/kdOdi4miapQ3NypRSscnJhQT1LY8dsZ6aU6GPrdexjgKVFUs4BGoEwWMkr9tEHxKoZCGVtwQcg/XQtZI6hn7PJ5GKMCMEEeGpxKjNcyf2es1K5ZfwflrNFkQcGcOXK9NGeD+HLpxNeBQW+YQ07yJJUmZOeEdQpZf2mO4AG538Adcbbb5rlUQ0dLF2tVUOI4kzjmY9MnwHiT4AE6vL2V2enp6Z6umZWtdMXjgqSMCrlxiaqP7uByJ5KD4k6l1F2xSfMp09O9wIM4m4Fqr/CnCtuqnW10Ko9dUzDvVlSxzHG2BgIgzIVGwyq9dEKD2ZWexi3LS0okt9tJqW7UZaurDtG0ngQgDMB0BYeWmejuacRw25bSW90ruarkqAuCYixxj1kIAHkMnVae272lLb+GYaC1TAVF1aUCRNuWBTysy/wCIjlB8gT46z62scipfr4y6xa6wbW5+uwgYe1OitXElDw7a2p1soleKrrCMmaSQkyShvIHO/j8sap7jC+VXHF6rLpIZpoQoIVVPLTQcxEMY8ttz5ljpcgzI5dsgKCowPEjp9ASftozbL3V2iingpWSNJX7Vm5AWyF5Rv5Aba169OtR3IOZkWalrhssPGYEmpwGEWOUftAeA8tdDEpKeSHOP4aLQRUlREJKppjVTszyyA/BnoMeJ14tpM08sdPMpWLALvsC3kPT11SH9ZNs9IKI5J4z+IMv8/wCWsljAZZB1Hdb5f7a9q07GSDmIyJlXI9cjRD9FzSLAy8hiqCUVuYbN4g+Wi3AQNpgWqiw8MniH5T8jt/pqEaMy0sigd6KRiv3zo3JRVBpZnMLFI37NnG4DDw/hrcUq0lBBPIQGqJGYL+7nGfvru4eJzaYA5DEBKucY3+Xkf+ttbTLzyKys4dh3eU4yfL56lBezMsZG0blfprlHRtVFooiquql15jjPLvgHz2OjJg4MZOGqUyJTR181dS0dfzClljkKRysCQy5Gwb02OrBt9hhoUFPTQlY88xySWJ8yT1OkDhC7QVhn4euPettyYNG3jBPjZ18icfcDzOra4VqZp6SWnrVBuNDIaeYgfGw6OP8AEMHWZqrGUmaujrVgPr5TX9Dt/Z6zTT2M/wDY6zUHvBmp7sIC4UsL3GsqaGncpWVdJLT07j9lnwrN8hGZCfQauDiiijj4dh4PsxMJq4FpmkUb0tEP62U4/aYAqo8Sx8tVrS8a0PCeKfhqx3KqvFxIplrbiFYjJ+FIYz6A4zvgZJA09VH6ctVHRwUtBB+kLhNhprnPzzVEgUlpHWPYKoxtzYUYAGuXFiwY8emf5+EVSFwQO/nH8fOTL/UU3CvA9alKRRr2K00b5GaeM9zm9WCAhVG/MSdfI3Flxnvl6nfsSvZqIYKVe92MSLhU28gMn1ydNntnuMtTVrTVV1nuNypayWnmYAR08fKikpFENlALkFjuSNBrNCOGuDqm4yri6X9TT0gOzRUYP62X07QgRjzUP56s0tfTXeeSZHq7eq3TAwBAdxno5WpobdTt7vTwrEHdOVpG+J3b1LE/QAagSd1sMQRgDAG2SdtTQpc79NcRB20qn95m+2w1ojgYmaQSZvG+QSVwBv8AMa3RMxjPU769mQJ2ceMmRsfTqf4a1q0Z4jGucvgHHUAn+fTQ5hbYOqqCW4RGSA9ymX3tyB1RSAPuT+WpLRFWODjB1ZvDXCbD2f3+5SxfraynkEQx0jjU4x8zk/QareU5CL0c4b5gf9tBXaHYj0jLaSiqT5kaeeeIt32xJ3z/AIwCM/PB1yrnepVUPWOMJgdAfL6DbU2siI7NtgoYnJGw2/jqIV5FJIxnffTxiTn0kaknEVeWdFlV40d436NsQf4a51zmWbIyoAPIPIZzjPpn7a2it8jwJdVJ7KJo6WQY/GGIP3AH111ZVfkJG4bb7HOvAgmeIIEgIhhqEcNyA7gj9kg9focHX0X7Pp6e+G4XWP8ArpEgE6nYRyBCHHy2znyOvnKoXBUN8Ib8iCDph4N4sqLJOyPM3uVUBHOUOxAzysR6fz1Pq6OqmF7ynQ6kUWZbtPp33qj/AL3F/wAWs1VP6eov7/S//KNZrH9wP5zc/wCiv5S4vZtbhU8QzVQTnko6Ruz/APckIRfrjn0dquILanEdJWT1Cmm95W0UAG/bPnMrj0LKRnyUeek638QCyc1it7yS3G596pnplLOirET2cQ2yQObLnAHN59KWi4vmv/GPDss3JR22gqoxTwFsJTx8+WLE9WPUn0x0A0zoG52bxj6/eIOoFCr65gha22Vlxrb3eR732lRLPFbVJBqHZi2ZXHwRjbIHebGBgb6k3i4T11nttXWESV9wlqKuVwvKAisIo0UDZUUI2FGw0ooHYIFGWIGx2302XyWnmqoaOjdZKO308VNHKBjtOUEu49GkZyPTGtVkAYTIRyQcwXF1Bzra2lZSoG5WNSfmd9dFh7NS52Cgkn01Lt/DlXaYLWsuXqrovMsaLuuGChfU7/nrjOB3hJWScgSQtolqamhZIi7Tu8MKk458DLtnwUbAt0G+jFxpLFJdrLZKarQ01OGmuFzjjd+2kbGeQKCSqgcq4GMknzOrc4I4KgsoNVX8s9ayCLvDmWGPOeRc7Y/id9G7JZEtlZc7nPKj3K4SmSaUHARBska+SqoH1zrNfVgtx4mpXoiBz5gOq4o4TewVtBQ3aiDLRyRxU7ExttGQFCuASdUrVcPww8JWq8Mjc1WZEJYbIFGY8fPkf76vrjm21F/4crKWigjq6qcBIywVsZYAsCemBk6U+POC6ax+zuqoqFXWKOpp5FV2LcrcwVuXPQHJOPU6Gi0KQB5MPU0lgSfAlMy8sqAgDlO+h9VCX5ggy2Puf++2i8tM0UPKBlugHlorwvw+zxV1/qo2ehtcPPTxhSTU1DErEB5jmOfU61DYFGTMgVFztEmcE8GTXD2Z8SmQZmllYQ7dGhUEY/zZGq2kjH6snYNIuPqNfRPDlVfeGuHaG2/0RklpKdMSFatPeJCSS7FMYySTtn66pa522iNnnqojIlVSXb3fsJe66xFWK8y+B2x9NIotO9s+TKNTSNigdwIt1ESqUz+LH8dHOErDbrstXBUwkOAJEkjblZDuDg+XTY6A1mS3KTjlAP3OP9dN/s3iM9ZWuTgJH0+bf7atsbCEyCpd1gGIT/8AD23f3us/5P8A86zTn7v+7+es1F7y34pf7mn4YVpEpeFeHOMrhTRhK2S2rRQykln7Spm5WbmOTkIjao6vp+SVZOXCTqJVHoSQfzB1e12tplJ55SaRoyskHLszfstn0Bbb11W/tJtq0H9HqmkgHZ1ltiRY1GP18ZMci/Mtyn/NrtDBXwfM5qFLJkeJX0lbBRzNJM6ryKWRSQOdugG/3+mutprHmqqjm6NErjHTY4219IUln/oHbqi12ultyTUSBLjX1FIs0lbUBQZAWb4YwzciqNsDOCSdV9xjwXSXe3PxFYKMW2upW5bhQRIVjZCd5IxjHrsACPAEbiNarNtxx6wj7PsRA+ee+Ip0VGt5qKW3doU97njhLDqAW3/IHVvcH2moucHClxanDy2yoraScYGUDcwDAejKP+LSDwHbIZOOLVSTK6SRVJypGwIjc46fXV+U3DkFGl1gSaUUtwkaUrGeRoy64flYdMkZHkdS6y3B2yzRVAgsfrGDKs449rs1oqay3cOUkdZU0ndqayXeCBiSAoA+Js+vgeuNV/D7SOO/fwtdxC1AjHvmpolCRZ6cycnMFPnvsc6eOJfZ21j4WsVnpGzm41TzS43lk5T2JJ8ygIHlvpGrKTim83q/X64yTtcoYmmesq9yzjAUgkYburgAbYxp9FVOzKjMk1F1/U+0SPhLY4Iv1yj4iS08R26K3XkgyQVtB3aa4KN2VlHcJI3DLg+mdM3F9qvPGjpbKaOK32qKUO9TUtzNMw+HlRd+UZJ3xk6ZIrH2dNZ5q1FevSliaVioH67kAZgMbHLNqfycvTWfY+yzK+JqVrvrAY95T1k9ljTV7zXd5GtcLEJA6dlJVYz8QBJSPPrzEeWmygpIuH6OKKvlSpqZJ2n/AFEB78mMKEjGSFRQFUeAA04SRmTVO+3Krro6E26gu8VtMdFLXTZkMclUodEWBCN8kszYHUIdErve4UmAy16dC4EsaC9Qzc6JFJ2yjaKUBT9QCSBqqPanYo6Dh6mfKtOkpqqmo5MGaV5V5m+W5AHgAPXSVw57N+34Lq75RzLScRWcLVCakqhIzowLjnC55HAzt6bjRnj/AIya88EcNGYoKy4L7xUBRgAREj6Ayb/TVNdBSxdpzzJrNQLKmLjHHH8StaqmzVqAOdzygqPPqFHrllHz0/cC24WC5XmjrpI4qiCNOYM2xGc5Hn1GgXDnD9Wt34YqatAsFY7VMaE94pH3uZh4AnBGrzt/DoqpBcEgUVEqBC5X4lDEj8zp+s1Kquzwf7/yTaLTMzdTyP6/2AO3j/u9V/8AXf8A01mnf9DVnm321mszrLNfpN9CC5MVOVXvE6TbzZqqsakmrKoLT2qvWqSljjBUIGjDkt1yVjyR0zpqqad6eQz00hETZww/MaHmqHMyypzq+QwxsQeoOqxZnkSM1j7rS17tSx203SZ4BLJ77NhfxO0h5fuCN/LSbb6Oqq+LlkravtYZKSVJKdl/V4DDuIvhgnOTuRnRmw8T0F7tyWi9VS0lWkaQJVTHljqgm0bGTokoUBTzYV+UHOcjXl84PrnJ7Opip6yI80NQyMro2+GwDg7HHkRrOxsYhppq4sQEeJxu3AtDUX+3XmnxBPSpynsxyklSDG3rjvKQeqt6DR1iddi5ZQGIL43wMAnxxrQrkaEsT3MIKF7QbcaOG5U7004YxsQ2VOGRlOVZT4EEZB1CPDFPUz07TzyTU8LCQ05RQkjA5UvgZIB3xsM9dGjFk+musUYXGurYyjAM49SNywzJJaSVi8jlmPUnW3TWoPhrNcg4nkkixAFth0zqovafwZT32+PXV1Q1PA8MCxzs2FCKHEiDYjnyysB1IzjVtThmikVX5GZSAxXmx64PXXKX4eUZx5adTaam3CKupFqbDELhThCSxcDXOjp6eGmuN8LGKnYD9SrryRhh6KSx9Tqq6jhy23h7maehWphpofcrV2khRBEmY1c42JZhJISfPV7XZ/crfcKoLh4qeVwR15uQ4/PGq/mpaagApYI1jSjhjpcj9plGWP0Jx886oS9mYn1iH06LXj0nSz2qjWW3PUKstbTQCnEpOwGADgeuNPpvUNEWjBjEMSbnG+fLVXCZklBR8HwOpF1qmoaWAyyg9sSdvADQWU9Rhkz1VxRTgR5/p5Sf2Ems1V/6Vh/tB9tZr3uaek776/rGWgrpWoJY3UFWIIJ8Plr2OWZIZoo2KxS/GuOurF4K9lNTxVYp7jU1EtBBUJmhjUcrSj+0c45lQ9AFwT8XTANV8cW7ibgQzxXDhx6ZNxHX+8S1NO3qH2X6MAfTT1CuxA7yVnKAEyWFyhUgFSMEHy0PuvEfE9kp7dS8NyTmOOJxPDU8ksDOZDyCMMcqOTGQMDI1J9m9ivvGkU1XVzvSWtMrHUdgpM7+IQHYgeLee2u/GNGOGbqKOGSSqUJkyTMsbA4ycYTHiNM2fa2cEwN527wSB6xI9nvtE4lunF1TV1lwmq1eMyNQDAieNWwyxr0V1BDA+OCD119FUtdTV1NFU00qywSjKsPzBHgR0I8NUvwTTU134w4dtNNb46cB5o4WjdTyKYZMjYZI2yc6ama4W4tW2srzthp6ZwSku3XA3DDzG/z1LqkG/AGJZoXPTOTnmWJzZG2tgDpasXGNvugSKc+5VjbdlOw5XP7j9G+Wx9NM+QpweupCpHeW7ge03VSdD3vdMlTLAsVTKYWKSPHGOUN4gZI5vpnRESDXkp5wD3c+PMudtcEHMGW++Ud5etWk7bNFN2EoliMZD8obGD12I1JZsddde6oIAAGc7DGhF6u9JaAgqHZp5P6qmiHNNL/hXy9TgDxOiAycCcLYHMgcZ1sUHDlXG7cpqytKmOpLnvY+SBj9NVNeK6FYvd6MFIx03Jx9TuT66n8X3C411fDJW8kaBW7GmjbmWEHrlv2nOBlumwA2G6vN8XnrR09YCgmZmouLMQJJoK10qE7ZuZAep1pdK2SumLOcqNlXwA1EjUux1IWnYn09dUbRnMn3HbiQuVvLWaJe6v8A9DWaLInMGfZN79o9p4bgc1VSnbYysEZBkb0C+A9TgaqSr9uFXM9YHpqc9sh7KLmyo36P+IY8vHUOs4utVrtjtS08YVWHMsKbsfU9SfUnVfcS8XSXyREiYw0sZ5lUgczHzY4/Ibalp0v2sERr6jC5BjHbONrhbmkamjpoYpHMjQRxcsLEk5PINlz5rjOlfi24yX+aolr8U8lRJzRSxHKocYUAnx26HroK90q4OVoxDMoPejbuk+obpn0OpBuKViNEyKOYd6J98j5eI1oCgA7hIzeWG0mMHsbqaPhi8Xa8XaVZb1TRGC20yjCOrjvy5PjsFI6qM+emeirgJMseuqiqqKSMZp3Z4weYRlu+h80b+R++i1p4qZ3WnqnBlOQkmOXnI6qR4N/HUt+kJY2A5lem1ioorIxHq926GpR5qZVJbd4sbN640v0nEF0s+BQ17rGv/p5x2sXywTlf8pGtlvhU/FoZcpkq2MkZCynqPBv99KWrjBlJvB7RqT2x0dtRGvtE9MpcJ21I/bKSencOHH56aU9oXDkw7t1QMRnszFJzn5Ly5OvnXiOZTHT08gUmaXJVhnupufz5ftoZABTyrJTyS07gYzC5UEeWOmmr7PWxcjiS2e0Wrfb3l7Xbji6VjOlERa6TJAkKh6lx575WP5Dmb1GtuDzbPfppLhVtGJFLSTysXklPkWOSdU3T3irV2jkq5cFTyNnmAbwBU52+WNSo+IalIFkljDbZYwnp55U7/bOvPoSF2iCmvBO4/vLR4iks1dJLGvagIx7OQdcaXv0TSSyIUZ+zQEylzjSe/EBlYMr7j7/bWhvL75mb6HXl0zKMAwm1SsckQxVSU8FRNyApED3Q3XGozXRFOVb6DQSsuEcp5gXMh+IseuojVeCOXx1StPHMka/niMn6Y/db7azS774dZouiJzrmONTRWhqcotNypued55OYn8THmGTpJmWATdpA80K7jEUzYB+p17crlJJQqmNi2+dBnqCqlgMeY89VLVg5Mja3IAEnTXa40sgHbLPEehkGGB8iR/HGtouKMyBZh2bjoHH8CNCpJi2x3HTXCUcw3AIPUHTNkV1DHam4gjk/aAz4g5GvK54a4dohXtR49Q3ofMfnpOslrqbverdaaYw+8V9QlPC02QFZjgcxAJx9Dpj4v4an4M4or7DUVUdTUUJRXniQxgsVBIAJJwCcZPXyHTXdgzie6hxmdaa/TQZin5gg2BY5K/M+I9fvop+ldt230mSVEir3iJIz+IYYfXVjezH2PX/2nWe519ruVvpoKGY0ypWBy0kgiaXGVHdXlUjm7xz+z46W9C942vUN2iRdStynDSSiMojMjk45WDD+XhqAlVNDGrS4ZT1I6r89QhXlwGC7HffXKarLgpyjfqddRCvEGywNzGS31A947U/DGNvmf9tTpZxPlFA55Dyj5nS0lV2EaqAdh11Jp68xI7lcyEbN+FfHHqfPTHGBFo2TH6+3Kz1tBElRTO706BEnjbkk2GAqnG/yOw0gtUFZJF3HKxGGwT6Zx6axatpT2j5JA7o8FH+vrqHI3aTSk7b42+Q0lKgojXuLGSvfAG33HjryauV2yi8qjw1AeRQNgc+Z1p2p0WyAbIQ99HmdZof2x1mu7JzqT//Z'),
    3: ('pré-adolescent', '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'),
    4: ('adolescent', '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'),
    5: ('jeune adulte', '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'),
    6: ('adulte', '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'),
    7: ('adulte mature', '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'),
    8: ('personne mûre', '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'),
    9: ('personne âgée', '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAQDAwQDAwQEBAQFBQQFBwsHBwYGBw4KCggLEA4RERAOEA8SFBoWEhMYEw8QFh8XGBsbHR0dERYgIh8cIhocHRz/2wBDAQUFBQcGBw0HBw0cEhASHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBz/wAARCACeAJMDASIAAhEBAxEB/8QAHAAAAQQDAQAAAAAAAAAAAAAABgMEBQcAAQII/8QASxAAAgECBAMFBQMFDQYHAAAAAQIDBBEABRIhBjFBEyJRYXEUMkKBkQcjsxVSYqGxFiQmM0NjcnSCkrLB0TZkZXOi8Bc0NVR1o+H/xAAaAQADAQEBAQAAAAAAAAAAAAACAwQFAQAG/8QAKhEAAgIBBAICAAYDAQAAAAAAAAECEQMEEiExIkETUQUyYXGhwRQjsfD/2gAMAwEAAhEDEQA/APIrE1DyzVDGaaQlnll7zOTzJJ5nDJ0jYk9mn90YUEhsRfbHB540kq7ESknwhEwx9Y0/ujG0hRmCrEpJNgAoxP0eRxT5ZHVV9VFl0DSMYppEZ3qFsAQkY3IBB72w3IvifyXg7hrMW/2odj1jFN2TefvE/XHHNI6sUpdAzRZBQVZVPyknbE20QUcku/gCB3vlg9h+zv8ALVLTU1TmdVRUtOpEcDUIjQ3NywUuW1GwuzDpg/yHK+H8jpewyx4AzCzOH1yyepAufQbYfEVDn96qUj565QR8wi7/AFIwiWR+izHp4pckHlPDFFw+HqKSuqIKePShfLajs+xO4DMqkltzuW8eVsGENXmQrHnp+IaqmrCuiU0qxwSS25a9iGI8dN/PEHPkk1c5mqKxgygjtAioAP1k+hON0cdXSJLDUR09ZTQbLLMTAyL0GoA7eAIvhMkpO3yUxuKpdHS8LUdHUvUrNmMVTIxZpTKxLMbkk9yx54Xn9pjQgulQh5GSIo/1Flb0NsPqKaSuEsFPT5lD2QBIE6Km/wCmBf5WvhrmfDss4Xt50jLNbTG0kkjnwuzAH6Wx79zvrxBuqzaLLdc5pCuj+NNM7FlG+7xNuR6XGCDJc4oq2KNbRpDUAmJrfdkna4vy32YdL47TgfKH0rVCpqSOStKVUegGITOMz4QyFHoYKSeqdGOqmoHZgjEHmxOlT+vHeHwgfKPLfBOvQUsOdZc0va06iRoklhH3lO7A7C/NTz0nYkEYluM/s6os5ooqiqjhikYAJXQIO6DcK/6UZNwVPeU7X5YCqvN0zHK3akFSjwqA0VXbtot+4SRsy3Fgw3F98T9Jmkwho11uRMJZXZje5fcfqH6sLlGTdxdMdCUKqStMrD2SVVzLhvNIF9syqKWehcC5iEZ1ywg23jZCZFHwsDbZziAalAteIC97Erzx6fzrg/JMtynPM9qoEfMjRy08M7kjs7wOmhR8Z+90k9Ao8MUDl1O1Ya2hcEj2SWpjJ+CWGMv/ANSqynx7vhhmn1G5N/X/AJkmp02xpX31/QPxwKre6tvTBvleZ5Xl9E9JUQxVcVYoilhts6sQCD5WJ9DY9MBTODywvTbzw2/PX/EMWNW0RxdJ8FXZtRpl2bZhRoWZKaolhVjzIVyoJ+mMw44ouvE+eDwr6j8RsZhrqyNC4w8y6GN52lnTXTwIZZEvbWBYBb+bFR6E4RoqWauqFggTXMwJVAbFrAmw8TtsOZ6YWpWcmaljjZ5KhQgRRdrhgw25/DbC2x6Q/oqHMeMM2cNIpkK6pZnFo4YxsNhyUbAKPIDF0cLcKUmVwCmgjPZLZ5nkHfmb4dfl10DYDncnDDg/hSoy3LIYpIkp2JE07Sbs79LgfCo2A6kk4OoaYQQiOk1SMSSZXHMnmfM+WJsk74Rfgw7eZdiNZFSy9pBKJVUx6NcI2B97vKLE9CT5gYWo46+WAAT9rbYWCsRz5vaw/WcdQ0USz9m7K8537K9z6sP9dsPp632NV7QszsdMcabs58FH+fIYVfopr2MJofY5dVRHPLIB75N7k8kjU8yfE2sN8PKDJp66JKuaIpEG7pF9CnqE/Obxc/LG6Vo4neWtZJayQFeyjNwg/Nv4eJ5n0xMVPEdRR0Sw1E8EMEa2WNkAIX0F2t9L4CTfoKKT7EpaqLL40hjSxN9Ea8yep/1OGMlRBSK9VVOokItqtyB+FR5/U4bU+cHMtdRT0IVHbs45pRbXY95yPhjXew5sfDErS5LS10j1UlaiJGpaMzg628wo2ufAchj112FSfQF5yuZZ3G8UbvR0sp7NIlNpJSerke6oFyVHQWJ3wvScN0sFPBQQD97w+6tgAW6u3n18sGOX5GldnohE8bIkIs3uqpe5tv10qLnzxAfaNLBw3kGcGOYLJIIqNJBvZ5d5CPRAfrgt3oFxS8mAL57ltfmU9NQ0LIkcb9jWM5/fYH8YpS1gpW5XrdRicpcxNDTwFQhZEUPIwPdW3uLbkxG5b4QbDc4EMspDA8cj6D2TJKrL7siFtN19QRcYnMyzE5JSRrTpG9eVtEZF1LCvLWV6sTso8r4NxXSExk3yw0XPI8xlgpa+my9qV10QpU0TrF17uvtNSnzw7znhjhHK8jzWrno6/I6sxdhLLCWrESN23aME+63uk7kA264FOFcyrc+yaupMxkM1fTWdJXWxdTcqSLdCCPQ4OclzH2mhipquJamgnisYZNwAe6yH9Enb9EkHliXKtv5SvFU15FCZzkHsUEtfluY02cZSrBGqqZWRoWN9IlibvITyB3Unkb7YiomJlp1G33ik2/pDBLnHD37jeM/YlkebKqsrEGOxnpJjYX/SU/R474ghTGlr+xYhmhn7MsOpV7X/AFY0sMtyTuzIyw22qorXin/anPf6/UfitjMd8WLbivPx/wAQqPxWxmHy7ZBHpDhbq4Katd+7p536Wt1vi2OGc7zSkr6PKa2oOYZvO1nQhbUYsSRJLbUzAXJA5cib4rfKqj8nzz1qi89NEWgJ+GQkKG/s3JHmBiwfswy1ZKeprJEZ5J5PZkHUooDyb/pEot/XE+R8F2BPckizMtnzGdjJUCigpBcr2epncb73Oyj645jrDGHWtq6uen1HROs2mEr0DFVupHW+x8cMzULW1E0N0aJD/J2cv+lptuL7Actr45qMrFc69mkzEbdrPI4VPQXF/QAYn4NBJ0EkKwyUZSlhjhDHuyREOAfEW5n1xxNDSUxaaY65iLGeqkCbeA8B5DEIeDaHsGcs2sXZ5XkMaAePdsAPXfEavDNIzGaqpw1KvejgiBM1V4Ek7ql+mxOOKjrv6JmHP6asrBl+V1HtVTYsyUI0RoB1eU8h6XOHq5G8yytWdmZGfsoo4gQiE8233ZgOp64e5XTU/D2X1FXPHElTIBrWMWVTySJfIcvW5xMGDspAr84I7G357bscC3XR2Kvsj3hDyR08aBKWJV1KNhYe4n+Z/wD3Eh2ym8etVIUu7NsEUc2PgP8ATEDJmkXbiCD9+VkrnRTwnulupd+VgLXtyGB7iOqmzekqcuopC1MxC1NQgsKqQmwjX+bB5+Nrcr3W5JDqtcBtkVQK3LPyj/Fx1ZM4LC1ouSE/2FB+eAzizMEzqh4daJCxzB5qlVcdDpVSfQf54k+K81egySPJqPeaaERyMOaQgWPza1vS+IyjgWpg4bl/9tSTxDyPaW/ZgJzqLZ2MLaQlUcK5e0KCJTHMqlS6k6XvzuvKx8t8QPEOTZhFFJPGVk1t33DaWUWsANtvC/h4b4PliPhjiqphU000TAd9SMTQ1E4vsonp4SXQGfZR2M3EObUoEsU3sTF43bVuHG4PUb4umLJDkqSsqRyiJY6uNJB3WWQaZIz5E33874qLgOmWDi2srdhoy51bzu6gf54s+gzWWoqilRKXjjVYrnpFawPyuD8/LD8spSVoTiiovawS+1jJ4zBl2fUyyCnoag9vFKO/Ex3UE8irPHsfHV1OKZhmEtXADIrSPKvXcksMehftYqPyLw9w/nHaO1CaiWkzClU/+YgdR2gt+chTUp6MAcUDWS5hkuevQPmEz9hUqgkjIQSrqBVhYDZlIPzxXoJuUEmQfiEVGborXivvcV5+f+IVH4rYzHHEjauJM7J5muqD/wDY2MxpPsw4vhEzTZdXNXtRnL615ZLxtEsDFx8rdCBi8+DuDpsqyilpq9XTSGeSIDvSMxuQ1uSiw7oNzbfbbFV8N8TZxkuX5hPHmVcaCkVFWiWpdYmZ2IF7HYAAmwtg/wCGMzq+KMoWrq1ERknMSxxySFWRbFmbUxJ2uLXttiLJb76NbAop8dhrVx0VbGKZEgYp3daqLQ+SkfF5Dl1wtNBFRRJGK2pD2skZIkkI+Y2H/e+Bqt4gpUkMFNmLnQdC09Ggsu9goIW256k/LCK1FRV1M9DQ5vQQ5mCQadGZpXYX7omYaS3kPrieUox4bothFy/KrCKppnZQJXeaYG6RSsWSM7kFhtqPkB9OeI+LMzA60uXJLV1UzEvU31a28QfiI/ur59RekaoSSaE09RPLcrJDYogO9+1kO55chztgvyqsbLI2aWIT1syi6xpYhOiqvwr67nBMGPL+jZp5DmeW0tazSSzzgBVJKxqt3a225IUAt57WwjxLmVTOyUvtkMCVReokWZ9JZL2UEDvEX+FQScbyurzLNuI4KmeNabLlE0admbmVtBvduZAG21gTiMnqXUSVtNl088syF2WErrKC4F2a1gNhhGTIukPx42+ejBVVMdO1JR0tSKabu1NYir7RMPzVS4KR/o8z1xN5ayGmjhiQVBjmvphQq9/hTQdwxIsB5E9MV3U8U1cFPUO2UVEKQ1GmZ+0QspIOlDcCwNjvvfocbquKoqmnSnqqfMaCVQawSVFKxDBhZZC0e6gKO6bbXPjgFBvtBfJGPTLESmSpWSpeRZKl2vMBzjbkFsdwABYfPHCUrIaUwEI8FRUKFPukMEfSfI2bfpgIo+L8xEkK1Nq+NwTFUK+p2Xf3ZV3PowNuuCejzxJZ5VTWZFjFR2MqaZSYyQQOjXQtax304F42rad2Es8WopqqYUFw6HSCjjmGG64Rkc2Nh9MaiqGrnlnRQKdfu4yCG12O7XG1r7D0OI3MeweknM6hpO10RAkghuhHgBuScRqPNFjfFgy08uR5LUZibpPWV8FLGvUxRN2kx9LlF+eLXpadNDlVBOll9RvtiquII1rcn1pcxIqpTg/mdoCX9XYlvQDFl5BmArqarTQEaGaREA+JLtZvqGxc5eBGl5nH2q0D1/2ez1UTdrAOxzFDb3T/ABUwO3O5BOKAqz7TFwvUEfeyRJA58TDMYwf7gQfLHqzPUynK8iiyLNZlp6fOopqQSv7sc0qkgk9BqUAnyXHmDOcvfKc4yjJ5QRNlsdPHKG2++kcSv9C4X+zhv4bO/H9f4I/xONeX6fyVXxED+6LOf67P+I2MwpxKAOJc7HhXVH4rYzGy+z59dEktW8eX1dEFBWpkidmPMaC23z1YuXhKhEeQ5PFMAlLHRdvLq2DM7sVB+Vzbrtiukyanrs0pYpiY455kjeRDuFZrE+HI88G2WcUUubcRRZNldKKPK6dJFRmJeWURqbC5929um/njOlLd1+5tYobHz+yCrtxV1iLDAFhprzRx6LF5b6UJHQBmuB+iTjWb5BLS5Y1PR0issQuJHYRpGd7uWPxXw+p6iloK5xpF4oomIA3Co7Bz8u0U4ic8ifiDOKinnfXS0zhEjLWjUabl/Akk7HGbmn/sNfBBPFf2R+cwpW0tJmU0rTTl0Sb2WU9nKVbS3Ib7EG+CkrUfkqoaLsI5JLhViQkR963vdWF/TDbhvh2CLhGaUntZKoSTLfcJe4AAt4DfC1KjVVHRO8ixJPKo03ssYVNlAtz1Hn44PFkqLX0LzY/KL+yUko5KeiiWkVQ9KV7MNytbSf1E4TymihTL4uzFw6jUzDdiNt/2WxJxzA66edQX02YdHB2uPX9WNxxJCrgMxDNq73T/AL/zxnubqjQUfLcDtVwxDLIuuJ5kVdKsrWkRd+7c7MovsDyw9geqyVZvZjIxkXSxnpbuQAQBqXmADyO2JYq17g45eJ5QQ0pVPBBufn0wccsl7FyxRfoAqXhnK5ZpZ0hNGZJDMqxkq0c63OpFttcHcctsSkWQQK8LsTNPIQ7AtcRLvzt8RuRb1wSimhhN400tbnckn540IReygC5vsLC+C+Vv2CsSqqBjijiSDhXLQexFNECIk0KNKk3sAOX1wB0PFCZnPJUVGUrU0CqwKx1O4JvdnfqfUAYM/tE4aXNooqKeUgCsRtSjneNrDEBl3CeR0jZjUVz19BmHYmOi/JkYEatpNnY82FxuvXVz2xVp3BR57JNSsrlx0SFTUQZjltQaPL8xjjigeqZnjRlsnXUG5X09N8WDw9lj5pTUq5VqhnjUMxf3+0kZV38QHBH9o4DOAcuzHNkzPLMxo2jEEoNbUKtkmiU6o41Ftizbt+iMWl2o4NyPOM4VBqocrkmW42MiuNI5dHcD5HAZcj3OC7GY4LYsjYEfbHHV8V8KZXnVAe1paIyrVQJvoBbSWtbcK62PgHU8sVZHxNmea1OXxVFZSJNEYoBXT08JnCBrAGUqXNhsOu1r4keHeJI6/wCz7i3h2vY6oohm1JOL3WVGRJUPk6t9RgGpgqTw2561/wAQxo6XDtThL0zJ1Wfc1OPtAlxN3eJs8HhX1HP/AJrYzGcVn+FWfcv/AFCo/FbGY032Yy5ROxVkkSFBcgb+mFsnrRkWYJmqsGenJMUV95GIIN/0QCb+dhiPWSwcdDhEHXIEUanY2CgXLE8gB1viNovUnaPQOYxqkj5hSOO1p5YXgLe7IskW6N5MCt/C1+mHMWVZXnuV+3UkstOhBN7XMVjvG6nY6T0PyNsM+G8qqJMqjoqoIZ6Y0vtA1AmLTGRpbwawF8aqsxmyLih46COOpjmp71lPr0hpQO6VNrBwpAN9iLXxm6jHa3LtG3psu17X0/8ApOcIZfVZVDVpJVQ1FDUP21P2asNF/eFjyB2I+eFVo5FKS9mNKyd2AAbJq8xa9+98sCtR9pMy5lQQRZSIKN6hIZWqHvJZm03ULsLH1vg/jj+6Vm1FwTsOQ3Nza2JI2rb9lUtrpL0ZJEX694cjhSnYvECws24Iwoq3ONxgaDtYXP7cSlZsLcYxgFUliAB1x0hOgFgATvbwxw0ioe8wB8zjyONnHS9jbzGM0X5D5Y49oicEq4YA228cMUnqDM5OYUyhLkwmDQLb82JJ+eGbGL3I44myqoFKWZe8vZzix1bA+XlfG8vooKzsoZpooFZheWUgKg6tc7CwviEbjaqzurFFkdPqhRtMte6fdIu99APvEjxwT0tKJWmY0jVccUZc0yi5mJIWOPl8UjIv1wTuKpgpxlyiVanp8r4azPOa2vamyt2nroaOBQFjVwFQsbXkkYaCAdhrHhgI+0TjRcy+zEZolTK/7pTBQpSkDRRiBtc6Cwtcuq+t74Z/aHxNFmvBdTS0cyTJl2ZwUVXLHbSwVJG7QW+B5yQDy7i+WKdOfV9JB7HBUOKPQEemkUPE53JZo2BUm7He1+W+LdLpm0py7v8Agztbq0rxx6r+Tiir46TLMxj3aprQkAFtkiDiRifMsiADwDeWOKa7Swm22tf2jDBASSTzOJSliIeEddS/tGNqC5MOT4A3io/wpz3+v1H4jYzG+KVtxRno/wB/qPxGxmGy7ZLD8qJdY9QNsOqDNq/LI3jpKjsASe/HGgkFxY2ktrA9CMJhBucd0zQRzBqil9ph6xdoY9X9ob4kaT7Lla6Lr+yOCGi4XlkqtmzCSSrIPMxJ3A3oW1Hzth/SZdTZ9ndRmgcrFVUtNUJoFr6h3gduugYr3I8yrKk5hWzyqKmvojT09PGNMcEPaCKNVXoNRaw/Rv1xZHDOWSZPUx0oDyUvYtEkmm4XS1wp8ObW8b+WM3VT2p/bNnRRUnF+kdca5ZFVZFMEiVTEC8YVbaSvfFvmv68E0FpwXS/ZSDUptuwO9/Ib41XxI9FJsDo79j1A5/qviCXO4slMFDmN4Itkpqw/xUgA2Vz8LAbb7Na9+YxDilfBoZlXkEgGklTa48MY5A1p8RUm2Mcrc6FJsty3+n7b4SMydmZCQYwNVx4YCcGmHCaaGmY1jU1PLK4k7GLSpEKlndj0Ft7AeG+IKn4uyqSSYQgwOoIL1EEkTHny1Lv9cEkIkEqLLpDIus2G4Zud/QbfXD4sdBJY2t44ep/F4pck+x5fK+Abg4iyypRUhqoHdRYhJL7C99ueE6tZa6op5acRNAlxpUix58z19Oflh62Y0M8zKoqO2W/eSnNx88CmdZLFmwq2oMy7CdiUdooxsRfZl5g367Yassr8uhbxR9dhZDlT0sQ7OFjTFiI2RdhzOk25EWNvHEX9oHGv/h7meV5CiLPVaPa84jV9JVZI2SOBWHJlR2kv+cyeGJDIOLa7J+D88zPOqeDVlfYq2k9yrlVroALc3NgQOQLHpjzvmmYVmd5rW5pmE5nr62Vp55T8bsbk+nQDoAMHp9OsuVyl1/YjVal4sUYR7/oVpMxqMtkmNBVTwh0MJZTpLx+DAbdAbeOIqbckk3Pjhyo2OG8m7WxrJUYjYtAgLKLXxK06/fxf01/aMNKSK5JHMDD6nU+0Qi2/aL+0YdFAMB+LB/CvP/8A5Co/FbGY3xYP4V5/fn+UKj8VsZhrXJLHpBFFluYTRPLFQVckS83WI2GGC1EZPvr9cNIqhK13lkDPMWOszXZ9V97k8ziQpqWatqIKWlpnqKmodYo4UW7MzGyjwFz44gUmuzScU+g6+ynKfy1xZHO51w5bD27WO1x3Y1/vMT/ZOLupoey7SPop29LYDfsfyV8n4Zq62WERVGZTkgW3Ecd1X6trP0wcMQs99twFxiavJvyv9D6HQ4vjwr7fJyy3DL0YWwN08EOdZVPQVa9osbGFvEEciD0PLBWEDXxCwxCDOa6MrZZQsqm2x6HE8WVS7AjL83zLgusbL6hDW0Ce7E2zBTyaMn9anbwtg6y3MqPNoTVUohdCxICqRoIvsQdwfXDPiTJFzij7gAqormM+PivzxWKz1mXVLSU0jwTqwDrcgSBTfS9um3rjQwzU1yZ2WDg6XRctQOxIlLgHQAVtu35oA8d742ZwqElhpvbn18MCXDvHVPmtS1LVD2SuLHRFIw+8G+6nkb77cxgvVoZCGsLRqQpA6Hnb1tbBZNOpvdYOLO4KiJmpY8xq2uHUIpDOLqTfw8QNzhPLsljoTOwj++mcazbdtrKOXh+3BBpS41Df3fTx+gwRe15fkfDtfxNVUplkySncqoW+sgjRccr3IUnoMBli4wUYh45pycpFC/bDWRwz5XkNNWJJ7GJKivhiO0dWx0hW6ErHYeWput8VhbvWw4nnmq55Z6iQyVEztLK55s7Elj8yThNE1MdsauLGscFEw8uR5Zub9nPwnCAQtLa2Hzx6VNxhPQIwDqUlhc26eWGXyBQ/ooCVLEWB8cP6cwRVcId7OsiGx/pDEYlZogKb6hyIwlC7SV1Ox3JlS/8AeGOpOT5OOSiuFbBLitr8VZ8fGvqPxWxmOOKr/upz3+v1H4rYzFLqyKK4ROcPZbk9bn8K51V1NJl0xs8lOFvr5C7H3VPVgDbHq7hzhzh3Kshnyaky2EZfUj79GuzTkHYu/vMR0N9ulsePA910mxHIg4tv7NftKkpFiybNJdQUaaWoc7kdI2P7D8vDGbmxNq0a2nzRTqRcNXks3DURnoamatylnt7FM2qohJv/ABTc5B+ge9YbE8sM6muhqKY1VLKskVgysvkd/wDS2BubjKbMc0o5ojppKWdgAf5Q2Kk+XUY44kzWNGFVTP2UtQSkygXWXbYsPzrfENz1vjPyaW/I1MWrrx9BgK4DTuN98Ma/NFpqqnlawje8THwJ3X9hGBOm4gWqWNWOidFsyX5+Y8RjjMsyZ6drN3lIZfUG+ELT8lD1PFhuKxD1FsBvGOVCYnMKZbn+WUD/AKv8jhvHnRdQ2rnhRM708zcYOGJwdoCeeM1TAitpIpkeOdVdSLkX5engfPEnlvGXEsFTR0FHFTZiGKxIkgKysdwCWG2wt06YzN6WJ5GqKYoqH30Y2Av1H+mHFVmeXcL8NZhJQ97N6lPZUqyPdaS4bs/AKms353K4rTdJJEbS5bdUStB9sOWSiQVNHVxSLqCxjS9x9Ra/psB54Z8afajPxJk8OT5ek1Jlp79UGIDVDdFNvgFgQOp3PIYr1eIKkRJDK0dTAihVjqo1lAA6AsLj5EYQNdSPOGameKI+9HTyW+Y16rehP0xT8STtroieaTTSfYusWo4eUtMC1jhOakMVA2YUM61dEjBZQ6iOeAnlrS5up6MpI8bHDRM1EQuy2A63w29y4FVtfkSNYiRmxtiFW2t7CwLEgYd508tC8SyhXE0Kzo0DiRSjC43W4v4jmMQ8VV2mluRPMeGCiuAJyV0SrG2wxlLIBXUw/nU/xDDFqrnfCdLUn2ynP86n+IYdGImUkkQ3FG/E+eH/AH+o/FbGY44ka/EmdG/Oun/EbGYY1yIi7SNNILhr7Y77Tzw0I2NtvLGtZFsBtD3B/wAOcRmWmFLPKfaYzdGPOQdPmMTtdmzT0zAqSR3hbxH/AGcVKGNwQSCDcEdMTlBnNXMjI5Vmjt3jzI/1wqWJD4Z2uGGH5QWRFIYi26kbEeYw4izh9NpjcctY5fPwwGJXEMUsVIO1twMOjVmFHmN+6p1DnqHgR1wr4UUf5DCiLMdBePV7p29OmNtmunrgGXO43LSwLIqoO8GA9dt8YucGoTWgbTcjfHPhR752T1XmE1ZUmNnKxK3IeHj64heJs6NTWQUyn7mmQ2HTU3M/QAfLGhWsFZvAXxF1ESOx7QX1Kp1DmDY4ZDEk7E5czcaO4qw6tBN9u6T+zCpnZvit6c8REyPTShdVyNwcKdsSScNqxG9kk9VZdt26E4Rq5GqALuRp5AcsMle5J8DjtpDbBKJxzs6iqZYNXZu0Z66TbEtR1q5hAlLJZa5WJimZtpQf5Nr8jfkeW5B53xAObnzxpTf0x6UbOKdEy05uVYFSLggixBxqmmvWU/8AzU/xDCVc0j9hUyNqeojDMepI2JPrYYQpmPtUB/nF/aMHDmgMrq0Zn51Z9mx8ayb8RsZjjOTfOczPjVTf4zjMdl2zmP8AKj//2Q=='),
}

def portrait_anime_html(av, width=300, border=True, age=None):
    """Portrait illustré avec une vraie progression visuelle selon l'âge.

    Les étapes de l'enfance et de la vieillesse utilisent des illustrations dédiées.
    À l'âge adulte, le portrait choisi à la création est conservé pour respecter
    la personnalisation du personnage.
    """
    av = av or {}
    try:
        idx = int(av.get("portrait_id", 0)) % len(PORTRAITS_ANIME)
    except (TypeError, ValueError):
        idx = 0
    label, adult_data = PORTRAITS_ANIME[idx]
    if age is None:
        try: age = int(av.get("age_visuel", 16))
        except (TypeError, ValueError): age = 16
    try: age = max(0, int(age))
    except (TypeError, ValueError): age = 16

    # Choix d'une illustration correspondant à l'étape de vie, pas un filtre sur un visage adulte.
    if age <= 2:
        stage_idx, phase = 0, "Bébé · chauve"
    elif age <= 5:
        stage_idx, phase = 1, "Petite enfance · cheveux courts"
    elif age <= 9:
        stage_idx, phase = 2, "Enfance"
    elif age <= 12:
        stage_idx, phase = 3, "Pré-adolescence"
    elif age <= 15:
        stage_idx, phase = 4, "Adolescence"
    elif age <= 20:
        stage_idx, phase = None, "Jeune adulte"
    elif age <= 30:
        stage_idx, phase = None, "Adulte"
    elif age <= 40:
        stage_idx, phase = 7, "Adulte mature"
    elif age <= 59:
        stage_idx, phase = 8, "Maturité"
    else:
        stage_idx, phase = 9, "Personne âgée"

    if stage_idx is None:
        image_label, image_data = label, adult_data
    else:
        image_label, image_data = PORTRAITS_EVOLUTION_AGE[stage_idx]
    outline = "border:1px solid rgba(95,165,255,.55);" if border else ""
    # La couleur choisie est conservée dans la fiche. Pas de filtre global trompeur : il teinte aussi la peau.
    return (f'<div title="{html.escape(phase)} · {age} ans" style="position:relative;width:min(100%,{int(width)}px);margin:0 auto;overflow:hidden;border-radius:18px;{outline}box-shadow:0 14px 34px rgba(0,0,0,.28);background:#101b32">'
            f'<img src="data:image/jpeg;base64,{image_data}" alt="Portrait illustré {html.escape(image_label)}, {html.escape(phase)}" style="display:block;width:100%;aspect-ratio:4/5;object-fit:cover;object-position:center 30%;"/>'
            f'<span style="position:absolute;left:8px;bottom:8px;background:rgba(8,15,31,.90);color:#e2e8f0;border:1px solid rgba(147,197,253,.45);border-radius:999px;padding:4px 9px;font-size:11px;font-weight:700">{age} ans · {html.escape(phase)}</span></div>')

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
    # Cohérence visuelle stricte avec l'âge : nourrisson chauve, enfant aux cheveux courts.
    if age <= 2:
        c = "Chauve"
    elif age <= 7:
        c = "Court"
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
    # Les très jeunes enfants ont une tête plus ronde et des traits plus doux.
    if age < 3:
        face = '<path d="M39 82 Q35 34 100 32 Q165 34 161 82 L151 119 Q139 151 100 153 Q61 151 49 119Z"'
    elif age < 8:
        face = '<path d="M42 78 Q43 36 100 36 Q157 36 158 78 L148 120 Q137 155 100 158 Q63 155 52 120Z"'
    elif face_shape == "Rond":
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
    if age <= 2:
        back = ""
        hair_front = ""  # nourrisson chauve, pas de calotte de cheveux
    elif age <= 7:
        # cheveux courts simples, sans longues mèches ni queue de cheval
        back = ""
        hair_front = f'<path d="M42 88 Q38 43 100 36 Q162 43 158 88 L143 74 L126 81 L109 67 L92 80 L74 70 L56 88Z" fill="{hc}" stroke="#080b16" stroke-width="3"/>'
    # Expressive anime eyes; infants have larger eyes relative to their face.
    eye_y = 100
    if age < 3:
        eyes = ''.join(f'<path d="M{x-18} 101 Q{x} 78 {x+18} 101 Q{x+14} 124 {x} 125 Q{x-14} 124 {x-18} 101Z" fill="#fffdf8" stroke="{ink}" stroke-width="3.2"/><ellipse cx="{x}" cy="105" rx="11" ry="14" fill="{iris}"/><ellipse cx="{x}" cy="109" rx="6.5" ry="9" fill="#171827"/><circle cx="{x-4}" cy="99" r="4.5" fill="#fff"/><circle cx="{x+5}" cy="112" r="2.4" fill="#fff" opacity=".9"/>' for x in (76,124))
    elif av.get("yeux") == "Souriants":
        eyes = ''.join(f'<path d="M{x-15} 103 Q{x} 87 {x+15} 103" fill="none" stroke="{ink}" stroke-width="5" stroke-linecap="round"/><path d="M{x-12} 104 Q{x} 98 {x+12} 104" fill="none" stroke="#ffffff" stroke-opacity=".7" stroke-width="2"/>' for x in (76,124))
    elif av.get("yeux") == "Fatigués":
        eyes = ''.join(f'<path d="M{x-15} 99 Q{x} 91 {x+15} 99 Q{x+12} 116 {x} 117 Q{x-12} 116 {x-15} 99Z" fill="#fff" stroke="{ink}" stroke-width="3"/><ellipse cx="{x}" cy="107" rx="7" ry="9" fill="{iris}"/><circle cx="{x-2}" cy="103" r="3" fill="#fff"/><path d="M{x-15} 99 L{x+14} 101" stroke="{ink}" stroke-width="4" stroke-linecap="round"/><path d="M{x-9} 119 Q{x} 123 {x+9} 119" fill="none" stroke="#865e63" stroke-opacity=".5" stroke-width="2"/>' for x in (76,124))
    else:
        eyes = ''.join(f'<path d="M{x-16} 101 Q{x} 83 {x+16} 101 Q{x+13} 119 {x} 120 Q{x-13} 119 {x-16} 101Z" fill="#fffdf8" stroke="{ink}" stroke-width="3"/><ellipse cx="{x}" cy="105" rx="9" ry="12" fill="{iris}"/><ellipse cx="{x}" cy="108" rx="5.5" ry="8" fill="#171827"/><circle cx="{x-3}" cy="100" r="4" fill="#fff"/><circle cx="{x+4}" cy="111" r="2" fill="#fff" opacity=".85"/><path d="M{x-16} 101 Q{x-3} 87 {x+16} 101" fill="none" stroke="{ink}" stroke-width="4" stroke-linecap="round"/><path d="M{x-13} 97 l-4 -5 M{x+11} 96 l4 -4" stroke="{ink}" stroke-width="2.5" stroke-linecap="round"/>' for x in (76,124))
    brows = f'<path d="M59 83 Q73 77 89 81 M111 81 Q127 77 141 83" fill="none" stroke="{hc}" stroke-width="5" stroke-linecap="round"/><path d="M61 85 Q74 82 87 84 M113 84 Q126 82 139 85" fill="none" stroke="#ffffff" stroke-opacity=".18" stroke-width="1.5"/>'
    nose = '<path d="M100 105 Q93 119 100 122" fill="none" stroke="#8f5e4c" stroke-opacity=".8" stroke-width="2.4" stroke-linecap="round"/><ellipse cx="97" cy="123" rx="3" ry="1.5" fill="#8f5e4c" opacity=".45"/>'
    mouth_type = av.get("bouche", "Sourire")
    if age < 3:
        mouth = '<path d="M92 137 Q100 143 108 137" fill="none" stroke="#81394a" stroke-width="3" stroke-linecap="round"/>'
    elif mouth_type == "Neutre": mouth = '<path d="M86 141 L114 141" stroke="#81394a" stroke-width="4" stroke-linecap="round"/>'
    elif mouth_type == "Grand sourire": mouth = '<path d="M80 135 Q100 157 120 135 Q116 153 100 153 Q84 153 80 135Z" fill="#7b293b" stroke="#642334" stroke-width="2"/><path d="M85 138 Q100 145 115 138" fill="none" stroke="#fff4ee" stroke-width="3"/>'
    elif mouth_type == "Moue": mouth = '<path d="M86 145 Q100 132 114 145" fill="none" stroke="#81394a" stroke-width="4" stroke-linecap="round"/>'
    else: mouth = '<path d="M82 137 Q100 153 118 137" fill="none" stroke="#81394a" stroke-width="4.5" stroke-linecap="round"/><path d="M88 140 Q100 147 112 140" fill="none" stroke="#f3a6a0" stroke-width="1.5"/>'
    wrinkles = '<path d="M65 128 Q74 132 82 128 M118 128 Q126 132 135 128" fill="none" stroke="#7c5547" stroke-opacity=".3" stroke-width="2"/>' if age >= 55 else ""
    if age < 3:
        wrinkles = ""
        brows = f'<path d="M60 86 Q73 82 88 85 M112 85 Q127 82 140 86" fill="none" stroke="{hc}" stroke-width="2.5" stroke-linecap="round"/>' 
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
    s = 0.94 if age < 3 else (0.96 if age < 8 else (0.98 if age < 14 else 1.0))
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
            "avatar": {"coupe": "Court", "couleur": "Noir", "peau": "Beige", "yeux": "Ronds", "bouche": "Sourire", "accessoire": "Aucun", "tenue": "Classique", "iris": "Marron", "forme_visage": "Ovale"},
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
            "chakra": 50, "jutsu": [], "rang_ninja": "Aspirant", "victoires_combat": 0, "clan": "", "nom_famille": "", "volonte_D": False, "personnes_scellees": [], "bijuu": "", "bijuu_maitrise": 0, "sharingans_voles": 0, "akatsuki": False, "ami_vexe": None,
            "faction_manga": "Indépendant·e", "notoriete_manga": 0, "fruit_demon": "",
            "energie_occulte": 0, "techniques_maudites": [], "agence_heros": "",
            "faction_fantasy": "Aucune", "renommee_fantasy": 0, "statut_ninja": "Village",
            "armure_niveau": 0, "entrainement_heroique": 0, "radio_lue": [], "journal_actualites": [], "secrets": [],
            "actualites_monde": [], "etat_monde": {}, "monnaie_monde": "Euro", "alliance_monde": [],
            "missions_reussies": 0, "missions_echouees": 0, "examens_ninja_reussis": 0, "progression_grade": 0, "performance_metier": 35, "succes_reclames": [], "evenements_vus": [],
            "prix_marche": {}, "objets_uniques": [], "titres": [], "prime_recherchee": 0, "marche_noir_debloque": False, "coffres_ouverts": 0,
            "maj": "",
            "personnalite": {"curiosite": 50, "discipline": 50, "empathie": 50, "impulsivite": 50, "ambition": 50},
            "humeurs": [], "monde_factions": {}, "boss_historique": [], "objectifs_heritage": [], "objets_histoire": {}, "traits_evolutifs": [], "derniere_maj_monde": -1}


def new_game(nom, genre, univers, ville, av, attirance="Je préfère ne pas préciser", clan_choisi="Aléatoire", nom_famille=""):
    g = defauts()
    g.update(nom=nom.strip() or "Alex", genre=genre, univers=univers, ville=ville, avatar=av, attirance=attirance)
    if univers == "manga":
        g["saga_manga"] = (
            "jujutsu" if "exorcisme" in ville.lower() else
            "onepiece" if any(x in ville.lower() for x in ("grand line", "marineford", "baltigo", "port libre")) else
            "naruto"
        )
        if g.get("saga_manga") == "naruto":
            clans = ["Uchiha", "Senju", "Uzumaki", "Nara", "Hyûga", "Akimichi", "Aburame", "Inuzuka", "Yamanaka", "Sans clan"]
            g["clan"] = random.choice(clans) if clan_choisi == "Aléatoire" else clan_choisi
            g["nom_famille"] = nom_famille.strip() or g["clan"]
            avantages = {
                "Uchiha": ("Sharingan", {"intelligence": 5, "force": 3}),
                "Senju": ("Affinité Mokuton", {"sante": 8, "force": 4}),
                "Uzumaki": ("Maîtrise des sceaux", {"chakra": 12, "sante": 5}),
                "Nara": ("Esprit stratégique", {"intelligence": 12}),
                "Hyûga": ("Byakugan", {"intelligence": 4, "force": 3}),
                "Akimichi": ("Expansion corporelle", {"force": 8, "sante": 4}),
                "Aburame": ("Symbiose avec les insectes", {"intelligence": 5}),
                "Inuzuka": ("Compagnon canin", {"force": 5, "sante": 3}),
                "Yamanaka": ("Techniques mentales", {"intelligence": 8}),
                "Sans clan": ("Aucun héritage de clan", {})}
            pouvoir, bonus = avantages[g["clan"]]
            g["jutsu"] = [pouvoir] if pouvoir != "Aucun héritage de clan" else []
            for stat, value in bonus.items():
                if stat in g["stats"]: g["stats"][stat] = clamp(g["stats"].get(stat, 50) + value)
            g["origine_familiale"] = f"le clan {g['clan']}" if g["clan"] != "Sans clan" else "une famille sans clan connu"
        else:
            g["clan"] = "Sans clan"
            g["nom_famille"] = nom_famille.strip()
            g["jutsu"] = []
        if g.get("saga_manga") == "onepiece":
            g["volonte_D"] = random.random() < 0.20
            if g["volonte_D"]:
                g.setdefault("secrets", []).append("Porteur·se de la Volonté du D.")
        else:
            g["volonte_D"] = False
    # Tout personnage possède un nom de famille affichable, même si le joueur laisse le champ vide.
    if not str(g.get("nom_famille", "")).strip():
        noms_famille = {
            "real": ["Martin", "Bernard", "Moreau", "Laurent", "Petit", "Lefèvre", "Roux"],
            "manga": (["D.", "Monkey D.", "Portgas D.", "Trafalgar D."] if g.get("saga_manga") == "onepiece" else ["Kurosawa", "Mori", "Sato", "Hayashi", "Takahashi"]),
            "fantasy": ["Valombre", "Aubéclat", "Drakefeu", "Boisargent", "Rochebrune", "Lunegrise"],
            "cyber": ["Kane", "Voss", "Kuroda", "Vale", "Cross"]
        }
        g["nom_famille"] = random.choice(noms_famille.get(univers, noms_famille["real"]))
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
    g["personnalite"] = {
        "curiosite": random.randint(30, 85), "discipline": random.randint(25, 80),
        "empathie": random.randint(30, 85), "impulsivite": random.randint(20, 75),
        "ambition": random.randint(25, 85)
    }
    g["monde_factions"] = initialiser_factions_monde(g)
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
        if g.get("saga_manga") == "onepiece" and g.get("volonte_D"):
            log(g, "🌑 SECRET DE NAISSANCE — Tu portes initialement l'énigmatique initiale D. Environ une naissance sur cinq révèle cette volonté ; ses conséquences restent inconnues.")
        if g.get("saga_manga") == "naruto":
            log(g, f"🍃 Nom de clan : {g.get('nom_famille') or g.get('clan', 'Sans clan')} · Héritage : {', '.join(g.get('jutsu', [])) or 'aucune capacité héréditaire connue'}.")
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
    g.setdefault("personnalite", {"curiosite": 50, "discipline": 50, "empathie": 50, "impulsivite": 50, "ambition": 50})
    g.setdefault("humeurs", [])
    g.setdefault("monde_factions", initialiser_factions_monde(g))
    g.setdefault("boss_historique", [])
    g.setdefault("objectifs_heritage", [])
    g.setdefault("objets_histoire", {})
    g.setdefault("traits_evolutifs", [])
    g.setdefault("derniere_maj_monde", -1)
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
    g["avatar"].setdefault("barbe", "Aucune")
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
    if key == "ninja" and g.get("saga_manga", "naruto") == "naruto":
        if g.get("age", 0) < 12:
            m.append("suivre le cursus de l'Académie ninja jusqu'à 12 ans")
        if g.get("examens_ninja_reussis", 0) < 1:
            m.append("réussir l'examen de fin d'Académie via un événement de parcours")
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


def generer_evenement_histoire_annuel(g):
    """Ajoute un jalon d'histoire aux âges importants et un événement narratif aléatoire."""
    age = int(g.get("age", 0))
    univ = g.get("univers", "real")
    saga = g.get("saga_manga", "naruto") if univ == "manga" else univ
    jalons = {
        1: ("Premiers liens", "Tes proches commencent à reconnaître tes habitudes et à créer des souvenirs avec toi."),
        3: ("Premières découvertes", "Tu explores ton environnement et développes tes premières préférences."),
        6: ("Nouvelle étape", "Une nouvelle routine commence et ton cercle social s'élargit."),
        10: ("Un talent se révèle", "Un adulte remarque une aptitude chez toi et t'encourage à la développer."),
        13: ("Changements", "Tu affirmes davantage ta personnalité et tes relations évoluent."),
        16: ("Vers l'indépendance", "Tu réfléchis à ton avenir et aux choix qui définiront la suite de ta vie."),
        18: ("Majorité", "De nouvelles responsabilités et possibilités s'ouvrent à toi."),
        25: ("Un nouveau chapitre", "Tes choix passés commencent à dessiner une direction plus nette pour ton avenir."),
        40: ("Faire le point", "Tu mesures le chemin parcouru et ce que tu souhaites transmettre."),
        60: ("Mémoire et héritage", "Les souvenirs de ta vie prennent une nouvelle valeur auprès de tes proches."),
    }
    if age in jalons:
        titre, texte = jalons[age]
        log(g, f"📖 {titre} — {texte}")
        g.setdefault("jalons_histoire", []).append({"age": age, "titre": titre, "texte": texte})
    evenements = {
        "real": [
            ("Rencontre inattendue", "Une personne croisée par hasard te donne un conseil que tu gardes en tête."),
            ("Occasion à saisir", "Une petite opportunité se présente : elle pourrait ouvrir une porte si tu t'en occupes."),
            ("Souvenir retrouvé", "Un objet ou une photo réveille un souvenir important de ton histoire familiale."),
            ("Coup de chance", "Une bonne nouvelle inattendue égaye ton année."),
            ("Contretemps", "Un imprévu bouleverse tes plans et t'oblige à revoir tes priorités."),
            ("Solidarité", "Un proche a besoin d'aide. Ta réaction pourrait renforcer ou fragiliser votre lien."),
            ("Rumeur locale", "Une histoire fait parler dans ton quartier, mais les faits restent incertains."),
        ],
        "naruto": [
            ("Mission de rang D", "Une mission apparemment simple révèle un détail étrange sur les environs."),
            ("Rivalité à l'entraînement", "Un autre shinobi te provoque pendant un exercice. Votre rivalité pourrait devenir une motivation."),
            ("Secret de clan", "Un membre de ta famille laisse échapper un indice sur une ancienne histoire du clan."),
            ("Patrouille à la frontière", "Des traces inhabituelles sont repérées près d'une frontière du village."),
            ("Tournoi annoncé", "Un tournoi local est évoqué. Les jeunes ninjas espèrent pouvoir montrer leurs progrès."),
            ("Rumeur sur un nukenin", "Un ninja déserteur aurait été aperçu non loin, sans confirmation officielle."),
        ],
        "jujutsu": [
            ("Résidu d'énergie occulte", "Une présence étrange est détectée près d'un lieu public, mais sa nature reste inconnue."),
            ("Exercice imprévu", "Un instructeur transforme un entraînement en simulation de crise."),
            ("Objet maudit", "Un objet ordinaire semble attirer une énergie occulte inhabituelle."),
            ("Rumeur de fléau", "Des témoins racontent une apparition, et les exorcistes cherchent à vérifier les faits."),
        ],
        "onepiece": [
            ("Carte mystérieuse", "Une carte incomplète circule dans un port et pourrait mener à une aventure."),
            ("Tempête en mer", "Une météo brutale force les équipages à choisir entre attendre et prendre un risque."),
            ("Prime affichée", "Une nouvelle affiche de prime attire l'attention et change l'ambiance du port."),
            ("Trésor disputé", "Plusieurs groupes cherchent le même trésor supposé sur une île voisine."),
            ("Navire inconnu", "Un navire sans pavillon est aperçu à l'horizon."),
        ],
        "fantasy": [
            ("Étrange lueur", "Une lumière magique apparaît près d'un ancien chemin au coucher du soleil."),
            ("Contrat de guilde", "Une guilde affiche une mission qui pourrait améliorer ta réputation."),
            ("Caravane attaquée", "Des voyageurs rapportent une attaque sur une route commerciale."),
            ("Présage ancien", "Un érudit découvre un signe qui pourrait annoncer un changement dans le royaume."),
            ("Créature aperçue", "Une créature rare aurait été vue près des bois, mais personne ne sait si elle est dangereuse."),
        ],
    }
    if random.random() < 0.68:
        titre, texte = random.choice(evenements.get(saga, evenements["real"]))
        log(g, f"🎲 {titre} — {texte}")
        g.setdefault("evenements_histoire", []).append({"age": age, "titre": titre, "texte": texte})
        g["evenements_histoire"] = g["evenements_histoire"][-100:]



def generer_evenement_quotidien(g):
    """Petit imprévu de vie courante annuel : effets modestes, journalisés, sans diagnostic médical."""
    age = int(g.get("age", 0))
    stats = g.setdefault("stats", {})
    univers = g.get("univers", "real")
    evenements = [
        ("💸 Une facture oubliée", "Une facture oubliée arrive avec des frais supplémentaires.", {"argent": -random.randint(80, 450), "bonheur": -2}),
        ("😮‍💨 Une période sans énergie", "Tu as du mal à te motiver et tu repousses plusieurs petites tâches. Tu prends le temps de souffler.", {"bonheur": -random.randint(2, 5)}),
        ("🌧️ Un passage à vide", "Tu traverses une période moralement difficile. En parler à un proche t'aide à ne pas tout garder pour toi.", {"bonheur": -random.randint(3, 7), "famille_relations": 1}),
        ("⚡ Un regain de motivation", "Un déclic te donne envie de reprendre un projet laissé de côté.", {"bonheur": random.randint(3, 7), "intelligence": 1}),
        ("🔎 Une curiosité inattendue", "Un sujet t'intrigue et tu passes du temps à apprendre quelque chose de nouveau.", {"intelligence": random.randint(1, 3), "bonheur": 2}),
        ("🗯️ Une embrouille familiale", "Une remarque est mal prise et une dispute éclate avec un membre de ta famille. Il faudra peut-être en reparler calmement.", {"famille_relations": -random.randint(3, 8), "bonheur": -2}),
        ("🤝 Une réconciliation", "Après un malentendu, vous prenez le temps de vous expliquer et la tension retombe.", {"famille_relations": random.randint(3, 7), "bonheur": 3}),
        ("🧺 Une semaine de flemme", "Tu remets quelques obligations au lendemain. Rien de dramatique, mais tu prends du retard.", {"bonheur": 1, "notes": -1}),
        ("🍀 Une petite chance", "Tu retrouves un billet ou reçois un petit remboursement que tu n'attendais plus.", {"argent": random.randint(20, 180), "bonheur": 2}),
        ("🧑‍🤝‍🧑 Un ami a besoin de toi", "Un ami traverse une mauvaise journée et vient te parler. Tu prends le temps de l'écouter.", {"bonheur": 2, "famille_relations": 1}),
        ("📦 Une dépense imprévue", "Un objet important casse et tu dois payer pour le réparer ou le remplacer.", {"argent": -random.randint(40, 300), "bonheur": -1}),
        ("🎯 Une nouvelle habitude", "Tu te mets à une petite routine qui te fait du bien et t'aide à te sentir plus organisé·e.", {"sante": 2, "bonheur": 2}),
        ("😳 Un moment gênant", "Tu vis un petit moment embarrassant. Sur le coup tu y repenses beaucoup, puis ça finit par passer.", {"bonheur": -2}),
        ("🧹 Un coup de rangement", "Tu ranges ton espace et retrouves un objet que tu croyais perdu.", {"bonheur": 2}),
    ]
    if age < 6:
        evenements = [
            ("🧸 Un jouet préféré", "Tu t'attaches à un jouet ou à un objet rassurant.", {"bonheur": 3}),
            ("😢 Un petit chagrin", "Une séparation ou un changement de routine te rend triste, puis un proche te réconforte.", {"bonheur": -2, "famille_relations": 2}),
            ("✨ Une grande curiosité", "Tu veux toucher, regarder et comprendre tout ce qui t'entoure.", {"intelligence": 2, "bonheur": 2}),
            ("🤗 Un moment tendre", "Un proche passe un moment calme avec toi et te rassure.", {"bonheur": 3, "famille_relations": 2}),
        ]
    elif age < 18:
        evenements += [
            ("📚 Un devoir oublié", "Tu réalises au dernier moment qu'un devoir ou une tâche devait être rendu.", {"notes": -random.randint(1, 4), "bonheur": -2}),
            ("👀 Une nouvelle passion", "Tu découvres une activité, un artiste ou un sujet qui occupe tes pensées pendant des semaines.", {"bonheur": 3, "intelligence": 1}),
            ("🙄 Un désaccord avec un adulte", "Tu as l'impression de ne pas être compris·e et la discussion se termine mal.", {"famille_relations": -3, "bonheur": -2}),
        ]
    elif age >= 18:
        evenements += [
            ("🧾 Un budget serré", "Plusieurs dépenses tombent au même moment. Tu dois revoir tes priorités pour finir le mois.", {"argent": -random.randint(100, 600), "bonheur": -2}),
            ("📨 Une opportunité inattendue", "Un contact te parle d'une possibilité intéressante pour tes projets ou ton travail.", {"bonheur": 3, "reputation": 1}),
            ("🛌 Besoin de repos", "Tu comprends que tu as besoin de ralentir et de te réserver un peu de temps.", {"sante": 2, "bonheur": 2}),
        ]
    if univers == "manga":
        evenements += [
            ("🍜 Un repas partagé", "Tu partages un repas simple avec des proches après une journée chargée.", {"bonheur": 3, "famille_relations": 2}),
            ("🥋 Entraînement repoussé", "Tu n'as pas la tête à t'entraîner aujourd'hui et tu reportes la séance.", {"bonheur": 1, "force": -1}),
        ]
        if g.get("saga_manga") == "onepiece":
            evenements.append(("⛵ Corvée sur le navire", "Une tâche de routine prend plus longtemps que prévu, mais l'équipage s'organise.", {"force": 1, "bonheur": -1}))
    elif univers == "fantasy":
        evenements += [
            ("🪙 Une taxe de guilde", "Une petite taxe ou cotisation imprévue réduit tes économies.", {"argent": -random.randint(10, 100), "bonheur": -1}),
            ("🍲 Une soirée à l'auberge", "Une conversation autour d'un repas te remonte le moral.", {"bonheur": 3, "famille_relations": 1}),
        ]
    titre, texte, effets = random.choice(evenements)
    for cle, valeur in effets.items():
        if cle == "argent":
            g["argent"] = int(g.get("argent", 0) + valeur)
        elif cle == "reputation":
            g["reputation"] = clamp(g.get("reputation", 50) + valeur)
        elif cle == "famille_relations":
            g["famille_relations"] = clamp(g.get("famille_relations", 60) + valeur)
        elif cle == "notes":
            g["notes"] = clamp(g.get("notes", 50) + valeur)
        elif cle in stats:
            stats[cle] = clamp(stats.get(cle, 50) + valeur)
    log(g, f"☀️ VIE QUOTIDIENNE — {titre} : {texte}")
    g.setdefault("evenements_quotidiens", []).append({"age": age, "titre": titre, "texte": texte, "effets": effets})
    g["evenements_quotidiens"] = g["evenements_quotidiens"][-120:]


def initialiser_factions_monde(g):
    """État simplifié des factions : évolue chaque année, même sans intervention du joueur."""
    univers = g.get("univers", "real")
    if univers == "manga":
        saga = g.get("saga_manga", "naruto")
        noms = {"naruto": ["Village", "Clans", "Akatsuki"], "jujutsu": ["Écoles d’exorcisme", "Conseil occulte", "Fléaux"], "onepiece": ["Gouvernement mondial", "Pirates", "Révolutionnaires"]}.get(saga, ["Village", "Clans", "Akatsuki"])
    elif univers == "fantasy":
        noms = ["Couronne", "Guildes", "Ordre ancien"]
    else:
        noms = ["Gouvernement", "Économie", "Mouvements citoyens"]
    return {n: random.randint(35, 70) for n in noms}


def faire_evoluer_personnalite(g):
    """Les habitudes et décisions modifient progressivement les traits, sans verrouiller le personnage."""
    p = g.setdefault("personnalite", {"curiosite": 50, "discipline": 50, "empathie": 50, "impulsivite": 50, "ambition": 50})
    for k in ("curiosite", "discipline", "empathie", "impulsivite", "ambition"):
        p.setdefault(k, 50)
    historique = " ".join(str(x[1]).lower() for x in g.get("journal", [])[-18:] if isinstance(x, (list, tuple)) and len(x) > 1)
    tendances = {
        "curiosite": (("curieux", "découvre", "explore", "apprends", "secret"), ("routine", "ignore")),
        "discipline": (("entraînement", "étudie", "mission réussie", "travaille", "réussis"), ("flemme", "abandonne", "sèche")),
        "empathie": (("aides", "bénévolat", "excuses", "réconcil", "protège"), ("trahis", "dépouilles", "kidnapp", "humilie")),
        "impulsivite": (("impulsif", "dispute", "assaut direct", "braquage", "colère"), ("méditation", "négocie", "patience")),
        "ambition": (("promotion", "boss", "victoire", "objectif", "réputation"), ("démission", "renonce")),
    }
    for k, (plus, moins) in tendances.items():
        delta = sum(1 for word in plus if word in historique) - sum(1 for word in moins if word in historique)
        if delta:
            p[k] = clamp(int(p[k]) + max(-3, min(3, delta)))
    g["traits_evolutifs"] = [label for key, label in [("curiosite", "Curieux·se"), ("discipline", "Discipliné·e"), ("empathie", "Empathique"), ("impulsivite", "Impulsif·ve"), ("ambition", "Ambitieux·se")] if p.get(key, 50) >= 72]


def traiter_consequences_differees(g):
    """Rappels scénarisés après plusieurs années, avec une issue liée au choix d'origine."""
    reste = []
    for c in g.get("consequences_differees", []):
        if c.get("due_age", g.get("age", 0) + 1) <= g.get("age", 0):
            kind = c.get("type", "souvenir")
            if kind == "rivalite":
                nom = c.get("nom", "un ancien rival")
                g.setdefault("rivalites", []).append({"nom": nom, "niveau": 2, "origine": c.get("origine", "un ancien conflit")})
                log(g, f"⚡ RETOUR DU PASSÉ — {nom} réapparaît : une vieille dispute refait surface. Tu peux chercher l'apaisement ou raviver la rivalité lors d'un prochain événement.")
            elif kind == "dette":
                montant = min(max(0, int(c.get("montant", 500))), max(0, int(g.get("argent", 0))))
                g["argent"] -= montant
                log(g, f"💸 CONSÉQUENCE — Une ancienne dette revient te hanter : tu rembourses {fm(g, montant)}.")
            elif kind == "heritage_boss":
                g.setdefault("objectifs_heritage", []).append({"nom": c.get("nom", "Vaincre l'ennemi familial"), "origine": c.get("origine", "Échec d'une génération"), "termine": False})
                log(g, f"🧬 HÉRITAGE — {c.get('origine', 'Un échec familial')} devient un objectif pour cette génération : {c.get('nom', 'prouver sa valeur')}.")
            else:
                log(g, f"⌛ Le temps révèle les conséquences de : {c.get('texte', 'un choix passé')}.")
        else:
            reste.append(c)
    g["consequences_differees"] = reste


def faire_evoluer_monde(g):
    """Fait bouger les factions une fois par âge et produit parfois une actualité contextualisée."""
    if g.get("derniere_maj_monde") == g.get("age"):
        return
    factions = g.setdefault("monde_factions", {})
    if not factions:
        factions.update(initialiser_factions_monde(g))
    changements = []
    for nom in list(factions):
        ancien = int(factions[nom])
        nouveau = clamp(ancien + random.choice([-8, -5, -2, 0, 2, 5, 8]))
        factions[nom] = nouveau
        if abs(nouveau - ancien) >= 6:
            changements.append((nom, ancien, nouveau))
    g["derniere_maj_monde"] = g.get("age", 0)
    if changements and random.random() < 0.72:
        nom, ancien, nouveau = random.choice(changements)
        direction = "gagne de l'influence" if nouveau > ancien else "perd de l'influence"
        texte = f"{nom} {direction} dans les affaires du monde ({nouveau}/100)."
        g.setdefault("actualites_monde", []).append({"age": g.get("age", 0), "type": "information", "titre": "Équilibre des pouvoirs", "texte": texte})
        log(g, "🌍 MONDE EN MOUVEMENT — " + texte)


def verifier_objets_herites(g):
    """Les objets importants gardent une provenance narrative et peuvent traverser les générations."""
    lore = g.setdefault("objets_histoire", {})
    for item in g.get("inventaire_objets", []):
        nom = item.get("nom", item.get("id", "Objet inconnu"))
        if nom not in lore:
            lore[nom] = {"origine": "Acquis au cours de cette vie", "generation": g.get("generation", 1), "age": g.get("age", 0)}


def passer_annee(g):
    if not g["vivant"]:
        return
    S, V = g["stats"], ville_info(g)
    g["age"] += 1
    a = g["age"]
    g["actions"] = ACTIONS_PAR_AN
    log(g, f"🎂 Tu as {a} ans.")
    generer_evenement_histoire_annuel(g)
    # Un petit événement banal par année, en complément des événements propres à l’univers.
    if random.random() < 0.88:
        generer_evenement_quotidien(g)
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
    traiter_consequences_differees(g)
    faire_evoluer_monde(g)
    faire_evoluer_personnalite(g)
    verifier_objets_herites(g)
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
    if g["vivant"] and random.random() < 0.78:
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



# --- Banque d'événements de parcours : les choix influencent les compétences,
# les relations et les étapes de progression. Les probabilités sont réévaluées
# à chaque tirage pour éviter que la même histoire revienne trop souvent.
def ev_parcours(g, kind, choice):
    if kind == "naruto_examen":
        if choice == "technique":
            score = g.get("chakra", 0) + random.randint(-8, 18)
            if score >= 25:
                g["examens_ninja_reussis"] = g.get("examens_ninja_reussis", 0) + 1
                g["metier"] = None
                g["progression_grade"] = max(1, g.get("progression_grade", 0))
                return res(g, "🎓 Tu réussis l'examen pratique ! L'Académie te reconnaît comme Genin. Le parcours ninja remplace une candidature classique.", karma=5, bonheur=8, intelligence=4, celebrite=2)
            return res(g, "💨 Ta technique échoue devant les examinateurs. Tu devras t'entraîner avant une nouvelle tentative.", bonheur=-3, intelligence=2)
        if choice == "clone":
            if g.get("chakra", 0) + random.randint(-5, 12) >= 20:
                g["examens_ninja_reussis"] = g.get("examens_ninja_reussis", 0) + 1
                g["progression_grade"] = max(1, g.get("progression_grade", 0))
                return res(g, "🍃 Tes clones tiennent suffisamment longtemps : examen validé, te voilà Genin !", karma=4, bonheur=7, intelligence=3)
            return res(g, "Les clones se dissipent trop vite. L'examen est raté, mais tu comprends quoi travailler.", bonheur=-2, intelligence=3)
        return res(g, "Tu aides un camarade paniqué. L'examinateur remarque ton sang-froid; tu gagnes du respect, mais l'examen reste à repasser.", karma=8, relations=4, bonheur=3)
    if kind == "onepiece_recrutement":
        if choice == "rejoindre":
            g["faction_manga"] = random.choice(["Équipage indépendant", "Alliance pirate", "Équipage d'exploration"])
            return res(g, f"🏴‍☠️ Tu rejoins {g['faction_manga']}. Un nouveau parcours s'ouvre à toi.", celebrite=4, karma=-1, bonheur=8)
        if choice == "test":
            return res(g, "Tu demandes une épreuve avant de t'engager. Le capitaine te confie une petite mission de confiance.", intelligence=3, karma=2, bonheur=2)
        return res(g, "Tu refuses poliment et gardes ton indépendance. Une autre occasion pourra se présenter.", bonheur=2, intelligence=1)
    if kind == "jjk_recrutement":
        if choice == "accepter":
            g["faction_manga"] = "École d'exorcisme"
            g["energie_occulte"] = g.get("energie_occulte", 0) + 8
            return res(g, "🏯 Tu acceptes d'intégrer l'école d'exorcisme. Ta formation commence officiellement.", bonheur=5, intelligence=3, celebrite=2)
        if choice == "observer":
            g["energie_occulte"] = g.get("energie_occulte", 0) + 4
            return res(g, "Tu observes les exorcistes à distance et apprends à ressentir l'énergie occulte.", intelligence=4, bonheur=1)
        return res(g, "Tu refuses pour l'instant. Le phénomène reste mystérieux, mais tu pourras y revenir.", bonheur=1)
    if kind == "entrainement":
        if choice == "intense":
            return res(g, "💪 L'entraînement est éprouvant mais utile.", sante=-3, force=5, bonheur=2, intelligence=1)
        if choice == "equipe":
            return res(g, "🤝 L'entraînement en équipe améliore ta coordination et tes liens.", force=2, relations=6, bonheur=4)
        return res(g, "Tu privilégies la récupération et évites la blessure.", sante=3, energie=6, bonheur=2)
    if kind == "opportunite":
        if choice == "accepter":
            return res(g, "🌟 Tu saisis l'occasion et gagnes en visibilité. Une conséquence pourra arriver plus tard.", celebrite=5, reputation=3, bonheur=4)
        if choice == "preparer":
            return res(g, "Tu te prépares avant de te lancer : moins spectaculaire, mais plus sûr.", intelligence=4, reputation=2)
        return res(g, "Tu passes ton tour. Tu préserves ton énergie et restes libre de choisir la suite.", energie=5, bonheur=1)
    return res(g, "Tu prends une décision qui influencera la suite de ton histoire.", bonheur=1)

event("parcours_naruto_examen_academie", "L'examen de fin d'Académie", "🍃 C'est le jour de l'examen ! Les élèves doivent prouver leur maîtrise des bases. Une réussite débloque le rang de Genin; une tentative ratée demandera davantage d'entraînement.", lambda g: g.get("univers") == "manga" and g.get("saga_manga", "naruto") == "naruto" and 6 <= g.get("age", 0) <= 17 and g.get("examens_ninja_reussis", 0) == 0 and g.get("chakra", 0) >= 8 and random.random() < .28, [("Démontrer une technique", lambda g: ev_parcours(g,"naruto_examen","technique")), ("Tenter le clonage", lambda g: ev_parcours(g,"naruto_examen","clone")), ("Aider un camarade", lambda g: ev_parcours(g,"naruto_examen","aide"))])
event("parcours_onepiece_recrutement", "Une invitation à rejoindre un équipage", "🏴‍☠️ Un équipage cherche de nouveaux membres. Le capitaine veut connaître tes motivations avant de t'embarquer dans ses aventures.", lambda g: g.get("univers") == "manga" and g.get("saga_manga") == "onepiece" and g.get("age", 0) >= 12 and g.get("faction_manga") in (None, "", "Indépendant·e") and random.random() < .22, [("Rejoindre l'équipage", lambda g: ev_parcours(g,"onepiece_recrutement","rejoindre")), ("Demander une épreuve", lambda g: ev_parcours(g,"onepiece_recrutement","test")), ("Rester indépendant", lambda g: ev_parcours(g,"onepiece_recrutement","refuser"))])
event("parcours_jjk_recrutement", "Un exorciste a remarqué ton potentiel", "👁️ Après un incident étrange, un exorciste te propose de découvrir le monde occulte. Tu peux accepter, observer ou refuser.", lambda g: g.get("univers") == "manga" and g.get("saga_manga") == "jujutsu" and g.get("age", 0) >= 12 and g.get("faction_manga") != "École d'exorcisme" and random.random() < .2, [("Accepter la formation", lambda g: ev_parcours(g,"jjk_recrutement","accepter")), ("Observer d'abord", lambda g: ev_parcours(g,"jjk_recrutement","observer")), ("Refuser", lambda g: ev_parcours(g,"jjk_recrutement","refuser"))])
event("aleatoire_entrainement", "Une occasion de s'entraîner", "🥋 Un professeur, un ami ou un rival te propose un entraînement imprévu. Comment réagis-tu ?", lambda g: g.get("age", 0) >= 7 and random.random() < .2, [("M'entraîner intensément", lambda g: ev_parcours(g,"entrainement","intense")), ("M'entraîner en équipe", lambda g: ev_parcours(g,"entrainement","equipe")), ("Récupérer", lambda g: ev_parcours(g,"entrainement","repos"))])
event("aleatoire_opportunite_notoriete", "Une occasion de te faire connaître", "✨ Une occasion inattendue se présente : participer à une démonstration, aider lors d'un événement ou apparaître dans les médias. Cela pourrait augmenter ta notoriété.", lambda g: g.get("age", 0) >= 10 and random.random() < .18, [("Saisir l'occasion", lambda g: ev_parcours(g,"opportunite","accepter")), ("Me préparer", lambda g: ev_parcours(g,"opportunite","preparer")), ("Passer mon tour", lambda g: ev_parcours(g,"opportunite","refuser"))])
event("aleatoire_rival_defi", "Un rival te lance un défi", "⚡ Un rival te provoque devant plusieurs personnes. Tu peux accepter le défi, répondre avec stratégie ou désamorcer la situation.", lambda g: g.get("age", 0) >= 8 and random.random() < .16, [("Accepter le défi", lambda g: res(g, "Tu relèves le défi. Tu progresses, même si le résultat reste incertain.", force=4, celebrite=2, bonheur=2, sante=-2)), ("Répondre avec stratégie", lambda g: res(g, "Tu retournes la situation avec calme et intelligence.", intelligence=4, reputation=3)), ("Désamorcer", lambda g: res(g, "Tu refuses l'escalade et gagnes le respect de certaines personnes.", karma=4, relations=3, bonheur=2))])
event("aleatoire_coup_de_chance", "Un coup de chance", "🍀 Une rencontre ou un petit événement te donne une chance inattendue. À toi de décider comment en profiter.", lambda g: g.get("age", 0) >= 5 and random.random() < .14, [("Tenter ma chance", lambda g: res(g, "La chance te sourit !", argent=random.randint(80, 650), bonheur=5, reputation=1)), ("Partager avec quelqu'un", lambda g: res(g, "Tu partages ce que tu as reçu et renforces un lien.", argent=120, relations=5, karma=4)), ("Garder la tête froide", lambda g: res(g, "Tu transformes cette opportunité en apprentissage.", intelligence=3, bonheur=2))])

# ----------------------------------------------------------------------
# COUCHES D'ÉVÉNEMENTS DYNAMIQUES : saisons, relations, économie, carrière,
# réputation, conséquences différées et crises propres aux univers.
# Les conditions sont évaluées au moment du tirage : pas de scripts figés.
# ----------------------------------------------------------------------
def _evt_once(g, key):
    return key not in g.setdefault("evenements_vus", [])

def _evt_mark(g, key):
    g.setdefault("evenements_vus", []).append(key)

event("dynamique_soutien_ami", "Un proche a besoin de toi", "🤝 Un proche traverse une période compliquée et te demande du soutien. Ta réponse peut renforcer votre lien ou te coûter de l'énergie.", lambda g: g.get("age", 0) >= 8 and bool(g.get("amis") or g.get("partenaire") or g.get("enfants")) and random.random() < .25, [
    ("Prendre du temps pour lui/elle", lambda g: res(g, "Tu prends le temps d'écouter. Votre lien se renforce, même si tu es fatigué.", relations=8, bonheur=3, energie=-5)),
    ("Aider à trouver une solution", lambda g: res(g, "Vous trouvez ensemble une piste concrète.", intelligence=3, relations=5, reputation=1)),
    ("Dire que tu ne peux pas maintenant", lambda g: res(g, "Tu poses une limite honnête. La personne est un peu déçue, mais tu préserves ton énergie.", energie=3, bonheur=1))])

event("dynamique_rumeur", "Une rumeur circule", "🗣️ Une rumeur à ton sujet circule dans ton entourage ou ton milieu. Tu peux répondre, vérifier la source ou laisser retomber.", lambda g: g.get("age", 0) >= 12 and random.random() < .22, [
    ("Répondre publiquement", lambda g: res(g, "Tu clarifies les faits. Certaines personnes te soutiennent, d'autres restent sceptiques.", reputation=3, celebrite=2, bonheur=-2)),
    ("Chercher la source", lambda g: res(g, "Tu remontes à l'origine de la rumeur sans envenimer la situation.", intelligence=4, relations=2)),
    ("Ignorer", lambda g: res(g, "La rumeur finit par perdre de l'importance.", energie=2, bonheur=1))])

event("dynamique_opportunite_carriere", "Une opportunité inattendue", "📨 Une personne te propose une occasion liée à tes compétences. Ce n'est pas une garantie de réussite, mais cela peut ouvrir une porte.", lambda g: g.get("age", 16) >= 16 and not g.get("retraite") and random.random() < .24, [
    ("Accepter le défi", lambda g: res(g, "Tu tentes ta chance et apprends beaucoup de cette expérience.", intelligence=3, reputation=4, celebrite=2, bonheur=3)),
    ("Négocier les conditions", lambda g: res(g, "Tu clarifies les attentes avant de t'engager.", intelligence=3, argent=120, reputation=2)),
    ("Refuser pour l'instant", lambda g: res(g, "Tu préfères attendre une occasion plus adaptée.", bonheur=2, energie=3))])

event("dynamique_depense_imprevue", "Une dépense imprévue", "🧾 Une facture ou une réparation arrive au mauvais moment. Tu dois décider comment gérer ton budget.", lambda g: g.get("age", 18) >= 18 and not g.get("prison", 0) and random.random() < .27, [
    ("Payer immédiatement", lambda g: res(g, "Tu règles le problème avant qu'il ne s'aggrave.", argent=-min(max(g.get("argent", 0), 0), 450), bonheur=-1)),
    ("Comparer les solutions", lambda g: res(g, "Tu trouves une solution moins coûteuse en prenant le temps de comparer.", intelligence=2, argent=-min(max(g.get("argent", 0), 0), 180))),
    ("Demander un délai", lambda g: res(g, "Tu obtiens un peu de temps pour organiser tes finances.", reputation=1, bonheur=-1))])

event("dynamique_occasion_reseau", "Une rencontre utile", "🌐 Lors d'une sortie ou d'une mission, tu rencontres quelqu'un qui pourrait t'aider plus tard.", lambda g: g.get("age", 14) >= 14 and random.random() < .23, [
    ("Garder contact", lambda g: res(g, "Vous échangez vos coordonnées. Une nouvelle relation pourrait compter à l'avenir.", relations=5, reputation=2)),
    ("Proposer ton aide", lambda g: res(g, "Tu rends service et la personne se souviendra de toi.", relations=4, karma=3)),
    ("Rester prudent", lambda g: res(g, "Tu restes cordial sans trop t'engager.", intelligence=1, bonheur=1))])

event("dynamique_epuisement", "Tu tires trop sur la corde", "🌧️ Plusieurs obligations se sont accumulées. Tu sens que ton énergie baisse et qu'il faut choisir tes priorités.", lambda g: g.get("age", 7) >= 7 and g.get("stats", {}).get("energie", 50) < 45 and random.random() < .45, [
    ("Prendre une vraie pause", lambda g: res(g, "Tu lèves le pied et récupères progressivement.", energie=14, sante=3, bonheur=3)),
    ("Finir une seule priorité", lambda g: res(g, "Tu avances sur l'essentiel sans tout porter à la fois.", intelligence=2, energie=5, reputation=1)),
    ("Continuer malgré tout", lambda g: res(g, "Tu termines ce que tu peux, mais la fatigue se fait sentir.", energie=-6, sante=-2, bonheur=-3))])

event("dynamique_reparation_reputation", "L'occasion de réparer une erreur", "🧭 Tu repenses à une décision passée qui a blessé quelqu'un ou terni ton image. Une occasion de réparer les choses se présente.", lambda g: g.get("age", 12) >= 12 and (g.get("karma", 50) < 45 or g.get("reputation", 50) < 45) and random.random() < .32, [
    ("Présenter des excuses", lambda g: res(g, "Tu reconnais ta part de responsabilité. Tout n'est pas effacé, mais un premier pas est fait.", karma=7, relations=3, reputation=3)),
    ("Réparer concrètement", lambda g: res(g, "Tu poses un acte concret pour corriger les conséquences.", karma=5, reputation=5, argent=-min(max(g.get("argent", 0), 0), 100))),
    ("Laisser le temps faire", lambda g: res(g, "Tu ne forces pas les choses. La confiance devra se reconstruire plus lentement.", bonheur=1))])

event("dynamique_concours", "Un concours ou tournoi local", "🏅 Un concours est organisé. Il peut tester tes compétences, ton sang-froid et ta capacité à gérer la pression.", lambda g: g.get("age", 8) >= 8 and random.random() < .2, [
    ("Participer sérieusement", lambda g: res(g, "Tu donnes le meilleur de toi-même et progresses grâce à l'expérience.", intelligence=3, force=2, celebrite=3, bonheur=3)),
    ("Y aller pour le plaisir", lambda g: res(g, "Tu profites de l'expérience sans te mettre trop de pression.", bonheur=5, relations=2)),
    ("Encourager quelqu'un", lambda g: res(g, "Tu soutiens un autre participant et gagnes son estime.", relations=4, karma=3))])

event("dynamique_monde_crise", "Une crise bouleverse la région", "🚨 Une crise touche la région : pénurie, tensions ou incident majeur. Même si tu n'es pas directement visé, tes choix peuvent compter.", lambda g: g.get("age", 10) >= 10 and random.random() < .12, [
    ("Aider les personnes touchées", lambda g: res(g, "Tu participes à l'entraide locale. Ton geste est apprécié.", karma=6, relations=3, energie=-5, reputation=3)),
    ("Protéger tes proches", lambda g: res(g, "Tu vérifies que tes proches sont en sécurité et organises le nécessaire.", relations=5, bonheur=2, energie=-2)),
    ("Suivre les informations", lambda g: res(g, "Tu te renseignes avant d'agir et évites de propager des rumeurs.", intelligence=3, reputation=1))])

event("dynamique_manga_rivalite", "Un rival veut te dépasser", "⚔️ Un rival s'entraîne pour te dépasser et te propose un défi. Votre relation dépendra de ta réaction.", lambda g: g.get("univers") == "manga" and g.get("age", 8) >= 8 and random.random() < .28, [
    ("Accepter un entraînement", lambda g: res(g, "Le duel d'entraînement est intense. Vous progressez tous les deux.", force=4, intelligence=2, relations=2, energie=-4)),
    ("Étudier sa technique", lambda g: res(g, "Tu observes ses habitudes et identifies une piste de progression.", intelligence=5, chakra=2)),
    ("Proposer une alliance", lambda g: res(g, "Votre rivalité devient plus saine et vous apprenez à coopérer.", relations=5, karma=3, bonheur=2))])

event("dynamique_naruto_mission_equipe", "Mission d'équipe imprévue", "🍃 Ton équipe reçoit une mission qui semble simple, mais un imprévu met votre coordination à l'épreuve.", lambda g: g.get("univers") == "manga" and g.get("saga_manga", "naruto") == "naruto" and g.get("age", 12) >= 12 and g.get("examens_ninja_reussis", 0) > 0 and random.random() < .3, [
    ("Prendre les devants", lambda g: res(g, "Tu coordonnes l'équipe et assume la responsabilité de la décision.", intelligence=3, reputation=4, chakra=-3, relations=2)),
    ("Protéger ton coéquipier", lambda g: res(g, "Tu privilégies la sécurité de l'équipe. Votre confiance mutuelle grandit.", relations=6, karma=4, sante=-1)),
    ("Analyser avant d'agir", lambda g: res(g, "Ton analyse permet d'éviter une erreur et de terminer la mission proprement.", intelligence=4, chakra=2, reputation=2))])

event("dynamique_onepiece_butin", "Un butin inattendu", "🏴‍☠️ Après une escale, une piste mène à une caisse abandonnée. Elle peut contenir quelque chose d'utile… ou attirer des ennuis.", lambda g: g.get("univers") == "manga" and g.get("saga_manga") == "onepiece" and g.get("age", 12) >= 12 and random.random() < .24, [
    ("Inspecter prudemment", lambda g: res(g, "Tu fouilles avec méthode et récupères une petite récompense.", argent=random.randint(100, 700), intelligence=2)),
    ("Partager avec l'équipage", lambda g: res(g, "Le partage renforce la confiance à bord.", argent=100, relations=5, reputation=2)),
    ("Laisser la caisse", lambda g: res(g, "Tu évites un risque inutile et poursuis la route.", karma=2, bonheur=1))])

event("dynamique_jjk_energie", "Une anomalie d'énergie occulte", "👁️ Une anomalie d'énergie occulte apparaît à proximité. Elle semble faible, mais sa nature est inconnue.", lambda g: g.get("univers") == "manga" and g.get("saga_manga") == "jujutsu" and g.get("age", 12) >= 12 and random.random() < .25, [
    ("Observer à distance", lambda g: res(g, "Tu analyses les traces sans t'exposer inutilement.", intelligence=4, energie_occulte=3)),
    ("Prévenir un exorciste", lambda g: res(g, "Un professionnel prend le relais. Tu as fait preuve de prudence.", karma=4, reputation=2)),
    ("Intervenir", lambda g: res(g, "Tu interviens avec courage, mais l'effort est éprouvant.", energie_occulte=5, sante=-3, celebrite=3))])

event("dynamique_fantasy_ruines", "Des ruines viennent d'être découvertes", "🗺️ Des voyageurs parlent de ruines récemment révélées après un glissement de terrain. Une expédition se prépare.", lambda g: g.get("univers") == "fantasy" and g.get("age", 10) >= 10 and random.random() < .24, [
    ("Explorer avec prudence", lambda g: res(g, "Tu découvres des inscriptions et un objet de valeur modeste.", intelligence=4, argent=250, reputation=2)),
    ("Partir avec un groupe", lambda g: res(g, "Le groupe partage les découvertes et couvre les risques.", relations=4, argent=120, bonheur=3)),
    ("Noter l'emplacement", lambda g: res(g, "Tu gardes la piste pour une expédition mieux préparée.", intelligence=2, bonheur=1))])

event("dynamique_anniversaire", "Un anniversaire marquant", "🎂 Un anniversaire devient l'occasion de faire le point sur tes choix et les personnes qui comptent pour toi.", lambda g: g.get("age", 0) >= 10 and g.get("age", 0) % 5 == 0 and random.random() < .7, [
    ("Réunir les proches", lambda g: res(g, "Tu célèbres avec les personnes importantes de ta vie.", bonheur=7, relations=4, argent=-min(max(g.get("argent", 0), 0), 120))),
    ("Faire le bilan", lambda g: res(g, "Tu définis un objectif réaliste pour la suite.", intelligence=3, bonheur=3, reputation=1)),
    ("T'offrir quelque chose", lambda g: res(g, "Tu t'accordes un petit plaisir.", bonheur=5, argent=-min(max(g.get("argent", 0), 0), 180)) )])

EVENTS_BY_ID = {e["id"]: e for e in EVENTS}


def tirer_evenement(g):
    eligibles = [e for e in EVENTS if e["cond"](g)]
    if not eligibles:
        return
    # Algorithme anti-répétition : les événements vus récemment sont moins
    # probables, tandis que les nouveautés et les parcours propres à l'univers
    # sont favorisés. Le tirage reste pondéré et non déterministe.
    historique = g.setdefault("evenements_vus", [])
    recents = set(historique[-5:])
    saga = g.get("saga_manga", "naruto")
    def poids_evenement(ev):
        eid = ev["id"]
        poids = 1.0
        if eid in recents:
            poids *= 0.12
        elif eid not in historique:
            poids *= 1.65
        if eid.startswith("parcours_"):
            poids *= 2.0
        if g.get("univers") == "manga":
            if saga == "naruto" and (eid.startswith("naruto_") or eid.startswith("parcours_naruto")): poids *= 1.8
            elif saga == "onepiece" and (eid.startswith("onepiece_") or eid.startswith("parcours_onepiece")): poids *= 1.8
            elif saga == "jujutsu" and (eid.startswith("jjk_") or eid.startswith("parcours_jjk")): poids *= 1.8
        if eid.startswith("aleatoire_") or eid.startswith("dynamique_"):
            poids *= 1.35
        # Diversification par couche : privilégier les systèmes peu représentés
        # dans l'historique récent, sans supprimer les événements rares.
        couches = {
            "relations": ("dynamique_soutien_ami", "dynamique_rumeur", "dynamique_occasion_reseau"),
            "economie": ("dynamique_depense_imprevue", "dynamique_opportunite_carriere", "dynamique_butin"),
            "monde": ("dynamique_monde_crise", "dynamique_fantasy_ruines"),
            "progression": ("parcours_", "dynamique_naruto_", "dynamique_jjk_", "dynamique_manga_"),
            "bien_etre": ("dynamique_epuisement", "dynamique_anniversaire", "dynamique_concours")
        }
        couche = next((nom for nom, prefixes in couches.items() if any(eid.startswith(pref) for pref in prefixes)), None)
        if couche:
            vus_couche = sum(1 for ancien in historique[-12:] if any(ancien.startswith(pref) for pref in couches[couche]))
            poids *= max(0.45, 1.25 - vus_couche * 0.16)
        return poids
    # On conserve les événements urgents, mais on évite de répéter un même
    # événement si d'autres possibilités valides existent.
    if len(eligibles) > 1:
        non_recents = [e for e in eligibles if e["id"] not in recents]
        if non_recents:
            eligibles = non_recents + [e for e in eligibles if e["id"] in recents and e["id"] in WORLD_EVENT_IDS]
    urgents = [e for e in eligibles if e["id"] in ("ami_revanche", "bijuu_voix", "sharingan_vole", "akatsuki_recrutement", "recrutement_agence_heroique", "famille_sortie", "parent_colere", "dispute_fratrie", "sortie_amis", "onepiece_faction_choice", "onepiece_fruit_demon", "jjk_eveil_occult",
        "monde_guerre", "monde_paix", "monde_devise", "monde_independance", "monde_attentat", "monde_gang", "monde_arrestations", "monde_president",
        "naruto_hokage_mort", "naruto_akatsuki_war", "naruto_kazekage_manipule", "naruto_peace_treaty",
        "jjk_fléau_majeur", "jjk_crise_ecole", "onepiece_offensive_marine", "onepiece_independence",
        "fantasy_guerre", "fantasy_paix", "fantasy_dragon_capitale", "fantasy_nouvelle_monnaie")]
    metiers = [e for e in eligibles if e["id"].startswith("metier_")]
    manga = [e for e in eligibles if e["id"] in ("bijuu_naissance", "bijuu_scellage", "heritage_clan", "mission_ninja_rare", "bijuu_voix", "sharingan_vole", "akatsuki_recrutement") or e["id"].startswith(("jjk_", "onepiece_", "naruto_"))]
    autres = [e for e in eligibles if e not in metiers and e not in urgents and e not in manga]
    # Priorité aux conséquences déjà annoncées, puis au contenu propre à l'univers et au métier.
    if urgents and random.random() < .58:
        e = random.choices(urgents, weights=[poids_evenement(x) for x in urgents], k=1)[0]
    elif g.get("univers") == "manga" and manga and random.random() < .68:
        saga = g.get("saga_manga", "naruto")
        saga_events = [x for x in manga if (saga == "jujutsu" and x["id"].startswith("jjk_")) or (saga == "onepiece" and x["id"].startswith("onepiece_")) or (saga == "naruto" and (x["id"].startswith("naruto_") or x["id"] in ("bijuu_naissance", "bijuu_scellage", "heritage_clan", "mission_ninja_rare", "bijuu_voix", "sharingan_vole", "akatsuki_recrutement")))]
        pool = saga_events or (manga if saga == "naruto" else (autres or eligibles))
        e = random.choices(pool, weights=[poids_evenement(x) for x in pool], k=1)[0]
    elif metiers and random.random() < .58:
        e = random.choices(metiers, weights=[poids_evenement(x) for x in metiers], k=1)[0]
    else:
        pool = autres or eligibles
        e = random.choices(pool, weights=[poids_evenement(x) for x in pool], k=1)[0]
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



@action("sceller_cible")
def a_sceller_cible(g):
    if g.get("univers") != "manga" or g.get("saga_manga") != "jujutsu":
        raise Refus("Cette technique est réservée à l'univers Jujutsu Kaisen.")
    if g.get("age", 0) < 12:
        raise Refus("Il faut avoir au moins 12 ans pour tenter un scellement complexe.")
    energie = g.get("energie_occulte", 0)
    if energie < 25:
        raise Refus("Il te faut au moins 25 points d'énergie occulte.")
    g["energie_occulte"] = max(0, energie - 25)
    cible = random.choice(["un fléau de grade inférieur", "un objet maudit instable", "un adversaire affaibli"])
    chance = min(.88, .42 + g.get("stats", {}).get("intelligence", 50) / 250 + g.get("maitrise_occulte", 0) / 250)
    if random.random() < chance:
        g.setdefault("personnes_scellees", []).append({"cible": cible, "age": g["age"]})
        log(g, f"🔒 Scellement réussi : {cible} est enfermé dans un sceau à l'âge de {g['age']} ans.")
        chg(g, intelligence=2, bonheur=2, celebrite=2)
        return f"🔒 Tu as scellé {cible}. Énergie occulte -25."
    chg(g, sante=-8, bonheur=-4)
    return f"⚠️ Le sceau se brise en tentant de capturer {cible}. Tu perds 25 points d'énergie occulte et subis un contrecoup."

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
    g.setdefault("objets_histoire", {}).setdefault(article["nom"], {"origine": "Acheté au marché", "generation": g.get("generation", 1), "age": g.get("age", 0)})
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
                   objectifs_heritage=[dict(x) for x in parent.get("objectifs_heritage", []) if not x.get("termine")],
                   objets_histoire=dict(parent.get("objets_histoire", {})),
                   boss_historique=[dict(x) for x in parent.get("boss_historique", [])],
                   personnalite={k: clamp(int(v)+random.randint(-8,8)) for k,v in parent.get("personnalite", {}).items()},
                   boss_victoires=parent.get("boss_victoires", 0), boss_echecs=parent.get("boss_echecs", 0),
                   parents=[{"nom": parent.get("nom", "Parent"), "role": "Parent", "age": parent.get("age", 0),
                             "relation": lien, "vivant": False, "personnalite": "Héritage familial", "confiance": lien}])
    nouveau["journal"] = parent.get("journal", [])[:] + [[enfant.get("age", 0), f"🧬 Génération {nouveau['generation']} : {nouveau['nom']} reprend le flambeau de {parent['nom']}. Lien parent-enfant : {lien}/100. Héritage : {fm(nouveau, nouveau['argent'])}."]]
    if nouveau.get("frustration_heritage", 0):
        nouveau["journal"].append([nouveau["age"], f"💢 Héritage émotionnel : un échec face à un boss hante encore la famille ({nouveau['frustration_heritage']} souvenir(s)). Tu peux tenter de réparer cet héritage."])
    nouveau["avatar"] = dict(parent.get("avatar", defauts()["avatar"]))
    # Les reliques non vendues et les objets uniques sont transmis comme héritage narratif.
    nouveau["inventaire_objets"] = [dict(x) for x in parent.get("inventaire_objets", []) if x.get("rare") or x.get("unique") or x.get("heritage")]
    if nouveau["inventaire_objets"]:
        nouveau["journal"].append([nouveau["age"], f"🎁 Héritage matériel : {len(nouveau['inventaire_objets'])} objet(s) rare(s) transmis par {parent['nom']}. Leur histoire continue."])
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
    av = {"coupe": s["c_coupe"], "couleur": s["c_couleur"], "peau": s["c_peau"], "yeux": s["c_yeux"], "bouche": s["c_bouche"], "accessoire": s["c_accessoire"], "tenue": s["c_tenue"], "iris": s["c_iris"], "visage": s.get("c_visage", "Manga"), "portrait_id": int(s.get("c_portrait_id", 0)), "barbe": s.get("c_barbe", "Aucune")}
    g = new_game(s["c_nom"], s["c_genre"], univ, s[f"c_ville_{univ}"], av, s.get("c_attirance", "Je préfère ne pas préciser"), s.get("c_clan", "Aléatoire"), s.get("c_nom_famille", ""))
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
@media (max-width: 700px) { div[data-testid="stHorizontalBlock"] { flex-wrap: wrap; } div[data-testid="stHorizontalBlock"] > div { min-width: 100% !important; } }
.year-chat-line {padding:7px 0;border-bottom:1px solid rgba(148,163,184,.14);font-size:.9rem;line-height:1.45} .year-chat-dot{color:#38bdf8;font-weight:900;margin-right:5px}

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

/* Contraste renforcé : les expandeurs et leurs boutons doivent clairement sembler cliquables. */
[data-testid="stExpander"] {border:1px solid #35577d !important;border-radius:14px !important;overflow:hidden;background:#111d31 !important;}
[data-testid="stExpander"] details {background:#111d31 !important;}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary:hover {background:linear-gradient(100deg,#18385b,#17263e) !important;color:#f8fafc !important;border-bottom:1px solid #35577d !important;}
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary svg {color:#f8fafc !important;fill:#f8fafc !important;font-weight:750 !important;}
[data-testid="stExpander"] summary:hover {filter:brightness(1.18) !important;}
[data-testid="stExpander"] [data-testid="stVerticalBlock"] {background:transparent !important;}
.stButton > button,
div[data-testid="stButton"] > button {color:#f8fafc !important;background:linear-gradient(135deg,#294a70,#1e3552) !important;border:1px solid #5d83ad !important;box-shadow:0 3px 10px #02061755 !important;font-weight:750 !important;}
.stButton > button:hover,
div[data-testid="stButton"] > button:hover {color:#ffffff !important;background:linear-gradient(135deg,#2563eb,#0e7490) !important;border-color:#7dd3fc !important;box-shadow:0 0 0 2px #38bdf833,0 7px 16px #02061766 !important;filter:brightness(1.08) !important;}
.stButton > button:active {transform:scale(.985) !important;}
.stButton > button:disabled {color:#a8b6c9 !important;background:#263447 !important;border-color:#3b4b60 !important;opacity:.72 !important;box-shadow:none !important;}
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
/* V21: grandes zones tactiles, lisibles sur ordinateur et mobile */
.stButton > button {min-height:54px!important;padding:.65rem .9rem!important;line-height:1.25!important;font-size:.96rem!important;white-space:normal!important;}
[data-testid="stExpander"] summary {min-height:54px!important;padding:.8rem 1rem!important;font-size:1rem!important;}
@media(max-width:700px){.stButton > button{min-height:58px!important;font-size:1rem!important;} [data-testid="stHorizontalBlock"]{gap:.65rem!important;}}
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
 .year-chat-line{padding:.42rem .15rem;border-bottom:1px solid rgba(148,163,184,.12);font-size:.88rem;line-height:1.35}.year-chat-dot{color:#38bdf8;font-weight:900;margin-right:.25rem}

/* Navigation plus lisible : les onglets ressemblent à des boutons sélectionnables. */
div[data-testid="stTabs"] button[role="tab"] {background:#17263d !important;color:#dbeafe !important;border:1px solid #334b68 !important;border-radius:10px 10px 0 0 !important; margin-right:3px !important;}
div[data-testid="stTabs"] button[role="tab"]:hover {background:#24476b !important;color:#ffffff !important;border-color:#60a5fa !important;}
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {background:linear-gradient(135deg,#1d4ed8,#0e7490) !important;color:#ffffff !important;border:1px solid #7dd3fc !important;box-shadow:0 0 0 1px #38bdf833 !important;}
div[data-testid="stTabs"] button[role="tab"] p {color:inherit !important;font-weight:750 !important;}
div[data-testid="stPopover"] button {background:#1b2d46 !important;color:#f8fafc !important;border:1px solid #54749b !important;}
div[data-testid="stPopover"] button:hover {background:#1d4ed8 !important;color:#fff !important;}
/* V26 : contraste fort pour boutons, sous-menus et infobulles Streamlit */
div[data-testid="stButton"] > button,
.stButton > button,
[data-testid="stExpander"] div[data-testid="stButton"] > button,
[data-testid="stPopover"] div[data-testid="stButton"] > button {
  background:#203b5c !important;
  background-image:linear-gradient(135deg,#29496d,#1b304b) !important;
  color:#ffffff !important;
  -webkit-text-fill-color:#ffffff !important;
  border:1px solid #6b91bd !important;
  opacity:1 !important;
  font-weight:750 !important;
  text-shadow:0 1px 1px #0008 !important;
}
div[data-testid="stButton"] > button p,
div[data-testid="stButton"] > button span,
div[data-testid="stButton"] > button div,
.stButton > button p, .stButton > button span {color:#ffffff !important;-webkit-text-fill-color:#ffffff !important;}
div[data-testid="stButton"] > button:hover,
.stButton > button:hover {
  background:#155e91 !important;
  background-image:linear-gradient(135deg,#2563eb,#0891b2) !important;
  color:#ffffff !important;border-color:#7dd3fc !important;
  box-shadow:0 0 0 2px #38bdf844,0 5px 15px #02061766 !important;
}
div[data-testid="stButton"] > button:disabled,
.stButton > button:disabled {
  background:#27364a !important;color:#cbd5e1 !important;
  -webkit-text-fill-color:#cbd5e1 !important;border-color:#475569 !important;
  opacity:1 !important;cursor:not-allowed !important;filter:saturate(.45) !important;
}
/* Infobulles de la propriété help : fond sombre, texte clair, sans débordement pâle */
[data-testid="stTooltipContent"],
[data-testid="stTooltipContent"] *,
[data-baseweb="tooltip"],
[data-baseweb="tooltip"] *,
[role="tooltip"], [role="tooltip"] * {
  background-color:#0b1729 !important;color:#f8fafc !important;
  -webkit-text-fill-color:#f8fafc !important;border-color:#47729d !important;
  opacity:1 !important;text-shadow:none !important;
}
[data-testid="stTooltipContent"], [role="tooltip"] {
  border:1px solid #60a5fa !important;border-radius:10px !important;
  box-shadow:0 8px 24px #020617cc !important;padding:10px 12px !important;
  max-width:min(360px,85vw) !important;white-space:normal !important;
}
/* Les menus déroulants et leurs options conservent le même contraste */
[data-baseweb="popover"] [role="listbox"],
[data-baseweb="popover"] [role="option"] {background:#14243a !important;color:#f8fafc !important;}
[data-baseweb="popover"] [role="option"] * {color:#f8fafc !important;-webkit-text-fill-color:#f8fafc !important;}
[data-baseweb="popover"] [role="option"][aria-selected="true"] {background:#1d4ed8 !important;}
</style>
"""


def ecran_accueil():
    st.markdown("""<div class='creation-hero'><div><div class='eyebrow'>NOUVELLE PARTIE · MULTIVERS</div><h1>Crée ton personnage</h1><p>Personnalise son apparence, son histoire et son destin.</p></div><div class='creation-orb'>✦</div></div>""", unsafe_allow_html=True)
    s = st.session_state
    defaults = {"c_nom":"Alex", "c_genre":"Non-binaire", "c_univ":"real", "c_coupe":"Pointes (manga)", "c_couleur":"Noir", "c_peau":"Beige", "c_yeux":"Manga", "c_bouche":"Sourire", "c_accessoire":"Aucun", "c_tenue":"Classique", "c_iris":"Marron", "c_attirance":"Hétérosexuel·le", "c_origine_heroique":"Aucune", "c_portrait_id":0, "c_barbe":"Aucune", "c_forme_visage":"Ovale"}
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
                st.selectbox("Forme du visage", ["Ovale", "Doux", "Anguleux"], key="c_forme_visage")
                st.selectbox("Couleur des cheveux", list(HAIR_COLORS), key="c_couleur")
                st.selectbox("Teint (fiche)", list(SKINS), key="c_peau")
            with a2:
                st.selectbox("Couleur des yeux", COULEURS_YEUX, key="c_iris")
                st.selectbox("Barbe / pilosité", ["Aucune", "Barbe légère", "Barbe courte", "Barbe complète", "Moustache", "Bouc"], key="c_barbe", help="La barbe apparaît visuellement à partir de 14 ans.")
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
            st.text_input(
                "Nom de famille (facultatif, tous les univers)",
                key="c_nom_famille",
                placeholder=("Ex. Uchiha, Uzumaki…" if univ == "manga" else "Choisis ton nom de famille"),
                help="Si tu laisses ce champ vide, un nom cohérent avec l'univers sera attribué automatiquement."
            )
            if univ == "manga":
                st.selectbox("Héritage / origine spéciale",["Aléatoire", "Aucune", "Famille de shinobi", "Clan prestigieux", "Descendance secrète", "Famille de pirates", "Lignée inconnue"],key="c_origine_speciale")
                if "Village de la Feuille" in s.get(f"c_ville_{univ}", "") or "Village" in s.get(f"c_ville_{univ}", ""):
                    st.selectbox("Clan de naissance", ["Aléatoire", "Uchiha", "Senju", "Uzumaki", "Nara", "Hyûga", "Akimichi", "Aburame", "Inuzuka", "Yamanaka", "Sans clan"], key="c_clan")
            else:
                st.selectbox("Origine familiale",["Aléatoire", "Famille modeste", "Classe moyenne", "Famille aisée", "Famille célèbre", "Origines mystérieuses", "Héritage exceptionnel"],key="c_origine_speciale")
            st.markdown("<div class='creation-section-title'>04 · PERSONNALITÉ</div>",unsafe_allow_html=True)
            st.info("🎲 Ton trait inné sera tiré au sort à la naissance. Tu le découvriras dans ton histoire : pas besoin de tout choisir avant de commencer.")
            st.selectbox("Accessoire",ACCESSOIRES,key="c_accessoire")
            st.info("🧬 Les pouvoirs et les grands destins se découvrent au fil des événements, des rencontres et des décisions.")
        with right:
            av={"coupe":s["c_coupe"],"couleur":s["c_couleur"],"peau":s["c_peau"],"yeux":s["c_yeux"],"bouche":s["c_bouche"],"accessoire":s["c_accessoire"],"tenue":s["c_tenue"],"iris":s["c_iris"],"visage":s.get("c_forme_visage","Ovale"),"portrait_id":int(s.get("c_portrait_id",0)),"barbe":s.get("c_barbe","Aucune"),"forme_visage":s.get("c_forme_visage","Ovale")}
            st.markdown("<div class='live-preview-label'>APERÇU EN DIRECT</div>",unsafe_allow_html=True)
            st.markdown(f"<div class='creation-preview'><div class='preview-backdrop'></div>{avatar_svg(av, age=18, univ=s["c_univ"], taille=300)}<h2>{s['c_nom'] or 'Alex'}</h2><p>{UNIVERS[s['c_univ']]['nom']} · {s['c_genre']}</p><div class='preview-chips'><span>{PORTRAITS_ANIME[int(s.get('c_portrait_id',0)) % len(PORTRAITS_ANIME)][0]}</span><span>{s['c_tenue']}</span><span>{s['c_couleur']} · cheveux</span><span>{s['c_iris']} · yeux</span><span>Barbe : {s.get('c_barbe','Aucune')}</span></div></div>",unsafe_allow_html=True)
            st.markdown("**Évolution du portrait avec l’âge**")
            age_cols = st.columns(5)
            for age_col, sample_age in zip(age_cols, [0, 4, 10, 16, 65]):
                with age_col:
                    st.markdown(avatar_svg(av, age=sample_age, univ=s["c_univ"], taille=105), unsafe_allow_html=True)
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
    avatar = portrait_anime_html({**g.get("avatar", {}), "age_visuel": g.get("age", 0)}, 220, age=g.get("age", 0))
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


ACTION_PREVIEWS = {
    "gym": ("🏋️ Salle de sport", "Force +3 à +7 · Santé +1 à +4 · Apparence +1 · Bonheur +2. Consomme 1 action."),
    "lire": ("📖 Lecture", "Intelligence +2 à +4 · Bonheur +1. Consomme 1 action."),
    "meditation": ("🧘 Méditation", "Bonheur +3 à +6 · Santé +1. Consomme 1 action."),
    "entrainement": ("💪 Entraînement", "Améliore les capacités selon ton univers ; peut fatiguer le personnage. Consomme 1 action."),
    "fete": ("🎉 Faire la fête", "Peut améliorer les relations et le bonheur, avec un risque de fatigue. Réservé aux 15 ans et plus."),
    "voyage": ("✈️ Voyage", "Coûte de l'argent ; améliore généralement le bonheur et peut déclencher une rencontre."),
    "medecin_visite": ("🩺 Médecin", "Coûte 150 ; restaure de la santé."),
    "benevolat": ("🤝 Bénévolat", "Améliore le karma et le bonheur."),
    "coiffeur": ("💇 Changer de look", "Coûte 40 ; applique la coupe et la couleur sélectionnées."),
    "etudier": ("✏️ Étudier", "Améliore les notes et l'intelligence ; peut réduire le bonheur à court terme."),
    "secher": ("🛹 Sécher les cours", "Améliore momentanément le bonheur, mais fait baisser les notes et le karma."),
    "rencontrer": ("💘 Rencontrer quelqu'un", "Tente de créer une nouvelle relation ; le résultat dépend de la chance et de ta situation."),
    "promotion": ("📈 Demander une promotion", "Peut améliorer ton grade et ton salaire ; le résultat dépend de tes performances."),
    "demission": ("👋 Démissionner", "Quitte ton poste actuel. Tu perds le salaire lié à ce métier."),
}

def btn(label, aid, key, disabled=False, **kw):
    """Action directe : aucun écran de confirmation. Le résultat apparaît dans le fil de l'année."""
    titre, description = ACTION_PREVIEWS.get(aid, (label, "Cette action peut modifier les statistiques, l'argent ou les relations."))
    if disabled:
        st.button(label, key=key, disabled=True, use_container_width=True, help=description)
        return
    st.button(label, key=key, on_click=run_action, args=(aid,), kwargs=kw,
              disabled=bool(st.session_state.get("g", {}).get("evt")),
              use_container_width=True, help=f"{titre} — {description}")


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


def metier_compatible_partie(g, key, job):
    """Filtre les carrières ; les rangs exceptionnels se gagnent par événements narratifs."""
    # Ces statuts ne sont pas des métiers à choisir librement dans le catalogue.
    # Une candidature ou une nomination doit venir d'un événement narratif explicite.
    if key in {"anbu", "kage", "sensei_ninja"}:
        return False
    univ = g.get("univers", "real")
    if job.get("univ") != "all" and univ not in job.get("univ", []):
        return False
    saga = g.get("saga_manga", "naruto") if univ == "manga" else None
    # Métiers modernes : monde réel/cyberpunk uniquement, sauf quelques carrières de spectacle.
    modernes = {"ouvrier_btp", "employe", "plombier", "agriculteur", "policier", "pompier", "infirmier", "medecin", "avocat", "dev", "enseignant", "ingenieur", "comptable", "pilote", "astronaute", "influenceur", "mannequin", "footballeur", "hacker", "ripperdoc", "pilote_drone"}
    if univ == "fantasy" and key in modernes:
        return False
    if univ == "real" and key in {"ninja", "anbu", "sensei", "sensei_ninja", "medecin_ninja", "ninja_chercheur", "kage", "pirate", "marine", "revolutionnaire", "exorciste_jujutsu", "chasseur_primes", "dango", "coursier_parchemins"}:
        return False
    if univ == "manga":
        naruto = {"ninja", "anbu", "sensei", "sensei_ninja", "medecin_ninja", "ninja_chercheur", "kage", "dango", "coursier_parchemins"}
        onepiece = {"pirate", "marine", "revolutionnaire", "chasseur_primes"}
        jujutsu = {"exorciste_jujutsu"}
        fantasy_like = {"forgeron", "alchimiste", "palefrenier", "aide_auberge"}
        if key in naruto and saga != "naruto": return False
        if key in onepiece and saga != "onepiece": return False
        if key in jujutsu and saga != "jujutsu": return False
        if key in fantasy_like: return False
        # Les métiers propres à la magie héroïque ne sont pas proposés dans une saga sans rapport.
        if saga == "naruto" and key in {"exorciste_jujutsu", "pirate", "marine", "revolutionnaire", "chasseur_primes"}: return False
        if saga == "onepiece" and key in {"ninja", "anbu", "sensei_ninja", "medecin_ninja", "ninja_chercheur", "kage", "exorciste_jujutsu"}: return False
        if saga == "jujutsu" and key in {"ninja", "anbu", "sensei_ninja", "medecin_ninja", "ninja_chercheur", "kage", "pirate", "marine", "revolutionnaire", "chasseur_primes"}: return False
    if univ == "fantasy":
        # Pas de postes de factions manga dans le médiéval fantastique.
        if key in {"ninja", "anbu", "sensei_ninja", "medecin_ninja", "ninja_chercheur", "kage", "pirate", "marine", "revolutionnaire", "exorciste_jujutsu", "chasseur_primes", "ripperdoc", "pilote_drone"}:
            return False
    return True


def afficher_parcours_quete(g):
    """Parcours narratifs guidés, adaptés à la saga et à l'âge du personnage."""
    age = int(g.get("age", 0))
    saga = g.get("saga_manga", "naruto")
    if g.get("univers") != "manga":
        return
    st.markdown("### 🧭 Métier & parcours — quêtes")
    st.caption("Dans les univers manga, les métiers spéciaux se débloquent par la formation, les examens et les événements, pas par une candidature classique.")
    if saga == "naruto":
        steps = [
            ("academie_inscription", "Intégrer l'Académie ninja", age >= 6, "Accessible à partir de 6 ans"),
            ("academie_taijutsu", "Suivre les cours de Taijutsu", g.get("chakra", 0) >= 20 or g.get("taches_metier", 0) >= 1, "Entraîne-toi ou réalise une activité"),
            ("academie_ninjutsu", "Maîtriser les bases du Ninjutsu", len(g.get("jutsu", [])) >= 1 or g.get("chakra", 0) >= 35, "Développe ton chakra ou découvre une technique"),
            ("academie_examens", "Réussir l'examen de fin d'Académie", g.get("examens_ninja_reussis", 0) >= 1, "Un événement d'examen doit te permettre de le réussir"),
        ]
        titre, prochain = "Parcours ninja", "Genin"
    elif saga == "onepiece":
        steps = [
            ("onepiece_recrutement", "Rejoindre un équipage ou une faction", g.get("faction_manga") not in (None, "Indépendant·e", ""), "Attends un événement de recrutement"),
            ("onepiece_premiere_mission", "Réussir une première mission", g.get("missions_reussies", 0) >= 1, "Accepte une mission quand elle apparaît"),
            ("onepiece_reputation", "Gagner une réputation en mer", g.get("notoriete_manga", 0) >= 20, "Participe aux événements et aux combats"),
        ]
        titre, prochain = "Parcours en mer", "Officier / capitaine reconnu·e"
    else:
        steps = [
            ("jjk_eveil", "Éveiller l'énergie occulte", g.get("energie_occulte", 0) >= 15, "Entraîne-toi ou attends un événement surnaturel"),
            ("jjk_formation", "Suivre une formation d'exorciste", age >= 15, "Accessible à partir de 15 ans"),
            ("jjk_mission", "Réussir une mission d'exorcisme", g.get("missions_reussies", 0) >= 1, "Réussis une mission adaptée à ton niveau"),
        ]
        titre, prochain = "Parcours d'exorciste", "Exorciste confirmé·e"
    done = sum(1 for _, _, ok, _ in steps if ok)
    st.markdown(f"**{titre}** · {done}/{len(steps)} étapes")
    st.progress(done / max(1, len(steps)))
    for key, label, ok, aide in steps:
        st.markdown(("✅" if ok else "🔒") + " **" + label + "**" + ("" if ok else f"  \n   <small>{html.escape(aide)}</small>"), unsafe_allow_html=True)
    if done == len(steps):
        st.success(f"Parcours terminé : tu peux viser le rang suivant — **{prochain}**.")
    else:
        st.info("Les étapes se valident au fil de la partie. Certaines dépendent d'événements aléatoires : continue à vivre et à t'entraîner.")


def tab_carriere(g):
    afficher_parcours_quete(g)
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
        if not metier_compatible_partie(g, key, j):
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
    if g.get("univers") == "manga" and g.get("saga_manga") == "jujutsu":
        st.divider()
        st.markdown("#### 🔒 Techniques de scellement")
        st.caption("Sceller un fléau, un objet maudit ou un adversaire affaibli coûte 25 points d'énergie occulte. Accessible dès 12 ans.")
        btn("🔒 Tenter un scellement", "sceller_cible", "jjk_scellage", disabled=g.get("age", 0) < 12 or g.get("energie_occulte", 0) < 25)
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
    if random.random() < 0.35:
        g.setdefault("consequences_differees", []).append({"type": "rivalite", "due_age": g.get("age", 0)+random.randint(2,5), "nom": cible, "origine": "Une action passée a laissé des traces"})
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
        g.setdefault("boss_historique", []).append({"nom": boss["nom"], "age": g.get("age", 0), "issue": "victoire"})
        log(g,f"🏆 VICTOIRE — Tu as vaincu {boss['nom']}. Cette réussite devient un héritage familial.")
        msg=f"🏆 Tu vaincs {boss['nom']} ! Bonheur et réputation progressent."
    else:
        g["boss_echecs"] = g.get("boss_echecs",0)+1; g["frustration_heritage"] = g.get("frustration_heritage",0)+1
        g.setdefault("boss_historique", []).append({"nom": boss["nom"], "age": g.get("age", 0), "issue": "défaite"})
        g.setdefault("consequences_differees", []).append({"type": "heritage_boss", "due_age": g.get("age", 0)+1, "nom": boss["nom"], "origine": f"La défaite de {boss['nom']} à la génération {g.get('generation',1)}"})
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
            st.write("La carrière de ninja commence par les voies accessibles. Les statuts spéciaux (ANBU, sensei, Kage…) ne sont jamais choisis directement : ils ne deviennent accessibles que si un événement narratif te propose de postuler ou te nomme.")
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
            st.caption("Les postes spéciaux comme ANBU, sensei ou Kage ne sont pas des métiers à sélectionner dans le catalogue : attends un événement narratif qui te propose explicitement une candidature ou une nomination.")
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
            st.caption("Tu peux voyager vers d'autres villages, nouer des alliances ou devenir déserteur. Les candidatures ANBU, les nominations comme sensei et l'accès au titre de Kage doivent être déclenchés par des événements narratifs.")
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
    """Journal complet présenté comme une timeline chronologique."""
    st.markdown("## 📖 Journal de vie")
    st.caption("Tous les souvenirs et événements de ta vie, classés par âge.")
    entries = list(g.get("journal", []))
    if not entries:
        st.info("Ton histoire commencera ici dès tes premières actions.")
        return
    groups = {}
    for age, txt in entries:
        groups.setdefault(int(age), []).append(str(txt))
    for age in sorted(groups):
        stage = "👶 Petite enfance" if age < 3 else "🧒 Enfance" if age < 13 else "🎒 Adolescence" if age < 18 else "🧑 Vie adulte" if age < 60 else "🧓 Retraite & maturité"
        with st.container(border=True):
            st.markdown(f"### {stage} · {age} an{'s' if age != 1 else ''}")
            for txt in groups[age]:
                st.markdown(f"<div style='display:flex;gap:10px;align-items:flex-start;padding:7px 0;border-left:2px solid #38bdf8;margin-left:4px;padding-left:12px'><span style='color:#38bdf8'>●</span><span>{html.escape(accord_genre_texte(txt, g))}</span></div>", unsafe_allow_html=True)


def tab_profil(g):
    nom_complet_profil = f"{str(g.get('nom', 'Alex')).strip()} {str(g.get('nom_famille') or g.get('nom_famille_personnage') or '').strip()}".strip()
    st.markdown(f"## 🪪 {html.escape(nom_complet_profil)}")
    st.caption(f"Nom : {html.escape(str(g.get('nom', 'Alex')))} · Nom de famille : {html.escape(str(g.get('nom_famille') or g.get('nom_famille_personnage') or 'Non renseigné'))}")
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
        with st.expander("🧠 Personnalité évolutive"):
            for key, label in [("curiosite", "Curiosité"), ("discipline", "Discipline"), ("empathie", "Empathie"), ("impulsivite", "Impulsivité"), ("ambition", "Ambition")]:
                val = int(g.get("personnalite", {}).get(key, 50))
                st.progress(max(0, min(100, val))/100, text=f"{label} · {val}/100")
            if g.get("traits_evolutifs"):
                st.caption("Traits développés : " + " · ".join(g["traits_evolutifs"]))
        if g.get("monde_factions"):
            with st.expander("🌍 Équilibre du monde"):
                for nom, niveau in g["monde_factions"].items():
                    st.progress(max(0, min(100, int(niveau)))/100, text=f"{nom} · influence {niveau}/100")
        if g.get("objectifs_heritage"):
            with st.expander("🧬 Objectifs hérités"):
                for obj in g["objectifs_heritage"]:
                    st.write(("✅ " if obj.get("termine") else "🎯 ") + obj.get("nom", "Objectif familial"))
                    st.caption(obj.get("origine", "Conséquence d'une génération précédente"))
        if g.get("objets_histoire"):
            with st.expander("🏺 Histoire des objets"):
                for nom, info in list(g["objets_histoire"].items())[-12:]:
                    st.write(f"**{nom}** — génération {info.get('generation', 1)}, acquis à {info.get('age', 0)} ans. {info.get('origine', '')}")
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



# ======================================================================
#  MUSIQUE DE FOND — playlist YouTube personnalisable
# ======================================================================
MUSIQUES_DEFAUT = [
    {"titre": "My Color", "url": "https://www.youtube.com/watch?v=tZLR2IgoEXM"},
    {"titre": "X", "url": "https://www.youtube.com/watch?v=2uuPU2K_w9c"},
    {"titre": "Naruto", "url": "https://www.youtube.com/watch?v=2upuBiEiXDk"},
    {"titre": "Jujutsu Kaisen", "url": "https://www.youtube.com/watch?v=gcgKUcJKxIs"},
    {"titre": "Cry Baby", "url": "https://www.youtube.com/watch?v=By_JYrhx-WY"},
]

def extraire_id_youtube(url):
    # Parse une URL YouTube ou un ID.
    valeur = str(url or "").strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", valeur):
        return valeur
    motifs = [r"[?&]v=([A-Za-z0-9_-]{11})", r"youtu\.be/([A-Za-z0-9_-]{11})", r"youtube\.com/embed/([A-Za-z0-9_-]{11})"]
    for motif in motifs:
        m = re.search(motif, valeur)
        if m:
            return m.group(1)
    return None

def lecteur_musique():
    """Lecteur YouTube qui tente de démarrer dès le chargement de la page.

    La lecture automatique avec son ne peut pas être imposée par une application web :
    les navigateurs exigent généralement une interaction de l'utilisateur. On démarre
    donc en muet, puis l'utilisateur peut activer le son dans les commandes YouTube.
    """
    st.session_state.setdefault("playlist_ma_vie", [dict(x) for x in MUSIQUES_DEFAUT])
    st.session_state.setdefault("musique_selection", 0)
    playlist = st.session_state["playlist_ma_vie"]
    playlist[:] = [x for x in playlist if isinstance(x, dict) and extraire_id_youtube(x.get("url", ""))]
    if playlist:
        st.sidebar.divider()
        st.sidebar.header("🎵 Musique de fond")
        noms = [f"{i+1}. {x.get('titre') or 'Sans titre'}" for i, x in enumerate(playlist)]
        if st.session_state["musique_selection"] >= len(playlist):
            st.session_state["musique_selection"] = 0
        choix = st.sidebar.selectbox(
            "Playlist", options=list(range(len(playlist))),
            format_func=lambda i: noms[i], index=st.session_state["musique_selection"],
            key="choix_musique_ui")
        st.session_state["musique_selection"] = choix
        ids = [extraire_id_youtube(x["url"]) for x in playlist]
        current = ids[choix]
        ids_playlist = ",".join(x for x in ids if x)
        # Le mode muet est nécessaire pour que la plupart des navigateurs autorisent l'autoplay.
        embed = (f"https://www.youtube-nocookie.com/embed/{current}"
                 f"?autoplay=1&mute=1&controls=1&loop=1&playlist={ids_playlist}"
                 "&playsinline=1&rel=0&enablejsapi=1")
        titre = html.escape(playlist[choix].get('titre') or 'Musique')
        st.components.v1.html(
            f'''<div style="font-family:Arial,sans-serif;color:#f8fafc;background:#101b31;border:1px solid #4776a8;border-radius:12px;padding:9px;box-sizing:border-box;width:100%;">
            <div style="font-size:13px;font-weight:700;margin:0 0 7px 2px;color:#f8fafc;">🎧 Lecture automatique · {titre}</div>
            <iframe width="100%" height="155" src="{html.escape(embed, quote=True)}" title="Lecteur musical Ma Vie" frameborder="0"
            allow="autoplay; encrypted-media; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen
            style="display:block;border:0;border-radius:8px;max-width:100%;"></iframe>
            <div style="font-size:11px;line-height:1.45;color:#cbd8eb;margin-top:7px;">La musique tente de démarrer automatiquement, d'abord sans son. Clique sur l'icône du son dans le lecteur pour l'entendre.</div></div>''',
            height=225, scrolling=False)
        with st.sidebar.expander("➕ Ajouter une musique YouTube", expanded=False):
            with st.form("ajouter_musique_form", clear_on_submit=True):
                titre_nouveau = st.text_input("Titre de la musique", placeholder="Ex. Musique de combat")
                url = st.text_input("Lien YouTube", placeholder="https://www.youtube.com/watch?v=...")
                ajouter = st.form_submit_button("Ajouter à la playlist", use_container_width=True)
            if ajouter:
                video_id = extraire_id_youtube(url)
                if not video_id:
                    st.sidebar.error("Lien non reconnu. Colle un lien YouTube ou l'ID de la vidéo.")
                elif any(extraire_id_youtube(x.get("url", "")) == video_id for x in playlist):
                    st.sidebar.info("Cette vidéo est déjà dans ta playlist.")
                else:
                    playlist.append({"titre": titre_nouveau.strip() or f"Musique {len(playlist)+1}", "url": f"https://www.youtube.com/watch?v={video_id}"})
                    st.session_state["musique_selection"] = len(playlist)-1
                    st.sidebar.success("Musique ajoutée !")
                    st.rerun()
        if len(playlist) > 1:
            with st.sidebar.expander("🧹 Gérer la playlist", expanded=False):
                supprimer_idx = st.selectbox("Retirer une musique", options=list(range(len(playlist))),
                    format_func=lambda i: f"{playlist[i].get('titre','Sans titre')}", key="supprimer_musique_idx")
                if st.button("Retirer de la playlist", key="retirer_musique_btn", use_container_width=True):
                    playlist.pop(supprimer_idx)
                    st.session_state["musique_selection"] = min(st.session_state["musique_selection"], len(playlist)-1)
                    st.rerun()
        st.sidebar.caption("Le navigateur peut bloquer l'autoplay selon ses réglages ; les vidéos interdites à l'intégration ne pourront pas être lues.")


def sidebar(g):
    lecteur_musique()
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
        avatar = avatar_svg({**g.get("avatar", {}), "metier": titre_metier(g), "village": g.get("saga_manga") == "naruto", "saga_manga": g.get("saga_manga")}, age=g.get("age", 0), univ=g.get("univers", "real"), taille=260)
        st.markdown(f"<div class='avatar-profile-card'><div class='avatar-halo'></div><div class='avatar-art'>{avatar}</div><div class='avatar-status'><span></span>{'EN VIE' if g.get('vivant', True) else 'FIN DE VIE'} · {g.get('age', 0)} ANS</div></div>", unsafe_allow_html=True)
        nom_perso = str(g.get('nom','Alex'))
        nom_famille_perso = str(g.get('nom_famille') or g.get('nom_famille_personnage') or '').strip()
        nom_complet = f"{nom_perso} {nom_famille_perso}".strip()
        st.markdown(f"### {html.escape(nom_complet)}")
        if nom_famille_perso:
            st.caption(f"📛 Nom de famille : **{html.escape(nom_famille_perso)}**")
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
        p = g.get("personnalite", {})
        st.caption("🧠 " + " · ".join(label for key, label in [("curiosite", "Curiosité"), ("discipline", "Discipline"), ("empathie", "Empathie"), ("impulsivite", "Impulsivité"), ("ambition", "Ambition")] if int(p.get(key, 50)) >= 72) if any(int(p.get(k, 50)) >= 72 for k in ("curiosite", "discipline", "empathie", "impulsivite", "ambition")) else "🧠 Ta personnalité se construit avec tes choix.")
        # Mini-fil de discussion : uniquement les actions/événements de l'année actuelle.
        st.markdown("#### 💬 Cette année")
        anne_courante = int(g.get("age", 0))
        activites = [(age, texte) for age, texte in g.get("journal", []) if int(age) == anne_courante]
        with st.container(border=True, height=230):
            if activites:
                for age, texte in activites[-8:]:
                    st.markdown(f"<div class='year-chat-line'><span class='year-chat-dot'>•</span> {accord_genre_texte(str(texte), g)}</div>", unsafe_allow_html=True)
            else:
                st.caption("Aucune action pour le moment. Choisis une action à droite : son résultat apparaîtra ici.")
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
            q1, q2 = st.columns(2, gap="medium")
            with q1: btn("🏋️ Salle de sport", "gym", "home_quick_gym")
            with q2: btn(ENTRAINEMENTS[g.get("univers", "real")][0], "entrainement", "home_quick_training")
            q3, q4 = st.columns(2, gap="medium")
            with q3: btn("🩺 Médecin (150)", "medecin_visite", "home_quick_doc")
            with q4: btn("📖 Lire", "lire", "home_quick_read")
            q5, q6 = st.columns(2, gap="medium")
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
    # Sous les actions : journal annuel à gauche, événement interactif à droite.
    recap_col, event_col = st.columns([1, 1.35], gap="medium")
    with recap_col:
        st.markdown(f"### 🗓️ Cette année · {g.get('age', 0)} ans")
        recap = [(age, txt) for age, txt in g.get("journal", []) if int(age) == int(g.get("age", 0))]
        with st.container(border=True, height=270):
            if recap:
                for age, txt in recap[-6:]:
                    st.markdown(f"<div class='year-chat-line'><span class='year-chat-dot'>•</span> {html.escape(accord_genre_texte(str(txt), g))}</div>", unsafe_allow_html=True)
            else:
                st.caption("Aucune action enregistrée cette année. Choisis une action pour commencer.")
    with event_col:
        if g.get("evt"):
            st.markdown("### 🔔 Événement en cours")
            # Le choix à résoudre est placé dans l'espace vide à côté du récapitulatif annuel.
            bloc_evenement(g)
        else:
            st.markdown("### 🌍 Événements de l'année")
            news = actualites_annee_courante(g)[-3:]
            with st.container(border=True, height=270):
                if news:
                    for item in reversed(news):
                        st.markdown(f"**{html.escape(str(item.get('titre','Actualité')))}**")
                        st.caption(f"{html.escape(str(item.get('type','information')).capitalize())} · {item.get('age',g.get('age',0))} ans")
                        st.write(item.get('texte',''))
                        st.divider()
                else:
                    st.caption("Aucun événement mondial cette année. Les nouvelles apparaîtront ici.")
    if g.get("evt"):
        st.markdown("### 🌍 Actualités de l'année")
        news = actualites_annee_courante(g)[-2:]
        if news:
            news_cols = st.columns(len(news))
            for col, item in zip(news_cols, news):
                with col:
                    with st.container(border=True):
                        st.markdown(f"**{html.escape(str(item.get('titre','Actualité')))}**")
                        st.caption(f"{html.escape(str(item.get('type','information')).capitalize())} · {item.get('age',g.get('age',0))} ans")
                        st.write(item.get('texte',''))
    # Bouton circulaire centré, placé après le récapitulatif et l'événement.
    st.markdown("""<style>
    div[data-testid="stButton"] button[key="advance_year_circle"] {border-radius:999px!important;min-height:76px!important;width:76px!important;height:76px!important;font-size:1.55rem!important;background:linear-gradient(135deg,#7c3aed,#0891b2)!important;border:2px solid #7dd3fc!important;box-shadow:0 0 24px #38bdf855!important;margin:auto!important;display:block!important}
    .year-advance-label{text-align:center;color:#cbd5e1;font-weight:850;font-size:.72rem;letter-spacing:.08em;margin-top:5px}
    </style>""", unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,1,1])
    with c2:
        st.button("⏭", key="advance_year_circle", on_click=next_year, type="primary", disabled=not g.get("vivant", True), help="Passer à l’année suivante")
        st.markdown("<div class='year-advance-label'>PASSER L’ANNÉE</div>", unsafe_allow_html=True)
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
    # Bannière d'identité inspirée des jeux de simulation de vie.
    origine_banniere = g.get("origine_familiale") or g.get("ville", "Origine inconnue")
    st.markdown(
        f"<div style=\"display:flex;align-items:center;gap:.65rem;flex-wrap:wrap;"
        f"padding:.7rem .9rem;margin:.2rem 0 .7rem;border-radius:15px;"
        f"border:1px solid #31577c;background:linear-gradient(110deg,#102943,#0a1728);\">"
        f"<span style=\"font-size:1.35rem\">🧬</span>"
        f"<span><b>{html.escape(str(g.get('nom','Alex')))} {html.escape(str(g.get('nom_famille') or g.get('nom_famille_personnage') or ''))}</b>"
        f"<br><small>{int(g.get('age',0))} ans · {html.escape(str(titre_metier(g)))} · {html.escape(str(origine_banniere))}</small></span>"
        f"<span style=\"margin-left:auto;color:#7dd3fc;font-weight:800\">{html.escape(str(UNIVERS.get(g.get('univers'),{}).get('nom',g.get('univers',''))))}</span></div>",
        unsafe_allow_html=True,
    )
    st.divider()

    page = st.session_state.get("nav_page", "🏠 Ma vie")
    msg = st.session_state.get("flash")
    # Sur l'accueil, les résultats sont affichés dans le mini-journal sous la personnalité.
    # Les autres pages gardent le message global de retour.
    if msg and page != "🏠 Ma vie":
        afficher_effet_action(msg)

    if page == "🏠 Ma vie":
        # Priorité visuelle aux événements qui attendent une décision, comme BitLife.
        if not g.get("vivant", True):
            bloc_mort(g)
        else:
            st.markdown("## 📅 Une nouvelle année t'attend")
            st.caption("Tes décisions façonnent ta vie. Les événements en attente apparaissent dans le panneau à côté du récapitulatif annuel.")
            st.metric("⏳ Temps libre cette année", f"{g.get('actions',0)}/{ACTIONS_PAR_AN}")
        # La page d'accueil réunit les panneaux demandés : avatar, naissance, famille, défis et actualités.
        tab_apercu(g)
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


def injecter_style_boutons_v28():
    """Renforce le contraste et les états interactifs des boutons Streamlit."""
    st.markdown("""<style>
    /* Boutons d'action : fort contraste, état cliquable évident */
    div[data-testid="stButton"] > button, .stButton > button,
    div[data-testid="stFormSubmitButton"] > button,
    div[data-testid="stDownloadButton"] > button {
      background: linear-gradient(135deg,#244b78 0%,#173451 100%) !important;
      color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;
      border:1px solid #75bfff !important; border-radius:12px !important;
      min-height:2.8rem !important; font-weight:800 !important;
      box-shadow:0 3px 12px rgba(0,0,0,.25) !important;
      transition:background .15s ease, box-shadow .15s ease, transform .15s ease !important;
    }
    div[data-testid="stButton"] > button p,
    div[data-testid="stButton"] > button span,
    div[data-testid="stButton"] > button div,
    div[data-testid="stFormSubmitButton"] > button p,
    div[data-testid="stDownloadButton"] > button p {
      color:#fff !important; -webkit-text-fill-color:#fff !important;
    }
    div[data-testid="stButton"] > button:hover,
    .stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover,
    div[data-testid="stDownloadButton"] > button:hover {
      background:linear-gradient(135deg,#2563eb 0%,#0891b2 100%) !important;
      color:#fff !important; border-color:#a5f3fc !important;
      box-shadow:0 0 0 3px rgba(56,189,248,.2),0 7px 18px rgba(0,0,0,.35) !important;
      transform:translateY(-1px) !important; cursor:pointer !important;
    }
    div[data-testid="stButton"] > button:focus-visible,
    div[data-testid="stFormSubmitButton"] > button:focus-visible,
    div[data-testid="stDownloadButton"] > button:focus-visible {
      outline:3px solid #fde68a !important; outline-offset:3px !important;
    }
    div[data-testid="stButton"] > button:disabled,
    div[data-testid="stFormSubmitButton"] > button:disabled {
      background:#26364a !important; color:#d2dbe8 !important;
      -webkit-text-fill-color:#d2dbe8 !important; border-color:#53657a !important;
      opacity:1 !important; box-shadow:none !important; transform:none !important;
    }
    [data-testid="stExpander"] summary {cursor:pointer !important;}
    [data-testid="stExpander"] summary:hover {filter:brightness(1.18) !important;}
    @media(max-width:700px) {
      div[data-testid="stButton"] > button,
      div[data-testid="stFormSubmitButton"] > button {min-height:3rem !important; padding:.55rem .65rem !important;}
    }
    </style>""", unsafe_allow_html=True)


def main():
    injecter_style_boutons_v28()
    st.set_page_config(page_title="Ma Vie — Simulateur de vie", page_icon="🧬", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    # V31 — refonte responsive mobile : cartes plus compactes, identité en bannière,
    # journal prioritaire et navigation tactile. Les règles sont ajoutées après le CSS existant.
    st.markdown(r"""
    <style>
    :root { color-scheme: dark; }
    .stApp { background: radial-gradient(ellipse at top, #142b48 0%, #071321 55%, #050b14 100%) !important; }
    [data-testid="stAppViewContainer"] .main .block-container { max-width: 1180px; padding-top: .7rem; padding-bottom: 6rem; }
    [data-testid="stVerticalBlockBorderWrapper"] { border-color: rgba(93,150,205,.28) !important; border-radius: 16px !important; background: linear-gradient(145deg,rgba(18,38,62,.88),rgba(7,20,35,.94)); }
    [data-testid="stMetric"] { background: rgba(12,30,51,.8); border: 1px solid #284a6b; border-radius: 13px; padding: .65rem .8rem; }
    [data-testid="stTabs"] button { border-radius: 10px 10px 0 0; font-weight: 750; }
    [data-testid="stExpander"] { border: 1px solid #294968 !important; border-radius: 13px !important; overflow: hidden; }
    [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3 { letter-spacing: -.025em; }
    [data-testid="stSidebar"] { background: #071525; }
    @media (max-width: 700px) {
      [data-testid="stAppViewContainer"] .main .block-container { padding: .45rem .55rem 5.8rem !important; }
      [data-testid="stHeader"] { height: 2.4rem; }
      [data-testid="stHorizontalBlock"] { gap: .45rem !important; flex-wrap: wrap !important; }
      [data-testid="stHorizontalBlock"] > [data-testid="column"] { min-width: calc(50% - .3rem) !important; flex: 1 1 calc(50% - .3rem) !important; }
      [data-testid="stHorizontalBlock"] > [data-testid="column"]:only-child { min-width: 100% !important; }
      [data-testid="stMetric"] { padding: .5rem .6rem; }
      [data-testid="stMetricValue"] { font-size: 1.25rem !important; }
      [data-testid="stMarkdownContainer"] h1 { font-size: 1.55rem !important; }
      [data-testid="stMarkdownContainer"] h2 { font-size: 1.28rem !important; }
      [data-testid="stMarkdownContainer"] h3 { font-size: 1.08rem !important; }
      [data-testid="stButton"] > button, [data-testid="stFormSubmitButton"] > button { min-height: 2.75rem !important; padding: .45rem .55rem !important; font-size: .9rem !important; white-space: normal !important; }
      [data-testid="stTabs"] [role="tablist"] { gap: .25rem; overflow-x: auto; flex-wrap: nowrap; }
      [data-testid="stTabs"] button[role="tab"] { flex: 0 0 auto; padding: .55rem .7rem; font-size: .82rem; }
      [data-testid="stImage"] img { border-radius: 14px; }
      [data-testid="stVerticalBlockBorderWrapper"] { padding: .6rem !important; }
      [data-testid="stDataFrame"] { overflow-x: auto; }
    }
    </style>
    """, unsafe_allow_html=True)
    # V30 : surcharge finale après toutes les feuilles de style pour corriger
    # les boutons Streamlit qui apparaissaient blancs avec un texte pâle.
    st.markdown("""
    <style>
    div[data-testid="stButton"] > button,
    div[data-testid="stFormSubmitButton"] > button,
    div[data-testid="stDownloadButton"] > button,
    .stButton > button,
    button[kind="secondary"] {
      background: #203b5c !important;
      background-image: linear-gradient(135deg, #29496d, #1b304b) !important;
      color: #ffffff !important;
      -webkit-text-fill-color: #ffffff !important;
      border: 1px solid #6b91bd !important;
      border-radius: 10px !important;
      font-weight: 750 !important;
      opacity: 1 !important;
      box-shadow: 0 3px 10px rgba(0,0,0,.22) !important;
    }
    div[data-testid="stButton"] > button p,
    div[data-testid="stButton"] > button span,
    div[data-testid="stButton"] > button div,
    div[data-testid="stFormSubmitButton"] > button p,
    div[data-testid="stDownloadButton"] > button p,
    .stButton > button * {
      color: #ffffff !important;
      -webkit-text-fill-color: #ffffff !important;
      opacity: 1 !important;
    }
    div[data-testid="stButton"] > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover,
    div[data-testid="stDownloadButton"] > button:hover,
    .stButton > button:hover,
    button[kind="secondary"]:hover {
      background: #155e91 !important;
      background-image: linear-gradient(135deg, #2563eb, #0891b2) !important;
      color: #ffffff !important;
      -webkit-text-fill-color: #ffffff !important;
      border-color: #7dd3fc !important;
      box-shadow: 0 0 0 2px rgba(56,189,248,.28), 0 6px 16px rgba(2,6,23,.4) !important;
      filter: brightness(1.08) !important;
    }
    div[data-testid="stButton"] > button:disabled,
    div[data-testid="stFormSubmitButton"] > button:disabled,
    div[data-testid="stDownloadButton"] > button:disabled {
      background: #27364a !important;
      background-image: none !important;
      color: #dbe5f1 !important;
      -webkit-text-fill-color: #dbe5f1 !important;
      border-color: #53657a !important;
      opacity: 1 !important;
      box-shadow: none !important;
    }
    /* Les en-têtes repliables doivent aussi sembler interactifs et lisibles. */
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary * {
      color: #f1f5f9 !important;
      -webkit-text-fill-color: #f1f5f9 !important;
    }
    [data-testid="stExpander"] summary {
      background: #172c46 !important;
      border: 1px solid #46688e !important;
      border-radius: 9px !important;
      font-weight: 750 !important;
    }
    [data-testid="stExpander"] summary:hover {
      background: #24476b !important;
      border-color: #7dd3fc !important;
    }
    @media(max-width:700px) {
      div[data-testid="stButton"] > button,
      div[data-testid="stFormSubmitButton"] > button { min-height: 3rem !important; }
    }
    </style>
    """, unsafe_allow_html=True)
    st.session_state.setdefault("g", None)
    g = st.session_state["g"]
    if g is None:
        ecran_accueil()
    else:
        ecran_jeu(g)


if __name__ == "__main__":
    main()
