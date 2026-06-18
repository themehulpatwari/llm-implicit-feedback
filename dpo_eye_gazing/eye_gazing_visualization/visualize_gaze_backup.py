"""
Eye-gaze trajectory visualization for user {WORKER_ID}, task 317.

Character positions are measured from the actual renderer (via
get_window_extent) so gaze dots align with the text they reference.
"""

import os
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize
import matplotlib.patches as mpatches
from matplotlib.font_manager import FontProperties

# ── Load responses ────────────────────────────────────────────────────────────
responses = {}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample_query_logs_table.csv')) as f:
    for row in csv.DictReader(f):
        if row['user_id'] == '{WORKER_ID}' and row['task_id'] == '317':
            responses[row['query_ID']] = {
                'text': row['llm_response_1'],
                'ts':   row['query_timestamp'],
            }

query_order = sorted(responses.keys(), key=lambda q: responses[q]['ts'])

# ── Match gaze rows to responses ──────────────────────────────────────────────
def find_query(snippet, char_idx):
    snippet = snippet.strip()
    if len(snippet) < 5:
        return None
    best, best_d = None, 999
    for qid, d in responses.items():
        p = d['text'].find(snippet)
        if p != -1:
            dist = abs(p - char_idx)
            if dist < 50 and dist < best_d:
                best_d, best = dist, qid
    return best

gaze_by_q = {q: [] for q in query_order}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '{WORKER_ID}', '317', 'rel_gaze_one.csv')) as f:
    for r in csv.reader(f):
        if len(r) > 3 and r[3].strip():
            qid = find_query(r[2], int(r[3]))
            if qid:
                rlen = len(responses[qid]['text'])
                gaze_by_q[qid].append({
                    'char_idx': min(int(r[3]), rlen - 1),
                    'unix_ts':  int(r[6]),
                })

for q in query_order:
    gaze_by_q[q].sort(key=lambda g: g['unix_ts'])

# ── Word-wrap preserving original char_idx positions ──────────────────────────
WRAP = 70

def build_map(text, wrap_width=WRAP):
    """
    Manual word-wrap that returns display_lines and char_to_pos.
    char_to_pos[i] = (col, line_num) in the displayed layout.
    Handles explicit \\n as hard line breaks (no textwrap, which embeds \\n
    inside line strings and causes cumulative drift).
    """
    char_to_pos = {}
    display_lines = ['']
    col, line_num = 0, 0
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == '\n':
            char_to_pos[i] = (col, line_num)
            display_lines.append('')
            line_num += 1
            col = 0
            i += 1
        elif ch in ' \t\r':
            char_to_pos[i] = (col, line_num)
            display_lines[-1] += ch
            col += 1
            i += 1
        else:
            j = i
            while j < len(text) and text[j] not in ' \t\r\n':
                j += 1
            word_len = j - i
            if col > 0 and col + word_len > wrap_width:
                display_lines.append('')
                line_num += 1
                col = 0
            for k in range(word_len):
                char_to_pos[i + k] = (col + k, line_num)
                display_lines[-1] += text[i + k]
            col += word_len
            i = j
    while display_lines and display_lines[-1].strip() == '':
        display_lines.pop()
    return display_lines, char_to_pos

# ── Measure true character dimensions from renderer ───────────────────────────
FONT_SIZE = 8   # pt  (monospace → one measurement gives all char widths)

def measure_char_dims(fig, ax, font_size=FONT_SIZE):
    """
    Adapted from vis_text_loc_2.py:
    Render an invisible 'M', call get_window_extent(renderer), invert back
    to axes coordinates to get the true char width/height.
    """
    fp = FontProperties(size=font_size, family='monospace')
    renderer = fig.canvas.get_renderer()
    inv = ax.transAxes.inverted()

    ref = ax.text(0, 0, 'M', fontproperties=fp,
                  transform=ax.transAxes, alpha=0)
    bbox = ref.get_window_extent(renderer=renderer)
    p0 = inv.transform((bbox.x0, bbox.y0))
    p1 = inv.transform((bbox.x1, bbox.y1))
    char_w = p1[0] - p0[0]
    char_h = p1[1] - p0[1]
    ref.remove()
    line_h = char_h * 1.4   # 40 % leading, same as vis_text_loc_2.py
    return char_w, char_h, line_h, fp

