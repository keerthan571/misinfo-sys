import csv
from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)

from app.services.nlp_service import nlp_service


# ============================================================
# PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "dataset.csv"


# ============================================================
# CONVERT PROJECT OUTPUT TO BINARY LABEL
# ============================================================

def normalize_prediction(result):
    """
    Converts the project's prediction output into:
    misinformation / not_misinformation
    """

    prediction = str(
        result.get("prediction", "")
    ).strip().lower()

    risk_score = float(
        result.get("risk_score", 0)
    )

    # Direct misinformation-related predictions
    if prediction in [
        "misinformation",
        "fake",
        "false",
        "likely misinformation",
        "high risk",
    ]:
        return "misinformation"

    # Direct genuine-related predictions
    if prediction in [
        "not misinformation",
        "true",
        "real",
        "likely true",
        "low risk",
        "credible",
    ]:
        return "not_misinformation"

    # Fallback based on project's risk score
    if risk_score >= 50:
        return "misinformation"

    return "not_misinformation"


# ============================================================
# LOAD DATASET AND RUN PROJECT MODEL
# ============================================================

y_true = []
y_pred = []

print("\n" + "=" * 60)
print("AI MISINFO - RESEARCH PAPER EVALUATION")
print("=" * 60 + "\n")


with open(
    DATASET_PATH,
    mode="r",
    encoding="utf-8",
    newline=""
) as file:

    reader = csv.DictReader(file)

    for index, row in enumerate(reader, start=1):

        text = row["text"].strip()
        actual_label = row["label"].strip()

        print(f"[{index}] Analyzing...")
        print(f"Text: {text}")

        result = nlp_service.analyze_text(text)

        predicted_label = normalize_prediction(result)

        y_true.append(actual_label)
        y_pred.append(predicted_label)

        print(f"Actual:    {actual_label}")
        print(f"Predicted: {predicted_label}")
        print(
            f"Raw Prediction: {result.get('prediction', 'Unknown')}"
        )
        print(
            f"Risk Score: {result.get('risk_score', 0)}"
        )
        print("-" * 60)


# ============================================================
# CALCULATE METRICS
# ============================================================

accuracy = accuracy_score(y_true, y_pred)

precision = precision_score(
    y_true,
    y_pred,
    pos_label="misinformation",
    zero_division=0
)

recall = recall_score(
    y_true,
    y_pred,
    pos_label="misinformation",
    zero_division=0
)

f1 = f1_score(
    y_true,
    y_pred,
    pos_label="misinformation",
    zero_division=0
)


# ============================================================
# PRINT FINAL RESULTS
# ============================================================

print("\n" + "=" * 60)
print("FINAL EVALUATION RESULTS")
print("=" * 60)

print(f"Total Test Cases : {len(y_true)}")
print(f"Accuracy         : {accuracy * 100:.2f}%")
print(f"Precision        : {precision * 100:.2f}%")
print(f"Recall           : {recall * 100:.2f}%")
print(f"F1-Score         : {f1 * 100:.2f}%")

print("\nConfusion Matrix:")
print(
    confusion_matrix(
        y_true,
        y_pred,
        labels=[
            "misinformation",
            "not_misinformation"
        ]
    )
)

print("\nClassification Report:")
print(
    classification_report(
        y_true,
        y_pred,
        labels=[
            "misinformation",
            "not_misinformation"
        ],
        zero_division=0
    )
)