import pandas as pd 


def extract(predictions) -> pd.DataFrame:
    luad_tiles = []
    for idx, row in predictions.predictions.iterrows():
        if row['prediction'].index(max(row['prediction'])) == 1: 
            coord_string = [str(x) for x in row['tile_position']]
            luad_tiles.append('tiles/'+ row['slide_id']+'_files/20.0/'+ '_'.join(coord_string) +'.jpeg')
    return luad_tiles 