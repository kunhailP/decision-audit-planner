#!/usr/bin/env python3
"""Prototype: does a policy-correlated (non-neutral) AI judge kill the audit
savings of prediction-powered selection certificates, even when its global
accuracy is unchanged?  Two cutoff policies over a shared ranked pool (same
structure as decision-audit-planner), set-F1 utility, sequential looks,
Bonferroni over looks, alpha=0.1, eps=0.01.

Methods: human-only paired certificate (current planner, normal CI),
PPI++ paired certificate (judge on all queries + human rectifier),
judge-as-truth (no human correction; shows the danger).
"""
import math, sys
import numpy as np

N, D, KA = 20000, 40, 8
ALPHA, EPS = 0.10, 0.01
LOOKS = [10, 30, 50, 70, 90, 150, 250]
REPS = 200
p_rank = 0.55 * np.exp(-np.arange(D) / 7.0) + 0.02


def z_of(alpha_one_sided):
    lo, hi = 0.0, 10.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if 0.5 * (1 - math.erf(mid / math.sqrt(2))) > alpha_one_sided:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


Z = z_of(ALPHA / len(LOOKS))


def f1(cumtp, k, nG):
    tp = cumtp[np.arange(len(k)), k - 1]
    return np.where(tp > 0, 2.0 * tp / (k + nG), 0.0)


def population(rng, b_noise):
    r = (rng.random((N, D)) < p_rank).astype(np.int8)
    nG = r.sum(1)
    keep = nG > 0
    r, nG = r[keep], nG[keep]
    n = len(r)
    kA = np.full(n, KA)
    cum = np.cumsum(r, 1)
    ks = np.arange(1, D + 1)[None, :]
    f1_all = np.where(cum > 0, 2.0 * cum / (ks + nG[:, None]), 0.0)
    k_star = f1_all.argmax(1) + 1                       # F1-optimal cutoff
    k_noisy = np.clip(KA + rng.integers(-4, 8, n), 1, 20)
    kB = np.where(rng.random(n) < b_noise, k_star, k_noisy).astype(int)  # b_noise = q
    uA, uB = f1(cum, kA, nG), f1(cum, kB, nG)
    return r, nG, kA, kB, uA, uB


def judge(rng, r, kA, kB, e, bias):
    n = len(r)
    flip = rng.random(r.shape) < e
    rhat = np.where(flip, 1 - r, r)
    if bias > 0:  # judge over-credits docs that only policy B retrieves
        cols = np.arange(D)[None, :]
        band = (cols >= kA[:, None]) & (cols < kB[:, None]) & (r == 0)
        extra = rng.random(r.shape) < bias
        rhat = np.where(band & extra, 1, rhat)
    nGh = rhat.sum(1)
    cum = np.cumsum(rhat, 1)
    uAh = np.where(nGh > 0, f1(cum, kA, np.maximum(nGh, 1)), 0.0)
    uBh = np.where(nGh > 0, f1(cum, kB, np.maximum(nGh, 1)), 0.0)
    acc = float((rhat == r).mean())
    return uAh, uBh, acc


def certify(est, se, delta_true):
    """pick by sign of estimate; ACT if UCB of regret <= EPS."""
    if est >= 0:      # pick B, regret = -delta
        ucb = Z * se - est
        regret = max(0.0, -delta_true)
    else:             # pick A, regret = delta
        ucb = est + Z * se
        regret = max(0.0, delta_true)
    return ucb <= EPS, regret


def run_cell(e, bias, b_noise, seed):
    rng = np.random.default_rng(seed)
    r, nG, kA, kB, uA, uB = population(rng, b_noise)
    uAh, uBh, acc = judge(rng, r, kA, kB, e, bias)
    d, dh = uB - uA, uBh - uAh
    delta_true = float(d.mean())
    rho = float(np.corrcoef(d, dh)[0, 1])
    n_pop = len(d)
    out = {m: dict(act=0, T=[], wrong=0) for m in ["human", "ppi", "judge_only"]}
    for rep in range(REPS):
        perm = rng.permutation(n_pop)
        done = {m: False for m in out}
        # judge-only certifies at first look with no human evidence
        est_j, se_j = float(dh.mean()), float(dh.std(ddof=1) / math.sqrt(n_pop))
        ok, reg = certify(est_j, se_j, delta_true)
        if ok:
            out["judge_only"]["act"] += 1; out["judge_only"]["wrong"] += reg > EPS
        out["judge_only"]["T"].append(0); done["judge_only"] = True
        for T in LOOKS:
            S = perm[:T]
            dS, dhS = d[S], dh[S]
            if not done["human"]:
                est, se = float(dS.mean()), float(dS.std(ddof=1) / math.sqrt(T))
                ok, reg = certify(est, se, delta_true)
                if ok:
                    out["human"]["act"] += 1; out["human"]["wrong"] += reg > EPS
                    out["human"]["T"].append(T); done["human"] = True
            if not done["ppi"]:
                v = dhS.var(ddof=1)
                lam = float(np.clip(np.cov(dS, dhS)[0, 1] / v, 0, 1)) if v > 0 else 0.0
                resid = dS - lam * dhS
                est = lam * float(dh.mean()) + float(resid.mean())
                se = math.sqrt(lam ** 2 * dh.var(ddof=1) / n_pop + resid.var(ddof=1) / T)
                ok, reg = certify(est, se, delta_true)
                if ok:
                    out["ppi"]["act"] += 1; out["ppi"]["wrong"] += reg > EPS
                    out["ppi"]["T"].append(T); done["ppi"] = True
            if all(done.values()):
                break
        for m in ["human", "ppi"]:
            if not done[m]:
                out[m]["T"].append(LOOKS[-1])
    row = dict(e=e, bias=bias, acc=acc, rho=rho, delta=delta_true)
    for m, o in out.items():
        row[m] = dict(act=o["act"] / REPS, meanT=float(np.mean(o["T"])),
                      wrong=o["wrong"] / REPS)
    return row


if __name__ == "__main__":
    b_noise = float(sys.argv[1]) if len(sys.argv) > 1 else 3.0
    print(f"{'e':>5}{'bias':>6}{'acc':>7}{'rho':>7}{'delta':>8} | "
          f"{'human act/T/wrong':>20} | {'PPI act/T/wrong':>20} | {'judge-only act/wrong':>22}")
    for e in [0.05, 0.15, 0.30]:
        for bias in [0.0, 0.3, 0.6]:
            row = run_cell(e, bias, b_noise, seed=1000 * int(e * 100) + int(bias * 10))
            h, p, j = row["human"], row["ppi"], row["judge_only"]
            print(f"{e:>5.2f}{bias:>6.1f}{row['acc']:>7.3f}{row['rho']:>7.3f}{row['delta']:>8.4f} | "
                  f"{h['act']:>6.2f}{h['meanT']:>7.1f}{h['wrong']:>7.3f} | "
                  f"{p['act']:>6.2f}{p['meanT']:>7.1f}{p['wrong']:>7.3f} | "
                  f"{j['act']:>10.2f}{j['wrong']:>11.3f}", flush=True)
