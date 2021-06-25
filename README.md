# Opdracht: FARM-emission
> Visualize the Soil in Kenya

## Usage Command

OS X & Linux:

```sh
python <filename.py>
```

Windows:

```sh
python <filename.py>

```

## Usage 
- Baseline Model: Baseline Model Code
- Spectrogram Maker & Lucas Dataset Processing: Code #51404
- CNN & KNN model: code #49213 (Jupyter notebook runs whole process & Python files contains the function codes)

This code is to predict the organic corbon values based on the reflectence given of an area. 
To run the program, one can first use the trained model or train the model themselves.
To train a model you use one of the notebooks in the code #49213 folder. Here you have different models one can use to train.

- First part:
First you have the CNN model, which has 2 versions. One version is to run on google colab and the other is for jupyter notebook.
To run the one for google colab you must change the data source it obtains by first hooking up your drive. To do this run the first 2
cells and the program will give you a link to obtain a key from and use it. Then you specify which files to be used for the model in 
the third cell. Ours is an hdf5 file named "labeled_data_pickle4.hdf5", which is split in different landcodes, if this set up differntly in your dataset
change the code up to the "loading dataset done" line to fit how your dataset needs to be retrieved, but the end variable needs to be a pandas dataframe
containing all your features and a target value as it's last column.

- Second Part:
The second part removes certain landscapes from the dataset, if this is not needed for your dataset remove this part.
After this the outliers in your target value gets filtered out.
In the "setup data..." section the dataset is split in X (features) and y (target) values, and those are split again in train and test data.

All code after this is the setup and running of the CNN model.

In the code for jupyter notebook all the same principles apply as for the previous version but there is no need to hook up your drive, the folder containing
your dataset is directly retrieved from your computer, the folder containing your dataset needs to be changed. And all the code filtering landscapes and how the data
is retrieved from your files needs to be personalized.

The KNN model is a more accurate model, all the setup needed is to retrieve the data in the second cell, how this is done most likely will be different
for your data depending on how the data is set up. The end result of the second cell is a pandas dataframe containing all your features and a target on the last column.

## Library Install
Describes how to install all the Libraries

OS X & Linux:
```sh
pip3 install numpy
pip3 install pandas
pip3 install sklearn
pip3 install csv
pip3 install matplotlib
pip3 install scipy
pip3 install io
pip3 install pickle
pip3 install tensorflow
```

Windows:
```sh
pip install numpy
pip install pandas
pip install sklearn
pip install csv
pip install matplotlib
pip install scipy
pip install io
pip install pickle
pip install tensorflow
```

## Student:
Quinn de Groot:
[https://github.com/DragonKiller952](github)

Ruben v Raaij: [https://github.com/GameModes](github)

Adam Chebil: [https://github.com/AdamMC-GL](github)

Guy Veenhoff: [https://github.com/AI-Gio](github)

Koen Heertum :


## Code Explaination
Documentation is included in both the Python files and Jupyter Notebooks


