# Plan de mise en œuvre

**Source de référence :** [Blueprint Synaptic](https://github.com/Zero-Limit-Agency/Synaptic/blob/main/blueprints/CODEX-WEEKLY-MAINTENANCE.md) (actuellement [PR #1](https://github.com/Zero-Limit-Agency/Synaptic/pull/1) si non fusionnée).

## V1
1. Définir une liste autorisée de repos GitHub et la méthode d'authentification à lecture seule (préférer GitHub App limitée à ces repos ; vérifier les contraintes réelles).
2. Interroger les données d'activité GitHub sur une fenêtre de 7 jours : commits, PR, fichiers et signaux CI ; ignorer les dépôts sans activité significative.
3. Prioriser **sans modèle IA** et produire un rapport Markdown privé + un prompt standardisé différent par dépôt, avec références explicites aux PR/commits.
4. Ajouter une exécution GitHub Actions manuelle (`workflow_dispatch`) et des tests sans secrets.
5. Ajouter un push de test ntfy avec contenu non sensible, puis un lien authentifié vers le rapport privé.
6. Éviter les notifications en doublon, les logs sensibles et les permissions excessives.

## Condition d'automatisation
Le suivi de quota hebdomadaire et de la date de reset reste **à valider**. Tant qu'aucune source sûre sans API payante n'est démontrée, aucune alerte ne peut prétendre connaître le quota restant. Un mode assisté peut utiliser des valeurs ponctuelles saisies par l'utilisateur avec provenance et date d'expiration.

## À vérifier avant activation
- Permissions GitHub App entre compte personnel et organisation.
- Comportement des notifications ntfy sur iOS.
- Confidentialité des artefacts Actions / issues et conservation des prompts.
- Seuils de quota et stratégie de rappel.
- Aucun coût API OpenAI supplémentaire.

## Hors scope
Fusion automatique, correction directe des repos métiers, robots Codex pilotés par session ChatGPT, installation globale de skills, déploiements.
