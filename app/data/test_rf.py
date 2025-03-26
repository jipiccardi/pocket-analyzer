import skrf as rf
from skrf.data import ring_slot
import matplotlib.pyplot as plt
from os import path
ring_s1p = ring_slot.subnetwork([0])
basedir = path.dirname(__file__)

open = rf.Network(basedir+'./open_1p.s1p')


#ring_s1p.plot_s_smith(draw_labels=True, show_legend=True)
#open.plot_s_smith(draw_labels=True, show_legend=True)
print(open.frequency.f_scaled)
print(open.frequency.f[-1])
#plt.show()

lines = [
    {'marker_idx': [1, -1], 'color': 'g', 'm': 0, 'n': 0, 'ntw': open}
    #{'marker_idx': [1, -1], 'color': 'r', 'm': 1, 'n': 0, 'ntw': ring_slot},
]

# prepare figure
fig, ax = plt.subplots(1, 1, figsize=(7,8))

# impedance smith chart
rf.plotting.smith(ax = ax, draw_labels = True, ref_imm = 50.0, chart_type = 'z')

# plot data
col_labels = ['Frequency', 'Real Imag']
row_labels = []
row_colors = []
cell_text = []
for l in lines:
    m = l['m']
    n = l['n']
    l['ntw'].plot_s_smith(m=m, n=n, ax = ax, color=l['color'])
    #plot markers
    for i, k in enumerate(l['marker_idx']):
        x = l['ntw'].s.real[k, m, n]
        y = l['ntw'].s.imag[k, m, n]
        z = l['ntw'].z[k, m, n]
        z = f'{z.real:.4f} + {z.imag:.4f}j ohm'
        f = l['ntw'].frequency.f_scaled[k] / 1e6
        f_unit = "MHz" #l['ntw'].frequency.unit
        row_labels.append(f'M{i + 1}')
        row_colors.append(l['color'])
        ax.scatter(x, y, marker = 'v', s=20, color=l['color'])
        ax.annotate(row_labels[-1], (x, y), xytext=(-7, 7), textcoords='offset points', color=l['color'])
        cell_text.append([f'{f:.3f} {f_unit}', z])
leg1 = ax.legend(loc="upper right", fontsize= 6)

plt.show()