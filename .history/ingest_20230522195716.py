import os
from dotenv import load_dotenv
from typing import Tuple, List, Dict
import PyPDF4


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


if __name__ == '__main__':
    load_dotenv()   

    # step1 : parse the PDF
    file_path = './《走过天涯还有路》场记本巡演版.pdf'
    # raw_pages, metadata = parse_pdf(file_path)


    print(parse_pdf(2))