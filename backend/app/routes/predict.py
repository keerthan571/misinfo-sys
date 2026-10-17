
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
import math
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, model_validator

from app.auth.dependencies import get_current_user
from app.services.graph.graph_generator import graph_generator
from app.database.mongodb import (
    spread_predictions_collection,
    analysis_collection,
)

router = APIRouter()

# Initial heuristic thresholds. Validate against a larger dataset
# before treating spreading-level classifications as reliable.
LOW_GROWTH_MAX = 0.01
MEDIUM_GROWTH_MAX = 0.05

GROWTH_METRICS = (
    "views",
    "likes",
    "comments",
    "shares",
    "reposts",
    "bookmarks",
    "replies",
    "quotes",
    "reactions",
)


class PredictRequest(BaseModel):
    analysis_id: str
    engagement: dict
    detection: dict = Field(default_factory=dict)
    platform: str = "Unknown"

    follower_count: Optional[int] = Field(default=None, ge=0)

    # Both dates are mandatory.
    posted_at: datetime
    screenshot_captured_at: datetime

    @model_validator(mode="after")
    def validate_timestamps(self):
        posted = self.posted_at
        captured = self.screenshot_captured_at

        # Treat timezone-naive values consistently as UTC.
        if posted.tzinfo is None:
            posted = posted.replace(tzinfo=timezone.utc)

        if captured.tzinfo is None:
            captured = captured.replace(tzinfo=timezone.utc)

        if posted > captured:
            raise ValueError(
                "Post publication time cannot be after screenshot capture time."
            )

        return self


def normalize_datetime(value: Optional[datetime]):
    """Return a timezone-aware UTC datetime or None."""
    if value is None:
        return None

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def numeric_metrics(metrics: dict) -> dict:
    """Keep valid, non-negative numeric observations without inventing zeros."""
    cleaned = {}

    for key in GROWTH_METRICS:
        value = metrics.get(key)

        if value is None or isinstance(value, bool):
            continue

        try:
            number = float(value)
        except (TypeError, ValueError):
            continue

        if math.isfinite(number) and number >= 0:
            cleaned[key] = number

    return cleaned


def calculate_spreading_level(observations: list) -> dict:
    """
    Classify observed engagement growth between the two latest distinct
    screenshot dates. This is a heuristic, not verified real-world reach.
    """
    valid = [
        item
        for item in observations
        if item.get("screenshot_captured_at")
    ]

    valid.sort(key=lambda item: item["screenshot_captured_at"])

    if len(valid) < 2:
        return {
            "level": "Insufficient historical data",
            "daily_log_growth": None,
            "elapsed_days": None,
            "metrics_compared": [],
            "method": "dated_observation_growth",
            "message": (
                "At least two observations captured on different dates "
                "are required to estimate spreading speed."
            ),
        }

    earlier = valid[-2]
    latest = valid[-1]

    try:
        earlier_date = datetime.fromisoformat(
            earlier["screenshot_captured_at"].replace("Z", "+00:00")
        )
        latest_date = datetime.fromisoformat(
            latest["screenshot_captured_at"].replace("Z", "+00:00")
        )
    except (TypeError, ValueError):
        return {
            "level": "Insufficient historical data",
            "daily_log_growth": None,
            "elapsed_days": None,
            "metrics_compared": [],
            "method": "dated_observation_growth",
            "message": "The observation dates are invalid.",
        }

    if earlier_date.tzinfo is None:
        earlier_date = earlier_date.replace(tzinfo=timezone.utc)

    if latest_date.tzinfo is None:
        latest_date = latest_date.replace(tzinfo=timezone.utc)

    elapsed_days = (
        latest_date - earlier_date
    ).total_seconds() / 86400

    if elapsed_days <= 0:
        return {
            "level": "Insufficient historical data",
            "daily_log_growth": None,
            "elapsed_days": elapsed_days,
            "metrics_compared": [],
            "method": "dated_observation_growth",
            "message": (
                "Observations must have different, correctly ordered "
                "screenshot dates."
            ),
        }

    old_metrics = earlier.get("engagement", {})
    new_metrics = latest.get("engagement", {})

    rates = []
    compared = []

    for key in GROWTH_METRICS:
        old_value = old_metrics.get(key)
        new_value = new_metrics.get(key)

        if old_value is None or new_value is None:
            continue

        try:
            old_value = float(old_value)
            new_value = float(new_value)
        except (TypeError, ValueError):
            continue

        if (
            not math.isfinite(old_value)
            or not math.isfinite(new_value)
            or old_value < 0
            or new_value < 0
        ):
            continue

        # Preserve increases and decreases.
        # Never force negative growth to zero.
        daily_log_growth = (
            math.log1p(new_value) - math.log1p(old_value)
        ) / elapsed_days

        rates.append(daily_log_growth)
        compared.append(key)

    if not rates:
        return {
            "level": "Insufficient historical data",
            "daily_log_growth": None,
            "elapsed_days": round(elapsed_days, 4),
            "metrics_compared": [],
            "method": "median_daily_log_growth",
            "message": (
                "No comparable numeric engagement metrics were found "
                "in the two latest observations."
            ),
        }

    rates.sort()
    middle = len(rates) // 2

    if len(rates) % 2:
        median_rate = rates[middle]
    else:
        median_rate = (
            rates[middle - 1] + rates[middle]
        ) / 2

    if median_rate < LOW_GROWTH_MAX:
        level = "Low"
    elif median_rate < MEDIUM_GROWTH_MAX:
        level = "Medium"
    else:
        level = "High"

    return {
        "level": level,
        "daily_log_growth": round(median_rate, 6),
        "elapsed_days": round(elapsed_days, 4),
        "metrics_compared": compared,
        "method": "median_daily_log_growth",
        "thresholds": {
            "low_below": LOW_GROWTH_MAX,
            "medium_below": MEDIUM_GROWTH_MAX,
        },
        "message": (
            "This level summarizes observed engagement growth between "
            "the two latest dated observations. It does not verify "
            "actual reach or establish that the content is misinformation."
        ),
    }


