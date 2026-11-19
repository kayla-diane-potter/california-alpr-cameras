"""Charts and county map for the Flock / ALPR case study.
Usage: python scripts/charts_flock.py   (run analyze_flock.py first; writes charts/01-04)"""
import sys, json, pandas as pd, numpy as np, matplotlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]   # repo root, so the script runs from anywhere
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon, Patch
src=ROOT/'data'/'processed'/'flock_by_county.csv'; geo=ROOT/'data'/'raw'/'ca_counties.geojson'; out=ROOT/'charts'
import logging; logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)  # quiet if Inter isn't installed
SLATE='#4A3F48'; PEANUT='#BF9A84'; DPEANUT='#8A6450'; INK='#2E262C'; PLUM='#6B5E62'; LINEN='#E0D8CC'; BG='#FBFAF7'; WOOL='#C9C0B0'; PEBBLE='#8E8180'; COTTON='#F4F3EE'
plt.rcParams.update({'font.family':['Inter','DejaVu Sans'],'font.size':11,'text.color':INK,'axes.labelcolor':PLUM,'xtick.color':PLUM,'ytick.color':PLUM,
 'axes.edgecolor':LINEN,'figure.facecolor':BG,'axes.facecolor':BG,'savefig.facecolor':BG,'axes.spines.top':False,'axes.spines.right':False})
m=pd.read_csv(src); STATE=m.alpr.sum()/m.population_2026.sum()*1e5
def title(ax,t,s,pad=26):
    ax.set_title(t,loc='left',fontsize=15,fontweight='semibold',color=INK,pad=pad)
    ax.text(0,1.0+0.012*26/pad*1.5 if pad!=26 else 1.02,s,transform=ax.transAxes,fontsize=10.5,color=PLUM,va='bottom')
def save(fig,name): fig.tight_layout(); fig.savefig(f'{out}/{name}',dpi=200); plt.close(fig)

# 1 map
bins=[0,0.001,25,50,75,100,1e9]; labs=['None mapped','Under 25','25 to 50','50 to 75','75 to 100','100 or more']
cols=[COTTON,LINEN,WOOL,PEBBLE,PLUM,SLATE]
rate=dict(zip(m.county,m.alpr_per_100k))
g=json.load(open(geo))
fig,ax=plt.subplots(figsize=(7.6,8.6))
for f in g['features']:
    n=f['properties']['NAME']; r=rate[n]; c=cols[np.digitize(r,bins)-1]
    polys=[f['geometry']['coordinates']] if f['geometry']['type']=='Polygon' else f['geometry']['coordinates']
    for p in polys:
        ax.add_patch(Polygon(p[0],closed=True,fc=c,ec='#FFFFFF' if c!=COTTON else WOOL,lw=0.6))
for f in g['features']:
    if f['properties']['NAME']=='Monterey':
        polys=[f['geometry']['coordinates']] if f['geometry']['type']=='Polygon' else f['geometry']['coordinates']
        for p in polys: ax.add_patch(Polygon(p[0],closed=True,fc='none',ec=PEANUT,lw=2.4,zorder=5))
        ax.annotate('Monterey\n87 per 100K',xy=(-121.3,36.2),xytext=(-123.9,35.2),fontsize=10,fontweight='semibold',color=INK,
            arrowprops=dict(arrowstyle='-',color=DPEANUT,lw=1))
ax.set_xlim(-124.6,-114); ax.set_ylim(32.4,42.1); ax.set_aspect(1/np.cos(np.radians(37.2)))
ax.axis('off')
ax.legend(handles=[Patch(fc=c,ec=WOOL if c==COTTON else c,label=l) for c,l in zip(cols,labs)],title='Cameras per 100K residents',
    frameon=False,loc='upper right',bbox_to_anchor=(1.0,0.98),fontsize=9.5,title_fontsize=10)
title(ax,'Plate cameras cluster in the Bay Area and Inland Empire',f'Mapped license plate cameras per 100,000 residents, by county (state: {STATE:.0f})')
save(fig,'01_map_alpr_per_100k.png')

