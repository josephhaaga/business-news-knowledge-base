import json
import time
from typing import Dict
from typing import List
from typing import Sequence

from newspaper import Article
import requests
import spacy
from spacy.kb import KnowledgeBase
from spacy import displacy


class LanguageService:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_md")
        self.vocab = self.nlp.vocab
        self.kb = KnowledgeBase(vocab=self.vocab, entity_vector_length=300)

    def download_article(self, url: str) -> spacy.tokens.doc.Doc:
        article = Article(url)
        article.download()
        article.parse()
        doc = self.nlp(article.text)
        doc.user_data["title"] = article.title
        # initial = displacy.serve(doc, style="ent")
        return doc

    def get_entity_mentions(self, doc) -> Dict[str, spacy.tokens.span.Span]:
        entities = [
            o
            for o in doc.ents
            if o.label_ in ["ORG", "PERSON", "GPE", "WORK_OF_ART", "FAC"]
        ]
        mentions_grouped_by_entity = {
            entity.text: [mention for mention in entities if mention.text == entity.text]
            for entity in entities
        }
        return mentions_grouped_by_entity


QID_FOR_POS_TAG = {
    "ORG": "Q43229",
    "PERSON": "Q5",
    "GPE": "Q15642541",
    "WORK_OF_ART": "Q15621286",
    "FAC": "Q811979",
}


def search_wikidata(entity_name: str, entity_pos_tag: str) -> List[Dict]:
    """Search Wikidata for entities named `entity_name`, whose type is a hyponym or match of `entity_type`.
    """
    url = "https://query.wikidata.org/sparql"
    QID = QID_FOR_POS_TAG[entity_pos_tag]
    clean_entity_name = entity_name.replace('"', "'")
    query = f"""
SELECT ?entity ?entityLabel WHERE {{
    SERVICE wikibase:mwapi {{
        bd:serviceParam wikibase:endpoint "www.wikidata.org";
        wikibase:api "EntitySearch";
        mwapi:search "{clean_entity_name}";
        mwapi:language "en".
        ?entity wikibase:apiOutputItem mwapi:item.
    }}
    ?entity wdt:P31/wdt:P279* wd:{QID} .
    SERVICE wikibase:label {{ #BabelRainbow
        bd:serviceParam wikibase:language "[AUTO_LANGUAGE],fr,ar,be,bg,bn,ca,cs,da,de,el,en,es,et,fa,fi,he,hi,hu,hy,id,it,ja,jv,ko,nb,nl,eo,pa,pl,pt,ro,ru,sh,sk,sr,sv,sw,te,th,tr,uk,yue,vec,vi,zh"
    }}
}}
LIMIT 10
    """
    try:
        r = requests.get(
            url,
            headers={"Accept": "application/json"},
            params={"format": "json", "query": query},
        )
        data = r.json()
        return data["results"]["bindings"]
    except json.decoder.JSONDecodeError:
        print("The following query failed")
        print(query)
        print()
        print(r)
        print()
        return []


def print_mention_of_entity(mention: spacy.tokens.span.Span) -> None:
    # sent, start_char, text_with_ws, end_char
    sent = mention.sent
    white_fg = "\u001b[37m"
    red_bg = "\u001b[41m"
    reset = "\u001b[0m"
    print(sent[:mention.start], end=' ')
    print(f"{red_bg}{white_fg}{mention.text}{reset}", end=' ')
    print(sent[mention.end:])
