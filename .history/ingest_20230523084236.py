import os
import re
from dotenv import load_dotenv
from typing import Tuple, List, Dict, Callable
import PyPDF4
import pdfplumber

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma


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


def clean_text(
        pages, cleaning_functions: List[Callable[[str],str]]
) -> List[Tuple[int, str]]:
    cleaned_pages = []
    for page_num, text in pages:
        for cleaning_function in cleaning_functions:
            text = cleaning_function(text)
        cleaned_pages.append((page_num, text))
    return cleaned_pages


def merge_hyphenated_words(text:str) -> str:
    return re.sub(r"(\w)-\n(\w)", r"\1\2", text)

def fix_newlines(text:str) -> str:
    return re.sub(r"(?<!\n)\n(?!\n)", " ", text)

def remove_multiple_newlines(text:str) -> str:
    return re.sub(r"\n{2,}", "\n", text)

def text_to_docs(
        text: List[Tuple[int, str]], metadata: Dict[str, str]
    ) -> List[Document]:
    """
    Converts list of strings to a list of Documents with metadata.
    """
    doc_chunks = []

    for page_num, page in text:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", "","？", "！", "。", "，"],
            chunk_overlap = 200,
        )
        chunks = text_splitter.split_text(page)

        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "page_number": page_num,
                    "chunk": i,
                    "source": f"p{page_num}-{i}",
                    **metadata,
                }
            )
            doc_chunks.append(doc)
    
    return doc_chunks



if __name__ == '__main__':
    load_dotenv()   

    # step1 : parse the PDF
    file_path = './《走过天涯还有路》场记本巡演版.pdf'
    raw_pages, metadata = parse_pdf(file_path)

    # step2 : create text chuncks
    cleaning_functions = [
        merge_hyphenated_words,
        fix_newlines,
        remove_multiple_newlines,
    ]

    cleaned_text_pdf = clean_text(raw_pages, cleaning_functions)
    document_chuncks = text_to_docs(cleaned_text_pdf, metadata)

    # Optional: Reduce embedding cost by only using the first 70 chuncks
    document_chuncks = document_chuncks[:70]

    # step3+4 : Generate embedding and store them in DB
    embedding = OpenAIEmbeddings()

    vector_store = Chroma.from_documents(
        documents=document_chuncks,
        embedding=embedding,
        collection_name="走过天涯剧本",
        persist_directory="/Users/kissshot/data/chroma",
    )

    # Save DB to hard drive
    vector_store.persist()

