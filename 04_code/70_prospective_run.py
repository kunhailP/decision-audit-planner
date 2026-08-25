#!/usr/bin/env python3
"""P4 — Prospective primary run on cqadupstack-android (PROSPECTIVE_LOCK_2026-08-25).

Training (classifier, tau transfer, trunc regressor) uses ONLY the 13
development collections, pooled (the extreme form of LODO: full external
transfer). The target contributes nothing to any fitting or tuning step.
Planner logic is byte-identical to 40_planner_replay.py (frozen v0.3,
cross-fitted selection, look-corrected recalibration). Single primary run,
50 repeat draws, results reported regardless of outcome.
"""
import hashlib, importlib.util, json, os, zlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
HUB = os.path.dirname(HERE)


def load_mod(fname, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fname))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bc = load_mod("20_budget_curves.py", "bc")
pr = load_mod("40_planner_replay.py", "pr")

TARGET = "cqadupstack-android"
ALPHA, EPS_CAL, EPS_SEL = 0.10, 0.005, 0.01
LOOKS = [10, 30, 50, 70, 90]
BOOT, REPS = 400, 50
OUT = os.path.join(HUB, "05_results", "prospective_android")
os.makedirs(OUT, exist_ok=True)


def main():
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.ensemble import HistGradientBoostingRegressor
    import pandas as pd

    lock = os.path.join(HUB, "03_data", "PROSPECTIVE_LOCK_2026-08-25.md")
    lock_sha = hashlib.sha256(open(lock, "rb").read()).hexdigest()
    cand_dir = os.path.join("/root/shift-study", "runs", "candidates")

    dev = bc.load(cand_dir)                      # the 13 development collections
    assert TARGET not in dev
    # load target with the same reader
    saved = bc.ALL_DATASETS
    bc.ALL_DATASETS = [TARGET]
    tgt = bc.load(cand_dir)
    bc.ALL_DATASETS = saved
    assert TARGET in tgt, "target candidates missing — run 60_prospective_build.py first"

    # ---- fit on development pool only ----
    Xtr = np.concatenate([dev[d]["X"] for d in dev])
    ytr = np.concatenate([dev[d]["rel"] for d in dev])
    rng_global = np.random.default_rng(0)
    if len(Xtr) > bc.MAX_TRAIN:
        idx = rng_global.choice(len(Xtr), bc.MAX_TRAIN, replace=False)
        Xtr, ytr = Xtr[idx], ytr[idx]
    sc = StandardScaler().fit(Xtr)
    clf = CalibratedClassifierCV(LogisticRegression(max_iter=2000),
                                 method="sigmoid", cv=3
                                 ).fit(sc.transform(Xtr), ytr)
    dev_structs = {d: bc.build_structs(dev, d,
                   clf.predict_proba(sc.transform(dev[d]["X"]))[:, 1]) for d in dev}
    tau_scores = np.zeros(len(bc.TAUS)); n_tr_q = 0
    Xk, yk = [], []
    for d in dev:
        for s in dev_structs[d]:
            for ti in range(len(bc.TAUS)):
                tau_scores[ti] += bc.util_at_k(s, int(s["tau_ks"][ti]))
            n_tr_q += 1
            Xk.append(s["feat"]); yk.append(s["k_star"])
    tau_transfer_i = int(np.argmax(tau_scores / n_tr_q))
    reg = HistGradientBoostingRegressor(random_state=0).fit(
        np.asarray(Xk), np.asarray(yk))

    # ---- target structs (no fitting) ----
    H = bc.build_structs(tgt, TARGET,
                         clf.predict_proba(sc.transform(tgt[TARGET]["X"]))[:, 1])
    k_trunc = np.clip(np.round(reg.predict(np.asarray([s["feat"] for s in H]))),
                      1, [len(s["sp"]) for s in H]).astype(int)
    c_star = float(np.median([s["nG"] / s["Sp"] for s in H if s["Sp"] > 0]))
    for s, kt in zip(H, k_trunc):
        s["f_adc"] = bc.util_at_k(s, bc.gate_k(s["sp"], s["cump"], c_star * s["Sp"]))
        s["f_trunc"] = bc.util_at_k(s, int(kt))
        s["f_tau"] = np.array([bc.util_at_k(s, int(s["tau_ks"][ti]))
                               for ti in range(len(bc.TAUS))])
    cap = len(H) // 2
    looks = [t for t in LOOKS if t <= cap] or [cap]
    menu_names = ["glob_probe", "trunc", "ad_probe"]
    a_sel = ALPHA / (len(LOOKS) * (len(menu_names) - 1))
    a_cal = ALPHA / len(LOOKS)
    salt = zlib.crc32(f"planner|{TARGET}".encode()) % 100_000

    rows = []
    for rep in range(REPS):
        rng = np.random.default_rng(5_000_000 + 1000 * rep + salt)
        perm = rng.permutation(len(H))
        state = {"recalibration": None, "selection": None}
        for T in looks:
            probe = [H[i] for i in perm[:T]]
            ratios = np.array([s["nG"] / s["Sp"] for s in probe if s["Sp"] > 0])
            c_hat = float(np.median(ratios))
            tau_i = int(np.argmax(np.mean([s["f_tau"] for s in probe], axis=0)))
            if state["recalibration"] is None:
                bs = rng.integers(0, len(ratios), (BOOT, len(ratios)))
                bmed = np.median(ratios[bs], axis=1)
                c_lo, c_hi = np.quantile(bmed, [a_cal / 2, 1 - a_cal / 2])
                u_hat = pr.u_gate_mean(probe, c_hat)
                u_spread = max(abs(pr.u_gate_mean(probe, c_lo) - u_hat),
                               abs(pr.u_gate_mean(probe, c_hi) - u_hat))
                if u_spread <= EPS_CAL:
                    state["recalibration"] = ("act", T, dict(c_hat=c_hat))
            if state["selection"] is None:
                pu = pr.policy_utils_crossfit(probe)
                U = np.stack([pu[n] for n in menu_names], axis=1)
                means = U.mean(axis=0)
                se = U.std(axis=0, ddof=1) / np.sqrt(len(U))
                cand = int(np.argmax(means - se))
                bs = rng.integers(0, len(U), (BOOT, len(U)))
                bmeans = U[bs].mean(axis=1)
                diffs = bmeans - bmeans[:, [cand]]
                ucb = np.quantile(diffs, 1 - a_sel, axis=0)
                ucb[cand] = -np.inf
                if ucb.max() <= EPS_SEL:
                    state["selection"] = ("act", T, dict(pick=menu_names[cand],
                                                         c_hat=c_hat, tau_i=tau_i))
            if all(v is not None for v in state.values()):
                break
        for dec in ["recalibration", "selection"]:
            if state[dec] is None:
                state[dec] = ("abstain", looks[-1], dict(c_hat=c_hat, tau_i=tau_i))
        for dec, (action, T, pl) in state.items():
            ev = [H[i] for i in perm[T:]]
            if dec == "recalibration":
                loss = abs(pr.u_gate_mean(ev, pl["c_hat"])
                           - float(np.mean([s["f_adc"] for s in ev])))
                picked = "ad_probe"
                loss_reported = loss
            else:
                pu = pr.policy_utils(ev, pl["c_hat"], pl.get("tau_i", 0))
                ev_means = {n: float(v.mean()) for n, v in pu.items()}
                picked = pl.get("pick", max(menu_names, key=lambda n: ev_means[n]))
                loss_reported = (max(ev_means.values()) - ev_means[picked]
                                 ) if action == "act" else None
            eps = EPS_CAL if dec == "recalibration" else EPS_SEL
            rows.append(dict(collection=TARGET, repeat_id=rep, decision=dec,
                             action=action, final_T=T,
                             final_B_pool=int(sum(H[i]["pool"] for i in perm[:T])),
                             selected_policy=picked, loss=loss_reported,
                             wrong_cert=(action == "act" and loss_reported is not None
                                         and loss_reported > eps),
                             cap=cap, c_star=c_star,
                             seed=5_000_000 + 1000 * rep + salt))

    import pandas as pd
    df = pd.DataFrame(rows)
    df.to_parquet(os.path.join(OUT, "primary_run.parquet"), index=False)
    head = dict(
        lock_sha256=lock_sha, target=TARGET,
        n_queries=len(H), cap=cap, looks=looks, c_star=c_star,
        alpha=ALPHA, eps_cal=EPS_CAL, eps_sel=EPS_SEL, repeats=REPS,
        by_decision={dec: dict(
            act_rate=float((sub["action"] == "act").mean()),
            abstain_rate=float((sub["action"] == "abstain").mean()),
            mean_T=float(sub["final_T"].mean()),
            wrong_cert_rate=float(sub["wrong_cert"].mean()),
            mc_se=float(np.sqrt(0.1 * 0.9 / len(sub))),
            picks=sub["selected_policy"].value_counts().to_dict())
            for dec, sub in df.groupby("decision")},
        primary_criterion_pass={dec: bool(sub["wrong_cert"].mean() <= ALPHA)
                                for dec, sub in df.groupby("decision")})
    json.dump(head, open(os.path.join(OUT, "primary_headline.json"), "w"), indent=2)
    print(json.dumps(head, indent=2))


if __name__ == "__main__":
    main()
