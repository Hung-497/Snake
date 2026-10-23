"""Write a Bot Report as an HTML page that anyone can read.

The page states each group's result in plain words, ranks the bots, shows how
their games ended as one histogram per bot, lets the reader compare any two
bots, and keeps every number in tables for developers. It has a light and a
dark theme and uses system fonts, so it works offline. Everything is written
into the page; the small script only adds the theme switch, the hover line on
the histograms, and the comparison picker.
"""

from html import escape
import json

from snake.analysis import ReportColors
from snake.analysis.BotReport import (
    COMPARISON_HEADINGS, NOT_EVALUATED_SENTENCE, ONE_BOT_SENTENCE, OVERVIEW_HEADINGS,
    PROVENANCE_HEADINGS, bin_count, ranking_rows, reading_notes, row_cells, source_sentence,
)
from snake.analysis.ScoreChart import BIN_WIDTH, axis_ticks, bin_label, score_bins
from snake.bots.BotModeCatalogue import BOT_MODES


FAMILIES_BY_LABEL = {mode.label: mode.family for mode in BOT_MODES}

# What each number means, for readers who are new to the project.
TERMS = (
    ("Average", "Total food eaten across all games, divided by the number of games. "
                "The headline number, but it hides bad games."),
    ("Median", "The middle game: half the games scored less, half scored more. Far from "
               "the average means a few very good or very bad games."),
    ("Histogram", "Across is the score a game ended with, in ranges of 10; up is how many "
                  "games ended there. Hover over a bar to read its count."),
    ("Stopped by limit", "Share of games still running when the move limit ran out. A "
                         "high value means the bot survives but eats slowly."),
    ("Moves per food", "Moves needed for each piece of food. Lower is faster. Hand-written "
                       "bots chase food directly; learned bots play safer and slower."),
    ("95% range", "Where the real difference between two bots most likely lies if they "
                  "played other games. If the whole range is above zero, the lead is reliable."),
)

LIGHT = {"ground": "#F6F7F9", "surface": "#FFFFFF", "ink": "#14171C",
         "muted": ReportColors.LIGHT_TEXT_MUTED, "line": "#E1E4E9", "soft": "#EEF0F3"}
DARK = {"ground": "#0D0F12", "surface": "#161A1F", "ink": "#ECEEF2",
        "muted": "#A3AAB6", "line": "#262B33", "soft": "#1E2329"}


def tokens(theme):
    return " ".join(f"--{name}: {value};" for name, value in theme.items())


