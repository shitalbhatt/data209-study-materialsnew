"""Builds the PowerPoint decks for Lectures 13-14 and 15-16 (decks/*.pptx) and renders them to PDF with LibreOffice.

Content follows the narration scripts of the lecture videos in the course Drive folder.
Usage: python3 scripts/make_decks.py OUT_DIR
Needs python-pptx, matplotlib and LibreOffice (soffice).
"""
import pathlib, subprocess, sys, tempfile
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

NAVY, BLUE, GOLD, GREY, LIGHT = RGBColor(0x1E, 0x27, 0x5E), RGBColor(0x2B, 0x6C, 0xB0), RGBColor(0xD9, 0x9A, 0x2B), RGBColor(0x55, 0x5B, 0x6E), RGBColor(0xF2, 0xF4, 0xFB)
FOOT = "DATA209 · Advanced Exploratory Data Analysis · Dr. Shital Bhatt · Vidyashilp University"
HEX = {"navy": "#1E275E", "blue": "#2B6CB0", "gold": "#D99A2B", "red": "#C0392B", "grey": "#9AA0B4", "green": "#2E8B57"}


def deck():
    p = Presentation(); p.slide_width, p.slide_height = Inches(13.333), Inches(7.5); return p


def textbox(slide, x, y, w, h, text, size=20, bold=False, color=NAVY, align=None, font="Calibri"):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame; tf.word_wrap = True
    para = tf.paragraphs[0]; r = para.add_run(); r.text = text; r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color; r.font.name = font
    if align: para.alignment = align
    return tb


def base(prs, kicker, title, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bar = s.shapes.add_shape(1, 0, 0, Inches(0.25), prs.slide_height); bar.fill.solid(); bar.fill.fore_color.rgb = BLUE; bar.line.fill.background()
    textbox(s, 0.6, 0.3, 11, 0.4, kicker.upper(), 14, True, GOLD)
    textbox(s, 0.6, 0.65, 12, 1.0, title, 34, True, NAVY, font="Cambria")
    textbox(s, 0.6, 7.0, 10, 0.3, FOOT, 11, False, GREY)
    textbox(s, 12.2, 7.0, 0.8, 0.3, str(n), 12, False, GREY, PP_ALIGN.RIGHT)
    return s


def bullets(slide, items, x=0.6, y=1.9, w=12, size=22, gap=10):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(4.8)); tf = tb.text_frame; tf.word_wrap = True
    for i, it in enumerate(items):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); para.space_after = Pt(gap)
        lead, _, rest = it.partition("||")
        if rest:
            r = para.add_run(); r.text = lead + " "; r.font.bold = True; r.font.size = Pt(size); r.font.color.rgb = BLUE; r.font.name = "Calibri"
            r2 = para.add_run(); r2.text = rest; r2.font.size = Pt(size); r2.font.color.rgb = RGBColor(0x22, 0x26, 0x38); r2.font.name = "Calibri"
        else:
            r = para.add_run(); r.text = "•  " + it; r.font.size = Pt(size); r.font.color.rgb = RGBColor(0x22, 0x26, 0x38); r.font.name = "Calibri"


def cards(slide, items, y=2.0, h=4.2):
    n = len(items); w = (12.1 - 0.3 * (n - 1)) / n
    for i, (head, body) in enumerate(items):
        x = 0.6 + i * (w + 0.3)
        box = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h)); box.fill.solid(); box.fill.fore_color.rgb = LIGHT; box.line.color.rgb = RGBColor(0xD5, 0xDA, 0xEC)
        textbox(slide, x + 0.2, y + 0.15, w - 0.4, 0.8, head, 22, True, BLUE)
        textbox(slide, x + 0.2, y + (1.0 if n < 5 else 1.35), w - 0.4, h - 1.4, body, 17, False, RGBColor(0x22, 0x26, 0x38))


