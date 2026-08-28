---
name: project-tracker
description: Bootstrap et maintient à jour un jeu standard de fichiers markdown de suivi (README, ROADMAP, STATUS, JOURNAL, CHANGELOG, CLAUDE, DECISIONS, ERRORS, BACKLOG) pour les projets sous les périmètres définis dans ~/.claude/project-tracker/scopes.txt, gère la création de repos GitHub, et régénère PORTFOLIO.html. Utilise-le au début d'une session dans un projet de ces périmètres, après un changement significatif, ou explicitement à la demande.
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/generate_portfolio.py *)
---

# project-tracker

## Principe transversal : ne jamais deviner

Chaque fois qu'une information nécessaire (objectif du projet, stack, rationale d'une décision, contenu d'une entrée JOURNAL...) manque ou est ambiguë : **pose la question à l'utilisateur**. N'infère jamais, n'invente jamais un contenu plausible. Une section sans réponse reste marquée "à compléter", jamais remplie par supposition.

## Périmètre

Le fichier `~/.claude/project-tracker/scopes.txt` liste les racines couvertes. Le hook `SessionStart` ne s'active déjà que dans ce périmètre — mais si tu es invoqué explicitement par l'utilisateur dans un dossier hors périmètre :
1. Avertis-le : "ce dossier n'est pas dans tes périmètres de suivi automatique (`<liste des entrées de scopes.txt>`)".
2. Continue quand même normalement — n'agis jamais en refusant.
3. Propose d'ajouter un chemin à `scopes.txt` pour l'avenir : *"Je l'ajoute à tes périmètres — ce dossier précisément, ou un chemin en amont que tu préfères préciser ?"*. Si accepté, ajoute la ligne exacte demandée à `~/.claude/project-tracker/scopes.txt`. Si décliné, n'ajoute rien et continue.

## Détection de la racine d'un projet

