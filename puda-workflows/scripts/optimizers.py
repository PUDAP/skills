"""
Optimizers for colour mixing RMSE minimization.

Classes:
    BOOptimizer      — abstract base: GP fitting, normalisation, volume constraint
    BOOptimizerEI    — Bayesian Optimization with Expected Improvement (LogEI)
    BOOptimizerLCB   — Bayesian Optimization with Lower Confidence Bound (UCB)
    LLMOptimizer     — LLM-driven optimization via OpenRouter

Dependencies:
    pip install botorch gpytorch torch openai

Environment variable (LLMOptimizer only):
    OPENROUTER_API_KEY — your OpenRouter API key
"""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod

from openai import OpenAI

# torch / botorch / gpytorch are only required by the BO optimizers.
# Imported lazily inside BOOptimizer.__init__ so that LLMOptimizer can be
# used without installing the full torch stack.
try:
    import torch
    from botorch.acquisition import LogExpectedImprovement, UpperConfidenceBound
    from botorch.fit import fit_gpytorch_mll
    from botorch.models import SingleTaskGP
    from botorch.optim import optimize_acqf
    from gpytorch.mlls import ExactMarginalLogLikelihood
    _BO_AVAILABLE = True
except ImportError:
    _BO_AVAILABLE = False


# ---------------------------------------------------------------------------
# OpenRouter model shorthand lookup
# ---------------------------------------------------------------------------

OPENROUTER_MODELS: dict[str, str] = {
    "gpt-4o":            "openai/gpt-4o",
    "gpt-4.1":           "openai/gpt-4.1",
    "claude-sonnet-4-5": "anthropic/claude-sonnet-4-5",
    "claude-opus-4":     "anthropic/claude-opus-4",
    "gemini-2.5-pro":    "google/gemini-2.5-pro-preview",
    "llama-4-maverick":  "meta-llama/llama-4-maverick",
    "deepseek-r2":       "deepseek/deepseek-r2",
}


# ---------------------------------------------------------------------------
# Bayesian Optimization — base
# ---------------------------------------------------------------------------

