from unittest import TestCase, mock
from tests.helper import get_metadata, get_testset
import scripts.extract as extract

from copy import deepcopy
from bs4 import BeautifulSoup
from datetime import datetime
from requests.exceptions import ConnectionError

def product_to_card_raw(product):
   product = ''.join([f'<p>{data}</p>' for data in product])
   return f'<div class="product-details">{product}</div>'

metadata = get_metadata()
products = get_testset('example.csv').to_numpy().tolist()

now       = str(datetime.now())
cards_raw = [product_to_card_raw(product) for product in products]

html  = ''.join(cards_raw)
html += '<ul><li class="page-item current">1 of 1</li></ul>'
html  = BeautifulSoup(f'<html><body>{html}</body></html>', 'html.parser')

# ========================================================================

result = {
   'get'   : [[1, card, now] for card in html.select('.product-details')],
   'parse' : [[*product, now] for product in products]
}

# ========================================================================

class TestExtract(TestCase):

   @mock.patch('scripts.extract.datetime')
   @mock.patch('requests.get')
   def test_get_success(self, m_requests_get, m_datetime):
      mo_request_get = mock.Mock()
      mo_request_get.status_code = 200
      mo_request_get.content     = str(html).encode()

      m_requests_get.return_value = mo_request_get
      m_datetime.now.return_value = now

      get_test = extract.get(metadata)

      self.assertEqual(get_test, result['get'])

   @mock.patch('scripts.extract.print_fail')
   @mock.patch('requests.get')
   def test_get_fail(self, m_requests_get, m_print_fail):
      m_requests_get.side_effect = ConnectionError('Cannot connect.')

      with self.assertRaises(ValueError) as context:
         extract.get(metadata)

      msg_error = 'No data collected. Terminate the program.'
      msg_fail  = f'Failed to fetch {metadata["domain"]}/: Cannot connect.'
      m_print_fail.assert_called_with(msg_fail)
      self.assertEqual(str(context.exception), msg_error)

   # ======================================================

   def test_parse_success(self):
      parse_test = extract.parse(metadata, result['get'])
      self.assertEqual(parse_test, result['parse'])

   @mock.patch('scripts.extract.print_fail')
   def test_parse_fail(self, m_print_fail):
      fake_html   = BeautifulSoup('<p>Fake</p>', 'html.parser')
      fake_result = deepcopy(result['get'])
      fake_result[4][1].append(fake_html)

      extract.parse(metadata, fake_result)

      msg = f'Product 5 (page 1) has less/more data than expected, skipping this product.'
      m_print_fail.assert_called_once_with(msg)

   # ======================================================

   @mock.patch('scripts.extract.parse')
   @mock.patch('scripts.extract.get')
   def test_main_success(self, m_get, m_parse):
      extract.main(metadata)

      m_get.assert_called_once()
      m_parse.assert_called_once()

   @mock.patch('scripts.extract.get')
   def test_main_fail(self, m_get):
      m_get.side_effect = KeyboardInterrupt()

      with self.assertRaises(KeyboardInterrupt) as context:
         extract.main(metadata)

      msg = 'Operation stopped on `extract.py`.'
      self.assertEqual(str(context.exception), msg)