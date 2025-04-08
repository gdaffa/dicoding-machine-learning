import os
import hashlib
from PIL import Image

# --------------------------------------------------------------------------------

folders = os.listdir('../datasets')

# --------------------------------------------------------------------------------

for folder in folders:
   print(f'\n🔵 {folder}')

   hash_dict   = {}
   folder_path = f'../datasets/{folder}'

   if os.path.isfile(folder_path):
      print(f'❗ {folder} adalah file')
      continue

   for image_path in os.listdir(folder_path):

      try:
         # load gambar dan mengubahnya ke rgb
         with Image.open(f'{folder_path}/{image_path}') as image:
            image = image.convert('RGB')

         # menyimpan hasil hashing
         hash = hashlib.md5(image.tobytes()).hexdigest()

         if hash not in hash_dict:
            hash_dict[hash] = image_path
            continue

         print(f'🔴 {image_path} == {hash_dict[hash]}')
         print(f'❌ {image_path}')
         os.remove(f'{folder_path}/{image_path}')

      except Exception as e:
         print(f'❗ {image_path}: {e}')