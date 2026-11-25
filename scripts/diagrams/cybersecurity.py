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
from svgkit import INK, FONT, Svg, flowchart, save_dot  # noqa: E402

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


def wpa2_handshake():
    """The WPA2 4-way handshake as a sequence diagram: capturing all four lets you guess the passphrase offline."""
    s = Svg(460, 330, 'A sequence diagram of the WPA2 four-way handshake between the router and '
            'the device: four messages that let both sides derive the session key, and which an '
            'eavesdropper can capture to test passphrase guesses offline.')
    ax, cx, top, bot = 120, 340, 60, 300
    # lifelines
    for x, label in [(ax, 'Router (AP)'), (cx, 'Device')]:
        s.text(x, top - 18, label, size=13, weight='bold')
        s.line(x, top, x, bot, color='#9ca3af', width=1.5, dash='4,3')
    msgs = [
        (ax, cx, 'M1: ANonce (router’s random number)'),
        (cx, ax, 'M2: SNonce + proof it has the key'),
        (ax, cx, 'M3: group key + proof'),
        (cx, ax, 'M4: acknowledgement'),
    ]
    y = top + 34
    for frm, to, text in msgs:
        s.line(frm, y, to, y, color=INK, width=1.6)
        # arrowhead
        head = '▶' if to > frm else '◀'
        s.text(to + (-8 if to > frm else 8), y + 4, head, size=11, color=INK)
        s.text((ax + cx) / 2, y - 7, text, size=11)
        y += 48
    # the eavesdropper note
    s.rect(70, y + 2, 320, 40, '#fee2e2', stroke=RED, width=1.2)
    s.text(230, y + 18, 'An eavesdropper who captures M1–M4 can test', size=11, color='#7f1d1d')
    s.text(230, y + 33, 'passphrase guesses offline — strong passphrase = safe.', size=11, color='#7f1d1d')
    s.save('eh-wpa2-handshake.svg', OUT)


# ---------------------------------------------------------------------------
# Network security (03-network-security): the defender's side of the same VPS
# the ethical-hacking section scanned. Running example: lesson 06's nmap found
# 22 (SSH), 80/443 (nginx) and 5432 (PostgreSQL) open on the VPS.
# ---------------------------------------------------------------------------

def stateful_firewall():
    """How a stateful, default-deny firewall decides one incoming packet."""
    src = f'''digraph {{
      bgcolor="white"; pad=0.3; rankdir=TB; nodesep=0.45; ranksep=0.4;
      node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2];
      edge [fontname="{FONT}", fontsize=11, color="{INK}", fontcolor="#374151"];

      pkt [label="A packet arrives at the VPS", fillcolor="#e5e7eb"];
      q1 [label="Is it part of a connection\\nalready allowed?\\n(the state table)", shape=diamond, fillcolor="#dbeafe", width=3.0];
      q2 [label="Does a rule allow it?\\n80/443 from anyone,\\n22 from your IP only", shape=diamond, fillcolor="#dbeafe", width=3.0];
      ok1 [label="ACCEPT", fillcolor="#d1fae5", color="{GREEN}"];
      ok2 [label="ACCEPT, and remember\\nthe new connection", fillcolor="#d1fae5", color="{GREEN}"];
      drop [label="DROP\\n(default deny: 5432 lands here)", fillcolor="#fee2e2", color="{RED}"];

      pkt -> q1;
      q1 -> ok1 [label="  yes"];
      q1 -> q2 [label="  no"];
      q2 -> ok2 [label="  yes"];
      q2 -> drop [label="  no"];
      ok2 -> q1 [label="  replies now\\n  match here", style=dashed, color="{ORANGE}", fontcolor="{ORANGE}", constraint=false];
    }}'''
    save_dot(src, 'ns-stateful-firewall.svg',
             'A decision chart for one incoming packet: if it belongs to a connection already allowed '
             'it is accepted; otherwise it is accepted only if a rule allows it (ports 80 and 443 from '
             'anyone, 22 from your IP), and everything else, including port 5432, is dropped.', OUT)


def segmented_vps():
    """The VPS split into zones: only nginx faces the internet; the database sits on an internal network."""
    src = f'''digraph {{
      bgcolor="white"; pad=0.3; rankdir=LR; nodesep=0.4; ranksep=0.6; compound=true;
      node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2];
      edge [fontname="{FONT}", fontsize=11, color="{INK}", fontcolor="#374151"];

      internet [label="The internet\\n(including attackers)", fillcolor="#fee2e2"];

      subgraph cluster_front {{
        label="frontend network (the DMZ)"; fontname="{FONT}"; fontsize=12; color="{INK}"; style="rounded"; penwidth=1.4;
        nginx [label="nginx\\nports 80, 443", fillcolor="#dbeafe"];
        app [label="The app", fillcolor="#dbeafe"];
      }}

      subgraph cluster_back {{
        label="backend network (internal: no route out or in)"; fontname="{FONT}"; fontsize=12; color="{GREEN}"; style="rounded"; penwidth=1.6;
        db [label="PostgreSQL\\nport 5432", fillcolor="#d1fae5"];
      }}

      internet -> nginx [label="  allowed"];
      nginx -> app;
      app -> db [label="  the only path in"];
      internet -> db [label="  no route", style=dashed, color="{RED}", fontcolor="{RED}", lhead=cluster_back];
    }}'''
    save_dot(src, 'ns-segmented-vps.svg',
             'A diagram of the segmented VPS: the internet can reach nginx on ports 80 and 443 in the '
             'frontend network, nginx passes requests to the app, and only the app can reach PostgreSQL '
             'on the internal backend network; the internet has no route to the database.', OUT)


def wireguard_tunnel():
    """SSH moved behind a WireGuard tunnel: the public port 22 is closed, only the tunnel reaches it."""
    src = f'''digraph {{
      bgcolor="white"; pad=0.3; rankdir=LR; nodesep=0.5; ranksep=0.8; compound=true;
      node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2];
      edge [fontname="{FONT}", fontsize=11, color="{INK}", fontcolor="#374151"];

      laptop [label="Your laptop\\nwg0 = 10.8.0.2", fillcolor="#dbeafe"];
      attacker [label="Anyone else\\non the internet", fillcolor="#fee2e2"];

      subgraph cluster_vps {{
        label="Your VPS"; fontname="{FONT}"; fontsize=12; color="{INK}"; style="rounded"; penwidth=1.4;
        wg [label="WireGuard\\nUDP 51820\\nwg0 = 10.8.0.1", fillcolor="#d1fae5"];
        ssh [label="SSH, port 22\\n(allowed on wg0 only)", fillcolor="#d1fae5"];
      }}

      laptop -> wg [label="  encrypted tunnel", color="{GREEN}", fontcolor="{GREEN}", penwidth=2];
      wg -> ssh [label="  10.8.0.2 → 10.8.0.1:22"];
      attacker -> ssh [label="  public :22 dropped", style=dashed, color="{RED}", fontcolor="{RED}"];
    }}'''
    save_dot(src, 'ns-wireguard-tunnel.svg',
             'A diagram of SSH behind WireGuard: your laptop (10.8.0.2) reaches the VPS through an '
             'encrypted tunnel on UDP port 51820 and then SSH on 10.8.0.1 port 22, while anyone else '
             'trying the public port 22 is dropped.', OUT)


