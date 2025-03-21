import os
import requests
import xml.etree.ElementTree as ET
import time

# Step 1: Define the GROBID API endpoint (use local Docker)
GROBID_URL = "http://localhost:8070/api/processFulltextDocument"

# Step 2: Define input and output directories
PDF_DIR = "/Users/rehamjamal/Desktop/ARENA 2025/papers"
OUTPUT_DIR = "/Users/rehamjamal/Desktop/ARENA 2025/extracted_text"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Step 3: Function to extract text from PDF
def extract_text_from_pdf(pdf_path, retries=3):
    with open(pdf_path, 'rb') as f:
        files = {'input': f}
        for attempt in range(retries):
            try:
                response = requests.post(GROBID_URL, files=files, timeout=300)  # Increase timeout to 300 seconds (5 minutes)
                if response.status_code == 200:
                    # Save raw XML output for debugging
                    with open("grobid_output.xml", "w", encoding="utf-8") as xml_file:
                        xml_file.write(response.text)
                    return response.text
                else:
                    print(f"Attempt {attempt + 1}: Failed to extract text from {pdf_path}. Status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1}: Error extracting text from {pdf_path}: {e}")
            time.sleep(5)  # Wait 5 seconds before retrying
        return None

# Step 4: Function to parse title and abstract
def parse_grobid_output(xml_text):
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

# Step 5: Process PDFs
for pdf_file in os.listdir(PDF_DIR):
    if pdf_file.endswith(".pdf"):
        pdf_path = os.path.join(PDF_DIR, pdf_file)
        print(f"Processing: {pdf_file}")

        extracted_text = extract_text_from_pdf(pdf_path)
        if extracted_text:
            title, abstract = parse_grobid_output(extracted_text)

            # Save to output file
            output_file = os.path.join(OUTPUT_DIR, f"{os.path.splitext(pdf_file)[0]}.txt")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Title: {title}\n\n")
                f.write(f"Abstract: {abstract}\n")
            print(f"Extracted title and abstract saved to: {output_file}")