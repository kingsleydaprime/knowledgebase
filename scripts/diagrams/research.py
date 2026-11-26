"""Draw the research-and-paper-writing diagrams (research/).

    python3 scripts/diagrams/research.py      # run from the vault root

Output: research/images/rs-*.svg. These pictures carry ideas rather than numbers, so the
checks here are structural: every stage the lessons name appears in the picture, in order.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, FONT, Svg, save_dot  # noqa: E402

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
    print('research diagrams: done')
