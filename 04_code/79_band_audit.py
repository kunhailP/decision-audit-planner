#!/usr/bin/env python3
"""Band-localised (pair-level) auditing — Proposition C made practical.

For a policy pair (a, b) acting on the same ranked pool, the true paired
difference depends on the labels of the disagreement band Δ(q) = ranks between
the two cutoffs, plus policy-neutral quantities (nG, relevant docs both
policies return).  The HYBRID predictor labels only Δ(q) with humans and lets
the AI judge fill the rest:  d̂_hyb(q) = f(human labels on Δ(q), judge labels
elsewhere).  Judge errors inside the band — the ones F6 / §12.2 showed to be
harmful — are removed by construction; judge errors outside the band are
common-mode to both policies and largely cancel.  d̂_hyb is then used exactly
like any predictor inside the split/PPI certificate (Prop. B′ ⇒ validity), so
the audit spends its pair-judgment budget where the decision lives.

Fixed-budget comparison at equal PAIR-JUDGMENT budget B (docs judged by humans):
  human_full : n_A = B / pool_avg fully judged queries, t certificate
  judge_ppi  : same n_A fully judged queries + judge on all other queries, PPI
  hybrid     : n_C = n_A/2 fully judged queries (rectifier) + band-only human
               labels on N_hyb = (B/2) / band_avg further queries, PPI with d̂_hyb
Reports rho(judge), rho(hybrid), band fraction, ACT rates / wrong rates per eps.

Usage: python3 79_band_audit.py --pools <dir> --stack judged --names dbpedia-entity --judge llm --train_dir <dir>
"""
import argparse, importlib.util, math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); HUB = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location("pv", os.path.join(HERE, "63_planner_v2.py"))
pv = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv)
bc, cert, MENU = pv.bc, pv.cert, pv.MENU
ALPHA = 0.10


UTIL = "f1"


def f1_from(rel, k, nG):
    tp = int(rel[:k].sum())
    if UTIL == "prec":
        return tp / k if k > 0 else 0.0
    return 2.0 * tp / (k + nG) if tp > 0 else 0.0


def per_query_arrays(H, HJ, c, tau_i):
    """true per-doc relevance, judge per-doc relevance, cutoffs per policy."""
    out = []
    for s, sj in zip(H, HJ):
        r = np.diff(np.r_[0, s["cumtp"]]).astype(np.int8); rj = np.diff(np.r_[0, sj["cumtp"]]).astype(np.int8)
        ks = [pv.cutoffs(s, m, c, tau_i) for m in MENU]
        out.append((r, rj, ks))
    return out


def util_mat(arr):
    return np.array([[f1_from(r, ks[m], int(r.sum())) for m in range(len(MENU))] for r, _, ks in arr])


def pop_mu(arr):
    return util_mat(arr).mean(axis=0)


def pair_preds(arr, ia, ib):
    """true d, judge-only d̂, hybrid d̂ (human band + judge elsewhere), band size, pool size."""
    d, dj, dh, band, pool = [], [], [], [], []
    for r, rj, ks in arr:
        ka, kb = ks[ia], ks[ib]; lo, hi = min(ka, kb), max(ka, kb)
        nG = int(r.sum()); nGj = int(rj.sum())
        rh = rj.copy(); rh[lo:hi] = r[lo:hi]; nGh = int(rh.sum())
        d.append(f1_from(r, ka, nG) - f1_from(r, kb, nG))
        dj.append(f1_from(rj, ka, max(nGj, 1)) - f1_from(rj, kb, max(nGj, 1)) if nGj > 0 else 0.0)
        dh.append(f1_from(rh, ka, max(nGh, 1)) - f1_from(rh, kb, max(nGh, 1)) if nGh > 0 else 0.0)
        band.append(hi - lo); pool.append(len(r) if UTIL == "f1" else max(hi, 1))   # cost of a fully judged query
    return np.array(d), np.array(dj), np.array(dh), np.array(band), np.array(pool)


