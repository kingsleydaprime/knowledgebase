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


if __name__ == '__main__':
    knowledge_edge()
    lifecycle()
    three_pass()
    citation_map()
    print('research diagrams: done')