# 2 ranked bar, counties of 100K+
b=m[m.population_2026>=100000].sort_values('alpr_per_100k')
fig,ax=plt.subplots(figsize=(9,9.4))
colors=[PEANUT if c=='Monterey' else SLATE for c in b.county]
bars=ax.barh(b.county,b.alpr_per_100k,color=colors,height=0.68)
for r,v in zip(bars,b.alpr_per_100k): ax.text(v+1.2,r.get_y()+r.get_height()/2,f"{v:.0f}",va='center',fontsize=9,color=INK,zorder=4,bbox=dict(boxstyle='square,pad=0.15',fc=BG,ec='none'))
ax.axvline(STATE,color=DPEANUT,lw=1,ls=(0,(3,3)),zorder=1)
ax.text(STATE+1,len(b)-0.2,f'State: {STATE:.0f}',color=DPEANUT,fontsize=9.5,va='bottom')
ax.set_xlim(0,118); ax.tick_params(axis='y',length=0,labelsize=9.5); ax.set_xticks([]); ax.spines['bottom'].set_visible(False)
ax.set_ylim(-0.7,len(b)+0.6)
title(ax,'Imperial has 7 times the camera rate of Humboldt','Mapped plate cameras per 100,000 residents, the 36 counties with 100K+ people')
save(fig,'02_rank_per_100k.png')

# 3 size bands
m['band']=pd.cut(m.population_2026,[0,100e3,500e3,1.5e6,20e6],labels=['Under 100K','100K to 500K','500K to 1.5M','1.5M and up'])
s=m.groupby('band',observed=True).agg(n=('county','size'),a=('alpr','sum'),p=('population_2026','sum')); s['r']=s.a/s.p*1e5
fig,ax=plt.subplots(figsize=(9,4.8))
bars=ax.bar(s.index.astype(str),s.r,color=SLATE,width=0.58)
for r,v,n in zip(bars,s.r,s.n):
    ax.text(r.get_x()+r.get_width()/2,v+1.5,f"{v:.0f}",ha='center',va='bottom',fontsize=12,fontweight='semibold',color=INK)
    ax.annotate(f"{n} counties",xy=(r.get_x()+r.get_width()/2,0),xycoords=('data','axes fraction'),xytext=(0,-32),textcoords='offset points',ha='center',va='top',fontsize=9,color=PLUM)
ax.set_ylim(0,72); ax.set_yticks([]); ax.spines['left'].set_visible(False); ax.tick_params(axis='x',length=0,pad=8)
title(ax,'County size barely changes the rate','Mapped plate cameras per 100,000 residents, grouped by county population')
save(fig,'03_rate_by_county_size.png')

# 4 Flock share, 12 counties with most cameras + Monterey
t=m.nlargest(12,'alpr'); t=pd.concat([t,m[m.county=='Monterey']]).drop_duplicates('county').sort_values('alpr')
t['share']=t.flock/t.alpr*100
fig,ax=plt.subplots(figsize=(9,6.6))
ax.barh(t.county,100,color=LINEN,height=0.62)
bars=ax.barh(t.county,t.share,color=[PEANUT if c=='Monterey' else SLATE for c in t.county],height=0.62)
for r,v,a in zip(bars,t.share,t.alpr):
    ax.text(v-1.5,r.get_y()+r.get_height()/2,f"{v:.0f}%",va='center',ha='right',fontsize=9.5,color='#FFFFFF',fontweight='semibold')
    ax.text(101.5,r.get_y()+r.get_height()/2,f"{a:,} cameras",va='center',ha='left',fontsize=9,color=PLUM)
ax.set_xlim(0,125); ax.set_xticks([]); ax.spines['bottom'].set_visible(False); ax.tick_params(axis='y',length=0)
title(ax,'Flock makes about 3 in 4 of the state\'s mapped cameras','Share of mapped plate cameras tagged as Flock Safety, counties with the most cameras')
save(fig,'04_flock_share.png')
print('state rate',STATE); print(s)
