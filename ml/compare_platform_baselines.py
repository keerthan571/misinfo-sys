
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ml"))
import train_engagement_model as training

def metrics(actual, predicted):
    return {
        "MAE": mean_absolute_error(actual, predicted),
        "RMSE": np.sqrt(mean_squared_error(actual, predicted)),
        "R2": r2_score(actual, predicted)
    }

def main():
    df = training.load_data().reset_index(drop=True)
    X = df[training.NUMERIC_FEATURES + training.CATEGORICAL_FEATURES + ["caption"]]
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, valid_idx = next(splitter.split(X, df["likes"], groups=df["page_id"]))
    train = df.iloc[train_idx]
    valid = df.iloc[valid_idx].copy()

    for target in ["likes", "comments"]:
        print(f"\n{'=' * 10} {target.upper()} {'=' * 10}")
        model = training.make_model("random_forest")
        model.fit(X.iloc[train_idx], train[target])
        valid["model_prediction"] = np.maximum(0, model.predict(X.iloc[valid_idx]))
        valid["platform_median"] = valid["platform"].map(
            train.groupby("platform")[target].median()
        )
        valid["global_median"] = train[target].median()

        for platform, part in valid.groupby("platform"):
            print(f"\nPlatform: {platform} | Rows: {len(part)}")
            for label, pred_col in [
                ("Shared Random Forest", "model_prediction"),
                ("Training platform median", "platform_median")
            ]:
                result = metrics(part[target], part[pred_col])
                print(label, {k: round(v, 3) for k, v in result.items()})

if __name__ == "__main__":
    main()
