import pikepdf
from PyPDF2 import PdfFileWriter, PdfFileReader

def check_encryption(filename):
    pdf_reader = PdfFileReader(open(filename, "rb"))
    if pdf_reader.isEncrypted:
        return(True)
    else:
        return(False)

def decrypt_pdf(filename):
    pdf_reader = PdfFileReader(open(filename, "rb"))
    if pdf_reader.isEncrypted:
        name = filename.replace('.pdf','')
        pdf = pikepdf.open(filename)
        pdf.save(name+'_decrypted.pdf')
        print('file decrypted')
        return(name+'_decrypted.pdf')