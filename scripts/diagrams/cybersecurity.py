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


def main():
    os.makedirs(OUT, exist_ok=True)
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
