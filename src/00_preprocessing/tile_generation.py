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
from optparse import OptionParser
from multiprocessing import Process, JoinableQueue
import openslide 
from openslide import open_slide, ImageSlide
from openslide.deepzoom import DeepZoomGenerator
from unicodedata import normalize

# TODO
# - documentation code
# - associated images?! 
# - replace optparse by argsparse! 


class TileWorker(Process):
    """ 
    TODO Documentation 
    Attributes:
    -----------
    Methods:
    --------
    """ 

    def __init__(self, queue, slidepath, tile_size, overlap, limit_bounds, quality, background_threshold):
        Process.__init__(self, name='TileWorker')
        self.daemon = True
        self._queue = queue 
        self._slidepath = slidepath 
        self._tile_size = tile_size 
        self._overlap = overlap 
        self._limit_bounds = limit_bounds 
        self._quality = quality 
        self._slide = None 
        self._background_threshold = background_threshold 

    def run(self):
        """
        TODO the tiling is done here, tasks are put into the queue by DeepZoomImageTiler _write_tiles()
        """ 
        self._slide = open_slide(self._slidepath)
        last_associated = None
        dz = self._get_dz()

        while True:
            data = self._queue.get()
            if data is None: # ???? 
                self._queue.task_done()
                break 
            associated, level, address, outfile = data 
            if last_associated != associated:
                dz = self._get_dz(associated)
                last_associated = associated

            try:
                tile = dz.get_tile(level, address)
                # only store tile if there is enough amount of information, i.e. low amount of background
                avg_Bkg = self._get_Bkg(tile)
                if avg_Bkg <= (self._background_threshold / 100.0):
                    tile.save(outfile, quality=self._quality)
                self._queue.task_done()
            except Exception as e:
                print("Slide %s failed at dz.get_tile for level %f" %(self._slidepath, level), '\n', e)
                self._queue.task_done 

    def _get_dz(self, associated=None):
        """ 
        TODO Documentation - get deep zoom generator 
        """ 
        # would OpenSlide be better??? what is meant with associated? 
        if associated is not None: 
            image = ImageSlide(self._slide.associated_images[associated])
        else: 
            image = self._slide 
        dz = DeepZoomGenerator(image, self._tile_size, self._overlap, limit_bounds=self._limit_bounds)

        return dz 

    def _get_Bkg(self, tile):
        """
        TODO Documentation 
        """ 
        grey = tile.convert(mode='L') # mode 'L' 
        bw = grey.point(lambda x: 0 if x < 220 else 1, mode='F')
        avg_Bkg = np.average(np.array(np.asarray(bw)))
        return avg_Bkg


class DeepZoomImageTiler(object):
    """ 
    TODO Documentation
    Handles generation of tiles and metadata for a single image.
    """ 

    def __init__(self, dz, slide, queue, associated, basename, basenameJPG, format, magnification):
        self._dz = dz 
        self._slide = slide 
        self._queue = queue 
        self._associated = associated
        self._basename = basename 
        self._basenameJPG = basenameJPG
        self._format = format  
        self._magnification = magnification
        self._processed = 0
        
    def run(self):
        self._write_tiles()
        self._write_dzi()

    def _write_tiles(self):
        """
        TODO Documentation: 
        for every level 
        put tasks into queue 
        """
        
        # Get downsampling factors for the slide, information about the microscope's objective and available magnifications
        factors = self._slide.level_downsamples
        try: 
            objective = float(self._slide.properties[openslide.PROPERTY_NAME_OBJECTIVE_POWER])
        except: 
            print('%s: no objective information found' %(self._basenameJPG))
            return 
        available = tuple(objective/x for x in factors) # magnifications that are available

        # Create the tiling tasks and put them in the queue
        for level in range(self._dz.level_count-1, -1, -1):
            this_magnification = available[0]/pow(2, self._dz.level_count - (level+1)) # compute the magnification depending on the recent level 
            if self._magnification > 0: 
                if this_magnification != self._magnification: # check if we have the desired magnification, otherwise discard 
                    continue 
            
            tiledir = os.path.join('%s_files' %(self._basename), str(this_magnification)) 
            if not os.path.exists(tiledir):
                os.makedirs(tiledir)
            
            cols, rows = self._dz.level_tiles[level] # get number of tiles in this label as (nr_tiles_xAxis, nr_tiles_yAxis)
            for row in range(rows):
                for col in range(cols): 
                    tilename = os.path.join(tiledir, '%d_%d.%s' %(col, row, self._format))
                    if not os.path.exists(tilename):
                        self._queue.put((self._associated, level, (col,row), tilename)) # put the tiling task in the queue
                    self._tile_done()

    def _tile_done(self):
        self._processed = 1
        count, total = self._processed, self._dz.tile_count 
        if count % 100 == 0 or count == total:
            print('Tiling %s: wrote %d/%d tiles' %(self._associated or 'slide', count, total), end='\r', file=sys.stderr)
            if count == total:
                print(file=sys.stderr)

    def _write_dzi(self):
        with open('%s.dzi' %(self._basename), 'w') as out:
            out.write(self.get_dzi())

    def get_dzi(self):
        return self._dz.get_dzi(self._format)