La racine candidate est le dossier où la session a été ouverte (`cwd`). Exception : si un ancêtre de `cwd`, jusqu'à la racine du périmètre, possède déjà un `docs/project-tracker/STATUS.md`, c'est lui la racine du projet suivi (évite un faux "nouveau projet" en ouvrant une session dans un sous-dossier profond d'un projet déjà suivi).

Trois états possibles :
- **Suivi** : `docs/project-tracker/STATUS.md` présent à la racine trouvée.
  - Si son frontmatter n'a **pas du tout** la clé `reminders_list` (jamais posée — distinct d'une clé présente valant `"non"`, qui signifie déclinée) : pose la question de liaison Reminders tout de suite, avant toute autre chose, indépendamment de si un changement significatif a lieu dans cette session (voir `references/reminders-sync.md`) — cette question ne doit jamais attendre un déclenchement de "Mise à jour en continu".
  - Si son frontmatter n'a pas du tout la clé `backlog_model` : vérifie d'abord si `ROADMAP.md` mentionne/référence explicitement un fichier nommé `BACKLOG.md` (à son emplacement standard `docs/project-tracker/BACKLOG.md`, ou à un chemin non standard ailleurs dans le projet — ex. imbriqué dans un sous-dossier ; ne pose pas comme condition qu'il soit à l'emplacement standard, cherche plutôt la mention explicite) — si oui, le projet a déjà adopté le modèle sans être passé par le bootstrap de `project-tracker` : écris `backlog_model: "adopté"` directement, sans poser la question ; pour savoir s'il faut consolider ce fichier dans `docs/project-tracker/` ou le laisser où il est, voir `## Rétrofit d'un projet existant` (deux cas selon qu'un `STATUS.md` propre existe à ce chemin ou non). Sinon, pose la question d'adoption du modèle Backlog/Roadmap (voir `references/backlog-phases.md`), une fois, jamais reposée ensuite.
  - Si `backlog_model` vaut `"adopté"` (ou vient d'être auto-reconnu ci-dessus) et que le frontmatter n'a pas du tout la clé `phase_model` : vérifie si des fichiers au patron `PHASE_N_SPEC.md` existent déjà dans le projet — si oui, auto-reconnais `phase_model: "leger"` sans poser de question (même logique que ci-dessus). Sinon, ne pose **pas** de question ici : `phase_model` reste absent jusqu'à ce qu'une phase soit effectivement proposée (voir `references/backlog-phases.md`, "Mécanisme des phases").
  - Ces vérifications sont indépendantes les unes des autres — pose-les l'une après l'autre plutôt que simultanément dans le même message.
  - Puis va à "Mise à jour en continu".
- **Exclu** : le chemin absolu figure dans `~/.claude/project-tracker/trackignore.txt` (une entrée égale à une racine de périmètre n'ignore que ce dossier exact, pas les projets à l'intérieur) → ne rien faire, sauf si l'utilisateur t'en parle explicitement.
- **Nouveau/inconnu** : ni l'un ni l'autre → va à "Bootstrap d'un nouveau projet".

Quand tu es invoqué via le rappel du hook `SessionStart`, il t'indique déjà lequel de ces trois états s'applique (avec le contenu de `STATUS.md` le cas échéant) — pas besoin de re-détecter toi-même dans ce cas.

## Bootstrap d'un nouveau projet

Séquence de questions, une à la fois, jamais de supposition :

1. *"Ce dossier n'est pas encore suivi — je mets en place le suivi ?"*
   - Si non → ajoute le chemin absolu du dossier à `~/.claude/project-tracker/trackignore.txt` (crée le fichier s'il n'existe pas). Fin du flow, aucune justification demandée.
2. *"Objectif du projet en quelques mots ?"* → alimentera l'intro du README et le premier STATUS.md.
3. *"Stack technique ?"*
4. *"Pour git, on fait comment ?"* — trois options à proposer :
   - **Pas de suivi git** → saute toute la partie GitHub ci-dessous ; note ce choix dans `CLAUDE.md` (`uses_git: false`) pour ne plus jamais reposer la question ; la détection de staleness se basera sur les dates de modification de fichiers plutôt que `git log`.
   - **Créer un nouveau repo GitHub** → demande *"Quel nom pour le repo ?"* (suggestion par défaut = nom du dossier, à valider ou changer). Puis :
     ```bash
     gh auth status   # vérifier avant toute chose
     ```
     Si `gh` absent ou non authentifié : signale-le clairement, saute la partie GitHub, continue le reste du bootstrap sans bloquer.
     Si OK :
     ```bash
     cd <racine du projet>
     git init   # si pas déjà un dépôt
     gh repo create <nom> --private --source=. --remote=origin
     ```
     Committe les fichiers standard une fois créés (voir plus bas), puis demande *"je pousse ce premier commit ?"* avant tout `git push`.
   - **Un repo existe déjà** → demande l'URL, puis :
     ```bash
     git init   # si pas déjà un dépôt
     git remote add origin <url>
     git fetch origin
     ```
     - Si le repo distant est vide → rien de plus, le premier commit/push suit le flow normal ci-dessus.
     - Si le repo distant contient déjà des fichiers → tente une fusion (`git merge --allow-unrelated-histories origin/main` ou la branche par défaut). En cas de conflit de chemins entre contenu local et distant, ne tranche pas : montre le conflit à l'utilisateur et demande comment concilier (garder le local, garder le distant, fusionner à la main) avant de continuer.
5. *"Tu veux lier ce projet à une liste Reminders, pour que je puisse aussi te proposer/suivre les tâches depuis l'app Rappels ?"* — optionnel.
   - Si l'outil `reminders_lists` échoue faute de serveur MCP `apple-reminders` disponible sur cette machine : même traitement que "Outil MCP indisponible" dans `references/reminders-sync.md`, étape 0 (propose de l'installer toi-même, scope `user` impératif) — ne bloque pas le reste du bootstrap pour autant.
   - Si oui et qu'une liste existante correspond déjà au projet (`reminders_lists` action `read`) : propose de la réutiliser plutôt que d'en créer une nouvelle.
   - Si oui et qu'aucune liste existante ne convient : demande *"Quel nom pour la liste ?"* (suggestion par défaut = nom du projet, à valider ou changer — jamais créée sans confirmation du nom), puis crées-en une nouvelle à plat (`reminders_lists` action `create`) — l'outil ne peut pas la ranger automatiquement dans un dossier Reminders, l'utilisateur le fait lui-même s'il veut.
   - Dans tous les cas (oui ou non), écris la réponse dans le frontmatter `reminders_list` (nom de la liste, ou `"non"` si décliné — jamais une chaîne vide, qui se confond trop facilement avec "pas encore rempli") — jamais reposée ensuite. Voir `references/reminders-sync.md` pour le fonctionnement une fois lié.
6. *"Projet assez complexe pour mériter un `ARCHITECTURE.md` séparé, ou `CLAUDE.md` suffit ?"* et *"du jargon métier qui justifierait un `GLOSSARY.md` ?"* — optionnels, décidés au cas par cas ; crée-les seulement si la réponse est oui.

Crée d'abord `mkdir -p docs/project-tracker/` à la racine du projet, puis les fichiers standard (section suivante) remplis avec les réponses obtenues — jamais de contenu inventé pour ce qui n'a pas été répondu. `README.md` et `CLAUDE.md` vont à la racine du projet ; les 7 autres fichiers standard dans `docs/project-tracker/` (voir section suivante pour le détail par fichier). Le frontmatter du `STATUS.md` ainsi créé inclut immédiatement `backlog_model: "adopté"`, écrit automatiquement en même temps que les autres champs — jamais posé comme question à ce stade, puisque `BACKLOG.md` fait partie des fichiers standard créés sans condition (voir section suivante).

## Les fichiers standard

Neuf fichiers pour chaque projet suivi. `README.md` et `CLAUDE.md` à la racine du projet (auto-découverte GitHub/Claude Code — voir le spec du 27/08) ; les 7 autres dans `docs/project-tracker/` :

| Fichier | Contenu | Rythme |
|---|---|---|
| `README.md` (racine) | Quoi, pourquoi, stack, installation/lancement, liens (repo, docs) | Rare |
| `docs/project-tracker/ROADMAP.md` | Synthèse priorisée dérivée de `BACKLOG.md` : phases passées, phase en cours, phases anticipées — jamais le détail brut. Voir `references/backlog-phases.md` | Occasionnel |
| `docs/project-tracker/STATUS.md` | Instantané de l'état actuel (ce qui marche/casse, 3 prochaines actions) + frontmatter machine-lisible (voir plus bas). **Se réécrit entièrement**, ne s'accumule pas | À chaque session/changement significatif |
| `docs/project-tracker/JOURNAL.md` | Log chronologique daté des sessions : ce qui a été fait, pourquoi | **Append-only**, à chaque session significative |
| `docs/project-tracker/CHANGELOG.md` | Format Keep a Changelog (Added/Changed/Fixed) par version | À chaque changement livrable |
| `CLAUDE.md` (racine) | Instructions pour toi : conventions de code, commandes build/test, pièges connus, résumé d'archi, choix git/GitHub du projet | Quand les conventions évoluent |
| `docs/project-tracker/DECISIONS.md` | Pourquoi tel choix technique plutôt qu'un autre, alternatives écartées | **Append-only**, une entrée par décision structurante |
| `docs/project-tracker/ERRORS.md` | Bug rencontré → cause → fix, recherchable | **Append-only**, à chaque bug résolu significatif |
| `docs/project-tracker/BACKLOG.md` | Réservoir brut et complet de toute idée/feature envisagée (effort, valeur perçue). Jamais purgé, enrichi et archivé. Voir `references/backlog-phases.md` | **Append-only** (archivage, jamais de purge) |

Optionnels (créés seulement si demandé à l'étape 6 du bootstrap, dans `docs/project-tracker/`) : `ARCHITECTURE.md`, `GLOSSARY.md`.

### Frontmatter de `STATUS.md`

```yaml
---
project: <nom du projet>
status: active            # active | paused | blocked | archived
uses_git: true            # ou false selon le choix du bootstrap
repo: https://github.com/<user>/<repo>   # vide si non applicable
stack: [Python, FastAPI, ...]
last_updated: <YYYY-MM-DD>
next_milestone: "<texte libre>"
reminders_list: "<nom de la liste Reminders>"   # "non" si décliné, absent si jamais posée
backlog_model: "adopté"   # automatique au bootstrap ; "non" seulement possible via rétrofit décliné ; absent seulement pour un projet suivi avant cette fonctionnalité et pas encore rétrofité
phase_model: "superpowers"   # ou "leger" ; absent si aucune phase jamais proposée
---
```

C'est la seule partie strictement structurée de tous ces fichiers — le reste est narratif libre. Ce frontmatter est ce que `generate_portfolio.py` consomme pour le portfolio (voir plus bas) : `project`, `status` et `last_updated` sont obligatoires, sans eux le projet est simplement omis du portfolio.

## Mise à jour en continu

Quand tu juges avoir fait un changement significatif dans une session (nouvelle feature, fix important, décision d'archi tranchée) :
1. Relis `STATUS.md` à l'instant présent (jamais une version vue plus tôt dans la session), puis réécris-le (état + 3 prochaines actions, frontmatter à jour dont `last_updated`).
2. Ajoute une entrée datée à `JOURNAL.md` (append réel — n'ouvre pas le fichier en entier pour le réécrire, ajoute juste la nouvelle entrée à la fin).
3. Si pertinent : ajoute une entrée à `CHANGELOG.md` (changement livrable), `DECISIONS.md` (choix technique tranché), ou `ERRORS.md` (bug résolu) — toujours en append, jamais en réécrivant tout le fichier.
4. Si `uses_git: true` et qu'il y a des changements non commités qui traînent, signale-le et propose un commit (message conventional commits) — jamais de commit/push sans confirmation explicite.
5. La synchro Reminders elle-même n'est plus déclenchée ici (voir `references/reminders-sync.md` — un hook `PostToolUse` s'en charge au premier changement de `docs/project-tracker/STATUS.md`/`docs/project-tracker/ROADMAP.md` de chaque session (un rappel par session et par projet)) ; la question de liaison, pour un projet qui ne l'a jamais eue, se pose plus tôt — voir `## Détection de la racine d'un projet` — pas ici.

