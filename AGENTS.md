# Codex Weekly Maintenance — instructions agents

Le cahier des charges de référence est dans le dépôt privé `Zero-Limit-Agency/Synaptic`, fichier `blueprints/CODEX-WEEKLY-MAINTENANCE.md` (PR #1 tant que non fusionnée). Lire aussi `AGENTS.md` du dépôt Synaptic si accessible.

## Mission
Préparer une maintenance **hebdomadaire** assistée de plusieurs repos GitHub privés, sans API OpenAI payante ni PC allumé. GitHub Actions collecte les changements et génère des rapports + prompts distincts par repo ; ntfy notifie sur iPhone. L'utilisateur lance **manuellement** les prompts dans Codex Cloud sur le repo correspondant.

## Invariants
- Aucun accès aux sessions/cookies ChatGPT ni export de jetons d'authentification.
- Un quota Codex non consultable de façon sûre = **inconnu**. Ne pas inventer de % ou date de reset.
- GitHub Actions n'appelle aucun LLM payant et n'exécute aucun code provenant d'une PR externe.
- Repos surveillés explicitement autorisés, accès lecture seule et permissions minimales.
- Rapports et prompts privés ; notification publique ntfy sans nom de repo, diff ou information sensible.
- Pas de changements dans les repos métiers, pas de déploiement ou fusion automatique.
- Limiter la maintenance proposée à sécurité, bugs, tests, dépendances et refactoring préservant le comportement.
- Épingler les GitHub Actions tierces par SHA ou utiliser des commandes simples auditées.
- Pour les choix non résolus, documenter le compromis et une alternative sûre. Ne pas revendiquer une automatisation du quota non démontrée.

## Livraison
Commencer par des tests, un workflow `workflow_dispatch` sécurisé et une notification synthétique de test ; n'activer la planification qu'après validation de la configuration. Fournir PR, preuves des tests, prérequis utilisateur et limites.