def ids_vs_ips():
    """Where each sits: an IDS watches a copy of the traffic; an IPS sits in the path and can drop it."""
    src = f'''digraph {{
      bgcolor="white"; pad=0.3; rankdir=LR; nodesep=0.35; ranksep=0.6;
      node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2];
      edge [fontname="{FONT}", fontsize=11, color="{INK}", fontcolor="#374151"];

      subgraph cluster_ids {{
        label="IDS: beside the traffic, watching a copy"; fontname="{FONT}"; fontsize=12; color="{INK}"; style="rounded";
        t1 [label="Traffic", fillcolor="#e5e7eb"];
        s1 [label="Your server", fillcolor="#dbeafe"];
        ids [label="IDS", fillcolor="#fde68a"];
        a1 [label="Alert to a human\\n(the attack still arrives)", fillcolor="#fef3c7"];
        t1 -> s1;
        t1 -> ids [label="  copy", style=dashed];
        ids -> a1;
      }}

      subgraph cluster_ips {{
        label="IPS: in the path, can drop"; fontname="{FONT}"; fontsize=12; color="{INK}"; style="rounded";
        t2 [label="Traffic", fillcolor="#e5e7eb"];
        ips [label="IPS", fillcolor="#fde68a"];
        s2 [label="Your server", fillcolor="#dbeafe"];
        d2 [label="Dropped\\n(also a false positive's fate)", fillcolor="#fee2e2", color="{RED}"];
        t2 -> ips;
        ips -> s2 [label="  clean"];
        ips -> d2 [label="  matches a rule", color="{RED}", fontcolor="{RED}"];
      }}
    }}'''
    save_dot(src, 'ns-ids-vs-ips.svg',
             'Two diagrams side by side: an IDS sits beside the traffic, watching a copy and alerting a '
             'human while the attack still reaches the server; an IPS sits in the path and drops traffic '
             'that matches a rule, which is also what happens to a false positive.', OUT)


# ---------------------------------------------------------------------------
# Cryptography (05-cryptography)
# ---------------------------------------------------------------------------

def ecb_vs_gcm():
    """Three identical plaintext blocks: ECB gives three identical ciphertext blocks, GCM doesn't."""
    s = Svg(660, 250, 'Two rows of blocks: the same three identical plaintext blocks encrypted with ECB '
            'give three identical ciphertext blocks, so the repetition shows; encrypted with GCM they '
            'give three different-looking blocks plus an authentication tag.')
    plain = ['ATTACK AT DAWN!!'] * 3
    ecb = ['9f3a…', '9f3a…', '9f3a…']        # same colour = same bytes
    gcm = ['41c7…', 'e08b…', '7d52…']
    x0, w, gap = 130, 120, 12
    rows = [(30, 'Plaintext', plain, ['#e5e7eb'] * 3),
            (105, 'ECB', ecb, ['#fca5a5'] * 3),
            (180, 'GCM', gcm, ['#bfdbfe', '#bbf7d0', '#fde68a'])]
    for y, label, cells, fills in rows:
        s.text(60, y + 24, label, size=13, weight='bold')
        for i, (cell, fill) in enumerate(zip(cells, fills)):
            x = x0 + i * (w + gap)
            s.rect(x, y, w, 38, fill, stroke=INK, width=1.2)
            s.text(x + w / 2, y + 24, cell, size=11)
    s.rect(x0 + 3 * (w + gap), 180, 34, 38, '#d1fae5', stroke=GREEN, width=1.2)
    s.text(x0 + 3 * (w + gap) + 17, 204, 'tag', size=10)
    s.text(x0 + 3 * (w + gap) + 4, 128, '← the repeats show', size=12, color=RED, anchor='start')
    s.save('cr-ecb-vs-gcm.svg', OUT)


def diffie_hellman():
    """Toy Diffie–Hellman with p=23, g=5: both sides reach the same secret, 2, without sending it."""
    p, g, a, b = 23, 5, 6, 15
    A, B = pow(g, a, p), pow(g, b, p)
    assert (A, B) == (8, 19)
    assert pow(B, a, p) == pow(A, b, p) == 2
    src = f'''digraph {{
      bgcolor="white"; pad=0.3; rankdir=TB; nodesep=0.6; ranksep=0.45;
      node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2];
      edge [fontname="{FONT}", fontsize=11, color="{INK}", fontcolor="#374151"];

      pub [label="Public, agreed in the open:  p = {p},  g = {g}", fillcolor="#e5e7eb"];
      alice [label="Ada keeps a = {a} secret\\nsends A = {g}^{a} mod {p} = {A}", fillcolor="#dbeafe"];
      bayo [label="Bayo keeps b = {b} secret\\nsends B = {g}^{b} mod {p} = {B}", fillcolor="#dbeafe"];
      eve [label="An eavesdropper sees\\np, g, A = {A}, B = {B}\\n…but not a or b", fillcolor="#fee2e2", color="{RED}"];
      ka [label="Ada: B^a mod p\\n= {B}^{a} mod {p} = 2", fillcolor="#d1fae5", color="{GREEN}"];
      kb [label="Bayo: A^b mod p\\n= {A}^{b} mod {p} = 2", fillcolor="#d1fae5", color="{GREEN}"];

      pub -> alice; pub -> bayo;
      alice -> ka [label="  receives B = {B}\\n  from Bayo"];
      bayo -> kb [label="  receives A = {A}\\n  from Ada"];
      alice -> eve [style=dashed, color="{RED}"]; bayo -> eve [style=dashed, color="{RED}"];
      {{ rank=same; alice; bayo; }}
      {{ rank=same; ka; eve; kb; }}
    }}'''
    save_dot(src, 'cr-diffie-hellman.svg',
             'A toy Diffie–Hellman exchange with p = 23 and g = 5: Ada keeps 6 secret and sends 8, Bayo '
             'keeps 15 secret and sends 19, and both compute the same shared secret, 2, while an '
             'eavesdropper sees only 23, 5, 8 and 19.', OUT)


def hybrid_encryption():
    """Asymmetric crypto agrees a key; symmetric crypto carries the data."""
    flowchart([
        ('Key exchange (asymmetric)\\nX25519 / ECDH: both sides\\ncompute one shared secret', 'prog'),
        ('Key derivation\\nturn the shared secret into\\na 256-bit AES key (HKDF)', 'fixed'),
        ('Bulk data (symmetric)\\nAES-GCM or ChaCha20 encrypts\\nevery byte that follows', 'data'),
    ], 'cr-hybrid-encryption.svg',
        'A three-step flow: an asymmetric key exchange gives both sides one shared secret, a key '
        'derivation step turns it into a symmetric key, and a fast symmetric cipher encrypts all the data.',
        OUT, rankdir='LR')


