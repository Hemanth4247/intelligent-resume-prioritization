import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
# import spacy # Uncomment and ensure 'en_core_web_sm' is downloaded for advanced use

class TextCleaner:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        # self.nlp = spacy.load("en_core_web_sm") # Load SpaCy model if needed for NER

    def clean_text(self, text: str) -> str:
        """Applies basic cleaning to text."""
        text = text.lower()
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove special characters
        tokens = text.split()
        tokens = [word for word in tokens if word not in self.stop_words]
        tokens = [self.lemmatizer.lemmatize(word) for word in tokens]
        return ' '.join(tokens)

    # def extract_entities_spacy(self, text: str):
    #     """Extracts named entities using SpaCy (if nlp model loaded)."""
    #     if hasattr(self, 'nlp'):
    #         doc = self.nlp(text)
    #         entities = {ent.label_: [ent.text for ent in doc.ents] for ent in doc.ents}
    #         return entities
    #     return {}