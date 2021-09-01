import os
from glob import glob 
import numpy as np
import pandas as pd
from openslide import open_slide
from openslide.deepzoom import DeepZoomGenerator
from PIL.Image import Image
import subprocess
from multiprocessing import Process


def generate_tiles(slides_folder: str, metadata_path: str, output_folder: str, save_every_xth_tile: int, google_cloud_project_id: str) -> None:
    """ 
    Run tiling for each slide separately. If tiles for the respective slide are already present, the slide is skipped. 

    Args:
        slides_folder (str): absolute path to the folder containing the DICOM slides. 
        metadata_path (str): absolute path to the metadata file. 
        output_folder (str): absolute path to the output folder. A separate subfolder containing the tiles will be created for every slide.
        google_cloud_project_id (str): ID of the Google Cloud Project used. 

    Returns:
        None
    """

    print('Reading input data from %s' %(slides_folder))
    slides_metadata = pd.read_csv(metadata_path)
    for _, row in slides_metadata.iterrows():
        path_to_slide = _get_path_to_slide_from_gcs_url(row['gcs_url'], slides_folder) 
        slide_id = row['slide_id']
        gcs_url = row['gcs_url']
        _generate_tiles_for_slide_in_process(path_to_slide, slide_id, gcs_url, output_folder, save_every_xth_tile, google_cloud_project_id)


# Workaround for a potential memory leak in Openslide 
def _generate_tiles_for_slide_in_process(path_to_slide: str, slide_id: str, gcs_url: str, output_folder: str, save_every_xth_tile: int, google_cloud_project_id: str) -> None:
    p = Process(target=_generate_tiles_for_slide, args=(path_to_slide, slide_id, gcs_url, output_folder, save_every_xth_tile, google_cloud_project_id)) 
    p.start()
    p.join()


def _generate_tiles_for_slide(path_to_slide: str, slide_id: str, gcs_url: str, output_folder: str, save_every_xth_tile: int, google_cloud_project_id: str) -> None:

    # Check if slide is already tiled
    output_dir_tiles = os.path.join(output_folder, slide_id) 
    if os.path.exists(output_dir_tiles):
        print("Slide %s already downloaded and tiled" % slide_id)
        return
    
    # Download slide in DICOM format using gsutil
    cmd = ['gsutil -u {id}  cp {url} {local_dir}'.format(id=google_cloud_project_id, url=gcs_url, local_dir=os.path.dirname(path_to_slide))]
    subprocess.run(cmd, shell=True)

    # Open slide and instantiate a DeepZoomGenerator for that slide
    print('Processing: %s' %(slide_id))

    try: 
        slide = open_slide(path_to_slide)  
        thumbnail = slide.get_thumbnail((300,300)) # get and save thumbnail image
        thumbnail.save(os.path.join(os.path.dirname(path_to_slide), slide_id + '.png'))
        dz = DeepZoomGenerator(slide, tile_size=128, overlap=0, limit_bounds=True)
    except: 
        print('Some processing error for slide %s' %(slide_id))
        return 
    
    # Tiling 
    level = dz.level_count-3 # take third highest level 
    os.makedirs(output_dir_tiles) 
    cols, rows = dz.level_tiles[level] # get number of tiles in this level as (nr_tiles_xAxis, nr_tiles_yAxis)
    counter = 0 # use counter to only save every x-th tile
    for row in range(rows):
        for col in range(cols): 
            counter += 1
            if not counter % save_every_xth_tile == 0:
                pass
            tilename = os.path.join(output_dir_tiles, '%d_%d.%s' %(col, row, 'jpeg'))
            if not os.path.exists(tilename):
                tile = dz.get_tile(level, address=(col, row)) 
                # only store tile if there is enough amount of information, i.e. < 50 % background and the tile size is alright
                avg_bkg = _get_amount_of_background(tile)
                if avg_bkg <= 0.5 and tile.size[0] == 128 and tile.size[1] == 128: 
                    tile.save(tilename, quality=90)

    # After tiling delete the WSI to save disk space
    os.remove(path_to_slide)


def _get_path_to_slide_from_gcs_url(gcs_url, slides_folder):
    filename = os.path.basename(gcs_url)
    return os.path.join(slides_folder, filename)


def _get_amount_of_background(tile: Image) -> float:
    grey = tile.convert(mode='L') 
    thresholded = grey.point(lambda x: 0 if x < 220 else 1, mode='F') 
    avg_bkg = np.average(np.array(thresholded))
    return avg_bkg   