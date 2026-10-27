# Data extraction and project paths

### 1. Path Discovery (config.py)

Automatically finds project root via:
1. `PUDA_PROJECT_ROOT` env var
2. `puda.db` in parent directories
3. `puda.config` in parent directories
4. `experiment.md` in parent directories
5. `protocols/` in parent directories
6. `cwd()` fallback

```python
from config import get_project_root, get_db_path, get_report_dir

print(get_project_root())  # /path/to/workspace
print(get_db_path())       # /path/to/workspace/puda.db
```

### Extractor

```python
from extractor import (
    extract_measurement_data,  # Get DataFrame for a run
    get_runs_by_type,          # List runs by command type
    get_latest_measurements,   # Get recent measurement DataFrames
    get_run_info,              # Get run metadata
    get_protocol,              # Get protocol definition
    list_all_runs,             # List all runs
)

# Examples
df = extract_measurement_data(run_id, "CV", device="biologic")
runs = get_runs_by_type("CV", limit=10)
measurements = get_latest_measurements("PEIS", limit=5)
info = get_run_info(run_id)
protocol = get_protocol(protocol_id)
all_runs = list_all_runs(limit=20)
```

## Database Schema

```sql
protocol(run_id, user_id, username, description, commands, created_at)
run(run_id, protocol_id, created_at)
sample(sample_id, run_id, data_payload, created_at)
measurement(measurement_id, sample_id, data_payload, created_at)
command_log(command_log_id, run_id, step_number, command_name, payload, machine_id, command_type, created_at)
```

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `PUDA_PROJECT_ROOT` | Override project root discovery | `/home/user/puda-project` |
