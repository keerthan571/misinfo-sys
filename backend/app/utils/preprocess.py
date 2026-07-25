import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Download required data
nltk.download("stopwords", quiet=True)

# Initialize
stemmer = PorterStemmer()
stop_words = set(stopwords.words("english"))

def preprocess_text(text):
    # Handle invalid input
    if not isinstance(text, str):
        return ""

    # Convert to lowercase
    text = text.lower()

    # Remove special characters and numbers
    text = re.sub(r'[^a-z\s]', ' ', text)

    # Split into words (much faster than word_tokenize)
    words = text.split()

    # Remove stopwords and apply stemming
    processed_words = [
        stemmer.stem(word)
        for word in words
        if word not in stop_words
    ]

    return " ".join(processed_words)