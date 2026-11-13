# Geomagnetic Activity and Reported Aurora Sightings — 2024

### Scientific Computing — Final Integrative Project (PIA)

**Universidad Autónoma de Nuevo León (UANL)**  
**Faculty:** Facultad de Ciencias Físico-Matemáticas (FCFM)  
**Program:** Doctorado en Ingeniería Física (PhD in Physical Engineering)  
**Course:** Scientific Computing (D06)  
**Semester:** August–December 2026  
**Instructor:** Dr. Guillermo Ezequiel Sánchez Guerrero  
**Author:** Mohamed Ayas Mohamed Kasim

## 1. Project overview

This repository contains a reproducible scientific-computing project investigating the association between **geomagnetic activity** and **citizen-reported aurora sightings**. Its main analysis covers **January 1–December 31, 2024**. An additional **October 2026** case study demonstrates shorter-period monitoring, while **NASA DONKI** geomagnetic storm records provide independent supporting context for 2024.

The project uses Python to acquire and process scientific data, CSV/Parquet/JSON files for traceable storage, and Power BI to explore time-series patterns, summaries, and comparisons.

**Main research question:** *How was the daily maximum planetary Kp index associated with the number of reported aurora sightings during 2024?*

The study examines **reported sightings**, not a complete count of all auroras that occurred. Correlation does not establish causation.

## 2. Data sources and scope

