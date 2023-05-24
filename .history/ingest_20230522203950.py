import os
from dotenv import load_dotenv
from typing import Tuple, List, Dict
import PyPDF4
import pdfplumber


def parse_pdf(file_path: str) -> Tuple[List[Tuple[int, str]], Dict[str, str]]:
    """
    Extract the title and text from each page of the PDF.

    :param file_path: 
    :return: A tuple ( [(pagenum, raw_text)...], [metadata, metadata])
    """

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    pages = extract_pages_from_pdf(file_path)
    metadata = extract_metadata_from_pdf(file_path)
    
    return pages, metadata


def extract_metadata_from_pdf(file_path: str) -> dict:
    with open(file_path, 'rb') as pdf_file:
        reader = PyPDF4.PdfFileReader(pdf_file)
        metadata = reader.getDocumentInfo()
        return {
            "title": metadata.get("/Title","").strip(),
            "author": metadata.get("/Author", "").strip(),
            "creation_date": metadata.get("/CreationDate", "").strip(),
        }


def extract_pages_from_pdf(file_path: str) -> List[Tuple[int, str]]:
    """
    Extract the text from each page of the PDF.

    :param file_path: 
    :return: list[(pagenum, text),,,,]
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with pdfplumber.open(file_path) as pdf:
        pages = []
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text.strip(): # Check if extracted text is not empty
                pages.append((page_num+1, text))
    return pages



if __name__ == '__main__':
    load_dotenv()   

    # step1 : parse the PDF
    file_path = './《走过天涯还有路》场记本巡演版.pdf'
    raw_pages, metadata = parse_pdf(file_path)

    print(raw_pages)
    print(metadata)