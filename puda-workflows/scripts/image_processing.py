"""
Image processing pipeline for colour mixing experiments.

CameraParams (plate corners, ROI size, stride) are detected by Qwen3 VL 32B
Instruct ONCE during calibration at the start of the experiment, then cached
and reused for every iteration without further VLM calls.

VLM re-calibration is only triggered when Level 2 validation keeps failing
across multiple retries, indicating the camera may have shifted.

Perspective correction uses PIL's Image.PERSPECTIVE transform and a
find_coeffs() solver — no OpenCV required.

Three-level pipeline:
    Level 1  — Apply cached perspective correction, extract ROI patches,
               compute mean RGB. No VLM call per iteration.
    Level 2  — Plausibility validation of extracted RGB values.
    Level 3  — Retry Level 1, then re-calibrate via VLM if camera shifted.

Default model: "qwen/qwen3-vl-32b-instruct"

Dependencies:
    pip install numpy Pillow openai
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

import numpy as np
from PIL import Image


# ---------------------------------------------------------------------------
# Camera parameters dataclass
# ---------------------------------------------------------------------------

@dataclass
class CameraParams:
    """
    Cached camera calibration parameters.

    Detected by VLM once before the experiment loop starts.
    Passed into run_level1() for every iteration — no VLM call per iteration.
    Re-calibrate only if the camera shifts.

    Attributes:
        plate_corners: Four plate corners in the raw image, ordered
                       [TL, TR, BR, BL], each as [x, y] in pixels.
        roi_w:         Width of a single well ROI patch in pixels.
        roi_h:         Height of a single well ROI patch in pixels.
        stride_x:      Horizontal step between adjacent well centres in pixels.
        stride_y:      Vertical step between adjacent well centres in pixels.
    """
    plate_corners: list[list[float]]
    roi_w: int
    roi_h: int
    stride_x: int
    stride_y: int

    @property
    def output_size(self) -> tuple[int, int]:
        """
        (width, height) of the perspective-corrected output image.
        Derived from the real distances between the detected plate corners.
        """
        pts = np.array(self.plate_corners, dtype=np.float64)
        tl, tr, br, bl = pts
        top_w    = int(np.linalg.norm(tr - tl))
        bottom_w = int(np.linalg.norm(br - bl))
        left_h   = int(np.linalg.norm(bl - tl))
        right_h  = int(np.linalg.norm(br - tr))
        return max(top_w, bottom_w), max(left_h, right_h)

    @property
    def reference_rect(self) -> list[tuple[int, int]]:
        """Flat destination rectangle matching output_size, ordered TL, TR, BR, BL."""
        w, h = self.output_size
        return [(0, 0), (w, 0), (w, h), (0, h)]


# ---------------------------------------------------------------------------
# Perspective correction (PIL-based, no OpenCV)
# ---------------------------------------------------------------------------

def find_coeffs(
    pa: list[tuple[int, int]],
    pb: list[tuple[int, int]],
) -> list[float]:
    """
    Compute 8 perspective transformation coefficients for PIL's Image.PERSPECTIVE.

    Solves the least-squares system mapping source points (pa) to destination
    points (pb).  Pass to img.transform(..., Image.PERSPECTIVE, coeffs, ...).

    Args:
        pa: Four points in the OUTPUT image (destination), e.g. a flat rectangle.
        pb: Four corresponding points in the INPUT image (source plate corners).

    Returns:
        List of 8 floats [a, b, c, d, e, f, g, h] for use in img.transform().
    """
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0] * p1[0], -p2[0] * p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1] * p1[0], -p2[1] * p1[1]])
    A = np.array(matrix, dtype=np.float64)
    B = np.array(pb, dtype=np.float64).reshape(8)
    res = np.linalg.lstsq(A, B, rcond=None)[0]
    return res.tolist()


def apply_perspective_correction(
    image_pil: Image.Image,
    params: CameraParams,
) -> Image.Image:
    """
    Apply perspective correction using cached CameraParams.

    Maps the detected plate corners to a flat rectangle, producing a
    top-down view of the plate at the natural plate dimensions.

    Args:
        image_pil: Raw captured PIL Image.
        params: Cached CameraParams (plate_corners, output_size, reference_rect).

    Returns:
        Perspective-corrected PIL Image sized params.output_size.
    """
    coeffs = find_coeffs(params.reference_rect, params.plate_corners)
    return image_pil.transform(
        params.output_size,
        Image.PERSPECTIVE,
        coeffs,
        Image.BICUBIC,
    )


# ---------------------------------------------------------------------------
# ROI extraction and RGB computation
# ---------------------------------------------------------------------------

def extract_roi_patches(
    image: np.ndarray,
    roi_w: int,
    roi_h: int,
    stride_x: int,
    stride_y: int,
) -> list[np.ndarray]:
    """
    Slide a window across the corrected plate image to extract per-well patches.

    Args:
        image: Perspective-corrected plate image as a NumPy array (H, W, 3).
        roi_w: ROI patch width in pixels.
        roi_h: ROI patch height in pixels.
        stride_x: Horizontal step between adjacent well centres in pixels.
        stride_y: Vertical step between adjacent well centres in pixels.

    Returns:
        List of ROI patches as NumPy arrays, in row-major order.
    """
    patches = []
    h, w = image.shape[:2]
    for y in range(0, h - roi_h + 1, stride_y):
        for x in range(0, w - roi_w + 1, stride_x):
            patches.append(image[y:y + roi_h, x:x + roi_w])
    return patches


def mean_rgb(patch: np.ndarray) -> tuple[int, int, int]:
    """
    Compute the mean RGB of a patch.

    Args:
        patch: ROI image patch as a NumPy array (H, W, 3) in RGB.

    Returns:
        (R, G, B) mean values as integers 0–255.
    """
    mean = patch.mean(axis=(0, 1))
    return tuple(int(v) for v in mean)


# ---------------------------------------------------------------------------
# VLM helper
# ---------------------------------------------------------------------------

DEFAULT_VLM_MODEL = "qwen/qwen3-vl-32b-instruct"


def _vlm_call(
    image_path: str,
    prompt: str,
    model: str = DEFAULT_VLM_MODEL,
    api_key: str | None = None,
) -> dict:
    """
    Send an image + prompt to Qwen3 VL 32B via OpenRouter and parse JSON.

    Args:
        image_path: Path to the image file.
        prompt: Instruction prompt asking for a JSON response.
        model: OpenRouter model identifier.
        api_key: OpenRouter API key. Falls back to OPENROUTER_API_KEY env var.

    Returns:
        Parsed JSON dict from the VLM response.

    Raises:
        ValueError: If the response cannot be parsed as valid JSON.
    """
    import base64
    from openai import OpenAI

    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key or os.environ["OPENROUTER_API_KEY"],
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                ],
            }
        ],
    )
    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(f"VLM returned invalid JSON:\n{content}") from exc


# ---------------------------------------------------------------------------
# Calibration (run once before the experiment loop)
# ---------------------------------------------------------------------------

VLM_CALIBRATE_CORNERS_PROMPT = """\
This is an image captured by an external camera showing a laboratory well plate.

