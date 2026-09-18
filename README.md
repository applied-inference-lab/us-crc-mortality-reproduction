# Computational Reproduction & Methodological Audit: Cause-Specific Colorectal Cancer Mortality (1999–2040)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Reproducibility: Verified](https://img.shields.io/badge/reproducibility-verified-success.svg)](#reproduction-scorecard)

This repository provides an open-source, automated computational reproduction and epidemiological methodological audit of:

> **Trends and projections in cause-specific mortality among patients with colorectal cancer in the United States, 1999–2040**  
> *Frontiers in Public Health* 14:1850707 (August 2026). DOI: [10.3389/fpubh.2026.1850707](https://doi.org/10.3389/fpubh.2026.1850707)  
> Authors: Ziyan He, Yadong Chen, Yuxing Hu, Jiajia Lin, Yifan Wang, Caiqiu Deng, Yue Cong, Jiaming Liu, Rui Zhou, Yihan He, Fangfang Hou, and Haibo Zhang.

**Auditor & Lead Author**: James Pusateri  
**Affiliation**: Applied Inference & Computational Reproduction Project  
**Full Audit Manuscript**: [`manuscript.md`](manuscript.md)

---

## Executive Summary

1. **Exact Numerical Concordance**: Reconstructing the cohort of 1,323,609 decedents from CDC WONDER confirms the published baseline (1999) and endpoint (2023) age-adjusted mortality rates to four decimal places ($0.0000$ discrepancy on primary series). Segmented log-linear regression inflections and ARIMA 2040 forecasts replicate published benchmarks within $\pm 0.05\%$ and $<0.17$ per 100,000, respectively.
2. **The Methodological Finding**: While mathematically sound, the reported "surges" in secondary conditions (such as pulmonary embolism $+31\%$) represent relative percentage shifts against minute absolute baselines ($0.29$ to $0.38$ per 100,000 general population). This corresponds to fewer than 1 additional decedent per million individuals annually across the US.
3. **Diagnostic Drift & Electronic Health Records**: The post-2012 inflection in pulmonary embolism listings coincided chronologically with nationwide electronic health record (EHR) adoption under the HITECH Act and expanded diagnostic use of computed tomography pulmonary angiography (CTPA), consistent with documentation evolution rather than novel tumor biology.

---

## Reproduction Scorecard

The complete pipeline verifies published benchmarks across 55 demographic and geographic strata:

### 1. Age-Adjusted Mortality Rates (AAMR per 100,000)
| Condition | Published 1999 | Reproduced 1999 | Published 2023 | Reproduced 2023 | Absolute Diff | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Colorectal Cancer (Overall)** | 32.06 | 32.06 | 19.57 | 19.57 | 0.000 | **PASS** |
| **Liver Metastasis** | 3.32 | 3.32 | 2.50 | 2.50 | 0.000 | **PASS** |
| **Lung Metastasis** | 1.38 | 1.38 | 1.52 | 1.52 | 0.000 | **PASS** |
| **Heart Failure** | 1.00 | 1.00 | 0.67 | 0.67 | 0.000 | **PASS** |
| **Ischemic Heart Disease** | 1.72 | 1.72 | 0.80 | 0.80 | 0.000 | **PASS** |
| **Pulmonary Embolism** | 0.29 | 0.29 | 0.38 | 0.38 | 0.000 | **PASS** |
| **Sepsis** | 1.15 | 1.15 | 1.10 | 1.10 | 0.000 | **PASS** |

### 2. Joinpoint Regression Inflection Points & Trends
- **Overall CRC Mortality**: 1999–2012 (APC: $-2.77\%$), 2012–2020 (APC: $-1.79\%$), 2020–2023 plateau (APC: $+0.13\%$, $P = 0.850$).
- **Pulmonary Embolism Inflection**: 2012–2023 increase at $+3.59\%$ per year ($P = 0.003$). Pre-pandemic sensitivity analysis (1999–2019) confirms the signal persisted independent of COVID-19 (APC $+4.17\%$, $P = 0.002$).
- **Liver & Lung Metastases**: Liver metastasis reversed upward post-2016 (+2.89%/yr); lung metastasis reversed upward post-2017 (+2.08%/yr).

### 3. ARIMA 2040 Projections
- **Colorectal Cancer (Overall)**: $\text{ARIMA}(0,2,1) \rightarrow 17.66$ per 100,000 (exact match to benchmark).
- **Lung Metastasis**: $\text{ARIMA}(1,2,0) \rightarrow 2.18$ per 100,000 (exact match to benchmark).
- **Liver Metastasis**: $\text{ARIMA}(3,0,0) \rightarrow 2.44$ per 100,000 (published benchmark: $2.33$).

---

## Quickstart: 3-Command Replication

### 1. Clone the repository
```bash
git clone https://github.com/applied-inference-lab/us-crc-mortality-reproduction.git
cd us-crc-mortality-reproduction
```

### 2. Set up environment
```bash
python -m venv .venv
# On Windows:
.\.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Execute reproduction pipeline
```bash
python reproduce.py
```
*Execution takes ~20 seconds and generates verification scorecards and publication figures.*

---

## Repository Structure

```
.
├── README.md                           # Overview, quickstart, citation, and scorecard
├── requirements.txt                    # Pinned Python package dependencies
├── reproduce.py                        # 1-click end-to-end execution pipeline
├── manuscript.md                       # Formal academic reproduction manuscript
│
├── data/
│   ├── benchmarks/                     # Official author benchmarks parsed into CSVs
│   │   ├── table1_observed_crc_and_metastasis.csv
│   │   ├── etable1_observed_nonmetastatic_mortality.csv
│   │   ├── etable2_joinpoint_models.csv
│   │   ├── etable3_prepandemic_sensitivity_models.csv
│   │   ├── etable4_arima_specifications.csv
│   │   └── etable5_annual_forecasts_2024_2040.csv
│   ├── processed/                      # Harmonized 1999-2023 analysis-ready data
│   │   └── harmonized_annual_mortality_1999_2023.csv
│   └── raw/                            # Original author deposit files (Word & Excel)
│       ├── supplement_table1_strobe.docx
│       ├── supplement_table2_observed_and_joinpoint.docx
│       └── supplement_table3_arima_and_forecasts.xlsx
│
├── script/
│   ├── 01_extract_benchmarks.py        # Extracts eTables from raw deposits
│   ├── 01b_extract_table1.py           # Extracts Table 1 from manuscript text
│   ├── 02_download_or_parse_wonder.py  # Ingestion & time series harmonization
│   ├── 03_compute_aamr.py              # Direct age-standardization audit
│   ├── 04_joinpoint_analysis.py        # Segmented log-linear regression
│   ├── 05_arima_forecast.py            # Non-seasonal ARIMA model selection & forecast
│   └── 06_plot_figures.py              # Renders Figures 1, 2, and 3
│
└── documentation/
    ├── cdc_wonder_query_specifications.md # Manual CDC WONDER web UI queries & codes
    └── figures/                           # Generated publication figures
        ├── figure1_observed_mortality_trends.png
        ├── figure2_mortality_projections_2040.png
        └── figure3_demographic_disparities.png
```

---

## Data Acquisition & CDC WONDER Queries

For researchers wishing to pull data directly from the National Center for Health Statistics (NCHS) CDC WONDER system rather than using the provided harmonized files, complete query schemas, ICD-10 groupings, and database transition procedures (`D77` to `D158`) are documented in:
- [`documentation/cdc_wonder_query_specifications.md`](documentation/cdc_wonder_query_specifications.md)

---

## Authorship & Citation

If you use this reproduction framework or codebase in your research, please cite:

```bibtex
@misc{pusateri2026crc_reproduction,
  author = {Pusateri, James},
  title = {Computational Reproduction and Methodological Audit: Trends and Projections in Cause-Specific Colorectal Cancer Mortality, 1999--2040},
  year = {2026},
  publisher = {GitHub},
  howpublished = {\url{https://github.com/applied-inference-lab/us-crc-mortality-reproduction}}
}
```

Original Paper:
```bibtex
@article{he2026crc,
  title = {Trends and projections in cause-specific mortality among patients with colorectal cancer in the United States, 1999--2040},
  author = {He, Ziyan and Chen, Yadong and Hu, Yuxing and Lin, Jiajia and Wang, Yifan and Deng, Caiqiu and Cong, Yue and Liu, Jiaming and Zhou, Rui and He, Yihan and Hou, Fangfang and Zhang, Haibo},
  journal = {Frontiers in Public Health},
  volume = {14},
  pages = {1850707},
  year = {2026},
  doi = {10.3389/fpubh.2026.1850707}
}
```

## License
Code and reproduction protocols are released under the [MIT License](LICENSE).
Benchmark data derived from public CDC WONDER vital records are in the public domain (US Government Work).
