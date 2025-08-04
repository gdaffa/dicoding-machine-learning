import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class LogTransformer(BaseEstimator, TransformerMixin):
   '''
   Transformer that change all value with logarithmic function.
   This is useful for handling exponential distribution.
   '''
   def fit(self, X):
      return self

   def transform(self, X):
      return np.log(X)

   def inverse_transform(self, X):
      return np.exp(X)