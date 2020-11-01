from typing import Dict
from typing import List
from typing import Sequence

from bs4 import BeautifulSoup
from newspaper import Article
import requests
import spacy
from spacy import displacy


nlp = spacy.load("en_core_web_md")

def main() -> int:
    # download an article
    URL = "https://www.cnbc.com/2020/09/22/palantir-says-it-expects-42percent-revenue-growth-this-year-to-1point06-billion.html"
    article = download_article(URL)
    doc = nlp(article.text)
    doc.user_data["title"] = article.title
    # initial = displacy.serve(doc, style="ent")
    entities = [o for o in doc.ents if o.label_ in ["ORG", "PERSON", "GPE", "WORK_OF_ART", "FAC"]]
    print(f"Extracted {len(entities)} entities")

    consolidated_entities = {entity.text: [mention for mention in entities if mention.text == entity.text] for entity in entities}
    for entity, mentions in consolidated_entities.items():
        mention_spans = [get_mention_of_entity(mention) for mention in mentions]
        composite_mention = " ".join([mention.text for mention in mention_spans])
        print(f"Searching for {entity} using the following context")
        print(composite_mention)
        possible_matches = search_wikidata(entity)
        breakpoint()
        if len(possible_matches) == 1:
            match = possible_matches[0]
            print(f"{entity} is actually {match['id']} - {match['title']}: {match['description']}")
        elif len(possible_matches) > 1:
            embedded_composite_mention = nlp(composite_mention)
            results = []
            for match in possible_matches:
                # use a Wikidata library to grab metadata/categories (description embeddings don't work)
                if len(match["description"]) > 0:
                    results += [(
                        match["id"],
                        nlp(match["description"]).similarity(embedded_composite_mention)
                    )]
            breakpoint()
            results.sort(key=lambda x: x[1], reverse=True)
            top_result, *_ = results
            best_match, = [match for match in possible_matches if match["id"] == top_result[0]]
            print(f"{entity} is likely {best_match['id']} - {best_match['title']}: {best_match['description']} with confidence {top_result[1]}")
        else:
            print(f"Wikidata has no match for {entity}")
        print()
        # TODO: add to KnowledgeBase
    breakpoint()
    # TODO: retrain the model/KnowledgeBase


    # resolve to entities on wikidata
    for org in orgs:
        wikidata_matches = search_wikidata(org)
        print(f"{org} returned {len(wikidata_matches)} Wikidata matches:")
        for match in wikidata_matches:
            print(f"  {match['id']} - {match['title']}: {match['description']}")


def download_article(url: str) -> Article:
    article = Article(url)
    article.download()
    article.parse()
    return article


def get_mention_of_entity(entity):
    total = 0
    for sent in entity.doc.sents:
        total += len(sent.text)
        if total > entity.start_char:
            return sent


def search_wikidata(query: str) -> List[Dict]:
    page = requests.get(f"https://www.wikidata.org/w/index.php?search={query}")
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find_all('li', class_='mw-search-result')
    return [{
        "title": result.find("span", class_="wb-itemlink-label").text,
        "id": result.find("span", class_="wb-itemlink-id").text.lstrip("(").rstrip(")"),
        "description": result.find("span", class_="wb-itemlink-description").text
    } for result in results]


if __name__ == "__main__":
    exit(main())
