# Annotation

### Installation
- The easiet way to pull the code is to use the [Git GUI Clinet](https://git-scm.com/downloads/guis).
- Create a `conda` environemnt using the provided `env.yml` file: `conda env create -f env.yml`. This will create create an envoronment wih name `annotation2`.


___
### Data
- Create a folder named `data` in the project folder (beside the `src` folder)
- Download the test images and put them in the `data/test_imgs` folder
- Download the train images and put them in the `data/train_imgs` folder

### Links
* Test images: https://drive.google.com/file/d/1fdqnqGMJdGCttU_S2ud2aV4LR08P47tb/view?usp=sharing
* Train images: https://drive.google.com/file/d/1mFo5qyN0FyvecA1YMmem2ptZkUBIShkK/view?usp=sharing

___
### Example commands

All the commands should be run from inside the `src` folder.
* Creating the seed list (the initial sorted list):  
`python main.py --make_seed_list`

* Starting a session for rating the test images:  
`python main.py --annotator [YourName] --session_name sort --data_mode test --ui_verbosity 2`  
 As soon as you start the first session, the `output` folder will be created.

* Splitting the sorted list to bins needed for sorting train data:  
`python main.py --annotator [YourName] --session_name split --n_bins [NumBins]`  
 After running this command, you should see the files containing images in different bins. The files are named like `bin_0.txt`, `bin_1.txt` etc. and are located in
 the `output` folder.

* Starting a session for rating train images:  
`python main.py --annotator [YourName] --session_name sort --data_mode train --ui_verbosity 2`


___
### Important running arguments
* `--session_name`: Specifies the type of the session, could be either `sort` (for rating test/train images) or `split` (for splitting the perfectly sorted list).
* `--data_mode`: Specifies the type of data that is being rated, could be either `test` or `train`.
* `--annotator`: The name of the annotator, this should always be provided when beginning a session for rating test/train images.
* `--ui_verbosity`: Determines how much the UI should be verbose (default: 1). Use a value of 2 to also see the image names, a value of 3 to also see the search intervals and other details in the UI. A value of 4 is used for debugging (automatically set when using `--debug`).
* `--max_imgs_per_session`: The number images that one should rate in each session (default: 10).
* `--resize_factor`: Determines how much the DICOM high resolution images should be resized (default: 7).

Note that the default values of all the parameters could be found in the `globals.py` file.
