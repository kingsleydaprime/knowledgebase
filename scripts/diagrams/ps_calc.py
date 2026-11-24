"""The sums behind the planning and scheduling lessons: CPM passes, PERT, crashing, priority rules
and Brooks' algorithm. Imported by planning_scheduling.py, which asserts the lessons' numbers."""
import math


def close(a, b, tol=1e-6):
    return abs(a - b) <= tol


# ---------- CPM on an activity-on-node network ----------

def cpm(acts):
    """acts: {name: (duration, [predecessors])}, in any order. Returns {name: dict(ES, EF, LS, LF, TF, FF)}, T."""
    order, done = [], set()
    while len(order) < len(acts):
        for a, (_, pre) in acts.items():
            if a not in done and all(p in done for p in pre):
                order.append(a)
                done.add(a)
    r = {}
    for a in order:
        d, pre = acts[a]
        es = max((r[p]['EF'] for p in pre), default=0)
        r[a] = dict(ES=es, EF=es + d, d=d)
    T = max(v['EF'] for v in r.values())
    succ = {a: [b for b, (_, pre) in acts.items() if a in pre] for a in acts}
    for a in reversed(order):
        lf = min((r[s]['LS'] for s in succ[a]), default=T)
        r[a]['LF'] = lf
        r[a]['LS'] = lf - r[a]['d']
        r[a]['TF'] = r[a]['LS'] - r[a]['ES']
    for a in order:
        r[a]['FF'] = min((r[s]['ES'] for s in succ[a]), default=T) - r[a]['EF']
    return r, T


def paths(acts):
    """Every start-to-finish path with its length."""
    succ = {a: [b for b, (_, pre) in acts.items() if a in pre] for a in acts}
    starts = [a for a, (_, pre) in acts.items() if not pre]
    out = []

    def walk(a, path, length):
        path, length = path + [a], length + acts[a][0]
        if not succ[a]:
            out.append(('-'.join(path), length))
        for s in succ[a]:
            walk(s, path, length)
    for a in starts:
        walk(a, [], 0)
    return out


def critical(r):
    return [a for a, v in r.items() if close(v['TF'], 0)]


# ---------- CPM on an activity-on-arrow network ----------

def aoa(arrows):
    """arrows: {(i, j): duration}. Returns event earliest/latest times and per-arrow ES..TF, and T."""
    events = sorted({e for ij in arrows for e in ij})
    early = {e: 0 for e in events}
    for e in events:
        ins = [early[i] + d for (i, j), d in arrows.items() if j == e]
        early[e] = max(ins, default=0)
    T = early[events[-1]]
    late = {e: T for e in events}
    for e in reversed(events):
        outs = [late[j] - d for (i, j), d in arrows.items() if i == e]
        late[e] = min(outs, default=T)
    acts = {}
    for (i, j), d in arrows.items():
        acts[(i, j)] = dict(ES=early[i], EF=early[i] + d, LF=late[j], LS=late[j] - d, TF=late[j] - d - early[i])
    return early, late, acts, T


# ---------- PERT ----------

def te(a, m, b):
    return (a + 4 * m + b) / 6


def var(a, b):
    return ((b - a) / 6) ** 2


def phi(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


# ---------- crashing ----------

def slope(tn, tc, cn, cc):
    return (cc - cn) / (tn - tc)


def crash_table(acts, crash, indirect):
    """Greedy one-day-at-a-time crashing by the cheapest set of critical activities.
    acts: {name: (Tn, [pre])}; crash: {name: (Tc, Cn, Cc)}. Returns [(duration, direct, total, crashed)]."""
    dur = {a: v[0] for a, v in acts.items()}
    direct = sum(c[1] for c in crash.values())
    rows = []

    def length():
        return cpm({a: (dur[a], acts[a][1]) for a in acts})[1]
    T = length()
    rows.append((T, direct, direct + indirect * T, ''))
    while True:
        best = None
        cands = [a for a in acts if dur[a] > crash[a][0]]
        import itertools
        for k in range(1, 4):
            for combo in itertools.combinations(cands, k):
                for a in combo:
                    dur[a] -= 1
                newT = length()
                for a in combo:
                    dur[a] += 1
                if newT < T:
                    cost = sum(slope(acts[a][0], crash[a][0], crash[a][1], crash[a][2]) for a in combo)
                    if best is None or cost < best[0]:
                        best = (cost, combo)
            if best:
                break
        if not best:
            return rows
        for a in best[1]:
            dur[a] -= 1
        direct += best[0]
        T = length()
        rows.append((T, direct, direct + indirect * T, '+'.join(best[1])))


# ---------- priority rules ----------

def caf_table(tasks, avail, w):
    """tasks: {name: (a, m, b, [res...])}. Returns {name: dict(t, s, RAF, sRAF, sSAF, CAF, sCAF)}."""
    out = {}
    for n, (a, m, b, res) in tasks.items():
        t, s = te(a, m, b), (b - a) / 6
        out[n] = dict(t=t, s=s, RAF=(1 / t) * sum(x / y for x, y in zip(res, avail)), st=s / t)
    rmax = max(v['RAF'] for v in out.values())
    tmax = max(v['t'] for v in out.values())
    stmax = max(v['st'] for v in out.values())
    for v in out.values():
        v['sRAF'] = v['RAF'] / rmax * 100
        v['sSAF'] = v['t'] / tmax * 50 + v['st'] / stmax * 50
        v['CAF'] = w * v['sRAF'] + (1 - w) * v['sSAF']
    cmax = max(v['CAF'] for v in out.values())
    for v in out.values():
        v['sCAF'] = v['CAF'] / cmax * 100
    return out


def brooks(tasks, avail, prio):
    """Serial scheduling. tasks: {name: (duration, [pre], [res...])}; prio: {name: score}, higher first.
    Returns {name: (start, finish)}."""
    sched, running, now = {}, [], 0.0
    free = list(avail)
    while len(sched) < len(tasks):
        done = {n for n, (s, f) in sched.items() if f <= now + 1e-9}
        ready = [n for n in tasks if n not in sched and all(p in done for p in tasks[n][1])]
        for n in sorted(ready, key=lambda n: -prio[n]):
            need = tasks[n][2]
            if all(f >= q for f, q in zip(free, need)):
                sched[n] = (now, now + tasks[n][0])
                running.append(n)
                free = [f - q for f, q in zip(free, need)]
        nxt = min(sched[n][1] for n in running)
        now = nxt
        for n in [n for n in running if close(sched[n][1], now)]:
            running.remove(n)
            free = [f + q for f, q in zip(free, tasks[n][2])]
    return sched
