"""Draw the Artificial Intelligence subject diagrams (artificial-intelligence/) as small SVG files.

    python3 scripts/diagrams/artificial_intelligence.py      # run from the vault root

The running example of the whole subject is a road trip from Lagos to Abuja on a
small map of Nigerian cities. The distances are rounded road distances in km,
chosen to be realistic but kept simple for hand tracing; they are illustrative,
not survey figures. Every path cost the lessons quote is computed and asserted
here before anything is drawn. Output: artificial-intelligence/images/ai-*.svg.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, ACCENT, FONT, Svg, flowchart, save_dot  # noqa: E402

OUT = os.path.join('artificial-intelligence', 'images')
ORANGE = '#f59e0b'
NODE_FILL = '#dbeafe'
START_FILL = '#d1fae5'
GOAL_FILL = '#fde68a'

# ---------- the running example: the Nigeria road map ----------

ROADS = {
    ('Lagos', 'Ibadan'): 130,
    ('Lagos', 'Benin'): 330,
    ('Ibadan', 'Ilorin'): 160,
    ('Ibadan', 'Akure'): 210,
    ('Benin', 'Akure'): 165,
    ('Benin', 'Lokoja'): 300,
    ('Ilorin', 'Abuja'): 520,
    ('Akure', 'Lokoja'): 250,
    ('Lokoja', 'Abuja'): 200,
}
# Rough map positions (inches) so the picture looks like the country: west on the left, north at the top.
POS = {
    'Lagos': (0.3, 0.6), 'Ibadan': (1.1, 1.6), 'Ilorin': (2.0, 2.9), 'Benin': (2.9, 0.2),
    'Akure': (2.5, 1.4), 'Lokoja': (4.1, 2.0), 'Abuja': (4.7, 3.4),
}


def neighbours(city):
    out = []
    for (a, b), d in ROADS.items():
        if a == city:
            out.append((b, d))
        elif b == city:
            out.append((a, d))
    return out


def all_paths(start, goal, path=None):
    path = path or [start]
    if path[-1] == goal:
        yield path
        return
    for nxt, _ in neighbours(path[-1]):
        if nxt not in path:
            yield from all_paths(start, goal, path + [nxt])


def cost(path):
    total = 0
    for a, b in zip(path, path[1:]):
        total += ROADS.get((a, b)) or ROADS[(b, a)]
    return total


def check_route_numbers():
    """The numbers lesson 05 (problem solving) and the index quote."""
    assert len(POS) == 7 and len(ROADS) == 9
    paths = {tuple(p): cost(p) for p in all_paths('Lagos', 'Abuja')}
    assert paths[('Lagos', 'Ibadan', 'Ilorin', 'Abuja')] == 810
    assert paths[('Lagos', 'Benin', 'Lokoja', 'Abuja')] == 830
    assert paths[('Lagos', 'Ibadan', 'Akure', 'Lokoja', 'Abuja')] == 790
    best = min(paths, key=paths.get)
    assert best == ('Lagos', 'Ibadan', 'Akure', 'Lokoja', 'Abuja') and paths[best] == 790
    fewest = min(len(p) for p in paths) - 1
    assert fewest == 3  # two 3-road routes exist, and neither is the cheapest
    assert sorted(n for n, _ in neighbours('Lagos')) == ['Benin', 'Ibadan']
    assert sorted(n for n, _ in neighbours('Ibadan')) == ['Akure', 'Ilorin', 'Lagos']
    return paths


def save_neato(src, name, title):
    r = subprocess.run(['neato', '-n', '-Tsvg'], input=src, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr)
    svg = r.stdout
    svg = re.sub(r'<\?xml.*?\?>\s*', '', svg)
    svg = re.sub(r'<!DOCTYPE.*?>\s*', '', svg, flags=re.S)
    svg = re.sub(r'<!--.*?-->\s*', '', svg, flags=re.S)
    svg = svg.replace(' xmlns:xlink="http://www.w3.org/1999/xlink"', '')
    svg = re.sub(r'<title>[^<]*</title>\s*', '', svg)
    svg = re.sub(r'(\d+\.\d)\d+', r'\1', svg)
    svg = svg.replace('<svg ', '<svg role="img" ', 1)
    svg = re.sub(r'(<svg[^>]*>)', lambda m: m.group(1) + '\n<title>' + title + '</title>', svg, count=1)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), 'w') as f:
        f.write(svg)
    print(f'{name}: {len(svg)} bytes')


def route_map(name, title, highlight=None):
    highlight = highlight or []
    hl_edges = {frozenset(e) for e in zip(highlight, highlight[1:])}
    lines = ['graph { bgcolor="white"; pad=0.3; splines=line;',
             f'node [fontname="{FONT}", fontsize=13, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2, margin="0.12,0.06"];',
             f'edge [fontname="{FONT}", fontsize=12, color="{INK}", fontcolor="#374151", penwidth=1.4];']
    for city, (x, y) in POS.items():
        fill = START_FILL if city == 'Lagos' else GOAL_FILL if city == 'Abuja' else NODE_FILL
        lines.append(f'"{city}" [pos="{x * 72:.0f},{y * 72:.0f}!", fillcolor="{fill}"];')
    for (a, b), d in ROADS.items():
        on = frozenset((a, b)) in hl_edges
        style = f', color="{ORANGE}", penwidth=3.5' if on else ''
        lines.append(f'"{a}" -- "{b}" [label=" {d}"{style}];')
    lines.append('}')
    save_neato('\n'.join(lines), name, title)


# ---------- lesson pictures ----------

def four_approaches():
    s = Svg(620, 330, 'The four approaches to AI: think like humans, think rationally, act like humans, act rationally')
    x0, y0, cw, ch = 150, 60, 220, 110
    s.text(x0 + cw / 2, 40, 'Like a human', size=14, weight='bold')
    s.text(x0 + cw * 1.5, 40, 'Rationally (the right way)', size=14, weight='bold')
    s.text(75, y0 + ch / 2 + 5, 'Thinking', size=14, weight='bold')
    s.text(75, y0 + ch * 1.5 + 5, 'Acting', size=14, weight='bold')
    cells = [
        (0, 0, 'Think like humans', 'cognitive modelling', '#e5e7eb'),
        (1, 0, 'Think rationally', '"laws of thought" (logic)', '#e5e7eb'),
        (0, 1, 'Act like humans', 'the Turing test', '#dbeafe'),
        (1, 1, 'Act rationally', 'the rational agent', '#d1fae5'),
    ]
    for c, r, head, sub, fill in cells:
        x, y = x0 + c * cw, y0 + r * ch
        s.rect(x + 4, y + 4, cw - 8, ch - 8, fill, stroke=INK, width=1.2)
        s.text(x + cw / 2, y + ch / 2 - 4, head, size=15, weight='bold')
        s.text(x + cw / 2, y + ch / 2 + 18, sub, size=13)
    s.rect(x0 + cw + 2, y0 + ch + 2, cw - 4, ch - 4, 'none', stroke=ORANGE, width=3)
    s.text(x0 + cw * 1.5, y0 + 2 * ch + 30, 'the approach this subject takes', size=12, color='#b45309')
    s.save('ai-four-approaches.svg', OUT)


def agent_loop():
    src = f'''digraph {{ bgcolor="white"; pad=0.3; rankdir=LR; nodesep=0.5; ranksep=0.9;
node [fontname="{FONT}", fontsize=13, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2];
edge [fontname="{FONT}", fontsize=12, color="{INK}", fontcolor="#374151", penwidth=1.3];
subgraph cluster_agent {{ label="Agent"; fontname="{FONT}"; fontsize=14; style="rounded"; color="{INK}";
  sensors [label="Sensors", fillcolor="#dbeafe"];
  brain [label="Agent program\\n(decides what to do)", fillcolor="#fde68a"];
  actuators [label="Actuators", fillcolor="#dbeafe"];
  sensors -> brain; brain -> actuators; }}
env [label="Environment\\n(the world the agent lives in)", fillcolor="#d1fae5", width=2.2, height=1.6];
env -> sensors [label="percepts"];
actuators -> env [label="actions"];
}}'''
    save_dot(src, 'ai-agent-loop.svg',
             'An agent takes percepts from its environment through sensors, its agent program decides, and actuators send actions back into the environment', OUT)


def problem_solving_steps():
    flowchart([
        ('1. Identify the problem', 'data'),
        ('2. Formulate the problem\\n(states, actions, goal, cost)', 'prog'),
        ('3. Formulate a strategy\\n(search for a plan)', 'prog'),
        ('4. Execute and monitor', 'fixed'),
        ('5. Learn and adapt', 'data'),
    ], 'ai-problem-solving-steps.svg',
        'The five steps of problem solving in AI: identify the problem, formulate it, formulate a strategy, execute and monitor, then learn and adapt',
        OUT)


def history_timeline():
    s = Svg(760, 230, 'A timeline of AI: the Turing test 1950, Dartmouth 1956, early game playing and theorem proving in the 1950s and 60s, '
                      'the Lighthill report 1973, expert systems in the 1970s and 80s, neural nets return 1986, and data-driven AI from the 1990s')
    events = [
        (1950, 'Turing test', 'paper'),
        (1956, 'Dartmouth', 'conference'),
        (1960, 'game playing,', 'theorem proving'),
        (1973, 'Lighthill', 'report (winter)'),
        (1980, 'expert systems', 'boom'),
        (1986, 'neural nets', 'return'),
        (1997, 'Deep Blue', 'beats Kasparov'),
        (2012, 'deep learning', 'takes over'),
    ]
    x_of = lambda yr: 50 + (yr - 1945) / (2020 - 1945) * 660  # noqa: E731
    s.line(40, 120, 720, 120, width=2.5)
    for i, (yr, a, b) in enumerate(events):
        x = x_of(yr)
        up = i % 2 == 0
        s.circle(x, 120, 6, ORANGE if 'Lighthill' in a else ACCENT)
        s.line(x, 120, x, 82 if up else 158, color='#9ca3af', width=1)
        s.text(x, 112 - 54 if up else 182, str(yr), size=12, weight='bold')
        s.text(x, 112 - 38 if up else 198, a, size=12)
        s.text(x, 112 - 24 if up else 212, b, size=12)
    s.save('ai-history-timeline.svg', OUT)


def ai_ml_nesting():
    s = Svg(560, 330, 'Three nested boxes: Artificial intelligence contains machine learning, which contains deep learning; '
                      'search and game playing sit inside AI but outside machine learning')
    boxes = [
        (20, 20, 520, 290, '#e5e7eb', 'Artificial intelligence', 'machines doing things that need intelligence'),
        (180, 90, 340, 200, '#dbeafe', 'Machine learning', 'learning rules from data'),
        (300, 170, 200, 100, '#d1fae5', 'Deep learning', 'many-layered neural nets'),
    ]
    for x, y, w, h, fill, head, sub in boxes:
        s.rect(x, y, w, h, fill, stroke=INK, width=1.2)
        s.text(x + 14, y + 26, head, size=15, weight='bold', anchor='start')
        s.text(x + 14, y + 46, sub, size=12, anchor='start')
    for i, item in enumerate(['search', 'game playing', 'planning', 'logic and rules']):
        s.text(36, 120 + i * 26, '• ' + item, size=13, anchor='start', color='#b45309')
    s.save('ai-ml-nesting.svg', OUT)


if __name__ == '__main__':
    check_route_numbers()
    ai_ml_nesting()
    four_approaches()
    agent_loop()
    problem_solving_steps()
    history_timeline()
    route_map('ai-route-map.svg',
              'The running example map: Lagos, Ibadan, Benin, Ilorin, Akure, Lokoja and Abuja joined by nine roads with distances in km; '
              'Lagos is the start and Abuja the goal')
    route_map('ai-route-map-cheapest.svg',
              'The cheapest route from Lagos to Abuja, Lagos to Ibadan to Akure to Lokoja to Abuja, 790 km, highlighted in orange',
              highlight=['Lagos', 'Ibadan', 'Akure', 'Lokoja', 'Abuja'])
