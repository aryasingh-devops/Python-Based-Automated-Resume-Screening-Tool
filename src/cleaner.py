"""
Text Cleaner Module.
Performs NLP preprocessing, regex scrubbing, normalization, and stopword removal.
"""

import re
from typing import Set

# Comprehensive English stopwords set (standard NLP stopwords)
DEFAULT_STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", 
    "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", 
    "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", 
    "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", 
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", 
    "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", 
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", 
    "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", 
    "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", 
    "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", 
    "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", 
    "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", 
    "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", 
    "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", 
    "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", 
    "yours", "yourself", "yourselves", "also", "using", "responsible", "worked", "working", 
    "including", "etc", "experience", "years", "well"
}


def clean_text(text: str, remove_stopwords: bool = True) -> str:
    """
    Cleans raw resume or job description text.
    1. Removes URLs and hyperlinks
    2. Removes email addresses and phone numbers
    3. Normalizes special tech terms (e.g., C++ -> cplusplus, C# -> csharp, .NET -> dotnet)
    4. Removes non-alphanumeric punctuation
    5. Normalizes spaces and lowercases
    6. Filters stopwords
    """
    if not text or not isinstance(text, str):
        return ""

    # 1. Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)

    # 2. Remove Emails
    text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', ' ', text)

    # 3. Remove Phone numbers
    text = re.sub(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}', ' ', text)

    # 4. Normalize special tech keywords before removing symbols
    text = re.sub(r'\bC\+\+\b', ' cplusplus ', text, flags=re.IGNORECASE)
    text = re.sub(r'\bC#\b', ' csharp ', text, flags=re.IGNORECASE)
    text = re.sub(r'\.NET\b', ' dotnet ', text, flags=re.IGNORECASE)
    text = re.sub(r'\bCI/CD\b', ' cicd ', text, flags=re.IGNORECASE)

    # 5. Remove special characters and digits but keep clean alphabets
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)

    # 6. Lowercase
    text = text.lower()

    # 7. Tokenize and remove stopwords
    tokens = text.split()
    if remove_stopwords:
        tokens = [word for word in tokens if word not in DEFAULT_STOPWORDS and len(word) > 1]

    # Re-map preserved tech tokens back to clean readable format
    normalized_tokens = []
    for t in tokens:
        if t == 'cplusplus':
            normalized_tokens.append('c++')
        elif t == 'csharp':
            normalized_tokens.append('c#')
        elif t == 'dotnet':
            normalized_tokens.append('.net')
        elif t == 'cicd':
            normalized_tokens.append('ci/cd')
        else:
            normalized_tokens.append(t)

    return " ".join(normalized_tokens)
