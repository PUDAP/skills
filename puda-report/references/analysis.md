---
name: puda-analysis
description: Data analysis using puda with Python. Use when users want to explore puda database data, run data analysis, create data visualizations, or work with puda data in Python.
---

## Goal

Perform data analysis on the puda SQLite database in Python inside the **analysis/** directory: understand the schema, load data into pandas, and perform analysis and plotting.

## Workflow

### 1. Understand the schema

**Before writing any SQL or Python**, run:

```bash
puda db schema
```

Use the output to identify:
- Table names and column names (use these exactly; do not assume)
- Column types (for correct pandas dtypes and plotting choices)
- Which tables/columns are relevant to the user’s analysis

### 2. Ensure Python environment

- **sqlite3**: Part of the Python standard library; no install needed.
- **pandas** and **matplotlib**: Install if missing:

```bash
pip install pandas matplotlib
```

### 3. Create analysis folder

Create an **analysis/** folder inside the experiment folder if missing. Keep all analysis work there: Python scripts, Jupyter notebooks, exported data (e.g. CSV), and generated plots.

### 3. Generate python file

1. Use the schema from step 1 to write valid SQL queries. Prefer a single clear SQL query that selects only the columns and data needed.
2. **biologic**: data is in the `payload` column at `payload["response"]["data"]`; parse JSON and use that path for analysis.

```python
import json
import sqlite3
from pathlib import Path
import pandas as pd

# Resolve puda.db from project root (2 levels up from this script)
_db_path = Path(__file__).resolve().parent.parent.parent / "puda.db"

with sqlite3.connect(_db_path) as conn:
    row = pd.read_sql_query(
        "SELECT payload FROM command_log WHERE run_id='f379e2a4-09f1-42dd-bedf-4016e799e317' AND command_name='CV'",
        conn,
    ).iloc[0]

# json data
data = json.loads(row["payload"])["response"]["data"]
```

### 4. Analysis and plotting

Continue the script from the loaded data (SQL result or parsed payload): apply pandas for analysis and matplotlib for plotting as requested.

- **Analysis**: Use pandas for filtering, grouping, aggregations, time series, etc., according to what the user asked for.
- **Plotting**: Use matplotlib. Choose chart types that match the question (e.g. time series → line plot, distributions → histograms, categories → bar charts).

## Instructions summary

1. Run **`puda db schema`** and use it to choose tables and columns.
2. Install **pandas** and **matplotlib** if needed (`pip install pandas matplotlib`); **sqlite3** is built-in.
3. Load data into a pandas DataFrame with `sqlite3` + `pd.read_sql_query`; DB is `puda.db` in project root.
4. Perform the analysis and create the plots the user requested, using the schema to avoid invalid names and types. 