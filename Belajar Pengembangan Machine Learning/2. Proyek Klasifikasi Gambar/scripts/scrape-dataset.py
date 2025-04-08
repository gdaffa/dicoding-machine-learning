from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import time
import os
import requests
import base64
import json

# --------------------------------------------------------------------------------

scrape_id  = 2
class_list = ['echinacea', 'marigold', 'markisa', 'sepatu', 'teratai']

# query yang akan menjadi kunci pencarian
queries = [
   '{name} flower',
   '{name} flower photo'
]
# situs yang akan digunakan untuk mencari
sites = [
   {
      'name'       : 'google',
      'url'        : 'https://www.google.com/search?q={query}&tbm=isch&as_filetype=jpg&tbs=sur:fmc&udm=2',
      'selector'   : 'img.YQ4gaf:not(.zr758c)',
      'pagination' : False,
      'pages'      : 4,
      'amount'     : 40,
   },
   {
      'name'       : 'freepik',
      'url'        : 'https://www.freepik.com/search?'
         'format=search&'
         'query={query}&'
         'page={page}&'
         'selection=1&'
         'type=photo&'
         'ai=excluded'
         '#uuid=6e000a25-b7fa-4252-baa3-20a88ff9d9ef', #! penting jangan dihapus
      'selector'   : 'img.\\$block.\\$rounded.\\$object-cover.\\$object-center.\\$h-auto.\\$w-full',
      'pagination' : True,
      'pages'      : 2,
      'amount'     : 80,
   }
]

# --------------------------------------------------------------------------------

# ambil gambar berdasarkan situs dan query
def fetch(site, query) -> list[str]:
   images = []
   _, url, selector, pagination, pages, amount = site.values()

   # loop berdasarkan jumlah pages jika situs berbentuk paginasi
   for page in range(pages if pagination else 1):
      driver.get(url.replace('{query}', query).replace('{page}', str(page)))
      time.sleep(2)

      # scroll berdasarkan jumlah pages jika situs tidak bersifat paginasi
      for scroll in range(pages if not pagination else 1):
         driver.find_element('tag name', 'body').send_keys(Keys.END)
         time.sleep(2)

         # jika situs bersifat paginasi, akan mengambil gambar setiap 1 loop
         if pagination:
            images.extend(get_images(selector))

      # jika situs tidak bersifat paginasi, akan mengambil gambar setelah scroll selesai 
      if not pagination:
         images.extend(get_images(selector))

   return images[:amount]

# ambil gambar dengan driver
def get_images(selector):
   return [img.get_attribute('src') for img in driver.find_elements('css selector', selector)]

# --------------------------------------------------------------------------------

# inisialisasi driver
driver  = webdriver.Chrome(service=Service('../chromedriver-win64/chromedriver.exe'))

for flower in class_list:
   print(f'\n🔵 {flower}')

   new_queries = map(
      lambda query: query.replace('{name}', flower.replace('-', ' ')),
      queries
   )

   folder_path = f'../datasets/{flower}'
   os.makedirs(folder_path, exist_ok=True)

   # cari gambar dengan semua query
   for idx_query, query in enumerate(new_queries):

      # cari gambar dengan semua situs setiap query
      for site in sites:

         # mengunduh gambar yang ditemukan dari hasil fetch
         for idx, src in enumerate(fetch(site, query)):

            filename = f'{flower}_scrape-{scrape_id}_query-{idx_query + 1}_{site['name']}_{idx + 1}.jpg'

            try:
               # menyimpan gambar yang didapat dalam bentuk url ataupun base64
               binary = base64.b64decode(src.split(',')[1]) if src.startswith('data:image') else requests.get(src).content
               with open(f'{folder_path}/{filename}', 'wb') as file:
                  file.write(binary)

               print(f'✅ {filename}')

            except Exception as e:
               print(f'❗ {filename}: {e}')

driver.quit()
