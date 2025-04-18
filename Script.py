#!/usr/bin/env python3

import os
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# ---------------------------------------------------------------------------
# PARAMÈTRES CONFIGURABLES
# ---------------------------------------------------------------------------
CHEMIN_RACINE = "/LE_VOLUME"  # Chemin racine où commence l'analyse
AGE_MAX_ANNEES = 2  # Nombre d'années avant qu'un dossier soit considéré comme obsolète
PROFONDEUR_MAX = 3  # Profondeur maximale de recherche dans les sous-dossiers
FICHIER_RAPPORT = "rapport_analyse.txt"  # Nom du fichier de rapport généré

# Configuration de l'email
EMAIL_EXPEDITEUR = "ADRESSE_MAIL"  # Adresse email de l'expéditeur
EMAIL_DESTINATAIRE = "ADRESSE_MAIL"  # Adresse email du destinataire
SERVEUR_SMTP = "SRV_SMTP"  # Serveur SMTP
PORT_SMTP = 587  # Port SMTP
MOT_DE_PASSE_EMAIL = "MDP_APPLICATION"  # Mot de passe ou clé d'application pour l'email

# ---------------------------------------------------------------------------
# VARIABLES GLOBALES
# ---------------------------------------------------------------------------
date_actuelle = datetime.date.today()  # Date actuelle
seuil_obsolescence = date_actuelle.replace(year=date_actuelle.year - AGE_MAX_ANNEES)  # Date limite d'obsolescence

# Liste des dossiers système ou spécifiques à ignorer
DOSSIERS_SYSTEME = [
    "@eaDir", "#recycle", "#snapshot", ".DS_Store", "ActiveBackupforBusiness"
]

# Compteurs pour suivre les statistiques de l'analyse
total_analyse = 0  # Nombre total de dossiers analysés
dossiers_obsoletes = 0  # Nombre de dossiers obsolètes

# ---------------------------------------------------------------------------
# FONCTIONS
# ---------------------------------------------------------------------------

def est_dossier_systeme_ou_ignorer(entree):
    """
    Vérifie si un dossier ou fichier doit être ignoré.
    Retourne True si le dossier est dans la liste des dossiers système ou commence par '@'.
    """
    return entree in DOSSIERS_SYSTEME or entree.startswith("@")

def analyser_dossier_sauvegarde(chemin_dossier):
    """
    Analyse un dossier de sauvegarde pour déterminer s'il est obsolète ou valide.
    - Récupère la dernière date de modification du dossier.
    - Compare cette date avec le seuil d'obsolescence.
    - Met à jour les compteurs globaux.
    """
    global total_analyse, dossiers_obsoletes
    derniere_modif = os.path.getmtime(chemin_dossier)  # Récupère la dernière date de modification
    date_dossier = datetime.date.fromtimestamp(derniere_modif)  # Convertit le timestamp en date
    total_analyse += 1  # Incrémente le compteur de dossiers analysés
    nom_dossier = os.path.basename(chemin_dossier)  # Nom du dossier
    if date_dossier < seuil_obsolescence:  # Si la date de modification est antérieure au seuil
        print(f"  ❌ {nom_dossier:<30} | Dernière modif : {date_dossier}  → Obsolète")
        dossiers_obsoletes += 1  # Incrémente le compteur de dossiers obsolètes
    else:
        print(f"  ✅ {nom_dossier:<30} | Dernière modif : {date_dossier}  → Valide")

def traiter_dossier_parent(chemin_parent):
    """
    Analyse un dossier parent contenant des sauvegardes.
    - Si le dossier se termine par .hbk, il est analysé directement.
    - Sinon, parcourt les sous-dossiers et analyse chaque sous-dossier valide.
    """
    nom_parent = os.path.basename(chemin_parent)  # Nom du dossier parent
    
    if nom_parent.endswith(".hbk"):  # Si le dossier est une sauvegarde directe
        print(f"\n📦 Dossier de sauvegarde détecté : {nom_parent}")
        print("-" * 50)
        analyser_dossier_sauvegarde(chemin_parent)
        return

    print(f"\n📂 Analyse du dossier parent : {nom_parent}")
    print("-" * 50)

    try:
        for entree in os.listdir(chemin_parent):  # Parcourt les entrées du dossier parent
            if est_dossier_systeme_ou_ignorer(entree):  # Ignore les dossiers système
                continue

            chemin_complet = os.path.join(chemin_parent, entree)  # Chemin complet de l'entrée

            if os.path.isdir(chemin_complet):  # Si l'entrée est un dossier, elle est analysée
                analyser_dossier_sauvegarde(chemin_complet)

    except (PermissionError, FileNotFoundError) as e:
        print(f"⚠️ Impossible d'accéder au dossier parent {nom_parent}: {e}")

