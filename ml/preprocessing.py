import pandas as pd
import numpy as np


def create_features(df):

    df = df.copy()

    # ---------------------------------------------------------
    # DATE FEATURES
    # ---------------------------------------------------------

    df["date_posted"] = pd.to_datetime(
        df["date_posted"],
        errors="coerce"
    )

    df["recorded_at"] = pd.to_datetime(
        df["recorded_at"],
        errors="coerce"
    )

    df["posting_hour"] = (
        df["date_posted"].dt.hour
    )

    df["posting_day"] = (
        df["date_posted"].dt.dayofweek
    )

    df["posting_month"] = (
        df["date_posted"].dt.month
    )

    # ---------------------------------------------------------
    # OBSERVATION WINDOW
    # ---------------------------------------------------------

    df["observation_hours"] = (
        (
            df["recorded_at"]
            - df["date_posted"]
        ).dt.total_seconds() / 3600
    )

    df["observation_hours"] = (
        df["observation_hours"]
        .clip(lower=0)
    )

    # Log transform observation time
    df["log_observation_hours"] = np.log1p(
        df["observation_hours"]
    )

    # ---------------------------------------------------------
    # CAPTION FEATURES
    # ---------------------------------------------------------

    df["caption"] = (
        df["caption"]
        .fillna("")
        .astype(str)
    )

    df["caption_length"] = (
        df["caption"].str.len()
    )

    df["word_count"] = (
        df["caption"]
        .str.split()
        .str.len()
    )

    df["hashtag_count"] = (
        df["caption"]
        .str.count("#")
    )

    df["mention_count"] = (
        df["caption"]
        .str.count("@")
    )

    df["question_count"] = (
        df["caption"]
        .str.count(r"\?")
    )

    df["exclamation_count"] = (
        df["caption"]
        .str.count("!")
    )

    df["newline_count"] = (
        df["caption"]
        .str.count("\n")
    )

    # ---------------------------------------------------------
    # SELECT FEATURES
    # ---------------------------------------------------------

    feature_columns = [
        "platform",
        "content_type",
        "posting_hour",
        "posting_day",
        "posting_month",
        "observation_hours",
        "log_observation_hours",
        "caption_length",
        "word_count",
        "hashtag_count",
        "mention_count",
        "question_count",
        "exclamation_count",
        "newline_count"
    ]

    return df[feature_columns]