def chain_of_trust():
    """Root CA in the trust store signs an intermediate, which signs the site's certificate."""
    src = f'''digraph {{
      bgcolor="white"; pad=0.3; rankdir=TB; nodesep=0.4; ranksep=0.45;
      node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2];
      edge [fontname="{FONT}", fontsize=11, color="{INK}", fontcolor="#374151"];

      store [label="Your browser / OS trust store\\n(ships with ~150 root certificates)", fillcolor="#e5e7eb"];
      root [label="Root CA certificate\\n(self-signed, kept offline)", fillcolor="#d1fae5", color="{GREEN}"];
      inter [label="Intermediate CA certificate\\nsigned by the root", fillcolor="#dbeafe"];
      leaf [label="lab.example.com certificate\\npublic key + name, signed by the intermediate", fillcolor="#fde68a"];

      store -> root [label="  trusts"];
      root -> inter [label="  signs"];
      inter -> leaf [label="  signs"];
      leaf -> store [label="  browser checks each\\n  signature back up to here", style=dashed, color="{ORANGE}", fontcolor="{ORANGE}", constraint=false];
    }}'''
    save_dot(src, 'cr-chain-of-trust.svg',
             'A chain of trust: the browser trust store trusts a root CA, the root signs an intermediate CA, '
             'and the intermediate signs the certificate for lab.example.com; the browser checks each '
             'signature back up to the trust store.', OUT)


# ---------------------------------------------------------------------------
# Fundamentals (01-fundamentals): running example is Mama Put, the food-ordering API
# ---------------------------------------------------------------------------

def mama_put_dfd():
    """Mama Put's order flow as a data-flow diagram with its trust boundaries."""
    src = f'''digraph {{
      bgcolor="white"; pad=0.3; rankdir=LR; nodesep=0.4; ranksep=0.55; compound=true;
      node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2];
      edge [fontname="{FONT}", fontsize=10, color="{INK}", fontcolor="#374151"];

      customer [label="Customer\\n(phone browser)", shape=box, style="filled", fillcolor="#e5e7eb"];
      paystack [label="Payment provider", shape=box, style="filled", fillcolor="#e5e7eb"];

      subgraph cluster_server {{
        label="Trust boundary: your server"; fontname="{FONT}"; fontsize=12; color="{RED}"; style="dashed,rounded"; penwidth=1.6;
        api [label="Mama Put API", shape=ellipse, fillcolor="#dbeafe"];
        subgraph cluster_db {{
          label="Trust boundary: database"; fontname="{FONT}"; fontsize=11; color="{RED}"; style="dashed,rounded";
          db [label="orders, users\\n(data store)", shape=cylinder, fillcolor="#d1fae5"];
        }}
      }}

      customer -> api [label="  1. place order\\n  (login, items, address)"];
      api -> db [label="  2. save order"];
      api -> paystack [label="  3. charge card"];
      paystack -> api [label="  4. webhook: paid"];
      api -> customer [label="  5. confirmation"];
    }}'''
    save_dot(src, 'fu-mama-put-dfd.svg',
             'A data-flow diagram of Mama Put: the customer places an order with the API, the API saves it '
             'to the database and charges the card through a payment provider, the provider sends a paid '
             'webhook back, and the API confirms to the customer; dashed red boxes mark the trust '
             'boundaries around the server and the database.', OUT)


# ---------------------------------------------------------------------------
# Attacks and threats (06-attacks-and-threats)
# ---------------------------------------------------------------------------

def arp_spoofing():
    """Before and after ARP spoofing on the lab's Docker network: the victim's traffic detours via the attacker."""
    src = f'''digraph {{
      bgcolor="white"; pad=0.3; rankdir=LR; nodesep=0.35; ranksep=0.7;
      node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2];
      edge [fontname="{FONT}", fontsize=10, color="{INK}", fontcolor="#374151"];

      subgraph cluster_after {{
        label="After: forged ARP replies"; fontname="{FONT}"; fontsize=12; color="{RED}"; style="rounded";
        v2 [label="victim\\n10.9.0.3", fillcolor="#dbeafe"];
        a2 [label="attacker\\n10.9.0.4\\nMAC …:04", fillcolor="#fee2e2", color="{RED}"];
        g2 [label="gateway\\n10.9.0.2\\nMAC …:02", fillcolor="#d1fae5"];
        v2 -> a2 [label="  10.9.0.2 is at …:04 (a lie)", color="{RED}", fontcolor="{RED}"];
        a2 -> g2 [label="  forwards, reading\\n  everything", style=dashed];
      }}

      subgraph cluster_before {{
        label="Before: the victim's ARP table is honest"; fontname="{FONT}"; fontsize=12; color="{INK}"; style="rounded";
        v1 [label="victim\\n10.9.0.3", fillcolor="#dbeafe"];
        g1 [label="gateway\\n10.9.0.2\\nMAC …:02", fillcolor="#d1fae5"];
        v1 -> g1 [label="  10.9.0.2 is at …:02"];
      }}
    }}'''
    save_dot(src, 'at-arp-spoofing.svg',
             'Two panels: before ARP spoofing, the victim (10.9.0.3) sends traffic for the gateway '
             '(10.9.0.2) straight to the gateway\'s MAC address ending 02; after forged ARP replies, '
             'the victim believes 10.9.0.2 is at the attacker\'s MAC ending 04, so its traffic detours '
             'through the attacker (10.9.0.4), who reads it and forwards it on.', OUT)


# ---------------------------------------------------------------------------
# Security operations (07-security-operations)
# ---------------------------------------------------------------------------

def defense_in_depth():
    """Layers an attacker must pass through one by one; the defender only needs one to hold."""
    stages = [
        ('Attacker', 'prog'),
        ('Perimeter\\nfirewall, deny by default', 'fixed'),
        ('Network\\nsegmentation, zero trust', 'fixed'),
        ('Host\\nhardening, patching, EDR', 'fixed'),
        ('Application\\nvalidation, auth, HTTPS', 'fixed'),
        ('Data\\nencryption, least privilege', 'fixed'),
        ('The crown jewels', 'data'),
    ]
    notes = ['must pass', 'and this', 'and this', 'and this', 'and this', 'to reach']
    flowchart(stages, 'so-defense-in-depth.svg',
              'A single file of layers the attacker must pass one after another: perimeter firewall, '
              'then network segmentation, then host hardening, then application controls, then data '
              'encryption, before reaching the crown jewels; the attacker must defeat every layer, the '
              'defender needs only one to hold, and monitoring watches across all of them.',
              OUT, rankdir='LR')


