import numpy as np
import copy
import matplotlib
import matplotlib.pyplot as plt
from typing import List

from evaluation.predictions import Predictions 

class Heatmap():
    """ Represents a heatmap visualization for one whole slide image """

    def __init__(self, predictions: Predictions, slide_id: str, colormap_strings: List[str]) -> None:
        pred = predictions.get_predictions_for_slide(slide_id)
        coord = predictions.get_tile_positions_for_slide(slide_id)
        max_cols, max_rows = max([c[0] for c in coord]) + 1, max([c[1] for c in coord]) + 1
        colormaps = self._get_colormaps(colormap_strings)

        # create heatmap
        slide_heatmap = -1 * np.ones((max_rows, max_cols, 4))
        for c, p in zip(coord, pred):
            print('p', p)
            colormap_to_use = colormaps[p.index(max(p))] 
            slide_heatmap[c[1], c[0], :] = colormap_to_use(max(p))
        
        self.slide_heatmap = slide_heatmap


    def _get_colormaps(self, colormap_strings: List[str]) -> List[matplotlib.colors.Colormap]:
        colormaps = []
        for cstring in colormap_strings:
            cmap = copy.copy(plt.cm.get_cmap(cstring))
            cmap.set_over(alpha=0)
            cmap.set_under(alpha=0)
            colormaps.append(cmap)
        return colormaps
    
    def plot(self, output_path: str) -> None:
        plt.imshow(self.slide_heatmap)
        plt.savefig(output_path)