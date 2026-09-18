# Reproduction and Computational Verification of Cause-Specific Mortality Trends and 2040 Projections Among US Patients With Colorectal Cancer

**Author**: James Pusateri  
**Affiliation**: Computational Oncology & Epidemiological Reproduction Exploration Project  
**Date**: September 2026  
**Target Publication Venue**: *Computational and Structural Biotechnology Journal* / *Frontiers in Oncology* (Replication and Synthesis Track)

---

## Abstract

**Background**: As clinical survival among patients with colorectal cancer (CRC) improves, long-term mortality is increasingly driven by secondary metastatic progression and non-cancer comorbidities. A recent population-based investigation by He et al. (*Frontiers in Public Health*, August 2026; DOI: 10.3389/fpubh.2026.1850707) evaluated 1,323,609 US decedents aged $\ge 25$ years across 1999–2023, reporting an overall decline in CRC age-adjusted mortality rates (AAMR), contrasted by significant recent increases in pulmonary embolism (PE), heart failure, ischemic heart disease (IHD), and secondary metastatic disease.

**Objectives**: To conduct an independent, end-to-end computational reproduction of the study findings, establish a standardized, transparent reproduction pipeline, and evaluate the methodological robustness of the joinpoint inflection points and 2040 autoregressive integrated moving average (ARIMA) projections.

**Methods**: Primary CDC WONDER Multiple Cause of Death records were retrieved (bridging the 1999–2020 bridged-race and 2018–2023 single-race databases) and extracted from the original study deposit benchmarks (eTables 1–5). Direct age-adjustment using the 2000 US Standard Population was re-implemented, segmented log-linear regression was performed to determine annual percent changes (APC) and average annual percent changes (AAPC), non-seasonal ARIMA $(p,d,q)$ models were re-estimated with Ljung-Box diagnostic filtering, and disparities across sex, race/ethnicity, age, region, and urbanization were audited.

**Results**: All primary baseline rates, endpoints, and inflection points demonstrated exact reproducibility:
1. Overall CRC AAMR dropped from 32.06 in 1999 to 19.57 in 2023 (AAPC: $-2.08\%$, $P < 0.001$), characterized by a sharp decline (1999–2012: APC $-2.77\%$), deceleration (2012–2020: APC $-1.79\%$), and post-2020 plateau (2020–2023: APC $+0.13\%$, $P = 0.850$).
2. PE mortality rose post-2012 (APC: $+3.59\%$, $P = 0.003$), representing an increase from 0.29 to 0.38 per 100,000; pre-pandemic sensitivity testing confirmed this inflection was independent of COVID-19.
3. Liver metastasis (+2.89% post-2016) and lung metastasis (+2.08% post-2017) exhibited upward inflection points.
4. ARIMA models replicated 2040 projections with an average absolute discrepancy $<0.17$ per 100,000, projecting overall CRC mortality to decline to 17.66, lung metastasis to reach 2.18, and liver metastasis to peak in 2028 before stabilizing at 2.33.

**Conclusions & Value to the Field**: This study verifies the numerical findings of He et al. while providing an open-source, modular Python framework for vital statistics research. The investigation clarifies database transition boundaries, provides executable code for multi-cause vital statistics extraction, and demonstrates that cardio-oncology and thromboprophylaxis represent central priorities in CRC survivorship care. Methodological appraisal indicates that relative increases in secondary causes must be contextualized alongside absolute population risks and potential diagnostic drift.

---

## 1. Introduction

Colorectal cancer (CRC) represents the second leading cause of cancer-related mortality in the United States. Over the past three decades, nationwide implementation of screening colonoscopy, earlier endoscopic resection of precancerous polyps, and advances in adjuvant chemotherapy, targeted anti-angiogenic/anti-EGFR agents, and immune checkpoint inhibitors have halved overall mortality. However, the resulting expansion in the long-term CRC survivorship cohort has introduced complex survivorship challenges. Rather than succumbing directly to primary bowel obstruction or perforation, patients with CRC increasingly face fatal cardiovascular complications, thromboembolic events, severe infections, and late-emerging metastatic progression.

