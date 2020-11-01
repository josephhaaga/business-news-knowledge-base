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

    # process the article
    entities = [o for o in doc.ents if o.label_ in ["ORG", "PERSON", "GPE", "WORK_OF_ART", "FAC"]]
    print(f"Extracted {len(entities)} entities")


    # TODO: Consolidate multiple mentions of each entity into one (multiple sentences reference Palantir, but they all resolve to different Wikidata entities)
    for entity in entities:
        mention = get_mention_of_entity(entity)
        possible_matches = search_wikidata(entity.text)
        if len(possible_matches) == 1:
            match = possible_matches[0]
            print(f"{entity.text} is actually {match['id']} - {match['title']}: {match['description']}")
        elif len(possible_matches) > 1:
            results = []
            for match in possible_matches:
                if len(match["description"]) > 0:

                    results += [(
                        match["id"],
                        nlp(match["description"]).similarity(mention)
                    )]
            breakpoint()
            results.sort(key=lambda x: x[1], reverse=True)
            top_result, *_ = results
            best_match, = [match for match in possible_matches if match["id"] == top_result[0]]
            print(f"{entity.text} is likely {best_match['id']} - {best_match['title']}: {best_match['description']} with confidence {top_result[1]}")
        else:
            print(f"Wikidata has no match for {entity.text}")
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
    sentences = list(entity.doc.sents)
    i = 0
    for ind, length in enumerate([len(sent.text) for sent in sentences]):
        i += length
        if i > entity.start_char:
            return sentences[ind]


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
