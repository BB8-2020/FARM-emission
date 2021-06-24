import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier


def get_data():
    """
     Reads all csv files of the LUCAS 2015 dataset. Reads the reflectance
     values and OC values of all given location points and gets put in a pandas dataframe.
     Returns
     -------
          A pandas dataframe with all the raw data.
     """
    # Every land code, each code is a csv file.
    LC = ["AT", "BE", "NL", "DE", "UK", "EL", "EE", "DK", "CZ", "CY", "BG", "FI", "FR",
          "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "PL", "PT", "RO", "SE", "SI", "SK"]

    result = pd.DataFrame()
    spec = pd.read_csv(r'LUCAS2015_topsoildata_20200323/LUCAS_Topsoil_2015_20200323.csv')

    for c in LC:
        df = pd.read_csv(r"LUCAS2015_spectra/LUCAS2015_Soil_Spectra_EU28/spectra_ "+c+" .csv")
        columns = df.columns[5:]
        columns = columns.insert(0, 'PointID')
        left = df[columns]
        right = spec[['Point_ID', 'OC']]
        right = right.rename(columns={'Point_ID': 'PointID'})
        r = pd.merge(left, right, on="PointID")
        result = pd.concat([result, r], axis=0)
    return result


def filter_data(result):
    """Filters every 20th reflectance value, it has been shown to increase the accuracy of
    our model and also speeds up the fitting process"""
    filt_columns = list(result.columns[::20])
    filt_columns.append("OC")
    result = result[filt_columns]
    return result


def remove_outliers(result):
    """
    Remove all strong outliers of the OC values in the dataset.
    Parameters
    ----------
        result (pandas dataframe): complete dataset.
    Returns
    -------
         A pandas dataframe with its outliers removed.
    """
    Q1 = result['OC'].quantile(0.25)
    Q3 = result['OC'].quantile(0.75)
    IQR = Q3 - Q1
    print(Q1, Q3, IQR)
    result = result[result['OC'] < Q3 + IQR * 1.5]
    result = result[result['OC'] > Q1 - IQR * 1.5]
    U_result = result.reset_index()
    return U_result


def convert_to_categories(y, ranges=1):
    """
    Turn all labels in categories. The values where continues
    values and are turned into ranges.
    Parameters
    ----------
        y (numpy array): all the target variables.
        ranges (int): The size of the range per category.
    Returns
    -------
         4 variables containing the feature test and train set, and
         target train and test set.
    """
    maxvaluey = int(max(y))
    catlist = []
    for i in y:
        for j in range(0, maxvaluey + ranges, ranges):
            if j <= i < j + ranges:
                catlist.append(f'{j}-{j + ranges}')
    y = catlist
    return y


def split_data(result, test_size=0.09, random_state=3):
    """
    Seperate the dataset into its label (y) and input data (X), and
    split the data into train and test data, the test data is test_size% of the entire dataset.
    Parameters
    ----------
        result (pandas dataframe): complete dataset.
        test_size (float): How much of the dataset becomes the test set.
        random_state (int): The seed that splits the dataset for consistent outputs.
    Returns
    -------
         4 variables containing the feature test and train set, and
         target train and test set.
    """
    X = result[result.columns[2:-1]].values
    y = result[result.columns[-1]].values
    y = convert_to_categories(y)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    print("Labels:\n {} \n".format(y))
    print("Training data: \n {} \n".format(X))

    print("Size of test dataset: {}".format(len(X_test)))
    print("Size of train dataset: {}".format(len(X_train)))

    return X_train, X_test, y_train, y_test


def KNN_model(X_train, X_test, y_train, y_test):
    """
    The K-nearest neighbour model, build and fitted. Here the
    results also get printed.
    Parameters
    ----------
        X_train (numpy list): The features the model gets trained on
        X_test (numpy list): The features the model gets tested on
        y_train (numpy list): The targets the model gets trained on
        y_test (numpy list): The targets the model gets tested on
    """
    neigh = KNeighborsClassifier(n_neighbors=1, weights='distance')
    neigh.fit(X_train, y_train)
    score = neigh.score(X_test, y_test)
    print("Score of the model: {}".format(score))
    print("Score of the model in percentage: {}%".format(round(score * 100, 1)))
