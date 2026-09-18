"""
Generate publication-grade figures matching Figures 1, 2, and 3 in the published paper.
Saves PNG charts to documentation/figures/.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
FIG_DIR = os.path.join(BASE_DIR, "documentation", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# Styling configuration
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "Arial"
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8


def plot_figure_1(ts_df):
    """
    Figure 1: Overall trends in colorectal cancer and major contributing causes, 1999-2023.
    Panel A: Colorectal cancer overall
    Panel B: 6 contributing causes
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)

    # Panel A: Overall CRC
    crc_df = ts_df[(ts_df["outcome"] == "Colorectal Cancer") & (ts_df["subgroup"] == "Both")].sort_values("year")
    ax1.plot(crc_df["year"], crc_df["aamr"], marker="o", markersize=4, color="#1f77b4", linewidth=2, label="Colorectal cancer AAMR")
    # Annotate joinpoints (2012, 2020)
    ax1.axvline(2012, color="#7f7f7f", linestyle="--", alpha=0.7)
    ax1.axvline(2020, color="#7f7f7f", linestyle="--", alpha=0.7)
    ax1.text(2005, 27, "1999-2012\nAPC: -2.77%*", ha="center", fontsize=9, bbox=dict(boxstyle="round,pad=0.3", facecolor="#f0f0f0", edgecolor="#ccc"))
    ax1.text(2016, 21.5, "2012-2020\nAPC: -1.79%*", ha="center", fontsize=9, bbox=dict(boxstyle="round,pad=0.3", facecolor="#f0f0f0", edgecolor="#ccc"))
    ax1.text(2021.5, 20.2, "2020-2023\nAPC: +0.13%", ha="center", fontsize=9, bbox=dict(boxstyle="round,pad=0.3", facecolor="#f0f0f0", edgecolor="#ccc"))

    ax1.set_title("(A) Overall Colorectal Cancer Mortality, 1999–2023", fontsize=12, fontweight="bold", pad=10)
    ax1.set_xlabel("Year of Death", fontsize=10)
    ax1.set_ylabel("Age-Adjusted Mortality Rate (per 100,000)", fontsize=10)
    ax1.set_xlim(1998, 2024)
    ax1.set_ylim(15, 35)

    # Panel B: Contributing conditions
    conditions = [
        ("Liver Metastasis", "#d62728", "-"),
        ("Lung Metastasis", "#2ca02c", "-"),
        ("Ischemic Heart Disease", "#ff7f0e", "--"),
        ("Sepsis", "#9467bd", "--"),
        ("Heart Failure", "#8c564b", ":"),
        ("Pulmonary Embolism", "#17becf", "-.")
    ]

    for cond, color, style in conditions:
        cdf = ts_df[(ts_df["outcome"] == cond) & (ts_df["subgroup"] == "Both")].sort_values("year")
        if not cdf.empty:
            ax2.plot(cdf["year"], cdf["aamr"], marker="s", markersize=3, color=color, linestyle=style, linewidth=1.8, label=cond)

    ax2.set_title("(B) Contributing Causes of Death in Colorectal Cancer, 1999–2023", fontsize=12, fontweight="bold", pad=10)
    ax2.set_xlabel("Year of Death", fontsize=10)
    ax2.set_ylabel("Age-Adjusted Mortality Rate (per 100,000)", fontsize=10)
    ax2.set_xlim(1998, 2024)
    ax2.set_ylim(0, 4.0)
    ax2.legend(frameon=True, facecolor="white", edgecolor="#ddd", fontsize=8.5, loc="upper right")

    plt.tight_layout()
    out_path = os.path.join(FIG_DIR, "figure1_observed_mortality_trends.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Saved Figure 1 -> {out_path}")


