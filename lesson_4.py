# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "pandas",
#     "requests",
#     "pulp",
#     "mcp==2.1.1",
# ]
# ///

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Lesson 4 · The Draft as an Optimization Problem

    *Data-Driven Snake Drafting — run me with* `uvx marimo edit --sandbox lesson_4.py`

    Your cheat sheet ranks players. But a draft isn't "pick the best player" sixteen times —
    it's a **constrained sequential decision problem**:

    - You get exactly 16 picks at known pick numbers (your slot decides them).
    - The roster has **structure**: you must end with ~1–2 QB, 4+ RB, 4+ WR, 1–2 TE, 1 K, 1 DST.
    - A player is only choosable at a pick if the market hasn't taken him yet — and ADP tells
      you, probabilistically, when the market takes each player.

    That is, word for word, an **integer program (IP)**: binary decision variables, linear
    constraints, a linear objective. Today you meet the field's standard toolkit
    ([PuLP](https://coin-or.github.io/pulp/), which bundles the open-source CBC solver) and use
    it two ways:

    1. **Offline:** solve for your *perfect draft* — the best roster reachable from your slot
       if everyone else drafts by ADP.
    2. **Online (the widget):** during the live draft, opponents deviate from ADP — so we
       re-optimize greedily every pick using **opportunity cost**: take the player whose value
       *disappears* by your next pick, not the highest-VOR player.
    """)
    return


@app.cell
def _():
    import json

    import pandas as pd
    import pulp
    import requests

    import marimo as mo

    return json, mo, pd, pulp, requests


@app.cell
def _(json, pd, requests):
    URL = (
        "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/"
        "seasons/2026/segments/0/leaguedefaults/3"
    )
    POSITIONS = {1: "QB", 2: "RB", 3: "WR", 4: "TE", 5: "K", 16: "DST"}

    fantasy_filter = {
        "players": {
            "limit": 400,
            "sortDraftRanks": {
                "sortPriority": 1,
                "sortAsc": True,
                "value": "PPR",
            },
        }
    }
    resp = requests.get(
        URL,
        params={"view": "kona_player_info"},
        headers={"X-Fantasy-Filter": json.dumps(fantasy_filter)},
        timeout=30,
    )
    resp.raise_for_status()

    rows = []
    for _entry in resp.json()["players"]:
        _pl = _entry["player"]
        _weekly = [
            s["appliedTotal"]
            for s in _pl.get("stats", [])
            if s.get("seasonId") == 2026
            and s.get("statSourceId") == 1
            and s.get("statSplitTypeId") == 1
            and s.get("appliedTotal")
        ]
        _own = _pl.get("ownership") or {}
        rows.append(
            {
                "name": _pl["fullName"],
                "pos": POSITIONS.get(_pl["defaultPositionId"], "?"),
                "proj": sum(_weekly),
                "adp": _own.get("averageDraftPosition"),
            }
        )

    ranked = (
        pd.DataFrame(rows)
        .query("proj > 0")
        .dropna(subset=["adp"])
        .reset_index(drop=True)
    )
    ranked["pos_rank"] = (
        ranked.groupby("pos")["proj"]
        .rank(ascending=False, method="first")
        .astype(int)
    )

    BASELINE_RANK = {
        "QB": 13,
        "RB": 30,
        "WR": 30,
        "TE": 13,
        "K": 12,
        "DST": 12,
    }
    repl = {
        pos: ranked.loc[
            (ranked.pos == pos) & (ranked.pos_rank == rank), "proj"
        ].iloc[0]
        for pos, rank in BASELINE_RANK.items()
    }
    sheet = (
        ranked.assign(vor=ranked.proj - ranked.pos.map(repl))
        .sort_values("vor", ascending=False)
        .round({"proj": 0, "vor": 1, "adp": 1})
        .reset_index(drop=True)
    )
    return (sheet,)


@app.cell
def _(mo):
    slot = mo.ui.slider(1, 12, value=6, label="Your draft slot")
    slot
    return (slot,)


@app.cell
def _(slot):
    my_picks = [
        (r - 1) * 12 + slot.value if r % 2 == 1 else r * 12 - slot.value + 1
        for r in range(1, 17)
    ]
    my_picks
    return (my_picks,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Part A — the perfect draft, as an integer program

    **Decision variables:** $x_{p,r} \in \{0,1\}$ — "I take player $p$ with my $r$-th pick."
    We only *create* the variable when $p$ is plausibly available there
    (his ADP ≥ pick number − 3), which encodes the market model directly in the
    variable set.

    **Objective:** maximize $\sum_{p,r} \text{VOR}_p \cdot x_{p,r}$. VOR (not raw projection!)
    is what makes one objective work across positions — bench-depth players sit near zero, so
    the optimizer naturally spends early picks where replacement is far away.

    **Constraints:** exactly one player per pick; each player at most once; and the roster
    shape — which is **your TODO**. Define `ROSTER_LIMITS`: a dict mapping each position to a
    `(min, max)` tuple across your 16 picks. Sensible bounds: 1–2 QB, 4–7 RB, 4–7 WR, 1–2 TE,
    exactly 1 K, exactly 1 DST. (Sanity: the mins must sum ≤ 16 and the maxes ≥ 16, or the
    program is infeasible — the solver will tell you!)
    """)
    return


@app.cell
def _():
    ROSTER_LIMITS = {
        "QB": (1, 2),
        "RB": (4, 7),
        "WR": (4, 7),
        "TE": (1, 2),
        "K": (1, 1),
        "DST": (1, 1),
    }
    return (ROSTER_LIMITS,)


@app.cell(hide_code=True)
def _(ROSTER_LIMITS, mo):
    if ROSTER_LIMITS is None:
        _out = mo.callout(
            "⏳ Define ROSTER_LIMITS above — the solver below waits for you.",
            kind="neutral",
        )
    elif set(ROSTER_LIMITS) != {"QB", "RB", "WR", "TE", "K", "DST"}:
        _out = mo.callout(
            "✗ Cover exactly the six positions: QB, RB, WR, TE, K, DST.",
            kind="danger",
        )
    else:
        _lo = sum(v[0] for v in ROSTER_LIMITS.values())
        _hi = sum(v[1] for v in ROSTER_LIMITS.values())
        _ok = (
            _lo <= 16 <= _hi
            and ROSTER_LIMITS["K"] == (1, 1)
            and ROSTER_LIMITS["DST"] == (1, 1)
            and all(v[0] <= v[1] for v in ROSTER_LIMITS.values())
        )
        _out = (
            mo.callout(
                f"✓ Feasible shape: mins sum to {_lo} ≤ 16 ≤ {_hi} (maxes). "
                "Solver is running below.",
                kind="success",
            )
            if _ok
            else mo.callout(
                f"✗ Infeasible or off-spec: mins sum {_lo}, maxes sum {_hi} "
                "(need mins ≤ 16 ≤ maxes), K and DST exactly (1, 1), min ≤ max.",
                kind="danger",
            )
        )
    _out
    return


@app.cell
def _(ROSTER_LIMITS, my_picks, pulp, sheet):
    if ROSTER_LIMITS is None:
        best_roster = None
    else:
        _pool = sheet[sheet.adp <= 220].reset_index(drop=True)
        _players = _pool.to_dict("records")

        _prob = pulp.LpProblem("perfect_draft", pulp.LpMaximize)
        _x = {
            (i, r): pulp.LpVariable(f"x_{i}_{r}", cat="Binary")
            for i, _p in enumerate(_players)
            for r, _pk in enumerate(my_picks)
            if _p["adp"] >= _pk - 3
        }

        _prob += pulp.lpSum(_players[i]["vor"] * v for (i, r), v in _x.items())
        for _r in range(16):
            _prob += (
                pulp.lpSum(v for (i, rr), v in _x.items() if rr == _r) == 1
            )
        for _i in range(len(_players)):
            _vars = [v for (ii, r), v in _x.items() if ii == _i]
            if _vars:
                _prob += pulp.lpSum(_vars) <= 1
        for _pos, (_lo2, _hi2) in ROSTER_LIMITS.items():
            _pvars = [
                v for (i, r), v in _x.items() if _players[i]["pos"] == _pos
            ]
            _prob += pulp.lpSum(_pvars) >= _lo2
            _prob += pulp.lpSum(_pvars) <= _hi2

        _prob.solve(pulp.PULP_CBC_CMD(msg=0))
        best_roster = sorted(
            (
                {"rd": r + 1, "pick": my_picks[r], **_players[i]}
                for (i, r), v in _x.items()
                if v.value() == 1
            ),
            key=lambda d: d["rd"],
        )
    return (best_roster,)


@app.cell(hide_code=True)
def _(best_roster, mo, pd):
    if best_roster is None:
        _view = mo.callout("⏳ Waiting on ROSTER_LIMITS.", kind="neutral")
    else:
        _df = pd.DataFrame(best_roster)[
            ["rd", "pick", "name", "pos", "proj", "vor", "adp"]
        ]
        _view = mo.vstack(
            [
                mo.md(
                    f"### Your perfect draft from this slot — total VOR {_df.vor.sum():.0f}"
                ),
                mo.ui.table(_df, page_size=16),
                mo.md(
                    "Look at *where the solver put each position*. Nobody told it 'K and DST "
                    "last' or 'RB/WR early' — those rules **fall out of the optimization**. "
                    "Your quick-reference heuristics are the solver's optimal policy, rediscovered."
                ),
            ]
        )
    _view
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Part B — the live draft widget 🎛️

    The perfect draft assumes everyone follows ADP. Live, they won't — so we **re-optimize every
    pick** with a one-step lookahead. For each position:

    $$\text{dropoff} = \text{best VOR available now} - \text{best VOR likely available at your next pick}$$

    Take from the position where value is *evaporating*; skip the position that will wait for
    you. (Q2 below makes you prove to yourself why this beats "highest VOR now".)

    **During the draft:** every time anyone picks, add the player to *Drafted by others* — or to
    *My picks* when it's yours. Everything recomputes instantly: recommendations, roster needs,
    and the best-available board. Both boxes are searchable — type a few letters.
    """)
    return


@app.cell
def _(mo, sheet):
    _opts = {
        f"{p['name']}  ·  {p['pos']}  ·  ADP {p['adp']}": p["name"]
        for p in sheet.sort_values("adp").to_dict("records")
    }
    gone = mo.ui.multiselect(options=_opts, label="🚫 Drafted by others")
    mine = mo.ui.multiselect(
        options=_opts, label="✅ My picks", max_selections=16
    )
    mo.vstack([gone, mine])
    return gone, mine


@app.cell(hide_code=True)
def _(gone, mine, mo, my_picks, pd, sheet):
    _taken = set(gone.value) | set(mine.value)
    _avail = sheet[~sheet.name.isin(_taken)]
    _overall = len(_taken) + 1
    _upcoming = [p for p in my_picks if p >= _overall] or [my_picks[-1]]
    _now_pk = _upcoming[0]
    _next_pk = _upcoming[1] if len(_upcoming) > 1 else _now_pk + 12

    _caps = {"QB": 2, "RB": 6, "WR": 6, "TE": 2, "K": 1, "DST": 1}
    _have = {
        pos: sum(
            1
            for n in mine.value
            if sheet.loc[sheet.name == n, "pos"].iloc[0] == pos
        )
        for pos in _caps
    }
    _rounds_left = len(_upcoming)

    _recs = []
    for _pos, _cap in _caps.items():
        if _have[_pos] >= _cap:
            continue
        if _pos in ("K", "DST") and _rounds_left > 2:
            continue
        _pool = _avail[_avail.pos == _pos]
        if _pool.empty:
            continue
        _best_now = _pool.iloc[0]
        _later = _pool[_pool.adp >= _next_pk - 2]
        _best_later_vor = _later.vor.max() if not _later.empty else 0.0
        _recs.append(
            {
                "pos": _pos,
                "take now": _best_now["name"],
                "vor now": round(_best_now.vor, 1),
                "vor at next pick": round(_best_later_vor, 1),
                "dropoff": round(_best_now.vor - _best_later_vor, 1),
            }
        )
    _recs.sort(key=lambda d: -d["dropoff"])

    _roster_line = " · ".join(f"{p} {_have[p]}/{c}" for p, c in _caps.items())
    if _recs:
        _top = _recs[0]
        _headline = (
            f"### 👉 Pick {_now_pk} (next: {_next_pk}): take **{_top['take now']}** "
            f"({_top['pos']}) — {_top['dropoff']:.0f} VOR vanishes by your next pick"
        )
    else:
        _headline = "### Roster full — enjoy the show."

    _panel = mo.vstack(
        [
            mo.md(_headline),
            mo.md(
                f"**Roster:** {_roster_line} &nbsp;·&nbsp; picks left: {_rounds_left}"
            ),
            mo.ui.table(
                pd.DataFrame(_recs),
                page_size=6,
                label="Dropoff board (sorted by urgency)",
            ),
            mo.ui.table(
                _avail.head(15)[
                    ["name", "pos", "pos_rank", "proj", "vor", "adp"]
                ],
                page_size=15,
                label="Best available by VOR",
            ),
        ]
    )
    _panel
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Check yourself
    """)
    return


