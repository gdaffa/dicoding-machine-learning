from unittest import TestCase, mock
from tests.helper import get_metadata, get_testset
import scripts.load as load

from copy import deepcopy

metadata = get_metadata()
metadata['repo'] = {
   'csv'         : 0,
   'spreadsheet' : 0,
   'database'    : 0
}

testset = {
   'transform_result' : get_testset('transform_result.csv')
}

# ========================================================================

def get_result(repo, count):
   new_metadata = deepcopy(metadata)
   new_metadata['repo'][repo] = count
   return new_metadata

result = {
   'csv'         : get_result('csv', 1),
   'spreadsheet' : get_result('spreadsheet', testset['transform_result'].shape[0]),
   'database'    : get_result('database', testset['transform_result'].shape[0]),
}

# ========================================================================

class TestLoad(TestCase):

   @mock.patch('scripts.load.print_success')
   @mock.patch('pandas.DataFrame.to_csv')
   def test_csv_success(self, m_df_to_csv, m_print_success):
      csv_test = load.csv(metadata, testset['transform_result'])

      msg = 'Saved to CSV as `dataset1.csv`.'
      self.assertEqual(csv_test, result['csv'])
      m_df_to_csv.assert_called_once()
      m_print_success.assert_called_once_with(msg)

   @mock.patch('scripts.load.print_fail')
   @mock.patch('pandas.DataFrame.to_csv')
   def test_csv_fail(self, m_df_to_csv, m_print_fail):
      m_df_to_csv.side_effect = OSError('Folder not found.')
      csv_test = load.csv(metadata, testset['transform_result'])

      msg = 'Failed to save to CSV: Folder not found.'
      self.assertEqual(csv_test, metadata)
      m_print_fail.assert_called_once_with(msg)

   # ======================================================

   @mock.patch('scripts.load.print_success')
   @mock.patch('scripts.load.build')
   @mock.patch('scripts.load.Credentials.from_service_account_file')
   def test_spreadsheet_success(self, m_credential, m_build, m_print_success):
      mo_service = mock.Mock()
      m_build.return_value.spreadsheets.return_value = mo_service

      spreadsheet_test = load.spreadsheet(metadata, testset['transform_result'])

      msg = 'Saved to Google Spreadsheet with range A2:H19.'
      self.assertEqual(spreadsheet_test, result['spreadsheet'])
      mo_service.values().update().execute.assert_called_once()
      m_print_success.assert_called_once_with(msg)

   @mock.patch('scripts.load.print_fail')
   @mock.patch('scripts.load.Credentials.from_service_account_file')
   def test_spreadsheet_fail(self, m_credential, m_print_fail):
      m_credential.side_effect = ValueError('Unexpected format.')
      spreadsheet_test = load.spreadsheet(metadata, testset['transform_result'])

      msg = 'Failed to save to Google Spreadsheet: Unexpected format.'
      self.assertEqual(spreadsheet_test, metadata)
      m_print_fail.assert_called_once_with(msg)
   
   # ======================================================

   @mock.patch('scripts.load.print_success')
   @mock.patch('scripts.load.create_engine')
   def test_database_success(self, m_engine_create, m_print_success):
      conn = m_engine_create.return_value.connect.return_value.__enter__.return_value
      database_test = load.database(metadata, testset['transform_result'])

      msg = 'Saved to Database from id 1 to 17.'
      self.assertEqual(database_test, result['database'])
      self.assertTrue(conn.execute.called or conn.method_calls)
      m_print_success.assert_called_once_with(msg)

   @mock.patch('scripts.load.print_fail')
   @mock.patch('scripts.load.create_engine')
   def test_database_fail(self, m_create_engine, m_print_fail):
      m_create_engine.side_effect = Exception("DB fail.")
      database_test = load.database(metadata, testset['transform_result'])

      msg = 'Failed to save to Database: DB fail.'
      self.assertEqual(database_test, metadata)
      m_print_fail.assert_called_once_with(msg)

   # ======================================================

   @mock.patch('scripts.load.database')
   @mock.patch('scripts.load.spreadsheet')
   @mock.patch('scripts.load.csv')
   def test_main_success(self, m_csv, m_spreadsheet, m_database):
      load.main(metadata, testset['transform_result'])

      m_csv.assert_called_once()
      m_spreadsheet.assert_called_once()
      m_database.assert_called_once()

   @mock.patch('scripts.load.csv')
   def test_main_fail(self, m_csv):
      m_csv.side_effect = KeyboardInterrupt()

      with self.assertRaises(KeyboardInterrupt) as context:
         load.main(metadata, testset['transform_result'])

      msg = 'Operation stopped on `load.py`.'
      self.assertEqual(str(context.exception), msg)