def plot_figure_2(ts_df, fc_df):
    """
    Figure 2: Historical and Projected Mortality Rates Through 2040.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)

    # Panel A: CRC Projections
    hist_crc = ts_df[(ts_df["outcome"] == "Colorectal Cancer") & (ts_df["subgroup"] == "Both")].sort_values("year")
    fc_crc = fc_df[(fc_df["outcome"] == "Colorectal cancer") & (fc_df["subgroup"] == "Both")].sort_values("year")

    ax1.plot(hist_crc["year"], hist_crc["aamr"], color="#1f77b4", linewidth=2, label="Observed (1999-2023)")
    if not fc_crc.empty:
        # Link 2023 to 2024
        link_years = [2023] + list(fc_crc["year"])
        link_rates = [hist_crc.iloc[-1]["aamr"]] + list(fc_crc["point_forecast"])
        ax1.plot(link_years, link_rates, color="#d62728", linestyle="--", linewidth=2, label="ARIMA(0,2,1) Forecast (2024-2040)")
        ax1.fill_between(fc_crc["year"], fc_crc["lower_95_ci"], fc_crc["upper_95_ci"], color="#d62728", alpha=0.15, label="95% Prediction Interval")

    ax1.set_title("(A) Colorectal Cancer Mortality Projections to 2040", fontsize=12, fontweight="bold", pad=10)
    ax1.set_xlabel("Year", fontsize=10)
    ax1.set_ylabel("Age-Adjusted Mortality Rate (per 100,000)", fontsize=10)
    ax1.set_xlim(1998, 2041)
    ax1.legend(frameon=True, facecolor="white", edgecolor="#ddd", fontsize=9)

    # Panel B: Liver vs Lung Metastasis Projections
    colors = {"Liver Metastasis": "#d62728", "Lung Metastasis": "#2ca02c"}
    for cond in ["Liver Metastasis", "Lung Metastasis"]:
        h_df = ts_df[(ts_df["outcome"] == cond) & (ts_df["subgroup"] == "Both")].sort_values("year")
        f_df = fc_df[(fc_df["outcome"] == cond) & (fc_df["subgroup"] == "Both")].sort_values("year")

        col = colors[cond]
        ax2.plot(h_df["year"], h_df["aamr"], color=col, linewidth=2, label=f"{cond} Observed")
        if not f_df.empty:
            link_years = [2023] + list(f_df["year"])
            link_rates = [h_df.iloc[-1]["aamr"]] + list(f_df["point_forecast"])
            ax2.plot(link_years, link_rates, color=col, linestyle="--", linewidth=2, label=f"{cond} Projected")
            ax2.fill_between(f_df["year"], np.maximum(0, f_df["lower_95_ci"]), f_df["upper_95_ci"], color=col, alpha=0.12)

    ax2.set_title("(B) Liver and Lung Metastasis Projections to 2040", fontsize=12, fontweight="bold", pad=10)
    ax2.set_xlabel("Year", fontsize=10)
    ax2.set_ylabel("Age-Adjusted Mortality Rate (per 100,000)", fontsize=10)
    ax2.set_xlim(1998, 2041)
    ax2.set_ylim(0, 4.5)
    ax2.legend(frameon=True, facecolor="white", edgecolor="#ddd", fontsize=8.5, loc="upper left")

    plt.tight_layout()
    out_path = os.path.join(FIG_DIR, "figure2_mortality_projections_2040.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Saved Figure 2 -> {out_path}")


def plot_figure_3(ts_df):
    """
    Figure 3: Disparities by Sex and Race/Ethnicity.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)

    # Panel A: Sex Disparities (CRC, Liver, Lung)
    for sub, col in [("Male", "#1f77b4"), ("Female", "#e377c2")]:
        cdf = ts_df[(ts_df["outcome"] == "Colorectal Cancer") & (ts_df["subgroup"] == sub)].sort_values("year")
        ax1.plot(cdf["year"], cdf["aamr"], color=col, linewidth=2, label=f"CRC ({sub})")
        ldf = ts_df[(ts_df["outcome"] == "Liver Metastasis") & (ts_df["subgroup"] == sub)].sort_values("year")
        ax1.plot(ldf["year"], ldf["aamr"], color=col, linestyle="--", linewidth=1.5, label=f"Liver Met ({sub})")

    ax1.set_title("(A) Mortality Disparities by Sex, 1999–2023", fontsize=12, fontweight="bold", pad=10)
    ax1.set_xlabel("Year of Death", fontsize=10)
    ax1.set_ylabel("Age-Adjusted Mortality Rate (per 100,000)", fontsize=10)
    ax1.set_xlim(1998, 2024)
    ax1.legend(frameon=True, facecolor="white", edgecolor="#ddd", fontsize=8.5)

    # Panel B: Racial/Ethnic Disparities in CRC Mortality
    races = [
        ("NH Black", "#d62728", "-"),
        ("NH White", "#1f77b4", "-"),
        ("Hispanic", "#ff7f0e", "--"),
        ("NH Asian", "#2ca02c", ":")
    ]
    for r, col, style in races:
        rdf = ts_df[(ts_df["outcome"] == "Colorectal Cancer") & (ts_df["subgroup"] == r)].sort_values("year")
        if not rdf.empty:
            ax2.plot(rdf["year"], rdf["aamr"], color=col, linestyle=style, linewidth=2, label=r)

    ax2.set_title("(B) Colorectal Cancer Mortality Disparities by Race/Ethnicity", fontsize=12, fontweight="bold", pad=10)
    ax2.set_xlabel("Year of Death", fontsize=10)
    ax2.set_ylabel("Age-Adjusted Mortality Rate (per 100,000)", fontsize=10)
    ax2.set_xlim(1998, 2024)
    ax2.legend(frameon=True, facecolor="white", edgecolor="#ddd", fontsize=9)

    plt.tight_layout()
    out_path = os.path.join(FIG_DIR, "figure3_demographic_disparities.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Saved Figure 3 -> {out_path}")


def main():
    ts_df = pd.read_csv(os.path.join(PROCESSED_DIR, "harmonized_annual_mortality_1999_2023.csv"))
    fc_df = pd.read_csv(os.path.join(PROCESSED_DIR, "reproduced_annual_forecasts_2024_2040.csv"))

    plot_figure_1(ts_df)
    plot_figure_2(ts_df, fc_df)
    plot_figure_3(ts_df)


if __name__ == "__main__":
    main()
