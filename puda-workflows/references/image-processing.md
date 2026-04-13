---
name: colour-mixing-image-processing
description: Five-step image processing pipeline for colour mixing experiments. VLM (Qwen3-235B) runs once at calibration to detect plate corners, wellplate crop box, and ROI parameters; all values are cached and reused every iteration without further VLM calls.
---

# Image Processing

**Script**: [../scripts/image_processing.py](../scripts/image_processing.py)  
**Dependencies**: `pip install numpy Pillow openai`  
**VLM model**: `qwen/qwen3-vl-235b-a22b-instruct` via OpenRouter

---

## Design

Calibration runs **once** before the experiment loop — triggered on the first image captured after the initial 3 mixes are dispensed. The VLM produces three cached values:

1. **Plate corners** (detected on the raw image) — used for perspective correction
2. **Crop box coordinates** — bounding rectangle of the wellplate in the corrected image
3. **ROI patch size and stride** — detected from the cropped plate image

All values are stored in `CameraParams` and reused for every iteration — **no VLM call is made per iteration**.

```
Before loop:  calibrate_camera(reference_image)   ← image of whole wellplate after initial mixes
                    │
                    ├── Step 1: VLM → plate_corners (from raw image)
                    ├── Step 2: Apply perspective correction → flat corrected image
                    ├── Step 3: VLM → crop_box (wellplate bounding box in corrected image)
                    ├── Step 4: Crop corrected image to wellplate area
                    └── Step 5: VLM → roi_size, stride (from cropped image)  → CameraParams (cached)
                                                                                      │
Each iteration:  run_pipeline(image, params)  ◄── no VLM, uses cache ────────────────┘
                    │
                    ├── Step 1: Apply perspective correction (plate_corners)
                    ├── Step 2: Crop to wellplate area (crop_box)
                    ├── Step 3: Sliding window ROI extraction — ALL wells (roi_w, roi_h, stride)
                    └── Step 4: Mean RGB per well → rgb_values[well_index]
```

VLM re-detection only triggers automatically when Level 2 validation keeps failing, indicating the camera may have shifted.

---

## Camera Capture

Images are captured by the Opentrons edge camera (`camera_capture` command). One image is captured **per iteration** after all mixes for that iteration are dispensed — never one image per mix. Save each image as:
```
Base-colour-RGB-exp-<N>.jpg
```

Use a consistent lighting setup and fixed camera position. If the camera is physically moved, re-run `calibrate_camera()`.

---

## `CameraParams` — Cached Calibration Values

| Field | Set by | Description |
|---|---|---|
| `plate_corners` | Step 1 VLM | Four plate corners [TL, TR, BR, BL] detected from the raw image — used to compute perspective coefficients |
| `crop_box` | Step 3 VLM | `[x1, y1, x2, y2]` bounding box of the wellplate in the corrected image — isolates the plate before ROI extraction |
| `roi_w`, `roi_h` | Step 5 VLM | ROI patch size in pixels, detected from the cropped plate image; **must be smaller than the well diameter** |
| `stride_x`, `stride_y` | Step 5 VLM | Step between adjacent well centres in pixels, detected from the cropped plate image |

---

## Step 1 — Perspective Correction (VLM once → cached coefficients)

The overhead camera captures the entire OT-2 deck at a slight angle, producing a
perspective-distorted image. The goal of this step is to flatten the **full deck**
into a straight top-down view before any labware-specific processing begins.

**First time only**: The VLM receives the raw camera image and identifies the four
outer corners of the **OT-2 deck platform** (the large flat rectangular surface
that holds all labware). These corners — not any individual labware corners — are
used to compute the perspective correction coefficients.

> Using deck corners rather than individual labware corners produces a more reliable
> and stable correction because the deck boundary is always visible and clearly
> defined even when multiple labware items are present.

**VLM task**: Detect the four outer corners of the OT-2 deck platform →
`[[x1,y1],[x2,y2],[x3,y3],[x4,y4]]` ordered TL, TR, BR, BL.

**Output**: `plate_corners` (deck corners) stored in `CameraParams`. Coefficients
are re-derived from corners each call via `find_coeffs()` + PIL `Image.PERSPECTIVE`.

