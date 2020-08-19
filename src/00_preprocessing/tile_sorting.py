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
# - geht das mit dem new_patient nicht eleganter? 
# - patientID glaub gar nicht nötig und ist ein fehler im example code...

class TileSorter():
    """ TODO """

    def __init__(self, img_folders, json_data, arguments):
        # Parameters 
        self.img_folders = img_folders
        self.json_data = json_data 
        self.args = arguments 

        # Prepare the statistics used to control balancing 
        self.classes = defaultdict(list) 
        self.patient_set = {}
        self.nr_tiles_categ =  {} # number of tiles per category, category = train/validation/test
        self.percent_tiles_categ = {} # percentage of tiles per category
        self.nr_slides_categ = {} # number of images per category
        self.percent_slides_categ = {} # percentage of images per category
        self.nr_patients_categ = {} # number of patients per category
        self.percent_patients_categ = {} # percentage of patients per category
    
    def _initialize_statistics(self, sorting_class): 
        """ 
        TODO 
        """ 
        if sorting_class in self.nr_tiles_categ.keys():
            pass 
        else: 
            self.nr_tiles_categ[sorting_class] = 0
            self.nr_tiles_categ[sorting_class + '_train'] = 0
            self.nr_tiles_categ[sorting_class + '_valid'] = 0
            self.nr_tiles_categ[sorting_class + '_test'] = 0
            
            self.percent_tiles_categ[sorting_class + '_train'] = 0
            self.percent_tiles_categ[sorting_class + '_valid'] = 0
            self.percent_tiles_categ[sorting_class + '_test'] = 0
            
            self.nr_slides_categ[sorting_class] = 0
            self.nr_slides_categ[sorting_class + '_train'] = 0
            self.nr_slides_categ[sorting_class + '_valid'] = 0
            self.nr_slides_categ[sorting_class + '_test'] = 0
            
            self.percent_slides_categ[sorting_class + '_train'] = 0
            self.percent_slides_categ[sorting_class + '_valid'] = 0
            self.percent_slides_categ[sorting_class + '_test'] = 0
            
            self.nr_patients_categ[sorting_class] = 0
            self.nr_patients_categ[sorting_class + '_name-list'] = {}
            self.nr_patients_categ[sorting_class + '_train'] = 0
            self.nr_patients_categ[sorting_class + '_valid'] = 0
            self.nr_patients_categ[sorting_class + '_test'] = 0

            self.percent_patients_categ[sorting_class + '_train'] = 0
            self.percent_patients_categ[sorting_class + '_valid'] = 0
            self.percent_patients_categ[sorting_class + '_test'] = 0


    def _get_category(self, sorting_class):
        """ TODO 
        # Balancing wrt tiles (0), slides (1), patients (2)
        # # rename images with the root name and put them in train/test/valid 
        # """ 
        if self.args.balance == 0:   
            if self.percent_tiles_categ.get(sorting_class + '_test') <= self.args.percent_test/100 and self.args.percent_test/100 > 0:
                ttv = 'test'
            elif self.percent_tiles_categ.get(sorting_class + '_valid') <= self.args.percent_valid/100 and self.args.percent_valid/100 > 0: 
                ttv = 'valid'
            else:
                ttv = 'train'
        elif self.args.balance == 1: 
            if self.percent_slides_categ.get(sorting_class + '_test') <= self.args.percent_test/100 and self.args.percent_test/100 > 0:
                ttv = 'test'
            elif self.percent_slides_categ.get(sorting_class + '_valid') <= self.args.percent_valid/100 and self.args.percent_valid/100 > 0: 
                ttv = 'valid'
            else:
                ttv = 'train'
        else: 
            if percent_patients_categ.get(sorting_class + '_test') <= self.args.percent_test/100 and self.args.percent_test/100 > 0:
                ttv = 'test'
            elif percent_patients_categ.get(sorting_class + '_valid') <= self.args.percent_valid/100 and self.args.percent_valid/100 > 0: 
                ttv = 'valid'
            else:
                ttv = 'train'
        return ttv 

    def _update_statistics(self, ttv, nr_tiles, new_patient, sorting_class): 
        """ 
        TODO
        """ 
        self._update_amounts(ttv, nr_tiles, new_patient, sorting_class)
        self._update_percentages(sorting_class)
    
    def _update_amounts(self, ttv, nr_tiles, new_patient, sorting_class):
        """ 
        TODO
        """ 
        self.nr_tiles_categ[sorting_class] += nr_tiles
        self.nr_slides_categ[sorting_class] += 1
        
        if new_patient: 
            self.nr_patients_categ[sorting_class] += 1

        if ttv == 'train':
            if new_patient: 
                self.nr_patients_categ[sorting_class + '_train'] += 1
            self.nr_tiles_categ[sorting_class + '_train'] += nr_tiles
            self.nr_slides_categ[sorting_class + '_train'] += + 1
        elif ttv == 'test':
            if new_patient: 
                self.nr_patients_categ[sorting_class + '_test'] += 1
            self.nr_tiles_categ[sorting_class + '_test'] += nr_tiles
            self.nr_slides_categ[sorting_class + '_test'] += + 1
        else:
            if new_patient: 
                self.nr_patients_categ[sorting_class + '_valid'] += 1
            self.nr_tiles_categ[sorting_class + '_valid'] += nr_tiles
            self.nr_slides_categ[sorting_class + '_valid'] += + 1


    def _update_percentages(self, sorting_class):
        """ 
        TODO
        """
        self.percent_tiles_categ[sorting_class + '_train'] = float(self.nr_tiles_categ[sorting_class + '_train']) / float(self.nr_tiles_categ[sorting_class])
        self.percent_tiles_categ[sorting_class + '_test'] = float(self.nr_tiles_categ[sorting_class + '_test']) / float(self.nr_tiles_categ[sorting_class])
        self.percent_tiles_categ[sorting_class + '_valid'] = float(self.nr_tiles_categ[sorting_class + '_valid']) / float(self.nr_tiles_categ[sorting_class])

        self.percent_slides_categ[sorting_class + '_train'] = float(self.nr_slides_categ[sorting_class + '_train']) / float(self.nr_slides_categ[sorting_class])
        self.percent_slides_categ[sorting_class + '_test'] = float(self.nr_slides_categ[sorting_class + '_test']) / float(self.nr_slides_categ[sorting_class])
        self.percent_slides_categ[sorting_class + '_valid'] = float(self.nr_slides_categ[sorting_class + '_valid']) / float(self.nr_slides_categ[sorting_class])
        
        self.percent_patients_categ[sorting_class + '_train'] = float(self.nr_patients_categ[sorting_class + '_train']) / float(self.nr_patients_categ[sorting_class])
        self.percent_patients_categ[sorting_class + '_test'] = float(self.nr_patients_categ[sorting_class + '_test']) / float(self.nr_patients_categ[sorting_class])
        self.percent_patients_categ[sorting_class + '_valid'] = float(self.nr_patients_categ[sorting_class + '_valid']) / float(self.nr_patients_categ[sorting_class])

    def _print_final_statistics(self): 
        """ 
        TODO 
        """ 
        for k, v in sorted(self.classes.items()):
            print('List of images in class %s :' % k)
            print(v)
        for k, v in sorted(self.nr_tiles_categ.items()):
            print(k, v)
        for k, v in sorted(self.percent_tiles_categ.items()):
            print(k, v)
        for k, v in sorted(self.nr_slides_categ.items()):
            print(k, v)
        if self.args.patientID > 0:
            for k, v in sorted(self.nr_patients_categ.items()):
                print(k, v)

    def run(self): 
        # For each slide's tiles extract metadata and do the following ...
        for folder in self.img_folders:
            folder_root = os.path.basename(folder).replace('_files', '')
            try:
                image_meta = self.json_data[folder_root] 
            except KeyError:
                print('File name %s not found in metadata.' %(folder_root))
                try: 
                    image_meta = self.json_data[folder_root[:args.patientID]]
                except KeyError:
                    print('File name %s not found in metadata.' %(folder_root[:args.patientID]))
            
            # Get the information on how to sort the tiles of the considered slide. Sorting classes differ depending on the experiment that we want to do afterwards
            sorting_class = sort_function(image_meta) # get sorting class e.g. 'normal', 'TCGA-LUAD', 'TCGA-LUSC'
            if sorting_class is None: 
                print('Slide is not valid for this sorting option and is skipped.')
                continue 
            
            # Create folder corresponding to the sorting category if not already existent 
            if not os.path.exists(sorting_class):
                os.makedirs(sorting_class)
            self.classes[sorting_class].append(folder_root) # store which slide's tiles are assigned to which sorting class 
            
            # Check in the reference directories whether there is a set of tiles at the desired magnification 
            avail_mag = [float(x) for x in os.listdir(folder) if os.path.isdir(os.path.join(folder, x))]
            if max(avail_mag) < 0: 
                print('Magnification not known for that slide. The slide is skipped. ')
                continue
            elif float(args.magnification) not in avail_mag: 
                print('Desired magnification not available. This slide is skipped. ')
                continue 

            # Sorting tiles into the appropriate sorting category (e.g. normal, LUAD, LUSC)
            print('Sorting tiles into subdirectory %s...' %(sorting_class))
            source_dir = os.path.join(folder, str(args.magnification), '*')
            all_tiles = glob(source_dir)
            print('Number of tiles: ' + str(len(all_tiles)))
            if len(all_tiles) == 0:
                continue 

            # Initialize statistics for balancing if not already done
            self._initialize_statistics(sorting_class)  

            nr_tiles = 0 # count number of tiles to track when there is a new patient (then its nr_tiles == 1)
            for tile_path in all_tiles:
                nr_tiles += 1 
                tile_name = os.path.basename(tile_path)
                ttv = self._get_category(sorting_class) # check whether to put the tile in train, test or validation set

                ## ????? 
                if args.patientID > 0: 
                    patient = folder_root[:args.patientID]
                else: 
                    patient = folder_root

                # Check if patient is in this particular class --> ist das so nötig? sieht mir überflüssig aus... 
                if patient not in self.nr_patients_categ[sorting_class + '_name-list'].keys():
                    # Check if patient in ANY class is train, valid or test 
                    print('ljslfd', self.patient_set)
                    if patient in self.patient_set.keys(): 
                        ttv = self.patient_set[patient]
                        self.nr_patients_categ[sorting_class + '_name-list'][patient] = self.patient_set[patient]
                    else: 
                        self.patient_set[patient] = ttv 
                        self.nr_patients_categ[sorting_class + '_name-list'][patient] = ttv
                    if nr_tiles == 1: 
                        new_patient = True 
                else: 
                    # it is in the class -> not a new patient
                    ttv = self.patient_set[patient]
                    if nr_tiles == 1: 
                        new_patient = False 
                        
            new_image_dir = os.path.join(sorting_class, '_'.join((ttv, folder_root, tile_name)))
            ### here goes the linking/writing into csv files whatever we want to do

            # Update statistics
            self._update_statistics(ttv, nr_tiles, new_patient, sorting_class)
            print("Done. %d tiles added to %s " % (nr_tiles, sorting_class))

        self._print_final_statistics()


