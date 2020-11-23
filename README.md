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


```bash
$ python3 main.py
processing article "palantir says in updated filing it expects 42% revenue growth this year to $1.06 billion"

extracted 5 entities; 5 not found in knowledgebase

1. "palantir alex karp"
is this an entity? (y/n)
>> n
how many entities are present in this span? (enter a number >= 0)
>> 2
entity 1 name:
>> palantir
entity 1 (palantir) label:
>> org
entity 2 name:
>> alex karp
entity 2 (alex karp) label:
>> person
2 entities added to knowledge base

3. "elysee palace"
is this an entity? (y/n)
>> y
is "elysee palace" a fac? (e.g. building, highway, airport, bridge)
>> y
1 entity added to knowledge base

...

...querying wikidata to resolve entities...
```
