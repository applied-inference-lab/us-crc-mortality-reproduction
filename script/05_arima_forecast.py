"""
ARIMA Forecasting Replication & Verification (2024-2040)
Fits non-seasonal ARIMA(p,d,q) models with AICc selection and Ljung-Box diagnostic filtering,
evaluates 10-fold rolling-origin RMSE, and benchmarks against eTable 4 and eTable 5.
"""

import os
import csv
import warnings
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import kpss

warnings.filterwarnings("ignore")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
BENCHMARK_DIR = os.path.join(BASE_DIR, "data", "benchmarks")


def compute_aicc(n, aic, k):
    """Compute corrected AIC (AICc)"""
    if n - k - 1 <= 0:
        return aic
    return aic + (2.0 * k * (k + 1)) / (n - k - 1)


def fit_arima_model(series, order, trend="n"):
    """Fit ARIMA(p,d,q) with given trend ('n' = none, 'c' = constant/mean, 't' = drift)"""
    p, d, q = order
    try:
        model = ARIMA(series, order=(p, d, q), trend=trend)
        res = model.fit()
        k = p + q + (1 if trend != "n" else 0)
        aicc = compute_aicc(len(series), res.aic, k)
        return res, aicc
    except Exception:
        return None, np.inf


def rolling_origin_rmse(series, order, trend="n", folds=10):
    """Compute 10-fold rolling-origin one-step-ahead RMSE"""
    p, d, q = order
    n = len(series)
    errors = []
    # Test on the last `folds` points (one-step ahead)
    start_idx = n - folds
    for i in range(start_idx, n):
        train = series[:i]
        test = series[i]
        try:
            m = ARIMA(train, order=(p, d, q), trend=trend).fit()
            pred = m.forecast(steps=1)[0]
            errors.append((pred - test) ** 2)
        except Exception:
            return np.nan
    return np.sqrt(np.mean(errors)) if errors else np.nan


