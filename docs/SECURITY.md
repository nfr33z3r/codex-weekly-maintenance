# Sécurité et confidentialité

## Frontières de confiance

- **Fiable :** code versionné de ce dépôt orchestrateur, configuration relue sur la branche principale et workflows épinglés par SHA.
- **Non fiable :** titres de PR, messages de commit, noms de fichiers, noms de workflows et toute page liée depuis un dépôt surveillé.
- **Secret :** PAT GitHub, URL de sujet ntfy et éventuel jeton ntfy.
- **Privé :** rapports, prompts, liste des dépôts et lien d’exécution GitHub.

Le workflow lit des objets API mais ne fait jamais de checkout d’un dépôt surveillé, n’exécute aucun script distant et ne passe aucune métadonnée à un LLM. Les prompts isolent les métadonnées sous une section « Données non fiables » et imposent une nouvelle vérification dans Codex Cloud.

## Secrets GitHub

| Secret | Obligatoire | Contenu | Portée minimale |
|---|---:|---|---|
| `MAINTENANCE_GITHUB_TOKEN` | pour `analyze` | Fine-grained PAT dédié | uniquement les dépôts listés ; Metadata read, Contents read, Pull requests read, Actions read |
| `NTFY_TOPIC_URL` | pour notifier | URL HTTPS complète, sujet aléatoire | publication sur un seul sujet |
| `NTFY_TOKEN` | non | jeton d’accès ntfy | droit de publication sur ce sujet uniquement |

Ne jamais stocker de token, cookie, session ou export ChatGPT. Le PAT doit avoir une expiration courte raisonnable, être renouvelé manuellement et révoqué dès qu’il n’est plus utilisé.

## PAT ou GitHub App

Le PAT finement limité est retenu pour la V1 car il est natif, simple et suffisant pour une utilisation personnelle. Son défaut est sa durée de vie et son rattachement à un compte humain.

Une GitHub App privée est préférable lorsque l’installation couvre une organisation ou de nombreux dépôts. Elle offre un jeton d’installation court et une identité distincte, mais oblige à conserver une clé privée et à signer un JWT dans Actions. Cette complexité n’est pas justifiée avant validation de la V1.

## Fuites évitées

- notification générique, sans nom de dépôt ni détails ;
- erreurs réseau sans corps de réponse ;
- aucun secret en argument de ligne de commande ;
- sorties créées avec des permissions locales restrictives ;
- artefact supprimé après 7 jours ;
- dépôt orchestrateur obligatoirement privé ;
- aucun `pull_request_target`, aucune exécution de contribution distante ;
- appels API plafonnés pour éviter coût et abus.

## Limites connues

- Un administrateur du dépôt GitHub peut accéder aux secrets et artefacts selon les règles de la plateforme.
- Un sujet public ntfy est accessible à qui devine son nom ; utiliser un identifiant aléatoire long et, idéalement, un jeton ACL.
- Les heuristiques par mots-clés peuvent produire des faux positifs ou faux négatifs.
- Le workflow ne lit pas les alertes Dependabot/code scanning, qui demanderaient d’autres permissions.
- Le quota hebdomadaire Codex et sa date de remise à zéro restent inconnus.