def verifier_dossiers_parents(chemin):
    """
    Vérifie si un dossier contient des sauvegardes et les analyse.
    - Si le dossier contient @eaDir, il est considéré comme pertinent.
    - Parcourt les sous-dossiers et appelle traiter_dossier_parent pour chaque sous-dossier valide.
    """
    try:
        contenu = os.listdir(chemin)  # Liste les contenus du dossier

        if "@eaDir" in contenu:  # Si le dossier contient @eaDir
            print(f"\n🔍 Répertoire détecté : {os.path.basename(chemin)} (contient @eaDir)")
            print("-" * 50)

            for entree in contenu:  # Parcourt les entrées du dossier
                if est_dossier_systeme_ou_ignorer(entree):  # Ignore les dossiers système
                    continue

                chemin_complet = os.path.join(chemin, entree)  # Chemin complet de l'entrée

                if os.path.isdir(chemin_complet):  # Si l'entrée est un dossier, elle est analysée
                    traiter_dossier_parent(chemin_complet)

    except (PermissionError, FileNotFoundError) as e:
        print(f"⚠️ Impossible d'accéder au dossier {chemin}: {e}")

def rechercher_recursivement(chemin, profondeur_actuelle=0):
    """
    Recherche récursive des dossiers jusqu'à une profondeur maximale.
    - Vérifie les sauvegardes dans le dossier courant.
    - Continue la recherche dans les sous-dossiers si la profondeur maximale n'est pas atteinte.
    """
    if profondeur_actuelle > PROFONDEUR_MAX:  # Arrête la recherche si la profondeur maximale est atteinte
        return

    verifier_dossiers_parents(chemin)  # Vérifie les sauvegardes dans le dossier courant

    try:
        for entree in os.listdir(chemin):  # Parcourt les entrées du dossier
            if est_dossier_systeme_ou_ignorer(entree):  # Ignore les dossiers système
                continue

            chemin_complet = os.path.join(chemin, entree)  # Chemin complet de l'entrée
            if os.path.isdir(chemin_complet):  # Si l'entrée est un dossier, continue la recherche récursive
                rechercher_recursivement(chemin_complet, profondeur_actuelle + 1)
    except (PermissionError, FileNotFoundError):
        pass

def generer_rapport():
    """
    Génère un rapport dans un fichier texte.
    - Contient un résumé global et les détails de chaque dossier analysé.
    """
    with open(FICHIER_RAPPORT, "w", encoding="utf-8") as rapport:
        rapport.write("\n" + "=" * 60 + "\n")
        rapport.write(f"🔍 DÉMARRAGE DE L'ANALYSE DES SAUVEGARDES\n")
        rapport.write(f"📁 Dossier racine       : {CHEMIN_RACINE}\n")
        rapport.write(f"📅 Date du jour         : {date_actuelle}\n")
        rapport.write(f"📉 Seuil d'obsolescence : {seuil_obsolescence}\n")
        rapport.write("=" * 60 + "\n\n")

        # Redirige les sorties vers le fichier
        original_stdout = os.sys.stdout
        os.sys.stdout = rapport
        rechercher_recursivement(CHEMIN_RACINE)
        os.sys.stdout = original_stdout

        rapport.write("\n" + "=" * 60 + "\n")
        rapport.write(f"📊 ANALYSE TERMINÉE\n")
        rapport.write(f"📁 Total dossiers analysés : {total_analyse}\n")
        rapport.write(f"❌ Dossiers obsolètes      : {dossiers_obsoletes}\n")
        rapport.write(f"✅ Dossiers valides        : {total_analyse - dossiers_obsoletes}\n")
        rapport.write("=" * 60 + "\n")

    print(f"✅ Rapport généré : {FICHIER_RAPPORT}")

def envoyer_email():
    """
    Envoie le rapport par email.
    - Ajoute le fichier rapport en pièce jointe.
    - Utilise le serveur SMTP configuré pour envoyer l'email.
    """
    sujet = "Rapport d'analyse des sauvegardes"
    corps = "Veuillez trouver ci-joint le rapport d'analyse des sauvegardes."

    # Création du message
    msg = MIMEMultipart()
    msg['From'] = EMAIL_EXPEDITEUR
    msg['To'] = EMAIL_DESTINATAIRE
    msg['Subject'] = sujet

    msg.attach(MIMEText(corps, 'plain'))

    # Pièce jointe
    with open(FICHIER_RAPPORT, "rb") as piece_jointe:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(piece_jointe.read())

    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename={FICHIER_RAPPORT}",
    )

    msg.attach(part)

    # Envoi de l'email
    with smtplib.SMTP(SERVEUR_SMTP, PORT_SMTP) as serveur:
        serveur.starttls()  # Démarre une connexion sécurisée
        serveur.login(EMAIL_EXPEDITEUR, MOT_DE_PASSE_EMAIL)  # Authentification
        serveur.sendmail(EMAIL_EXPEDITEUR, EMAIL_DESTINATAIRE, msg.as_string())  # Envoi de l'email

    print("✅ Email envoyé avec succès.")

# ---------------------------------------------------------------------------
# POINT D'ENTRÉE
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    generer_rapport()  # Génère le rapport
    envoyer_email()  # Envoie le rapport par email
