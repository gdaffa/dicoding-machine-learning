import sys
import os

# Append root folder to access transformer folder.
sys.path.append(os.path.abspath('../'))

import time
import psutil
import requests
import joblib

import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)
MODEL_URL = 'http://localhost:5001/'

INPUT_SIZE_BUCKETS = [
   50_000, 100_000, 250_000, 500_000, 1_000_000, 1_500_000, 2_000_000, 3_000_000, float('inf')
]

# System metrics.
M_CPU_USAGE = Gauge('system_cpu_usage', 'Persentase penggunaan CPU.')
M_RAM_USAGE = Gauge('system_ram_usage', 'Persentase penggunaan RAM.')

# Request metrics.
M_REQUEST_COUNT      = Counter('http_requests_total', 'Total permintaan HTTP.')
M_REQUEST_LATENCY    = Histogram('http_request_duration_seconds', 'Latensi permintaan HTTP.')
M_REQUEST_THROUGHPUT = Counter('http_requests_throughput', 'Total permintaan perdetik.')
M_REQUEST_SIZE       = Histogram('input_payload_size_bytes', 'Besar input yang dikirimkan.', buckets=INPUT_SIZE_BUCKETS)
M_REQUEST_INFLIGHT   = Gauge('http_inprogress_requests', 'Jumlah permintaan yang sedang diproses.')

# Model Metrics.
M_MODEL_SUCCESS  = Counter('inference_success_total', 'Total inferensi yang sukses.')
M_MODEL_ERROR    = Counter('inference_error_total', 'Total inferensi yang error.')
M_MODEL_DURATION = Histogram('model_duration_seconds', 'Waktu eksekusi model tanpa overhead HTTP.')

preprocessor = {
   'x': joblib.load('joblibs/x_preprocessor.joblib'),
   'y': joblib.load('joblibs/y_preprocessor.joblib')
}

@app.route('/metrics', methods=['GET'])
def res_metrics():
   '''
   Endpoint to get the latest metrics.
   '''
   M_CPU_USAGE.set(psutil.cpu_percent(interval=1))
   M_RAM_USAGE.set(psutil.virtual_memory().percent)

   return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route('/predict', methods=['POST'])
@M_REQUEST_INFLIGHT.track_inprogress()
def res_predict():
   '''
   Endpoint to forward the prediction and log some metrics.
   '''
   time.sleep(5) # To handle unwanted spam.
   start_time = time.time()

   M_REQUEST_COUNT.inc()
   M_REQUEST_THROUGHPUT.inc()

   try:
      M_REQUEST_SIZE.observe(request.content_length)

      # Preprocess the data before request the prediction.
      df = pd.DataFrame(request.get_json())
      X  = preprocessor['x'].transform(df).tolist()

      cols_preprocessor = preprocessor['x'].get_feature_names_out()
      cols_real         = [col.split('__')[1] for col in cols_preprocessor]

      # Request data structure.
      req_data = {
         'dataframe_split': {
            'data'    : X,
            'columns' : cols_real
         }
      }

      response = requests.post(f'{MODEL_URL}/invocations', json=req_data)
      response.raise_for_status()

      # Get and inverse the predictions.
      pred_raw  = response.json()['predictions']
      pred_2d   = np.reshape(pred_raw, [-1, 1])
      pred_true = preprocessor['y'].inverse_transform(pred_2d)

      M_REQUEST_LATENCY.observe(time.time() - start_time)
      M_MODEL_DURATION.observe(response.elapsed.total_seconds())
      M_MODEL_SUCCESS.inc()

      return jsonify(pred_true.reshape(-1).tolist())

   except Exception as e:
      M_MODEL_ERROR.inc()
      return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
   app.run(host='localhost', port=8000)