"""
Evaluation of a trained model includes:
1. Variance-bias tradeoff. Showing the training accuracy/loss and validation accuracy/loss with respect to time
2. Different accuracy metrics for test dataset (example: confusion matrix)
3. Other use-case dependent intermediate outputs such as weights and feature outputs.
"""

import tensorflow as tf
from tensorboard import default
from tensorboard import program
import os
from os import listdir
from os.path import isfile, join
import sys
import importlib
import numpy as np
import cv2
import math
import matplotlib
import matplotlib.pyplot as plt

class TensorBoard:
    def __init__(self, dir_path):
        self.dir_path = dir_path

    def run(self):
        tb = program.TensorBoard(default.get_plugins(), default.get_assets_zip_provider())
        tb.configure(argv=[None, '--logdir', self.dir_path])
        url = tb.launch()
        print('TensorBoard at %s \n' % url)

def tensorboard_evaluation(args, project_path):
    summary_dir = project_path + "/debug/summary_" + str(args.model) + \
                "_" + str(args.param) + "_" + args.dataset
    tb_obj = TensorBoard(summary_dir)
    tb_obj.run()
    programPause = raw_input("Press the <ENTER> key to move on.")

def get_hyper_parameters(version, project_path):
    import hyperparameter.hyperparameter as hp
    hp_obj = hp.HyperParameters(version, project_path)
    param_dict = hp_obj.get_params()
    return param_dict

def get_data_provider(dataset, project_path, param_dict):
    data_provider_module_path = "dataset." + dataset + ".data_provider"
    data_provider_module = importlib.import_module(data_provider_module_path)
    dp_obj = data_provider_module.get_obj(project_path)
    with tf.name_scope('input'):
        img_batch = tf.placeholder(tf.float32, [None, 28, 28, 1])
    with tf.name_scope('output'):
        label_batch = tf.placeholder(tf.int64, [None, 10])
    return img_batch, label_batch, dp_obj

def get_model(version, inputs, param_dict):
    model_module_path = "architecture.version" + str(version) + ".model"
    model_module = importlib.import_module(model_module_path)
    model = model_module.create_model(inputs, param_dict)
    return model

def profile_model(args, project_path):
    with tf.name_scope('input'):
        img_batch = tf.placeholder(tf.float32, [1, 28, 28, 1])
    param_dict = get_hyper_parameters(args.param, project_path)
    model = get_model(args.model, img_batch, param_dict)
    graph = tf.get_default_graph()
    import debug.profiler as p
    profile_obj = p.profiler(graph)
    profile_obj.profile_param()
    profile_obj.profile_flops()
    profile_obj.profile_nodes()
    tf.reset_default_graph()

class evaluation_on_input:
    def __init__(self, args, project_path):
        tf.reset_default_graph()
        self.project_path = project_path
        self.param_dict = get_hyper_parameters(args.param, self.project_path)
        self.img_batch, self.label_batch, self.dp = get_data_provider(args.dataset, self.project_path, self.param_dict)
        self.model = get_model(args.model, self.img_batch, self.param_dict)
        self.args = args
        logs_path = project_path + "/checkpoint/checkpoint_" + str(args.model) + \
                    "_" + str(args.param) + "_" + args.dataset
        chk_name = os.path.join(logs_path, 'model.ckpt')
        self.saver = tf.train.Saver()
        self.sess = tf.Session()
        if tf.train.checkpoint_exists(chk_name):
            self.saver.restore(self.sess, chk_name)
        else:
            print("Session cannot be restored")
            sys.exit()

    def evaluate(self, tf_op, feed_dict):
        op_out = self.sess.run(tf_op, feed_dict)
        return op_out

    def get_placeholders(self):
        return self.img_batch, self.label_batch

    def get_model(self):
        return self.model

    def get_data_provider(self):
        return self.dp

def test_accuracy_confusion(e):
    img_placeholder, label_placeholder = e.get_placeholders()
    model = e.get_model()
    dp = e.get_data_provider()
    output_probability = model['feature_out']
    confusion_matrix_op = tf.confusion_matrix(tf.argmax(label_placeholder, axis=1), tf.argmax(output_probability, axis=1))
    img_validation_data, label_validation_data = dp.validation()
    feed_dict = {img_placeholder: img_validation_data, label_placeholder: label_validation_data}
    confusion_matrix = e.evaluate(confusion_matrix_op, feed_dict)
    print(confusion_matrix)

def generate_layer_activation(e, input):
    img_placeholder, label_placeholder = e.get_placeholders()
    model = e.get_model()
    feed_dict = {img_placeholder: input}
    op = model['layer_1']
    return op, feed_dict

def plot_activation(feature, path):
    nr_feature = feature.shape[3]
    plt.figure(1, figsize=(20,20))
    n_columns = 6
    n_rows = math.ceil(nr_feature / n_columns) + 1
    for i in range(nr_feature):
        plt.subplot(n_rows, n_columns, i+1)
        plt.title('Filter ' + str(i))
        plt.imshow(feature[0,:,:,i], interpolation="nearest", cmap="gray")
    plt.savefig(path + '/vis_plot.jpg')

def evaluation_on_sample(e, args, project_path, all=True):
    sample_path = project_path + "/dataset/" + args.dataset + "/sample/"
    write_path = project_path + "/visualization/vis" + str(args.model) + "_" + str(args.param) + "_" + args.dataset
    if not os.path.isdir(write_path):
        os.mkdir(write_path)
    sample_files = [f for f in listdir(sample_path) if isfile(join(sample_path, f))]
    for file in sample_files:
        input = cv2.imread(sample_path + file, 0)
        input = input.reshape((1,28,28,1))/255.0
        op, feed_dict = generate_layer_activation(e, input)
        out = e.evaluate(op, feed_dict)
        plot_activation(out, write_path)
        programPause = raw_input("Press the <ENTER> key to move on.")

def execute(args):
    project_path = os.getcwd()
    tensorboard_evaluation(args, project_path)
    profile_model(args, project_path)
    eval_obj = evaluation_on_input(args, project_path)
    test_accuracy_confusion(eval_obj)
    evaluation_on_sample(eval_obj,args, project_path)
