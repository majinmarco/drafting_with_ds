# Working Notes

## Learner profile
- Marco. Comfortable with Python/pandas; can wrangle dataframes and plot unaided. No optimization-library experience yet.
- **New to fantasy football** — game mechanics must be taught, but he has quant intuition, so teach concepts through data framing rather than folksy analogies.
- Goal is dual: win the league AND build DS/optimization skills. Lessons should always pair a fantasy concept with the DS technique that formalizes it.

## League facts
- 12-team, head-to-head points, snake draft, ESPN platform.
- Marco confirmed (Sep 2): scoring & settings are ESPN defaults (PPR fractional; 1QB/2RB/2WR/1TE/1FLEX/1K/1DST + bench).
- **DRAFT IS SEP 4, 2026.** Draft slot not yet assigned (ESPN typically randomizes shortly before the draft).

## Data pipeline (verified working Sep 2)
- Source: ESPN public fantasy API — `lm-api-reads.fantasy.espn.com/.../seasons/2026/segments/0/leaguedefaults/3?view=kona_player_info` with `X-Fantasy-Filter` header. No auth needed. Weekly projections (statSourceId=1, statSplitTypeId=1) summed to season; ADP from `ownership.averageDraftPosition`.
- FantasyPros pages are now JS-rendered — `pandas.read_html` gets only 10-row previews. Don't build lessons on scraping them.
- `code/pull_espn_data.py` (uv PEP 723 script) → `data/espn_players_2026.csv`; frozen sample at `data/espn_players_2026_sample.csv`.
- Real 2026 gaps (top vs last starter): QB ~81, RB ~166, WR ~141, TE ~73. Top-30 ADP: 25 RB/WR, 1 QB.
- No system pandas — everything runs via `uv run` with inline deps.

## Compressed pre-draft curriculum (draft Sep 4)
1. ✅ 0001 — How the game & snake draft work; value is relative (replacement-level intuition)
2. ✅ 0002 — Pull ESPN projections+ADP into pandas; derive scarcity curves (exercise: `code/explore_scarcity.py`)
3. ✅ (Sep 4) `lesson_3.py` — VOR cheat sheet notebook: reactive baseline sliders, one TODO (vor column) with auto-check, mo.ui.table sheet + edge column, draft-slot slider → per-pick plan; saves `data/cheat_sheet_2026.csv`
4. ✅ (Sep 4) `reference/draft-day-quick-reference.html` — printable draft rules (position timing, per-pick checklist, traps)
5. Draft slot: STILL UNKNOWN as of Sep 4 morning — slider in lesson_3.py handles any slot

Marco completed lesson 2's TODOs unaided (learning record 0002 — note the "dropoff range" misconception to reinforce).

**File naming rule (Marco, Sep 4): notebook filenames follow COURSE lesson numbers, one file per lesson, never reuse/renumber an existing file.** `lesson_1.py` is the one historical exception (it holds course lesson 2; Marco created it — leave it alone). Course lesson 3 = `lesson_3.py`. Next lessons: `lesson_4.py`, etc.

6. ✅ (Sep 4) `lesson_4.py` — the draft as an integer program (PuLP/CBC, x_{p,r} formulation, availability in the variable set, VOR objective) + **live draft widget** (gone/mine multiselects → dropoff board with one-step-lookahead recommendations). TODO: ROSTER_LIMITS. Solve time ~1s on 380 players × 16 picks. Marco requested the widget himself.

Tools (off the books, not lessons): `draft_widget.py` — standalone live-draft widget extracted from lesson_4 Part B (slot slider, gone/mine multiselects, dropoff recommendations, my-team tracker). Marco's request, Sep 4.

Post-draft (learning continues): Monte Carlo opponent simulation (replace ±3-pick availability rule with a probability model), retro of his actual draft vs the optimizer, in-season management basics.

## Preferences observed
- **marimo everywhere (Sep 3, user rule):** all lessons/exercises are marimo notebooks (see `CLAUDE.md` in this dir; also added to the teach skill itself). Marco started `lesson_1.py` himself — his numbering for code notebooks; conceptual HTML lessons 0001/0002 predate the rule. Lesson 2's exercise now lives in `lesson_1.py` (pull + scarcity TODOs with reactive check cells); the old `code/` scripts were removed.
- Run notebooks: `uvx marimo edit --sandbox lesson_1.py`; validate: `marimo check --fix` + `uv run`.
