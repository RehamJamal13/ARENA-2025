Research Goals & Approach

The main goal of this project is to automate the extraction of relations between entities in scientific literature related to Land Use and Land Cover (LULC).

To achieve this, we explored two complementary strategies:

1. Pipeline Approach

Entity Extraction

Rule-based: SpaCy + custom vocabulary

Transformer-based: fine-tuned RoBERTa model for improved NER

Relation Extraction

Tested multiple models, including Mistral AI and LLaMA 3, to link extracted entities with appropriate relation types

2. Joint Entity + Relation Extraction

Unified models to simultaneously extract both entities and their relations in one step

Goal: reduce error propagation from pipeline design and improve consistency

3. Relevant Sentence Extraction

To focus only on sentences likely to contain LULC information, two methods were tested:

Sentence Classification: fine-tuned BERT model for sentence-level relevance detection

Information Retrieval: embedding-based retrieval using all-MiniLM-L6-v2
