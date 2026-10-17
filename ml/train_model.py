import os
import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    RandomForestClassifier,
    HistGradientBoostingClassifier
)

# PATHS
DATA_PATH = (
    r"C:\Users\Keerthan\Downloads"
    r"\social-media-post-performance-forecasting"
    r"\archive\train.csv"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# LOAD DATA
print("Loading dataset...")
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)
print(f"Original dataset shape: {df.shape}")

# KEEP FACEBOOK AND INSTAGRAM
df["platform"] = df["platform"].astype(str).str.lower()
df = df[df["platform"].isin(["facebook", "instagram"])].copy()

if df.empty:
    raise ValueError("No Facebook or Instagram records found.")

print(f"Facebook + Instagram shape: {df.shape}")
print("\nPlatform distribution:")
print(df["platform"].value_counts())

# PREPARE DATES
df["date_posted"] = pd.to_datetime(
    df["date_posted"], errors="coerce", utc=True
)

df = df.dropna(subset=["date_posted"]).copy()

df["posting_hour"] = df["date_posted"].dt.hour
df["posting_day"] = df["date_posted"].dt.dayofweek
df["posting_month"] = df["date_posted"].dt.month

# CAPTION FEATURES
df["caption"] = df["caption"].fillna("").astype(str)
df["content_type"] = df["content_type"].fillna("Unknown").astype(str)

df["caption_length"] = df["caption"].str.len()
df["word_count"] = df["caption"].str.split().str.len()
df["hashtag_count"] = df["caption"].str.count("#")
df["mention_count"] = df["caption"].str.count("@")
df["question_count"] = df["caption"].str.count(r"\?")
df["exclamation_count"] = df["caption"].str.count("!")
df["newline_count"] = df["caption"].str.count("\n")

# VALIDATE ENGAGEMENT VALUES
df["likes"] = pd.to_numeric(df["likes"], errors="coerce")
df["comments"] = pd.to_numeric(df["comments"], errors="coerce")

df = df.dropna(subset=["likes", "comments"]).copy()
df = df[
    (df["likes"] >= 0) & (df["comments"] >= 0)
].copy()

if df.empty:
    raise ValueError("No valid engagement records remain.")

# CREATE PLATFORM-AWARE TARGET
# Likes and comments define the target but are NOT model inputs.
df["total_engagement"] = df["likes"] + df["comments"]
df["high_spread"] = 0
thresholds = {}

for platform in ["facebook", "instagram"]:
    mask = df["platform"] == platform

    if mask.sum() < 4:
        raise ValueError(
            f"Insufficient records for platform: {platform}"
        )

    threshold = float(
        df.loc[mask, "total_engagement"].quantile(0.75)
    )

    thresholds[platform] = threshold

    df.loc[mask, "high_spread"] = (
        df.loc[mask, "total_engagement"] >= threshold
    ).astype(int)

    print(
        f"\n{platform.upper()} high-engagement threshold: "
        f"{threshold:.2f}"
    )

print("\nTARGET DISTRIBUTION")
print(
    df.groupby("platform")["high_spread"]
    .value_counts()
    .unstack(fill_value=0)
)

# FEATURES
# observation_hours is intentionally excluded because it describes
# the delay until dataset recording and is not known for a new upload.
feature_columns = [
    "platform",
    "content_type",
    "posting_hour",
    "posting_day",
    "posting_month",
    "caption_length",
    "word_count",
    "hashtag_count",
    "mention_count",
    "question_count",
    "exclamation_count",
    "newline_count"
]

X = df[feature_columns].copy()
y = df["high_spread"].astype(int)

categorical_features = ["platform", "content_type"]
numeric_features = [
    column for column in feature_columns
    if column not in categorical_features
]

# SPLIT DATA
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print(f"\nTraining samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")

# PREPROCESSING
# Dense one-hot output also supports HistGradientBoostingClassifier.
preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False
            ),
            categorical_features
        ),
        (
            "numeric",
            "passthrough",
            numeric_features
        )
    ],
    remainder="drop"
)

# MODELS
models = {
    "baseline": DummyClassifier(
        strategy="most_frequent"
    ),
    "logistic_regression": LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42
    ),
    "random_forest": RandomForestClassifier(
        n_estimators=400,
        max_depth=18,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    ),
    "hist_gradient_boosting": HistGradientBoostingClassifier(
        max_iter=300,
        learning_rate=0.05,
        max_leaf_nodes=31,
        l2_regularization=1.0,
        random_state=42
    )
}

results = []
trained_models = {}

# TRAIN AND EVALUATE
for name, model in models.items():
    print("\n" + "=" * 45)
    print(f"MODEL: {name.upper()}")
    print("=" * 45)

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model)
        ]
    )

    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)
    probabilities = pipeline.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(
        y_test, predictions, zero_division=0
    )
    recall = recall_score(
        y_test, predictions, zero_division=0
    )
    f1 = f1_score(
        y_test, predictions, zero_division=0
    )
    auc = roc_auc_score(y_test, probabilities)

    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")
    print(f"ROC-AUC  : {auc:.4f}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            predictions,
            labels=[0, 1],
            target_names=["Normal Engagement", "High Engagement"],
            zero_division=0
        )
    )

    print("Confusion Matrix:")
    print(confusion_matrix(y_test, predictions))

    results.append({
        "model": name,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": auc
    })

    trained_models[name] = pipeline

# COMPARE MODELS
results_df = pd.DataFrame(results)

print("\n" + "=" * 65)
print("FINAL MODEL COMPARISON")
print("=" * 65)
print(
    results_df.sort_values("f1", ascending=False).to_string(
        index=False
    )
)

# SELECT BEST NON-BASELINE MODEL
candidate_results = results_df[
    results_df["model"] != "baseline"
].copy()

if candidate_results.empty:
    raise RuntimeError("No candidate models were evaluated.")

best_row = candidate_results.sort_values(
    ["f1", "roc_auc"],
    ascending=False
).iloc[0]

best_model_name = best_row["model"]
best_model = trained_models[best_model_name]

# SAVE MODEL AND METADATA
model_path = os.path.join(
    MODEL_DIR,
    "fb_instagram_spread_model.pkl"
)

threshold_path = os.path.join(
    MODEL_DIR,
    "spread_thresholds.pkl"
)

results_path = os.path.join(
    MODEL_DIR,
    "model_results.csv"
)

metadata_path = os.path.join(
    MODEL_DIR,
    "spread_model_metadata.pkl"
)

joblib.dump(best_model, model_path)
joblib.dump(thresholds, threshold_path)
results_df.to_csv(results_path, index=False)

joblib.dump(
    {
        "features": feature_columns,
        "target": (
            "High engagement: total likes + comments "
            "at or above the platform-specific 75th percentile"
        ),
        "platforms": ["facebook", "instagram"],
        "best_model": best_model_name,
        "evaluation_split": "Random stratified 80/20 split",
        "random_state": 42
    },
    metadata_path
)

# FINAL SUMMARY
print("\n" + "=" * 45)
print("BEST CANDIDATE MODEL")
print("=" * 45)
print(f"Model    : {best_model_name}")
print(f"F1 Score : {best_row['f1']:.4f}")
print(f"ROC-AUC  : {best_row['roc_auc']:.4f}")

print("\nSaved files:")
print(model_path)
print(threshold_path)
print(results_path)
print(metadata_path)