Ce déclenchement (juger qu'un changement est "significatif") est ton propre jugement, pas une règle mécanique. Filet de sécurité : l'utilisateur peut à tout moment te demander explicitement une mise à jour — dans ce cas, vérifie l'état réel avant d'écrire quoi que ce soit (ne réécris pas si rien n'a en fait changé depuis le dernier `last_updated`).

### Collisions entre sessions concurrentes

L'utilisateur travaille souvent avec plusieurs sessions Claude Code ouvertes en parallèle sur le même projet. Avant de réécrire `STATUS.md` (ou tout fichier réécrit en entier plutôt qu'accumulé) :
- Si `uses_git: true` : juste avant d'écrire, vérifie s'il y a un diff non commité sur ce fichier qui ne vient pas de cette session (`git diff -- docs/project-tracker/STATUS.md`). Si oui, n'écrase pas : montre le diff à l'utilisateur et demande comment fusionner les deux mises à jour plutôt que de trancher toi-même.
- Sans git : compare la date de modification du fichier à celle vue lors de ta dernière lecture ; si elle a changé entre-temps, même traitement (montrer, demander).

Pour `JOURNAL.md`, `CHANGELOG.md`, `DECISIONS.md`, `ERRORS.md`, `BACKLOG.md` : l'écriture doit toujours être un véritable ajout en fin de fichier (ou une mise à jour ciblée d'un item existant, ex. cocher `[x]`) — jamais un cycle "relire tout / réécrire tout" — pour que deux sessions qui ajoutent chacune une entrée en parallèle ne s'écrasent pas l'une l'autre.

