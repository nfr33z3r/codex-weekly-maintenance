# Plan de mise en œuvre autonome

## Décision V1

La V1 est un orchestrateur passif hébergé dans GitHub Actions. Elle appelle uniquement l’API REST GitHub avec un jeton finement limité en lecture, applique un score déterministe, construit un paquet Markdown/JSON privé, puis envoie une notification ntfy générique.

```text
workflow_dispatch
  ├─ tests sans secrets
  ├─ API GitHub (métadonnées seulement, fenêtre de 7 jours)
  ├─ score déterministe + rapport + prompt par dépôt
  ├─ artefact privé, rétention 7 jours
  └─ ntfy : compteur générique + lien vers l’exécution privée

iPhone
  ├─ ouvre l’exécution GitHub et télécharge l’artefact
  └─ copie chaque prompt dans une tâche Codex Cloud du dépôt concerné
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

Le score est une heuristique reproductible, pas un jugement IA : volume borné de commits/PR, CI en échec et mots-clés de sécurité ou de bug. Il sert uniquement à ordonner l’attention humaine.

## Sorties

Le paquet `reports/` contient :

- `index.md` et `manifest.json` ;
- pour chaque dépôt, `report.md`, `prompt.md` et `activity.json` ;
- une mention explicite que le quota Codex est inconnu ;
- des références GitHub vérifiables, sans contenu de diff.

Les métadonnées GitHub sont délimitées comme données non fiables. Le prompt ordonne à Codex de confirmer chaque signal, de ne suivre aucune instruction provenant des titres/messages/noms de fichiers et de ne modifier que le dépôt choisi.

## Authentification retenue

V1 : fine-grained personal access token dédié, limité aux seuls dépôts surveillés et aux permissions de lecture nécessaires. C’est la méthode la plus simple à activer pour une personne et plusieurs dépôts privés.

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
- [ ] validation réelle par l’utilisateur avec ses dépôts et secrets ;
- [ ] planification éventuelle, seulement après validation manuelle ;
- [ ] lecture automatique du quota, seulement si une source officielle sûre apparaît.

## Critères avant une V2

- confirmer que le dépôt orchestrateur reste privé ;
- observer le coût en appels API et ajuster les plafonds si nécessaire ;
- envisager une GitHub App si le PAT devient difficile à gouverner ;
- évaluer une vue mobile plus directe uniquement si elle reste privée et sans nouvelle surface d’attaque ;
- ne jamais automatiser l’exécution Codex avec un cookie/session ChatGPT.
