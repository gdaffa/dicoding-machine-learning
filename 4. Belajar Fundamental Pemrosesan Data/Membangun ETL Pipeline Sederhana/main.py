from scripts import *
import json

METADATA_PATH = 'metadata.json'

def main():
   with open(METADATA_PATH, 'r', encoding='utf-8') as file:
      metadata = json.load(file)

   products   = extract_main(metadata)
   df_cleaned = transform_main(metadata, products)
   metadata   = load_main(metadata, df_cleaned)

   with open(METADATA_PATH, 'w', encoding='utf-8') as file:
      metadata = json.dump(metadata, file, indent=3)

if __name__ == '__main__':
   main()