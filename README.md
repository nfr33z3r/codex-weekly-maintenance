# Codex Weekly Maintenance

Orchestrateur privé et sans LLM pour préparer chaque semaine des prompts de maintenance par dépôt. GitHub Actions lit les métadonnées des 7 derniers jours, les priorise de façon déterministe, publie un artefact privé et envoie un push ntfy générique. Chaque prompt est ensuite lancé **manuellement** dans Codex Cloud depuis l’iPhone.

La V1.2 n’utilise aucune API OpenAI payante, aucun secret ChatGPT, aucun PC allumé et ne modifie jamais les dépôts surveillés.

## Architecture

- Python 3, bibliothèque standard uniquement ;
- API REST GitHub, lecture seule, sans checkout des dépôts métiers ;
- allow-list propriétaire → identifiant dans `config/repositories.json`, avec au plus deux identifiants distincts ;
- workflow manuel `Weekly maintenance` ;
- cartes courtes et prompts copiables depuis le résumé privé GitHub Actions, borné à 500 Kio ;
- un rapport et un prompt par dépôt actif dans un artefact conservé 7 jours ;
- risque et activité évalués séparément, PR de dépendances regroupées et CI contextualisée ;
- aucun prompt pour un dépôt sans commit, PR mise à jour ou CI en échec ;
- notification ntfy testable séparément et envoyée après analyse seulement si une tâche existe ;
- planification préparée mais désactivée dans `config/schedule.json` ;
- quota Codex toujours affiché comme **inconnu**.

Voir [le parcours iPhone](docs/IPHONE-GUIDE.md), [le plan](docs/IMPLEMENTATION-PLAN.md), [l’étude comparative](docs/RESEARCH.md) et [le modèle de sécurité](docs/SECURITY.md).

## Activation — actions manuelles exactes

1. Vérifier dans **Settings → General → Danger Zone** que `nfr33z3r/codex-weekly-maintenance` est **Private**. Ne pas activer tant qu’il est public.
2. Modifier `config/repositories.json` sur une branche. Associer chaque propriétaire à un alias différent, puis lister les dépôts :

   ```json
   {
     "owner_credentials": {
       "proprietaire-a": "github_1",
       "proprietaire-b": "github_2"
     },
     "repositories": [
       {"name": "proprietaire-a/depot-prive"},
       {"name": "proprietaire-b/autre-depot"}
     ]
   }
   ```

   Un propriétaire absent, un alias inconnu ou le même alias attribué à deux propriétaires arrête l’exécution.
3. Pour `proprietaire-a`, créer un **fine-grained personal access token** dédié :
   - Resource owner : uniquement `proprietaire-a` ;
   - Repository access : **Only select repositories**, puis sélectionner exactement ses dépôts configurés ;
   - Repository permissions : **Metadata: Read-only**, **Contents: Read-only**, **Pull requests: Read-only**, **Actions: Read-only** ;
   - choisir une expiration, noter la rotation et obtenir l’approbation de l’organisation si elle l’exige.
4. Répéter l’étape précédente pour `proprietaire-b` avec un **autre** PAT, dont le Resource owner et les dépôts sélectionnés appartiennent uniquement à `proprietaire-b`. Ne jamais créer un PAT global couvrant tous les dépôts.
5. Dans **Settings → Secrets and variables → Actions**, créer `MAINTENANCE_GITHUB_TOKEN_1` avec le PAT de `github_1` et `MAINTENANCE_GITHUB_TOKEN_2` avec celui de `github_2`. Supprimer l’ancien secret `MAINTENANCE_GITHUB_TOKEN` s’il existe. Un alias utilisé sans secret ou deux secrets de même valeur font échouer l’exécution.
6. Fusionner la modification de configuration après passage du workflow `Tests`.
7. Installer l’app **ntfy** sur l’iPhone, choisir un sujet aléatoire long (au moins 128 bits d’entropie) sur un serveur de confiance, puis s’y abonner. Ne pas employer un nom descriptif.
8. Dans les secrets Actions, créer `NTFY_TOPIC_URL` avec l’URL HTTPS complète, par exemple `https://ntfy.sh/<sujet-aleatoire>`.
9. Recommandé si le serveur ntfy utilise des ACL : créer aussi `NTFY_TOKEN` avec un jeton limité à la publication sur ce sujet. Sinon laisser ce secret absent.
10. Ouvrir **Actions → Weekly maintenance → Run workflow**, choisir `notification-test`, puis **Run workflow**. Confirmer sur l’iPhone que le message ne contient aucune donnée métier et que son lien exige bien l’authentification GitHub.
11. Relancer avec `analyze` et `notify: true`. Vérifier que chaque propriétaire est lu uniquement par son identifiant, que l’artefact `weekly-maintenance-<run id>` existe et que sa rétention est de 7 jours.
12. Depuis l’iPhone, suivre [le parcours iPhone](docs/IPHONE-GUIDE.md) : ouvrir l’exécution via la notification puis son **Summary**, déplier le bloc et copier le prompt. Ouvrir ensuite Codex Cloud et sélectionner manuellement le dépôt exact avant de coller le prompt.
13. Si l’app GitHub n’affiche pas correctement le résumé ou ne permet pas une copie fiable, ouvrir le run dans Safari. Si nécessaire, télécharger l’artefact ZIP, puis utiliser `<owner>/<repo>/prompt.md` dans Fichiers.
14. Examiner chaque PR produite par Codex avant toute fusion. Laisser le workflow en déclenchement manuel : aucun `schedule` ne doit encore être ajouté.

## Utilisation locale

Les tests ne nécessitent ni réseau ni secret :

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Pour une collecte locale volontaire :

```bash
export MAINTENANCE_GITHUB_TOKEN_1='...'
export MAINTENANCE_GITHUB_TOKEN_2='...'
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

La V1.2 n’inspecte pas le code complet, les diffs, les alertes Dependabot ou le code scanning. Elle reconnaît les PR du bot dans les métadonnées déjà accessibles, les regroupe et évite d’assimiler leur CI à un incident de production. Elle prépare une file d’attention vérifiable. Aucune méthode sûre de lecture automatique du quota Codex n’est connue dans ce projet : le quota et la date de reset restent **inconnus**.

Une relance manuelle identique peut produire une nouvelle notification : aucune mémoire externe ni permission d’écriture n’a été ajoutée pour dédupliquer entre deux runs. Les exécutions concurrentes sont sérialisées et un run sans tâche n’envoie pas de push.

`config/schedule.json` documente le futur choix de fréquence, mais sa modification seule n’active rien. L’activation exigera une PR séparée ajoutant un événement `schedule` au workflow avec un cron UTC explicitement approuvé ; aucun horaire arbitraire n’est fourni.
