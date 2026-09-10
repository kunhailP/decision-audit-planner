#!/usr/bin/env python3
"""F4: PPI effective-sample-size gain vs decision-relevant agreement rho."""
import glob, os
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

HUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root = os.path.join(HUB, "05_results", "ppi_gain")
fs = glob.glob(os.path.join(root, "ppi_gain_*.csv"))
df = pd.concat([pd.read_csv(f).assign(pool=os.path.basename(f).split("_")[2]) for f in fs])
d = df[df["T"] == 10]
fig, ax = plt.subplots(figsize=(6.5, 4.5))
for (st, jd), mk, col in [(("legacy", "rr"), "o", "C0"), (("modern", "rr"), "s", "C1"),
                          (("trecdl", "rr"), "^", "C2"), (("trecdl", "llm"), "*", "C3")]:
    s = d[(d["pool"] == st) & (d["judge"] == jd)]
    lab = {"rr": "Qwen3-Reranker judge", "llm": "Qwen3-8B LLM judge"}[jd]
    ax.scatter(s["rho"], s["ess_gain"], marker=mk, s=70 if mk == "*" else 55, alpha=.85, edgecolors="k",
               linewidths=.5, c=col, label=f"{st} pools, {lab} (n={len(s)})")
r = np.linspace(-0.3, 0.8, 200); ax.plot(r, 1 / (1 - r ** 2), "k--", lw=1, label="1/(1−ρ²)")
ax.set_xlabel("ρ = corr(true paired difference, judge paired difference)")
ax.set_ylabel("PPI effective-sample-size gain at T=10")
ax.set_title("PPI gain follows decision-relevant agreement ρ, not judge accuracy")
ax.grid(alpha=.25); ax.legend(fontsize=8); fig.tight_layout()
fig.savefig(os.path.join(root, "F4_gain_vs_rho.png"), dpi=160)
for st, g in d.groupby(["pool", "judge"]):
    print(f"{st:8} n={len(g):2d} corr(gain,rho)={np.corrcoef(g['rho'], g['ess_gain'])[0,1]:.3f} "
          f"corr(gain,acc)={np.corrcoef(g['judge_acc'], g['ess_gain'])[0,1]:.3f}")
print(f"all      n={len(d):2d} corr(gain,rho)={np.corrcoef(d['rho'], d['ess_gain'])[0,1]:.3f} "
      f"corr(gain,acc)={np.corrcoef(d['judge_acc'], d['ess_gain'])[0,1]:.3f}")
