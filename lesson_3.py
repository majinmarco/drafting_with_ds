# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "pandas",
#     "requests",
# ]
# ///

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Lesson 3 · The VOR Cheat Sheet

    *Data-Driven Snake Drafting — draft day. Run me with* `uvx marimo edit --sandbox lesson_3.py`

    Yesterday you measured the top-vs-last-starter **gaps**. Today you generalize them: instead
    of scoring only the top player at each position, score **every** player by

    $$\text{VOR} = \text{projection} - \text{replacement level at his position}$$

    VOR puts a QB, an RB, and a TE on **one scale**, which is exactly what a draft pick demands:
    every pick is a choice *between positions*.

    ### The one modeling decision: where is "replacement level"?

    Yesterday we used the last starter (QB12, RB24, WR24, TE12) and ignored the FLEX. Here's the
    promised why-it-matters: the 12 FLEX slots are filled by the best *leftover* RB/WR/TEs, so the
    true "last starter" sits deeper — league-wide, FLEX spots historically go mostly to RBs and
    WRs. And because benches hold backups, the player you could actually grab off waivers sits
    deeper still. There is no single right answer — **the baseline is a modeling choice, and your
    cheat sheet is only as good as it**. So this notebook makes the baselines *sliders*: drag one
    and watch the whole sheet re-rank. That sensitivity you feel is the lesson.
    """)
    return


@app.cell
def _():
    import json
    from pathlib import Path

    import pandas as pd
    import requests

    import marimo as mo

    return Path, json, mo, pd, requests


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 1 — fresh data (ADP moves daily; on draft day, pull live)
    """)
    return


@app.cell
def _(json, requests):
    URL = ("https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/"
           "seasons/2026/segments/0/leaguedefaults/3")
    POSITIONS = {1: "QB", 2: "RB", 3: "WR", 4: "TE", 5: "K", 16: "DST"}

    fantasy_filter = {"players": {
        "limit": 400,
        "sortDraftRanks": {"sortPriority": 1, "sortAsc": True, "value": "PPR"},
    }}
    resp = requests.get(URL, params={"view": "kona_player_info"},
                        headers={"X-Fantasy-Filter": json.dumps(fantasy_filter)},
                        timeout=30)
    resp.raise_for_status()
    return POSITIONS, resp


@app.cell
def _(POSITIONS, pd, resp):
    rows = []
    for _entry in resp.json()["players"]:
        _pl = _entry["player"]
        _weekly = [s["appliedTotal"] for s in _pl.get("stats", [])
                   if s.get("seasonId") == 2026
                   and s.get("statSourceId") == 1
                   and s.get("statSplitTypeId") == 1
                   and s.get("appliedTotal")]
        _own = _pl.get("ownership") or {}
        rows.append({
            "name": _pl["fullName"],
            "pos": POSITIONS.get(_pl["defaultPositionId"], "?"),
            "proj": sum(_weekly),
            "adp": _own.get("averageDraftPosition"),
        })

    ranked = (pd.DataFrame(rows)
                .query("proj > 0")
                .dropna(subset=["adp"])
                .reset_index(drop=True))
    ranked["pos_rank"] = (ranked.groupby("pos")["proj"]
                                .rank(ascending=False, method="first").astype(int))
    return (ranked,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 2 — set the baselines

    Defaults are flex-and-bench-aware: QB **13** (streamers make QB13 free), RB **30** / WR **30**
    (24 starters + most of the 12 FLEX slots + early waiver churn), TE **13**, K/DST **12**
    (everyone streams those). Drag and watch Step 3 re-rank — notice how much the QB/TE order
    moves and how little the top RBs/WRs care.
    """)
    return


@app.cell
def _(mo):
    base_qb = mo.ui.slider(10, 20, value=13, label="QB baseline rank")
    base_rb = mo.ui.slider(24, 45, value=30, label="RB baseline rank")
    base_wr = mo.ui.slider(24, 45, value=30, label="WR baseline rank")
    base_te = mo.ui.slider(10, 20, value=13, label="TE baseline rank")
    mo.vstack([base_qb, base_rb, base_wr, base_te])
    return base_qb, base_rb, base_te, base_wr


@app.cell
def _(base_qb, base_rb, base_te, base_wr, ranked):
    BASELINE_RANK = {"QB": base_qb.value, "RB": base_rb.value,
                     "WR": base_wr.value, "TE": base_te.value,
                     "K": 12, "DST": 12}

    # replacement-level projection for each position, at the chosen rank
    repl = {pos: ranked.loc[(ranked.pos == pos) & (ranked.pos_rank == rank), "proj"].iloc[0]
            for pos, rank in BASELINE_RANK.items()}
    repl
    return (repl,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 3 — YOUR TODO (the only one today): score every player

    Build `cheat`: a copy of `ranked` with a `vor` column — each player's `proj` minus his
    position's replacement projection from `repl`.
    *Hint: `ranked.pos.map(repl)` broadcasts the dict across the column.*
    Solution in the accordion at the bottom if the clock is ticking.
    """)
    return


