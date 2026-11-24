"""Draw the cybersecurity lesson diagrams as small SVG files.

    python3 scripts/diagrams/cybersecurity.py      # run from the vault root

Flows are drawn with Graphviz (`dot`, which must be installed). Grids and boxes are drawn
with svgkit. Output: cybersecurity/images/*.svg.

The ethical-hacking track teaches against targets the learner owns: an app they wrote and
deployed to their own VPS, a real open-source app they cloned onto that VPS, a PDF they locked
themselves, and a database of dummy accounts they seeded. These diagrams carry that model.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, FONT, Svg, save_dot  # noqa: E402

OUT = os.path.join('cybersecurity', 'images')
ORANGE = '#f59e0b'
GREEN = '#059669'
RED = '#dc2626'
GREY = '#9ca3af'


def authorization_decision():
    """The one question that decides whether a test is legal: do you have authority over the target?"""
    src = f'''digraph {{
      bgcolor="white"; pad=0.3; rankdir=TB; nodesep=0.4; ranksep=0.4;
      node [fontname="{FONT}", fontsize=13, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2];
      edge [fontname="{FONT}", fontsize=11, color="{INK}", fontcolor="#374151"];

      q1 [label="Do you own the target,\\nor hold written permission\\nfrom someone who does?", shape=diamond, fillcolor="#dbeafe", width=3.2];
      q2 [label="Is the exact target in scope,\\nright now, in writing?", shape=diamond, fillcolor="#dbeafe", width=3.2];
      ok [label="LEGAL to test", fillcolor="#d1fae5", color="{GREEN}"];
      stop1 [label="STOP. Testing it is a crime,\\nwhatever your intent.", fillcolor="#fee2e2", color="{RED}"];
      stop2 [label="STOP. Out of scope.\\nReport it, ask for an amendment,\\ndo not touch it.", fillcolor="#fee2e2", color="{RED}"];

      q1 -> stop1 [label="  no"];
      q1 -> q2 [label="  yes"];
      q2 -> stop2 [label="  no"];
      q2 -> ok [label="  yes"];
    }}'''
    save_dot(src, 'eh-authorization-decision.svg',
             'A decision chart: you may test a target only if you own it or hold written '
             'permission, and only while it is in scope; otherwise stop.', OUT)


def engagement_loop():
    """The loop every pentest lesson runs: find, prove, report, fix, detect."""
    stages = [
        ('1. Scope\\nAgree in writing what is in bounds', 'fixed'),
        ('2. Recon\\nLearn the target from the outside', 'prog'),
        ('3. Scan & enumerate\\nMap what is reachable and running', 'prog'),
        ('4. Exploit\\nProve one weakness really works', 'prog'),
        ('5. Chain & escalate\\nTurn a small win into a big one', 'prog'),
        ('6. Report\\nFinding, impact, risk rating', 'data'),
        ('7. Fix & detect\\nClose it, and write what would catch it', 'data'),
    ]
    src = ['digraph { bgcolor="white"; pad=0.3; rankdir=TB; nodesep=0.3; ranksep=0.35;',
           f'node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2, width=3.6];',
           f'edge [fontname="{FONT}", fontsize=11, color="{INK}"];']
    fills = {'prog': '#dbeafe', 'fixed': '#e5e7eb', 'data': '#d1fae5'}
    for i, (label, kind) in enumerate(stages):
        src.append(f'n{i} [label="{label}", fillcolor="{fills[kind]}"];')
    for i in range(len(stages) - 1):
        src.append(f'n{i} -> n{i + 1};')
    # the loop back: a new finding sends you back to recon on the next area
    src.append(f'n6 -> n1 [label="  next target /\\n  next area", constraint=false, color="{ORANGE}", fontcolor="{ORANGE}"];')
    src.append('}')
    save_dot('\n'.join(src), 'eh-engagement-loop.svg',
             'A loop of seven stages from scope through recon, scanning, exploitation, '
             'escalation and reporting to fixing and detection, then back to the next area.', OUT)


def lab_topology():
    """The tiered owned-target lab: attacker box + Juice Shop container on the laptop, real app on the VPS."""
    src = f'''digraph {{
      bgcolor="white"; pad=0.3; rankdir=LR; nodesep=0.35; ranksep=0.7; compound=true;
      node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2];
      edge [fontname="{FONT}", fontsize=11, color="{INK}", fontcolor="#374151"];

      subgraph cluster_laptop {{
        label="Your laptop (you own it)"; fontname="{FONT}"; fontsize=12; color="{INK}"; style="rounded"; penwidth=1.4;
        attacker [label="Attacker tools\\n(nmap, Burp, curl)", fillcolor="#fee2e2"];
        juice [label="Juice Shop\\n(Docker, localhost:3000)", fillcolor="#dbeafe"];
      }}

      subgraph cluster_vps {{
        label="Your VPS (you rent it)"; fontname="{FONT}"; fontsize=12; color="{INK}"; style="rounded"; penwidth=1.4;
        realapp [label="A real open-source app\\nyou deployed", fillcolor="#d1fae5"];
      }}

      attacker -> juice [label="  tier 1: today"];
      attacker -> realapp [label="  tier 2: when you\\n  rent the box", lhead=cluster_vps];
    }}'''
    save_dot(src, 'eh-lab-topology.svg',
             'A diagram of the lab: on your own laptop, attacker tools point at a Juice Shop '
             'container on localhost for tier 1, and at a real app on your own rented VPS for tier 2.',
             OUT)


def attack_chain():
    """How one small bug becomes total compromise — the escalation a report tells as a story."""
    stages = [
        ('A login box', '#e5e7eb', 'Low on its own'),
        ("SQL injection:\\n' OR 1=1--", '#fee2e2', 'Auth bypass'),
        ('Logged in as\\nthe first user', '#fde68a', '...who is admin'),
        ('Admin API lists\\nevery user', '#fecaca', 'All accounts'),
        ('Full account\\ntakeover', '#fca5a5', 'CRITICAL'),
    ]
    src = ['digraph { bgcolor="white"; pad=0.3; rankdir=LR; nodesep=0.3; ranksep=0.45;',
           f'node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2];',
           f'edge [fontname="{FONT}", fontsize=10, color="{INK}", fontcolor="{RED}"];']
    for i, (label, fill, _) in enumerate(stages):
        src.append(f'n{i} [label="{label}", fillcolor="{fill}"];')
    for i, (_, _, note) in enumerate(stages[1:]):
        src.append(f'n{i} -> n{i + 1} [label="  {note}"];')
    src.append('}')
    save_dot('\n'.join(src), 'eh-attack-chain.svg',
             'A left-to-right chain showing a login box escalate through SQL injection to '
             'authentication bypass, admin access, listing every user, and full account takeover.',
             OUT)


def risk_matrix():
    """Severity = likelihood x impact. The Juice Shop login SQLi plots top-right: critical."""
    s = Svg(440, 400, 'A risk matrix with likelihood on the vertical axis and impact on the '
            'horizontal axis; each cell is coloured from low (green) to critical (red), and the '
            'login SQL injection is plotted in the top-right critical cell.')
    x0, y0, cell = 90, 40, 90       # grid origin and cell size
    labels = ['Low', 'Medium', 'High']
    # colour by likelihood index (row) + impact index (col): 0..4 -> green..red
    palette = ['#16a34a', '#84cc16', '#f59e0b', '#f97316', '#dc2626']
    for row in range(3):            # row 0 = low likelihood (bottom)
        for col in range(3):
            score = row + col
            px = x0 + col * cell
            py = y0 + (2 - row) * cell
            s.rect(px, py, cell, cell, palette[score], stroke='#ffffff', width=2)
    # the plotted finding: high likelihood (row 2), high impact (col 2) -> top-right centre
    fx = x0 + 2 * cell + cell / 2
    fy = y0 + 0 * cell + cell / 2
    s.circle(fx, fy, 9, '#111827', stroke='#ffffff')
    s.text(fx, fy - 16, 'Login SQLi', size=12, color='#111827', weight='bold')
    s.text(fx, fy + 28, 'CRITICAL', size=11, color='#ffffff', weight='bold')
    # axis labels
    for col, lab in enumerate(labels):
        s.text(x0 + col * cell + cell / 2, y0 + 3 * cell + 20, lab, size=12)
    s.text(x0 + 1.5 * cell, y0 + 3 * cell + 42, 'Impact  →', size=13, weight='bold')
    for row, lab in enumerate(labels):
        s.text(x0 - 12, y0 + (2 - row) * cell + cell / 2 + 4, lab, size=12, anchor='end')
    # rotated y-axis title
    s.add(f'<text x="24" y="{y0 + 1.5 * cell}" font-size="13" fill="{INK}" '
          f'text-anchor="middle" font-weight="bold" font-family="system-ui, sans-serif" '
          f'transform="rotate(-90 24 {y0 + 1.5 * cell})">Likelihood  →</text>')
    s.save('eh-risk-matrix.svg', OUT)


def main():
    os.makedirs(OUT, exist_ok=True)
    authorization_decision()
    engagement_loop()
    lab_topology()
    attack_chain()
    risk_matrix()


if __name__ == '__main__':
    main()
