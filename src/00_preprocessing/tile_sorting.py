# Step 1: build pandas dataframe -> patientID | nr_tiles | class (normal, LUSC, LUAD)
# Step 2: sort patients into train, valid, test set
# - sorting per class
# - sort patients such that the one with the highest nr_tiles is taken first
# - first fill test, then validation set, rest comes into training
# - output csv file for each test/train/valid -> slidepath, class

# Import libraries
import os 
from argparse import ArgumentParser
from glob import glob
import json
from collections import defaultdict
import pandas as pd

def is_cancer(metadata):
    sample_type = metadata['cases'][0]['samples'][0]['sample_type']
    if 'normal' in sample_type.lower():
        return False
    return True

def extract_class(metadata):
    if is_cancer(metadata):
        subtype = metadata['cases'][0]['project']['project_id'][5:]
        return subtype
    else:
        return 'normal'


if __name__ == '__main__':

    description = """ TODO
    Always sorting >= 15 percent into test, >= 15 percent into validation and rest into training
     """ 
    parser = ArgumentParser(description=description)

    parser.add_argument("source_folder", 
                        help="Path to the tiled images")
    parser.add_argument("json_file", 
                        help="Path to metadata file in json format")
    parser.add_argument("--magnification", 
                        help="Magnification to use", type=float, default=20, 
                        dest='magnification')

    args = parser.parse_args()
    
    # Extract all slide folders from the source foulder
    slide_folders = glob(os.path.join(args.source_folder, '*_files'))

    # Load provided JSON file containing the metadata  
    if not '.json' in args.json_file:
        raise ValueError('Please provide a metadata file in JSON format.')
    else: 
        with open(args.json_file) as json_file: 
            json_data = json.loads(json_file.read())
            json_data = dict((jd['file_name'].replace('.svs', ''), jd) for jd in json_data) # convert to dict

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
    
    patient_meta = pd.DataFrame.from_dict(patient_meta, orient='index', columns=['nr_tiles', 'class'])
    patient_meta.sort_values(by=['nr_tiles'], ascending=False, inplace=True) # sort decending wrt nr_tiles

    # Step 2
    # keep track of the amount of tiles in training, test and validation set
    # Sort separately per class 