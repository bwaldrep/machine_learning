# ada.py
# Bill Waldrep, November 2012
#
# Implementation of AdaBoost with decision stubs
# as weak learners.

import numpy as np
import math as m
import matplotlib 
import matplotlib.pyplot as pl
import matplotlib.cm as cm

def load_data(suffix='train.csv'):
  data_file = 'data/ada_x_' + suffix
  label_file = 'data/ada_y_' + suffix
  delim = ','
  data = np.loadtxt(data_file, delimiter=delim)
  labels = np.loadtxt(label_file, delimiter=delim)
  return data, labels

def show_image(img):
  """Plot the input as a greyscale
  image for sanity checking"""
  temp = np.reshape(x[3], (28,28))
  pl.imshow(temp, cmap = cm.Greys_r)
  pl.show()

class DecisionStump:
  def __init__(self, dimension=-1, thresh=-1, inequal=-1):
    self.dim = dimension
    self.t = thresh
    self.iq = inequal

  def classify(self, data):
    # start by labeling everything 1
    results = np.ones(len(data),'int')
    if self.iq == "gte":
      # flip the labels of everything greater than or equal to the threshold
      results[data[:,self.dim] >= self.t] = -1
    else:
      # flip the labels of everything less than or equal to the threshold
      results[data[:,self.dim] <= self.t] = -1
    return results

  def train(self, data, label, D):
      rows, cols = np.shape(data)
      min_error = np.inf
      for dim in xrange(cols):
        # get all possible thresholds we could split on
        vals = np.unique(data[:,dim])
        for t in vals:
          for flip in ["gte", "lte"]:
            candidate = DecisionStump(dim,t,flip)
            guess = candidate.classify(data)
            # initialize to zero error
            error = np.zeros(rows,'int')
            error[guess != label] = 1
            weighted = np.dot(error,D)
            #print "dim %d, t %d, iq %s, w %f, min %f" % (dim, t, flip, weighted, min_error)
            if weighted < min_error:
              min_error = weighted
              self.dim = dim
              self.t = t
              self.iq = flip
      return self.classify(data), min_error

  def debug(self):
    print self.dim, self.t, self.iq

class AdaBoost:
  def train(self, T=500, suffix='train.csv'):
    data, labels = load_data(suffix)
    tdat, tlab = load_data('test.csv')
    rows, cols = np.shape(data)
    weights = np.ones(rows, 'float')/rows
    self.alphas = []
    self.classifiers = []
    trainerr = []
    testerr = []
    for i in xrange(T):
      h = DecisionStump()
      guess, herr = h.train(data,labels,weights)
      # print i, herr
      # add new classifier and coefficient
      self.alphas.append(m.log((1-herr)/max(herr,1e-16))/2)
      self.classifiers.append(h)

      # normalization factor
      z = 2 * m.sqrt(max(herr,1e-16) * (1 - herr))

      # re-weight the features
      temp = np.multiply(-self.alphas[i] * labels, guess)
      weights = np.multiply(weights, np.exp(temp))/z

      # compute and save training and testing error
      trainerr.append(self.check(data, labels))
      testerr.append(self.check(tdat, tlab))

      # We need to plot this stuff
      print i, self.alphas[i], trainerr[i], testerr[i]
    return trainerr, testerr

  def evaluate(self, data):
    n = len(data)
    # start with a neutral prediction
    result = np.zeros(n, 'float')

    # add the weighted vote of each weak classifier
    for i in range(len(self.alphas)):
      h = self.classifiers[i]
      result += h.classify(data) * self.alphas[i]
    # take the sign to get the final classification
    return np.sign(result)

  def check(self, data, labels):
    guess = self.evaluate(data)
    error = np.zeros(len(guess), 'int')
    error[guess != labels] = 1
    return error.sum()/float(len(error))

# Debugging
a = AdaBoost()
train, test = a.train()
