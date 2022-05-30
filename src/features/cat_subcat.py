import pandas as pd
import numpy as np

## add thhis in function (,start_rang, end_range)

def add_cat_subcat(input_file, output, start_rang, end_range, extraction):

    last_catagory = ''
    last_subcategory = ''
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    for j in range(start_rang, end_range):
        if(extraction == "xpdf"):
            df1 = pd.read_excel(input_file,sheet_name=str(j))
        else:
            df1 = pd.read_excel(input_file,sheet_name='page'+str(j)+'_table_1x')
        if len(df1) > 0:
            data_to_analyse = df1
            category_value = ''
            subcategory_value = ''
            category = []
            subcategory = []

            for i in range(0, data_to_analyse.shape[0]):
                boolean = data_to_analyse[i:i + 1].isna()

                if i == 0:
                    if (boolean.iloc[0].values[1] == False) & (boolean.iloc[0].values[2] == False):
                        category_value = last_catagory
                        subcategory_value = last_subcategory

                    if (boolean.iloc[0].values[1] == True) & (boolean.iloc[0].values[2] == False):
                        category_value = last_catagory
                        subcategory_value = last_subcategory

                    if (boolean.iloc[0].values[1] == False) & (boolean.iloc[0].values[2] == True):
                        category_value = last_catagory
                        subcategory_value = last_subcategory

                    if (boolean.iloc[0].values[1] == True) & (boolean.iloc[0].values[2] == True):
                        initial_category_check = data_to_analyse[i + 1:i + 2].isna()
                        if (initial_category_check.iloc[0].values[1] == False) or (
                                initial_category_check.iloc[0].values[2] == False):
                            category_value = last_catagory

                if len(boolean.loc[(boolean[boolean.columns[1]] == True) & (boolean[boolean.columns[2]] == True)]) > 0:
                    category_check = data_to_analyse[i + 1:i + 2].isna()
                    if len(category_check.loc[(category_check[category_check.columns[1]] == True) & (
                            category_check[category_check.columns[2]] == True)]) > 0:
                        category_value = (data_to_analyse.iloc[i].values[0])
                    else:
                        subcategory_value = (data_to_analyse.iloc[i].values[0])

                if category_value:
                    category.append(category_value)
                else:
                    category.append(np.nan)

                if subcategory_value:
                    subcategory.append(subcategory_value)
                else:
                    subcategory.append(np.nan)

            data_to_analyse['Category'] = category
            data_to_analyse['Subcategory'] = subcategory
            boolean_drop = data_to_analyse.isna()
            df_bool = boolean_drop.loc[
                (boolean_drop[boolean_drop.columns[1]] == True) & (boolean_drop[boolean_drop.columns[2]] == True)]
            data_to_analyse.drop(df_bool.index, inplace=True)
            data_to_analyse['Line'] = data_to_analyse.index
            data_to_analyse.reset_index(inplace=True)
            last_catagory = category[-1]
            last_subcategory = subcategory[-1]
            if 'index' in data_to_analyse.columns:
                data_to_analyse.drop(['index'], axis=1, inplace=True)
            if len(data_to_analyse['Category']) == data_to_analyse['Category'].isna().sum():
                data_to_analyse.rename(columns={'Category': 'Subcategory', 'Subcategory': 'Category'}, inplace=True)
            data_to_analyse = data_to_analyse.loc[:, ~data_to_analyse.columns.str.contains('^Unnamed')]
            data_to_analyse.to_excel(writer, sheet_name='Table' + str(j), encoding='utf-8')



    writer.save()