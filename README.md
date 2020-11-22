# business-news-knowledge-base

Constructing a Spacy KnowledgeBase (and, soon, a knowledge graph) by reading news articles and referencing Wikidata.

## Usage

```bash
pip install -r requirements.txt
python3 main.py
```


## Notes

We use the [entity type labels](https://spacy.io/api/annotation#named-entities) from Spacy NER to query Wikidata for appropriate entity matches, but I'm realizing that the `en_core_web_md` model's NER tagging isn't great on business news (at least not on [this](https://www.cnbc.com/2020/09/22/palantir-says-it-expects-42percent-revenue-growth-this-year-to-1point06-billion.html) Palantir article).

The plan is to add a human-in-the-loop component where the user annotates the article to their liking, and a spacy KnowledgeBase is updated with their annotations. This should make resolving subsequent encounters of these entities easier.


