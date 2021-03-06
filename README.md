# nci_isbi2013_segmentation by Paul F. Jaeger
This project was carried out as part of the recruitment processs for a major AI company. The task was to implement a model for
CG and PZ Prostate segementation on T2-weighted MR images. Project time were 7 days. 

This framework is able to train 2D and 3D UNet architectures on this data. This framework was written following a 'low-level-code-policy' as far as possible. Most files other than exec.py are merely collections of functions to make the code more understandable. See the project report for more info:
https://drive.google.com/file/d/1WhBnVY1xc7pXJHaq9Y2PyaFW4WUQiZP0/view?usp=sharing


## Get Dependencies

```
pip install numpy scipy tensorflow tensorflow-gpu sklearn matplotlib dicom dicom_numpy pynrrd

https://github.com/MIC-DKFZ/batchgenerators.git
cd batchgenerators
pip install .
```


## Get the Data
Download the Data set from https://wiki.cancerimagingarchive.net/display/DOI/NCI-ISBI+2013+Challenge%3A+Automated+Segmentation+of+Prostate+Structures.
Make sure all 6 downloaded folders are placed in the same directory and specify this location as 'raw_data_dir' in configs.py

## Execute

Preprocess the data:

```
python preprocessing.py
```

Train the network (change settings in configs.py if desired. by default trains a 2D UNet with dice loss.)
```
python exec.py               
```
by default, one training is executed, where the training data is split into 80% training and 20% validation data. If you want to run a cross-validation, specify which folds to train (the default split is fold 0 of a 5 fold-cross validation):
```
python exec.py --folds 0 1 2 .... # specify any combination of folds [0-4]              
```
During training the configs file is copied to the specified experiment folder (default is raw_data_dir/my_experiment).
Get test set predictions of a trained model:
```
python exec.py --mode test --exp /path/to/experiment/folder 
```
This prints evaluation scores, saves ndarray softmax predictions and predictions_plots to /path/to/experiment/folder /test_files . By default this gets predictions only from the "fold 0 model". use --folds to average predictions over several trained models.
