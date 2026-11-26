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


if __name__ == '__main__':
    knowledge_edge()
    lifecycle()
    three_pass()
    citation_map()
    good_question_venn()
    lit_review_shapes()
    scope_scale()
    print('research diagrams: done')
