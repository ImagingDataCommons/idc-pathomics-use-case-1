""" 
TODO Documentation + Licence 
based on: <https://github.com/ncoudray/DeepPATH/blob/master/DeepPATH_code/00_preprocessing/0d_SortTiles.py>

""" 
# Import libraries 
import os 
from argparse import ArgumentParser
from glob import glob
import json
import random 
from collections import defaultdict

# TODO 
# - argsparse variable style einheitlich und wie in tile-generation 
# - argsparse define range of variables, optional and mandatory arguments etc. 
# - where is the mutation data stuff? 

class TileSorter():
    """ TODO""" 
    pass


def extract_cancer(metadata):
    return metadata['cases'][0]['project']['project_id']

def extract_sample_type(metadata):
    return metadata['cases'][0]['samples'][0]['sample_type']

def sort_type(metadata, **kwargs):
    cancer = extract_cancer(metadata)
    sample_type = extract_sample_type(metadata)
    if "Normal" in sample_type:
        return sample_type.replace(' ', '_')
    return cancer 

sort_options = [sort_type, 'test']

if __name__ == '__main__':

    description = """ TODO
    we need sorting options: 
    - classification cancer vs. normal tissue --> 6 ??
    - classification luad vs. lusc --> 4 
    - classification luad. vs. lusc vs. cancer --> 3 
    - gene mutations luad 
    Sorting options can be extended
    
     """ 
    parser = ArgumentParser(description=description)

    parser.add_argument("SourceFolder", 
                        help="Path to the tiled images")
    parser.add_argument("JsonFile", 
                        help="Path to metadata file in json format")
    #parser.add_argument("--MagDiffAllowed", 
    #                    help="difference allowed on Magnification", type=float, # probably not necessary as coudray uses 0 !! 
    #                    dest='MagDiffAllowed')
    parser.add_argument("SortingOption", 
                        help="See options given in the description", type=int, choices=[0,1,2]) 
    parser.add_argument("--Magnification", 
                        help="Magnification to use", type=float, default=20., 
                        dest='Magnification')
    parser.add_argument("--PercentValid", 
                        help="Percentage of images for validation (between 0 and 100, default: 15) ", metavar='[0-100]', type=float, choices=range(0,101), default=15,
                        dest='PercentValid')
    parser.add_argument("--PercentTest", help="Percentage of images for testing (between 0 and 100, default: 15)", metavar='[0-100]', type=float, choices=range(0,101), default=15, 
                        dest='PercentTest')
    parser.add_argument("--PatientID",
                        help="Patient ID is supposed to be the first PatientID characters (integer expected) of the folder in which the pyramidal jpgs are [0]." \
                             "Slides from same patient will be in same train/test/valid set. This option is ignored if set to 0 or -1 ", type=int, default=0,
                        dest='PatientID')
    #parser.add_argument("--TMB", help="Path to json file with mutational loads; or to BRAF mutations", dest='TMB')
    #parser.add_argument("--nSplit", 
    #                    help="Integer n: Split into train/test in n different ways [0].", type=int, default=0, 
    #                    dest='nSplit')                                      # not yet understood what this is doing --> we do not need to modify this I guess. 
    parser.add_argument("--Balance", 
                        help="Balance datasets by: 0 - tiles (default); 1 - slides; 2 - patients (have to provide PatientID) [0]", type=int, choices=[0,1,2], default=0, 
                        dest='balance')
    #parser.add_argument("--outFilenameStats",
    #                    help="Check if the tile exists in an out_filename_Stats.txt file and copy it only if it True, or is the expLabel option had the highest probability",
    #                   dest='outFilenameStats')
    #parser.add_argument("--expLabel",
    #                    help="Index of the expected label within the outFilenameStats file (if only True/False is needed, leave this option empty). comma separated string expected",
    #                    dest='expLabel')
    ##parser.add_argument("--threshold",
    #                    help="threshold above which the probability the class should be to be considered as true (if not specified, it would be considered as true if it has the max probability). comma separated string expected",
    #                    dest='threshold')
    parser.add_argument("--outputtype",
                        help="Type of output: list source/destination in a file (file), do symlink (symlink, default) or both (both)", choices=['file', 'symlink', 'both'], default='symlink', 
                        dest='outputtype')

    args = parser.parse_args()

    # Extract all separate image folders from the source foulder
    args.SourceFolder = os.path.abspath(args.SourceFolder)
    img_folders = glob(os.path.join(args.SourceFolder, '*_files'))
    print('test', img_folders)
    random.shuffle(img_folders) # randomize order of the images

    # Load provided JSON file containing the metadata and prepare the information we need. 
    if not '.json' in args.JsonFile:
        raise ValueError('Please provide a metadata file in JSON format.')
    else: 
        with open(args.JsonFile) as json_file: 
            json_data = json.loads(json_file.read())
        try:
            json_data = dict((jd['file_name'].replace('.svs', ''), jd) for jd in json_data)
        except:
            raise KeyError('Cannot find "file_name" as key in the json data.')

    # Extract the sorting option 
    try: 
        sort_function = sort_options[args.SortingOption-1] # use -1 to transform to zero-based index
    except IndexError:
        raise ValueError('Unknown sorting option specified.')

    
    print('==========================================================')
    classes = defaultdict(list) 
    patient_set = {}
    nr_tiles_categ =  {} # number of tiles per category, category = train/validation/test
    percent_tiles_categ = {} # percentage of tiles per category
    nr_slides_categ = {} # number of images per category
    percent_slides_categ = {} # percentage of images per category
    nr_patients_categ = {} # number of patients per category
    percent_patients_categ = {} # percentage of patients per category
    

    # Extract metadata for each image folder and what else?????
    for folder in img_folders:
        folder_root = os.path.basename(folder).replace('_files', '')
        try:
            image_meta = json_data[folder_root] 
        except KeyError:
            print('File name %s not found in metadata.' %(folder_root))
            try: 
                image_meta = json_data[folder_root[:args.PatientID]]
            except KeyError:
                print('File name %s not found in metadata.' %(folder_root[:args.PatientID]))
        
        sub_dir = sort_function(image_meta) # get sorting category e.g. normal, TCGA-LUAD, TCGA-LUSC
        if sub_dir is None: 
            print('Slide is not valid for this sorting option and is skipped.')
            continue 
        if not os.path.exists(sub_dir):
            os.makedirs(sub_dir)
        classes[sub_dir].append(folder_root)

        
        # Check in the reference directories whether there is a set of tiles at the desired magnification 
        avail_mag = [float(x) for x in os.listdir(folder) if os.path.isdir(os.path.join(folder, x))]
        if max(avail_mag) < 0: 
            print('Magnification not known for that slide. The slide is skipped. ')
            continue
        elif float(args.Magnification) not in avail_mag: 
            print('Desired magnification not available. This slide is skipped. ')
            continue 

        # Sorting tiles into the appropriate sorting category (e.g. normal, LUAD, LUSC)
        print('Sorting tiles into subdirectory %s...' %(sub_dir))
        source_dir = os.path.join(folder, str(args.Magnification), '*')
        all_tiles = glob(source_dir)
        print('Number of tiles: ' + str(len(all_tiles)))
        if len(all_tiles) == 0:
            continue 

        # Initialize statistics for balancing if not already done 
        if sub_dir in nr_tiles_categ.keys():
            pass 
        else: 
            nr_tiles_categ[sub_dir] = 0
            nr_tiles_categ[sub_dir + '_train'] = 0
            nr_tiles_categ[sub_dir + '_valid'] = 0
            nr_tiles_categ[sub_dir + '_test'] = 0
            
            percent_tiles_categ[sub_dir + '_train'] = 0
            percent_tiles_categ[sub_dir + '_valid'] = 0
            percent_tiles_categ[sub_dir + '_test'] = 0
            
            nr_slides_categ[sub_dir] = 0
            nr_slides_categ[sub_dir + '_train'] = 0
            nr_slides_categ[sub_dir + '_valid'] = 0
            nr_slides_categ[sub_dir + '_test'] = 0
            
            percent_slides_categ[sub_dir + '_train'] = 0
            percent_slides_categ[sub_dir + '_valid'] = 0
            percent_slides_categ[sub_dir + '_test'] = 0
            
            nr_patients_categ[sub_dir] = 0
            nr_patients_categ[sub_dir + '_name-list'] = {}
            nr_patients_categ[sub_dir + '_train'] = 0
            nr_patients_categ[sub_dir + '_valid'] = 0
            nr_patients_categ[sub_dir + '_test'] = 0

            percent_patients_categ[sub_dir + '_train'] = 0
            percent_patients_categ[sub_dir + '_valid'] = 0
            percent_patients_categ[sub_dir + '_test'] = 0

        nr_tiles = 0
        ttv = 'None'
        for tile_path in all_tiles:
            tile_name = os.path.basename(tile_path)

            # Balancing wrt tiles (0), slides (1), patients (2)
            if args.balance == 0: 
                # rename images with the root name and put them in train/test/valid 
                if percent_tiles_categ.get(sub_dir + '_test') <= args.PercentTest/100 and args.PercentTest/100 > 0:
                    ttv = 'test'
                elif percent_tiles_categ.get(sub_dir + '_valid') <= args.PercentValid/100 and args.PercentValid/100 > 0: 
                    ttv = 'valid'
                else:
                    ttv = 'train'
            elif args.balance == 1: 
                if percent_slides_categ.get(sub_dir + '_test') <= args.PercentTest/100 and args.PercentTest/100 > 0:
                    ttv = 'test'
                elif percent_slides_categ.get(sub_dir + '_valid') <= args.PercentValid/100 and args.PercentValid/100 > 0: 
                    ttv = 'valid'
                else:
                    ttv = 'train'
            else: 
                if percent_patients_categ.get(sub_dir + '_test') <= args.PercentTest/100 and args.PercentTest/100 > 0:
                    ttv = 'test'
                elif percent_patients_categ.get(sub_dir + '_valid') <= args.PercentValid/100 and args.PercentValid/100 > 0: 
                    ttv = 'valid'
                else:
                    ttv = 'train'

        ## ????? 
        if args.PatientID > 0: 
            patient = folder_root[:args.PatientID]
        else: 
            patient = folder_root
            print('patient folder', patient, folder_root)

            if True: 
                # Check if patient is in this particular class 
                if patient not in nr_patients_categ[sub_dir + '_name-list'].keys():
                    # Check if patient in ANY class is train, valid or test 
                    if patient in patient_set: 
                        ttv = patient_set[patient]
                        nr_patients_categ[sub_dir + '_name-list'][patient] = patient_set[patient]
                    else: 
                        patient_set[patient] = ttv 
                        nr_patients_categ[sub_dir + '_name-list'][patient] = ttv 
                    if nr_tiles == 1: 
                        new_patient = True 

                else: 
                    # it is in the class -> not a new patient
                    ttv = patient_set[patient]
                    if nr_tiles == 1: 
                        new_patient = False 
                
        new_image_dir = os.path.join(sub_dir, '_'.join((ttv, folder_root, tile_name)))
        ### here goes the linking/writing into csv files whatever we want to do

        # Update statistics
        nr_tiles_categ[sub_dir] += nr_tiles
        nr_slides_categ[sub_dir] += 1
        if new_patient: 
            nr_patients_categ[sub_dir] += 1

        if ttv == 'train':
            if new_patient: 
                nr_patients_categ[sub_dir + '_train'] += 1
            nr_tiles_categ[sub_dir + '_train'] += nr_tiles
            nr_slides_categ[sub_dir + '_train'] += + 1
        elif ttv == 'test':
            if new_patient: 
                nr_patients_categ[sub_dir + '_test'] += 1
            nr_tiles_categ[sub_dir + '_test'] += nr_tiles
            nr_slides_categ[sub_dir + '_test'] += + 1
        elif ttv == 'valid':
            if new_patient: 
                nr_patients_categ[sub_dir + '_valid'] += 1
            nr_tiles_categ[sub_dir + '_valid'] += nr_tiles
            nr_slides_categ[sub_dir + '_valid'] += + 1
        else:
            continue
        
        ### to be improved  
        print("New Patient: " + str(new_patient))
        print("nr_patients_categ[sub_dir]: " + str(nr_patients_categ[sub_dir]))
        print("imgRootName: " + str(imgRootName))

        percent_tiles_categ[sub_dir + '_train'] = float(nr_tiles_categ[sub_dir + '_train') / float(nr_tiles_categ[sub_dir]
        percent_tiles_categ[sub_dir + '_test'] = float(nr_tiles_categ[sub_dir + '_test') / float(nr_tiles_categ[sub_dir]
        percent_tiles_categ[sub_dir + '_valid'] = float(nr_tiles_categ[sub_dir + '_valid') / float(nr_tiles_categ[sub_dir]

        percent_slides_categ[sub_dir + '_train'] = float(nr_slides_categ[sub_dir + '_train') / float(nr_slides_categ[sub_dir]
        percent_slides_categ[sub_dir + '_test'] = float(nr_slides_categ[sub_dir + '_test') / float(nr_slides_categ[sub_dir]
        percent_slides_categ[sub_dir + '_valid'] = float(nr_slides_categ[sub_dir + '_valid') / float(nr_slides_categ[sub_dir]
        
        percent_patients_categ[sub_dir + '_train'] = float(nr_patients_categ[sub_dir + '_train') / float(nr_patients_categ[sub_dir]
        percent_patients_categ[sub_dir + '_test'] = float(nr_patients_categ[sub_dir + '_test') / float(nr_patients_categ[sub_dir]
        percent_patients_categ[sub_dir + '_valid'] = float(nr_patients_categ[sub_dir + '_valid') / float(nr_patients_categ[sub_dir]


        print("Done. %d tiles added to %s " % (nr_tiles, sub_dir))
        print("Train / Test / Validation tiles sets for %s = %f %%  / %f %% / %f %%" % (
            sub_dir, percent_tiles_categ[sub_dir + '_train'], percent_tiles_categ[sub_dir + '_test'], percent_tiles_categ[sub_dir + '_valid'])

        print("Train / Test / Validation slides sets for %s = %f %%  / %f %% / %f %%" % (
            sub_dir, percent_slides_categ[sub_dir + '_train'], percent_slides_categ[sub_dir + '_test'], percent_slides_categ[sub_dir + '_valid'])
        if args.PatientID > 0:
            print("Train / Test / Validation tiles sets for %s = %f %%  / %f %% / %f %%" % (
                sub_dir, percent_patients_categ[sub_dir + '_train'], percent_patients_categ[sub_dir + '_test'], percent_patients_categ[sub_dir + '_valid'])

    for k, v in sorted(classes.items()):
        print('list of images in class %s :' % k)
        print(v)
    for k, v in sorted(nr_tiles_categ.items()):
        print(k, v)
    for k, v in sorted(percent_tiles_categ.items()):
        print(k, v)
    for k, v in sorted(nr_slides_categ.items()):
        print(k, v)
    if args.PatientID > 0:
        for k, v in sorted(nr_patients_categ.items()):
            print(k, v)



        
            

            


