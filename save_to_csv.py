import os
import csv

# Define input and output directories
PDF_DIR = "/Users/rehamjamal/Desktop/ARENA 2025/papers"
OUTPUT_DIR = "/Users/rehamjamal/Desktop/ARENA 2025/extracted_text"
CSV_FILE = os.path.join(OUTPUT_DIR, "extracted_data.csv")

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Function to parse GROBID output (replace this with your actual function)
def parse_grobid_output(xml_text):
    import xml.etree.ElementTree as ET
    root = ET.fromstring(xml_text)
    namespace = {'tei': 'http://www.tei-c.org/ns/1.0'}

    # Extract title
    title = root.find('.//tei:titleStmt/tei:title', namespace)
    title_text = title.text if title is not None else "No title found"

    # Extract abstract
    abstract = root.find('.//tei:profileDesc/tei:abstract', namespace)
    abstract_text = ""
    if abstract is not None:
        for p in abstract.findall('.//tei:p', namespace):
            abstract_text += p.text + "\n"
    else:
        abstract_text = "No abstract found"

    return title_text, abstract_text.strip()

# Function to extract text from PDF (replace this with your actual function)
def extract_text_from_pdf(pdf_path):
    import requests
    GROBID_URL = "http://localhost:8070/api/processFulltextDocument"
    with open(pdf_path, 'rb') as f:
        files = {'input': f}
        response = requests.post(GROBID_URL, files=files, timeout=300)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to extract text from {pdf_path}")
        return None

# Save extracted data to a CSV file
with open(CSV_FILE, "w", encoding="utf-8", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Title", "Abstract"])  # Write header (without authors)

    # Process each PDF in the input directory
    for pdf_file in os.listdir(PDF_DIR):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(PDF_DIR, pdf_file)
            print(f"Processing: {pdf_file}")

            extracted_text = extract_text_from_pdf(pdf_path)
            if extracted_text:
                title, abstract = parse_grobid_output(extracted_text)
                writer.writerow([title, abstract])  # Write row to CSV (without authors)

print(f"Extracted data saved to: {CSV_FILE}")