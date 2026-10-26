"""Cadence에서 추출한 TG RON 테이블(CSV)을 vin-Ron 그래프로 출력."""
import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "TG_RON.csv"
OUT_PATH = HERE / "ron_vs_vin_sweep.png"

COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]

df = pd.read_csv(CSV_PATH)
df = df.sort_values("vin").reset_index(drop=True)  # Cadence 출력은 행 순서가 섞여 있음

fig, ax = plt.subplots(figsize=(9, 5.5), dpi=150)
for col, color in zip(df.columns[1:], COLORS):
    n = re.search(r'"N"\s*(\d+)', col).group(1)
    ax.plot(df["vin"], df[col], color=color, linewidth=2,
            solid_joinstyle="round", solid_capstyle="round", label=f"N = {n}")
    ax.annotate(f"N={n}", (df["vin"].iloc[-1], df[col].iloc[-1]),
                xytext=(6, 0), textcoords="offset points",
                va="center", fontsize=9, color="#52514e")

ax.set_xlabel("Vin [V]")
ax.set_ylabel("Ron [Ω]")
ax.set_title("Transmission Gate Ron vs Vin")
ax.set_xlim(df["vin"].min(), df["vin"].max())
ax.grid(True, color="#e5e4df", linewidth=0.8)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
ax.legend(frameon=False)
fig.tight_layout()

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT_PATH)
print(f"saved: {OUT_PATH}")
