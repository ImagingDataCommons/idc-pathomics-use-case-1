import json

def read_metadata(metadata_file):
    with open(metadata_file) as f:
        mteadata = json.loads(f.read())
    # extract relevant information and generate dict of patient-id -> information

def get_all_patches(data_dir):
    

def split_data_cancer_type(data_dir, metadata_file, output_dir):
    metadata = read_metadata(metadata_file)