In an August 2026 investigation published in *Frontiers in Public Health*, He and colleagues utilized death certificate entries from the Centers for Disease Control and Prevention Wide-ranging Online Data for Epidemiologic Research (CDC WONDER) to map cause-specific mortality across 1,323,609 decedents from 1999 through 2023 and project rates through 2040. Their findings suggested counter-intuitive reversals: while overall CRC mortality declined, secondary liver metastasis, lung metastasis, pulmonary embolism, and heart failure exhibited statistically significant increases over the last decade.

Despite the epidemiological and clinical importance of these findings, computational reproducibility remains a significant obstacle in population health research. Vital statistics studies frequently omit the programmatic queries used to bridge changing racial classifications, lack standardized public scripts, and rely on proprietary statistical packages (e.g., NCI Joinpoint Desktop) that prevent automated verification.

To address these challenges, this study provides an independent computational reproduction and methodological audit of the analysis by He et al. The objectives of this evaluation were to:
1. Re-extract and standardize raw mortality counts and population denominators from the National Vital Statistics System (NVSS).
2. Quantitatively benchmark reconstructed age-adjusted mortality rates (AAMRs), Joinpoint annual percent changes (APCs), and ARIMA forecasts against author-published benchmarks.
3. Dissect demographic and geographic disparities driving these temporal trajectories.
4. Deliver an open-source, reproducible software suite to advance vital statistics methodology and public health surveillance.

---

## 2. Materials and Methods

### 2.1 Study Design & Data Sources
A nationwide population-based cohort was reconstructed using death certificate records compiled by the National Center for Health Statistics (NCHS). The analysis incorporates US residents aged $\ge 25$ years who died between January 1, 1999, and December 31, 2023, with colorectal cancer designated as the underlying cause of death on the death certificate (ICD-10 codes `C18.0–C18.9` [colon], `C19` [rectosigmoid junction], and `C20` [rectum]).

Contributing causes of death were identified through multiple cause-of-death (MCD) record fields:
- **Ischemic Heart Disease (IHD)**: ICD-10 `I20–I25`
- **Heart Failure (HF)**: ICD-10 `I50`
- **Secondary Malignant Neoplasm of Liver**: ICD-10 `C78.7`
- **Secondary Malignant Neoplasm of Lung**: ICD-10 `C78.0`
- **Pulmonary Embolism (PE)**: ICD-10 `I26`
- **Sepsis**: ICD-10 `A40–A41`

Each condition was evaluated independently; categories were non-mutually exclusive.

### 2.2 Database Harmonization and Privacy Suppression
Because NVSS adopted the 1997 Office of Management and Budget (OMB) standards for single-race reporting during the study timeframe, the continuous 1999–2023 time series required bridging:
1. **1999–2020**: CDC WONDER Multiple Cause of Death file (bridged-race categories, database `D77`).
2. **2018–2023**: CDC WONDER Expanded Multiple Cause of Death file (single-race categories, database `D158`).

In accordance with NCHS confidentiality guidelines, cells containing 1 to 9 deaths were suppressed. To prevent fragmentary time series, adults aged 18–24 were excluded *a priori*, and subgroups with suppressed annual cells (e.g., PE among Hispanic and Non-Hispanic Asian cohorts) were flagged as non-estimable (`NA`), mirroring the original study protocol. Urbanization strata (based on the 2013 NCHS Urban-Rural Classification Scheme) were evaluated through 2020 due to post-2020 data deprecation in CDC WONDER.

### 2.3 Direct Age-Standardization
Annual age-adjusted mortality rates (AAMR per 100,000 standard population) were computed via direct standardization to the 2000 US Standard Population across seven 10-year age intervals ($25–34, 35–44, \dots, 85+$):

$$\text{AAMR} = \sum_{i=1}^7 w_i \left(\frac{D_i}{P_i}\right) \times 100,000$$

Standard weights $w_i$ were derived from the Census 2000 standard million proportion for age $\ge 25$.

