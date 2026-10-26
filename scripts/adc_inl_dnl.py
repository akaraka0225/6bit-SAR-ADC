"""SAR ADC static linearity (DNL/INL) from Cadence ramp CSV (CORE_INL_DNL.csv).

Code-density (histogram) test, endpoint-corrected:
- VIN: 0 -> 5 V linear ramp, Fs = 1 MS/s; sample count from sim length (1.024 ms -> 16/code, 2.048 ms -> 32/code)
- vout = ideal DAC of output bits (code*5/64); sampled once per period after it settles
- End codes 0 and 63 are excluded (they absorb the out-of-range input)
- DNL(k) = H(k)/H_avg - 1,  H_avg = mean hits of codes 1..62
- INL(k) = sum_{j=1..k} DNL(j)   (endpoint fit -> INL(62) = 0)
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BLUE = "#0000ff"

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "data", "raw", "CORE_INL_DNL.csv")
DATA_DIR = os.path.join(HERE, "..", "data", "inl_dnl")
FIG_DIR = os.path.join(HERE, "..", "figures")

NBIT = 6
NCODE = 2 ** NBIT
VREF = 5.0
LSB = VREF / NCODE
FS = 1e6
T_SAMPLE = 0.97e-6   # sample point in each period, after vout settles (same as FFT script)


def get_codes():
    d = pd.read_csv(CSV)
    t, vout = d.iloc[:, 2].values, d.iloc[:, 3].values
    n = int(round(t[-1] * FS))                         # ramp length sets sample count (1.024 ms -> 1024)
    ts = T_SAMPLE + np.arange(n) / FS
    idx = np.searchsorted(t, ts, side="right") - 1      # zero-order hold value
    return np.round(vout[idx] / LSB).astype(int)


def dnl_inl(codes):
    H = np.bincount(codes, minlength=NCODE)
    h_in = H[1:NCODE - 1]
    h_avg = h_in.mean()
    dnl = h_in / h_avg - 1
    inl = np.cumsum(dnl)
    return H, h_avg, dnl, inl


def plot(k, y, ylabel, path):
    fig, ax = plt.subplots(figsize=(10, 3.6), dpi=150)
    ax.plot(k, y, color=BLUE, lw=1.2)
    ax.axhline(0, color="#888888", lw=0.6)
    ax.set_xlim(0, NCODE - 1); ax.set_xticks(np.arange(0, NCODE, 8))
    lim = max(0.5, np.ceil(np.abs(y).max() * 10 + 1) / 10)
    ax.set_ylim(-lim, lim)
    ax.tick_params(labelsize=8)
    ax.grid(True, ls=(0, (4, 4)), color="#c8c8c8", lw=0.6)
    ax.set_xlabel("Output Code", fontsize=9); ax.set_ylabel(ylabel, fontsize=9)
    for s in ax.spines.values():
        s.set_color("#888888")
    txt = f"{ylabel.split()[0]} = {y.min():+.3f} / {y.max():+.3f} LSB"
    ax.text(0.98, 0.96, txt, transform=ax.transAxes, va="top", ha="right",
            fontsize=12, fontweight="bold")
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def plot_stack(k, dnl, inl, path):
    fig, axes = plt.subplots(2, 1, figsize=(6, 5), dpi=200)
    for ax, y, name in zip(axes, (dnl, inl), ("DNL", "INL")):
        ax.plot(k, y, color=BLUE, lw=1.2)
        ax.axhline(0, color="#888888", lw=0.6)
        ax.set_xlim(0, NCODE); ax.set_xticks(np.arange(0, NCODE + 1, 8))
        ax.set_ylim(-1, 1); ax.set_yticks(np.arange(-1, 1.01, 0.5))
        ax.tick_params(labelsize=8)
        ax.grid(True, ls=(0, (4, 4)), color="#c8c8c8", lw=0.6)
        ax.set_xlabel("CODE", fontsize=8, fontweight="bold")
        ax.set_ylabel(f"{name} [LSB]", fontsize=8, fontweight="bold")
        for sp in ax.spines.values():
            sp.set_color("#888888")
        ax.set_title(f"{name} = {y.min():+.2f} / {y.max():+.2f} LSB", loc="left",
                     fontsize=10, fontweight="bold")
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


if __name__ == "__main__":
    codes = get_codes()
    tag = f"_{len(codes) // NCODE}hits"                 # e.g. _16hits, _32hits
    H, h_avg, dnl, inl = dnl_inl(codes)
    k = np.arange(1, NCODE - 1)
    print("hits per code:", H.tolist())
    print(f"H(0)={H[0]}, H(63)={H[-1]}, H_avg(1..62)={h_avg:.4f}, missing={np.where(H == 0)[0].tolist()}")
    print(f"DNL: {dnl.min():+.4f} / {dnl.max():+.4f} LSB  (min @ code {k[dnl.argmin()]}, max @ {k[dnl.argmax()]})")
    print(f"INL: {inl.min():+.4f} / {inl.max():+.4f} LSB  (min @ code {k[inl.argmin()]}, max @ {k[inl.argmax()]})")
    # gain/offset from the same histogram (transition levels relative to ideal, truncation convention)
    T = np.cumsum(H)[:-1] * VREF / len(codes)                     # T(k) = input level where code k starts, k=1..63
    print(f"T1 = {T[0]*1e3:.2f} mV (ideal {LSB*1e3:.2f}),  T63 = {T[-1]:.4f} V (ideal {63*LSB:.4f})")
    print(f"T1 shift = {(T[0]-LSB)/LSB:+.3f} LSB, T32 shift (mid-scale offset) = {(T[31]-32*LSB)/LSB:+.3f} LSB, "
          f"T63 shift = {(T[-1]-63*LSB)/LSB:+.3f} LSB")
    print(f"gain = 62 LSB / (T63-T1) = {62*LSB/(T[-1]-T[0]):.4f}")
    pd.DataFrame({"code": k, "hits": H[1:-1], "DNL_LSB": dnl, "INL_LSB": inl}).to_csv(
        os.path.join(DATA_DIR, f"inl_dnl_table{tag}.csv"), index=False)
    plot(k, dnl, "DNL (LSB)", os.path.join(FIG_DIR, f"DNL{tag}.png"))
    plot(k, inl, "INL (LSB)", os.path.join(FIG_DIR, f"INL{tag}.png"))
    plot_stack(k, dnl, inl, os.path.join(FIG_DIR, f"DNL_INL{tag}.png"))
