# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "pandas",
#     "requests",
#     "matplotlib==3.11.1",
#     "mcp==2.1.1",
# ]
# ///

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Lesson 2 · The Projections, the Market, and the Curves

    *Data-Driven Snake Drafting — run me with* `uvx marimo edit --sandbox lesson_1.py`

    In [Lesson 1](lessons/0001-snake-drafts-and-replacement-value.html) you learned that
    **value is relative to replacement level**, from an *illustrative* table. Today you pull
    the real thing — 2026 data from the same API that powers your ESPN league — and derive
    the scarcity story yourself. Two datasets matter, and your entire edge lives in the
    difference between them:

    1. **Projections** — what players are *worth*. ESPN's estimate of each player's fantasy
       points, in your league's exact scoring. We sum their weekly projections into a season total.
    2. **ADP (average draft position)** — what players *cost*. The average pick number across
       thousands of real drafts: the market price, and your best model of what your 11
       opponents will do.

    > **Projections are value; ADP is price.** Drafting well means buying value for less than
    > the market price — visible only when you hold both datasets side by side.
    """)
    return


@app.cell
def _():
    import json
    from pathlib import Path

    import matplotlib.pyplot as plt
    import pandas as pd
    import requests

    import marimo as mo

    return Path, json, mo, pd, plt, requests


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 1 — pull the data

    The next four cells call ESPN's public fantasy API. `leaguedefaults/3` = the default PPR
    settings your league uses; the `X-Fantasy-Filter` header is how this API takes query
    parameters. Read the parsing cell closely — decoding a messy nested payload is a real DS
    skill, and ESPN's stat tagging (`statSourceId` 1 = projection, `statSplitTypeId` 1 =
    single week) is a nice specimen.
    """)
    return


@app.cell
def _():
    URL = ("https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/"
           "seasons/2026/segments/0/leaguedefaults/3")
    POSITIONS = {1: "QB", 2: "RB", 3: "WR", 4: "TE", 5: "K", 16: "DST"}

    fantasy_filter = {"players": {
        "limit": 400,
        "sortDraftRanks": {"sortPriority": 1, "sortAsc": True, "value": "PPR"},
    }}
    return POSITIONS, URL, fantasy_filter


@app.cell
def _(URL, fantasy_filter, json, requests):
    resp = requests.get(URL, params={"view": "kona_player_info"},
                        headers={"X-Fantasy-Filter": json.dumps(fantasy_filter)},
                        timeout=30)
    resp.raise_for_status()
    return (resp,)


@app.cell
def _(POSITIONS, resp):
    rows = []
    for _entry in resp.json()["players"]:
        _pl = _entry["player"]
        _weekly_proj = [s["appliedTotal"] for s in _pl.get("stats", [])
                        if s.get("seasonId") == 2026
                        and s.get("statSourceId") == 1      # 1 = projection (0 = actual)
                        and s.get("statSplitTypeId") == 1   # 1 = single week
                        and s.get("appliedTotal")]
        _ownership = _pl.get("ownership") or {}
        rows.append({
            "name": _pl["fullName"],
            "pos": POSITIONS.get(_pl["defaultPositionId"], "?"),
            "proj": sum(_weekly_proj),                      # season = sum of weeks
            "adp": _ownership.get("averageDraftPosition"),
        })
    return (rows,)


@app.cell
def _(pd, rows):
    df = (pd.DataFrame(rows)
            .query("proj > 0")
            .dropna(subset=["adp"])
            .sort_values("adp")
            .reset_index(drop=True))
    df
    return (df,)