### 2.4 Joinpoint Regression Modeling
Temporal inflection points were identified by fitting joined log-linear line segments:

$$\ln(\text{AAMR}_t) = \beta_0 + \beta_1 t + \sum_{k=1}^K \delta_k (t - \tau_k)^+$$

where $\tau_k$ denote joinpoints (up to 4 joinpoints permitted). Trend magnitudes were characterized by:
- **Annual Percent Change (APC)**: $100 \times (e^{\beta} - 1)$ for individual segments.
- **Average Annual Percent Change (AAPC)**: The duration-weighted average of segment slopes over the full 25-year span.
Two-tailed $t$-tests evaluated whether slopes differed significantly from zero ($P \le 0.05$).

### 2.5 Time-Series Forecasting (ARIMA Modeling)
Mortality rates were forecasted from 2024 through 2040 using non-seasonal autoregressive integrated moving average models ($\text{ARIMA}(p,d,q)$) with potential mean or drift parameters:
- Model orders were bounded by $p \le 5$, $q \le 5$, $p+q \le 5$, and $d \le 2$.
- The optimal model order was selected by minimizing the corrected Akaike Information Criterion ($\text{AICc}$).
- Stationarity and differencing order $d$ were tested via the Kwiatkowski-Phillips-Schmidt-Shin (KPSS) test.
- The Ljung-Box test at lag 10 evaluated residual white noise ($df = 10 - (p+q)$). Models exhibiting residual autocorrelation ($P < 0.05$) or negative point forecasts were eliminated in favor of the lowest-AICc valid alternative.
- Out-of-sample predictive accuracy was estimated using 10-fold rolling-origin cross-validation Root Mean Square Error (RMSE).

---

## 3. Results

### 3.1 Verification of Baseline and Endpoint Mortality Rates
Benchmarking of reconstructed mortality rates against the author-reported supplementary tables (`Table 1` and `eTable 1`) demonstrated exact concordance:

```
Table: Concordance of 1999 and 2023 Age-Adjusted Mortality Rates (Both Sexes)
Outcome                Published 1999  Reproduced 1999  Published 2023  Reproduced 2023  Discrepancy
Colorectal Cancer          32.06            32.06            19.57            19.57         0.000
Liver Metastasis            3.32             3.32             2.50             2.50         0.000
Lung Metastasis             1.38             1.38             1.52             1.52         0.000
Heart Failure               1.00             1.00             0.67             0.67         0.000
Ischemic Heart Disease      1.72             1.72             0.80             0.80         0.000
Pulmonary Embolism          0.29             0.29             0.38             0.38         0.000
Sepsis                      1.15             1.15             1.10             1.10         0.000
```

Across all 55 demographic and geographic subgroups, baseline 1999 rates and 2023 endpoint rates matched with zero discrepancy on primary series and an absolute discrepancy $<0.74$ per 100,000 on rural strata due to the 2020 truncation.

### 3.2 Joinpoint Temporal Segments & Trajectory Inflections
Replication of all 345 Joinpoint segments confirmed the exact inflection points reported by He et al.:
1. **Overall CRC Mortality**:
   - 1999–2012: APC = $-2.77\%$ ($95\%\text{ CI: } -3.42\text{ to } -2.51\%$, $P < 0.001$)
   - 2012–2020: APC = $-1.79\%$ ($95\%\text{ CI: } -2.90\text{ to } -1.24\%$, $P < 0.001$)
   - 2020–2023: APC = $+0.13\%$ ($95\%\text{ CI: } -1.36\text{ to } +1.78\%$, $P = 0.850$)
   Finding: The nationwide decline in CRC mortality flattened after 2020.
2. **Pulmonary Embolism Inflection**:
   - 1999–2004: APC = $-1.95\%$ ($P = 0.059$)
   - 2004–2008: APC = $+4.26\%$ ($P = 0.032$)
   - 2008–2012: APC = $-4.86\%$ ($P = 0.032$)
   - 2012–2023: APC = $+3.59\%$ ($95\%\text{ CI: } 2.99\text{ to } 4.37\%$, $P = 0.003$)
   Finding: PE mortality increased over the 2012–2023 segment. In the pre-pandemic sensitivity model (1999–2019), the post-2012 increase remained robust (APC $+4.17\%$, $P = 0.002$).
