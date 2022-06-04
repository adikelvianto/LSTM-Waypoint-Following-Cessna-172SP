# Import library
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# Function to create correlation tablle separated positive and negative

def df_corr(df,var):
    """clean up NaN values after using correlation function, convert it into percentage,
    convert it as dataframe both for positive and negative value,
    and sort descending for the absolute value.
    (df is dataframe that want to be analyzed, and var is name of parameter which we want to correlate)"""
    
    # Positive values section
    
    # Calculating pos_correlation of all dataframe in percent
    corr = np.round(df.corr()*100,2)
    
    # Sort pos_correlation value descending
    corr = corr.sort_values(by=[var], ascending=False)[var]
    corr = corr.to_frame() # Convert series to DataFrame
    corr = corr.dropna() # Drop NaN values of the DataFrame

    # Create new column for positive pos_correlation value
    pos_corr = corr[[var]].copy() # Create a copy of correlation dataframe
    pos_corr['pos_cor_'+ var] = pos_corr[var].where(pos_corr[var]>0)

    # Drop original column
    pos_corr.drop(var,axis=1,inplace=True)

    # Drop NaN value as a result of filtering positive value only
    pos_corr = pos_corr.dropna(subset=['pos_cor_'+ var])
    
# -----------------------------------------------------------------------
    # Negative values section
    
    # Create new column for negative correlation value
    neg_corr = corr[[var]].copy() # Create a copy of correlation dataframe
    neg_corr['neg_corr'+ var] = neg_corr[var].where(neg_corr[var]<0)

    # Drop original column
    neg_corr.drop(var,axis=1,inplace=True)

    # Drop NaN value as a result of filtering positive value only
    neg_corr = neg_corr.dropna(subset=['neg_corr'+ var])
    neg_corr = neg_corr.sort_values(by=['neg_corr'+ var],axis=0, ascending=True)

    return pos_corr, neg_corr

# Function to convert specific dataframe column name to array
def df_to_array(df,list):
    '''Pass dataframe column name as list and convert it to array
    df is whole dataframe and list argument is column name you want to convert'''
    
    # Count how many variable in list
    count = len(list)
    # Create new blank dataframe
    new_df = pd.DataFrame()
    
    for i in range(count):
        new_df[list[i]] = df[list[i]]
    
    array = new_df.iloc[:,0:].values
    
    return array

# Function to correcting yaw error value
def yaw_error_corrected(df):
    '''Calculate yaw error that have shortest angle to turn'''
    
    psi = df['psi'].values
    ref = df['yaw_reff'].values

    # Modified angle 
    for row in range(len(df)):
        if psi[row] >= 180:
            psi[row] = psi[row]- 360

    for row in range(len(df)):
        if ref[row] >= 180:
            ref[row] = ref[row]- 360

    # Calculate Yaw Error and assign back to dataframe
    mye1 = (psi - ref)
    mye2 = np.empty(shape=(len(df),), dtype=object)
    mye = np.empty(shape=(len(df),), dtype=object)

    for row in range(len(df)):
        if mye1[row] <= 0:
            mye2[row] = mye1[row] + 360;
        else:
            mye2[row] = mye1[row] - 360;

        if abs(mye1[row]) <= abs(mye2[row]):
            mye[row] = mye1[row];
        else:
            mye[row] = mye2[row];

    df['yaw_error'] = mye
    
    return df

# Function to locate index of each waypoint defined
def index_wp(df):
    '''Find the first index of each waypoint'''

    wp_x_list = df['x_wp'].tolist()
    wp_y_list = df['y_wp'].tolist()
    num_wp_list = df['num_wp'].tolist()

    # Create list of x waypoint in sequence refer to waypoint -n index
    indexes_x = np.unique(num_wp_list,return_index=True)[1]  #Showing first occurance index 
    xx = [wp_x_list[index] for index in sorted(indexes_x)]
    indexes_x.sort()   # Sort the index ascending

   # Create new index and xx variable for the last point of waypoint
    indexes_x = indexes_x.tolist()
    print(indexes_x)
    indexes_x.insert(len(indexes_x)+1,len(df))
    indexes_x.pop(0)
    
    return indexes_x