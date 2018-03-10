import json, os, sys, codecs
import spacy
from etk.etk import ETK
from etk.extractors.glossary_extractor import GlossaryExtractor
from etk.extractors.date_extractor import DateExtractor, DateParser
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))


etk = ETK()
nlp = etk.default_nlp

dp = DateParser()
settings = {
    'STRICT_PARSING': True
}

with open('date_ground_truth.txt', 'r', encoding='utf-8') as infile:
    for line in infile:
        line = line.strip()
        if line == "":
            print("\n")
            continue
        if line[0] == "#":
            continue

        values = line.split("|")
        print("===> {}".format(values[0]))
        nlp_text = "Hello, I will see you on {}. See you later".format(values[0])
        doc = nlp(nlp_text)
        gt = values[1] if len(values) > 1 else ""
        for ent in doc.ents:
            if ent.label_ in ['DATE']:
                parsed = dp.parse_date(ent.text, settings=settings)
                iso = dp.convert_to_iso_format(parsed)
                print("{} ({}) -> {}".format(ent.text, iso, gt))