def ppi_ucb_pair(d_lab, dh_lab, dh_unl, alpha_prime):
    n = len(d_lab); N = len(dh_unl)
    lam_vec = cert.crossfit_lambda(d_lab, dh_lab, n_over_N=n / max(N, 1)); lam = float(lam_vec.mean())
    resid = d_lab - lam_vec * dh_lab
    est = lam * dh_unl.mean() + resid.mean()
    se = math.sqrt(lam ** 2 * dh_unl.var(ddof=1) / N + resid.var(ddof=1) / n) if N > 1 else resid.std(ddof=1) / math.sqrt(n)
    return est + cert.t_quantile(1 - alpha_prime, n - 1) * se


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pools", required=True); ap.add_argument("--stack", required=True)
    ap.add_argument("--names", nargs="+", required=True); ap.add_argument("--judge", default="llm")
    ap.add_argument("--train_dir", default=None); ap.add_argument("--train_names", nargs="+", default=["nfcorpus", "scifact", "arguana", "cqadupstack-android"])
    ap.add_argument("--nA", nargs="+", type=int, default=[30, 60, 90]); ap.add_argument("--eps", nargs="+", type=float, default=[0.005, 0.01, 0.02])
    ap.add_argument("--draws", type=int, default=300)
    ap.add_argument("--utility", default="f1", choices=["f1", "prec"]); ap.add_argument("--hyb_frac", nargs="+", type=float, default=[0.5, 0.7, 0.85])
    a = ap.parse_args()
    global UTIL; UTIL = a.utility
    pv.NAMES = a.names; pv.JUDGE = a.judge
    data = pv.load_with_judge(os.path.join(a.pools, a.stack, "runs", "candidates"))
    if a.train_dir:
        pv.JUDGE = "rr"; data.update(pv.load_train_only(a.train_dir, a.train_names)); pv.JUDGE = a.judge
    rng_global = np.random.default_rng(0); rng = np.random.default_rng(23)
    M = len(MENU); a_sim = ALPHA / (M * (M - 1))
    rows, diag = [], []
    for held in [d for d in data if d not in pv.TRAIN_ONLY]:
        P, structs, reg = pv.fit_lodo(data, held, rng_global)
        H = structs[held]; c_star = pv.finalize(H, reg); N = len(H)
        HJ = bc.build_structs({held: data[held]["judge"]}, held, P[held]); pv.finalize(HJ, reg)
        _, tau_star, _ = pv.fit_params(H)
        # --- diagnostics at population policy params: rho judge vs hybrid, band fraction ---
        arr = per_query_arrays(H, HJ, c_star, tau_star)
        pool_avg = float(np.mean([len(r) if UTIL == "f1" else max(max(ks), 1) for r, _, ks in arr]))
        for i, j in [(0, 1), (0, 2), (1, 2)]:
            d, dj, dh, band, pool = pair_preds(arr, i, j)
            rj = float(np.corrcoef(d, dj)[0, 1]) if d.std() > 0 and dj.std() > 0 else 0.0
            rh = float(np.corrcoef(d, dh)[0, 1]) if d.std() > 0 and dh.std() > 0 else 0.0
            diag.append(dict(collection=held, judge=a.judge, pair=f"{MENU[i]}_vs_{MENU[j]}", rho_judge=rj, rho_hybrid=rh,
                             band_mean=float(band.mean()), pool_mean=pool_avg, band_frac=float(band.mean() / pool_avg),
                             gain_judge=1 / (1 - rj ** 2) if abs(rj) < 1 else float("inf"), gain_hybrid=1 / (1 - rh ** 2) if abs(rh) < 1 else float("inf")))
            print(f"{held} {MENU[i]} vs {MENU[j]}: rho judge={rj:.2f} hybrid={rh:.2f} band={band.mean():.1f}/{pool_avg:.0f} docs ({band.mean()/pool_avg:.0%})", flush=True)
        # --- fixed-budget certificates at equal pair budget ---
        U_pop = pv.utils(H, c_star, tau_star)
        for nA in a.nA:
            if nA + 20 > N:
                continue
            B = nA * pool_avg
            for eps in a.eps:
                cnt = {m: [0, 0] for m in ["human_full", "judge_ppi"] + [f"hybrid_{f}" for f in a.hyb_frac]}
                for _ in range(a.draws):
                    perm = rng.permutation(N)
                    # human_full & judge_ppi: nA fully judged queries, split train/val
                    aud = perm[:nA]; ntr = nA // 2; tr = [H[k] for k in aud[:ntr]]; va_idx = aud[ntr:]
                    c_tr, tau_tr, _ = pv.fit_params(tr)
                    arr_tr = per_query_arrays(H, HJ, c_tr, tau_tr)          # policy params from train half
                    U_va = util_mat([arr_tr[k] for k in va_idx]) if UTIL == "prec" else pv.utils([H[k] for k in va_idx], c_tr, tau_tr); cand = cert.pick_candidate(U_va)
                    mu = pop_mu(per_query_arrays(H, HJ, c_tr, tau_tr)) if UTIL == "prec" else pv.utils(H, c_tr, tau_tr).mean(axis=0); regret = float(mu.max() - mu[cand])
                    others = [j for j in range(M) if j != cand]
                    # human_full: t bounds
                    ut = cert.ucb_t(U_va, cand, a_sim)
                    if ut.max() <= eps:
                        cnt["human_full"][0] += 1; cnt["human_full"][1] += regret > eps
                    # judge_ppi: predictor = judge everywhere on all non-audited queries
                    unl = perm[nA:]
                    ok = True
                    for j in others:
                        d, dj, dh, band, pool = pair_preds([arr_tr[k] for k in va_idx], j, cand)
                        _, dj_u, _, _, _ = pair_preds([arr_tr[k] for k in unl], j, cand)
                        if ppi_ucb_pair(d, dj, dj_u, a_sim) > eps:
                            ok = False; break
                    if ok:
                        cnt["judge_ppi"][0] += 1; cnt["judge_ppi"][1] += regret > eps
                    # hybrid: nC = frac*nA fully judged (train half fits params), band-only labels on further queries with the rest of B
                    for frac in a.hyb_frac:
                        nC = max(int(round(frac * nA)), 8); audC = perm[:nC]; ntrC = nC // 2
                        c_c, tau_c, _ = pv.fit_params([H[k] for k in audC[:ntrC]]); vaC = audC[ntrC:]
                        arr_c = per_query_arrays(H, HJ, c_c, tau_c)
                        U_vaC = util_mat([arr_c[k] for k in vaC]) if UTIL == "prec" else pv.utils([H[k] for k in vaC], c_c, tau_c); candC = cert.pick_candidate(U_vaC)
                        muC = pop_mu(arr_c) if UTIL == "prec" else pv.utils(H, c_c, tau_c).mean(axis=0); regretC = float(muC.max() - muC[candC])
                        okC = True; spent = nC * pool_avg
                        for j in [x for x in range(M) if x != candC]:
                            d, dj, dh, band, pool = pair_preds([arr_c[k] for k in vaC], j, candC)
                            rest = perm[nC:]
                            _, _, dh_u, band_u, _ = pair_preds([arr_c[k] for k in rest], j, candC)
                            cum = np.cumsum(band_u); n_hyb = int((cum <= (B - spent)).sum()); n_hyb = max(min(n_hyb, len(rest)), 2)
                            if ppi_ucb_pair(d, dh, dh_u[:n_hyb], a_sim) > eps:
                                okC = False; break
                        if okC:
                            cnt[f"hybrid_{frac}"][0] += 1; cnt[f"hybrid_{frac}"][1] += regretC > eps
                for m, (act, wr) in cnt.items():
                    rows.append(dict(collection=held, judge=a.judge, nA=nA, budget_docs=B, eps=eps, method=m, act=act / a.draws, wrong=wr / a.draws))
                print(f"  {held} nA={nA} eps={eps}: " + " ".join(f"{m}={v[0]/a.draws:.2f}/{v[1]/a.draws:.3f}" for m, v in cnt.items()), flush=True)
    import pandas as pd
    out = os.path.join(HUB, "05_results", "band_audit"); os.makedirs(out, exist_ok=True)
    pd.DataFrame(rows).to_csv(os.path.join(out, f"band_audit_{a.stack}_{a.judge}_{a.utility}.csv"), index=False)
    pd.DataFrame(diag).to_csv(os.path.join(out, f"band_diag_{a.stack}_{a.judge}_{a.utility}.csv"), index=False)


if __name__ == "__main__":
    main()
