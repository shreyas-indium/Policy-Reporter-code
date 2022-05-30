import pandas as pd
from nltk.corpus import stopwords
import glob
import re
import os

stop_words = stopwords.words('english')
#dosage_form_keywords = []
sheetnames_list = []
df_list = []

def save_xls(list_dfs, sheetnames, columns, xls_path):
    """
    This function is used to combine all the excel files in the directory.

    Parameters:
    list_dfs: dataframe for reading excel file.
    sheetnames: sheet_names of excel file.
    columns: name of the columns to write in excel.
    xls_path: path to excel file.

    Returns
    it returns dosage form keywords
    """
    # print('reading...',df.info)
    with pd.ExcelWriter(xls_path) as writer:
        for n, df in enumerate(list_dfs):
            df.to_excel(writer,sheetnames[n],columns=columns, encoding='utf8')
        writer.save()
 
 

def get_dosage():
    """
    This function is used to get all the dosage keywords from the file and the dictionary.

    Returns
    it returns dosage form keywords
    """
    print("Dosage___________________check")
    print(os.getcwd())
    dosage_forms = pd.read_excel('features/dosage_forms.xlsx', engine='openpyxl')['SPL Acceptable Term'].tolist()
    dosage_form_keywords = []
    for dosage_form in dosage_forms:
        keywords = dosage_form.replace(',','').replace('/','').split()
        keywords = [keyword for keyword in keywords if keyword.lower() not in stop_words]
        dosage_form_keywords = dosage_form_keywords + keywords
    dosage_form_keywords = set(dosage_form_keywords)
#     update_keys(dosage_form_keywords)

# # add some missing keywords
#     # add some missing keywords
    dosage_form_keywords.update({'ORAL','NON-','RECON','HANDLE','SYRINGE','SYRINGES','INHALER','PACKET','EXTERNAL','PEN',
                             'PAD','AUTOINJECTOR','AUTO-INJECTOR','LANCING','EJECTOR','NEEDLE','NEEDLES',
                             'NEBULIZER','NASAL','INHALATION','DR/EC','INTRAVENOUS','MOUTH','RECONSTITUTED',
                                 'SUBCUTANEOUS','VAGINAL','FOR','RECONSTITUTION','RECONSTITUED','SUBLINGUAL','CARTRIDGE','ACTIVATED','SOLN'
                             ,'CONDOM','TRANSMITTER','SYR','ULTRAFINE','U/F','MASK','SYRING','SYRN','DISPERSIBLE'
                             ,'SPRINKLE','PEN-INJECTOR','HOUR','PACK','INJECTOR','COMBO','STRIPS','INTRAMUSCULAR','DETERRENT','TRANSDERMAL'
                             ,'LANCETS','LANCET','CAP','TABS','CAPS','ER CPCR','TAB','TAB ER','CAP','TAB','ODT','INJ','LA CAP','CAP SR','GRANULES','inj',"INJ",'er','INH','SUSP','SUSP','PRSY','OPHTHALMIC','SUBL','PATCH','PTCH','VIAL','LIQD','SOSY','ER','PT72','TB12','CP12','LOTN','pt72',"PTTW",'AERS','TBEC','SUPP','AERO','SUPPOS','SUP','SUS','OIN','CHW','SOL','INH','ARE','SPR','INH','NEB','PAK','DIS','SUS','POW','LIQ','GRA','IMP','CHW','MIS','SYP','DM','LIQ','LOT','CRE','OIN','E','TAP','LOT','LIQ','POW','DPR','SPR','REFILL','ENEM','PTWK','TBDP','TBPK','AEPB','AEPB','DPRH','IUD','SUB','EMU','GRAN','CPDR','PSKT','SYRP','SOPN','POWD','SHAM','TROC','CPPK','troc','SOAJ','PT24','NEBY','NEBU','SUSR','CPCR','PT','CONC','TBCR','AER','SUSR','LOZG','OINT','CREA','SOLR','LOZH','CHEW','SUSP','ELIX','CPEP','CSDR','TBEC','CPSP','TP12','CR12','TB24','CP24','topical', 'intramuscular', 'percutaneous', 'for reconstitution', 'for injection', 'for soln', 'iv solution', 'im soln', 'otic', 'ophthalmic', 'intraocular', 'iontophoresis', 'perianal', 'vaginal', 'LAR', 'In vitro', 'er multiphase', 'combination kit', 'scalp', 'dental','dr/ec','ORAL PACKET', 'THERAPY PACK','STARTER PACK', 'NASAL LIQUID', 'ONE PACK', 'TWO PACK', 'STARTER PACK','TITRATION', 'COMBINATION', 'PREMED','PREMIUM','HEMODIALYSIS', 'SIZE','COMPRESSED','MELT','FLAVOR','CLINISAFE','PODS','SAFEPACK','RELIEF'})
    dosage_form_keywords_list = list(dosage_form_keywords)
    for i, word in enumerate(dosage_form_keywords_list):
        dosage_form_keywords_list[i] = word.upper()
    dosage_form_keywords = set(dosage_form_keywords_list)
    return dosage_form_keywords


