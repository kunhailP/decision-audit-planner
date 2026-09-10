#!/usr/bin/env python3
"""Interval reporting for the P4 prospective primary run (no re-execution).

Reads 05_results/prospective_android/primary_run.parquet and reports, per
decision: ACT count, wrong-certificate count, wrong-cert rate with an exact
Clopper–Pearson 95% interval, and the conditional rate P(wrong | ACT) with
its interval.  The primary criterion (rate <= alpha) is a point-estimate
test; the intervals show what the 50-repeat run can and cannot exclude.
"""
import os
import pandas as pd
from scipy.stats import beta

HUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def clopper_pearson(k, n, level=0.95):
    a = (1 - level) / 2
    lo = beta.ppf(a, k, n - k + 1) if k > 0 else 0.0
    hi = beta.ppf(1 - a, k + 1, n - k) if k < n else 1.0
    return lo, hi


def main():
    df = pd.read_parquet(os.path.join(HUB, "05_results", "prospective_android", "primary_run.parquet"))
    rows = []
    for dec, sub in df.groupby("decision"):
        n = len(sub); acts = int((sub["action"] == "act").sum()); wrong = int(sub["wrong_cert"].sum())
        lo, hi = clopper_pearson(wrong, n)
        clo, chi = clopper_pearson(wrong, acts) if acts else (float("nan"), float("nan"))
        rows.append(dict(decision=dec, repeats=n, act=acts, wrong=wrong,
                         wrong_rate=wrong / n, wrong_rate_ci95=f"[{lo:.3f}, {hi:.3f}]",
                         wrong_given_act=wrong / acts if acts else float("nan"),
                         wrong_given_act_ci95=f"[{clo:.3f}, {chi:.3f}]",
                         mean_T=float(sub["final_T"].mean())))
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(HUB, "05_results", "prospective_android", "primary_intervals.csv"), index=False)
    pd.set_option("display.width", 200)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