**Every iteration (no VLM)**: Apply stored corners → compute coefficients →
apply `PIL Image.PERSPECTIVE` transform → flat, straight top-down view of the
entire deck.

```
Raw image (tilted, full deck)  →  find_coeffs(deck corners)  →  PIL PERSPECTIVE  →  Flat deck image
```

---

## Step 2 — Crop Area of Interest (VLM once → cached crop box)

**First time only**:
1. The perspective correction coefficients derived from the deck corners (Step 1) are applied to the **raw image**, producing a flat top-down view of the entire deck.
2. The VLM receives this corrected flat deck image and visually locates the target wellplate (the labware with circular wells arranged in a grid) among all labware items on the deck. It returns the wellplate's bounding box in corrected image pixels.

**VLM input**: The flat corrected deck image (full deck, all labware visible).

**VLM task**: Identify the well plate labware and return its bounding box in corrected image pixels:
```json
{"crop_box": [x1, y1, x2, y2]}
```
The box must tightly enclose only the target wellplate including all outermost wells — not the whole deck, and not any other labware item. Coordinates are pixel positions in the corrected image.

**Optional hint**: Pass `plate_description` to `calibrate_camera()` (e.g. `"96-well plate in deck slot 5"`) to help the VLM identify the correct labware when multiple similar items are visible.

**Output**: `crop_box` stored in `CameraParams`.

**Every iteration (no VLM)**: Apply the stored perspective correction coefficients (from `plate_corners`) to the raw image, then apply the stored `crop_box` to the corrected result — no VLM call.

```
Raw image  →  perspective correction (stored deck-corner coefficients)  →  Flat deck image
Flat deck image  →  crop(stored crop_box)  →  Cropped wellplate image (plate only)
```

---

## Step 3 — ROI Extraction for All Wells (VLM once → cached patch size and stride)

Slide a window across the **cropped wellplate image** to extract one ROI patch per well, covering the **entire plate** in row-major order (left to right, top to bottom).

**First time only**: The VLM receives the cropped wellplate image and detects well positions. It returns the ROI patch size (`roi_w`, `roi_h`) and the step between well centres (`stride_x`, `stride_y`). These are stored in `CameraParams` and reused for all future iterations — **no VLM call per iteration**.

**VLM task**: Detect well layout → `{"roi_size": [roi_w, roi_h], "stride": [stride_x, stride_y]}` in cropped image pixels.

**ROI size rule**: The ROI must be **smaller than the well size** so it captures only the interior colour and avoids well edges. Centre the ROI at each well position.

**Every iteration (no VLM)**:
- Starting from the top-left well, step by cached `stride_x` / `stride_y` to reach each well centre
- At each well, extract a patch of cached size `roi_w × roi_h` centred on that position
- Patches are collected in row-major order for the **whole plate** (all wells)

```
Cropped wellplate image  →  sliding window (roi_w < well_w, roi_h < well_h)  →  [patch_well1, ..., patch_wellN]
                                                                                        (one patch per well, all wells)
```

**Entry point**: `extract_roi_patches(image, roi_w, roi_h, stride_x, stride_y)`

---

## Step 4 — RGB Extraction

Compute the mean RGB value of each ROI patch.

- Input: list of ROI patches for all wells (NumPy arrays, shape `H × W × 3`, RGB)
- Output: `[(R1, G1, B1), (R2, G2, B2), ..., (RN, GN, BN)]` — one tuple per well, values 0–255, in row-major order

