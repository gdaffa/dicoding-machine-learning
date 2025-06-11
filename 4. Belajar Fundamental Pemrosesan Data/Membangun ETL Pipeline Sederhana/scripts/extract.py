from .helper import print_head, print_success, print_fail
import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime

FETCH_DELAY  = 0.5

def get(metadata):
   print_head('Scraping the Products')

   products   = []
   page       = 0
   total_page = 1

   # Scrape all pages.
   while (page < total_page):
      page += 1
      print(f'🔄 Working on page {page}...')

      url = f'{metadata['domain']}/{f"page{page}" if page != 1 else ""}'

      try:
         response = requests.get(url)
         response.raise_for_status()

      # Skip the page if error occurs when fetching `url`.
      except requests.exceptions.RequestException as e:
         print_fail(f'Failed to fetch {url}: {e}')
         continue

      now    = str(datetime.now())
      parser = BeautifulSoup(response.content.decode(), 'html.parser')
      cards  = parser.select('.product-details')

      # Add all item in a single page, each row is `[page, card, now]`.
      products.extend([[page, card, now] for card in cards])

      # Get total page in pagination section.
      if total_page == 1:
         pager = parser.select_one('li.page-item.current').get_text()
         total_page = int(pager.split(' ')[-1])

      print_success(f'{url} fetched successfully.')

      time.sleep(FETCH_DELAY)
   
   if len(products) == 0:
      raise ValueError(f'No data collected. Terminate the program.')

   return products

def parse(metadata, products):
   print_head('Parsing the Products')

   parsed_products = []
   products_lenght = len(products)
   parsed_lenght   = 0

   for index, (page, card, batch_time) in enumerate(products):

      # Get all children inner text.
      try:
         children     = card.find_all(recursive=False)
         product_data = [child.get_text() for child in children]

         # Excluding `timestamp` column.
         if (len(children) != (len(metadata['columns']) - 1)):
            raise ValueError

      # If total children is not the same lenght as expected.
      except ValueError:
         print_fail(f'Product {index + 1} (page {page}) has less/more data than expected, skipping this product.')
         continue

      parsed_products.append([ *product_data, batch_time ])
      parsed_lenght += 1

      # Feedback after every 10 parsed products.
      if parsed_lenght % 10 == 0:
         print_success(f'{parsed_lenght} / {products_lenght} products parsed.')

   return parsed_products

def main(metadata):
   try:
      products = get(metadata)
      products = parse(metadata, products)
      return products

   except KeyboardInterrupt:
      raise KeyboardInterrupt('Operation stopped on `extract.py`.')