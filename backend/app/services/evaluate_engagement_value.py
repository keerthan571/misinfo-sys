from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


BASE_DIR = Path(__file__).resolve().parents[2]
DATA = BASE_DIR / "data" / "future_audience_feature_table.csv"
OUTPUT = BASE_DIR / "engagement_adjusted_baseline_results.csv"

METRICS = [
    "likes",
    "comments",
    "shares",
    "reposts",
    "bookmarks",
    "replies",
    "quotes",
]

MIN_RATE = -0.03
MAX_RATE = 0.08

# Multiple predefined candidates, instead of a single fixed strength.
ADJUSTMENT_STRENGTHS = (0.0, 0.1, 0.25, 0.5, 0.75, 1.0)


def load_data():
    df = pd.read_csv(DATA)

    df["platform"] = (
        df["platform"].astype(str).str.lower().str.strip()
    )
    df = df[df["platform"].isin(["x", "twitter"])].copy()

    required = [
        "views_earlier",
        "views_latest",
        "elapsed_days",
        "post_age_earlier_days",
    ]
    df = df.dropna(subset=required)

    df = df[
        (df["views_earlier"] >= 0)
        & (df["views_latest"] >= 0)
        & (df["elapsed_days"] > 0)
        & (df["post_age_earlier_days"] >= 0)
    ].reset_index(drop=True)

    return df


def growth_rates(df):
    earlier = df["views_earlier"].to_numpy(dtype=float)
    latest = df["views_latest"].to_numpy(dtype=float)
    elapsed = df["elapsed_days"].to_numpy(dtype=float)

    return (np.log1p(latest) - np.log1p(earlier)) / elapsed


def predict_views(start_views, days, rate):
    log_prediction = np.log1p(start_views) + rate * days

    return np.maximum(
        0.0,
        np.expm1(np.clip(log_prediction, -20, 30)),
    )


def engagement_strengths(row):
    views = float(row["views_earlier"])
    denominator = max(views, 1.0)
    values = []

    for metric in METRICS:
        col = f"{metric}_earlier"

        if col not in row.index:
            continue

        value = pd.to_numeric(row[col], errors="coerce")

        if pd.isna(value) or value < 0:
            continue

        ratio = float(value) / denominator
        signal = np.tanh(np.log1p(ratio * 1000.0))
        values.append(float(signal))

    return float(np.mean(values)) if values else np.nan


def build_engagement_signal(df):
    return np.array(
        [engagement_strengths(row) for _, row in df.iterrows()],
        dtype=float,
    )


def adjustment_from_signal(signal, train_signals, strength):
    available = train_signals[np.isfinite(train_signals)]

    if not np.isfinite(signal) or len(available) < 3:
        return 0.0

    center = float(np.median(available))
    mad = float(np.median(np.abs(available - center)))

    if mad < 1e-9:
        return 0.0

    standardized = (signal - center) / (1.4826 * mad)
    standardized = float(np.clip(standardized, -2.0, 2.0))

    return float(
        np.clip(strength * standardized * 0.005, -0.01, 0.01)
    )


def score(actual, predictions):
    return {
        "MAE": round(
            float(mean_absolute_error(actual, predictions)), 2
        ),
        "RMSE": round(
            float(np.sqrt(mean_squared_error(actual, predictions))), 2
        ),
    }


def choose_strength_inner_cv(
    outer_train_indices,
    rates,
    starts,
    actual,
    days,
    signals,
):
    """
    Select adjustment strength using inner leave-one-out validation.
    Inner-held-out outcomes are excluded from rate estimation.
    Their engagement signals are also excluded from normalization.
    """

    best_strength = 0.0
    best_mae = float("inf")

    for strength in ADJUSTMENT_STRENGTHS:
        inner_actual = []
        inner_predictions = []

        for inner_held in outer_train_indices:
            inner_train = outer_train_indices[
                outer_train_indices != inner_held
            ]

            if len(inner_train) < 3:
                continue

            baseline_rate = float(
                np.median(
                    np.clip(
                        rates[inner_train],
                        MIN_RATE,
                        MAX_RATE,
                    )
                )
            )

            adjustment = adjustment_from_signal(
                signals[inner_held],
                signals[inner_train],
                strength,
            )

            adjusted_rate = float(
                np.clip(
                    baseline_rate + adjustment,
                    MIN_RATE,
                    MAX_RATE,
                )
            )

            prediction = predict_views(
                starts[inner_held],
                days[inner_held],
                adjusted_rate,
            )

            inner_actual.append(actual[inner_held])
            inner_predictions.append(prediction)

        if not inner_actual:
            continue

        mae = float(
            mean_absolute_error(inner_actual, inner_predictions)
        )

        # Strict comparison preserves the smaller strength on ties.
        if mae < best_mae - 1e-9:
            best_mae = mae
            best_strength = strength

    return best_strength


