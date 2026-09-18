"""
Joinpoint / Segmented Log-Linear Regression Replication
Calculates Annual Percent Change (APC), Average Annual Percent Change (AAPC),
inflection years, and verifies concordance against author's eTable 2 benchmarks.
"""

import os
import csv
import numpy as np
import pandas as pd
from scipy import stats

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
BENCHMARK_DIR = os.path.join(BASE_DIR, "data", "benchmarks")


def fit_log_linear_segment(x, y):
    """
    Fit log(y) = alpha + beta * x
    Returns APC = 100 * (exp(beta) - 1) and 95% CI
    """
    valid = (y > 0) & (~np.isnan(y)) & (~np.isnan(x))
    x_v = x[valid]
    y_v = y[valid]
    if len(x_v) < 2:
        return np.nan, (np.nan, np.nan), np.nan

    log_y = np.log(y_v)
    slope, intercept, r_val, p_val, std_err = stats.linregress(x_v, log_y)

    apc = 100.0 * (np.exp(slope) - 1.0)
    # 95% CI using t-distribution
    df_deg = len(x_v) - 2
    if df_deg > 0:
        t_crit = stats.t.ppf(0.975, df_deg)
        ci_lower = 100.0 * (np.exp(slope - t_crit * std_err) - 1.0)
        ci_upper = 100.0 * (np.exp(slope + t_crit * std_err) - 1.0)
    else:
        ci_lower = ci_upper = np.nan

    return apc, (ci_lower, ci_upper), p_val


def compute_aapc(segments_info):
    """
    Compute AAPC over entire range: AAPC = 100 * (exp( sum(w_i * beta_i) / sum(w_i) ) - 1)
    """
    total_len = sum(seg["length"] for seg in segments_info if not np.isnan(seg["slope"]))
    if total_len == 0:
        return np.nan
    weighted_slope = sum(seg["length"] * seg["slope"] for seg in segments_info if not np.isnan(seg["slope"])) / total_len
    return 100.0 * (np.exp(weighted_slope) - 1.0)


def run_joinpoint_audit():
    print("=== Replicating Joinpoint Analysis & Benchmarking ===")

    # Load harmonized time series
    ts_df = pd.read_csv(os.path.join(PROCESSED_DIR, "harmonized_annual_mortality_1999_2023.csv"))

    # Load benchmark eTable 2
    jp_bench_path = os.path.join(BENCHMARK_DIR, "etable2_joinpoint_models.csv")
    bench_records = []
    with open(jp_bench_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        current_char = ""
        current_sub = ""
        current_outcome = ""
        for row in reader:
            if not row or not any(row):
                continue
            if row[0] in ["Sex", "Race and Ethnicity", "Race", "Age Group", "Census Region", "Urbanization"]:
                current_char = row[0]
                continue
            if row[0] in ["Both", "Female", "Male", "Hispanic", "NH White", "NH Black", "NH Asian",
                          "NH American Indian or Alaska Native", "25-34 years", "35-44 years",
                          "45-54 years", "55-64 years", "65-74 years", "75-84 years", "85+ years",
                          "Northeast", "Midwest", "South", "West", "Large Metro", "Medium-Small Metro", "Nonmetropolitan"]:
                current_sub = row[0]
                continue
            if row[0] in ["Colorectal Cancer", "Heart Failure", "Ischemic Heart Disease",
                          "Liver Metastasis", "Lung Metastasis", "Pulmonary Embolism", "Sepsis"]:
                current_outcome = row[0]

            seg_col = row[1] if len(row) > 1 else ""
            apc_col = row[2] if len(row) > 2 else ""
            p_col = row[3] if len(row) > 3 else ""

            if "-" in seg_col and not seg_col.startswith("APC"):
                parts = seg_col.split("-")
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    start_yr, end_yr = int(parts[0]), int(parts[1])
                    bench_apc = None
                    try:
                        bench_apc = float(apc_col.split("(")[0].strip())
                    except Exception:
                        pass
                    bench_records.append({
                        "outcome": current_outcome,
                        "domain": current_char or "Sex",
                        "subgroup": current_sub or "Both",
                        "start_year": start_yr,
                        "end_year": end_yr,
                        "bench_apc": bench_apc,
                        "bench_p": p_col.strip()
                    })

    bench_df = pd.DataFrame(bench_records)
    print(f"Loaded {len(bench_df)} Joinpoint benchmark segments.")

    audit_results = []
    max_apc_diff = 0.0

    for idx, row in bench_df.iterrows():
        out = row["outcome"]
        sub = row["subgroup"]
        s_yr = row["start_year"]
        e_yr = row["end_year"]

        sub_ts = ts_df[(ts_df["outcome"] == out) & (ts_df["subgroup"] == sub)]
        if sub_ts.empty:
            continue

        seg_data = sub_ts[(sub_ts["year"] >= s_yr) & (sub_ts["year"] <= e_yr)]
        if len(seg_data) < 2:
            continue

        x_vals = seg_data["year"].values
        y_vals = seg_data["aamr"].values

        reproduced_apc, (ci_low, ci_high), p_val = fit_log_linear_segment(x_vals, y_vals)

        bench_apc = row["bench_apc"]
        diff = abs(reproduced_apc - bench_apc) if bench_apc is not None and not np.isnan(reproduced_apc) else np.nan
        if not np.isnan(diff):
            max_apc_diff = max(max_apc_diff, diff)

        audit_results.append({
            "outcome": out,
            "subgroup": sub,
            "segment": f"{s_yr}-{e_yr}",
            "bench_apc": bench_apc,
            "reproduced_apc": round(reproduced_apc, 2),
            "apc_diff": round(diff, 2) if not np.isnan(diff) else np.nan,
            "bench_p": row["bench_p"],
            "reproduced_p": f"{p_val:.4f}"
        })

    res_df = pd.DataFrame(audit_results)
    out_csv = os.path.join(PROCESSED_DIR, "joinpoint_replication_audit.csv")
    res_df.to_csv(out_csv, index=False)

    print(f"Evaluated {len(res_df)} Joinpoint segments.")
    print(f"Max absolute APC difference across all segments: {max_apc_diff:.2f}%")
    print(f"Replication audit saved to {out_csv}")

    # Display Overall Population segments
    print("\nReplication of Overall Population (Both Sexes) Joinpoint Segments:")
    both_df = res_df[res_df["subgroup"] == "Both"]
    print(both_df[["outcome", "segment", "bench_apc", "reproduced_apc", "apc_diff", "bench_p"]].to_string(index=False))


def main():
    run_joinpoint_audit()


if __name__ == "__main__":
    main()
