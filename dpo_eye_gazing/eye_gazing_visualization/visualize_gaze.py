"""
Eye-gaze and mouse trajectory visualization — batch mode.

Scans all user/task folders under ROOT for the four required CSV files
(rel_gaze_one, rel_gaze_two, rel_mouse_left, rel_mouse_right) and
produces four figures per qualifying task, saved alongside the CSVs:
  gaze_trajectory.png, gaze_timeline.png,
  mouse_trajectory.png, mouse_timeline.png
"""

import os
import csv
import datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import Normalize
import matplotlib.patches as mpatches
from matplotlib.font_manager import FontProperties

ROOT     = os.path.dirname(os.path.abspath(__file__))
REQUIRED = {'rel_gaze_one.csv', 'rel_gaze_two.csv',
            'rel_mouse_left.csv', 'rel_mouse_right.csv'}

# ── Load all responses from query_logs_table.csv ───────────────────────────────
all_responses = {}   # (user_id, task_id) → {query_ID: {text, ts}}
with open(os.path.join(ROOT, 'query_logs_table.csv')) as f:
    for row in csv.DictReader(f):
        key = (row['user_id'], row['task_id'])
        if key not in all_responses:
            all_responses[key] = {}
        all_responses[key][row['query_ID']] = {
            'text1': row['llm_response_1'],
            'text2': row['llm_response_2'],
            'ts':    row['query_timestamp'],
        }

# ── Constants ──────────────────────────────────────────────────────────────────
WRAP      = 60
FONT_SIZE = 8
BG        = '#0b0b18'
PANBG     = '#10101e'
TXTCLR    = '#6b6b8a'
CMAP      = 'summer'
BORDERS   = ['#00b4d8', '#4cc9f0', '#7bf1a8', '#ffd60a', '#ff6b6b']
X0, Y0    = 0.02, 0.97

# ── Helpers ────────────────────────────────────────────────────────────────────
def _ts_to_ms(ts_str):
    dt = datetime.datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S').replace(
        tzinfo=datetime.timezone.utc)
    return int(dt.timestamp() * 1000)


def build_map(text, wrap_width=WRAP):
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


def measure_char_dims(fig, ax):
    fp = FontProperties(size=FONT_SIZE, family='monospace')
    renderer = fig.canvas.get_renderer()
    inv = ax.transAxes.inverted()
    ref = ax.text(0, 0, 'M', fontproperties=fp, transform=ax.transAxes, alpha=0)
    bbox = ref.get_window_extent(renderer=renderer)
    p0 = inv.transform((bbox.x0, bbox.y0))
    p1 = inv.transform((bbox.x1, bbox.y1))
    char_w = p1[0] - p0[0]
    char_h = p1[1] - p0[1]
    ref.remove()
    return char_w, char_h, char_h * 1.4, fp


def _find_query_by_time(unix_ts_ms, response_intervals):
    for t0, t1, qid in response_intervals:
        if t0 <= unix_ts_ms < t1:
            return qid
    return None


def load_gaze(path, query_order, responses, response_intervals, text_key='text1'):
    gaze_by_q = {q: [] for q in query_order}
    try:
        with open(path) as f:
            for r in csv.reader(f):
                if len(r) > 6 and r[6].strip() and r[3].strip():
                    try:
                        unix_ts = int(r[6])
                        qid = _find_query_by_time(unix_ts, response_intervals)
                        if qid:
                            rlen = len(responses[qid][text_key])
                            gaze_by_q[qid].append({
                                'char_idx': min(int(r[3]), rlen - 1),
                                'unix_ts':  unix_ts,
                            })
                    except (ValueError, IndexError):
                        pass
    except FileNotFoundError:
        pass
    for q in query_order:
        gaze_by_q[q].sort(key=lambda g: g['unix_ts'])
    return gaze_by_q