def table(slide, rows, y=1.9, colw=None, size=16):
    nr, nc = len(rows), len(rows[0]); colw = colw or [12.1 / nc] * nc
    t = slide.shapes.add_table(nr, nc, Inches(0.6), Inches(y), Inches(sum(colw)), Inches(0.5 * nr)).table
    for j, w in enumerate(colw): t.columns[j].width = Inches(w)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.cell(i, j); c.text = str(val); para = c.text_frame.paragraphs[0]; para.runs[0].font.size = Pt(size); para.runs[0].font.name = "Calibri"
            if i == 0:
                c.fill.solid(); c.fill.fore_color.rgb = NAVY; para.runs[0].font.color.rgb = RGBColor(255, 255, 255); para.runs[0].font.bold = True
            else:
                c.fill.solid(); c.fill.fore_color.rgb = LIGHT if i % 2 else RGBColor(255, 255, 255)


def picture(slide, path, x, y, w=None, h=None):
    slide.shapes.add_picture(str(path), Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)


def note(slide, text, y=6.35):
    textbox(slide, 0.6, y, 12.1, 0.6, text, 18, True, NAVY)


def title_slide(prs, kicker, title, sub):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bar = s.shapes.add_shape(1, 0, 0, Inches(0.25), prs.slide_height); bar.fill.solid(); bar.fill.fore_color.rgb = BLUE; bar.line.fill.background()
    textbox(s, 0.9, 1.8, 11.5, 0.5, kicker.upper(), 18, True, GOLD)
    textbox(s, 0.9, 2.4, 11.5, 2.2, title, 48, True, NAVY, font="Cambria")
    textbox(s, 0.9, 4.7, 11.5, 1.0, sub, 22, False, GREY)
    textbox(s, 0.9, 6.5, 11.5, 0.4, FOOT, 14, False, GREY)


# ------------------------------------------------------------------ figures
def fig_anscombe(path):
    x = [10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5]; x4 = [8] * 7 + [19] + [8] * 3
    ys = [[8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68], [9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74],
          [7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73], [6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89]]
    fig, ax = plt.subplots(2, 2, figsize=(7.4, 5.2), sharex=True, sharey=True)
    for a, xs, y, t in zip(ax.flat, [x, x, x, x4], ys, "I II III IV".split()):
        a.scatter(xs, y, color=HEX["navy"], s=34); a.plot([3, 20], [3 + 0.5 * 3, 3 + 0.5 * 20], color=HEX["gold"], lw=2.2); a.set_title(t, fontsize=12)
        a.set_xlim(3, 20); a.set_ylim(2, 14)
    fig.tight_layout(); fig.savefig(path, dpi=160); plt.close(fig)


def fig_channels(path):
    labels = ["Position (common scale)", "Length", "Angle / slope", "Area", "Colour intensity"]; vals = [95, 80, 62, 45, 28]
    fig, a = plt.subplots(figsize=(7.4, 4.6)); a.barh(labels[::-1], vals[::-1], color=[HEX["grey"], HEX["grey"], HEX["blue"], HEX["blue"], HEX["navy"]])
    a.set_xlabel("How precisely people judge it (illustrative rank)"); a.set_xlim(0, 105)
    for s in ("top", "right"): a.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(path, dpi=160); plt.close(fig)


def fig_axis(path):
    vals = [100, 102, 103, 105]; names = ["A", "B", "C", "D"]
    fig, ax = plt.subplots(1, 2, figsize=(8.6, 3.8))
    for a, lo, t in zip(ax, [95, 0], ["Axis starts at 95 (misleading)", "Axis starts at 0 (honest)"]):
        a.bar(names, vals, color=[HEX["grey"]] * 3 + [HEX["gold"]]); a.set_ylim(lo, 107); a.set_title(t, fontsize=12)
        for s in ("top", "right"): a.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(path, dpi=160); plt.close(fig)