@app.cell
def _(mo):
    q_ilp = mo.ui.radio(
        options=[
            "player p is still available at my pick r",
            "player p is chosen with my r-th pick",
            "player p is ranked r-th on my sheet",
        ],
        label="**Q1.** In Part A's integer program, $x_{p,r} = 1$ means…",
    )
    q_ilp
    return (q_ilp,)


@app.cell(hide_code=True)
def _(mo, q_ilp):
    if q_ilp.value is None:
        _fb = mo.callout("Pick an answer.", kind="neutral")
    elif q_ilp.value == "player p is chosen with my r-th pick":
        _fb = mo.callout(
            "✓ It's a *decision* variable — the solver's choice, not a fact about "
            "the world. Availability lives in which (p, r) variables we created; "
            "rank lives in the objective coefficients.",
            kind="success",
        )
    else:
        _fb = mo.callout(
            "✗ x is the solver's *decision*: 'take p at my r-th pick'. Availability "
            "was encoded by only creating variables where ADP ≥ pick − 3; VOR rank "
            "enters through the objective, not the variables.",
            kind="danger",
        )
    _fb
    return


@app.cell
def _(mo):
    q_opp = mo.ui.radio(
        options=[
            "the RB — highest VOR on the board wins",
            "the WR — waiting on WR costs 17 points",
            "either — both plans total the same VOR",
        ],
        label="**Q2.** Best RB now: VOR 80 (drops to 72 by your next pick). Best WR now: "
        "VOR 75 (drops to 50). One pick now, one at your next turn. Who now?",
    )
    q_opp
    return (q_opp,)


