from PyPDF2 import PdfFileWriter, PdfFileReader
import pdfplumber
import os
from typing import Tuple
import fitz
import base64
import os

def get_final_range(pdffile: str) -> Tuple[int, int]:
    '''
    This function is used to get lower and upper range values.
    
    Parameters
    pdffile:uploded pdf file.
    
    Returns
    table page range
    '''
    reader = PdfFileReader(pdffile)
    end_range = reader.numPages
    middle = end_range//2
    lst = []
    list_pages = []
    with pdfplumber.open(pdffile) as pdf:
        first_page = pdf.pages[middle]
        list_pages.append(first_page.extract_text())
        second = pdf.pages[middle+1]
        list_pages.append(second.extract_text())
        third = pdf.pages[middle-1]
        list_pages.append(third.extract_text())
    common = os.path.commonprefix(list_pages)
    print("common :", common)
    words=' '.join(common.split()[:2])
    doc = fitz.open(pdffile)
    for page in doc:
        text = ''
        text += page.get_text()
        search_match = all(map(lambda w: w in text, (common.split())))
        if search_match == True:
            lst.append( page.number + 1,)
    min_rng=min(lst)
    max_rng=max(lst)
    return(min_rng,max_rng)

def create_download_link(val: str, filename: str) -> str:
    """
    This method creates the hyperlink to download JSON and Excel File.

    Parameters:
        val: file from local directory which is read in binary format. 
        file_name: name of the file.
      
    Returns:
        download_link named as Download Excel & Download Json.
    """

    with open(val, 'rb') as f:
        b64 = base64.b64encode(f.read())  # val looks like b'...'
        if "xlsx" in filename: 
            return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}">Download Excel</a>'
        else:
            return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}">Download Json</a>'


def split_pdf_using_range(pdf,start_rang,end_range):
    pdffile_name = pdf.replace('.pdf', '')
    output = PdfFileWriter()
    for i in range(start_rang, end_range):
        output.addPage(PdfFileReader(pdf).getPage(i))

    with open(pdffile_name +"_split.pdf", "wb") as output_stream:
        output.write(output_stream)
    return(pdffile_name +"_split.pdf")