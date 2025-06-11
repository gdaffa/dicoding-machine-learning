from .helper import print_head, print_success, print_fail
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from sqlalchemy import create_engine
from copy import deepcopy

SERVICE_ACCOUNT_FILE = 'service-account.json'

def csv(metadata, df: pd.DataFrame):
   print_head('Saving Data to CSV')

   new_metadata = deepcopy(metadata)
   new_metadata['repo']['csv'] += 1

   # Save with unique id each set.
   try:
      df = df.copy()
      df.index += 1

      filename = f'dataset{new_metadata["repo"]["csv"]}.csv'
      df.to_csv(f'datasets/{filename}', index_label='id')

   except Exception as e:
      print_fail(f'Failed to save to CSV: {e}')
      return metadata

   print_success(f'Saved to CSV as `{filename}`.')
   return new_metadata

def spreadsheet(metadata, df: pd.DataFrame):
   print_head('Saving Data to Google Spreadsheet')

   new_metadata = deepcopy(metadata)
   new_metadata['repo']['spreadsheet'] += df.shape[0]

   try:
      # Add id column and change `price` column data type into float.
      df = df.copy()
      df.index += metadata['repo']['spreadsheet'] + 1
      df = df.reset_index()
      df['price'] = df['price'].astype('float32')

      # Calculate subset how much column and row are needed.
      subset_x = [ 'A', chr(64 + df.shape[1]) ]
      subset_y = [
         metadata['repo']['spreadsheet'] + 2,
         new_metadata['repo']['spreadsheet'] + 2
      ]
      range_str = f'{subset_x[0]}{subset_y[0]}:{subset_x[1]}{subset_y[1]}'

      # Authenticate the credential and create Google Sheet API.
      credential = Credentials.from_service_account_file(
         SERVICE_ACCOUNT_FILE,
         scopes = [ 'https://www.googleapis.com/auth/spreadsheets' ]
      )
      sheet = build('sheets', 'v4', credentials=credential).spreadsheets()

      # Update the Google Sheet.
      sheet.values().update(
         spreadsheetId    = metadata['spreadsheet_id'],
         range            = range_str,
         valueInputOption = 'RAW',
         body             = { 'values': df.to_numpy().tolist() }
      ).execute()

   except Exception as e:
      print_fail(f'Failed to save to Google Spreadsheet: {e}')
      return metadata

   print_success(f'Saved to Google Spreadsheet with range {range_str}.')
   return new_metadata


def database(metadata, df: pd.DataFrame):
   print_head('Saving Data to Database')

   new_metadata = deepcopy(metadata)
   new_metadata['repo']['database'] += df.shape[0]

   # Save the data to database with the correct value format.
   try:
      df = df.copy()
      df.index += metadata['repo']['database'] + 1
      df['price']     = df['price'].astype('float32')
      df['timestamp'] = pd.to_datetime(df['timestamp'])

      engine = create_engine(metadata['database_engine_url'])
      with engine.connect() as con:
         df.to_sql('etl-project', con)

   except Exception as e:
      print_fail(f'Failed to save to Database: {e}')
      return metadata

   print_success(f'Saved to Database from id {df.index.min()} to {df.index.max()}.')
   return new_metadata

def main(metadata, df: pd.DataFrame):
   try:
      metadata = csv(metadata, df)
      metadata = spreadsheet(metadata, df)
      metadata = database(metadata, df)
      return metadata

   except KeyboardInterrupt:
      raise KeyboardInterrupt('Operation stopped on `load.py`.')