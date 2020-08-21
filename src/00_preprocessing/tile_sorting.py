# Step 1: build pandas dataframe -> patientID | nr_tiles | class (normal, LUSC, LUAD)
# Step 2: assign patients into train, valid, test set
# - assign per class
# - assign patients such that the one with the highest nr_tiles is taken first
# - first fill test, then validation set, rest goes into training
# Step 3: create csv file
# -output csv file for each test/train/valid -> slidepath, class

# Import libraries
import os 
from argparse import ArgumentParser
from glob import glob
import json
from collections import defaultdict
import pandas as pd

SORTING_OPTIONS = {'1': {'normal':0, 'luad':1, 'lusc':1}, '2': {'luad':1, 'lusc':2}, '3': {'normal':0, 'luad':1, 'lusc':2}}


class statistics_tracker():
    # Keep track of the amount of tiles in training, test and validation set
    def __init__(self, nr_tiles):
        self.nr_tiles_categ = {}
        self.nr_tiles_categ['total'] = nr_tiles
        self.nr_tiles_categ['valid'] = 0
        self.nr_tiles_categ['test'] = 0
        
        self.percent_tiles_categ = {}
        self.percent_tiles_categ['test'] = 0
        self.percent_tiles_categ['valid'] = 0

    def assign(self, patient, nr_tiles, patient_to_category):
        ''' Assign patient to a category: train, test or validation '''
        if self.percent_tiles_categ['test'] < 0.15:
            category = 'test'
        elif self.percent_tiles_categ['valid'] < 0.15:
            category = 'valid' 
        else:
            category = 'train'
        
        patient_to_category[patient] = category
        self._update(category, nr_tiles)

    def _update(self, category, nr_tiles):
        if category in ['test', 'valid']:
            self.nr_tiles_categ[category] += nr_tiles
            self.percent_tiles_categ[category] = float(self.nr_tiles_categ[category] / self.nr_tiles_categ['total'])


def is_cancer(metadata):
    sample_type = metadata['cases'][0]['samples'][0]['sample_type']
    if 'normal' in sample_type.lower():
        return False
    return True


def extract_class(metadata):
    if is_cancer(metadata):
        subtype = metadata['cases'][0]['project']['project_id'][5:]
        return subtype.lower()
    else:
        return 'normal'

def get_classes(sorting_option):
    return SORTING_OPTIONS[sorting_option]

def create_patient_meta(slide_folders, json_data):
    # Step 1
    patient_meta = defaultdict(lambda: [0, None])
    for folder in slide_folders:
        slide_name = os.path.basename(folder).replace('_files', '')
        slide_meta = json_data[slide_name] 
        nr_tiles_slide = len([x for x in os.listdir(os.path.join(folder, '20.0')) if x.endswith('.jpeg')])
        patientID = slide_name[:12]

        # Check if we already have the information, otherwise get them
        if patientID not in patient_meta:
            patient_meta[patientID][0] += nr_tiles_slide
            patient_class = extract_class(slide_meta) 
            patient_meta[patientID][1] = patient_class
        else: 
            patient_meta[patientID][0] += nr_tiles_slide
    
    patient_meta = pd.DataFrame.from_dict(patient_meta, orient='index', columns=['nr_tiles', 'class']).reset_index()
    patient_meta.rename({'index':'patientID'}, axis='columns', inplace=True)
    patient_meta.sort_values(by=['nr_tiles'], ascending=False, inplace=True) # sort decending wrt nr_tiles
    return patient_meta


def assign_patients_to_category(patient_meta, classes):
    # Step 2
    # Assign patients to a category (train, test, valid) separately per class 
    patient_to_category = dict() 
    for c in classes:
        patient_meta_c = patient_meta[patient_meta['class'] == c] 
        nr_all_tiles = patient_meta_c['nr_tiles'].sum()
        statistics = statistics_tracker(nr_all_tiles)

        for i, row in patient_meta_c.iterrows():
            patient, nr_tiles_patient = row['patientID'], row['nr_tiles']
            statistics.assign(patient, nr_tiles_patient, patient_to_category)
    
    return patient_to_category


def write_csv_files(slide_folders, output_folder, patient_meta, patient_to_category, classes):
    # Step 3
    path_train = os.path.join(output_folder, 'csv_train.csv')
    path_test = os.path.join(output_folder, 'csv_test.csv')
    path_valid = os.path.join(output_folder, 'csv_valid.csv')

    with open(path_train, 'w') as csv_train, open(path_test, 'w') as csv_test, open(path_valid, 'w') as csv_valid:
        output_csv = {'train': csv_train, 'test': csv_test, 'valid': csv_valid}
        # Add header to the csv files
        for csv in output_csv.values(): 
            csv.write('path,reference_value\n')

        # Fill csv files
        for folder in slide_folders:
            tiles = os.listdir(os.path.join(folder, '20.0'))
            tiles = [os.path.join(folder, '20.0', t) for t in tiles] # get full paths 
            tiles = [os.path.relpath(t, start=output_folder) for t in tiles] # convert to paths relative to output directory
            for tile in tiles:
                patient = tile.split('/')[-3][:12]
                patient_class = patient_meta[patient_meta['patientID'] == patient]['class'].to_string(index=False).strip()
                patient_class = str(classes[patient_class]) # get the "number" corresponding to the class
                category = patient_to_category[patient]
                output_csv[category].write(','.join([tile, patient_class]))
                output_csv[category].write('\n')


def run(source_folder, json_file, output_folder, sorting_option):
    # Extract all slide folders from the source foulder
    slide_folders = glob(os.path.join(args.source_folder, '*_files'))

    # Load provided JSON file containing the metadata  
    if not '.json' in args.json_file:
        raise ValueError('Please provide a metadata file in JSON format.')
    else: 
        with open(args.json_file) as json_file: 
            json_data = json.loads(json_file.read())
            json_data = dict((jd['file_name'].replace('.svs', ''), jd) for jd in json_data) # convert to dict
    
    # Get classes for the chosen sorting option
    classes = get_classes(sorting_option)

    # Step 1
    patient_meta = create_patient_meta(slide_folders, json_data)
    # Step 2
    patient_to_category = assign_patients_to_category(patient_meta, classes)
    # Step 3
    write_csv_files(slide_folders, output_folder, patient_meta, patient_to_category, classes)


if __name__ == '__main__':

    description = """ TODO
    Always sorting >= 15 percent into test, >= 15 percent into validation and rest into training
     """ 
    parser = ArgumentParser(description=description)

    parser.add_argument("source_folder", 
                        help="Path to the tiled images")
    parser.add_argument("json_file", 
                        help="Path to metadata file in json format")
    parser.add_argument("output_folder", 
                        help="Path to output folder")
    parser.add_argument("sorting_option", 
                        help="Specify the sorting option")

    args = parser.parse_args()

    run(args.source_folder, args.json_file, args.output_folder, args.sorting_option)
    
    

    

    
    
    
    

                


        