class BOOptimizer(ABC):
    """
    Abstract base class for Bayesian Optimization of RGB colour mixing volumes.

    Maintains a running history of (volume_ratios, RMSE) observations, refits a
    SingleTaskGP surrogate after each observation, and suggests the next
    (R_vol, G_vol, B_vol) expected to reduce RMSE.

    Inputs are normalised to [0, 1] per dimension so that the equality constraint
    x1 + x2 + x3 = 1 is enforced directly in the optimisation. RMSE is negated
    because botorch maximises the acquisition function.

    Equality constraint: x1 + x2 + x3 = 1  (normalised space)
    This maps to R_vol + G_vol + B_vol = total_volume in µL.

    Args:
        total_volume (float): Total well volume in µL. All suggested volumes sum to this.
        num_restarts (int): Restarts for acquisition function optimisation. Default: 10.
        raw_samples (int): Raw samples for initialising the optimisation. Default: 64.
    """

    N_DIMS = 3  # R_vol, G_vol, B_vol

    # Equality constraint: indices [0,1,2], coefficients [1,1,1], rhs = 1.0
    # Enforces x1 + x2 + x3 = 1 in normalised space during optimize_acqf.
    _EQUALITY_CONSTRAINTS = [
        (
            torch.tensor([0, 1, 2]),          # indices of all three dimensions
            torch.tensor([1.0, 1.0, 1.0]),    # coefficients
            1.0,                               # rhs: x1 + x2 + x3 = 1
        )
    ]

    def __init__(
        self,
        total_volume: float,
        num_restarts: int = 10,
        raw_samples: int = 64,
    ) -> None:
        self.total_volume = total_volume
        self.num_restarts = num_restarts
        self.raw_samples = raw_samples

        self._bounds = torch.zeros(2, self.N_DIMS)
        self._bounds[1] = 1.0

        self._train_X: list[list[float]] = []  # normalised inputs
        self._train_Y: list[float] = []         # negated RMSE

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def observe(self, volumes: list[float], rmse: float) -> None:
        """
        Record a new observation.

        Args:
            volumes: [R_vol, G_vol, B_vol] in µL from the last protocol run.
            rmse: Measured RMSE for those volumes.
        """
        self._train_X.append([v / self.total_volume for v in volumes])
        self._train_Y.append(-rmse)

    def suggest(self) -> list[float]:
        """
        Suggest the next (R_vol, G_vol, B_vol) in µL.

        Refits the GP on all observations and optimises the acquisition function
        subject to the equality constraint x1 + x2 + x3 = 1 (normalised space),
        which guarantees the returned volumes sum to total_volume.

        Returns:
            [R_vol, G_vol, B_vol] in µL, guaranteed to sum to total_volume.

        Raises:
            RuntimeError: If called before any observations have been recorded.
        """
        if not self._train_X:
            raise RuntimeError("No observations recorded. Call observe() first.")

        train_X = torch.tensor(self._train_X, dtype=torch.double)
        train_Y = torch.tensor(self._train_Y, dtype=torch.double).unsqueeze(-1)

        model = self._fit_model(train_X, train_Y)
        acquisition = self._build_acquisition(model, train_Y)

        candidate, _ = optimize_acqf(
            acq_function=acquisition,
            bounds=self._bounds,
            q=1,
            num_restarts=self.num_restarts,
            raw_samples=self.raw_samples,
            equality_constraints=self._EQUALITY_CONSTRAINTS,
        )

        return self._denormalise_and_constrain(candidate)

    @property
    def n_observations(self) -> int:
        """Number of observations recorded so far."""
        return len(self._train_X)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fit_model(self, train_X: torch.Tensor, train_Y: torch.Tensor) -> SingleTaskGP:
        """
        Fit a SingleTaskGP surrogate on all observations.

        Args:
            train_X: Normalised input tensor, shape (n, 3).
            train_Y: Negated RMSE tensor, shape (n, 1).

        Returns:
            Fitted SingleTaskGP.
        """
        model = SingleTaskGP(train_X, train_Y)
        mll = ExactMarginalLogLikelihood(model.likelihood, model)
        fit_gpytorch_mll(mll)
        return model

    def _denormalise_and_constrain(self, candidate: torch.Tensor) -> list[float]:
        """
        Convert a normalised candidate back to µL.

        The equality constraint x1 + x2 + x3 = 1 is already enforced by
        optimize_acqf, so the candidate should sum to 1 in normalised space.
        The rescaling step below is a numerical safety clip only.

        Args:
            candidate: Optimised candidate, shape (1, 3), values in [0, 1]
                       satisfying x1 + x2 + x3 = 1.

        Returns:
            [R_vol, G_vol, B_vol] in µL summing to total_volume.
        """
        volumes = candidate.squeeze() * self.total_volume
        # Safety clip: re-normalise if floating-point drift breaks the sum
        total = volumes.sum().item()
        if abs(total - self.total_volume) > 1e-3:
            volumes = volumes / total * self.total_volume
        return volumes.tolist()

    @abstractmethod
    def _build_acquisition(self, model: SingleTaskGP, train_Y: torch.Tensor):
        """Build and return the acquisition function for this optimizer variant."""


# ---------------------------------------------------------------------------
# Bayesian Optimization — Expected Improvement
# ---------------------------------------------------------------------------

class BOOptimizerEI(BOOptimizer):
    """
    Bayesian Optimizer using Expected Improvement (LogEI) acquisition.

    Best for most cases — balances exploration and exploitation.
    Selects candidates most likely to improve over the current best observation.

    Args:
        total_volume (float): Total well volume in µL.
        num_restarts (int): Restarts for acquisition optimisation. Default: 10.
        raw_samples (int): Raw samples for initialisation. Default: 64.

    Example:
        optimizer = BOOptimizerEI(total_volume=300.0)
        for volumes, rmse in x_init_results:
            optimizer.observe(volumes, rmse)
        next_volumes = optimizer.suggest()
    """

    def _build_acquisition(
        self, model: SingleTaskGP, train_Y: torch.Tensor
    ) -> LogExpectedImprovement:
        """
        Build a LogExpectedImprovement acquisition function.

        Args:
            model: Fitted SingleTaskGP surrogate.
            train_Y: Negated RMSE observations, shape (n, 1).

        Returns:
            LogExpectedImprovement acquisition function.
        """
        return LogExpectedImprovement(model=model, best_f=train_Y.max())