def detection_pipeline():
    """How a raw log line becomes an alert an analyst acts on."""
    src = f'''digraph {{
      bgcolor="white"; pad=0.3; rankdir=LR; nodesep=0.35; ranksep=0.6;
      node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2];
      edge [fontname="{FONT}", fontsize=10, color="{INK}", fontcolor="#374151"];

      subgraph cluster_src {{
        label="Log sources"; fontname="{FONT}"; fontsize=12; color="{GREY}"; style="rounded";
        host [label="host / OS\\nauth.log", fillcolor="#e5e7eb"];
        net [label="network\\nfirewall, DNS", fillcolor="#e5e7eb"];
        app [label="application\\naccess logs", fillcolor="#e5e7eb"];
        cloud [label="cloud\\naudit logs", fillcolor="#e5e7eb"];
      }}
      siem [label="SIEM\\naggregate + normalise\\n+ correlate", fillcolor="#dbeafe", width=2.2];
      rule [label="detection rule\\n(Sigma)", fillcolor="#fef3c7", color="{ORANGE}"];
      alert [label="alert", fillcolor="#fee2e2", color="{RED}"];
      analyst [label="analyst / SOAR\\ninvestigate + respond", fillcolor="#d1fae5", color="{GREEN}", width=2.2];

      host -> siem; net -> siem; app -> siem; cloud -> siem;
      siem -> rule -> alert -> analyst;
    }}'''
    save_dot(src, 'so-detection-pipeline.svg',
             'A pipeline: host, network, application and cloud logs all flow into a SIEM that '
             'aggregates, normalises and correlates them; a Sigma detection rule turns a correlated '
             'pattern into an alert, which an analyst or SOAR system then investigates and responds to.',
             OUT)


def kill_chain():
    """The seven stages of an intrusion; every stage is a chance to break the chain."""
    stages = [
        ('1. Reconnaissance\\nstudy the target', 'prog'),
        ('2. Weaponisation\\nbuild the payload', 'prog'),
        ('3. Delivery\\nemail, link, USB', 'prog'),
        ('4. Exploitation\\nrun the code', 'prog'),
        ('5. Installation\\ngain persistence', 'prog'),
        ('6. Command & control\\nphone home', 'prog'),
        ('7. Actions on objectives\\nsteal, encrypt, destroy', 'data'),
    ]
    notes = ['detect here', 'or here', 'or here', 'or here', 'or here', 'or here']
    flowchart(stages, 'so-kill-chain.svg',
              'The seven sequential stages of the Lockheed Martin cyber kill chain, from '
              'reconnaissance through weaponisation, delivery, exploitation, installation and command '
              'and control to actions on objectives; a defender who detects and disrupts the intrusion '
              'at any one stage breaks the chain and the attack fails.',
              OUT, notes=notes)


def ir_lifecycle():
    """The six IR phases as a loop; lessons learned feed back into preparation."""
    src = f'''digraph {{
      bgcolor="white"; pad=0.3; rankdir=LR; nodesep=0.3; ranksep=0.45;
      node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2, width=1.7];
      edge [fontname="{FONT}", fontsize=10, color="{INK}", fontcolor="#374151"];

      p [label="1. Preparation", fillcolor="#e5e7eb"];
      i [label="2. Identification", fillcolor="#dbeafe"];
      c [label="3. Containment", fillcolor="#fef3c7", color="{ORANGE}"];
      e [label="4. Eradication", fillcolor="#fee2e2", color="{RED}"];
      r [label="5. Recovery", fillcolor="#dbeafe"];
      l [label="6. Lessons learned", fillcolor="#d1fae5", color="{GREEN}"];

      p -> i -> c -> e -> r -> l;
      l -> p [label="  feed back", style=dashed, constraint=false];
    }}'''
    save_dot(src, 'so-ir-lifecycle.svg',
             'The six incident-response phases in order: preparation, identification, containment, '
             'eradication, recovery and lessons learned, with a dashed arrow carrying lessons learned '
             'back into preparation so the next incident is handled better.', OUT)


def order_of_volatility():
    """Collect evidence most-volatile first, because the top of the list vanishes on power-off."""
    stages = [
        ('CPU registers & cache\\ngone in nanoseconds', 'prog'),
        ('RAM\\nprocesses, keys, fileless malware\\ngone on power-off', 'prog'),
        ('Network state\\nconnections, ARP table', 'prog'),
        ('Disk\\nfiles, timestamps, logs', 'fixed'),
        ('Backups & archives\\nmost durable', 'data'),
    ]
    notes = ['collect first', 'then', 'then', 'then last']
    flowchart(stages, 'so-order-of-volatility.svg',
              'The order of volatility as a top-down list from most to least fleeting: CPU registers '
              'and cache first, then RAM holding processes, keys and fileless malware, then network '
              'state, then disk, then backups; you capture the most volatile evidence first because it '
              'vanishes on power-off while disk and backups survive.', OUT)


# ---------------------------------------------------------------------------
# Governance, risk and compliance (08-governance-risk-and-compliance)
# ---------------------------------------------------------------------------

def risk_treatment():
    """A 2x2 of likelihood x impact, with the right treatment in each quadrant."""
    s = Svg(460, 380, 'A risk matrix: likelihood across, impact up, with a treatment in each quadrant.')
    x0, y0, cw, ch = 140, 50, 150, 130
    # quadrants: (col, row) -> (fill, label, sublabel)  row 0 = top = high impact
    cells = {
        (0, 0): ('#fef3c7', 'TRANSFER', 'rare but severe:\ninsure / outsource'),
        (1, 0): ('#fee2e2', 'AVOID / MITIGATE', 'likely and severe:\nfix this first'),
        (0, 1): ('#d1fae5', 'ACCEPT', 'rare and minor:\nlive with it'),
        (1, 1): ('#fde9c8', 'MITIGATE / ACCEPT', 'likely but minor:\nreduce if cheap'),
    }
    for (col, row), (fill, label, sub) in cells.items():
        x, y = x0 + col * cw, y0 + row * ch
        s.rect(x, y, cw, ch, fill, stroke=INK, width=1.2)
        s.text(x + cw / 2, y + ch / 2 - 14, label, size=13, weight='bold')
        for i, ln in enumerate(sub.split('\n')):
            s.text(x + cw / 2, y + ch / 2 + 8 + i * 15, ln, size=11, color='#374151')
    # axes
    s.text(x0 + cw, y0 + 2 * ch + 28, 'Likelihood →', size=13, weight='bold')
    s.text(x0 - 28, y0 + 10, 'high', size=11, color='#6b7280')
    s.text(x0 - 28, y0 + ch, 'low', size=11, color='#6b7280')
    s.text(x0 + cw / 2, y0 + 2 * ch + 20, 'low', size=11, color='#6b7280')
    s.text(x0 + cw + cw / 2, y0 + 2 * ch + 20, 'high', size=11, color='#6b7280')
    # vertical "Impact" label, letter-stacked
    for i, ch_ in enumerate('IMPACT'):
        s.text(x0 - 60, y0 + 30 + i * 18, ch_, size=13, weight='bold')
    s.text(x0 - 60, y0 - 16, '↑', size=14, weight='bold')
    s.save('gr-risk-treatment.svg', OUT)


def nist_csf():
    """The five NIST CSF functions, each mapped to the course section that does it."""
    stages = [
        ('Identify\\nassets, risks (section 01, 08)', 'fixed'),
        ('Protect\\nharden, segment, encrypt (03, 04)', 'data'),
        ('Detect\\nlogging, SIEM, hunting (07)', 'prog'),
        ('Respond\\nincident response (07)', 'prog'),
        ('Recover\\nbackups, lessons learned (07)', 'data'),
    ]
    flowchart(stages, 'gr-nist-csf.svg',
              'The five functions of the NIST Cybersecurity Framework in order — Identify, Protect, '
              'Detect, Respond, Recover — each labelled with the course section that puts it into '
              'practice, showing the framework is a map of the whole course.',
              OUT, rankdir='LR')


