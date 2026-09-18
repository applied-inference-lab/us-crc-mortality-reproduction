# CDC WONDER Query Specifications & Extraction Recipes

This document provides complete, auditable specifications for querying the **Centers for Disease Control and Prevention Wide-ranging Online Data for Epidemiologic Research (CDC WONDER)** system to extract the raw mortality data analyzed in:

> **He Z, Chen Y, Hu Y, Lin J, Wang Y, Deng C, et al.**  
> *Trends and projections in cause-specific mortality among patients with colorectal cancer in the United States, 1999–2040.*  
> *Frontiers in Public Health* (2026) 14:1850707. DOI: [10.3389/fpubh.2026.1850707](https://doi.org/10.3389/fpubh.2026.1850707)

---

## 1. System Architecture & Databases

Because the National Vital Statistics System (NVSS) transitioned from the 1977 OMB bridged-race standard to the 1997 OMB single-race standard, the full 1999–2023 historical series spans two distinct online databases on CDC WONDER:

| Database Period | Database Name | Internal ID | Web URL | Race Standard | Urbanization |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1999–2020** | Multiple Cause of Death, 1999–2020 | `D77` | [wonder.cdc.gov/mcd-icd10.html](https://wonder.cdc.gov/mcd-icd10.html) | Bridged Race (4 categories) | 2013 NCHS scheme available |
| **2018–2023** | Multiple Cause of Death, 2018–2023, Single Race | `D158` / `D176` | [wonder.cdc.gov/mcd-icd10-expanded.html](https://wonder.cdc.gov/mcd-icd10-expanded.html) | Single Race (6+ categories) | Suppressed / not updated |

> [!NOTE]
> The overlapping years (2018–2020) serve as a validation window. For overall CRC and major non-cancer conditions, mortality rates between the bridged-race and single-race databases exhibit $>99.5\%$ concordance.

---

## 2. Cohort Definition & Filter Parameters

The following inclusion criteria and filter options apply to **all** queries across both databases:

### 2.1 Decedents & Age Filtering
* **Target Population**: Decedents aged $\ge 25$ years residing in the 50 US States and District of Columbia.
* **CDC WONDER Form Field**: `Ten-Year Age Groups`
* **Selected Values**:
  - `25-34 years` (Code: `25-34`)
  - `35-44 years` (Code: `35-44`)
  - `45-54 years` (Code: `45-54`)
  - `55-64 years` (Code: `55-64`)
  - `65-74 years` (Code: `65-74`)
  - `75-84 years` (Code: `75-84`)
  - `85+ years` (Code: `85+`)
* **Excluded**: `< 1 year`, `1-4 years`, `5-14 years`, `15-24 years` (ages 18–24 were explicitly excluded in the study protocol because counts with selected contributing comorbidities were $<10$ deaths/year, triggering CDC WONDER privacy suppression).

### 2.2 Underlying Cause of Death (UCOD)
* **CDC WONDER Form Field**: `Underlying Cause of Death` -> `ICD-10 113 Cause List` or `ICD-10 Codes`
* **Selected ICD-10 Range**: `C18-C20` (Malignant neoplasms of colon, rectosigmoid junction, and rectum)
  - `C18`: Malignant neoplasm of colon (`C18.0`–`C18.9`)
  - `C19`: Malignant neoplasm of rectosigmoid junction
  - `C20`: Malignant neoplasm of rectum

---

## 3. The Seven Condition-Specific Multiple Cause Queries

To study colorectal cancer mortality alongside major metastatic complications and non-cancer comorbidities, 7 distinct queries are executed. The Underlying Cause of Death is kept as `C18-C20`, while the **Multiple Cause of Death (MCOD)** filter is varied:

| Query # | Condition / Outcome Name | Underlying Cause (UCOD) | Multiple Cause (MCOD) ICD-10 Filter | Clinical Description |
| :---: | :--- | :--- | :--- | :--- |
| **Q1** | **Overall Colorectal Cancer** | `C18-C20` | *None / All (unrestricted)* | All deaths primarily caused by CRC |
| **Q2** | **Liver Metastasis** | `C18-C20` | `C78.7` | Secondary malignant neoplasm of liver and intrahepatic bile duct |
| **Q3** | **Lung Metastasis** | `C18-C20` | `C78.0` | Secondary malignant neoplasm of bronchus and lung |
| **Q4** | **Pulmonary Embolism (PE)** | `C18-C20` | `I26` (`I26.0`, `I26.9`) | Pulmonary embolism with or without acute cor pulmonale |
| **Q5** | **Heart Failure (HF)** | `C18-C20` | `I50` (`I50.0`–`I50.9`) | Congestive, left ventricular, or unspecified heart failure |
| **Q6** | **Ischemic Heart Disease (IHD)** | `C18-C20` | `I20-I25` | Angina, acute MI, subsequent MI, chronic ischemic heart disease |
| **Q7** | **Sepsis** | `C18-C20` | `A40-A41` | Streptococcal sepsis (`A40`) and other sepsis (`A41`) |

> [!IMPORTANT]
> Because contributing causes are recorded in the secondary/contributing fields of the death certificate, these categories are **non-mutually exclusive**. A decedent who died of metastatic colon cancer with both sepsis and pulmonary embolism will be captured in Q1, Q4, and Q7.

---

## 4. Group Results By (Stratification Strata)

To produce the data required for each table, model, and figure in the paper, each of the 7 condition queries is grouped by the following demographic or geographic axes:

### Strata Configuration Table

| Target Analysis | Group Results By (1st) | Group Results By (2nd) | Group Results By (3rd) | Applicable Database | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Overall National Trend** | `Year` | *None* | *None* | `D77` (1999–2020), `D158` (2021–2023) | Figure 1A, Table 1 national row |
| **Sex Stratification** | `Gender` | `Year` | *None* | `D77` & `D158` | Male, Female (Figure 2A) |
| **Race & Ethnicity** | `Race / Ethnicity` | `Year` | *None* | `D77` & `D158` | Hispanic, NH White, NH Black, NH Asian, NH AIAN |
| **10-Year Age Groups** | `Ten-Year Age Groups` | `Year` | *None* | `D77` & `D158` | 25–34, 35–44, ..., 85+ (Figure 2B) |
| **Census Region** | `Census Region` | `Year` | *None* | `D77` & `D158` | Northeast, Midwest, South, West (Figure 3A) |
| **2013 Urbanization** | `2013 Urbanization` | `Year` | *None* | `D77` only (1999–2020) | Large Metro, Medium-Small, Nonmetro |

### Detailed Race/Ethnicity Field Mappings
* **In Database `D77` (1999–2020)**:
  - `Race`: White, Black or African American, Asian or Pacific Islander, American Indian or Alaska Native
  - `Hispanic Origin`: Hispanic or Latino, Not Hispanic or Latino
  - *Combined Category Filter*:
    - Non-Hispanic White (`Race` = White, `Hispanic Origin` = Not Hispanic)
    - Non-Hispanic Black (`Race` = Black, `Hispanic Origin` = Not Hispanic)
    - Non-Hispanic Asian / Pacific Islander (`Race` = Asian/PI, `Hispanic Origin` = Not Hispanic)
    - Non-Hispanic American Indian or Alaska Native (`Race` = AIAN, `Hispanic Origin` = Not Hispanic)
    - Hispanic (`Hispanic Origin` = Hispanic or Latino, all races)
* **In Database `D158` (2018–2023)**:
  - `Single Race 6`: White, Black or African American, Asian, American Indian or Alaska Native, Native Hawaiian or Other Pacific Islander, More than one race
  - Combined with `Hispanic Origin` to form the corresponding OMB 1997 single-race non-Hispanic groups.

### Urbanization Reclassification Mapping (1999–2020)
The 2013 NCHS Urban-Rural Classification outputs 6 county tiers, aggregated into the 3 study strata:
1. **Large Metro**:
   - `Large Central Metro`
   - `Large Fringe Metro` (suburbs)
2. **Medium / Small Metro**:
   - `Medium Metro` (counties in MSAs of 250,000–999,999 population)
   - `Small Metro` (counties in MSAs of $<250,000$ population)
3. **Nonmetropolitan**:
   - `Micropolitan (Nonmetro)`
   - `NonCore (Nonmetro)`

---

## 5. Output Measures & Calculation Options

In the CDC WONDER web request form, configure section **"6. Select other options"** and **"4. Select measures"**:

* **Measures to Check**:
  - `[x] Deaths`
  - `[x] Population`
  - `[x] Crude Rate`
  - `[x] Age Adjusted Rate`
  - `[x] Standard Error (Age Adjusted)`
  - `[x] 95% Confidence Interval (Age Adjusted)`
* **Age Standardization Options**:
  - `Age-Adjusted Rate Method`: Direct Standardization
  - `Standard Population`: **2000 U.S. Standard Population**
* **Precision**:
  - Rates per 100,000 population.
  - Decimal precision: standard (2 decimal places).
* **Export Format**:
  - Select `Export Results` (tab-delimited `.txt` format).

---

## 6. Step-by-Step Manual Web UI Execution Guide

If manually retrieving data from the CDC WONDER portal:

1. Open browser to **[wonder.cdc.gov/mcd-icd10.html](https://wonder.cdc.gov/mcd-icd10.html)** (1999–2020).
2. Click **"I Agree"** to the data use restrictions.
3. In **1. Organize table layout**:
   - Set `Group Results By` to the desired stratum (e.g., `Gender`, `Race`, `Census Region`), then `Year`.
4. In **4. Select measures**:
   - Check `Deaths`, `Population`, `Crude Rate`, `Age Adjusted Rate`.
5. In **6. Select demographics**:
   - Set `Age Groups` -> Check `25-34 years`, `35-44 years`, `45-54 years`, `55-64 years`, `65-74 years`, `75-84 years`, `85+ years`.
6. In **7. Select cause of death**:
   - Set `Underlying Cause of Death` -> Check `C18-C20` (`C18`, `C19`, `C20`).
   - Set `Multiple Cause of Death` -> If querying a specific comorbidity, enter the ICD-10 code (e.g., `C78.7` for Liver Metastasis, `I26` for PE). Otherwise leave blank for overall CRC.
7. Click **"Export"** at the top or bottom right.
8. Save the exported tab-delimited text file to `data/raw/wonder_exports/` with an informative filename (e.g., `wonder_d77_crc_overall_1999_2020.txt`, `wonder_d77_pe_by_sex_1999_2020.txt`).
9. Repeat steps 1–8 on **[wonder.cdc.gov/mcd-icd10-expanded.html](https://wonder.cdc.gov/mcd-icd10-expanded.html)** for years 2021–2023.

---

## 7. Automated Querying via CDC WONDER API (XML Specification)

CDC WONDER provides an automated API endpoint via HTTP POST of an XML request payload to `https://wonder.cdc.gov/controller/datarequest/{database_id}`.

### Parameter Code Reference

| XML Parameter Name | Description | Value for Study Query |
| :--- | :--- | :--- |
| `b_1` | 1st Group By variable | `D77.V1-level1` (Year), `D77.V7` (Gender), `D77.V8` (Race), etc. |
| `b_2` | 2nd Group By variable | `D77.V1-level1` (Year) |
| `m_1` | Measure: Deaths | `1` (Checked) |
| `m_2` | Measure: Population | `1` (Checked) |
| `m_3` | Measure: Crude Rate | `1` (Checked) |
| `m_4` | Measure: Age Adjusted Rate | `1` (Checked) |
| `m_41` | Measure: Std Error Age Adjusted | `1` (Checked) |
| `v_D77.V5` | Ten-Year Age Groups | `25-34`, `35-44`, `45-54`, `55-64`, `65-74`, `75-84`, `85+` |
| `v_D77.V22` | Underlying ICD-10 Codes | `C18`, `C18.0`–`C18.9`, `C19`, `C20` |
| `v_D77.V13` | Multiple Cause ICD-10 Codes | Outcome specific (e.g., `C78.7`, `C78.0`, `I26`, `I50`, `I20-I25`, `A40-A41`) |
| `O_age` | Age Standardization Method | `D77.V5` (2000 US Standard Population) |
| `action-Send` | Action trigger | `Send` |

### Sample Python Script for Automated Extraction

Below is an automated retrieval script template (`script/fetch_cdc_wonder.py`) that can be executed to programmatically pull records into `data/raw/wonder_exports/`:

```python
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

API_URL_D77 = "https://wonder.cdc.gov/controller/datarequest/D77"


def build_wonder_request_xml(ucod_codes, mcod_codes=None, group_by="D77.V1-level1"):
  """Builds CDC WONDER XML request payload for 1999-2020 Multiple Cause of Death."""
  root = ET.Element("request-parameters")

  # Add parameter helper
  def add_p(name, values):
    p = ET.SubElement(root, "parameter")
    ET.SubElement(p, "name").text = name
    if isinstance(values, list):
      for v in values:
        ET.SubElement(p, "value").text = str(v)
    else:
      ET.SubElement(p, "value").text = str(values)

  # Grouping & measures
  add_p("B_1", group_by)
  add_p("B_2", "D77.V1-level1")  # Year
  add_p("M_1", "1")  # Deaths
  add_p("M_2", "1")  # Population
  add_p("M_3", "1")  # Crude Rate
  add_p("M_4", "1")  # Age-Adjusted Rate

  # Ages 25+
  age_codes = [
      "25-34",
      "35-44",
      "45-54",
      "55-64",
      "65-74",
      "75-84",
      "85+",
  ]
  add_p("F_D77.V5", age_codes)

  # Underlying Cause (C18-C20)
  add_p("F_D77.V22", ucod_codes)

  # Multiple Cause (Contributing)
  if mcod_codes:
    add_p("F_D77.V13", mcod_codes)

  # Standard Population 2000
  add_p("O_age", "D77.V5")
  add_p("action-Send", "Send")

  return ET.tostring(root, encoding="utf-8")


def send_wonder_query(xml_bytes, out_filepath):
  """Submits the query to CDC WONDER API and saves the tab-delimited response."""
  params = urllib.parse.urlencode({"request_xml": xml_bytes.decode("utf-8")})
  data = params.encode("utf-8")
  req = urllib.request.Request(API_URL_D77, data=data)
  with urllib.request.urlopen(req) as response:
    content = response.read().decode("utf-8")
    with open(out_filepath, "w", encoding="utf-8") as f:
      f.write(content)
  print(f"Saved WONDER response -> {out_filepath}")
```

---

## 8. Data Parsing and Processing Pipeline

Once the raw export files are deposited into `data/raw/wonder_exports/`, running:

```bash
python script/02_download_or_parse_wonder.py
```

performs the following automated operations:
1. **Header Identification**: Locates the header line (`Year`, `Deaths`, `Population`, `Crude Rate`, `Age Adjusted Rate`).
2. **Metadata Stripping**: Automatically detects footer records (`---`, `Total`, `Notes`) and isolates valid annual rows.
3. **Suppression Handling**: Flags suppressed cells ($<10$ counts) and converts them into standardized missing values (`NA`).
4. **Data Harmonization**: Combines the 1999–2020 and 2021–2023 streams into the unified output table:
   `data/processed/harmonized_annual_mortality_1999_2023.csv`.
