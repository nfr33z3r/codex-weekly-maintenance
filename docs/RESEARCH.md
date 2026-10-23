# Étude des solutions

Évaluation réalisée le **23 octobre 2026** à partir des dépôts publics et de la documentation officielle. Les SHA figent l’état consulté ; les liens `blob/<sha>` permettent de reproduire la lecture.

## Résultat

| Solution | Apport pertinent | Incompatibilité avec la V1 | Décision |
|---|---|---|---|
| [Pullfrog](https://github.com/pullfrog/pullfrog/tree/82247c3a490f7a17f8672a3af207279989dc873b) | Action GitHub, credentials courts, agents Codex/Claude/OpenCode | Lance un agent et demande une authentification de fournisseur ou une clé ; vise revue/autofix et peut écrire | Non retenu ; utile si une future V2 autorise un agent CI |
| [Everything Claude Code / ECC](https://github.com/affaan-m/ECC/tree/90606c8315ee09cafc303515c5f33024db6b9882) | Discipline plan-test-review, skills de maintenance et sécurité | Très large ensemble d’agents, skills, hooks et adaptateurs ; majoritairement conçu comme harness interactif | Ne pas installer ; reprendre seulement les principes de vérification |
| [Find Skills / skills](https://github.com/vercel-labs/skills/tree/a80e4c9d12d607631249d4d7d059f835d4b2f13a) | Découverte/installation de `SKILL.md`, compatible Codex | Ne collecte ni ne priorise l’activité GitHub ; Node 22.20+ et télémétrie/audit réseau par défaut documentés | Hors chemin d’exécution ; aucun skill requis pour la V1 |
| [Understand Anything](https://github.com/egonex-ai/understand-anything/tree/e24fcf6d371bcfa529bc110bacb1bb43de1b8d33) | Graphe de code et analyse incrémentale | Première analyse consommatrice de tokens, pipeline multi-agent, clone/analyse complète du code | Non retenu ; la V1 n’a besoin que de métadonnées récentes |
| [Strix](https://github.com/usestrix/strix/tree/14cc948c36e90517a774cf32bdfe5d8cd3605b62) | Pentest spécialisé et validation dynamique | Docker, clé LLM ou service cloud, exécution offensive et périmètre bien plus large | Non retenu ; réserver à un audit sécurité explicitement autorisé |
| GitHub Actions + API REST | Exécution hébergée, déclenchement manuel, permissions, secrets, artefacts, API des commits/PR/runs | Le `GITHUB_TOKEN` du workflow ne donne pas accès aux autres dépôts privés | **Socle retenu**, complété par un PAT finement limité en lecture |
| Codex Cloud officiel | Tâche manuelle dans le dépôt, instructions `AGENTS.md`, abonnement ChatGPT séparé de l’API | Pas de méthode sûre validée ici pour lire le quota ou lancer automatiquement via une session ChatGPT | **Exécution manuelle retenue**, hors du workflow |

## Pourquoi aucun framework agentique

Le besoin automatisable est une collecte structurée, pas une compréhension sémantique complète. Un script de bibliothèque standard est plus petit, auditable et prévisible. Il évite quatre risques communs aux solutions plus lourdes : consommation de tokens, secret d’agent dans CI, exécution de code non fiable et capacité d’écriture sur les dépôts métiers.

Les composants réutilisés sont donc des conventions, pas des runtimes : `AGENTS.md`, prompts versionnés, vérification par tests, citations GitHub, permissions minimales et séparation collecte/exécution.

## Solutions officielles GitHub

- [Déclenchement manuel `workflow_dispatch`](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#workflow_dispatch).
- [Permissions du `GITHUB_TOKEN`](https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication) : limité au dépôt du workflow, donc insuffisant pour plusieurs dépôts privés.
- [Fine-grained personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) : sélection explicite des dépôts et permissions.
- [Authentification avec une GitHub App](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app-installation) : option plus robuste à jeton court mais plus complexe.
- [API REST commits](https://docs.github.com/en/rest/commits/commits), [pull requests](https://docs.github.com/en/rest/pulls/pulls) et [workflow runs](https://docs.github.com/en/rest/actions/workflow-runs).
- [Sécurisation des GitHub Actions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions) : les actions sont épinglées par SHA complet.
- [Stockage et rétention des artefacts](https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts).

Actions officielles épinglées lors de l’étude :

- [`actions/checkout@3d3c42e5…` (v7.0.1)](https://github.com/actions/checkout/tree/3d3c42e5aac5ba805825da76410c181273ba90b1) ;
- [`actions/upload-artifact@cf430e03…` (v7.0.2)](https://github.com/actions/upload-artifact/tree/cf430e030ddbb5b0abf93d22962f4752f3646cd9).

## Solution officielle Codex

- [Codex Cloud](https://developers.openai.com/codex/cloud) est l’environnement cible pour l’exécution manuelle.
- [Codex dans ChatGPT](https://help.openai.com/en/articles/11369540-codex-in-chatgpt) décrit l’accès via les offres ChatGPT ; cela ne transforme pas l’abonnement en API automatisable.
- [Dépôt officiel Codex](https://github.com/openai/codex/tree/2839ed763bd3f404398e1f0c95bf4e2d172213c0) : connexion ChatGPT possible dans les clients officiels, mais aucune authentification utilisateur n’est exportée vers GitHub Actions dans cette architecture.
- [Guide `AGENTS.md`](https://developers.openai.com/codex/guides/agents-md) : les prompts demandent systématiquement de lire les instructions propres au dépôt métier.

Conclusion : GitHub prépare des preuves privées ; l’utilisateur choisit et lance ensuite chaque tâche dans Codex Cloud. Cette frontière est intentionnelle.

## ntfy

La publication utilise l’API HTTP simple de [ntfy](https://docs.ntfy.sh/publish/). Le sujet est un secret à forte entropie ou un sujet protégé par jeton. Le message n’inclut aucun nom de dépôt, commit, PR ou diff ; son lien ouvre seulement l’exécution privée GitHub, qui exige l’authentification GitHub de l’utilisateur.
