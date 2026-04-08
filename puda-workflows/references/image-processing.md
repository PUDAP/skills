---
name: colour-mixing-image-processing
description: Three-level image processing pipeline for colour mixing experiments. CameraParams (plate corners, ROI size, stride) are detected by Qwen3 VL 32B Instruct once at calibration and cached for all iterations. PIL Image.PERSPECTIVE handles perspective correction — no OpenCV required.
---

# Image Processing

**Script**: [../scripts/image_processing.py](../scripts/image_processing.py)  
**Dependencies**: `pip install numpy Pillow openai`  
**VLM model**: `qwen/qwen3-vl-32b-instruct` via OpenRouter (default)

---

## Design

Camera calibration happens **once** before the experiment loop. The VLM detects plate corners and ROI parameters from a reference image. Those values are stored in a `CameraParams` object and reused for every iteration — **no VLM call is made per iteration**.

VLM re-detection only triggers automatically when Level 2 validation keeps failing across retries, indicating the camera may have shifted.

```
Before loop:  calibrate_camera(reference_image) → CameraParams
                                                        ↓
Each iteration:  run_pipeline(image, params)  ← no VLM, uses cache
                                                        ↓
               If validation fails repeatedly: recalibrate → new CameraParams
```

---

## Camera Capture

Images are captured by an **external camera**. Save each image as:
```
Base-colour-RGB-exp-<N>.jpg
```

Use a consistent lighting setup. If the camera is physically moved, re-run `calibrate_camera()`.

---

## Step 0 — Calibration (once per session)

Call `calibrate_camera()` before starting the experiment loop.

**Flow**:

| Step | Tool | Output |
|---|---|---|
| 1. Detect plate corners | Qwen3 VL 32B (`VLM_CALIBRATE_CORNERS_PROMPT`) on reference image | `plate_corners` [TL, TR, BR, BL] |
| 2. Apply perspective correction | `find_coeffs()` + PIL `Image.PERSPECTIVE` | Corrected reference image |
| 3. Save corrected image | `<reference>_calibrated.jpg` | Input for ROI inference |
| 4. Infer ROI parameters | Qwen3 VL 32B (`VLM_CALIBRATE_ROI_PROMPT`) on corrected image | `roi_w`, `roi_h`, `stride_x`, `stride_y` |

All four values are stored in a `CameraParams` dataclass.

**`CameraParams` fields**:

| Field | Description |
|---|---|
| `plate_corners` | 4 plate corner coordinates [TL, TR, BR, BL] in raw image pixels |
| `roi_w`, `roi_h` | Well ROI patch size in pixels |
| `stride_x`, `stride_y` | Step between adjacent well centres in pixels |
| `output_size` *(derived)* | Output image size computed from corner distances |
| `reference_rect` *(derived)* | Flat destination rectangle for `find_coeffs()` |

**Entry point**: `calibrate_camera()` in `image_processing.py`

---

## Step 4 — Three-Level Processing Pipeline (per iteration)

### Level 1 — Apply Cached Params (No VLM)

| Step | Tool | Output |
|---|---|---|
| 1. Load image | PIL | Raw image |
| 2. Perspective correction | `find_coeffs()` + PIL `Image.PERSPECTIVE` using cached `plate_corners` | Flat top-down plate image |
| 3. Save corrected image | `<image>_corrected.jpg` | Audit record |
| 4. Extract ROI patches | Sliding window using cached `roi_w`, `roi_h`, `stride_x`, `stride_y` | Per-well patches |
| 5. Compute mean RGB | NumPy mean per patch | `(R, G, B)` per well |

**Entry point**: `run_level1(image_path, params)` in `image_processing.py`

### Level 2 — Validation

| Check | Condition | Action if failed |
|---|---|---|
| RGB range | All R, G, B values in 0–255 | Escalate to Level 3 |
| Patch count | Matches expected well count | Escalate to Level 3 |
| Patch variance | Non-zero variance per patch (not blank/black) | Escalate to Level 3 |
| Colour spread | At least one channel differs by > 10 across wells | Warn; optionally escalate |

**Entry point**: `validate_results()` in `image_processing.py`

### Level 3 — Fallback

**Step 1 — Retry Level 1**  
Re-run `run_level1()` with the same cached params. Transient image noise may have caused the failure.

**Step 2 — VLM re-calibration (camera shifted)**  
Call `recalibrate_and_run()`. This re-runs the full `calibrate_camera()` flow on the current image and returns a **new `CameraParams`**. The caller must store the new params for all future iterations.

**Entry point**: `recalibrate_and_run()` in `image_processing.py`

---

## Full Pipeline

Call `run_pipeline()` each iteration. It returns `(rgb_values, params)` — if re-calibration occurred, the returned `params` is new and must replace the old one.

```python
# Before the experiment loop
params = calibrate_camera("reference.jpg", vlm_model="qwen/qwen3-vl-32b-instruct")

# Each iteration
rgb_values, params = run_pipeline(
    image_path="Base-colour-RGB-exp-1.jpg",
    params=params,
    expected_well_count=3,
)
```

**Inputs to `run_pipeline()`**:

| Argument | Source | Description |
|---|---|---|
| `image_path` | External camera | Path to the captured image |
| `params` | `calibrate_camera()` or previous `run_pipeline()` | Cached `CameraParams` |
| `expected_well_count` | Labware definition | e.g. `3` for x_init mixes |
| `vlm_model` | Default or user choice | OpenRouter model ID |
| `vlm_api_key` | Environment / user | OpenRouter API key (or `OPENROUTER_API_KEY` env var) |

---

## Rules

- Always run `calibrate_camera()` before the experiment loop — never skip it.
- If the camera is physically moved or adjusted, re-run `calibrate_camera()` manually.
- Always store the `params` returned by `run_pipeline()` — it may be updated after re-calibration.
- Save all raw images, corrected images, and the calibration reference image for every session.
- If all three pipeline levels fail — stop, save the raw image, and report to the user.
