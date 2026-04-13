---
name: colour-mixing-image-processing
description: Five-step image processing pipeline for colour mixing experiments. Crops the wellplate from the raw deck image first, then perspective-corrects only the cropped region. VLM (Qwen3-235B) runs once at calibration; all values are cached and reused every iteration without further VLM calls.
---

# Image Processing

**Script**: [../scripts/image_processing.py](../scripts/image_processing.py)  
**Dependencies**: `pip install numpy Pillow openai`  
**VLM model**: `qwen/qwen3-vl-235b-a22b-instruct` via OpenRouter

---

## Design — Why Crop First, Then Correct

The overhead camera captures the entire OT-2 deck at a slight angle. Attempting to perspective-correct the full deck image requires all four outer deck corners to be visible — but in practice one or more corners are frequently cut off by the camera frame or obscured by the robot arm. This causes the perspective transform to produce a distorted image with large black areas.

**Solution**: Locate and crop the wellplate from the raw image first, then perspective-correct only that small, focused crop. The four wellplate corners are always fully visible within the crop, making the correction reliable.

```
Before loop:  calibrate_camera(reference_image)   ← full raw deck image
                    │
                    ├── Step 1: VLM → raw_crop_box (wellplate location in raw image)
                    ├── Step 2: Crop raw image to wellplate region
                    ├── Step 3: VLM → plate_corners (wellplate corners within the crop)
                    ├── Step 4: Perspective-correct the crop → flat wellplate image
                    └── Step 5: VLM → roi_size, stride    → CameraParams (cached)
                                                                  │
Each iteration:  run_pipeline(image, params)  ◄── no VLM ────────┘
                    │
                    ├── Step 1: Crop raw image using stored raw_crop_box
                    ├── Step 2: Apply perspective correction (stored plate_corners)
                    ├── Step 3: Sliding window ROI extraction — ALL wells
                    └── Step 4: Mean RGB per well → rgb_values[well_index]
```

VLM re-detection only triggers automatically when Level 2 validation keeps failing, indicating the camera may have shifted.

---

## Camera Capture

Images are captured by the Opentrons edge camera (`camera_capture` command). One image of the **full deck** is captured **per iteration** after all mixes for that iteration are dispensed — never one image per mix. Save each image as:
```
Base-colour-RGB-exp-<N>.jpg
```

The pipette arm must be in a clear position (home or park) so the wellplate is unobstructed.

---

## `CameraParams` — Cached Calibration Values

| Field | Set by | Description |
|---|---|---|
| `raw_crop_box` | Step 1 VLM | `[x1, y1, x2, y2]` bounding box of the wellplate in the **raw** image — used to crop the wellplate region each iteration |
| `plate_corners` | Step 3 VLM | Four corners [TL, TR, BR, BL] of the wellplate **within the raw crop** — used to compute the perspective correction coefficients |
| `roi_w`, `roi_h` | Step 5 VLM | ROI patch size in pixels, detected from the flat corrected image; **must be smaller than the well diameter** |
| `stride_x`, `stride_y` | Step 5 VLM | Step between adjacent well centres in pixels, detected from the flat corrected image |

---

## Step 1 — Locate Wellplate in Raw Image (VLM once → cached raw_crop_box)

**First time only**: The VLM receives the full raw deck image and identifies the bounding box of the target wellplate (the labware with a grid of circular wells). The box is stored and used every iteration to crop the wellplate region from the raw image before any perspective correction is applied.

**VLM input**: Full raw camera image of the OT-2 deck (angled/tilted view).

**VLM task**: Find the wellplate and return its bounding box in raw image pixels:
```json
{"raw_crop_box": [x1, y1, x2, y2]}
```

**Output**: `raw_crop_box` stored in `CameraParams`. Add ~20 px padding so the plate edges are fully included.

**Every iteration (no VLM)**: `raw_pil.crop(raw_crop_box)` → wellplate raw crop.

---

## Step 2 — Detect Wellplate Corners in Crop (VLM once → cached plate_corners)

**First time only**: The VLM receives the raw crop (which still appears slightly angled) and identifies the four corners of the wellplate surface. These corners are used to compute the perspective correction coefficients.

**VLM input**: Raw crop of the wellplate region (still angled/in perspective).

**VLM task**: Detect the wellplate's four outer corners within the crop:
```json
{"plate_corners": [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]}
```
Ordered: top-left, top-right, bottom-right, bottom-left. Use the outer plate frame edges, not well positions.

**Output**: `plate_corners` stored in `CameraParams` (coordinates are within the crop, not the full raw image).

**Every iteration (no VLM)**: Apply stored corners → compute coefficients → `PIL Image.PERSPECTIVE` on the crop → flat wellplate image.

```
Raw crop (angled wellplate)  →  find_coeffs(plate_corners)  →  PIL PERSPECTIVE  →  Flat wellplate image
```

---

## Step 3 — ROI Extraction for All Wells (VLM once → cached patch size and stride)

**First time only**: The VLM receives the flat corrected wellplate image and detects the well layout. It returns the ROI patch size and centre-to-centre stride. These are stored and reused for all future iterations.

**VLM input**: Flat top-down wellplate image (output of perspective correction).

