# Scientific Computing — Final Integrative Project (PIA)

## Universidad Autónoma de Nuevo León (UANL)

**Faculty:** Facultad de Ciencias Físico Matemáticas (FCFM)  
**Program:** PhD in Physical Engineering  
**Course:** Scientific Computing (D06)  
**Semester:** August–December 2026  
**Instructor:** Dr. Guillermo Ezequiel Sánchez Guerrero  
**Author:** MOHAMED AYAS MOHAMED KASIM

---

## 1. Project Overview

This repository contains the Final Integrative Project (PIA) developed for the Scientific Computing course at UANL.

**Project title:** Geomagnetic Activity and Aurora Potential — October 2026

The project investigates geomagnetic activity using the planetary Kp index. It integrates scientific data acquisition, Python-based processing, reproducible data storage, and interactive visualization in Power BI.

The workflow consists of three main components:

1. A documented GitHub repository for version control and reproducibility.
2. A Python pipeline that retrieves geomagnetic Kp measurements from the GFZ scientific data service and processes them into JSON and Parquet files.
3. A Power BI data model and dashboard for exploring geomagnetic activity during October 2026.

## 2. Scientific Research Question

**How did geomagnetic activity vary throughout October 2026, and which periods showed elevated geomagnetic disturbance associated with increased auroral potential?**

The analysis uses the planetary Kp index as an indicator of global geomagnetic activity.

Higher Kp values indicate stronger geomagnetic disturbances and can be associated with an increased potential for auroral activity. However, the Kp index alone does not establish whether auroras were visible at a particular location.

## 3. Scientific Data

**Data source:** GFZ Helmholtz Centre for Geosciences — Geomagnetic Kp Index

**Official website:** https://kp.gfz.de/

**Data description:** Three-hour planetary Kp observations for October 2026.

**Measurement:** Planetary Kp index, a dimensionless geomagnetic activity index.

**Temporal coverage:** October 1–31, 2026.

**Temporal resolution:** Three hours.

**Time reference:** Coordinated Universal Time (UTC).

**Total observations:** 248.

**Data license:** To be confirmed from the applicable GFZ dataset terms before final release.

### Data organization

- `data/raw/kp_october_2026.json` — Original API response.
- `data/processed/kp_october_2026.parquet` — Processed dataset.
- `data/processed/kp_summary.json` — Summary statistics.

The original JSON data are preserved separately from the processed dataset to support traceability.

## 4. Python Data Processing

The Python pipeline is implemented in:

`src/fetch_and_process.py`

The workflow:

1. Retrieves geomagnetic Kp observations from the GFZ API.
2. Processes the returned scientific data.
3. Organizes observations by date and time.
4. Identifies intervals with Kp ≥ 5.
5. Saves the processed data in Parquet format.
6. Generates a JSON file containing summary statistics.

### Reproduction instructions

**Requirements:** Python 3.13 and the project's required Python packages.

From the repository root, create a virtual environment:

```powershell
python -m venv .venv
```

Activate the environment on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the packages used by the pipeline:

```powershell
python -m pip install requests pandas pyarrow
```

Run the data processing script:

```powershell
python src/fetch_and_process.py
```

The expected output files are:

- `data/raw/kp_october_2026.json`
- `data/processed/kp_october_2026.parquet`
- `data/processed/kp_summary.json`

These instructions assume the script is executed from the repository root. Exact dependency versions should be recorded for the final reproducible release.

## 5. Power BI Data Model and Dashboard

The Power BI report is stored in the `reportes/` directory.

The project includes both a `.pbix` report and a `.pbip` project structure.

### Data model

**FactKp:** Contains three-hour Kp observations, timestamps, dates, and activity classifications.

**DimDate:** Provides the date dimension for time-based analysis.

The tables are connected through a one-to-many relationship between the date dimension and the observation table.

### DAX measures

The dashboard includes:

- Average Kp.
- Maximum Kp.
- Storm-level intervals (Kp ≥ 5).
- Total observations.
- Days analyzed.

### Visualizations

The dashboard presents:

1. Daily maximum geomagnetic Kp during October 2026.
2. Distribution of geomagnetic activity categories.
3. Three-hour Kp measurements during the October 10, 2026 disturbance.

The activity categories are project-defined groupings for descriptive analysis.

## 6. Results and Validation

The Python analysis produced the following summary statistics:

| Parameter | Result |
|---|---:|
| Total observations | 248 |
| Days analyzed | 31 |
| Average Kp | 1.93 |
| Maximum Kp | 7.333 |
| Storm-level intervals (Kp ≥ 5) | 7 |

### Scientific findings

The strongest geomagnetic activity in the analyzed period occurred on October 10, 2026.

The maximum observed Kp value was approximately 7.33.

The dataset contained seven three-hour intervals with Kp ≥ 5, indicating periods of elevated geomagnetic disturbance.

### Cross-platform validation

Five summary results were compared between the Python-generated JSON summary and Power BI DAX calculations.

| Parameter | Python | Power BI |
|---|---:|---:|
| Total observations | 248 | 248 |
| Days analyzed | 31 | 31 |
| Average Kp | 1.93 | 1.93 |
| Maximum Kp | 7.333 | 7.333 |
| Storm-level intervals | 7 | 7 |

All five summary results matched.

This validates agreement between the saved Python summary and the corresponding Power BI calculations. It does not constitute a record-by-record comparison of the entire dataset.

## 7. Project Structure

```text
Semester_2_CS_2026/
├── src/
│   └── fetch_and_process.py
├── data/
│   ├── raw/
│   │   └── kp_october_2026.json
│   └── processed/
│       ├── kp_october_2026.parquet
│       └── kp_summary.json
├── reportes/
│   ├── Geomagnetic_Kp_October_2026.pbix
│   ├── Geomagnetic_Kp_October_2026.pbip
│   ├── Geomagnetic_Kp_October_2026.Report/
│   └── Geomagnetic_Kp_October_2026.SemanticModel/
├── docs/
├── README.md
├── CITATION.cff
├── .gitignore
└── LICENSE
```

## 8. Reproducibility

The repository provides the Python processing script, original scientific data, processed datasets, summary statistics, and Power BI project files.

The analysis can be reproduced by running the Python pipeline and opening the Power BI report.

For reproducibility, the following should be documented in the final release:

- Python and dependency versions.
- Data source and retrieval information.
- Processing methodology.
- Power BI model and calculations.
- Scientific results and validation.

## 9. License and Citation

The repository's `LICENSE` file describes the applicable software license. The scientific data may be subject to separate GFZ licensing and attribution terms.

Citation information is provided in `CITATION.cff`.

**Project repository:** https://github.com/mohamedayas16/Semester_2_CS_2026