Identify the well plate and return its four corner pixel coordinates in the image.

Return ONLY valid JSON, no explanation:
{
  "plate_corners": [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
}

Order: top-left, top-right, bottom-right, bottom-left.
"""

VLM_CALIBRATE_ROI_PROMPT = """\
This is a perspective-corrected top-down image of a laboratory well plate.

Analyse the image and return:
1. roi_size — [width, height] in pixels of a single well ROI patch.
2. stride   — [stride_x, stride_y] in pixels between adjacent well centres.

Return ONLY valid JSON, no explanation:
{
  "roi_size": [roi_w, roi_h],
  "stride": [stride_x, stride_y]
}
"""


def calibrate_camera(
    reference_image_path: str,
    vlm_model: str = DEFAULT_VLM_MODEL,
    vlm_api_key: str | None = None,
    corrected_save_path: str | None = None,
) -> CameraParams:
    """
    Detect plate corners and ROI parameters from a reference image.

    Call this ONCE before the experiment loop starts.
    The returned CameraParams are reused for every iteration.
    Re-call only if the camera shifts.

    Steps:
        1. Qwen3 VL detects plate corners from the raw image.
        2. PIL applies perspective correction using the detected corners.
        3. Save the corrected image.
        4. Qwen3 VL infers roi_size and stride from the corrected image.

    Args:
        reference_image_path: Path to a representative image (e.g. the first
                               capture, or a blank-plate setup image).
        vlm_model: OpenRouter model identifier.
        vlm_api_key: OpenRouter API key (optional, falls back to env var).
        corrected_save_path: Optional path to save the corrected reference image.

    Returns:
        CameraParams ready to pass into run_level1() for all iterations.
    """
    # Step 1: VLM detects plate corners
    corners_resp = _vlm_call(reference_image_path, VLM_CALIBRATE_CORNERS_PROMPT, vlm_model, vlm_api_key)
    plate_corners = corners_resp["plate_corners"]

    # Step 2: Build temporary params (without ROI yet) and apply correction
    temp_params = CameraParams(plate_corners=plate_corners, roi_w=0, roi_h=0, stride_x=0, stride_y=0)
    image_pil = Image.open(reference_image_path).convert("RGB")
    corrected_pil = apply_perspective_correction(image_pil, temp_params)

    # Step 3: Save corrected image for ROI inference
    if corrected_save_path is None:
        base, ext = os.path.splitext(reference_image_path)
        corrected_save_path = f"{base}_calibrated{ext or '.jpg'}"
    corrected_pil.save(corrected_save_path)

    # Step 4: VLM infers ROI params from corrected image
    roi_resp = _vlm_call(corrected_save_path, VLM_CALIBRATE_ROI_PROMPT, vlm_model, vlm_api_key)
    roi_w, roi_h = roi_resp["roi_size"]
    stride_x, stride_y = roi_resp["stride"]

    return CameraParams(
        plate_corners=plate_corners,
        roi_w=roi_w,
        roi_h=roi_h,
        stride_x=stride_x,
        stride_y=stride_y,
    )


# ---------------------------------------------------------------------------
# Level 1 — Per-iteration processing (no VLM call)
# ---------------------------------------------------------------------------

def run_level1(
    image_path: str,
    params: CameraParams,
    corrected_save_path: str | None = None,
) -> tuple[list[np.ndarray], list[tuple[int, int, int]]]:
    """
    Process one captured image using cached CameraParams.

    No VLM call is made. All geometric parameters come from the cached params.

    Flow:
        1. Load raw image
        2. Apply perspective correction using params.plate_corners
        3. Extract ROI patches using params.roi_w / roi_h / stride_x / stride_y
        4. Compute mean RGB per patch

    Args:
        image_path: Path to the captured image for this iteration.
        params: CameraParams from calibrate_camera() — reused every iteration.
        corrected_save_path: Optional path to save the corrected image for audit.

    Returns:
        (patches, rgb_values) — list of ROI patches and their mean RGB tuples.
    """
    # Step 1: Load image
    image_pil = Image.open(image_path).convert("RGB")

    # Step 2: Perspective correction
    corrected_pil = apply_perspective_correction(image_pil, params)

    # Save corrected image for audit
    if corrected_save_path is None:
        base, ext = os.path.splitext(image_path)
        corrected_save_path = f"{base}_corrected{ext or '.jpg'}"
    corrected_pil.save(corrected_save_path)

    # Step 3: Extract ROI patches
    corrected_np = np.array(corrected_pil)
    patches = extract_roi_patches(corrected_np, params.roi_w, params.roi_h, params.stride_x, params.stride_y)

    # Step 4: Compute mean RGB
    rgb_values = [mean_rgb(p) for p in patches]

    return patches, rgb_values


# ---------------------------------------------------------------------------
# Level 2 — Validation
# ---------------------------------------------------------------------------

def validate_results(
    patches: list[np.ndarray],
    rgb_values: list[tuple[int, int, int]],
    expected_well_count: int,
    min_variance: float = 1.0,
    min_colour_spread: int = 10,
) -> tuple[bool, list[str]]:
    """
    Validate that Level 1 results are plausible before passing to the optimizer.

    Checks:
        1. RGB range      — all values in 0–255
        2. Patch count    — matches expected_well_count
        3. Patch variance — each patch has non-zero pixel variance (not blank/black)
        4. Colour spread  — at least one channel differs by > min_colour_spread across wells

    Args:
        patches: List of extracted ROI patches.
        rgb_values: List of (R, G, B) mean values per patch.
        expected_well_count: Number of wells expected.
        min_variance: Minimum acceptable pixel variance per patch. Default: 1.0.
        min_colour_spread: Minimum channel range across wells. Default: 10.

    Returns:
        (passed, failures) — passed is True if all checks pass.
    """
    failures = []

    for i, (r, g, b) in enumerate(rgb_values):
        if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
            failures.append(f"Well {i}: RGB ({r},{g},{b}) out of 0–255 range.")

    if len(patches) != expected_well_count:
        failures.append(
            f"Patch count {len(patches)} does not match expected {expected_well_count} wells."
        )

    for i, patch in enumerate(patches):
        if patch.var() < min_variance:
            failures.append(f"Well {i}: patch variance {patch.var():.2f} below threshold {min_variance}.")

    if rgb_values:
        for ch in range(3):
            values = [rgb[ch] for rgb in rgb_values]
            if (max(values) - min(values)) >= min_colour_spread:
                break
        else:
            failures.append(
                f"All wells have nearly identical colours — spread < {min_colour_spread} on all channels."
            )

    return len(failures) == 0, failures


# ---------------------------------------------------------------------------
# Level 3 — Re-calibration (camera shifted)
# ---------------------------------------------------------------------------

def recalibrate_and_run(
    image_path: str,
    expected_well_count: int,
    vlm_model: str = DEFAULT_VLM_MODEL,
    vlm_api_key: str | None = None,
) -> tuple[list[np.ndarray], list[tuple[int, int, int]], CameraParams]:
    """
    Re-run VLM calibration on the current image and immediately process it.

    Called when Level 2 validation keeps failing, suggesting the camera has
    shifted since the initial calibrate_camera() call.

    Args:
        image_path: Path to the current captured image.
        expected_well_count: Number of wells expected.
        vlm_model: OpenRouter model identifier.
        vlm_api_key: OpenRouter API key (optional).

    Returns:
        (patches, rgb_values, new_params) — new_params should be stored by
        the caller to replace the old CameraParams for future iterations.
    """
    new_params = calibrate_camera(image_path, vlm_model, vlm_api_key)
    patches, rgb_values = run_level1(image_path, new_params)
    return patches, rgb_values, new_params


# ---------------------------------------------------------------------------
# Full pipeline entry point
# ---------------------------------------------------------------------------

def run_pipeline(
    image_path: str,
    params: CameraParams,
    expected_well_count: int,
    vlm_model: str = DEFAULT_VLM_MODEL,
    vlm_api_key: str | None = None,
) -> tuple[list[tuple[int, int, int]], CameraParams]:
    """
    Run the full three-level pipeline for one iteration.

    Level 1 uses cached CameraParams — no VLM call unless camera has shifted.
    Returns updated CameraParams so the caller can detect if re-calibration occurred.

    Args:
        image_path: Path to the captured image for this iteration.
        params: CameraParams from calibrate_camera() or a previous run_pipeline() call.
        expected_well_count: Number of wells expected.
        vlm_model: OpenRouter model identifier.
        vlm_api_key: OpenRouter API key (optional, falls back to env var).

    Returns:
        (rgb_values, params) — params is unchanged unless re-calibration occurred,
        in which case the new CameraParams is returned for use in future iterations.

    Raises:
        RuntimeError: If all three levels fail.
    """
    # Level 1: use cached params — no VLM call
    patches, rgb_values = run_level1(image_path, params)

    # Level 2: validate
    passed, failures = validate_results(patches, rgb_values, expected_well_count)
    if passed:
        return rgb_values, params

    # Level 3a: retry Level 1 with same params
    try:
        patches, rgb_values = run_level1(image_path, params)
        passed, failures = validate_results(patches, rgb_values, expected_well_count)
        if passed:
            return rgb_values, params
    except Exception:
        pass

    # Level 3b: camera may have shifted — re-calibrate via VLM
    try:
        patches, rgb_values, new_params = recalibrate_and_run(
            image_path, expected_well_count, vlm_model, vlm_api_key
        )
        passed, failures = validate_results(patches, rgb_values, expected_well_count)
        if passed:
            return rgb_values, new_params   # caller should update their stored params
    except Exception:
        pass

    raise RuntimeError(
        f"All three pipeline levels failed. Final failures: {failures}. "
        "Save the raw image and report to the user for manual inspection."
    )
