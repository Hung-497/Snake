"""Write a Run Report as an HTML page about one saved Bot Experiment.

It uses the Bot Report page's styles, script, logo, and bot colours, so both
pages look and behave the same, and it links back to the full Bot Report.
"""

from html import escape
import math
import re

from snake.analysis.ReportPage import (
    LOGO, PAGE_SCRIPT, PAGE_STYLE, Palette, games_text, histogram_note, histograms,
)
from snake.analysis.RunReport import alone_sentence, headline, headline_detail, partner_row
from snake.analysis.ScoreChart import axis_ticks


RUN_REPORT_TITLE = "Run Report"

# One row per other bot: its name, a bar from the zero line, and the words.
# On a phone each row stacks: the name, the bar, then the words.
RUN_STYLE = """
.rivals { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }
.rival, .rivals-scale { display: grid; grid-template-columns: 160px minmax(0, 1fr) 230px;
  align-items: center; gap: 16px; }
.rivals-scale { font-size: 13px; color: var(--muted); }
.rivals-scale .ends { display: flex; justify-content: space-between; gap: 8px; }
.rival { min-height: 56px; }
.rival .name { display: flex; align-items: center; gap: 10px; font-weight: 600; }
.duel { position: relative; height: 40px; }
.duel .zero { position: absolute; left: 50%; top: 0; bottom: 0; width: 2px; margin-left: -1px;
  background: var(--line); }
.duel .lead { position: absolute; top: 11px; height: 18px; background: var(--bot); border-radius: 4px; }
.duel .range { position: absolute; top: 19px; height: 2px; background: var(--ink); }
.rival .words { display: flex; flex-direction: column; line-height: 1.35; }
.rival .words small { font-size: 13px; color: var(--muted); }
.jump { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-top: 20px; }
.jump a { color: var(--ink); text-decoration: none; background: var(--surface);
  border: 1px solid var(--line); border-radius: 999px; padding: 10px 16px; font-size: 14px; }
.jump a:hover, .jump a:focus-visible { border-color: var(--muted); }
/* A section jumped to keeps a little room above it. */
section.group[id] { scroll-margin-top: 24px; }
/* Only two histograms, so they share the full width; one alone keeps half. */
.histograms { grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
.alone .histograms { max-width: 560px; }
@media (max-width: 600px) {
  .rival { grid-template-columns: minmax(0, 1fr); gap: 4px; padding: 10px 0;
    border-top: 1px solid var(--soft); }
  .rival .words { order: 3; }
  .rivals-scale { grid-template-columns: minmax(0, 1fr); }
  .rivals-scale > span { display: none; }
}
"""


def lead_text(rival):
    if rival.difference > 0:
        return f"Leads by {rival.difference:.1f}"
    if rival.difference < 0:
        return f"Trails by {-rival.difference:.1f}"
    return "Level"


def rival_title(bot, rival):
    text = f"{bot.label} against {rival.label}: {rival.difference:+.1f} food per game"
    if rival.low is not None:
        text += f" (95% range {rival.low:.1f} to {rival.high:.1f})"
    return text + f", won {rival.wins} of {games_text(rival.game_count)}"


def against_everyone(bot, palette):
    """One row per other bot: how far this bot leads or trails it, on one shared scale."""
    reach = max(max(abs(rival.difference), abs(rival.low or 0), abs(rival.high or 0))
                for rival in bot.rivals)
    reach = axis_ticks(math.ceil(reach) or 1)[-1]

    def at(difference):
        return 50 + difference / reach * 50

    parts = [f'<div class="card rivals-box"><div class="rivals-scale"><span></span>'
             f'<div class="ends"><span>{escape(bot.label)} eats less</span>'
             f"<span>no difference</span><span>{escape(bot.label)} eats more</span></div>"
             f'<span></span></div><ul class="rivals" aria-label="{escape(bot.label)} '
             'against each other bot">']
    for rival in bot.rivals:
        leader = bot.label if rival.difference >= 0 else rival.label
        bar = (f'<span class="lead {palette.of(leader)}" style="left: '
               f'{min(at(0), at(rival.difference)):.1f}%; '
               f'width: {abs(at(rival.difference) - at(0)):.1f}%"></span>')
        line = "" if rival.low is None else (
            f'<span class="range" style="left: {at(rival.low):.1f}%; '
            f'width: {at(rival.high) - at(rival.low):.1f}%"></span>'
        )
        parts.append(
            f'<li class="rival {palette.of(rival.label)}" title="{escape(rival_title(bot, rival))}">'
            f'<span class="name"><span class="swatch"></span>{escape(rival.label)}</span>'
            f'<span class="duel"><span class="zero"></span>{bar}{line}</span>'
            f'<span class="words"><b>{lead_text(rival)}</b>'
            f"<small>won {rival.wins} of {games_text(rival.game_count)} · {rival.reliability}</small>"
            "</span></li>"
        )
    parts.append("</ul></div>")
    return parts