@app.cell
def _(Path, df, mo):
    DATA_DIR = Path("data")
    DATA_DIR.mkdir(exist_ok=True)
    df.to_csv(DATA_DIR / "espn_players_2026.csv", index=False)
    mo.md(f"✅ Saved **{len(df)} players** → `data/espn_players_2026.csv` "
          f"(Gibbs, Bijan, and Chase should top the ADP order above).")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 2 — your turn: derive the scarcity story

    Complete the three TODOs below. Each has a check cell under it that **re-grades your work
    automatically** the instant you change the code — marimo re-runs everything downstream of
    what you edit. Solutions are in the accordion at the bottom of the notebook; try first.

    ---

    ### TODO 1 — positional rank

    Build `ranked`: a copy of `df` with an integer column `pos_rank` — 1 for the
    highest-projected player at each position, 2 for the next, and so on.
    *Hint: `groupby` + `rank(ascending=False, method="first")` (so ties don't duplicate ranks).*
    """)
    return


@app.cell
def _(df):
    ranked = df.assign(pos_rank=df.groupby(by='pos')[["proj"]].rank(ascending=False, method = "first"))
    # ranked = df.assign(pos_rank=...)
    return (ranked,)


@app.cell(hide_code=True)
def _(mo, ranked):
    if ranked is None:
        _out = mo.callout("⏳ Complete TODO 1 above — this check updates automatically.", kind="neutral")
    elif "pos_rank" not in ranked.columns:
        _out = mo.callout("✗ `ranked` has no `pos_rank` column yet.", kind="danger")
    else:
        _ok = (
            ranked.groupby("pos")["pos_rank"].min().eq(1).all()
            and not ranked.duplicated(["pos", "pos_rank"]).any()
            and ranked.sort_values(["pos", "pos_rank"])
                      .groupby("pos")["proj"]
                      .apply(lambda s: s.is_monotonic_decreasing).all()
        )
        _out = (mo.callout("✓ Correct — every position ranked 1..N by projection, no duplicate ranks.",
                           kind="success")
                if _ok else
                mo.callout("✗ Not quite: ranks should start at 1 per position, be unique, and "
                           "follow descending projection. Check `ascending` and `method=\"first\"`.",
                           kind="danger"))
    _out
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### TODO 2 — scarcity curves

    Assign a matplotlib figure to `scarcity_fig`: one line per position (QB, RB, WR, TE —
    skip K and DST), **x** = `pos_rank` (1–40), **y** = `proj`. This is the empirical version
    of Lesson 1's table. Look at it: which curves fall off a cliff, and which glide?
    """)
    return


@app.cell
def _(mo, plt, ranked):
    scarcity_fig = None
    _fig, _ax = plt.subplots(figsize=(8, 5))
    for _pos in ["QB", "RB", "WR", "TE"]:
        group = ranked[ranked['pos'] == _pos].sort_values('pos_rank', ascending=True)[:40]
        _ax.scatter(group['pos_rank'], group['proj'], label=_pos)
    _fig.legend()
    scarcity_fig = _fig
    scarcity_fig if scarcity_fig is not None else mo.callout(
        "⏳ Build the plot (needs `ranked` from TODO 1).", kind="neutral")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    As seen above, QB has the largest dropoff in projected points but maintains itself hgih for a good bit. RB and WR are somewhat stable but declining. WR has a alarge dropoff in the beginning. TE starts low and declines slowly.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### TODO 3 — the last-starter baseline

    In a 12-team default league the "last starters" are roughly **QB12, RB24, WR24, TE12**
    (2 RB + 2 WR slots each; the flex is deliberately ignored for now — ask me why, or wait
    for Lesson 3). Build `gaps`: a dict mapping each position to
    `round(top_proj - last_starter_proj)`.
    """)
    return


@app.cell
def _(ranked):
    BASELINE_RANK = {"QB": 12, "RB": 24, "WR": 24, "TE": 12}

    gaps = {pos: ranked[(ranked['pos'] == pos) & (ranked['pos_rank'] == 1)]['proj'].iloc[0] - ranked[(ranked['pos'] == pos) & (ranked['pos_rank'] == rank)]['proj'].iloc[0] for pos, rank in BASELINE_RANK.items()}
    return (gaps,)


@app.cell
def _(gaps):
    gaps
    return


@app.cell(hide_code=True)
def _(gaps, mo):
    _expected = {"QB": 81, "RB": 166, "WR": 141, "TE": 73}   # pulled Sep 2; small drift is normal
    if gaps is None:
        _out = mo.callout("⏳ Complete TODO 3 — this check updates automatically.", kind="neutral")
    else:
        _close = all(abs(gaps.get(p, -999) - v) <= 15 for p, v in _expected.items())
        _out = (mo.callout(f"✓ {gaps} — matches the Sep 2 checkpoints (QB ~81, RB ~166, WR ~141, TE ~73). "
                           "RB/WR cliff, QB/TE glide: exactly what Lesson 1's theory predicted.",
                           kind="success")
                if _close else
                mo.callout(f"✗ Got {gaps}; expected roughly QB 81, RB 166, WR 141, TE 73 (±15). "
                           "Are you using pos_rank 1 vs the BASELINE_RANK row at each position?",
                           kind="danger"))
    _out
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Bonus — the market already knows

    Count positions among the 30 lowest-ADP players (the first 2.5 rounds):
    `df.nsmallest(30, "adp").pos.value_counts()`. You should see ~25 RB/WR and just **one**
    QB — even though Josh Allen (~371) is the highest-projected player in the entire pool,
    the market lets him fall to pick ~19. The crowd understands replacement value.

    ---

    ## Check yourself
    """)
    return


