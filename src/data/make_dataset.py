import os
import streamlit as st
import shutil
import fitz

def generate_images(pdffile: str, pdffile_name: str) -> None:
    """
    This function is used to generate the images for model.

    Parameters:
    pdffile: uploded pdf file
    pdffile_name: name of the uploded pdf file
    
    """
    doc = fitz.open(pdffile)
    for i in range(0,doc.pageCount):
        page = doc.loadPage(i)  # number of page
        pix = page.get_pixmap()
        output = pdffile_name+"page_"+str(i)+".png"
        pix.save(output)

def save_uploaded_file(uploadedfile: 'streamlit.UploadedFile', file_name: str) -> str:
    '''
    this method is used for saving binary file in our local directory.
    
    Parameters
        uploadedfile: uploded pdf file.
    
    Returns
        save the file in our local directory
    '''
    with open(os.path.abspath("../data/raw/"+file_name),"wb") as f:
        f.write(uploadedfile.getbuffer())
    return st.success("Saved file :{} internally".format(file_name))

def clear_images_dir() -> None:
    """
    This function is used to clear directory.
    
    Parameters:
        image_output: path of the directory.
    
    """
    images_path = os.path.abspath("../data/external/")
    clear_dir(images_path)

def clear_dir(images_path: str) -> None:
    """
    This function is used to clear directory.
    
    Parameters:
        image_output: path of the directory.
    
    """
    shutil.rmtree(images_path)
    os.mkdir(images_path)


