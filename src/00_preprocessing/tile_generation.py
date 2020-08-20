""" 
TODO Documentation + Licence 

<https://github.com/ncoudray/DeepPATH/blob/master/DeepPATH_code/00_preprocessing/0b_tileLoop_deepzoom4.py>
<https://github.com/openslide/openslide-python/blob/master/examples/deepzoom/deepzoom_tile.py>

""" 

# Import libraries
import os
from glob import glob 
import numpy as np 
import re 
from argparse import ArgumentParser
from multiprocessing import Process, JoinableQueue
import openslide 
from openslide import open_slide, ImageSlide
from openslide.deepzoom import DeepZoomGenerator
from unicodedata import normalize

# """ # TODO
# # - documentation code
# # - associated images?! 
# # - replace optparse by argsparse! 

# class TileWorker(Process):
#     """ 
#     TODO Documentation 
#     Attributes:
#     -----------
#     Methods:
#     --------
#     """ 

#     def __init__(self, queue, slidepath, tile_size, overlap, limit_bounds, quality, background_threshold):
#         Process.__init__(self, name='TileWorker')
#         self.daemon = True
#         self._queue = queue 
#         self._slidepath = slidepath 
#         self._tile_size = tile_size 
#         self._overlap = overlap 
#         self._limit_bounds = limit_bounds 
#         self._quality = quality 
#         self._slide = None 
#         self._background_threshold = background_threshold 

#     def run(self):
#         """
#         TODO the tiling is done here, tasks are put into the queue by DeepZoomImageTiler _write_tiles()
#         """ 
#         self._slide = open_slide(self._slidepath)
#         last_associated = None
#         dz = self._get_dz()

#         while True:
#             data = self._queue.get()
#             if data is None: # ???? 
#                 self._queue.task_done()
#                 break 
#             associated, level, address, outfile = data 
#             if last_associated != associated:
#                 dz = self._get_dz(associated)
#                 last_associated = associated

#             try:
#                 tile = dz.get_tile(level, address)
#                 # only store tile if there is enough amount of information, i.e. low amount of background
#                 avg_Bkg = self._get_Bkg(tile)
#                 if avg_Bkg <= (self._background_threshold / 100.0):
#                     tile.save(outfile, quality=90)
#                 self._queue.task_done()
#             except Exception as e:
#                 print("Slide %s failed at dz.get_tile for level %f" %(self._slidepath, level), '\n', e)
#                 self._queue.task_done 

#     def _get_dz(self, associated=None):
#         """ 
#         TODO Documentation - get deep zoom generator 
#         """ 
#         # would OpenSlide be better??? what is meant with associated? 
#         if associated is not None: 
#             image = ImageSlide(self._slide.associated_images[associated])
#         else: 
#             image = self._slide 
#         dz = DeepZoomGenerator(image, self._tile_size, self._overlap, limit_bounds=self._limit_bounds)

#         return dz 

    


# class DeepZoomImageTiler(object):
#     """ 
#     TODO Documentation
#     Handles generation of tiles and metadata for a single image.
#     """ 

#     def __init__(self, dz, slide, queue, associated, basename, basenameJPG, format, magnification):
#         self._dz = dz 
#         self._slide = slide 
#         self._queue = queue 
#         self._associated = associated
#         self._basename = basename 
#         self._basenameJPG = basenameJPG
#         self._format = format  
#         self._magnification = magnification
#         self._processed = 0
        
#     def run(self):
#         self._write_tiles()
#         self._write_dzi()

#     def _write_tiles(self):
#         """
#         TODO Documentation: 
#         for every level 
#         put tasks into queue 
#         """
        
        
#                     self._tile_done()

#     def _tile_done(self):
#         self._processed = 1
#         count, total = self._processed, self._dz.tile_count 
#         if count % 100 == 0 or count == total:
#             print('Tiling %s: wrote %d/%d tiles' %(self._associated or 'slide', count, total), end='\r', file=sys.stderr)
#             if count == total:
#                 print(file=sys.stderr)

#     def _write_dzi(self):
#         with open('%s.dzi' %(self._basename), 'w') as out:
#             out.write(self.get_dzi())

#     def get_dzi(self):
#         return self._dz.get_dzi('jpeg')


# class DeepZoomStaticTiler(object): 
#     """
#     TODO Documentation, code is from openslide example and modified by coudray
#     Handles generation of tiles and metadata for all images in a slide. <-- images in a slide???
#     """ 

#     def __init__(self, slidepath, basename, basenameJPG, format, tile_size, overlap, limit_bounds, quality, workers, background_threshold, magnification):
#         self._slide = open_slide(slidepath)
#         self._basename = basename 
#         self._basenameJPG = basenameJPG
#         self._format = format
#         self._tile_size = tile_size
#         self._overlap = overlap
#         self._limit_bounds = limit_bounds
#         self._workers = workers 
#         self._magnification = magnification 
#         self._queue = JoinableQueue(2 * workers)
#         self._dzi_data = {}
#         for i in range(workers):
#             TileWorker(self._queue, slidepath, tile_size, overlap, limit_bounds, quality, background_threshold).start()