def policy_hierarchy():
    """Policy down to guideline: the WHY narrows to the exact HOW."""
    src = f'''digraph {{
      bgcolor="white"; pad=0.3; rankdir=TB; nodesep=0.3; ranksep=0.35;
      node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2, width=5.0];
      edge [fontname="{FONT}", fontsize=10, color="{INK}", fontcolor="#374151"];

      p [label="POLICY — \\"we protect customer data\\"\\nthe what and why; leadership-approved, stable", fillcolor="#dbeafe"];
      s [label="STANDARD — \\"data at rest must be AES-256\\"\\nspecific, measurable, mandatory", fillcolor="#e0e7ff"];
      pr [label="PROCEDURE — \\"to encrypt a new database: do X, Y, Z\\"\\nthe step-by-step how, repeatable by anyone", fillcolor="#d1fae5"];
      g [label="GUIDELINE — \\"prefer managed keys where possible\\"\\nrecommended, not enforced", fillcolor="#f3f4f6"];

      p -> s [label="  gets specific"];
      s -> pr [label="  gets actionable"];
      pr -> g [label="  plus advice"];
    }}'''
    save_dot(src, 'gr-policy-hierarchy.svg',
             'A top-down hierarchy from policy to guideline: a high-level policy ("we protect customer '
             'data") narrows to a measurable standard ("data at rest must be AES-256"), then to a '
             'step-by-step procedure, then to an optional guideline, showing how the why becomes the '
             'exact how.', OUT)


def supply_chain_risk():
    """The attacker reaches a hardened target through a weaker supplier or dependency."""
    src = f'''digraph {{
      bgcolor="white"; pad=0.3; rankdir=LR; nodesep=0.4; ranksep=0.7;
      node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2];
      edge [fontname="{FONT}", fontsize=10, color="{INK}", fontcolor="#374151"];

      attacker [label="attacker", fillcolor="#fee2e2", color="{RED}"];
      lib [label="weak open-source\\nlibrary / update", fillcolor="#fef3c7", color="{ORANGE}"];
      vendor [label="trusted vendor\\n(SaaS, contractor)", fillcolor="#fef3c7", color="{ORANGE}"];
      you [label="YOUR hardened app\\nfirewall, MFA, patched", fillcolor="#d1fae5", color="{GREEN}", width=2.2];

      attacker -> lib [label="  1. poison it", color="{RED}", fontcolor="{RED}"];
      attacker -> vendor [label="  1. breach it", color="{RED}", fontcolor="{RED}"];
      lib -> you [label="  2. you pull it", style=dashed];
      vendor -> you [label="  2. they have access", style=dashed];
    }}'''
    save_dot(src, 'gr-supply-chain.svg',
             'An attacker cannot breach your hardened app directly, so instead poisons a weak '
             'open-source library you depend on and breaches a trusted vendor with access to you; both '
             'paths then reach your app through the trust you placed in them, bypassing your own '
             'defences.', OUT)


# ---------------------------------------------------------------------------
# Cloud security (09-cloud-security)
# ---------------------------------------------------------------------------

def shared_responsibility():
    """Who secures what across IaaS, PaaS and SaaS: the line moves up, but data+access are always yours."""
    s = Svg(520, 360, 'Shared responsibility across IaaS, PaaS and SaaS: the provider/you line moves up the stack.')
    cols = ['IaaS\n(raw VM)', 'PaaS\n(platform)', 'SaaS\n(software)']
    rows = ['Data & access', 'Application', 'Runtime / platform', 'OS / patching', 'Hypervisor', 'Physical & network']
    # 'you' or 'prov' for each row (top->bottom) per column
    own = {
        'Data & access':       ['you', 'you', 'you'],
        'Application':         ['you', 'you', 'prov'],
        'Runtime / platform':  ['you', 'prov', 'prov'],
        'OS / patching':       ['you', 'prov', 'prov'],
        'Hypervisor':          ['prov', 'prov', 'prov'],
        'Physical & network':  ['prov', 'prov', 'prov'],
    }
    x0, y0, cw, rh = 150, 56, 110, 42
    for c, name in enumerate(cols):
        for i, ln in enumerate(name.split('\n')):
            s.text(x0 + c * cw + cw / 2, y0 - 20 + i * 14, ln, size=11, weight='bold')
    for r, row in enumerate(rows):
        s.text(x0 - 10, y0 + r * rh + rh / 2 + 4, row, size=11, anchor='end')
        for c in range(3):
            who = own[row][c]
            fill = '#d1fae5' if who == 'prov' else '#dbeafe'
            s.rect(x0 + c * cw, y0 + r * rh, cw - 4, rh - 4, fill, stroke=INK, width=1)
            s.text(x0 + c * cw + cw / 2, y0 + r * rh + rh / 2 + 4,
                   'provider' if who == 'prov' else 'you', size=10,
                   color='#065f46' if who == 'prov' else '#1e40af')
    # legend
    s.rect(x0, y0 + 6 * rh + 10, 16, 14, '#dbeafe', stroke=INK, width=1)
    s.text(x0 + 22, y0 + 6 * rh + 21, 'you secure', size=11, anchor='start')
    s.rect(x0 + 130, y0 + 6 * rh + 10, 16, 14, '#d1fae5', stroke=INK, width=1)
    s.text(x0 + 152, y0 + 6 * rh + 21, 'provider secures', size=11, anchor='start')
    s.save('cl-shared-responsibility.svg', OUT)


def iam_evaluation():
    """Every cloud API call is an IAM decision: principal + action + resource + conditions -> allow/deny."""
    stages = [
        ('Principal\\nwho is asking\\n(user, app, role)', 'prog'),
        ('Action\\nwhat they want\\n(s3:GetObject)', 'prog'),
        ('Resource\\non what\\n(this bucket)', 'prog'),
        ('Conditions\\nMFA? IP? time?', 'fixed'),
        ('Allow / Deny', 'data'),
    ]
    flowchart(stages, 'cl-iam-evaluation.svg',
              'An IAM decision evaluated on every API call: a principal (who), an action (what), a '
              'resource (on what) and conditions combine to an allow-or-deny, so identity, not the '
              'network, is the control.',
              OUT, rankdir='LR')