| Dataset | Source | Period | Role |
|---|---|---|---|
| Planetary Kp index | [GFZ Helmholtz Centre for Geosciences](https://kp.gfz.de/en/data) | Full year 2024 | Primary geomagnetic measurement (3-hour intervals, UTC) |
| Cleaned citizen aurora reports | [Aurorasaurus dataset on Zenodo](https://zenodo.org/records/16783265) | Filtered to 2024 | Reported aurora sightings and report counts |
| Geomagnetic storm events | [NASA DONKI GST API](https://api.nasa.gov/) | Full year 2024 | Independent storm-event record; authenticated request |
| Planetary Kp index | [GFZ](https://kp.gfz.de/en/data) | October 2026 | Separate case study |

**Important methodological distinctions:**

- The **Kp index** is a dimensionless, global geomagnetic activity indicator; it is not a direct observation of an aurora.
- The cleaned **Aurorasaurus** file contains citizen-submitted reports. A date with zero reports does **not** prove that no aurora occurred.
- **NASA DONKI GST events** are event records, whereas GFZ `Kp >= 5` counts **three-hour intervals**. These counts must not be equated.
- NASA **storm-start days** indicate dates on which recorded events *began*, not necessarily all days during which storms remained active.
- Dates are aligned in **UTC** for the main daily comparison; observation time zones and reporting conditions can affect interpretation.

## 3. Main results — 2024

The following figures are outputs from the project's Python processing and were cross-checked in Power BI where noted:

| Metric | 2024 result |
|---|---:|
| GFZ three-hour Kp records | **2,928** |
| Days covered | **366** |
| Mean Kp | **1.92** |
| Maximum Kp | **9.0** |
| Three-hour storm-level intervals (`Kp >= 5`) | **97** |
| Aurorasaurus report rows | **11,465** |
| Dates with at least one report | **318** |
| Pearson correlation: daily maximum Kp vs daily report count | **0.4498** |
| Spearman rank correlation | **0.6181** |
| NASA DONKI GST events returned for 2024 | **20** |
| Months with NASA-recorded GST starts | **7** |
| Maximum Kp listed among NASA events | **9.0** |

The two correlation coefficients describe a **positive association** between daily maximum Kp and daily citizen-report counts. The relationship is observational and may be influenced by viewing conditions, reporting behavior, location, and major storm outliers.

**May 2024 case study:** The May geomagnetic storm coincided with a substantial increase in reported aurora sightings. A separate Power BI comparison uses mean reports per day on **NASA storm-start dates** versus other dates; these are averages, not totals or causal estimates.

### October 2026 secondary case study

The original October 1–31, 2026 analysis is retained for comparison and reproducibility:

| Metric | October 2026 |
|---|---:|
| Kp measurements | 248 |
| Days | 31 |
| Mean Kp | 1.93 |
| Maximum Kp | 7.333 |
| Storm-level three-hour intervals | 7 |

The strongest October interval in this analysis occurred on **October 10, 2026**. This separate period is not pooled into the 2024 correlation calculations.

## 4. Python pipeline

### Requirements

- Python (developed using Python 3.13)
- `requests`, `pandas`, `pyarrow`, `matplotlib`
- Power BI Desktop for the report
- A free NASA API key for the DONKI download; **no key is required for GFZ**

From the repository root in Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install requests pandas pyarrow matplotlib
python src/fetch_and_process.py
```

The main script retrieves GFZ Kp measurements, processes the cleaned Aurorasaurus reports, checks coverage, creates daily/monthly summaries and correlations, and produces figures. The original October-only script/results should be retained separately as a backup if the main script has been replaced by the 2024 version.

### NASA DONKI API (keep credentials private)

Request a free key at https://api.nasa.gov/. In the **same PowerShell session**, set the environment variable and run the separate NASA script:

```powershell
$env:NASA_API_KEY = "YOUR_OWN_NASA_API_KEY"
python src/fetch_nasa_storms.py
```

The NASA script requests **each month of 2024 separately**, combines the responses, and deduplicates storm IDs before generating monthly counts.

**Never commit an actual API key**, `.env` credentials, terminal screenshots containing a key, or raw request logs that expose it. If a key has been disclosed, revoke/regenerate it. Ensure `.env`, `.venv/`, `__pycache__/`, and other local secrets are excluded by `.gitignore`.

## 5. Expected files and organization

The paths below describe the analysis files; the precise locations of Power BI source files may vary depending on your local repository layout.

```text
Semester_2_CS_2026/
├── src/
│   ├── fetch_and_process.py         # 2024 GFZ + Aurorasaurus processing
│   └── fetch_nasa_storms.py          # 2024 NASA DONKI acquisition
├── data/
│   ├── raw/
│   │   ├── kp_2024.json
│   │   ├── web_observations_2014-08-01_to_2025-08-02_cleaned.csv
│   │   ├── nasa_storms_2024.json
│   │   └── kp_october_2026.json      # retained previous analysis
│   └── processed/
│       ├── kp_2024.csv
│       ├── kp_2024.parquet
│       ├── aurora_reports_2024.csv
│       ├── kp_aurora_daily_2024.csv
│       ├── kp_aurora_monthly_2024.csv
│       ├── kp_summary_2024.json
│       ├── nasa_storms_2024.csv
│       ├── nasa_storms_monthly_2024.csv
│       ├── nasa_storm_summary_2024.json
│       └── kp_october_2026.parquet
├── figures/                          # Python-generated figures
├── reportes/                         # Power BI .pbix and/or .pbip files
├── docs/                             # final report and presentation PDFs
├── README.md
├── .gitignore
├── CITATION.cff
└── LICENSE
```

Data files and visualization artifacts should be included or linked according to repository size and GitHub limits. The large original Aurorasaurus file can be downloaded from its cited Zenodo record instead of being committed.

## 6. Power BI report and data model

The same Power BI report contains **three analytical sections/pages**:

1. **2024 — Geomagnetic Activity and Aurora Sightings:** Five KPI cards, monthly comparison, annual Kp series, daily Kp–report scatterplot, and May 2024 case study.
2. **NASA DONKI — 2024:** Monthly storm-event counts and comparison of daily aurora reporting on NASA storm-start days versus other days.
3. **October 2026 — Case Study:** Daily maximum Kp, activity-category distribution, and the October 10 disturbance.

**2024 relationships:** `DimDate2024[Date]` filters `FactKp2024[date]`, `AuroraDaily[date]`, and `NASAStormEvents[date]`. `AuroraMonthly` and `NASAStorms2024` are standalone pre-aggregated monthly tables. The older `DimDate`–`FactKp` relationship is retained for the October 2026 case study.


### Validation of Power BI DAX measures using pandas

Three existing Power BI measures were compared with
calculations made using Python and pandas on the
processed GFZ 2024 dataset.

| DAX measure | Power BI | pandas | Result |
|---|---:|---:|---|
| Kp Observations 2024 | 2,928 | 2,928 | Match |
| Average Kp 2024 | 1.92 | 1.9203 | Match (rounded) |
| Storm Intervals 2024 | 97 | 97 | Match |

**Dataset:** `data/processed/kp_2024.csv`

**Python validation command:**

```powershell
python -c "import pandas as pd; d=pd.read_csv('data/processed/kp_2024.csv'); print('Kp Observations:',len(d)); print('Average Kp:',round(d['kp'].mean(),4)); print('Storm Intervals:',int((d['kp']>=5).sum()))"
```

The validation uses all 2,928 three-hour Kp measurements
recorded during 2024. A storm-level interval is defined
as a measurement with Kp >= 5.

The Power BI values are displayed to two decimal places
for the average Kp.

**Six 2024/NASA visualizations:**

1. Monthly geomagnetic activity vs aurora report count.
2. Daily maximum Kp vs daily aurora reports (scatterplot and linear trend).
3. Daily maximum Kp throughout 2024 (storm threshold at Kp = 5).
4. May 2024 geomagnetic storm vs daily aurora reports.
5. NASA DONKI geomagnetic storm events by month.
6. Mean daily aurora reports on NASA storm-start days vs other days.

## 7. Validation and interpretation

- The GFZ 2024 dataset contains the expected **2,928 = 366 × 8** three-hour intervals.
- The total **11,465 Aurorasaurus reports** calculated in Python matched the total obtained in Power BI from the daily data.
- The NASA script returned **20 unique events** in **seven months**, after monthly retrieval and event-ID deduplication.
- The 2024 correlation coefficients were calculated using **daily** observations. NASA event counts were not added to the correlation dataset.
- The October 2026 Python–Power BI comparison was previously checked on five summary metrics; that validation applies to the October case study, not automatically to every new 2024 metric.

**Limitations:** Citizen-report counts are subject to geographic and temporal sampling, meteorological conditions, darkness, and public attention. NASA storm-event start dates may not coincide exactly with local aurora visibility or the full storm duration. Extreme days can strongly influence correlation and averages. This is an exploratory association study, not a causal model or a global aurora occurrence inventory.

## 8. Attribution, license, and citation

- **GFZ Kp:** https://kp.gfz.de/en/data — consult the applicable GFZ data terms and acknowledge the source.
- **Aurorasaurus cleaned reports:** https://zenodo.org/records/16783265 — cite the dataset record and respect its license and attribution instructions.
- **NASA DONKI:** https://api.nasa.gov/ — identify the NASA DONKI GST endpoint as an event-data source.
- Project software licensing: see [`LICENSE`](LICENSE).
- Citation metadata: see [`CITATION.cff`](CITATION.cff).

**Repository:** https://github.com/mohamedayas16/Semester_2_CS_2026

**Reproducibility note:** Private API keys are intentionally excluded. Users must obtain their own key to rerun the NASA DONKI request.
