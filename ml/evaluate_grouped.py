import numpy as np
import pandas as pd

from sklearn.model_selection import GroupKFold
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GroupShuffleSplit, GroupKFold
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)

DATA_PATH = (
    r"C:\Users\Keerthan\Downloads"
    r"\social-media-post-performance-forecasting"
    r"\archive\train.csv"
)

RANDOM_STATE = 42
N_SPLITS = 5

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

df = df.dropna(
    subset=[
        "page_id", "date_posted", "likes", "comments",
        "posting_hour", "posting_day", "posting_month",
    ]
).copy()

df = df[(df["likes"] >= 0) & (df["comments"] >= 0)].copy()
df["total_engagement"] = df["likes"] + df["comments"]

features = [
    "platform", "content_type",
    "posting_hour", "posting_day", "posting_month",
    "caption_length", "word_count", "hashtag_count",
    "mention_count", "question_count",
    "exclamation_count", "newline_count",
]

categorical = ["platform", "content_type"]
numeric = [c for c in features if c not in categorical]

# --------------------------------------------------
# 2. GROUPED HOLDOUT SPLIT
# --------------------------------------------------

splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.20,
    random_state=RANDOM_STATE,
)

train_idx, test_idx = next(
    splitter.split(df[features], groups=df["page_id"])
)

train_df = df.iloc[train_idx].copy().reset_index(drop=True)
test_df = df.iloc[test_idx].copy().reset_index(drop=True)

assert set(train_df["page_id"]).isdisjoint(set(test_df["page_id"]))

print("Training rows:", len(train_df))
print("Testing rows:", len(test_df))
print("Training pages:", train_df["page_id"].nunique())
print("Testing pages:", test_df["page_id"].nunique())
print("Page overlap: 0")

# --------------------------------------------------
# 3. THRESHOLDS AND LABELS
# --------------------------------------------------

def learn_thresholds(reference_df):
    result = {}

    for platform in ["facebook", "instagram"]:
        rows = reference_df[
            reference_df["platform"] == platform
        ]

        if rows.empty:
            raise ValueError(
                f"No training rows for platform: {platform}"
            )

        result[platform] = float(
            rows["total_engagement"].quantile(0.75)
        )

    return result


def make_labels(data, thresholds):
    return np.array([
        int(row.total_engagement >= thresholds[row.platform])
        for row in data.itertuples()
    ])


# --------------------------------------------------
# 4. MODELS AND PREPROCESSING
# --------------------------------------------------

def make_preprocessor():
    return ColumnTransformer([
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical,
        ),
        (
            "numeric",
            Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]),
            numeric,
        ),
    ])


models = {
    "logistic_regression": LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    ),
    "random_forest": RandomForestClassifier(
        n_estimators=400,
        max_depth=18,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    ),
    "extra_trees": ExtraTreesClassifier(
        n_estimators=400,
        max_depth=18,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    ),
}

# --------------------------------------------------
# 5. OOF PROBABILITIES FOR THRESHOLD TUNING
# --------------------------------------------------

X_train = train_df[features]
groups_train = train_df["page_id"]

cv = GroupKFold(n_splits=5)

oof_prob = np.full(len(train_df), np.nan)
oof_true = np.full(len(train_df), -1, dtype=int)

logistic_model = LogisticRegression(
    max_iter=2000,
    class_weight="balanced",
    random_state=RANDOM_STATE,
)

for fold, (fit_idx, val_idx) in enumerate(
    cv.split(X_train, groups=groups_train), start=1
):
    fold_train = train_df.iloc[fit_idx]
    fold_val = train_df.iloc[val_idx]

    # Learn the engagement thresholds from fold-training pages only.
    fold_thresholds = learn_thresholds(fold_train)

    y_fit = make_labels(fold_train, fold_thresholds)
    y_val = make_labels(fold_val, fold_thresholds)

    pipeline = Pipeline([
        ("preprocessor", make_preprocessor()),
        ("model", clone(logistic_model)),
    ])

    pipeline.fit(fold_train[features], y_fit)

    probabilities = pipeline.predict_proba(
        fold_val[features]
    )[:, 1]

    oof_prob[val_idx] = probabilities
    oof_true[val_idx] = y_val

    print(
        f"Fold {fold}: "
        f"F1 at 0.50 = "
        f"{f1_score(y_val, (probabilities >= 0.50).astype(int), zero_division=0):.4f}"
    )

assert not np.isnan(oof_prob).any()
assert (oof_true >= 0).all()


# --------------------------------------------------
# 6. SELECT SEPARATE THRESHOLDS USING TRAINING OOF
# --------------------------------------------------

threshold_results = []
platform_thresholds = {}

train_platforms = train_df["platform"].to_numpy()

for platform in ["facebook", "instagram"]:
    mask = train_platforms == platform

    platform_true = oof_true[mask]
    platform_prob = oof_prob[mask]

    print("\n" + "=" * 60)
    print(f"THRESHOLD TUNING: {platform.upper()}")
    print("=" * 60)

    candidates = []

    for threshold in np.arange(0.20, 0.81, 0.02):
        predictions = (platform_prob >= threshold).astype(int)

        candidates.append({
            "threshold": round(float(threshold), 2),
            "precision": precision_score(
                platform_true, predictions, zero_division=0
            ),
            "recall": recall_score(
                platform_true, predictions, zero_division=0
            ),
            "f1": f1_score(
                platform_true, predictions, zero_division=0
            ),
        })

    results_df = pd.DataFrame(candidates)

    print(
        results_df.sort_values("f1", ascending=False)
        .head(5)
        .to_string(index=False, float_format=lambda x: f"{x:.4f}")
    )

    best_row = results_df.loc[results_df["f1"].idxmax()]
    platform_thresholds[platform] = float(best_row["threshold"])

    print(
        f"Selected {platform} threshold: "
        f"{platform_thresholds[platform]:.2f}"
    )

print("\nTraining-only platform thresholds:")
print(platform_thresholds)

# --------------------------------------------------
# 7. FINAL EVALUATION BY PLATFORM
# --------------------------------------------------

final_thresholds = learn_thresholds(train_df)

y_train = make_labels(train_df, final_thresholds)
y_test = make_labels(test_df, final_thresholds)

final_model = Pipeline([
    ("preprocessor", make_preprocessor()),
    ("model", clone(logistic_model)),
])

final_model.fit(train_df[features], y_train)

test_prob = final_model.predict_proba(test_df[features])[:, 1]

print("\nTraining-only engagement thresholds:")
print(final_thresholds)

for platform in ["facebook", "instagram"]:
    mask = test_df["platform"].to_numpy() == platform

    actual = y_test[mask]
    probabilities = test_prob[mask]

    if len(actual) == 0:
        continue

    thresholds_to_test = [
        ("DEFAULT", 0.50),
        ("PLATFORM_TUNED", platform_thresholds[platform]),
    ]

    for label, threshold in thresholds_to_test:
        predictions = (probabilities >= threshold).astype(int)

        print(f"\n{platform.upper()} — {label}")
        print("Threshold:", round(threshold, 2))
        print("Precision:", round(
            precision_score(actual, predictions, zero_division=0), 4
        ))
        print("Recall:", round(
            recall_score(actual, predictions, zero_division=0), 4
        ))
        print("F1:", round(
            f1_score(actual, predictions, zero_division=0), 4
        ))
        print("Confusion matrix:")
        print(confusion_matrix(actual, predictions, labels=[0, 1]))
print("\nPlatform evaluation complete. No application files were changed.")