def fig_facets(path):
    rng = np.random.default_rng(3); fig, ax = plt.subplots(1, 4, figsize=(9.6, 2.9), sharex=True, sharey=True)
    for a, g, m in zip(ax, ["Central", "East", "South", "West"], [30, 42, 38, 50]):
        a.hist(rng.normal(m, 9, 400), bins=18, color=HEX["blue"]); a.set_title(g, fontsize=12)
        for s in ("top", "right"): a.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(path, dpi=160); plt.close(fig)


def fig_dashboard(path):
    fig = plt.figure(figsize=(8.6, 4.8)); fig.patch.set_facecolor("white")
    for i, (k, v) in enumerate([("Sales", "$2.3M"), ("Profit", "$286K"), ("Orders", "8,399"), ("Margin", "12.4%")]):
        ax = fig.add_axes([0.03 + i * 0.24, 0.78, 0.22, 0.19]); ax.set_facecolor("#F2F4FB"); ax.set_xticks([]); ax.set_yticks([])
        ax.text(0.5, 0.62, v, ha="center", fontsize=17, fontweight="bold", color=HEX["navy"]); ax.text(0.5, 0.2, k + " (KPI card)", ha="center", fontsize=10, color="#555B6E")
    ax = fig.add_axes([0.06, 0.1, 0.42, 0.55]); ax.plot(range(12), np.cumsum(np.random.default_rng(1).normal(5, 2, 12)), color=HEX["blue"], lw=2.5); ax.set_title("Trend over time", fontsize=11)
    ax2 = fig.add_axes([0.58, 0.1, 0.18, 0.55]); ax2.bar(["Tech", "Office", "Furn"], [429, 120, 68], color=[HEX["gold"], HEX["grey"], HEX["grey"]]); ax2.set_title("Breakdown", fontsize=11)
    ax3 = fig.add_axes([0.84, 0.1, 0.13, 0.55]); ax3.barh(["Central", "West"], [0.24, 0.11], color=[HEX["red"], HEX["grey"]]); ax3.set_title("Comparison", fontsize=11)
    fig.savefig(path, dpi=160); plt.close(fig)


def fig_boroughs(path):
    names = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Is."]; proper = [21985, 20376, 5751, 1107, 376]; low = [131, 122, 39, 5, 3]
    fig, a = plt.subplots(figsize=(7.4, 4.3)); x = np.arange(5); a.bar(x - 0.2, proper, 0.4, color=HEX["blue"], label="Proper case"); a.bar(x + 0.2, [l * 40 for l in low], 0.4, color=HEX["gold"], label="lowercase copies (counts ×40)")
    a.set_xticks(x); a.set_xticklabels(names); a.legend(); a.set_title("10 labels for 5 boroughs", fontsize=12)
    for s in ("top", "right"): a.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(path, dpi=160); plt.close(fig)


def fig_merge(path):
    fig, a = plt.subplots(figsize=(7.4, 3.6)); a.barh(["B only", "Both", "A only"], [0, 1000, 47895], color=[HEX["grey"], HEX["gold"], HEX["blue"]])
    for i, v in enumerate([0, 1000, 47895]): a.text(v + 500, i, f"{v:,}", va="center", fontsize=13)
    a.set_xlim(0, 56000); a.set_title("Rows by source (outer join with indicator)", fontsize=12)
    for s in ("top", "right"): a.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(path, dpi=160); plt.close(fig)


def fig_missing(path):
    fig, a = plt.subplots(figsize=(7.4, 3.6)); a.barh(["name", "host_name", "last_review", "reviews_per_month"], [0.03, 0.04, 20.58, 20.58], color=HEX["blue"])
    for i, v in enumerate([0.03, 0.04, 20.58, 20.58]): a.text(v + 0.3, i, f"{v}%", va="center", fontsize=12)
    a.set_xlim(0, 26); a.set_title("Missing share by column (79.4% of rows have no gap)", fontsize=12)
    for s in ("top", "right"): a.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(path, dpi=160); plt.close(fig)


