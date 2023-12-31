# Input - results csv / df
# Output - tif file with recovery rates, rsq, and local min for each 
# recovery as a layer 
# take calculated return rates and turn them into maps / layers 

import pandas as pd
import rasterio as rs
# from rasterio import features
import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib.cm as cm
from matplotlib.colors import ListedColormap
from df_to_map import df_to_map
import pickle


# get results you want to process
county = input('Input the county to process: ')

#./RESULTS/V2/
ndvi_results = pd.read_csv('ndvi_results_'+county+'_V2.csv')


#get metadata back
with open('veg_meta.pkl', 'rb') as file:
    ndvi_meta, ndvi_bound =pickle.load(file)

col_names = ndvi_results.filter(like = 'recov').columns.values.tolist() + ndvi_results.filter(like = 'rsq').columns.values.tolist()+ ndvi_results.filter(like = 'min').columns.values.tolist()
    
ndvi_results_array = df_to_map(ndvi_results, col_names, savefile=True, 
                             fname='ndvi_results_'+county+'_V2.tif', meta=ndvi_meta)

# plt.imshow(ndvi_results_array[:,:,0])
# plt.show()

print('donezo')