PAGE_STYLE = f"""
:root {{ color-scheme: light; {tokens(LIGHT)} }}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{ color-scheme: dark; {tokens(DARK)} }}
}}
:root[data-theme="dark"] {{ color-scheme: dark; {tokens(DARK)} }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--ground); color: var(--ink);
  font: 16px/1.6 ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  font-variant-numeric: tabular-nums; transition: background-color .25s ease, color .25s ease; }}
main {{ max-width: 1120px; margin: 0 auto; padding: 28px 24px 96px; }}
h1, h2, h3 {{ letter-spacing: -0.02em; line-height: 1.1; }}
h1 {{ font-size: 18px; margin: 0; letter-spacing: 0; }}
h2 {{ font-size: clamp(32px, 5vw, 54px); margin: 6px 0 14px; max-width: 22ch; }}
h3 {{ font-size: 26px; margin: 0 0 6px; }}
h4 {{ font-size: 15px; margin: 22px 0 10px; color: var(--muted); }}
p {{ margin: 0; }}
.muted {{ color: var(--muted); }}
.top {{ display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center;
  gap: 16px; }}
.brand {{ display: flex; align-items: center; gap: 12px; }}
.theme-toggle {{ font: inherit; font-size: 14px; color: var(--ink); background: var(--surface);
  border: 1px solid var(--line); border-radius: 999px; padding: 10px 18px; min-height: 44px;
  cursor: pointer; }}
.lede {{ margin-top: 28px; font-size: 18px; color: var(--muted); max-width: 64ch; }}
section.group {{ margin-top: 72px; display: flex; flex-direction: column; gap: 56px; }}
.part {{ display: flex; flex-direction: column; gap: 16px; }}
.part > p {{ color: var(--muted); max-width: 70ch; }}
.card {{ background: var(--surface); border: 1px solid var(--line); border-radius: 16px;
  padding: 24px 28px; }}
.conditions {{ font-size: 14px; color: var(--muted); }}
.swatch {{ display: inline-block; width: 10px; height: 10px; border-radius: 3px;
  background: var(--bot); flex: none; }}
.ranking {{ display: flex; flex-direction: column; gap: 14px; }}
.rank {{ display: flex; flex-wrap: wrap; align-items: center; gap: 6px 16px; }}
.rank .name {{ flex: 0 0 160px; display: flex; align-items: center; gap: 10px; font-weight: 600; }}
.rank .track {{ flex: 1 1 320px; display: flex; align-items: center; gap: 12px; min-width: 0; }}
.rank .lane {{ flex: 1; height: 26px; background: var(--soft); border-radius: 6px; overflow: hidden; }}
.rank .fill {{ height: 100%; background: var(--bot); border-radius: 6px; transform-origin: left center;
  animation: grow .9s cubic-bezier(.2,.8,.2,1) both; }}
.rank .value {{ width: 60px; text-align: right; font-weight: 600; font-size: 18px;
  animation: rise .5s ease-out both; }}
.rank .newest {{ font-size: 12px; font-weight: 600; padding: 1px 8px; border-radius: 999px;
  background: var(--ink); color: var(--surface); }}
.rank .kind {{ flex: 0 0 112px; text-align: center; font-size: 13px; color: var(--muted);
  padding: 2px 10px; border-radius: 999px; border: 1px solid var(--line); }}
@keyframes grow {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: none; }} }}
.histograms {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }}
.histogram {{ background: var(--surface); border: 1px solid var(--line); border-radius: 14px;
  padding: 16px 18px 12px; display: flex; flex-direction: column; gap: 6px; }}
.histogram .head {{ display: flex; justify-content: space-between; align-items: baseline; gap: 8px; }}
.histogram .head span:first-child {{ display: flex; align-items: center; gap: 8px; font-weight: 600; }}
.axis-name {{ font-size: 12px; color: var(--muted); }}
.plot-row {{ display: flex; gap: 8px; }}
.y-axis {{ position: relative; flex: 0 0 28px; height: 150px; font-size: 12px; color: var(--muted); }}
.y-axis span {{ position: absolute; right: 0; transform: translateY(50%); }}
.histogram.pointing .y-axis span {{ opacity: .35; }}
.y-axis .guide-tag {{ right: -6px; padding: 1px 7px; border-radius: 6px; background: var(--bot);
  color: var(--surface); font-weight: 700; white-space: nowrap; opacity: 1 !important; z-index: 1; }}
.plot {{ flex: 1; position: relative; height: 150px; border-left: 1px solid var(--line);
  border-bottom: 1px solid var(--muted); }}
.plot .grid {{ position: absolute; left: 0; right: 0; height: 1px; background: var(--soft); }}
.plot .bar {{ position: absolute; bottom: 0; background: var(--bot); border-radius: 3px 3px 0 0;
  min-height: 2px; outline-offset: 2px; transition: opacity .15s ease; }}
.histogram.pointing .bar {{ opacity: .45; }}
.histogram.pointing .bar.on {{ opacity: 1; }}
.plot .guide {{ position: absolute; left: 0; border-top: 2px dashed var(--bot); pointer-events: none; }}
.x-axis {{ position: relative; height: 16px; margin-left: 36px; font-size: 12px; color: var(--muted); }}
.x-axis span {{ position: absolute; top: 0; transform: translateX(-50%); }}
.histogram .x-name {{ text-align: center; }}
.compare, .verdict {{ display: flex; flex-direction: column; gap: 24px; }}
.picker, .stat {{ display: grid; grid-template-columns: minmax(0, 1fr) 160px minmax(0, 1fr);
  align-items: center; gap: 12px; }}
.picker label {{ display: flex; flex-direction: column; align-items: flex-start; gap: 6px;
  font-size: 14px; color: var(--muted); }}
.picker label:first-child {{ align-items: flex-end; text-align: right; }}
.select {{ position: relative; display: inline-block; max-width: 100%; }}
.select select {{ appearance: none; -webkit-appearance: none; font: inherit; font-size: 16px;
  color: var(--ink); background: var(--ground); border: 1px solid var(--line); border-radius: 10px;
  padding: 10px 44px 10px 14px; min-height: 46px; min-width: 220px; cursor: pointer; }}
.select svg {{ position: absolute; right: 14px; top: 15px; pointer-events: none; }}
.picker .against {{ align-self: end; padding-bottom: 12px; text-align: center; font-weight: 600;
  color: var(--muted); }}
.picker select {{ color: var(--bot); font-weight: 700; }}
.faceoff {{ display: flex; flex-direction: column; }}
.stat {{ padding: 8px 0; border-top: 1px solid var(--soft); }}
.stat .left, .stat .right {{ display: flex; align-items: center; gap: 10px; }}
.stat .left {{ justify-content: flex-end; }}
.stat .num {{ min-width: 64px; font-size: 17px; }}
.stat .left .num {{ text-align: right; }}
.stat .lane {{ flex: 1; max-width: 300px; height: 18px; display: flex; background: var(--soft);
  border-radius: 5px; }}
.stat .left .lane {{ justify-content: flex-end; }}
.stat .lane span {{ background: var(--bot); border-radius: 5px; transition: width .3s ease, opacity .2s ease; }}
.stat .better .num {{ font-weight: 800; }}
.stat .weaker .lane span {{ opacity: .4; }}
.stat .label {{ display: flex; flex-direction: column; text-align: center; line-height: 1.3; }}
.stat .label b {{ font-size: 15px; }}
.stat .label small {{ font-size: 12px; color: var(--muted); }}
.sentence {{ font-size: clamp(22px, 3vw, 30px); font-weight: 650; line-height: 1.25; max-width: 34ch;
  letter-spacing: -0.01em; }}
.note {{ display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px 12px; padding: 14px 16px;
  border-radius: 12px; background: var(--soft); }}
.note b {{ font-weight: 650; }}
.note span {{ color: var(--muted); font-size: 15px; flex: 1 1 360px; }}
.terms {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }}
.terms div {{ background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 18px 20px; }}
.terms h4 {{ margin: 0 0 4px; color: var(--ink); font-size: 16px; }}
.terms p {{ color: var(--muted); font-size: 15px; }}
.table-box {{ background: var(--surface); border: 1px solid var(--line); border-radius: 14px; overflow-x: auto; }}
table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
th, td {{ padding: 10px 14px; text-align: right; white-space: nowrap; }}
th {{ color: var(--muted); font-weight: 500; font-size: 13px; }}
tbody tr {{ border-top: 1px solid var(--line); }}
th.text, td.text {{ text-align: left; }}
td.text:not(.bot) {{ color: var(--muted); }}
td.bot {{ font-weight: 600; }}
td.bot .swatch {{ margin-right: 10px; }}
ul.missing {{ color: var(--muted); }}
footer {{ margin-top: 72px; padding-top: 24px; border-top: 1px solid var(--line); color: var(--muted);
  font-size: 14px; display: flex; flex-direction: column; gap: 6px; }}
:focus-visible {{ outline: 2px solid var(--ink); outline-offset: 2px; }}
@media (prefers-reduced-motion: reduce) {{
  .rank .fill, .rank .value {{ animation: none; }}
  body, .plot .bar, .stat .lane span {{ transition: none; }}
}}
@media (max-width: 600px) {{
  main {{ padding: 20px 16px 64px; }}
  .rank .name {{ flex-basis: 100%; }}
  .stat {{ grid-template-columns: minmax(0, 1fr) 96px minmax(0, 1fr); gap: 8px; }}
  .stat .lane {{ display: none; }}
  /* The two dropdowns stack, full width, so bot names are never cut off. */
  .picker {{ grid-template-columns: minmax(0, 1fr); }}
  .picker label, .picker label:first-child {{ align-items: stretch; text-align: left; }}
  .picker .against {{ padding: 0; }}
  .select {{ display: block; }}
  .select select {{ min-width: 0; width: 100%; }}
}}
"""