def metadata_ssrf():
    """The Capital One chain: an SSRF reaches the metadata endpoint and steals the VM's role credentials."""
    src = f'''digraph {{
      bgcolor="white"; pad=0.3; rankdir=LR; nodesep=0.35; ranksep=0.6;
      node [fontname="{FONT}", fontsize=11, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2];
      edge [fontname="{FONT}", fontsize=10, color="{INK}", fontcolor="#374151"];

      attacker [label="attacker", fillcolor="#fee2e2", color="{RED}"];
      app [label="vulnerable app\\n(SSRF)\\non a cloud VM", fillcolor="#fef3c7", color="{ORANGE}"];
      imds [label="metadata service\\n169.254.169.254", fillcolor="#e5e7eb"];
      creds [label="VM role\\ncredentials", fillcolor="#fee2e2", color="{RED}"];
      bucket [label="storage bucket\\nthe role can read", fillcolor="#dbeafe"];

      attacker -> app [label="  1. send crafted URL"];
      app -> imds [label="  2. app fetches\\n  the metadata IP", color="{RED}", fontcolor="{RED}"];
      imds -> creds [label="  3. returns creds"];
      creds -> bucket [label="  4. read data\\n  from anywhere", style=dashed, color="{RED}", fontcolor="{RED}"];
    }}'''
    save_dot(src, 'cl-metadata-ssrf.svg',
             'The Capital One attack chain: an attacker sends a crafted URL to an app with a '
             'server-side request forgery flaw, the app fetches the cloud metadata endpoint at '
             '169.254.169.254, which returns the VM role credentials, and the attacker then uses those '
             'credentials to read the storage bucket the role could access, from anywhere.', OUT)


def cloud_kill_chain():
    """How cloud misconfigurations compose into a breach, step by step."""
    stages = [
        ('1. Initial access\\nleaked key, SSRF, phished login', 'prog'),
        ('2. Credential theft\\nmetadata service, secrets, IAM', 'prog'),
        ('3. Escalation\\nover-broad IAM -> assume admin', 'prog'),
        ('4. Discovery\\nenumerate buckets, accounts', 'prog'),
        ('5. Actions\\nexfiltrate, mine, ransom, persist', 'data'),
    ]
    flowchart(stages, 'cl-cloud-kill-chain.svg',
              'The cloud attacker kill chain in five steps — initial access, credential theft, '
              'privilege escalation, discovery, and actions on objectives — where every step is '
              'enabled by a customer-side misconfiguration, so fixing the early steps collapses the '
              'chain.', OUT)


def container_layers():
    """Four stacked layers of container attack surface, each with insecure defaults."""
    stages = [
        ('CLUSTER — Kubernetes RBAC, secrets,\\nnetwork policies, the API server', 'fixed'),
        ('RUNTIME — how it runs: user, capabilities,\\nprivilege, read-only filesystem', 'prog'),
        ('IMAGE — what\'s inside: dependencies,\\nbase image, baked-in secrets', 'data'),
        ('HOST — the node\'s OS (Linux hardening)', 'fixed'),
    ]
    flowchart(stages, 'cl-container-layers.svg',
              'The four stacked layers of container security from top to bottom — cluster, runtime, '
              'image and host — where a weakness at any layer undermines the ones above and every '
              'layer ships with insecure defaults.', OUT)


def cloud_defence_loop():
    """The three automated fronts of cloud defence, feeding findings back into policy."""
    src = f'''digraph {{
      bgcolor="white"; pad=0.3; rankdir=LR; nodesep=0.35; ranksep=0.55;
      node [fontname="{FONT}", fontsize=11, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2, width=2.0];
      edge [fontname="{FONT}", fontsize=10, color="{INK}", fontcolor="#374151"];

      sl [label="shift left\\nscan IaC + secrets,\\npolicy-as-code in the PR", fillcolor="#d1fae5", color="{GREEN}"];
      sc [label="scan continuously\\nCSPM / CIEM / CNAPP\\ncatch drift in minutes", fillcolor="#dbeafe"];
      dr [label="detect & respond\\nCloudTrail -> SIEM,\\nthreat detection", fillcolor="#fef3c7", color="{ORANGE}"];

      sl -> sc -> dr;
      dr -> sl [label="  feed findings back into policy", style=dashed, constraint=false];
    }}'''
    save_dot(src, 'cl-cloud-defence-loop.svg',
             'The cloud-defence loop on three automated fronts: shift left catches misconfigurations '
             'in the pull request, continuous scanning catches drift in production within minutes, and '
             'detect-and-respond catches what got through, with findings fed back into policy.', OUT)


# ---------------------------------------------------------------------------
# Protecting yourself (10-protecting-yourself)
# ---------------------------------------------------------------------------

def credential_stuffing():
    """How a password you reused becomes an open account years later, with no one hacking you."""
    stages = [
        ('A shop you forgot about is breached\\nyour email + password end up in a public dump', 'prog'),
        ('Software replays that one pair against\\nGmail, your bank, Instagram, your work login', 'prog'),
        ('Every site where you reused it\\nis opened — nobody had to hack you', 'data'),
    ]
    flowchart(stages, 'ps-credential-stuffing.svg',
              'Credential stuffing in three steps: a shop you used is breached and your email and '
              'password land in a public dump, software automatically replays that one pair against '
              'Gmail, your bank and your work login, and every site where you reused it is opened '
              'without anyone having to hack you.', OUT)


def sim_swap():
    """Why moving your phone number to an attacker's SIM unlocks everything that texts you a code."""
    stages = [
        ('Attacker convinces your network\\nto move your number to their SIM', 'prog'),
        ('Your number now rings on their phone', 'prog'),
        ('Forgot-password on your email\\n→ code texted → to them', 'prog'),
        ('They own your email, and everything\\nyour email can reset', 'data'),
    ]
    flowchart(stages, 'ps-sim-swap.svg',
              'A SIM swap in four steps: the attacker convinces your mobile network to move your '
              'number to their SIM, so your number now rings on their phone, a forgot-password on your '
              'email texts the reset code to them, and they then own your email and everything it can '
              'reset.', OUT)


def sync_not_backup():
    """Why a sync service is not a backup: it copies your mistake everywhere at once."""
    stages = [
        ('You delete, corrupt, or ransomware\\nencrypts a file on one device', 'prog'),
        ('Sync makes everywhere match', 'fixed'),
        ('The bad version lands on every\\ndevice — the good copy is gone', 'data'),
    ]
    flowchart(stages, 'ps-sync-not-backup.svg',
              'Why sync is not a backup, in three steps: you delete or corrupt a file, or ransomware '
              'encrypts it, on one device; the sync service makes every device match; so the bad '
              'version is copied to every device and the good copy is gone everywhere at once.', OUT)


def privacy_to_breach():
    """How public facts about you become the answers that reset your account."""
    stages = [
        ('Attacker reads your social media\\ndog\'s name, school, birthday', 'prog'),
        ('Those facts answer your bank\'s\\nsecurity questions', 'prog'),
        ('Account reset — or a phone call\\nthat sounds completely real', 'data'),
    ]
    flowchart(stages, 'ps-privacy-to-breach.svg',
              'How a privacy footprint becomes a breach, in three steps: an attacker reads public '
              'facts from your social media such as your dog\'s name, school and birthday; those facts '
              'answer your bank\'s security questions; and the account is reset, or a phone call using '
              'the details sounds completely real.', OUT)


# ---------------------------------------------------------------------------
# Binary exploitation (11-binary-exploitation)
# ---------------------------------------------------------------------------

