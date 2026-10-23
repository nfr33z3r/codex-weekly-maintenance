# Parcours iPhone — de ntfy à Codex Cloud

Ce parcours reste volontairement manuel : GitHub Actions prépare les tâches, mais l’utilisateur choisit lui-même le dépôt dans Codex Cloud et colle le prompt. Aucun lien capable de préremplir une tâche Codex n’est supposé.

## Parcours normal

1. Ouvrir la notification ntfy « Maintenance hebdomadaire prête ».
2. S’authentifier sur GitHub si nécessaire. Le lien mène à l’exécution privée, jamais à un rapport public.
3. Ouvrir le **Summary** de l’exécution. Chaque dépôt justifiant une action possède une carte courte avec son risque, son activité et ses principales sources.
4. Déplier **Copier le prompt**, sélectionner le bloc de texte et le copier.
5. Suivre le lien générique **Ouvrir Codex Cloud**, démarrer une nouvelle tâche et sélectionner manuellement le dépôt exact affiché sur la carte.
6. Coller le prompt, vérifier une dernière fois le nom du dépôt, puis lancer la tâche.
7. Examiner la PR produite avant toute fusion. L’orchestrateur ne modifie jamais le dépôt surveillé.

Le lien Codex est volontairement générique (`https://chatgpt.com/codex`). La documentation officielle décrit la sélection d’un dépôt et le lancement d’une tâche dans Codex Cloud, mais ce projet ne connaît aucun schéma officiel de lien iOS préremplissant à la fois dépôt et prompt.

## Solution de secours Safari et ZIP

L’app GitHub sur iOS permet de suivre l’activité et les exécutions, mais la documentation GitHub ne garantit pas une expérience identique à github.com pour l’affichage du résumé, la sélection d’un long bloc Markdown ou le téléchargement d’un artefact. Si une de ces opérations échoue dans l’app :

1. ouvrir le lien de l’exécution dans Safari ;
2. se connecter au compte autorisé à lire le dépôt orchestrateur privé ;
3. essayer de copier le prompt depuis le **Summary** ;
4. sinon télécharger l’artefact `weekly-maintenance-<run id>` depuis la page de l’exécution ;
5. ouvrir le ZIP dans Fichiers, puis `<owner>/<repo>/prompt.md`.

Les artefacts exigent une session GitHub authentifiée et un accès en lecture au dépôt. Ils expirent ici après 7 jours. Le résumé et le ZIP contiennent des informations privées sur l’activité des dépôts : ne pas les partager hors des comptes autorisés.

## Ce qui doit être validé sur un vrai iPhone

- réception de la notification ntfy et ouverture du bon run privé ;
- accès au **Summary** dans la version installée de l’app GitHub ;
- sélection et copie intégrales d’un prompt long ;
- bascule vers Safari si le rendu ou la copie sont incomplets ;
- téléchargement, décompression et lecture du ZIP dans Fichiers ;
- ouverture de Codex Cloud, sélection manuelle du bon dépôt et collage du prompt.

Ces points dépendent des versions d’iOS, de GitHub Mobile et de l’interface web. Les tests automatisés vérifient le contenu et la taille du résumé, pas les gestes ni le presse-papiers iOS.

## Références officielles

- [GitHub Mobile](https://docs.github.com/en/get-started/using-github/github-mobile)
- [Afficher l’historique d’un workflow](https://docs.github.com/en/actions/how-tos/monitor-workflows/view-workflow-run-history)
- [Télécharger les artefacts d’un workflow](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/download-workflow-artifacts)
- [Résumés de job GitHub Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands#adding-a-job-summary)
- [Codex Cloud](https://developers.openai.com/codex/cloud)

