
from pathlib import Path
from datetime import datetime, timezone
from typing import Literal, Optional

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from app.services.graph.graph_generator import graph_generator
from app.auth.dependencies import get_current_user
from app.database.mongodb import analysis_collection
from app.services.audience_forecast_hybrid import (
    predict_x_future_views,
)

router = APIRouter(tags=["Future Audience Exposure"])

DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "future_audience_feature_table.csv"
)

MAX_HORIZON_DAYS = 88

ENGAGEMENT_FIELDS = [
    "likes",
    "comments",
    "shares",
    "reposts",
    "bookmarks",
    "replies",
    "quotes",
]

# Engagements per 1,000 views.
BENCHMARKS = {
    "low": {
        "likes": (1, 8),
    },
    "medium": {
        "likes": (20, 50),
        "comments": (1, 5),
        "shares": (1, 10),
    },
    "high": {
        "likes": (70, 120),
        "comments": (5, 10),
        "shares": (8, 15),
    },
}


class PredictionRequest(BaseModel):
    analysis_id: str
    platform: Literal["Instagram", "Facebook", "X"]
    horizon_days: int = Field(ge=0, le=MAX_HORIZON_DAYS)
    post_age_days: int = Field(ge=0)

    views: Optional[float] = Field(default=None, ge=0)
    followers_count: Optional[float] = Field(default=None, gt=0)

    likes: Optional[float] = Field(default=None, ge=0)
    comments: Optional[float] = Field(default=None, ge=0)
    shares: Optional[float] = Field(default=None, ge=0)
    reposts: Optional[float] = Field(default=None, ge=0)
    bookmarks: Optional[float] = Field(default=None, ge=0)
    replies: Optional[float] = Field(default=None, ge=0)
    quotes: Optional[float] = Field(default=None, ge=0)

    # Engagement at the first screenshot.
    likes_earlier: Optional[float] = Field(default=None, ge=0)
    comments_earlier: Optional[float] = Field(default=None, ge=0)
    shares_earlier: Optional[float] = Field(default=None, ge=0)
    reposts_earlier: Optional[float] = Field(default=None, ge=0)
    bookmarks_earlier: Optional[float] = Field(default=None, ge=0)
    replies_earlier: Optional[float] = Field(default=None, ge=0)
    quotes_earlier: Optional[float] = Field(default=None, ge=0)

    # Post age at the first screenshot.
    earlier_post_age_days: Optional[int] = Field(
        default=None,
        ge=0,
    )


def save_future_audience_forecast(
    analysis_id: str,
    user_email: str,
    forecast: dict,
) -> dict:
    """
    Save the future-audience forecast and regenerate the propagation
    graph using that forecast.

    The graph uses the forecast as an audience-exposure proxy.
    It does not represent verified unique reach or actual people.
    """

    query = {
        "analysis_id": analysis_id,
        "email": user_email,
    }

    existing_analysis = analysis_collection.find_one(query)

    if not existing_analysis:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found for the authenticated user.",
        )

    saved_forecast = jsonable_encoder(forecast)
    now = datetime.now(timezone.utc).isoformat()

    # Resolve the platform stored in the analysis document.
    raw_platform = existing_analysis.get("platform", "Unknown")

    if isinstance(raw_platform, dict):
        platform = raw_platform.get("platform", "Unknown")
    else:
        platform = raw_platform or "Unknown"

    # Prepare the existing analysis metadata for graph generation.
    analysis_for_graph = {
        "analysis_id": analysis_id,
        "text": existing_analysis.get("text", ""),
        "display_text": existing_analysis.get("display_text", ""),
        "platform": platform,
        "publisher": existing_analysis.get("publisher"),
        "publisher_confidence": existing_analysis.get(
            "publisher_confidence", 0
        ),
        "spreading_level": existing_analysis.get(
            "spreading_level", {}
        ),
        "engagement_observations": existing_analysis.get(
            "engagement_observations", []
        ),
    }

    # Regenerate the graph with the newly calculated forecast.
    graph = graph_generator.generate(
        {
            "analysis": analysis_for_graph,
            "engagement": existing_analysis.get("engagement", {}),
            "spread_prediction": (
                existing_analysis.get("prediction") or {}
            ),
            "future_audience": saved_forecast,
        }
    )

    # Save both the forecast and the regenerated graph.
    result = analysis_collection.update_one(
        query,
        {
            "$set": {
                "future_audience": saved_forecast,
                "graph": graph,
                "metadata.graph_generated_once": True,
                "metadata.graph_generated_with_future_audience": True,
                "metadata.updated_at": now,
            }
        },
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found for the authenticated user.",
        )

    return forecast