PAGE_SCRIPT = """
(function () {
  var root = document.documentElement;
  var toggle = document.querySelector(".theme-toggle");
  try {
    var saved = localStorage.getItem("bot-report-theme");
    if (saved) root.setAttribute("data-theme", saved);
  } catch (error) {}
  function isDark() {
    var chosen = root.getAttribute("data-theme");
    if (chosen) return chosen === "dark";
    return window.matchMedia && matchMedia("(prefers-color-scheme: dark)").matches;
  }
  function label() { toggle.textContent = isDark() ? "Light mode" : "Dark mode"; }
  if (toggle) {
    label();
    toggle.addEventListener("click", function () {
      var next = isDark() ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("bot-report-theme", next); } catch (error) {}
      label();
    });
  }

  document.querySelectorAll(".histogram").forEach(function (chart) {
    var guide = chart.querySelector(".guide");
    var tag = chart.querySelector(".guide-tag");
    function show(bar) {
      guide.style.bottom = tag.style.bottom = bar.dataset.height + "%";
      guide.style.width = bar.dataset.reach + "%";
      tag.textContent = bar.dataset.count;
      guide.hidden = tag.hidden = false;
      chart.classList.add("pointing");
      bar.classList.add("on");
    }
    function hide(bar) {
      guide.hidden = tag.hidden = true;
      chart.classList.remove("pointing");
      bar.classList.remove("on");
    }
    chart.querySelectorAll(".bar").forEach(function (bar) {
      bar.addEventListener("mouseenter", function () { show(bar); });
      bar.addEventListener("focus", function () { show(bar); });
      bar.addEventListener("mouseleave", function () { hide(bar); });
      bar.addEventListener("blur", function () { hide(bar); });
    });
  });

  document.querySelectorAll(".compare").forEach(function (box) {
    var matchups = JSON.parse(box.querySelector(".matchups").textContent);
    var first = box.querySelector(".pick-a");
    var second = box.querySelector(".pick-b");
    function update() {
      var same = first.value === second.value;
      box.querySelector(".same").hidden = !same;
      box.querySelector(".verdict").hidden = same;
      var parts = matchups[first.value + "|" + second.value];
      if (same || !parts) return;
      box.querySelectorAll("[data-field]").forEach(function (node) {
        node.textContent = parts[node.dataset.field];
      });
      box.querySelectorAll("[data-color]").forEach(function (node) {
        node.className = node.className.replace(/c-\\d+/, parts[node.dataset.color]);
      });
      box.querySelectorAll(".stat").forEach(function (row, index) {
        var stat = parts.stats[index];
        ["left", "right"].forEach(function (side) {
          var cell = row.querySelector("." + side);
          var other = side === "left" ? "right" : "left";
          cell.querySelector(".num").textContent = stat[side + "Text"];
          cell.querySelector(".lane span").style.width = stat[side + "Pct"] + "%";
          cell.classList.toggle("better", stat[side + "Better"]);
          cell.classList.toggle("weaker", stat[other + "Better"]);
        });
      });
    }
    first.addEventListener("change", update);
    second.addEventListener("change", update);
  });
})();
"""

