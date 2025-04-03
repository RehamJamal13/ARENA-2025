# Full Clean and Complete NER Pipeline for LULCC Domain (Enhanced Version with Confidence)

import spacy
from spacy.pipeline import EntityRuler
from spacy.tokens import Span, Doc
from spacy.matcher import PhraseMatcher
import pandas as pd
import re
from tqdm import tqdm
import pycountry
from typing import List, Dict, Tuple

# Initialize spaCy with medium model for better NER
nlp = spacy.load("en_core_web_md", disable=["lemmatizer", "textcat"])

# -----------------------------
# 1. Text Cleaning Function
# -----------------------------
def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    replacements = [
        (r"\{.*?\}", " "),
        (r"'#text':", ""),
        (r"'@xmlns':", ""),
        (r"'\w+':\s*", " "),
        (r"km\s*[²2]", "km²"),
        (r"(\d)\s*-\s*(\d)", r"\1-\2"),
        (r"[^a-zA-Z0-9 .%°\-]+", " "),
        (r"\s+", " ")
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)
    return text.strip()

# -----------------------------
# 2. Vocabulary Loading
# -----------------------------
def load_vocabulary(filepath: str) -> List[str]:
    try:
        df = pd.read_csv(filepath)
        return df["word"].dropna().str.strip().unique().tolist()
    except Exception as e:
        print(f"Error loading vocabulary: {str(e)}")
        return []

# -----------------------------
# 3. Entity Extraction Class
# -----------------------------
class LULCExtractor:
    def __init__(self, nlp):
        self.nlp = nlp
        self.ruler = self._setup_entity_ruler()
        self.matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
        self._setup_matchers()

    def _setup_entity_ruler(self):
        if "entity_ruler" in nlp.pipe_names:
            nlp.remove_pipe("entity_ruler")
        ruler = nlp.add_pipe("entity_ruler", before="ner")

        geo_terms = [c.name for c in pycountry.countries] + [
            "Africa", "Asia", "Europe", "North America", "South America", "Oceania",
            "Sub-Saharan Africa", "North Africa", "East Africa", "West Africa", "Central Africa",
            "Southern Africa", "Sahel", "Sahara", "Middle East", "Western Asia", "Central Asia",
            "South Asia", "Southeast Asia", "East Asia", "Central America", "Caribbean",
            "Amazon", "Andes", "Patagonia", "Western Europe", "Eastern Europe", "Northern Europe",
            "Southern Europe", "Balkans", "Scandinavia", "Arctic", "Antarctica", "Australasia",
            "Melanesia", "Micronesia", "Polynesia"
        ]

        patterns = [
            {"label": "SURFACE_UNIT", "pattern":[
                {"TEXT": {"REGEX": r"\d+\.?\d*"}},
                {"LOWER": {"IN": ["km²", "ha", "hectares", "acres"]}}
            ]},
            {"label": "COORDINATES", "pattern": [
        {"TEXT": {"REGEX": r"\d{1,3}"}}, {"TEXT": "°"},
        {"TEXT": {"REGEX": "[NSEW]"}}, {"TEXT": "–"},
        {"TEXT": {"REGEX": r"\d{1,3}"}}, {"TEXT": "°"},
        {"TEXT": {"REGEX": "[NSEW]"}}
       ]},
            {"label": "CHANGE", "pattern": [
                {"LEMMA": {"IN": ["increase", "decrease", "expand", "convert"]}}
            ]},
            {"label": "CHANGE", "pattern": [{"LOWER": {"REGEX": r"(increase|decrease|loss(es)?|gain(s)?|expansion|expand)"}}]}

        ]
        ruler.add_patterns(patterns)
        return ruler

    def _setup_matchers(self):
        lulc_terms = load_vocabulary("/Users/rehamjamal/Desktop/ARENA 2025/data/LULC.csv")
        process_terms = load_vocabulary("/Users/rehamjamal/Desktop/ARENA 2025/data/LCprocess.csv")

        self.matcher.add("LULC", [self.nlp(term) for term in lulc_terms if len(term.split()) > 1])
        self.matcher.add("LULC_PROCESS", [self.nlp(term) for term in process_terms if len(term.split()) > 1])

    def extract(self, text: str) -> List[Dict]:
        doc = self.nlp(text)
        entities = []

        for ent in doc.ents:
            if ent.label_ in ["LULC", "LULC_PROCESS", "GEO", "SURFACE_UNIT", "CHANGE"]:
                entities.append({
                    "text": ent.text,
                    "label": ent.label_,
                    "confidence": 1.0,
                    "context": self._get_context(doc, ent)
                })

        for ent in doc.ents:
            if ent.label_ in ["DATE", "LOC", "ORG"]:
                confidence = self._estimate_confidence(ent)
                if confidence > 0.7:
                    entities.append({
                        "text": ent.text,
                        "label": ent.label_,
                        "confidence": confidence,
                        "context": self._get_context(doc, ent)
                    })

        matches = self.matcher(doc)
        for match_id, start, end in matches:
            label = self.nlp.vocab.strings[match_id]
            span = doc[start:end]
            entities.append({
                "text": span.text,
                "label": label,
                "confidence": 0.9,
                "context": self._get_context(doc, span)
            })

        return entities

    def _get_context(self, doc: Doc, span: Span, window: int = 5) -> str:
        start = max(0, span.start - window)
        end = min(len(doc), span.end + window)
        return doc[start:end].text

    def _estimate_confidence(self, ent: Span) -> float:
        length_factor = min(1.0, len(ent.text.split()) * 0.2)
        type_factor = 1.0 if ent.label_ == "LOC" else 0.8
        return round(length_factor * type_factor, 2)

# -----------------------------
# 4. Main Processing Function
# -----------------------------
def process_documents(input_csv: str, output_csv: str):
    extractor = LULCExtractor(nlp)
    df = pd.read_csv(input_csv)
    results = []

    for idx, row in tqdm(df.iterrows(), total=len(df)):
        text = " ".join(str(row[col]) for col in ["title", "abstract", "sections"] if pd.notnull(row[col]))
        text = clean_text(text)

        for entity in extractor.extract(text):
            results.append({
                "doc_id": idx,
                "authors": row.get("authors", ""),
                "title": row.get("title", "")[:100],
                **entity
            })

    pd.DataFrame(results).to_csv(output_csv, index=False)

# -----------------------------
# Run the pipeline
# -----------------------------
if __name__ == "__main__":
    process_documents(
        input_csv="/Users/rehamjamal/Desktop/ARENA 2025/extracted_text/extracted_data_full.csv",
        output_csv="/Users/rehamjamal/Desktop/ARENA 2025/notebook/lulc_entities_withCONF.csv"
    )
    print("✅ Processing complete! Results saved with confidence scores.")
