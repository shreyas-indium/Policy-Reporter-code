from transformers import ViTFeatureExtractor,ViTForImageClassification
from tensorflow import keras
import os
import tensorflow as tf
import numpy as np
import torch
import streamlit as st
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

def get_class(img: np.ndarray) -> str:
    """
    This is the function used to check whether a single table or multi table is present in the pdf file.
    
    Parameters:
    img:image of the pdf page.
    
    Returns:
    single table or multi table present in page.
    """
    img_arr = keras.preprocessing.image.img_to_array(img)
    img_arr = tf.expand_dims(img_arr, 0)
    pred = model_new.predict(img_arr)
    pred = (pred>0.5).astype(np.int)
    return class_name[pred[0][0]]


def input_array(image_array: np.ndarray) -> str:
    """
    This is the function is used to check whether a borders or partial borders.
    
    Parameters:
    images:image in numpy array fromat.
    
    Returns:
    borders or partial borders present in page.
    """
    inputs = feature_extractor(images = image_array, 
                               return_tensors="pt")
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    inputs = inputs.to(device)
    outputs = model(**inputs)
    logits = outputs.logits

    predicted_class_idx = logits.argmax(-1).item()

    if predicted_class_idx == 0:
        st.write('The table has row and column borders')
    elif predicted_class_idx == 1:
        st.write("The table has partial row and column borders")
    elif predicted_class_idx == 2:
        st.write("The table has partial table")
    else:
        st.write('class is missing')
    return predicted_class_idx




print("loading model")
#table classification model for normal and other pdf files
cwd = os.getcwd()
model_name_or_path = os.path.abspath("../data/interim/table_classification_model_normal_other")
feature_extractor = ViTFeatureExtractor.from_pretrained(model_name_or_path,local_files_only=True)
model = ViTForImageClassification.from_pretrained(model_name_or_path,local_files_only=True)


#classification model for multi table and single tables
model_new_path = os.path.abspath("../data/interim/new2/new.h5")
model_new =keras.models.load_model(model_new_path)
class_name = ['Multiple tables', 'Single table']


