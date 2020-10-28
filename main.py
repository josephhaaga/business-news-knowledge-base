from typing import Dict
from typing import List

from bs4 import BeautifulSoup
from newspaper import Article
import requests
import spacy


def main() -> int:
    # download an article
    URL = "https://www.cnbc.com/2020/09/22/palantir-says-it-expects-42percent-revenue-growth-this-year-to-1point06-billion.html"
    article = Article(URL)
    article.download()
    article.parse()
    print(f"Processing article: \"{article.title}\"")

    # process the article
    nlp = spacy.load("en_core_web_md")
    parsed = nlp(article.text)
    orgs = {o.text for o in parsed.ents if o.label_ == "ORG"}
    print(f"Extracted {len(orgs)} ORG entities")
    print(orgs)

    # look for entities on wikidata
    for org in orgs:
        wikidata_matches = search_wikidata(org)
        print(f"{org} returned {len(wikidata_matches)} Wikidata matches:")
        for match in wikidata_matches:
            print(f"  {match['id']} - {match['title']}: {match['description']}")
        # TODO: embed descriptions and predict the best match (similarity to article text)



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
