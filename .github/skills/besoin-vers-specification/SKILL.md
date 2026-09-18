---
name: besoin-vers-specification
description: >-
  Clarifier un besoin d'application ou une évolution fonctionnelle par un entretien
  de cinq questions maximum, puis rédiger des spécifications avec des critères
  d'acceptation observables. Utiliser pour cadrer une demande métier, préciser un
  périmètre ou transformer un brief en spécifications. Convient notamment aux
  ateliers de développement avec IAG. Ne pas déclencher pour une simple question
  sur les Skills ou pour coder une fonctionnalité déjà spécifiée.
---

# Du besoin aux spécifications

## Objectif

Conduire un entretien dans le chat, puis produire une spécification fonctionnelle
utilisable pour la conception, le développement et la recette. Adapter le vocabulaire
au demandeur et conserver les choix exprimés. Rester indépendant du domaine métier
et des technologies.

## Règles de l'entretien

- Poser au maximum **cinq questions au total, validation comprise**. Réserver la
  dernière question disponible à la validation de la synthèse : au plus quatre
  questions de clarification, suivies d'une question de validation.
- Poser **une seule question par message**, sur un seul point à décider. Afficher
  `Question n/5`, puis attendre la réponse avant de poursuivre.
- Compter toute nouvelle sollicitation d'information ou d'arbitrage, y compris
  une relance, une confirmation ou une demande formulée à l'impératif. Ne pas
  dissimuler plusieurs questions dans une phrase ou une liste.
- Réutiliser toutes les informations déjà fournies. Une réponse peut couvrir
  plusieurs sujets : ne pas les redemander pour suivre un questionnaire prédéfini.
- Répondre aux questions de l'utilisateur sans consommer une question si aucune
  nouvelle information ne lui est demandée.
- Accepter « je ne sais pas », une réponse partielle ou le refus de répondre.
  Consigner l'incertitude et employer les questions restantes sur les décisions
  les plus utiles.
- Conserver le compteur pendant le même cadrage, même après une correction ou une
  reprise de conversation. Ne modifier le budget que sur instruction explicite
  de l'utilisateur.
- Si l'utilisateur demande de rédiger immédiatement ou d'arrêter les questions,
  passer directement à la rédaction avec les éléments disponibles.

## 1. Préparer la première question

Lire la demande, les échanges pertinents et les documents fournis ou explicitement
désignés. Si une pièce est inaccessible, le signaler sans lui attribuer un contenu.
Éviter une exploration générale du projet ou du système d'information.

Repérer en interne :

| Sujet | Informations utiles |
| --- | --- |
| Finalité | Problème à résoudre et résultat métier attendu |
| Utilisateurs | Utilisateurs cibles et action ou décision à faciliter |
| Périmètre | Parcours principal, fonctionnalités indispensables et exclusions explicites |
| Données | Entrées, provenance, formats, sorties et règles métier |
| Contraintes | Contraintes exprimées d'usage, d'intégration, de délai ou de qualité |
| Acceptation | Comportements permettant de déclarer une fonctionnalité conforme |

Utiliser cette grille pour choisir les questions, sans la transformer en formulaire
à remplir intégralement. Repérer d'abord les contradictions susceptibles de changer
le périmètre.

Annoncer brièvement : « Je vais préciser le besoin avec vous, en cinq questions
maximum, validation comprise, puis rédiger les spécifications. » Poser directement
la première question utile. Si le besoin est déjà suffisamment décrit, passer à
la synthèse sans consommer artificiellement les quatre questions de clarification.

## 2. Choisir les questions

Après chaque réponse, actualiser les décisions et les inconnues. Choisir la question
dont la réponse modifierait le plus le périmètre, le parcours principal ou la recette.
Privilégier une contradiction importante, puis la finalité et le parcours, puis les
données ou règles métier qui conditionnent ce parcours.

Formuler une question concrète. Si cela aide, proposer deux ou trois réponses
possibles en précisant qu'une réponse libre convient. Présenter ces options comme
des propositions, jamais comme des choix déjà retenus.

Exemples de questions à sélectionner selon le contexte :

- « Quelle décision l'utilisateur doit-il pouvoir prendre grâce à l'application ? »
- « Quel parcours doit absolument fonctionner dans la première version ? »
- « Quelle source de données sera utilisée pour ce parcours ? »
- « Quel comportement attendez-vous lorsqu'une donnée obligatoire manque ? »

Ne pas imposer un langage, une architecture ou un modèle de données à ce stade.
Enregistrer les contraintes techniques déjà choisies par l'utilisateur.

Pour une application prédictive, repérer l'événement à prédire, son horizon, les
données disponibles au moment de la prédiction et l'usage du résultat. Consacrer une
question à une ambiguïté déterminante ou l'inscrire parmi les points à préciser.
Ne pas attribuer au modèle une performance, un seuil ou une interprétation
probabiliste qui n'ont pas été établis.

## 3. Clore l'entretien

