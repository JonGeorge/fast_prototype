# A more systematic approach for prototyping research ideas

This repository contains an easy-to-use and easy-to-follow heirarchy of code base :octocat: that aids in conducting Machine Learning research. Internally, the code base relies on tensorflow framework, but same coding style can be incorporated with any ML library such as py-torch and caffe. Each file in this project has been written by keeping one thing in mind: **multiple experimentation with several revisions of ML models and several revisions of hyper-parameters**. Thus, this code-base is an intial step to manage the experiments in a systematic way and track multiple results with ample amount of visualization. :muscle:

## Dependency
`numpy` `ntfy` `slackclient` `ntfy[slack]` `tensorflow` or `tensorflow_gpu` `keyboard` `opencv_python` `netron` `wget` `pathlib` `statistics` `argparse` `scikit-optimize` `matplotlib` `scipy` `Pillow`

Tested on python version 2
All packages can be updated/installed with `pip install -r requirements.txt` except `ntfy[slack]`. Install `ntfy[slack]` seperately with `pip install ntfy[slack]` post requirements.txt installation.

## About the code-base
The main controller is *master.py*. There are two parts which is needed to be detailed.
* How to make use of this code-base in your own projects.
* Where should you make changes.

## How to make use of it.
Fork the whole repository or make a copy of it. In order to remain updated, :star2::star2:**star mark this repository**:star2::star2:, and you will be notified :calling: about the newer versions. Install the requirements and update the dependencies as described in requirements.txt file.

Once the repository is being copied :floppy_disk:, interact **only** with *master.py*.
"master.py" handles following:
* **Phase 1:** Get ready with benchmark dataset(s)
    * Dataset download
    * Data pre-processing
    * Data provider as required in training phase.
* **Phase 2:** Declararing the architecture(s) and training detail(s)
    * Model architecture design
    * Hyper-parameter settings
    * Setup intermediate results saving infrastructure
* **Phase 3:** Training and evaluation
    * Training
    * Testing and setting visualization infrastructure
* **Phase 4:** Record results
    * Create tabular results
    * Visualization

### Options for *master.py*
* Dataset Phase
> python master.py --phase "dataset" --dataset "CIFAR-10" --download True --preprocess True

* Training Phase
> python master.py --phase "train" --dataset "CIFAR-10" --model 1 --param 1

* Evaluation Phase
> python master.py --phase "evaluate" --dataset "CIFAR-10" --model 1 --param 1

* Visualization
> python master.py --phase "visualize" --model 1 --param 1

* Do all of the above
> python master.py --dataset "CIFAR-10" --download True --preprocess True

## Where to make changes
* dataset/*dataset_name*/dataset_script.py
```
Here define the methods to retrive, download and process the dataset.
Two folders namely raw and pre-processed shall be used for any pre-processing.
Do not change getter function name and class signature
```

* dataset/*dataset_name*/dataset_provider.py
```
Must define atleast two functions namely set_batch(batch_size) and next()
Do not change getter function name and class signature
```

* architecture/version_x/model.py
```
Define the architecture in build function.
Do not change anything else.
For a new model, a new folder with a incremental version number
should be created.
```

* core/model_trainer.py
```
Make changes to get_data_provider() function. Change code only inside
session of execute() function
```

* core/generate_visualization.py
```
Make changes to get_model() function only.
```

* hyperparameter/version_x/param
```
Modify param.json file in a provided version folder or add a new verson
folder with param.json file.
```
