import nltk

# Download required NLTK data files
# nltk.download('punkt_tab')
# nltk.download('stopwords')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('wordnet')

from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return synonyms


def preprocess_and_expand(sentence):
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(sentence)
    filtered_tokens = [w for w in tokens if w.lower() not in stop_words]
    expanded_sentence = []

    for word in filtered_tokens:
        synonyms = get_synonyms(word)
        if synonyms:
            expanded_sentence.extend(synonyms)
        else:
            expanded_sentence.append(word)

    return ' '.join(expanded_sentence)


def calculate_similarity(sentence1, sentence2):
    sentence1_expanded = preprocess_and_expand(sentence1)
    sentence2_expanded = preprocess_and_expand(sentence2)

    vectorizer = CountVectorizer().fit_transform([sentence1_expanded, sentence2_expanded])
    vectors = vectorizer.toarray()
    similarity = cosine_similarity(vectors)
    return similarity[0, 1]


correct_answer = "Cat is a pet, it can be black"
user_answer = "Usually cots are black"

similarity_score = calculate_similarity(correct_answer, user_answer)
print(f"Similarity score: {similarity_score:.2f}")

if similarity_score > 0.5:
    print("The answers are similar.")
else:
    print("The answers are not similar.")