CHEVRON = ('<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><path '
           'd="M3.5 6l4.5 4.5L12.5 6" fill="none" stroke="currentColor" stroke-width="1.8" '
           'stroke-linecap="round" stroke-linejoin="round"/></svg>')

LOGO = ('<svg width="30" height="30" viewBox="0 0 30 30" aria-hidden="true">'
        '<rect x="1" y="20" width="8" height="8" rx="2" fill="#2EAA82"/>'
        '<rect x="9" y="20" width="8" height="8" rx="2" fill="#2EAA82"/>'
        '<rect x="17" y="20" width="8" height="8" rx="2" fill="#2EAA82"/>'
        '<rect x="17" y="11" width="8" height="9" rx="3" fill="#8FC23A"/>'
        '<circle cx="19.5" cy="14" r="1.2" fill="#14171C"/>'
        '<circle cx="22.5" cy="14" r="1.2" fill="#14171C"/>'
        '<circle cx="21" cy="4" r="3" fill="#E04848"/></svg>')

# Columns that name a bot get its colour swatch; text columns align left.
BOT_COLUMNS = {"overview": (0,), "comparisons": (0, 1), "provenance": (0,)}
TEXT_COLUMNS = {"overview": (0, 1, 2), "comparisons": (0, 1, 5, 6), "provenance": (0, 1, 4)}


