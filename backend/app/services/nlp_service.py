import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

from ..utils.preprocess import preprocess_text

import os


class NLPService:

    def __init__(self):

        # Logistic Regression Model
        self.model = LogisticRegression(
            max_iter=1000
        )

        # TF-IDF Vectorizer
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=10000,
            ngram_range=(1, 2)
        )

        self.is_trained = False

    def train_model(self):
        """
        Load and train NLP models
        """

        try:

            # -----------------------------------
            # Load datasets
            # -----------------------------------

            fake_path = os.path.join(
                os.path.dirname(__file__),
                '../../data/Fake.csv'
            )

            true_path = os.path.join(
                os.path.dirname(__file__),
                '../../data/True.csv'
            )

            # Read datasets
            fake_df = pd.read_csv(fake_path)

            true_df = pd.read_csv(true_path)

            # Add labels
            fake_df['label'] = 'Fake'

            true_df['label'] = 'Real'

            # Combine datasets
            df = pd.concat(
                [fake_df, true_df],
                ignore_index=True
            )

            # Keep only required columns
            df = df[['text', 'label']]

            # Remove duplicate news articles
            df = df.drop_duplicates(subset=['text'])

            # Remove rows with missing text
            df = df.dropna(subset=['text'])

            # Remove empty text rows
            df = df[df['text'].str.strip() != ""]

            # Shuffle dataset
            df = df.sample(frac=1, random_state=42).reset_index(drop=True)

            # -----------------------------------
            # Text preprocessing
            # -----------------------------------

            df['text'] = df['text'].apply(
                preprocess_text
            )

            # -----------------------------------
            # TF-IDF Feature Extraction
            # -----------------------------------

            X = self.vectorizer.fit_transform(
                df['text']
            )

            y = df['label']

            # -----------------------------------
            # Train-Test Split
            # -----------------------------------

            X_train, X_test, y_train, y_test = train_test_split(
                X,
                y,
                test_size=0.2,
                random_state=42,
                stratify=y
            )

            # -----------------------------------
            # Logistic Regression
            # -----------------------------------

            self.model.fit(
                X_train,
                y_train
            )

            lr_predictions = self.model.predict(
                X_test
            )

            lr_accuracy = accuracy_score(
                y_test,
                lr_predictions
            )
            self.lr_precision = round(
                precision_score(
                    y_test,
                    lr_predictions,
                    pos_label="Real"
                ) * 100,
                2
            )

            self.lr_recall = round(
                recall_score(
                    y_test,
                    lr_predictions,
                    pos_label="Real"
                ) * 100,
                2
            )

            self.lr_f1 = round(
                f1_score(
                    y_test,
                    lr_predictions,
                    pos_label="Real"
                ) * 100,
                2
            )

            # -----------------------------------
            # Naive Bayes
            # -----------------------------------

            nb_model = MultinomialNB()

            nb_model.fit(
                X_train,
                y_train
            )

            nb_predictions = nb_model.predict(
                X_test
            )

            nb_accuracy = accuracy_score(
                y_test,
                nb_predictions
            )

            # Save model accuracies
            self.lr_accuracy = round(
                lr_accuracy * 100,
                2
            )

            self.nb_accuracy = round(
                nb_accuracy * 100,
                2
            )

            # Select best model
            if lr_accuracy >= nb_accuracy:

                self.best_model = (
                    "Logistic Regression"
                )

            else:

                self.best_model = (
                    "Naive Bayes"
                )

            self.is_trained = True

            print(
                "Professional NLP Model trained successfully."
            )

        except Exception as e:
            import traceback
            traceback.print_exc()

    def analyze_text(self, text: str):
        """
        Analyze user input text
        """

        # Train model if needed
        if not self.is_trained:

            self.train_model()

        if not self.is_trained:

            return {
                "error": "Model not trained."
            }

        # -----------------------------------
        # Preprocess Input
        # -----------------------------------

        processed_input = preprocess_text(
            text
        )

        # Convert text to TF-IDF vector
        X_input = self.vectorizer.transform(
            [processed_input]
        )

        # -----------------------------------
        # Prediction
        # -----------------------------------

        prediction = self.model.predict(
            X_input
        )[0]

        # Confidence score
        confidence = self.model.predict_proba(
            X_input
        ).max()

        # -----------------------------------
        # Suspicious Term Detection
        # -----------------------------------

        suspicious_terms = [

            "breaking",
            "secret",
            "miracle",
            "immortal",
            "overnight",
            "conspiracy",
            "fraud",
            "scam",
            "dangerous",
            "shocking",
            "exclusive",
            "hidden",
            "viral",
            "magic",
            "urgent",
            "leaked",
            "banned",
            "warning",
            "hoax"
        ]

        detected_terms = []

        lower_text = text.lower()

        for term in suspicious_terms:

            if term in lower_text:

                detected_terms.append(term)

        # -----------------------------------
        # AI Explanation
        # -----------------------------------

        if prediction == "Fake":

            reason = (
                "Text contains linguistic patterns "
                "commonly associated with fake "
                "or misleading news content."
            )

        else:

            reason = (
                "Text structure resembles "
                "reliable and factual news reporting."
            )

        # -----------------------------------
        # Final Response
        # -----------------------------------

        return {

            "text_analyzed": text,

            "prediction": prediction,

            "confidence": round(
                confidence * 100,
                2
            ),

            "reason": reason,

            "suspicious_terms_detected":
                detected_terms,

            "logistic_regression_accuracy":
                self.lr_accuracy,

            "logistic_regression_precision":
                self.lr_precision,

            "logistic_regression_recall":
                self.lr_recall,

            "logistic_regression_f1_score":
                self.lr_f1,

            "naive_bayes_accuracy":
                self.nb_accuracy,

            "best_model":
                self.best_model
        }

# Create NLP Service Object
nlp_service = NLPService()