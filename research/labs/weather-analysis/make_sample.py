"""Write sample-data.csv: four made-up weeks that give lesson 05's example numbers exactly.
    python3 make_sample.py      (run from this folder)"""
import csv
import random

rng = random.Random(7)
while True:  # 29 dates: the first is only "yesterday" for the first scored day
    rain = [rng.random() < 0.55 for _ in range(29)]
    days = range(1, 29)
    if sum(rain[d] for d in days) == 16 and sum(rain[d] == rain[d - 1] for d in days) == 17:
        break
guess_right = [d for d in days if rain[d] == rain[d - 1]]
guess_wrong = [d for d in days if rain[d] != rain[d - 1]]
# app B: right on 15 of the guess's right days and 7 of its wrong days (22 in all)
b_right = set(rng.sample(guess_right, 15) + rng.sample(guess_wrong, 7))
a_right = set(rng.sample(list(days), 18))
c_right = set(rng.sample(list(days), 15))

with open('sample-data.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['date', 'app', 'rain_chance', 'forecast_high', 'rain_mm', 'actual_high', 'read_at', 'notes'])
    for d in range(29):
        mm = round(rng.uniform(1.5, 40), 1) if rain[d] else round(rng.uniform(0, 0.8), 1)
        high = rng.choice([28, 29, 30, 31, 32])
        for app, ok, miss in (('A', a_right, 2), ('B', b_right, 1), ('C', c_right, 3)):
            says_rain = rain[d] == (d in ok) if d else rain[d]
            chance = rng.choice([60, 70, 80, 90]) if says_rain else rng.choice([10, 20, 30, 40])
            off = rng.choice([-miss, 0, miss])
            w.writerow([f'2026-06-{d + 1:02d}', app, chance, high + off, mm, high, '20:00', ''])
