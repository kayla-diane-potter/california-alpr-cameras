"""Turn overpass turbo 'raw OSM data' JSON exports into CSVs.
Usage: python3 -I parse_exports.py counties <export.json> <out.csv>
       python3 -I parse_exports.py operators <export.json> <out.csv>"""
import sys, json, csv
mode, src, out = sys.argv[1:4]
els = json.load(open(src))['elements']
print('elements:', len(els))
rows = []
if mode == 'counties':
    i = 0
    while i < len(els):
        e = els[i]
        if e.get('type') == 'relation':
            t = e.get('tags', {})
            counts = [x for x in els[i+1:i+3] if x.get('type') == 'count']
            if len(counts) == 2:
                rows.append({'county': t.get('name', ''), 'wikipedia': t.get('wikipedia', ''),
                             'alpr': int(counts[0]['tags']['total']), 'flock': int(counts[1]['tags']['total'])})
                i += 3; continue
        i += 1
    # keep California counties only (shared border relations can sneak in)
    rows = [r for r in rows if 'California' in r['wikipedia'] or not r['wikipedia']]
    cols = ['county', 'alpr', 'flock']
else:
    for e in els:
        t = e.get('tags', {})
        rows.append({'manufacturer': t.get('manufacturer', ''), 'operator': t.get('operator', ''), 'operator:type': t.get('operator:type', '')})
    cols = ['manufacturer', 'operator', 'operator:type']
with open(out, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore'); w.writeheader(); w.writerows(rows)
print('rows written:', len(rows))
