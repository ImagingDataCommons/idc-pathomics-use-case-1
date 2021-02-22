import pandas as pd 


def extract(predictions) -> pd.DataFrame:
    for idx, row in predictions.predictions.iterrows():
        print(row['prediction'], type(row['prediction']))
        print(row['prediction'].index(max(row['prediction']))) 
    #luad_tiles = df[df['prediction'].index(max(df['prediction'])) == 1]
    #print(luad_tiles)

    #predictions.predictions['prediction']
    # maximum value at index 1 = luad tile 
    #all_slide_ids = list(set(predictions.predictions['slide_id'].tolist()))
    #for slide_id in all_slide_ids:
    #    slide_predictions = predictions.get_predictions_for_slide(slide_id)
        