import argparse

def get_config():
   arg_parser = argparse.ArgumentParser()

   arg_parser.add_argument('dataset')
   arg_parser.add_argument('--target-col', default='price')
   arg_parser.add_argument('--y-preprocessor', default='y_preprocessor.joblib')

   args = arg_parser.parse_args()

   return dict(args._get_kwargs())