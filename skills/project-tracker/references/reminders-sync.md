# Sync Reminders

Référencé depuis `SKILL.md` (`## Détection de la racine d'un projet`, `## Bootstrap d'un nouveau projet` étape 5, `## Mise à jour en continu` étape 5).

Le tag `#tracker-sync` marque un rappel comme actuellement suivi/absorbé par Claude dans les fichiers de suivi — posé aussi bien sur un rappel que l'utilisateur écrit que sur un rappel que Claude crée, une fois son périmètre discuté et reflété dans `STATUS.md`/`ROADMAP.md`. Un rappel sans ce tag est une capture brute pas encore vue par Claude. Ce `#` est l'affichage natif de l'app Reminders — dans les paramètres `tags`/`addTags`/`filterTags` de l'outil `reminders_tasks`, le tag se passe sans le `#` (`"tracker-sync"`), comme les tags thématiques (`#ROI` → `"ROI"`, etc.).

La question de liaison se pose au bootstrap (étape 5) ou, pour un projet déjà suivi qui ne l'a jamais eue, dès la détection de l'état "Suivi" (voir `## Détection de la racine d'un projet` dans `SKILL.md`) — jamais ici, et jamais en attendant un déclenchement de "Mise à jour en continu".

Si `reminders_list` est absent (question jamais posée — ne devrait normalement plus arriver une fois la détection ci-dessus passée, mais filet de sécurité si cette section est atteinte avant) ou vaut `"non"` (déclinée) : saute entièrement cette section, comportement inchangé.