def memory_map():
    """The process address space: stack grows down, heap grows up, code read-only at the bottom."""
    s = Svg(460, 380, 'A process address space from high to low addresses: stack, heap, bss/data, and text.')
    x, w = 150, 200
    rows = [
        ('stack', 'local variables, return addresses', '#dbeafe', 'grows down'),
        ('heap', 'malloc / new', '#d1fae5', 'grows up'),
        ('bss / data', 'global variables', '#e5e7eb', ''),
        ('text', 'machine code: read-only + executable', '#fef3c7', ''),
    ]
    y, h = 54, 62
    for i, (name, sub, fill, grow) in enumerate(rows):
        yy = y + i * (h + 8)
        s.rect(x, yy, w, h, fill, stroke=INK, width=1.2)
        s.text(x + w / 2, yy + 26, name, size=14, weight='bold')
        s.text(x + w / 2, yy + 45, sub, size=10, color='#374151')
        if grow:
            s.text(x + w + 48, yy + h / 2 + 4, grow, size=10, color='#6b7280')
            arrow = '↓' if grow == 'grows down' else '↑'
            s.text(x + w + 20, yy + h / 2 + 5, arrow, size=18, color=ORANGE, weight='bold')
    s.text(x - 16, y + 6, 'HIGH', size=11, color='#6b7280', anchor='end')
    s.text(x - 16, y + 4 * (h + 8) - 8, 'LOW', size=11, color='#6b7280', anchor='end')
    s.text(x + w / 2, y + 4 * (h + 8) + 16, 'addresses', size=10, color='#6b7280')
    s.save('be-memory-map.svg', OUT)


def stack_overflow():
    """A stack frame: input written into buffer overflows upward into the saved return address."""
    s = Svg(500, 320, 'A stack frame where writing past the buffer overflows upward into the saved return address.')
    x, w = 150, 210
    rows = [
        ('saved return address', 'where the function jumps next — THE TARGET', '#fee2e2', RED),
        ('saved RBP', 'frame reference', '#e5e7eb', INK),
        ('char buffer[64]', 'your input is written here', '#dbeafe', INK),
    ]
    y, h = 60, 64
    for i, (name, sub, fill, stroke) in enumerate(rows):
        yy = y + i * (h + 6)
        s.rect(x, yy, w, h, fill, stroke=stroke, width=1.4 if stroke == RED else 1.1)
        s.text(x + w / 2, yy + 26, name, size=13, weight='bold')
        s.text(x + w / 2, yy + 45, sub, size=9.5, color='#374151')
    s.text(x - 16, y + 6, 'higher', size=10, color='#6b7280', anchor='end')
    s.text(x - 16, y + 3 * (h + 6) - 10, 'lower', size=10, color='#6b7280', anchor='end')
    # overflow arrow: from buffer up through RBP into return address
    ax = x + w + 34
    s.line(ax, y + 2 * (h + 6) + h / 2, ax, y + 18, color=ORANGE, width=3)
    s.path(f'M {ax - 6} {y + 26} L {ax} {y + 14} L {ax + 6} {y + 26}', color=ORANGE, width=3)
    s.text(ax + 12, y + h, 'strcpy writes', size=10, color=ORANGE, anchor='start', weight='bold')
    s.text(ax + 12, y + h + 15, 'past the buffer,', size=10, color='#374151', anchor='start')
    s.text(ax + 12, y + h + 30, 'up into the', size=10, color='#374151', anchor='start')
    s.text(ax + 12, y + h + 45, 'return address', size=10, color='#374151', anchor='start')
    s.save('be-stack-overflow.svg', OUT)


def stack_canary():
    """The canary sits between the buffer and the return address; an overflow must cross it."""
    s = Svg(520, 230, 'A stack canary placed between the buffer and the return address, which a linear overflow must cross and corrupt.')
    cells = [
        ('buffer', '#dbeafe', INK),
        ('CANARY', '#fef3c7', ORANGE),
        ('saved RBP', '#e5e7eb', INK),
        ('return address', '#fee2e2', RED),
    ]
    x0, y, w, h = 30, 70, 118, 54
    for i, (name, fill, stroke) in enumerate(cells):
        xx = x0 + i * (w + 4)
        s.rect(xx, y, w, h, fill, stroke=stroke, width=1.4 if stroke != INK else 1.1)
        s.text(xx + w / 2, y + h / 2 + 5, name, size=12, weight='bold')
    s.text(x0, y - 16, 'lower addresses', size=10, color='#6b7280', anchor='start')
    s.text(x0 + 4 * (w + 4), y - 16, 'higher', size=10, color='#6b7280', anchor='end')
    s.line(x0 + 20, y + h + 20, x0 + 3 * (w + 4) + 40, y + h + 20, color=ORANGE, width=2.5)
    s.path(f'M {x0 + 3 * (w + 4) + 32} {y + h + 14} L {x0 + 3 * (w + 4) + 42} {y + h + 20} L {x0 + 3 * (w + 4) + 32} {y + h + 26}', color=ORANGE, width=2.5)
    s.text(x0 + 10, y + h + 42, 'a linear overflow reaching the return address must first smash the CANARY — and the check catches it', size=10, color='#374151', anchor='start')
    s.save('be-stack-canary.svg', OUT)


def escalation_ladder():
    """Each rung adds a defence; the technique you need steps up with it."""
    stages = [
        ('No defences\\ninject shellcode, jump to it', 'data'),
        ('NX\\nret2libc / ROP (reuse code)', 'prog'),
        ('NX + ASLR\\nleak an address first, then ROP', 'prog'),
        ('NX + ASLR + PIE\\nleak the binary base too', 'prog'),
        ('+ Full RELRO\\nno GOT overwrite: pure-ROP execve', 'prog'),
        ('+ canary\\nleak the canary, or avoid the return address', 'prog'),
        ('+ CET / shadow stack\\nROP detected: JOP or data-only attacks', 'fixed'),
    ]
    flowchart(stages, 'be-escalation-ladder.svg',
              'The exploitation escalation ladder: with no defences you inject shellcode; NX forces '
              'code reuse (ret2libc/ROP); ASLR forces leaking an address first; PIE forces leaking the '
              'binary base; Full RELRO forces a pure-ROP execve; a canary must be leaked or avoided; '
              'and CET or a shadow stack detects ROP, pushing to JOP or data-only attacks — the '
              'checksec output tells you which rung you are on.', OUT)


# ---------------------------------------------------------------------------
# Active Directory (12-active-directory)
# ---------------------------------------------------------------------------

