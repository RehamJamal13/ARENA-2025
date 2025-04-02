import os
import csv
import xml.etree.ElementTree as ET
import requests
from tqdm import tqdm

# Configuration
PDF_DIR = "/Users/rehamjamal/Desktop/ARENA 2025/papers"
OUTPUT_DIR = "/Users/rehamjamal/Desktop/ARENA 2025/extracted_text"
CSV_FILE = os.path.join(OUTPUT_DIR, "extracted_data_full.csv")
GROBID_URL = "http://localhost:8070/api/processFulltextDocument"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_text_from_pdf(pdf_path, retries=3):
    """Extract XML from PDF using GROBID"""
    for attempt in range(retries):
        try:
            with open(pdf_path, 'rb') as f:
                response = requests.post(
                    GROBID_URL,
                    files={'input': f},
                    params={
                        'consolidateHeader': '1',
                        'consolidateCitations': '1',
                        'includeRawAffiliations': '1'
                    },
                    timeout=120
                )
                if response.status_code == 200:
                    return response.text
        except Exception:
            time.sleep(5)
    return None

def parse_paper_content(xml_text):
    """Parse all paper components from GROBID XML"""
    try:
        root = ET.fromstring(xml_text)
        ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
        
        # Extract metadata
        title = root.findtext('.//tei:titleStmt/tei:title', namespaces=ns, default="No title")
        
        # Extract authors
        authors = []
        for author in root.findall('.//tei:sourceDesc//tei:author', ns):
            pers_name = author.find('.//tei:persName', ns)
            if pers_name is not None:
                first = pers_name.findtext('tei:forename', namespaces=ns, default="")
                last = pers_name.findtext('tei:surname', namespaces=ns, default="")
                authors.append(f"{first} {last}".strip())
        
        # Extract abstract
        abstract = "\n".join(
            p.text for p in root.findall('.//tei:profileDesc/tei:abstract//tei:p', ns)
        ) or "No abstract"
        
        # Extract sections
        sections = []
        for div in root.findall('.//tei:text//tei:body//tei:div', ns):
            section_title = div.findtext('tei:head', namespaces=ns, default="Untitled Section")
            section_content = "\n".join(
                p.text for p in div.findall('.//tei:p', ns) if p.text
            )
            sections.append(f"{section_title}: {section_content}")
        
        # Extract references
        references = []
        for ref in root.findall('.//tei:text//tei:listBibl//tei:biblStruct', ns):
            ref_title = ref.findtext('.//tei:title', namespaces=ns, default="No title")
            ref_authors = []
            for author in ref.findall('.//tei:author', ns):
                first = author.findtext('tei:forename', namespaces=ns, default="")
                last = author.findtext('tei:surname', namespaces=ns, default="")
                ref_authors.append(f"{first} {last}".strip())
            ref_date = ref.findtext('.//tei:date', namespaces=ns, default="")
            references.append({
                'title': ref_title,
                'authors': ", ".join(ref_authors),
                'date': ref_date
            })
        
        return {
            'title': title,
            'authors': "; ".join(authors),
            'abstract': abstract,
            'sections': " | ".join(sections),
            'references': " || ".join(
                f"{ref['title']} ({ref['authors']}, {ref['date']})" 
                for ref in references
            )
        }
    except ET.ParseError:
        return None

def process_pdfs_to_csv():
    """Process all PDFs and save to CSV"""
    pdf_files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith('.pdf')]
    
    with open(CSV_FILE, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[
            'title', 'authors', 'abstract', 'sections', 'references'
        ])
        writer.writeheader()
        
        for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
            pdf_path = os.path.join(PDF_DIR, pdf_file)
            xml_content = extract_text_from_pdf(pdf_path)
            
            if xml_content:
                paper_data = parse_paper_content(xml_content)
                if paper_data:
                    writer.writerow(paper_data)
                else:
                    print(f"Failed to parse: {pdf_file}")
            else:
                print(f"Failed to extract: {pdf_file}")

if __name__ == "__main__":
    process_pdfs_to_csv()
    print(f"\nExtraction complete! Data saved to: {CSV_FILE}")