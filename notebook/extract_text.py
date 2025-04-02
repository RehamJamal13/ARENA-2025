import os
import requests
import xml.etree.ElementTree as ET
import time
from tqdm import tqdm  # For progress bars (pip install tqdm)

# Configuration
GROBID_URL = "http://localhost:8070/api/processFulltextDocument"
PDF_DIR = "/Users/rehamjamal/Desktop/ARENA 2025/papers"
OUTPUT_DIR = "/Users/rehamjamal/Desktop/ARENA 2025/extracted_text"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_text_from_pdf(pdf_path, retries=3):
    """Send PDF to GROBID and return XML with retries"""
    for attempt in range(retries):
        try:
            with open(pdf_path, 'rb') as f:
                response = requests.post(
                    GROBID_URL,
                    files={'input': f},
                    params={
                        'consolidateHeader': '1',
                        'consolidateCitations': '1',
                        'includeRawCitations': '1',
                        'includeRawAffiliations': '1',
                        'teiCoordinates': '1'
                    },
                    timeout=120
                )
                if response.status_code == 200:
                    return response.text
                print(f"Attempt {attempt+1}: Status {response.status_code}")
        except Exception as e:
            print(f"Attempt {attempt+1}: {str(e)}")
        time.sleep(5)
    return None

def parse_full_paper(xml_text):
    """Extract structured content from GROBID XML"""
    try:
        root = ET.fromstring(xml_text)
        ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
        paper = {
            'title': root.findtext('.//tei:titleStmt/tei:title', namespaces=ns, default="No title"),
            'authors': [],
            'abstract': "",
            'sections': [],
            'references': []
        }

        # Authors
        for author in root.findall('.//tei:sourceDesc//tei:author', ns):
            name = author.find('.//tei:persName', ns)
            if name is not None:
                first = name.findtext('tei:forename', namespaces=ns, default="")
                last = name.findtext('tei:surname', namespaces=ns, default="")
                paper['authors'].append(f"{first} {last}".strip())

        # Abstract
        paper['abstract'] = "\n".join(
            p.text for p in root.findall('.//tei:profileDesc/tei:abstract//tei:p', ns)
        ) or "No abstract"

        # Sections
        for div in root.findall('.//tei:text//tei:body//tei:div', ns):
            paper['sections'].append({
                'title': div.findtext('tei:head', namespaces=ns, default="Untitled"),
                'content': "\n".join(p.text for p in div.findall('.//tei:p', ns))
            })

        # References
        for ref in root.findall('.//tei:text//tei:listBibl//tei:biblStruct', ns):
            paper['references'].append({
                'title': ref.findtext('.//tei:title', namespaces=ns, default="No title"),
                'authors': [f"{a.findtext('tei:forename', default='')} {a.findtext('tei:surname', default='')}".strip()
                           for a in ref.findall('.//tei:author', ns)],
                'date': ref.findtext('.//tei:date', namespaces=ns, default="")
            })

        return paper
    except ET.ParseError as e:
        print(f"XML Parsing Error: {e}")
        return None

def save_paper_content(content, output_path):
    """Save extracted content to a structured text file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        # Header
        f.write(f"{'='*80}\nTITLE: {content['title']}\n{'='*80}\n\n")
        
        # Authors
        f.write("AUTHORS:\n" + "\n".join(f"- {a}" for a in content['authors']) + "\n\n")
        
        # Abstract
        f.write(f"ABSTRACT:\n{content['abstract']}\n\n")
        
        # Sections
        f.write(f"{'='*80}\nPAPER CONTENT:\n{'='*80}\n\n")
        for sec in content['sections']:
            f.write(f"## {sec['title']} ##\n{sec['content']}\n\n")
        
        # References
        f.write(f"{'='*80}\nREFERENCES:\n{'='*80}\n")
        for i, ref in enumerate(content['references'], 1):
            f.write(f"{i}. {ref['title']}\n")
            if ref['authors']:
                f.write(f"   Authors: {', '.join(ref['authors'])}\n")
            if ref['date']:
                f.write(f"   Date: {ref['date']}\n")
            f.write("\n")

def process_pdfs():
    """Process all PDFs in the input directory"""
    pdf_files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith('.pdf')]
    for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
        pdf_path = os.path.join(PDF_DIR, pdf_file)
        xml_content = extract_text_from_pdf(pdf_path)
        
        if not xml_content:
            print(f"\nFailed to process: {pdf_file}")
            continue
            
        paper_data = parse_full_paper(xml_content)
        if not paper_data:
            print(f"\nFailed to parse XML for: {pdf_file}")
            continue
            
        output_path = os.path.join(OUTPUT_DIR, f"{os.path.splitext(pdf_file)[0]}.txt")
        save_paper_content(paper_data, output_path)

if __name__ == "__main__":
    process_pdfs()
    print("\nExtraction complete!")