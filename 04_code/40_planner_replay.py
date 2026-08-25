#!/usr/bin/env python3
"""Sequential Decision-Specific Audit Planner — development-data replay (C2).

Implements FREEZE_PROPOSAL_v0.3: looks T in {10,30,50,70,90} (capped at n/2),
alpha=0.1, Bonferroni-corrected paired-bootstrap certificates, outputs
act / collect-more / abstain per decision. Replayed over the 13 development
collections (retrospective; D-007 — not confirmatory).

True losses are computed on the never-audited complement of the final audit
set. Wrong certificate = ACT whose true loss exceeds the frozen tolerance.
Reuses the exact LODO fold construction from 20_budget_curves.py via importlib.
"""
import importlib.util, json, os, zlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
HUB = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location(
    "bc", os.path.join(HERE, "20_budget_curves.py"))
bc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bc)

ALPHA = 0.10
EPS_CAL = 0.005
EPS_SEL = 0.01
LOOKS = [10, 30, 50, 70, 90]
BOOT = 400
REPS = 50
OUT = os.path.join(HUB, "05_results", "planner_replay")
os.makedirs(OUT, exist_ok=True)


def u_gate_mean(structs, c):
    return float(np.mean([bc.f1_at_k(s["cumtp"],
                                     bc.gate_k(s["sp"], s["cump"], c * s["Sp"]),
                                     s["nG"]) for s in structs]))


def policy_utils(structs, c_hat, tau_i):
    """Per-query utilities for the frozen menu given current probe estimates."""
    ad = np.array([bc.f1_at_k(s["cumtp"],
                              bc.gate_k(s["sp"], s["cump"], c_hat * s["Sp"]),
                              s["nG"]) for s in structs])
    gl = np.array([float(s["f_tau"][tau_i]) for s in structs])
    tr = np.array([s["f_trunc"] for s in structs])
    return dict(ad_probe=ad, glob_probe=gl, trunc=tr)


def policy_utils_crossfit(probe):
    """Leave-one-out cross-fitted per-query utilities (METHOD_SPEC v0.2).

    For probe query i, ad_probe uses c estimated on probe\\{i} and glob_probe
    uses tau tuned on probe\\{i}. Without this, in-sample certificates are
    anticonservative (observed: scifact selection wrong-cert 0.36 > alpha,
    preserved in 05_results/planner_replay_insample_ablation/)."""
    n = len(probe)
    ratios = np.array([s["nG"] / s["Sp"] if s["Sp"] > 0 else np.nan for s in probe])
    F = np.stack([s["f_tau"] for s in probe])          # (n, n_taus)
    colsum = F.sum(axis=0)
    ad = np.empty(n); gl = np.empty(n)
    for i, s in enumerate(probe):
        others = np.delete(ratios, i)
        others = others[~np.isnan(others)]
        c_loo = float(np.median(others)) if len(others) else 1.0
        ad[i] = bc.f1_at_k(s["cumtp"],
                           bc.gate_k(s["sp"], s["cump"], c_loo * s["Sp"]),
                           s["nG"])
        gl[i] = float(s["f_tau"][int(np.argmax(colsum - F[i]))])
    tr = np.array([s["f_trunc"] for s in probe])
    return dict(ad_probe=ad, glob_probe=gl, trunc=tr)


