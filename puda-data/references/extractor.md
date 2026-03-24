# puda-data Phase 1: Data Extractor

## Overview

Extract experimental data from PUDA database. Supports multiple measurement types.

## Database Schema

### Tables

| Table | Description |
| ------ |-------------|
| `protocol` | Protocol definitions (7 rows) |
| `run` | Experiment runs (14 rows) |
| `command_log` | Command responses (94 rows) - **data is here** |

### Command Types in command_log

- **With Data**: CV (currently has data)
- **Without Data**: home, load_deck, attach_tip, aspirate_from, dispense_to, drop_tip, move_electrode, wait, startup, start, complete

### CV Data Format

Each data point has 5 columns:
- Column 0: `potential` (V) - Applied voltage
- Column 1: `current` (A) - Measured current  
- Column 2: `time` (s) - Elapsed time
- Column 3: `extra` - Additional data
- Column 4: `flag` - Scan direction (0=forward, 1=backward)

## Extraction Functions

### extract_measurement_data(run_id, command_name)

Extract measurement data for a specific run and command type.

```python
from extractor import extract_measurement_data

df = extract_measurement_data("f3677d75-1e5e-4ff6-9b04-4e9d55670a58", "CV")
# Returns: DataFrame with columns [potential, current, time, extra, flag]
```

### get_runs_by_type(command_name, limit)

List runs containing a specific command type.

```python
from extractor import get_runs_by_type

runs = get_runs_by_type("CV", limit=10)
# Returns: [(run_id, step_number, created_at), ...]
```

### get_latest_measurements(command_name, limit)

Get most recent measurement data.

```python
from extractor import get_latest_measurements

measurements = get_latest_measurements("CV", limit=5)
# Returns: [(run_id, DataFrame), ...]
```

### get_run_info(run_id)

Get experiment metadata.

```python
from extractor import get_run_info

info = get_run_info("f3677d75-1e5e-4ff6-9b04-4e9d55670a58")
# Returns: {run_id, protocol_id, created_at, commands: [(step, name), ...]}
```

### get_protocol(protocol_id)

Get protocol definition.

```python
from extractor import get_protocol

protocol = get_protocol("fea22b4e-9989-4636-87f6-223ba69930e1")
# Returns: {protocol_id, user_id, username, description, commands: [...], created_at}
```

## Column Mapping for Different Data Types

| Data Type | Col 0 | Col 1 | Col 2 | Col 3 | Col 4 |
|-----------|-------|-------|-------|-------|-------|
| CV | potential (V) | current (A) | time (s) | extra | flag |
| OCV | voltage (V) | current (A) | time (s) | - | - |
| CA | time (s) | current (A) | voltage (V) | - | - |
| PEIS | frequency (Hz) | Z_real | Z_imag | - | - |

Note: Currently only CV has data in the database. Other types will return empty DataFrames until more experiments are run.