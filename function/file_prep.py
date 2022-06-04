# Import library
import os
import zipfile
import glob
import h5py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from timeit import default_timer as timer
from datetime import datetime


# Function to unzip rar and rename 
def unzip_and_rename(source_dir, target_dir):
    """Unzip file and rename archive file, and assign it to target directory folder,
    source and target dir need too be absolute path
    source_dir containing full path of folder containing zip files
    target_dir containing destination folder to unpack .mat files"""
    
    # This is the name of file inside zip files
    filelist = ['FlightDataRecorder.mat']

    for item in os.listdir(source_dir):  # loop through items in dir
        if item.endswith(".zip"):  # check for ".zip" extension
            file_path = os.path.join(source_dir, item).replace("\\","/")  # get zip file path
            with zipfile.ZipFile(file_path) as zf:  # open the zip file
                for target_file in filelist:  # loop through the list of files to extract
                    if target_file in zf.namelist():  # check if the file exists in the archive
                        # generate the desired output name:
                        full_path = os.path.splitext(file_path)[0]
                        target_name = full_path.split('/')[-1] + ".mat"   # Create target name based on zip file name + extension .mat
                        target_path = os.path.join(target_dir, target_name).replace("\\","/")  # output path
                        with open(target_path, 'wb') as f:  # open the output path for writing
                            f.write(zf.read(target_file))

# Function to resample dataframe to certain sample rate
def resample_df(df,freq): 
    '''Resampling dataframe into some frequencies, fill freq parameters with string consisting of number and unit
    Example: to make the sampling rate become 4s, freq need to be fill with str(4S)'''

    time_s = df['index'].values # Convert 'time_s' column into array
    date_time = []

    # Looping over 'time_s' and append date_time empty list
    for x in time_s:
        dt_object = datetime.fromtimestamp(x)
        date_time.append(dt_object)

    df['date_time']= date_time  # Add date_time list as a dataframe
    date_time = pd.to_datetime(date_time)
    df = df.set_index('date_time') # Set 'date_time' as dataframe index
    df = df.resample(freq).first()
    df.reset_index(drop=True, inplace=True)
    
    return df

# Low Pass Filter Function
def low_pass_filter(df, filter_column):
    '''Passing list of column name that want to be low pass filtered using algorithm from 
    https://www.delftstack.com/howto/python/low-pass-filter-python/'''

    import numpy as np
    from scipy.signal import butter, lfilter, freqz

    def butter_lowpass(cutoff, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def butter_lowpass_filter(data, cutoff, fs, order=5):
        b, a = butter_lowpass(cutoff, fs, order=order)
        y = lfilter(b, a, data)
        return y
    
    # Setting standard filter requirements.
    order = 5
    fs = 30.0       
    cutoff = 3.667 

    # Calling function to create lowpass criteria
    b, a = butter_lowpass(cutoff, fs, order)

    storage = []
    # Looping over column name list to apply low pass filter function and store it to storage list
    for i in filter_column:
        data = df[i].tolist()
        y = butter_lowpass_filter(data, cutoff, fs, order)
        storage.append(y)

    # Looping to replace old column name value with value that have been filtered
    for j in range (len(filter_column)):
        df[filter_column[j]] = storage[j]
        
    return df

# Function to preprocessing .mat file and convert to csv file
def processing_mat_file_to_csv(mat_path, csv_path, filter_column):
    '''this function will loop over .mat file in a folder and do preprocessing data such as:
    cut early data, create coordinates from wp, low pass filtering, and convert each processed file to csv
    filter_column containing list of header column name that want to be filtered using low pass filter
    Ex: filter_column = ['left_ail', 'right_ail', 'rudder', 'phi','elevator']'''
    
    # Initiate Timer 
    top_timer = timer()
    start_time = timer()

    # Initiate file path of csv files
    mat_files = glob.glob(mat_path)
    
    # Creating empty list to store how many data is used
    values = []
    count = 0     
    
    for file in mat_files:
        # Read .mat file using python 
        f = h5py.File(file,'r')

        # Get file.keys() list to be used
        data  = f.get('FlightData')
        data = np.array(data)       # Convert FlightData to array
        df = pd.DataFrame(data)     # Convert array to Dataframe

        # Created 17 March 2022, with data channel list as follow:
        column_list = ['index','lat', 'lon', 'alt', 'X', 'Y', 'Z',
                       'psi', 'theta', 'phi','TAS', 'JSHead', 'JSPitch', 'JSRoll',
                      'throttle', 'thrust', 'fuel_flow', 'rudder', 'elevator',
                      'left_ail', 'right_ail', 'ground_speed', 'wind_speed', 'wind_dir',
                      'num_wp', 'x_wp', 'y_wp', 'z_wp', 'wp_dist', 'yaw_reff',
                      'wp_stat', 'ph_stat', 'wl_stat']

        df.columns = column_list    #Assign column_list variable as dataframe column name

        # Using pre-built function to resample dataframe to 4S
        df = resample_df(df, freq = '4S')

        # Using pre-built function to find closest intersection point between aircraft and waypoint

        # Using pre-built function to low pass filtered all column that mentioned above
        df = low_pass_filter(df, filter_column)
        
        # Save as new CSV files
        path = csv_path
        location = file.split("\\")[-1]
        file_name = location[:-4] + ".csv"
        df.to_csv(os.path.join(path,file_name))
        print('Done:', file.split("\\")[-1])   
        print('-------------------------------------------------------------------------------------------------------------------------------')
        values.append('1')
        
    print("Time used: {:.2f} minutes".format((timer() - start_time)/60))
    start_time   = timer()
    print("Number of used data:", len(values)) 

# Function to concatenate csv in folder
def concat_csv(csv_path, concatenated_file_name):
    '''csv_path containing folder consist of csv files to concat
    concatenated_file_name is concatenated csv file name'''

    os.chdir(csv_path)
    extension = 'csv'
    all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
    
    # Combine all files in the list
    combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ])
    # Export to csv with assigned name
    combined_csv.to_csv(concatenated_file_name, index=False, encoding='utf-8-sig')
