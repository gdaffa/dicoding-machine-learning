import os
import shutil
import random

# --------------------------------------------------------------------------------

folders     = os.listdir('../datasets')
# rasio untuk membagi dataset
split_ratio = {
   'train'      : .8,
   'validation' : .1,
   'test'       : .1
}

# --------------------------------------------------------------------------------

for folder in folders:
   print(f'\n🔵 {folder}')

   folder_path = f'../datasets/{folder}'

   if os.path.isfile(folder_path):
      print(f'❗ {folder} adalah file')
      continue

   total = 1
   files = set(os.listdir(f'../datasets/{folder}'))

   for split_key in split_ratio:

      split_path = f'../model-datasets/{split_key}/{folder}'
      os.makedirs(split_path, exist_ok=True)

      ratio    = split_ratio[split_key]
      # mengambil dataset random sesuai rasio relatif pada sisa dataset
      selected = random.sample(list(files), round(len(files) * ratio / total))
      # mendapatkan dataset yang tidak dipilih
      files    = files - set(selected)
      total   -= ratio

      for file in selected:
         shutil.copy(f'{folder_path}/{file}',  split_path)
         print(f'✅ {split_key}: {file}')