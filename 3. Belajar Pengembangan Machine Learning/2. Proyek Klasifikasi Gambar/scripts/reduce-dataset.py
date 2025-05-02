import os
import random

# --------------------------------------------------------------------------------

folders  = os.listdir('../datasets')
max_item = 400

# --------------------------------------------------------------------------------

for folder in folders:
   print(f'\n🔵 {folder}')

   folder_path = f'../datasets/{folder}'

   if os.path.isfile(folder_path):
      print(f'❗ {folder} adalah file')
      continue

   image_paths = os.listdir(folder_path)

   if len(image_paths) <= max_item:
      continue

   # memilih gambar secara acak
   for image_path in random.sample(image_paths, (len(image_paths) - max_item)):
      image_path = f'{folder_path}/{image_path}'
      os.remove(image_path)
      print(f'❌ {image_path}')