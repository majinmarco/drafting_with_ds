# Built the VOR cheat sheet; hit marimo's cross-cell-mutation pitfall (lesson 3 complete)

Marco completed lesson 3's TODO and generated a correct cheat sheet (`data/cheat_sheet_2026.csv`, 393 players — Gibbs VOR 185 at the default RB30 baseline checks out). VOR-across-positions and baseline-as-modeling-choice are now demonstrated, not just covered.

**Notable:** instead of the hinted one-liner, he added a separate cell that *mutates* `ranked` in place (`ranked['repl'] = ranked.pos.map(repl)`) and consumed the new column in the TODO cell. It ran correctly this session, but marimo's dependency graph doesn't track mutations: there is no edge between the mutating cell and the consuming cell, so execution order between them is not guaranteed, and slider changes to the baselines re-run the mutation without re-running the VOR cell — silently stale output. Corrected on draft day (fold the map into the same cell / use `assign`).

**Implication:** he now has personal evidence for *why* marimo's one-definition/no-mutation discipline exists — reference this when teaching notebook hygiene, and watch for in-place `df[col] = ...` habits carried over from script pandas.