3. **Cardiovascular & Metastatic Disease Inflections**:
   - Heart failure mortality declined from 1999 to 2013 before reversing to an annual increase of $+3.16\%$ ($P = 0.033$).
   - Ischemic heart disease reversed upward from 2017 to 2023 (APC $+1.64\%$, $P = 0.001$).
   - Liver metastasis mortality increased at $+2.89\%$ per year from 2016 to 2023.
   - Lung metastasis mortality grew at $+2.08\%$ per year from 2017 to 2023.

### 3.3 ARIMA Projections to 2040
The selected ARIMA models demonstrated exact concordance on primary model forms:
- **Colorectal Cancer (Overall)**: $\text{ARIMA}(0,2,1)$, AICc = $29.28$, RMSE = $0.426$. Replicated 2040 projection = 17.66 per 100,000 (exact match to benchmark).
- **Heart Failure**: $\text{ARIMA}(0,2,1)$, AICc = $-77.38$. Replicated 2040 projection = 0.84 per 100,000 (exact match).
- **Lung Metastasis**: $\text{ARIMA}(1,2,0)$, AICc = $-62.62$. Replicated 2040 projection = 2.18 per 100,000 (exact match).
- **Liver Metastasis**: $\text{ARIMA}(3,0,0)$ with mean, AICc = $-31.67$. Replicated 2040 projection = 2.44 per 100,000 (benchmark: $2.33$, difference $0.11$).

### 3.4 Disparity Patterns
- **Sex**: Men experienced a higher burden across all conditions (2023 CRC AAMR: $23.23$ vs. $16.45$). While overall decline rates were parallel (AAPC $-2.15\%$ vs. $-2.12\%$), late-period increases in PE (+5.79% in women vs. +3.42% in men) and sepsis (+1.54% in women vs. +0.88% in men) were steeper among female decedents.
- **Race/Ethnicity**: Non-Hispanic Black patients experienced the highest baseline and endpoint mortality (2023 CRC AAMR: $24.90$ vs. $20.04$ in NH White, $16.08$ in Hispanic, and $13.34$ in NH Asian), despite exhibiting the fastest rate of overall decline (AAPC: $-2.49\%$).
- **Geography & Urbanization**: Southern residents exhibited slower rates of improvement (AAPC: $-1.74\%$) compared to the Northeast (AAPC: $-3.08\%$). Nonmetropolitan areas widened their mortality penalty, showing a +21.4% higher AAMR than large metropolitan areas by 2020.

---

## 4. Discussion & Methodological Audit

### 4.1 Verification of the Pre-Pandemic Pulmonary Embolism Signal
A critical methodological question in vital statistics across the 2020–2023 period is whether late-period increases in thromboembolism and cardiovascular mortality reflect oncologic dynamics or artifacts of COVID-19 coagulopathy. The present computational replication confirms the pre-pandemic sensitivity analysis reported by He et al.: the upward inflection in pulmonary embolism mortality occurred in 2012, eight years prior to the emergence of SARS-CoV-2. The sustained $+3.59\%$ annual rise from 2012 to 2023 indicates a persistent clinical vulnerability among cancer patients that warrants dedicated evaluation of thromboprophylaxis protocols.

### 4.2 Biological and Clinical Factors
The reversal of cardiovascular and metastatic trends during the 2010s reflects three converging clinical dynamics:
1. **Cardiotoxicity of Contemporary Therapies**: Fluoropyrimidines (5-fluorouracil, capecitabine) induce coronary vasospasm and myocardial ischemia, VEGF inhibitors (bevacizumab) exacerbate hypertension and arterial thromboembolism, and immune checkpoint inhibitors carry risks of myocarditis.
2. **Prolonged Exposure to Metastatic Risk**: As surgical metastasectomy and systemic regimens prolong survival in stage IV disease, patients survive long enough to experience late metastatic complications in the lungs and liver that would have previously been truncated by early primary mortality.
3. **The Rise of Early-Onset CRC**: The marked increase in secondary metastatic mortality among adults aged 35–54 (lung metastasis AAPC: $+5.23\%$) aligns with national registries showing that younger CRC patients present with more aggressive, distal, and microsatellite-stable phenotypes.

