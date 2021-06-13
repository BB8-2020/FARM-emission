# FARM-emision

This code is to predict the organic corbon values based on the reflectence geven off of an area. 

The run the program one can first either use the trained model or train the model themselves.
To train a model you used one of the notebooks in the code #49213 folder. Here you have different models one can use to train.
First you have the CNN model, which there are 2 versions off. One version is run on google colab and the other is for jupyter notebook.
The run the one for google colab you must change the data source it obtains by furst hooking up your drive. To do this run the first 2
cells and the program will give you a link to obtain a key from and use it. Then you specify which files to be used for the model in 
the third cell. Ours is hdf5 file named "labeled_data_pickle4.hdf5", Which is split in different landcodes, if this set up differntly in your dataset
change the code up to the "loading dataset done" line to fit how yours dataset needs to be retrieved, but the end variable needs to be a pandas dataframe
containing all your features and a target value as its last column.

The second part removes certain landscapes from the dataset, if this is not needed for your dataset remove this part.
After this the outliers in your target value gets filtered out.
In the "setup data..." section the dataset is plit in X (features) and y (target) values, and those are split again in train and test data.

All code after this is the setup and running of the CNN model.

In the code for jupyter notebook all the same principles apply as the previous version but there is no need to hook up your drive, the folder containing
your dataset is directly retrieved from your computer, the folder containing your dataset needs to be changed. And all the code filtering landscapes and how the data
is retrieved from your files needs to be personalized.

The KNN model is a more accurate model, all the setup needed is to retrieve the data in the second cell, how this is done most likely will be different
for your data depending on how the data is set up. The end result of the second cell is a pandas dataframe containing all your features and a target on the last column.

