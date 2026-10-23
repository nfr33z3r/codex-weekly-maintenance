# Codex Weekly Maintenance

Orchestrateur privé et sans LLM pour préparer chaque semaine des prompts de maintenance par dépôt. GitHub Actions lit les métadonnées des 7 derniers jours, les priorise de façon déterministe, publie un artefact privé et envoie un push ntfy générique. Chaque prompt est ensuite lancé **manuellement** dans Codex Cloud depuis l’iPhone.

La V1 n’utilise aucune API OpenAI payante, aucun secret ChatGPT, aucun PC allumé et ne modifie jamais les dépôts surveillés.

## Architecture

- Python 3, bibliothèque standard uniquement ;
- API REST GitHub, lecture seule, sans checkout des dépôts métiers ;
- allow-list dans `config/repositories.json` ;
- workflow manuel `Weekly maintenance` ;
- un rapport et un prompt par dépôt actif dans un artefact conservé 7 jours ;
- aucun prompt pour un dépôt sans commit, PR mise à jour ou CI en échec ;
- notification ntfy testable séparément ;
- quota Codex toujours affiché comme **inconnu**.

Voir [le plan](docs/IMPLEMENTATION-PLAN.md), [l’étude comparative](docs/RESEARCH.md) et [le modèle de sécurité](docs/SECURITY.md).

## Activation — actions manuelles exactes

1. Vérifier dans **Settings → General → Danger Zone** que `nfr33z3r/codex-weekly-maintenance` est **Private**. Ne pas activer tant qu’il est public.
2. Modifier `config/repositories.json` sur une branche : ajouter chaque dépôt sous la forme `owner/repo`, désactiver ou supprimer l’exemple, puis fusionner la PR après passage du workflow `Tests`.
3. Dans GitHub, créer un **fine-grained personal access token** dédié :
   - Resource owner : le compte ou l’organisation qui possède les dépôts ;
   - Repository access : **Only select repositories**, puis sélectionner exactement les dépôts configurés ;
   - Repository permissions : **Metadata: Read-only**, **Contents: Read-only**, **Pull requests: Read-only**, **Actions: Read-only** ;
   - choisir une expiration et noter une date de rotation ;
   - si plusieurs propriétaires empêchent un seul PAT de couvrir la liste, créer une GitHub App ou séparer les orchestrateurs ; ne pas élargir à tous les dépôts par commodité.
4. Dans ce dépôt, ouvrir **Settings → Secrets and variables → Actions → New repository secret** et créer `MAINTENANCE_GITHUB_TOKEN` avec ce PAT.
5. Installer l’app **ntfy** sur l’iPhone, choisir un sujet aléatoire long (au moins 128 bits d’entropie) sur un serveur de confiance, puis s’y abonner. Ne pas employer un nom descriptif.
6. Dans les secrets Actions, créer `NTFY_TOPIC_URL` avec l’URL HTTPS complète, par exemple `https://ntfy.sh/<sujet-aleatoire>`.
7. Recommandé si le serveur ntfy utilise des ACL : créer aussi `NTFY_TOKEN` avec un jeton limité à la publication sur ce sujet. Sinon laisser ce secret absent.
8. Ouvrir **Actions → Weekly maintenance → Run workflow**, choisir `notification-test`, puis **Run workflow**. Confirmer sur l’iPhone que le message ne contient aucune donnée de dépôt et que son lien exige bien l’authentification GitHub.
9. Relancer le même workflow avec `analyze` et `notify: true`. Vérifier que les tests passent, que l’artefact `weekly-maintenance-<run id>` existe et que sa rétention est de 7 jours.
10. Depuis l’iPhone, ouvrir l’exécution via la notification, télécharger l’artefact, lire `index.md`, puis pour chaque dépôt retenu :
    - ouvrir Codex Cloud avec ce dépôt ;
    - créer une nouvelle tâche ;
    - copier le contenu du fichier `<owner>/<repo>/prompt.md` ;
    - lancer la tâche et examiner sa PR avant toute fusion.
11. Laisser le workflow en déclenchement manuel. N’ajouter un `schedule` qu’après plusieurs exécutions validées et une décision explicite sur la fréquence.

## Utilisation locale

Les tests ne nécessitent ni réseau ni secret :

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Pour une collecte locale volontaire :

```bash
export MAINTENANCE_GITHUB_TOKEN='...'
PYTHONPATH=src python3 -m weekly_maintenance collect \
  --config config/repositories.json \
  --output reports
```

Pour tester ntfy localement :

```bash
export NTFY_TOPIC_URL='https://ntfy.sh/<sujet-aleatoire>'
export NTFY_TOKEN='...' # facultatif
PYTHONPATH=src python3 -m weekly_maintenance notify --test
```

## Coût et limites

Le workflow utilise les minutes GitHub Actions incluses au compte et les API GitHub/ntfy ; aucun appel de modèle n’a lieu dans CI. Le temps Codex est consommé uniquement quand l’utilisateur lance un prompt dans Codex Cloud.

La V1 n’inspecte pas le code complet, les diffs, Dependabot ou code scanning. Elle prépare une file d’attention vérifiable. Aucune méthode sûre de lecture automatique du quota Codex n’est connue dans ce projet : le quota et la date de reset restent **inconnus**.
