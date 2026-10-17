
from pathlib import Path
from statistics import median
import math

import pandas as pd


DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "future_audience_feature_table.csv"
)

MAX_HORIZON_DAYS = 88

# Provisional assumptions, not validated conversion rates.
PLATFORM_BENCHMARKS = {
    "instagram": {"low": 10.0, "normal": 17.5, "high": 25.0},
    "facebook": {"low": 25.0, "normal": 62.5, "high": 100.0},
}

ENGAGEMENT_METRICS = (
    "likes",
    "comments",
    "shares",
    "reposts",
    "replies",
    "quotes",
    "bookmarks",
)


def _load_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    required = {
        "platform",
        "elapsed_days",
        "views_earlier",
        "views_latest",
    }
    missing = required.difference(df.columns)

    if missing:
        raise ValueError(
            "Dataset missing columns: " + ", ".join(sorted(missing))
        )

    df["platform"] = df["platform"].astype(str).str.strip().str.lower()

    for column in df.columns:
        if column.endswith(
            ("_earlier", "_latest", "_days")
        ):
            df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


def _x_view_pairs(df):
    pairs = df[df["platform"].isin(["x", "twitter"])].copy()
    pairs = pairs.dropna(
        subset=["elapsed_days", "views_earlier", "views_latest"]
    )

    return pairs[
        (pairs["elapsed_days"] > 0)
        & (pairs["views_earlier"] > 0)
        & (pairs["views_latest"] > 0)
    ]


def _median_daily_log_growth(df):
    pairs = _x_view_pairs(df)

    if pairs.empty:
        return None, 0

    rates = (
        pairs["views_latest"].apply(math.log1p)
        - pairs["views_earlier"].apply(math.log1p)
    ) / pairs["elapsed_days"]

    rates = rates.replace([float("inf"), float("-inf")], float("nan"))
    rates = rates.dropna().clip(lower=-0.03, upper=0.08)

    if rates.empty:
        return None, 0

    return float(median(rates.tolist())), len(rates)


def _normalise_metrics(metrics):
    if not isinstance(metrics, dict):
        return {}

    result = {}

    for key in ENGAGEMENT_METRICS:
        value = metrics.get(key)

        try:
            value = float(value)
        except (TypeError, ValueError):
            continue

        if math.isfinite(value) and value >= 0:
            result[key] = value

    return result


def _engagement_total(metrics):
    # Missing metrics are excluded, not treated as observed zeroes.
    return sum(_normalise_metrics(metrics).values())


def _engagement_growth_rate(earlier_metrics, latest_metrics, elapsed_days):
    if not isinstance(earlier_metrics, dict):
        return None

    if not isinstance(latest_metrics, dict):
        return None

    try:
        days = float(elapsed_days)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(days) or days <= 0:
        return None

    earlier = _normalise_metrics(earlier_metrics)
    latest = _normalise_metrics(latest_metrics)

    common = set(earlier) & set(latest)

    if not common:
        return None

    old_total = sum(earlier[key] for key in common)
    new_total = sum(latest[key] for key in common)

    return (
        math.log1p(new_total) - math.log1p(old_total)
    ) / days


def _growth_thresholds(df, platform):
    """
    Estimate low/normal/high cutoffs from historical engagement growth.
    Small platform samples make these cutoffs experimental.
    """
    subset = df[df["platform"] == platform].copy()
    rates = []

    for _, row in subset.iterrows():
        earlier = {
            metric: row.get(f"{metric}_earlier")
            for metric in ENGAGEMENT_METRICS
        }
        latest = {
            metric: row.get(f"{metric}_latest")
            for metric in ENGAGEMENT_METRICS
        }

        rate = _engagement_growth_rate(
            earlier,
            latest,
            row.get("elapsed_days"),
        )

        if rate is not None and math.isfinite(rate):
            rates.append(rate)

    if len(rates) < 3:
        return None

    series = pd.Series(rates)

    return (
        float(series.quantile(1 / 3)),
        float(series.quantile(2 / 3)),
        len(rates),
    )


def _classify_growth(rate, thresholds):
    if rate is None or thresholds is None:
        return "normal"

    low_cutoff, high_cutoff, _ = thresholds

    if rate <= low_cutoff:
        return "low"

    if rate >= high_cutoff:
        return "high"

    return "normal"


