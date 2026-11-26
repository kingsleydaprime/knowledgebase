"""Run analyse.py on the sample data and check it prints the numbers lessons 05 and 06 quote."""
import subprocess
import sys

out = subprocess.run([sys.executable, 'analyse.py', 'sample-data.csv'], capture_output=True, text=True, check=True).stdout
print(out)
for line in ['28 days scored', '22/28', '79%', '17/28', '61%', '16/28', '57%', '18/28', '64%', '15/28', '54%',
             '0.7°C', '1.2°C', '2.0°C', 'won 7, lost 2', 'p = 0.090']:
    assert line in out, f'missing from output: {line}'
print('weather-analysis: the sample matches the lessons')
