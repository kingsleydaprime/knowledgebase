"""Score the weather study.   python3 analyse.py data.csv"""
import csv
import sys
from math import comb

RAIN_CHANCE = 50   # the app "said rain" at this % or more (from plan.md)
RAIN_MM = 1.0      # "it rained" at this many mm or more (from plan.md)

rows = [r for r in csv.DictReader(open(sys.argv[1])) if all(r[c].strip() for c in
        ('date', 'app', 'rain_chance', 'forecast_high', 'rain_mm', 'actual_high'))]
apps = sorted({r['app'] for r in rows})
rained = {r['date']: float(r['rain_mm']) >= RAIN_MM for r in rows}
said = {(r['app'], r['date']): float(r['rain_chance']) >= RAIN_CHANCE for r in rows}
error = {(r['app'], r['date']): abs(float(r['forecast_high']) - float(r['actual_high'])) for r in rows}

# Score every app on the same days: days where every app has a reading and yesterday's rain is known.
dates = sorted(rained)
days = [d for prev, d in zip(dates, dates[1:]) if all((a, d) in said for a in apps)]
yesterday = dict(zip(dates[1:], dates))

right = {a: {d: said[a, d] == rained[d] for d in days} for a in apps}
right['always "rain"'] = {d: rained[d] for d in days}
right['"like today"'] = {d: rained[yesterday[d]] == rained[d] for d in days}

print(f'{len(days)} days scored\n')
print(f'{"":16}{"right":>8}{"hit rate":>10}{"avg error":>11}')
for name, r in right.items():
    hits = sum(r.values())
    err = f'{sum(error[name, d] for d in days) / len(days):.1f}°C' if name in apps else ''
    print(f'{name:16}{hits:>5}/{len(days):<3}{100 * hits / len(days):>8.0f}%{err:>11}')

print('\nEach app against "like today", on the days they disagree:')
for a in apps:
    wins = sum(right[a][d] and not right['"like today"'][d] for d in days)
    losses = sum(right['"like today"'][d] and not right[a][d] for d in days)
    n = wins + losses
    p = sum(comb(n, k) for k in range(wins, n + 1)) / 2 ** n if n else 1.0
    print(f'{a:16}won {wins}, lost {losses}   chance of {wins}+ wins out of {n} by luck: p = {p:.3f}')