# ------------------------------------------------------------------ L13-14
def build_l1314(out, tmp):
    prs = deck(); n = 1
    title_slide(prs, "Lectures 13-14", "Data Visualization: From Grammar to Storytelling", "Grammar of Graphics · Good vs misleading charts · Non-numeric data · Dashboards · Storytelling · Preparing Assignment 1")
    n += 1; s = base(prs, "Roadmap", "Five ideas today", n)
    bullets(s, ["1||The Grammar of Graphics: building any chart from layers", "2||Good versus misleading charts", "3||Visualizing non-numeric data: categories, hierarchies, text, networks", "4||Dashboard logic", "5||Storytelling with data", "Also prepares you for Assignment 1"])
    n += 1; s = base(prs, "Why visualize at all?", "Anscombe's quartet: same statistics, four different pictures", n)
    fig_anscombe(tmp / "anscombe.png"); picture(s, tmp / "anscombe.png", 0.6, 1.8, h=4.4)
    bullets(s, ["Same mean, same variance", "Same correlation: r = 0.82", "Same fitted line", "Yet: a clean trend, a curve, a line with one outlier, a vertical stack with one extreme point"], x=7.9, y=2.0, w=5, size=19)
    note(s, "Summary statistics compress, and compression hides structure. Only the picture shows the difference.", 6.4)
    n += 1; s = base(prs, "Grammar of Graphics", "Every chart is built from layers", n)
    cards(s, [("Data", "The table you plot."), ("Aesthetics", "Which column controls x, y, colour, size or shape."), ("Geometry", "The shape that draws the data: points, lines, bars or boxes."), ("Scales · Labels · Theme", "Axis ranges, titles, colours and fonts.")])
    note(s, "If you can name the layers, you can build or debug any chart.")
    n += 1; s = base(prs, "Visual channels", "Not all channels are equally accurate", n)
    fig_channels(tmp / "channels.png"); picture(s, tmp / "channels.png", 0.6, 1.8, h=4.5)
    bullets(s, ["People judge position on a common scale best, then length, then angle and slope, then area, and colour intensity least precisely.", "That is why bar charts and dot plots beat pie charts for comparing values.", "Put your most important comparison on the most accurate channel."], x=8.1, y=2.0, w=4.8, size=18)
    n += 1; s = base(prs, "Choosing the geometry", "Pick the chart from the question you are asking", n)
    table(s, [["Question", "Chart"], ["How is one number distributed?", "Histogram, density or box plot"], ["How do two numbers relate?", "Scatter plot"], ["How does a number change over time?", "Line chart"], ["How do groups compare?", "Bar, box or violin plot"], ["How do two categories overlap?", "Heatmap of a cross-tab"], ["How do parts make a whole?", "Stacked bar or treemap"]], colw=[6.4, 5.7], size=18)
    n += 1; s = base(prs, "Facets", "Small multiples: one chart per group", n)
    fig_facets(tmp / "facets.png"); picture(s, tmp / "facets.png", 1.6, 1.8, w=10.0)
    bullets(s, ["Facets repeat the same chart once per group in a grid.", "Every panel shares the same axes, so groups compare at a glance.", "One line of code, for example col = the grouping column in seaborn, beats piling many lines or colours onto one cluttered plot."], y=5.0, size=18, gap=4)
    n += 1; s = base(prs, "Misleading charts 1", "The truncated axis", n)
    fig_axis(tmp / "axis.png"); picture(s, tmp / "axis.png", 0.6, 1.8, w=8.3)
    bullets(s, ["Both charts show exactly the same four numbers.", "Left: the axis starts at 95, so a 5% rise looks like a five-fold jump.", "Right: the axis starts at zero and shows the true, modest change.", "When bars encode a quantity, the axis must start at zero."], x=9.1, y=2.0, w=3.9, size=17)
    n += 1; s = base(prs, "Misleading charts 2", "Other ways charts mislead", n)
    cards(s, [("Dual axes", "Two axes can be scaled to fake any correlation."), ("Cherry-picked range", "Shows only the dates that suit the story."), ("Distorted areas", "Doubling a circle's radius quadruples its area."), ("Clutter and 3-D", "Hide the data and bend the values."), ("Missing context", "No baseline, sample size or source leaves viewers guessing.")], h=3.8)
    n += 1; s = base(prs, "Honest charts", "Principles of an honest chart", n)
    bullets(s, ["Start bar charts at zero; line charts may zoom, but say so.", "Label axes with units and give an informative title.", "Use colour with purpose, and check it works for colour-blind readers.", "Remove decoration that carries no data: heavy gridlines, 3-D and shadows.", "Always show the sample size and the source."])
    n += 1; s = base(prs, "Non-numeric data", "Mean and correlation do not apply to categories, hierarchies or text", n)
    table(s, [["Data", "Natural chart"], ["Categories", "Sorted bar chart (sort by value, not alphabetically)"], ["Hierarchies", "Treemap: area shows share, nesting shows structure"], ["Text", "Word-frequency bar chart (better than a word cloud)"], ["Relationships", "Network diagram: nodes are items, edges are links"]], colw=[3.6, 8.5], size=20)
    n += 1; s = base(prs, "Dashboard logic", "A dashboard is several panels sharing one figure, built around a single purpose", n)
    fig_dashboard(tmp / "dash.png"); picture(s, tmp / "dash.png", 0.6, 1.9, h=4.4)
    bullets(s, ["Start with the audience and the decision.", "Key numbers first, in a row of KPI cards.", "Then a trend, a breakdown and one comparison.", "Same colours, scales and filters across panels.", "Fewer panels, each with a clear job."], x=8.2, y=2.0, w=4.8, size=17, gap=6)
    n += 1; s = base(prs, "Storytelling", "Turn a chart into a message", n)
    bullets(s, ["Insight titles: write Central's discount stands out, not Discount by region.", "Highlight one thing: gray out the rest and colour the bar that matters.", "Annotate the key moment directly on the chart.", "Declutter: remove everything that does not support the message."])
    n += 1; s = base(prs, "Story structure", "Context, Conflict, Resolution", n)
    cards(s, [("Context", "What is the situation, and why does it matter?"), ("Conflict", "What did the data reveal that is surprising or wrong?"), ("Resolution", "What action do you recommend, and what will it change?")], h=3.6)
    note(s, "Every chart in your presentation should serve one of these three parts.", 5.9)
    n += 1; s = base(prs, "Assignment 1", "How to structure your presentation", n)
    bullets(s, ["Problem statement: the question, the unit of observation and the target.", "Data audit: shape, types, missing values, duplicates and hidden zeros.", "Univariate and bivariate EDA with honest charts.", "Two or three hypotheses, labelled exploratory.", "A story: insight titles, one highlighted finding per slide, and a recommendation.", "Every chart needs an honest axis, labels with units and an insight title."], size=20)
    n += 1; s = base(prs, "Key takeaways", "What to remember", n)
    bullets(s, ["Statistics hide structure, so always plot. Remember Anscombe's quartet.", "Every chart is data, aesthetics, geometry, scales and theme.", "Choose the geometry from the question, and use facets for groups.", "Start bar axes at zero and avoid decoration that bends the data.", "Categories, hierarchies, text and networks each have a natural chart.", "Dashboards have one purpose; stories have one message.", "Next: the lab, where you build all of these in Python."], size=20, gap=6)
    prs.save(out / "L13-14_Data_Visualization_Grammar_to_Storytelling.pptx")


