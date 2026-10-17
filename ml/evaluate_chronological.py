
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)

DATA_PATH = (
    r"C:\Users\Keerthan\Downloads"
    r"\social-media-post-performance-forecasting"
    r"\archive\train.csv"
)

NUMERIC_FEATURES = [
    "posting_hour", "posting_day", "posting_month",
    "caption_length", "word_count", "hashtag_count",
    "mention_count", "question_count",
    "exclamation_count", "newline_count",
]

CATEGORICAL_FEATURES = [
    "platform", "content_type_simplified",
]

PREDICTION_THRESHOLD = 0.50


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

df = df.sort_values("date_posted").reset_index(drop=True)


# --------------------------------------------------
# 2. CHRONOLOGICAL SPLIT
# --------------------------------------------------

cutoff = df["date_posted"].quantile(0.80)

train = df[df["date_posted"] < cutoff].copy()
test = df[df["date_posted"] >= cutoff].copy()

print("Chronological cutoff:", cutoff)
print("Training rows:", len(train))
print("Test rows:", len(test))
print("Training date range:",
      train["date_posted"].min(), "to",
      train["date_posted"].max())
print("Test date range:",
      test["date_posted"].min(), "to",
      test["date_posted"].max())

train_pages = set(train["page_id"])
test_pages = set(test["page_id"])

print("Training pages:", len(train_pages))
print("Test pages:", len(test_pages))
print("Pages in both periods:", len(train_pages & test_pages))
print("Pages only in test:", len(test_pages - train_pages))


# --------------------------------------------------
# 3. LEARN LABEL THRESHOLDS FROM TRAIN ONLY
# --------------------------------------------------

engagement_thresholds = {}

for platform in ["facebook", "instagram"]:
    platform_train = train[train["platform"] == platform]

    if platform_train.empty:
        raise ValueError(f"No training rows for {platform}")

    engagement_thresholds[platform] = float(
        platform_train["total_engagement"].quantile(0.75)
    )

print("\nTraining-only engagement thresholds:")
print(engagement_thresholds)


def make_labels(data):
    return np.array([
        int(
            row.total_engagement
            >= engagement_thresholds[row.platform]
        )
        for row in data.itertuples()
    ])


y_train = make_labels(train)
y_test = make_labels(test)

print("\nPositive label rate:")
print("Training:", round(float(y_train.mean()), 4))
print("Test:", round(float(y_test.mean()), 4))


# --------------------------------------------------
# 4. BUILD AND TRAIN COMBINED MODEL
# --------------------------------------------------

preprocessor = ColumnTransformer([
    (
        "categorical",
        OneHotEncoder(handle_unknown="ignore"),
        CATEGORICAL_FEATURES,
    ),
    (
        "numeric",
        Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]),
        NUMERIC_FEATURES,
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

model = Pipeline([
    ("preprocessor", preprocessor),
    (
        "model",
        LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=42,
        ),
    ),
])

model.fit(train, y_train)
test_prob = model.predict_proba(test)[:, 1]


# --------------------------------------------------
# 5. OVERALL TEST EVALUATION
# --------------------------------------------------

for threshold in [0.40, 0.44, 0.50]:
    predictions = (test_prob >= threshold).astype(int)

    print("\n" + "=" * 60)
    print(f"CHRONOLOGICAL TEST RESULTS | Threshold {threshold:.2f}")
    print("=" * 60)

    print("Accuracy:",
          round(accuracy_score(y_test, predictions), 4))
    print("Precision:",
          round(precision_score(
              y_test, predictions, zero_division=0
          ), 4))
    print("Recall:",
          round(recall_score(
              y_test, predictions, zero_division=0
          ), 4))
    print("F1:",
          round(f1_score(
              y_test, predictions, zero_division=0
          ), 4))

    if len(np.unique(y_test)) == 2:
        print("ROC-AUC:",
              round(roc_auc_score(y_test, test_prob), 4))
    else:
        print("ROC-AUC: undefined (test labels contain one class)")

    print("Confusion matrix [[TN, FP], [FN, TP]]:")
    print(confusion_matrix(y_test, predictions, labels=[0, 1]))


# --------------------------------------------------
# 6. PLATFORM-WISE TEST RESULTS
# --------------------------------------------------

test_platforms = test["platform"].to_numpy()

print("\n" + "=" * 60)
print("PLATFORM-WISE CHRONOLOGICAL TEST RESULTS")
print("=" * 60)

for platform in ["facebook", "instagram"]:
    mask = test_platforms == platform
    actual = y_test[mask]
    probabilities = test_prob[mask]

    print(f"\n{platform.upper()} | Rows: {len(actual)}")
    print("Positive label rate:", round(float(actual.mean()), 4))

    for threshold in [0.40, 0.44, 0.50]:
        predictions = (probabilities >= threshold).astype(int)

        print(
            f"Threshold {threshold:.2f} | "
            f"Precision: {precision_score(actual, predictions, zero_division=0):.4f} | "
            f"Recall: {recall_score(actual, predictions, zero_division=0):.4f} | "
            f"F1: {f1_score(actual, predictions, zero_division=0):.4f}"
        )

    if len(np.unique(actual)) == 2:
        print("Platform ROC-AUC:",
              round(roc_auc_score(actual, probabilities), 4))
    else:
        print("Platform ROC-AUC: undefined (only one class present)")


# --------------------------------------------------
# 7. SAVE TEST PREDICTIONS FOR AUDIT
# --------------------------------------------------

output = test[[
    "page_id", "platform", "date_posted",
    "likes", "comments", "total_engagement",
]].copy()

output["actual_high_engagement"] = y_test
output["predicted_probability"] = test_prob

output.to_csv("ml/chronological_test_predictions.csv", index=False)

print("\nSaved: ml/chronological_test_predictions.csv")
print("Chronological evaluation complete.")
print("No application files were changed.")
