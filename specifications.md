# Spécifications — Application d'aide au rappel commercial (score de risque de churn)

**Statut** : périmètre validé (entretien de cadrage du 2026-09-18).

## Objectif et périmètre

L'application aide les commerciaux à **prioriser leurs rappels de prévention** en
attribuant à chaque client un score de risque de churn. Le score est une estimation
pédagogique produite par un modèle de démonstration : il ne constitue ni une
probabilité calibrée, ni une certitude de résiliation. Aucun horizon temporel de
prédiction n'est documenté par les données source ; l'application ne doit donc pas
en présenter un.

Utilisateurs cibles : les **commerciaux**, qui consultent les scores et choisissent
qui rappeler. Un analyste entraîne le modèle séparément, en amont, hors de
l'interface.

Le fichier `customer_churn.csv` est un historique étiqueté (colonne `Churn`) utilisé
pour l'**entraînement** et l'**évaluation** du modèle (jeu de test séparé, 20 %). Il
peut aussi être chargé dans l'interface à titre de **démonstration** du parcours
d'import ; dans ce cas, la colonne `Churn` n'est pas utilisée pour le scoring et les
scores affichés ne doivent pas être présentés comme une nouvelle mesure de
performance du modèle.

Technologie retenue : interface web **Flask**, en français.

Hors périmètre (non demandé) : authentification, API externe, hébergement, gestion
des coordonnées de contact (téléphone/email), dispositif MLOps, ré-entraînement
automatique du modèle depuis l'interface.

## Parcours utilisateur

### Parcours 1 — Scorer un client via un formulaire

1. Le commercial saisit les 5 variables du client : `Age`, `Total_Purchase`,
   `Account_Manager`, `Years`, `Num_Sites`.
2. L'application valide les valeurs saisies (mêmes règles que pour l'import, voir
   F-04).
3. L'application calcule le score à l'aide de la pipeline de modèle pré-entraînée
   et l'affiche en pourcentage, avec le seuil de décision (0,5) rappelé à l'écran.
4. L'application affiche une alerte **Risque élevé** (score ≥ 0,5) ou **Risque
   faible** (score < 0,5).

### Parcours 2 — Scorer une liste de clients via un fichier CSV

1. Le commercial importe un fichier CSV contenant, pour chaque ligne, au minimum
   les 5 variables du modèle, et éventuellement `Names` et `Company`.
2. L'application valide le fichier (voir F-04). En cas de rejet, elle affiche un
   message d'erreur identifiant la colonne en cause et, si possible, la ligne.
3. Pour chaque ligne valide, l'application calcule le score, attribue un
   identifiant de ligne stable, et affiche la liste triée par score décroissant,
   avec l'alerte Risque faible/élevé pour chaque client.
4. Le commercial sélectionne un ou plusieurs clients dans la liste.
5. Le commercial exporte la sélection dans un fichier CSV contenant : l'identifiant
   stable, `Names` et `Company` (si présents dans le fichier importé), les 5
   variables, le score (entre 0 et 1) et l'alerte.

## Exigences et critères d'acceptation

**F-01 — Scorer un client saisi manuellement.**
Étant donné un formulaire avec les 5 variables renseignées et valides, lorsque le
commercial lance le calcul, alors l'application affiche le score en pourcentage et
le seuil de décision (0,5).

**F-02 — Afficher l'alerte de risque.**
Étant donné un score calculé, lorsque le score est ≥ 0,5, alors l'application
affiche l'alerte « Risque élevé » ; lorsque le score est < 0,5, alors elle affiche
l'alerte « Risque faible ». Le libellé rappelle qu'il s'agit d'une convention
pédagogique, pas d'un seuil métier optimisé.

**F-03 — Importer un fichier CSV de clients.**
Étant donné un fichier CSV valide contenant au moins les 5 variables du modèle,
lorsque le commercial l'importe, alors l'application calcule un score et une alerte
pour chaque ligne et affiche la liste correspondante.

**F-04 — Valider les données en entrée (formulaire et import).**
Étant donné un fichier ou une saisie soumis, lorsque l'application les contrôle,
alors elle rejette et signale par un message en français, identifiant la colonne
concernée et, pour un fichier, la ligne concernée si elle est identifiable :
- un fichier vide ;
- une colonne obligatoire absente ;
- une valeur manquante, non numérique ou non finie ;
- `Account_Manager` en dehors de {0, 1} ;
- `Age` ou `Num_Sites` non entier ou négatif ;
- `Total_Purchase` ou `Years` négatif.

