#!/usr/bin/env python3
"""Controlled simulation (C2 coverage check + C3 mechanism map).

Synthetic DGP with known ground truth validates the frozen planner
(FREEZE_PROPOSAL_v0.3): Bonferroni-corrected paired-bootstrap certificates,
looks T in {10,30,50,70,90}, alpha=0.1.

Selection arm: M policies, best has population advantage `gap` over the rest;
per-query noise sigma. Wrong certificate = ACT on a policy whose true regret
exceeds eps_sel. Mechanism claim: stopping budget scales with gap and M,
not with the decision's name.

Recalibration arm: audited query i yields ratio observation c_i = c_T*exp(eta),
eta ~ N(0, s); utility loss is curvature*|log(c_hat/c_T)| (monotone proxy).
Budget scales with dispersion s and eps_cal only — independent of M and gap.

Seeds are explicit; no Date/random ambient state.
"""
import json, os
import numpy as np

HUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HUB, "05_results", "simulation")
os.makedirs(OUT, exist_ok=True)

ALPHA = 0.10
EPS_SEL = 0.01
EPS_CAL = 0.005
LOOKS = [10, 30, 50, 70, 90]
BOOT = 400
REPS = 200
N_POP = 20000

GAPS = [0.0, 0.005, 0.01, 0.02, 0.05, 0.10]
MENUS = [2, 3, 5]
SIGMAS = [0.10, 0.20]


def selection_cell(gap, M, sigma, reps=REPS, seed0=0):
    aprime = ALPHA / (len(LOOKS) * (M - 1))
    rows = []
    for rep in range(reps):
        rng = np.random.default_rng(
            1_000_000 + hash_free_seed(gap, M, sigma, rep))
        base = rng.beta(2.0, 4.0, N_POP)
        delta = np.r_[0.0, np.full(M - 1, -gap)]
        u = np.clip(base[:, None] + delta[None, :]
                    + rng.normal(0, sigma, (N_POP, M)), 0, 1)
        mu = u.mean(axis=0)
        true_best = mu.max()
        perm = rng.permutation(N_POP)
        action, T_act, pick = "abstain", LOOKS[-1], None
        for T in LOOKS:
            s = u[perm[:T]]
            bs = rng.integers(0, T, (BOOT, T))
            bmeans = s[bs].mean(axis=1)              # (BOOT, M)
            means = s.mean(axis=0)
            se = s.std(axis=0, ddof=1) / np.sqrt(T)
            cand = int(np.argmax(means - se))
            diffs = bmeans - bmeans[:, [cand]]        # bootstrap of mu_j - mu_cand
            ucb = np.quantile(diffs, 1 - aprime, axis=0)
            ucb[cand] = -np.inf
            if ucb.max() <= EPS_SEL:
                action, T_act, pick = "act", T, cand
                break
        true_regret = float(true_best - mu[pick]) if pick is not None else None
        rows.append(dict(gap=gap, M=M, sigma=sigma, rep=rep, action=action,
                         T=T_act, pick=pick, true_regret=true_regret,
                         wrong_cert=(action == "act" and true_regret > EPS_SEL)))
    return rows


def recal_cell(s_disp, curvature=0.02, reps=REPS):
    rows = []
    for rep in range(reps):
        rng = np.random.default_rng(9_000_000 + int(s_disp * 1000) * 10_000 + rep)
        c_T = 1.0
        action, T_act, loss = "abstain", LOOKS[-1], None
        for T in LOOKS:
            obs = c_T * np.exp(rng.normal(0, s_disp, T))
            c_hat = float(np.median(obs))
            bs = rng.integers(0, T, (BOOT, T))
            bmed = np.median(obs[bs], axis=1)
            a_look = ALPHA / len(LOOKS)   # Bonferroni over looks (sim-selected)
            c_lo, c_hi = np.quantile(bmed, [a_look / 2, 1 - a_look / 2])
            u_spread = curvature * max(abs(np.log(c_lo / c_hat)),
                                       abs(np.log(c_hi / c_hat)))
            if u_spread <= EPS_CAL:
                action, T_act = "act", T
                loss = curvature * abs(np.log(c_hat / c_T))
                break
        rows.append(dict(s=s_disp, rep=rep, action=action, T=T_act,
                         true_loss=loss,
                         wrong_cert=(action == "act" and loss > EPS_CAL)))
    return rows


