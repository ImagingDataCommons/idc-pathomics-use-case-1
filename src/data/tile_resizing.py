import os
from PIL import Image
from glob import glob


def copy_folder_structure(input_path, output_path):
    for dirpath, _, _ in os.walk(input_path):
        structure = os.path.join(output_path, dirpath[len(input_path):])
        if not os.path.isdir(structure):
            os.mkdir(structure)

def copy_and_resize_tiles(tile_paths_in, output_folder):
    for tile_path_in in tile_paths_in:
        print(tile_path_in)
        len_out = len(output_folder.split('/'))
        tile_path_out = os.path.join(output_folder, '/'.join(tile_path_in.split('/')[len_out-1:]))
        img = Image.open(tile_path_in)
        resized = img.resize((256,256))
        resized.save(tile_path_out)

if __name__ == '__main__':
    input_path = '/home/dschacherer/mnt/gaia/imageData/deep_learning/output/imaging-data-commons/idc-pathomics-use-case-1/tiles/'
    output_path = '/home/dschacherer/mnt/gaia/imageData/deep_learning/output/imaging-data-commons/idc-pathomics-use-case-1/tiles_256/'
    #copy_folder_structure(input_path, output_path)
    tile_paths_in = glob(input_path + '/*/*/*jpeg')
    print(len(tile_paths_in), tile_paths_in)
    copy_and_resize_tiles(tile_paths_in, output_path)
