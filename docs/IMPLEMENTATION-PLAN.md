# Plan de mise en œuvre autonome

## Décision V1.2

La V1.2 est un orchestrateur passif hébergé dans GitHub Actions. Elle appelle uniquement l’API REST GitHub avec l’identifiant en lecture seule explicitement associé au propriétaire, applique des scores déterministes d’activité et de risque, construit un résumé mobile et un paquet Markdown/JSON privés, puis envoie une notification ntfy générique seulement si une tâche est justifiée.

```text
workflow_dispatch
  ├─ tests sans secrets
  ├─ allow-list propriétaire A → identifiant github_1
  ├─ allow-list propriétaire B → identifiant github_2
  ├─ API GitHub (métadonnées seulement, fenêtre de 7 jours, aucun repli)
  ├─ activité et risque séparés + contexte CI + dépendances regroupées
  ├─ carte courte et prompt copiable par dépôt, maximum 500 Kio
  ├─ artefact privé, rétention 7 jours
  └─ ntfy : compteur générique + lien vers l’exécution privée

iPhone (app GitHub ou Safari)
  ├─ ouvre le résumé privé et copie chaque prompt
  ├─ lance manuellement une tâche Codex Cloud dans le dépôt concerné
  └─ utilise le ZIP uniquement comme solution de secours
```

Ce choix ne nécessite ni LLM dans CI, ni API OpenAI, ni PC allumé, ni secret ChatGPT. Le code d’un dépôt surveillé n’est jamais cloné ni exécuté.

## Collecte et bornes

Pour chaque entrée explicitement activée dans `config/repositories.json` :

1. récupérer la branche par défaut ;
2. récupérer au plus 25 commits de la fenêtre exacte de 7 jours ;
3. récupérer les détails de ces commits uniquement pour les noms de fichiers ;
4. récupérer au plus 50 PR triées par mise à jour et conserver celles de la fenêtre ;
5. récupérer au plus 100 exécutions Actions créées depuis le début de la fenêtre ;
6. nettoyer et borner les chaînes distantes avant rendu ;
7. signaler explicitement toute troncature.

Un dépôt sans commit, PR mise à jour ni CI en échec est ignoré pour éviter un prompt et une consommation Codex sans signal concret.

Les scores sont des heuristiques reproductibles, pas un jugement IA. L’activité mesure le volume borné de commits, PR et signaux CI. Le risque utilise les mots-clés de sécurité ou de bug et le contexte des échecs CI. Un échec rattaché à une PR Dependabot n’est pas assimilé à un incident de production ; un succès et un échec du même workflow sur la même branche ou PR sont signalés comme potentiellement intermittents.

## Sorties

Le paquet `reports/` contient :

- `index.md` et `manifest.json` ;
- `summary.md`, copie exacte du résumé mobile publié dans `GITHUB_STEP_SUMMARY` ;
- pour chaque dépôt, `report.md`, `prompt.md` et `activity.json` ;
- une mention explicite que le quota Codex est inconnu ;
- des références GitHub vérifiables, sans contenu de diff.

Les prompts sont publiés par priorité décroissante. Leur liste de sources omet les CI réussies redondantes et regroupe les PR de dépendances ; le rapport d’archive conserve les métadonnées complètes. Le résumé est borné à 500 Kio ; les prompts de moindre priorité qui ne tiennent pas sont signalés comme omis et restent disponibles dans le ZIP.

Les métadonnées GitHub sont délimitées comme données non fiables. Les caractères Markdown/HTML dangereux et les URL non canoniques sont neutralisés. Le prompt ordonne à Codex de confirmer chaque signal, de ne suivre aucune instruction provenant des titres/messages/noms de fichiers et de ne modifier que le dépôt choisi.

## Authentification retenue

V1.1 : deux fine-grained personal access tokens distincts, `github_1` et `github_2`. Chaque alias est assigné à un seul propriétaire dans `owner_credentials`. Chaque dépôt utilise exclusivement l’alias de son propriétaire. Une association absente ou dupliquée, un secret manquant, deux secrets identiques ou un refus API arrête l’exécution ; aucun autre identifiant n’est essayé.

Alternative renforcée : GitHub App privée avec jetons d’installation courts. Elle réduit la durée d’exposition mais exige une génération de JWT, la gestion d’une clé privée et davantage de code/dépendances. Elle devient préférable pour une organisation, de nombreux dépôts ou une rotation stricte. Voir `docs/SECURITY.md`.

## État

- [x] configuration allow-list stricte ;
- [x] client GitHub sans dépendance ;
- [x] collecte bornée sur 7 jours ;
- [x] score déterministe ;
- [x] rapport et prompt par dépôt ;
- [x] protection explicite contre l’injection indirecte ;
- [x] notification ntfy générique et mode de test ;
- [x] workflow manuel et actions épinglées par SHA ;
- [x] tests unitaires sans secrets ;
- [x] identifiants distincts pour deux propriétaires, sélection stricte et échec fermé ;
- [x] résumé mobile privé, borné et copiable ;
- [x] ZIP conservé comme solution de secours ;
- [x] tests de confidentialité, permissions de fichiers et données distantes non fiables ;
- [x] cartes iPhone, lien Codex générique et sélection manuelle explicite du dépôt ;
- [x] activité et risque séparés, dépendances regroupées et CI contextualisée ;
- [x] notification d’analyse supprimée quand aucune tâche n’est produite ;
- [x] configuration de planification versionnée mais désactivée ;
- [ ] validation réelle par l’utilisateur avec ses dépôts et secrets ;
- [ ] planification éventuelle, seulement après validation manuelle ;
- [ ] lecture automatique du quota, seulement si une source officielle sûre apparaît.

## Critères avant une V2

- confirmer que le dépôt orchestrateur reste privé ;
- observer le coût en appels API et ajuster les plafonds si nécessaire ;
- envisager une GitHub App si le PAT devient difficile à gouverner ;
- mesurer l’ergonomie du résumé mobile avant d’envisager une autre vue ;
- ne jamais automatiser l’exécution Codex avec un cookie/session ChatGPT.

## Planification préparée, non activée

`config/schedule.json` conserve `enabled: false` et `cron_utc: null`. Il sert de garde-fou et de trace de décision ; le workflow reste exclusivement `workflow_dispatch`. Une activation ultérieure devra passer par une PR dédiée qui :

1. recueille l’horaire souhaité par l’utilisateur et le convertit explicitement en UTC ;
2. ajoute le déclencheur `schedule` au workflow de la branche par défaut ;
3. conserve le mode manuel et les mêmes permissions en lecture seule ;
4. vérifie le comportement GitHub documenté, notamment les retards possibles des exécutions planifiées ;
5. valide sur iPhone le parcours complet avant de considérer l’automatisation active.
