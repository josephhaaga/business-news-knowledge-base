import operator

import spacy

from utils import download_article
from utils import get_entity_mentions
from utils import get_mention_of_entity
from utils import search_wikidata


def main() -> int:
    URL = "https://www.cnbc.com/2020/09/22/palantir-says-it-expects-42percent-revenue-growth-this-year-to-1point06-billion.html"

    doc = download_article(URL)
    entity_mentions = get_entity_mentions(doc)
    print(f"Extracted {len(entity_mentions)} entities")

    for entity, mentions in entity_mentions.items():
        mention_spans = [get_mention_of_entity(mention) for mention in mentions]
        composite_mention = " ".join([mention.text for mention in mention_spans])
        print(f"Searching for {entity} using the following context:\n{composite_mention}")

        # pos_tag_description = spacy.explain(mentions[0].label_)
        _ = [mention.label_ for mention in mentions]
        labels_and_counts = {i: _.count(i) for i in set(_)}
        most_frequent_label = max(labels_and_counts.items(), key=operator.itemgetter(1))[0]

        potential_matches = search_wikidata(entity, most_frequent_label)
        breakpoint()


if __name__ == "__main__":
    exit(main())