**F-05 — Trier la liste par score décroissant.**
Étant donné une liste de clients scorés, lorsqu'elle s'affiche, alors les clients
sont classés du score le plus élevé au plus faible, permettant une priorisation
même sous le seuil de 0,5.

**F-06 — Sélectionner et exporter une liste de clients.**
Étant donné une liste de clients scorés affichée, lorsque le commercial sélectionne
des clients puis demande l'export, alors l'application génère un fichier CSV limité
aux lignes sélectionnées, contenant : identifiant de ligne stable, `Names` et
`Company` (si présents dans le fichier importé), les 5 variables, le score (entre 0
et 1) et l'alerte.

**F-07 — Identifier chaque client de façon stable après tri/sélection.**
Étant donné un fichier importé, lorsque les scores sont calculés, alors chaque ligne
reçoit un identifiant unique conservé lors du tri, de la sélection et de l'export,
indépendamment des doublons possibles de `Names`.

**F-08 — Charger une pipeline de modèle pré-entraînée.**
Étant donné une pipeline de modèle sauvegardée, lorsque l'interface démarre ou
traite une demande de score, alors elle charge cette pipeline sans la
ré-entraîner.

**F-09 — Entraîner et évaluer le modèle (hors interface).**
Étant donné `customer_churn.csv`, lorsque l'entraînement est lancé, alors :
- le jeu est séparé en 80 % apprentissage / 20 % test, de façon mélangée et
  stratifiée sur `Churn`, avec une graine aléatoire fixe ;
- un modèle de régression logistique est entraîné sur les 5 variables prescrites ;
- tout prétraitement (mise à l'échelle, encodage, etc.) est appris uniquement sur
  le jeu d'apprentissage ;
- la pipeline entraînée (prétraitement + modèle) est sauvegardée pour être chargée
  par l'interface.

**F-10 — Rapporter les performances mesurées sur le jeu de test.**
Étant donné le modèle entraîné et le jeu de test séparé, lorsque l'évaluation est
exécutée, alors un rapport au format Markdown est produit, contenant : la matrice
de confusion, l'exactitude (accuracy), la précision, le rappel et le F1-score pour
la classe churn (1), l'aire sous la courbe ROC (ROC-AUC), une explication en
effectifs (nombre de résiliations détectées, manquées, et de fausses alertes), et
une comparaison à un modèle de référence qui prédirait systématiquement
« non-churn ». Le rapport ne doit présenter que des valeurs réellement mesurées.

**F-11 — Démonstration d'import avec le fichier historique.**
Étant donné que le commercial importe `customer_churn.csv` via le parcours 2,
lorsque l'application traite le fichier, alors elle ignore la colonne `Churn` pour
le calcul des scores et affiche un avertissement indiquant que ce chargement est
une démonstration du parcours d'import, distincte de l'évaluation du modèle
réalisée sur le jeu de test (F-10).

## Données et contraintes

- **Entrée du modèle** (formulaire et import) : `Age`, `Total_Purchase`,
  `Account_Manager`, `Years`, `Num_Sites` — obligatoires.
- **Champs d'identification optionnels** (import uniquement) : `Names`, `Company`
  — repris s'ils sont présents, sans être obligatoires pour le scoring.
- **Sortie du score** : valeur continue entre 0 et 1 (affichée en pourcentage à
  l'écran, conservée entre 0 et 1 dans l'export).
- **Seuil de décision** : 0,5, fixe, présenté comme une convention pédagogique.
- **Fichier historique** `customer_churn.csv` : source d'entraînement et
  d'évaluation (colonne `Churn` en vérité terrain), utilisable aussi en
  démonstration d'import (F-11).
- **Modèle** : régression logistique, 5 variables prescrites, split 80/20 mélangé
  stratifié, graine fixe, prétraitement appris sur l'entraînement uniquement,
  pipeline sauvegardée et chargée par l'interface (jamais ré-entraînée à l'import).
- **Rapport de performance** : Markdown, contenu détaillé en F-10.
- **Technologie** : application web Flask, interface en français.

## Points à préciser

- Format exact de l'identifiant de ligne stable (ex. entier séquentiel ou
  identifiant généré) : à trancher lors de la conception, sans impact fonctionnel
  identifié à ce stade.
- Formulation précise des messages d'erreur (texte exact affiché pour chaque cas de
  F-04) : à définir lors de la rédaction des messages, en respectant l'exigence
  d'identifier la colonne et, si possible, la ligne.
- Emplacement et nom du fichier de rapport Markdown (F-10) et de la pipeline
  sauvegardée (F-09) : à définir lors de la conception technique.
