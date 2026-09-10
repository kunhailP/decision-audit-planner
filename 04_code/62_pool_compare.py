#!/usr/bin/env python3
"""Go/no-go #1 (2027 design §6.1): does the decision structure survive a modern
retrieval stack?

Runs the frozen fixed-budget protocol of 20_budget_curves.py (LODO training,
same policies, same seeds formula) on the legacy and modern candidate pools
built by 61_build_pool.py, and reports per collection and stack:
  pool relevant-recall (nG_in_pool / nG), best-policy set-F1, 1st-2nd policy
  gap, calibration loss and selection regret at k in {10, 30, 50}.

Usage: python3 62_pool_compare.py --pools <dir> [--repeats 50]
"""
import argparse, csv, importlib.util, json, os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
HUB = os.path.dirname(HERE)
NAMES = ["nfcorpus", "scifact", "arguana", "cqadupstack-android"]


def pool_recall(cand_dir, name):
    rel_in_pool = {}
    with open(os.path.join(cand_dir, f"{name}.csv")) as f:
        for r in csv.DictReader(f):
            if int(float(r["relevant"])):
                rel_in_pool[r["qid"]] = rel_in_pool.get(r["qid"], 0) + 1
    nG = {r["qid"]: int(r["nG"]) for r in csv.DictReader(open(os.path.join(cand_dir, f"{name}_meta.csv")))}
    fr = [rel_in_pool.get(q, 0) / n for q, n in nG.items() if n > 0]
    return float(np.mean(fr))


def run_stack(pools, stack, repeats, out_root):
    src = os.path.join(pools, stack)
    out = os.path.join(out_root, stack)
    spec = importlib.util.spec_from_file_location("bc", os.path.join(HERE, "20_budget_curves.py"))
    bc = importlib.util.module_from_spec(spec); spec.loader.exec_module(bc)
    bc.ALL_DATASETS = NAMES
    bc.UNTOUCHED = {"cqadupstack-android"}
    bc.K_GRID = [10, 30, 50]
    sys.argv = ["20_budget_curves.py", "--source", src, "--out", out, "--repeats", str(repeats)]
    bc.main()
    return out


def summarize(out, pools, stack):
    import pandas as pd
    df = pd.read_parquet(os.path.join(out, "per_repeat.parquet"))
    rows = []
    for name, g in df.groupby("collection"):
        rec = pool_recall(os.path.join(pools, stack, "runs", "candidates"), name)
        means = {p: g[f"ev_{p}"].mean() for p in ["ad_probe", "glob_probe", "trunc"]}
        top = sorted(means.values(), reverse=True)
        row = dict(stack=stack, collection=name, pool_recall=rec, best_f1=top[0], gap12=top[0] - top[1],
                   best_policy=max(means, key=means.get), ad_c=g["ev_ad_c"].mean())
        for k, gk in g.groupby("k_requested"):
            row[f"cal_loss@{k}"] = gk["cal_loss"].mean()
            row[f"cal_ok@{k}"] = (gk["cal_loss"] <= 0.005).mean()
            row[f"regret@{k}"] = gk["regret3"].mean()
            row[f"sel_ok@{k}"] = (gk["regret3"] <= 0.01).mean()
        rows.append(row)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pools", required=True); ap.add_argument("--repeats", type=int, default=50)
    ap.add_argument("--out", default=os.path.join(HUB, "05_results", "pool_compare"))
    a = ap.parse_args()
    import pandas as pd
    tabs = []
    for stack in ["legacy", "modern"]:
        out = run_stack(a.pools, stack, a.repeats, a.out)
        tabs.append(summarize(out, a.pools, stack))
    tab = pd.concat(tabs)
    tab.to_csv(os.path.join(a.out, "pool_compare.csv"), index=False)
    pd.set_option("display.width", 250)
    print(tab.round(4).to_string(index=False))
