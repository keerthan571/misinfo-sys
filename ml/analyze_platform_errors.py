
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ml"))
import train_engagement_model as training

def main():
    df = training.load_data()
    features = training.NUMERIC_FEATURES + training.CATEGORICAL_FEATURES + ["caption"]
    X = df[features]
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, valid_idx = next(splitter.split(X, df["likes"], groups=df["page_id"]))
    X_train, X_valid = X.iloc[train_idx], X.iloc[valid_idx]
    valid = df.iloc[valid_idx].copy()

    for target in ["likes", "comments"]:
        model = training.make_model("random_forest")
        model.fit(X_train, df[target].iloc[train_idx])
        valid["actual"] = df[target].iloc[valid_idx].to_numpy()
        valid["predicted"] = np.maximum(0, model.predict(X_valid))
        valid["absolute_error"] = abs(valid["actual"] - valid["predicted"])

        print(f"\n{'=' * 12} {target.upper()} BY PLATFORM {'=' * 12}")
        rows = []
        for platform, part in valid.groupby("platform"):
            rows.append({
                "platform": platform,
                "rows": len(part),
                "MAE": mean_absolute_error(part["actual"], part["predicted"]),
                "RMSE": np.sqrt(mean_squared_error(part["actual"], part["predicted"])),
                "R2": r2_score(part["actual"], part["predicted"]) if len(part) > 1 else np.nan,
                "median_actual": part["actual"].median(),
                "median_prediction": np.median(part["predicted"])
            })
        print(pd.DataFrame(rows).to_string(index=False))

if __name__ == "__main__":
    main()
