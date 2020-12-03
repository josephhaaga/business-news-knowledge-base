import random

import spacy
from spacy.util import minibatch, compounding

from utils import LanguageService


n_iter = 3

TRAIN_DATA = [
    (
        "Alex Karp is the CEO of Palantir",
        {"entities": [(0, 9, "PERSON"), (24, 32, "ORG")]},
    ),
    (
        "CEO of Palantir Alex Karp leaves the Elysee Palace in Paris, on May 23, 2018 after the “Tech for Good” summit.",
        {"entities": [(7, 15, "ORG"), (16, 25, "PERSON"), (37, 50, "FAC"), (54, 59, "GPE")]}
    )
]


def main():
    """Train a model to recognize custom entities."""

    nlp = spacy.load("en_core_web_md")

    URL = "https://www.cnbc.com/2020/09/22/palantir-says-it-expects-42percent-revenue-growth-this-year-to-1point06-billion.html"
    language_service = LanguageService()
    original_article = language_service.download_article(URL)

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]

    with nlp.disable_pipes(*other_pipes):
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            losses = {}
            batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(texts, annotations, drop=0.35, losses=losses)
            print("Losses", losses)

    # test the trained model
    for text, _ in TRAIN_DATA:
        doc = nlp(text)
        print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
        print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])
        print()

    nlp.meta["name"] = "My New Model"

    new_article = nlp(original_article.text)
    breakpoint()

if __name__ == "__main__":
    exit(main())
