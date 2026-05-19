import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Initialize stemmer
stemmer = PorterStemmer()

# Load stopwords
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()

    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z]', ' ', text)

    # Tokenize text
    words = word_tokenize(text)

    # Remove stopwords and apply stemming
    processed_words = []

    for word in words:
        if word not in stop_words:
            stemmed_word = stemmer.stem(word)
            processed_words.append(stemmed_word)

    # Join words back into sentence
    processed_text = " ".join(processed_words)

    return processed_text