Sinon, à chaque déclenchement (hook `PostToolUse`, backfill au linking, ou demande explicite de l'utilisateur) :

0. Vérifie que `reminders_list` résout vers une liste existante (`reminders_lists` action `read`). Deux échecs possibles à distinguer, aucun des deux ne doit faire échouer le reste de la mise à jour continue :
   - **Outil MCP `apple-reminders` indisponible** (le skill est portable multi-machines, cf. `install-project-tracker.sh` — le serveur MCP n'est pas forcément installé partout) : propose de l'installer toi-même maintenant, tout de suite (`claude mcp add apple-reminders -s user -- npx -y mcp-server-apple-events` — scope `user` impératif, pas le scope `local` par défaut de la commande, sinon le serveur reste invisible depuis les sessions ouvertes dans un autre projet que celui où tu l'installes). Si l'utilisateur accepte, exécute la commande toi-même plutôt que de simplement l'indiquer, puis explique-lui qu'il doit redémarrer sa session Claude Code pour que les nouveaux outils deviennent visibles. Si l'utilisateur décline, saute le reste de cette section pour cette session sans bloquer le reste de la mise à jour continue.
   - **Liste introuvable** (renommée ou supprimée côté app) : ne devine pas, demande explicitement à l'utilisateur — se greffer sur une liste existante (propose celles disponibles), créer une nouvelle liste (met à jour `reminders_list`), ou arrêter de suivre les rappels pour ce projet (`reminders_list: "non"`). Tant que ce n'est pas résolu, saute le reste de cette section pour cette session.
1. Lis tous les rappels ouverts de la liste (`reminders_tasks` action `read`, `filterList: <reminders_list>`).
2. **Rappels sans tag `#tracker-sync`** (captures brutes de l'utilisateur) : annonce combien ont été trouvés et demande si tu les traites maintenant ou si tu remets à plus tard (ils restent non tagués, donc reproposés à l'identique à la prochaine passe — rien n'est perdu). Si oui, aborde-les un par un, mais entre chaque, redemande si tu continues avec les suivants ou si tu t'arrêtes là pour cette passe — un feu vert au début ne vaut jamais accord pour traiter tout le lot d'un coup. Pour chaque rappel que tu traites, discute pour cerner le périmètre exact. Une fois clarifié :
   - Réécris éventuellement le titre/les notes du rappel (`reminders_tasks` action `update`) pour que ce soit plus clair et détaillé — la discussion elle-même vaut confirmation, pas de validation séparée pour la réécriture.
   - Fixe la priorité selon le mapping ci-dessous.
   - Écris l'item dans `STATUS.md` ("Prochaines actions") ou `ROADMAP.md` (contenu de la phase en cours), selon ce qui a été décidé ensemble — jamais `BACKLOG.md` (voir "Décision de périmètre" plus bas : le backlog brut n'est jamais synchronisé, dans un sens comme dans l'autre).
   - Pose le tag `#tracker-sync`, plus un tag thématique choisi en discussion si pertinent (ex. `#ROI`, `#NUC` — voir "Sections de liste" ci-dessous), via `addTags` (jamais `tags`, qui remplacerait entièrement les tags déjà posés par l'utilisateur sur ce rappel — `addTags` fusionne sans y toucher).
3. **Rappels tagués `#tracker-sync` et encore ouverts** : compare par jugement (jamais de correspondance texte exacte — reconnais une tâche reformulée) à l'état actuel de `STATUS.md`/`ROADMAP.md`/de la conversation/du `git log`. Si tu penses qu'une tâche est terminée, propose-le explicitement. Si confirmé : coche le rappel (`reminders_tasks` action `update`, `completed: true`) **et** mets à jour `STATUS.md`/`JOURNAL.md` dans la même confirmation — un seul aller-retour couvre les deux écritures.
4. **Couverture complète** : diff entre tous les objectifs de `STATUS.md` ("Prochaines actions") + `ROADMAP.md` (contenu de la phase en cours) et les rappels ouverts existants, par le même rapprochement par jugement qu'à l'étape 3 (jamais de correspondance texte exacte). Tout objectif sans rappel correspondant est proposé à la création (`reminders_tasks` action `create`, `targetList: <reminders_list>`, tags via `tags: ["tracker-sync", ...]` — ici un vrai `create`, rien à préserver), priorité selon la section d'origine (voir mapping ci-dessous). Si plusieurs items sont concernés en une passe, montre la liste et demande confirmation avant de les créer en lot ; pour un seul item ajouté au fil de la session, la confirmation normale de mise à jour de `STATUS.md` suffit, pas de validation séparée. Ce diff n'est plus limité aux items ajoutés pendant la session courante — voir "Déclenchement" ci-dessous.

Si un appel à l'un de ces outils échoue en cours de route, à n'importe quelle étape (ex. permission macOS Rappels/Calendrier révoquée après le premier accord) : signale-le clairement à l'utilisateur et arrête le reste de cette section pour cette session — ne fais jamais échouer le reste de la mise à jour continue (`STATUS.md`, `JOURNAL.md`, etc.) à cause de ça.

## Décision de périmètre : Reminders ↔ Backlog

`BACKLOG.md` n'est **jamais** synchronisé vers Reminders — ni par le hook (voir "Déclenchement"), ni par l'étape 4 ci-dessus. Seuls `STATUS.md` (section "Prochaines actions") et `ROADMAP.md` (contenu de la phase en cours) alimentent Reminders. Raison : `BACKLOG.md` est un réservoir brut et volontairement non trié (voir `references/backlog-phases.md`) — un outil de *grooming*, pas une liste d'engagements. Synchroniser tout le backlog noierait les vraies prochaines actions dans du bruit. Un item de backlog n'entre dans le monde des rappels qu'au moment où il est promu dans une phase concrète de `ROADMAP.md`.

## Déclenchement

Un hook `PostToolUse` (`hooks/reminders_sync_trigger.sh`, voir sa documentation dans le script lui-même) se déclenche automatiquement au premier changement de `STATUS.md`/`ROADMAP.md` de chaque session, pour un projet suivi et lié (un rappel par session et par projet — debounce via un marqueur clé session_id+projet, cohérent avec "un seul rappel de vérification par session") — c'est lui qui garantit que l'étape 4 ci-dessus tourne sans dépendre de ton propre jugement sur ce qui compte comme "changement significatif" (l'ancien gating, qui avait déjà causé un bug réel de retrofit jamais déclenché — voir le spec du 25/08). Le hook ne fait qu'injecter un rappel textuel ; toute la logique (étapes 0-4 ci-dessus) reste ton jugement, jamais mécanisé côté hook.

**Backfill au linking** : juste après une liaison de liste réussie (bootstrap étape 5, ou rétrofit d'un projet déjà suivi), lance immédiatement l'étape 4 ci-dessus une fois — couvre les objectifs déjà présents dans `STATUS.md`/`ROADMAP.md` au moment de la liaison, pas seulement les futurs ajouts.

## Mapping priorité Reminders → section du fichier

| Priorité Reminders | Signification | Section fichier |
|---|---|---|
| Basse (`priority: 9`) | Prochaine tâche normale | `STATUS.md` → "Prochaines actions" |
| Moyenne (`priority: 5`) | Tâche importante | `STATUS.md` → "Prochaines actions" |
| Haute (`priority: 1`) | Tâche importante ET prioritaire | `STATUS.md` → "Prochaines actions" |

L'encodage numérique de l'outil `reminders_tasks` est contre-intuitif (inversé par rapport à l'ordre naturel) — vérifié sur le schéma réel du serveur MCP en implémentation. Toujours utiliser la valeur numérique ci-dessus, jamais deviner un ordre "plus grand nombre = plus prioritaire".

Basse/Moyenne/Haute vivent toutes dans "Prochaines actions" ; le niveau exprime le poids relatif à l'intérieur de cet ensemble actif. La priorité n'est jamais figée : Claude peut la faire monter ou descendre à tout moment si la discussion change l'évaluation d'une tâche (ex. une tâche Basse devient Haute si elle bloque autre chose).

## Sections de liste (limitation connue)

L'app Reminders (Tahoe) permet de regrouper les rappels d'une liste sous des en-têtes thématiques (ex. "ROI", "NUC", "Image" dans une liste projet) — fonctionnalité purement UI, invisible et impilotable via l'outil MCP (même limite que les dossiers Projects/Domains). Les rappels que tu crées ou modifies arrivent donc toujours hors section — l'utilisateur les range lui-même dans l'app s'il veut. Palliatif : pose un tag thématique (étape 2 ci-dessus) en plus de `#tracker-sync` pour approximer un classement filtrable.

## Sous-tâches

Objectif : garder la liste lisible (peu d'items top-level) tout en capturant le détail des tâches composées.

- **Tâche composée** (plusieurs étapes concrètes identifiées en discussion) → un seul rappel top-level pour l'action globale, avec chaque étape en sous-tâche — plutôt que plusieurs rappels top-level séparés qui diluent la priorité et encombrent la liste.
  - **Rappel nouveau** (ex. étape 4, création à partir d'un item de fichier) et toutes les étapes déjà connues au moment de la création : un seul appel, `reminders_tasks` action `create` avec `subtasks: ["étape 1", "étape 2", ...]` — crée le rappel et ses sous-tâches d'un coup plutôt que `create` + N appels `reminders_subtasks` action `create` séparés.
  - **Rappel qui existe déjà** (ex. capture de l'utilisateur retravaillée à l'étape 2, ou une étape découverte après coup) : `subtasks` inline ne joue qu'à la création, donc ajoute chaque étape via `reminders_subtasks` action `create`.
- **Tâche atomique** → rappel simple, pas de sous-tâches.
- Cocher une sous-tâche (`reminders_subtasks` action `toggle`) suit la même règle que cocher le rappel parent : jamais silencieux, toujours proposé et confirmé avant d'écrire.
- Quand toutes les sous-tâches d'un rappel sont cochées, signale-le et propose de cocher le rappel parent — se branche sur l'étape 3 ci-dessus.
- Optionnel, à ton appréciation : reflète l'avancement des sous-tâches dans `STATUS.md` (ex. "2/3 étapes faites") lors d'une réécriture normale du fichier — pure lecture d'état, ne déclenche pas de confirmation à part.

## Garde-fou : rappel coché en dehors du flow

Si un rappel est coché directement dans l'app (plutôt que via l'étape 3 ci-dessus), rien ne le répercute automatiquement dans `STATUS.md`/`JOURNAL.md` — un filet de sécurité couvre ce cas pour éviter une incohérence silencieuse entre le fichier et l'app.

Pour chaque item de "Prochaines actions" déjà lié à un rappel (donc normalement tagué `#tracker-sync`) : vérifie par une recherche ciblée (`reminders_tasks` action `read`, `search: <mots-clés du titre>`, `filterList: <reminders_list>`, `showCompleted: true`) si le rappel correspondant est coché. Ne lis jamais tout l'historique des rappels complétés en masse — ça grossirait sans fin sur la durée de vie du projet ; la recherche ciblée reste bornée par la taille de "Prochaines actions" (toujours petite), pas par l'historique accumulé.

La recherche peut renvoyer zéro, un ou plusieurs résultats — utilise ton jugement pour identifier lequel correspond réellement à l'item (même logique que l'étape 3, pas de correspondance texte exacte). Si aucun résultat net ne se dégage (zéro match, ou plusieurs candidats sans façon fiable de trancher) : n'invente pas de correspondance, laisse cet item de côté pour cette passe plutôt que de risquer un faux positif.

Si un rappel correspondant est identifié avec confiance et qu'il est coché : c'est une incohérence — signale-la explicitement à l'utilisateur et propose de mettre à jour `STATUS.md`/`JOURNAL.md` en conséquence, avec la même confirmation que l'étape 3.
