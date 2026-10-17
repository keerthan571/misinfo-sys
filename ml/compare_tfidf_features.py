import numpy as np
import pandas as pd

from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline, FeatureUnion
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
    "page_id", "date_posted", "likes", "comments",
    "posting_hour", "posting_day", "posting_month",
]).copy()

df = df[(df["likes"] >= 0) & (df["comments"] >= 0)].copy()
df["total_engagement"] = df["likes"] + df["comments"]
df = df.reset_index(drop=True)

# --------------------------------------------------
# 2. FEATURES
# --------------------------------------------------

numeric_features = [
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

categorical_features = [
    "platform",
    "content_type_simplified",
]

# --------------------------------------------------
# 3. HELPERS
# --------------------------------------------------

def learn_thresholds(reference_df):
    thresholds = {}

    for platform in ["facebook", "instagram"]:
        rows = reference_df[reference_df["platform"] == platform]

        if rows.empty:
            raise ValueError(f"No rows for platform: {platform}")

        thresholds[platform] = float(
            rows["total_engagement"].quantile(0.75)
        )

    return thresholds


def make_labels(data, thresholds):
    return np.array([
        int(row.total_engagement >= thresholds[row.platform])
        for row in data.itertuples()
    ])


def make_model(use_tfidf):
    categorical_pipeline = OneHotEncoder(handle_unknown="ignore")

    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    transformers = [
        (
            "categorical",
            categorical_pipeline,
            categorical_features,
        ),
        (
            "numeric",
            numeric_pipeline,
            numeric_features,
        ),
    ]

    if use_tfidf:
        # Text vectorization is fitted inside each training fold.
        transformers.append((
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
        ))

    preprocessor = ColumnTransformer(
        transformers=transformers,
        remainder="drop",
    )

    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        )),
    ])


# --------------------------------------------------
# 4. GROUPED CROSS-VALIDATION
# --------------------------------------------------

feature_sets = {
    "baseline_simplified": False,
    "baseline_plus_tfidf": True,
}

cv = GroupKFold(n_splits=N_SPLITS)
results = []

print("Total rows:", len(df))
print("Unique pages:", df["page_id"].nunique())
print("Evaluation: five-fold page-grouped CV")
print("Decision threshold: 0.50")
print("TF-IDF vocabulary is learned within each training fold.")

for experiment_name, use_tfidf in feature_sets.items():
    print("\n" + "=" * 65)
    print("EXPERIMENT:", experiment_name.upper())
    print("=" * 65)

    oof_true = np.full(len(df), -1, dtype=int)
    oof_prob = np.full(len(df), np.nan)
    fold_f1_scores = []

    for fold, (train_idx, val_idx) in enumerate(
        cv.split(df, groups=df["page_id"]), start=1
    ):
        fold_train = df.iloc[train_idx]
        fold_val = df.iloc[val_idx]

        # Thresholds are learned only from the fold's training pages.
        thresholds = learn_thresholds(fold_train)

        y_train = make_labels(fold_train, thresholds)
        y_val = make_labels(fold_val, thresholds)

        model = make_model(use_tfidf)
        model.fit(fold_train, y_train)

        probabilities = model.predict_proba(fold_val)[:, 1]
        predictions = (probabilities >= 0.50).astype(int)

        oof_true[val_idx] = y_val
        oof_prob[val_idx] = probabilities

        fold_f1 = f1_score(
            y_val, predictions, zero_division=0
        )
        fold_f1_scores.append(fold_f1)

        print(
            f"Fold {fold}: F1={fold_f1:.4f}, "
            f"validation_pages={fold_val['page_id'].nunique()}"
        )

    valid = (oof_true >= 0) & np.isfinite(oof_prob)
    actual = oof_true[valid]
    probabilities = oof_prob[valid]
    predictions = (probabilities >= 0.50).astype(int)

    result = {
        "experiment": experiment_name,
        "accuracy": accuracy_score(actual, predictions),
        "precision": precision_score(
            actual, predictions, zero_division=0
        ),
        "recall": recall_score(
            actual, predictions, zero_division=0
        ),
        "f1": f1_score(actual, predictions, zero_division=0),
        "mean_fold_f1": float(np.mean(fold_f1_scores)),
        "fold_f1_std": float(np.std(fold_f1_scores)),
        "roc_auc": (
            roc_auc_score(actual, probabilities)
            if len(np.unique(actual)) == 2
            else float("nan")
        ),
    }

    results.append(result)

    for metric in [
        "accuracy", "precision", "recall",
        "f1", "mean_fold_f1", "fold_f1_std", "roc_auc",
    ]:
        print(f"{metric}: {result[metric]:.4f}")

# --------------------------------------------------
# 5. COMPARE AND SAVE
# --------------------------------------------------

results_df = pd.DataFrame(results)

print("\n" + "=" * 65)
print("FINAL COMPARISON")
print("=" * 65)

print(results_df.to_string(
    index=False,
    float_format=lambda x: f"{x:.4f}",
))

results_df.to_csv("ml/tfidf_comparison.csv", index=False)

print("\nSaved: ml/tfidf_comparison.csv")
print("Experiment complete. No application files were changed.")