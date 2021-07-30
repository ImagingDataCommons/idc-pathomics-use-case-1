import pandas as pd


def attach_tissue_type_information(cohort_df: pd.DataFrame, tissue_type_data: pd.DataFrame):
    tissue_types = []
    for i, row in cohort_df.iterrows():
        slide_id = row['slide_id']
        try: 
            tissue_type = tissue_type_data[tissue_type_data['Slide_ID'] == slide_id]['Specimen_Type'].item()
            tissue_types.append(tissue_type)
        except: 
            cohort_df = cohort_df.drop(index=i)
    complete_df = _add_column_to_dataframe(cohort_df, tissue_types)
    
    # Replace certain column values for clarity
    complete_df.replace({'cancer_subtype': 'CPTAC-LSCC'}, 'lscc', inplace=True)
    complete_df.replace({'cancer_subtype': 'CPTAC-LUAD'}, 'luad', inplace=True)
    complete_df.replace({'tissue_type': 'normal_tissue'}, 'normal', inplace=True)
    complete_df.replace({'tissue_type': 'tumor_tissue'}, 'tumor', inplace=True)
    complete_df.sort_values('slide_id')
    return complete_df

def _add_column_to_dataframe(dataframe, column): 
    assert len(dataframe) == len(column), 'Number of new column values not matching length of dataframe.'
    dataframe.insert(3, 'tissue_type', column)
    return dataframe    