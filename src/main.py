import operator

import spacy
from spacy.kb import KnowledgeBase

from utils import LanguageService
from utils import prompt_user_to_annotate_entity
from utils import search_wikidata


def main() -> int:
    URL = "https://www.cnbc.com/2020/09/22/palantir-says-it-expects-42percent-revenue-growth-this-year-to-1point06-billion.html"

    language_service = LanguageService()
    doc = language_service.download_article(URL)


    p = doc.ents[0]
    prompt_user_to_annotate_entity(p)
    breakpoint()

    # add Palantir to the KnowledgeBase
    entity_to_add = "Palantir"
    entity_id = "Q2047336"
    start_of_first_mention = doc.text.index(entity_to_add)
    end_of_first_mention = start_of_first_mention + len(entity_to_add)
    span = doc.char_span(start_of_first_mention, end_of_first_mention)

    language_service.kb.add_entity(
        entity=entity_id,
        freq=doc.text.count(entity_to_add),
        entity_vector=span.vector,
    )

    language_service.kb.add_alias(
        alias=entity_to_add, entities=[entity_id], probabilities=[1.0]
    )

    # Looks like we also need add the entities and retrain the model

    doc = language_service.download_article(URL)
    entity_mentions = language_service.get_entity_mentions(doc)
    print(f"Extracted {len(entity_mentions)} entities")
    for entity, mentions in entity_mentions.items():
        _ = [mention.label_ for mention in mentions]
        labels_and_counts = {i: _.count(i) for i in set(_)}
        most_frequent_label = max(
            labels_and_counts.items(), key=operator.itemgetter(1)
        )[0]

        print(f"Searching for {entity} using entity label {most_frequent_label}")
        potential_matches = search_wikidata(entity, most_frequent_label)
        print(f"{len(potential_matches)} matches found")

        for match in potential_matches:
            print(f"{match['entityLabel']['value']} - {match['entity']['value']}")
        print()


if __name__ == "__main__":
    exit(main())