The caller selects specific well indices (from the protocol's well assignments) to read the RGB values for the wells that contain mixed colours.

**Entry point**: `mean_rgb(patch)` applied to each patch from Step 3.

---

## Calibration Flow (once per session)

Call `calibrate_camera()` before starting the experiment loop, using the image captured after the initial 3 mixes are dispensed.

| Sub-step | Tool | Input | Output |
|---|---|---|---|
| 1 | VLM (`qwen/qwen3-vl-235b-a22b-instruct`) | Raw angled camera image | `plate_corners` — four outer corners of the OT-2 **deck platform** |
| 2 | `find_coeffs()` + PIL `Image.PERSPECTIVE` | Raw image + deck corners | Flat corrected image of the full deck |
| 3 | VLM (`qwen/qwen3-vl-235b-a22b-instruct`) | Flat corrected deck image | `crop_box` [x1, y1, x2, y2] — bounding box of the target wellplate |
| 4 | `image.crop(crop_box)` | Flat corrected deck image | Cropped wellplate image |
| 5 | VLM (`qwen/qwen3-vl-235b-a22b-instruct`) | Cropped wellplate image | `roi_w`, `roi_h`, `stride_x`, `stride_y` |

All values are stored in a single `CameraParams` object.

**Entry point**: `calibrate_camera(reference_image_path, vlm_model="qwen/qwen3-vl-235b-a22b-instruct")`

---

## Per-Iteration Pipeline (no VLM)

Call `run_pipeline()` each iteration. It returns `(rgb_values, params)`. If re-calibration occurred, the returned `params` is new and must replace the old one.

```python
# Before the experiment loop — use the image captured after the initial 3 mixes
params = calibrate_camera("Base-colour-RGB-exp-1.jpg", vlm_model="qwen/qwen3-vl-235b-a22b-instruct")

# Each iteration — image shows the whole wellplate
rgb_values, params = run_pipeline(
    image_path="Base-colour-RGB-exp-1.jpg",
    params=params,
    expected_well_count=96,   # total wells on the plate (e.g. 96 for a 96-well plate)
)

# Select RGB for the specific wells that have mixes (by well index in row-major order)
# e.g. well A1 = index 0, A2 = index 1, A3 = index 2 for a 96-well plate
rgb_well_A1 = rgb_values[0]
rgb_well_A2 = rgb_values[1]
rgb_well_A3 = rgb_values[2]
```

### Level 1 — Apply Cached Params (no VLM)

| Step | Action | Output |
|---|---|---|
| 1 | Load raw image | PIL Image |
| 2 | Apply stored perspective correction coefficients (from `plate_corners`) to raw image | Flat corrected image |
| 3 | Apply stored `crop_box` to corrected image | Wellplate-only image |
| 4 | Extract ROI patches via sliding window for ALL wells | Per-well patches (whole plate) |
| 5 | Compute mean RGB per patch | `[(R,G,B), …]` — one per well |

**Entry point**: `run_level1(image_path, params)`

### Level 2 — Validation

| Check | Condition | Action if failed |
|---|---|---|
| RGB range | All R, G, B in 0–255 | Escalate to Level 3 |
| Patch count | Matches `expected_well_count` (total plate wells) | Escalate to Level 3 |
| Patch variance | Non-zero variance per patch (not blank/black) | Escalate to Level 3 |
| Colour spread | At least one channel differs by > 10 across wells with mixes | Warn; optionally escalate |

**Entry point**: `validate_results(patches, rgb_values, expected_well_count)`

### Level 3 — Fallback

**Step 1 — Retry Level 1**: Re-run with same cached params. Transient noise may have caused the failure.

**Step 2 — VLM re-calibration**: Call `recalibrate_and_run()` — re-runs the full `calibrate_camera()` flow on the current image and returns a **new `CameraParams`**. The caller must store the new params for all future iterations.

**Entry point**: `recalibrate_and_run(image_path, expected_well_count, vlm_model="qwen/qwen3-vl-235b-a22b-instruct")`

---

## Rules

- Always run `calibrate_camera()` before the experiment loop — never skip it.
- Use the image captured **after all initial mixes are dispensed** as the calibration reference image.
- VLM is called **only during calibration** — never inside the iteration loop.
- ROI size (`roi_w × roi_h`) must always be **smaller than the well size** — never equal or larger.
- ROI patches must be **centred** on each well position.
- ROI extraction covers the **entire wellplate** — all wells, not just the active ones. The caller filters by well index.
- Always store the `params` returned by `run_pipeline()` — it may be updated after re-calibration.
- If the camera is physically moved or adjusted, re-run `calibrate_camera()` manually.
- Save all raw, corrected, and cropped images for every session.
- If all three pipeline levels fail — stop, save the raw image, and report to the user.
