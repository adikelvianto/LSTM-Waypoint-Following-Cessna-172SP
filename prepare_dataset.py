# Import Library
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os 
import glob
import h5py

from function.file_prep import unzip_and_rename, processing_mat_file_to_csv, concat_csv

# Define folder path of zip train & test
zip_train_dir = r"\file\zip\train"
zip_test_dir = r"\file\zip\test"

# Define folder path of extracted train & test
extracted_train_dir = r"\file\mat\train"
extracted_test_dir = r"\file\mat\test"

# Define folder path of converted csv train & test
csv_train_dir = r"\file\csv\train"
csv_test_dir = r"\file\csv\test"

# Define list of column name that want to be filtered using low pass filter
filter_column = ['JSRoll', 'phi']


# --------------------------------------------------------------------------------

# Do unzip and rename for both train data & test data
unzip_and_rename(zip_train_dir, extracted_train_dir)
unzip_and_rename(zip_test_dir, extracted_test_dir)

# Converting .mat train to .csv by resampling sample rate into 4 seconds
processing_mat_file_to_csv(extracted_train_dir, csv_train_dir, filter_column)
processing_mat_file_to_csv(extracted_test_dir, csv_test_dir, filter_column)

# Concatenate all csv files in folder train also test to become dataset
train_dataset_name = "train_dataset.csv"
test_dataset_name = 'test_dataset.csv'

concat_csv(csv_train_dir, train_dataset_name)
concat_csv(csv_test_dir, test_dataset_name)