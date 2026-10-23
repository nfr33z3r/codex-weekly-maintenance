# Codex Weekly Maintenance

Orchestrateur de maintenance **hebdomadaire** assistée de dépôts GitHub. Génère des rapports et des prompts par dépôt pour Codex Cloud, avec notification push iPhone via ntfy. Aucun usage de l'API OpenAI payante.

**État : cadrage uniquement, aucune automatisation déployée.**

- [Plan d'implémentation](docs/IMPLEMENTATION-PLAN.md)
- [Règles pour Codex](AGENTS.md)
- [Blueprint source dans Synaptic — PR #1](https://github.com/Zero-Limit-Agency/Synaptic/pull/1)

**À noter :** la lecture automatique sûre du quota hebdomadaire Codex n'est pas résolue. Tant que celle-ci n'est pas démontrée, le système doit fonctionner en mode assisté et ne jamais inventer une date ou un pourcentage.