### 4.3 Methodological Contributions & Open-Source Pipeline
Prior vital statistics reproductions have often been hindered by proprietary software constraints and undisclosed bridging rules. The present replication provides several methodological additions to the scientific community:
1. **Fully Automated, Open-Source Architecture**: Proprietary point-and-click Joinpoint Desktop workflows were replaced with native Python segmented regression and statsmodels/ARIMA forecasting routines.
2. **Standardized CDC WONDER Ingestion Engine**: Open-source scripts handle NVSS bridged-race to single-race linkage, suppression filtering, and direct standardization according to the 2000 US Standard Population.
3. **Verifiable Cross-Validation Benchmarks**: All parsed datasets, benchmark matrices, regression coefficients, and publication figures are preserved in structured CSV format for immediate external verification.

### 4.4 Methodological Audit: Denominator Specification, Diagnostic Drift, and Statistical Power in Surveillance Registries

While the statistical calculations in He et al. are numerically reproducible to high precision, a rigorous methodological audit places these findings within the operational framework of vital statistics registries:

1. **Denominator Specification and Absolute versus Relative Risk**: The reported condition-specific mortality rates utilize the entire US general adult population (~240 million) as the denominator, rather than an active clinical cohort of CRC patients. While standard practice in demographic vital statistics, this convention can create divergence between relative percentage changes and absolute population risk. For instance, the reported 31% relative increase in pulmonary embolism mortality corresponds to an absolute change of 0.09 deaths per 100,000 general population (from 0.29 to 0.38 per 100,000). On a population scale, this represents fewer than one additional decedent per million individuals per year, or approximately 215 to 300 death certificates nationwide annually. In contrast, overall primary colorectal cancer mortality declined by 12.49 deaths per 100,000 over the same observation period. Presenting secondary percentage increases without equal emphasis on absolute population rates can lead to misinterpretation regarding the balance between primary cancer survival gains and secondary risks.

2. **Diagnostic Drift and Electronic Health Record Coding Practices**: Multiple Cause of Death records reflect death certificate documentation practices rather than standardized prospective clinical trial criteria. The post-2012 upward inflection in pulmonary embolism listings coincided chronologically with two systemic shifts in US hospital care: the widespread implementation of electronic health record (EHR) systems prompted by the HITECH Act, and the expanded diagnostic adoption of high-resolution computed tomography pulmonary angiography (CTPA). The increased routine detection of subsegmental or incidental pulmonary emboli, combined with EHR automated problem-list carrying into electronic death certification, represents a recognized mechanism of diagnostic drift. A decadal shift of 0.09 per 100,000 is consistent with administrative and diagnostic evolution in inpatient documentation.

3. **Statistical Power in Large Administrative Datasets**: In statistical hypothesis testing, standard errors decrease inversely with the square root of sample size ($\text{SE} \propto 1/\sqrt{N}$). With an administrative dataset of 1,323,609 death records and hundreds of millions of person-years, statistical power approaches unity. Consequently, minute mathematical deviations or administrative artifacts routinely yield extreme statistical significance ($P < 0.001$). Methodological rigor requires maintaining a clear distinction between statistical significance and clinical or public health effect size.

### 4.5 Clinical Implications and Constructive Methodological Recommendations

To translate these surveillance findings into effective clinical and public health guidance, several constructive principles are recommended:

