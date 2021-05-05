import os 
import re 
from glob import glob
import json
from collections import defaultdict
import pandas as pd
from typing import List, Tuple, Dict, Any


SORTING_OPTIONS = {'norm_cancer': {'normal':0, 'luad':1, 'lusc':1}, 'luad_lusc': {'luad':0, 'lusc':1}, 'norm_luad_lusc': {'normal':0, 'luad':1, 'lusc':2}}


def sort_tiles(source_folder: str, json_file: str, output_folder: str, sorting_option: str) -> None:
    """ 
    Sort the tiles by one of the following three options while balancing classes to be distributed equally to training
    test and validation set. 
    Stores separate csv files for training, test and validation set, each in the format "path, reference_class" 
        > 'normal_cancer': 'normal' vs. 'cancer'
        > 'luad_lusc': 'cancer subtype LUAD' vs. 'cancer subtype LUSC'
        > 'normal_luad_lusc': 'normal' vs. 'LUAD' vs. 'LUSC'

    Args:
        source_folder (str): absolute path to the folder containing all tiles (in separate subfolders per slide)
        json_file (str): absolute path to JSON file containing the metadata (information about classes etc.)
        output_folder (str): absolute path to the output folder where to store the csv files
        sorting_option (int): one of the three above-mentioned sorting options specified by the respective identifier

    Returns:
        None
    """

    slide_folders = glob(os.path.join(source_folder, '*_files'))

    if not '.json' in json_file:
        raise ValueError('Please provide a metadata file in JSON format.')
    else: 
        with open(json_file) as json_file: 
            json_data = json.loads(json_file.read())
            json_data = dict((jd['file_name'].replace('.svs', ''), jd) for jd in json_data) 
    
    classes = _get_classes(sorting_option)
    
    patient_meta_path = os.path.join(output_folder, 'patient_meta.csv')
    slides_meta_path = os.path.join(output_folder, 'slides_meta.csv')
    patient_meta = _get_patient_meta(patient_meta_path, slide_folders, json_data)
    slides_meta = _get_slides_meta(slides_meta_path, slide_folders, json_data)     
    patient_to_category = _assign_patients_to_category(patient_meta, classes) 
    _write_csv_files(slide_folders, output_folder, patient_to_category, slides_meta, classes, sorting_option)


def _get_classes(sorting_option: str) -> Dict[str, int]:
    try:
        return SORTING_OPTIONS[sorting_option]
    except:
        raise ValueError('Please specify a valid sorting option.')


def _get_patient_meta(patient_meta_path: str, slide_folders: str, json_data: Dict[Any, Any]) -> pd.DataFrame: 
    # load or generate internally used dataframe in the format: patientID | nr_tiles | class (normal, LUSC, LUAD)
    if os.path.isfile(patient_meta_path): 
        patient_meta = pd.read_csv(patient_meta_path)
    else: 
        patient_meta = _generate_patient_meta(slide_folders, json_data)
        patient_meta.to_csv(patient_meta_path, index=False)
    return patient_meta


def _generate_patient_meta(slide_folders: str, json_data: Dict[Any, Any]) -> pd.DataFrame:
    patient_meta = defaultdict(lambda: [0, 0, None]) # store nr_tiles_total, nr_tiles_cancer and cancer type per patient

    for slide_folder in slide_folders:
        metadata, nr_tiles, patientID = _get_info_about_slide(slide_folder, json_data)
        if patientID not in patient_meta:
            patient_cancer_type = _extract_patient_cancer_type(metadata) 
            patient_meta[patientID][2] = patient_cancer_type

        patient_meta[patientID][0] += nr_tiles 
        if _is_cancer_slide(metadata):
            patient_meta[patientID][1] += nr_tiles
    
    return _convert_to_dataframe(patient_meta)


def _get_slides_meta(slides_meta_path: str, slide_folders: str, json_data: Dict[Any, Any]) -> Dict[str, str]:
    if os.path.isfile(slides_meta_path): 
        with open(slides_meta_path, 'r') as slides_meta_file: 
            slides_meta = json.loads(slides_meta_file.read())
    else: 
        slides_meta = _generate_slides_meta(slide_folders, json_data)
        with open(slides_meta_path, 'w') as slides_meta_file:
            json.dump(slides_meta, slides_meta_file)
    return slides_meta


def _generate_slides_meta(slide_folders: str, json_data: Dict[Any, Any]) -> Dict[str, str]:
    slides_meta = defaultdict(lambda: None)
    for slide_folder in slide_folders:
        slide_id = slide_folder.split('/')[-1]
        metadata, nr_tiles, patientID = _get_info_about_slide(slide_folder, json_data)
        if _is_cancer_slide(metadata):
            slide_class = _extract_patient_cancer_type(metadata) 
        else: 
            slide_class = 'normal'
        slides_meta[slide_id] = slide_class
    return slides_meta