**VLM task**: Detect well layout:
```json
{"roi_size": [roi_w, roi_h], "stride": [stride_x, stride_y]}
```

**ROI size rule**: Must be **smaller than the well diameter** — captures only the interior colour, not the well edge.

**Every iteration (no VLM)**: Slide the cached window across the flat image → one patch per well in row-major order (all wells, left to right, top to bottom).

```
Flat wellplate image  →  sliding window (roi_w, roi_h, stride_x, stride_y)  →  [patch_well1, ..., patch_wellN]
```

**Entry point**: `extract_roi_patches(image, roi_w, roi_h, stride_x, stride_y)`

---

## Step 4 — RGB Extraction

Compute the mean RGB of each ROI patch.

- Input: list of ROI patches for all wells (NumPy arrays, `H × W × 3`, RGB)
- Output: `[(R1,G1,B1), ..., (RN,GN,BN)]` — one tuple per well, values 0–255, row-major order

The caller selects specific well indices (from the protocol's well assignments) to read RGB for active (dispensed) wells.

**Entry point**: `mean_rgb(patch)` applied to each patch.

---

## Calibration Flow (once per session)

Call `calibrate_camera()` before starting the experiment loop, using the image captured after the initial 3 mixes are dispensed.

| Sub-step | Tool | Input | Output |
|---|---|---|---|
| 1 | VLM (`qwen/qwen3-vl-235b-a22b-instruct`) | Full raw deck image | `raw_crop_box` [x1, y1, x2, y2] |
| 2 | `PIL Image.crop(raw_crop_box)` | Raw image | Wellplate raw crop (still angled) |
| 3 | VLM (`qwen/qwen3-vl-235b-a22b-instruct`) | Wellplate raw crop | `plate_corners` [TL, TR, BR, BL] |
| 4 | `find_coeffs()` + PIL `Image.PERSPECTIVE` | Raw crop + plate_corners | Flat wellplate image |
| 5 | VLM (`qwen/qwen3-vl-235b-a22b-instruct`) | Flat wellplate image | `roi_w`, `roi_h`, `stride_x`, `stride_y` |

**Entry point**: `calibrate_camera(reference_image_path, vlm_model="qwen/qwen3-vl-235b-a22b-instruct")`

Optional: pass `plate_description` (e.g. `"black 96-well plate in slot 9"`) to help the VLM identify the correct labware when multiple similar items are visible.

---

## Per-Iteration Pipeline (no VLM)

```python
# Before the experiment loop — image taken after the initial 3 mixes
params = calibrate_camera(
    "Base-colour-RGB-exp-1.jpg",
    vlm_model="qwen/qwen3-vl-235b-a22b-instruct",
    plate_description="black 96-well plate in slot 9",  # optional hint
)

# Each iteration — full raw deck image
rgb_values, params = run_pipeline(
    image_path="Base-colour-RGB-exp-1.jpg",
    params=params,
    expected_well_count=96,  # total wells on the plate
)

# Select RGB for the specific wells that received mixes (row-major index)
rgb_well_A1 = rgb_values[0]
rgb_well_A2 = rgb_values[1]
rgb_well_A3 = rgb_values[2]
```

### Level 1 — Apply Cached Params (no VLM)

| Step | Action | Output |
|---|---|---|
| 1 | Load full raw image | PIL Image |
| 2 | Crop to wellplate using stored `raw_crop_box` | Wellplate raw crop (angled) |
| 3 | Apply perspective correction using stored `plate_corners` | Flat wellplate image |
| 4 | Extract ROI patches via sliding window for ALL wells | Per-well patches |
| 5 | Compute mean RGB per patch | `[(R,G,B), …]` — one per well |

**Entry point**: `run_level1(image_path, params)`

### Level 2 — Validation

| Check | Condition | Action if failed |
|---|---|---|
| RGB range | All R, G, B in 0–255 | Escalate to Level 3 |
| Patch count | Matches `expected_well_count` | Escalate to Level 3 |
| Patch variance | Non-zero variance per patch (not blank) | Escalate to Level 3 |
| Colour spread | At least one channel differs by > 10 across wells | Warn; optionally escalate |

### Level 3 — Fallback

**Step 1 — Retry Level 1**: Re-run with same cached params.

**Step 2 — VLM re-calibration**: Call `recalibrate_and_run()` — re-runs the full `calibrate_camera()` flow and returns a **new `CameraParams`** that must replace the old one.

---

## Rules

- Always run `calibrate_camera()` before the experiment loop — never skip it.
- Use the image captured **after all initial mixes are dispensed** as the calibration reference.
- The pipette arm must be clear of the wellplate when the image is captured.
- VLM is called **only during calibration** — never inside the iteration loop.
- `plate_corners` are coordinates **within the raw crop**, not the full raw image.
- ROI size must always be **smaller than the well diameter**.
- ROI extraction covers the **entire wellplate** — all wells, not just active ones. Filter by well index.
- Always store the `params` returned by `run_pipeline()` — it may be updated after re-calibration.
- If the camera is physically moved, re-run `calibrate_camera()`.
- Save raw crops and corrected images every session for debugging.
- If all three pipeline levels fail — stop, save the raw image, and report to the user.
