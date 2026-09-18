"""
Compute and verify Age-Adjusted Mortality Rates (AAMR) against author benchmarks
for all 7 conditions (Colorectal Cancer, Liver Metastasis, Lung Metastasis,
Heart Failure, Ischemic Heart Disease, Pulmonary Embolism, Sepsis).
"""

import os
import csv
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCHMARK_DIR = os.path.join(BASE_DIR, "data", "benchmarks")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
OUT_DIR = os.path.join(BASE_DIR, "data", "processed")

# Year 2000 Standard Population proportions for age groups 25+
# Census 2000 standard weights for 10-year age groups 25-34 to 85+
STD_WEIGHTS_2000 = {
    "25-34": 0.20966,
    "35-44": 0.25146,
    "45-54": 0.20850,
    "55-64": 0.13492,
    "65-74": 0.10212,
    "75-84": 0.06934,
    "85+":   0.02400
}


def load_harmonized_data():
    csv_path = os.path.join(PROCESSED_DIR, "harmonized_annual_mortality_1999_2023.csv")
    df = pd.read_csv(csv_path)
    return df


def audit_rates_against_benchmarks(df):
    """
    Compare 1999 and 2023 values in harmonized dataset with published Table 1 and eTable 1 benchmarks.
    """
    print("=== Auditing Harmonized Rates against Published Benchmarks ===")

    # 1. Load Table 1
    t1_path = os.path.join(BENCHMARK_DIR, "table1_observed_crc_and_metastasis.csv")
    t1_benchmarks = []
    with open(t1_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        next(reader)
        for row in reader:
            if not row:
                continue
            char = row[0].split(":")[-1].strip()
            # parse CRC 1999 and 2023
            try:
                t1_benchmarks.append({
                    "outcome": "Colorectal Cancer",
                    "subgroup": char,
                    "bench_1999": float(row[1].split("(")[0].strip()),
                    "bench_2023": float(row[2].split("(")[0].strip())
                })
            except Exception:
                pass
            # parse Liver 1999 and 2023
            try:
                t1_benchmarks.append({
                    "outcome": "Liver Metastasis",
                    "subgroup": char,
                    "bench_1999": float(row[4].split("(")[0].strip()),
                    "bench_2023": float(row[5].split("(")[0].strip())
                })
            except Exception:
                pass
            # parse Lung 1999 and 2023
            try:
                t1_benchmarks.append({
                    "outcome": "Lung Metastasis",
                    "subgroup": char,
                    "bench_1999": float(row[7].split("(")[0].strip()),
                    "bench_2023": float(row[8].split("(")[0].strip())
                })
            except Exception:
                pass

    # 2. Load eTable 1
    et1_path = os.path.join(BENCHMARK_DIR, "etable1_observed_nonmetastatic_mortality.csv")
    with open(et1_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 14 or row[0].startswith("eTable") or row[0] in ["Characteristic", "Sex", "Race,", "Age Group,", "Census Region,", "Urbanization1,"]:
                continue
            char = row[0].strip()
            # HF
            try:
                t1_benchmarks.append({
                    "outcome": "Heart Failure",
                    "subgroup": char,
                    "bench_1999": float(row[1].split("(")[0].strip()),
                    "bench_2023": float(row[2].split("(")[0].strip())
                })
            except Exception:
                pass
            # IHD
            try:
                t1_benchmarks.append({
                    "outcome": "Ischemic Heart Disease",
                    "subgroup": char,
                    "bench_1999": float(row[4].split("(")[0].strip()),
                    "bench_2023": float(row[5].split("(")[0].strip())
                })
            except Exception:
                pass
            # PE
            try:
                t1_benchmarks.append({
                    "outcome": "Pulmonary Embolism",
                    "subgroup": char,
                    "bench_1999": float(row[7].split("(")[0].strip()),
                    "bench_2023": float(row[8].split("(")[0].strip())
                })
            except Exception:
                pass
            # Sepsis
            try:
                t1_benchmarks.append({
                    "outcome": "Sepsis",
                    "subgroup": char,
                    "bench_1999": float(row[10].split("(")[0].strip()),
                    "bench_2023": float(row[11].split("(")[0].strip())
                })
            except Exception:
                pass

    bench_df = pd.DataFrame(t1_benchmarks)
    results = []
    max_diff_1999 = 0.0
    max_diff_2023 = 0.0

    for idx, b_row in bench_df.iterrows():
        sub = b_row["subgroup"]
        out = b_row["outcome"]
        sub_df = df[(df["outcome"] == out) & (df["subgroup"] == sub)]
        if sub_df.empty:
            continue
        target_year_end = 2020 if sub in ["Large Metro", "Medium-Small Metro", "Nonmetropolitan", "Large metro", "Medium-small metro"] else 2023
        r1999_series = sub_df[sub_df["year"] == 1999]["aamr"].values
        rend_series = sub_df[sub_df["year"] == target_year_end]["aamr"].values

        val_1999 = r1999_series[0] if len(r1999_series) > 0 else np.nan
        val_end = rend_series[0] if len(rend_series) > 0 else np.nan

        diff_1999 = abs(val_1999 - b_row["bench_1999"])
        diff_end = abs(val_end - b_row["bench_2023"])

        max_diff_1999 = max(max_diff_1999, diff_1999)
        max_diff_2023 = max(max_diff_2023, diff_end)

        results.append({
            "outcome": out,
            "subgroup": sub,
            "bench_1999": b_row["bench_1999"],
            "reproduced_1999": val_1999,
            "diff_1999": round(diff_1999, 4),
            "bench_end": b_row["bench_2023"],
            "reproduced_end": val_end,
            "end_year": target_year_end,
            "diff_end": round(diff_end, 4)
        })

    res_df = pd.DataFrame(results)
    out_audit_csv = os.path.join(PROCESSED_DIR, "aamr_audit_vs_benchmarks.csv")
    res_df.to_csv(out_audit_csv, index=False)
    print(f"Audited {len(res_df)} outcome-subgroup benchmark pairs.")
    print(f"Max absolute difference for 1999: {max_diff_1999:.4f}")
    print(f"Max absolute difference for 2023: {max_diff_2023:.4f}")
    print(f"Benchmark audit results saved to {out_audit_csv}")

    # Summary table for Both sexes
    print("\nSummary for Overall Population (Both Sexes):")
    both_df = res_df[res_df["subgroup"] == "Both"]
    print(both_df[["outcome", "bench_1999", "reproduced_1999", "bench_end", "reproduced_end"]].to_string(index=False))


def main():
    df = load_harmonized_data()
    audit_rates_against_benchmarks(df)


if __name__ == "__main__":
    main()
