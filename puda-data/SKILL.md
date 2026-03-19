---
name: puda-data
description: Extract, hash, export, and report on PUDA experimental data. Provides data provenance through SHA-256 hashing. Supports CV, OCV, CA, PEIS, GEIS measurements.
---

# PUDA Data Skills

Comprehensive data management for PUDA laboratory experiments. All 4 phases complete!

## Quick Start

```python
import sys
sys.path.append("/home/bears/.openclaw/workspace/.claude/skills/puda-data/scripts")

# Phase 1: Extract
from extractor import get_runs_by_type, extract_measurement_data

# Phase 2: Hash  
from hasher import hash_measurement, generate_fingerprint

# Phase 3: Export
from exporter import export_to_csv, export_to_json

# Phase 4: Report
from report import generate_report
from visualizer import plot_cv

# Full workflow
run_id = get_runs_by_type("CV", 1)[0][0]
df = extract_measurement_data(run_id, "CV")
fp = generate_fingerprint(run_id)
print(f"Hash: {fp['measurement_hash']}")
generate_report(run_id)
```

## Phase Summary

| Phase | Module | Purpose |
|-------|--------|---------|
| 1 | `extractor.py` | Query database for data |
| 2 | `hasher.py` | SHA-256 hashing for provenance |
| 3 | `exporter.py` | Export to CSV/JSON |
| 4 | `report.py` + `visualizer.py` | Markdown reports with plots |

## Phase 1: Data Extractor

See: `references/extractor.md`

```python
from extractor import (
    extract_measurement_data,
    get_runs_by_type,
    get_latest_measurements,
    get_run_info,
    get_protocol,
    list_all_runs
)

# Get latest CV
run_id, df = get_latest_measurements("CV", 1)[0]
print(f"Points: {len(df)}")
```

## Phase 2: Data Hasher

See: `references/hasher.md`, `references/provenance-demo.md`

```python
from hasher import (
    hash_measurement,
    hash_run,
    generate_fingerprint,
    verify_integrity,
    demonstrate_integrity
)

# Get fingerprint with all hashes
fp = generate_fingerprint(run_id)
print(f"Measurement Hash: {fp['measurement_hash']}")
print(f"Run Hash: {fp['run_hash']}")
print(f"Checksum: {fp['checksum']}")

# Verify data hasn't been tampered
is_valid = verify_integrity(run_id, stored_hash)
```

### Provenance Demo

**Original hash:** `sha256:7bd7b697...`

**After 1% change:** `sha256:a03a6830...`

**Completely different!** ✅

See `references/provenance-demo.md` for full example.

## Phase 3: Exporter

See: `references/exporter.md`

```python
from exporter import (
    export_to_csv,
    export_to_json,
    export_protocol,
    export_full_experiment
)

# Export everything
export_full_experiment(run_id, "/path/to/exports/")
```

## Phase 4: Report Generator

See: `references/report.md`

```python
from report import ExperimentReport, generate_report
from visualizer import plot_cv

# Simple one-liner
generate_report(run_id)

# Custom report
report = ExperimentReport(run_id, "CV", "My Experiment")
report.add_metadata()
report.add_hashes()
report.add_summary()
report.add_plot("CV Curve", plot_cv, {"run_id": run_id})
report.add_markdown("## Notes\nCustom observations here.")
report.save("report.md")
```

### Report Always Includes

- ✅ Run ID, Protocol ID, Command Type
- ✅ Measurement Hash (SHA-256)
- ✅ Run Hash 
- ✅ Checksum
- ✅ Data Summary (points, ranges)

### Customizable

- ✅ Add any plot function
- ✅ Add data tables
- ✅ Add markdown notes

## Database

**Path:** `/home/bears/.openclaw/workspace/puda.db`

| Table | Rows |
|-------|------|
| protocol | 7 |
| run | 14 |
| command_log | 94 |

### Supported Data Types

| Type | Status |
|------|--------|
| CV | ✅ Has data |
| OCV | Ready (no data yet) |
| CA | Ready (no data yet) |
| PEIS | Ready (no data yet) |
| GEIS | Ready (no data yet) |

## Files

```
puda-data/
├── SKILL.md
├── scripts/
│   ├── extractor.py      # Phase 1: Data extraction
│   ├── hasher.py         # Phase 2: Hashing & provenance
│   ├── exporter.py       # Phase 3: Export to CSV/JSON
│   ├── visualizer.py     # Phase 4: Plotting functions
│   └── report.py         # Phase 4: Report builder
└── references/
    ├── extractor.md
    ├── hasher.md
    ├── exporter.md
    ├── report.md
    └── provenance-demo.md    # Hash difference demo
```

## Requirements

```bash
pip install pandas matplotlib numpy
```