class Palette:
    """One colour class per bot on the page, in light and dark versions."""

    def __init__(self, groups):
        self.classes = {}
        for group in groups:
            for row in group.rows:
                self.classes.setdefault(row.bot, f"c-{len(self.classes)}")

    def of(self, bot):
        return self.classes.get(bot, "c-muted")

    def style(self):
        """CSS giving each bot class its colour: light by default, dark when chosen."""
        lines = [f".c-muted {{ --bot: {ReportColors.LIGHT_TEXT_MUTED}; }}"]
        dark_rules = []
        for bot, name in self.classes.items():
            lines.append(f".{name} {{ --bot: {ReportColors.bot_color(bot, light=True)}; }}")
            dark_rules.append(f".{name} {{ --bot: {ReportColors.bot_color(bot)}; }}")
        # Dark follows the system unless the reader picked light, or picked dark.
        lines.append("@media (prefers-color-scheme: dark) {")
        lines += [f':root:not([data-theme="light"]) {rule}' for rule in dark_rules]
        lines.append("}")
        lines += [f':root[data-theme="dark"] {rule}' for rule in dark_rules]
        return "\n".join(lines) + "\n"


HISTOGRAM_AXES = ("Across: the score a game ended with, in ranges of 10. Up: how many games "
                  "ended there.")


def histogram_note(shared=None):
    """How to read the histograms; shared names the charts that share one scale."""
    if shared is None:
        return f"{HISTOGRAM_AXES} Hover over or tab to a bar to read its count."
    return f"{HISTOGRAM_AXES} {shared} share one scale; hover over or tab to a bar to read its count."


def games_text(count):
    return f"{count} game" + ("" if count == 1 else "s")


def headline(group):
    leader = ranking_rows(group)[0]
    if len(group.rows) == 1:
        return f"{leader.bot} eats {leader.mean_score:.1f} food per game on average."
    return f"{leader.bot} eats the most food: {leader.mean_score:.1f} per game on average."


def kind(bot):
    return "Learned" if FAMILIES_BY_LABEL.get(bot) else "Hand-written"


def ranking(group, palette):
    rows = ranking_rows(group)
    top = max(row.mean_score for row in rows) or 1
    parts = ['<div class="card ranking" role="list" aria-label="Average food per game, best first">',
             '<div class="top muted" style="font-size: 14px"><span>Average food eaten per game</span>'
             f"<span>{games_text(rows[0].game_count)} each</span></div>"]
    for place, row in enumerate(rows):
        delay = f"{place * 0.09:.2f}s"
        parts.append(
            f'<div class="rank {palette.of(row.bot)}" role="listitem" '
            f'title="{escape(row.bot)}: {row.mean_score:.1f} food per game on average, '
            f'best game {row.best_score}">'
            f'<span class="name"><span class="swatch"></span>{escape(row.bot)}'
            + ('<span class="newest">Newest</span>' if row.bot == group.newest_bot else "")
            + "</span>"
            f'<span class="track"><span class="lane"><span class="fill" style="display: block; '
            f'width: {row.mean_score / top * 92:.1f}%; animation-delay: {delay}"></span></span>'
            f'<span class="value" style="animation-delay: {delay}">{row.mean_score:.1f}</span></span>'
            f'<span class="kind">{kind(row.bot)}</span></div>'
        )
    parts.append("</div>")
    return parts


