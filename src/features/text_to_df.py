import numpy as np
import pandas as pd
import re 
from collections import Counter
import shutil
import glob
import os


def create_df(pdf_name):

    ind = 1
    import re
    re_to_pdf=re.sub('.pdf','',pdf_name)
    file_name = re_to_pdf
    with pd.ExcelWriter(os.path.abspath("../data/raw/{}.xlsx".format(file_name))) as writer:

        for filename in glob.glob(os.path.abspath("../data/Xpdf_out/*.txt")):
            print('in loop',file_name)


            file1 = open(filename,"r+") 
            list_index = []
            import re
            for i in file1.readlines():
                list_line = (re.split(r'\s{2,}', i))
                for elem in list_line:
                    list_index.append(i.index(elem))


            var = Counter(list_index)
            print(var)


            with open('somefile.txt', 'w') as the_file:
                file1 = open(filename,"r+") 
                for i in file1.readlines():
                    text = i
                    for key in var.keys():
                        if(len(text)>key):
                            if ((text[key] == " " and text[key-1] == " ") or (text[key] == " " and text[key+1] == " ")):
                                text = text[:key] + '#' + text[key:]
                                text = text[:key+1] + '' + text[key+2:]
                    the_file.write(text)

                    
            #remove 2021 from 1st lines if present
            with open('somefile.txt', 'r+') as fd:
                lines = fd.readlines()
                fd.seek(0)
                fd.writelines(line for line in lines if line.strip() and '2021' not in line)
                fd.truncate()
                

            with open('somefile.txt','r') as f:
                lines = f.readlines()
            print(lines[0])
            lines[0] = re.sub('[!,*)@#%(&$_?.^]', ' ', lines[0])
            print(lines[0])

            with open("somefile_upd.txt", "w") as f:
                f.writelines(lines)
                
                
            with open('somefile_upd.txt','r') as f:
                lines = f.readlines()
            print("upddddddd  ",lines[0])





            file = open('somefile_upd.txt')
            df = pd.read_table(file,
               # skiprows=1,
               # header=None,
               # names=col_names,
               delimiter=r'\s{2,}',
               # skipinitialspace=True,
               skipfooter = 1,
               error_bad_lines=False)

            def count_br(text_input,openBr, closeBr):
                text  = text_input
                for index in range(0, len(text)):
                    if text[index] == '(':
                        openBr+=1

                    if text[index] == ')':
                        closeBr+=1
                return openBr, closeBr

            print("df info", df.info())
            for i, row in df.iterrows():
                drug_tier = row['Drug Tier']
                if re.findall('\((.*?)\)',str(drug_tier)):
                            transcript = re.findall('\((.*?)\)',drug_tier)[0]
                            df.loc[i, 'Drug Name'] = df.loc[i, 'Drug Name'] +' '+ df.loc[i, 'Drug Tier']
            df['Drug Tier'] = [re.sub("\((.*?)\)","", str(x)) for x in df['Drug Tier']]

            for i, row in df.iterrows():
                drug_tier = row['Drug Tier']
                if "(" in drug_tier:
                    df.loc[i, 'Drug Name'] = df.loc[i, 'Drug Name'] +' '+ df.loc[i, 'Drug Tier']
                    df.loc[i, 'Drug Tier'] = "None"
                if ")" in drug_tier:
                    df.loc[i, 'Drug Name'] = df.loc[i, 'Drug Name'] +' '+ df.loc[i, 'Drug Tier']
                    df.loc[i, 'Drug Tier'] = "None"

            import re
            for i, row in df.iterrows():
                specialty = str(row['Specialty'])
                if re.findall('[0-9]+',specialty):
                            transcript = re.findall('[0-9]+',specialty)[0]
                            df.loc[i, 'Drug Tier'] = str(df.loc[i, 'Drug Tier']) +' '+ str(df.loc[i, 'Specialty'])
            df['Specialty'] = [re.sub("[0-9]+","", str(x)) for x in df['Specialty']]
            df['Drug Tier'] = df['Drug Tier'].replace(r'^\s*$', np.nan, regex=True)

            df.rename({'Drug Name': 'A'}, axis=1, inplace=True)
            df.rename({'Drug Tier': 'B'}, axis=1, inplace=True)

            form_words = pd.read_excel('features/form_words_all_possible_cases.xlsx')

            i =0
            while i< len(df)-1:
                if(df.loc[i, 'B'] == 'None'):
                    for elem in df.loc[i, 'A'].split():
                        if form_words['SPL Acceptable Term'].eq(elem).any():
                            # print("yesssssssssssssssss", elem)
                            df.loc[i-1, 'A'] = df.loc[i-1, 'A'] +' '+ df.loc[i, 'A']
                            df.drop(i, inplace = True)
                            df = df.reset_index(drop=True)
                            i = 0
                            break
                i+=1


            #code to add row data to above row if no. is present in it and 
            i =0
            while i< len(df)-1:
                if(df.loc[i, 'B'] == 'None'):
                    for elem in df.loc[i, 'A'].split():
                        # if form_words['SPL Acceptable Term'].eq(elem).any():
                        if elem.isdigit():
                            # print(elem)
                            # print(elem.isdigit())
                            # print(type(elem))
                            df.loc[i-1, 'A'] = df.loc[i-1, 'A'] +' '+ df.loc[i, 'A']
                            df.drop(i, inplace = True)
                            df = df.reset_index(drop=True)
                i+=1

            df = df.replace('#',"0")
            df = df.replace('·',"1")
            df = df.replace('.',"1")
            df = df.fillna('0')
            df = df.replace(r'^\s*$', "0", regex=True)
            # df['test'] = df['Prior Authorization'].str.replace('.', '1', regex=True).astype(float)


            df2 =  df[['Specialty','Prior Authorization', 'Quantity Limits', 'Responsible Steps', 'Limited Distribution']]

            df["Req_Lim"] = df2.eq('1').dot(df2.columns + ',').str[:-1].str.split(',')

            df['Req_Lim'] =  df['Req_Lim'].apply(lambda x: str(x).replace('[','').replace(']','')) 

            df['Req_Lim'] = df['Req_Lim'].replace('Specialty',"SP")
            df['Req_Lim'] = df['Req_Lim'].replace('Prior Authorization',"PA")
            df['Req_Lim'] = df['Req_Lim'].replace('Quantity Limits',"QL")
            df['Req_Lim'] = df['Req_Lim'].replace('Responsible Steps',"RS")
            df['Req_Lim'] = df['Req_Lim'].replace('Limited Distribution',"LD")

            df.rename({'Req_Lim': 'C'}, axis=1, inplace=True)

            # code to add bracket data to previous row 

            i = 0

            while i< len(df)-1:

                if(df.loc[i+1, 'A'].startswith('(')):
                    df.loc[i, 'A'] = df.loc[i, 'A'] +' '+ df.loc[i+1, 'A']
                    df.drop(i+1, inplace = True)
                    df = df.reset_index(drop=True)
                i+=1


            #code to merge incomplete bracket data in A col
            i = 0
            while i < len(df):
                row = i
                pos = 0
                openBr = 0
                closeBr = 0
                text = ''
                if '(' in df.loc[row, 'A']:
                    text = df.loc[i, 'A']
                    openBr,closeBr = count_br(df.loc[row, 'A'],openBr, closeBr )
                    while openBr-closeBr != 0:
                        openBr = 0
                        closeBr = 0
                        text = text + df.loc[row+1, 'A']

                        df.iloc[i] = (df.iloc[i] + ' ' + df.iloc[row+1])
                        openBr,closeBr = count_br(text,openBr, closeBr )
                        df.drop(row+1, inplace = True)
                        df = df.reset_index(drop=True)

                i+=1

            #code to add row comtaining forms name like mg ml.. to upper row
            i =0
            list_dosages = ['mg', 'ml', 'gm']
            while i< len(df)-1:
                if(df.loc[i, 'B'] == 'None'):
                    for elem in (df.loc[i, 'A'].split("/")):
                        if elem.lower() in list_dosages:
                            df.loc[i-1, 'A'] = df.loc[i-1, 'A'] +' '+ df.loc[i, 'A']
                            df.drop(i, inplace = True)
                            df = df.reset_index(drop=True)
                            break
                i+=1

            # Code to merge row besed on None value in B and C col , avoiding Cat sub cat
            df = df.replace({np.nan: None})
            def num_there(s):
                return any(i.isdigit() for i in s)
            i = 0
            while i < len(df):
                # print(i)
                # row = i
                if df.loc[i, 'B'] ==None and df.loc[i, 'C'] == None:
                    if num_there(str(df.loc[i, 'B'])) == True:
                        if df.loc[i-1, 'B'] == None and df.loc[i-1, 'C'] == None:
                            # print('Cont',i)
                            pass
                        else:
                            df.loc[i-1, 'A'] = df.loc[i-1, 'A'] +' '+ df.loc[i, 'A']
                            df.drop(i, inplace = True)
                            df = df.reset_index(drop=True)
                i+=1

            i = 0
            while i < len(df):
                if df.loc[i, 'B']==None and df.loc[i, 'C'] == None:
                    if '(' in str(df.loc[i, 'A']) or ')' in str(df.loc[i, 'A']):
                        if df.loc[i-1, 'B'] == None and df.loc[i-1, 'C'] == None:
                            pass
                        else:
                            df.loc[i-1, 'A'] = df.loc[i-1, 'A'] +' '+ df.loc[i, 'A']
                            df.drop(i, inplace = True)
                            df = df.reset_index(drop=True)
                i+=1



            #code to merge incomplete bracket data in A col

            i = 0
            while i < len(df):

                row = i
                pos = 0
                openBr = 0
                closeBr = 0
                text = ''
                if '(' in df.loc[row, 'A']:
                    text = df.loc[i, 'A']
                    openBr,closeBr = count_br(df.loc[row, 'A'],openBr, closeBr )
                    while openBr-closeBr != 0:
                        openBr = 0
                        closeBr = 0
                        text = text + df.loc[row+1, 'A']

                        df.iloc[i] = (df.iloc[i] + ' ' + df.iloc[row+1])
                        openBr,closeBr = count_br(text,openBr, closeBr )
                        # df = df.iloc[i+1:].reset_index(drop=True)
                        df.drop(row+1, inplace = True)
                        df = df.reset_index(drop=True)

                i+=1

            df3 = df[['A','B', 'C']]

            for i, col in enumerate(df3.columns):
                df3.iloc[:, i] = df3.iloc[:, i].str.replace('#', '')
                df3.iloc[:, i] = df3.iloc[:, i].str.replace('None', '')
                df3.iloc[:, i] = df3.iloc[:, i].str.replace('"', '')
                df3.iloc[:, i] = df3.iloc[:, i].str.replace("'", '')

            df3.to_excel(writer, sheet_name=str(ind))

            ind+=1



