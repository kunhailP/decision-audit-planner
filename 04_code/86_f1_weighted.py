#!/usr/bin/env python3
"""Appendix: decision-weighted document auditing for set-F1 (nonlinear in labels through nG).

Linearisation at the judge labels (no unobserved truth used):
  D(y) = 2 tp_a/(k_a + nG) − 2 tp_b/(k_b + nG),  nG = Σ_pool y_d, tp_m = Σ_{d∈R_m} y_d
  w_d := ∂D/∂y_d |_{y=ĵ} = 2·1[d∈R_a]/(k_a+n̂G) − 2·1[d∈R_b]/(k_b+n̂G) − 2 t̂p_a/(k_a+n̂G)² + 2 t̂p_b/(k_b+n̂G)²
  D̂_lin(q) = D(ĵ) + Σ_{d sampled} w_d (y_d − ĵ_d)/π_d ,  π_d ∝ |w_d|  (every pool doc has |w_d| > 0 through nG)
D̂_lin is unbiased for the first-order expansion only; the second-order remainder is a bias whose size we measure
directly (mean of D̂_lin − D over fully labelled queries) and whose effect on the certificate we report as the
wrong-certificate rate.  Arms at equal document budget: human_full (whole pool), weighted_lin (humans only, HT on
linearised weights), judge_ppi (query-level PPI on fully labelled queries), weighted_lin_cv (as written above).
"""
import argparse, importlib.util, math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); HUB = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location("pv", os.path.join(HERE, "63_planner_v2.py")); pv = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv)
spec = importlib.util.spec_from_file_location("sb", os.path.join(HERE, "81_sampling_baselines.py")); sb = importlib.util.module_from_spec(spec); spec.loader.exec_module(sb)
bc, cert, MENU = pv.bc, pv.cert, pv.MENU
ALPHA = 0.10; ARMS = ["human_full", "weighted_lin", "judge_ppi", "weighted_lin_cv"]


def f1(y, k, nG):
    tp = float(y[:k].sum()); return 2 * tp / (k + nG) if tp > 0 else 0.0


