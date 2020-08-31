# Import libraries
import os 
from argparse import ArgumentParser
from glob import glob
import json
from collections import defaultdict
import pandas as pd

SORTING_OPTIONS = {1: {'normal':0, 'luad':1, 'lusc':1}, 2: {'luad':0, 'lusc':1}, 3: {'normal':0, 'luad':1, 'lusc':2}}
SORTING_SUFFIX = {1: 'norm_cancer', 2: 'luad_lusc', 3: 'norm_luad_lusc'}

def run_tile_sorting(source_folder, json_file, output_folder, sorting_option):
    """ 
    Sort the tiles by one of the following three options. 
    Stores separate csv files for training, test and validation set, each in the format "path, reference_class" 
        > 1: 'normal' vs. 'cancer'
        > 2: 'cancer subtype LUAD' vs. 'cancer subtype LUSC'
        > 3: 'normal' vs. 'LUAD' vs. 'LUSC'

    Args:
        source_folder (str): absolute path to the folder containing the all tiles (in separate subfolders per slide)
        json_file (str): absolute path to JSON file containing the metadata (information about classes etc.)
        output_folder (str): absolute path to the output folder where to store the csv files
        sorting_option (int): one of the three above-mentioned sorting options specified by the respective identifier

    Returns:
        None
    """

    # Extract all slide folders from the source foulder
    slide_folders = glob(os.path.join(source_folder, '*_files'))

    # Load provided JSON file containing the metadata  
    if not '.json' in json_file:
        raise ValueError('Please provide a metadata file in JSON format.')
    else: 
        with open(json_file) as json_file: 
            json_data = json.loads(json_file.read())
            json_data = dict((jd['file_name'].replace('.svs', ''), jd) for jd in json_data) # convert to dict
    
    # Get classes for the chosen sorting option
    try: 
        classes = get_classes(sorting_option)
        if sorting_option == 1: 
            print('Sorting NORMAL vs. CANCER')
        elif sorting_option == 2: 
            print('Sorting LUAD vs. LUSC')
        else: 
            print('Sorging NORMAL vs. LUAD vs. LUSC')
    except: 
        raise ValueError('Please specify a valid sorting option.')

    # Step 1: build internally used dataframe in the format: patientID | nr_tiles | class (normal, LUSC, LUAD)
    patient_meta = create_patient_meta(slide_folders, json_data)
    # Step 2: assign patients to training, valididation or test set
    patient_to_category = assign_patients_to_category(patient_meta, classes)
    # Step 3: write output files
    write_csv_files(slide_folders, output_folder, patient_meta, patient_to_category, classes, sorting_option)


def get_classes(sorting_option):
    return SORTING_OPTIONS[sorting_option]


def create_patient_meta(slide_folders, json_data):
    patient_meta = defaultdict(lambda: [0, None]) # store nr_tiles and class per patient

    for folder in slide_folders:
        metadata, nr_tiles, patientID = get_info_about_slide(folder, json_data)
        if patientID not in patient_meta:
            patient_class = extract_class(metadata)
            patient_meta[patientID][0] += nr_tiles
            patient_meta[patientID][1] = patient_class
        else: 
            patient_meta[patientID][0] += nr_tiles
    
    return convert_to_sorted_dataframe(patient_meta)

def get_info_about_slide(folder, json_data):
    slide_name = os.path.basename(folder).replace('_files', '')
    metadata = json_data[slide_name] 
    nr_tiles = len([x for x in os.listdir(os.path.join(folder, '20.0')) if x.endswith('.jpeg')])
    patientID = slide_name[:12]
    return metadata, nr_tiles, patientID

def extract_class(metadata):
    if is_cancer(metadata):
        subtype = metadata['cases'][0]['project']['project_id'][5:]
        return subtype.lower()
    else:
        return 'normal'

def is_cancer(metadata):
    sample_type = metadata['cases'][0]['samples'][0]['sample_type']
    if 'normal' in sample_type.lower():
        return False
    return True

def convert_to_sorted_dataframe(patient_meta):
    patient_meta = pd.DataFrame.from_dict(patient_meta, orient='index', columns=['nr_tiles', 'class']).reset_index()
    patient_meta.rename({'index':'patientID'}, axis='columns', inplace=True)
    return patient_meta


def assign_patients_to_category(patient_meta, classes):
    # Assign patients to a category (training, validation, test) separately per class 
    patient_to_category = dict() 
    for c in classes:
        patient_meta_c = patient_meta[patient_meta['class'] == c] 
        assign_patients(patient_meta_c, patient_to_category)
    return patient_to_category

def assign_patients(patient_meta, patient_to_category):
    nr_all_tiles = patient_meta['nr_tiles'].sum()
    nr_tiles_to_test = int(0.15 * nr_all_tiles)
    nr_tiles_to_valid = int(0.15 * nr_all_tiles)

    for i, row in patient_meta.iterrows():
        patient, nr_tiles_patient = row['patientID'], row['nr_tiles']

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


def write_csv_files(slide_folders, output_folder, patient_meta, patient_to_category, classes, sorting_option):
    suffix = SORTING_SUFFIX[sorting_option]
    path_train = os.path.join(output_folder, 'csv_train_' + suffix + '.csv')
    path_test = os.path.join(output_folder, 'csv_test_' + suffix + '.csv')
    path_valid = os.path.join(output_folder, 'csv_valid_' + suffix + '.csv')

    with open(path_train, 'w') as csv_train, open(path_test, 'w') as csv_test, open(path_valid, 'w') as csv_valid:
        output_csv = {'train': csv_train, 'test': csv_test, 'valid': csv_valid}
        # Add header
        for csv in output_csv.values(): 
            csv.write('path,reference_value\n')

        # Fill csv files
        for slide_folder in slide_folders:
            write_info(slide_folder, output_csv, output_folder, patient_meta, patient_to_category, classes)
            

def write_info(slide_folder, output_csv, output_folder, patient_meta, patient_to_category, classes):
    tiles = os.listdir(os.path.join(slide_folder, '20.0'))
    tiles = [os.path.join(slide_folder, '20.0', t) for t in tiles] # get full paths 
    tiles = [os.path.relpath(t, start=output_folder) for t in tiles] # convert to paths relative to output directory
    
    patient = slide_folder.split('/')[-1][:12]
    patient_class = patient_meta[patient_meta['patientID'] == patient]['class'].to_string(index=False).strip()
    patient_class = str(classes[patient_class]) 
    category = patient_to_category[patient]
    
    for tile in tiles:    
        output_csv[category].write(','.join([tile, patient_class]))
        output_csv[category].write('\n')


if __name__ == '__main__':

    parser = ArgumentParser()

    parser.add_argument("source_folder", 
                        help="Path to the tiled images")
    parser.add_argument("json_file", 
                        help="Path to metadata file in json format")
    parser.add_argument("output_folder", 
                        help="Path to output folder")
    parser.add_argument("sorting_option", 
                        help="Specify the sorting option")

    args = parser.parse_args()

    #run_tile_sorting(args.source_folder, args.json_file, args.output_folder, args.sorting_option)
    
    

    

    
    
    
    

                


        