# Backlog / Roadmap / Phases

Référencé depuis `SKILL.md` (`## Les fichiers standard`, `## Bootstrap d'un nouveau projet`, `## Détection de la racine d'un projet`, `## Rétrofit d'un projet existant`). S'applique à tout projet suivi — `BACKLOG.md` existe pour tous, même vide au départ, créé sans condition ni question par le bootstrap (`backlog_model: "adopté"` écrit automatiquement dans ce cas — voir `## Bootstrap d'un nouveau projet` dans `SKILL.md` ; le `"non"` décliné n'existe que via le chemin de rétrofit d'un projet qui préexistait à cette fonctionnalité, voir `## Rétrofit d'un projet existant`) ; le mécanisme de phases ci-dessous ne s'active que quand assez d'items s'accumulent.

## `BACKLOG.md` — réservoir brut

Toute idée/feature envisagée pour le projet, jamais purgée — seulement enrichie et archivée. Organisé par priorité (haute/moyenne/basse, ou "sans priorité définie"/"idées non priorisées" pour ce qui n'est même pas encore trié) plutôt que par ordre chronologique. Pour chaque item, autant que possible : effort estimé (S/M/L) et valeur perçue (⭐ à ⭐⭐⭐) — aide à choisir quoi grouper dans une phase. Statuts `[ ]` à faire / `[~]` en cours / `[x]` fait / `[-]` abandonné. Termine par une courte section "Comment utiliser ce backlog" rappelant le cycle : démarrer une phase (choisir des items cohérents, les grouper) → suivre l'avancement (`[~]`) → archiver à la clôture (`[x]` puis section "Complété" en bas du fichier).

## `ROADMAP.md` — synthèse dérivée

Ne liste jamais le détail brut (effort/valeur, notes techniques) — pointeur vers `BACKLOG.md` pour ça. Structure :
1. **Fait** — phases passées, une ligne chacune, pointeur vers `STATUS.md`/`CHANGELOG.md` pour le détail.
2. **Phase N — 🎯 en cours** — la phase active en ce moment (voir "Mécanisme des phases" ci-dessous), avec le détail de son contenu.
3. **Après Phase N** — phases suivantes déjà anticipées, groupées par priorité.
4. **Idées non priorisées** — résumé très court (quelques mots par thème, pas la liste complète — celle-ci vit dans `BACKLOG.md`).

Si un projet n'a pas encore assez de contenu pour justifier plusieurs phases : `ROADMAP.md` peut rester une simple liste priorisée sans la structure "Phase N" tant qu'aucune phase n'a démarré — la structure complète se met en place au moment de la première phase.

## Mécanisme des phases

Quand assez d'items cohérents du backlog s'accumulent (jugement de Claude — pas de seuil chiffré fixe, cohérent avec "ne jamais deviner" : c'est une proposition, jamais une décision automatique), propose de démarrer une phase. Si accepté :

1. Détermine `phase_model` si pas encore fait pour ce projet (frontmatter `STATUS.md`, absent = jamais posé) :
   - `claude plugin list` → si `superpowers` présent et activé : `phase_model: "superpowers"`, pas de question.
   - Sinon (absent, ou présent mais désactivé) : propose l'installation/l'activation toi-même (`claude plugin marketplace list` → `claude plugin marketplace add anthropics/claude-plugins-official` si besoin → `claude plugin install superpowers@claude-plugins-official` → `claude plugin enable superpowers`), exécute-la toi-même si acceptée plutôt que d'expliquer comment faire, préviens qu'un redémarrage de session est nécessaire, puis `phase_model: "superpowers"`. Si déclinée : propose le format léger à la place plutôt que de bloquer la fonctionnalité, puis `phase_model: "leger"`.
   - Une fois déterminé, jamais reposé pour ce projet — même si `superpowers` devient disponible plus tard sur la machine (cohérence entre toutes les phases d'un même projet). Un changement de format reste possible à la demande explicite de l'utilisateur, mais jamais reproposé automatiquement.
2. Produit le document de la phase selon `phase_model` :
   - `"superpowers"` : invoque le skill `writing-plans` pour produire un plan dans `docs/superpowers/plans/YYYY-MM-DD-<sujet>.md`, dans le dépôt du projet suivi (pas celui de `project-tracker`).
   - `"leger"` : rédige toi-même `docs/project-tracker/phases/PHASE_N_SPEC.md` (objectif, périmètre, règles à respecter) — pas de cérémonie SDD, implémentation directe.
3. `ROADMAP.md` gagne/actualise sa section "Phase N — 🎯 en cours" qui référence ce document.
4. Les items concernés passent en `[~]` dans `BACKLOG.md`.

À la clôture d'une phase : items terminés → `[x]` puis archivés dans la section "Complété" de `BACKLOG.md` ; la section "Phase N — en cours" de `ROADMAP.md` bascule dans "Fait".
