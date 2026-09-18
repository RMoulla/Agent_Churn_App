# Agent_Churn_App

## Objectif

Application pédagogique d'aide au rappel commercial : aide les commerciaux à
**prioriser leurs rappels de prévention** à partir d'un score de risque de
churn (résiliation), calculé par une régression logistique entraînée sur
[customer_churn.csv](customer_churn.csv). Le score est une **estimation
pédagogique** : il ne constitue ni une probabilité calibrée, ni une garantie
de résiliation, et n'a pas d'horizon temporel documenté.

Voir [specifications.md](specifications.md) pour les spécifications
fonctionnelles complètes et [AGENTS.md](AGENTS.md) pour le plan de
réalisation et les règles impératives (graine fixe, seuil fixe, 5 variables
prédictives, pas de fuite de cible, etc.).

## Architecture

```
config.py          # constantes uniques : 5 variables, seuil 0.5, graine 42, chemins
train_model.py      # entraîne la pipeline (prétraitement + régression logistique)
evaluate_model.py   # évalue sur le jeu de test, génère reports/evaluation_report.md
validation.py        # validation partagée entre le formulaire et l'import CSV
scoring.py           # chargement de la pipeline (jamais ré-entraînée) et calcul du score/alerte
app.py               # application Flask : formulaire, import CSV, résultats, export
templates/, static/  # vues (français) et feuille de style de l'interface
model/               # pipeline entraînée (pipeline.joblib) et indices du split (générés)
reports/             # rapport d'évaluation et rapport de tests (générés)
tests/               # tests pytest (modèle + interface Flask)
customer_churn.csv   # données historiques, en lecture seule, jamais modifiées
```

Le modèle est entraîné **hors ligne** par `train_model.py` puis chargé tel
quel par l'interface (`scoring.load_pipeline`) : il n'est **jamais
ré-entraîné** au démarrage de l'application ni à l'import d'un fichier.

## Installation

Testé avec **Python 3.14.2**. Les versions de `requirements.txt` sont figées
sur des distributions binaires (wheels) compatibles avec cette version ;
n'imposez pas d'anciennes versions sans wheel disponible, sous peine de
déclencher une compilation depuis les sources.

```bash
python3 -m venv .venv
source .venv/bin/activate          # active le venv (à refaire à chaque nouvelle session shell)
pip install -r requirements.txt -r requirements-dev.txt
```

Sans activation du venv, utilisez les exécutables du venv explicitement,
par exemple `.venv/bin/python` plutôt que `python` (voir plus bas).

## Entraîner et évaluer le modèle

```bash
source .venv/bin/activate
python train_model.py      # entraîne la pipeline, la sauvegarde dans model/
python evaluate_model.py   # évalue sur le jeu de test, génère reports/evaluation_report.md
```

Résultats mesurés sur le jeu de test (180 clients, jamais vus à
l'entraînement) — détail complet dans
[reports/evaluation_report.md](reports/evaluation_report.md) :

| Métrique | Modèle | Baseline « toujours non-churn » |
| --- | --- | --- |
| Exactitude | 0,906 | 0,833 |
| Précision (churn) | 0,810 | 0,000 |
| Rappel (churn) | 0,567 | 0,000 |
| F1 (churn) | 0,667 | 0,000 |
| ROC-AUC | 0,913 | — |

Sur 30 résiliations réelles dans le jeu de test, le modèle en détecte 17,
en manque 13, et déclenche 4 fausses alertes. Le modèle reste nettement
supérieur à la baseline, mais **rate plus d'un tiers des résiliations
réelles** de ce jeu de test : ce n'est pas un outil de détection exhaustive,
seulement une aide à la priorisation.

## Lancer l'interface web

Un modèle entraîné (`model/pipeline.joblib`) doit exister au préalable.

```bash
source .venv/bin/activate
python app.py
```

Si le venv n'est pas activé (ou pour éviter toute ambiguïté avec un autre
interpréteur Python du système), utilisez explicitement l'interpréteur du
venv, sans activation préalable :

```bash
.venv/bin/python app.py
```

Puis ouvrir http://127.0.0.1:5000/ dans un navigateur.

### Parcours 1 — Client unique

Sur la page d'accueil, saisir `Age`, `Total_Purchase`, `Account_Manager`
(0 ou 1), `Years`, `Num_Sites`, puis cliquer sur « Calculer le score ».
Exemple : `Age=42`, `Total_Purchase=11066.8`, `Account_Manager=0`,
`Years=7.22`, `Num_Sites=8` → score affiché en %, avec l'alerte « Risque
faible » ou « Risque élevé » selon le seuil (0,5).

### Parcours 2 — Import CSV

Sur `/import`, déposer un fichier CSV contenant au moins les 5 colonnes
`Age`, `Total_Purchase`, `Account_Manager`, `Years`, `Num_Sites` (et
optionnellement `Names`, `Company`). Exemple minimal :

```csv
Names,Company,Age,Total_Purchase,Account_Manager,Years,Num_Sites
Alice Martin,Harvey LLC,42,11066.8,0,7.22,8
Bob Martin,Miller LLC,38,12884.75,0,6.67,12
```

La liste des clients scorés s'affiche triée par risque décroissant ;
sélectionner des lignes puis cliquer sur « Exporter la sélection en CSV »
télécharge un fichier avec l'identifiant, le nom/société si présents, les 5
variables, le score (0 à 1) et l'alerte.

## Tests

```bash
source .venv/bin/activate
pytest
```

Couvre la reproductibilité du split, l'absence de fuite de cible et les
colonnes exclues ([tests/test_model_pipeline.py](tests/test_model_pipeline.py)),
ainsi que les parcours de l'interface Flask via le client de test
([tests/test_app.py](tests/test_app.py)). Détail des cas et des corrections
apportées dans [reports/test_report.md](reports/test_report.md).

## Limites

- Score pédagogique, non calibré, sans horizon de prédiction documenté.
- Seuil de décision (0,5) et découpage train/test (graine 42) fixés par
  convention pédagogique, pas optimisés métier.
- Stockage des résultats d'import côté serveur en mémoire du processus
  (par jeton de session) : convient à une démonstration mono-processus, non
  persistant, non adapté à un déploiement multi-instance ou en production.