## Sync Reminders

Si `reminders_list` (frontmatter `STATUS.md`) est lié (présent, différent de `"non"`) : voir `references/reminders-sync.md` pour le déclenchement (hook + diff complet + backfill), le tag `#tracker-sync`, le mapping de priorité, les sous-tâches, et le garde-fou de cohérence. La question de liaison elle-même se pose ailleurs — voir `## Bootstrap d'un nouveau projet` (étape 5) et `## Détection de la racine d'un projet`.

## Portfolio

Après toute écriture de `STATUS.md`, régénère le portfolio du périmètre concerné :

```bash
${CLAUDE_SKILL_DIR}/scripts/generate_portfolio.py <racine du périmètre>
```

Exemple : `${CLAUDE_SKILL_DIR}/scripts/generate_portfolio.py ~/Documents/Code`. Le script écrit `PORTFOLIO.html` à la racine du périmètre et affiche un résumé (nombre de projets, avertissements). Ne rédige jamais le HTML toi-même — le script garantit une présentation cohérente, ton rôle s'arrête à l'invoquer après une mise à jour de `STATUS.md`.

## Rétrofit d'un projet existant

Quand le projet a déjà des fichiers de suivi non standard (ex. des `.pages`, un `CLAUDE.md`/`JOURNAL.md` déjà présents) : traite-le comme un bootstrap, mais réutilise ce qui existe déjà plutôt que de reposer les questions depuis zéro. Si une doc source n'est pas lisible nativement (ex. fichiers `.pages` d'Apple, binaires zip) : dis-le clairement à l'utilisateur et propose soit qu'il l'exporte en texte/markdown/PDF, soit de repartir directement des questions du bootstrap.