def update_observation_history(
    existing_analysis: dict,
    engagement: dict,
    posted_at: Optional[datetime],
    screenshot_captured_at: Optional[datetime],
    now: str,
) -> list:
    """
    Preserve dated observations on the analysis document.

    A repeated submission for the same capture date updates that entry
    rather than creating a duplicate daily observation.
    """
    observations = list(
        existing_analysis.get("engagement_observations", [])
    )

    if screenshot_captured_at is None:
        return observations

    capture_date = screenshot_captured_at.date().isoformat()

    observation = {
        "observation_id": str(uuid.uuid4()),
        "screenshot_captured_at": screenshot_captured_at.isoformat(),
        "capture_date": capture_date,
        "posted_at": posted_at.isoformat() if posted_at else None,
        "engagement": numeric_metrics(engagement),
        "recorded_at": now,
    }

    existing_index = next(
        (
            index
            for index, item in enumerate(observations)
            if item.get("capture_date") == capture_date
        ),
        None,
    )

    if existing_index is not None:
        previous = observations[existing_index]
        observation["observation_id"] = previous.get(
            "observation_id",
            observation["observation_id"],
        )
        observations[existing_index] = observation
    else:
        observations.append(observation)

    observations.sort(
        key=lambda item: item.get("screenshot_captured_at", "")
    )

    return observations


@router.post("/")
def predict_spread(
    request: PredictRequest,
    current_user=Depends(get_current_user),
):
    """
    Save a verified engagement snapshot, update the observed spreading
    level, and regenerate the propagation graph.

    Future audience forecasting is handled separately by
    /api/future-audience/predict.
    """
    user_email = current_user.get("email")

    if not user_email:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user email is missing.",
        )

    existing_analysis = analysis_collection.find_one(
        {
            "analysis_id": request.analysis_id,
            "email": user_email,
        }
    )

    if not existing_analysis:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found.",
        )

    engagement = request.engagement
    platform = request.platform or "Unknown"

    posted_at = normalize_datetime(request.posted_at)
    screenshot_captured_at = normalize_datetime(
        request.screenshot_captured_at
    )

    # Extra guard: never save an observation without both dates.
    if posted_at is None or screenshot_captured_at is None:
        raise HTTPException(
            status_code=422,
            detail=(
                "Both publication date and screenshot capture date "
                "are required."
            ),
        )

    post_age_hours = round(
        (screenshot_captured_at - posted_at).total_seconds() / 3600,
        2,
    )

    now = datetime.now(timezone.utc).isoformat()

    observations = update_observation_history(
        existing_analysis=existing_analysis,
        engagement=engagement,
        posted_at=posted_at,
        screenshot_captured_at=screenshot_captured_at,
        now=now,
    )

    spreading_level = calculate_spreading_level(observations)

    graph = graph_generator.generate(
        {
            "analysis": {
                "analysis_id": request.analysis_id,
                "text": existing_analysis.get("text", ""),
                "platform": platform,
                "publisher": existing_analysis.get("publisher"),
                "publisher_confidence": existing_analysis.get(
                    "publisher_confidence", 0
                ),
                "spreading_level": spreading_level,
                "engagement_observations": observations,
            },
            "engagement": numeric_metrics(engagement),
        }
    )

    analysis_update = {
        "engagement": engagement,
        "verified_engagement": engagement,
        "engagement_observations": observations,
        "spreading_level": spreading_level,
        "graph": graph,
        "metadata.graph_generated_once": True,
        "metadata.graph_generated_from_verified_engagement": True,
        "metadata.updated_at": now,
        "posted_at": posted_at.isoformat(),
        "screenshot_captured_at": screenshot_captured_at.isoformat(),
        "post_age_hours": post_age_hours,
    }

    if request.follower_count is not None:
        analysis_update["follower_count"] = request.follower_count

    analysis_collection.update_one(
        {
            "analysis_id": request.analysis_id,
            "email": user_email,
        },
        {"$set": analysis_update},
    )

    # Store observation history without legacy spread predictions.
    prediction_document = {
        "analysis_id": request.analysis_id,
        "prediction_id": str(uuid.uuid4()),
        "user": user_email,
        "platform": platform,
        "engagement": engagement,
        "engagement_observations": observations,
        "spreading_level": spreading_level,
        "graph": graph,
        "posted_at": posted_at.isoformat(),
        "screenshot_captured_at": screenshot_captured_at.isoformat(),
        "post_age_hours": post_age_hours,
        "follower_count": request.follower_count,
        "timestamp": now,
    }

    spread_predictions_collection.insert_one(prediction_document)

    return {
        "analysis_id": request.analysis_id,
        "spreading_level": spreading_level,
        "engagement_observations": observations,
        "graph": graph,
        "post_age_hours": post_age_hours,
    }
