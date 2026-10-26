"""TG on-resistance vs. V_in — single-column figure for a two-column paper.

Conceptual (textbook-style) sketch, not simulation data:
  - R_on,N rises toward V_DD - V_TH, R_on,P rises toward |V_THP|
  - R_on,eq = R_on,N || R_on,P is computed exactly, so it always sits below
    both device curves and peaks where they cross (R_on,eq = R/2 there).

Outputs two versions:
  Ron_review.*  colour (R_on,eq in red)        — 심사용
  Ron_submit.*  monochrome (print-safe)        — 투고용
"""
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "font.size": 9,
    "axes.linewidth": 0.9,
    "savefig.dpi": 600,
})

VDD = 1.0                          # normalized axis
v_thp, v_thn = 0.12, 0.88          # |V_THP| and V_DD - V_TH markers
V_C = 0.5                          # crossing point
YMAX = 1.0
R_C = 0.42                         # R_on,N = R_on,P at the crossing
TAU = (V_C - v_thp) / np.log(YMAX / R_C)   # each curve leaves the top at its marker

vin = np.linspace(0, VDD, 4001)
rn = R_C * np.exp((vin - V_C) / TAU)
rp = R_C * np.exp((V_C - vin) / TAU)
req = rn * rp / (rn + rp)

def draw(eq_color, eq_lw, dev_color, name):
    fig, ax = plt.subplots(figsize=(3.4, 2.1))
    ax.plot(vin, rp, color=dev_color, lw=1.1)
    ax.plot(vin, rn, color=dev_color, lw=1.1)
    ax.plot(vin, req, color=eq_color, lw=eq_lw, zorder=3)
    for v in (v_thp, v_thn):
        ax.axvline(v, color="black", lw=0.7, ls=(0, (1.5, 2)), zorder=0)

    ax.set_xlim(0, VDD * 1.04)
    ax.set_ylim(0, YMAX)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.plot(1, 0, ">k", transform=ax.transAxes, clip_on=False, ms=4)
    ax.plot(0, 1, "^k", transform=ax.transAxes, clip_on=False, ms=4)
    ax.set_yticks([])
    ax.set_xticks([v_thp, v_thn])
    ax.set_xticklabels([r"$|V_{\mathrm{THP}}|$", r"$V_{\mathrm{DD}}-V_{\mathrm{TH}}$"])
    ax.tick_params(axis="x", length=0, pad=4)
    ax.text(1.03, 0, r"$V_{\mathrm{in}}$", transform=ax.transAxes,
            ha="left", va="center")
    ax.text(0, 1.05, r"$R_{\mathrm{on}}$", transform=ax.transAxes,
            ha="center", va="bottom")

    # Curve labels at the top, between the two device curves
    y_lab = YMAX * 0.86
    x_p = vin[np.argmax(rp < y_lab)]
    x_n = vin[np.argmax(rn > y_lab)]
    ax.text(x_p + 0.015 * VDD, y_lab, r"$R_{\mathrm{on,P}}$", ha="left", va="center")
    ax.text(x_n - 0.015 * VDD, y_lab, r"$R_{\mathrm{on,N}}$", ha="right", va="center")
    x_e = 0.5 * (v_thp + v_thn) + 0.06 * VDD
    ax.text(x_e, req[np.searchsorted(vin, x_e)] - YMAX * 0.05,
            r"$R_{\mathrm{on,eq}}$", color=eq_color, ha="center", va="top")

    fig.tight_layout(pad=0.3)
    out = Path(__file__).resolve().parent.parent / "figures" / name
    for ext in ("pdf", "svg", "png"):
        fig.savefig(out.with_suffix(f".{ext}"), bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


draw("#d62020", 1.6, "black", "Ron_review")
draw("black", 2.0, "0.45", "Ron_submit")
print("done")
