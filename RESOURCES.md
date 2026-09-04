# Data-Driven Fantasy Drafting Resources

## Knowledge

- [Article: "Winning Fantasy Football with Projections, VOR, and Value-Based Drafting" — Fantasy Football Analytics](https://fantasyfootballanalytics.net/2024/08/winning-fantasy-football-with-projections-value-over-replacement-and-value-based-drafting.html)
  The canonical quantitative treatment of VOR/VBD, by the most statistically rigorous fantasy site. Use for: replacement baselines, why VOR beats raw projections.
- [App: Fantasy Football Snake Draft Optimizer — Fantasy Football Analytics](https://fantasyfootballanalytics.net/apps/fantasy-football-snake-draft-optimizer)
  A working reference implementation of what we're building. Use for: sanity-checking our own optimizer's outputs.
- [Article: "Snake Value Based Drafting" — Subvertadown](https://subvertadown.com/article/fantasy-snake-drafts-and-strategizing-for-scarcity----snake-value-based-drafting)
  Scarcity-aware VBD specifically for snake drafts. Use for: how snake position changes value math.
- [Tutorial: "A Value-Based Draft Model" — Fantasy Football Data Pros](https://www.fantasyfootballdatapros.com/blog/intermediate/5)
  Pandas walkthrough of building a VBD model. Use for: lesson code scaffolding on VOR computation.
- [Library: nfl_data_py / nflreadpy (nflverse)](https://github.com/nflverse/nfl_data_py)
  Free, well-maintained Python access to NFL play-by-play, weekly, seasonal, roster, and ID-mapping data. Prefer [nflreadpy](https://nflreadpy.nflverse.com/) (the maintained successor). Use for: all historical stat pulls.
- [Repo: dlm1223/fantasy-football — Snake Draft Optimization](https://github.com/dlm1223/fantasy-football)
  Optimization code for snake drafts (LP + simulation). Use for: the optimization lessons.
- [Docs: PuLP — linear/integer programming in Python](https://coin-or.github.io/pulp/)
  The COIN-OR modeling library (bundled CBC solver) used in the optimization lessons. Use for: LpProblem/LpVariable syntax, solver options.
- [Paper: "Drafting strategies in fantasy football: a study of competitive sequential human decision making" (Judgment & Decision Making)](https://www.sas.upenn.edu/~baron/journal/22/220318/jdm220318.html)
  Peer-reviewed study of how real drafters behave (and err). Use for: modeling opponents in simulations.
- [API: ESPN Fantasy public read API (`leaguedefaults/3`, `kona_player_info` view)](https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2026/segments/0/leaguedefaults/3?view=kona_player_info)
  Verified working Sep 2, 2026, no auth: 2026 weekly projections + ADP in Marco's exact league scoring. Use for: all lesson data pulls (`code/pull_espn_data.py`).
- [ESPN: Fantasy Football 101 — Settings](https://www.espn.com/fantasy/football/story/_/id/19540805/fantasy-football-101-settings)
  Official reference for ESPN scoring/roster defaults. Use for: grounding the league-rules lesson.
- [ESPN: 2026 Cheat Sheet Central (rankings, PPR)](https://www.espn.com/fantasy/football/story/_/page/FFCheatSheetCent26-48640423/2026-fantasy-football-rankings-cheat-sheet-depth-charts-ppr)
  Current-season consensus rankings and ADP context on Marco's own platform. Use for: live 2026 player data context.

## Wisdom (Communities)

- [r/fantasyfootball](https://reddit.com/r/fantasyfootball)
  Largest, well-moderated fantasy community; strong weekly threads. Use for: league-settings questions, draft-grade feedback.
- Mock draft lobbies (ESPN Mock Draft Lobby, FantasyPros Draft Wizard simulator)
  Not a forum but the real practice arena: free live mock drafts against humans/bots. Use for: rehearsing strategy before draft day.

## Gaps

- ~~A free 2026 projections + ADP dataset~~ **Resolved Sep 2:** ESPN's public API (above). Note: FantasyPros tables are now JS-rendered; `pandas.read_html` only gets 10-row previews — don't build on scraping them.
- A high-trust source on **Monte Carlo draft simulation methodology** beyond blog posts (the Medium post found was thin; the UPenn paper covers behavior, not simulation design).