# ------------------------------------------------------------------ L15-16
def build_l1516(out, tmp):
    prs = deck(); n = 1
    title_slide(prs, "Lectures 15-16", "Data Quality, Integration and Validation", "Four dimensions of quality · Combining sources · Duplicates · Inconsistent encoding · Validation rules")
    n += 1; s = base(prs, "Roadmap", "What we learn today", n)
    bullets(s, ["The four dimensions of data quality", "How to combine data from multiple sources", "How to detect duplicates", "How to fix inconsistent encoding", "How to write validation rules", "The lab that follows runs all of this on a real merged Airbnb file"])
    n += 1; s = base(prs, "Raw versus clean", "Raw data was collected for another purpose", n)
    cards(s, [("Raw data", "Duplicates, gaps and mixed spellings. Hidden sentinel values like 0, 999 or NA. Often several files with different schemas."), ("Clean data", "One row per entity. Gaps explained. One spelling. Sentinels converted to real missing values. One integrated, documented table.")], h=3.6)
    note(s, "The rule: audit first, fix second, and re-audit after every fix.", 5.9)
    n += 1; s = base(prs, "Data quality", "Four dimensions", n)
    cards(s, [("Accuracy", "Is the value correct in the real world?"), ("Completeness", "Is everything we need present?"), ("Consistency", "Is one fact stored one way everywhere?"), ("Validity", "Does the value obey the rules?")])
    note(s, "We look at each in turn, with examples from the New York City Airbnb data.")
    n += 1; s = base(prs, "Accuracy", "Accuracy needs a reference", n)
    bullets(s, ["Check a value against reality, a trusted source or a peer group.", "A private room in Queens listed at $10,000 a night, against a peer median of $59.", "A good proxy: the median price of listings with the same borough and room type.", "Flag suspicious values rather than deleting them: the true value is unknown, and deleting real rows biases the data.", "Decide whether to cap, fix or remove later, once you know why."], size=21)
    n += 1; s = base(prs, "Completeness", "How much is missing, and why?", n)
    fig_missing(tmp / "missing.png"); picture(s, tmp / "missing.png", 0.6, 1.8, h=3.9)
    bullets(s, ["Measure the missing share per column, and the share of rows with no gap at all: only 79.4% here.", "Why? Every listing missing last_review has zero reviews, so the gap is structural, not random.", "Coverage matters too: a column can be fully filled and still never contain January or April."], x=8.1, y=1.9, w=4.9, size=17)
    n += 1; s = base(prs, "Consistency", "One fact, one way", n)
    fig_boroughs(tmp / "boroughs.png"); picture(s, tmp / "boroughs.png", 0.6, 1.8, h=4.0)
    bullets(s, ["Ten labels for five boroughs: lowercase copies sit next to the proper-case ones.", "A group by gives ten groups instead of five.", "It breaks across rows, across columns (price and price in dollars) and across sources (Manhattan versus manhattan).", "Fix: choose one standard form and apply it everywhere."], x=8.1, y=1.9, w=4.9, size=17)
    n += 1; s = base(prs, "Validity", "Write the rules first, test every row against every rule", n)
    table(s, [["Rule type", "Example", "Result in the lab"], ["Range", "price >= 0", "0 failures"], ["Set", "room type is one of three allowed values", "300 failures (lowercase)"], ["Format / type", "price is an integer", "passes"], ["Geographic box", "latitude inside New York", "5 failures: real Staten Island listings"], ["Uniqueness", "IDs unique, no duplicate rows or columns", "checked after cleaning"]], colw=[2.8, 5.2, 4.1], size=17)
    n += 1; s = base(prs, "Validity versus accuracy", "A value can pass one check and fail the other", n)
    cards(s, [("Validity asks", "Is it possible? Checked against a rule."), ("Accuracy asks", "Is it correct? Checked against reality.")], h=2.6)
    bullets(s, ["A $10,000 room passes every validity rule and is still wrong.", "The five latitude failures are real, so rules need review too."], y=4.9, size=22)
    n += 1; s = base(prs, "Data integration", "Four steps", n)
    cards(s, [("1  Match a key", "Find a shared identifier and check it is unique in each source."), ("2  Align the schema", "Rename columns so both sources use the same names and types."), ("3  Resolve conflicts", "Where sources disagree, decide which one wins and why."), ("4  Re-audit", "Check the merged table for duplicates, gaps and new conflicts.")])
    n += 1; s = base(prs, "Merging in practice", "Outer join with an indicator column", n)
    fig_merge(tmp / "merge.png"); picture(s, tmp / "merge.png", 0.6, 1.8, h=3.7)
    bullets(s, ["The indicator shows whether each row is in A only, B only, or both.", "Compare matched rows field by field: 300 borough conflicts, 300 room type conflicts, 0 price conflicts.", "All were case differences only, so keep source A's spelling.", "Result: 48,895 rows with no duplicates."], x=8.1, y=1.9, w=4.9, size=17)
    n += 1; s = base(prs, "Duplicates", "Three kinds", n)
    cards(s, [("Exact", "Every column identical: 700 rows in the lab."), ("Same key", "Same ID, other fields differ: 1,000 rows, the 700 copies plus 300 lowercase rows."), ("Near-duplicates", "Almost the same after cleaning text, such as the same host with a similar name: 481 candidates.")], h=3.4)
    note(s, "Exact duplicates can be dropped automatically. Near-duplicates should be reviewed by a person.", 5.7)
    n += 1; s = base(prs, "Inconsistent encoding", "Standardise, then re-audit", n)
    bullets(s, ["Strip whitespace, fix the case, and collapse repeated spaces.", "For messy codes, use a mapping so BK, Bklyn and brooklyn all become Brooklyn.", "But standardising can create new duplicates: after title-casing, the 300 lowercase rows became exact copies of other rows.", "Order matters, so re-run the audit after every fix."], size=22)
    n += 1; s = base(prs, "Validation rules", "One reusable rule table", n)
    bullets(s, ["Range rules: price at least zero; availability between 0 and 365.", "Type rules: price is an integer.", "Uniqueness rules: unique IDs; no duplicate rows or columns.", "Set rules: room type and borough in the allowed sets.", "Write the rules once and re-run them on every new load.", "In the lab, all twelve rules pass after cleaning."], size=21)
    n += 1; s = base(prs, "Workflow", "Audit, diagnose, fix, validate", n)
    cards(s, [("Audit", "Shape, types, missing values and duplicates."), ("Diagnose", "Test accuracy, completeness, consistency and validity."), ("Fix", "Integrate sources, deduplicate and standardise."), ("Validate", "Re-run the rules, re-audit and document what you did.")])
    note(s, "Document the steps so that someone else can trust and repeat them.")
    n += 1; s = base(prs, "Key takeaways", "What to remember", n)
    bullets(s, ["Data quality has four dimensions: accuracy, completeness, consistency and validity.", "Validity is checked against rules, accuracy against reality.", "Completeness includes why data is missing and which categories never appear.", "Integrate sources on a key, align schemas, resolve conflicts, then re-audit.", "Standardising can create new duplicates, so re-audit after every fix.", "Document the rules and re-run them on every load.", "Next: the lab."], size=21, gap=6)
    prs.save(out / "L15-16_Data_Quality_Integration_and_Validation.pptx")


def main():
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as t:
        tmp = pathlib.Path(t)
        for f in (fig_anscombe, fig_channels, fig_axis, fig_facets, fig_dashboard, fig_boroughs, fig_merge, fig_missing):
            pass
        fig_anscombe(tmp / "anscombe.png"); fig_channels(tmp / "channels.png"); fig_axis(tmp / "axis.png"); fig_facets(tmp / "facets.png")
        fig_dashboard(tmp / "dash.png"); fig_boroughs(tmp / "boroughs.png"); fig_merge(tmp / "merge.png"); fig_missing(tmp / "missing.png")
        build_l1314(out, tmp); build_l1516(out, tmp)
    for f in out.glob("*.pptx"):
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(out), str(f)], check=True, capture_output=True)
    print(sorted(p.name for p in out.iterdir()))


if __name__ == "__main__":
    main()
