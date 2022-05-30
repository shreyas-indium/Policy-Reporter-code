import camelot
from PyPDF2 import PdfFileReader, PdfFileWriter
import pandas as pd
import os
import openpyxl
import fitz


def extract_data(inputpdf,outputxl, start_rang, end_range):
    """
    The function extract_data extracts the tables data from PDF files including category & subcategory

    Parameters:
    inputpdf: is the pdf file you have uploaded on the web interface,
    outputxl: is the name we are providing for our extracted excel file,
    page_range: is specific pages of a PDF having tables. 

    """
    # all pages same width and height, so this is done only once
    input1 = PdfFileReader(open(inputpdf, 'rb'))
    width, height = input1.getPage(0).mediaBox[2], input1.getPage(0).mediaBox[3]


    for page_number in range(start_rang, end_range):
        tables = camelot.read_pdf(inputpdf,
                                  flavor='lattice',pages=str(page_number), line_scale=40)

        tables.export('../data/processed/page' + str(page_number) + '_table_1.xlsx', f='excel', compress=False)


    ##################################################################################
    #combine all the excels into a single file
    output_xl_name = outputxl

    with pd.ExcelWriter(output_xl_name) as writer:
        for page_file_name in sorted(os.listdir('../data/processed'), key=lambda x: int(x.split('_')[0][4:])):
            contents = pd.read_excel('../data/processed/'+page_file_name).drop('Unnamed: 0', 1)
            df = contents
            df[0][0] = 'Drug Name'
            df[1][0] = 'Drug Tier'
            df[2][0] = 'Limits'
            df.to_excel(writer,sheet_name=page_file_name.replace('.xls',''),index=False,header=False)

    # auto adjust column width of xl file
    wb = openpyxl.load_workbook(filename=output_xl_name)

    for worksheet in wb.worksheets:
        for col in worksheet.columns:
            max_length = 0
            column = col[0].column_letter  # Get the column name
            for cell in col:
                try:  # Necessary to avoid error on empty cells
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            worksheet.column_dimensions[column].width = adjusted_width

    wb.save(output_xl_name)