# ---------------------------------------------------------------------------
# Bayesian Optimization — Lower Confidence Bound
# ---------------------------------------------------------------------------

class BOOptimizerLCB(BOOptimizer):
    """
    Bayesian Optimizer using Lower Confidence Bound (UCB) acquisition.

    More explorative than EI — useful when the RMSE landscape is uncertain or noisy.
    Higher beta increases exploration; lower beta increases exploitation.

    Args:
        total_volume (float): Total well volume in µL.
        beta (float): Exploration weight. Default: 1.0.
        num_restarts (int): Restarts for acquisition optimisation. Default: 10.
        raw_samples (int): Raw samples for initialisation. Default: 64.

    Example:
        optimizer = BOOptimizerLCB(total_volume=300.0, beta=1.0)
        for volumes, rmse in x_init_results:
            optimizer.observe(volumes, rmse)
        next_volumes = optimizer.suggest()
    """

    def __init__(
        self,
        total_volume: float,
        beta: float = 1.0,
        num_restarts: int = 10,
        raw_samples: int = 64,
    ) -> None:
        super().__init__(total_volume, num_restarts, raw_samples)
        self.beta = beta

    def _build_acquisition(
        self, model: SingleTaskGP, train_Y: torch.Tensor
    ) -> UpperConfidenceBound:
        """
        Build an UpperConfidenceBound acquisition function.

        Args:
            model: Fitted SingleTaskGP surrogate.
            train_Y: Negated RMSE observations (unused — UCB does not need best_f).

        Returns:
            UpperConfidenceBound acquisition function.
        """
        return UpperConfidenceBound(model=model, beta=self.beta)


# ---------------------------------------------------------------------------
# LLM Optimizer
# ---------------------------------------------------------------------------