def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    required = {
        "platform",
        "elapsed_days",
        "views_earlier",
        "views_latest",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Dataset missing columns: {sorted(missing)}"
        )

    return df


def eligible_x_view_pairs() -> pd.DataFrame:
    df = load_data()

    df["platform"] = (
        df["platform"].astype(str).str.strip().str.lower()
    )

    for column in (
        "views_earlier",
        "views_latest",
        "elapsed_days",
    ):
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    return df[
        df["platform"].eq("x")
        & df["views_earlier"].notna()
        & df["views_latest"].notna()
        & df["elapsed_days"].notna()
        & (df["elapsed_days"] > 0)
    ].copy()


def estimate_median_daily_log_growth():
    pairs = eligible_x_view_pairs()

    if len(pairs) < 5:
        raise ValueError(
            "Not enough complete X view pairs to estimate growth."
        )

    start = (
        pairs["views_earlier"]
        .astype(float)
        .clip(lower=0)
        .to_numpy()
    )

    end = (
        pairs["views_latest"]
        .astype(float)
        .clip(lower=0)
        .to_numpy()
    )

    days = pairs["elapsed_days"].astype(float).to_numpy()

    daily_rates = (
        np.log1p(end) - np.log1p(start)
    ) / days

    median_rate = float(
        np.clip(np.median(daily_rates), -0.03, 0.08)
    )

    return (
        median_rate,
        int(len(pairs)),
        int(pairs["elapsed_days"].min()),
        int(pairs["elapsed_days"].max()),
    )


def observed_metrics(request: PredictionRequest) -> dict:
    fields = ["views", "followers_count"] + ENGAGEMENT_FIELDS

    return {
        field: getattr(request, field)
        for field in fields
        if getattr(request, field) is not None
    }


def safe_number(value) -> Optional[float]:
    if value is None:
        return None

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    if not np.isfinite(number) or number < 0:
        return None

    return number


def calculate_request_growth(
    request: PredictionRequest,
) -> dict:
    """
    Calculate daily engagement growth.

    post_age_days is the age at the latest screenshot.
    earlier_post_age_days is the age at the first screenshot.
    """

    current_age = request.post_age_days
    earlier_age = request.earlier_post_age_days

    if earlier_age is not None and earlier_age >= current_age:
        raise ValueError(
            "earlier_post_age_days must be less than post_age_days."
        )

    elapsed_days = (
        current_age - earlier_age
        if earlier_age is not None
        else current_age
    )

    if elapsed_days <= 0:
        raise ValueError(
            "A positive observation interval is required."
        )

    metric_growth = {}
    available_rates = []

    for metric in ENGAGEMENT_FIELDS:
        current = safe_number(getattr(request, metric))
        earlier = safe_number(
            getattr(request, f"{metric}_earlier")
        )

        if current is None:
            continue

        if earlier is not None and earlier_age is not None:
            change = current - earlier
            basis = "between_screenshots"
        else:
            change = current
            basis = "since_publication_approximation"

        rate = change / elapsed_days

        metric_growth[metric] = {
            "current_count": current,
            "earlier_count": earlier,
            "change": change,
            "growth_per_day": rate,
            "calculation": basis,
        }

        available_rates.append(rate)

    if not available_rates:
        raise ValueError(
            "Provide at least one engagement metric."
        )

    combined_rate = float(sum(available_rates))

    response_metrics = {
        metric: {
            **details,
            "change": round(details["change"], 4),
            "growth_per_day": round(
                details["growth_per_day"], 4
            ),
        }
        for metric, details in metric_growth.items()
    }

    return {
        "metrics": metric_growth,
        "response_metrics": response_metrics,
        "elapsed_days": elapsed_days,
        "combined_engagement_growth_per_day": round(
            combined_rate, 4
        ),
        "growth_basis": (
            "between_screenshots"
            if earlier_age is not None
            else "since_publication_approximation"
        ),
    }


