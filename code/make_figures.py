from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'figures'; OUT.mkdir(exist_ok=True)
R = ROOT / 'results'
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

q2 = json.loads((R/'q2_probability.json').read_text(encoding='utf-8'))
q3 = json.loads((R/'q3_threshold.json').read_text(encoding='utf-8'))
q4 = json.loads((R/'q4_mixture_search.json').read_text(encoding='utf-8'))

def save(name):
    plt.tight_layout(); plt.savefig(OUT/name, bbox_inches='tight'); plt.close()

# 1. Q1 group counts
plt.figure(figsize=(6,4)); plt.bar(['组1','组2','组3'], [12,49,535], color='#3973ac'); plt.ylabel('介质 A 数量'); plt.title('附件三组介质数量'); save('fig_q1_counts.pdf')

# 2. Q2 probability curve
x=np.array([d['fraction']*100 for d in q2]); y=np.array([d['probability'] for d in q2]);
plt.figure(figsize=(6,4)); plt.plot(x,y,'o-',lw=2,color='#c44e52'); plt.axhline(.9,ls='--',color='gray'); plt.xlabel('A体积分数 (%)'); plt.ylabel('导通概率'); plt.ylim(0,1.08); save('fig_q2_curve.pdf')

# 3. Q2 confidence intervals
lo=np.array([d['wilson95_low'] for d in q2]); hi=np.array([d['wilson95_high'] for d in q2]);
plt.figure(figsize=(6,4)); plt.errorbar(x,y,[y-lo,hi-y],fmt='o',capsize=5,color='#4c72b0'); plt.axhline(.9,ls='--',color='gray'); plt.xlabel('A体积分数 (%)'); plt.ylabel('概率及 Wilson 95% 区间'); plt.ylim(0,1.08); save('fig_q2_ci.pdf')

# 4. Q3 threshold scan
x3=np.array([d['fraction']*100 for d in q3]); y3=np.array([d['probability'] for d in q3]);
plt.figure(figsize=(6,4)); plt.plot(x3,y3,'s-',color='#55a868'); plt.axhline(.9,ls='--',color='gray'); plt.xlabel('A体积分数 (%)'); plt.ylabel('导通概率'); plt.ylim(0,1.08); save('fig_q3_scan.pdf')

# 5. Q4 cost-probability scatter
c=np.array([d['cost'] for d in q4]); p=np.array([d['probability'] for d in q4]);
plt.figure(figsize=(6,4)); plt.scatter(c,p,c=p,cmap='viridis',s=45); plt.axhline(.9,ls='--',color='gray'); plt.xlabel('总成本（元）'); plt.ylabel('导通概率'); plt.colorbar(label='概率'); save('fig_q4_cost.pdf')

# 6. Q4 A/B fraction map for all candidates
fa=np.array([d['fraction_a']*100 for d in q4]); fb=np.array([d['fraction_b']*100 for d in q4]);
plt.figure(figsize=(6,4)); plt.scatter(fa,fb,c=p,cmap='RdYlGn',s=55,edgecolor='k',lw=.2); plt.xlabel('A体积分数 (%)'); plt.ylabel('B体积分数 (%)'); plt.colorbar(label='导通概率'); save('fig_q4_map.pdf')

# 7. actual group 1 geometry projection
import openpyxl
wb=openpyxl.load_workbook(ROOT/'00_题目与数据/附件.xlsx',data_only=True); ws=wb.worksheets[0]
rows=[]
for row in ws.iter_rows(min_row=3, values_only=True):
    if row[0] is not None: rows.append(row)
plt.figure(figsize=(7,4));
for row in rows:
    plt.plot([row[0],row[3]],[row[1],row[4]],'-',lw=1.5,alpha=.8)
plt.axvline(-5000,color='k',ls='--'); plt.axvline(5000,color='k',ls='--'); plt.xlabel('X (nm)'); plt.ylabel('Y (nm)'); plt.title('附件组1介质 A 投影'); save('fig_q1_geometry.pdf')

# 8. workflow schematic
fig,ax=plt.subplots(figsize=(11,2.8)); ax.axis('off'); labels=['附件数据','周期距离','连通图','蒙特卡洛','阈值/成本','论文验收']; xs=[.08,.25,.42,.59,.76,.93]
for i,(xx,lab) in enumerate(zip(xs,labels)):
    box=FancyBboxPatch((xx-.07,.38),.14,.24,boxstyle='round,pad=.02',fc=['#d9eaf7','#dff0d8','#fff2cc','#fce4d6','#eadcf8','#e5e5e5'][i],ec='#555')
    ax.add_patch(box); ax.text(xx,.5,lab,ha='center',va='center',fontsize=11)
    if i<len(xs)-1: ax.add_patch(FancyArrowPatch((xx+.075,.5),(xs[i+1]-.075,.5),arrowstyle='->',mutation_scale=15,color='#555'))
save('fig_workflow.pdf')
