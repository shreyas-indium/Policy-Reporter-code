import camelot
from PyPDF2 import PdfFileReader, PdfFileWriter
import pandas as pd
import os
import openpyxl
import re
import fitz
from tabula import read_pdf,read_pdf_with_template


def extract_data(inputpdf,output, start_rang, end_range, f_name):

    file_name = f_name
    print("filename :", file_name)
    # all pages same width and height, so this is done only once
    input1 = PdfFileReader(open(inputpdf, 'rb'))
    width, height = input1.getPage(0).mediaBox[2], input1.getPage(0).mediaBox[3]

    for page_number in range(start_rang,end_range):

        tables = camelot.read_pdf(inputpdf,
                                  table_regions=['30,' + str(height) + ',' + str(int(width / 2)) + ',' + str(height - 730)],
                                  flavor='lattice', pages=str(page_number), line_scale=40)

# os.path.abspath("../data/raw/"+str(docx_file.name))
        print("Path ..", os.path.abspath("../data/raw/pdf_pages/page") + str(page_number) + '_table_1.xlsx')
        tables.export(
            os.path.abspath("../data/raw/pdf_pages/page"+ str(page_number) + '_table_1.xlsx'),
            f='excel', compress=False)

        if page_number!=98: # final page has only one table
            tables = camelot.read_pdf(inputpdf,
                                      table_regions=[str(int(width / 2)) + ',' + str(height) + ',' + str(int(width)-30) + ','+str(height-730)],
                                      flavor='lattice', pages=str(page_number), line_scale=40)

            tables.export(
                os.path.abspath("../data/raw/pdf_pages/page" + str(page_number) + '_table_2.xlsx'),
                f='excel', compress=False)

    ##################################################################################
    #combine all the excels into a single file
    output_xl_name = os.path.abspath("../data/raw/{}.xlsx".format(file_name))

    with pd.ExcelWriter(output_xl_name) as writer:
        for page_file_name in sorted(os.listdir(os.path.abspath("../data/raw/pdf_pages")), key=lambda x: int(x.split('_')[0][4:])):

            print('file_name',page_file_name)

            contents = pd.read_excel(os.path.abspath("../data/raw/pdf_pages/"+page_file_name)).drop('Unnamed: 0', 1)

            df = contents

            df = df.dropna(how='all', axis=0)

            df = df.dropna(how='all', axis=1)

            # print('columns',df.columns)

            for row_index,row in df.iterrows():
                #print('row',row)
                if str(df.loc[row_index,df.columns[0]]).startswith('Drug Name'):

                    if len(df.columns)==2:
                        df['2'] = ['']*len(df)

                    df.loc[row_index,df.columns[0]] = 'Drug Name'
                    df.loc[row_index,df.columns[1]] = 'Tier'
                    df.loc[row_index,df.columns[2]] = 'Notes'

                if (not '*' in str(df.loc[row_index,df.columns[0]])) and \
                        (pd.isna(df.loc[row_index,df.columns[1]])) and (pd.isna(df.loc[row_index,df.columns[2]])):
                    lines = str(df.loc[row_index,df.columns[0]]).splitlines()
                    print('lines',lines)
                    df.loc[row_index, df.columns[0]] = lines[0]
                    if len(lines) > 1:
                        df.loc[row_index, df.columns[1]] = lines[1]
                    if len(lines)>2:
                        df.loc[row_index, df.columns[2]] = lines[2]


            df.to_excel(writer,sheet_name=page_file_name.replace('.xlsx',''),index=False,header=False)

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