@app.cell
def _(df):
    df.nsmallest(30, "adp").pos.value_counts()
    return


@app.cell
def _(mo):
    q_scarcity = mo.ui.radio(
        options=["WR", "QB", "RB", "TE"],
        label="**Q1.** Which position's scarcity curve drops most steeply in the 2026 data — "
              "the strongest argument for drafting it early?",
    )
    q_scarcity
    return (q_scarcity,)


@app.cell(hide_code=True)
def _(mo, q_scarcity):
    if q_scarcity.value is None:
        _fb = mo.callout("Pick an answer.", kind="neutral")
    elif q_scarcity.value == "RB":
        _fb = mo.callout("✓ RB: ~166 points from RB1 to RB24 — steeper than WR (~141), "
                         "roughly double QB (~81) or TE (~73).", kind="success")
    else:
        _fb = mo.callout("✗ Check your TODO 3 output: RB falls ~166 points from top to last "
                         "starter, the steepest of the four.", kind="danger")
    _fb
    return


@app.cell
def _(mo):
    q_edge = mo.ui.radio(
        options=[
            "always drafting the highest projected player",
            "gaps between projected value and market price",
            "knowing more player news than opponents",
        ],
        label="**Q2.** Where does your draft-day edge fundamentally come from?",
    )
    q_edge
    return (q_edge,)


@app.cell(hide_code=True)
def _(mo, q_edge):
    if q_edge.value is None:
        _fb2 = mo.callout("Pick an answer.", kind="neutral")
    elif q_edge.value == "gaps between projected value and market price":
        _fb2 = mo.callout("✓ Exactly: when ADP prices a player below his value over replacement, "
                          "you profit — like Josh Allen at pick ~19.", kind="success")
    else:
        _fb2 = mo.callout("✗ The edge is the spread between value (projection vs replacement) and "
                          "price (ADP). Highest-projected ignores scarcity; news is already priced in.",
                          kind="danger")
    _fb2
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion({
        "🔓 Reference solutions (try the TODOs first!)": mo.md(
            r"""
    ```python
    # TODO 1
    ranked = df.assign(
        pos_rank=df.groupby("pos")["proj"]
                   .rank(ascending=False, method="first").astype(int)
    )

    # TODO 2
    _fig, _ax = plt.subplots(figsize=(8, 5))
    for _pos in ["QB", "RB", "WR", "TE"]:
        _d = ranked[(ranked.pos == _pos) & (ranked.pos_rank <= 40)].sort_values("pos_rank")
        _ax.plot(_d.pos_rank, _d.proj, label=_pos)
    _ax.set_xlabel("positional rank"); _ax.set_ylabel("projected points"); _ax.legend()
    scarcity_fig = _fig

    # TODO 3
    gaps = {
        pos: round(ranked.loc[(ranked.pos == pos) & (ranked.pos_rank == 1), "proj"].iloc[0]
                   - ranked.loc[(ranked.pos == pos) & (ranked.pos_rank == rank), "proj"].iloc[0])
        for pos, rank in BASELINE_RANK.items()
    }
    ```
    """
        )
    })
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    **Primary source:** [A Value-Based Draft Model — Fantasy Football Data Pros](https://www.fantasyfootballdatapros.com/blog/intermediate/5)
    (~20 min) — a pandas walkthrough of turning exactly this data into a draft model; the next
    lesson builds ours on your ESPN data.

    **Next lesson (today — draft is tomorrow, Sep 4!):** the full **VOR cheat sheet** — every
    player scored by value over replacement, merged with ADP to expose market mispricings.
    Tell your teacher your **draft slot** as soon as ESPN assigns it.

    New terms live in the [course glossary](reference/glossary.html). Stuck or curious about
    anything — the API payload, the pandas, why the flex was ignored? **Ask your teacher in
    the terminal.**
    """)
    return


if __name__ == "__main__":
    app.run()