def create_df_multi_partial(pdf_name):
    ind = 1
    import re
    re_to_pdf=re.sub('.pdf','',pdf_name)
    file_name = re_to_pdf
    with pd.ExcelWriter(os.path.abspath("../data/raw/{}.xlsx".format(file_name))) as writer:

        for filename in glob.glob(os.path.abspath("../data/Xpdf_out/*.txt")):
            print('in loop',file_name)

            file1 = open(filename,"r+") 
            list_index = []
            import re
            for i in file1.readlines():
                list_line = (re.split(r'\s{2,}', i))
                for elem in list_line:
                    list_index.append(i.index(elem))


            var = Counter(list_index)

            with open('somefile.txt', 'w') as the_file:
                file1 = open(filename,"r+") 
                for i in file1.readlines():
                    text = i
                    for key in var.keys():
                        if(len(text)>key):
                            if ((text[key] == " " and text[key-1] == " ") or (text[key] == " " and text[key+1] == " ")):
                                text = text[:key] + '#' + text[key:]
                                text = text[:key+1] + '' + text[key+2:]
                    the_file.write(text)


            # remove 2021 from 1st lines if present
            with open('somefile.txt', 'r+') as fd:
                lines = fd.readlines()
                fd.seek(0)
                fd.writelines(line for line in lines if line.strip() and '2021' not in line)
                fd.truncate()


            with open('somefile.txt','r') as f:
                lines = f.readlines()
            # print(lines[2])
            lines[0] = re.sub('[!,*)@#%(&$_?.^]', ' ', lines[0])
            # lines[2] = re.sub('[!,*)@#%(&$_?.^]', ' ', lines[2])
            # print(lines[2])

            with open("somefile_upd.txt", "w") as f:
                f.writelines(lines)


            with open('somefile_upd.txt','r') as f:
                lines = f.readlines()
            # print("upddddddd  ",lines[0])





            file = open('somefile_upd.txt')
            df = pd.read_table(file,
               # skiprows=2,
               header=None,
               # names=col_names,
               delimiter=r'\s{2,}',
               # skipinitialspace=True,
               skipfooter = 2,
               error_bad_lines=False)

            # df.columns = ['A','B','C']
            # df.reset_index(inplace = True)
            df.reset_index(inplace = True)
            df['tmp'] = df.index




            df = df.fillna(value=np.nan)
            df = df.replace(np.nan, "#")

            print("check ",df['index'].equals(df['tmp']))

            if(df['index'].equals(df['tmp']) == False):
                print("Y")
                df. drop("tmp", axis=1, inplace=True)
                df = df.iloc[2: , :]
                df["comb"] = (df[df.columns[2]]) +" "+ (df[df.columns[3]])  
                df["Ext_Tier"] = df.apply(calc_new_col_tier, axis=1)
                df["comb"] = df.apply(calc_new_col_req, axis=1)
                df["Tier"] = df[df.columns[1]] + df["Ext_Tier"] 
                df.drop(0, axis=1, inplace=True)
                df.drop(1, axis=1, inplace=True)
                df.drop(2, axis=1, inplace=True)
                df.drop("Ext_Tier", axis=1, inplace=True)
                df = df[['index', 'Tier', 'comb']]
                df.columns = ['A','B','C']
            else:
                df = df.iloc[2: , :]
                df. drop("tmp", axis=1, inplace=True)
                df. drop("index", axis=1, inplace=True)
                df.columns = ['A','B','C']


            def count_br(text_input,openBr, closeBr):
                # print("in function")
                # print(text_input)
                text  = text_input
                for index in range(0, len(text)):
                    if text[index] == '(':
                        openBr+=1

                    if text[index] == ')':
                        # print("yessss")
                        closeBr+=1
                        # openBr-=1
                return openBr, closeBr

            for i, row in df.iterrows():
                drug_tier = row[df.columns[1]]
                if re.findall('\((.*?)\)',str(drug_tier)):
                            transcript = re.findall('\((.*?)\)',drug_tier)[0]
                            #print(row['Drug Tier'])
                            df.loc[i,  df.columns[0]] = df.loc[i, df.columns[0]] +' '+ df.loc[i, df.columns[1]]
            df[ df.columns[1]] = [re.sub("\((.*?)\)","", str(x)) for x in df[ df.columns[1]]]


            for i, row in df.iterrows():
                drug_tier = row[df.columns[1]]
                if "(" in drug_tier:
                    print(drug_tier)
                    df.loc[i, df.columns[0]] = df.loc[i, df.columns[0]] +' '+ df.loc[i, df.columns[1]]
                    df.loc[i, df.columns[1]] = "None"

                if ")" in drug_tier:
                    df.loc[i, df.columns[0]] = df.loc[i, df.columns[0]] +' '+ df.loc[i, df.columns[1]]
                    df.loc[i, df.columns[1]] = "None"

            df = df.reset_index(drop=True)

            form_words = pd.read_excel('features/form_words_all_possible_cases.xlsx')

            i =0
            while i< len(df)-1:
                if(df.loc[i, 'B'] == '#' or df.loc[i, 'B'] == '##'):
                    for elem in df.loc[i, 'A'].split():
                        if form_words['SPL Acceptable Term'].eq(elem).any():
                            df.loc[i-1, 'A'] = df.loc[i-1, 'A'] +' '+ df.loc[i, 'A']
                            df.drop(i, inplace = True)
                            df = df.reset_index(drop=True)
                            i = 0
                            break
                i+=1

            #code to add row data to above row if no. is present in it and 
            i =0
            while i< len(df)-1:
                if(df.loc[i, 'B'] == '#' or df.loc[i, 'B'] == '##'):
                    for elem in df.loc[i, 'A'].split():
                        # if form_words['SPL Acceptable Term'].eq(elem).any():
                        if elem.isdigit():
                            # print(elem)
                            # print(elem.isdigit())
                            # print(type(elem))
                            df.loc[i-1, 'A'] = df.loc[i-1, 'A'] +' '+ df.loc[i, 'A']
                            df.drop(i, inplace = True)
                            df = df.reset_index(drop=True)
                i+=1


            i = 0

            while i< len(df)-1:

                if(df.loc[i+1, 'A'].startswith('(')):
                    df.loc[i, 'A'] = df.loc[i, 'A'] +' '+ df.loc[i+1, 'A']
                    df.drop(i+1, inplace = True)
                    df = df.reset_index(drop=True)
                i+=1


            #code to merge incomplete bracket data in A col

            i = 0
            # for i, df_row in df.iterrows():
            while i < len(df):
                # if df.loc[i, 'B'] == None:
                row = i
                pos = 0
                openBr = 0
                closeBr = 0
                text = ''
                if '(' in df.loc[row, 'A']:
                    text = df.loc[i, 'A']
                    openBr,closeBr = count_br(df.loc[row, 'A'],openBr, closeBr )
                    while openBr-closeBr != 0:
                        openBr = 0
                        closeBr = 0
                        text = text + df.loc[row+1, 'A']

                        df.iloc[i] = (df.iloc[i] + ' ' + df.iloc[row+1])
                        openBr,closeBr = count_br(text,openBr, closeBr )
                        df.drop(row+1, inplace = True)
                        df = df.reset_index(drop=True)

                i+=1


            # code to add row comtaining forms name like mg ml.. to upper row
            i =0
            list_dosages = ['mg', 'ml', 'gm']
            while i< len(df)-1:
                if(df.loc[i, 'B'] == '#' or df.loc[i, 'B'] == '##'):
                    for elem in (df.loc[i, 'A'].split()):
                        if elem.lower() in list_dosages:
                            df.loc[i-1, 'A'] = df.loc[i-1, 'A'] +' '+ df.loc[i, 'A']
                            df.drop(i, inplace = True)
                            df = df.reset_index(drop=True)
                            i = 0
                            break  
                i+=1


            i = 0
            while i < len(df):
                if (df.loc[i, 'B']=="#" and df.loc[i, 'C'] == "#") or (df.loc[i, 'B']=="##" and df.loc[i, 'C'] == "##"):
                    if '(' in str(df.loc[i, 'A']) or ')' in str(df.loc[i, 'A']):
                        if (df.loc[i-1, 'B'] == "#" and df.loc[i-1, 'C'] == "#") or (df.loc[i-1, 'B'] == "##" and df.loc[i-1, 'C'] == "##"):
                            pass
                        else:
                            df.loc[i-1, 'A'] = df.loc[i-1, 'A'] +' '+ df.loc[i, 'A']
                            df.drop(i, inplace = True)
                            df = df.reset_index(drop=True)
                i+=1


            i = 0
            while i < len(df):
                if (df.loc[i, 'A']=="#" or df.loc[i, 'A']=="##")  and (df.loc[i, 'B'] == "#" or df.loc[i, 'B'] == "##"):
                    if '(' in str(df.loc[i, 'C']) or ')' in str(df.loc[i, 'C']):
                        df.loc[i-1, 'C'] = df.loc[i-1, 'C'] +' '+ df.loc[i, 'C']
                        df.drop(i, inplace = True)
                        df = df.reset_index(drop=True)
                        i = 0
                i+=1



            #code to merge incomplete bracket data in A col

            i = 0
            while i < len(df):

                row = i
                pos = 0
                openBr = 0
                closeBr = 0
                text = ''
                if '(' in df.loc[row, 'A']:
                    text = df.loc[i, 'A']
                    openBr,closeBr = count_br(df.loc[row, 'A'],openBr, closeBr )
                    while openBr-closeBr != 0:
                        openBr = 0
                        closeBr = 0
                        text = text + df.loc[row+1, 'A']

                        df.iloc[i] = (df.iloc[i] + ' ' + df.iloc[row+1])
                        openBr,closeBr = count_br(text,openBr, closeBr )
                        # df = df.iloc[i+1:].reset_index(drop=True)
                        df.drop(row+1, inplace = True)
                        df = df.reset_index(drop=True)

                i+=1

            for i, col in enumerate(df.columns):
                df.iloc[:, i] = df.iloc[:, i].str.replace('#', '')

            df.to_excel(writer, sheet_name=str(ind))
            ind+=1