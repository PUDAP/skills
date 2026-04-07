---
name: colour-mixing-opt
description: Optimize colour mixing on an Opentrons OT-2 to match a target colour by minimizing RMSE through Bayesian Optimization or LLM feedback, using camera capture and VLM-based image processing.
---

# Colour Mixing Optimization

Iteratively mix RGB colours on an Opentrons OT-2 and minimize RMSE between the mixed colour and a target colour using real-time camera feedback and BO or LLM optimization.

## Required Skills

Invoke these skills before generating any commands:
- **puda-machines** → opentrons machine (liquid handling + `camera_capture`)
- **puda-protocol** → protocol generation and execution
- **puda-memory** → update `experiment.md` after every protocol creation and run

## Required Machine

- **Opentrons OT-2** with camera attached (`machine_id: "opentrons"`)

## Optimization Approaches

Ask the user which approach to use if not specified:

| Approach | When to use |
|---|---|
| **Bayesian Optimization (BO)** | Efficient for continuous volume ratios; fewer iterations to converge |
| **LLM** | Flexible reasoning; good when constraints or colour theory context matters |

See [optimization.md](optimization.md) for implementation details.

---

## Workflow

### Phase 1 — Initialization

**Step 1 — Inputs (ask user before proceeding)**

Collect all of the following before starting. Do not proceed until every value is confirmed:

| Input | Description |
|---|---|
| Target colour | `(R, G, B)` where each value is 0–255 |
| Total well volume | Total volume in µL per well (e.g. 300 µL) |
| `x_init` — 3 initial mixes | User-provided volume sets (see below) |
| Optimization approach | BO (EI or LCB) or LLM (choose model) |
| RMSE threshold | Stop when RMSE ≤ this value |
| Maximum iterations | Stop after this many iterations |

**`x_init` — Initial volume inputs**

Ask the user to provide exactly 3 initial volume combinations for R, G, B dye in µL. Each set must sum to the total well volume.

Example prompt to the user:
```
Please provide 3 initial (R_vol, G_vol, B_vol) combinations in µL.
Each must sum to <total_volume> µL.

Mix 1: R_vol = ?, G_vol = ?, B_vol = ?
Mix 2: R_vol = ?, G_vol = ?, B_vol = ?
Mix 3: R_vol = ?, G_vol = ?, B_vol = ?
```

Validate each set before generating the protocol — reject and re-ask if any set does not sum to `total_volume` (±1 µL tolerance).

**Step 2 — Initial mixes (`x_init`)**
Generate a protocol using the 3 user-provided volume combinations and execute it on the Opentrons.

**Step 3 — Capture image**
After dispensing each mix, use `camera_capture`. Save and name images as:
```
Base-colour-RGB-exp-<N>.jpg
```
`<N>` increments from 1 for each iteration.

---

### Phase 2 — Per-Iteration Loop

**Step 4 — Image crop and pre-processing (VLM)**
Pass the captured image to a VLM. See [image-processing.md](image-processing.md) for prompts.

**Step 5 — ROI extraction (VLM)**
Use the VLM to identify and extract the Region of Interest for each well. Return per-well pixel crops.

**Step 6 — RGB extraction**
Compute mean RGB of each ROI crop — this is `(R_mix, G_mix, B_mix)`.

**Step 7 — RMSE calculation**
```
RMSE = sqrt(((R_mix - R_target)² + (G_mix - G_target)² + (B_mix - B_target)²) / 3)
```
Use [../scripts/rmse.py](../scripts/rmse.py).

**Step 8 — Optimizer feedback**
Pass `(volume_ratios, RMSE)` pairs to the chosen optimizer:
- **BO**: update the surrogate model with the new observation
- **LLM**: provide full history of `(ratios, RGB, RMSE)` and request next suggestion

**Step 9 — New volume ratio suggestion**
The optimizer returns the next `(R_vol, G_vol, B_vol)` to try.

**Step 10 — Iteration report**
Append one block to `logs/colour-mixing-report.md` after every iteration:

```markdown
## Iteration <N>

| Field | Value |
|---|---|
| Iteration | <N> |
| Volume ratio (R, G, B) | (<R_vol> µL, <G_vol> µL, <B_vol> µL) |
| Mixed colour RGB | (<R_mix>, <G_mix>, <B_mix>) |
| Target colour RGB | (<R_target>, <G_target>, <B_target>) |
| RMSE | <value> |
| Image saved | Base-colour-RGB-exp-<N>.jpg |
| Next suggested ratio (R, G, B) | (<R_next> µL, <G_next> µL, <B_next> µL) |
| Stop condition reached | Yes / No |
```

**Step 11 — Generate and execute protocol**
Use **puda-protocol** to generate a new protocol with the suggested volumes and execute it on the Opentrons. Then repeat from Step 3.

---

### Phase 3 — Stop Condition

Stop when **either** is met:

| Condition | Description |
|---|---|
| `RMSE ≤ threshold` | Target colour matched within acceptable error |
| `iteration ≥ max_iter` | Maximum iterations reached |

On stop: generate a final summary report and save to `logs/`.

## Rules

- Always ask for target colour, RMSE threshold, and max iterations **before** starting.
- Never assume volume ratios — they must come from the optimizer at each iteration.
- Image names must follow `Base-colour-RGB-exp-<N>.jpg` exactly.
- Protocol must always end with no tip attached (Opentrons sequencing rule).
- Invoke **puda-memory** after every protocol creation and run.
- **If unsure about any input, parameter, or decision — ask the user. Do not assume.**
