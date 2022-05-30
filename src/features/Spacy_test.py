from tabula import read_pdf,read_pdf_with_template
from PyPDF2 import PdfFileReader
import warnings
import pandas as pd
import numpy as np
warnings.filterwarnings('ignore')
import os
import spacy
import pandas as pd
import re


def dosages(df, nlp_dose):
    """
    This function is used to seperate the dosage from drug name using spacy model.
    Parameters:
    df: dataframe from excel.
    nlp_dose: trained spacy model for seperating dosage.

    Returns
    it returns dosage form keywords.
    """
    
    dosages = []
    # print("df in dosages", df.info())
    for i in df[df.columns[6]]: # mention col drug name
        i = str(i).replace(';_x000D_',' ~ ')
        i = i.replace('_x000D_',' ')
        i = i.replace(';',' ~ ')
        i = i.replace('(','')
        i = i.replace(')','')
        i = i.replace(' ML','ML')
        i = i.replace(' ml','ml')
        i = i.replace(' GM','GM')
        i = i.replace(' gm','GM')
        entity = ''
        for j in i.split('~'):
            docx = nlp_dose(j)
            for ent in docx.ents:
                entity += str(ent)+','        
        dosages.append(str(entity)[:-1])
    return dosages

def get_file_len(input_file):
    """
    This function is used to return the number of pages in the file.
    Parameters:
    input_file: upploaded PDF file. 
    
    Returns
    return the number of pages in the file.
    """

    xl = pd.ExcelFile(input_file, engine='openpyxl')
    res = len(xl.sheet_names)
    return res


def gen_excel(input_file, output_file, nlp_dose):
    """
    This function is used to write the data seperated by the model in excel file.

    Parameters:
    input_file: is output of extract_data function,
    output_file: is the name we are providing for the file which is updated with dosage column,
    nlp_dose: loading the model-best from the trained model. 
    """    

    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
    table_len = get_file_len(input_file)  
    print("table_len", table_len)
    for k in range(0,table_len): # get 110 using next cell or items()
    # for k in range(0,4): # get sample
        print(k)
        df =  pd.read_excel(input_file,sheet_name=k, engine='openpyxl')
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        dosage = dosages(df, nlp_dose)
        df['Dosage'] = dosage
            # def dosage_form(df):
        drug_drug_form = []
        for i in range(0,df.shape[0]):
            string = str(df['drugname'].iloc[i]).replace(';_x000D_','; ')
            pattern = r'\[[^\]]*\]'
            string = re.sub(pattern, '', string)
            string = string.replace('_x000D_',' ')
            string = string.replace('(',' ')
            string = string.replace(')',' ')
            string = string.replace(' ML','ML')
            string = string.replace(' ml','ml')
            string = string.replace(' GM','GM')
            string = string.replace(' gm','GM')

            if df.iloc[i].isna()['Dosage'] != True:
                dosage = df['Dosage'].iloc[i]
                dosage = dosage.replace('+','')
                dosage = dosage.replace(',,',',')
                string = string.replace(',',' ')
                string = re.sub('[0-9#]','',string)
                for j in dosage.split():
                    j = j.replace('[','')
                    j = j.replace(']','')
                    string = re.sub(j,'',string)

            string = re.sub('mg/ml|gm/ml|MG/ML|GM/ML|%','',string)
            drug_drug_form.append(string)


        df['drugname'] = drug_drug_form

        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df.to_excel(writer, sheet_name='Table'+str(k))
    writer.save()
