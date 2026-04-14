---
name: colour-mixing-image-processing
description: Deterministic image processing pipeline using OpenCV homography warp, grid-based ROI slicing, and per-well RGB extraction. No VLM required. Calibrate once with ImageConfig; reuse for every captured image.
---

# Image Processing

**Script**: [../scripts/image_processing.py](../scripts/image_processing.py)  
**Dependencies**: `pip install numpy Pillow opencv-python`

---

## Design

The camera is in a fixed position. All geometry is calibrated once in `ImageConfig` and reused for every image. No VLM or runtime detection is needed.

```
run_pipeline(image_path, well_ids, config)
    │
    ├── Step 1  compute_homography(src_corners → plate rectangle)  →  H (3×3 matrix)
    ├── Step 2  cv2.warpPerspective(raw, H, output_size)           →  flat plate image
    ├── Step 3  get_grid_dimensions(plate, 12, 8)                  →  cell_w, cell_h
    ├── Step 4  slice_roi_patches(plate, 12, 8, offset_array)      →  96 ROI patches
    ├── Step 5  save_roi_debug_image(...)                          →  <name>_roi_debug.jpg
    └── Step 6  extract_well_rgb(patches, well_ids)                →  {well_id: (R,G,B)}
```

**Well orientation** — standard 96-well plate:

```
       col 1   col 2  …  col 12
row A   A1      A2         A12     ← top-left to top-right
row B   B1      B2         B12
 …
row H   H1      H2         H12     ← bottom-left to bottom-right
```

---

## `ImageConfig` — Calibrated Parameters

| Field | Type | Description |
|---|---|---|
| `src_corners` | `list[(x,y)]` × 4 | Wellplate corners in the **raw** image [TL, TR, BR, BL]. Measure from the actual photo. |
| `plate_width` | int | Width in pixels of the warped plate output. |
| `plate_height` | int | Height in pixels of the warped plate output. |
| `col_num` | int | Grid columns — `12` for plate columns 1–12 (left → right). |
| `row_num` | int | Grid rows — `8` for plate rows A–H (top → bottom). |
| `offset_array` | `[[xl,xr],[yt,yb]]` | Pixel inset per grid cell — keeps ROI inside the well, away from the rim. |

`dst_corners` and `output_size` are **auto-derived** properties:
- `dst_corners = [(0,0),(plate_width,0),(plate_width,plate_height),(0,plate_height)]`
- `output_size = (plate_width, plate_height)`

### Default Calibration (`DEFAULT_CONFIG`)

```python
DEFAULT_CONFIG = ImageConfig(
    src_corners=[(814, 20), (1615, 0), (1500, 820), (883, 790)],
    plate_width=1520,
    plate_height=1460,
    col_num=12,    # columns 1–12, left → right
    row_num=8,     # rows A–H, top → bottom
    offset_array=[[22, 22], [14, 14]],
)
```

---

## Step 1 — Homography Matrix

```
src_corners (raw image)  →  compute_homography()  →  H (3×3 float64)
```

`cv2.findHomography(src, dst, cv2.RANSAC)` fits the best projective transform mapping the four raw plate corners to the flat `plate_width × plate_height` rectangle. RANSAC makes it robust to small localisation errors.

Unlike an 8-coefficient approximation, a full homography matrix handles all projective distortions (rotation, shear, perspective tilt) correctly.

---

## Step 2 — Perspective Warp

```
raw image  →  cv2.warpPerspective(raw, H, output_size)  →  flat plate image
```

Every pixel in the output is back-projected through H to its source location in the raw image and interpolated with `cv2.INTER_CUBIC`. Result: a clean, upright, undistorted view of the wellplate exactly `plate_width × plate_height` pixels.

Saved as `<name>_warped.jpg`.

---

## Step 3 — Grid Dimensions

