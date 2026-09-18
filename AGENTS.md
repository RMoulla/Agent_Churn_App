# AGENTS.md — Agent_Churn_App

Ce document consigne le plan de réalisation et les règles impératives pour ce
projet, à respecter par tout agent ou contributeur intervenant sur le code.
Référence fonctionnelle : [specifications.md](specifications.md).

## Contexte

Application pédagogique aidant les commerciaux à prioriser leurs rappels de
prévention à partir d'un score de risque de churn (régression logistique),
via une interface web Flask en français. Le score est une estimation
pédagogique, jamais une certitude ni une probabilité calibrée métier.

## Règles impératives

- **Ne jamais modifier `customer_churn.csv`** (fichier source, lecture seule).
- **Graine aléatoire fixe : `42`**, utilisée pour tout tirage aléatoire
  (split train/test, initialisation du modèle).
- **Seuil de décision fixe : `0.5`** (risque élevé si score ≥ 0,5).
- **Cinq variables prédictives, et uniquement celles-ci** :
  `Age`, `Total_Purchase`, `Account_Manager`, `Years`, `Num_Sites`.
- **Colonnes jamais utilisées comme prédicteurs** : `Names`, `Company`,
  `Onboard_date`, `Location` (identification ou métadonnées uniquement).
  `Churn` est la cible, jamais une variable d'entrée du modèle.
- **Pas de fuite de cible** : `Churn` ne doit jamais apparaître parmi les
  variables transmises au modèle pour l'entraînement ou l'inférence.
- **Prétraitement appris uniquement sur le jeu d'apprentissage** (`fit` sur
  train, `transform` sur test), jamais l'inverse.
- **Split train/test reproductible et traçable** : le découpage 80/20
  stratifié réalisé par `train_model.py` est sauvegardé (indices) et rechargé
  tel quel par `evaluate_model.py`, qui ne doit pas recalculer un nouveau
  découpage.
- Toute constante partagée (variables, seuil, graine, colonnes exclues) est
  définie **une seule fois** dans `config.py` et importée partout ailleurs.
- Pas de commit, push ou publication sans demande explicite de l'utilisateur.

## Plan de réalisation

### Étape 1 — Spécifications (terminé)
`specifications.md`.

### Étape 2 — Modèle : entraînement et évaluation (terminé)
1. `config.py` — constantes partagées (variables, cible, seuil, graine,
   colonnes exclues, chemins des artefacts).
2. `train_model.py` — charge `customer_churn.csv`, split 80/20 stratifié
   (graine 42), pipeline (prétraitement + régression logistique) entraînée
   sur le train uniquement, sauvegarde la pipeline (`model/pipeline.joblib`)
   et les indices du split (`model/split_indices.json`).
3. `evaluate_model.py` — recharge la pipeline et les indices de test,
   calcule les métriques réellement mesurées, compare à un modèle de
   référence « toujours non-churn », génère
   `reports/evaluation_report.md`.
4. `tests/` — tests pytest : reproductibilité du split, absence de fuite de
   cible, exclusion des colonnes non prédictives, cohérence des scores.
5. `requirements.txt`, `requirements-dev.txt`, `.gitignore`, `README.md`.

### Étape 3 — Interface Flask (terminé)
`validation.py`, `scoring.py`, `app.py`, `templates/`, `static/style.css` —
formulaire individuel, import CSV, tri par risque, sélection et export.
Scores d'import conservés côté serveur par jeton de session (aucune variable
globale partagée entre utilisateurs, aucun cookie volumineux). Testé
manuellement : formulaire valide/invalide, import valide (dont noms en
double), fichier vide, colonne manquante, export d'une sélection, modèle
absent.

### Étape 4 — Tests fonctionnels de l'interface (terminé)
`tests/test_app.py` (client de test Flask) : formulaire valide/invalide,
import CSV (valide avec/sans colonnes optionnelles, colonne manquante,
fichier vide, fichier à en-têtes seules, valeurs manquantes/non finies),
identifiants stables après tri et export exact d'une sélection (dont noms
en double), modèle absent, isolation des sessions et des imports successifs
(un import rejeté invalide l'ancien résultat), cohérence du score entre
formulaire et CSV, seuil appliqué sur le score non arrondi, absence de
ré-entraînement dans les routes, démonstration d'import avec
`customer_churn.csv` complet (`Churn` ignoré, avertissement affiché).
Rapport détaillé : `reports/test_report.md`.

### Étape 5 — Documentation finale (terminé)
`README.md` complet (objectif, architecture, installation compatible
Python 3.14.2, entraînement/évaluation, lancement Flask, tests, exemples,
limites). Contrôle manuel au navigateur du formulaire (voir
`reports/test_report.md`).

### Étape 6 — Mise en gestion de version (terminé)
Branche dédiée `tp-churn-app`, poussée sur `origin`, sans modification ni
fusion de `main`.

## Commandes utiles

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
python train_model.py
python evaluate_model.py
pytest
python app.py
```
