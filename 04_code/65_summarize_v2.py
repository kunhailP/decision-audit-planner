#!/usr/bin/env python3
"""Join planner_v2 summaries (both stacks) with judge diagnostics into one table."""
import json, os, sys
import pandas as pd

HUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root = os.path.join(HUB, "05_results", "planner_v2")
tabs, diag_rows = [], []
for st in ["legacy", "modern"]:
    d = os.path.join(root, st)
    if not os.path.exists(os.path.join(d, "summary.csv")):
        continue
    t = pd.read_csv(os.path.join(d, "summary.csv")); t.insert(0, "stack", st); tabs.append(t)
    for c, v in json.load(open(os.path.join(d, "judge_diagnostics.json"))).items():
        diag_rows.append(dict(stack=st, collection=c, **v))
pd.set_option("display.width", 250)
if tabs:
    t = pd.concat(tabs)
    piv = t.pivot_table(index=["stack", "collection"], columns="method",
                        values=["act_rate", "mean_T", "wrong_cert_rate"])
    print(piv.round(3).to_string())
    t.to_csv(os.path.join(root, "summary_all.csv"), index=False)
if diag_rows:
    dg = pd.DataFrame(diag_rows)
    print(dg.round(3).to_string(index=False))
    dg.to_csv(os.path.join(root, "judge_diagnostics_all.csv"), index=False)