def predict_audience_exposure(
    platform,
    metrics,
    horizon_days,
    post_age_days=None,
    follower_count=None,
    earlier_metrics=None,
    elapsed_days=None,
):
    """
    Experimental audience-exposure estimate.

    X: projects a supplied views count using paired X view observations.

    Instagram/Facebook: estimates a rough exposure proxy using likes and
    provisional platform-specific views-per-like benchmarks. Engagement
    growth selects the low, normal, or high benchmark.

    Follower count is reported as context, not used as a multiplier:
    the current dataset cannot validate how it should affect predictions.
    """
    platform_name = str(platform or "").strip().lower()

    if platform_name == "twitter":
        platform_name = "x"

    if platform_name not in {"x", "instagram", "facebook"}:
        return {
            "status": "unsupported_platform",
            "platform": platform_name,
            "predicted_audience_exposure": None,
        }

    try:
        horizon = float(horizon_days)
    except (TypeError, ValueError):
        horizon = -1

    if (
        not math.isfinite(horizon)
        or not horizon.is_integer()
        or not 0 <= horizon <= MAX_HORIZON_DAYS
    ):
        return {
            "status": "unsupported_horizon",
            "platform": platform_name,
            "horizon_days": horizon_days,
            "predicted_audience_exposure": None,
            "uncertainty": f"Horizon must be a whole number from 0 to {MAX_HORIZON_DAYS}.",
        }

    horizon = int(horizon)
    metrics = dict(metrics) if isinstance(metrics, dict) else {}
    metrics.update(_normalise_metrics(metrics))

    try:
        followers = (
            float(follower_count)
            if follower_count is not None
            else None
        )
    except (TypeError, ValueError):
        followers = None

    if (
        followers is not None
        and (not math.isfinite(followers) or followers < 0)
    ):
        followers = None

    try:
        df = _load_data()
        daily_rate, growth_samples = _median_daily_log_growth(df)
    except Exception as exc:
        return {
            "status": "dataset_error",
            "platform": platform_name,
            "predicted_audience_exposure": None,
            "error": str(exc),
        }

    if daily_rate is None:
        return {
            "status": "insufficient_training_data",
            "platform": platform_name,
            "predicted_audience_exposure": None,
        }

    result = {
        "platform": platform_name,
        "horizon_days": horizon,
        "follower_count": followers,
        "post_age_days": post_age_days,
        "growth_training_samples": growth_samples,
        "uncertainty": (
            "Experimental estimate, not validated. Estimated exposure is "
            "not measured reach or a guarantee of future views."
        ),
    }

    if platform_name == "x":
        try:
            baseline = float(metrics.get("views"))
        except (TypeError, ValueError):
            baseline = None

        if (
            baseline is None
            or not math.isfinite(baseline)
            or baseline < 0
        ):
            return {
                **result,
                "status": "missing_baseline_views",
                "predicted_audience_exposure": None,
            }

        predicted = (
            baseline
            if horizon == 0
            else math.expm1(math.log1p(baseline) + daily_rate * horizon)
        )

        result.update({
            "status": "experimental_estimate",
            "baseline_audience_exposure_proxy": round(baseline, 2),
            "predicted_audience_exposure": round(max(0, predicted), 2),
            "daily_log_growth_rate": round(daily_rate, 6),
        })

        return result

    # Instagram/Facebook require a usable likes count for this benchmark.
    likes = metrics.get("likes")

    if likes is None or likes <= 0:
        return {
            **result,
            "status": "missing_likes",
            "predicted_audience_exposure": None,
            "uncertainty": (
                "A positive likes count is required for this provisional "
                "views-per-like benchmark."
            ),
        }

    observed_growth = _engagement_growth_rate(
        earlier_metrics,
        metrics,
        elapsed_days,
    )

    thresholds = _growth_thresholds(df, platform_name)
    growth_category = _classify_growth(observed_growth, thresholds)
    ratio = PLATFORM_BENCHMARKS[platform_name][growth_category]

    baseline = likes * ratio

    if platform_name == "x":
        predicted = (
            baseline
            if horizon == 0
            else math.expm1(math.log1p(baseline) + daily_rate * horizon)
        )
    else:
        # No validated Instagram/Facebook future-view growth rate is available.
        # Return the benchmark-based baseline without projecting X growth.
        predicted = baseline

    result.update({
        "status": "experimental_estimate",
        "growth_category": growth_category,
        "observed_engagement_log_growth_per_day": (
            round(observed_growth, 6)
            if observed_growth is not None
            else None
        ),
        "growth_threshold_samples": (
            thresholds[2] if thresholds is not None else 0
        ),
        "views_per_like_benchmark": ratio,
        "baseline_audience_exposure_proxy": round(baseline, 2),
        "predicted_audience_exposure": round(max(0, predicted), 2),
         
        "uncertainty": (
            "Instagram/Facebook views-per-like values are provisional "
            "assumptions, not learned or validated platform-specific rates. "
            "No future growth projection is applied to Instagram/Facebook. "
            "Follower count is recorded but not yet used in the calculation."
        ),
    })

    return result
