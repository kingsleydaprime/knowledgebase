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


if __name__ == '__main__':
    knowledge_edge()
    lifecycle()
    print('research diagrams: done')