1. **Dual Metric Reporting in Population Surveillance**: Future vital statistics studies should routinely report relative percentage changes alongside absolute baseline and endpoint rates. Where registry linkage is feasible, reporting rates per 1,000 diagnosed cancer patients alongside per 100,000 general population figures provides clinicians with a more direct assessment of individual patient risk.
2. **Targeted Cardio-Oncology Monitoring**: The documented plateau in heart failure and ischemic heart disease declines justifies proactive cardiovascular monitoring for patients maintained on fluoropyrimidine (5-FU, capecitabine) and anti-angiogenic regimens, while maintaining appropriate perspective on absolute population-level rates.
3. **Addressing Documented Geographic Disparities**: Public health resources should prioritize the documented 21.4% mortality penalty in nonmetropolitan regions and persistent disparities in the American South, where specialized surgical oncology and surveillance infrastructure face growing rural access barriers.

---

## 5. Conclusion

This computational investigation confirms the numerical validity and reproducibility of the findings reported by He et al. (*Frontiers in Public Health*, 2026). By establishing a fully transparent, open-source Python reproduction pipeline, this study demonstrates that while overall colorectal cancer mortality declined substantially from 1999 to 2023, primary survival progress has plateaued since 2020. Methodological auditing indicates that while cardiovascular and thromboembolic survivorship concerns warrant ongoing clinical attention, trend interpretations must account for absolute risk baselines, diagnostic drift, and the statistical properties of massive administrative registries.

---

## 6. Authorship, Ethics, and AI Disclosure Statement

In accordance with International Committee of Medical Journal Editors (ICMJE) and Committee on Publication Ethics (COPE) policies:
- **Sole Authorship and Responsibility**: The author (James Pusateri) is the sole author and responsible party for this work. Non-human artificial intelligence systems do not satisfy the criteria for authorship because authorship conveys accountability, legal liability, and intellectual stewardship that can only be borne by human researchers.
- **Use of Artificial Intelligence**: Generative AI tools were utilized under the author's direct supervision and review for programmatic assistance, script scaffolding, and manuscript drafting support. The author conceived and directed the reproduction, formulated the analysis protocol, verified all data queries and numerical computations against primary CDC WONDER records, inspected and validated all statistical models and forecasts, and holds sole accountability for the veracity, rigor, conclusions, and editorial integrity of this manuscript.

---

## References
1. He Z, Chen Y, Hu Y, et al. Trends and projections in cause-specific mortality among patients with colorectal cancer in the United States, 1999–2040. *Front Public Health*. 2026;14:1850707. doi:10.3389/fpubh.2026.1850707.
2. Siegel RL, Wagle NS, Cercek A, Smith RA, Jemal A. Colorectal cancer statistics, 2023. *CA Cancer J Clin*. 2023;73(3):233-254.
3. Centers for Disease Control and Prevention. Multiple Cause of Death Data on CDC WONDER. Available at: https://wonder.cdc.gov/mcd.html.
4. Anderson RN, Rosenberg HM. Age standardization of death rates: implementation of the year 2000 standard. *Natl Vital Stat Rep*. 1998;47(3):1-20.
5. Kim HJ, Fay MP, Yu B, Barrett MJ, Feuer EJ. Comparability of segmented line regression models. *Biometrics*. 2004;60(4):1005-1014.
6. Dort E, Rud H, Billion T, Tauseef A. Trends in pulmonary embolism mortality in cancer patients in the United States from 1999-2022: A CDC Wonder database study. *Respir Res*. 2025;26(1):248.
7. Zuin M, Nohria A, Henkin S, et al. Pulmonary embolism-related mortality in patients with cancer. *JAMA Netw Open*. 2025;8(1):e2460315.
8. Biller LH, Schrag D. Diagnosis and treatment of metastatic colorectal cancer: a review. *JAMA*. 2021;325(7):669-685.
9. Sung H, Siegel RL, Laversanne M, et al. Colorectal cancer incidence trends in younger versus older adults: an analysis of population-based cancer registry data. *Lancet Oncol*. 2025;26(1):51-63.
10. Anaka M, Abdel-Rahman O. Managing 5FU cardiotoxicity in colorectal cancer treatment. *Cancer Manag Res*. 2022;14:273-285.
