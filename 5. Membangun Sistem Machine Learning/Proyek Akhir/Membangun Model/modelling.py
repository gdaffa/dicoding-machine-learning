import sys
import os

# Append root folder to access transformer folder.
sys.path.append(os.path.abspath('../'))

import mlflow
import pandas as pd
import joblib
import config as conf

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

config = conf.get_config()

y_preprocessor = joblib.load(f'joblibs/{config['y_preprocessor']}')

mlflow.set_tracking_uri('http://localhost:5000')

with mlflow.start_run() as r:
   mlflow.autolog()

   df = pd.read_csv(f'dataset/{config['dataset']}')
   df_feat = df.drop(columns=config['target_col'])
   df_targ = df[[config['target_col']]]

   X_train, X_test, y_train, y_test = train_test_split(
      df_feat, df_targ, train_size=0.8, random_state=0
   )

   rf_model = RandomForestRegressor()
   rf_model.fit(X_train, y_train.to_numpy().reshape(-1))

   y_pred = rf_model.predict(X_test).reshape(-1, 1)

   # Inverse the preprocessor method.
   y_pred = y_preprocessor.inverse_transform(y_pred)
   y_true = y_preprocessor.inverse_transform(y_test)

   metrics = {
      'test_mae'  : mean_absolute_error(y_true, y_pred),
      'test_rmse' : root_mean_squared_error(y_true, y_pred),
      'test_r2'   : r2_score(y_true, y_pred)
   }

   mlflow.log_param('feature_importances_', rf_model.feature_importances_)
   mlflow.log_metrics(metrics)