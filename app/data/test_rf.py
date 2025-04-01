import skrf as rf
from skrf.data import ring_slot
import matplotlib.pyplot as plt
from os import path
ring_s1p = ring_slot.subnetwork([0])
basedir = path.dirname(__file__)

open = rf.Network(basedir+'./dut_c.s2p')

#ring_s1p.plot_s_smith(draw_labels=True, show_legend=True)
open.plot_s_smith(draw_labels=True, show_legend=True)
print(open.frequency.f[1])
print(open.frequency.f[-1])
#plt.show()

lines = [
    {'marker_idx': [1, -1], 'color': 'g', 'm': 0, 'n': 0, 'ntw': ring_slot},
    {'marker_idx': [1, -1], 'color': 'r', 'm': 1, 'n': 0, 'ntw': ring_slot},
    {'marker_idx': [1, -1], 'color': 'm', 'm': 1, 'n': 1, 'ntw': ring_slot}
]

#open.plot_s_db(m=0,n=0,label="Theory")

plt.show()