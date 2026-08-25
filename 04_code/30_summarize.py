#!/usr/bin/env python3
"""C1 diagnostic summary: decision-specific success curves from row-level data.

Reads 05_results/budget_curves/per_repeat.parquet (never aggregates by hand),
computes per (collection, k, decision) success rates with Monte Carlo standard
errors, the smallest grid k reaching a target success rate per decision, and
renders figure F1. All numbers are regenerated from stored rows.
"""
import json, os
import numpy as np
import pandas as pd

HUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN_DIR = os.path.join(HUB, "05_results", "budget_curves")
EPS_CAL = 0.005
EPS_SEL = 0.01
TARGET_RATE = 0.9

df = pd.read_parquet(os.path.join(IN_DIR, "per_repeat.parquet"))
df["cal_ok"] = df["cal_loss"] <= EPS_CAL
df["sel_ok"] = df["regret3"] <= EPS_SEL

g = df.groupby(["collection", "untouched", "k_requested", "k_effective", "clipped"],
               as_index=False).agg(
    n=("repeat_id", "size"),
    cal_rate=("cal_ok", "mean"), sel_rate=("sel_ok", "mean"),
    cal_loss_mean=("cal_loss", "mean"), regret_mean=("regret3", "mean"),
    regret_p90=("regret3", lambda s: float(np.quantile(s, 0.9))),
    param_err=("c_hat", lambda s: np.nan))
g["cal_se"] = np.sqrt(g["cal_rate"] * (1 - g["cal_rate"]) / g["n"])
g["sel_se"] = np.sqrt(g["sel_rate"] * (1 - g["sel_rate"]) / g["n"])
g = g.drop(columns=["param_err"])
g.to_csv(os.path.join(IN_DIR, "summary_by_collection_k.csv"), index=False)

# smallest grid k whose success rate >= TARGET_RATE, per decision
rows = []
for coll, sub in g.groupby("collection"):
    sub = sub.sort_values("k_requested")
    unclipped = sub[~sub["clipped"]]
    def first_k(col):
        hit = sub[sub[col] >= TARGET_RATE]
        return int(hit["k_requested"].iloc[0]) if len(hit) else None
    rows.append(dict(collection=coll,
                     untouched=bool(sub["untouched"].iloc[0]),
                     k_star_cal=first_k("cal_rate"),
                     k_star_sel=first_k("sel_rate"),
                     max_k_effective=int(sub["k_effective"].max())))
ks = pd.DataFrame(rows).sort_values(["untouched", "collection"])
ks.to_csv(os.path.join(IN_DIR, "budget_gap_by_collection.csv"), index=False)

# pooled success curves (mean over 13 collections at each k)
pooled = g.groupby("k_requested", as_index=False).agg(
    cal_rate=("cal_rate", "mean"), sel_rate=("sel_rate", "mean"))

summary = dict(
    eps_cal=EPS_CAL, eps_sel=EPS_SEL, target_rate=TARGET_RATE,
    repeats=int(df["repeat_id"].max()) + 1,
    collections=int(df["collection"].nunique()),
    pooled_curves=pooled.to_dict("records"),
    budget_gap=ks.to_dict("records"),
    headline=dict(
        n_collections_cal_ok_at_k10=int((g.query("k_requested==10")["cal_rate"] >= TARGET_RATE).sum()),
        n_collections_sel_ok_at_k10=int((g.query("k_requested==10")["sel_rate"] >= TARGET_RATE).sum()),
        n_collections_sel_ok_at_k100=int((g.query("k_requested==100")["sel_rate"] >= TARGET_RATE).sum()),
    ))
json.dump(summary, open(os.path.join(IN_DIR, "c1_summary.json"), "w"), indent=2)
print(json.dumps(summary["headline"], indent=2))
print(ks.to_string(index=False))

# ---- Figure F1 ----
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
kx = sorted(df["k_requested"].unique())
for coll, sub in g.groupby("collection"):
    sub = sub.sort_values("k_requested")
    style = dict(color="#c44" if sub["untouched"].iloc[0] else "#888",
                 alpha=0.75, lw=1.2)
    axes[0].plot(sub["k_requested"], sub["cal_rate"], **style)
    axes[1].plot(sub["k_requested"], sub["sel_rate"], **style)
for ax, col, title in [(axes[0], "cal_rate", f"Recalibration: P(|Δutility| ≤ {EPS_CAL})"),
                       (axes[1], "sel_rate", f"Selection: P(regret ≤ {EPS_SEL})")]:
    p = g.groupby("k_requested", as_index=False)[col].mean().sort_values("k_requested")
    ax.plot(p["k_requested"], p[col], color="#06c", lw=3, marker="o",
            label="mean over 13 collections")
    ax.axhline(TARGET_RATE, color="#333", ls=":", lw=1)
    ax.set_xscale("log")
    ax.set_xticks(kx)
    ax.set_xticklabels([str(k) for k in kx])
    ax.set_xlabel("audited target queries k (requested)")
    ax.set_title(title, fontsize=11)
    ax.grid(alpha=0.25)
axes[0].set_ylabel("success rate over repeats")
axes[0].legend(loc="lower right", fontsize=9)
fig.suptitle("F1 — Same audit sample, different decisions: success vs budget "
             "(red = untouched-4, grey = development-9)", fontsize=12)
fig.tight_layout()
fig.savefig(os.path.join(IN_DIR, "F1_budget_curves.png"), dpi=160)
print(f"[saved] {IN_DIR}/F1_budget_curves.png")