def main():
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.ensemble import HistGradientBoostingRegressor
    import pandas as pd

    source = "/root/shift-study"
    data = bc.load(os.path.join(source, "runs", "candidates"))
    avail = list(data)
    rng_global = np.random.default_rng(0)
    rows = []
    menu_names = ["glob_probe", "trunc", "ad_probe"]
    a_sel = ALPHA / (len(LOOKS) * (len(menu_names) - 1))
    a_cal = ALPHA / len(LOOKS)

    for held in avail:
        tr_idx = [d for d in avail if d != held]
        Xtr = np.concatenate([data[d]["X"] for d in tr_idx])
        ytr = np.concatenate([data[d]["rel"] for d in tr_idx])
        if len(Xtr) > bc.MAX_TRAIN:
            idx = rng_global.choice(len(Xtr), bc.MAX_TRAIN, replace=False)
            Xtr, ytr = Xtr[idx], ytr[idx]
        sc = StandardScaler().fit(Xtr)
        clf = CalibratedClassifierCV(LogisticRegression(max_iter=2000),
                                     method="sigmoid", cv=3
                                     ).fit(sc.transform(Xtr), ytr)
        structs = {d: bc.build_structs(data, d,
                   clf.predict_proba(sc.transform(data[d]["X"]))[:, 1])
                   for d in avail}
        tau_scores = np.zeros(len(bc.TAUS)); n_tr_q = 0
        Xk, yk = [], []
        for d in tr_idx:
            for s in structs[d]:
                for ti in range(len(bc.TAUS)):
                    tau_scores[ti] += bc.f1_at_k(s["cumtp"], int(s["tau_ks"][ti]), s["nG"])
                n_tr_q += 1
                Xk.append(s["feat"]); yk.append(s["k_star"])
        tau_transfer_i = int(np.argmax(tau_scores / n_tr_q))
        reg = HistGradientBoostingRegressor(random_state=0).fit(
            np.asarray(Xk), np.asarray(yk))
        H = structs[held]
        k_trunc = np.clip(np.round(reg.predict(np.asarray([s["feat"] for s in H]))),
                          1, [len(s["sp"]) for s in H]).astype(int)
        c_star = float(np.median([s["nG"] / s["Sp"] for s in H if s["Sp"] > 0]))
        for s, kt in zip(H, k_trunc):
            s["f_adc"] = bc.f1_at_k(s["cumtp"],
                                    bc.gate_k(s["sp"], s["cump"], c_star * s["Sp"]),
                                    s["nG"])
            s["f_trunc"] = bc.f1_at_k(s["cumtp"], int(kt), s["nG"])
            s["f_tau"] = np.array([bc.f1_at_k(s["cumtp"], int(s["tau_ks"][ti]), s["nG"])
                                   for ti in range(len(bc.TAUS))])
        cap = len(H) // 2
        looks = [t for t in LOOKS if t <= cap] or [cap]
        salt = zlib.crc32(f"planner|{held}".encode()) % 100_000

        for rep in range(REPS):
            rng = np.random.default_rng(5_000_000 + 1000 * rep + salt)
            perm = rng.permutation(len(H))
            state = {"recalibration": None, "selection": None}  # (action, T, payload)
            for T in looks:
                probe = [H[i] for i in perm[:T]]
                ratios = np.array([s["nG"] / s["Sp"] for s in probe if s["Sp"] > 0])
                c_hat = float(np.median(ratios))
                tau_i = int(np.argmax(np.mean([s["f_tau"] for s in probe], axis=0)))
                # --- recalibration certificate ---
                if state["recalibration"] is None:
                    bs = rng.integers(0, len(ratios), (BOOT, len(ratios)))
                    bmed = np.median(ratios[bs], axis=1)
                    c_lo, c_hi = np.quantile(bmed, [a_cal / 2, 1 - a_cal / 2])
                    u_hat = u_gate_mean(probe, c_hat)
                    u_spread = max(abs(u_gate_mean(probe, c_lo) - u_hat),
                                   abs(u_gate_mean(probe, c_hi) - u_hat))
                    if u_spread <= EPS_CAL:
                        state["recalibration"] = ("act", T, dict(c_hat=c_hat, u_spread=u_spread))
                # --- selection certificate (cross-fitted, METHOD_SPEC v0.2) ---
                if state["selection"] is None:
                    pu = policy_utils_crossfit(probe)
                    U = np.stack([pu[n] for n in menu_names], axis=1)  # (T, M)
                    means = U.mean(axis=0)
                    se = U.std(axis=0, ddof=1) / np.sqrt(len(U))
                    cand = int(np.argmax(means - se))
                    bs = rng.integers(0, len(U), (BOOT, len(U)))
                    bmeans = U[bs].mean(axis=1)
                    diffs = bmeans - bmeans[:, [cand]]
                    ucb = np.quantile(diffs, 1 - a_sel, axis=0)
                    ucb[cand] = -np.inf
                    if ucb.max() <= EPS_SEL:
                        state["selection"] = ("act", T,
                                              dict(pick=menu_names[cand],
                                                   c_hat=c_hat, tau_i=tau_i))
                if all(v is not None for v in state.values()):
                    break
            for dec in ["recalibration", "selection"]:
                if state[dec] is None:
                    state[dec] = ("abstain", looks[-1], dict(c_hat=c_hat, tau_i=tau_i))
            # --- true losses on never-audited complement ---
            for dec, (action, T, pl) in state.items():
                ev = [H[i] for i in perm[T:]]
                pool_b = int(sum(H[i]["pool"] for i in perm[:T]))
                if dec == "recalibration":
                    loss = abs(u_gate_mean(ev, pl["c_hat"])
                               - float(np.mean([s["f_adc"] for s in ev])))
                    picked = "ad_probe"
                else:
                    pu = policy_utils(ev, pl["c_hat"], pl.get("tau_i", 0))
                    ev_means = {n: float(v.mean()) for n, v in pu.items()}
                    picked = pl.get("pick", max(menu_names,
                             key=lambda n: ev_means[n]))  # abstain: no pick
                    loss = (max(ev_means.values()) - ev_means[picked]
                            ) if action == "act" else None
                eps = EPS_CAL if dec == "recalibration" else EPS_SEL
                rows.append(dict(collection=held, untouched=held in bc.UNTOUCHED,
                                 repeat_id=rep, decision=dec, action=action,
                                 final_T=T, final_B_pool=pool_b,
                                 selected_policy=picked, loss=loss,
                                 wrong_cert=(action == "act" and loss is not None
                                             and loss > eps),
                                 cap=cap, seed=5_000_000 + 1000 * rep + salt))
        sub = [r for r in rows if r["collection"] == held]
        for dec in ["recalibration", "selection"]:
            d = [r for r in sub if r["decision"] == dec]
            acts = [r for r in d if r["action"] == "act"]
            print(f"{held:16} {dec:14} act={len(acts)/len(d):.2f} "
                  f"meanT={np.mean([r['final_T'] for r in d]):.0f} "
                  f"wrong={np.mean([r['wrong_cert'] for r in d]):.3f}", flush=True)

    import pandas as pd
    df = pd.DataFrame(rows)
    df.to_parquet(os.path.join(OUT, "planner_replay.parquet"), index=False)
    g = df.groupby(["collection", "untouched", "decision"], as_index=False).agg(
        act_rate=("action", lambda a: float((a == "act").mean())),
        abstain_rate=("action", lambda a: float((a == "abstain").mean())),
        mean_T=("final_T", "mean"), mean_B_pool=("final_B_pool", "mean"),
        wrong_cert_rate=("wrong_cert", "mean"))
    g.to_csv(os.path.join(OUT, "planner_summary.csv"), index=False)
    head = dict(alpha=ALPHA, eps_cal=EPS_CAL, eps_sel=EPS_SEL,
                overall_wrong_cert_rate=float(df["wrong_cert"].mean()),
                by_decision={dec: dict(
                    act_rate=float((sub["action"] == "act").mean()),
                    mean_T=float(sub["final_T"].mean()),
                    wrong_cert_rate=float(sub["wrong_cert"].mean()))
                    for dec, sub in df.groupby("decision")})
    json.dump(head, open(os.path.join(OUT, "replay_headline.json"), "w"), indent=2)
    print(json.dumps(head, indent=2))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.5, 5))
    for dec, mk in [("recalibration", "o"), ("selection", "s")]:
        sub = g[g.decision == dec]
        ax.scatter(sub["mean_T"], sub["act_rate"], marker=mk, s=70,
                   c=["#c44" if u else "#888" for u in sub["untouched"]],
                   label=dec, alpha=0.85, edgecolors="k", linewidths=0.5)
        for _, r in sub.iterrows():
            ax.annotate(r["collection"], (r["mean_T"], r["act_rate"]),
                        fontsize=6.5, xytext=(3, 3), textcoords="offset points")
    ax.set_xlabel("mean audited queries at stop (T)")
    ax.set_ylabel("certificate (ACT) rate")
    ax.set_title("F2 — Planner replay on 13 development collections\n"
                 "(circles=recalibration, squares=selection; red=untouched-4)")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "F2_planner_frontier.png"), dpi=160)
    print(f"[saved] {OUT}")


if __name__ == "__main__":
    main()
