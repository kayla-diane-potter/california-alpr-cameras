"""Who runs California's mapped plate cameras, from the operator tag.
Usage: python scripts/operators_flock.py   (writes data/processed/ca_alpr_operators_classified.csv and charts/05_who_operates.png)"""
import sys, re, pandas as pd, matplotlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]   # repo root, so the script runs from anywhere
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
src=ROOT/'data'/'raw'/'ca_alpr_operators.csv'; out=ROOT/'charts'
o=pd.read_csv(src,dtype=str).fillna('')
LAW=r'police|sheriff|highway patrol|\bchp\b|public safety|\blasd\b|\blapd\b|\bpd\b|customs and border|marshal|district attorney|law enforcement'
GOV=r'^city of|^town of|^county of|county$|city$|authority|transit|transportation|caltrans|department of|public works|parks|port of|airport|unified school|school district|state of california'
BIZ=r'home dep|lowe|walmart|sam.s club|costco|target|mall|galleria|kaiser|hospital|medical|shopping|center|plaza|market|bank|apartments|hotel|casino|inc\.?$|llc|company|corp'
COMM=r'association|hoa|homeowners|community|estates|ranch|village|club'
UNI=r'university|college|campus|\buc\b|csu'
def kind(s,t):
    l=s.lower(); t=t.lower()
    if not l: return 'Not tagged'
    if 'flock' in l: return 'Not tagged'   # vendor named as operator, owner unknown
    if re.search(LAW,l) or t=='law enforcement': return 'Police, sheriff or CHP'
    if re.search(UNI,l) or t=='university': return 'University'
    if re.search(COMM,l) or t in('community','association'): return 'HOA or community group'
    if re.search(BIZ,l) or t=='private': return 'Private business'
    if re.search(GOV,l) or t in('government','public'): return 'City or other agency'
    return 'City or other agency' if len(l.split())<=2 else 'Other'
o['kind']=[kind(a,b) for a,b in zip(o.operator,o['operator:type'])]
o['flock_any']=o.manufacturer.str.contains('flock',case=False)
print('Flock incl. Flock Group:',o.flock_any.sum(), round(o.flock_any.mean()*100,1))
print(o.kind.value_counts())
tg=o[o.kind!='Not tagged']; v=tg.kind.value_counts(); print((v/v.sum()*100).round(1))
print(tg[tg.kind=='Other'].operator.value_counts().head(20))
o.to_csv(ROOT/'data'/'processed'/'ca_alpr_operators_classified.csv',index=False)
import logging; logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)  # quiet if Inter isn't installed
SLATE='#4A3F48'; PEANUT='#BF9A84'; INK='#2E262C'; PLUM='#6B5E62'; LINEN='#E0D8CC'; BG='#FBFAF7'
plt.rcParams.update({'font.family':['Inter','DejaVu Sans'],'font.size':11,'text.color':INK,'axes.labelcolor':PLUM,'xtick.color':PLUM,'ytick.color':PLUM,
 'axes.edgecolor':LINEN,'figure.facecolor':BG,'axes.facecolor':BG,'savefig.facecolor':BG,'axes.spines.top':False,'axes.spines.right':False})
v=v.sort_values(); pct=v/v.sum()*100
fig,ax=plt.subplots(figsize=(9,4.8))
bars=ax.barh(v.index,pct,color=[PEANUT if k=='Private business' else SLATE for k in v.index],height=0.6)
for r,p,n in zip(bars,pct,v): ax.text(p+1,r.get_y()+r.get_height()/2,(f"{p:.0f}%" if p>=1 else "<1%")+f"  ({n:,})",va='center',fontsize=10,color=INK)
ax.set_xlim(0,max(pct)*1.3); ax.set_xticks([]); ax.spines['bottom'].set_visible(False); ax.tick_params(axis='y',length=0)
ax.set_title('Police run most tagged cameras, but businesses run 1 in 8',loc='left',fontsize=15,fontweight='semibold',color=INK,pad=26)
ax.text(0,1.02,f"Who operates the {v.sum():,} mapped cameras that name an operator ({(o.kind=="Not tagged").mean()*100:.0f}% name none)",transform=ax.transAxes,fontsize=10.5,color=PLUM,va='bottom')
fig.tight_layout(); fig.savefig(f'{out}/05_who_operates.png',dpi=200)
