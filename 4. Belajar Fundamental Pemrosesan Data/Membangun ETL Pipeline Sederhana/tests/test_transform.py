from unittest import TestCase, mock
from tests.helper import get_metadata, get_testset
import scripts.transform as transform

import pandas as pd
from copy import deepcopy
from decimal import Decimal, InvalidOperation

metadata = get_metadata()

testset = {
   'extract_result'    : get_testset('extract_result.csv'),
   'transform-extract' : get_testset('transform-extract.csv'),
   'transform_result'  : get_testset('transform_result.csv'),
}
testset_extract_result_list = testset['extract_result'].to_numpy().tolist()

# ========================================================================

def get_reformat_result():
   df = testset['transform-extract'].copy()
   for column, (format, dtype) in metadata['columns_format'].items():
      df[column] = df[column].astype(dtype)
   return df

def get_change_currency_result():
   df = testset['transform_result'].copy()
   df['price'] = df['price'].apply(Decimal)
   return df

result = {
   'dataframe'       : testset['extract_result'].copy(),
   'extract'         : testset['transform-extract'].copy(),
   'reformat'        : get_reformat_result(),
   'change_currency' : get_change_currency_result()
}

# ========================================================================

class TestTransform(TestCase):

   def setUp(self):
      self.metadata = deepcopy(metadata)

   # ======================================================

   def test_dataframe_success(self):
      dataframe_test = transform.dataframe(metadata, testset_extract_result_list)
      pd.testing.assert_frame_equal(dataframe_test, result['dataframe'])

   @mock.patch('pandas.DataFrame')
   def test_dataframe_fail(self, m_pandas_dataframe):
      m_pandas_dataframe.side_effect = ValueError('Column lenght mismatch.')

      with self.assertRaises(ValueError) as context:
         transform.dataframe(self.metadata, testset_extract_result_list)

      msg = 'Failed to convert products into dataframe: Column lenght mismatch.'
      self.assertEqual(str(context.exception), msg)
   
   # ======================================================

   def test_extract_success(self):
      extract_test = transform.extract(metadata, testset['extract_result'])
      pd.testing.assert_frame_equal(extract_test, result['extract'])

   def test_extract_fail(self):
      self.metadata['columns_format']['size'][0] = ''

      with self.assertRaises(ValueError) as context:
         transform.extract(self.metadata, testset['extract_result'])

      msg = 'Failed to extract column `size`: pattern contains no capture groups'
      self.assertEqual(str(context.exception), msg)
   
   # ======================================================

   def test_reformat_success(self):
      reformat_test = transform.reformat(metadata, result['extract'])
      pd.testing.assert_frame_equal(reformat_test, result['reformat'])

   def test_reformat_fail(self):
      self.metadata['columns_format']['size'][1] = 'int32'

      with self.assertRaises(ValueError) as context:
         transform.reformat(self.metadata, result['extract'])

      msg = "Failed to reformat column `size`: invalid literal for int() with base 10: 'M'"
      self.assertEqual(str(context.exception), msg)
   
   # ======================================================

   def test_change_currency_success(self):
      change_currency_test = transform.change_currency(metadata, result['reformat'])

      pd.testing.assert_series_equal(
         change_currency_test['price'],
         result['change_currency']['price']
      )

   def test_change_currency_fail_TypeError(self):
      self.metadata['exchange'] = 'abc'

      with self.assertRaises(InvalidOperation) as context:
         transform.change_currency(self.metadata, result['reformat'])

      msg = '`price` column or `metadata.exchange` has incorrect data type.'
      self.assertEqual(str(context.exception), msg)

   # ======================================================

   @mock.patch('scripts.transform.change_currency')
   @mock.patch('scripts.transform.reformat')
   @mock.patch('scripts.transform.extract')
   @mock.patch('scripts.transform.dataframe')
   def test_main_success(self, m_dataframe, m_extract, m_reformat, m_change_currency):
      transform.main(metadata, testset['extract_result'])

      m_dataframe.assert_called_once()
      m_extract.assert_called_once()
      m_reformat.assert_called_once()
      m_change_currency.assert_called_once()

   @mock.patch('scripts.transform.dataframe')
   def test_main_fail(self, m_dataframe):
      m_dataframe.side_effect = KeyboardInterrupt()

      with self.assertRaises(KeyboardInterrupt) as context:
         transform.main(metadata, testset['extract_result'])

      msg = 'Operation stopped on `transform.py`.'
      self.assertEqual(str(context.exception), msg)