# ── Palette ───────────────────────────────────────────────────────────────────
BG      = '#0b0b18'
PANBG   = '#10101e'
TXTCLR  = '#6b6b8a'
CMAP    = 'plasma'
BORDERS = ['#00b4d8', '#4cc9f0', '#7bf1a8', '#ffd60a', '#ff6b6b']

X0, Y0 = 0.02, 0.97   # top-left origin in axes coordinates

n = len(query_order)
total_fix = sum(len(gaze_by_q[q]) for q in query_order)

fig = plt.figure(figsize=(28, n * 10 + 1), facecolor=BG)
fig.suptitle(
    'Eye-Gaze Trajectory on LLM Responses\n'
    f'User: {WORKER_ID}  ·  Task 317  ·  {total_fix} fixations across {n} responses',
    color='white', fontsize=17, fontweight='bold', y=1.0,
)

gs = gridspec.GridSpec(
    n, 2, figure=fig,
    left=0.01, right=0.99,
    top=0.985, bottom=0.005,
    hspace=0.07, wspace=0.03,
    width_ratios=[3, 1],
)

# Force the layout so axes sizes are fixed before we call get_renderer()
fig.canvas.draw()

for idx, qid in enumerate(query_order):
    text   = responses[qid]['text']
    ts_str = responses[qid]['ts']
    gpts   = gaze_by_q[qid]
    border = BORDERS[idx % len(BORDERS)]

    display_lines, c2p = build_map(text)
    n_lines = len(display_lines)

    ax_t = fig.add_subplot(gs[idx, 0])   # text + gaze panel
    ax_r = fig.add_subplot(gs[idx, 1])   # char-idx timeline

    # Text panel uses axes coordinates [0,1]×[0,1] so data coords = axes coords
    ax_t.set_xlim(0, 1)
    ax_t.set_ylim(0, 1)
    ax_t.set_facecolor(PANBG)
    ax_t.set_xticks([]); ax_t.set_yticks([])
    for sp in ax_t.spines.values():
        sp.set_visible(True); sp.set_edgecolor(border); sp.set_linewidth(1.8)

    ax_r.set_facecolor(PANBG)
    for sp in ax_r.spines.values():
        sp.set_edgecolor(border); sp.set_linewidth(1.8)

    # ── Measure true character size (vis_text_loc_2 approach) ────────────────
    char_w, char_h, line_h, fp = measure_char_dims(fig, ax_t)

    # Helper: char_idx → center in axes (= data) coords
    def char_center(col, line_num):
        x = X0 + col * char_w + char_w / 2
        y = Y0 - line_num * line_h - char_h / 2
        return x, y

    # ── Render background text lines ──────────────────────────────────────────
    for ln, line in enumerate(display_lines):
        y = Y0 - ln * line_h
        if y < 0:
            break
        ax_t.text(X0, y, line, fontproperties=fp,
                  transform=ax_t.transAxes,
                  color=TXTCLR, va='top', ha='left', zorder=2)

    # ── Compute gaze positions using measured character locations ─────────────
    if gpts:
        xs, ys, ts_a, ci_a = [], [], [], []
        for g in gpts:
            ci  = g['char_idx']
            pos = c2p.get(ci)
            if pos is None:
                pos = c2p[min(c2p, key=lambda k: abs(k - ci))]
            col, ln = pos
            x, y = char_center(col, ln)
            xs.append(x); ys.append(y)
            ts_a.append(g['unix_ts']); ci_a.append(ci)

        xs    = np.array(xs);   ys    = np.array(ys)
        ts_a  = np.array(ts_a); ci_a  = np.array(ci_a)
        tnorm = (ts_a - ts_a.min()) / max(ts_a.max() - ts_a.min(), 1)

        # ── Per-character reading heat ────────────────────────────────────────
        freq = {}
        for ci in ci_a:
            freq[ci] = freq.get(ci, 0) + 1
        max_freq = max(freq.values())
        hcmap = plt.colormaps['YlOrRd']
        for ci, cnt in freq.items():
            pos = c2p.get(ci)
            if pos is None:
                continue
            col, ln = pos
            x_rect = X0 + col * char_w
            y_rect = Y0 - ln * line_h - char_h   # bottom-left of cell
            intensity = cnt / max_freq
            rect = mpatches.FancyBboxPatch(
                (x_rect, y_rect), char_w, char_h,
                boxstyle='square,pad=0',
                facecolor=hcmap(intensity),
                alpha=0.35 * intensity + 0.05,
                linewidth=0, zorder=1,
            )
            ax_t.add_patch(rect)

        # ── Trajectory lines — all segments, colored by time ─────────────────
        cmap_fn = plt.colormaps[CMAP]
        segments  = [[[xs[i], ys[i]], [xs[i+1], ys[i+1]]]
                     for i in range(len(xs) - 1)]
        seg_colors = [cmap_fn((tnorm[i] + tnorm[i+1]) / 2)
                      for i in range(len(xs) - 1)]
        lc = LineCollection(segments, colors=seg_colors,
                            linewidths=0.6, alpha=0.5, zorder=3)
        ax_t.add_collection(lc)

        # ── Gaze dots ─────────────────────────────────────────────────────────
        ax_t.scatter(xs, ys, c=tnorm, cmap=CMAP, s=30, alpha=0.92,
                     zorder=4, vmin=0, vmax=1, linewidths=0)
        ax_t.scatter([xs[0]], [ys[0]], marker='*', s=240,
                     color='lime', zorder=7, edgecolors='white', linewidths=0.5)
        ax_t.scatter([xs[-1]], [ys[-1]], marker='X', s=140,
                     color='tomato', zorder=7, edgecolors='white', linewidths=0.5)

        # Colorbar
        sm = plt.cm.ScalarMappable(cmap=CMAP, norm=Normalize(0, 1))
        sm.set_array([])
        cb = plt.colorbar(sm, ax=ax_t, fraction=0.009, pad=0.004)
        cb.set_label('Fixation time (early → late)', color='white', fontsize=8)
        cb.ax.yaxis.set_tick_params(color='white', labelcolor='white', labelsize=7)
        cb.outline.set_edgecolor(border)

        # Legend
        hdl = [
            mpatches.Patch(color='#cc6622', alpha=0.6, label='Reading heat'),
            mpatches.Patch(color='lime',   label='Start'),
            mpatches.Patch(color='tomato', label='End'),
        ]
        ax_t.legend(handles=hdl, loc='lower right', fontsize=7.5,
                    framealpha=0.4, labelcolor='white', facecolor='#1a1a2e')

        # ── Timeline: char_idx vs elapsed time ────────────────────────────────
        elapsed = (ts_a - ts_a.min()) / 1000.0
        ax_r.scatter(elapsed, ci_a, c=tnorm, cmap=CMAP,
                     s=14, alpha=0.8, vmin=0, vmax=1, linewidths=0, zorder=2)
        ax_r.plot(elapsed, ci_a, color='#333355', lw=0.5, alpha=0.5, zorder=1)
        ax_r.set_xlabel('Elapsed time (s)', color='white', fontsize=9)
        ax_r.set_ylabel('Character index', color='white', fontsize=9)
        ax_r.tick_params(colors='white', labelsize=8)
        ax_r.set_ylim(len(text), -0.5)
        ax_r.set_title(f'{len(gpts)} fixations  ·  {len(text)} chars',
                       color=border, fontsize=9)
        ax_r.yaxis.grid(True, color='#222244', linewidth=0.5, zorder=0)
        ax_r.xaxis.grid(True, color='#222244', linewidth=0.5, zorder=0)

    short = text[:68].replace('\n', ' ')
    ax_t.set_title(
        f'Response {idx + 1}  (query {qid}  ·  {ts_str})\n"{short}…"',
        color='white', fontsize=9.5, pad=5, loc='left',
    )

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gaze_trajectory.png')
plt.savefig(out, dpi=160, bbox_inches='tight', facecolor=BG)
plt.close()
print(f'Saved → {out}')