def evaluate(df):
    n = len(df)

    if n < 6:
        raise ValueError(
            f"Need at least 6 paired posts; found {n}."
        )

    rates = growth_rates(df)
    starts = df["views_earlier"].to_numpy(dtype=float)
    actual = df["views_latest"].to_numpy(dtype=float)
    days = df["elapsed_days"].to_numpy(dtype=float)
    signals = build_engagement_signal(df)

    baseline_predictions = np.zeros(n)
    adjusted_predictions = np.zeros(n)
    selected_strengths = []
    applied_adjustments = np.zeros(n)

    for held in range(n):
        outer_train = np.flatnonzero(np.arange(n) != held)

        # Baseline uses only outer-training outcomes.
        baseline_rate = float(
            np.median(
                np.clip(
                    rates[outer_train],
                    MIN_RATE,
                    MAX_RATE,
                )
            )
        )

        baseline_predictions[held] = predict_views(
            starts[held],
            days[held],
            baseline_rate,
        )

        # Select strength exclusively within the outer training fold.
        best_strength = choose_strength_inner_cv(
            outer_train,
            rates,
            starts,
            actual,
            days,
            signals,
        )
        selected_strengths.append(best_strength)

        adjustment = adjustment_from_signal(
            signals[held],
            signals[outer_train],
            best_strength,
        )
        applied_adjustments[held] = adjustment

        adjusted_rate = float(
            np.clip(
                baseline_rate + adjustment,
                MIN_RATE,
                MAX_RATE,
            )
        )

        adjusted_predictions[held] = predict_views(
            starts[held],
            days[held],
            adjusted_rate,
        )

    baseline_errors = np.abs(actual - baseline_predictions)
    adjusted_errors = np.abs(actual - adjusted_predictions)

    details = pd.DataFrame(
        {
            "post_id": (
                df["post_id"].astype(str).to_numpy()
                if "post_id" in df.columns
                else np.arange(n).astype(str)
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
            "selected_strength": selected_strengths,
            "daily_rate_adjustment": applied_adjustments,
        }
    )

    # Explicit output path: backend/engagement_adjusted_baseline_results.csv
    details.to_csv(OUTPUT, index=False)

    print("\n=== NESTED LOOCV RESULTS ===")
    print("Posts evaluated:", n)
    print("Baseline:", score(actual, baseline_predictions))
    print("Engagement-adjusted:", score(actual, adjusted_predictions))
    print(
        "Improved posts:",
        int(np.sum(adjusted_errors < baseline_errors)),
    )
    print(
        "Worsened posts:",
        int(np.sum(adjusted_errors > baseline_errors)),
    )
    print(
        "Tied posts:",
        int(np.sum(adjusted_errors == baseline_errors)),
    )

    baseline_mae = mean_absolute_error(actual, baseline_predictions)
    adjusted_mae = mean_absolute_error(actual, adjusted_predictions)

    if baseline_mae > 0:
        improvement = (
            (baseline_mae - adjusted_mae) / baseline_mae
        ) * 100
        print(f"MAE change vs baseline: {improvement:.2f}%")

    print("\nSelected strength counts:")
    print(
        pd.Series(selected_strengths)
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\nPost-level results:")
    print(details.to_string(index=False))

    print(f"\nSaved results to: {OUTPUT}")


if __name__ == "__main__":
    data = load_data()
    print("X paired posts:", len(data))
    evaluate(data)
