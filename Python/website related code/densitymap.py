"""
Given a dataframe with x_coord, y_coord, produce a density map given the criteria provided
as inuput
"""

import pandas as pd
import numpy as np
import math
from scipy import ndimage

# data range: x_range=(-10, 130), y_range=(-10, 90)
x_arr = np.arange(-10, 130)
y_arr = 90 - np.arange(100)

## Produce a 140 * 100 array that represents the density given the condition
def grid_mat(df, rating_bar = 0, review_num = 1):
    """
    Given a df (either all doctors, or a specific category), create a grid matrix that shows the number of points within each
    grid that satisfy the rating_bar (rating >= rating_bar) and minimum review_num (review_count >= review_num)
    
    parameters
    ----------
    df: dataframe that contains the relevant info
    rating_bar: the threshold of the rating
    review_num: the minimum review count
               
    Returns
    -------
    A 140 * 100 array that represents the grid density map  
    """
    
    df['grid_x'] = df['coord_x'].map(lambda x: int(x) + 10)
    df['grid_y'] = df['coord_y'].map(lambda x: 90 - int(x))
    # rating smaller than rating_bar is filtered out
    df_rateF = df[df['rating'] >= rating_bar]
    # review count smaller than review_num is filtered out
    df_rateF_revF = df_rateF[df_rateF['review_count'] >= review_num]
    df_gped = df_rateF_revF.groupby(['grid_x', 'grid_y']).size()
    
    grid_matrix = np.zeros((140, 100))
    for index in df_gped.index:
        row, col = index
        if (col >= 0 and col < 100) and (row >= 0 and row < 140):
            grid_matrix[row, col] = df_gped.ix[index]
    return grid_matrix
            
# return a dataframe that 
def density_map(grid_matrix, filter_dist):
    filter_size = 2 * filter_dist + 1
    return ndimage.filters.uniform_filter(grid_matrix, size = filter_size)
    
def main(filename, rate_bar, rev_num, f_dist):
    data = pd.read_csv(filename)
    grid_matrix = grid_mat(data, rating_bar = rate_bar, review_num = rev_num)
    density_map_mat = density_map(grid_matrix, f_dist)
    g_x = np.repeat(x_arr, 100)
    g_y = np.tile(y_arr, 140)
    count = density_map_mat.reshape(14000)
    df = pd.DataFrame({'g_x':g_x, 'g_y':g_y, 'count': count})
    df_nz = df[df['count'] > 0.0001]
    output_name = filename[:-4] + '_rb' + str(rate_bar) + '_revc'+ str(rev_num) + '_densitymap.csv'
    df_nz.to_csv(output_name)
    
if __name__ == '__main__':
    filename = 'static/data_RH.csv' 
    rate_arr = [0.0, 3.5, 4.0, 4.5, 5.0]
    rev_num_arr = [0, 10]
    for rate_bar in rate_arr:
        for rev_num in rev_num_arr:
            main(filename, rate_bar, rev_num, 1)
    