#     def run(self):
#         self._run_image()
#         self._shutdown()

#     def _run_image(self, associated=None):
#         """
#         TODO 
#         """
#         if associated is None: 
#             image = self._slide 
#             basename = self._basename
        
#         else: 
#             image = ImageSlide(self._slide.associated_images[associated])
#             basename = os.path.join(self._basename, self._slugify(associated))
        
#         # Instantiate generator and image tiler
#         dz = DeepZoomGenerator(image, self._tile_size, self._overlap, limit_bounds=True)
#         tiler = DeepZoomImageTiler(dz, self._slide, self._queue, associated, basename, self._basenameJPG, self._format, self._magnification)
#         tiler.run()
#         self._dzi_data[self._url_for(associated)] = tiler.get_dzi()

#     def _url_for(self, associated): 
#         """
#         TODO Documentation 
#         """
#         if associated is None: 
#             base = 'slide'
#         else: 
#             base = self._slugify(associated)
#         return '%s.dzi' %(base)
    
#     @classmethod
#     def _slugify(cls, text):
#         """
#         TODO 
#         """
#         text = normalize('NFKD', text.lower()).encode('ascii', 'ignore').decode()
#         return re.sub('[^a-z0-9]+', '_', text)
    
#     def _shutdown(self):
#         """
#         TODO 
#         """
#         for _i in range(self._workers):
#             self._queue.put(None)
#         self._queue.join()
#  """

def get_Bkg(tile):
        """
        TODO Documentation 
        """ 
        grey = tile.convert(mode='L') # mode 'L' 
        bw = grey.point(lambda x: 0 if x < 220 else 1, mode='F')
        avg_Bkg = np.average(np.array(np.asarray(bw)))
        return avg_Bkg





if __name__ == '__main__':
    description = 'Usage: %prog [options] <path-to-slides>'
    parser = ArgumentParser(description=description)

    parser.add_argument('slidespath', 
                        help='Path to the input slides')
    parser.add_argument('output_folder', 
                        help='Full path to output folder') 
    parser.add_argument("--tile_size", 
                        help='Tile size [512]', metavar='PIXELS', type=int, default=512, 
                        dest='tile_size')       
    parser.add_argument('--overlap', 
                        help='Overlap of adjacent tiles [0]', metavar='PIXELS', type=int, default=0, 
                        dest='overlap')
    parser.add_argument('--background', 
                        help='Max background threshold [50]; percentage of background allowed', metavar='PIXELS', type=float, default=50, 
                        dest='background_threshold')
    parser.add_argument('--magnification', 
                        help='Magnification at which tiling should be done [20]', metavar='PIXELS', choices=range(0,100), type=float, default=20, 
                        dest='magnification')                    
    

    args = parser.parse_args()

    print('Reading input data from %s' %(args.slidespath))
    slides = glob(args.slidespath) # get all images from the data folder

    for i in range(len(slides)):
        slidepath = slides[i]
        basenameJPG = os.path.splitext(os.path.basename(slidepath))[0] 
        basename = os.path.join(args.output_folder, basenameJPG)
        print('Processing: %s' %(basenameJPG))

        # Generate tiles
        slide = open_slide(slidepath)
        dz = DeepZoomGenerator(slide, args.tile_size, args.overlap, limit_bounds=True)

        # Get downsampling factors for the slide, information about the microscope's objective and available magnifications
        factors = slide.level_downsamples
        try: 
            objective = float(slide.properties[openslide.PROPERTY_NAME_OBJECTIVE_POWER])
        except: 
            print('%s: no objective information found. Slide is skipped.' %(basenameJPG))
            continue 
        available = tuple(objective/x for x in factors) # magnifications that are available

        for level in range(dz.level_count-1, -1, -1):
            this_magnification = available[0]/pow(2, dz.level_count - (level+1)) # compute the magnification depending on the recent level  
            if this_magnification != args.magnification: # check if this is the desired magnification, otherwise move on 
                continue 
            
            tiledir = os.path.join('%s_files' %(basename), str(this_magnification)) 
            if not os.path.exists(tiledir):
                os.makedirs(tiledir)
            
            cols, rows = dz.level_tiles[level] # get number of tiles in this label as (nr_tiles_xAxis, nr_tiles_yAxis)
            for row in range(rows):
                for col in range(cols): 
                    tilename = os.path.join(tiledir, '%d_%d.%s' %(col, row, 'jpeg'))
                    if not os.path.exists(tilename):
                        tile = dz.get_tile(level, (col, row)) # adress=(col,row)
                        # only store tile if there is enough amount of information, i.e. low amount of background
                        avg_Bkg = get_Bkg(tile)
                        if avg_Bkg <= (args.background_threshold / 100.0):
                            tile.save(tilename, quality=90)
