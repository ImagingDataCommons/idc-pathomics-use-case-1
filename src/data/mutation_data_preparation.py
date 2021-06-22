import os 
import json
import pandas as pd
from glob import glob 
from collections import defaultdict
from typing import List, Dict

MUTATION_LABELS = {'stk11':0, 'egfr':1, 'setbp1':2, 'tp53':3, 'fat1':4, 'kras':5, 'keap1':6, 'lrp1b':7, 'fat4':8, 'nf1':9}


def prepare_mutation_data(source_folder: str, mutations_gt_path: str, tiles_predicted_as_luad: str = None) -> None:
    slide_folders = glob(os.path.join(source_folder, 'tiles', '*_files'))

    mutations_per_patient = _get_mutations_per_patient(mutations_gt_path)

    patient_meta_path = os.path.join(source_folder, 'patient_meta_20x.csv')
    if not os.path.isfile(patient_meta_path): 
        raise ValueError('File patient_meta.csv not found.')
    else:
        patient_meta = pd.read_csv(patient_meta_path)
        #patient_meta = patient_meta.sample(frac=1, random_state=3) # shuffle rows to permit randomized assignment of patients to categories
        patient_to_category = _assign_patients_to_category(patient_meta, mutations_per_patient)

    slides_meta_path = os.path.join(source_folder, 'slides_meta.csv')
    if not os.path.isfile(slides_meta_path): 
        raise ValueError('File slides_meta.csv not found.')
    else: 
        with open(slides_meta_path, 'r') as slides_meta_file: 
            slides_meta = json.loads(slides_meta_file.read())
    
    if tiles_predicted_as_luad: 
        luad_tiles = _load_predicted_as_luad(tiles_predicted_as_luad)
        _write_csv_files(slide_folders, source_folder, patient_to_category, mutations_per_patient, slides_meta, luad_tiles)
    else: 
        _write_csv_files(slide_folders, source_folder, patient_to_category, mutations_per_patient, slides_meta)

def _get_mutations_per_patient(mutations_gt_path: str) -> Dict[str, list]: 
    mutations_per_patient = defaultdict(list)
    with open(mutations_gt_path, 'r') as mutations_gt:
        for line in mutations_gt:
            line = line.strip().split(',')
            patient_id = line[0][:-2]
            mutation_string = line[1].lower()
            mutations_per_patient[patient_id].append(MUTATION_LABELS[mutation_string])
    return mutations_per_patient


def _assign_patients_to_category(patient_meta: pd.DataFrame, mutations_per_patient: Dict[str, list]) -> Dict[str, str]:
    # Assign patients to a category (training, validation, test)
    patient_meta_luad = patient_meta[patient_meta['cancer_subtype'] == 'luad'] # select luad patients
    patient_meta_luad = patient_meta_luad[patient_meta_luad['patientID'].isin(mutations_per_patient)] # select only patients with known mutations
    patient_to_category = _assign_patients(patient_meta_luad)
    print(patient_meta_luad)
    print(patient_to_category)
    return patient_to_category

def _assign_patients(patient_meta: pd.DataFrame) -> Dict[str, str]:
    patient_to_category = dict() 

    tiles_to_consider = 'nr_tiles_cancer' # >= than number of LUAD tiles finally used 
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

def _load_predicted_as_luad(predicted_luad_tiles):
    luad_tiles = []
    with open(predicted_luad_tiles, 'r') as predicted_luad_tiles_file:
        for line in predicted_luad_tiles_file:
            luad_tiles.append(line.strip())
    return luad_tiles


def _write_csv_files(slide_folders: str, output_folder: str, patient_to_category: Dict[str, str], mutations_per_patient: Dict[str, list], slides_meta: Dict[str, str], luad_tiles: List[str] = None) -> None:
    path_train = os.path.join(output_folder, 'csv_train_mutations_split1.csv')
    path_test = os.path.join(output_folder, 'csv_test_mutations_split1.csv')
    path_valid = os.path.join(output_folder, 'csv_valid_mutations_split1.csv')

    with open(path_train, 'w') as csv_train, open(path_test, 'w') as csv_test, open(path_valid, 'w') as csv_valid:
        output_csv = {'train': csv_train, 'test': csv_test, 'valid': csv_valid}
        # Add header
        for csv in output_csv.values(): 
            csv.write('path,reference_value\n')

        # Fill csv 
        for slide_folder in slide_folders:
            _write_info(slide_folder, output_csv, output_folder, patient_to_category, mutations_per_patient, slides_meta, luad_tiles)
            

def _write_info(slide_folder: str, output_csv: dict, output_folder: str, patient_to_category: Dict[str, str], mutations_per_patient: Dict[str, list], slides_meta: Dict[str, str], luad_tiles: List[str] = None) -> None:
    patient = slide_folder.split('/')[-1][:12]
    if patient in patient_to_category: 
        category = patient_to_category[patient]
        mutations = mutations_per_patient[patient]
        mutations.sort()
        mutations = ';'.join([str(m) for m in mutations])
        slide_id = slide_folder.split('/')[-1]
        slide_class = slides_meta[slide_id]
        if slide_class == 'luad':
            tiles = os.listdir(os.path.join(slide_folder, '20.0'))
            tiles = [os.path.join(slide_folder, '20.0', t) for t in tiles] # get full paths 
            tiles = [os.path.relpath(t, start=output_folder) for t in tiles] # convert to paths relative to output directory
            for tile in tiles:
                if luad_tiles is None: 
                    output_csv[category].write(','.join([tile, mutations]))
                    output_csv[category].write('\n')
                else: 
                    if tile in luad_tiles:  # only consider tiles that were predicted as luad
                        output_csv[category].write(','.join([tile, mutations]))
                        output_csv[category].write('\n')
                    

def prepare_mutation_data_as_binary_problem(path_multilabel_mutation_file: str, mutation: str) -> None: 
    mutation_label = MUTATION_LABELS[mutation]
    path_binary_mutation_file = _create_output_file_path(path_multilabel_mutation_file, mutation)

    with open(path_multilabel_mutation_file, 'r') as multilabel, open(path_binary_mutation_file, 'w') as binary:
        binary.write('path,reference_value\n') # Add header to output
        for line in multilabel:
            if not line.startswith('path'):
                tile = line.split(',')[0]
                labels = line.split(',')[1]
                if str(mutation_label) in labels: 
                    binary.write(','.join([tile, str(1)]))
                    binary.write('\n')
                else: 
                    binary.write(','.join([tile, str(0)]))
                    binary.write('\n')


def _create_output_file_path(input_path: str, mutation: str) -> str: 
    dirname = os.path.dirname(input_path)
    modified_basename = os.path.basename(input_path).split('.')[0] + '_' + str(mutation) + '.csv'
    return os.path.join(dirname, modified_basename)