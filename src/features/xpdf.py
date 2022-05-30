import fitz
import shutil
import os
from PyPDF2 import PdfFileWriter, PdfFileReader
import os
import warnings
warnings.filterwarnings('ignore')

#code for splitting pdf use incase required
def split_vertical(file):

    file = file
    file_name = file.replace(".pdf","")
    with open(file, "rb") as in_f:
        input1 = PdfFileReader(in_f)
        output = PdfFileWriter()

        numPages = input1.getNumPages()

        for i in range(numPages):
            page = input1.getPage(i)
            page.cropBox.lowerLeft = (0, 50)
            page.cropBox.upperRight = (306, 792)
            output.addPage(page)

        with open(file+'_left.pdf', "wb") as out_f:
            output.write(out_f)

    #split right
    with open(file, "rb") as in_f:
        input1 = PdfFileReader(in_f)
        output = PdfFileWriter()

        numPages = input1.getNumPages()

        for i in range(numPages):
            page = input1.getPage(i)
            page.cropBox.lowerLeft = (306, 50)
            page.cropBox.upperRight = (612, 792)
            output.addPage(page)

        with open(file+'_right.pdf', "wb") as out_f:
            output.write(out_f)

    #combine splitted files
    input1 = PdfFileReader(open(file+'_left.pdf',"rb"))
    input2 = PdfFileReader(open(file+'_right.pdf',"rb"))
    output = PdfFileWriter()
    numPages = input1.getNumPages()

    for i in range(numPages):
        l = input1.getPage(i)
        output.addPage(l)
        r = input2.getPage(i)
        output.addPage(r)

    with open(file_name+'_out.pdf', "wb") as out_f:
        output.write(out_f)
    return(file_name+'_out.pdf')

def pdf_cut(file_n):
    path = os.path.abspath("..\data\Xpdf_out")
    print(path)
    inputpdf = PdfFileReader(open(file_n, "rb"))
    for i in range(inputpdf.numPages):
        output = PdfFileWriter()
        output.addPage(inputpdf.getPage(i))
        with open(path+'\\'+'file'+"_page_%s.pdf" % i, "wb") as outputStream:
            output.write(outputStream)

def pdftotext():
    original = os.getcwd()    
    dir_name = os.path.abspath("..\data\Xpdf_out")
    os.chdir(dir_name)   # provide path where pdf and exe is available
    # Get list of all files in a given directory sorted by name
    list_of_files = sorted(filter( lambda x: os.path.isfile(os.path.join(dir_name, x)),
                            os.listdir(dir_name) ) )
    # file_list =[]
    for file_name in list_of_files:
        print(file_name)
        # file_list.append(file_name)
        # file_name=file_name.replace(" ", "_")
        # print(file_name)
        command = "pdftotext -layout -table "+str(file_name)
        type(command)
        print(command)
        os.system(command)
    os.chdir(original)

def clear_pdftotext():
    test = os.listdir(os.path.abspath("..\data\Xpdf_out"))
    dir_name = os.path.abspath("..\data\Xpdf_out")
    for item in test:
        if item.endswith(".pdf"):
            os.remove(os.path.join(dir_name, item))
        if item.endswith(".txt"):
            os.remove(os.path.join(dir_name, item))    