def ad_structure():
    """The AD hierarchy: forest is the real boundary, the DC is the prize."""
    src = f'''digraph {{
      bgcolor="white"; pad=0.3; rankdir=TB; nodesep=0.35; ranksep=0.4;
      node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2];
      edge [color="{INK}", penwidth=1.1, arrowsize=0.7];

      forest [label="FOREST\\nthe true security boundary", fillcolor="#e5e7eb", width=3.0];
      domain [label="DOMAIN  (corp.local)\\na unit of administration", fillcolor="#dbeafe", width=3.0];
      dc  [label="Domain Controllers (DCs)\\nrun AD — THE prize", fillcolor="#fee2e2", color="{RED}", width=2.4];
      ou  [label="Organizational Units\\nfolders for objects", fillcolor="#f3f4f6", width=2.0];
      usr [label="Users\\npeople + services", fillcolor="#f3f4f6", width=1.8];
      cmp [label="Computers\\nevery joined machine", fillcolor="#f3f4f6", width=1.9];
      grp [label="Groups\\nmembership = rights", fillcolor="#f3f4f6", width=1.9];

      forest -> domain;
      domain -> dc; domain -> ou; domain -> usr; domain -> cmp; domain -> grp;
    }}'''
    save_dot(src, 'ad-structure.svg',
             'An Active Directory hierarchy drawn top to bottom: a FOREST, the true security boundary, '
             'contains a DOMAIN corp.local, which contains the Domain Controllers that run AD and are '
             'the prize, plus Organizational Units, Users, Computers and Groups.', OUT)


def ad_kerberos_flow():
    """The three-step ticket exchange; which account's hash seals each ticket is the whole attack surface."""
    src = f'''digraph {{
      bgcolor="white"; pad=0.3; rankdir=TB; nodesep=0.4; ranksep=0.5;
      node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2, width=2.2];
      edge [fontname="{FONT}", fontsize=10.5, color="{INK}", fontcolor="#374151"];

      client [label="Client\\n(Alice)", fillcolor="#dbeafe"];
      kdc [label="KDC\\n(on the Domain Controller)", fillcolor="#e5e7eb", width=2.6];
      svc [label="SQL service", fillcolor="#d1fae5"];

      client -> kdc [label="  1. AS-REQ: \\"I'm Alice\\""];
      kdc -> client [label="  AS-REP: TGT,\\n  sealed with KRBTGT's hash", color="{RED}", fontcolor="{RED}"];
      client -> kdc [label="  2. TGS-REQ: TGT + \\"I want SQL\\""];
      kdc -> client [label="  TGS-REP: service ticket,\\n  sealed with the service\\n  account's hash", color="{ORANGE}", fontcolor="{ORANGE}"];
      client -> svc [label="  3. AP-REQ: service ticket"];
      svc -> client [label="  decrypts with its own key,\\n  trusts you", style=dashed];
    }}'''
    save_dot(src, 'ad-kerberos-flow.svg',
             'The Kerberos ticket exchange in three request/response pairs: the client asks the KDC and '
             'gets a TGT sealed with the KRBTGT account hash, presents that TGT and gets a service ticket '
             'sealed with the service account hash, then presents the service ticket to the SQL server, '
             'which decrypts it with its own key and trusts the client.', OUT)


def ad_bloodhound_path():
    """A BloodHound shortest path: three legitimate permissions chained to Domain Admin."""
    stages = [
        ('Your user\\n(low privilege)', 'prog'),
        ('Help Desk\\n(group)', 'prog'),
        ('Server Admins\\n(group)', 'prog'),
        ('DC01\\n(Domain Controller)', 'data'),
    ]
    notes = ['MemberOf', 'GenericAll', 'AdminTo']
    flowchart(stages, 'ad-bloodhound-path.svg',
              'A BloodHound attack path as four nodes joined by three labelled edges: your low-privilege '
              'user is MemberOf the Help Desk group, which has GenericAll over the Server Admins group, '
              'which is AdminTo the DC01 Domain Controller — three legitimate permissions chained from a '
              'foothold to Domain Admin.', OUT, rankdir='LR', notes=notes)


def ad_kill_chain():
    """One foothold to the whole domain in seven stages."""
    stages = [
        ('1. Foothold\\none credential', 'prog'),
        ('2. Enumerate\\nBloodHound -> path to DA', 'prog'),
        ('3. Harvest\\nKerberoast, mimikatz', 'prog'),
        ('4. Move\\npass-the-hash', 'prog'),
        ('5. Escalate\\nACL / delegation / ADCS / DCSync', 'prog'),
        ('6. Domain Admin\\nDCSync KRBTGT -> Golden Ticket', 'fixed'),
        ('7. Persist\\nand DOCUMENT every step', 'data'),
    ]
    flowchart(stages, 'ad-kill-chain.svg',
              'The Active Directory kill chain in seven stages: foothold from one credential, enumerate '
              'with BloodHound to find the path to Domain Admin, harvest credentials by Kerberoasting and '
              'mimikatz, move laterally with pass-the-hash, escalate through ACL, delegation, ADCS or '
              'DCSync, reach Domain Admin by DCSyncing KRBTGT and forging a Golden Ticket, then persist '
              'and document every step.', OUT)


def ad_tiering():
    """The tiered administration model: higher-tier credentials never touch lower-tier machines."""
    s = Svg(560, 320, 'Microsoft tiered administration model')
    rows = [
        ('Tier 0', 'Domain Controllers, AD, KRBTGT', 'the crown jewels', '#fee2e2', RED),
        ('Tier 1', 'Servers and applications', '', '#fef3c7', ORANGE),
        ('Tier 2', 'Workstations', '', '#dbeafe', INK),
    ]
    x, w, h, gap = 60, 440, 64, 20
    for i, (tier, body, note, fill, stroke) in enumerate(rows):
        y = 40 + i * (h + gap)
        s.rect(x, y, w, h, fill, stroke=stroke, width=1.6)
        s.text(x + 18, y + 27, tier, size=15, color=stroke, anchor='start', weight='bold')
        s.text(x + 18, y + 48, body, size=12.5, anchor='start')
        if note:
            s.text(x + w - 14, y + 27, note, size=11.5, color=stroke, anchor='end')
    # the rule, as a locked arrow between tiers
    s.text(280, 300, 'A Tier 0 credential is used ONLY on Tier 0 — so owning a '
                     'workstation yields no Domain Admin to steal.', size=11.5, color=INK)
    s.save('ad-tiering.svg', OUT)


def main():
    os.makedirs(OUT, exist_ok=True)
    ad_structure()
    ad_kerberos_flow()
    ad_bloodhound_path()
    ad_kill_chain()
    ad_tiering()
    memory_map()
    stack_overflow()
    stack_canary()
    escalation_ladder()
    credential_stuffing()
    sim_swap()
    sync_not_backup()
    privacy_to_breach()
    shared_responsibility()
    iam_evaluation()
    metadata_ssrf()
    cloud_kill_chain()
    container_layers()
    cloud_defence_loop()
    risk_treatment()
    nist_csf()
    policy_hierarchy()
    supply_chain_risk()
    defense_in_depth()
    detection_pipeline()
    kill_chain()
    ir_lifecycle()
    order_of_volatility()
    arp_spoofing()
    ecb_vs_gcm()
    diffie_hellman()
    hybrid_encryption()
    chain_of_trust()
    mama_put_dfd()
    stateful_firewall()
    segmented_vps()
    wireguard_tunnel()
    ids_vs_ips()
    authorization_decision()
    engagement_loop()
    lab_topology()
    attack_chain()
    risk_matrix()
    wpa2_handshake()


if __name__ == '__main__':
    main()
