#!/usr/bin/env python3
"""Hub test suite (CONTRACTS.md: unit / leakage / regeneration).

Run: python3 04_code/tests/run_tests.py   (exit 0 = all pass)
"""
import importlib.util, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.dirname(HERE)
HUB = os.path.dirname(CODE)
RESULTS = os.path.join(HUB, "05_results")

spec = importlib.util.spec_from_file_location("bc", os.path.join(CODE, "20_budget_curves.py"))
bc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bc)

FAILURES = []


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)


# ---------- unit ----------
def unit_tests():
    # f1 at boundaries
    cumtp = np.array([1, 1, 2])
    check("f1: k=0 returns 0", bc.f1_at_k(cumtp, 0, 2) == 0.0)
    check("f1: exact value", abs(bc.f1_at_k(cumtp, 3, 2) - 2 * 2 / (3 + 2)) < 1e-12)
    # gate_k boundaries
    sp = np.array([0.9, 0.5, 0.1]); cump = np.cumsum(sp)
    check("gate: R<=0 returns 0", bc.gate_k(sp, cump, 0.0) == 0)
    check("gate: huge R includes all", bc.gate_k(sp, cump, 100.0) == 3)
    # utility dispatch
    s = dict(cumtp=cumtp, nG=2, cumdcg=np.cumsum(np.array([1, 0, 1]) /
             np.log2(np.arange(3) + 2.0)))
    bc.UTILITY = "recall"
    check("recall utility", abs(bc.util_at_k(s, 3) - 1.0) < 1e-12)
    bc.UTILITY = "ndcg"
    ideal = 1 / np.log2(2) + 1 / np.log2(3)
    check("ndcg utility", abs(bc.util_at_k(s, 3) - float(s["cumdcg"][2]) / ideal) < 1e-12)
    bc.UTILITY = "set_f1"
    # regret sign/range from stored rows
    import pandas as pd
    df = pd.read_parquet(os.path.join(RESULTS, "budget_curves", "per_repeat.parquet"))
    check("regret nonnegative", bool((df["regret3"] >= -1e-12).all()))
    check("regret bounded by 1", bool((df["regret3"] <= 1.0).all()))
    check("select3 equals a menu policy's eval mean",
          bool(np.isclose(df["select3"],
               df[["ev_ad_probe", "ev_glob_probe", "ev_trunc"]].values[
                   np.arange(len(df)),
                   df["pick3"].map({"ad_probe": 0, "glob_probe": 1, "trunc": 2}).values],
               atol=1e-12).all()))


# ---------- leakage ----------
def leakage_tests():
    import pandas as pd
    df = pd.read_parquet(os.path.join(RESULTS, "budget_curves", "per_repeat.parquet"))
    # probe ids count matches k_effective; probe/eval partition the eligible set
    src = os.path.join("/root/shift-study", "runs", "candidates")
    import csv as _csv
    eligible = {}
    for name in df["collection"].unique():
        with open(os.path.join(src, f"{name}_meta.csv")) as f:
            eligible[name] = sum(1 for r in _csv.DictReader(f) if int(r["nG"]) > 0)
    ok_count, ok_part, ok_dup = True, True, True
    for _, r in df.sample(min(len(df), 400), random_state=0).iterrows():
        qids = json.loads(r["probe_query_ids"])
        if len(qids) != r["k_effective"]:
            ok_count = False
        if len(set(qids)) != len(qids):
            ok_dup = False
        if r["k_effective"] + r["n_eval"] != eligible[r["collection"]]:
            ok_part = False
    check("probe ids count == k_effective (sampled 400 rows)", ok_count)
    check("probe ids unique", ok_dup)
    check("probe + eval partitions eligible queries", ok_part)
    # seed uniqueness within collection
    dup = df.groupby(["collection", "seed"]).size().max()
    check("seed uniqueness per (collection, draw)", int(dup) == 1)
    # planner replay: wrong_cert only defined for act
    pr = pd.read_parquet(os.path.join(RESULTS, "planner_replay", "planner_replay.parquet"))
    check("planner: abstain rows carry no selection loss",
          bool(pr[(pr.decision == "selection") & (pr.action == "abstain")]["loss"].isna().all()))
    check("planner: T never exceeds cap", bool((pr["final_T"] <= pr["cap"]).all()))


# ---------- regeneration ----------
def regeneration_tests():
    import pandas as pd
    df = pd.read_parquet(os.path.join(RESULTS, "budget_curves", "per_repeat.parquet"))
    summ = json.load(open(os.path.join(RESULTS, "budget_curves", "c1_summary.json")))
    g = df.groupby(["collection", "k_requested"]).agg(
        cal=("cal_loss", lambda s: (s <= 0.005).mean()),
        sel=("regret3", lambda s: (s <= 0.01).mean()))
    k10 = g.xs(10, level="k_requested")
    check("c1_summary regenerates from rows (cal@k10)",
          int((k10["cal"] >= 0.9).sum()) == summ["headline"]["n_collections_cal_ok_at_k10"])
    check("c1_summary regenerates from rows (sel@k10)",
          int((k10["sel"] >= 0.9).sum()) == summ["headline"]["n_collections_sel_ok_at_k10"])
    # legacy cross-check: k=10 first 20 repeats reproduce Block 1 dataset means
    legacy = {r["dataset"]: r for r in json.load(open(
        "/root/shift-study/runs/block1_confirm/agg.json"))["per_dataset"]}
    sub = df[(df.k_requested == 10) & (df.repeat_id < 20)]
    m = sub.groupby("collection")[["ev_ad_probe", "select3", "regret3"]].mean()
    ok = all(abs(m.loc[c, "ev_ad_probe"] - legacy[c]["ad_probe"]) < 1e-9 and
             abs(m.loc[c, "select3"] - legacy[c]["select3"]) < 1e-9 and
             abs(m.loc[c, "regret3"] - legacy[c]["regret3"]) < 1e-9
             for c in m.index)
    check("k=10 rows reproduce Block 1 legacy numbers exactly", ok)


# ---------- statistical (smoke) ----------
def statistical_tests():
    sim = json.load(open(os.path.join(RESULTS, "simulation", "sim_headline.json")))
    check("simulation: wrong-cert <= alpha in all selection cells",
          sim["wrong_cert_by_cell_ok"],
          f"max={sim['max_wrong_cert_rate_selection']}")
    check("simulation: budget shrinks with gap",
          sim["mean_T_large_gap"] < sim["mean_T_small_gap"])
    check("simulation: recal wrong-cert <= alpha",
          all(r["wrong_cert_rate"] <= 0.1 for r in sim["recal"]))


if __name__ == "__main__":
    unit_tests()
    leakage_tests()
    regeneration_tests()
    statistical_tests()
    print(f"\n{len(FAILURES)} failures" + (f": {FAILURES}" if FAILURES else " — all green"))
    sys.exit(1 if FAILURES else 0)
