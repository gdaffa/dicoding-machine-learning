import time
from datetime import datetime
import requests
import argparse

import pandas as pd
import numpy as np

from scipy.io.arff import loadarff
from sklearn.metrics import r2_score

URL = 'http://localhost:8000/predict'

MIN_TIME = 5
MAX_TIME = 9 # Will be added by 1

# Get identifier for each executed script.
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('id', default=1)
args = arg_parser.parse_args()

data, _    = loadarff('dataset/diamonds-price.arff')
total_data = len(data)

# Load the dataset and convert `byte` type to a `string` type.
df = pd.DataFrame(data)
category_cols     = df.select_dtypes('object').columns
df[category_cols] = df[category_cols].apply(lambda series: series.str.decode('utf-8'))

df_feat = df.drop(columns='price')
y_true  = df['price']

def print_log(*values):
   '''
   To log the action with time in console.
   '''
   print(datetime.now().strftime('[%H:%M:%S]'), f'ID {args.id}:', *values)

def run_request(time_passed):
   '''
   Sending request depend on how much time passed.
   It always add 1 to keep data selected.
   '''
   # Calculate how much sample data can be cover.
   cov_percent = (time_passed - MIN_TIME + 1) / (MAX_TIME - MIN_TIME + 1)
   print_log(f'Covering {cov_percent * 100:.2f}%.')

   # Get sample count randomized with maximum data count from coverage.
   max_sample_amount = np.ceil(total_data * cov_percent)
   sample_count      = np.random.randint(1, max_sample_amount)
   print_log(f'Sending {sample_count} request.')

   df_sample = df_feat.sample(sample_count)
   response  = requests.post(URL, json=df_sample.to_dict('list'))
   print_log(f'Request sended successfully.')

   if response.status_code == 200:
      index = df_sample.index
      return r2_score(y_true[index], response.json())
   else:
      return response.text

# Call the request until it stopped by the user.
while True:
   waiting_time = np.random.randint(MIN_TIME, MAX_TIME)
   print_log(f'Sleep for {waiting_time} seconds...')
   time.sleep(waiting_time)
   print_log(run_request(waiting_time))