"""
Image processing pipeline for colour mixing experiments.

CameraParams (plate corners, wellplate crop box, ROI size, and stride) are
detected by Qwen3 VL 32B Instruct ONCE during calibration — triggered on the
first image captured after all initial mixes are dispensed. Parameters are
cached and reused for every iteration without further VLM calls.

VLM re-calibration is only triggered when Level 2 validation keeps failing
across multiple retries, indicating the camera may have shifted.

Perspective correction uses PIL's Image.PERSPECTIVE transform and a
find_coeffs() solver — no OpenCV required.

Calibration flow (run once):
    Step 1  — VLM detects the four outer corners of the OT-2 DECK PLATFORM
              from the raw angled camera image (not individual labware corners)
    Step 2  — Apply perspective correction → flat top-down view of the full deck
    Step 3  — VLM locates the target wellplate in the corrected deck image
              and returns its crop_box in corrected image pixels
    Step 4  — Crop corrected deck image to the wellplate area
    Step 5  — VLM detects ROI patch size and stride from the cropped wellplate image

Three-level per-iteration pipeline (no VLM):
    Level 1  — Correct perspective → crop to plate →
               extract ROI patches for ALL wells → compute mean RGB per well.
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
        crop_box:      Bounding box [x1, y1, x2, y2] of the wellplate region
                       in the perspective-corrected image. Used to isolate the
                       plate area before ROI extraction.
        roi_w:         Width of a single well ROI patch in pixels. Must be
                       smaller than the physical well diameter in pixels.
        roi_h:         Height of a single well ROI patch in pixels. Must be
                       smaller than the physical well diameter in pixels.
        stride_x:      Horizontal step between adjacent well centres in pixels.
        stride_y:      Vertical step between adjacent well centres in pixels.
    """
    plate_corners: list[list[float]]
    crop_box: list[int]
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
    Slide a window across the cropped wellplate image to extract per-well patches.

    Covers every well on the plate in row-major order (left to right, top to
    bottom). Patches are extracted for ALL wells regardless of whether they
    contain a mix — the caller filters by well index for active wells.

    Args:
        image: Cropped wellplate image as a NumPy array (H, W, 3), RGB.
               Must be the output of crop(crop_box), not the raw corrected image.
        roi_w: ROI patch width in pixels (must be smaller than the well diameter).
        roi_h: ROI patch height in pixels (must be smaller than the well diameter).
        stride_x: Horizontal step between adjacent well centres in pixels.
        stride_y: Vertical step between adjacent well centres in pixels.

    Returns:
        List of ROI patches as NumPy arrays (H, W, 3), in row-major order.
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
This is an image captured by an overhead camera mounted above an Opentrons OT-2 \
liquid handling robot. The camera is slightly angled, so the image is not a \
perfect top-down view — the deck appears in perspective.

Your task is to find the four outer corners of the OT-2 deck platform (the large \
flat white/light-grey rectangular surface that holds all the labware). These \
corners will be used to apply a perspective correction that produces a flat, \
straight top-down view of the entire deck.

Do NOT return corners of any individual labware item (well plates, tip racks, \
vials, etc.). Return the corners of the DECK PLATFORM BOUNDARY itself.

