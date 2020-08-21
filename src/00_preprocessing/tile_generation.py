""" 
TODO Documentation + Licence 
""" 

# Import libraries
import os
from glob import glob 
import numpy as np
from argparse import ArgumentParser
import openslide 
from openslide import open_slide
from openslide.deepzoom import DeepZoomGenerator


def get_Bkg(tile):
    """
    TODO 
    """
    grey = tile.convert(mode='L') # mode 'L' 
    bw = grey.point(lambda x: 0 if x < 220 else 1, mode='F')
    avg_Bkg = np.average(np.array(np.asarray(bw)))
    return avg_Bkg


def generate_tiles(slidepath, slide_name, output_path, args):
    """ 
    TODO 
    """
    # Open slide and instantiate a DeepZoomGenerator for that slide
    slide = open_slide(slidepath)  
    dz = DeepZoomGenerator(slide, tile_size=512, overlap=0, limit_bounds=True)

    # Get downsampling factors, information about the microscope's objective and available magnifications
    factors = slide.level_downsamples
    try: 
        objective = float(slide.properties[openslide.PROPERTY_NAME_OBJECTIVE_POWER])
    except: 
        print('%s: no objective information found. Slide is skipped.' %(slide_name))
        return       
    available = tuple(objective/x for x in factors) 

    # Tiling
    for level in range(dz.level_count-1, -1, -1):
        this_magnification = available[0]/pow(2, dz.level_count - (level+1)) # compute current magnification depending on the recent level  
        if this_magnification != 20.0: # our desired magnification is 20x 
            continue 
        
        tiledir = os.path.join('%s_files' %(output_path), str(this_magnification)) 
        if not os.path.exists(tiledir):
            os.makedirs(tiledir)
        
        cols, rows = dz.level_tiles[level] # get number of tiles in this label as (nr_tiles_xAxis, nr_tiles_yAxis)
        for row in range(rows):
            for col in range(cols): 
                tilename = os.path.join(tiledir, '%d_%d.%s' %(col, row, 'jpeg'))
                if not os.path.exists(tilename):
                    tile = dz.get_tile(level, address=(col, row)) 
                    # only store tile if there is enough amount of information, i.e. low amount of background
                    avg_Bkg = get_Bkg(tile)
                    if avg_Bkg <= 0.5: # only save the tile if less than 50% is background
                        tile.save(tilename, quality=90)


def run(slidespath, output_folder):
    print('Reading input data from %s' %(args.slidespath))
    slides = glob(args.slidespath) # get all images from the data folder

    for slidepath in slides:
        slide_name = os.path.splitext(os.path.basename(slidepath))[0]
        output_path = os.path.join(args.output_folder, slide_name)
        print('Processing: %s' %(slide_name))
        generate_tiles(slidepath, slide_name, output_path, args)


if __name__ == '__main__':
    description = 'Usage: %prog [options] <path-to-slides>'
    parser = ArgumentParser(description=description)

    parser.add_argument('slidespath', 
                        help='Path to the input slides')
    parser.add_argument('output_folder', 
                        help='Full path to output folder')                   

    args = parser.parse_args()

    run(slidespath, output_folder)

        