```python
cell_w, cell_h = get_grid_dimensions(plate_np, col_num=12, row_num=8)
# e.g. cell_w = 1520/12 ≈ 126.7 px,  cell_h = 1460/8 = 182.5 px
```

Divides the plate image dimensions by the grid counts to get the floating-point size of each well cell. Used by both `slice_roi_patches` and `crop_well`.

---

## Step 4 — ROI Grid Slicing

```
plate image  →  slice_roi_patches(plate, 12, 8, offset_array)  →  96 patches + 96 boxes
```

Each cell is shrunk inward by `offset_array` so the ROI sits inside the well and avoids the rim. Patches are in row-major order: A1, A2, …, A12, B1, …, H12.

### Single-well crop

`crop_well(plate_np, "B3", 12, 8, offset_array)` returns `(patch_array, (x1,y1,x2,y2))` for just that well, without slicing the whole grid.

---

## Step 5 — ROI Debug Image

After slicing, `save_roi_debug_image()` draws a **red rectangle** at every ROI patch and labels it with:
- **Well ID** (e.g. `A1`)
- **Patch size** (e.g. `82×138`)

```
┌─────────────────────────────────────────────────────────────┐
│  A1 82×138  A2 82×138  A3 82×138  …  A12 82×138            │
│  B1 82×138  B2 82×138  …                                    │
│  …                                                          │
│  H1 82×138  …          H12 82×138                           │
└─────────────────────────────────────────────────────────────┘
```

Saved as `<name>_roi_debug.jpg`.

**When RGB results look wrong, inspect this image first.** Misaligned rectangles mean `src_corners`, `offset_array`, or `crop_box` need adjusting.

---

## Step 6 — RGB Extraction

```python
rgb_values = extract_well_rgb(patches, well_ids=["A1","A2","A3"], col_num=12)
# → {"A1": (210, 45, 30), "A2": (30, 190, 55), "A3": (20, 40, 200)}
```

Uses **median** per channel to suppress outlier pixels (dust, reflections, bubbles).

---

## Usage

```python
from image_processing import run_pipeline, DEFAULT_CONFIG

rgb_values = run_pipeline(
    image_path="Base-colour-RGB-exp-1.jpg",
    well_ids=["A1", "A2", "A3"],
    config=DEFAULT_CONFIG,
    # optional — auto-derived from image_path if omitted:
    # warped_save_path="Base-colour-RGB-exp-1_warped.jpg",
    # roi_debug_save_path="Base-colour-RGB-exp-1_roi_debug.jpg",
)
# → {"A1": (210, 45, 30), "A2": (30, 190, 55), "A3": (20, 40, 200)}
```

### Saved files per run

| File | Description |
|---|---|
| `<name>_warped.jpg` | Homography-corrected flat plate image |
| `<name>_roi_debug.jpg` | Red ROI rectangles + well ID + `W×H` label at every well |

### Re-calibrating `src_corners`

Open the raw camera photo in any image viewer. Hover over each physical corner of the wellplate and read the `(x, y)` pixel coordinates:

```
src_corners = [
    (x_TL, y_TL),   # top-left  corner of the plate
    (x_TR, y_TR),   # top-right
    (x_BR, y_BR),   # bottom-right
    (x_BL, y_BL),   # bottom-left
]
```

`plate_width` and `plate_height` set the output resolution — increase them for higher-resolution ROI patches.

---

## Validation

`validate_results(rgb_values)` checks:

| Check | Condition | Failure action |
|---|---|---|
| RGB range | All R, G, B in 0–255 | `RuntimeError` |
| Colour spread | At least one channel varies by > 10 across active wells | `RuntimeError` — check dispense completed |

---

## Rules

- Recalibrate `src_corners` whenever the camera is physically moved or refocused.
- Capture **one image per iteration** after all dispenses are complete and the pipette arm is clear.
- `run_pipeline()` always saves the warped image and the ROI debug image every call.
- Inspect `<name>_roi_debug.jpg` first when RGB results look wrong.
