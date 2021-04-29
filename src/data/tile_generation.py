import os
from glob import glob 
import numpy as np
import openslide 
from openslide import open_slide
from openslide.deepzoom import DeepZoomGenerator
from PIL.Image import Image
from typing import Tuple


def generate_tiles(slidespath: str, output_folder: str) -> None:
    """ 
    Run tiling for each slide separately. If tiles for the respective slide are already present, the slide is skipped. 

    Args:
        slidespath (str): absolute path to the folder containing each svs-slide in a separate subfolder as done by default when downloading the data from the GDC.
        output_folder (str): absolute path to the output folder. A subfolder will be created for every slide containing the tiles.

    Returns:
        None
    """

    print('Reading input data from %s' %(slidespath))
    slides = glob(slidespath + '/*/*svs', recursive=True) 
    for slidepath in slides:
        _generate_tiles_for_slide(slidepath, output_folder)


def _generate_tiles_for_slide(slidepath: str, output_folder: str) -> None:

    # Check if slide is already tiled
    slide_name = os.path.splitext(os.path.basename(slidepath))[0]
    output_path = os.path.join(output_folder, slide_name) 
    if os.path.exists(os.path.join('%s_files' %(output_path))):
        print("Slide %s already tiled" % slide_name)
        return 
    
    # Open slide and instantiate a DeepZoomGenerator for that slide
    print('Processing: %s' %(slide_name))
    slide = open_slide(slidepath)  
    dz = DeepZoomGenerator(slide, tile_size=512, overlap=0, limit_bounds=True)
    
    # Tiling 
    level = _get_required_level(slide, dz)
    if level != -1: 

        tiledir = os.path.join('%s_files' %(output_path), str(this_magnification)) 
        if not os.path.exists(tiledir):
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


def _get_required_level(slide: openslide.OpenSlide, dz: DeepZoomGenerator) -> int:
     
    level = -1
    available_magnifications = _get_available_magnifications(slide)
    for level in range(dz.level_count-1, -1, -1):
        this_magnification = available[0]/pow(2, dz.level_count - (level+1)) # compute current magnification depending on the recent level  
        if this_magnification != 5.0: # our desired magnification is 20x 
            continue
    return level 


def _get_available_magnifications(slide: openslide.OpenSlide) -> Tuple[float]:

    factors = slide.level_downsamples
    try: 
        objective = float(slide.properties[openslide.PROPERTY_NAME_OBJECTIVE_POWER])
    except: 
        print('%s: no objective information found. Slide is skipped.' %(slide_name))
    available_magnifications = tuple(objective/x for x in factors) 
    return available_magnifications


def _get_amount_of_background(tile: Image) -> float:

    grey = tile.convert(mode='L') 
    bw = grey.point(lambda x: 0 if x < 220 else 1, mode='F') 
    avg_bkg = np.average(np.array(np.asarray(bw)))
    return avg_bkg   
