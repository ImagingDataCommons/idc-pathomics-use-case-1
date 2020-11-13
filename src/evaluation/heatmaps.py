import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# for 2-class problem --> visualize probability for being cancer
def create_heatmap_for_slide_2class(df, slide_id, output_path):
    
    predictions = df.loc[df['slide_id'] == slide_id]['predictions'].tolist()
    coordinates = df.loc[df['slide_id'] == slide_id]['coordinates'].tolist()
    max_cols, max_rows = max([c[0] for c in coordinates]) + 1, max([c[1] for c in coordinates]) + 1
    reference_value = df.loc[df['slide_id'] == slide_id]['reference_value'].tolist()[0]
    
    slide_heatmap = -1 * np.ones((max_rows, max_cols))
    for coord, pred in zip(coordinates, predictions):
        slide_heatmap[coord[1], coord[0]] = pred
    
    return slide_heatmap

    # convert and save as image 
    #cmap = plt.get_cmap('coolwarm')
    #cmap.set_under('k', alpha=0)
    #plt.imshow(hm, cmap=cmap, vmin=0.0)
    

def create_heatmap_for_slide_3class(df, slide_id, output_path):
    
    predictions = df.loc[df['slide_id'] == slide_id]['predictions'].tolist()
    coordinates = df.loc[df['slide_id'] == slide_id]['coordinates'].tolist()
    max_cols, max_rows = max([c[0] for c in coordinates]) + 1, max([c[1] for c in coordinates]) + 1
    reference_value = df.loc[df['slide_id'] == slide_id]['reference_value'].tolist()[0]
    
    slide_heatmap = -1 * np.ones((max_rows, max_cols, 3))
    for coord, pred in zip(coordinates, predictions):
        slide_heatmap[coord[1], coord[0], pred.index(max(pred))] = max(pred)
    
    slide_heatmap_luad = slide_heatmap[:, :, 0]
    slide_heatmap_lusc = slide_heatmap[:, :, 1]
    slide_heatmap_norm = slide_heatmap[:, :, 2]
    
    return slide_heatmap_luad, slide_heatmap_lusc, slide_heatmap_norm
    