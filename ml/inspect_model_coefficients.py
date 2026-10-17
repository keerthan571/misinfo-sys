import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupShuffleSplit

DATA_PATH = (
    r"C:\Users\Keerthan\Downloads"
    r"\social-media-post-performance-forecasting"
    r"\archive\train.csv"
)

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
# 2. PAGE-GROUPED TRAINING SPLIT
# --------------------------------------------------

splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.20,
    random_state=42,
)

train_idx, test_idx = next(
    splitter.split(df[features], groups=df["page_id"])
)

train_df = df.iloc[train_idx].copy()
test_df = df.iloc[test_idx].copy()

assert set(train_df["page_id"]).isdisjoint(set(test_df["page_id"]))

# Calculate thresholds using training pages only.
thresholds = {}

for platform in ["facebook", "instagram"]:
    rows = train_df[train_df["platform"] == platform]
    thresholds[platform] = float(
        rows["total_engagement"].quantile(0.75)
    )

y_train = np.array([
    int(row.total_engagement >= thresholds[row.platform])
    for row in train_df.itertuples()
])

y_test = np.array([
    int(row.total_engagement >= thresholds[row.platform])
    for row in test_df.itertuples()
])

print("Training rows:", len(train_df))
print("Held-out rows:", len(test_df))
print("Training thresholds:", thresholds)

# --------------------------------------------------
# 3. TRAIN LOGISTIC REGRESSION
# --------------------------------------------------

preprocessor = ColumnTransformer([
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

model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42,
    )),
])

model.fit(train_df[features], y_train)

# --------------------------------------------------
# 4. EXTRACT COEFFICIENTS
# --------------------------------------------------

fitted_preprocessor = model.named_steps["preprocessor"]
classifier = model.named_steps["classifier"]

feature_names = fitted_preprocessor.get_feature_names_out()
coefficients = classifier.coef_[0]

coef_df = pd.DataFrame({
    "feature": feature_names,
    "coefficient": coefficients,
})

coef_df["absolute_coefficient"] = coef_df["coefficient"].abs()

coef_df = coef_df.sort_values(
    "absolute_coefficient", ascending=False
)

print("\n" + "=" * 65)
print("TOP 15 FEATURES BY ABSOLUTE COEFFICIENT")
print("=" * 65)
print(
    coef_df.head(15)[["feature", "coefficient"]]
    .to_string(index=False, float_format=lambda x: f"{x:.4f}")
)

print("\n" + "=" * 65)
print("TOP 10 POSITIVE COEFFICIENTS")
print("=" * 65)
print(
    coef_df.nlargest(10, "coefficient")[
        ["feature", "coefficient"]
    ].to_string(index=False, float_format=lambda x: f"{x:.4f}")
)

print("\n" + "=" * 65)
print("TOP 10 NEGATIVE COEFFICIENTS")
print("=" * 65)
print(
    coef_df.nsmallest(10, "coefficient")[
        ["feature", "coefficient"]
    ].to_string(index=False, float_format=lambda x: f"{x:.4f}")
)

# --------------------------------------------------
# 5. PLATFORM-SPECIFIC HELD-OUT PERFORMANCE
# --------------------------------------------------

test_prob = model.predict_proba(test_df[features])[:, 1]

from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score
)

print("\n" + "=" * 65)
print("HELD-OUT PERFORMANCE AT DEFAULT THRESHOLD")
print("=" * 65)

for platform in ["facebook", "instagram"]:
    mask = test_df["platform"].to_numpy() == platform

    actual = y_test[mask]
    probabilities = test_prob[mask]
    predictions = (probabilities >= 0.50).astype(int)

    print(f"\n{platform.upper()}")
    print("Posts:", len(actual))
    print("Precision:", round(
        precision_score(actual, predictions, zero_division=0), 4
    ))
    print("Recall:", round(
        recall_score(actual, predictions, zero_division=0), 4
    ))
    print("F1:", round(
        f1_score(actual, predictions, zero_division=0), 4
    ))

    if len(np.unique(actual)) == 2:
        print("ROC-AUC:", round(
            roc_auc_score(actual, probabilities), 4
        ))

# --------------------------------------------------
# 6. SAVE COEFFICIENT REPORT
# --------------------------------------------------

output_path = "ml/feature_coefficients.csv"
coef_df.to_csv(output_path, index=False)

print(f"\nCoefficient report saved to: {output_path}")
print("Inspection complete. No application files were changed.")
