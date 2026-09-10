#!/usr/bin/env python3
"""F5: cumulative ACT rate vs audit budget T for valid certificates, by judge (dbpedia-entity, 500 repeats)."""
import os, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

HUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
coll = sys.argv[1] if len(sys.argv) > 1 else "dbpedia-entity"
looks = [10, 30, 50, 70, 90, 120, 150, 190]
fig, ax = plt.subplots(figsize=(6.5, 4.4))
styles = {"rr": ("Qwen3-Reranker judge", "C1"), "llm": ("Qwen3-8B LLM judge", "C3"), "mpnet": ("MPNet rank judge (other family)", "C4"), "inv": ("inverted reranker (adversarial)", "C7")}
for j, (lab, col) in styles.items():
    fp = os.path.join(HUB, "05_results", "planner_v2", f"judged_{j}_ext", "planner_v2.parquet")
    if not os.path.exists(fp):
        continue
    d = pd.read_parquet(fp); d = d[d.collection == coll]
    for m, ls in [("split_ppi", "-"), ("split_t", "--")]:
        s = d[d.method == m]; acts = s[s.action == "act"]; n = len(s)
        curve = [(acts.final_T <= T).sum() / n for T in looks]
        wrong = int(s.wrong_cert.sum())
        if m == "split_t" and j != "rr":
            continue   # human-only curve is judge-independent; draw once
        ax.plot(looks, curve, ls, marker="o", ms=4, color="k" if m == "split_t" else col,
                label=("humans only (split_t)" if m == "split_t" else f"split_ppi, {lab}") + f"  [wrong {wrong}/{n}]")
ax.set_xlabel("audited queries T (looks)"); ax.set_ylabel("cumulative ACT rate (500 repeats)")
ax.set_title(f"{coll}: valid ε-regret certificates vs budget, α=0.1, ε=0.01"); ax.grid(alpha=.25); ax.legend(fontsize=7.5)
fig.tight_layout(); out = os.path.join(HUB, "05_results", "planner_v2", f"F5_act_vs_budget_{coll}.png"); fig.savefig(out, dpi=160); print("saved", out)
