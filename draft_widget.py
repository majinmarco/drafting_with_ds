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
    # 🏈 Live Draft Widget

    Standalone draft-day tool (no lesson, no TODOs). Run: `uvx marimo edit --sandbox draft_widget.py`

    Set your **slot**, then log every pick as it happens — 🚫 for anyone else's, ✅ for yours.
    The recommendation, dropoff board, roster tracker, and best-available board update instantly.
    Fresh ESPN projections + ADP are pulled each time the notebook starts; VOR baselines:
    QB13 / RB30 / WR30 / TE13 / K12 / DST12 (see `lesson_3.py` to tune them).
    """)
    return


@app.cell
def _():
    import json

    import pandas as pd
    import requests

    import marimo as mo

    return json, mo, pd, requests


@app.cell
def _(json, pd, requests):
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

    BASELINE_RANK = {"QB": 13, "RB": 30, "WR": 30, "TE": 13, "K": 12, "DST": 12}
    repl = {pos: ranked.loc[(ranked.pos == pos) & (ranked.pos_rank == rank), "proj"].iloc[0]
            for pos, rank in BASELINE_RANK.items()}
    sheet = (ranked.assign(vor=ranked.proj - ranked.pos.map(repl))
                   .sort_values("vor", ascending=False)
                   .round({"proj": 0, "vor": 1, "adp": 1})
                   .reset_index(drop=True))
    return (sheet,)


@app.cell
def _(mo):
    slot = mo.ui.slider(1, 12, value=6, label="Your draft slot")
    slot
    return (slot,)


@app.cell
def _(slot):
    my_picks = [(r - 1) * 12 + slot.value if r % 2 == 1 else r * 12 - slot.value + 1
                for r in range(1, 17)]
    return (my_picks,)


@app.cell
def _(mo, sheet):
    _opts = {f"{p['name']}  ·  {p['pos']}  ·  ADP {p['adp']}": p["name"]
             for p in sheet.sort_values("adp").to_dict("records")}
    gone = mo.ui.multiselect(options=_opts, label="🚫 Drafted by others")
    mine = mo.ui.multiselect(options=_opts, label="✅ My picks", max_selections=16)
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
    _have = {pos: sum(1 for n in mine.value
                      if sheet.loc[sheet.name == n, "pos"].iloc[0] == pos)
             for pos in _caps}
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
        _recs.append({"pos": _pos, "take now": _best_now["name"],
                      "vor now": round(_best_now.vor, 1),
                      "vor at next pick": round(_best_later_vor, 1),
                      "dropoff": round(_best_now.vor - _best_later_vor, 1)})
    _recs.sort(key=lambda d: -d["dropoff"])

    _roster_line = " · ".join(f"{p} {_have[p]}/{c}" for p, c in _caps.items())
    if _recs:
        _top = _recs[0]
        _headline = (f"### 👉 Pick {_now_pk} (next: {_next_pk}): take **{_top['take now']}** "
                     f"({_top['pos']}) — {_top['dropoff']:.0f} VOR vanishes by your next pick")
    else:
        _headline = "### Roster full — enjoy the show."

    _panel = mo.vstack([
        mo.md(_headline),
        mo.md(f"**Roster:** {_roster_line} &nbsp;·&nbsp; picks left: {_rounds_left}"),
        mo.ui.table(pd.DataFrame(_recs), page_size=6,
                    label="Dropoff board (sorted by urgency)"),
        mo.ui.table(_avail.head(20)[["name", "pos", "pos_rank", "proj", "vor", "adp"]],
                    page_size=20, label="Best available by VOR"),
    ])
    _panel
    return


@app.cell(hide_code=True)
def _(mine, mo, sheet):
    if mine.value:
        _my = sheet[sheet.name.isin(mine.value)][["name", "pos", "proj", "vor", "adp"]]
        _out = mo.vstack([mo.md(f"### My team ({len(_my)}/16) — total VOR {_my.vor.sum():.0f}"),
                          mo.ui.table(_my, page_size=16)])
    else:
        _out = mo.md("*Your picks will appear here.*")
    _out
    return


if __name__ == "__main__":
    app.run()
