# puda-data Phase 4: Report Generator

## Overview

Generate markdown reports with pluggable visualizations. The report always includes fixed metadata (hashes, run info) but allows users to add custom visualizations.

## Report Structure

### Always Included (Fixed)

- **Header**: Run ID, Protocol ID, Command Type
- **Integrity**: Measurement hash, Run hash, Checksum
- **Metadata**: Created at, Data points, Parameters

### Customizable (Pluggable)

- **Plots**: Add any visualization function
- **Tables**: Add custom data tables
- **Notes**: Add free-form markdown

## Usage

### Simple Report

```python
from report import generate_report

generate_report(
    run_id="f3677d75...",
    output_dir="/path/to/reports/"
)
```

### Report with Custom Plot

```python
from report import ExperimentReport
from visualizer import plot_cv

# Create report
report = ExperimentReport(run_id="f3677d75...")

# Add standard metadata (always included)
report.add_metadata()

# Add custom visualization
report.add_plot(
    title="CV Curve",
    plot_function=plot_cv,
    plot_kwargs={"run_id": "f3677d75...", "output_path": "plot.png"}
)

# Save
report.save("/path/to/report.md")
```

### Custom Visualization Function

```python
def my_custom_plot(run_id, output_path):
    # Your plotting code here
    df = extract_measurement_data(run_id, "CV")
    # ... create plot ...
    plt.savefig(output_path)
    return output_path

# Use it in report
report.add_plot("My Plot", my_custom_plot, {"run_id": run_id})
```

## Class: ExperimentReport

### Methods

| Method | Description |
|--------|-------------|
| `add_metadata()` | Add run info, protocol, timestamps |
| `add_hashes()` | Add measurement_hash, run_hash, checksum |
| `add_plot(title, func, kwargs)` | Add custom visualization |
| `add_table(title, data)` | Add data table |
| `add_markdown(content)` | Add raw markdown |
| `save(path)` | Save report to file |

### Attributes

| Attribute | Description |
|-----------|-------------|
| `run_id` | Current run ID |
| `sections` | List of report sections |
| `plots` | List of added plots |

## Output Example

```markdown
# Experiment Report

## Run Information
- **Run ID**: f3677d75-1e5e-4ff6-9b04-4e9d55670a58
- **Protocol ID**: a1b2c3d4-e5f6-7890-abcd-ef1234567890
- **Command**: CV
- **Created**: 2026-03-13 15:38:39+08:00

## Data Integrity

| Hash Type | Value |
|-----------|-------|
| Measurement Hash | sha256:7bd7b697d34f6620236dee5ddc7847c043354de8d739cfb815c8cb1787c3f2e1 |
| Run Hash | sha256:139d200e2598c627b5ab13b76a93bc754b0e78da324106bc41035658dbbd55f7 |
| Checksum | sha256:eb26c8b499920a812c0bf5d66941774e7312c89fabc11b26e04ab8e9125515e1 |

## Data Summary
- **Points**: 504
- **Potential Range**: [-0.051, 5.206] V
- **Current Range**: [-9.88e-06, 1.71e-05] A

## Visualizations

### CV Curve
![CV Curve](plots/cv_f3677d75.png)

## Notes
[Your custom notes here]
```

## Default Paths

- Database: `/home/bears/.openclaw/workspace/puda.db`
- Default reports: `/home/bears/.openclaw/workspace/reports/`
- Plots subdir: `reports/plots/`