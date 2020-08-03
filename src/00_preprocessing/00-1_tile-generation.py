""" 
TODO Documentation + Licence 

<https://github.com/ncoudray/DeepPATH/blob/master/DeepPATH_code/00_preprocessing/0b_tileLoop_deepzoom4.py>
<https://github.com/openslide/openslide-python/blob/master/examples/deepzoom/deepzoom_tile.py>

""" 

# Import libraries
import numpy as np 

from multiprocessing import Process, JoinableQueue
import openslide 
from openslide import open_slide, ImageSlide
from openslide.deepzoom import DeepZoomGenerator


class TileWorker(Process):
    """ 
    TODO Documentation 
    Attributes:
    -----------
    Methods:
    --------
    """ 

    def __init__(self, queue, slidepath, tile_size, overlap, limit_bounds, quality, _Bkg_threshold):
        Process.__init__(self, name='TileWorker')
        self.daemon = True
        self._queue = queue 
        self._slidepath = slidepath 
        self._tile_size = tile_size 
        self._overlap = overlap 
        self._limit_bounds = limit_bounds 
        self._quality = quality 
        self._slide = None 
        self._Bkg_threshold = _Bkg_threshold # from coudray 

    def run(self):
        """
        TODO 
        """ 
        self._slide = open_slide(self._slidepath)
        last_associated = None
        dz = self._get_dz()

        while True:
            data = self._queue.get()
            if data is None: # ???? 
                self._queue.task_done()
                break 
            associated, level, address, outfile = data # more things in coudray code 
            if last_associated != associated:
                dz = self._get_dz(associated)
                last_associated = associated

            try:
                tile = dz.get_tile(level, address)
                # only store tile if there is enough amount of information, i.e. low amount of background
                avg_Bkg = get_Bkg(tile)
                if avg_Bkg <= (self._Bkg_threshold / 100.0):
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
    TODO Documentation, code is from coudray and not part of openslide example
    Handles generation of tiles and metadata for a single image.
    """ 

    def __init__(self, dz, queue, associated, basename, format):
        self._dz = dz 
        self._queue = queue 
        self._associated = associated
        self._basename = basename 
        self._format = format  
        self._processed = 0
        # to be completed by things needed from coudray 
        
    def run(self):
        self._write_tiles()
        self._write_dzi()

    def _write_tiles(self):
        """
        TODO Documentation 
        """

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

    def _get_dzi(self):
        return self._dz.get_dzi(self._format)

    # other methods by coudray needed? 


class DeepZoomStaticTiler(object): 
    """
    TODO Documentation, code is from openslide example and modified by coudray
    Handles generation of tiles and metadata for all images in a slide. <-- images in a slide???
    """ 

    def __init__(self, slidepath, basename, format, tile_size, overlap, limit_bounds, quality, workers, with_viewer):
        self._slide = open_slide(slidepath)
        self._basename = basename
        self._format = format
        self._tile_size = tile_size
        self._overlap = overlap
        self._limit_bounds = limit_bounds
        self._workers = workers 
        self._with_viewer = with_viewer
        self._queue = JoinableQueue(2 * workers)
        self._dzi_data = {}
        for i in range(workers):
            TileWorker(self._queue, slidepath, tile_size, overlap, limit_bounds, quality).start()

    def run(self):
        """
        TODO 
        """

    def _run_image(self, associated=None):
        """
        TODO 
        """
    def _url_for(self, associated): 
        """
        TODO 
        """
    def _write_html(self): 
        """
        TODO 
        """
    def _write_static(self): 
        """
        TODO 
        """
    def _copydir(self, src, dest):
        """
        TODO 
        """
    
    @classmethod
    def _slugify(cls, text):
        """
        TODO 
        """
    
    def_shutdown(self):
        """
        TODO 
        """


if __name__ == '__main__':
    echo('Hello world')