def calculate_historical_platform_growth(
    platform: str,
) -> pd.DataFrame:
    """Calculate daily engagement-growth scores for historical posts."""

    df = load_data()

    df["platform"] = (
        df["platform"].astype(str).str.strip().str.lower()
    )

    df = df[df["platform"].eq(platform.lower())].copy()

    if df.empty:
        raise ValueError(
            f"No historical rows found for {platform}."
        )

    if "elapsed_days" not in df.columns:
        raise ValueError(
            "Dataset is missing elapsed_days."
        )

    df["elapsed_days"] = pd.to_numeric(
        df["elapsed_days"],
        errors="coerce",
    )

    scores = []

    for _, row in df.iterrows():
        interval = safe_number(row.get("elapsed_days"))

        if interval is None or interval <= 0:
            continue

        rates = []

        for metric in ENGAGEMENT_FIELDS:
            earlier = safe_number(
                row.get(f"{metric}_earlier")
            )
            latest = safe_number(
                row.get(f"{metric}_latest")
            )

            if earlier is None or latest is None:
                continue

            # Preserve real engagement increases and decreases.
            rates.append((latest - earlier) / interval)

        if rates:
            scores.append({
                "combined_growth_per_day": float(sum(rates)),
            })

    return pd.DataFrame(scores)


def classify_performance(
    platform: str,
    combined_growth_per_day: float,
) -> dict:
    """Classify performance using platform-specific historical tertiles."""

    historical = calculate_historical_platform_growth(platform)

    if len(historical) < 3:
        raise ValueError(
            f"At least 3 historical paired engagement observations "
            f"are needed for {platform} tier classification."
        )

    lower_cutoff = float(
        historical["combined_growth_per_day"].quantile(1 / 3)
    )

    upper_cutoff = float(
        historical["combined_growth_per_day"].quantile(2 / 3)
    )

    if combined_growth_per_day <= lower_cutoff:
        tier = "low"
    elif combined_growth_per_day >= upper_cutoff:
        tier = "high"
    else:
        tier = "medium"

    return {
        "performance_tier": tier,
        "platform": platform,
        "classification_method": (
            "platform-specific historical growth-rate tertiles"
        ),
        "historical_posts_used": int(len(historical)),
        "low_medium_cutoff": round(lower_cutoff, 4),
        "medium_high_cutoff": round(upper_cutoff, 4),
        "post_growth_score": round(
            combined_growth_per_day, 4
        ),
    }


def project_engagement(
    request: PredictionRequest,
    growth: dict,
) -> dict:
    """
    Project engagement using full-precision observed daily rates.
    Projected counts are clipped at zero and rounded to integers.
    """

    projected_metrics = {}

    for metric in ENGAGEMENT_FIELDS:
        current_count = safe_number(
            getattr(request, metric)
        )

        if current_count is None:
            continue

        metric_info = growth["metrics"].get(metric)

        daily_rate = (
            float(metric_info["growth_per_day"])
            if metric_info is not None
            else 0.0
        )

        projected_count = max(
            0.0,
            current_count
            + daily_rate * request.horizon_days,
        )

        projected_metrics[metric] = int(
            round(projected_count)
        )

    return projected_metrics


def estimate_views_from_benchmarks(
    metrics: dict,
    tier: str,
) -> dict:
    """
    Estimate views from projected engagement using the selected tier.
    The median of metric-specific estimates is used.
    """

    tier_benchmarks = BENCHMARKS[tier]
    metric_estimates = {}

    for metric, (minimum_rate, maximum_rate) in (
        tier_benchmarks.items()
    ):
        count = safe_number(metrics.get(metric))

        if count is None or count <= 0:
            continue

        midpoint_rate = (
            minimum_rate + maximum_rate
        ) / 2.0

        if midpoint_rate <= 0:
            continue

        estimated_views = count * 1000.0 / midpoint_rate

        metric_estimates[metric] = {
            "engagement_count_used": count,
            "benchmark_engagements_per_1000_views": [
                minimum_rate,
                maximum_rate,
            ],
            "midpoint_rate_used": midpoint_rate,
            "estimated_views": int(
                round(estimated_views)
            ),
        }

    if not metric_estimates:
        raise ValueError(
            f"No usable engagement metrics are available for "
            f"the {tier} tier. Provide a positive likes count "
            "or another metric supported by that tier's benchmarks."
        )

    estimates = [
        item["estimated_views"]
        for item in metric_estimates.values()
    ]

    final_estimate = int(
        round(float(np.median(estimates)))
    )

    return {
        "performance_tier": tier,
        "metric_estimates": metric_estimates,
        "predicted_views": final_estimate,
        "combination_method": (
            "median_of_available_metric_estimates"
        ),
        "benchmark_source": (
            "user-provided engagement benchmark table"
        ),
    }