def get_sheets(input_file_name, dosage_form_keywords):
    """
    This function is used to get sheet from the excel file.
    
    Parameters:
    input_file_name: input excel file.
    dosage_form_keywords: adding additional keywards from dosage form keywords.
    """
    
    for input_file in glob.glob(input_file_name):

        print('file',input_file)

        if '_parsed.xlsx' in input_file:
            continue

        xls = pd.ExcelFile(input_file, engine='openpyxl')

        df_list = []
        sheetnames_list = []
        
        parse_excel(xls, input_file, dosage_form_keywords)
        

def parse_excel(xls, input_file, dosage_form_keywords):
    """
    This method will separates the forms from the drug name and resolve some unknown values into the excel.
    
    Parameters:
    xls: this is excel file named as dosage_forms in directory. 
    input_file: extracted excel output of PDF file.
    dosage_form_keywords: adding additional keywards from dosage form keywords.
    """

        # parse the XL now
    for sheetname in xls.sheet_names:
        # if sheetname == 'Table20':
            # break
        df = pd.read_excel(input_file,sheet_name=sheetname, engine='openpyxl')
        drug_unparsed_list = df[df.columns[1]]
        drugname_list, form_list, dosage_list=[],[],[]

        for drug_unparsed in drug_unparsed_list:
            words = str(drug_unparsed).replace('_',' ').split()
            words = [wrd for wrd in words if wrd != 'x000D']
            form_indices = [i for i, x in enumerate(words) if
                            (any(val in dosage_form_keywords for val in str(x).upper().split('/'))
                             or any(val in dosage_form_keywords for val in str(x).upper().split(','))
                             or any(val in dosage_form_keywords for val in str(x).upper().split('(')))]
            if len(form_indices)<1:
                dosage_index = len(words)

                drugname_list.append(' '.join(words[:dosage_index]))
                form_list.append('')
                dosage_list.append(' '.join(words[dosage_index:]))
            else:
                drugname_list.append(' '.join([words[i] for i in range(0,len(words)) if i not in form_indices]))
                # drugname_list.append(' '.join(words[:min(form_indices)]))
                # form_list.append(' '.join(words[min(form_indices):max(form_indices)+1]))
                form_list.append(' '.join([words[i] for i in range(0,len(words)) if i in form_indices]))
                if max(form_indices)+1<len(words):
                    if not any(c.isdigit() for c in ' '.join(words[max(form_indices) + 1:])):
                        dosage_list.append('')
                    else:
                        dosage_list.append(' '.join(words[max(form_indices) + 1:]))
                else:
                    dosage_list.append('')

        #change Drug Name to Drug Name unparsed
        # df['drug_unparsed'] = drug_unparsed_list
        df['drugname'] = drugname_list
        df['drugname'] = [re.sub("\(([a-zA-Z]+)\)","", str(x)) for x in df['drugname']]
        df['form'] = form_list
        
        df = df.fillna('')
        df = df.replace({'nan': '','_x005F_x000D_':' '},regex=True)
        df = df.replace({'nan': '','_x000D_':' '},regex=True)
        df = df.replace({'\n': '','_x000D_':' '},regex=True)
        print("info   ", df.info())
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        sheetnames_list.append(sheetname)
        df.rename(columns = {df.columns[0]:'drug-unparsed'}, inplace = True)
        df_list.append(df)
    print('check:......',df_list[0])
    print(df_list[0].columns[0:])
    save_xls(df_list, sheetnames_list,
             df_list[0].columns[0:],
             input_file.replace('.xlsx','_drug_parsed.xlsx'))

