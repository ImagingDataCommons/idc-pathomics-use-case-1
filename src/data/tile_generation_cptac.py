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
    print(os.path.join(slidespath, '*.dcm'))
    slides = glob(os.path.join(slidespath, '*.dcm')) 
    metadata = pd.read_csv(metadata_path)
    print(slides)
    for slidepath in slides:
        print(slidepath)
        #_generate_tiles_for_slide(slidepath, metadata, output_folder)


def _generate_tiles_for_slide(slidepath: str, output_folder: str, desired_magnification: float) -> None:

    # Check if slide is already tiled
    slide_name = os.path.splitext(slidepath)[0].split('/')[-2]
    output_path = os.path.join(output_folder, slide_name) 
    tiledir = os.path.join('%s_files' %(output_path)) 
    if os.path.exists(tiledir):
        print("Slide %s already tiled" % slide_name)
        return 
    
    # Open slide and instantiate a DeepZoomGenerator for that slide
    print('Processing: %s' %(slide_name))
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


def _get_slide_id_from_metadata(dcm_path, metadata):
    pass 


def _get_amount_of_background(tile: Image) -> float:

    grey = tile.convert(mode='L') 
    bw = grey.point(lambda x: 0 if x < 220 else 1, mode='F') 
    avg_bkg = np.average(np.array(np.asarray(bw)))
    return avg_bkg   
