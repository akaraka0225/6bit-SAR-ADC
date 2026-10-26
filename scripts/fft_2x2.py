"""2x2 FFT figure from Cadence spectrum tables (PRE -0.2 dB / POST -0.5 dB input, Peak Sat. Level 2.461).

Layout:  (a) PRE  low Fin  | (b) PRE  high Fin
         (c) POST low Fin  | (d) POST high Fin
- Spectrum is plotted exactly as exported from Cadence (DC bin dropped)
- SNDR/SFDR are typed in from Cadence Outputs (not computed here)
- ENOB = (SNDR - 1.76) / 6.02
Output: figures/10_fft_pre_post.png (17 cm wide, 300 dpi)
"""
import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(HERE, "..", "data", "fft")

# (label, csv file, Fin column tag, SNDR [dB], SFDR [dBc]) -- values from Cadence Outputs
PANELS = [
    ("(a)", "pre_98k_0.2dB.csv",  "98632.81", 37.82365, 50.68693),
    ("(b)", "pre_497k_0.2dB.csv", "497070.3", 37.802588, 51.086328),
    ("(c)", "post_98k.csv",  "98632.81", 37.232521, 55.05907),
    ("(d)", "post_497k.csv", "497070.3", 37.076661, 51.579274),
]

CM = 1 / 2.54
FIG_W, FIG_H = 17 * CM, 12 * CM
FS_TICK, FS_LABEL, FS_TXT = 6.5, 7, 7


def load(csv, fin):
    df = pd.read_csv(os.path.join(CSV_DIR, csv))
    col = next(c for c in df.columns[1:] if re.search(rf"Fin={re.escape(fin)}\b", c))
    return df.iloc[:, 0].to_numpy(float), df[col].to_numpy(float)


def draw_panel(ax, csv, fin, sndr, sfdr):
    f, db = load(csv, fin)
    ax.plot(f[1:] / 1e3, db[1:], color="#0000ff", lw=0.6)
    ax.set_xlim(0, 500); ax.set_ylim(-100, 5)
    ax.set_xticks(np.arange(0, 501, 50))
    ax.set_yticks(np.arange(-100, 1, 20))
    ax.tick_params(labelsize=FS_TICK, length=2, pad=1.5)
    ax.grid(True, ls=(0, (4, 4)), color="#c8c8c8", lw=0.4)
    ax.set_xlabel("(kHz)", fontsize=FS_LABEL, labelpad=1)
    ax.set_ylabel("(dB)", fontsize=FS_LABEL, labelpad=1)
    for s in ax.spines.values():
        s.set_color("#888888"); s.set_linewidth(0.6)
    lines =[f"Fin = {float(fin)/1e3:.3f}kHz @ 1MS/s"]
    if sndr is not None:
        lines += [f"SNDR = {sndr:.3f}dB", f"SFDR = {sfdr:.3f}dBc",
                  f"ENOB = {(sndr - 1.76) / 6.02:.3f} bits"]
    ax.text(0.27, 0.975, "\n".join(lines), transform=ax.transAxes, va="top", ha="left",
            fontsize=FS_TXT, fontweight="bold", linespacing=1.35)


def main():
    fig, axes = plt.subplots(2, 2, figsize=(FIG_W, FIG_H), dpi=300)
    for ax, (lab, csv, fin, sndr, sfdr) in zip(axes.flat, PANELS):
        draw_panel(ax, csv, fin, sndr, sfdr)
        ax.text(0.5, -0.24, lab, transform=ax.transAxes, ha="center", va="top",
                fontsize=FS_LABEL + 1)
    fig.tight_layout(h_pad=1.6, w_pad=1.2, rect=(0, 0, 1, 0.965))
    fig.text(0.01, 0.995, "1024 point FFT, fs = 1MHz", ha="left", va="top", fontsize=FS_LABEL + 1)
    fig.savefig(os.path.join(HERE, "..", "figures", "10_fft_pre_post.png"))
    plt.close(fig)


if __name__ == "__main__":
    main()