def alone(run_report, bot, palette):
    """What a bot with no other bot on its games shows: why, and its own games."""
    parts = [f'<div class="part"><h3>Nothing to compare yet</h3><p>{escape(alone_sentence(bot))}</p>']
    if run_report.other_games:
        parts.append(f"<p>Other bots were evaluated on these games. Evaluate {escape(bot.label)} "
                     "on the same games to compare them:</p>")
        parts.append('<ul class="missing">')
        parts += [f"<li>{escape(title)}: {count} bot{'' if count == 1 else 's'}</li>"
                  for title, count in run_report.other_games]
        parts.append("</ul>")
    parts.append("</div>")
    parts += ['<div class="part alone"><h3>How did its games end?</h3>',
              f"<p>{histogram_note()}</p>"]
    parts += histograms(run_report.group, palette, [bot.summary])
    parts.append("</div>")
    return parts


def bot_section(run_report, bot, palette):
    parts = [f'<section class="group" id="{anchor(bot.label)}"><div>',
             f'<p class="conditions">{escape(run_report.group.title)}</p>',
             f"<h2>{escape(headline(bot))}</h2>",
             f'<p class="muted">{escape(headline_detail(bot))}</p></div>']
    if not bot.rivals:
        return parts + alone(run_report, bot, palette) + ["</section>"]
    parts += [f'<div class="part"><h3>How does {escape(bot.label)} do against each bot?</h3>',
              f"<p>Bars to the right: {escape(bot.label)} eats more food per game than that "
              "bot. To the left: less. The thin line shows the 95% range; when it crosses "
              "the middle, these games cannot tell the two bots apart.</p>"]
    parts += against_everyone(bot, palette)
    parts.append("</div>")
    partner = partner_row(run_report.group, bot)
    parts += [f'<div class="part"><h3>How did its games end, next to {escape(partner.bot)}?</h3>',
              f"<p>{histogram_note('Both charts')}</p>"]
    parts += histograms(run_report.group, palette, [bot.summary, partner])
    parts += ["</div>", "</section>"]
    return parts


def anchor(label):
    """A section's id from its bot's label: "Q Learning v3" becomes q-learning-v3."""
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")


def jump_list(run_report):
    """Links to each bot's section, best average first; one bot needs none."""
    if len(run_report.bots) < 2:
        return []
    links = "".join(f'<a href="#{anchor(bot.label)}">{escape(bot.label)}</a>'
                    for bot in run_report.bots)
    return [f'<nav class="jump" aria-label="Bots in this run">'
            f'<span class="muted">Bots in this run:</span>{links}</nav>']


def write_run_html(run_report):
    palette = Palette((run_report.group,))
    parts = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{RUN_REPORT_TITLE}</title>",
        f"<style>{PAGE_STYLE}{RUN_STYLE}{palette.style()}</style>",
        "</head>",
        "<body>",
        "<main>",
        f'<header class="top"><div class="brand">{LOGO}<h1>Snake bots: {RUN_REPORT_TITLE}</h1></div>'
        '<button type="button" class="theme-toggle">Dark mode</button></header>',
        '<p class="lede"><a href="../bot_report.html">Back to the full Bot Report</a></p>',
        *jump_list(run_report),
    ]
    for bot in run_report.bots:
        parts += bot_section(run_report, bot, palette)
    parts += ["</main>", f"<script>{PAGE_SCRIPT}</script>", "</body>", "</html>"]
    return "\n".join(parts) + "\n"
