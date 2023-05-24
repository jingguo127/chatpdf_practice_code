from dotenv import load_dotenv
from typing import Tuple, List, Dict


def parse_pdf(file_path: str) -> Tuple[List[Tuple[int, str]], Dict[str, str]]:
    return file_path+1



if __name__ == '__main__':
    load_dotenv()   

    # step1 : parse the PDF
    file_path = './《走过天涯还有路》场记本巡演版.pdf'
    # raw_pages, metadata = parse_pdf(file_path)


    print(parse_pdf(2))