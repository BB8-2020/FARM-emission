from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten, BatchNormalization, Conv2D
from tensorflow.keras.regularizers import l2
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer


def get_data():
    """
    Used to read the data off of the dataset file (hdf5), and turn it into a pandas dataframe
    The data hdf5 file was created with pickle 4 protocol to support python 3.7.

    Returns
    -------
         A pandas dataframe with all the raw data.

    """
    print('loading data...')
    folder = r"D:\FARM_data\Soil_Spectra_Label"
    reread = pd.read_hdf(folder + r"\labeled_data.hdf5", key='FR')
    countries = ['AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'EL', 'ES', 'HR', 'HU', 'IE',
                 'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'UK']

    for country in countries:
        temppd = pd.read_hdf(folder + r"\labeled_data.hdf5", key=country)
        reread = pd.concat((reread, temppd), ignore_index=True)
    print('done')

    return reread


def add_landscapes(reread):
    """
    Adds the column 'LC1_Desc' which tells
    which type of landscape the data point is.

    Parameters
    ----------
        reread (pandas dataframe): complete raw dataset.

    Returns
    -------
         A pandas dataframe with landscape type column added.

    """
    print("Adding landscape column...")
    folder1 = r"D:\FARM_data\LUCAS2015_topsoildata_20200323"
    tempdf = pd.read_csv(folder1 + r"\LUCAS_Topsoil_2015_20200323.csv", usecols=["Point_ID", "LC1_Desc"])
    reread = pd.merge(reread, tempdf, on='Point_ID', how='left')

    print("done")
    print(len(reread))
    return reread


def remove_outliers(reread):
    """
    Filters all datapoints their outliers for each landscape type.
    This is measured based on the outliers of the OC value column.

    Parameters
    ----------
        reread (pandas dataframe): complete raw dataset.

    Returns
    -------
         A pandas dataframe with outliers removed.

    """
    print("Removing outliers...")
    all_landscapes = reread["LC1_Desc"].unique()
    filtered_df = pd.DataFrame(columns=reread.columns)

    for landscape in all_landscapes:
        temppd = reread.loc[reread['LC1_Desc'] == landscape]
        Q1 = temppd['OC'].quantile(0.25)
        Q3 = temppd['OC'].quantile(0.75)
        IQR = Q3 - Q1
        temppd = temppd[temppd['OC'] < Q3 + IQR * 1.5]
        temppd = temppd[temppd['OC'] > Q1 - IQR * 1.5]
        filtered_df = filtered_df.append(temppd)

    reread = filtered_df
    filtered_df = None  # Empty variable for RAM
    print("done")
    print(len(reread))
    return reread


def setup_data(reread):
    """
    Sets up the data to use it for the CNN model, First it splits
    the data from the input values and labels (x and y), then binarizes the labels.
    After this the all the data is plit into train and test data.

    Parameters
    ----------
        reread (pandas dataframe): complete raw dataset.

    Returns
    -------
         5 variables containing the feature test and train set,
         target train and test set, and the lenght of the target set.

    """
    print("Setup data...")
    X = np.array(list(reread['spectogram'].values))
    y = reread['OC_state'].values
    reread = None  # Empty variable for RAM
    lb = LabelBinarizer()
    y = lb.fit_transform(y)

    label_lenght = len(y[0])
    X_train, X_test, y_train, y_test = train_test_split(X, y)
    X = None  # Empty variable for RAM
    y = None  # Empty variable for RAM
    print("Setup data: Done\n")
    return label_lenght, X_train, X_test, y_train, y_test


def setup_model(label_train_length):
    """
    Sets up the whole model for the CNN.

    Parameters
    ----------
        label_train_length (int): The size of the target set.

    Returns
    -------
         A full unfitted CNN model.

    """
    print("Making model...")

    # Setup key parameters
    reg = l2(0.0005)
    init = "he_normal"
    chanDim = -1

    # The model:
    model = Sequential()
    model.add(Conv2D(32, (7, 7), strides=(2, 2), padding="valid",
              kernel_initializer=init, kernel_regularizer=reg,
              input_shape=(217, 335, 3)))

    # here we stack two CONV layers on top of each other where
    # each layerswill learn a total of 32 (3x3) filters
    model.add(Conv2D(32, (3, 3), padding="same",
                     kernel_initializer=init, kernel_regularizer=reg))
    model.add(Activation("relu"))
    model.add(BatchNormalization(axis=chanDim))
    model.add(Conv2D(32, (3, 3), strides=(2, 2), padding="same",
                     kernel_initializer=init, kernel_regularizer=reg))
    model.add(Activation("relu"))
    model.add(BatchNormalization(axis=chanDim))
    model.add(Dropout(0.25))

    # stack two more CONV layers, keeping the size of each filter
    # as 3x3 but increasing to 64 total learned filters
    model.add(Conv2D(64, (3, 3), padding="same",
                     kernel_initializer=init, kernel_regularizer=reg))
    model.add(Activation("relu"))
    model.add(BatchNormalization(axis=chanDim))
    model.add(Conv2D(64, (3, 3), strides=(2, 2), padding="same",
                     kernel_initializer=init, kernel_regularizer=reg))
    model.add(Activation("relu"))
    model.add(BatchNormalization(axis=chanDim))
    model.add(Dropout(0.25))

    # increase the number of filters again, this time to 128
    model.add(Conv2D(128, (3, 3), padding="same",
                     kernel_initializer=init, kernel_regularizer=reg))
    model.add(Activation("relu"))
    model.add(BatchNormalization(axis=chanDim))

    # fully-connected layer
    model.add(Flatten())
    model.add(Dense(512, kernel_initializer=init))
    model.add(Activation("selu"))
    model.add(BatchNormalization())
    model.add(Dropout(0.5))

    # softmax classifier
    model.add(Dense(label_train_length))
    model.add(Activation("softmax"))
    print("Making model: Done\n")
    return model


def train_model(model, X_train, y_train):
    """
    Trains the model

    Parameters
    ----------
        model (CNN): An unfitted CNN model.
        X_train (numpy array): The features the model gets trained on.
        y_train (numpy array): The targets the model gets trained on.

    Returns
    -------
         A fitted CNN model

    """
    print("Training model...")
    model.compile(loss='categorical_crossentropy', metrics='accuracy', optimizer="adamax")
    model.fit(X_train, y_train,
              batch_size=64,
              epochs=8,
              verbose=1, shuffle=True)
    print("Training model: Done\n")
    return model


def score_model(model, X_test, y_test):
    """
    Scores the models perfomance and prints it out

    Parameters
    ----------
        model (CNN): A fitted CNN model.
        X_test (numpy array): The features the model gets tested on.
        y_test (numpy array): The targets the model gets tested on.

    """
    score = model.evaluate(X_test, y_test)
    print('Test score:', score[0])
    print('Test accuracy:', score[1])


if __name__ == '__main__':
    # setup data
    reread = get_data()
    reread = add_landscapes(reread)
    reread = remove_outliers(reread)
    label_length, X_train, X_test, y_train, y_test = setup_data(reread)

    # Train and score model
    model = setup_model(label_length)
    model = train_model(model, X_train, y_train)
    score_model(model, X_test, y_test)
