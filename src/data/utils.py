import os
import pandas as pd
import subprocess
from openslide import open_slide

from src.data.tile_generation_cptac import _get_path_to_slide_from_gcs_url


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
    complete_df.rename(columns={'dataset': 'cancer_subtype'}, inplace=True)
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


def get_thumbnail(slide_ids, metadata_path, output_folder, google_cloud_project_id):  
    slides_metadata = pd.read_csv(metadata_path)
    for slide_id in slide_ids: 
        print('Generate thumbnail for slide %s' %(slide_id))
        gcs_url = slides_metadata[slides_metadata['slide_id']==slide_id]['gcs_url'].item()
        # Download slide
        path_to_slide = _get_path_to_slide_from_gcs_url(gcs_url, output_folder) 
        cmd = ['gsutil -u {id} cp {url} {local_dir}'.format(id=google_cloud_project_id, url=gcs_url, local_dir=os.path.dirname(path_to_slide))]
        subprocess.run(cmd, shell=True)
        # Open slide and generate thumbnail. Afterwards delete the slide.
        slide = open_slide(path_to_slide)
        thumbnail = slide.get_thumbnail((300,300)) # get and save thumbnail image
        thumbnail.save(os.path.join(os.path.dirname(path_to_slide), slide_id + '.png'))
        os.remove(path_to_slide)