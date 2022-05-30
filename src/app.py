import streamlit as st
import os
import random
from PyPDF2 import PdfFileWriter, PdfFileReader
import cv2
from PIL import Image as img
import torch
import spacy
import re
import base64

from models.loading_model import get_class, input_array
from features.xpdf import split_vertical, pdftotext, pdf_cut,clear_pdftotext
from data.make_dataset import save_uploaded_file, clear_images_dir, generate_images, clear_dir
from features.build_features import get_final_range, create_download_link, split_pdf_using_range
from features import encoding_form, normal_table, Spacy_test, table_encoding, xlsx_to_json, extract_tables_multi,cat_sub_gen, cat_subcat, decrypt

from features.text_to_df import create_df, create_df_multi_partial

# predict_border
# predict_tab_num

st.title("Data Extraction")

st.subheader("Upload your PDF files here")
docx_file = st.file_uploader("", type=["pdf","docx","txt"])

if st.button("Process"):

    if docx_file is not None:

        save_uploaded_file(docx_file, docx_file.name)
        clear_images_dir()


        file_details = {"filename":docx_file.name, "filetype":docx_file.type,
            "filesize":docx_file.size}
        st.write(file_details)
        st.caption('Getting range...')
        pdf = os.path.abspath("../data/raw/"+str(docx_file.name))
        only_name = str(docx_file.name)
        if decrypt.check_encryption(pdf) == True:
            st.caption('uploaded pdf file is encrypted attempting to decrypt')
            pdffile_name_decrypt = decrypt.decrypt_pdf(pdf) 
            pdf = str(pdffile_name_decrypt)
            pdffile_name = pdf.replace('pdf', '')
            pdffile = pdf
            st.write('uploaded pdf file decrypted successfully')
        else:
            pdf = os.path.abspath("../data/raw/"+str(docx_file.name))        
            pdffile_name = pdf.replace('pdf', '')
            pdffile = pdf


        start_rang, end_range = get_final_range(pdffile)
        print('in main__',start_rang, end_range)
        st.write('range for uploaded pdf file is..',start_rang,'to', end_range)
        clear_images_dir()

        split_pdf = split_pdf_using_range(pdf,start_rang,end_range)
           
        print('split_pdf',split_pdf)
        pdf2 = split_pdf        
        pdffile_name2 = pdf2.replace('.pdf', '')
        st.write('pdffile_name2',pdffile_name2)
        pdffile2 = pdf2
        generate_images(pdffile2,str(os.path.abspath("../data/external"))+'/'+str(docx_file.name))

        st.caption('Detecting Single_table or Multi_table....')
        images_path = os.path.abspath("../data/external")
        image_test = random.choice(os.listdir(images_path))
        image_test_path = images_path+'\\'+image_test

        
        img1 = cv2.imread(image_test_path)
        img1 = cv2.resize(img1, (256,256))

        class_image = get_class(img1)
        st.write('The file has',class_image, 'per page')

        st.caption('Detecting whether table has rows and columns borders...')
        image_array = img.open(image_test_path)

        predicted_class_idx = input_array(image_array)
        clear_dir(images_path)

        if predicted_class_idx == 0 and class_image =='Single table':
            flag = 0
            values = start_rang, end_range
            if flag == 0:
                clear_dir(os.path.abspath("../data/processed"))
                #inputfiles
                inputpdf = pdffile
                #'pdf/'+str(docx_file.name)
                st.caption('Initiating Extraction Pipeline for Single table having row and column borders')
                #pipeline
                re_to_pdf=re.sub('.pdf','',inputpdf)
                file_name = re_to_pdf
                output = file_name+".xlsx"

                print('inputpdf ', inputpdf)
                print('output ', output)
                print('values ', values)

                outputxlsx = output.replace('.xlsx', 'subcat.xlsx')
                normal_table.extract_data(inputpdf,output, start_rang, end_range)
                cat_subcat.add_cat_subcat(output, outputxlsx,start_rang, end_range,"Lib")

                #inputfiles
                input_pdf = inputpdf
                input_file = outputxlsx

                # encoding_form
                ext_file = input_file.replace('.xlsx','_drug_parsed.xlsx')

                # Spacy_test
                input_file_name = ext_file
                output_file = input_file_name.replace('.xlsx','_model_output.xlsx')   
                nlp_dose = spacy.load(os.path.abspath("../data/interim/DrugDosage/output/model-best"))

                # table_encoding  #"" _drug_parsed
                enc_file= output_file.replace('.xlsx','_encoded.xlsx')

                # xlsx_to_json
                re_to_pdf=re.sub('.pdf','',input_pdf)
                file_name = re_to_pdf
                output_json = file_name+".json"
                record_exel = 'features/record.xlsx'

                # encoding form 
                dosage_form_keywords = encoding_form.get_dosage()
                encoding_form.get_sheets(input_file, dosage_form_keywords)

                # Spacy_test
                dosage = Spacy_test.gen_excel(ext_file, output_file, nlp_dose)

                # table_encoding
                table_encoding.encoding(output_file,enc_file)

                # xlsx_to_json
                xlsx_to_json.json_header(enc_file, record_exel, file_name, input_pdf, output_json, start_rang)

                flag = 1

            if(flag == 1):

                inputpdf = pdffile
                re_to_pdf=re.sub('.pdf','',inputpdf)
                file_name = re_to_pdf
                output_json = file_name+".json"
                print(file_name)
                file1 =  open(str(re.sub('.pdf','subcat_drug_parsed_model_output_encoded.xlsx',input_pdf)), "rb")
                file2 =  open(output_json, "rb")           

                val = str(re.sub('.pdf','subcat_drug_parsed_model_output_encoded.xlsx',input_pdf))
                filename = re.sub('.pdf','.xlsx',str(docx_file.name))

                html = create_download_link(val, filename)
                st.markdown(html, unsafe_allow_html=True)

                filename_json = re.sub('.pdf','.json',str(docx_file.name))
                
                html = create_download_link(output_json, filename_json)
                st.markdown(html, unsafe_allow_html=True)

        elif(predicted_class_idx == 0 and class_image =='Multiple tables'):    
            flag = 0
            # values = start_rang, end_range
            if flag == 0:
                #inputfiles
                inputpdf = pdffile
                #'pdf/'+str(docx_file.name)
                st.caption('Initiating Extraction Pipeline for Multi table having row and column borders')
                #pipeline
                re_to_pdf=re.sub('.pdf','',inputpdf)
                file_name = re_to_pdf
                output = file_name+".xlsx"
                file = re.sub('.pdf','',docx_file.name)
                extract_tables_multi.extract_data(inputpdf,output, start_rang, end_range, file)
                clear_dir(os.path.abspath("../data/raw/pdf_pages/"))
                cat_sub_gen.generate_cat(output, start_rang, end_range)

                #inputfiles
                input_pdf = inputpdf
                input_file = output.replace('.xlsx','_out.xlsx')   

                # encoding_form
                ext_file = input_file.replace('.xlsx','_drug_parsed.xlsx')

                # Spacy_test
                input_file_name = ext_file
                output_file = input_file_name.replace('.xlsx','_model_output.xlsx')   
                nlp_dose = spacy.load(os.path.abspath("../data/interim/DrugDosage/output/model-best"))

                # table_encoding  #"" _drug_parsed
                enc_file= output_file.replace('.xlsx','_encoded.xlsx')

                # xlsx_to_json
                re_to_pdf=re.sub('.pdf','',input_pdf)
                file_name = re_to_pdf
                output_json = file_name+".json"
                record_exel = 'features/record.xlsx'

                # encoding form 
                dosage_form_keywords = encoding_form.get_dosage()
                encoding_form.get_sheets(input_file, dosage_form_keywords)

                # Spacy_test
                dosage = Spacy_test.gen_excel(ext_file, output_file, nlp_dose)

                # table_encoding
                table_encoding.encoding(output_file,enc_file)

                # xlsx_to_json
                file_name=docx_file.name
                xlsx_to_json.json_header(enc_file, record_exel, docx_file.name, input_pdf, output_json,start_rang)

                flag = 1

            if(flag == 1):

                inputpdf = str(os.path.abspath("../data/raw/"+str(docx_file.name)))
                re_to_pdf=re.sub('.pdf','',inputpdf)
                file_name = re_to_pdf
                output_json = file_name+".json"
                print(file_name)
                file1 =  open(str(re.sub('.pdf','_out_drug_parsed_model_output_encoded.xlsx',input_pdf)), "rb")
                file2 =  open(output_json, "rb")           

                val = str(re.sub('.pdf','_out_drug_parsed_model_output_encoded.xlsx',input_pdf))
                filename = re.sub('.pdf','.xlsx',str(docx_file.name))

                html = create_download_link(val, filename)
                st.markdown(html, unsafe_allow_html=True)

                filename_json = re.sub('.pdf','.json',str(docx_file.name))
                
                html = create_download_link(output_json, filename_json)
                st.markdown(html, unsafe_allow_html=True)
     
        elif(predicted_class_idx == 1 and class_image =='Multiple tables'):
            clear_pdftotext()

            print('here is xpdf')
            split_vertical(pdffile_name2+'.pdf')
            pdf_cut(pdffile_name2+'_out.pdf')
            pdftotext()

            create_df(str(docx_file.name))
            inputpdf = str(os.path.abspath("../data/raw/"+str(docx_file.name)))
            re_to_pdf=re.sub('.pdf','',inputpdf)
            file_name = re_to_pdf
            output = file_name+".xlsx"
            
            outputxlsx = output.replace('.xlsx', 'subcat.xlsx')
            cat_subcat.add_cat_subcat(output, outputxlsx, start_rang, end_range, "xpdf")
            
            #inputfiles
            input_pdf = inputpdf
            input_file = outputxlsx

            # encoding_form
            ext_file = input_file.replace('.xlsx','_drug_parsed.xlsx')

            # Spacy_test
            input_file_name = ext_file
            output_file = input_file_name.replace('.xlsx','_model_output.xlsx')   
            nlp_dose = spacy.load(os.path.abspath("../data/interim/DrugDosage/output/model-best"))

            # table_encoding  #"" _drug_parsed
            enc_file= output_file.replace('.xlsx','_encoded.xlsx')

            # xlsx_to_json
            re_to_pdf=re.sub('.pdf','',input_pdf)
            file_name = re_to_pdf
            output_json = file_name+".json"
            record_exel = 'features/record.xlsx'

            # encoding form 
            dosage_form_keywords = encoding_form.get_dosage()
            encoding_form.get_sheets(input_file, dosage_form_keywords)

            # Spacy_test
            dosage = Spacy_test.gen_excel(ext_file, output_file, nlp_dose)

            # table_encoding
            table_encoding.encoding(output_file,enc_file)

            # xlsx_to_json
            file_name=docx_file.name
            xlsx_to_json.json_header(enc_file, record_exel, docx_file.name, input_pdf, output_json,start_rang)

            flag = 1



            inputpdf = str(os.path.abspath("../data/raw/"+str(docx_file.name)))
            re_to_pdf=re.sub('.pdf','',inputpdf)
            file_name = re_to_pdf
            output_json = file_name+".json"
            print(file_name)
            file1 =  open(str(re.sub('.pdf','subcat_drug_parsed_model_output_encoded.xlsx',input_pdf)), "rb")
            file2 =  open(output_json, "rb")           

            val = str(re.sub('.pdf','subcat_drug_parsed_model_output_encoded.xlsx',input_pdf))
            filename = re.sub('.pdf','.xlsx',str(docx_file.name))

            html = create_download_link(val, filename)
            st.markdown(html, unsafe_allow_html=True)

            filename_json = re.sub('.pdf','.json',str(docx_file.name))

            html = create_download_link(output_json, filename_json)
            st.markdown(html, unsafe_allow_html=True)

            # clear_pdftotext()


        elif(predicted_class_idx == 2 and class_image =='Multiple tables'):
            clear_pdftotext()

            print('here is xpdf')
            split_vertical(pdffile_name2+'.pdf')
            pdf_cut(pdffile_name2+'_out.pdf')
            pdftotext()

            create_df_multi_partial(str(docx_file.name))
            inputpdf = str(os.path.abspath("../data/raw/"+str(docx_file.name)))
            re_to_pdf=re.sub('.pdf','',inputpdf)
            file_name = re_to_pdf
            output = file_name+".xlsx"
            
            outputxlsx = output.replace('.xlsx', 'subcat.xlsx')
            cat_subcat.add_cat_subcat(output, outputxlsx, start_rang, end_range, "xpdf")
            
            #inputfiles
            input_pdf = inputpdf
            input_file = outputxlsx

            # encoding_form
            ext_file = input_file.replace('.xlsx','_drug_parsed.xlsx')

            # Spacy_test
            input_file_name = ext_file
            output_file = input_file_name.replace('.xlsx','_model_output.xlsx')   
            nlp_dose = spacy.load(os.path.abspath("../data/interim/DrugDosage/output/model-best"))

            # table_encoding  #"" _drug_parsed
            enc_file= output_file.replace('.xlsx','_encoded.xlsx')

            # xlsx_to_json
            re_to_pdf=re.sub('.pdf','',input_pdf)
            file_name = re_to_pdf
            output_json = file_name+".json"
            record_exel = 'features/record.xlsx'

            # encoding form 
            dosage_form_keywords = encoding_form.get_dosage()
            encoding_form.get_sheets(input_file, dosage_form_keywords)

            # Spacy_test
            dosage = Spacy_test.gen_excel(ext_file, output_file, nlp_dose)

            # table_encoding
            table_encoding.encoding(output_file,enc_file)

            # xlsx_to_json
            file_name=docx_file.name
            xlsx_to_json.json_header(enc_file, record_exel, docx_file.name, input_pdf, output_json,start_rang)

            flag = 1

            inputpdf = str(os.path.abspath("../data/raw/"+str(docx_file.name)))
            re_to_pdf=re.sub('.pdf','',inputpdf)
            file_name = re_to_pdf
            output_json = file_name+".json"
            print(file_name)
            file1 =  open(str(re.sub('.pdf','subcat_drug_parsed_model_output_encoded.xlsx',input_pdf)), "rb")
            file2 =  open(output_json, "rb")           

            val = str(re.sub('.pdf','subcat_drug_parsed_model_output_encoded.xlsx',input_pdf))
            filename = re.sub('.pdf','.xlsx',str(docx_file.name))

            html = create_download_link(val, filename)
            st.markdown(html, unsafe_allow_html=True)

            filename_json = re.sub('.pdf','.json',str(docx_file.name))

            html = create_download_link(output_json, filename_json)
            st.markdown(html, unsafe_allow_html=True)



        else:
            print('in development for other formats like this')
            st.write('in development for other formats like this')

