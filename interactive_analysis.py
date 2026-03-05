"""
Othello AI – Interactive Algorithm Analysis
Run:  python3 interactive_analysis.py
"""

import time
import subprocess, sys
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.widgets import Slider, Button

# ── Font: match the game (Arial) ─────────────────────────────────────────────
plt.rcParams['font.family']     = 'Arial'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica Neue', 'DejaVu Sans']

from model.game_state import GameState
from algorithms.greedy          import get_greedy_move_generator
from algorithms.divide_and_conquer import choosebestmovevisual
from algorithms.dp              import get_dp_move_generator
from algorithms.backtracking    import get_backtracking_move_generator

# ── Benchmark ─────────────────────────────────────────────────────────────────

COUNTED = {'search_node', 'leaf', 'dp_hit'}

def benchmark(func, depth, is_greedy=False, is_dnc=False):
    state = GameState()
    gen = func(state) if is_greedy else (
          func(state.board, state.player, depth=depth) if is_dnc else
          func(state, depth=depth))
    n, t0 = 0, time.perf_counter()
    for evt in gen:
        if evt['type'] in COUNTED:
            n += 1
    return max(time.perf_counter() - t0, 1e-4), max(n, 1)

# ── Algorithm table ───────────────────────────────────────────────────────────

ALGOS = [
    ("Greedy",          get_greedy_move_generator,       True,  False, "O(b)",              "O(1)"),
    ("Divide & Conquer",choosebestmovevisual,             False, True,  "O(b^d/2)–O(b^d)",   "O(d)"),
    ("Backtracking",    get_backtracking_move_generator, False, False, "O(b^d/2)–O(b^d)",   "O(d) in-place"),
    ("DP",              get_dp_move_generator,           False, False, "O(|S|)",             "O(|S|)"),
]

NAMES  = [a[0] for a in ALGOS]
COLORS = ['#e05c5c', '#e8973a', '#4a86c8', '#4caf73']

COMPLEXITY_ROWS = [
    ("Algorithm",        "Time Complexity",      "Space Complexity", "Key Insight"),
    ("Greedy",           "O(b)",                 "O(1)",             "No look-ahead; instant greedy pick"),
    ("Divide & Conquer", "O(b^d/2) – O(b^d)",   "O(d)",             "Splits moves, merges sub-results"),
    ("Backtracking",     "O(b^d/2) – O(b^d)",   "O(d)  [in-place]","Single board; undo/redo; α-β pruning"),
    ("DP",               "O(|S|) unique states", "O(|S|)",           "Transposition table skips re-work"),
]

# ── Figure ────────────────────────────────────────────────────────────────────

plt.style.use('seaborn-v0_8-whitegrid')
fig = plt.figure(figsize=(16, 9), facecolor='#f5f5f5')
fig.suptitle("Othello AI  ·  Algorithm Analysis",
             fontsize=17, fontweight='bold', color='#222', y=0.97)

gs = gridspec.GridSpec(3, 2, figure=fig,
                       left=0.07, right=0.96, top=0.91, bottom=0.04,
                       hspace=0.55, wspace=0.30,
                       height_ratios=[4, 0.55, 1.8])

ax_time  = fig.add_subplot(gs[0, 0])
ax_nodes = fig.add_subplot(gs[0, 1])
ax_ctrl  = fig.add_subplot(gs[1, :])
ax_table = fig.add_subplot(gs[2, :])
ax_ctrl.set_axis_off()
ax_table.set_axis_off()

for ax in (ax_time, ax_nodes):
    ax.set_facecolor('white')
    for sp in ax.spines.values():
        sp.set_color('#ccc')

# ── Controls ──────────────────────────────────────────────────────────────────

ax_s = plt.axes([0.15, 0.385, 0.50, 0.025], facecolor='#e8e8e8')
slider = Slider(ax_s, 'Depth  d =', valmin=1, valmax=5,
                valinit=3, valstep=1, color='#4a90d9')
slider.label.set_color('#333')
slider.valtext.set_color('#1a6bb5')
slider.valtext.set_fontsize(13)
slider.valtext.set_fontweight('bold')

ax_b = plt.axes([0.70, 0.373, 0.14, 0.045])
btn = Button(ax_b, 'Run Benchmark', color='#4a90d9', hovercolor='#357abd')
btn.label.set_fontsize(12)
btn.label.set_color('white')

# ── Complexity table ──────────────────────────────────────────────────────────

