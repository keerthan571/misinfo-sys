
"""Experimental X future-view forecaster.

Uses a historical median daily log-growth baseline plus a fixed-strength
engagement adjustment. The adjustment is experimental and is not a causal
estimate.

Missing engagement values remain missing. Views are an audience-exposure
proxy, not verified unique reach.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Mapping, Any
import json
import math

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "future_audience_feature_table.csv"
)

MAX_HORIZON_DAYS = 88

ENGAGEMENT_FIELDS = (
    "likes",
    "comments",
    "shares",
    "reposts",
    "bookmarks",
    "replies",
    "quotes",
)

MIN_TRAINING_ROWS = 8
RATE_MIN = -0.03
RATE_MAX = 0.08

# Fixed strength tested in the latest leave-one-out experiment.
ENGAGEMENT_ADJUSTMENT_STRENGTH = 0.5

# Maximum absolute change in daily log-growth rate.
MAX_DAILY_ADJUSTMENT = 0.01


def _load_x_pairs(
    data_path: Optional[Path] = None,
) -> pd.DataFrame:
    path = Path(data_path) if data_path is not None else DATA_PATH

    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path)

    required = {
        "platform",
        "elapsed_days",
        "views_earlier",
        "views_latest",
        "post_age_earlier_days",
    }

    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Dataset missing columns: {sorted(missing)}"
        )

    df["platform"] = (
        df["platform"].astype(str).str.strip().str.lower()
    )
    df = df[df["platform"].isin({"x", "twitter"})].copy()

    numeric = [
        "elapsed_days",
        "views_earlier",
        "views_latest",
        "post_age_earlier_days",
    ] + [f"{metric}_earlier" for metric in ENGAGEMENT_FIELDS]

    for col in numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        elif col.endswith("_earlier"):
            df[col] = np.nan

    df = df.dropna(
        subset=["elapsed_days", "views_earlier", "views_latest"]
    )

    df = df[
        (df["elapsed_days"] > 0)
        & (df["views_earlier"] >= 0)
        & (df["views_latest"] >= 0)
    ].copy()

    # Invalid or unavailable engagement values remain NaN.
    for metric in ENGAGEMENT_FIELDS:
        col = f"{metric}_earlier"
        df.loc[df[col] < 0, col] = np.nan

    return df.reset_index(drop=True)


def _daily_rates(df: pd.DataFrame) -> np.ndarray:
    start = np.log1p(
        df["views_earlier"].to_numpy(dtype=float)
    )
    end = np.log1p(
        df["views_latest"].to_numpy(dtype=float)
    )
    days = df["elapsed_days"].to_numpy(dtype=float)

    return (end - start) / days


def _baseline_rate(rates: np.ndarray) -> float:
    valid = np.asarray(rates, dtype=float)
    valid = valid[np.isfinite(valid)]

    if len(valid) == 0:
        return 0.0

    return float(
        np.median(np.clip(valid, RATE_MIN, RATE_MAX))
    )


def _views_from_rate(
    start_views: float,
    rate: float,
    days: float,
) -> float:
    log_views = np.log1p(start_views) + rate * days

    return max(
        0.0,
        float(np.expm1(np.clip(log_views, -20, 30))),
    )


def _engagement_signal(
    views: float,
    engagement: Mapping[str, Optional[float]],
) -> float:
    """Build one bounded engagement-per-view signal.

    Only available, non-negative engagement values are used.
    Missing values are omitted, not replaced with zero.
    """
    safe_views = max(float(views), 0.0)
    denominator = max(safe_views, 1.0)
    values = []

    for metric in ENGAGEMENT_FIELDS:
        raw = engagement.get(metric)

        if raw is None:
            continue

        try:
            value = float(raw)
        except (TypeError, ValueError):
            continue

        if not math.isfinite(value) or value < 0:
            continue

        ratio = value / denominator
        transformed = math.tanh(math.log1p(ratio * 1000.0))
        values.append(float(transformed))

    if not values:
        return float("nan")

    return float(np.mean(values))


def _training_signals(df: pd.DataFrame) -> np.ndarray:
    signals = []

    for _, row in df.iterrows():
        engagement = {
            metric: row.get(f"{metric}_earlier")
            for metric in ENGAGEMENT_FIELDS
        }

        signals.append(
            _engagement_signal(
                float(row["views_earlier"]),
                engagement,
            )
        )

    return np.asarray(signals, dtype=float)


def _adjustment_from_signal(
    signal: float,
    training_signals: np.ndarray,
    strength: float = ENGAGEMENT_ADJUSTMENT_STRENGTH,
) -> float:
    """Calculate a robust, capped engagement adjustment."""
    available = np.asarray(training_signals, dtype=float)
    available = available[np.isfinite(available)]

    if not math.isfinite(signal) or len(available) < 3:
        return 0.0

    center = float(np.median(available))
    mad = float(np.median(np.abs(available - center)))

    if mad < 1e-9:
        return 0.0

    standardized = (signal - center) / (1.4826 * mad)
    standardized = float(np.clip(standardized, -2.0, 2.0))

    return float(
        np.clip(
            strength * standardized * 0.005,
            -MAX_DAILY_ADJUSTMENT,
            MAX_DAILY_ADJUSTMENT,
        )
    )


def evaluate_leave_one_out(
    data_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Evaluate the fixed-strength adjustment using leave-one-out CV."""
    df = _load_x_pairs(data_path)

    if len(df) < MIN_TRAINING_ROWS:
        raise ValueError(
            f"Need at least {MIN_TRAINING_ROWS} paired X posts; "
            f"found {len(df)}"
        )

    rates = _daily_rates(df)
    signals = _training_signals(df)

    actual = df["views_latest"].to_numpy(dtype=float)
    starts = df["views_earlier"].to_numpy(dtype=float)
    days = df["elapsed_days"].to_numpy(dtype=float)

    baseline_predictions = []
    adjusted_predictions = []
    adjustments = []

    for held in range(len(df)):
        train_indices = np.flatnonzero(
            np.arange(len(df)) != held
        )

        # Neither the held-out target rate nor its future views
        # are used to calculate this fold's baseline.
        baseline = _baseline_rate(rates[train_indices])

        adjustment = _adjustment_from_signal(
            signals[held],
            signals[train_indices],
            ENGAGEMENT_ADJUSTMENT_STRENGTH,
        )

        adjusted_rate = float(
            np.clip(baseline + adjustment, RATE_MIN, RATE_MAX)
        )

        baseline_predictions.append(
            _views_from_rate(starts[held], baseline, days[held])
        )
        adjusted_predictions.append(
            _views_from_rate(starts[held], adjusted_rate, days[held])
        )
        adjustments.append(adjustment)

    baseline_predictions = np.asarray(baseline_predictions)
    adjusted_predictions = np.asarray(adjusted_predictions)

    baseline_errors = np.abs(actual - baseline_predictions)
    adjusted_errors = np.abs(actual - adjusted_predictions)

    def metrics(predictions):
        return {
            "mae_views": round(
                float(mean_absolute_error(actual, predictions)), 2
            ),
            "rmse_views": round(
                math.sqrt(
                    mean_squared_error(actual, predictions)
                ),
                2,
            ),
        }

    details = pd.DataFrame({
        "post_id": (
            df["post_id"].astype(str).to_numpy()
            if "post_id" in df.columns
            else np.arange(len(df)).astype(str)
        ),
        "actual_views": np.round(actual).astype(int),
        "baseline_prediction": np.round(
            baseline_predictions
        ).astype(int),
        "adjusted_prediction": np.round(
            adjusted_predictions
        ).astype(int),
        "baseline_abs_error": np.round(
            baseline_errors
        ).astype(int),
        "adjusted_abs_error": np.round(
            adjusted_errors
        ).astype(int),
        "error_difference": np.round(
            adjusted_errors - baseline_errors
        ).astype(int),
        "adjustment_strength": ENGAGEMENT_ADJUSTMENT_STRENGTH,
        "daily_rate_adjustment": adjustments,
    })

    details.to_csv(
        "engagement_adjusted_baseline_results.csv",
        index=False,
    )

    baseline_metrics = metrics(baseline_predictions)
    adjusted_metrics = metrics(adjusted_predictions)

    return {
        "status": "offline_experiment",
        "rows": len(df),
        "method": "fixed-strength engagement-adjusted baseline",
        "adjustment_strength": ENGAGEMENT_ADJUSTMENT_STRENGTH,
        "baseline": baseline_metrics,
        "engagement_adjusted": adjusted_metrics,
        "improves_mae": (
            adjusted_metrics["mae_views"]
            < baseline_metrics["mae_views"]
        ),
        "improves_rmse": (
            adjusted_metrics["rmse_views"]
            < baseline_metrics["rmse_views"]
        ),
        "posts_improved": int(
            np.sum(adjusted_errors < baseline_errors)
        ),
        "posts_worsened": int(
            np.sum(adjusted_errors > baseline_errors)
        ),
        "posts_tied": int(
            np.sum(adjusted_errors == baseline_errors)
        ),
        "note": (
            "Experimental result on a small dataset. "
            "Views are an audience-exposure proxy, not unique reach."
        ),
    }


