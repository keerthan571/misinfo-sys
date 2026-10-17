
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GroupKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)

DATA_PATH = (
    r"C:\Users\Keerthan\Downloads"
    r"\social-media-post-performance-forecasting"
    r"\archive\train.csv"
)

N_SPLITS = 5
RANDOM_STATE = 42
PREDICTION_THRESHOLD = 0.50

NUMERIC_FEATURES = [
    "posting_hour",
    "posting_day",
    "posting_month",
    "caption_length",
    "word_count",
    "hashtag_count",
    "mention_count",
    "question_count",
    "exclamation_count",
    "newline_count",
]

CATEGORICAL_FEATURES = [
    "platform",
    "content_type_simplified",
]


# --------------------------------------------------
# 1. LOAD AND PREPARE DATA
# --------------------------------------------------

df = pd.read_csv(DATA_PATH)

df["platform"] = df["platform"].str.lower()
df = df[df["platform"].isin(["facebook", "instagram"])].copy()

df["date_posted"] = pd.to_datetime(
    df["date_posted"], errors="coerce", utc=True
)

df["caption"] = df["caption"].fillna("").astype(str)
df["content_type"] = df["content_type"].fillna("Unknown")

df["content_type_simplified"] = df["content_type"].replace({
    "GraphImage": "Image",
    "GraphVideo": "Video",
    "GraphSidecar": "Carousel",
})

df["posting_hour"] = df["date_posted"].dt.hour
df["posting_day"] = df["date_posted"].dt.dayofweek
df["posting_month"] = df["date_posted"].dt.month

df["caption_length"] = df["caption"].str.len()
df["word_count"] = df["caption"].str.split().str.len()
df["hashtag_count"] = df["caption"].str.count("#")
df["mention_count"] = df["caption"].str.count("@")
df["question_count"] = df["caption"].str.count(r"\?")
df["exclamation_count"] = df["caption"].str.count("!")
df["newline_count"] = df["caption"].str.count("\n")

df["likes"] = pd.to_numeric(df["likes"], errors="coerce")
df["comments"] = pd.to_numeric(df["comments"], errors="coerce")

df = df.dropna(subset=[
    "page_id",
    "date_posted",
    "likes",
    "comments",
    "posting_hour",
    "posting_day",
    "posting_month",
]).copy()

df = df[(df["likes"] >= 0) & (df["comments"] >= 0)].copy()

df["total_engagement"] = df["likes"] + df["comments"]
df = df.reset_index(drop=True)


# --------------------------------------------------
# 2. CREATE FOLD-SPECIFIC LABELS
# --------------------------------------------------

def learn_thresholds(reference_df):
    thresholds = {}

    for platform in ["facebook", "instagram"]:
        rows = reference_df[
            reference_df["platform"] == platform
        ]

        if rows.empty:
            raise ValueError(f"No training rows for {platform}")

        thresholds[platform] = float(
            rows["total_engagement"].quantile(0.75)
        )

    return thresholds


def make_labels(data, thresholds):
    return np.array([
        int(
            row.total_engagement >= thresholds[row.platform]
        )
        for row in data.itertuples()
    ])


# --------------------------------------------------
# 3. BUILD THE THREE FEATURE SETS
# --------------------------------------------------

def make_model(feature_set):
    transformers = []

    if feature_set in ["metadata", "combined"]:
        transformers.extend([
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL_FEATURES,
            ),
            (
                "numeric",
                Pipeline([
                    (
                        "imputer",
                        SimpleImputer(strategy="median"),
                    ),
                    ("scaler", StandardScaler()),
                ]),
                NUMERIC_FEATURES,
            ),
        ])

    if feature_set in ["caption", "combined"]:
        transformers.append(
            (
                "caption_tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    strip_accents="unicode",
                    ngram_range=(1, 2),
                    min_df=3,
                    max_features=5000,
                    sublinear_tf=True,
                    token_pattern=r"(?u)\b\w+\b",
                ),
                "caption",
            )
        )

    preprocessor = ColumnTransformer(
        transformers=transformers,
        remainder="drop",
    )

    return Pipeline([
        ("preprocessor", preprocessor),
        (
            "model",
            LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=RANDOM_STATE,
            ),
        ),
    ])


# --------------------------------------------------
# 4. GROUPED OUT-OF-FOLD EVALUATION
# --------------------------------------------------

feature_sets = {
    "A - Metadata only": "metadata",
    "B - Caption TF-IDF only": "caption",
    "C - Metadata + TF-IDF": "combined",
}

cv = GroupKFold(n_splits=N_SPLITS)
results = []

print("Rows:", len(df))
print("Unique pages:", df["page_id"].nunique())
print("Facebook rows:", (df["platform"] == "facebook").sum())
print("Instagram rows:", (df["platform"] == "instagram").sum())
print("\nStarting grouped cross-validation...")

for experiment_name, feature_set in feature_sets.items():
    oof_true = np.full(len(df), -1, dtype=int)
    oof_prob = np.full(len(df), np.nan)

    print(f"\n{'=' * 65}")
    print(experiment_name)
    print("=" * 65)

    for fold, (train_idx, val_idx) in enumerate(
        cv.split(df, groups=df["page_id"]), start=1
    ):
        fold_train = df.iloc[train_idx]
        fold_val = df.iloc[val_idx]

        # Learn engagement thresholds from training pages only.
        thresholds = learn_thresholds(fold_train)

        y_train = make_labels(fold_train, thresholds)
        y_val = make_labels(fold_val, thresholds)

        model = make_model(feature_set)
        model.fit(fold_train, y_train)

        probabilities = model.predict_proba(fold_val)[:, 1]

        oof_true[val_idx] = y_val
        oof_prob[val_idx] = probabilities

        fold_predictions = (
            probabilities >= PREDICTION_THRESHOLD
        ).astype(int)

        print(
            f"Fold {fold}: F1 = "
            f"{f1_score(y_val, fold_predictions, zero_division=0):.4f}"
        )

    assert np.all(oof_true >= 0)
    assert np.isfinite(oof_prob).all()

    oof_predictions = (
        oof_prob >= PREDICTION_THRESHOLD
    ).astype(int)

    metrics = {
        "experiment": experiment_name,
        "threshold": PREDICTION_THRESHOLD,
        "accuracy": accuracy_score(
            oof_true, oof_predictions
        ),
        "precision": precision_score(
            oof_true, oof_predictions, zero_division=0
        ),
        "recall": recall_score(
            oof_true, oof_predictions, zero_division=0
        ),
        "f1": f1_score(
            oof_true, oof_predictions, zero_division=0
        ),
        "roc_auc": roc_auc_score(oof_true, oof_prob),
    }

    results.append(metrics)

    print("\nPooled OOF metrics:")
    for metric, value in metrics.items():
        if isinstance(value, (float, np.floating)):
            print(f"{metric}: {value:.4f}")
        else:
            print(f"{metric}: {value}")


# --------------------------------------------------
# 5. COMPARE AND SAVE RESULTS
# --------------------------------------------------

results_df = pd.DataFrame(results)

print("\n" + "=" * 85)
print("FINAL FEATURE-SET COMPARISON")
print("=" * 85)

print(
    results_df.to_string(
        index=False,
        float_format=lambda value: f"{value:.4f}",
    )
)

output_path = "ml/feature_set_comparison.csv"
results_df.to_csv(output_path, index=False)

print(f"\nSaved results to: {output_path}")
print("Feature-set experiment complete.")
print("No application files were changed.")
