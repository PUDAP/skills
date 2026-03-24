# puda-data Phase 3: Data Exporter

## Overview

Export PUDA experimental data to various formats.

## Export Functions

### export_to_csv(run_id, output_dir, command_name='CV')

Export measurement data to CSV file.

```python
from exporter import export_to_csv

export_to_csv("f3677d75...", "/home/bears/exports/")
# Creates: cv_f3677d75_20260315_181700.csv
```

### export_to_json(run_id, output_dir, command_name='CV')

Export measurement data to JSON file.

```python
from exporter import export_to_json

export_to_json("f3677d75...", "/home/bears/exports/")
# Creates: cv_f3677d75_20260315_181700.json
```

### export_protocol(run_id, output_dir)

Export protocol definition to JSON.

```python
from exporter import export_protocol

export_protocol("f3677d75...", "/home/bears/exports/")
# Creates: protocol_fea22b4e.json
```

### export_full_experiment(run_id, output_dir)

Export everything: data + protocol + fingerprint.

```python
from exporter import export_full_experiment

export_full_experiment("f3677d75...", "/home/bears/exports/")
# Creates multiple files with run_id prefix
```

## Output Formats

### CSV

```csv
potential,current,time,extra,flag
5.205532,1.313262e-05,0.0001,6.836228e-05,0
-0.006484,-1.400851e-06,0.2541,9.083333e-09,0
...
```

### JSON

```json
{
  "run_id": "f3677d75-1e5e-4ff6-9b04-4e9d55670a58",
  "command_name": "CV",
  "data": [
    {"potential": 5.205532, "current": 1.313262e-05, "time": 0.0001, "extra": 6.836228e-05, "flag": 0},
    ...
  ],
  "metadata": {
    "potential_range": [-0.051, 5.206],
    "current_range": [-9.88e-06, 1.71e-05]
  }
}
```

## Default Paths

- Database: `/home/bears/.openclaw/workspace/puda.db`
- Default exports: `/home/bears/.openclaw/workspace/exports/`
- Auto-creates directory if not exists