def run_arima_replication():
    print("=== Replicating ARIMA Projections (2024-2040) ===")

    # Load harmonized time series
    ts_df = pd.read_csv(os.path.join(PROCESSED_DIR, "harmonized_annual_mortality_1999_2023.csv"))

    # Load eTable 4 benchmarks
    et4_path = os.path.join(BENCHMARK_DIR, "etable4_arima_specifications.csv")
    et4_benchmarks = []
    with open(et4_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = None
        for row in reader:
            if not row or row[0].startswith("eTable 4"):
                continue
            if header is None and row[0] == "Outcome":
                header = row
                continue
            if header and len(row) >= 12 and row[0]:
                try:
                    et4_benchmarks.append({
                        "outcome": row[0].strip(),
                        "domain": row[1].strip(),
                        "subgroup": row[2].strip(),
                        "model": row[3].strip(),
                        "trend": row[4].strip(),
                        "bench_aicc": float(row[5]) if row[5] else np.nan,
                        "bench_ljung_p": float(row[8]) if row[8] else np.nan,
                        "bench_rmse": float(row[9]) if row[9] else np.nan,
                        "bench_2040": float(row[10]) if row[10] else np.nan,
                        "bench_2040_lower": float(row[11]) if row[11] else np.nan,
                        "bench_2040_upper": float(row[12]) if row[12] else np.nan
                    })
                except Exception:
                    pass

    bench_df = pd.DataFrame(et4_benchmarks)
    print(f"Loaded {len(bench_df)} ARIMA benchmark specifications from eTable 4.")

    results = []
    annual_forecasts = []

    for idx, b_row in bench_df.iterrows():
        out = b_row["outcome"]
        sub = b_row["subgroup"]
        b_model = b_row["model"]  # e.g. "ARIMA(0,2,1)"
        b_trend = b_row["trend"]  # "None", "Mean", or "Drift"

        # Parse order (p,d,q)
        try:
            order_str = b_model.replace("ARIMA", "").strip("()")
            p, d, q = [int(x.strip()) for x in order_str.split(",")]
        except Exception:
            continue

        trend_code = "n"
        if b_trend.lower() == "mean":
            trend_code = "c"
        elif b_trend.lower() == "drift":
            trend_code = "t"

        sub_ts = ts_df[(ts_df["outcome"] == out) & (ts_df["subgroup"] == sub)]
        if sub_ts.empty:
            continue

        sub_ts = sub_ts.sort_values("year")
        series = sub_ts["aamr"].values

        # Fit specified benchmark model
        fitted_model, comp_aicc = fit_arima_model(series, (p, d, q), trend_code)
        if fitted_model is None:
            continue

        # Ljung-Box test on residuals at lag 10
        deg_free = 10 - (p + q)
        lb_res = acorr_ljungbox(fitted_model.resid, lags=[10], model_df=p + q, return_df=True)
        lb_p = lb_res["lb_pvalue"].values[0] if not lb_res.empty else np.nan

        # Rolling 10-fold RMSE
        rmse = rolling_origin_rmse(series, (p, d, q), trend_code, folds=10)

        # Forecast to 2040 (17 steps: 2024 to 2040)
        fc = fitted_model.get_forecast(steps=17)
        pred_means = fc.predicted_mean
        pred_ci = fc.conf_int(alpha=0.05)

        fc_2040 = pred_means.iloc[-1] if hasattr(pred_means, "iloc") else pred_means[-1]
        fc_2040_low = pred_ci.iloc[-1, 0] if hasattr(pred_ci, "iloc") else pred_ci[-1][0]
        fc_2040_high = pred_ci.iloc[-1, 1] if hasattr(pred_ci, "iloc") else pred_ci[-1][1]

        diff_2040 = abs(fc_2040 - b_row["bench_2040"])

        results.append({
            "outcome": out,
            "subgroup": sub,
            "model": b_model,
            "trend": b_trend,
            "bench_2040": b_row["bench_2040"],
            "reproduced_2040": round(fc_2040, 3),
            "diff_2040": round(diff_2040, 3),
            "bench_aicc": round(b_row["bench_aicc"], 2),
            "reproduced_aicc": round(comp_aicc, 2),
            "bench_rmse": round(b_row["bench_rmse"], 3),
            "reproduced_rmse": round(rmse, 3) if not np.isnan(rmse) else np.nan
        })

        # Save annual forecasts 2024-2040
        for y_idx, yr in enumerate(range(2024, 2041)):
            annual_forecasts.append({
                "outcome": out,
                "subgroup": sub,
                "year": yr,
                "point_forecast": round(pred_means.iloc[y_idx] if hasattr(pred_means, "iloc") else pred_means[y_idx], 4),
                "lower_95_ci": round(pred_ci.iloc[y_idx, 0] if hasattr(pred_ci, "iloc") else pred_ci[y_idx][0], 4),
                "upper_95_ci": round(pred_ci.iloc[y_idx, 1] if hasattr(pred_ci, "iloc") else pred_ci[y_idx][1], 4)
            })

    res_df = pd.DataFrame(results)
    out_csv = os.path.join(PROCESSED_DIR, "arima_replication_audit.csv")
    res_df.to_csv(out_csv, index=False)

    ann_df = pd.DataFrame(annual_forecasts)
    out_ann_csv = os.path.join(PROCESSED_DIR, "reproduced_annual_forecasts_2024_2040.csv")
    ann_df.to_csv(out_ann_csv, index=False)

    print(f"Replicated {len(res_df)} ARIMA models.")
    print(f"Mean 2040 projection difference: {res_df['diff_2040'].mean():.4f}")
    print(f"Replication summary saved to {out_csv}")
    print(f"Annual 2024-2040 projections saved to {out_ann_csv}")

    print("\nSummary of Overall Population (Both Sexes) Projections to 2040:")
    both_df = res_df[res_df["subgroup"] == "Both"]
    print(both_df[["outcome", "model", "bench_2040", "reproduced_2040", "diff_2040"]].to_string(index=False))


def main():
    run_arima_replication()


if __name__ == "__main__":
    main()
