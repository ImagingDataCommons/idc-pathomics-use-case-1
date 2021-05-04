import os
from PIL import Image
from glob import glob


def copy_folder_structure(input_path, output_path):
    for dirpath, _, _ in os.walk(input_path):
        structure = os.path.join(output_path, dirpath[len(input_path):])
        if not os.path.isdir(structure) and not structure.endswith('20.0'):
            os.mkdir(structure)

def copy_and_resize_tiles(tile_paths_in, output_folder):
    for tile_path_in in tile_paths_in:
        len_out = len(output_folder.split('/'))
        tile_path_out = os.path.join(output_folder, '/'.join(tile_path_in.split('/')[len_out-1:]))
        if not os.path.exists(tile_path_out):
            img = Image.open(tile_path_in)
            resized = img.resize((128,128))
            resized.save(tile_path_out)

if __name__ == '__main__':
    input_path = '/mnt/gaia/imageData/deep_learning/output/imaging-data-commons/idc-pathomics-use-case-1/tiles/'
    output_path = '/mnt/gaia/imageData/deep_learning/output/imaging-data-commons/idc-pathomics-use-case-1/tiles_128_5x/'
    #copy_folder_structure(input_path, output_path)
    tile_paths_in = glob(os.path.join(input_path, '*/5.0/*jpeg'))
    print(input_path)
    copy_and_resize_tiles(tile_paths_in, output_path)