def histograms(group, palette, rows=None):
    """One histogram per bot, every bot in the group unless rows names some."""
    rows = ranking_rows(group) if rows is None else rows
    count = bin_count(group)
    bins = [score_bins(row.scores, count) for row in rows]
    y_ticks = axis_ticks(max(max(counts) for counts in bins))
    x_ticks = axis_ticks(count * BIN_WIDTH)
    x_end, y_end = x_ticks[-1], y_ticks[-1]
    parts = ['<div class="histograms">']
    for row, counts in zip(rows, bins):
        parts.append(f'<div class="histogram {palette.of(row.bot)}">')
        parts.append(f'<div class="head"><span><span class="swatch"></span>{escape(row.bot)}</span>'
                     f'<span class="muted" style="font-size: 13px">average {row.mean_score:.1f}</span></div>')
        parts.append('<span class="axis-name">Games</span><div class="plot-row"><div class="y-axis">')
        parts += [f'<span style="bottom: {games / y_end * 100:.1f}%">{games}</span>' for games in y_ticks]
        parts.append('<span class="guide-tag" hidden></span></div><div class="plot">')
        parts += [f'<span class="grid" style="bottom: {games / y_end * 100:.1f}%"></span>'
                  for games in y_ticks[1:]]
        for index, games in enumerate(counts):
            if not games:
                continue
            left = index * BIN_WIDTH / x_end * 100
            width = BIN_WIDTH / x_end * 100
            height = games / y_end * 100
            label = f"{row.bot}: {games_text(games)} scored {bin_label(index)}"
            parts.append(
                f'<span class="bar" tabindex="0" role="img" aria-label="{escape(label)}" '
                f'title="{escape(label)}" data-count="{games_text(games)}" '
                f'data-height="{height:.1f}" data-reach="{left:.1f}" '
                f'style="left: calc({left:.2f}% + 1px); width: calc({width:.2f}% - 2px); '
                f'height: {height:.1f}%"></span>'
            )
        parts.append('<span class="guide" hidden></span></div></div><div class="x-axis">')
        parts += [f'<span style="left: {score / x_end * 100:.1f}%">{score}</span>' for score in x_ticks]
        parts.append('</div><span class="axis-name x-name">Score (food eaten)</span></div>')
    parts.append("</div>")
    return parts


def find_matchup(group, first, second):
    for matchup in group.matchups:
        if {matchup.first, matchup.second} == {first, second}:
            return matchup
    return None


# The face-off rows: label, hint, how to read a row's value, and which way is
# better (True: higher, False: lower, None: neither, so neither side is bold).
FACE_OFF = (
    ("Average food", "per game", "mean", True),
    ("Median food", "the middle game", "median", True),
    ("Best game", "most food in one game", "best", True),
    ("Games won", "head to head", "wins", True),
    ("Moves per food", "lower is faster", "moves", False),
    ("Stopped by limit", "still alive at the limit", "limit", None),
)


def stat_value(row, key, wins):
    return {
        "mean": row.mean_score, "median": row.median_score, "best": row.best_score,
        "wins": wins, "moves": row.moves_per_point, "limit": row.move_limit_rate,
    }[key]


def stat_text(key, value):
    if value is None:
        return NOT_SHOWN
    if key in ("best", "wins"):
        return str(value)
    if key == "limit":
        return f"{value:.1%}"
    return f"{value:.1f}"


NOT_SHOWN = "—"


def face_off_stats(group, first, second, first_wins, second_wins):
    """Each face-off row for one pair: both values, bar lengths, and which is better."""
    rows = {row.bot: row for row in ranking_rows(group)}
    stats = []
    for name, hint, key, higher_is_better in FACE_OFF:
        everyone = [stat_value(row, key, row.game_count) for row in rows.values()]
        top = max((value for value in everyone if value is not None), default=0) or 1
        left = stat_value(rows[first], key, first_wins)
        right = stat_value(rows[second], key, second_wins)
        comparable = higher_is_better is not None and None not in (left, right) and left != right
        left_better = comparable and (left > right) == higher_is_better
        stats.append({
            "name": name, "hint": hint,
            "leftText": stat_text(key, left), "rightText": stat_text(key, right),
            "leftPct": round((left or 0) / top * 100, 1), "rightPct": round((right or 0) / top * 100, 1),
            "leftBetter": left_better, "rightBetter": comparable and not left_better,
        })
    return stats


