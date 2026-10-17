
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ml"))
import train_engagement_model as training

def main():
    df = training.load_data()
    features = training.NUMERIC_FEATURES + training.CATEGORICAL_FEATURES + ["caption"]
    X = df[features]
    groups = df["page_id"]
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, valid_idx = next(splitter.split(X, df["likes"], groups=groups))
    X_train, X_valid = X.iloc[train_idx], X.iloc[valid_idx]
    print("Training rows:", len(train_idx))
    print("Validation rows:", len(valid_idx))
    print("Training pages:", groups.iloc[train_idx].nunique())
    print("Validation pages:", groups.iloc[valid_idx].nunique())
    print("Page overlap:", len(set(groups.iloc[train_idx]) & set(groups.iloc[valid_idx])))

    for target in ["likes", "comments"]:
        y = df[target].astype(float)
        y_train, y_valid = y.iloc[train_idx], y.iloc[valid_idx]
        print(f"\n{'=' * 12} {target.upper()} {'=' * 12}")

        baseline = DummyRegressor(strategy="median")
        baseline.fit(np.zeros((len(y_train), 1)), y_train)
        baseline_pred = baseline.predict(np.zeros((len(y_valid), 1)))

        preprocessor = training.build_preprocessor()
        forest = Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", RandomForestRegressor(
                n_estimators=180,
                min_samples_leaf=3,
                max_features=0.8,
                n_jobs=-1,
                random_state=42
            ))
        ])
        model = TransformedTargetRegressor(
            regressor=forest,
            func=np.log1p,
            inverse_func=np.expm1,
            check_inverse=False
        )
        model.fit(X_train, y_train)
        pred = np.maximum(0, model.predict(X_valid))

        for name, values in [
            ("Baseline", baseline_pred),
            ("Random Forest", pred)
        ]:
            print(
                f"{name}: "
                f"MAE={mean_absolute_error(y_valid, values):.2f}, "
                f"RMSE={np.sqrt(mean_squared_error(y_valid, values)):.2f}, "
                f"R2={r2_score(y_valid, values):.4f}"
            )

if __name__ == "__main__":
    main()
