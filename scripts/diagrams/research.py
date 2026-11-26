"""Draw the research-and-paper-writing diagrams (research/).

    python3 scripts/diagrams/research.py      # run from the vault root

Output: research/images/rs-*.svg. These pictures carry ideas rather than numbers, so the
checks here are structural: every stage the lessons name appears in the picture, in order.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, FONT, Svg, flowchart, save_dot  # noqa: E402

OUT = os.path.join('research', 'images')
BLUE = '#2563eb'
ORANGE = '#f59e0b'
GREEN = '#059669'
GREY = '#6b7280'
KNOWN = '#dbeafe'

# The lifecycle the lesson lists, in order; the picture is drawn from this list.
LIFECYCLE = ['curiosity', 'a question', 'read the literature', 'a sharp question or hypothesis', 'design a method',
             'run experiments or build', 'analyse honestly', 'write it up', 'peer review', 'publish',
             'others build on it']


def knowledge_edge():
    s = Svg(620, 360, 'Report versus research. The blue region is everything people already know, and its curved edge is '
                      'the limit of what anyone knows. A report (the dot inside) gathers and summarises knowledge that is '
                      'already inside the region. Research pushes the edge out: the small orange bump is a contribution, a '
                      'piece of new knowledge that was not inside before')
    s.add(f'<path d="M 0 360 L 0 120 Q 300 20 620 150 L 620 360 Z" fill="{KNOWN}" stroke="{BLUE}" stroke-width="2.5"/>')
    s.text(130, 300, 'everything people already know', size=14, weight='bold', color=BLUE)
    # the bump: a small region pushed out past the edge around x = 420
    s.add(f'<path d="M 385 87 Q 420 30 455 95 Z" fill="{ORANGE}" fill-opacity="0.85" stroke="{INK}" stroke-width="1.4"/>')
    s.text(470, 40, 'research: a contribution', size=13, weight='bold', color=ORANGE, anchor='start')
    s.text(470, 58, 'pushes the edge out', size=12, color=ORANGE, anchor='start')
    s.line(465, 46, 432, 60, color=ORANGE, width=1.6)
    for x, y in ((150, 220), (260, 190), (210, 250), (330, 240)):
        s.circle(x, y, 4, GREY)
    s.circle(250, 215, 9, GREEN)
    s.text(300, 190, 'a report: gathers what', size=12.5, weight='bold', color=GREEN, anchor='start')
    s.text(300, 206, 'is already known', size=12.5, weight='bold', color=GREEN, anchor='start')
    s.line(296, 200, 262, 213, color=GREEN, width=1.4)
    s.text(24, 150, 'the edge: the limit of what anyone knows', size=12.5, color=BLUE, weight='bold', anchor='start')
    s.save('rs-knowledge-edge.svg', OUT)


def lifecycle():
    assert LIFECYCLE[0] == 'curiosity' and LIFECYCLE[-1] == 'others build on it' and len(LIFECYCLE) == 11
    part = {0: 'A', 1: 'A', 2: 'A', 3: 'A', 4: 'A', 5: 'A', 6: 'A', 7: 'B', 8: 'C', 9: 'C', 10: 'C'}
    fills = {'A': '#dbeafe', 'B': '#d1fae5', 'C': '#fef3c7'}
    lines = ['digraph { bgcolor="white"; pad=0.25; rankdir=TB; nodesep=0.3; ranksep=0.28;',
             f'node [fontname="{FONT}", fontsize=13, shape=box, style="rounded,filled", color="{INK}", width=3.2];',
             f'edge [fontname="{FONT}", fontsize=11, color="{INK}"];']
    for i, name in enumerate(LIFECYCLE):
        lines.append(f'n{i} [label="{name}", fillcolor="{fills[part[i]]}"];')
    for i in range(len(LIFECYCLE) - 1):
        lines.append(f'n{i} -> n{i + 1};')
    lines.append(f'n{len(LIFECYCLE) - 1} -> n1 [constraint=false, color="{ORANGE}", penwidth=2, label="  new questions"];')
    lines.append('}')
    save_dot('\n'.join(lines), 'rs-lifecycle.svg',
             'The research lifecycle as a loop: curiosity leads to a question; you read the literature and sharpen it into a '
             'question or hypothesis; design a method; run experiments or build; analyse honestly (part A of the course, blue); '
             'write it up (part B, green); go through peer review, publish, and others build on it (part C, yellow), which '
             'raises new questions and starts the loop again', OUT)


PASSES = [('Pass 1: the flyover', '5–10 minutes', 'title, abstract, introduction, headings, conclusion, figures', 100),
          ('Pass 2: the walk-through', 'about an hour', 'the whole paper, skipping proofs; study every figure', 10),
          ('Pass 3: the deep dive', 'several hours', 'rebuild it yourself; challenge every choice', 3)]


def three_pass():
    assert [n for *_, n in PASSES] == [100, 10, 3]
    s = Svg(640, 330, 'The three-pass method as a funnel. Pass 1, the flyover, takes 5 to 10 minutes and reads only the title, '
                      'abstract, introduction, headings, conclusion and figures; you do it for about 100 papers. Pass 2, the '
                      'walk-through, takes about an hour and reads the whole paper but skips the proofs; about 10 papers get it. '
                      'Pass 3, the deep dive, takes several hours and rebuilds the paper yourself; only about 3 papers get it')
    widths = [620, 500, 380]
    fills = ['#dbeafe', '#d1fae5', '#fef3c7']
    for i, ((name, time, what, n), w, fill) in enumerate(zip(PASSES, widths, fills)):
        x, y = 320 - w / 2, 20 + i * 100
        nxt = widths[i + 1] if i + 1 < len(widths) else w - 60
        s.add(f'<polygon points="{x},{y} {x + w},{y} {320 + nxt / 2},{y + 88} {320 - nxt / 2},{y + 88}" fill="{fill}" '
              f'stroke="{INK}" stroke-width="1.4"/>')
        s.text(320, y + 26, f'{name}  ·  {time}', size=14, weight='bold')
        s.text(320, y + 48, what, size=12, color=GREY)
        s.text(320, y + 72, f'about {n} papers', size=13, weight='bold', color=BLUE)
    s.save('rs-three-pass.svg', OUT)


def citation_map():
    s = Svg(640, 340, 'Mapping a field from one survey paper. The survey sits in the middle. Following its references backward '
                      'leads to older papers on the left; the one that almost everything cites is a seminal paper, drawn '
                      'bigger. Following "cited by" forward leads to newer papers on the right, which show where the frontier '
                      'is now. Time runs from left to right')
    s.line(40, 310, 600, 310, color=GREY, width=1.4)
    s.add(f'<polygon points="600,310 590,305 590,315" fill="{GREY}"/>')
    s.text(320, 330, 'older  →  newer', size=12, color=GREY)
    nodes = {'survey': (320, 160, 34, ORANGE, 'the survey'),
             'seminal': (90, 110, 30, BLUE, 'seminal'),
             'old1': (150, 220, 18, BLUE, ''), 'old2': (210, 80, 18, BLUE, ''), 'old3': (230, 250, 16, BLUE, ''),
             'new1': (460, 90, 18, GREEN, ''), 'new2': (520, 190, 18, GREEN, ''), 'new3': (430, 250, 16, GREEN, ''),
             'new4': (580, 120, 16, GREEN, 'frontier')}
    edges = [('survey', 'seminal'), ('survey', 'old1'), ('survey', 'old2'), ('survey', 'old3'), ('old1', 'seminal'),
             ('old2', 'seminal'), ('old3', 'seminal'), ('new1', 'survey'), ('new2', 'survey'), ('new3', 'survey'),
             ('new4', 'new1'), ('new2', 'seminal')]
    for a, b in edges:
        (x1, y1, r1, *_), (x2, y2, r2, *_) = nodes[a], nodes[b]
        d = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / d, (y2 - y1) / d
        sx, sy, ex, ey = x1 + ux * r1, y1 + uy * r1, x2 - ux * (r2 + 2), y2 - uy * (r2 + 2)
        s.line(sx, sy, ex, ey, color=GREY, width=1.3)
        s.add(f'<polygon points="{ex:.1f},{ey:.1f} {ex - 8 * ux + 4 * uy:.1f},{ey - 8 * uy - 4 * ux:.1f} '
              f'{ex - 8 * ux - 4 * uy:.1f},{ey - 8 * uy + 4 * ux:.1f}" fill="{GREY}"/>')
    for x, y, r, col, lab in nodes.values():
        s.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}" fill-opacity="0.85" stroke="{INK}" stroke-width="1.2"/>')
        if lab:
            s.text(x, y + r + 16, lab, size=12, weight='bold', color=col)
    s.text(150, 30, '← backward: what it cites', size=13, weight='bold', color=BLUE)
    s.text(500, 30, 'forward: what cites it →', size=13, weight='bold', color=GREEN)
    s.save('rs-citation-map.svg', OUT)


def good_question_venn():
    s = Svg(580, 430, 'A good research question as three overlapping circles: novel (nobody has answered it), significant (the '
                      'answer matters to someone) and feasible (you can do it with your time, skills and equipment). Only the '
                      'small middle, where all three overlap, is a good question; outside it, a question is already answered, '
                      'or nobody cares, or it is out of reach')
    circles = [(210, 170, BLUE, 'novel', 'nobody has answered it', (80, 40)),
               (350, 170, GREEN, 'significant', 'the answer matters', (480, 40)),
               (280, 280, ORANGE, 'feasible', 'you can actually do it', (470, 400))]
    for cx, cy, col, name, sub, (lx, ly) in circles:
        s.add(f'<circle cx="{cx}" cy="{cy}" r="110" fill="{col}" fill-opacity="0.18" stroke="{col}" stroke-width="2.5"/>')
        s.text(lx, ly, name, size=15, weight='bold', color=col)
        s.text(lx, ly + 18, sub, size=12, color=GREY)
    s.add(f'<circle cx="280" cy="205" r="7" fill="{INK}"/>')
    s.text(280, 232, 'a good question', size=13, weight='bold')
    s.save('rs-good-question.svg', OUT)


def lit_review_shapes():
    s = Svg(660, 330, 'Two ways to write a literature review. Left, a list in date order: Smith 2015 did this, then Okafor 2018, '
                      'then Lee 2020, then Bello 2023, each described on its own; it shows reading but no understanding, and no '
                      'gap. Right, the same papers grouped by theme into two boxes, what the groups show together, and an arrow '
                      'from the themes to the gap: what nobody has done yet, which is what your study does')
    s.text(160, 26, 'a list by date: avoid', size=14, weight='bold', color='#dc2626')
    for i, name in enumerate(['Smith 2015 did …', 'Okafor 2018 did …', 'Lee 2020 did …', 'Bello 2023 did …']):
        s.rect(60, 46 + i * 62, 200, 44, '#f3f4f6', stroke=GREY)
        s.text(160, 73 + i * 62, name, size=12.5, color=GREY)
    s.line(330, 20, 330, 310, color='#d1d5db', width=1)
    s.text(500, 26, 'grouped by theme: do this', size=14, weight='bold', color=GREEN)
    for i, (theme, who) in enumerate([('theme A: what they agree on', 'Smith 2015, Lee 2020'),
                                      ('theme B: where they differ', 'Okafor 2018, Bello 2023')]):
        y = 46 + i * 86
        s.rect(380, y, 240, 66, '#dbeafe', stroke=BLUE)
        s.text(500, y + 28, theme, size=12.5, weight='bold', color=BLUE)
        s.text(500, y + 48, who, size=11.5, color=GREY)
    s.line(500, 200, 500, 236, color=ORANGE, width=2.5)
    s.add(f'<polygon points="500,244 494,232 506,232" fill="{ORANGE}"/>')
    s.rect(380, 248, 240, 54, '#fef3c7', stroke=ORANGE)
    s.text(500, 272, 'the gap: nobody has yet …', size=12.5, weight='bold', color=ORANGE)
    s.text(500, 290, 'which is what your study does', size=11.5, color=GREY)
    s.save('rs-lit-review-shapes.svg', OUT)


def scope_scale():
    s = Svg(660, 230, 'Scoping a research question on a scale from too broad to too narrow, using the weather study. Too broad: '
                      'make weather forecasting accurate, which is a whole career. Just right: how accurate are three free weather '
                      'apps for next-day rain and temperature in Lagos over four weeks, which one person can answer convincingly. '
                      'Too narrow: was one app right about rain on one Tuesday, which nobody would care about')
    s.add(f'<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#fecaca"/><stop offset="0.5" '
          f'stop-color="#bbf7d0"/><stop offset="1" stop-color="#fecaca"/></linearGradient></defs>')
    s.rect(30, 70, 600, 26, 'url(#g)', stroke=INK)
    items = [(80, 'too broad', '"Make weather forecasts', 'accurate": a career'),
             (330, 'just right', '"How accurate are 3 free apps', 'for next-day rain in Lagos, 4 weeks?"'),
             (580, 'too narrow', '"Was one app right about', 'rain one Tuesday?": so what?')]
    for x, head, l1, l2 in items:
        col = GREEN if head == 'just right' else '#dc2626'
        s.add(f'<polygon points="{x},{100} {x - 8},{116} {x + 8},{116}" fill="{col}"/>')
        s.text(x, 60, head, size=14, weight='bold', color=col)
        s.text(x, 140, l1, size=12)
        s.text(x, 158, l2, size=12)
    s.text(330, 205, 'aim for one question you can answer convincingly in one focused piece of work', size=12.5, color=GREY)
    s.save('rs-scope-scale.svg', OUT)


# Lesson 04: one worked week of the weather study. The lesson quotes these numbers, so they are asserted here.
WEEK = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
APP_SAYS_RAIN = [True, True, False, True, False, False, True]     # app's chance of rain is 50% or more
GAUGE_RAIN = [True, False, False, True, True, False, True]        # gauge caught 1 mm or more
FORECAST_MAX = [30, 29, 31, 30, 32, 31, 29]                       # app's forecast high, °C
ACTUAL_MAX = [28, 29, 33, 30, 31, 30, 28]                         # measured high, °C
RED = '#dc2626'


def week_numbers():
    hits = sum(a == g for a, g in zip(APP_SAYS_RAIN, GAUGE_RAIN))
    errors = [abs(f - a) for f, a in zip(FORECAST_MAX, ACTUAL_MAX)]
    assert hits == 5 and round(100 * hits / 7) == 71
    assert errors == [2, 0, 2, 0, 1, 1, 1] and sum(errors) / 7 == 1.0
    # the "tomorrow will be like today" guess: Monday's guess is Sunday's rain from the week before (dry)
    persistence = [False] + GAUGE_RAIN[:-1]
    p_hits = sum(p == g for p, g in zip(persistence, GAUGE_RAIN))
    assert persistence == [False, True, False, False, True, True, False] and p_hits == 2
    return hits, errors, p_hits


def question_funnel():
    s = Svg(660, 330, 'The funnel from topic to hypothesis, using the weather study. Top, widest: the topic, weather apps in '
                      'Lagos, which is a direction, not something you can answer. Middle: the question, how often is each free '
                      'app right about tomorrow\'s rain, over four weeks of rainy season, which you can answer. Bottom, '
                      'narrowest: the hypothesis, each app is right about rain more often than simply guessing tomorrow will be '
                      'like today, a predicted answer that could turn out false')
    rows = [('topic', 'weather apps in Lagos', 'a direction: you can\'t answer it', '#dbeafe', 640),
            ('question', 'how often is each app right about tomorrow\'s rain, over 4 weeks?', 'answerable: you know when you\'re done', '#d1fae5', 540),
            ('hypothesis', 'each app beats "tomorrow will be like today"', 'a predicted answer that could be wrong', '#fef3c7', 440)]
    for i, (name, text, note, fill, w) in enumerate(rows):
        x, y = 330 - w / 2, 15 + i * 105
        nxt = rows[i + 1][4] if i + 1 < len(rows) else w - 80
        s.add(f'<polygon points="{x},{y} {x + w},{y} {330 + nxt / 2},{y + 95} {330 - nxt / 2},{y + 95}" fill="{fill}" '
              f'stroke="{INK}" stroke-width="1.4"/>')
        s.text(330, y + 26, name, size=15, weight='bold', color=BLUE)
        s.text(330, y + 50, text, size=12.5, weight='bold')
        s.text(330, y + 72, note, size=12, color=GREY)
    s.save('rs-question-funnel.svg', OUT)


def rain_week():
    hits, _, p_hits = week_numbers()
    s = Svg(660, 300, 'One week of the weather study, scored for rain. For each day, Monday to Sunday, the top row shows whether '
                      'the app said rain (its chance of rain was 50 percent or more) and the second row whether the rain gauge '
                      'caught 1 millimetre or more. The app was right on Monday, Wednesday, Thursday, Saturday and Sunday, five '
                      'days out of seven, a hit rate of 71 percent. On Tuesday it said rain and none fell, a false alarm; on '
                      'Friday it said dry and rain fell, a missed rain')
    s.text(20, 80, 'app said rain?', size=12.5, weight='bold', anchor='start')
    s.text(20, 140, 'gauge: 1 mm+?', size=12.5, weight='bold', anchor='start')
    s.text(20, 200, 'right?', size=12.5, weight='bold', anchor='start')
    for i, (day, a, g) in enumerate(zip(WEEK, APP_SAYS_RAIN, GAUGE_RAIN)):
        x = 150 + i * 70
        s.text(x + 28, 36, day, size=13, weight='bold')
        for y, v in ((55, a), (115, g)):
            s.rect(x, y, 56, 40, '#dbeafe' if v else '#f3f4f6', stroke=GREY)
            s.text(x + 28, y + 26, 'rain' if v else 'dry', size=12.5, color=BLUE if v else GREY, weight='bold' if v else 'normal')
        ok = a == g
        s.rect(x, 175, 56, 40, '#d1fae5' if ok else '#fee2e2', stroke=GREEN if ok else RED)
        s.text(x + 28, 201, 'yes' if ok else 'no', size=13, weight='bold', color=GREEN if ok else RED)
        if not ok:
            s.text(x + 28, 233, 'false alarm' if a else 'missed rain', size=11.5, color=RED)
    s.text(330, 275, f'hit rate = {hits} right ÷ 7 days = {round(100 * hits / 7)}%', size=15, weight='bold', color=GREEN)
    s.save('rs-rain-week.svg', OUT)


def temp_week():
    _, errors, _ = week_numbers()
    s = Svg(660, 330, 'The same week scored for temperature. For each day the blue dot is the app\'s forecast high and the '
                      'orange dot is the measured high, in degrees Celsius, on a scale from 27 to 34. The grey gap between them '
                      'is that day\'s error, ignoring which way it was wrong: 2, 0, 2, 0, 1, 1 and 1 degrees. Their average is 7 '
                      'divided by 7, an average error of 1.0 degree')
    y0, top, lo, hi = 250, 40, 27, 34
    ty = lambda t: y0 - (t - lo) * (y0 - top) / (hi - lo)
    for t in range(lo, hi + 1):
        s.line(70, ty(t), 620, ty(t), color='#e5e7eb', width=1)
        s.text(60, ty(t) + 4, f'{t}°', size=11.5, color=GREY, anchor='end')
    for i, (day, f, a, e) in enumerate(zip(WEEK, FORECAST_MAX, ACTUAL_MAX, errors)):
        x = 110 + i * 78
        if e:
            s.line(x, ty(f), x, ty(a), color=GREY, width=4)
        s.circle(x - (4 if not e else 0), ty(f), 7, BLUE)
        s.circle(x + (4 if not e else 0), ty(a), 7, ORANGE)
        s.text(x, y0 + 22, day, size=12.5, weight='bold')
        s.text(x, y0 + 40, f'off by {e}°', size=11.5, color=GREY)
    s.circle(90, 18, 6, BLUE); s.text(102, 22, 'app forecast high', size=12, anchor='start')
    s.circle(260, 18, 6, ORANGE); s.text(272, 22, 'measured high', size=12, anchor='start')
    s.text(330, 318, f'average error = ({" + ".join(map(str, errors))}) ÷ 7 = {sum(errors) / 7:.1f}°C', size=14.5,
           weight='bold', color=GREEN)
    s.save('rs-temp-week.svg', OUT)


def variables():
    s = Svg(660, 320, 'The four kinds of variable in the weather study. The independent variable, which app, is what you '
                      'change; an arrow runs from it to the dependent variable, the rain hit rate and temperature error, which '
                      'is what you measure. Below, the controlled variables are held the same for every app: the same time of '
                      'reading, the same location setting, the same rain gauge. Above, a confound sneaks in with a dashed '
                      'arrow: if you read app A at 6 pm but app B at 10 pm, app B has seen four more hours of weather, and that, '
                      'not the app, could be why it scores better')
    s.rect(30, 110, 200, 80, '#dbeafe', stroke=BLUE, width=2)
    s.text(130, 140, 'independent', size=14, weight='bold', color=BLUE)
    s.text(130, 162, 'which app: A, B or C', size=12.5)
    s.text(130, 180, 'you change it', size=11.5, color=GREY)
    s.rect(430, 110, 200, 80, '#d1fae5', stroke=GREEN, width=2)
    s.text(530, 140, 'dependent', size=14, weight='bold', color=GREEN)
    s.text(530, 162, 'hit rate, temperature error', size=12.5)
    s.text(530, 180, 'you measure it', size=11.5, color=GREY)
    s.line(232, 150, 420, 150, color=INK, width=2.5)
    s.add(f'<polygon points="428,150 416,144 416,156" fill="{INK}"/>')
    s.text(330, 142, 'does it affect?', size=12, color=GREY)
    s.rect(130, 230, 400, 70, '#f3f4f6', stroke=GREY)
    s.text(330, 254, 'controlled: kept the same for every app', size=13.5, weight='bold')
    s.text(330, 276, 'read at 8 pm · same Lagos location · same rain gauge', size=12.5, color=GREY)
    s.rect(200, 15, 260, 62, '#fee2e2', stroke=RED, width=2)
    s.text(330, 38, 'confound: sneaks in', size=13.5, weight='bold', color=RED)
    s.text(330, 58, 'app A read at 6 pm, app B at 10 pm', size=12, color=RED)
    s.line(390, 79, 470, 106, color=RED, width=2, dash='6 4')
    s.add(f'<polygon points="478,109 465,108 470,98" fill="{RED}"/>')
    s.save('rs-variables.svg', OUT)


# Lesson 05: an example of four weeks' results against the baselines. Made-up numbers, labelled as such in the lesson.
DAYS = 28
RAINY_DAYS = 16
BASELINE_HITS = {'always "rain"': 16, '"like today"': 17, 'app A': 18, 'app B': 22, 'app C': 15}


def same_days_design():
    s = Svg(660, 300, 'Two ways to schedule the weather study over four weeks. Top, unfair: app A is read in week 1, app B in '
                      'week 2 and app C in week 3, so each app faces different weather and a stormy week can make one app look '
                      'bad. Bottom, fair: all three apps are read every evening for all four weeks, in a shuffled order, so '
                      'every app faces exactly the same weather and the only difference left is the app')
    s.text(20, 30, 'unfair: one app per week', size=14, weight='bold', color=RED, anchor='start')
    for w, lab in enumerate(['app A', 'app B', 'app C', '—']):
        s.rect(40 + w * 150, 45, 140, 50, '#fee2e2' if lab != '—' else '#f3f4f6', stroke=GREY)
        s.text(110 + w * 150, 70, f'week {w + 1}: {lab}', size=12.5, weight='bold')
        s.text(110 + w * 150, 87, ['dry spell', 'storms', 'mixed', ''][w], size=11.5, color=GREY)
    s.text(20, 140, 'fair: every app, every day', size=14, weight='bold', color=GREEN, anchor='start')
    for w in range(4):
        for k, lab in enumerate(['A', 'B', 'C']):
            s.rect(40 + w * 150, 155 + k * 30, 140, 26, '#d1fae5', stroke=GREY)
            s.text(110 + w * 150, 173 + k * 30, f'week {w + 1}: app {lab}', size=12)
    s.text(330, 268, 'same weather for all three · read in a shuffled order each evening', size=12.5, color=GREY)
    s.text(330, 288, 'the only thing left that differs is the app', size=13, weight='bold', color=GREEN)
    s.save('rs-same-days.svg', OUT)


def baselines_chart():
    pct = {k: round(100 * v / DAYS) for k, v in BASELINE_HITS.items()}
    assert BASELINE_HITS['always "rain"'] == RAINY_DAYS
    assert pct == {'always "rain"': 57, '"like today"': 61, 'app A': 64, 'app B': 79, 'app C': 54}
    best_simple = max(pct['always "rain"'], pct['"like today"'])
    assert [k for k in ('app A', 'app B', 'app C') if pct[k] <= best_simple] == ['app C']
    s = Svg(660, 330, 'An example of four weeks of results, 28 days, compared with two simple baselines. Always saying rain is '
                      'right on the 16 rainy days, 57 percent. Guessing tomorrow will be like today is right on 17 days, 61 '
                      'percent. App A is right on 18 days, 64 percent, barely above the guesses. App B is right on 22 days, 79 '
                      'percent, clearly better. App C is right on 15 days, 54 percent, worse than simply always saying rain. A '
                      'dashed line marks the best simple guess, 61 percent')
    y0, top = 270, 40
    sy = lambda v: y0 - v / 100 * (y0 - top)
    for v in (0, 25, 50, 75, 100):
        s.line(80, sy(v), 630, sy(v), color='#e5e7eb', width=1)
        s.text(70, sy(v) + 4, f'{v}%', size=11.5, color=GREY, anchor='end')
    s.line(80, sy(best_simple), 630, sy(best_simple), color=ORANGE, width=2, dash='6 4')
    for i, (k, v) in enumerate(BASELINE_HITS.items()):
        x = 110 + i * 105
        simple = not k.startswith('app')
        col = GREY if simple else (RED if pct[k] <= best_simple else BLUE)
        s.rect(x, sy(pct[k]), 70, y0 - sy(pct[k]), col, opacity=0.8)
        s.text(x + 35, sy(pct[k]) + 22, f'{v}/28', size=12.5, weight='bold', color='#ffffff')
        s.text(x + 35, sy(pct[k]) + 40, f'{pct[k]}%', size=12.5, weight='bold', color='#ffffff')
        s.text(x + 35, y0 + 20, k, size=12.5, weight='bold')
        s.text(x + 35, y0 + 37, 'simple guess' if simple else 'forecast app', size=11, color=GREY)
    s.text(632, sy(best_simple) - 6, 'best guess', size=11.5, color=ORANGE, anchor='end', weight='bold')
    s.text(330, 22, 'example: hit rate over 28 rainy-season days', size=14, weight='bold')
    s.save('rs-baselines.svg', OUT)


VALIDITY = [('internal', 'is the difference down to the app?', 'all apps, same days, same time', BLUE),
            ('construct', 'are you measuring what you mean?', 'gauge read at 7 am: 7 hours spill over', GREEN),
            ('external', 'does it hold beyond your setup?', 'one season, one area of Lagos', ORANGE),
            ('statistical', 'is the difference bigger than luck?', '28 days: 2 days\' gap may be chance', '#7c3aed')]


def validity_grid():
    assert [v[0] for v in VALIDITY] == ['internal', 'construct', 'external', 'statistical']
    s = Svg(660, 300, 'The four kinds of validity, each with its question and a threat from the weather study. Internal: is the '
                      'difference down to the app? Guarded by reading all apps on the same days at the same time. Construct: are '
                      'you measuring what you mean? Reading the gauge at 7 am means 7 hours of the next day spill into each '
                      'reading. External: does the result hold beyond your setup? Only one season and one area of Lagos were '
                      'tested. Statistical: is the difference bigger than luck? Over 28 days, a gap of 2 days may be chance')
    for i, (name, q, ex, col) in enumerate(VALIDITY):
        x, y = 20 + (i % 2) * 320, 20 + (i // 2) * 140
        s.rect(x, y, 300, 125, '#ffffff', stroke=col, width=2.5)
        s.text(x + 150, y + 32, f'{name} validity', size=15, weight='bold', color=col)
        s.text(x + 150, y + 60, q, size=12.5, weight='bold')
        s.text(x + 150, y + 90, 'weather study:', size=11.5, color=GREY)
        s.text(x + 150, y + 108, ex, size=12, color=GREY)
    s.save('rs-validity.svg', OUT)


# Lesson 06: app B (22/28) against "tomorrow will be like today" (17/28), from lesson 05's example, split by day.
PAIRED = {'both right': 15, 'only app B right': 7, 'only the guess right': 2, 'both wrong': 4}


def binom_tail(n, k):
    from math import comb
    return sum(comb(n, i) for i in range(k, n + 1)), 2 ** n


def paired_days():
    p = PAIRED
    assert sum(p.values()) == DAYS
    assert p['both right'] + p['only app B right'] == BASELINE_HITS['app B']
    assert p['both right'] + p['only the guess right'] == BASELINE_HITS['"like today"']
    s = Svg(660, 300, 'The 28 days of the example split four ways, comparing app B with the guess that tomorrow will be like '
                      'today. On 15 days both were right and on 4 days both were wrong; those 19 days say nothing about which is '
                      'better, so they are greyed out. On 7 days only app B was right, and on 2 days only the guess was right. '
                      'Only these 9 days where they disagree count: app B won 7 of them')
    cols = {'both right': '#f3f4f6', 'only app B right': BLUE, 'only the guess right': ORANGE, 'both wrong': '#9ca3af'}
    i = 0
    for k, n in p.items():
        for _ in range(n):
            x, y = 40 + (i % 14) * 42, 40 + (i // 14) * 48
            s.rect(x, y, 36, 40, cols[k], stroke=GREY)
            i += 1
    legend = [(40, 'both right: 15', '#9ca3af'), (200, 'only app B right: 7', BLUE), (390, 'only guess right: 2', ORANGE),
              (560, 'both wrong: 4', '#6b7280')]
    for x, t, c in legend:
        s.text(x, 170, t, size=12.5, weight='bold', color=c, anchor='start')
    s.text(330, 215, 'the 19 grey days can\'t tell you which is better: they agreed', size=13, color=GREY)
    s.text(330, 245, 'only the 9 days they disagreed count: app B won 7, the guess won 2', size=14, weight='bold')
    s.text(330, 275, 'question: could 7 out of 9 happen by luck?', size=13.5, weight='bold', color=GREEN)
    s.save('rs-paired-days.svg', OUT)


def coin_flip_test():
    hits4, total4 = binom_tail(9, 7)
    hits8, total8 = binom_tail(18, 14)
    assert (hits4, total4) == (46, 512) and round(hits4 / total4, 2) == 0.09
    assert (hits8, total8) == (4048, 262144) and round(hits8 / total8, 3) == 0.015
    from math import comb
    s = Svg(680, 340, 'The coin-flip test. If app B and the guess were really equally good, each disagreement day would be a '
                      'coin flip. Left, 4 weeks: the bars show how often each number of wins out of 9 would happen by luck; the '
                      'orange bars, 7 or more wins, add up to 46 in 512, about 0.09, so 7 out of 9 happens by luck about 9 times '
                      'in 100. Right, 8 weeks with the same pattern, 14 wins out of 18: the orange tail, 14 or more, adds up to '
                      'about 0.015, under 2 times in 100, so luck is a much poorer explanation')
    panels = [(20, 9, 7, '4 weeks: app B won 7 of 9', hits4 / total4), (350, 18, 14, '8 weeks: app B won 14 of 18', hits8 / total8)]
    for x0, n, k, title, pv in panels:
        w, base, h = 310, 260, 190
        peak = comb(n, n // 2) / 2 ** n
        bw = w / (n + 1)
        s.text(x0 + w / 2, 28, title, size=13.5, weight='bold')
        for i in range(n + 1):
            pr = comb(n, i) / 2 ** n
            bh = pr / peak * h
            s.rect(x0 + i * bw + 1, base - bh, bw - 2, bh, ORANGE if i >= k else '#cbd5e1')
            if n <= 9 or i % 3 == 0:
                s.text(x0 + i * bw + bw / 2, base + 16, str(i), size=11, color=GREY)
        s.text(x0 + w / 2, base + 36, 'wins out of ' + str(n) + ', if it were pure luck', size=11.5, color=GREY)
        s.text(x0 + w / 2, base + 62, f'chance of {k} or more by luck: p ≈ {pv:.2f}' if n == 9 else
               f'chance of {k} or more by luck: p ≈ {pv:.3f}', size=13, weight='bold', color=ORANGE)
    s.save('rs-coin-flip-test.svg', OUT)


# Lesson 07: honest mistake, grey zone, misconduct. Each band's examples come from the weather study.
INTEGRITY = [('honest mistake', 'fix it openly and log it', ['typed 32 for 23, then corrected it', 'with a dated note']),
             ('grey zone', 'questionable practices', ['dropping the storm week "as unusual"', 'trying thresholds until one wins']),
             ('misconduct', 'fabrication, falsification, plagiarism', ['filling a missed gauge reading', 'from memory; copying a review'])]


def integrity_spectrum():
    assert [b[0] for b in INTEGRITY] == ['honest mistake', 'grey zone', 'misconduct']
    s = Svg(660, 250, 'Research integrity as a spectrum, with weather-study examples. Left, green: an honest mistake, such as '
                      'typing 32 for 23 and then correcting it with a dated note, is fixed openly. Middle, amber: the grey zone '
                      'of questionable practices, such as dropping the storm week as unusual or trying thresholds until one '
                      'wins. Right, red: misconduct, which is fabrication, falsification or plagiarism, such as filling in a '
                      'missed gauge reading from memory or copying someone else\'s literature review')
    s.add('<defs><linearGradient id="ig" x1="0" x2="1"><stop offset="0" stop-color="#bbf7d0"/><stop offset="0.5" '
          'stop-color="#fde68a"/><stop offset="1" stop-color="#fecaca"/></linearGradient></defs>')
    s.rect(30, 30, 600, 30, 'url(#ig)', stroke=INK)
    for i, (name, sub, ex) in enumerate(INTEGRITY):
        x = 130 + i * 200
        col = [GREEN, '#b45309', RED][i]
        s.text(x, 90, name, size=15, weight='bold', color=col)
        s.text(x, 110, sub, size=12, color=GREY)
        s.text(x, 150, 'weather study:', size=11.5, color=GREY)
        s.text(x, 170, ex[0], size=12)
        s.text(x, 188, ex[1], size=12)
    s.text(330, 232, 'what keeps you safe across all three: keep the raw data, and report what you actually did', size=12.5,
           weight='bold')
    s.save('rs-integrity-spectrum.svg', OUT)


DATA_TRAIL = ['data-raw.csv: what you wrote down, never edited', 'corrections.md: each fix, dated, with the reason',
              'data.csv: raw data with the logged fixes applied', 'analyse.py', 'results.md']


def data_trail():
    assert DATA_TRAIL[0].startswith('data-raw.csv') and DATA_TRAIL[-1] == 'results.md'
    flowchart([(DATA_TRAIL[0], 'data'), (DATA_TRAIL[1], 'fixed'), (DATA_TRAIL[2], 'data'), (DATA_TRAIL[3], 'prog'),
               (DATA_TRAIL[4], 'fixed')], 'rs-data-trail.svg',
              'The data trail from notebook to results. data-raw.csv holds exactly what you wrote down and is never '
              'edited. corrections.md lists each fix with its date and reason. data.csv is the raw data with only those '
              'logged fixes applied. analyse.py reads data.csv and produces results.md. Anyone can follow every number in '
              'the results back to what was first written down', OUT,
              notes=['', 'apply only the logged fixes', '', 'scores it'])


def ethics_check():
    lines = ['digraph { bgcolor="white"; pad=0.25; rankdir=TB; nodesep=0.35; ranksep=0.3;',
             f'node [fontname="{FONT}", fontsize=13, shape=box, style="rounded,filled", color="{INK}", width=2.6];',
             f'edge [fontname="{FONT}", fontsize=12, color="{INK}"];',
             'q1 [label="Does it involve people or animals?\n(surveys, interviews, tests, photos, their data)", fillcolor="#dbeafe"];',
             'q2 [label="Does it use data someone else owns?\n(a weather service, a website, a dataset)", fillcolor="#dbeafe"];',
             'q3 [label="Do you gain if one answer wins?\n(you work for an app, someone pays you)", fillcolor="#dbeafe"];',
             'a1 [label="Get ethics-committee approval\nand informed consent BEFORE\ncollecting anything", fillcolor="#fee2e2"];',
             'a2 [label="Check its licence or terms;\ncredit it in the paper", fillcolor="#fef3c7"];',
             'a3 [label="Declare it as a\nconflict of interest", fillcolor="#fef3c7"];',
             'ok [label="Write the answers in plan.md\nunder Ethics, and carry on", fillcolor="#d1fae5"];',
             'q1 -> a1 [label="  yes"]; q1 -> q2 [label="  no"]; a1 -> q2;',
             'q2 -> a2 [label="  yes"]; q2 -> q3 [label="  no"]; a2 -> q3;',
             'q3 -> a3 [label="  yes"]; q3 -> ok [label="  no"]; a3 -> ok;',
             '{rank=same; q1; a1} {rank=same; q2; a2} {rank=same; q3; a3}',
             '}']
    save_dot('\n'.join(lines), 'rs-ethics-check.svg',
             'A three-question ethics check for a study. First: does it involve people or animals, through surveys, '
             'interviews, tests, photos or their data? If yes, get ethics-committee approval and informed consent before '
             'collecting anything. Second: does it use data someone else owns, such as a weather service, a website or a '
             'dataset? If yes, check its licence or terms and credit it in the paper. Third: do you gain if one answer '
             'wins, for example because you work for one of the app companies or someone pays you? If yes, declare it as a '
             'conflict of interest. After all three, write the answers in plan.md under Ethics and carry on', OUT)


if __name__ == '__main__':
    knowledge_edge()
    lifecycle()
    three_pass()
    citation_map()
    good_question_venn()
    lit_review_shapes()
    scope_scale()
    question_funnel()
    rain_week()
    temp_week()
    variables()
    same_days_design()
    baselines_chart()
    validity_grid()
    paired_days()
    coin_flip_test()
    integrity_spectrum()
    data_trail()
    ethics_check()
    print('research diagrams: done')
