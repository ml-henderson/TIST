#Maddie Henderson
# take a df of pixels through time, linearly fill gaps up to 2 months
# grab only sections that are continuous for more than 4 years
# use STL to decomp those sections and keep residual 

# import geopandas as gp 
import pandas as pd
# import rasterio as rs
# from rasterio import features
import numpy as np 
import matplotlib.pyplot as plt 
import STL_Fitting as stl
import pickle


# Load the veg data #############################################
county = input('Input the county to process: ')
# county = 'Tharaka'

ndvi_df = pd.read_csv('./intermediate landsat things/ndvi_pixels_'+county+'.csv', nrows=1000) #TEMP for testing , nrows =1000

nrows, dum = ndvi_df.shape
dates = pd.date_range(start='5/1/2013', periods=120, freq='MS')

#interpolate up to 2 missing points since a season is usually 3 months
# will lose about 20% ? of pixels this way 
smoothed_ndvi_df = ndvi_df.iloc[:, 4:].astype("float32").interpolate(method='linear', limit=2, axis = 1, limit_area='inside')

# Get an example plot
# plt.plot(dates, ndvi_df.iloc[55, 4:], 'go')
# plt.plot(dates, smoothed_ndvi_df.iloc[55, :], 'b-')
# plt.title('Example linear interpolation (Tharaka)')
# plt.xlabel('date')
# plt.ylabel('NDVI value')
# plt.legend('original', 'filled')
# plt.show()


#add a nan column to the end after interpolation so that it always splits on that 
smoothed_ndvi_df['empty']=np.nan
mask  = np.empty((nrows, 121)).flatten() #make a mask the size of the data 
mask[:] = np.nan 


#https://stackoverflow.com/questions/41494444/pandas-find-longest-stretch-without-nan-values

flat_ndvi = smoothed_ndvi_df.values.flatten().astype('float32')
m = np.concatenate(( [True], np.isnan(flat_ndvi), [True] ))  
ss = np.flatnonzero(m[1:] != m[:-1]).reshape(-1,2)   # Start-stop limits - for the whole df flattened to 1D
#get any sections longer than 48 pts in this row because need a few years for good seasonal decomp
ss = ss[((ss[:,1] - ss[:,0]) >= 48)]

#set everything outside of these intervals to NaN
for start, stop in ss:
    mask[start:stop] = 1

#apply mask - now all 'rows' have either 1 or 2 longer continuous runs 
flat_ndvi = flat_ndvi * mask

# STL decomp ###########################################
ndvi_res_flat = np.empty((nrows, 121)).flatten()
ndvi_res_flat[:] = np.nan

for start, stop in ss: 
    sample = flat_ndvi[start:stop] #get the continuous slice 
    #apply the decomp and get residual
    decomp = stl.robust_stl(sample, period = 12, smooth_length = 21)
    ndvi_res_flat[start:stop] = decomp.resid

    # decomp.plot()
    # plt.xticks(rotation=90)
    # plt.suptitle('STL')
    # plt.show()
    
smoothed_ndvi_df.loc[:,:] = ndvi_res_flat.reshape(nrows, 121)

#find the mean and std dev of the residuals after decomposing 
mean = smoothed_ndvi_df.mean(axis = 1)
stdev = smoothed_ndvi_df.std(axis = 1)
smoothed_ndvi_df = pd.concat([smoothed_ndvi_df, mean.rename('mean'), stdev.rename('stdev')], axis = 1)
#copy over the rows and columns etc
smoothed_ndvi_df = pd.concat([ndvi_df[['row','col','tist', 'county']], smoothed_ndvi_df], axis = 1)

#get the rows and cols of array that the ss is referring to once ndvi is reshaped 
ss_cols = ss % 121 #this now more closely aligns with the date 
ss_rows = np.floor(ss[:,0] / 121) #gives the row of the dataframe that it corresponds to 

#do NOT delete rows without enough data yet- makes it annoying to deal with loc instead of iloc 

#Save to CSV - writes indices to col 0
smoothed_ndvi_df.to_csv('ndvi_residuals_'+county+'.csv', encoding='utf-8', index=True)

#Save the ss !!
with open(county+'_ss.pkl', 'wb') as file:
    # A new file will be created
    pickle.dump([ss, ss_rows, ss_cols], file)

print('donezo')
