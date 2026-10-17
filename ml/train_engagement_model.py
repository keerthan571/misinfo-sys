
from pathlib import Path
import json
import warnings
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, FunctionTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.compose import TransformedTargetRegressor

warnings.filterwarnings("ignore", category=UserWarning)

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = Path.home() / "Downloads" / "social-media-post-performance-forecasting" / "archive" / "train.csv"
MODEL_DIR = ROOT / "ml" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
RANDOM_STATE = 42

def load_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    required = ["platform", "page_id", "date_posted", "recorded_at", "content_type", "caption", "likes", "comments"]
    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    df["date_posted"] = pd.to_datetime(df["date_posted"], utc=True, errors="coerce")
    df["recorded_at"] = pd.to_datetime(df["recorded_at"], utc=True, errors="coerce")
    df = df.dropna(subset=["date_posted", "recorded_at", "likes", "comments"]).copy()
    df = df[(df["recorded_at"] >= df["date_posted"]) & (df["likes"] >= 0) & (df["comments"] >= 0)].copy()
    age_hours = (df["recorded_at"] - df["date_posted"]).dt.total_seconds() / 3600
    df["post_age_hours"] = age_hours.clip(lower=0)
    df["posting_hour"] = df["date_posted"].dt.hour
    df["posting_day"] = df["date_posted"].dt.dayofweek
    df["posting_month"] = df["date_posted"].dt.month
    df["caption"] = df["caption"].fillna("").astype(str)
    df["caption_length"] = df["caption"].str.len()
    df["word_count"] = df["caption"].str.split().str.len()
    df["hashtag_count"] = df["caption"].str.count("#")
    df["mention_count"] = df["caption"].str.count("@")
    df["exclamation_count"] = df["caption"].str.count("!")
    df["question_count"] = df["caption"].str.count(r"\?")
    for col in ["platform", "page_id", "content_type"]:
        df[col] = df[col].fillna("unknown").astype(str).str.lower()
    return df.reset_index(drop=True)

NUMERIC_FEATURES = [
    "post_age_hours", "posting_hour", "posting_day", "posting_month",
    "caption_length", "word_count", "hashtag_count", "mention_count",
    "exclamation_count", "question_count"
]
CATEGORICAL_FEATURES = ["platform", "page_id", "content_type"]

def build_preprocessor():
    numeric = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scale", StandardScaler())
    ])
    categorical = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encode", OneHotEncoder(handle_unknown="ignore"))
    ])
    return ColumnTransformer([
        ("numeric", numeric, NUMERIC_FEATURES),
        ("categorical", categorical, CATEGORICAL_FEATURES),
        ("caption", TfidfVectorizer(max_features=3000, ngram_range=(1, 2), min_df=2, sublinear_tf=True), "caption")
    ], remainder="drop")

def make_model(model_name):
    if model_name == "baseline":
        estimator = DummyRegressor(strategy="median")
    elif model_name == "random_forest":
        estimator = RandomForestRegressor(
            n_estimators=180,
            min_samples_leaf=3,
            max_features=0.8,
            n_jobs=-1,
            random_state=RANDOM_STATE
        )
    else:
        raise ValueError(f"Unknown model: {model_name}")
    pipeline = Pipeline([
        ("preprocessor", build_preprocessor()),
        ("regressor", estimator)
    ])
    return TransformedTargetRegressor(
        regressor=pipeline,
        func=np.log1p,
        inverse_func=np.expm1,
        check_inverse=False
    )

def evaluate(y_true, y_pred):
    y_pred = np.maximum(0, np.asarray(y_pred))
    return {
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "R2": float(r2_score(y_true, y_pred))
    }

def main():
    print("Loading and preparing dataset...")
    df = load_data()
    print(f"Usable records: {len(df)}")
    print("Platform counts:")
    print(df["platform"].value_counts().to_string())

    features = NUMERIC_FEATURES + CATEGORICAL_FEATURES + ["caption"]
    X = df[features]
    results = []
    models = {}

    for target in ["likes", "comments"]:
        print(f"\n{'=' * 18} TARGET: {target.upper()} {'=' * 18}")
        y = df[target].astype(float)
        X_train, X_valid, y_train, y_valid = train_test_split(
            X, y, test_size=0.2, random_state=RANDOM_STATE
        )

        for model_name in ["baseline", "random_forest"]:
            print(f"Training {model_name}...")
            model = make_model(model_name)
            model.fit(X_train, y_train)
            predictions = model.predict(X_valid)
            metrics = evaluate(y_valid, predictions)
            row = {"target": target, "model": model_name, **metrics}
            results.append(row)
            print(json.dumps(row, indent=2))

            if model_name != "baseline":
                models[target] = model

    results_df = pd.DataFrame(results)
    metrics_path = MODEL_DIR / "validation_metrics.csv"
    results_df.to_csv(metrics_path, index=False)

    for target, model in models.items():
        model_path = MODEL_DIR / f"{target}_model.joblib"
        joblib.dump(model, model_path)
        print(f"Saved {target} model: {model_path}")

    metadata = {
        "dataset": str(DATA_PATH),
        "usable_rows": len(df),
        "features": features,
        "targets": ["likes", "comments"],
        "validation": "random 80/20 split; random_state=42",
        "target_transform": "log1p",
        "note": "Predicts engagement at the dataset's recorded observation time, not future engagement growth."
    }
    with open(MODEL_DIR / "model_metadata.json", "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)

    print(f"\nMetrics saved to: {metrics_path}")
    print("\nMODEL COMPARISON")
    print(results_df.sort_values(["target", "MAE"]).to_string(index=False))
    print("\nTraining completed. Review validation metrics before integrating into the application.")

if __name__ == "__main__":
    main()