Passer à la synthèse dès que le parcours principal est compréhensible, après la
quatrième réponse de clarification, ou à la demande de l'utilisateur.

Présenter une synthèse courte avec :

- l'objectif et l'utilisateur cible ;
- le parcours et les fonctionnalités retenus ;
- les données et contraintes connues ;
- les propositions éventuelles et les points non résolus.

Si l'utilisateur n'a pas déjà demandé la rédaction et qu'une question reste
disponible, poser la question de clôture, numérotée avec le compteur courant :

> Validez-vous cette synthèse pour passer à la rédaction des spécifications ?

Attendre sa réponse. Ne pas ajouter une autre question de clôture.

- En cas d'accord, rédiger les spécifications.
- En cas de corrections, les intégrer. Si elles suffisent pour rédiger, produire
  le document ; sinon, utiliser uniquement le budget restant. À budget épuisé,
  rédiger un brouillon qui rend visibles les ambiguïtés restantes.
- En cas de refus explicite de poursuivre, s'arrêter et conserver la synthèse.
- Sans réponse, laisser la synthèse en attente ; ne pas assimiler le silence à un accord.

Après la cinquième question, ne plus solliciter d'information ni de validation.
Les compléments spontanés de l'utilisateur restent utilisables. Une validation
du périmètre ne vaut ni preuve de faisabilité ni mesure de performance.

## 4. Rédiger les spécifications

Rédiger en français, sauf demande contraire, et adapter la longueur au projet.
Respecter le format demandé ou le document existant. À défaut, utiliser cette structure :

### Objectif et périmètre

Décrire le problème, les utilisateurs, le résultat attendu et les limites retenues.
N'inscrire comme exclusions que celles exprimées ou validées ; laisser le reste
non spécifié. Indiquer le statut : `brouillon`, `périmètre validé` ou `révisé après
corrections`, selon l'échange réellement observé.

### Parcours utilisateur

Décrire le parcours principal dans l'ordre : point de départ, actions de l'utilisateur,
réponses de l'application et résultat final. Ajouter les variantes qui changent
réellement le comportement attendu.

### Exigences et critères d'acceptation

Attribuer un identifiant stable à chaque exigence : `F-01`, `F-02`, etc. Pour chacune,
préciser le comportement, les règles métier nécessaires et les critères de recette.
Utiliser des user stories si elles rendent l'usage plus clair.

Rédiger les critères sous une forme observable : situation initiale, action,
résultat attendu. Couvrir le cas nominal et les erreurs pertinentes pour le besoin.
Remplacer les adjectifs vagues tels que « rapide » ou « intuitif » par un comportement
vérifiable ; si une mesure manque, la signaler sans inventer de valeur.

Distinguer les exigences retenues, les propositions de l'agent et les décisions
restant à prendre. Un critère qui introduit un nouveau choix fonctionnel reste une
proposition tant que ce choix n'a pas été accepté.

Exemple, uniquement si le rejet des fichiers incomplets a été choisi :

> F-02 — Vérifier les colonnes obligatoires.
> Étant donné un fichier auquel manque une colonne obligatoire définie dans le
> contrat d'entrée, lorsque l'utilisateur lance l'import, alors l'import est refusé
> et le nom de la colonne manquante est affiché.

### Données et contraintes

Décrire les entrées, les sorties et les règles connues de validation ou de calcul.
Reprendre les contraintes explicitement exprimées. Distinguer les données observées
dans un fichier des règles métier confirmées par l'utilisateur. Ne pas ajouter
automatiquement une authentification, une API, un hébergement ou un dispositif MLOps.

### Points à préciser

Pour chaque information manquante ou contradiction, préciser son impact et la partie
du travail qu'elle empêche éventuellement de finaliser. Présenter ces points comme
un registre d'incertitudes, sans relancer un questionnaire. N'attribuer un responsable
ou une échéance que s'ils sont connus.

## 5. Vérifier et livrer

Avant la livraison, vérifier que :

- le compteur n'a pas dépassé cinq questions, sauf changement explicite du budget ;
- les choix et corrections de l'utilisateur sont conservés ;
- les propositions, les décisions et les inconnues sont distinguées ;
- chaque fonctionnalité retenue possède un critère observable, ou indique ce qui
  manque pour pouvoir le définir ;
- les critères décrivent la conformité fonctionnelle, sans prétendre que des tests
  ont été exécutés ou que les performances ont été mesurées ;
- le document n'introduit pas de décisions métier ou techniques non exprimées.

Dans un environnement permettant de créer des fichiers, enregistrer le document à
l'emplacement demandé. Dans un projet ouvert, utiliser à défaut `specifications.md`
à la racine. Lire un document existant avant de le mettre à jour et préserver les
éléments qui ne sont pas concernés par la demande. Dans un chat sans accès aux
fichiers, fournir le document complet dans la réponse.

Terminer en indiquant le document produit et les principales décisions restant à
prendre. S'arrêter à la spécification ; engager la conception ou le développement
lorsque l'utilisateur le demande.
