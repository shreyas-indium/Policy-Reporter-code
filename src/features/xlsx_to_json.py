import pandas as pd
import numpy as np
import json
from openpyxl import load_workbook
import re
import pdfplumber

list_json = []
record_exel = 'features/record.xlsx'



def version(pdf_file):
    """
    generating the version field from the first page of the PDF file if it exists.

    Parameters:
    pdf_file: uploaded PDF file.

    Returns:
     returns version from the first page of the PDF.
    """

    pdf = pdfplumber.open(pdf_file)
    page = pdf.pages[0]
    text = page.extract_text()
    pdf.close()
    #replace , to space
    df=text.replace(',', '')
    
    regex = re.findall(r'([0-9]*) Version Number ([0-9]*)',df)
    if(len(regex) == 0):
        regex = re.findall(r'([0-9]*) Version ([0-9]*)',df)
    if(len(regex) != 0): 
        result = str(regex[0][0])+" Version " +str(regex[0][1])
    else:
        result = ""
    return result


def record(rec_exel):
    """
    creating a record excel file and assigning a unique id to each PDF.

    Parameters:
    rec_exel: record file maintianing unique if for each uploaded PDF.

    Returns:
     returns unique id for each PDF file uploaded.
    """

    df_record = pd.read_excel(rec_exel, engine='openpyxl')
    unq_id = df_record['unique_id'].iloc[-1] + 1
    return unq_id


def uniquid(file_name,unq_id,result):
    """
    assigning unique id's to each PDF file.

    Parameters:
    file_name: uploaded PDF file.
    unq_id: unique id for the PDF file.
    result: list of row entry for record file.
    """
    
    new_row_data = [[file_name,unq_id,result]]
    wb = load_workbook(record_exel)
    ws = wb.worksheets[0]
    for row_data in new_row_data:
        ws.append(row_data)
    wb.save(record_exel)
    

def json_body(enc_file,start_rang):
    """
    this method is used to align the keys in JSON structure as per the mentioned format.

    Parameters:
    enc_file: output file from table_encoding.
    """

    #input file
    sheets_dict = pd.read_excel(enc_file, index_col=0, sheet_name = None, engine='openpyxl')
    for name, sheet in sheets_dict.items():
        df = pd.read_excel(enc_file, index_col=0, sheet_name= name, engine='openpyxl')
        df['Branded'] = np.where(df['drugname'].str.isupper(), 1, 0)
        print("name :", name)

        list_page = [int(re.search(r'\d+', name).group())+start_rang] * df.shape[0]
        print('list_page ',list_page)
        df2 = df.assign(PageNumber = list_page, Preferred = 0, medicalbenefit = 0)
        df2.rename(columns = {df2.columns[1]:'Tier','Category':'product category','Subcategory':'product subcategory',
                              'Line':'LineNumber',df2.columns[2]:'Requirements & Limits unparsed'}, inplace = True)
        df2['LineNumber'] = df2['LineNumber']+1
        df2 = df2[['drugname','form','Dosage','drug-unparsed','Tier','Requirements & Limits unparsed','Branded',
                   'product category','product subcategory','Preferred','medicalbenefit','mailorder',
                   'priorauthorization','specialty','quantitylimit','steptherapy','PageNumber','LineNumber']]
        json_records = df2.to_json(orient ='records', date_format='iso')
        parsed = json.loads(json_records)
        list_json.append(parsed)
        
    

def json_header(enc_file, record_exel, file_name, pdf_file, output_json, start_rang):
    """
    to create the JSON keys shared by the entire file.

    Parameters:
    enc_file: output file from table_encoding.
    record_exel: record file maintianing unique if for each uploaded PDF.
    file_name: uploaded PDF file name.
    pdf_file: uploaded PDF file
    output_json: name of output JSON file.
    """
    
    unq_id =''
    json_body(enc_file,start_rang)
    result = version(pdf_file)
    
    df_new = pd.read_excel('features/record.xlsx', engine='openpyxl')
    for index, row in df_new.iterrows():
        # print(row['File'], row['unique_id'])
        if file_name == str(row['File']):
            unq_id = str(row['unique_id'])
            
    df_new = pd.read_excel('features/record.xlsx', engine='openpyxl')
    # file_name = '2021_EGWP_Formulary_cab'
    a1 = str(df_new['File'])
    # print(type(a1))
    if file_name not in a1:
        unq_id = record(record_exel) 
        uniquid(file_name,unq_id,result)
    
    data = {}
    data['Formulary Name'] = file_name
    data['Doc id'] = str(unq_id)
    data['Asset_revision_id '] = 0
    data['FormularyID'] = str(result)
    data['Preferred Tiers'] = {
      "Generic": "Tier 1, PG",
      "Brand": ""
    }
    data["formularydrug"] = list_json

    with open(output_json, "w") as json_file:
        json_file.write(json.dumps({"data": data}, indent=4 ))
        print(output_json,'file executed successfully')

    