def predict_x_future_views(
    current_views: float,
    horizon_days: int,
    current_engagement: Mapping[str, Optional[float]],
    post_age_days: float = 0,
    data_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Predict future X views using a baseline plus fixed adjustment."""
    try:
        views = float(current_views)
        horizon = int(horizon_days)
        age = float(post_age_days)
    except (TypeError, ValueError):
        raise ValueError(
            "current_views, horizon_days and post_age_days "
            "must be numeric"
        )

    if not math.isfinite(views) or views < 0:
        raise ValueError(
            "current_views must be finite and non-negative"
        )

    if horizon < 0 or horizon > MAX_HORIZON_DAYS:
        raise ValueError(
            f"horizon_days must be between 0 and {MAX_HORIZON_DAYS}"
        )

    if not math.isfinite(age) or age < 0:
        raise ValueError(
            "post_age_days must be finite and non-negative"
        )

    df = _load_x_pairs(data_path)

    if len(df) < MIN_TRAINING_ROWS:
        raise ValueError(
            f"Need at least {MIN_TRAINING_ROWS} paired X posts; "
            f"found {len(df)}"
        )

    rates = _daily_rates(df)
    training_signals = _training_signals(df)

    baseline_rate = _baseline_rate(rates)
    baseline_prediction = _views_from_rate(
        views, baseline_rate, horizon
    )

    signal = _engagement_signal(views, current_engagement)

    adjustment = _adjustment_from_signal(
        signal,
        training_signals,
        ENGAGEMENT_ADJUSTMENT_STRENGTH,
    )

    adjusted_rate = float(
        np.clip(
            baseline_rate + adjustment,
            RATE_MIN,
            RATE_MAX,
        )
    )

    prediction = _views_from_rate(
        views,
        adjusted_rate,
        horizon,
    )

    used = []
    missing = []

    for metric in ENGAGEMENT_FIELDS:
        raw = current_engagement.get(metric)

        try:
            value = float(raw) if raw is not None else float("nan")
        except (TypeError, ValueError):
            value = float("nan")

        if math.isfinite(value) and value >= 0:
            used.append(metric)
        else:
            missing.append(metric)

    return {
        "status": "experimental_engagement_adjusted_forecast",
        "platform": "X",
        "horizon_days": horizon,
        "current_views": round(views),
        "baseline_predicted_views": round(baseline_prediction),
        "predicted_views": round(prediction),
        "engagement_signals_used": used,
        "engagement_signals_missing": missing,

        # Compatibility fields retained for existing frontend consumers.
        # This value is now a fixed adjustment strength, not a model blend.
        "selected_engagement_blend_weight": (
            ENGAGEMENT_ADJUSTMENT_STRENGTH
        ),
        "engagement_model_daily_log_growth_rate": round(
            adjusted_rate, 6
        ),
        "blended_daily_log_growth_rate": round(
            adjusted_rate, 6
        ),

        "engagement_adjustment_strength": (
            ENGAGEMENT_ADJUSTMENT_STRENGTH
        ),
        "daily_rate_adjustment": round(adjustment, 6),
        "median_daily_log_growth_rate": round(
            baseline_rate, 6
        ),
        "post_age_days": age,
        "training_complete_view_pairs": len(df),
        "uncertainty": (
            "Experimental estimate using a fixed engagement adjustment "
            "validated on only 18 paired X posts. Post age is accepted "
            "but is not used in the adjustment formula. "
            "Views are an audience-exposure proxy, not unique reach."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(evaluate_leave_one_out(), indent=2))