def lin_weights(jhat, ka, kb):
    n = len(jhat); nG = float(jhat.sum()); tpa, tpb = float(jhat[:ka].sum()), float(jhat[:kb].sum())
    w = np.full(n, -2 * tpa / (ka + nG) ** 2 + 2 * tpb / (kb + nG) ** 2)
    w[:ka] += 2 / (ka + nG); w[:kb] -= 2 / (kb + nG)
    return w, 2 * tpa / (ka + nG) - 2 * tpb / (kb + nG)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pools", required=True); ap.add_argument("--stack", required=True)
    ap.add_argument("--names", nargs="+", required=True); ap.add_argument("--judge", default="llm")
    ap.add_argument("--train_dir", default=None); ap.add_argument("--train_names", nargs="+", default=["nfcorpus", "scifact", "arguana", "cqadupstack-android"])
    ap.add_argument("--budget_full", nargs="+", type=int, default=[30, 60, 90, 120]); ap.add_argument("--eps", nargs="+", type=float, default=[0.01, 0.02])
    ap.add_argument("--n_train", type=int, default=20); ap.add_argument("--docs_per_query", type=int, default=6); ap.add_argument("--draws", type=int, default=300)
    a = ap.parse_args()
    pv.NAMES = a.names; pv.JUDGE = a.judge
    data = pv.load_with_judge(os.path.join(a.pools, a.stack, "runs", "candidates"))
    if a.train_dir:
        pv.JUDGE = "rr"; data.update(pv.load_train_only(a.train_dir, a.train_names)); pv.JUDGE = a.judge
    rng_global = np.random.default_rng(0); rng = np.random.default_rng(43)
    M = len(MENU); a_sim = ALPHA / (M * (M - 1)); rows = []
    for held in [d for d in data if d not in pv.TRAIN_ONLY]:
        P, structs, reg = pv.fit_lodo(data, held, rng_global)
        H = structs[held]; c_star = pv.finalize(H, reg); N = len(H)
        HJ = bc.build_structs({held: data[held]["judge"]}, held, P[held]); pv.finalize(HJ, reg)
        Y = [np.diff(np.r_[0, s["cumtp"]]).astype(float) for s in H]; J = [np.diff(np.r_[0, s["cumtp"]]).astype(float) for s in HJ]
        pool = np.array([len(y) for y in Y], float)
        for Bq in a.budget_full:
            for eps in a.eps:
                cnt = {m: [0, 0] for m in ARMS}; bias = []
                for _ in range(a.draws):
                    perm = rng.permutation(N); tr = perm[:a.n_train]
                    c_tr, tau_tr, _ = pv.fit_params([H[k] for k in tr])
                    K = [[max(pv.cutoffs(H[k], m, c_tr, tau_tr), 1) for m in MENU] for k in range(N)]
                    U = np.array([[f1(Y[k], K[k][m], Y[k].sum()) for m in range(M)] for k in range(N)])
                    cand = cert.pick_candidate(U[tr]); mu = U.mean(axis=0); regret = float(mu.max() - mu[cand]); others = [j for j in range(M) if j != cand]
                    B = Bq * float(pool.mean()) - float(pool[tr].sum())
                    if B <= 0:
                        continue
                    rest = perm[a.n_train:]
                    # human_full & judge_ppi
                    cum = np.cumsum(pool[rest]); n_full = int((cum <= B).sum()); q_full = rest[:n_full]
                    if n_full >= 5:
                        Uf = U[q_full]; ut = cert.ucb_t(Uf, cand, a_sim)
                        if ut.max() <= eps:
                            cnt["human_full"][0] += 1; cnt["human_full"][1] += regret > eps
                        q_unl = rest[n_full:]
                        Uj_all = np.array([[f1(J[k], K[k][m], J[k].sum()) for m in range(M)] for k in q_unl]) if len(q_unl) > 2 else None
                        Uj_lab = np.array([[f1(J[k], K[k][m], J[k].sum()) for m in range(M)] for k in q_full])
                        if Uj_all is not None:
                            up = cert.ucb_ppi(Uf, Uj_lab, Uj_all, cand, a_sim)
                            if up.max() <= eps:
                                cnt["judge_ppi"][0] += 1; cnt["judge_ppi"][1] += regret > eps
                    # weighted (linearised) arms
                    b = max(a.docs_per_query, int(math.ceil(B / len(rest)))); n_w = int(B // b); q_w = rest[:min(n_w, len(rest))]
                    if len(q_w) >= 5:
                        ok_ht = ok_cv = True
                        for j in others:
                            Dht, Dcv, Dtrue = [], [], []
                            for k in q_w:
                                y, jh = Y[k], J[k]; w, D0 = lin_weights(jh, K[k][j], K[k][cand]); n = len(y)
                                pi = sb.sample_pi(np.abs(w), b, n); samp = (rng.random(n) < pi) & (pi > 0)
                                corr = float((w[samp] * (y[samp] - jh[samp]) / pi[samp]).sum())
                                Dcv.append(D0 + corr)
                                # humans-only linearised HT: expand around zero predictions (ĵ ≡ 0 gives w from the true-label-free point)
                                w0, D00 = lin_weights(np.zeros(n), K[k][j], K[k][cand]); pi0 = sb.sample_pi(np.abs(w0) + 1e-9, b, n); s0 = (rng.random(n) < pi0) & (pi0 > 0)
                                Dht.append(D00 + float((w0[s0] * y[s0] / pi0[s0]).sum()))
                                Dtrue.append(f1(y, K[k][j], y.sum()) - f1(y, K[k][cand], y.sum()))
                            bias.append(float(np.mean(Dcv) - np.mean(Dtrue)))
                            for name, D in [("weighted_lin", np.array(Dht)), ("weighted_lin_cv", np.array(Dcv))]:
                                nq = len(D); ucb = D.mean() + cert.t_quantile(1 - a_sim, nq - 1) * D.std(ddof=1) / math.sqrt(nq)
                                if ucb > eps:
                                    if name == "weighted_lin": ok_ht = False
                                    else: ok_cv = False
                        if ok_ht:
                            cnt["weighted_lin"][0] += 1; cnt["weighted_lin"][1] += regret > eps
                        if ok_cv:
                            cnt["weighted_lin_cv"][0] += 1; cnt["weighted_lin_cv"][1] += regret > eps
                for m in ARMS:
                    rows.append(dict(collection=held, judge=a.judge, budget_full_eq=Bq, eps=eps, method=m, act=cnt[m][0] / a.draws, wrong=cnt[m][1] / a.draws,
                                     lin_bias=float(np.mean(bias)) if bias else float("nan"), lin_bias_abs=float(np.mean(np.abs(bias))) if bias else float("nan"),
                                     docs=float(Bq * pool.mean())))
                print(f"{held} B={Bq}q eps={eps}: " + " ".join(f"{m}={cnt[m][0]/a.draws:.2f}/{cnt[m][1]/a.draws:.3f}" for m in ARMS) + f" | lin bias {np.mean(bias):+.4f} (|.| {np.mean(np.abs(bias)):.4f})", flush=True)
    import pandas as pd
    out = os.path.join(HUB, "05_results", "f1_weighted"); os.makedirs(out, exist_ok=True)
    pd.DataFrame(rows).to_csv(os.path.join(out, f"f1_weighted_{a.stack}_{a.judge}.csv"), index=False)


if __name__ == "__main__":
    main()
