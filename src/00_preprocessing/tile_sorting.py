""" 
TODO Documentation + Licence 
based on: <https://github.com/ncoudray/DeepPATH/blob/master/DeepPATH_code/00_preprocessing/0d_SortTiles.py>

""" 
# Import libraries 
import os 
from argparse import ArgumentParser
from glob import glob
import random 

# TODO 
# - optparse variable style einheitlich und wie in tile-generation 
# - argsparse define range of variables
# - where is the mutation data stuff? 

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

    parser.add_argument("--SourceFolder", 
                        help="Path to the tiled images", 
                        dest='SourceFolder')
    parser.add_argument("--JsonFile", 
                        help="Path to metadata file in json format", 
                        dest='JsonFile')
    parser.add_argument("--Magnification", 
                        help="Magnification to use", type=float, 
                        dest='Magnification')
    parser.add_argument("--MagDiffAllowed", 
                        help="difference allowed on Magnification", type=float, # probably not necessary as coudray uses 0 
                        dest='MagDiffAllowed')
    parser.add_argument("--SortingOption", 
                        help="See options given in the description", type=int, 
                        dest='SortingOption') 
    parser.add_argument("--PercentValid", 
                        help="Percentage of images for validation (between 0 and 100)", type=float,
                        dest='PercentValid')
    parser.add_argument("--PercentTest", help="Percentage of images for testing (between 0 and 100)", type=float,
                        dest='PercentTest')
    parser.add_argument("--PatientID",
                        help="Patient ID is supposed to be the first PatientID characters (integer expected) of the folder in which the pyramidal jpgs are [0]." \
                             "Slides from same patient will be in same train/test/valid set. This option is ignored if set to 0 or -1 ", type=int, default=0,
                        dest='PatientID')
    #parser.add_argument("--TMB", help="Path to json file with mutational loads; or to BRAF mutations", dest='TMB')
    parser.add_argument("--nSplit", 
                        help="Integer n: Split into train/test in n different ways [0].", type=int, default=0, 
                        dest='nSplit')                                      # not yet understood what this is doing
    parser.add_argument("--Balance", 
                        help="Balance datasets by: 0 - tiles (default); 1 - slides; 2 - patients (have to provide PatientID) [0]", type=int, default=0, 
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
                        help="Type of output: list source/destination in a file (File), do symlink (Symlink, default) or both (Both)", default='Symlink',
                        dest='outputtype')

    args = parser.parse_args()

    # outputW = open('img_list.txt', 'w') check if stdout stuff should be written to a log file?!
    # Get images
    img_folders = glob(os.path.join(args.SourceFolder))
    random.shuffle(img_folders) # randomize order of the images

    # Read metadata from the provided JSON file
    if args.JsonFile is None: 
    print('No metadata JSON file found.')
    args.JsonFile = ''

    if not '.json' in :
        print('Please provide a metadata file in JSON format.')
        break
    else: 
        with open(args.JsonFile) as json_file: 
            json_data = json.loads(json_file.read())
        try: 
            json_data = dict((jd['file_name'].replace('.svs', ''), jd) for jd in json_data)
        except: 
            json_data = dict((jd['Patient ID'], jd) for jd in json_data) ???
    print('jdata: \n', json_data)

    # Extract the sorting option 
    try: 
        sort_function = sort_options[args.SortingOption-1] # use -1 to transform to zero-based index
    except IndexError:
        raise ValueError('Unknown sorting option specified.')

    # Walk through the other command line parameters --> can some of them be specified in argsparse directly???
    if args.nSplit > 0: 
        args.PercentValid = 100/args.nSplit
        args.PercentTest = 0 
    
    if not 0 <= args.PercentValid/100 <= 1: 
        raise ValueError('PercentValid is not between 0 and 100.')
    if not 0 <= args.PercentTest/100 <= 1: 
        raise ValueError('PercentTest is not between 0 and 100.') 

    
    print('==========================================================')
    classes = {} ## category=class?
    nr_tiles_categ =  {} # number of tiles per category
    percent_tiles_categ = {} # percentage of tiles per category

    # Images  == slides here?? 
    nr_images_categ = {} # number of images per category
    percent_images_categ = {} # percentage of images per category

    nr_patients_categ = {} # number of patients per category
    percent_patients_categ = {} # percentage of patients per category
    patient_set = {}
    nr_slides = 0
    ttv_split = {} #???
    nr_valid = {} #??
    failed_images = [] 