### Rétrofit du modèle Backlog/Roadmap/Phases

Un projet déjà suivi peut avoir son propre `BACKLOG.md` (et parfois des `PHASE_N_SPEC.md`) à un chemin non standard, mis en place avant l'existence de cette fonctionnalité dans `project-tracker`. Deux cas à distinguer par la présence ou non d'un `STATUS.md` propre à ce sous-dossier :
- **Un `STATUS.md` propre existe à ce sous-dossier** : c'est un projet suivi séparément (sa propre racine, son propre `docs/project-tracker/`) — ne fusionne jamais son contenu dans le projet englobant.
- **Aucun `STATUS.md` propre** : ce sont des fichiers de détail orphelins (pas une identité de suivi à part) — consolide-les dans `docs/project-tracker/` du projet englobant plutôt que de les laisser où ils sont.

L'auto-reconnaissance (voir `## Détection de la racine d'un projet`) ne se déclenche que si `ROADMAP.md` référence explicitement ce `BACKLOG.md` (peu importe son chemin) — sinon, pose la question normalement, même si un `BACKLOG.md` existe quelque part dans le projet sans lien explicite depuis `ROADMAP.md` (ne devine pas qu'il joue ce rôle).

Si la question est posée et acceptée pour un projet qui a déjà un `ROADMAP.md` et/ou un contenu de suivi existant (ex. un `docs/BACKLOG.md` maison, ou un `ROADMAP.md` qui liste déjà des idées en vrac) : ne crée pas de fichier vide à côté — discute avec l'utilisateur pour résumer/reformater ce qui existe déjà selon la structure de `references/backlog-phases.md`, au cas par cas, plutôt que d'appliquer un script générique.
