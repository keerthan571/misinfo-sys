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

numeric_features = [
    "posting_hour", "posting_day", "posting_month",
    "caption_length", "word_count", "hashtag_count",
    "mention_count", "question_count",
    "exclamation_count", "newline_count",
]

categorical_features = [
    "platform", "content_type_simplified",
]

# --------------------------------------------------
# 2. HELPER FUNCTIONS
# --------------------------------------------------

def learn_thresholds(reference_df):
    thresholds = {}

    for platform in ["facebook", "instagram"]:
        rows = reference_df[reference_df["platform"] == platform]

        if rows.empty:
            raise ValueError(f"No rows found for {platform}")

        thresholds[platform] = float(
            rows["total_engagement"].quantile(0.75)
        )

    return thresholds


def make_labels(data, thresholds):
    return np.array([
        int(row.total_engagement >= thresholds[row.platform])
        for row in data.itertuples()
    ])


def make_model():
    preprocessor = ColumnTransformer([
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features,
        ),
        (
            "numeric",
            Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]),
            numeric_features,
        ),
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
        ),
    ])

    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        )),
    ])


# --------------------------------------------------
# 3. GENERATE OUT-OF-FOLD PROBABILITIES
# --------------------------------------------------

cv = GroupKFold(n_splits=N_SPLITS)

oof_true = np.full(len(df), -1, dtype=int)
oof_prob = np.full(len(df), np.nan)
oof_platform = df["platform"].to_numpy(copy=True)

print("Rows:", len(df))
print("Unique pages:", df["page_id"].nunique())
print("Generating out-of-fold predictions...")

for fold, (train_idx, val_idx) in enumerate(
    cv.split(df, groups=df["page_id"]), start=1
):
    fold_train = df.iloc[train_idx]
    fold_val = df.iloc[val_idx]

    thresholds = learn_thresholds(fold_train)

    y_train = make_labels(fold_train, thresholds)
    y_val = make_labels(fold_val, thresholds)

    model = make_model()
    model.fit(fold_train, y_train)

    probabilities = model.predict_proba(fold_val)[:, 1]

    oof_true[val_idx] = y_val
    oof_prob[val_idx] = probabilities

    predictions_050 = (probabilities >= 0.50).astype(int)

    print(
        f"Fold {fold}: "
        f"F1 at 0.50 = "
        f"{f1_score(y_val, predictions_050, zero_division=0):.4f}"
    )

assert np.all(oof_true >= 0)
assert np.isfinite(oof_prob).all()

# --------------------------------------------------
# 4. FIND THE BEST THRESHOLD
# --------------------------------------------------

threshold_rows = []

for threshold in np.arange(0.20, 0.81, 0.02):
    predictions = (oof_prob >= threshold).astype(int)

    threshold_rows.append({
        "threshold": round(float(threshold), 2),
        "precision": precision_score(
            oof_true, predictions, zero_division=0
        ),
        "recall": recall_score(
            oof_true, predictions, zero_division=0
        ),
        "f1": f1_score(
            oof_true, predictions, zero_division=0
        ),
        "accuracy": accuracy_score(oof_true, predictions),
    })

threshold_df = pd.DataFrame(threshold_rows)

print("\nTOP 10 THRESHOLDS BY OOF F1")
print(
    threshold_df.sort_values("f1", ascending=False)
    .head(10)
    .to_string(index=False, float_format=lambda x: f"{x:.4f}")
)

best_row = threshold_df.loc[threshold_df["f1"].idxmax()]
default_row = threshold_df.loc[
    (threshold_df["threshold"] - 0.50).abs().idxmin()
]

print("\nSelected threshold:", best_row["threshold"])
print("OOF F1 at selected threshold:", round(best_row["f1"], 4))
print("OOF F1 at 0.50:", round(default_row["f1"], 4))

# --------------------------------------------------
# 5. COMPARE THRESHOLDS ON OOF PREDICTIONS
# --------------------------------------------------

for label, threshold in [
    ("DEFAULT", 0.50),
    ("TUNED", float(best_row["threshold"])),
]:
    predictions = (oof_prob >= threshold).astype(int)

    print("\n" + "=" * 60)
    print(f"{label} THRESHOLD: {threshold:.2f}")
    print("=" * 60)

    print("Accuracy:", round(
        accuracy_score(oof_true, predictions), 4
    ))
    print("Precision:", round(
        precision_score(oof_true, predictions, zero_division=0), 4
    ))
    print("Recall:", round(
        recall_score(oof_true, predictions, zero_division=0), 4
    ))
    print("F1:", round(
        f1_score(oof_true, predictions, zero_division=0), 4
    ))
    print("ROC-AUC:", round(
        roc_auc_score(oof_true, oof_prob), 4
    ))

# --------------------------------------------------
# 6. PLATFORM-WISE OOF EVALUATION
# --------------------------------------------------

from sklearn.metrics import confusion_matrix

print("\n" + "=" * 65)
print("PLATFORM-WISE TF-IDF OOF EVALUATION")
print("=" * 65)

platform_thresholds = [0.40, 0.44, 0.50]

for platform in ["facebook", "instagram"]:
    mask = oof_platform == platform

    y_platform = oof_true[mask]
    prob_platform = oof_prob[mask]

    print(f"\n{platform.upper()} | Samples: {len(y_platform)}")

    for threshold in platform_thresholds:
        predictions = (prob_platform >= threshold).astype(int)

        precision = precision_score(
            y_platform, predictions, zero_division=0
        )
        recall = recall_score(
            y_platform, predictions, zero_division=0
        )
        f1 = f1_score(
            y_platform, predictions, zero_division=0
        )
        accuracy = accuracy_score(y_platform, predictions)

        cm = confusion_matrix(
            y_platform, predictions, labels=[0, 1]
        )

        print(
            f"\nThreshold: {threshold:.2f} | "
            f"Precision: {precision:.4f} | "
            f"Recall: {recall:.4f} | "
            f"F1: {f1:.4f} | "
            f"Accuracy: {accuracy:.4f}"
        )
        print("Confusion matrix [[TN, FP], [FN, TP]]:")
        print(cm)

threshold_df.to_csv("ml/tfidf_threshold_results.csv", index=False)

print("\nSaved: ml/tfidf_threshold_results.csv")
print("Threshold tuning complete. No application files were changed.")