@app.cell
def _(ranked, repl):
    ranked['repl'] = ranked.pos.map(repl)
    ranked
    return


@app.cell
def _(ranked):
    cheat = ranked.assign(vor=ranked['proj'] - ranked['repl'])
    return (cheat,)


@app.cell(hide_code=True)
def _(cheat, mo, ranked, repl):
    if cheat is None:
        _out = mo.callout("⏳ Complete the TODO — everything below lights up when you do.",
                          kind="neutral")
    elif "vor" not in cheat.columns:
        _out = mo.callout("✗ `cheat` needs a `vor` column.", kind="danger")
    else:
        _rb1 = ranked.loc[(ranked.pos == "RB") & (ranked.pos_rank == 1)].iloc[0]
        _want = _rb1.proj - repl["RB"]
        _got = cheat.loc[cheat.name == _rb1["name"], "vor"].iloc[0]
        _out = (mo.callout(f"✓ Correct — {_rb1['name']}'s VOR is {_got:.0f} "
                           f"(= {_rb1.proj:.0f} − replacement {repl['RB']:.0f}).", kind="success")
                if abs(_got - _want) < 0.5 else
                mo.callout(f"✗ {_rb1['name']}'s VOR should be {_want:.0f}; got {_got:.0f}. "
                           "Subtract each player's own position's replacement projection.",
                           kind="danger"))
    _out
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 4 — the cheat sheet

    Sorted by VOR. `edge = adp − vor_rank`: **positive** means the market drafts him *later* than
    his value warrants (target him — he'll likely still be there); **negative** means the market
    pays more than value (let someone else reach). Sort/filter the table live during your draft.
    """)
    return


@app.cell
def _(cheat, mo):
    if cheat is None:
        _view = mo.callout("⏳ Waiting on the TODO above.", kind="neutral")
        sheet = None
    else:
        sheet = (cheat.assign(vor_rank=cheat.vor.rank(ascending=False).astype(int),
                              rnd=((cheat.adp - 1) // 12 + 1).astype(int))
                      .sort_values("vor", ascending=False)
                      .round({"proj": 0, "vor": 0, "adp": 1})
                      [["name", "pos", "pos_rank", "proj", "vor", "vor_rank", "adp", "rnd"]])
        sheet = sheet.assign(edge=(sheet.adp - sheet.vor_rank).round(0))
        _view = mo.ui.table(sheet, page_size=25)
    _view
    return (sheet,)


@app.cell
def _(Path, mo, sheet):
    if sheet is not None:
        Path("data").mkdir(exist_ok=True)
        sheet.to_csv(Path("data") / "cheat_sheet_2026.csv", index=False)
        _msg = mo.md("💾 Saved **`data/cheat_sheet_2026.csv`** — your printable backup.")
    else:
        _msg = mo.md("")
    _msg
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 5 — your slot, your plan

    Set your slot when ESPN assigns it. For each of your 16 picks this shows the best players
    (by VOR) likely still available — "likely available" = ADP no more than 3 picks earlier
    than your pick. K/DST are hidden until your last two rounds, where they belong.
    """)
    return


@app.cell
def _(mo):
    slot = mo.ui.slider(1, 12, value=6, label="Your draft slot")
    slot
    return (slot,)


