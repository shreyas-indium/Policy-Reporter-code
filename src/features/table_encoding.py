import pandas as pd
import numpy as np
import re


def encoding(inputf,outputf):
    """
    encoding function separates each element in requirements/limits 
    column into a new column showcasing 0 and 1 where those values are present.

    Parameters:
    inputf: model seperated input file. 
    outputf: excel output file name
    """
    
    #output
    writer = pd.ExcelWriter(outputf, engine='xlsxwriter')

    # #input file
    sheets_dict = pd.read_excel(inputf, index_col=0, sheet_name = None, engine='openpyxl')

    all_sheets = []

    for name, sheet in sheets_dict.items():
        df = pd.read_excel(inputf, index_col=0, sheet_name = name, engine='openpyxl')
        
        for index, row in df.iterrows():
            row_drug = row['drugname']
            row_unpar = row['drug-unparsed']
            row_unpar = str(row_unpar)
            if re.findall('\((.*?)\)',row_unpar):
                transcript = re.findall('\((.*?)\)',row_unpar)[0]
            else:
                transcript = "" 
            row_drug = str(row_drug)            
            row_drug = row_drug.replace(transcript, '') #re.findall('\((.*?)\)',row_unpar)[0]  
            df.at[index,'drugname'] = row_drug
            
        df['dummy'] = df[df.columns[2]]
        df['dummy'].replace("PPACA",0 ,inplace=True)
        df['dummy'] = df['dummy'].fillna('')
        df['dummy'] = [re.sub("[\(\[].*?[\)\]]","", str(x)) for x in df['dummy']]
        df['priorauthorization'] = np.where(df['dummy'].astype(str).str.contains("PA|STPA|PA BvD|PA NSO"), 1, 0)
        df['quantitylimit'] = np.where(df['dummy'].astype(str).str.contains("QL"), 1, 0)
        df['steptherapy'] = np.where(df['dummy'].astype(str).str.contains("ST|STPA"), 1, 0)
        df['specialty'] = np.where(df['dummy'].astype(str).str.contains("SP|SPRx|SP-CVS"), 1, 0)
        df['mailorder'] = np.where(df['dummy'].astype(str).str.contains("RM|MAIL"), 1, 0)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df = df.drop(['dummy'], axis = 1)
        df.to_excel(writer, sheet_name= name)

    writer.save()
