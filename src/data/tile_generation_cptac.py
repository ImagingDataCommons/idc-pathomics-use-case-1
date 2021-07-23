import os
from glob import glob 
import numpy as np
import pandas as pd
from openslide import open_slide
from openslide.deepzoom import DeepZoomGenerator
from PIL.Image import Image


def generate_tiles(slidespath: str, metadata_path: str, output_folder: str) -> None:
    """ 
    Run tiling for each slide separately. If tiles for the respective slide are already present, the slide is skipped. 

    Args:
        slidespath (str): absolute path to the folder containing each svs-slide in a separate subfolder as done by default when downloading the data from the IDC.
        metadata_path (str): absolute path to the metadata file. 
        output_folder (str): absolute path to the output folder. A subfolder will be created for every slide containing the tiles.

    Returns:
        None
    """

    print('Reading input data from %s' %(slidespath))
    slides = glob(os.path.join(slidespath, '*.dcm')) 
    print(slides)
    for slidepath in slides:
        print(slidepath)
        metadata = pd.read_csv(metadata_path)
        slide_id = _get_slide_id_from_slidepath(slidepath, metadata)
        print(slide_id)
        #_generate_tiles_for_slide(slidepath, metadata_path, output_folder)


def _generate_tiles_for_slide(slidepath: str, metadata_path: str, output_folder: str) -> None:

    metadata = pd.read_csv(metadata_path)
    slide_id = _get_slide_id_from_slidepath(slidepath, metadata)
    output_path = os.path.join(output_folder, slide_id) 
    tiledir = os.path.join('%s_files' %(output_path)) 

    # Check if slide is already tiled
    if os.path.exists(tiledir):
        print("Slide %s already tiled" % slide_id)
        return 
    
    # Open slide and instantiate a DeepZoomGenerator for that slide
    print('Processing: %s' %(slide_id))
    slide = open_slide(slidepath)  
    dz = DeepZoomGenerator(slide, tile_size=512, overlap=0, limit_bounds=True)
    
    # Assert that highest resolution is 20x = 20000px/cm
    assert 20000 < int(slide.properties['tiff.XResolution']) < 20300, 'Wrong resolution. Slide is skipped.'
    assert 20000 < int(slide.properties['tiff.YResolution']) < 20300, 'Wrong resolution. Slide is skipped.'

    # Tiling 
    level = dz.level_count-1 # take highest level = original resolution
    if level != -1: 

        os.makedirs(tiledir) 
        cols, rows = dz.level_tiles[level] # get number of tiles in this level as (nr_tiles_xAxis, nr_tiles_yAxis)
        for row in range(rows):
            for col in range(cols): 
                tilename = os.path.join(tiledir, '%d_%d.%s' %(col, row, 'jpeg'))
                if not os.path.exists(tilename):
                    tile = dz.get_tile(level, address=(col, row)) 
                    # only store tile if there is enough amount of information, i.e. < 50 % background and the tile size is alright
                    avg_bkg = _get_amount_of_background(tile)
                    if avg_bkg <= 0.5 and tile.size[0] == 512 and tile.size[1] == 512: 
                        tile.save(tilename, quality=90)


def _get_slide_id_from_slidepath(slidepath, metadata):
    return os.path.basename(slidepath).replace('.dcm', '') 


def _get_amount_of_background(tile: Image) -> float:

    grey = tile.convert(mode='L') 
    bw = grey.point(lambda x: 0 if x < 220 else 1, mode='F') 
    avg_bkg = np.average(np.array(np.asarray(bw)))
    return avg_bkg   
