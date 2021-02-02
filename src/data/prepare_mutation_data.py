import os 


# TODO: For patient IDs in mutation file
# TODO: Slides meta maps to slide class (normal, luad, lusc --> again only take luad)

def _write_csv_files(slide_folders: str, output_folder: str, patient_to_category: Dict[str, str], slides_meta: Dict[str, str], classes: Dict[str, int], sorting_option: str) -> None:
    path_train = os.path.join(output_folder, 'csv_train_' + sorting_option + '.csv')
    path_test = os.path.join(output_folder, 'csv_test_' + sorting_option + '.csv')
    path_valid = os.path.join(output_folder, 'csv_valid_' + sorting_option + '.csv')

    with open(path_train, 'w') as csv_train, open(path_test, 'w') as csv_test, open(path_valid, 'w') as csv_valid:
        output_csv = {'train': csv_train, 'test': csv_test, 'valid': csv_valid}
        # Add header
        for csv in output_csv.values(): 
            csv.write('path,reference_value\n')

        # Fill csv files
        for slide_folder in slide_folders:
            _write_info(slide_folder, output_csv, output_folder, patient_meta, patient_to_category, slides_meta, classes)
            

def _write_info(slide_folder: str, output_csv: dict, output_folder: str, patient_to_category: Dict[str, str], slides_meta: Dict[str, str], classes: Dict[str, int]) -> None:
    patient = slide_folder.split('/')[-1][:12]
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