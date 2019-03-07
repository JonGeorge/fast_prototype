"""
Dataset script for MNIST
Used tensorflow TFRecords for datapipeline
"""

import wget
import tarfile
import six
from six.moves import cPickle as pickle
import tensorflow as tf
import numpy as np
import cv2
import sys
import os

class MNIST:
    def __init__(self, absolute_path):
        self.dataset_name = "MNIST"
        self.absolute_path = absolute_path

    def get_data(self):
        dataset_path = self.absolute_path + "/dataset/" + self.dataset_name
        if not os.path.isdir(dataset_path + "/raw"):
            os.mkdir(dataset_path + "/raw")

    def preprocess_data(self):
        dataset_path = self.absolute_path + "/dataset/" + self.dataset_name
        if not os.path.isdir(dataset_path + "/pre-processed"):
            os.mkdir(dataset_path + "/pre-processed")

    def process_image(self, img):
        img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_CUBIC)
        return img

def get_obj(absolute_path):
    obj = MNIST(absolute_path)
    return obj