@router.get("/health")
def future_audience_health():
    try:
        pairs = eligible_x_view_pairs()
        df = load_data()

        return {
            "status": "ok",
            "dataset_rows": int(len(df)),
            "complete_view_pairs_for_X": int(len(pairs)),
            "model_status": "experimental",
            "method": (
                "median daily log-growth with fixed "
                "engagement adjustment"
            ),
            "supported_numerical_forecast_platforms": [
                "X",
                "Instagram",
                "Facebook",
            ],
            "instagram_facebook_method": (
                "platform-specific engagement-growth tertiles, "
                "future engagement projection, and "
                "benchmark-based view estimation"
            ),
            "note": (
                "Instagram/Facebook tiers use historical engagement "
                "growth distributions for their respective platforms. "
                "Future engagement is linearly projected. "
                "View counts are benchmark-based estimates."
            ),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.post("/predict")
def predict_future_audience(
    request: PredictionRequest,
    current_user=Depends(get_current_user),
):
    user_email = current_user.get("email")

    if not user_email:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user email is missing.",
        )

    # Confirm that this analysis belongs to the logged-in user.
    existing_analysis = analysis_collection.find_one(
        {
            "analysis_id": request.analysis_id,
            "email": user_email,
        }
    )

    if not existing_analysis:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found for the authenticated user.",
        )

    metrics = observed_metrics(request)

    # Day zero returns supplied observations without forecasting.
    if request.horizon_days == 0:
        forecast = {
            "platform": request.platform,
            "horizon_days": 0,
            "status": "observed_baseline",
            "observed_metrics": metrics,
            "predicted_views": request.views,
            "audience_exposure_proxy": request.views,
            "unique_reach": None,
            "message": (
                "Day 0 returns supplied observations. "
                "Views are not verified unique reach."
            ),
        }

        return save_future_audience_forecast(
            request.analysis_id,
            user_email,
            forecast,
        )

    # ---------------------------------------------------------
    # Instagram / Facebook
    # ---------------------------------------------------------
    if request.platform in ("Instagram", "Facebook"):
        try:
            growth = calculate_request_growth(request)

            classification = classify_performance(
                platform=request.platform,
                combined_growth_per_day=(
                    growth["combined_engagement_growth_per_day"]
                ),
            )

            tier = classification["performance_tier"]

            projected_metrics = project_engagement(
                request=request,
                growth=growth,
            )

            estimate = estimate_views_from_benchmarks(
                metrics=projected_metrics,
                tier=tier,
            )

        except (ValueError, FileNotFoundError) as exc:
            raise HTTPException(
                status_code=422,
                detail=str(exc),
            )

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=str(exc),
            )

        max_projected_engagement = max(
            projected_metrics.values(),
            default=0,
        )

        predicted = max(
            estimate["predicted_views"],
            max_projected_engagement,
        )

        estimate["predicted_views"] = predicted

        forecast = {
            "platform": request.platform,
            "horizon_days": request.horizon_days,
            "status": "future_view_prediction",
            "observed_metrics": metrics,
            "engagement_growth": {
                "metrics": growth["response_metrics"],
                "elapsed_days": growth["elapsed_days"],
                "combined_engagement_growth_per_day": (
                    growth["combined_engagement_growth_per_day"]
                ),
                "growth_basis": growth["growth_basis"],
            },
            "projected_engagement_metrics": projected_metrics,
            "projection_method": (
                "latest engagement count plus full-precision observed "
                "daily growth multiplied by the requested horizon; "
                "projected counts are clipped at zero and rounded "
                "to whole numbers"
            ),
            "performance_tier": tier,
            "tier_classification": classification,
            "predicted_views": predicted,
            "audience_exposure_proxy": predicted,
            "unique_reach": None,
            "method": (
                "platform-specific historical engagement tier, "
                "linear engagement projection, and benchmark-based "
                "view estimation"
            ),
            "benchmark_estimate": estimate,
            "message": (
                f"Estimated views for {request.platform} using "
                "projected engagement and the selected tier."
            ),
            "cautions": [
                "The view count is estimated from engagement benchmarks, not directly observed.",
                "The low/medium/high tier is relative to historical posts from the same platform.",
                "Future engagement is a linear extrapolation of observed daily changes and may not reflect actual platform behavior.",
                "If an earlier screenshot is not supplied for a metric, its daily rate is approximated from the current count and post age.",
                "Views are an audience-exposure proxy, not verified unique reach.",
            ],
        }

        return save_future_audience_forecast(
            request.analysis_id,
            user_email,
            forecast,
        )

    # ---------------------------------------------------------
    # X: existing forecasting path preserved.
    # ---------------------------------------------------------
    if request.views is None:
        raise HTTPException(
            status_code=422,
            detail="Provide current views for an X forecast.",
        )

    current_engagement = {
        metric: getattr(request, metric)
        for metric in ENGAGEMENT_FIELDS
    }

    try:
        hybrid = predict_x_future_views(
            current_views=request.views,
            horizon_days=request.horizon_days,
            current_engagement=current_engagement,
            post_age_days=request.post_age_days,
            data_path=DATA_PATH,
        )

        _, n_pairs, min_days, max_days = (
            estimate_median_daily_log_growth()
        )

    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    within_interval = (
        min_days <= request.horizon_days <= max_days
    )

    predicted = int(round(hybrid["predicted_views"]))

    cautions = [
        (
            "Experimental engagement-adjusted estimate; "
            "not a validated forecast."
        ),
        (
            "Aggregate errors improved in a small evaluation sample, "
            "but some individual predictions worsened."
        ),
        "Views are an audience-exposure proxy, not verified unique reach.",
        "Engagement growth does not establish actual reach.",
    ]

    if not within_interval:
        cautions.append(
            "The requested horizon is outside the recorded "
            "observation interval; treat this as extrapolation."
        )
    else:
        cautions.append(
            "The horizon is within the recorded interval, but "
            "accuracy at this exact horizon is not validated."
        )

    forecast = {
        "platform": "X",
        "horizon_days": request.horizon_days,
        "status": hybrid["status"],
        "observed_metrics": metrics,
        "predicted_views": predicted,
        "audience_exposure_proxy": predicted,
        "unique_reach": None,
        "method": (
            "median daily log-growth with fixed engagement adjustment"
        ),
        "baseline_predicted_views": int(
            round(hybrid["baseline_predicted_views"])
        ),
        "median_daily_log_growth_rate": (
            hybrid["median_daily_log_growth_rate"]
        ),
        "engagement_model_daily_log_growth_rate": (
            hybrid["engagement_model_daily_log_growth_rate"]
        ),
        "blended_daily_log_growth_rate": (
            hybrid["blended_daily_log_growth_rate"]
        ),
        "engagement_adjustment_strength": (
            hybrid["engagement_adjustment_strength"]
        ),
        "daily_rate_adjustment": (
            hybrid["daily_rate_adjustment"]
        ),
        "selected_engagement_blend_weight": (
            hybrid["selected_engagement_blend_weight"]
        ),
        "engagement_signals_used": (
            hybrid["engagement_signals_used"]
        ),
        "engagement_signals_missing": (
            hybrid["engagement_signals_missing"]
        ),
        "training_complete_view_pairs": int(
            hybrid["training_complete_view_pairs"]
        ),
        "training_platform": "X only",
        "training_observation_interval_days": {
            "min": min_days,
            "max": max_days,
        },
        "horizon_within_observed_interval": bool(
            within_interval
        ),
        "post_age_days": request.post_age_days,
        "uncertainty": (
            "High: only 18 paired X observations are available, "
            "and no calibrated prediction interval exists. "
            "Post age is accepted but is not currently used "
            "to adjust the forecast."
        ),
        "cautions": cautions,
    }

    return save_future_audience_forecast(
        request.analysis_id,
        user_email,
        forecast,
    )
