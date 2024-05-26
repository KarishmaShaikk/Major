from flask import Flask, render_template
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Sample data (replace with your actual data)
data = pd.DataFrame({
    'Name': ['Investor 1', 'Investor 2', 'Investor 3'],
    'Interests': ['Technology, AI', 'Finance, Startups', 'Healthcare, Biotech'],
    'Budget': [10000, 20000, 15000]
})

# TF-IDF Vectorization
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(data['Interests'])

# Compute cosine similarity matrix
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

def get_similar_investors(problem_statement):
    # Preprocess problem statement
    preprocessed_statement = preprocess_text(problem_statement)
    # Compute similarity with all investors
    sim_scores = list(cosine_sim[0])
    # Get indices of top 3 similar investors
    top_indices = sorted(range(len(sim_scores)), key=lambda i: sim_scores[i], reverse=True)[:3]
    # Return names of top similar investors
    return data['Name'].iloc[top_indices]

def preprocess_text(text):
    # Tokenization, remove stopwords, and lemmatization
    # Implement your preprocessing steps here, similar to the previous example
    tokens = word_tokenize(text.lower())

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]

    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]

    # Join tokens back into a string
    preprocessed_text = ' '.join(tokens)

    return preprocessed_text




print(get_similar_investors("Power banks using lithium ion batteries"))