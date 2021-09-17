import os
from PIL import Image
from glob import glob


def copy_folder_structure(input_path, output_path):
    for dirpath, _, _ in os.walk(input_path):
        structure = os.path.join(output_path, dirpath[len(input_path):])
        if not os.path.isdir(structure):
            os.mkdir(os.path.join(output_path, structure))

def copy_and_resize_tiles(tile_paths_in, output_folder):
    for tile_path_in in tile_paths_in:
        tile_path_out = os.path.join(output_folder, '/'.join(tile_path_in.split('/')[-3:]))
        print(tile_path_in, tile_path_out)
        if not os.path.exists(tile_path_out):
            img = Image.open(tile_path_in)
            resized = img.resize((75,75))
            resized.save(tile_path_out)

if __name__ == '__main__':
    input_path = '/home/dschacherer/idc_input/tiles512_20x/'
    output_path = '/home/dschacherer/idc_input/tiles75_20x/'
    copy_folder_structure(input_path, output_path)
    tile_paths_in = glob(os.path.join(input_path, '*/20.0/*jpeg'))
    copy_and_resize_tiles(tile_paths_in, output_path)