class LLMOptimizer:
    """
    LLM-based optimizer for RGB colour mixing volume ratios via OpenRouter.

    Maintains the full iteration history and uses it as in-context learning in each
    prompt. Parses and validates the model's suggested volumes before returning them.

    Args:
        model (str): OpenRouter model identifier (e.g. "openai/gpt-4o").
                     Use OPENROUTER_MODELS for shorthand lookup.
        target_colour (tuple[int, int, int]): Target RGB (R, G, B), values 0–255.
        total_volume (float): Total well volume in µL. Suggested volumes must sum to this.
        api_key (str | None): OpenRouter API key. Falls back to OPENROUTER_API_KEY env var.
        max_retries (int): Times to re-prompt if the model returns invalid volumes. Default: 3.

    Example:
        optimizer = LLMOptimizer(
            model=OPENROUTER_MODELS["gpt-4o"],
            target_colour=(180, 60, 40),
            total_volume=300.0,
        )
        for volumes, rgb, rmse in x_init_results:
            optimizer.observe(volumes, rgb, rmse)
        next_volumes = optimizer.suggest()
    """

    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(
        self,
        model: str,
        target_colour: tuple[int, int, int],
        total_volume: float,
        api_key: str | None = None,
        max_retries: int = 3,
    ) -> None:
        self.model = model
        self.target_colour = target_colour
        self.total_volume = total_volume
        self.max_retries = max_retries

        self._client = OpenAI(
            base_url=self.OPENROUTER_BASE_URL,
            api_key=api_key or os.environ["OPENROUTER_API_KEY"],
        )

        # Each entry: {"iteration": int, "volumes": [R,G,B], "rgb": (R,G,B), "rmse": float}
        self._history: list[dict] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def observe(
        self,
        volumes: list[float],
        mixed_rgb: tuple[int, int, int],
        rmse: float,
    ) -> None:
        """
        Record a completed iteration result.

        Args:
            volumes: [R_vol, G_vol, B_vol] in µL used in the last protocol run.
            mixed_rgb: Measured RGB of the mixed colour (R, G, B), values 0–255.
            rmse: Measured RMSE for this iteration.
        """
        self._history.append({
            "iteration": len(self._history) + 1,
            "volumes": volumes,
            "rgb": mixed_rgb,
            "rmse": rmse,
        })

    def suggest(self) -> list[float]:
        """
        Ask the LLM for the next (R_vol, G_vol, B_vol) in µL.

        Builds a prompt with the full iteration history and validates that the
        returned volumes sum to total_volume. Re-prompts up to max_retries times
        if the response is invalid.

        Returns:
            [R_vol, G_vol, B_vol] in µL, summing to total_volume.

        Raises:
            RuntimeError: If no observations have been recorded.
            ValueError: If the model returns invalid volumes after all retries.
        """
        if not self._history:
            raise RuntimeError("No observations recorded. Call observe() first.")

        prompt = self._build_prompt()
        for attempt in range(1, self.max_retries + 1):
            try:
                raw = self._call_model(prompt)
                return self._parse_and_validate(raw)
            except (json.JSONDecodeError, KeyError, ValueError) as exc:
                if attempt == self.max_retries:
                    raise ValueError(
                        f"LLM returned invalid volumes after {self.max_retries} attempts: {exc}"
                    ) from exc
                prompt = self._build_retry_prompt(prompt, str(exc))

    @property
    def n_observations(self) -> int:
        """Number of observations recorded so far."""
        return len(self._history)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_prompt(self) -> str:
        """
        Build the optimization prompt with full iteration history.

        Returns:
            Formatted prompt string.
        """
        r_t, g_t, b_t = self.target_colour
        lines = [
            "You are helping optimize an RGB colour mixing experiment.",
            f"Target colour: ({r_t}, {g_t}, {b_t})",
            f"Total volume per well: {self.total_volume} µL",
            "",
            "History so far:",
            "| Iteration | R_vol (µL) | G_vol (µL) | B_vol (µL) | Mixed RGB | RMSE |",
            "|-----------|------------|------------|------------|-----------|------|",
        ]
        for e in self._history:
            r, g, b = e["volumes"]
            mr, mg, mb = e["rgb"]
            lines.append(
                f"| {e['iteration']} | {r:.1f} | {g:.1f} | {b:.1f} "
                f"| ({mr}, {mg}, {mb}) | {e['rmse']:.4f} |"
            )
        lines += [
            "",
            "Suggest the next (R_vol, G_vol, B_vol) in µL that you expect will reduce the RMSE.",
            f"Volumes must sum to exactly {self.total_volume} µL.",
            'Return only the three values as JSON: {"R_vol": <value>, "G_vol": <value>, "B_vol": <value>}',
        ]
        return "\n".join(lines)

    def _build_retry_prompt(self, original_prompt: str, error: str) -> str:
        """
        Build a corrective prompt when the previous response was invalid.

        Args:
            original_prompt: The original prompt sent to the model.
            error: Description of why the previous response was rejected.

        Returns:
            Updated prompt asking the model to correct the error.
        """
        return (
            original_prompt
            + f"\n\nYour previous response was rejected: {error}\n"
            f"Please correct it. Volumes must sum to exactly {self.total_volume} µL.\n"
            f'Return only JSON: {{"R_vol": <value>, "G_vol": <value>, "B_vol": <value>}}'
        )

    def _call_model(self, prompt: str) -> str:
        """
        Send a prompt to the OpenRouter model and return the raw response text.

        Args:
            prompt: Full prompt string.

        Returns:
            Raw text content from the model response.
        """
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def _parse_and_validate(self, response: str) -> list[float]:
        """
        Parse the model's JSON response and validate the volume constraint.

        Args:
            response: Raw model response, expected to contain JSON.

        Returns:
            [R_vol, G_vol, B_vol] in µL.

        Raises:
            json.JSONDecodeError: If the response is not valid JSON.
            KeyError: If required keys are missing.
            ValueError: If volumes do not sum to total_volume (±1 µL tolerance).
        """
        data = json.loads(response)
        r, g, b = float(data["R_vol"]), float(data["G_vol"]), float(data["B_vol"])

        if abs(r + g + b - self.total_volume) > 1.0:
            raise ValueError(
                f"Volumes sum to {r + g + b:.2f} µL, expected {self.total_volume} µL (±1 µL)."
            )

        return [r, g, b]
