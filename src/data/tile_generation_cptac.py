import os
from glob import glob 
import numpy as np
import pandas as pd
from openslide import open_slide
from openslide.deepzoom import DeepZoomGenerator
from PIL.Image import Image
import subprocess


def generate_tiles(slides_folder: str, metadata_path: str, output_folder: str, google_cloud_project_id: str) -> None:
    """ 
    Run tiling for each slide separately. If tiles for the respective slide are already present, the slide is skipped. 

    Args:
        slidesfolder (str): absolute path to the folder containing the DICOM slides. 
        metadata_path (str): absolute path to the metadata file. 
        output_folder (str): absolute path to the output folder. A separate subfolder containing the tiles will be created for every slide.

    Returns:
        None
    """

    print('Reading input data from %s' %(slides_folder))
    slides_metadata = pd.read_csv(metadata_path)
    for _, row in slides_metadata.iterrows():
        path_to_slide = _get_path_to_slide_from_gcs_url(row['gcs_url'], slides_folder) 
        slide_id = row['slide_id']
        gcs_url = row['gcs_url']
        _generate_tiles_for_slide(path_to_slide, slide_id, gcs_url, output_folder, google_cloud_project_id)


def _generate_tiles_for_slide(path_to_slide: str, slide_id: str, gcs_url: str, output_folder: str, google_cloud_project_id: str) -> None:

    # Check if slide is already tiled
    output_dir_tiles = os.path.join(output_folder, slide_id) 
    if os.path.exists(output_dir_tiles):
        print("Slide %s already tiled" % slide_id)
        return 
    
    # Download slide in DICOM format using gsutil
    cmd = ['gsutil', '-u {id}'.format(id=google_cloud_project_id), 
            'cp', '{url}'.format(url=gcs_url), '{local_dir}'.format(local_dir=os.path.dirname(path_to_slide))]
    cmd = ['echo', 'test']
    subprocess.call(cmd)

    # Open slide and instantiate a DeepZoomGenerator for that slide
    print('Processing: %s' %(slide_id))
    slide = open_slide(path_to_slide)  
    dz = DeepZoomGenerator(slide, tile_size=512, overlap=0, limit_bounds=True)
    
    # Assert that highest resolution is around 20x = 20000px/cm
    print(int(slide.properties['tiff.XResolution']), int(slide.properties['tiff.YResolution']))
    assert 19700 < int(slide.properties['tiff.XResolution']) < 20300, 'Wrong resolution. Slide is skipped.'
    assert 19700 < int(slide.properties['tiff.YResolution']) < 20300, 'Wrong resolution. Slide is skipped.'

    # Tiling 
    level = dz.level_count-1 # take highest level = original resolution
    if level != -1: 

        os.makedirs(output_dir_tiles) 
        cols, rows = dz.level_tiles[level] # get number of tiles in this level as (nr_tiles_xAxis, nr_tiles_yAxis)
        for row in range(rows):
            for col in range(cols): 
                tilename = os.path.join(output_dir_tiles, '%d_%d.%s' %(col, row, 'jpeg'))
                if not os.path.exists(tilename):
                    tile = dz.get_tile(level, address=(col, row)) 
                    # only store tile if there is enough amount of information, i.e. < 50 % background and the tile size is alright
                    avg_bkg = _get_amount_of_background(tile)
                    if avg_bkg <= 0.5 and tile.size[0] == 512 and tile.size[1] == 512: 
                        tile.save(tilename, quality=90)


def _get_path_to_slide_from_gcs_url(gcs_url, slides_folder):
    filename = os.path.basename(gcs_url)
    return os.path.join(slides_folder, filename)


def _get_amount_of_background(tile: Image) -> float:
    grey = tile.convert(mode='L') 
    bw = grey.point(lambda x: 0 if x < 220 else 1, mode='F') 
    avg_bkg = np.average(np.array(np.asarray(bw)))
    return avg_bkg   
