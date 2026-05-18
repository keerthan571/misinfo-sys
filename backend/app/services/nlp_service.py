import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import os

class NLPService:
    def __init__(self):
        # We will use a basic Logistic Regression model for demonstration
        self.model = LogisticRegression()
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.is_trained = False
        
    def train_model(self):
        """
        Loads the dummy dataset and trains a basic model.
        In a real scenario, this would load a pre-trained model file (e.g., .pkl)
        """
        csv_path = os.path.join(os.path.dirname(__file__), '../../dummy_dataset.csv')
        try:
            df = pd.read_csv(csv_path)
            # Simple preprocessing
            X = self.vectorizer.fit_transform(df['text'])
            y = df['label']
            self.model.fit(X, y)
            self.is_trained = True
            print("NLP Model trained successfully.")
        except Exception as e:
            print(f"Error training NLP model: {e}")

    def analyze_text(self, text: str):
        """
        Analyzes the given text for misinformation.
        """
        if not self.is_trained:
            self.train_model()
            
        if not self.is_trained:
             return {"error": "Model not trained."}

        # Vectorize input text
        X_input = self.vectorizer.transform([text])
        
        # Predict
        prediction = self.model.predict(X_input)[0]
        confidence = self.model.predict_proba(X_input).max()
        
        return {
            "text_analyzed": text,
            "prediction": prediction,
            "confidence": round(confidence * 100, 2)
        }

nlp_service = NLPService()
