"""Flock / ALPR cameras per resident by California county.
Usage: python scripts/analyze_flock.py   (writes data/processed/flock_by_county.csv)"""
import sys, re, pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]   # repo root, so the script runs from anywhere
c = pd.read_csv(ROOT/'data'/'raw'/'county_counts.csv'); p = pd.read_csv(ROOT/'data'/'raw'/'ca_county_population_2026.csv')
c['county'] = c['county'].astype(str).str.replace(r'^City and County of ', '', regex=True).str.replace(r' County$', '', regex=True).str.strip()
m = p.merge(c, on='county', how='left', indicator=True)
print('unmatched counties:', m.loc[m._merge != 'both', 'county'].tolist())
m[['alpr','flock']] = m[['alpr','flock']].fillna(0)
m['alpr_per_100k'] = m.alpr / m.population_2026 * 1e5
m['flock_share'] = m.flock / m.alpr.where(m.alpr > 0)
print('CA totals:', int(m.alpr.sum()), 'ALPR,', int(m.flock.sum()), 'Flock,', round(m.alpr.sum()/m.population_2026.sum()*1e5,1), 'per 100k')
print(m.sort_values('alpr_per_100k', ascending=False)[['county','population_2026','alpr','flock','alpr_per_100k','flock_share']].round(2).to_string(index=False))
m.drop(columns='_merge').to_csv(ROOT/'data'/'processed'/'flock_by_county.csv', index=False)
if True:
    o = pd.read_csv(ROOT/'data'/'raw'/'ca_alpr_operators.csv').fillna('(not tagged)')
    print(o['operator:type'].value_counts().head(10)); print(o['operator'].value_counts().head(20)); print(o['manufacturer'].value_counts().head(10))