@app.cell(hide_code=True)
def _(mo, sheet, slot):
    if sheet is None:
        _plan = mo.callout("⏳ Waiting on the TODO above.", kind="neutral")
    else:
        _lines = ["| Rd | Pick | Best likely available (VOR / ADP) |",
                  "|---:|-----:|:----------------------------------|"]
        for _r in range(1, 17):
            _p = (_r - 1) * 12 + slot.value if _r % 2 == 1 else _r * 12 - slot.value + 1
            _pool = sheet[sheet.adp >= _p - 3]
            if _r < 15:
                _pool = _pool[~_pool.pos.isin(["K", "DST"])]
            _top = _pool.nlargest(4, "vor")
            _cands = " · ".join(f"{_row['name']} {_row.pos} ({_row.vor:.0f} / {_row.adp})"
                                for _, _row in _top.iterrows())
            _lines.append(f"| {_r} | {_p} | {_cands} |")
        _plan = mo.md("\n".join(_lines))
    _plan
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Check yourself
    """)
    return


@app.cell
def _(mo):
    q_baseline = mo.ui.radio(
        options=[
            "it fixes which position gets drafted first overall",
            "it sets the zero point that all value is measured from",
            "it decides how many players your league will draft",
        ],
        label="**Q1.** Why is the baseline rank *the* modeling decision in a VOR system?",
    )
    q_baseline
    return (q_baseline,)


@app.cell(hide_code=True)
def _(mo, q_baseline):
    if q_baseline.value is None:
        _fb = mo.callout("Pick an answer.", kind="neutral")
    elif q_baseline.value == "it sets the zero point that all value is measured from":
        _fb = mo.callout("✓ Every VOR is measured against it — move a baseline and entire "
                         "positions rise or fall together, as your sliders showed.", kind="success")
    else:
        _fb = mo.callout("✗ Drag a slider and watch: the baseline is the zero point all value is "
                         "measured from, so changing it re-prices a whole position.", kind="danger")
    _fb
    return


@app.cell
def _(mo):
    q_edge2 = mo.ui.radio(
        options=[
            "draft him near his ADP, not his VOR rank",
            "draft him right now with your current pick",
            "avoid him because the market knows something",
        ],
        label="**Q2.** A player's VOR rank is 18 but his ADP is 41 (edge +23). Best play?",
    )
    q_edge2
    return (q_edge2,)


@app.cell(hide_code=True)
def _(mo, q_edge2):
    if q_edge2.value is None:
        _fb2 = mo.callout("Pick an answer.", kind="neutral")
    elif q_edge2.value == "draft him near his ADP, not his VOR rank":
        _fb2 = mo.callout("✓ The market will hand him to you ~2 rounds after his value rank — "
                          "taking him at pick 18 pays retail for what goes on sale at 41. Wait, "
                          "and spend pick 18 on value the market prices correctly.", kind="success")
    else:
        _fb2 = mo.callout("✗ Positive edge means the market underprices him — you exploit it by "
                          "waiting until near his ADP, banking other value first. (And projections "
                          "already fold in the news the market has.)", kind="danger")
    _fb2
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion({
        "🔓 TODO solution": mo.md(r"""
    ```python
    cheat = ranked.assign(vor=ranked.proj - ranked.pos.map(repl))
    ```
    """)
    })
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    **Primary source:** [Winning Fantasy Football with Projections, VOR, and Value-Based
    Drafting — Fantasy Football Analytics](https://fantasyfootballanalytics.net/2024/08/winning-fantasy-football-with-projections-value-over-replacement-and-value-based-drafting.html)
    — the rigorous version of exactly what you just built, including baseline choices.

    **For the draft itself:** print `reference/draft-day-quick-reference.html` (or keep it open) —
    the compressed rules for tonight. Keep this notebook open with the table sorted by VOR, and
    cross players off as they're drafted (the search box in the table works well).

    **After the draft:** tell your teacher your full roster and slot. We'll do a retro — where you
    beat the market, where you paid retail — and it becomes the springboard for the simulation and
    optimization lessons. Good luck. 🏈 Questions any time in the terminal.
    """)
    return


if __name__ == "__main__":
    app.run()