@app.cell(hide_code=True)
def _(mo, q_opp):
    if q_opp.value is None:
        _fb2 = mo.callout("Pick an answer.", kind="neutral")
    elif q_opp.value == "the WR — waiting on WR costs 17 points":
        _fb2 = mo.callout(
            "✓ WR now + RB later = 75 + 72 = **147**. RB now + WR later = 80 + 50 "
            "= 130. The 5-point 'best player' sacrifice buys back 22 at the next "
            "pick. That's the whole widget in one arithmetic line.",
            kind="success",
        )
    else:
        _fb2 = mo.callout(
            "✗ Do the two-pick totals: WR-then-RB = 75 + 72 = 147; RB-then-WR = "
            "80 + 50 = 130. Greedy-by-VOR leaves 17 points on the table — dropoff, "
            "not raw VOR, decides the position.",
            kind="danger",
        )
    _fb2
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "🔓 TODO solution": mo.md(r"""
    ```python
    ROSTER_LIMITS = {
        "QB": (1, 2), "RB": (4, 7), "WR": (4, 7),
        "TE": (1, 2), "K": (1, 1), "DST": (1, 1),
    }
    ```
    """)
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    **What you just learned, DS-wise:** framing a domain problem as an IP (decision variables /
    constraints / objective), encoding a market model in the *variable set*, why a
    replacement-adjusted objective makes cross-category tradeoffs solvable, and one-step-lookahead
    greedy re-optimization when reality deviates from the model. These transfer to scheduling,
    budgeting, logistics — anything with "pick under constraints over time."

    **Primary source:** [PuLP documentation](https://coin-or.github.io/pulp/) for the modeling
    API, and [dlm1223's snake-draft optimization repo](https://github.com/dlm1223/fantasy-football)
    to see a fuller formulation (ours is deliberately minimal).

    **Tonight:** widget open, [quick reference](reference/draft-day-quick-reference.html) printed,
    slot slider set. Log every pick in the widget. **After: bring me your roster for the retro.**
    Post-draft roadmap: Monte-Carlo-simulate the opponents (replace the ±3 availability rule with
    a probability model), then compare what the simulation-aware optimizer would have drafted
    against what you actually did. Questions any time — good luck! 🏈
    """)
    return


if __name__ == "__main__":
    app.run()
