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
import sys
import importlib
import numpy as np

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

def test_accuracy(args, project_path):
    # For now, we use test set and print confusion matrix on mnist example
    param_dict = get_hyper_parameters(args.param, project_path)
    img_batch, label_batch, dp = get_data_provider(args.dataset, project_path, param_dict)
    model = get_model(args.model, img_batch, param_dict)
    logs_path = project_path + "/checkpoint/checkpoint_" + str(args.model) + \
                "_" + str(args.param) + "_" + args.dataset
    chk_name = os.path.join(logs_path, 'model.ckpt')
    output_probability = model['feature_out']
    confusion_matrix_op = tf.confusion_matrix(tf.argmax(label_batch, axis=1), tf.argmax(output_probability, axis=1))
    saver = tf.train.Saver()
    with tf.Session() as sess:
        if tf.train.checkpoint_exists(chk_name):
            saver.restore(sess, chk_name)
        else:
            print("Train before test")
            sys.exit()
        img_validation_data, label_validation_data = dp.validation()
        feed_dict = {img_batch: img_validation_data, label_batch: label_validation_data}
        confusion_matrix = sess.run(confusion_matrix_op, feed_dict = feed_dict)
    print(confusion_matrix)

def execute(args):
    project_path = os.getcwd()
    tensorboard_evaluation(args, project_path)
    profile_model(args, project_path)
    test_accuracy(args, project_path)