def _get_info_about_slide(folder: str, json_data: Dict[Any, Any]) -> Tuple[Dict[Any,Any], int, str]:
    slide_name = os.path.basename(folder).replace('_files', '')
    metadata = json_data[slide_name] 
    nr_tiles = len([x for x in os.listdir(os.path.join(folder, '20.0')) if x.endswith('.jpeg')])
    patientID = slide_name[:12]
    return metadata, nr_tiles, patientID


def _extract_patient_cancer_type(metadata: Dict[Any, Any]) -> str:
    subtype = metadata['cases'][0]['project']['project_id'][5:]
    return subtype.lower()


def _is_cancer_slide(metadata: Dict[Any, Any]) -> bool:
    sample_type = metadata['cases'][0]['samples'][0]['sample_type']
    if 'normal' in sample_type.lower():
        return False
    return True


def _convert_to_dataframe(patient_meta: Dict[str, list]) -> pd.DataFrame: 
    # TODO sort the dataframe?
    patient_meta = pd.DataFrame.from_dict(patient_meta, orient='index', columns=['nr_tiles_total', 'nr_tiles_cancer', 'cancer_subtype']).reset_index()
    patient_meta.rename({'index':'patientID'}, axis='columns', inplace=True)
    return patient_meta


def _assign_patients_to_category(patient_meta: pd.DataFrame, classes: Dict[str, int]) -> Dict[str, str]:
    # Assign patients to a category (training, validation, test) separately per patient subtype 
    patient_to_category = dict() 
    for c_type in ['luad', 'lusc']:  
        patient_meta_c = patient_meta[patient_meta['cancer_subtype'] == c_type] 
        _assign_patients(patient_meta_c, patient_to_category, classes)
    return patient_to_category


def _assign_patients(patient_meta: pd.DataFrame, patient_to_category: Dict[str, str], classes: Dict[str, int]) -> Dict[str, str]:
    if 'normal' not in classes:
        tiles_to_consider = 'nr_tiles_cancer'
    else: 
        tiles_to_consider = 'nr_tiles_total'

    nr_all_tiles = patient_meta[tiles_to_consider].sum() 
    nr_tiles_to_test = int(0.15 * nr_all_tiles)
    nr_tiles_to_valid = int(0.15 * nr_all_tiles)

    for i, row in patient_meta.iterrows():
        patient, nr_tiles_patient = row['patientID'], row[tiles_to_consider]

        # Assign patient to the test set -> if test is full,  assign to validation -> if validation is full, assign to training 
        if nr_tiles_to_test > 0: 
            category = 'test'
            nr_tiles_to_test = nr_tiles_to_test - nr_tiles_patient
        elif nr_tiles_to_valid > 0: 
            category = 'valid'
            nr_tiles_to_valid = nr_tiles_to_valid - nr_tiles_patient
        else: 
            category = 'train'
        patient_to_category[patient] = category

    return patient_to_category


def _write_csv_files(slide_folders: str, output_folder: str, patient_to_category: Dict[str, str], slides_meta: Dict[str, str], classes: Dict[str, int], sorting_option: str) -> None:
    path_train = os.path.join(output_folder, 'csv_train_' + sorting_option + '_5x.csv')
    path_test = os.path.join(output_folder, 'csv_test_' + sorting_option + '_5x.csv')
    path_valid = os.path.join(output_folder, 'csv_valid_' + sorting_option + '_5x.csv')

    with open(path_train, 'w') as csv_train, open(path_test, 'w') as csv_test, open(path_valid, 'w') as csv_valid:
        output_csv = {'train': csv_train, 'test': csv_test, 'valid': csv_valid}
        # Add header
        for csv in output_csv.values(): 
            csv.write('path,reference_value\n')

        # Fill csv files
        for slide_folder in slide_folders:
            _write_info(slide_folder, output_csv, output_folder, patient_to_category, slides_meta, classes)
            

def _write_info(slide_folder: str, output_csv: dict, output_folder: str, patient_to_category: Dict[str, str], slides_meta: Dict[str, str], classes: Dict[str, int]) -> None:
    slide_id = slide_folder.split('/')[-1]
    patient = slide_id[:12]
    if patient in patient_to_category: 
        category = patient_to_category[patient]
        slide_class = slides_meta[slide_folder]
        try: 
            slide_class = str(classes[slide_class]) 
        except: # this skips 'normal' slides in the second sorting option that only considers luad vs. lusc slides
            return 
        tiles = os.listdir(os.path.join(slide_folder, '20.0'))
        tiles = [os.path.join(slide_folder, '20.0', t) for t in tiles] # get full paths 
        tiles = [os.path.relpath(t, start=output_folder) for t in tiles] # convert to paths relative to output directory
        for tile in tiles:    
            output_csv[category].write(','.join([tile, slide_class]))
            output_csv[category].write('\n')