def hash_free_seed(gap, M, sigma, rep):
    return (int(gap * 10000) * 1_000 + M * 101 + int(sigma * 100)) * 1000 + rep


def main():
    import pandas as pd
    sel_rows = []
    for gap in GAPS:
        for M in MENUS:
            for sigma in SIGMAS:
                sel_rows += selection_cell(gap, M, sigma)
        print(f"gap={gap} done", flush=True)
    sel = pd.DataFrame(sel_rows)
    sel.to_parquet(os.path.join(OUT, "selection_sim.parquet"), index=False)

    cal_rows = []
    for s in [0.3, 0.5, 1.0]:
        cal_rows += recal_cell(s)
    cal = pd.DataFrame(cal_rows)
    cal.to_parquet(os.path.join(OUT, "recal_sim.parquet"), index=False)

    g = sel.groupby(["gap", "M", "sigma"], as_index=False).agg(
        act_rate=("action", lambda a: float((a == "act").mean())),
        abstain_rate=("action", lambda a: float((a == "abstain").mean())),
        mean_T=("T", "mean"),
        wrong_cert_rate=("wrong_cert", "mean"))
    g.to_csv(os.path.join(OUT, "selection_summary.csv"), index=False)
    gc = cal.groupby("s", as_index=False).agg(
        act_rate=("action", lambda a: float((a == "act").mean())),
        mean_T=("T", "mean"), wrong_cert_rate=("wrong_cert", "mean"))
    gc.to_csv(os.path.join(OUT, "recal_summary.csv"), index=False)

    headline = dict(
        alpha=ALPHA,
        max_wrong_cert_rate_selection=float(g["wrong_cert_rate"].max()),
        wrong_cert_by_cell_ok=bool((g["wrong_cert_rate"] <= ALPHA).all()),
        abstain_rate_at_zero_gap=float(
            g.query("gap == 0")["abstain_rate"].mean()),
        mean_T_large_gap=float(g.query("gap >= 0.05")["mean_T"].mean()),
        mean_T_small_gap=float(
            g.query("gap > 0 and gap <= 0.01")["mean_T"].mean()),
        recal=gc.to_dict("records"))
    json.dump(headline, open(os.path.join(OUT, "sim_headline.json"), "w"),
              indent=2)
    print(json.dumps(headline, indent=2))
    print(g.to_string(index=False))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))
    for M, sub in g[g.sigma == 0.10].groupby("M"):
        axes[0].plot(sub["gap"], sub["mean_T"], marker="o", label=f"M={M}")
        axes[1].plot(sub["gap"], sub["abstain_rate"], marker="o", label=f"M={M}")
        axes[2].plot(sub["gap"], sub["wrong_cert_rate"], marker="o", label=f"M={M}")
    axes[0].set_ylabel("mean audited queries at stop")
    axes[0].set_title("Budget vs policy gap (σ=0.1)")
    axes[1].set_ylabel("abstain rate")
    axes[1].set_title("Abstention vs gap")
    axes[2].axhline(ALPHA, color="#333", ls=":", lw=1)
    axes[2].set_ylabel("wrong-certificate rate")
    axes[2].set_title(f"Risk control (nominal α={ALPHA})")
    for ax in axes:
        ax.set_xlabel("true policy gap")
        ax.grid(alpha=0.25)
        ax.legend(fontsize=9)
    fig.suptitle("F3 — Mechanism: selection budget is driven by gap × menu size; "
                 "wrong-certificate rate stays below α", fontsize=12)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "F3_mechanism_map.png"), dpi=160)
    print(f"[saved] {OUT}")


if __name__ == "__main__":
    main()
