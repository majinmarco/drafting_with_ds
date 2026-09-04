# Derived positional scarcity from real data (lesson 2 complete)

Marco completed all three TODOs in `lesson_1.py` unaided and both quizzes: built per-position ranks with `groupby`+`rank(method="first")`, plotted the four scarcity curves, and computed top-vs-last-starter gaps with a dict comprehension. ADP-as-market-price and VOR-as-value vocabulary is now established and usable.

**Evidence:** working code in `lesson_1.py` (his own variants, not the reference solutions — e.g. scatter plot, `[:40]` slicing, boolean-mask lookups).

**Misconception to reinforce against:** his written interpretation called QB "the largest dropoff" because QB1 (Josh Allen) towers over QB2–12. The elite-outlier premium is a real observation, but draft priority is set by the slope across the *whole starter range* (RB steepest, ~166), not the top step. Revisit when teaching baselines/VOR: "dropoff" must always name its range.

**Minor code notes for future exercises:** tends to skip `.astype(int)` after `rank` and to leak loop variables as marimo globals (`group`) instead of `_`-prefixing them.