col_x      = [0.01, 0.22, 0.44, 0.62, 0.82]
row_y      = [0.88, 0.68, 0.48, 0.28, 0.08]
hdr_color  = '#1a6bb5'
row_colors = ['#c0392b', '#d35400', '#2471a3', '#1e8449']

for ci, (txt, x) in enumerate(zip(COMPLEXITY_ROWS[0], col_x)):
    ax_table.text(x, row_y[0], txt, transform=ax_table.transAxes,
                  fontsize=10, fontweight='bold', color=hdr_color, va='top')

for ri, row in enumerate(COMPLEXITY_ROWS[1:], 1):
    for ci, (cell, x) in enumerate(zip(row, col_x)):
        ax_table.text(x, row_y[ri], cell, transform=ax_table.transAxes,
                      fontsize=9.5, va='top', fontfamily='monospace',
                      color=row_colors[ri-1] if ci == 0 else '#333')

ax_table.plot([0, 1], [0.955, 0.955], color='#ccc', linewidth=1,
              transform=ax_table.transAxes, clip_on=False)

# ── Chart draw ────────────────────────────────────────────────────────────────

def draw_charts(disp_t, disp_n, depth, final=False):
    for ax, vals, title, ylabel, marker, lc in [
        (ax_time,  disp_t, "Execution Time  ↓  Lower is Better",  "Seconds",    'o', '#c0392b'),
        (ax_nodes, disp_n, "Nodes Evaluated  ↓  Lower is Better", "Node Count", 's', '#1a5276'),
    ]:
        ax.clear()
        ax.set_facecolor('white')
        for sp in ax.spines.values():
            sp.set_color('#ccc')
        ax.tick_params(colors='#555', labelsize=9)

        bars = ax.bar(NAMES, vals, color=COLORS, alpha=0.82,
                      edgecolor='#aaa', linewidth=0.8)
        ax.plot(range(len(NAMES)), vals, color=lc,
                marker=marker, linewidth=2, markersize=7, zorder=5)
        ax.set_title(title, color='#222', fontsize=11, fontweight='bold', pad=8)
        ax.set_ylabel(ylabel, color='#555', fontsize=9)
        ax.set_xticks(range(len(NAMES)))
        ax.set_xticklabels(NAMES, rotation=12, ha='right', fontsize=9)
        ax.yaxis.grid(True, linestyle='--', color='#e0e0e0', linewidth=0.8)
        ax.set_axisbelow(True)

        if final:
            mx = max(vals) if max(vals) > 0 else 1
            for bar, v in zip(bars, vals):
                fmt = f'{v:.4f}s' if ylabel == 'Seconds' else f'{int(v)}'
                ax.text(bar.get_x() + bar.get_width()/2, v + mx*0.02, fmt,
                        ha='center', va='bottom', fontsize=9,
                        fontweight='bold', color='#222')

    ax_time.text(0.98, 0.97, f"Depth  d = {depth}",
                 transform=ax_time.transAxes, ha='right', va='top',
                 fontsize=10, color='#1a5276', fontweight='bold')
    fig.canvas.draw_idle()

# ── Benchmark callback ────────────────────────────────────────────────────────

prev = {'t': [0.0]*4, 'n': [0.0]*4}

def run_benchmark(_event=None):
    depth = int(slider.val)
    btn.label.set_text('Computing…')
    btn.color = '#888'
    fig.canvas.draw_idle()
    plt.pause(0.02)

    print(f"\n[Benchmark  depth={depth}]")
    times, nodes = [], []
    for name, func, gr, dnc, *_ in ALGOS:
        t, n = benchmark(func, depth, is_greedy=gr, is_dnc=dnc)
        times.append(t); nodes.append(float(n))
        print(f"  {name:<20} {t:.5f}s   {int(n)} nodes")

    # ── Smooth animation via plt.pause() loop (reliable on all backends) ──────
    FRAMES = 28
    pt, pn = list(prev['t']), list(prev['n'])
    for frame in range(FRAMES):
        a = (frame + 1) / FRAMES
        disp_t = [pt[i] + (times[i] - pt[i]) * a for i in range(4)]
        disp_n = [pn[i] + (nodes[i] - pn[i]) * a for i in range(4)]
        draw_charts(disp_t, disp_n, depth, final=(frame == FRAMES - 1))
        plt.pause(0.018)

    prev['t'] = list(times)
    prev['n'] = list(nodes)

    btn.label.set_text('Run Benchmark')
    btn.color = '#4a90d9'
    fig.canvas.draw_idle()

btn.on_clicked(run_benchmark)
run_benchmark()
plt.show()
