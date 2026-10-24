#!/usr/bin/env python3
"""Digitize the 原道十周年 (Yuandao 10th Anniversary) frequency response.

Source chart: the PNG in source/, a published comparison chart showing
原道十周年 against MX500 (B&K 5128). Published by 哔哩哔哩 UP主 "油兔几".

Three comparison charts were used in total. This script uses the MX500 one
because the comparison curve is teal and therefore never blends into the
black stroke. The other two gave the same shape to within 0.04 dB RMS after
1 kHz normalization (see README).

Axis calibration by least squares over every gridline in the image:
  x = -501.624 + 437.714 * log10(f)   (rms residual 0.33 px)
  y = 1400.364 - 11.691 * dB          (rms residual 0.47 px)

Usage:
    python digitize.py 24oct > data/Yuandao-10th_1-24oct.csv
    python digitize.py raw   > data/Yuandao-10th_raw.csv

The script writes CSV to stdout and never opens a file for writing; redirect
where you want it. The only file it reads is the fixed chart under source/.
"""
import os
import sys

import numpy as np
from PIL import Image

A_X, B_X = -501.624, 437.714
A_Y, B_Y = 1400.364, -11.691

X_LO, X_HI = 68, 1376
Y_TOP, Y_BOT = 39, 693

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def chart_path():
    """Resolve source/chart.png, refusing anything that escapes the repo."""
    joined = os.path.normpath(os.path.join(BASE_DIR, 'source', 'chart.png'))
    if os.path.commonpath([joined, BASE_DIR]) != BASE_DIR:
        raise ValueError(f'refusing path outside the repository: {joined!r}')
    return joined


def f_of(x):
    return 10 ** ((x - A_X) / B_X)


def db_of(y):
    return (y - A_Y) / B_Y


def load_trace():
    a = np.asarray(Image.open(chart_path()).convert('RGB')).astype(int)
    mx = a.max(axis=2)
    sat = mx - a.min(axis=2)
    # neutral black stroke; the teal comparison curve is chromatic
    black = (mx < 150) & (sat < 45)
    black[:Y_TOP + 1, :] = False
    black[Y_BOT:, :] = False
    black[:, :X_LO] = False
    black[:, X_HI + 1:] = False

    def runs_of(col):
        ys = np.nonzero(black[:, col])[0]
        if len(ys) == 0:
            return []
        out, s, p = [], ys[0], ys[0]
        for y in ys[1:]:
            if y - p <= 2:
                p = y
            else:
                out.append((s, p))
                s = p = y
        out.append((s, p))
        # strokes are ~3 px on flats, up to ~15 px on the steep roll-off;
        # caption glyphs are taller and are rejected by continuity too
        return [(s + e) / 2.0 for s, e in out if (e - s) <= 20]

    xs, ys = [], []
    prev = 570.0                     # ~71 dB at the 20 Hz end
    for x in range(X_LO, X_HI + 1):
        cands = runs_of(x)
        if not cands:
            continue
        best = min(cands, key=lambda v: abs(v - prev))
        if abs(best - prev) > 30.0:
            continue
        xs.append(x)
        ys.append(best)
        prev = best
    xs = np.array(xs, dtype=float)
    ys = np.array(ys, dtype=float)

    keep = np.ones(len(xs), bool)
    for i in range(1, len(xs) - 1):
        if xs[i] - xs[i - 1] == 1 and xs[i + 1] - xs[i] == 1:
            if abs(ys[i] - 0.5 * (ys[i - 1] + ys[i + 1])) > 6:
                keep[i] = False
    xs, ys = xs[keep], ys[keep]

    def medfilt(v, k=3):
        h = k // 2
        return np.array([np.median(v[max(0, i - h):i + h + 1])
                         for i in range(len(v))])

    smoothed = np.convolve(np.pad(medfilt(ys, 3), 2, mode='edge'),
                           np.ones(5) / 5, mode='valid')
    xfull = np.arange(X_LO, X_HI + 1)
    return xfull, np.clip(np.interp(xfull, xs, smoothed), Y_TOP, Y_BOT)


def emit(freqs, levels):
    out = sys.stdout
    out.write('frequency,spl\n')
    for a, b in zip(freqs, levels):
        out.write(f'{a:.2f},{b:.2f}\n')


def main(mode):
    px, py = load_trace()
    f_raw, db_raw = f_of(px), db_of(py)
    keep = f_raw >= 20.0
    f_raw, db_raw = f_raw[keep], db_raw[keep]

    if mode == 'raw':
        emit(f_raw, db_raw)
        return

    # the chart's right edge is labelled 19.5 kHz, so stop below 20 kHz
    octaves = np.arange(np.log2(20.0), np.log2(f_raw.max()) + 1e-9, 1.0 / 24.0)
    f_24 = 2.0 ** octaves
    emit(f_24, np.interp(f_24, f_raw, db_raw))


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in ('24oct', 'raw'):
        sys.exit('usage: python digitize.py {24oct|raw} > out.csv')
    main(sys.argv[1])