def verdict_parts(group, palette, first, second):
    """Everything the face-off shows for one ordered pair, as plain values."""
    matchup = find_matchup(group, first, second)
    first_is_winner = matchup.first == first
    first_wins = matchup.first_wins if first_is_winner else matchup.second_wins
    second_wins = matchup.second_wins if first_is_winner else matchup.first_wins
    games = matchup.game_count
    if matchup.low is None:
        sentence = f"Too few games to compare {matchup.first} and {matchup.second}."
        badge, explain = "Too few games", "A 95% range needs at least two games."
    elif matchup.low > 0:
        sentence = (f"{matchup.first} eats {matchup.mean_difference:.1f} more food per game than "
                    f"{matchup.second}, and wins {matchup.first_wins} of the {games} games.")
        badge = "Reliable result"
        explain = (f"On new games, {matchup.first} would most likely lead by {matchup.low:.1f} to "
                   f"{matchup.high:.1f} food per game (the 95% range). That range stays above "
                   "zero, so the lead is not luck.")
    else:
        sentence = f"No reliable difference between {matchup.first} and {matchup.second}."
        badge = "Too close to call"
        explain = (f"The 95% range runs from {matchup.low:.1f} to {matchup.high:.1f} and includes "
                   "zero, so these games cannot tell the two bots apart.")
    return {
        "firstColor": palette.of(first), "secondColor": palette.of(second),
        "stats": face_off_stats(group, first, second, first_wins, second_wins),
        "sentence": sentence, "badge": badge, "explain": explain,
    }


def select(kind, bots, chosen, label, color):
    options = "".join(
        f'<option value="{escape(bot)}"{" selected" if bot == chosen else ""}>{escape(bot)}</option>'
        for bot in bots
    )
    key = "firstColor" if kind == "a" else "secondColor"
    return (f'<label>{label}<span class="select {color}" data-color="{key}">'
            f'<select class="pick-{kind}">{options}</select>{CHEVRON}</span></label>')


def opening_pair(group, bots):
    """The face-off to show first: the newest bot against the leader, else the top two."""
    if group.newest_bot in bots and group.newest_bot != bots[0]:
        return group.newest_bot, bots[0]
    return bots[0], bots[1]


def comparison(group, palette):
    bots = [row.bot for row in ranking_rows(group)]
    first_bot, second_bot = opening_pair(group, bots)
    every_pair = {
        f"{first}|{second}": verdict_parts(group, palette, first, second)
        for first in bots for second in bots if first != second
    }
    shown = every_pair[f"{first_bot}|{second_bot}"]
    # A "</" inside the data would end the script tag early.
    data = json.dumps(every_pair, ensure_ascii=False).replace("</", "<\\/")

    def cell(side, stat):
        other = "right" if side == "left" else "left"
        state = " better" if stat[side + "Better"] else " weaker" if stat[other + "Better"] else ""
        color = shown["firstColor" if side == "left" else "secondColor"]
        number = f'<span class="num">{escape(stat[side + "Text"])}</span>'
        lane = f'<span class="lane"><span style="width: {stat[side + "Pct"]}%"></span></span>'
        content = number + lane if side == "left" else lane + number
        key = "firstColor" if side == "left" else "secondColor"
        return f'<div class="{side} {color}{state}" data-color="{key}">{content}</div>'

    rows = [
        f'<div class="stat">{cell("left", stat)}<div class="label"><b>{escape(stat["name"])}</b>'
        f'<small>{escape(stat["hint"])}</small></div>{cell("right", stat)}</div>'
        for stat in shown["stats"]
    ]
    return [
        '<div class="card compare">',
        f'<script type="application/json" class="matchups">{data}</script>',
        '<div class="picker">',
        select("a", bots, first_bot, "First bot", shown["firstColor"]),
        '<span class="against">versus</span>',
        select("b", bots, second_bot, "Second bot", shown["secondColor"]),
        "</div>",
        '<p class="same muted" hidden>Pick two different bots to compare them.</p>',
        '<div class="verdict">',
        '<div class="faceoff">', *rows, "</div>",
        f'<p class="sentence" data-field="sentence">{escape(shown["sentence"])}</p>',
        f'<div class="note"><b data-field="badge">{escape(shown["badge"])}</b>'
        f'<span data-field="explain">{escape(shown["explain"])}</span></div>',
        "</div></div>",
    ]


