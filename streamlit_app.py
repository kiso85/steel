import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# ---------- data ----------
h = np.linspace(0, 24, 4001)
D = 25.0

def pv_curve(h):
    pv = np.zeros_like(h)
    mask = (h >= 5) & (h <= 21)
    theta = np.pi * (h[mask] - 5) / 16
    pv[mask] = 160 * np.power(np.sin(theta), 1.5)
    return pv

PV = pv_curve(h)
G  = np.trapezoid(PV, h)
self_use = np.minimum(PV, D)
surplus  = np.maximum(PV - D, 0)
deficit  = np.maximum(D - PV, 0)
SU = np.trapezoid(self_use, h)

# --- calibrate bands to match thesis Eq. 4.7 / Table 4.3 exactly ---
alpha = 0.70                                  # self-consumption ratio (Table 4.3)
export_share = min(1 - alpha, 0.20)           # regulatory export cap term in Eq. 4.7 -> 0.20
target_bat = alpha * G - SU                   # battery must make self-use+battery = alpha*G
export_cap = export_share * G

lo, hi = 0.0, surplus.max()
for _ in range(80):
    mid = (lo + hi) / 2
    val = np.trapezoid(np.minimum(surplus, mid), h)
    lo, hi = (mid, hi) if val < target_bat else (lo, mid)
battery_rate = (lo + hi) / 2
battery = np.minimum(surplus, battery_rate)
remaining = surplus - battery

lo, hi = 0.0, remaining.max()
for _ in range(80):
    mid = (lo + hi) / 2
    val = np.trapezoid(np.minimum(remaining, mid), h)
    lo, hi = (mid, hi) if val < export_cap else (lo, mid)
export_rate = (lo + hi) / 2
export = np.minimum(remaining, export_rate)
curtail = remaining - export

BAT = np.trapezoid(battery, h)
EXP = np.trapezoid(export, h)
CUR = np.trapezoid(curtail, h)
DEF = np.trapezoid(deficit, h)

# ---------- style ----------
plt.rcParams['font.family'] = 'DejaVu Sans'
fig, ax = plt.subplots(figsize=(11, 6.4), dpi=200)
ax.set_facecolor('white')
fig.patch.set_facecolor('white')

c_self    = '#ffd28a'
c_battery = '#f0993f'
c_export  = '#4f8fc0'
c_curtail = '#c9cdd3'
c_deficit = '#bfe9dd'
c_pv      = '#e8821e'
c_demand  = '#1b9e77'

ax.stackplot(h, self_use, battery, export, curtail,
             colors=[c_self, c_battery, c_export, c_curtail],
             edgecolor='none', alpha=0.95, zorder=2)
ax.fill_between(h, D + battery + export, D + battery + export + curtail,
                 facecolor=c_curtail, edgecolor='#8a8f96', hatch='////',
                 linewidth=0.0, zorder=2.5)
ax.fill_between(h, PV, D, where=(PV < D), color=c_deficit, alpha=0.8, zorder=1)

ax.plot(h, PV, color=c_pv, linewidth=2.6, zorder=3)
ax.plot(h, np.full_like(h, D), color=c_demand, linewidth=2.6, zorder=3)

ax.plot(h, self_use + battery, linestyle='--', color='#3a3a3a', linewidth=1.6, zorder=4)
ax.annotate('\u03b1 = 70% boundary\n(self-use + battery, integrated over 24h)',
            xy=(9.4, self_use[np.searchsorted(h, 9.4)] + battery[np.searchsorted(h, 9.4)]),
            xytext=(1.0, 100),
            fontsize=9.5, color='#3a3a3a',
            arrowprops=dict(arrowstyle='-', color='#3a3a3a', lw=1.0))

ax.set_xlim(0, 24)
ax.set_ylim(0, 175)
ax.set_xticks(range(0, 25, 2))
ax.set_xticklabels([f"{x:02d}:00" for x in range(0, 25, 2)])
ax.set_xlabel('Hour of day', fontsize=13, labelpad=10)
ax.set_ylabel('Generation / demand (MWh/h)', fontsize=13, labelpad=10)
ax.grid(False)
for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)
for spine in ['left', 'bottom']:
    ax.spines[spine].set_color('#888888')
ax.tick_params(labelsize=11)

legend_handles = [
    Line2D([0], [0], color=c_pv, lw=2.6, label='PV generation (MWh/h)'),
    Line2D([0], [0], color=c_demand, lw=2.6, label='EAF demand (constant)'),
    Patch(facecolor=c_self, label='Self-use (direct to EAF)'),
    Patch(facecolor=c_battery, label='Battery charging (stored, later self-consumed)'),
    Patch(facecolor=c_export, label='Grid export (capped at 20% of generation)'),
    Patch(facecolor=c_curtail, edgecolor='#8a8f96', hatch='////', label='Curtailed / wasted (excess surplus)'),
    Patch(facecolor=c_deficit, label='Deficit \u2192 battery discharge / grid import'),
]
ax.legend(handles=legend_handles, loc='upper left', frameon=True, fontsize=10,
          framealpha=0.95, edgecolor='#cccccc')

ax.text(13, 12, f'Self-use\n{SU:.0f} MWh', ha='center', va='center',
        fontsize=10, color='#6b3e00', weight='bold')
ax.text(13, 55, f'Battery\n{BAT:.0f} MWh', ha='center', va='center',
        fontsize=10, color='white', weight='bold')
ax.text(13, 104, f'Export\n{EXP:.0f} MWh (20%)', ha='center', va='center',
        fontsize=9.5, color='white', weight='bold')
ax.annotate(f'Curtailed\n{CUR:.0f} MWh (10%)', xy=(13, 145), xytext=(17.6, 152),
            fontsize=10, color='#55585c', weight='bold',
            arrowprops=dict(arrowstyle='-', color='#55585c', lw=1.1))
ax.annotate('Peak generation\n~160 MWh/h', xy=(13, 160), xytext=(15.8, 168),
            fontsize=10.5, color=c_pv,
            arrowprops=dict(arrowstyle='-', color=c_pv, lw=1.2))
ax.annotate(f'Nighttime deficit\n(~{DEF:.0f} MWh)', xy=(22, 13), xytext=(18.3, 55),
            fontsize=10.5, color=c_demand,
            arrowprops=dict(arrowstyle='-', color=c_demand, lw=1.2))

plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/fig_pv_balance.png', dpi=200, facecolor='white')
print(f"G={G:.0f} SU={SU:.0f} BAT={BAT:.0f} (SU+BAT={SU+BAT:.0f}, {100*(SU+BAT)/G:.1f}%) EXP={EXP:.0f} ({100*EXP/G:.1f}%) CUR={CUR:.0f} ({100*CUR/G:.1f}%) DEF={DEF:.0f}")