class DeepZoomStaticTiler(object): 
    """
    TODO Documentation, code is from openslide example and modified by coudray
    Handles generation of tiles and metadata for all images in a slide. <-- images in a slide???
    """ 

    def __init__(self, slidepath, basename, basenameJPG, format, tile_size, overlap, limit_bounds, quality, workers, background_threshold, magnification):
        self._slide = open_slide(slidepath)
        self._basename = basename 
        self._basenameJPG = basenameJPG
        self._format = format
        self._tile_size = tile_size
        self._overlap = overlap
        self._limit_bounds = limit_bounds
        self._workers = workers 
        self._magnification = magnification 
        self._queue = JoinableQueue(2 * workers)
        self._dzi_data = {}
        for i in range(workers):
            TileWorker(self._queue, slidepath, tile_size, overlap, limit_bounds, quality, background_threshold).start()

    def run(self):
        self._run_image()
        self._shutdown()

    def _run_image(self, associated=None):
        """
        TODO 
        """
        if associated is None: 
            image = self._slide 
            basename = self._basename
        
        else: 
            image = ImageSlide(self._slide.associated_images[associated])
            basename = os.path.join(self._basename, self._slugify(associated))
        
        # Instantiate generator and image tiler
        dz = DeepZoomGenerator(image, self._tile_size, self._overlap, limit_bounds=self._limit_bounds)
        tiler = DeepZoomImageTiler(dz, self._slide, self._queue, associated, basename, self._basenameJPG, self._format, self._magnification)
        tiler.run()
        self._dzi_data[self._url_for(associated)] = tiler.get_dzi()

    def _url_for(self, associated): 
        """
        TODO Documentation 
        """
        if associated is None: 
            base = 'slide'
        else: 
            base = self._slugify(associated)
        return '%s.dzi' %(base)
    
    @classmethod
    def _slugify(cls, text):
        """
        TODO 
        """
        text = normalize('NFKD', text.lower()).encode('ascii', 'ignore').decode()
        return re.sub('[^a-z0-9]+', '_', text)
    
    def _shutdown(self):
        """
        TODO 
        """
        for _i in range(self._workers):
            self._queue.put(None)
        self._queue.join()


if __name__ == '__main__':
    parser = OptionParser(usage='Usage: %prog [options] <path-to-slides>')
    parser.add_option('-L', '--ignore-bounds', dest='limit_bounds', 
                default=True, action='store_false',
                help='Display entire scan area') 
    parser.add_option('-e', '--overlap', metavar='PIXELS', dest='overlap',
                type='int', default=0,
                help='Overlap of adjacent tiles [1]')
    parser.add_option('-f', '--format', metavar='{jpeg|png}', dest='format',
                default='jpeg',
                help='Image format for the tiles [jpeg]')
    parser.add_option('-j', '--jobs', metavar='COUNT', dest='workers',
                type='int', default=4,
                help='Number of worker processes to start [4]')
    parser.add_option('-o', '--output', metavar='NAME', dest='output_folder',
                help='Full path to output folder')
    parser.add_option('-Q', '--quality', metavar='QUALITY', dest='quality',
                type='int', default=90,
                help='JPEG compression quality [90]') 
    parser.add_option('-s', '--size', metavar='PIXELS', dest='tile_size',
                type='int', default=254,
                help='Tile size [254]')
    parser.add_option('-B', '--Background', metavar='PIXELS', dest='_background_threshold',
		        type='float', default=50,
		        help='Max background threshold [50]; percentager of background allowed')
    parser.add_option('-M', '--Mag', metavar='PIXELS', dest='magnification',
		type='float', default=20,
		help='Magnification at which tiling should be done (-1 means at any magnification available)') 

    (opts, args) = parser.parse_args()
    try:
        slidespath = args[0]
    except IndexError:
        parser.error('Missing slidespath argument')
    if opts.output_folder is None: 
        opts.output_folder = os.path.splittext(os.path.basename(slidespath))[0]

    print('Reading input data %s' %(slidespath))
    slides = glob(slidespath) # get all images from the data folder

    for i in range(len(slides)):
        slidepath = slides[i]
        opts.basenameJPG = os.path.splitext(os.path.basename(slidepath))[0] 
        print('Processing: %s' %(opts.basenameJPG))
        basename = os.path.join(opts.output_folder, opts.basenameJPG)

        # Generate tiles
        DeepZoomStaticTiler(slidepath, basename, opts.basenameJPG, opts.format, opts.tile_size, opts.overlap, opts.limit_bounds, 
                            opts.quality, opts.workers, opts._background_threshold, opts.magnification).run()
