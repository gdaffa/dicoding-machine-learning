'''
Unfortunately this file has to use MLflow 2.x
to compatible with dagshub MLflow.
'''
import sys
import os

# Append root folder to access transformer folder.
sys.path.append(os.path.abspath('../'))

import mlflow
import dagshub
import joblib
import config as conf

import pandas as pd
from scipy.stats import randint
from matplotlib import pyplot as plt

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, root_mean_squared_error, r2_score

def log_params(params: dict, inital_text=''):
   '''
   Rename dictionary key with specified starting text.
   '''
   inital_text = inital_text and f'{inital_text}_'
   new_params  = {}
   for key, val in params.items():
      new_params[f'{inital_text}{key}'] = val

   mlflow.log_params(new_params)

def log_metrics(name: str, y_group: list, model_uri: str):
   '''
   Log some of regression model peformance (metric)
   that defined in `sklearn.metrics`.
   '''
   metrics = {
      f'{name}_mae'  : mean_absolute_error(*y_group),
      f'{name}_mse'  : mean_squared_error(*y_group),
      f'{name}_r2'   : r2_score(*y_group),
      f'{name}_rmse' : root_mean_squared_error(*y_group)
   }

   mlflow.log_metrics(metrics)

def log_figure(num: int, title: str, xlabel='', ylabel='', legend=True):
   '''
   Define some information to the figure and log the figure
   for further inspection.
   '''
   fig = plt.figure(num)

   plt.title(title)
   plt.xlabel(xlabel)
   plt.ylabel(ylabel)
   plt.grid()

   if legend:
      plt.legend()

   filename = title.lower().replace(' ', '_') + '.png'
   mlflow.log_figure(fig, filename)

def log_figures(y_true, y_pred):
   '''
   Log 2 figure of regression model peformance
   with calling the `log_figure` function.
   '''
   title = 'Actual VS Prediction'
   plt.figure(1, figsize=[10, 10])
   plt.scatter(y_true, y_pred, alpha=0.5)
   plt.plot(y_true, y_true, label='Actual', color='orange')
   log_figure(1, title, 'Actual', 'Prediction')

   title = 'Residual Score'
   plt.figure(2, figsize=[12, 8])
   plt.scatter(y_true, y_true-y_pred, alpha=0.5)
   plt.axhline(color='k', linestyle='--')
   log_figure(2, title, 'Price', 'Residual', False)

def main():
   '''
   The main function to start tracking experiment.
   '''
   ITERATION = 30

   dagshub.init('submission-mlflow-dagshub', 'gibrandaffa', mlflow=True)

   config = conf.get_config()
   y_preprocessor = joblib.load(f'joblibs/{config["y_preprocessor"]}')

   with mlflow.start_run():
      df = pd.read_csv(f'dataset/{config["dataset"]}')
      df_feat = df.drop(columns=config['target_col'])
      df_targ = df[[config['target_col']]]

      X_train, X_test, y_train, y_test = train_test_split(
         df_feat, df_targ, train_size=0.8, random_state=0
      )

      # Parameter distribution for hyper parameter tuning.
      param_dist = {
         'n_estimators'      : randint(75, 125),
         'max_depth'         : randint(5, 50),
         'min_samples_split' : randint(2, 11),
         'min_samples_leaf'  : randint(1, 11)
      }

      model         = RandomForestRegressor(random_state=0)
      random_search = RandomizedSearchCV(
         estimator=model, param_distributions=param_dist,
         n_iter=ITERATION, scoring='r2', cv=5, verbose=2,
         random_state=0, n_jobs=-1
      )
      random_search.fit(X_train, y_train.to_numpy().reshape(-1))

      best_estimator = random_search.best_estimator_

      # Log the model and the model tuning.
      mlflow.sklearn.log_model(
         best_estimator,
         artifact_path = 'RandomForest',
         input_example = df_feat.sample(5)
      )
      mlflow.sklearn.log_model(
         random_search,
         artifact_path = 'RandomSearch',
         input_example = df_feat.sample(5)
      )

      # Get prediction and reshape for inverse transform.
      y_train_pred = best_estimator.predict(X_train).reshape(-1, 1)
      y_test_pred  = best_estimator.predict(X_test).reshape(-1, 1)

      # Group inverse transform result by set (train or test).
      y_train_group = [
         y_preprocessor.inverse_transform(y_train),
         y_preprocessor.inverse_transform(y_train_pred)
      ]
      y_test_group = [
         y_preprocessor.inverse_transform(y_test),
         y_preprocessor.inverse_transform(y_test_pred)
      ]

      imp_feat         = best_estimator.feature_importances_.round(8)
      imp_feat_indices = imp_feat.argsort()[::-1]
      imp_feat_report  = {}

      # Notes all features ordered by their importance (descending).
      for i, index in enumerate(imp_feat_indices):
         imp_feat_report[f'important_feature_{i + 1}'] = [
            df_feat.columns[index],
            float(imp_feat[index])
         ]

      # Log parameters, metrics, and graph figure.
      log_params(imp_feat_report)
      log_params(best_estimator.get_params(), 'model')
      log_params(random_search.best_params_, 'best')
      log_params(random_search.get_params(), 'random_search')
      log_metrics('train', y_train_group)
      log_metrics('test', y_test_group)
      log_figures(*y_test_group)

if __name__ == '__main__':
   main()