Return ONLY valid JSON, no explanation:
{
  "plate_corners": [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
}

Order: top-left, top-right, bottom-right, bottom-left of the deck platform.
"""

VLM_CALIBRATE_CROP_PROMPT = """\
This is a perspective-corrected flat top-down view of an Opentrons OT-2 deck. \
The deck contains multiple labware items arranged in a 3×3 slot grid.

Identify the WELL PLATE labware that contains circular wells arranged in a grid \
(it may be a 96-well, 24-well, or 12-well plate). Return the tight bounding \
rectangle around ONLY that well plate — not the whole deck, not any other labware.

Return pixel coordinates measured in THIS corrected image. Do NOT reference any \
transformation or use coordinates from the original raw image.

Return ONLY valid JSON, no explanation:
{
  "crop_box": [x1, y1, x2, y2]
}

x1, y1 = top-left pixel of the well plate in this corrected image.
x2, y2 = bottom-right pixel of the well plate in this corrected image.
"""

VLM_CALIBRATE_ROI_PROMPT = """\
This is a cropped top-down image of a single laboratory well plate \
(only the plate area is visible, not the surrounding deck).

Analyse the image and return:
1. roi_size — [width, height] in pixels of a single well ROI patch. \
   The patch must be SMALLER than the well diameter so it captures only the \
   interior colour and avoids the well edge.
2. stride   — [stride_x, stride_y] in pixels between adjacent well centres \
   (centre-to-centre distance, not edge-to-edge).

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
    cropped_save_path: str | None = None,
    plate_description: str | None = None,
) -> CameraParams:
    """
    Detect deck corners, perspective-correct the full deck image, locate the
    target wellplate, and extract ROI parameters.

    Call this ONCE before the experiment loop starts.
    The returned CameraParams are reused for every iteration.
    Re-call only if the camera shifts or the plate is repositioned.

    Steps:
        1. VLM detects the four outer corners of the OT-2 DECK PLATFORM from
           the raw image (not the wellplate — the whole deck). These are used
           to compute a perspective transform that produces a flat top-down view
           of the entire deck.
        2. PIL applies perspective correction to the raw image → flat deck image.
        3. VLM receives the corrected deck image and locates the target wellplate
           (the labware with circular wells). Returns crop_box in corrected
           image pixels.
        4. PIL crops the corrected image to the wellplate area.
        5. VLM detects ROI patch size and well stride from the cropped image.

    Args:
        reference_image_path: Path to a reference image captured after the
                               initial mixes are dispensed, showing the whole
                               OT-2 deck with the wellplate visible.
        vlm_model: OpenRouter model identifier.
        vlm_api_key: OpenRouter API key (optional, falls back to env var).
        corrected_save_path: Optional path to save the perspective-corrected
                             full deck image.
        cropped_save_path: Optional path to save the cropped wellplate image.
        plate_description: Optional hint for the VLM when locating the wellplate
                           (e.g. "96-well plate in slot 5", "24-well plate").
                           If None, the VLM uses visual features to identify it.

    Returns:
        CameraParams ready to pass into run_level1() for all iterations.
    """
    base, ext = os.path.splitext(reference_image_path)
    ext = ext or ".jpg"

    # Step 1: VLM detects the OT-2 deck platform corners from the raw image.
    # Using deck corners (not individual labware) gives a stable reference for
    # full-deck perspective correction.
    raw_pil = Image.open(reference_image_path).convert("RGB")
    corners_resp = _vlm_call(reference_image_path, VLM_CALIBRATE_CORNERS_PROMPT, vlm_model, vlm_api_key)
    plate_corners = corners_resp["plate_corners"]

    # Step 2: Apply perspective correction — flattens the tilted camera view
    # into a straight top-down view of the entire deck.
    temp_params = CameraParams(
        plate_corners=plate_corners,
        crop_box=[0, 0, 0, 0],
        roi_w=0,
        roi_h=0,
        stride_x=0,
        stride_y=0,
    )
    corrected_pil = apply_perspective_correction(raw_pil, temp_params)
    if corrected_save_path is None:
        corrected_save_path = f"{base}_calibrated{ext}"
    corrected_pil.save(corrected_save_path)

    # Step 3: VLM receives the corrected flat deck image and locates the
    # target wellplate. Optionally inject a plate_description hint.
    crop_prompt = VLM_CALIBRATE_CROP_PROMPT
    if plate_description:
        crop_prompt = (
            f"The target well plate is: {plate_description}.\n\n" + crop_prompt
        )
    crop_resp = _vlm_call(corrected_save_path, crop_prompt, vlm_model, vlm_api_key)
    crop_box = crop_resp["crop_box"]  # [x1, y1, x2, y2] in corrected image pixels

    # Step 4: Crop the corrected deck image to the wellplate area only.
    cropped_pil = corrected_pil.crop(tuple(crop_box))
    if cropped_save_path is None:
        cropped_save_path = f"{base}_calibrated_cropped{ext}"
    cropped_pil.save(cropped_save_path)

    # Step 5: VLM detects ROI patch size and well stride from the cropped image.
    roi_resp = _vlm_call(cropped_save_path, VLM_CALIBRATE_ROI_PROMPT, vlm_model, vlm_api_key)
    roi_w, roi_h = roi_resp["roi_size"]
    stride_x, stride_y = roi_resp["stride"]

    return CameraParams(
        plate_corners=plate_corners,
        crop_box=crop_box,
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
    cropped_save_path: str | None = None,
) -> tuple[list[np.ndarray], list[tuple[int, int, int]]]:
    """
    Process one captured image using cached CameraParams. No VLM call is made.

    Applies the stored perspective correction coefficients to the raw image,
    crops to the wellplate bounding box, then extracts ROI patches for every
    well across the entire plate.

    Flow:
        1. Load raw image
        2. Apply perspective correction (stored plate_corners → coefficients)
        3. Crop corrected image to wellplate area (stored crop_box)
        4. Extract ROI patches for ALL wells via sliding window
           (stored roi_w / roi_h / stride_x / stride_y)
        5. Compute mean RGB per well

    Args:
        image_path: Path to the captured image for this iteration.
                    The image must show the complete wellplate.
        params: CameraParams from calibrate_camera() — reused every iteration.
        corrected_save_path: Optional path to save the corrected image for audit.
        cropped_save_path: Optional path to save the cropped wellplate image for audit.

    Returns:
        (patches, rgb_values) — ROI patches and mean RGB tuples for every well
        across the whole plate, in row-major order (left to right, top to bottom).
        The caller selects specific well indices to get RGB for active wells.
    """
    base, ext = os.path.splitext(image_path)
    ext = ext or ".jpg"

    # Step 1: Load raw image
    raw_pil = Image.open(image_path).convert("RGB")

    # Step 2: Perspective correction
    corrected_pil = apply_perspective_correction(raw_pil, params)
    if corrected_save_path is None:
        corrected_save_path = f"{base}_corrected{ext}"
    corrected_pil.save(corrected_save_path)

    # Step 3: Crop to wellplate area of interest
    cropped_pil = corrected_pil.crop(tuple(params.crop_box))
    if cropped_save_path is None:
        cropped_save_path = f"{base}_cropped{ext}"
    cropped_pil.save(cropped_save_path)

    # Step 4: Extract ROI patches for ALL wells in the plate (sliding window)
    cropped_np = np.array(cropped_pil)
    patches = extract_roi_patches(cropped_np, params.roi_w, params.roi_h, params.stride_x, params.stride_y)

    # Step 5: Compute mean RGB per well
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

    Processes the whole wellplate image: corrects perspective, crops to the
    plate bounding box, extracts ROI patches for every well, and returns the
    mean RGB for each well. The caller selects the specific well indices that
    correspond to dispensed mixes.

    Level 1 uses cached CameraParams — no VLM call unless camera has shifted.
    Returns updated CameraParams so the caller can detect if re-calibration occurred.

    Args:
        image_path: Path to the captured image for this iteration.
                    The image should show the complete wellplate.
        params: CameraParams from calibrate_camera() or a previous run_pipeline() call.
        expected_well_count: Total number of wells in the plate (e.g. 96 for a
                             96-well plate). Used to validate the extracted patch count.
        vlm_model: OpenRouter model identifier.
        vlm_api_key: OpenRouter API key (optional, falls back to env var).

    Returns:
        (rgb_values, params) — rgb_values is a list of (R, G, B) tuples, one per
        well in row-major order. params is unchanged unless re-calibration occurred,
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
