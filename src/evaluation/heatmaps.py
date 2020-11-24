import numpy as np
import copy
import matplotlib.pyplot as plt

from evaluation.predictions import Predictions 


def generate_heatmap_for_slide(predictions, slide_id, colormap_strings):
    pred = predictions.get_predictions_for_slide(slide_id)
    coord = predictions.get_tile_positions_for_slide(slide_id)
    max_cols, max_rows = max([c[0] for c in coord]) + 1, max([c[1] for c in coord]) + 1
    colormaps = _get_colormaps(colormap_strings)

    # create heatmap
    slide_heatmap = -1 * np.ones((max_rows, max_cols, 4))
    for c, p in zip(coord, pred):
        p = p.tolist()
        colormap_to_use = colormaps[p.index(max(p))] 
        slide_heatmap[c[1], c[0], :] = colormap_to_use(max(p))
    
    return slide_heatmap
    

def _get_colormaps(colormap_strings):
    colormaps = []
    for cstring in colormap_strings:
        cmap = copy.copy(plt.cm.get_cmap(cstring))
        cmap.set_over(alpha=0)
        cmap.set_under(alpha=0)
        colormaps.append(cmap)
    return colormaps