# DragoSound

## Description du Projet

**DragoSound** est un lecteur audio de bureau conçu en Python. Il s'appuie sur les librairies `tkinter` pour son interface graphique utilisateur (GUI) et `pygame` pour la gestion de la lecture audio. L'application vise à offrir une expérience utilisateur simple pour l'écoute de fichiers musicaux.

## Fonctionnalités Clés

* **Gestion de Fichiers et Dossiers :** Permet de charger et lire des fichiers audio individuels ou d'importer toutes les pistes compatibles depuis un répertoire (album).
* **Liste de Lecture :** Affiche la liste des pistes chargées et permet la sélection directe d'un morceau pour la lecture.
* **Contrôles de Lecture :** Comprend les fonctions standards telles que Lecture, Pause, Piste Précédente et Piste Suivante. La fonction Pause permet de reprendre la lecture à l'endroit exact où elle a été interrompue.
* **Contrôle du Volume :** Dispose d'un curseur dédié pour ajuster le niveau sonore.
* **Indicateur de Progression :** Une barre visuelle indique le temps écoulé depuis le début de la piste en cours de lecture.

## Limitations Actuelles

Il est important de noter les limitations de la version actuelle de DragoSound :

* **Absence d'Affichage de la Durée Totale :** La durée complète de chaque piste n'est pas déterminée ni affichée dans l'interface utilisateur.
* **Barre de Progression Non Interactive :** La barre de progression sert uniquement d'indicateur visuel du temps écoulé et ne permet pas de cliquer ou de glisser pour naviguer à un point spécifique de la piste (fonctionnalité de 'seeking').
* **Fiabilité de l'Avance Automatique :** Sans la connaissance précise de la durée totale, l'enchaînement automatique vers la piste suivante à la fin d'un morceau peut être moins fiable.

## Prérequis Techniques

Pour exécuter DragoSound, assurez-vous d'avoir installé :

* **Python** (version 3.x est recommandée).
* La librairie **Pygame** (pour la lecture audio).
* La librairie **Pillow** (pour le traitement des images, notamment le logo).

Ces librairies peuvent être installées via pip en exécutant les commandes suivantes dans votre terminal ou invite de commande :

```bash
pip install pygame Pillow
