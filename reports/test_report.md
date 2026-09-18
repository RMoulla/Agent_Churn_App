# Rapport de tests — étape 5 (fonctionnels) et suivi étape 2 (modèle)

## Portée

29 tests pytest exécutés, tous passants :

- 7 tests dans [tests/test_model_pipeline.py](../tests/test_model_pipeline.py)
  (étape 2 : reproductibilité du split, absence de fuite de cible, colonnes
  exclues, cohérence des scores).
- 22 tests dans [tests/test_app.py](../tests/test_app.py) (étape 5 :
  parcours de l'interface Flask, via le client de test Flask).

```
29 passed in 2.70s
```

## Cas fonctionnels couverts (tests/test_app.py)

| Test | Cas | Résultat |
| --- | --- | --- |
| `test_t1_form_valid_values_returns_score_and_alert` | Formulaire valide | Score et alerte affichés — OK |
| `test_t2_form_invalid_values_returns_field_errors` | Formulaire invalide (négatif, non numérique, hors {0,1}, non entier) | Une erreur par champ fautif, aucun score — OK |
| `test_t3_import_valid_with_names_and_company` | Import CSV valide avec `Names`/`Company` | Colonnes Nom/Société affichées — OK |
| `test_t4_import_valid_without_optional_columns` | Import CSV valide sans colonnes optionnelles | Colonnes Nom/Société absentes du tableau — OK |
| `test_t5_import_missing_required_column_rejected` | Colonne obligatoire absente | Rejet, colonne identifiée — OK |
| `test_t6_import_empty_file_rejected` | Fichier totalement vide | Rejet « Le fichier est vide. » — OK |
| `test_t7_import_invalid_values_rejected_with_row_and_column` | Valeurs invalides sur une ligne | Rejet, ligne et colonnes identifiées — OK |
| `test_t8_t9_duplicate_names_stable_ids_and_exact_export` | 3 clients dont 2 homonymes, tri, sélection de 2 lignes non adjacentes | Identifiants stables après tri ; export strictement conforme (id, 5 variables, score) aux lignes sélectionnées — OK |
| `test_t10_scoring_without_model_shows_clear_error` | `model/pipeline.joblib` absent (formulaire et import) | Message clair, aucune exception non gérée — OK |
| `test_t11a_two_independent_sessions_do_not_share_results` | Deux sessions indépendantes | Aucun partage de résultats entre sessions — OK |
| `test_t11b_new_import_replaces_previous_results_in_same_session` | Deux imports successifs valides, même session | Le second import remplace entièrement le premier — OK |
| `test_t11c_rejected_import_clears_previous_results_in_same_session` | Import valide puis import rejeté, même session | L'import rejeté invalide l'ancien résultat ; `/resultats` redirige — OK |
| `test_same_values_give_same_score_via_form_and_csv` | Mêmes 5 valeurs via formulaire et via CSV | Score identique par les deux parcours — OK |
| `test_alert_threshold_uses_unrounded_score` (paramétré) | Score exactement 0,5 ; 0,5004 ; 0,4996 ; 0,4999999 (pipeline factice) | Seuil appliqué sur le score non arrondi ; l'affichage arrondi (« 50,0 % ») ne change pas la décision — OK |
| `test_form_missing_and_non_finite_values_rejected` | Champ manquant, `nan`, `inf` au formulaire | Messages distincts (« manquante » vs « nombre fini ») — OK |
| `test_import_missing_and_non_finite_values_rejected` | Cellule vide, `NaN`, `inf` dans un CSV | Mêmes messages, avec numéro de ligne — OK |
| `test_import_headers_only_treated_as_empty_file` | CSV avec uniquement l'en-tête (0 ligne de données) | Traité comme un fichier vide — OK |
| `test_full_historical_csv_import_is_a_demo_and_ignores_churn` | Import de `customer_churn.csv` complet (900 lignes) | Avertissement « démonstration » affiché, colonne `Churn` ignorée du scoring et absente des enregistrements — OK |
| `test_routes_never_call_pipeline_fit` | `LogisticRegression.fit` intercepté pour lever une erreur s'il est appelé | Formulaire et import CSV fonctionnent sans jamais appeler `fit` — OK |

## Corrections apportées pendant l'écriture des tests

- **T8/T9** : le premier découpage de test supposait à tort que les deux
  clients homonymes se retrouveraient à des rangs non adjacents après tri
  par score. Le tri réel plaçait les rangs 2 et 3 adjacents. Corrigé en
  sélectionnant dynamiquement le premier et le dernier rang du tri (toujours
  non adjacents pour 3 lignes ou plus), plutôt que de figer des identifiants
  supposés non adjacents.
- **Démonstration avec `customer_churn.csv`** (F-11) : fonctionnalité non
  encore implémentée au moment d'écrire le test. Ajout dans `app.py` d'une
  détection de la colonne `Churn` à l'import (`demo_import`), d'un
  avertissement dédié dans `templates/resultats.html`, et confirmation que
  `Churn` n'apparaît jamais dans les enregistrements scorés ni dans l'export.
- **Import rejeté n'invalidait pas un résultat précédent** : avant
  correction, un import invalide laissait dans le stockage serveur les
  résultats du dernier import valide, consultables/exportables via
  `/resultats` sans que rien ne signale qu'ils ne correspondent pas au
  fichier venant d'être rejeté. Corrigé : toute erreur d'import supprime
  désormais l'entrée de `_IMPORT_STORE` pour la session, avant même
  d'afficher le message d'erreur.

## Vérifications complémentaires

- `customer_churn.csv` non modifié (hash SHA-256 inchangé) après l'exécution
  de la suite complète, y compris le test d'intégration qui le lit en entier.
- L'import du fichier historique complet (900 lignes) est traité comme une
  **démonstration du parcours d'import**, jamais comme une nouvelle mesure
  de performance : les métriques restent celles de
  [evaluation_report.md](evaluation_report.md), calculées uniquement sur le
  jeu de test séparé.

## Contrôle manuel au navigateur

En complément des tests automatisés, un contrôle visuel a été effectué dans
un navigateur sur le formulaire (`/`) : saisie `Age=42`,
`Total_Purchase=11066.8`, `Account_Manager=0`, `Years=7.22`, `Num_Sites=8` →
score affiché **8,1 %**, alerte **Risque faible**, cohérent avec le calcul
automatisé (`test_t1_form_valid_values_returns_score_and_alert` et
`test_same_values_give_same_score_via_form_and_csv`). Le libellé du champ
`Total_Purchase` a été corrigé pour ne plus mentionner de devise (« euros »),
celle-ci n'étant pas documentée par les données source.