def table(headings, rows, palette, name):
    bot_columns, text_columns = BOT_COLUMNS[name], TEXT_COLUMNS[name]
    parts = ['<div class="table-box"><table><thead><tr>']
    parts += [f'<th class="text">{escape(heading)}</th>' if column in text_columns
              else f"<th>{escape(heading)}</th>" for column, heading in enumerate(headings)]
    parts.append("</tr></thead><tbody>")
    for cells in rows:
        # A comparison row names its pair, so a reader can find it by the two bots.
        opening = (f'<tr data-pair="{escape(cells[0])}|{escape(cells[1])}">'
                   if name == "comparisons" else "<tr>")
        row = []
        for column, cell in enumerate(cells):
            if column in bot_columns:
                bot = cell.split(" combined (")[0]
                row.append(f'<td class="text bot {palette.of(bot)}"><span class="swatch"></span>'
                           f"{escape(cell)}</td>")
            elif column in text_columns:
                row.append(f'<td class="text">{escape(cell)}</td>')
            else:
                row.append(f"<td>{escape(cell)}</td>")
        parts.append(opening + "".join(row) + "</tr>")
    parts.append("</tbody></table></div>")
    return parts


def group_section(group, palette):
    parts = ['<section class="group">', '<div>',
             f'<p class="conditions">{escape(group.title)}</p>',
             f"<h2>{escape(headline(group))}</h2></div>"]
    parts += ranking(group, palette)
    parts += ['<div class="part"><h3>How did each bot&#39;s games end?</h3>',
              f"<p>{histogram_note('All charts')}</p>"]
    parts += histograms(group, palette)
    parts.append("</div>")
    parts += ['<div class="part"><h3>Compare two bots</h3>',
              "<p>Pick two bots. Each row puts one number side by side, from the same "
              "games; the better one is bold.</p>"]
    if group.matchups:
        parts += comparison(group, palette)
    else:
        parts.append(f'<p class="muted">{escape(ONE_BOT_SENTENCE)}</p>')
    parts.append("</div>")
    parts += ['<div class="part"><h3>Every number</h3>',
              "<p>For developers: one row per bot file, every comparison, and where each "
              "trained bot came from. A bot file is the saved Q-table or network, shown by "
              "the start of its hash.</p>"]
    parts += table(OVERVIEW_HEADINGS, [row_cells(row) for row in group.rows], palette, "overview")
    if group.matchups:
        parts.append("<h4>Game by game</h4>")
        parts += table(COMPARISON_HEADINGS, group.comparisons, palette, "comparisons")
    parts.append("<h4>Where each bot came from</h4>")
    parts += table(PROVENANCE_HEADINGS, group.provenance, palette, "provenance")
    parts += ["</div>", "</section>"]
    return parts


def write_html(report):
    palette = Palette(report.groups)
    parts = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{escape(report.title)}</title>",
        f"<style>{PAGE_STYLE}{palette.style()}</style>",
        "</head>",
        "<body>",
        "<main>",
        f'<header class="top"><div class="brand">{LOGO}<h1>Snake bots: {escape(report.title)}</h1></div>'
        '<button type="button" class="theme-toggle">Dark mode</button></header>',
        f'<p class="lede">{escape(source_sentence(report))}</p>',
    ]
    for group in report.groups:
        parts += group_section(group, palette)
    parts += ['<section class="group"><div class="part"><h3>What the numbers mean</h3>',
              '<div class="terms">']
    parts += [f"<div><h4>{escape(name)}</h4><p>{escape(text)}</p></div>" for name, text in TERMS]
    parts.append("</div></div>")
    if report.not_evaluated:
        parts += ['<div class="part"><h3>Not evaluated yet</h3>',
                  f"<p>{escape(NOT_EVALUATED_SENTENCE)}</p>", '<ul class="missing">']
        parts += [f"<li>{escape(name)}</li>" for name in report.not_evaluated]
        parts.append("</ul></div>")
    parts.append("</section>")
    parts.append("<footer>")
    parts += [f"<p>{escape(note)}</p>" for note in reading_notes(report)]
    parts.append("<p>Generated by AnalyseBots from saved Bot Experiment reports. The same "
                 "games give the same numbers every time.</p></footer>")
    parts += ["</main>", f"<script>{PAGE_SCRIPT}</script>", "</body>", "</html>"]
    return "\n".join(parts) + "\n"
