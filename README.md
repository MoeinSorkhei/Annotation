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
* If one is interested to actually see the images, the PNG version of the test images could be downloaded from [here](https://drive.google.com/file/d/1UhQdmzNjKxiou5HqE_GEEXqvgpzXJ9Qp/view?usp=sharing) and train images from [here](https://drive.google.com/file/d/1Yu8a6VhhkohwV7fjdDqJK06cAZKFsZfg/view?usp=sharing).

___
### Instructions
All the commands should be run from inside the `src` folder.
* Make sure the conda environment is active:  
`conda activate annotation2`

* Starting a session for rating the test images:  
`python main.py --annotator Moein --new --session_name sort --data_mode test --ui_verbosity 2`

* Splitting the sorted list to bins needed for sorting train data:
`python main.py --session_name split --n_bins 12`  

* Starting a session for rating train images (once the bins are created):
`python main.py --annotator Moein --new --session_name sort --data_mode train --ui_verbosity 2`

* Variability:  
`python main.py --annotator Moein --already --session_name variability_intra --data_mode test --ui_verbosity 2`

* (Optional) In order to visualize the sorted list, you can run the following command:  
`python main.py --convert_to_png --image_list results`  
This will put the png version of the sorted images in the `output_visualized/sorted_imgs_png` folder. Note that the images will most likely appear to be sorted by name (default by the OS). You need to change the the View option to be sorted by "Date Created" so they match the order of the sorted list.



___
### Important running arguments
* `--session_name`: Specifies the type of the session, could be either `sort` (for rating test/train images) or `split` (for splitting the perfectly sorted list).
* `--data_mode`: Specifies the type of data that is being rated, could be either `test` or `train`.
* `--annotator`: The name of the annotator, this should always be provided when beginning a session for rating test/train images.
* `--ui_verbosity`: Determines how much the UI should be verbose (default: 1). Use a value of 2 to also see the image names, a value of 3 to also see the search intervals and other details in the UI. A value of 4 is used for debugging (automatically set when using `--debug`).
* `--max_imgs_per_session`: The number images that one should rate in each session (default: 10).
* `--resize_factor`: Determines how much the DICOM high resolution images should be resized (default: 7).

Note that the default values of all the parameters could be found in the `globals.py` file.

___
### Additional notes:
* It is OK if for any reason a session is not ended successfully, or if you decide to close a session (close the UI window) in the middle of the process. All the ratings are saved while you are using the tool and nothing will be lost. You can simply run a new session again by running the corresponding command.
* The UI will show a success message when an image is successfully inserted into the perfectly sorted list or bins. It could also show a message denoting that a case (the image that is being rated) is aborted due to inconsistency in rating. These are shown only to inform the rater, you can continue rating regardless of the message.