def extract_cancer(metadata):
    return metadata['cases'][0]['project']['project_id']

def extract_sample_type(metadata):
    return metadata['cases'][0]['samples'][0]['sample_type']

def sort_cancer_healthy(metadata, **kwargs):
    """ TODO """
    sample_type = extract_sample_type(metadata)
    if "Normal" in sample_type:
        return sample_type.replace(' ', '_')
    return "cancer"

def sort_subtype(metadata, **kwargs):
    """ TODO """
    sample_type = extract_sample_type(metadata)
    if "Normal" in sample_type:
        return None
    return extract_cancer(metadata)

def sort_subtype_healthy(metadata, **kwargs):
    """ TODO """
    cancer = extract_cancer(metadata)
    sample_type = extract_sample_type(metadata)
    if "Normal" in sample_type:
        return sample_type.replace(' ', '_')
    return cancer 

# List of the given options of how to sort the tiles
sort_options = [sort_cancer_healthy,
                sort_subtype,
                sort_subtype_healthy]

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

    parser.add_argument("source_folder", 
                        help="Path to the tiled images")
    parser.add_argument("json_file", 
                        help="Path to metadata file in json format")
    parser.add_argument("sorting_option", 
                        help="See options given in the description", type=int, choices=[0,1,2]) 
    parser.add_argument("--magnification", 
                        help="Magnification to use", type=float, default=20., 
                        dest='magnification')
    parser.add_argument("--percent_valid", 
                        help="Percentage of images for validation (between 0 and 100, default: 15) ", metavar='[0-100]', type=float, choices=range(0,101), default=15,
                        dest='percent_valid')
    parser.add_argument("--percent_test", help="Percentage of images for testing (between 0 and 100, default: 15)", metavar='[0-100]', type=float, choices=range(0,101), default=15, 
                        dest='percent_test')
    parser.add_argument("--patientID",
                        help="Patient ID is supposed to be the first PatientID characters (integer expected) of the folder in which the pyramidal jpgs are [0]." \
                             "Slides from same patient will be in same train/test/valid set. This option is ignored if set to 0 or -1 ", type=int, default=0,
                        dest='patientID')
    parser.add_argument("--balance", 
                        help="Balance datasets by: 0 - tiles (default); 1 - slides; 2 - patients (have to provide PatientID) [0]", type=int, choices=[0,1,2], default=0, 
                        dest='balance')

    args = parser.parse_args()

    
    # Extract all separate image folders from the source foulder
    img_folders = glob(os.path.join(args.source_folder, '*_files'))
    random.shuffle(img_folders) # randomize order of the images

    # Load provided JSON file containing the metadata and prepare the information we need. 
    if not '.json' in args.json_file:
        raise ValueError('Please provide a metadata file in JSON format.')
    else: 
        with open(args.json_file) as json_file: 
            json_data = json.loads(json_file.read())
        try:
            json_data = dict((jd['file_name'].replace('.svs', ''), jd) for jd in json_data)
        except:
            raise KeyError('Cannot find "file_name" as key in the json data.')

    # Extract the sorting option 
    try: 
        sort_function = sort_options[args.sorting_option-1] # use -1 to transform to zero-based index
    except IndexError:
        raise ValueError('Unknown sorting option specified.')

    # Run the sorting
    TileSorter(img_folders, json_data, args).run()

        
            

            


