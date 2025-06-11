from .helper import print_head, print_success
import pandas as pd
from decimal import Decimal, getcontext, InvalidOperation

getcontext().prec = 8

def dataframe(metadata, products):
   try:
      return pd.DataFrame(products, columns=metadata['columns'])
   except ValueError as e:
      raise ValueError(f'Failed to convert products into dataframe: {e}')

def extract(metadata, df: pd.DataFrame):
   print_head('Extracting Data')
   df = df.copy()

   # Extract all defined column in `metadata.columns_format` to desired pattern.
   try:
      for column, (format, dtype) in metadata['columns_format'].items():
         df[column] = df[column].str.extract(format)
         print_success(f'`{column}` column extracted.')

   # If regex formula is broken.
   except ValueError as e:
      raise ValueError(f'Failed to extract column `{column}`: {e}')

   df = df.dropna().drop_duplicates().reset_index(drop=True)

   return df

def reformat(metadata, df: pd.DataFrame):
   print_head('Changing Data Types')
   df = df.copy()

   # Reformat all defined column in `metadata.columns_format` to desired data type.
   try:
      for column, (format, dtype) in metadata['columns_format'].items():
         df[column] = df[column].astype(dtype)
         print_success(f'`{column}` column changed.')

   # If the column cannot be change to desired data type.
   except ValueError as e:
      raise ValueError(f'Failed to reformat column `{column}`: {e}')

   return df

def change_currency(metadata, df: pd.DataFrame):
   print_head('Changing the Currency')
   df = df.copy()

   # Changing the currency to IDR using `metadata.exchange` and `Decimal` type for precision.
   try:
      df['price'] = df['price'].apply(Decimal) * Decimal(str(metadata['exchange']))
      print_success('Currency changed to IDR.')

   # If `price` column or `metadata.exchange` cannot be changed into `Decimal` type.
   except InvalidOperation as e:
      raise InvalidOperation('`price` column or `metadata.exchange` has incorrect data type.')

   return df

def main(metadata, products):
   try:
      df = dataframe(metadata, products)
      df = extract(metadata, df)
      df = reformat(metadata, df)
      df = change_currency(metadata, df)
      return df

   except KeyboardInterrupt:
      raise KeyboardInterrupt('Operation stopped on `transform.py`.')