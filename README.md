# backup-solution

# Backup Solution

Ce script permet de vérifier l'état des sauvegardes sur un NAS Synology, de générer un rapport indiquant les sauvegardes valides ou obsolètes, et d'envoyer ce rapport par mail.

## Fonctionnalités
- Parcourt un volume féfinit du NAS pour identifier les sauvegardes obsolètes.
- Génère un rapport au format txt.
- Envoie un e-mail automatique avec le rapport.

## Installation

1. Clonez ce repository sur votre machine locale :
   ```bash
   git clone https://github.com/S1CH1/backup-solution.git

## Personnalisation nécessaire

Avant d'exécuter le script, il est important de **modifier certains paramètres** dans le script pour l'adapter à votre configuration :

- **Chemin du volume** : Modifiez le chemin du volume NAS dans le script pour qu'il pointe vers le répertoire correct contenant les sauvegardes.
- **Adresse e-mail de l'expéditeur** : Mettez à jour l'adresse e-mail de l'expéditeur dans le script (et dans le fichier de configuration si vous utilisez un tel fichier).
- **Adresse e-mail du destinataire** : Mettez à jour l'adresse e-mail du destinataire dans le script (et dans le fichier de configuration si vous utilisez un tel fichier).
- **Serveur SMTP** : Vérifiez et ajustez les paramètres SMTP pour l'envoi des e-mails (serveur, port, sécurité).
- **Mot de passe de l'application** : Pour plus de sécurité, veillez à ne pas laisser le mot de passe en clair dans le script. Il peut être préférable de le stocker dans un fichier séparé avec des droits restreints.
- **Le Seuil de validité** : Ajustez le seuil de validité des sauvegardes selon vos besoins (par exemple, une période de validité de 2 ans).
- **La Profondeur Max** : Modifiez la profondeur maximale à laquelle le script doit explorer les sous-dossiers. Cela peut être utile pour limiter l'analyse des répertoires trop profonds.
- **Les Dossiers Système** : Vérifiez et mettez à jour la liste des dossiers système ou interdits que vous souhaitez exclure de l'analyse.


Ces modifications sont essentielles pour garantir le bon fonctionnement du script dans votre environnement spécifique.

