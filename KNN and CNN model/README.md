# KNN and CNN model
These files create a model to predict soil organic carbon values based on reflectance values in a 
dataset. There is a K-nearest neighbour model and a Convolutional neural network model. The KNN model uses raw reflectance values from the dataset. And the CNN model uses spectograms made from the reflectance values. These spectograms can be made in the make dataset python file in the make and clean dataset folder.

There are jupyter notebook files that can complete the task, and python files where the file is devided in functions that can be used individually to complete the task.

## CNN model.py
In this file is a CNN model is made. 

* Used to read the data off of the dataset file (hdf5), and turn it into a pandas dataframe. The data hdf5 file was created with pickle 4 protocol to support python 3.7 (get_data())
* Adds the column 'LC1_Desc' which tells which type of landscape the data point is. (add_landscapes(dataframe))
* Remove all strong outliers of the OC values in the dataset. (remove_outliers(dataframe))
* Sets up the data to use it for the CNN model, First it splits the data from the input values and labels (x and y), then binarizes the labels. After this the all the data is plit into train and test data.(setup_data(dataframe))
* Sets up the whole model for the CNN. (setup_model(int))
* Trains the model (train_model(model, array, array))
* Scores the models perfomance and prints it out (score_model(model, array, array))


## KNN model.py
In this file a KNN model is made.

* Reads all csv files of the LUCAS 2015 dataset. Reads the reflectance values and OC values of all given location points and gets put in a pandas dataframe. (get_data())
* Filters every 20th reflectance value, it has been shown to increase the accuracy of our model and also speeds up the fitting process. (filter_data(dataframe))
* Remove all strong outliers of the OC values in the dataset. (remove_outliers(dataframe))
* Turn all labels in categories. The values where continues values and are turned into ranges (convert_to_categories(array, int))
* Seperate the dataset into its label (y) and input data (X), and split the data into train and test data, the test data is test_size% of the entire dataset. (split_data(dataframe, float, int))
* The K-nearest neighbour model, build and fitted. Here the results also get printed. (KNN_model(array, array, array, array))


## Usage Command

OS X & Linux:

```sh
python <filename.py>
```

Windows:

```sh
python <filename.py>

```