def draw_gaze_panel(fig, ax, text, ts_str, gpts, border, idx, qid, source_label):
    """Draw text + gaze/mouse overlay on ax.
    Returns (first_xy, last_xy, ts_to_xy)."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_facecolor(PANBG)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(True)
        sp.set_edgecolor(border)
        sp.set_linewidth(1.8)

    display_lines, c2p = build_map(text)
    char_w, char_h, line_h, fp = measure_char_dims(fig, ax)

    def char_center(char_col, line_num):
        x = X0 + char_col * char_w + char_w / 2
        y = Y0 - line_num * line_h - char_h / 2
        return x, y

    for ln, line in enumerate(display_lines):
        y = Y0 - ln * line_h
        if y < 0:
            break
        ax.text(X0, y, line, fontproperties=fp,
                transform=ax.transAxes,
                color=TXTCLR, va='top', ha='left', zorder=2)

    first_xy = last_xy = None
    ts_to_xy = {}

    if gpts:
        xs, ys, ts_a, ci_a = [], [], [], []
        for g in gpts:
            ci  = g['char_idx']
            pos = c2p.get(ci)
            if pos is None:
                pos = c2p[min(c2p, key=lambda k: abs(k - ci))]
            char_col, ln = pos
            x, y = char_center(char_col, ln)
            xs.append(x); ys.append(y)
            ts_a.append(g['unix_ts']); ci_a.append(ci)
            ts_to_xy[g['unix_ts']] = (x, y)

        xs   = np.array(xs);   ys   = np.array(ys)
        ts_a = np.array(ts_a); ci_a = np.array(ci_a)
        tnorm = (ts_a - ts_a.min()) / max(ts_a.max() - ts_a.min(), 1)

        first_xy = (xs[0], ys[0])
        last_xy  = (xs[-1], ys[-1])

        freq = {}
        for ci in ci_a:
            freq[ci] = freq.get(ci, 0) + 1
        max_freq = max(freq.values())
        hcmap = plt.colormaps['YlOrRd']
        for ci, cnt in freq.items():
            pos = c2p.get(ci)
            if pos is None:
                continue
            char_col, ln = pos
            rect = mpatches.FancyBboxPatch(
                (X0 + char_col * char_w, Y0 - ln * line_h - char_h),
                char_w, char_h,
                boxstyle='square,pad=0',
                facecolor=hcmap(cnt / max_freq),
                alpha=0.35 * (cnt / max_freq) + 0.05,
                linewidth=0, zorder=1,
            )
            ax.add_patch(rect)

        cmap_fn    = plt.colormaps[CMAP]
        seg_colors = np.array([cmap_fn((tnorm[i] + tnorm[i+1]) / 2)
                               for i in range(len(xs) - 1)])
        u = xs[1:] - xs[:-1]
        v = ys[1:] - ys[:-1]
        ax.quiver(xs[:-1], ys[:-1], u, v,
                  color=seg_colors,
                  angles='xy', scale_units='xy', scale=1,
                  width=0.003, headwidth=3, headlength=4, headaxislength=3.5,
                  alpha=0.65, zorder=3)

        ax.scatter(xs, ys, c=tnorm, cmap=CMAP, s=30, alpha=0.92,
                   zorder=4, vmin=0, vmax=1, linewidths=0)
        ax.scatter([xs[0]], [ys[0]], marker='*', s=240,
                   color='lime', zorder=7, edgecolors='white', linewidths=0.5)
        ax.scatter([xs[-1]], [ys[-1]], marker='X', s=140,
                   color='tomato', zorder=7, edgecolors='white', linewidths=0.5)

        sm = plt.cm.ScalarMappable(cmap=CMAP, norm=Normalize(0, 1))
        sm.set_array([])
        cb = plt.colorbar(sm, ax=ax, fraction=0.009, pad=0.004)
        cb.set_label('Fixation time (response start → end)', color='white', fontsize=7)
        cb.ax.yaxis.set_tick_params(color='white', labelcolor='white', labelsize=6)
        cb.outline.set_edgecolor(border)

        ax.legend(handles=[
            mpatches.Patch(color='#cc6622', alpha=0.6, label='Reading heat'),
            mpatches.Patch(color='lime',   label='Start'),
            mpatches.Patch(color='tomato', label='End'),
        ], loc='lower right', fontsize=7, framealpha=0.4,
           labelcolor='white', facecolor='#1a1a2e')

    short = text[:65].replace('\n', ' ')
    ax.set_title(
        f'[{source_label}]  Response {idx+1}  (query {qid}  ·  {ts_str})\n'
        f'"{short}…"  ·  {len(gpts)} fixations  ·  {len(text)} chars',
        color='white', fontsize=8.5, pad=5, loc='left',
    )
    return first_xy, last_xy, ts_to_xy


def draw_cross_links(fig, panel_data, key_a, key_b):
    """Draw ConnectionPatch lines from panel_a to panel_b for each response."""
    cmap_fn = plt.colormaps[CMAP]
    for pd in panel_data.values():
        ts2xy_a = pd[f'ts_to_xy_{key_a}']
        ts2xy_b = pd[f'ts_to_xy_{key_b}']
        if not ts2xy_a or not ts2xy_b:
            continue
        ts_a_sorted = np.array(sorted(ts2xy_a.keys()))
        all_ts_q = list(ts2xy_a.keys()) + list(ts2xy_b.keys())
        ts_q_min = min(all_ts_q)
        ts_q_max = max(all_ts_q)
        for ts2, (x2, y2) in ts2xy_b.items():
            i = np.searchsorted(ts_a_sorted, ts2)
            candidates = []
            if i < len(ts_a_sorted): candidates.append(ts_a_sorted[i])
            if i > 0:                candidates.append(ts_a_sorted[i - 1])
            ts1 = min(candidates, key=lambda t: abs(t - ts2))
            x1, y1 = ts2xy_a[ts1]
            t_norm = (ts2 - ts_q_min) / max(ts_q_max - ts_q_min, 1)
            fig.add_artist(mpatches.ConnectionPatch(
                xyA=(x1, y1), xyB=(x2, y2),
                coordsA='data', coordsB='data',
                axesA=pd[f'ax_{key_a}'], axesB=pd[f'ax_{key_b}'],
                color=cmap_fn(t_norm), lw=0.8, alpha=0.45, zorder=5,
            ))


# ── Per-task processing ────────────────────────────────────────────────────────
def process_task(user_id, task_id, task_dir, responses):
    query_order = sorted(responses.keys(), key=lambda q: responses[q]['ts'])
    if not query_order:
        print(f'  No responses found, skipping.')
        return

    # Build time intervals
    intervals = []
    for i, qid in enumerate(query_order):
        t0 = _ts_to_ms(responses[qid]['ts'])
        t1 = (_ts_to_ms(responses[query_order[i + 1]]['ts'])
              if i + 1 < len(query_order) else float('inf'))
        intervals.append((t0, t1, qid))

    gaze_one    = load_gaze(task_dir + '/rel_gaze_one.csv',    query_order, responses, intervals, text_key='text1')
    gaze_two    = load_gaze(task_dir + '/rel_gaze_two.csv',    query_order, responses, intervals, text_key='text2')
    mouse_left  = load_gaze(task_dir + '/rel_mouse_left.csv',  query_order, responses, intervals, text_key='text1')
    mouse_right = load_gaze(task_dir + '/rel_mouse_right.csv', query_order, responses, intervals, text_key='text2')

    # Height ratios proportional to line count of each response
    n_lines = []
    for qid in query_order:
        _, c2p1 = build_map(responses[qid]['text1'])
        _, c2p2 = build_map(responses[qid]['text2'])
        lines1 = max((ln for _, ln in c2p1.values()), default=0) + 1
        lines2 = max((ln for _, ln in c2p2.values()), default=0) + 1
        n_lines.append(max(lines1, lines2))
    per_line_in   = 10 / max(n_lines)
    height_ratios = n_lines
    n             = len(query_order)

    # Session-wide time range covering all 4 sources
    all_ts = [g['unix_ts']
              for src in (gaze_one, gaze_two, mouse_left, mouse_right)
              for q in query_order
              for g in src[q]]
    ts_global_min = min(all_ts) if all_ts else 0
    ts_global_max = max(all_ts) if all_ts else 1

    total_one   = sum(len(gaze_one[q])    for q in query_order)
    total_two   = sum(len(gaze_two[q])    for q in query_order)
    total_left  = sum(len(mouse_left[q])  for q in query_order)
    total_right = sum(len(mouse_right[q]) for q in query_order)

    # ── Figure 1: gaze trajectory ─────────────────────────────────────────────
    fig1 = plt.figure(figsize=(9, sum(n_lines) * per_line_in + 1), facecolor=BG)
    # fig1.suptitle(
    #     f'Eye-Gaze Trajectory  —  gaze_one (left)  ·  gaze_two (right)\n'
    #     f'User: {user_id}  ·  Task {task_id}  ·  '
    #     f'{total_one} fixations (gaze_one)  /  {total_two} fixations (gaze_two)  '
    #     f'across {n} responses',
    #     color='white', fontsize=14, fontweight='bold', y=1.0,
    # )
    gs1 = gridspec.GridSpec(n, 2, figure=fig1,
                            left=0.01, right=0.99, top=0.985, bottom=0.005,
                            hspace=0.08, wspace=0.03, height_ratios=height_ratios)
    fig1.canvas.draw()
    pd1 = {}
    for idx, qid in enumerate(query_order):
        text1 = responses[qid]['text1']; text2 = responses[qid]['text2']
        ts_str = responses[qid]['ts']
        border = BORDERS[idx % len(BORDERS)]
        ax_one = fig1.add_subplot(gs1[idx, 0])
        ax_two = fig1.add_subplot(gs1[idx, 1])
        _, _, ts2xy_one = draw_gaze_panel(fig1, ax_one, text1, ts_str,
                                          gaze_one[qid], border, idx, qid, 'gaze_one')
        _, _, ts2xy_two = draw_gaze_panel(fig1, ax_two, text2, ts_str,
                                          gaze_two[qid], border, idx, qid, 'gaze_two')
        pd1[qid] = {'ax_one': ax_one, 'ax_two': ax_two,
                    'ts_to_xy_one': ts2xy_one, 'ts_to_xy_two': ts2xy_two}
    draw_cross_links(fig1, pd1, 'one', 'two')
    out = task_dir + '/gaze_trajectory.png'
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close(fig1)
    print(f'  Saved → {out}')

    # ── Figure 2: gaze timeline ───────────────────────────────────────────────
    fig2 = plt.figure(figsize=(14, sum(n_lines) * per_line_in * 0.5 + 1), facecolor=BG)
    fig2.suptitle(
        f'Character Index vs Session Elapsed Time  —  gaze_one (left)  ·  gaze_two (right)\n'
        f'User: {user_id}  ·  Task {task_id}',
        color='white', fontsize=14, fontweight='bold', y=1.0,
    )
    gs2 = gridspec.GridSpec(n, 2, figure=fig2,
                            left=0.09, right=0.98, top=0.97, bottom=0.03,
                            hspace=0.50, wspace=0.30, height_ratios=height_ratios)
    for idx, qid in enumerate(query_order):
        border = BORDERS[idx % len(BORDERS)]
        for col, (gpts, label, text) in enumerate([
                (gaze_one[qid], 'gaze_one', responses[qid]['text1']),
                (gaze_two[qid], 'gaze_two', responses[qid]['text2'])]):
            ax = fig2.add_subplot(gs2[idx, col])
            ax.set_facecolor(PANBG)
            for sp in ax.spines.values():
                sp.set_edgecolor(border); sp.set_linewidth(1.5)
            if gpts:
                ts_a = np.array([g['unix_ts']  for g in gpts])
                ci_a = np.array([g['char_idx'] for g in gpts])
                tnorm   = (ts_a - ts_a.min()) / max(ts_a.max() - ts_a.min(), 1)
                elapsed = (ts_a - ts_global_min) / 1000.0
                ax.scatter(elapsed, ci_a, c=tnorm, cmap=CMAP,
                           s=14, alpha=0.8, vmin=0, vmax=1, linewidths=0, zorder=2)
                ax.plot(elapsed, ci_a, color='#333355', lw=0.5, alpha=0.5, zorder=1)
            ax.set_xlabel('Session elapsed time (s)', color='white', fontsize=8)
            ax.set_ylabel('Character index',          color='white', fontsize=8)
            ax.tick_params(colors='white', labelsize=7)
            ax.set_ylim(len(text), -0.5)
            ax.set_title(f'[{label}]  Response {idx+1}  (query {qid})  ·  {len(gpts)} fixations',
                         color=border, fontsize=8)
            ax.yaxis.grid(True, color='#222244', linewidth=0.5, zorder=0)
            ax.xaxis.grid(True, color='#222244', linewidth=0.5, zorder=0)
    out = task_dir + '/gaze_timeline.png'
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close(fig2)
    print(f'  Saved → {out}')

    # ── Figure 3: mouse trajectory ────────────────────────────────────────────
    fig3 = plt.figure(figsize=(9, sum(n_lines) * per_line_in + 1), facecolor=BG)
    fig3.suptitle(
        f'Mouse Trajectory  —  mouse_left (left)  ·  mouse_right (right)\n'
        f'User: {user_id}  ·  Task {task_id}  ·  '
        f'{total_left} events (mouse_left)  /  {total_right} events (mouse_right)  '
        f'across {n} responses',
        color='white', fontsize=14, fontweight='bold', y=1.0,
    )
    gs3 = gridspec.GridSpec(n, 2, figure=fig3,
                            left=0.01, right=0.99, top=0.985, bottom=0.005,
                            hspace=0.08, wspace=0.03, height_ratios=height_ratios)
    fig3.canvas.draw()
    pd3 = {}
    for idx, qid in enumerate(query_order):
        text1 = responses[qid]['text1']; text2 = responses[qid]['text2']
        ts_str = responses[qid]['ts']
        border = BORDERS[idx % len(BORDERS)]
        ax_left  = fig3.add_subplot(gs3[idx, 0])
        ax_right = fig3.add_subplot(gs3[idx, 1])
        _, _, ts2xy_left  = draw_gaze_panel(fig3, ax_left,  text1, ts_str,
                                            mouse_left[qid],  border, idx, qid, 'mouse_left')
        _, _, ts2xy_right = draw_gaze_panel(fig3, ax_right, text2, ts_str,
                                            mouse_right[qid], border, idx, qid, 'mouse_right')
        pd3[qid] = {'ax_left': ax_left, 'ax_right': ax_right,
                    'ts_to_xy_left': ts2xy_left, 'ts_to_xy_right': ts2xy_right}
    draw_cross_links(fig3, pd3, 'left', 'right')
    out = task_dir + '/mouse_trajectory.png'
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close(fig3)
    print(f'  Saved → {out}')

    # ── Figure 4: mouse timeline ──────────────────────────────────────────────
    fig4 = plt.figure(figsize=(14, sum(n_lines) * per_line_in * 0.5 + 1), facecolor=BG)
    fig4.suptitle(
        f'Character Index vs Session Elapsed Time  —  mouse_left (left)  ·  mouse_right (right)\n'
        f'User: {user_id}  ·  Task {task_id}',
        color='white', fontsize=14, fontweight='bold', y=1.0,
    )
    gs4 = gridspec.GridSpec(n, 2, figure=fig4,
                            left=0.09, right=0.98, top=0.97, bottom=0.03,
                            hspace=0.50, wspace=0.30, height_ratios=height_ratios)
    for idx, qid in enumerate(query_order):
        border = BORDERS[idx % len(BORDERS)]
        for col, (gpts, label, text) in enumerate([
                (mouse_left[qid],  'mouse_left',  responses[qid]['text1']),
                (mouse_right[qid], 'mouse_right', responses[qid]['text2'])]):
            ax = fig4.add_subplot(gs4[idx, col])
            ax.set_facecolor(PANBG)
            for sp in ax.spines.values():
                sp.set_edgecolor(border); sp.set_linewidth(1.5)
            if gpts:
                ts_a = np.array([g['unix_ts']  for g in gpts])
                ci_a = np.array([g['char_idx'] for g in gpts])
                tnorm   = (ts_a - ts_a.min()) / max(ts_a.max() - ts_a.min(), 1)
                elapsed = (ts_a - ts_global_min) / 1000.0
                ax.scatter(elapsed, ci_a, c=tnorm, cmap=CMAP,
                           s=14, alpha=0.8, vmin=0, vmax=1, linewidths=0, zorder=2)
                ax.plot(elapsed, ci_a, color='#333355', lw=0.5, alpha=0.5, zorder=1)
            ax.set_xlabel('Session elapsed time (s)', color='white', fontsize=8)
            ax.set_ylabel('Character index',          color='white', fontsize=8)
            ax.tick_params(colors='white', labelsize=7)
            ax.set_ylim(len(text), -0.5)
            ax.set_title(f'[{label}]  Response {idx+1}  (query {qid})  ·  {len(gpts)} events',
                         color=border, fontsize=8)
            ax.yaxis.grid(True, color='#222244', linewidth=0.5, zorder=0)
            ax.xaxis.grid(True, color='#222244', linewidth=0.5, zorder=0)
    out = task_dir + '/mouse_timeline.png'
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close(fig4)
    print(f'  Saved → {out}')


# ── Main: scan all user/task folders ──────────────────────────────────────────
processed = skipped = 0
for user_folder in sorted(os.listdir(ROOT)):
    user_dir = os.path.join(ROOT, user_folder)
    if not os.path.isdir(user_dir):
        continue
    for task_folder in sorted(os.listdir(user_dir)):
        task_dir = os.path.join(user_dir, task_folder)
        if not os.path.isdir(task_dir):
            continue
        if not REQUIRED.issubset(set(os.listdir(task_dir))):
            skipped += 1
            continue
        key = (user_folder, task_folder)
        responses = all_responses.get(key, {})
        if not responses:
            print(f'[SKIP] {user_folder}/{task_folder}: no query_logs entries')
            skipped += 1
            continue
        print(f'[Processing] {user_folder}/{task_folder}')
        process_task(user_folder, task_folder, task_dir, responses)
        processed += 1

print(f'\nDone. Processed {processed} task(s), skipped {skipped}.')
