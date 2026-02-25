---
name: puda-analysis
description: Data analysis using puda with Python. Use when users want to explore puda database data, run data analysis, create plots or charts, or work with puda data in Python.
---

# Puda Data Analysis

Analyze the puda SQLite database in Python: understand the schema, load data into pandas, and perform analysis and plotting.

## When to Use

Load this skill when the user wants to:
- Analyze puda database data in Python
- Create plots, charts, or visualizations from puda data
- Explore or summarize data with pandas
- Run custom data analysis on puda SQLite tables

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

### 3. Query and load data into pandas

DB path: project root, `puda.db`. In Python use direct SQLite (no CLI):
After fetching the specified row in command_log table
**biologic**: data is in the `payload` column at `payload["response"]["data"]`.
Turn it into a pandas dataframe

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect("puda.db")  # project root
df = pd.read_sql_query("SELECT payload FROM command_log WHERE run_id='<run_id>' AND command_name='CV'", conn)
conn.close()
```

Use the schema from step 1 to write valid SQL queries. Prefer a single clear SQL query that selects only the columns needed.

### 4. Analysis and plotting

- **Analysis**: Use pandas for filtering, grouping, aggregations, time series, etc., according to what the user asked for.
- **Plotting**: Use matplotlib. Choose chart types that match the question (e.g. time series → line plot, distributions → histograms, categories → bar charts).

## Instructions summary

1. Run **`puda db schema`** and use it to choose tables and columns.
2. Install **pandas** and **matplotlib** if needed (`pip install pandas matplotlib`); **sqlite3** is built-in.
3. Load data into a pandas DataFrame with `sqlite3` + `pd.read_sql_query`; DB is `puda.db` in project root.
4. Perform the analysis and create the plots the user requested, using the schema to avoid invalid names and types. 