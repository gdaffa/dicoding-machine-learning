import json
from pandas import read_csv

def get_metadata():
   with open('metadata.json', 'r', encoding='utf-8') as file:
      metadata = json.load(file)
   return metadata

def get_testset(filename, **kwargs):
   def_kwargs = {
      'dtype': 'object',
      'index_col': 0
   }
   def_kwargs.update(kwargs)

   return read_csv(f'testset/{filename}', **def_kwargs)